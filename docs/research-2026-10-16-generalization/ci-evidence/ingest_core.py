#!/usr/bin/env python3
"""Download and verify a complete Linux core archive for exact-SHA repairs."""
import argparse
from pathlib import Path
import subprocess
import zipfile

import ingest_ci as shared


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='alejandrozu/platonic-packing')
    p.add_argument('--run-id',type=int,required=True);p.add_argument('--commit',required=True)
    p.add_argument('--base-formal',type=Path,required=True)
    p.add_argument('--store',type=Path,default=Path(__file__).resolve().parent)
    args=p.parse_args();base=args.base_formal.resolve();store=args.store.resolve()/f'core-run-{args.run_id}'
    run=shared.gh_json(f'repos/{args.repo}/actions/runs/{args.run_id}')
    if run['head_sha']!=args.commit:raise ValueError('Core workflow commit differs from requested commit')
    shared.write(store/'run.json',run)
    artifacts=shared.gh_json(f'repos/{args.repo}/actions/runs/{args.run_id}/artifacts?per_page=100')['artifacts']
    selected=[a for a in artifacts if a['name']=='lean-complete-core-evidence']
    shared.write(store/'artifacts.json',artifacts)
    if not selected:
        print('No complete Linux core artifact is available yet.');return
    if len(selected)!=1:raise ValueError('Ambiguous complete-core artifacts')
    artifact=selected[0]
    if artifact['workflow_run']['id']!=args.run_id or artifact['workflow_run']['head_sha']!=args.commit:
        raise ValueError('Core artifact run/commit provenance mismatch')
    archive=store/'github-artifact.zip'
    if not archive.is_file():
        tmp=archive.with_suffix('.download')
        with tmp.open('wb')as out:subprocess.run(['gh','api',f'repos/{args.repo}/actions/artifacts/{artifact["id"]}/zip'],stdout=out,check=True)
        tmp.replace(archive)
    digest=artifact.get('digest')
    if digest and digest.startswith('sha256:')and shared.sha(archive)!=digest[7:]:
        raise ValueError('Core artifact GitHub-published digest mismatch')
    shared.write(store/'github-artifact.json',artifact)
    nested=store/'evidence.zip'
    with zipfile.ZipFile(archive)as z:
        entries=shared.zip_entries(z,2_000_000_000)
        matches=[n for n in entries if n=='evidence.zip'or n.endswith('/evidence.zip')]
        if len(matches)!=1:raise ValueError('Require exactly one nested complete core archive')
        data=z.read(matches[0])
        if nested.exists()and nested.read_bytes()!=data:raise ValueError('Core nested archive changed')
        if not nested.exists():nested.write_bytes(data)
    root=store/'validation/formal'
    inventory,relative=shared.extract_evidence(nested,root,2_000_000_000)
    if inventory.get('schema')!='complete-core-evidence-v1'or str(inventory['github_run_id'])!=str(args.run_id)or inventory['github_commit']!=args.commit:
        raise ValueError('Core nested inventory workflow provenance mismatch')
    receipt=shared.read(root/'core-verification.json')
    version=receipt['preflight']['lean_version_output']
    if 'linux'not in version.lower():raise ValueError('Supplement must be a genuine Linux core build')
    validated=shared.verify_core(base,root)
    provenance=dict(schema='verified-linux-core-supplement-v1',run_id=args.run_id,head_sha=args.commit,
        artifact_id=artifact['id'],github_archive=str(archive),github_archive_sha256=shared.sha(archive),
        github_published_digest=digest,evidence_zip=str(nested),evidence_zip_sha256=shared.sha(nested),
        inventory_path=str(root/relative),inventory_sha256=shared.sha(root/relative),
        formal_root=str(root),linux_lean_version=version,core_validation=validated,
        ingestor_sha256=shared.sha(Path(__file__)),core_receipt_sha256=shared.sha(root/'core-verification.json'))
    shared.write(store/'supplement-provenance.json',provenance)
    print(__import__('json').dumps(dict(verified_core_stages=validated['stages'],provenance=str(store/'supplement-provenance.json'))))


if __name__=='__main__':main()
