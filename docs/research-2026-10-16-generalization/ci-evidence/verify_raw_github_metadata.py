#!/usr/bin/env python3
"""Bind portable raw-archive indices to read-only GitHub API metadata.

This does not replay Lean or download archives. Absent archives are explicitly
not reported as locally hashed; their published SHA256 is checked against GitHub.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess


SCHEMA = 'github-raw-artifact-metadata-verification-v1'
FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'
COHORTS = {'published-402': 'rational-402', 'published-85': 'algebraic-3d85',
           'published-45': 'algebraic-nd45'}
VERIFIER = 'ci-evidence/verify_raw_github_metadata.py'
RECEIPT = 'ci-evidence/raw-github-metadata-verification.json'
PROVENANCE = 'ci-evidence/remote-aggregation-provenance.json'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def digest(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('Invalid SHA256')
    return value


def positive_integer(value):
    if type(value) is not int or value <= 0:
        raise ValueError('Expected a positive integer identity/size')
    return value


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative or '\0' in relative:
        raise ValueError('Unsafe relative evidence path')
    parts = PurePosixPath(relative).parts
    if PurePosixPath(relative).is_absolute() or any(p in {'.', '..'} for p in parts) or '/'.join(parts) != relative:
        raise ValueError('Unsafe relative evidence path')
    root = Path(root).resolve()
    path = root
    for part in parts:
        path = path / part
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Aliases/reparse points are not evidence paths')
    path.resolve().relative_to(root)
    return path


def cohort_directories(paper, names):
    result = {}
    for name in names:
        candidates = [paper / 'formal/ci-evidence' / name, paper / 'ci-evidence' / name]
        result[name] = next((p for p in candidates if (p / 'verified-catalogue.json').is_file()), candidates[0])
    return result


def inventory(paper, directories):
    """Read public indices only; archive bytes are not needed for validation."""
    paper = Path(paper).resolve(); sources = []; artifacts = {}
    for name, directory in sorted(directories.items()):
        if name not in COHORTS:
            raise ValueError('Unknown portable cohort')
        directory = Path(directory).resolve(); directory.relative_to(paper)
        report_path = directory / 'verified-catalogue.json'; report = read(report_path)
        if (report.get('schema') != 'portable-source-bound-lean-catalogue-v1' or
                report.get('frozen_catalogue_commit') != FREEZE or report.get('cohort_id') != COHORTS[name]):
            raise ValueError('Unsupported portable cohort identity')
        index = safe_path(directory, report.get('raw_artifact_index', 'raw-artifacts.json'))
        index_sha = sha(index)
        if digest(report['raw_artifact_index_sha256']) != index_sha:
            raise ValueError('Portable report/raw-index SHA mismatch')
        value = read(index)
        if value.get('schema') != 'preserved-lean-artifact-index-v1':
            raise ValueError('Unsupported raw artifact index')
        sources.append(dict(cohort_name=name, report_path=report_path.relative_to(paper).as_posix(),
            report_sha256=sha(report_path), index_path=index.relative_to(paper).as_posix(), index_sha256=index_sha))
        seen = set()
        for row in value['artifacts']:
            key = (positive_integer(row['run_id']), positive_integer(row['artifact_id']))
            if key in seen:
                raise ValueError('Duplicate artifact in one raw index')
            seen.add(key)
            expected = {k: row[k] for k in ('run_id', 'artifact_id', 'head_sha', 'bytes', 'sha256')}
            if not re.fullmatch(r'[0-9a-f]{40}', expected['head_sha']):
                raise ValueError('Invalid raw source commit')
            positive_integer(expected['bytes']); digest(expected['sha256'])
            if row.get('github_published_digest') != 'sha256:' + expected['sha256']:
                raise ValueError('Raw index lacks a matching GitHub-published SHA256')
            safe_path(paper, row['path'])
            if key in artifacts:
                if artifacts[key]['expected'] != expected:
                    raise ValueError('Conflicting raw artifact identities across cohorts')
            else:
                artifacts[key] = dict(expected=expected, paths=set(), names=set())
            artifacts[key]['paths'].add(row['path'])
            if row.get('artifact_name'):
                artifacts[key]['names'].add(row['artifact_name'])
    if not artifacts:
        raise ValueError('No preserved raw archives')
    for value in artifacts.values():
        if len(value['names']) > 1:
            raise ValueError('Conflicting artifact names')
    return sources, artifacts


def check_api_metadata(expected, artifact, run, repository, names=()):
    """Apply the same identity checks to fresh API responses and saved receipts."""
    workflow = artifact.get('workflow_run') or {}
    for value in (artifact.get('id'), workflow.get('id'), run.get('id'),
                  workflow.get('head_repository_id'), (run.get('head_repository') or {}).get('id')):
        positive_integer(value)
    if (artifact.get('id') != expected['artifact_id'] or workflow.get('id') != expected['run_id'] or
            run.get('id') != expected['run_id'] or run.get('head_sha') != expected['head_sha'] or
            workflow.get('head_sha') != expected['head_sha']):
        raise ValueError('GitHub artifact/run/head identity mismatch')
    if ((run.get('repository') or {}).get('full_name', '').casefold() != repository.casefold() or
            (run.get('head_repository') or {}).get('full_name', '').casefold() != repository.casefold()):
        raise ValueError('GitHub source repository mismatch')
    if workflow.get('head_repository_id') != (run.get('head_repository') or {}).get('id'):
        raise ValueError('GitHub artifact/run head-repository identity mismatch')
    if artifact.get('size_in_bytes') != expected['bytes']:
        raise ValueError('GitHub artifact byte count mismatch')
    if artifact.get('digest') != 'sha256:' + expected['sha256']:
        raise ValueError('GitHub artifact SHA256 is absent or does not match')
    if names and artifact.get('name') not in names:
        raise ValueError('GitHub artifact name mismatch')


def project_artifact(value):
    result = {k: value.get(k) for k in ('id', 'name', 'size_in_bytes', 'digest', 'expired', 'created_at', 'updated_at')}
    result['workflow_run'] = {k: (value.get('workflow_run') or {}).get(k)
                              for k in ('id', 'head_sha', 'head_repository_id')}
    return result


def project_run(value):
    result = {k: value.get(k) for k in ('id', 'head_sha', 'status', 'conclusion', 'run_attempt', 'workflow_id', 'path')}
    for key in ('repository', 'head_repository'):
        result[key] = {k: (value.get(key) or {}).get(k) for k in ('id', 'full_name')}
    return result


def verify(paper, directories, repository, api, verifier_path=None):
    paper = Path(paper).resolve(); verifier = Path(verifier_path or __file__).resolve()
    if verifier != safe_path(paper, VERIFIER):
        raise ValueError('Verifier must be the named publication operator')
    verifier_sha = sha(verifier); sources, artifacts = inventory(paper, directories)
    rows = []; runs = {}
    for (run_id, artifact_id), item in sorted(artifacts.items()):
        run_endpoint = f'repos/{repository}/actions/runs/{run_id}'
        artifact_endpoint = f'repos/{repository}/actions/artifacts/{artifact_id}'
        if run_id not in runs:
            runs[run_id] = project_run(api(run_endpoint))
        artifact = project_artifact(api(artifact_endpoint)); run = runs[run_id]
        check_api_metadata(item['expected'], artifact, run, repository, item['names'])
        local = []
        for name in sorted(item['paths']):
            path = safe_path(paper, name)
            if not path.exists():
                local.append(dict(path=name, status='absent_not_hashed_locally', sha256=None, bytes=None))
                continue
            before = path.stat()
            if not path.is_file() or before.st_size != item['expected']['bytes']:
                raise ValueError('Local raw archive has a wrong type/size')
            actual = sha(path); after = path.stat()
            identity = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
            if actual != item['expected']['sha256'] or identity(before) != identity(after):
                raise ValueError('Local raw archive changed or has a wrong SHA256')
            local.append(dict(path=name, status='present_sha256_verified', sha256=actual, bytes=after.st_size))
        rows.append(dict(expected=item['expected'], artifact_endpoint=artifact_endpoint,
            run_endpoint=run_endpoint, github_artifact=artifact, github_run=run, local_archives=local))
    remote = None; provenance_path = safe_path(paper, PROVENANCE)
    if provenance_path.is_file():
        provenance = read(provenance_path)
        run_id = positive_integer(provenance['aggregation_run_id'])
        actual = project_run(api(f'repos/{repository}/actions/runs/{run_id}'))
        if (provenance.get('schema') != 'remote-strict-lean-aggregation-v1' or
                provenance.get('repository') != repository or actual['id'] != run_id or
                actual['head_sha'] != provenance.get('aggregation_commit') or
                actual['status'] != 'completed' or actual['conclusion'] != 'success' or
                (actual['repository'].get('full_name') or '').casefold() != repository.casefold() or
                (actual['head_repository'].get('full_name') or '').casefold() != repository.casefold()):
            raise ValueError('Remote aggregation run is not the completed matching GitHub run')
        remote = dict(provenance_path=PROVENANCE, provenance_sha256=sha(provenance_path), github_run=actual)
    current, _ = inventory(paper, directories)
    if current != sources or sha(verifier) != verifier_sha:
        raise ValueError('Verifier or source indices changed during API verification')
    local_count = sum(any(p['status'] == 'present_sha256_verified' for p in row['local_archives']) for row in rows)
    return dict(schema=SCHEMA, status='passed', checked_at_utc=datetime.now(timezone.utc).isoformat(),
        repository=repository, frozen_catalogue_commit=FREEZE,
        verifier=dict(path=VERIFIER, source_sha256=verifier_sha), source_indices=sources,
        unique_raw_artifacts=len(rows), locally_hashed_artifacts=local_count,
        metadata_only_artifacts=len(rows)-local_count, remote_aggregation=remote, artifacts=rows,
        boundary='Read-only GitHub API identity/digest check. Absent local archives were not locally read or hashed. '
                 'This is not a Lean replay or a permanent-release upload receipt.')


def validate_receipt(paper, directories, receipt):
    """Validate a saved API receipt without network requests or local raw ZIPs."""
    paper = Path(paper).resolve(); sources, artifacts = inventory(paper, directories)
    if (receipt.get('schema') != SCHEMA or receipt.get('status') != 'passed' or
            receipt.get('repository') != 'alejandrozu/platonic-packing' or receipt.get('frozen_catalogue_commit') != FREEZE):
        raise ValueError('Unsupported GitHub raw-metadata verification receipt')
    if receipt.get('verifier', {}).get('path') != VERIFIER or sha(safe_path(paper, VERIFIER)) != receipt['verifier'].get('source_sha256'):
        raise ValueError('Raw-metadata verifier source changed')
    current = {r['cohort_name']: (r['report_sha256'], r['index_sha256']) for r in sources}
    original = {}
    for row in receipt['source_indices']:
        if row['cohort_name'] in original:
            raise ValueError('Duplicate raw-metadata source index')
        safe_path(paper, row['report_path']); safe_path(paper, row['index_path'])
        original[row['cohort_name']] = (digest(row['report_sha256']), digest(row['index_sha256']))
    if current != original:
        raise ValueError('Raw-metadata receipt does not bind the current exact cohort indices')
    checked = set(); local_count = 0
    for row in receipt['artifacts']:
        expected = row['expected']; key = (expected['run_id'], expected['artifact_id'])
        if key in checked or key not in artifacts or expected != artifacts[key]['expected']:
            raise ValueError('Raw-metadata receipt contains a changed/duplicate artifact')
        checked.add(key); item = artifacts[key]
        prefix = 'repos/' + receipt['repository'] + '/actions/'
        if (row['artifact_endpoint'] != prefix + 'artifacts/' + str(key[1]) or
                row['run_endpoint'] != prefix + 'runs/' + str(key[0])):
            raise ValueError('Wrong recorded GitHub API endpoint')
        check_api_metadata(expected, row['github_artifact'], row['github_run'], receipt['repository'], item['names'])
        locations = {}; locally_hashed = False
        for value in row['local_archives']:
            name = value['path']; safe_path(paper, name)
            if name in locations:
                raise ValueError('Duplicate local archive status')
            locations[name] = value
            if value['status'] == 'present_sha256_verified':
                if value['sha256'] != expected['sha256'] or value['bytes'] != expected['bytes']:
                    raise ValueError('Wrong locally recorded archive hash/size')
                locally_hashed = True
            elif value['status'] != 'absent_not_hashed_locally' or value.get('sha256') is not None or value.get('bytes') is not None:
                raise ValueError('Absent archives must never have an asserted local byte hash')
        if set(locations) != item['paths']:
            raise ValueError('Raw-metadata receipt has different archive locators')
        local_count += locally_hashed
    if (checked != set(artifacts) or receipt.get('unique_raw_artifacts') != len(artifacts) or
            receipt.get('locally_hashed_artifacts') != local_count or
            receipt.get('metadata_only_artifacts') != len(artifacts)-local_count):
        raise ValueError('Raw-metadata receipt coverage/count mismatch')
    return dict(raw_artifacts=len(artifacts), locally_hashed_artifacts=local_count,
                metadata_only_artifacts=len(artifacts)-local_count)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paper', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--repository', default='alejandrozu/platonic-packing')
    parser.add_argument('--cohort', choices=sorted(COHORTS), action='append',
                        help='Explicit subset; default verifies all three publication cohorts')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); paper = args.paper.resolve()
    if args.repository != 'alejandrozu/platonic-packing':
        raise ValueError('Only the named publication repository is supported')
    names = args.cohort or list(COHORTS)
    if len(names) != len(set(names)):
        raise ValueError('Duplicate cohort selection')
    def api(endpoint):
        result = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    directories = cohort_directories(paper, names)
    receipt = verify(paper, directories, args.repository, api)
    validate_receipt(paper, directories, receipt)
    output = (args.output or paper / RECEIPT).absolute(); output.relative_to(paper)
    output = safe_path(paper, output.relative_to(paper).as_posix())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(status='passed', receipt=output.relative_to(paper).as_posix(),
        unique_raw_artifacts=receipt['unique_raw_artifacts'], locally_hashed_artifacts=receipt['locally_hashed_artifacts'],
        metadata_only_artifacts=receipt['metadata_only_artifacts'])))


if __name__ == '__main__':
    main()
