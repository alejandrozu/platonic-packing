#!/usr/bin/env python3
"""Sequential kernel builds with complete dependency receipts for chunked proofs.

A record passes only when its data, every arithmetic block, and aggregate pass
with the prescribed audits, and all sources/dependencies remain unchanged.
Optional resume trusts only matching earlier receipts AND matching object,
source, core, manifest, and dependency hashes; no unchecked success is reused.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import time

import run_lean

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audited_theorems(log):
    found={name:sorted(x.strip() for x in values.split(',') if x.strip())
        for name,values in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]",log,re.S)}
    found.update({name:[] for name in re.findall(r"'([^']+)'\s+does not depend on any axioms",log)})
    return found


def core_hashes(extension):
    return {str(p.relative_to(FORMAL)).replace('\\','/'):digest(p)
        for p in sorted((FORMAL/'PackingCertificates').glob('*.'+extension))}


def normalize_row(row):
    row=dict(row)
    row.setdefault('record_id',row['id'])
    if row.get('steps'):
        return row
    path=FORMAL/row['path']
    source=path.read_text(encoding='utf8')
    audits=row.get('expected_audits') or re.findall(r'^\s*#print axioms\s+([A-Za-z0-9_.]+)',source,re.M)
    audits=[row['module']+'.'+name if '.' not in name else name for name in audits]
    step=dict(row,id='portable_'+row['id'],kind='ordinary',
        expected_audits=audits,
        generated_source_sha256=row.get('generated_source_sha256',digest(path)))
    row['steps']=[step]
    row['portable_original_kind']='ordinary'
    row.setdefault('dependencies',[])
    return row

def validate_plan(row):
    steps=row['steps']
    ordinary=row.get('portable_original_kind')=='ordinary'
    if not ordinary and (not steps or steps[0]['kind']!='data' or steps[-1]['kind']!='aggregate'):
        raise ValueError('Missing ordered data/aggregate stages: '+row['id'])
    indices=[i for step in steps if step['kind']=='proof_block' for i in step['piece_indices']]
    if not ordinary and indices!=list(range(row['n'])):
        raise ValueError('Proof blocks do not cover every piece exactly once: '+row['id'])
    if row.get('fine_vertex_coverage'):
        count=row.get('vertex_count')
        if row['fine_vertex_coverage'] is not True or not isinstance(count,int) or count<1:
            raise ValueError('Invalid fine vertex coverage declaration: '+row['id'])
        vertices=[tuple(pair) for step in steps if step['kind']=='proof_block'
            for pair in step.get('vertex_indices',[])]
        expected={(i,p) for i in range(row['n']) for p in range(count)}
        if len(vertices)!=len(expected) or set(vertices)!=expected:
            raise ValueError('Proof blocks do not cover every piece/vertex exactly once: '+row['id'])
    if len({s['module'] for s in steps})!=len(steps):
        raise ValueError('Duplicate module in plan: '+row['id'])
    for step in steps:
        path=(FORMAL/step['path']).resolve()
        if not path.is_relative_to(FORMAL.resolve()):
            raise ValueError('Module outside formal project')
        if digest(path)!=step['generated_source_sha256']:
            raise ValueError('Generated source differs from plan: '+step['path'])
        if not step.get('expected_audits'):
            raise ValueError('No declared axiom audit: '+step['path'])
    if row.get('original_witness_sha256'):
        locations=[HERE/folder/(row['record_id']+'.json') for folder in ('witnesses','witnesses_nd')]
        witness=next((p for p in locations if p.is_file()),None)
        if witness is None or digest(witness)!=row['original_witness_sha256']:
            raise ValueError('Exported witness differs from plan: '+row['record_id'])
        if row.get('fine_vertex_coverage'):
            witness_data=json.loads(witness.read_text(encoding='utf8'))
            if len(witness_data['template_vertices'])!=row['vertex_count']:
                raise ValueError('Fine vertex count differs from actual template: '+row['record_id'])
    if row.get('original_source_path') and row.get('original_json_sha256'):
        source=HERE/'inputs'/row['original_source_path']
        if digest(source)!=row['original_json_sha256']:
            raise ValueError('Original source differs from plan: '+row['record_id'])

    if row.get('original_geometry_path') and row.get('original_geometry_sha256'):
        geometry=HERE/'inputs'/row['original_geometry_path']
        if digest(geometry)!=row['original_geometry_sha256']:
            raise ValueError('Canonical geometry differs from plan: '+row['record_id'])

def current_sources(row):
    return {s['path']:digest(FORMAL/s['path']) for s in row['steps']}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--lean',type=Path,default=Path(shutil.which('lean') or str(Path.home()/'.elan/toolchains/leanprover--lean4---v4.31.0/bin/lean.exe')))
    ap.add_argument('--mathlib-project',type=Path,default=FORMAL)
    ap.add_argument('--manifest',default='generated-chunked-cube-modules.json')
    ap.add_argument('--receipt',default='lean-chunked-cube-verification.json')
    ap.add_argument('--only',nargs='*')
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--timeout',type=int,default=600)
    ap.add_argument('--memory-mb',type=int,default=4096)
    ap.add_argument('--resume',action='store_true')
    args=ap.parse_args()
    if args.memory_mb<1:
        ap.error('--memory-mb must be positive')
    manifest=HERE/args.manifest
    receipt_path=HERE/args.receipt
    plans=[normalize_row(r) for r in json.loads(manifest.read_text())]
    plans=sorted((r for r in plans if r['n']<=args.max_n and
        (not args.only or r['id'] in args.only or r['record_id'] in args.only)),key=lambda r:r['n'])
    if not plans:
        raise SystemExit('No chunked records match the selection')
    for row in plans:validate_plan(row)
    manifest_sha=digest(manifest)
    core_source=core_hashes('lean')
    core_objects=core_hashes('olean')
    old={}
    if args.resume and receipt_path.is_file():
        previous=json.loads(receipt_path.read_text())
        if (previous.get('manifest_sha256')==manifest_sha and
            previous.get('core_source_hashes')==core_source and
            previous.get('core_olean_hashes')==core_objects):
            old={r['id']:r for r in previous.get('results',[])}
    deps=[p/'.lake/build/lib/lean' for p in (args.mathlib_project/'.lake/packages').iterdir()
        if (p/'.lake/build/lib/lean').is_dir()]
    env=os.environ.copy()
    env['LEAN_PATH']=os.pathsep.join(map(str,[FORMAL,FORMAL/'.lake/build/lib/lean',*deps]))
    receipt=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
        compiler=subprocess.check_output([str(args.lean),'--version'],text=True).strip(),
        kernel_arithmetic='by decide +kernel; exact source-bound rational arithmetic; no native_decide',
        manifest=args.manifest,manifest_sha256=manifest_sha,memory_mb=args.memory_mb,
        core_source_hashes=core_source,core_olean_hashes=core_objects,
        results=[],passed_records=0,failed_records=0,
        completeness_rule='Data, all disjoint piece blocks, aggregate, all specified audits, stable source and dependency hashes are required.')

    def save():
        receipt['passed_records']=sum(r.get('passed',False) for r in receipt['results'])
        receipt['failed_records']=sum(r.get('complete',False) and not r.get('passed',False) for r in receipt['results'])
        receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')

    for row in plans:
        source_before=current_sources(row)
        result={k:v for k,v in row.items() if k!='steps'}
        result.update(steps=[],passed=False,complete=False,source_hashes_before=source_before,
            elapsed_seconds=0.0,verified_build_seconds=0.0)
        receipt['results'].append(result)
        previous_steps={s['id']:s for s in old.get(row['id'],{}).get('steps',[])}
        dependencies={}
        started=time.monotonic()
        for step in row['steps']:
            source=FORMAL/step['path']; target=source.with_suffix('.olean')
            previous=previous_steps.get(step['id'])
            reusable=(previous and previous.get('passed') and target.is_file() and
                previous.get('source_sha256')==digest(source) and
                previous.get('olean_sha256')==digest(target) and
                previous.get('dependency_olean_hashes')==dependencies and
                previous.get('all_expected_audits_seen') and
                (FORMAL/previous.get('log','')).is_file() and
                digest(FORMAL/previous['log'])==previous.get('log_sha256'))
            if reusable:
                built=dict(previous,reused_receipt=True,elapsed_this_run_seconds=0.0)
            else:
                built=run_lean.run_one(step,args.lean,env,args.timeout,args.memory_mb)
                built['reused_receipt']=False
                built['elapsed_this_run_seconds']=built['elapsed_seconds']
            log=(FORMAL/built['log']).read_text(encoding='utf8')
            audit=audited_theorems(log)
            missing=[a for a in step['expected_audits'] if a not in audit]
            built['audited_theorems']=audit
            built['missing_expected_audits']=missing
            built['all_expected_audits_seen']=not missing
            used={a for values in audit.values() for a in values}
            built['passed']=bool(built['passed'] and not missing and
                not (used-run_lean.ALLOWED) and 'sorryAx' not in log)
            built['dependency_olean_hashes']=dict(dependencies)
            stable=(digest(manifest)==manifest_sha and core_hashes('lean')==core_source and
                core_hashes('olean')==core_objects and current_sources(row)==source_before)
            built['all_sources_stable']=stable
            built['passed']=bool(built['passed'] and stable)
            result['steps'].append(built)
            result['elapsed_seconds']=round(time.monotonic()-started,3)
            result['verified_build_seconds']=round(sum(s['elapsed_seconds'] for s in result['steps']),3)
            save()
            print(json.dumps(dict(record_id=row['record_id'],step=step['id'],kind=step['kind'],
                passed=built['passed'],exit_code=built['exit_code'],
                elapsed_seconds=built['elapsed_seconds'],reused_receipt=built['reused_receipt'])),flush=True)
            if not built['passed']:
                break
            dependencies[step['module']]=digest(target)
        complete_steps=len(result['steps'])==len(row['steps'])
        all_pass=complete_steps and all(s['passed'] for s in result['steps'])
        result['source_hashes_after']=current_sources(row)
        result['dependency_olean_hashes']=dependencies
        result['dependency_source_hashes']={s['path']:source_before[s['path']] for s in row['steps'][:-1]}
        result['dependency_object_hashes']={s['path'].replace('.lean','.olean'):digest((FORMAL/s['path']).with_suffix('.olean'))
            for s in result['steps'] if s['passed'] and s['kind'] not in ('aggregate','ordinary')}
        result['passed']=bool(all_pass and result['source_hashes_after']==source_before)
        result['complete']=True
        result['exit_code']=0 if result['passed'] else next((s['exit_code'] for s in result['steps'] if not s['passed']),None)
        result['audit_output_seen']=bool(result['passed'] and all(s['all_expected_audits_seen'] for s in result['steps']))
        result['axioms']=sorted({a for s in result['steps'] for a in s.get('axioms',[])})
        result['unexpected_axioms']=sorted(set(result['axioms'])-run_lean.ALLOWED)
        result['olean_sha256']=digest(FORMAL/row['path'].replace('.lean','.olean')) if result['passed'] else None
        aggregate=result['steps'][-1] if result['steps'] and result['steps'][-1]['kind'] in ('aggregate','ordinary') else None
        if aggregate:
            for field in ('source_sha256','log','log_sha256','source_unchanged_during_build'):
                result[field]=aggregate.get(field)
        result['dependencies']=[dict(s) for s in result['steps'] if s['kind'] not in ('aggregate','ordinary')]
        result['elapsed_seconds']=round(time.monotonic()-started,3)
        save()
        print(json.dumps(dict(id=row['id'],passed=result['passed'],
            completed_steps=len(result['steps']),required_steps=len(row['steps']),
            elapsed_seconds=result['elapsed_seconds'])),flush=True)
    return int(receipt['failed_records']>0)


if __name__=='__main__':
    raise SystemExit(main())



