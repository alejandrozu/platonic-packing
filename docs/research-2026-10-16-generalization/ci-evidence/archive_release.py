#!/usr/bin/env python3
"""Preserve exact CI artifact ZIPs as permanent, hash-indexed GitHub assets.

This does not decide whether a proof passed. Cohort publishers do that separately.
By default it only writes a release plan; --execute performs the GitHub upload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paper', type=Path, required=True)
    parser.add_argument('--index', type=Path, action='append', required=True)
    parser.add_argument('--repository', default='alejandrozu/platonic-packing')
    parser.add_argument('--tag', required=True)
    parser.add_argument('--target', required=True, help='Exact final main commit SHA')
    parser.add_argument('--output-directory', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    paper = args.paper.resolve()
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not re.fullmatch(r'[0-9a-f]{40}', args.target):
        raise ValueError('The release target must be an exact commit SHA')
    if not re.fullmatch(r'[A-Za-z0-9._-]+', args.tag):
        raise ValueError('Unsafe release tag')
    artifacts = {}
    upload_sources = {}
    names = {}
    indices = []
    for index in args.index:
        index = index.resolve()
        index.relative_to(paper)
        value = json.loads(index.read_text(encoding='utf8'))
        if value['schema'] != 'preserved-lean-artifact-index-v1':
            raise ValueError('Unsupported artifact index schema')
        indices.append(dict(path=index.relative_to(paper).as_posix(), sha256=sha(index)))
        for row in value['artifacts']:
            source = (paper / row['path']).resolve()
            source.relative_to(paper)
            name = row['proposed_release_asset_name']
            if not re.fullmatch(r'[A-Za-z0-9._-]+\.zip', name):
                raise ValueError('Unsafe release asset name')
            if source.stat().st_size != row['bytes'] or sha(source) != row['sha256']:
                raise ValueError('Raw artifact bytes changed: ' + str(source))
            key = (row['run_id'], row['artifact_id'])
            if key in artifacts and artifacts[key]['sha256'] != row['sha256']:
                raise ValueError('Conflicting artifact identities')
            if name in names and names[name] != key:
                raise ValueError('Conflicting release asset names')
            names[name] = key
            upload_sources[name] = source
            artifacts[key] = dict(row, release_asset_name=name,
                release_url=f'https://github.com/{args.repository}/releases/download/{args.tag}/{name}')
    if not artifacts:
        raise ValueError('No preserved artifacts to archive')
    plan = dict(schema='permanent-lean-artifact-release-v1', repository=args.repository,
        tag=args.tag, target_commit=args.target, source_indices=indices,
        artifacts=[artifacts[key] for key in sorted(artifacts)],
        boundary='Raw ZIP preservation only; failed or superseded artifacts do not establish verified records.')
    plan_path = output / 'proof-artifact-release-index.json'
    plan_path.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf8')
    if args.execute:
        def gh(*command):
            return subprocess.run(['gh', *command, '--repo', args.repository], check=True)
        def api(path, allow_missing=False):
            result = subprocess.run(['gh', 'api', path], capture_output=True, text=True)
            try:
                body = json.loads(result.stdout)
            except json.JSONDecodeError:
                raise RuntimeError('GitHub API returned no valid JSON: ' + result.stderr)
            if result.returncode:
                if allow_missing and body.get('status') in {404, '404'}:
                    return None
                raise RuntimeError('GitHub API request failed: ' + result.stderr)
            return body
        def checked_tag(required):
            ref = api(f'repos/{args.repository}/git/ref/tags/{args.tag}', allow_missing=not required)
            if ref is None:
                return
            value = ref['object']
            visited = set()
            while value['type'] == 'tag':
                if value['sha'] in visited or len(visited) >= 16:
                    raise ValueError('Cyclic or excessively nested release tag')
                visited.add(value['sha'])
                value = api(f'repos/{args.repository}/git/tags/{value["sha"]}')['object']
            if value['type'] != 'commit' or value['sha'] != args.target:
                raise ValueError('Release tag points to another commit')
        checked_tag(required=False)
        existing = subprocess.run(['gh', 'release', 'view', args.tag, '--repo', args.repository],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if existing.returncode:
            notes = output / 'release-notes.md'
            notes.write_text('Immutable raw Lean build evidence for the frozen catalogue and family-extension study. '
                'The repository manuscript and source-bound verification manifests specify the accepted proof scope. '
                'This release also preserves failed or superseded checkpoints for audit; their presence is not a proof claim.\n',
                encoding='utf8')
            gh('release', 'create', args.tag, '--target', args.target, '--prerelease',
                '--title', 'Lean catalogue proof evidence, 16 October 2026', '--notes-file', str(notes))
        checked_tag(required=True)
        release = api(f'repos/{args.repository}/releases/tags/{args.tag}')
        existing_assets = {row['name']: row for row in release['assets']}
        def verify_asset(path, previous, expected_bytes, expected_sha):
            if previous['size'] != expected_bytes:
                raise ValueError('Release asset has different bytes: ' + path.name)
            if previous.get('digest'):
                if previous['digest'] != 'sha256:' + expected_sha:
                    raise ValueError('Release asset has different SHA-256: ' + path.name)
            else:
                restored = output / ('download-check-' + path.name)
                with restored.open('wb') as stream:
                    subprocess.run(['gh', 'api', f'repos/{args.repository}/releases/assets/{previous["id"]}',
                        '-H', 'Accept: application/octet-stream'], stdout=stream, check=True)
                if sha(restored) != expected_sha:
                    raise ValueError('Release asset download differs: ' + path.name)
        def upload(path, expected_bytes, expected_sha):
            previous = existing_assets.get(path.name)
            if previous:
                verify_asset(path, previous, expected_bytes, expected_sha)
                return
            gh('release', 'upload', args.tag, str(path))
            updated = api(f'repos/{args.repository}/releases/tags/{args.tag}')
            matches = [row for row in updated['assets'] if row['name'] == path.name]
            if len(matches) != 1:
                raise ValueError('Uploaded asset has no unique server record')
            verify_asset(path, matches[0], expected_bytes, expected_sha)
            existing_assets[path.name] = matches[0]
        assets = output / 'assets'
        assets.mkdir(exist_ok=True)
        for row in plan['artifacts']:
            source = upload_sources[row['release_asset_name']]
            staged = assets / row['release_asset_name']
            if not staged.exists():
                try:
                    os.link(source, staged)
                except OSError:
                    shutil.copyfile(source, staged)
            if staged.stat().st_size != row['bytes'] or sha(staged) != row['sha256']:
                raise ValueError('Staged release asset bytes differ from preserved raw ZIP')
            upload(staged, row['bytes'], row['sha256'])
        upload(plan_path, plan_path.stat().st_size, sha(plan_path))
    print(json.dumps(dict(executed=args.execute, artifacts=len(artifacts), plan=str(plan_path))))


if __name__ == '__main__':
    main()
