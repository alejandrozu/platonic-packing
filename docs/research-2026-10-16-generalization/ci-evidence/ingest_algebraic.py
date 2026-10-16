#!/usr/bin/env python3
"""Preserve and independently validate combined 3D85/ND45 Linux artifacts."""
import argparse
from collections import Counter
from pathlib import Path
import os
import re
import subprocess
import zipfile
import shutil
import evidence_store

import ingest_ci as shared
import validate_algebraic as validator

PATTERN=r'lean-algebraic-(3d85|nd45)-shard-(\d+)'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='alejandrozu/platonic-packing')
    p.add_argument('--run-id',type=int,required=True);p.add_argument('--commit',required=True)
    p.add_argument('--base-formal',type=Path,required=True)
    p.add_argument('--store',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--fetch',action='store_true');p.add_argument('--core-supplement',type=Path)
    p.add_argument('--stream-objects',action='store_true')
    p.add_argument('--bounded-nonobject-writes',action='store_true')
    p.add_argument('--download-artifact-ids',nargs='+',type=int)
    p.add_argument('--min-free-mb',type=int,default=512)
    p.add_argument('--require-complete',action='store_true')
    args=p.parse_args()
    if args.min_free_mb<0:p.error('min-free-mb must be nonnegative')
    shared._MIN_FREE_BYTES=args.min_free_mb*1024**2
    shared._BOUNDED_WRITES=args.bounded_nonobject_writes
    operator_reader_sha256=shared.sha(Path(evidence_store.__file__))
    base=args.base_formal.resolve();store=args.store.resolve()/f'algebraic-run-{args.run_id}';store.mkdir(parents=True,exist_ok=True)
    if args.fetch:
        run=shared.gh_json(f'repos/{args.repo}/actions/runs/{args.run_id}')
        if run['head_sha']!=args.commit:raise ValueError('Combined workflow commit mismatch')
        artifacts=[];page=1
        while True:
            response=shared.gh_json(f'repos/{args.repo}/actions/runs/{args.run_id}/artifacts?per_page=100&page={page}')
            artifacts+=response['artifacts']
            if len(response['artifacts'])<100:break
            page+=1
        shared.write(store/'run.json',run);shared.write(store/'artifacts.json',artifacts)
        requested=set(args.download_artifact_ids or [])
        available={a['id']for a in artifacts if re.fullmatch(PATTERN,a['name'])}
        if requested-available:raise ValueError('Requested algebraic artifacts absent from approved run')
        for artifact in artifacts:
            if not re.fullmatch(PATTERN,artifact['name']):continue
            if artifact['workflow_run']['id']!=args.run_id or artifact['workflow_run']['head_sha']!=args.commit:
                raise ValueError('Combined artifact workflow provenance mismatch')
            directory=store/'artifacts'/str(artifact['id']);directory.mkdir(parents=True,exist_ok=True)
            shared.write(directory/'github-artifact.json',artifact);archive=directory/'github-artifact.zip'
            if not archive.is_file():
                if requested and artifact['id']not in requested:continue
                if shutil.disk_usage(store).free<artifact['size_in_bytes']+args.min_free_mb*1024**2:
                    raise ValueError('Insufficient free space for raw artifact plus headroom')
                tmp=archive.with_suffix('.download')
                with tmp.open('wb')as out:subprocess.run(['gh','api',f'repos/{args.repo}/actions/artifacts/{artifact["id"]}/zip'],stdout=out,check=True)
                tmp.replace(archive)
            shared.write(directory/'download.json',dict(run_id=args.run_id,head_sha=args.commit,artifact_id=artifact['id'],sha256=shared.sha(archive)))
    else:run,artifacts=shared.read(store/'run.json'),shared.read(store/'artifacts.json')
    if run['id']!=args.run_id or run['head_sha']!=args.commit:raise ValueError('Stored combined workflow provenance mismatch')
    accepted={'3d85':[],'nd45':[]};failures={'3d85':[],'nd45':[]};unfetched=[]
    for artifact in artifacts:
        match=re.fullmatch(PATTERN,artifact['name'])
        if not match:continue
        objects=None;context=None
        kind,index=match.group(1),int(match.group(2));directory=store/'artifacts'/str(artifact['id'])
        if not(directory/'github-artifact.zip').is_file():unfetched.append(artifact['id']);continue
        try:
            if artifact['workflow_run']['id']!=args.run_id or artifact['workflow_run']['head_sha']!=args.commit:
                raise ValueError('Stored artifact run/commit mismatch')
            archive=directory/'github-artifact.zip';download=shared.read(directory/'download.json')
            if shared.sha(archive)!=download['sha256']:raise ValueError('Downloaded combined artifact changed')
            digest=artifact.get('digest')
            if digest and digest.startswith('sha256:')and shared.sha(archive)!=digest[7:]:raise ValueError('GitHub artifact digest mismatch')
            root=(Path.home()/'Documents/Codex/lean-ci'/str(artifact['id'])/'formal')if os.name=='nt'else directory/'validation/formal'
            root=root.resolve()
            objects=None
            if args.stream_objects:
                objects=evidence_store.EvidenceStore(archive,root,download['sha256'])
                inventory,relative=objects.validate(min_free_bytes=args.min_free_mb*1024**2,
                    bounded_writes=args.bounded_nonobject_writes)
                context=objects.activate()
                root=context.__enter__()
                supplement=shared.supplement_missing_probes(base,root,args.core_supplement)
            else:
                nested=directory/'evidence.zip'
                with zipfile.ZipFile(archive)as z:
                    entries=shared.zip_entries(z,10_000_000_000)
                    names=[n for n in entries if n=='evidence.zip'or n.endswith('/evidence.zip')]
                    if len(names)!=1:raise ValueError('Expected exactly one nested combined evidence archive')
                    data=z.read(names[0])
                    if nested.exists()and nested.read_bytes()!=data:raise ValueError('Nested combined evidence changed')
                    if not nested.exists():nested.write_bytes(data)
                # Deep generated module names exceed Windows' legacy 260-character
                # limit beneath the long paper directory. Raw ZIPs/provenance stay
                # together; only the reproducible isolated validation overlay uses
                # this short, persistent workspace path on Windows.
                root=(Path.home()/'Documents/Codex/lean-ci'/str(artifact['id'])/'formal')if os.name=='nt'else directory/'validation/formal'
                root=root.resolve();inventory,relative=shared.extract_evidence(nested,root,10_000_000_000)
                supplement=shared.supplement_missing_probes(base,root,args.core_supplement)
            core=shared.verify_core(base,root)
            if 'linux'not in shared.read(root/'core-verification.json')['preflight']['lean_version_output'].lower():
                raise ValueError('Remote combined evidence is not a Linux build')
            result=validator.validate(base,root,kind)
            if result['shard_index']!=index or str(result['github_run_id'])!=str(args.run_id)or result['github_commit']!=args.commit:
                raise ValueError('Combined worker status shard/run/commit mismatch')
            output=directory/'independent-validation.json';shared.write(output,result)
            provenance=dict(run_id=args.run_id,run_head_sha=args.commit,artifact_id=artifact['id'],artifact_name=artifact['name'],
                artifact_created_at=artifact['created_at'],cohort='algebraic-'+kind,shard_index=index,shard_count=result['shard_count'],
                validation_formal_root=str(root),validation_path=str(output),validation_sha256=shared.sha(output),
                github_archive_sha256=shared.sha(archive),evidence_zip_sha256=objects.nested_sha256 if objects else shared.sha(nested),
                evidence_inventory_path=relative,evidence_inventory_sha256=shared.sha(root/relative),core_validation=core,
                exact_sha_core_supplement=supplement,verified_records=result['verified_count'])
            if objects:
                context.__exit__(None,None,None);context=None
                provenance.update(storage_mode='zip-streamed-objects',object_store=objects.descriptor())
            shared.write(directory/'validation-provenance.json',provenance);accepted[kind].append((provenance,result))
        except Exception as exc:failures[kind].append(dict(artifact_id=artifact['id'],error=repr(exc)))
        finally:
            if context is not None:context.__exit__(None,None,None)
            if objects is not None:objects.close()
    all_complete=True
    if shared.sha(Path(evidence_store.__file__))!=operator_reader_sha256:
        raise ValueError('Operator ZIP reader changed during algebraic replay')
    for kind in ['3d85','nd45']:
        registry='generated3d-registry.json'if kind=='3d85'else'generated-nd-pilots-registry.json'
        expected={r['record_id']for r in shared.read(base/'catalogue/algebraic'/registry)['records']}
        latest={}
        for provenance,result in accepted[kind]:
            rank=(provenance['verified_records'],provenance['artifact_created_at'],provenance['artifact_id']);index=provenance['shard_index']
            if index not in latest or rank>latest[index][0]:latest[index]=(rank,provenance,result)
        rows=[dict(row,artifact_provenance=provenance)for _,provenance,result in latest.values()for row in result['verified_records']]
        counts=Counter(r['record_id']for r in rows)
        if any(n!=1 for n in counts.values())or not set(counts)<=expected:raise ValueError('Duplicate/unexpected algebraic pilot source ID')
        complete=set(counts)==expected;all_complete&=complete
        report=dict(schema='github-algebraic-cohort-ingestion-v1',cohort_id='algebraic-'+kind,expected_record_count=len(expected),
            run_id=args.run_id,run_head_sha=args.commit,frozen_catalogue_commit=shared.FREEZE,
            ingestor_sha256=shared.sha(Path(__file__)),validator_sha256=shared.sha(Path(validator.__file__)),
            operator_reader_sha256=operator_reader_sha256,
            artifact_validation_failures=failures[kind],not_downloaded_artifact_ids=unfetched,validated_shards=[x[1]for x in latest.values()],
            verified_records=shared.compact_rows(rows),record_evidence_storage='pinned-per-artifact-independent-validation-v1',
            missing_record_ids=sorted(expected-set(counts)),complete=complete)
        shared.write(store/('cohort-validation-'+kind+'.json'),report)
        print(__import__('json').dumps(dict(cohort=kind,verified=len(rows),eligible=len(expected),complete=complete,failed_artifacts=len(failures[kind]))))
    if args.require_complete and not all_complete:raise SystemExit(1)


if __name__=='__main__':main()
