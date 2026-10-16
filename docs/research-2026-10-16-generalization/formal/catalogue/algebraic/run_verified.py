#!/usr/bin/env python3
"""Sequential, source-bound algebraic packing builds with full import receipts.

Generation/export never counts as verification. Every imported local extension
is rebuilt (or reused only from an exactly matching receipt), followed by the
record module and its prescribed semantic declaration. Direct core objects
must match the already successful pinned core-verification.json.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parents[1]
sys.path.insert(0,str(FORMAL))
sys.path.insert(0,str(HERE))
import verify_core as core
import verify_extensions as closure
import generate_3d as record_generator
import geometry_intervals as geometry_generator

FREEZE='1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'


def read(path):return json.loads(path.read_text(encoding='utf8'))
def rel(path):return path.resolve().relative_to(FORMAL).as_posix()
def path(value):
    p=(FORMAL/value).resolve();p.relative_to(FORMAL)
    return p
def save(target,value):
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_suffix(target.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8');temporary.replace(target)
def digest_file(value,expected):
    p=path(value)
    if not p.is_file()or core.digest(p)!=expected:raise ValueError('Missing or changed frozen file '+value)
    return dict(path=rel(p),sha256=expected)
def number(value):return Fraction(value)


def rational_tree(value):
    if value is None:
        return None
    if isinstance(value,list):
        return [rational_tree(x)for x in value]
    return number(value)


def geometry_binding(row,proposal):
    geometry=read(path(row['geometry_source_path']))
    intervals=read(path(row['geometry_intervals_path']))
    if intervals['geometry_sha256']!=row['geometry_source_sha256']:
        raise ValueError('Interval templates are tied to a different exact geometry source')
    roots={r['id']:r for r in intervals['roots']}
    files=[]
    # Reconstruct the exact canonical source text from the audited source
    # coefficients, rather than accepting a module name or data hash alone.
    root_lines=['import PackingCertificates.Algebraic.Template','',
        'set_option maxRecDepth 0','set_option maxHeartbeats 0','',
        'namespace PackingCertificates.Algebraic.Generated','']
    for root in intervals['roots']:
        name=root['id']
        root_lines.extend([f'def {name} : RootSpec := ⟨{geometry_generator.polynomial(root["polynomial"])}, {geometry_generator.interval(root["interval"])}⟩',
            f'theorem {name}_checked : {name}.check = true := by decide +kernel',''])
    root_lines.extend(['end PackingCertificates.Algebraic.Generated',''])
    root_source=FORMAL/'PackingCertificates/Algebraic/Generated/RootData.lean'
    if root_source.read_bytes()!='\n'.join(root_lines).replace('\n','\r\n').encode('utf8'):
        raise ValueError('RootData source differs from exact source-root transcription')
    files.append(dict(path=rel(root_source),sha256=core.digest(root_source)))
    for name in dict.fromkeys([row['piece'],row['container']]):
        raw=geometry[name];template=intervals['templates'][name];root=roots[template['root_id']]
        if rational_tree(template['coefficients'])!=rational_tree(raw['V']):
            raise ValueError('Exact canonical coordinate coefficients changed: '+name)
        if rational_tree(template['normalizer_polynomial'])!=rational_tree(raw['D']):
            raise ValueError('Exact canonical normalization polynomial changed: '+name)
        if rational_tree(root['polynomial'])!=rational_tree(raw['minpoly'])or rational_tree(root['interval'])!=rational_tree(raw['interval']):
            raise ValueError('Exact canonical root or isolating interval changed: '+name)
        if template['vertex_count'] != len(raw['V']) or template['dimension'] != 3 or template['faces'] != raw['faces']:
            raise ValueError('Canonical combinatorics/dimension changed: '+name)
        lines=['import PackingCertificates.Algebraic.Generated.RootData','',
            'set_option maxRecDepth 0','set_option maxHeartbeats 0','',
            'namespace PackingCertificates.Algebraic.Generated','',
            f'def {name} : TemplateData 3 {template["vertex_count"]} where',
            f'  rootSpec := {template["root_id"]}',
            '  coefficients := '+geometry_generator.vector(template['coefficients'],lambda v:geometry_generator.vector(v,geometry_generator.polynomial)),
            '  normalizerPolynomial := '+('none'if template['normalizer_polynomial']is None else'(some '+geometry_generator.polynomial(template['normalizer_polynomial'])+')'),
            '  normalizerSqrtInterval := '+geometry_generator.interval(template['normalizer_sqrt_interval']),
            '  vertexIntervals := '+geometry_generator.vector(template['vertex_intervals'],lambda v:geometry_generator.vector(v,geometry_generator.interval)),
            '',f'theorem {name}_normalization_checked : {name}.normalizationCheck = true := by decide +kernel',
            f'theorem {name}_vertices_checked : {name}.verticesCheck = true := by decide +kernel',
            f'theorem {name}_centroid_checked : {name}.centroidCheck {len(template["coefficients"][0][0])} = true := by decide +kernel',
            f'theorem {name}_centered : (∑ j, {name}.vertex {template["root_id"]}_checked j) = 0 :=',
            f'  {name}.centroid_sound {len(template["coefficients"][0][0])} {template["root_id"]}_checked {name}_centroid_checked',
            '',f'theorem {name}_vertices_enclosed (j : Fin {template["vertex_count"]}) (a : Fin 3) :',
            f'    ({name}.vertexIntervals j a).Contains ({name}.vertex {template["root_id"]}_checked j a) :=',
            f'  {name}.vertices_sound {template["root_id"]}_checked {name}_normalization_checked {name}_vertices_checked j a',
            '', 'end PackingCertificates.Algebraic.Generated','']
        module=FORMAL/f'PackingCertificates/Algebraic/Generated/{name}.lean'
        if module.read_bytes()!='\n'.join(lines).replace('\n','\r\n').encode('utf8'):
            raise ValueError('Canonical Lean template differs from exact geometry transcription: '+name)
        files.append(dict(path=rel(module),sha256=core.digest(module)))
    piece_count=intervals['templates'][row['piece']]['vertex_count']
    for key in ['placed_vertex_intervals','normalized_vertex_intervals','containment']:
        if any(len(values)!=piece_count for values in proposal[key]):
            raise ValueError('Proposal does not cover every exact piece vertex: '+key)
    if proposal['vertex_count']!=row['n']*piece_count:
        raise ValueError('Proposal total exact vertex count mismatch')
    return files


def source_binding(row):
    if row['source_freeze']!=FREEZE:raise ValueError('Unexpected native source freeze')
    native=path('catalogue/algebraic/inputs/'+row['source_path'])
    files=[digest_file(rel(native),row['source_sha256']),
        digest_file(row['proposal_path'],row['proposal_sha256']),
        digest_file(row['generated_module'],row['generated_source_sha256']),
        digest_file(row['geometry_source_path'],row['geometry_source_sha256']),
        digest_file(row['geometry_intervals_path'],row['geometry_intervals_sha256'])]
    proposal=read(path(row['proposal_path']));raw=read(native)
    for key in ['record_id','source_path','source_sha256','source_freeze','dimension','n','piece','container']:
        if proposal[key]!=row[key]:raise ValueError('Proposal/registry source binding mismatch: '+key)
    if proposal['geometry_sha256']!=row['geometry_source_sha256']:
        raise ValueError('Proposal geometry source hash mismatch')
    exporter=HERE/'export_3d.py'
    if proposal['proposal_exporter_sha256']!=core.digest(exporter):
        raise ValueError('Proposal exporter changed since this source-bound proposal')
    files.append(dict(path=rel(exporter),sha256=core.digest(exporter)))
    if raw['n']!=row['n']or len(raw['pieces'])!=row['n']or raw['piece']!=row['piece']or raw['container']!=row['container']:
        raise ValueError('Native source piece/count mismatch')
    if number(proposal['scale'])!=number(raw['s_full']):raise ValueError('Native scale not preserved exactly')
    if list(map(number,proposal['container_center']))!=list(map(number,raw.get('container_center',[0,0,0]))):
        raise ValueError('Native container centre not preserved exactly')
    if len(proposal['quaternions'])!=raw['n']or len(proposal['centres'])!=raw['n']or len(proposal['rotations'])!=raw['n']:
        raise ValueError('Proposal omitted a pose')
    for i,pose in enumerate(raw['pieces']):
        if len(pose) != 7 or list(map(number,pose[:3])) != list(map(number,proposal['centres'][i])) or list(map(number,pose[3:])) != list(map(number,proposal['quaternions'][i])):
            raise ValueError('Native pose not preserved with exact binary64/rational semantics')
        w,x,y,z=list(map(number,pose[3:]));q=w*w+x*x+y*y+z*z
        if q<=0:raise ValueError('Zero source quaternion')
        R=[[(w*w+x*x-y*y-z*z)/q,2*(x*y-w*z)/q,2*(x*z+w*y)/q],
           [2*(x*y+w*z)/q,(w*w-x*x+y*y-z*z)/q,2*(y*z-w*x)/q],
           [2*(x*z-w*y)/q,2*(y*z+w*x)/q,(w*w-x*x-y*y+z*z)/q]]
        if R!=[list(map(number,r))for r in proposal['rotations'][i]]:
            raise ValueError('Proposal rotation differs from exact raw source quaternion map')
    pairs=[(p['i'],p['j'])for p in proposal['planes']]
    expected=[(i,j)for i in range(raw['n'])for j in range(i+1,raw['n'])]
    if pairs!=expected or proposal['pair_count']!=len(expected):raise ValueError('Proposal does not cover all unordered pairs exactly once')
    if len(proposal['placed_vertex_intervals'])!=raw['n']or len(proposal['normalized_vertex_intervals'])!=raw['n']or len(proposal['containment'])!=raw['n']:
        raise ValueError('Proposal piece interval/containment count mismatch')
    files.extend(geometry_binding(row,proposal))
    rendered=record_generator.generate(path(row['proposal_path']),write=False)
    for key in ['record_id','generated_module','generated_source_sha256','expected_declaration']:
        if rendered[key]!=row[key]:
            raise ValueError('Registry differs from exact proposal-to-Lean transcription: '+key)
    for helper in [HERE/'generate_3d.py',HERE/'geometry_intervals.py']:
        files.append(dict(path=rel(helper),sha256=core.digest(helper)))
    return files


def approved_core():
    receipt=read(FORMAL/'core-verification.json')
    if receipt.get('status')!='passed'or receipt.get('not_run')or receipt.get('expected_lean_version')!=core.LEAN_VERSION or receipt.get('expected_mathlib_revision')!=core.MATHLIB_REVISION:
        raise ValueError('A complete successful pinned direct-core receipt is required')
    if receipt.get('builder_sha256')!=core.digest(FORMAL/'verify_core.py'):
        raise ValueError('Direct-core builder implementation does not match its receipt')
    expected=[rel(p)for p in core.stages()]
    if [row.get('path')for row in receipt['results']]!=expected:
        raise ValueError('Direct-core receipt omits, duplicates or reorders required stages')
    attested={}
    for row in receipt['results']:
        if not row.get('passed') or row.get('exit_code') != 0 or row.get('errors')or row.get('unexpected_axioms'):raise ValueError('Unsuccessful core stage')
        for p,h in [('path','source_sha256'),('olean_path','olean_sha256'),('log','log_sha256')]:digest_file(row[p],row[h])
        parsed=core.axiom_audit(path(row['log']).read_text(encoding='utf8'))
        if parsed!=row['audited_theorems']or {a for v in parsed.values()for a in v}-core.ALLOWED_AXIOMS:
            raise ValueError('Core axiom audit does not match its log')
        source=path(row['path']).read_text(encoding='utf8')
        names=re.findall(r'^\s*#print\s+axioms\s+([\w.]+)',source,re.M)
        if any(not any(full==name or full.endswith('.'+name)for full in parsed)for name in names):
            raise ValueError('Direct-core source audit directive was not printed')
        negatives=core.negative_assertions(source)
        recorded=row.get('negative_checks',[])
        if len(negatives)!=len(recorded)or any(dict(case,kernel_checked=True)!=item for case,item in zip(negatives,recorded)):
            raise ValueError('Direct-core negative assertions were not independently matched')
        attested[row['path']]=dict(path=row['path'],source_sha256=row['source_sha256'],
            olean_path=row['olean_path'],olean_sha256=row['olean_sha256'],log=row['log'],log_sha256=row['log_sha256'])
    return attested


def build_order(sources,attested):
    ordered=[];seen=set()
    def visit(source):
        source=source.resolve()
        if source in seen:return
        seen.add(source)
        for dependency in closure.local_import_closure(source,FORMAL):visit(dependency)
        if rel(source)in attested:return
        ordered.append(source)
    for source in sources:visit(source)
    return ordered


def reusable(row,source,snapshot):
    try:
        if not row or not row.get('passed') or row.get('exit_code') != 0 or row.get('imported_dependencies') != snapshot:return False
        for p,h in [('path','source_sha256'),('olean_path','olean_sha256'),('log','log_sha256')]:digest_file(row[p],row[h])
        if row['path']!=rel(source)or row.get('changed_imported_dependencies'):return False
        parsed=core.axiom_audit(path(row['log']).read_text(encoding='utf8'))
        return parsed==row['audited_theorems']and not({a for v in parsed.values()for a in v}-core.ALLOWED_AXIOMS)
    except(ValueError,KeyError,OSError):return False


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registry',type=Path,default=HERE/'generated3d-registry.json')
    p.add_argument('--only',nargs='*');p.add_argument('--mathlib-project',type=Path,required=True)
    p.add_argument('--lean',type=Path,default=core.default_lean());p.add_argument('--memory-mb',type=int,default=3072)
    p.add_argument('--timeout',type=float,default=1800);p.add_argument('--resume',action='store_true')
    p.add_argument('--reuse-only',action='store_true',help='Audit a matching --resume receipt; never launch a compiler')
    p.add_argument('--cache-receipts',nargs='*',type=Path,default=[],help='Reuse only hash-matched complete stage evidence from these additional receipts')
    p.add_argument('--extra-modules',nargs='*',default=[],help='Additional local Lean modules, such as malformed-certificate regressions, built with the same closure checks')
    p.add_argument('--plan-only',action='store_true');p.add_argument('--receipt',type=Path,default=HERE/'lean-verification.json')
    args=p.parse_args()
    if args.memory_mb <= 0 or args.timeout <= 0:p.error('Memory and timeout must be positive')
    if args.reuse_only and not args.resume:p.error('--reuse-only requires --resume')
    registry=read(args.registry);registry_hash=core.digest(args.registry)
    records=[r for r in registry['records']if not args.only or r['record_id']in args.only]
    if args.only and set(args.only)-{r['record_id']for r in records}:p.error('Unknown requested record IDs')
    if not records:raise ValueError('No algebraic records selected')
    bindings={r['record_id']:source_binding(r)for r in records}
    # Canonical data need their own frozen source hashes, not only inclusion
    # of a template's module name in a generated record.
    canonical={r['module']:r['sha256']for r in registry.get('canonical_data_modules',[])}
    for r in records:
        for module in r['canonical_template_modules']:
            if module not in canonical:raise ValueError('Canonical template absent from hashed registry')
            digest_file(module,canonical[module])
    extra=[path(value)for value in args.extra_modules]
    if any(source.suffix!='.lean'or not source.is_file()or source.relative_to(FORMAL).parts[0]!='PackingCertificates'for source in extra):
        raise ValueError('Extra modules must be existing local PackingCertificates Lean sources')
    attested=approved_core();sources=extra+[path(r['generated_module'])for r in records]
    stages=build_order(sources,attested)
    for stage in stages:
        name=rel(stage)
        if name.startswith('PackingCertificates/Algebraic/Generated/')and '/Records/'not in name:
            if name not in canonical:raise ValueError('Generated canonical dependency lacks registry hash: '+name)
            digest_file(name,canonical[name])
    if args.plan_only:
        print(json.dumps(dict(records=len(records),modules=len(stages),ordered_modules=list(map(rel,stages)),source_binding_checked=True)))
        return
    env,preflight=core.preflight(args)
    old={}
    cache_inputs=[]
    for cache in args.cache_receipts:
        previous=read(cache)
        if previous.get('schema')=='algebraic-packing-build-v1':
            cached_stages=previous.get('stages',[])
        elif previous.get('schema')=='packing-extension-verification-v2'and previous.get('passed'):
            cached_stages=previous.get('results',[])
        else:raise ValueError('Unexpected or unsuccessful stage cache receipt schema')
        cache_inputs.append(dict(path=rel(cache),sha256=core.digest(cache)))
        for stage in cached_stages:
            if stage.get('passed'):old[stage['path']]=stage
    if args.resume and args.receipt.is_file():old.update({r['path']:r for r in read(args.receipt).get('stages',[])})
    # Each invocation has an immutable log namespace. Rebuilding a shared
    # dependency must not overwrite the log hash referenced by another record.
    invocation=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    receipt=dict(schema='algebraic-packing-build-v1',started_at_utc=datetime.now(timezone.utc).isoformat(),
        status='running',registry_path=rel(args.registry),registry_sha256=registry_hash,
        builder_path=rel(Path(__file__)),builder_sha256=core.digest(Path(__file__)),
        dependency_helper_sha256=core.digest(FORMAL/'verify_extensions.py'),
        core_builder_sha256=core.digest(FORMAL/'verify_core.py'),preflight=preflight,
        memory_mb=args.memory_mb,timeout_seconds=args.timeout,core_receipt_sha256=core.digest(FORMAL/'core-verification.json'),
        direct_core_attestation=attested,requested_record_ids=[r['record_id']for r in records],
        cache_receipts=cache_inputs,invocation=invocation,
        requested_extra_modules=list(map(rel,extra)),
        stages=[],verified_records=[],unverified_records=[],source_transcription_boundary='Python source parsing/generation is audited but not formalized.')
    save(args.receipt,receipt)
    failed=False
    log_origins={}
    for source in stages:
        snapshot=closure.dependency_snapshot(source,FORMAL)
        if reusable(old.get(rel(source)),source,snapshot):row=dict(old[rel(source)],reused=True)
        elif args.reuse_only:
            row=dict(path=rel(source),passed=False,exit_code=None,elapsed_seconds=0,
                errors=['no_matching_reusable_receipt'],audited_theorems={},reused=False)
        else:
            row=dict(core.build_one(source,args,env,set()),reused=False)
            original_log=path(row['log'])
            # Keep Windows paths below MAX_PATH even for deeply namespaced
            # proof fragments. The full source path remains in each stage.
            identity=hashlib.sha256(rel(source).encode('utf8')).hexdigest()
            log_name=source.stem[:24]+'-'+identity[:16]+'.log'
            if log_name in log_origins and log_origins[log_name]!=rel(source):
                raise ValueError('Immutable log identity collision')
            log_origins[log_name]=rel(source)
            immutable_log=HERE/'build-logs'/invocation/log_name
            immutable_log.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(original_log,immutable_log)
            row['log']=rel(immutable_log)
            row['log_sha256']=core.digest(immutable_log)
            row['immutable_log_source_path']=rel(source)
            row['immutable_log_identity_sha256']=identity
        row['imported_dependencies']=snapshot
        row['changed_imported_dependencies']=closure.changed_dependencies(snapshot,FORMAL)
        if row['changed_imported_dependencies']or core.digest(args.registry)!=registry_hash:
            row['passed']=False;row['errors'].append('dependency_or_registry_changed_during_build')
        receipt['stages'].append(row);save(args.receipt,receipt)
        print(json.dumps(dict(path=row['path'],passed=row['passed'],reused=row['reused'],seconds=row['elapsed_seconds'])),flush=True)
        if not row['passed']:failed=True;break
    bypath={r['path']:r for r in receipt['stages']if r['passed']}
    for record in records:
        source=record['generated_module'];stage=bypath.get(source)
        reason=None
        if not stage:reason='record_module_not_successfully_built'
        elif record['expected_declaration']not in stage['audited_theorems']:reason='prescribed_semantic_declaration_not_audited'
        elif closure.changed_dependencies(stage['imported_dependencies'],FORMAL):reason='imported_dependency_changed_after_build'
        elif source_binding(record)!=bindings[record['record_id']]:reason='native_source_binding_changed'
        if reason:receipt['unverified_records'].append(dict(record_id=record['record_id'],reason=reason));continue
        dependencies=stage['imported_dependencies']
        if any(dep['path']not in bypath and dep['path']not in attested for dep in dependencies):
            receipt['unverified_records'].append(dict(record_id=record['record_id'],reason='dependency_lacks_successful_source_bound_build'));continue
        receipt['verified_records'].append(dict(record,source_bindings=bindings[record['record_id']],
            proof_stage=stage['path'],proof_source_sha256=stage['source_sha256'],
            proof_olean_path=stage['olean_path'],proof_olean_sha256=stage['olean_sha256'],
            proof_log=stage['log'],proof_log_sha256=stage['log_sha256'],
            audited_declaration=record['expected_declaration'],imported_dependencies=dependencies))
    receipt['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    receipt['status']='passed'if not failed and len(receipt['verified_records'])==len(records)and core.digest(args.registry)==registry_hash else'partial_or_failed'
    save(args.receipt,receipt)
    print(json.dumps(dict(status=receipt['status'],verified_records=len(receipt['verified_records']),requested=len(records),receipt=str(args.receipt))))
    if receipt['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
