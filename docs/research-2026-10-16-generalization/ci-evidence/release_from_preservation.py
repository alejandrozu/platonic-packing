#!/usr/bin/env python3
"""Promote exact remotely preserved proof ZIPs after the final main merge.

The caller pins the preservation artifact ID and its GitHub-published SHA256.
The committed publication provenance independently pins that artifact's run/head.
Default behavior downloads/verifies and writes a release plan. Only --execute
calls the reviewed release uploader. No existing differing file is replaced.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import zipfile

REPOSITORY = 'alejandrozu/platonic-packing'
TAG = 'lean-frozen-catalogue-2026-10-16'
ARTIFACT_NAME = 'lean-532-original-raw-evidence'
COHORTS = ['published-402', 'published-85', 'published-45']
METADATA = ['raw-preservation-index.json', 'remote-aggregation-provenance.json',
            'operator-source-hashes.json']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def api(endpoint):
    result = subprocess.run(['gh', 'api', endpoint], check=True,
        capture_output=True, text=True, encoding='utf8')
    return json.loads(result.stdout)


def require_current_main(commit):
    ref = api(f'repos/{REPOSITORY}/git/ref/heads/main')
    if ref['object']['type'] != 'commit' or ref['object']['sha'] != commit:
        raise ValueError('The supplied final commit is no longer the current main head')
    return ref


def restore_exact(archive, paper, rows, metadata, safe_path, min_free_bytes):
    """Extract a closed allowlist; never invoke artifact code or extractall."""
    expected = {r['path']: (r['bytes'], r['sha256']) for r in rows}
    if len(expected) != 33:
        raise ValueError('Expected exactly 33 distinct raw archive paths')
    for name in metadata:
        original = safe_path(paper, 'ci-evidence/' + name)
        expected[name] = (original.stat().st_size, sha(original))
    with zipfile.ZipFile(archive) as z:
        found = {}; folded = set()
        for info in z.infolist():
            name = info.filename
            directory = info.is_dir()
            normalized = name[:-1] if directory else name
            safe_path(paper, normalized)
            mode = (info.external_attr >> 16) & 0xffff
            if stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in {0, stat.S_IFREG, stat.S_IFDIR}:
                raise ValueError('Aliases or special files are not preservation evidence')
            if name.casefold() in folded:
                raise ValueError('Duplicate or case-colliding preservation ZIP member')
            folded.add(name.casefold())
            if directory:
                if not any(p.startswith(normalized + '/') for p in expected):
                    raise ValueError('Unexpected preservation ZIP directory')
                continue
            if name not in expected or info.file_size != expected[name][0]:
                raise ValueError('Unexpected preservation ZIP member or byte count')
            found[name] = info
        if set(found) != set(expected):
            raise ValueError('Preservation ZIP does not contain the exact 33 raw ZIPs and 3 metadata files')
        for name, info in found.items():
            size, digest = expected[name]
            # Metadata is compared with committed originals, never overwritten.
            output = None
            if name not in metadata:
                destination = safe_path(paper, name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    if destination.stat().st_size != size or sha(destination) != digest:
                        raise ValueError('Existing raw archive differs; refusing replacement')
                else:
                    if shutil.disk_usage(paper).free < size + min_free_bytes:
                        raise ValueError('Insufficient headroom for the next original raw ZIP')
                    output = destination.open('xb')
            h = hashlib.sha256(); total = 0
            try:
                with z.open(info) as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        total += len(block)
                        if total > size:
                            raise ValueError('Preservation member exceeds its exact byte count')
                        h.update(block)
                        if output is not None:
                            if shutil.disk_usage(paper).free < len(block) + min_free_bytes:
                                raise ValueError('Required free-space headroom would be crossed')
                            output.write(block)
            finally:
                if output is not None:
                    output.close()
            if total != size or h.hexdigest() != digest:
                raise ValueError('Restored preservation member SHA256 differs')
    for row in rows:
        path = safe_path(paper, row['path'])
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Final original raw ZIP rehash failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paper', type=Path, required=True)
    parser.add_argument('--checkout', type=Path, required=True)
    parser.add_argument('--final-main-commit', required=True)
    parser.add_argument('--preservation-artifact-id', type=int, required=True)
    parser.add_argument('--preservation-artifact-sha256', required=True)
    parser.add_argument('--output-directory', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.final_main_commit):
        parser.error('final-main-commit must be an exact lowercase 40-hex SHA')
    if (args.preservation_artifact_id <= 0 or
            not re.fullmatch(r'[0-9a-f]{64}', args.preservation_artifact_sha256)):
        parser.error('Preservation artifact needs a positive ID and exact 64-hex SHA256')
    paper = args.paper.resolve(); checkout = args.checkout.resolve()
    paper.relative_to(checkout)
    actual = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'],
        text=True).strip()
    if actual != args.final_main_commit:
        raise ValueError('Checked-out publication differs from the provided final main commit')
    first_main = require_current_main(args.final_main_commit)
    ci = paper / 'ci-evidence'
    work = (args.output_directory or ci / 'release-work').resolve()
    work.relative_to(paper); work.mkdir(parents=True, exist_ok=True)
    bundle = load('_release_portable_validator', paper / 'formal/evidence_bundle.py')
    package = load('_release_package_validator', paper / 'validate_package.py')
    metadata = load('_release_raw_metadata', ci / 'verify_raw_github_metadata.py')
    cohorts = {}
    indices = []
    for name in COHORTS:
        folder = paper / 'formal/ci-evidence' / name
        report, _ = bundle.verify_portable_cohort(folder)
        cohorts[name] = (folder, report)
        indices.append(metadata.safe_path(folder, report['raw_artifact_index']))
    remote = package.validate_remote_publication(paper, bundle, cohorts)
    if remote['mode'] != 'remote-strict-aggregation' or remote['raw_artifacts'] != 33:
        raise ValueError('Final main does not contain the complete approved remote publication')
    provenance = read(ci / 'remote-aggregation-provenance.json')
    preservation = read(ci / 'raw-preservation-index.json')
    rows = preservation['artifacts']
    if len(rows) != 33 or len({(r['run_id'], r['artifact_id']) for r in rows}) != 33:
        raise ValueError('The committed preservation index is not exactly 33 unique artifacts')
    artifact = api(f'repos/{REPOSITORY}/actions/artifacts/{args.preservation_artifact_id}')
    aggregation = api(f'repos/{REPOSITORY}/actions/runs/{provenance["aggregation_run_id"]}')
    expected = dict(artifact_id=args.preservation_artifact_id,
        run_id=provenance['aggregation_run_id'], head_sha=provenance['aggregation_commit'],
        bytes=artifact['size_in_bytes'], sha256=args.preservation_artifact_sha256)
    metadata.check_api_metadata(expected, artifact, aggregation, REPOSITORY, [ARTIFACT_NAME])
    if (artifact.get('expired') or aggregation.get('status') != 'completed'
            or aggregation.get('conclusion') != 'success'):
        raise ValueError('The pinned preservation artifact is expired or its aggregation did not succeed')
    required = artifact['size_in_bytes'] + sum(r['bytes'] for r in rows) + 1024**3
    if shutil.disk_usage(work).free < required:
        raise ValueError('Runner lacks space for the outer artifact, exact originals and 1 GiB headroom')
    archive = work / f'preservation-artifact-{args.preservation_artifact_id}.zip'
    if archive.exists():
        if archive.stat().st_size != expected['bytes'] or sha(archive) != expected['sha256']:
            raise ValueError('Existing preservation download differs; refusing replacement')
    else:
        temporary = archive.with_suffix('.download')
        with temporary.open('xb') as out:
            subprocess.run(['gh', 'api', f'repos/{REPOSITORY}/actions/artifacts/{args.preservation_artifact_id}/zip'],
                stdout=out, check=True)
        if temporary.stat().st_size != expected['bytes'] or sha(temporary) != expected['sha256']:
            raise ValueError('Downloaded outer preservation artifact differs from the pinned API digest')
        # Exclusive hardlink creation cannot silently replace a target that
        # appears between checks. The diagnostic download is retained.
        os.link(temporary, archive)
    restore_exact(archive, paper, rows, METADATA, metadata.safe_path, 512 * 1024**2)
    uploader = ci / 'archive_release.py'; uploader_sha256 = sha(uploader)
    command = [sys.executable, str(uploader), '--paper', str(paper),
        '--repository', REPOSITORY, '--tag', TAG, '--target', args.final_main_commit,
        '--output-directory', str(work)]
    for index in indices:
        command.extend(['--index', str(index)])
    subprocess.run(command, check=True)  # Read-only release plan and all 33 hash checks.
    plan = read(work / 'proof-artifact-release-index.json')
    if len(plan['artifacts']) != 33 or plan['target_commit'] != args.final_main_commit:
        raise ValueError('Reviewed uploader did not plan the exact 33 original archives')
    last_main = require_current_main(args.final_main_commit)
    if sha(uploader) != uploader_sha256:
        raise ValueError('Reviewed release uploader changed before execution')
    receipt = dict(schema='verified-remote-raw-release-v1',
        checked_at_utc=datetime.now(timezone.utc).isoformat(), repository=REPOSITORY,
        final_main_commit=args.final_main_commit, tag=TAG,
        first_main_ref=first_main, last_main_ref=last_main,
        aggregation_run_id=provenance['aggregation_run_id'],
        aggregation_commit=provenance['aggregation_commit'],
        preservation_artifact=artifact, preservation_sha256=sha(archive),
        source_indices=[dict(path=p.relative_to(paper).as_posix(), sha256=sha(p)) for p in indices],
        original_raw_zips=33, original_byte_total=sum(r['bytes'] for r in rows),
        all_original_hashes_verified=True, uploader_sha256=uploader_sha256,
        release_executed=False, replacement_or_deletion_performed=False)
    write(work / 'release-raw-verification.json', receipt)
    if args.execute:
        subprocess.run([*command, '--execute'], check=True)
        receipt['release_executed'] = True
        write(work / 'release-raw-verification.json', receipt)
    print(json.dumps(dict(status='released' if args.execute else 'verified_plan_only',
        originals=33, tag=TAG, target=args.final_main_commit,
        release_url=f'https://github.com/{REPOSITORY}/releases/tag/{TAG}')))


if __name__ == '__main__':
    main()
