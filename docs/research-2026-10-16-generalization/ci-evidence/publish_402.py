#!/usr/bin/env python3
"""Replay selected cohorts and bundle portable numeric sources/logs, not objects."""
import argparse
from collections import defaultdict
from pathlib import Path
import hashlib
import zipfile
import evidence_store

import ingest_ci as checked


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-formal',type=Path,required=True)
    p.add_argument('--cohorts',nargs='+',type=Path,required=True)
    p.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent/'published-402')
    p.add_argument('--require-all-402',action='store_true')
    args=p.parse_args();base=args.base_formal.resolve();out=args.output_directory.resolve();out.mkdir(parents=True,exist_ok=True)
    operator_reader_sha256=checked.sha(Path(evidence_store.__file__))
    paper=base.parent;summary=checked.load_validator(base,base);eligible=summary.inventory()
    expected={r['record_id']for r in eligible};chosen={};environments={};cohorts=[];raw_artifacts={};cohort_snapshots={}
    for source in args.cohorts:
        source=source.resolve();data=source.read_bytes();digest=hashlib.sha256(data).hexdigest()
        snapshot=out/'working/cohort-inputs'/(digest+'.json');snapshot.parent.mkdir(parents=True,exist_ok=True)
        snapshot.write_bytes(data);cohort=checked.read(snapshot)
        if cohort['frozen_catalogue_commit']!=checked.FREEZE:raise ValueError('Publication cohort freeze mismatch')
        member='cohort-inputs/'+digest+'.json';cohort_snapshots[member]=snapshot
        cohorts.append(dict(path=source.relative_to(paper).as_posix(),sha256=digest,archive_member=member))
        failures={x['artifact_id']:x['error']for x in cohort.get('artifact_validation_failures',[])}
        for directory in (source.parent/'artifacts').glob('*'):
            archive=directory/'github-artifact.zip'
            if not archive.is_file():continue
            metadata=checked.read(directory/'github-artifact.json');published=metadata.get('digest')
            if published and published.startswith('sha256:')and checked.sha(archive)!=published[7:]:
                raise ValueError('Raw archive differs from GitHub-published digest')
            item=dict(role='packing',run_id=cohort['run_id'],head_sha=cohort['run_head_sha'],artifact_id=metadata['id'],
                artifact_name=metadata['name'],path=archive.relative_to(paper).as_posix(),bytes=archive.stat().st_size,
                sha256=checked.sha(archive),github_published_digest=published,
                proposed_release_asset_name=f'lean-run-{cohort["run_id"]}-artifact-{metadata["id"]}.zip',
                current_validation_failure=failures.get(metadata['id']))
            receipt=directory/'validation/formal/core-verification.json'
            if receipt.is_file():item['recorded_linux_toolchain']=checked.read(receipt)['preflight']['lean_version_output']
            raw_artifacts[(cohort['run_id'],metadata['id'])]=item
        for provenance in cohort['validated_shards']:
            ident=f'run-{provenance["run_id"]}-artifact-{provenance["artifact_id"]}'
            root=Path(provenance['validation_formal_root']).resolve()
            archive_root=source.parent/'artifacts'/str(provenance['artifact_id'])
            for name,key in [('github-artifact.zip','github_archive_sha256'),('evidence.zip','evidence_zip_sha256')]:
                if name=='evidence.zip'and provenance.get('storage_mode')=='zip-streamed-objects':
                    if provenance['object_store']['nested_sha256']!=provenance[key]:raise ValueError('Streamed nested provenance changed')
                elif checked.sha(archive_root/name)!=provenance[key]:raise ValueError('Preserved original artifact changed')
            original=Path(provenance['validation_path'])
            if checked.sha(original)!=provenance['validation_sha256']:raise ValueError('Original independent validation changed')
            original_result=checked.read(original)
            receipts=[checked.under(root,item['path'])for item in original_result['receipt_inputs']]
            for path,item in zip(receipts,original_result['receipt_inputs']):
                if checked.sha(path)!=item['sha256']:raise ValueError('Original accepted receipt changed')
            with evidence_store.reopen(provenance)as root:
                checked.verify_core(base,root)
                raw_artifacts[(provenance['run_id'],provenance['artifact_id'])]['recorded_linux_toolchain']=checked.read(root/'core-verification.json')['preflight']['lean_version_output']
                # All original receipt rows and their complete imported objects are
                # checked again now; the publication does not trust a stale count.
                replay=checked.replay(base,root,receipts,out/'working'/ident/'all-replay.json')
                if {r['record_id']for r in replay['verified_records']}!={r['record_id']for r in original_result['verified_records']}:
                    raise ValueError('Current independent replay changed accepted record scope')
            environments[ident]=dict(root=root,archive_root=archive_root,provenance=provenance)
            for record in replay['verified_records']:
                if record['record_id']not in expected:raise ValueError('Unexpected source record in publication')
                rank=(provenance['artifact_created_at'],provenance['run_id'],provenance['artifact_id'])
                if record['record_id']not in chosen or rank>chosen[record['record_id']][0]:
                    chosen[record['record_id']]=(rank,ident,record)
    groups=defaultdict(list)
    for _,ident,record in chosen.values():groups[ident].append(record)
    files=dict(cohort_snapshots);published=[];environment_rows=[]
    def add(root,ident,value):
        if not value:return
        path=checked.under(root,value)
        if path.suffix=='.olean':return
        if not path.is_file():raise ValueError('Selected source/log/receipt missing: '+value)
        name=f'environments/{ident}/formal/{value}'
        if name in files and checked.sha(files[name])!=checked.sha(path):raise ValueError('Publication namespace collision')
        files[name]=path
    for ident,records in sorted(groups.items()):
        env=environments[ident];root=env['root'];prov=env['provenance']
        receipt_paths=sorted({r['evidence']['receipt_path']for r in records})
        replay_path=out/'working'/ident/'selected-replay.json'
        with evidence_store.reopen(prov)as view:
            fresh=checked.replay(base,view,[checked.under(view,x)for x in receipt_paths],replay_path)
        if {r['record_id']for r in fresh['verified_records']}!={r['record_id']for r in records}:
            raise ValueError('Selected receipt replay has unexpected records')
        files[f'environments/{ident}/independent-validation.json']=replay_path
        core=checked.read(root/'core-verification.json');add(root,ident,'core-verification.json')
        for row in core['results']:
            for key in ['path','log']:add(root,ident,row[key])
        generic=prov.get('generic_extension_validation')
        if generic:
            add(root,ident,generic['path'])
            for row in checked.read(root/generic['path'])['results']:
                for key in ['path','log']:add(root,ident,row[key])
                for dependency in row['imported_dependencies']:add(root,ident,dependency['path'])
        for record in fresh['verified_records']:
            e=record['evidence']
            for key in ['generated_source_path','log_path','receipt_path','plan_manifest_path']:add(root,ident,e.get(key))
            for key in ['dependencies','steps','extension_dependencies']:
                for row in e.get(key,[]):
                    add(root,ident,row.get('path'));add(root,ident,row.get('log'))
            compact={k:e[k]for k in ['module','generated_source_path','generated_source_sha256','olean_path','olean_sha256',
                'log_path','log_sha256','receipt_path','receipt_sha256','plan_manifest_path','plan_manifest_sha256','audited_theorems','axioms']if k in e}
            compact.update(environment_id=ident,proof_step_count=len(e.get('steps',[])),
                complete_validation_member=f'environments/{ident}/independent-validation.json')
            published.append(dict(record,evidence=compact))
        supplement=prov.get('exact_sha_core_supplement')
        if supplement:
            portable_supplement={key:supplement[key]for key in ['schema','source_provenance_sha256','source_run_id',
                'source_head_sha','source_artifact_id','raw_original_archive_changed','boundary']}
            portable_supplement['files']=[{key:item[key]for key in ['path','sha256','was_missing','older_recorded_sha256']}for item in supplement['files']]
            portable_supplement['donor_raw_artifact_index_key']=f'run-{supplement["source_run_id"]}-artifact-{supplement["source_artifact_id"]}'
            portable_path=out/'working'/ident/'portable-core-supplement-provenance.json';checked.write(portable_path,portable_supplement)
            files[f'environments/{ident}/core-supplement-provenance.json']=portable_path
            donor=checked.read(Path(supplement['source_provenance_path']));archive=Path(donor['github_archive'])
            if checked.sha(archive)!=donor['github_archive_sha256']:raise ValueError('Core supplement raw archive changed')
            raw_artifacts[(donor['run_id'],donor['artifact_id'])]=dict(role='complete_core_supplement',run_id=donor['run_id'],
                head_sha=donor['head_sha'],artifact_id=donor['artifact_id'],path=archive.relative_to(paper).as_posix(),
                bytes=archive.stat().st_size,sha256=donor['github_archive_sha256'],github_published_digest=donor.get('github_published_digest'),
                recorded_linux_toolchain=donor['linux_lean_version'],
                proposed_release_asset_name=f'lean-core-run-{donor["run_id"]}-artifact-{donor["artifact_id"]}.zip',
                supplement_provenance_member=f'environments/{ident}/core-supplement-provenance.json')
        environment_rows.append(dict(environment_id=ident,formal_prefix=f'environments/{ident}/formal',
            run_id=prov['run_id'],run_head_sha=prov['run_head_sha'],artifact_id=prov['artifact_id'],shard_index=prov['shard_index'],
            github_archive_path=(env['archive_root']/'github-artifact.zip').relative_to(paper).as_posix(),
            github_archive_sha256=prov['github_archive_sha256'],evidence_zip_path=None if prov.get('storage_mode')=='zip-streamed-objects'else(env['archive_root']/'evidence.zip').relative_to(paper).as_posix(),
            storage_mode=prov.get('storage_mode','extracted'),object_store=evidence_store.public_descriptor(prov),
            evidence_zip_sha256=prov['evidence_zip_sha256'],core_validation=prov['core_validation'],
            exact_sha_core_supplement=portable_supplement if supplement else None))
    archive=out/'proof-sources-and-logs.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for name,path in sorted(files.items()):z.write(path,name)
    manifest=dict(schema='lean-catalogue-source-log-bundle-v1',archive=archive.name,archive_sha256=checked.sha(archive),
        files=[dict(path=name,bytes=path.stat().st_size,sha256=checked.sha(path))for name,path in sorted(files.items())])
    manifest_path=out/'proof-sources-and-logs-manifest.json';checked.write(manifest_path,manifest)
    for item in raw_artifacts.values():
        item['permanent_download_url']='https://github.com/alejandrozu/platonic-packing/releases/download/lean-frozen-catalogue-2026-10-16/'+item['proposed_release_asset_name']
        item['selected_record_ids']=sorted(r['record_id']for r in published if
            (item['run_id'],item['artifact_id'])==(environments[r['evidence']['environment_id']]['provenance']['run_id'],
                environments[r['evidence']['environment_id']]['provenance']['artifact_id']))
    raw_path=out/'raw-artifacts.json';checked.write(raw_path,dict(schema='preserved-lean-artifact-index-v1',
        artifacts=sorted(raw_artifacts.values(),key=lambda r:(r['run_id'],r['artifact_id'])),
        policy='Preserve exact raw ZIP bytes as permanent GitHub release assets; no release upload is performed by this exporter. '
            'Failed/superseded artifacts are indexed without being counted as verified records.'))
    published.sort(key=lambda r:r['record_id'])
    if checked.sha(Path(evidence_store.__file__))!=operator_reader_sha256:
        raise ValueError('Operator ZIP reader changed during publication replay')
    report=dict(schema='portable-source-bound-lean-catalogue-v1',cohort_id='rational-402',expected_record_count=402,
        frozen_catalogue_commit=checked.FREEZE,
        exporter_sha256=checked.sha(Path(__file__)),source_cohorts=cohorts,environments=environment_rows,
        operator_reader_sha256=operator_reader_sha256,
        verified_records=published,verified_totals=summary.totals(published),eligible_totals=summary.totals(eligible),
        missing_record_ids=sorted(expected-set(chosen)),complete_402=set(chosen)==expected,
        proof_source_bundle=archive.name,proof_source_bundle_sha256=checked.sha(archive),
        proof_source_manifest=manifest_path.name,proof_source_manifest_sha256=checked.sha(manifest_path),
        raw_artifact_index=raw_path.name,raw_artifact_index_sha256=checked.sha(raw_path),
        reproduction='Extract one environment under its named directory; supply the shared frozen catalogue input/witness tree '
            'and pinned Lean/mathlib, rebuild the plaintext generic library then its archived numeric modules. '
            'Each environment retains its own core/generic receipts and logs. Linux proof objects remain in the immutable raw artifact ZIPs only.',
        trust_boundary='Kernel certificate verification for source-linked coordinate hulls. Parsing/transcription and '
            'named-solid classification including edge-unit conventions remain explicit external boundaries.')
    checked.write(out/'verified-catalogue.json',report)
    print(__import__('json').dumps(dict(verified=len(published),eligible=402,complete_402=report['complete_402'],report=str(out/'verified-catalogue.json'),
        archive=str(archive),files=len(files))))
    if args.require_all_402 and not report['complete_402']:raise SystemExit(1)


if __name__=='__main__':main()
