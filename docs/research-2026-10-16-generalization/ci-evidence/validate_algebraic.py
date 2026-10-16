#!/usr/bin/env python3
"""Read-only replay of an extracted 85-pilot CI evidence tree.

No compiler or artifact-supplied Python is executed. Import the approved local
builder, then redirect its file readers to the isolated evidence tree. Linux
objects remain isolated from the working Windows objects.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import ingest_ci as digest_support
import evidence_store


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def under(root,name):
    p=(root/name).resolve();p.relative_to(root);return p


@contextmanager
def isolated_approved_modules(base):
    """Never reuse a generator imported from another approved asset version."""
    names={p.stem for folder in [base,base/'catalogue',base/'catalogue/algebraic']
        for p in folder.glob('*.py')}
    previous={name:sys.modules.pop(name)for name in names if name in sys.modules}
    try:
        yield
    finally:
        for name in names:
            sys.modules.pop(name,None)
        sys.modules.update(previous)


@contextmanager
def trusted_builder(base,root,kind='3d85'):
    previous_path=list(sys.path)
    try:
        with isolated_approved_modules(base):
            with bound_builder(base,root,kind)as verifier:
                yield verifier
    finally:
        # Includes an import-time error before the inner binding context has
        # reached its yield; the next approved-version replay stays isolated.
        sys.path[:]=previous_path


@contextmanager
def bound_builder(base,root,kind='3d85'):
    root=evidence_store.EvidencePath(root)
    old_sys_path=list(sys.path)
    sys.path[:0]=[str(base),str(base/'catalogue/algebraic'),str(base/'catalogue')]
    import run_verified as verifier
    verifier.closure.Path=evidence_store.EvidencePath
    changes=[]
    for module,key,value in [(verifier,'FORMAL',root),(verifier,'HERE',root/'catalogue/algebraic'),
        (verifier.core,'HERE',root),(verifier.record_generator,'FORMAL',root),
        (verifier.record_generator,'HERE',root/'catalogue/algebraic')]:
        changes.append((module,key,getattr(module,key)));setattr(module,key,value)
    if kind=='3d85':
        import run_verified_fragmented_3d as fragmented3d
        import generate_fragmented_3d_pilots as fragment_generator3d
        for module in [fragmented3d,fragment_generator3d]:
            for key,value in [('FORMAL',root),('HERE',root/'catalogue/algebraic')]:
                if hasattr(module,key):
                    changes.append((module,key,getattr(module,key)));setattr(module,key,value)
        changes.append((fragmented3d,'__file__',fragmented3d.__file__))
        fragmented3d.__file__=str(root/'catalogue/algebraic/run_verified_fragmented_3d.py')
        changes.append((fragment_generator3d,'__file__',fragment_generator3d.__file__))
        fragment_generator3d.__file__=str(root/'catalogue/algebraic/generate_fragmented_3d_pilots.py')
    else:
        # Native source binding imports this helper dynamically. Preload the
        # approved implementation before any redirected artifact path is used.
        import export_nd
        import run_verified_nd as native
        import run_verified_fragmented_nd as fragmented
        import generate_fragmented_nd_pilots as fragment_generator
        import generate_nd_pilots as nd_generator
        for module in [native,fragmented,fragment_generator,nd_generator]:
            for key,value in [('FORMAL',root),('HERE',root/'catalogue/algebraic')]:
                if hasattr(module,key):
                    changes.append((module,key,getattr(module,key)));setattr(module,key,value)
        for module,name in [(native,'run_verified_nd.py'),(fragmented,'run_verified_fragmented_nd.py'),
                            (fragment_generator,'generate_fragmented_nd_pilots.py')]:
            changes.append((module,'__file__',module.__file__))
            module.__file__=str(root/'catalogue/algebraic'/name)
    try:yield verifier
    finally:
        for module,key,value in reversed(changes):setattr(module,key,value)
        sys.path[:]=old_sys_path


def validate(base,root,kind='3d85',allow_local_pilot=False):
    root=evidence_store.EvidencePath(root)
    manifest_name='ci-pilot-assets.json'if kind=='3d85'else'ci-nd45-assets.json'
    registry_name='generated3d-registry.json'if kind=='3d85'else'generated-nd-pilots-registry.json'
    manifest=read(base/'catalogue/algebraic'/manifest_name)
    if read(root/'catalogue/algebraic'/manifest_name)!=manifest:
        raise ValueError('Artifact publication manifest differs from the approved 85-pilot manifest')
    for row in manifest['files']:
        source=under(base,row['path']);artifact=under(root,row['path'])
        if not source.is_file()or not artifact.is_file()or sha(source)!=row['sha256']or sha(artifact)!=row['sha256']or artifact.stat().st_size!=row['bytes']:
            raise ValueError('Artifact differs from approved publication source: '+row['path'])
    statuses=sorted((root/'catalogue/algebraic'/('ci'if kind=='3d85'else'ci-nd45')).glob('shard-*/status.json'))
    if len(statuses)!=1:raise ValueError('Require one isolated shard status per evidence tree')
    status=read(statuses[0]);accepted=[];failed=[]
    registry=read(root/'catalogue/algebraic'/registry_name)
    records={r['record_id']:r for r in registry['records']}
    with trusted_builder(base,root,kind)as verifier, digest_support.digest_memoization(
            [(verifier.core,'digest'),(sys.modules[__name__],'sha')])as digest_audit:
        if kind=='3d85':
            import run_ci_pilots as worker
            import run_verified_fragmented_3d as fragmented
            plan=worker.shard_plan(worker.catalogue(registry),8);count=8
            binding=fragmented.source_binding
        else:
            import run_ci_nd45 as worker
            import run_verified_fragmented_nd as fragmented
            plan=worker.plan(registry,12);count=12
            binding=fragmented.source_binding
        index=status['shard_index']
        if status['shard_count']!=count or not 0<=index<count or read(statuses[0].parent/'shard-plan.json')!=plan:
            raise ValueError('Artifact does not contain the approved deterministic eight-shard plan')
        assigned={r['record_id']for r in plan['shards'][index]['records']}
        actual=[r['record_id']for r in status['records']]
        local_pilot=allow_local_pilot and status.get('github_run_id')is None and status.get('github_commit')is None
        if len(set(actual))!=len(actual)or not set(actual)<=assigned or status['total_selected']!=(len(actual)if local_pilot else len(assigned)):
            raise ValueError('Artifact includes duplicate/out-of-partition records or a different declared selection')
        core=verifier.approved_core()
        for row in status['records']:
            if not row.get('passed'):
                failed.append(dict(record_id=row['record_id'],reason='worker_did_not_report_success'));continue
            receipt_path=under(root,row['receipt']);receipt=read(receipt_path)
            if sha(receipt_path)!=row['receipt_sha256']or receipt['status']!='passed':
                raise ValueError('Passed worker receipt is missing, changed or incomplete')
            for key,source in [('builder_sha256','catalogue/algebraic/run_verified.py'),
                ('dependency_helper_sha256','verify_extensions.py'),('core_builder_sha256','verify_core.py'),
                ('core_receipt_sha256','core-verification.json')]:
                if receipt[key]!=sha(root/source):raise ValueError('Receipt implementation/environment changed: '+key)
            ident=row['record_id'];record=records[ident]
            extra=['PackingCertificates/Algebraic/Regression.lean']if kind=='3d85'else[
                'PackingCertificates/Algebraic/RangeAssembly.lean',
                'PackingCertificates/Algebraic/RationalEncoding.lean']
            if receipt['requested_record_ids']!=[ident]or receipt.get('requested_extra_modules',[])!=extra:
                raise ValueError('Receipt has unexpected scope or omits prescribed helper proofs')
            if sha(under(root,receipt['registry_path']))!=receipt['registry_sha256']:
                raise ValueError('Receipt registry changed')
            fragments=read(under(root,receipt['registry_path']))
            if len(fragments['records'])!=1 or fragments['original_registry_sha256']!=sha(root/'catalogue/algebraic'/registry_name):
                raise ValueError('Fragment registry is not source-bound to the authoritative pilot registry')
            record=fragments['records'][0]
            if record['original_registry_row']!=records[ident]or receipt.get('fragment_semantic_audits_passed')is not True:
                raise ValueError('Fragment registry identity or semantic audit failed')
            wrapper='run_verified_fragmented_3d.py'if kind=='3d85'else'run_verified_fragmented_nd.py'
            if receipt['fragment_builder_sha256']!=sha(base/'catalogue/algebraic'/wrapper):
                raise ValueError('Fragment wrapper implementation changed')
            bindings=binding(record)
            sources=[root/x for x in extra]+[root/record['generated_module']]
            expected=list(map(verifier.rel,verifier.build_order(sources,core)))
            if [s['path']for s in receipt['stages']]!=expected:
                raise ValueError('Receipt omits or duplicates a required transitive proof stage')
            for stage in receipt['stages']:
                source=under(root,stage['path']);snapshot=verifier.closure.dependency_snapshot(source,root)
                if not verifier.reusable(stage,source,snapshot):
                    raise ValueError('Stage no longer has matching kernel/source/object/log/import evidence: '+stage['path'])
            verified=receipt['verified_records']
            if len(verified)!=1 or verified[0]['record_id']!=ident or verified[0]['source_bindings']!=bindings:
                raise ValueError('Published verified row disagrees with independently reconstructed native source bindings')
            proof=next(s for s in receipt['stages']if s['path']==record['generated_module'])
            if record['expected_declaration']not in proof['audited_theorems']:
                raise ValueError('Packing semantic declaration was not audited')
            bypath={s['path']:s for s in receipt['stages']}
            for entry in record['fragmentation']['files']:
                if any(name not in bypath[entry['path']]['audited_theorems']for name in entry['expected_audits']):
                    raise ValueError('Prescribed fragment soundness theorem not audited')
            if kind=='nd45':
                if any(name not in proof['audited_theorems']for name in record['expected_mu_declarations']):
                    raise ValueError('Native algebraic scale/literal binding not audited')
            evidence=dict(module=record['expected_declaration'].rsplit('.',1)[0],generated_source_path=proof['path'],
                generated_source_sha256=proof['source_sha256'],olean_path=proof['olean_path'],olean_sha256=proof['olean_sha256'],
                log_path=proof['log'],log_sha256=proof['log_sha256'],receipt_path=row['receipt'],receipt_sha256=sha(receipt_path),
                plan_manifest_path=receipt['registry_path'],plan_manifest_sha256=receipt['registry_sha256'],
                audited_theorems=proof['audited_theorems'],axioms=proof['axioms'],steps=receipt['stages'],
                dependencies=[],extension_dependencies=proof['imported_dependencies'])
            accepted.append(dict(record,evidence=evidence,source_bindings=bindings,receipt_path=row['receipt'],receipt_sha256=sha(receipt_path),
                proof_source_sha256=proof['source_sha256'],proof_olean_path=proof['olean_path'],proof_olean_sha256=proof['olean_sha256'],
                proof_log=proof['log'],proof_log_sha256=proof['log_sha256'],imported_dependencies=proof['imported_dependencies'],
                audited_declaration=record['expected_declaration']))
    if len({r['record_id']for r in accepted})!=len(accepted)or len(accepted)!=status['passed_records']:
        raise ValueError('Worker passed count disagrees with independently validated records')
    return dict(schema='independent-algebraic-pilot-replay-v1',formal_root=str(root),
        frozen_catalogue_commit='1abc63218db34cea95802aeb3b6d4a6b6fe1c61b',
        receipt_inputs=[dict(path=r['receipt_path'],sha256=r['receipt_sha256'])for r in accepted],
        cohort_id='algebraic-'+kind,expected_record_count=85 if kind=='3d85'else 45,scope_mode='explicit_local_pilot'if local_pilot else'fixed_full_shard',
        validator_sha256=sha(Path(__file__)),publication_manifest_sha256=sha(base/'catalogue/algebraic'/manifest_name),
        digest_audit=digest_audit.report(),
        shard_index=status['shard_index'],shard_count=status['shard_count'],github_run_id=status.get('github_run_id'),
        github_commit=status.get('github_commit'),verified_records=accepted,unverified_records=failed,
        verified_count=len(accepted),trust_boundary='Exact source/geometry/render and kernel build receipt replay; '
            'no compiler rerun and no artifact-supplied Python execution. Template classification and parser correctness remain external.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-formal',type=Path,required=True);p.add_argument('--formal-root',type=Path,required=True)
    p.add_argument('--kind',choices=['3d85','nd45'],default='3d85')
    p.add_argument('--allow-local-pilot',action='store_true',help='Permit a local non-GitHub explicit subset; never used for remote cohort acceptance')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=validate(args.base_formal.resolve(),args.formal_root.resolve(),args.kind,args.allow_local_pilot)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(verified=result['verified_count'],unverified=len(result['unverified_records']),output=str(args.output))))


if __name__=='__main__':main()
