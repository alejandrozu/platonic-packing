#!/usr/bin/env python3
"""Run the unchanged strict auditors/publishers on the final 532-record cohort.

No compiler is invoked. Approved proof helpers come from the separately pinned
Git checkout, never from an artifact. Original ZIPs are retained in this runner
for a separate preservation upload; this program never creates a release.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

BASE_COMMIT = '99bd4eb766cc3ae2e8ee5809aeba810a993f27b3'
FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'
CORE = (38850021923, '9e20447ad5fca7a9cc3b1e0e7d473263f225817e')
RATIONAL = (38849574471, '03d3fe6f155c15b2741f30d5626118bb34d1aadb')
THREE_D = (38854725447, '5b3b9c29ba63242ced22bbc464730cb11c317bf6')
ND = [(38857505608, BASE_COMMIT),
      (38857579749, 'f7e5a3ea1bcb8b72070aa0a6a5dbcf93e7b0d561'),
      (38857614151, '54025130e7f8613340ac93742b5d921233947b7e')]
MANIFESTS = {
    'catalogue/support-first-required-assets.json':
        'cd8741018ba6d10d62ab77acd3c6a3e4d3f7775992b0d04ceafa921dc2d34571',
    'catalogue/algebraic/ci-pilot-assets.json':
        '6c2667cd33e6a4ddb773d7d254c94e9eae508d28ebb985ad7df64c94af85a52e',
    'catalogue/algebraic/ci-nd45-assets.json':
        '11582d543121d4026134f106ecb18676986622cfff79266a6603a41b93cca240',
}
OPERATORS = ['aggregate_publication.py', 'ingest_ci.py', 'ingest_core.py',
             'ingest_algebraic.py', 'validate_algebraic.py', 'evidence_store.py',
             'compact_cohort.py', 'publish_402.py', 'publish_algebraic.py']


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')


def run(command, cwd=None):
    print(json.dumps({'command': list(map(str, command))}), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, check=True)


def checked_path(root, name):
    path = (root / name).resolve(); path.relative_to(root)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-formal', type=Path, required=True)
    parser.add_argument('--base-checkout', type=Path, required=True)
    parser.add_argument('--bundle-validator', type=Path,
        help='Reviewed current packaging-only helper, separate from frozen proof helpers')
    parser.add_argument('--repo', default='alejandrozu/platonic-packing')
    parser.add_argument('--min-free-mb', type=int, default=1024)
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    base = args.base_formal.resolve(); paper = base.parent
    operator = Path(__file__).resolve().parent
    bundle_validator = (args.bundle_validator or
                        operator.parent / 'formal/evidence_bundle.py').resolve()
    store = paper / 'ci-evidence'; portable = store / 'portable'
    if args.repo != 'alejandrozu/platonic-packing' or args.min_free_mb < 512:
        raise ValueError('Use the reviewed repository and at least 512 MiB headroom')
    actual = subprocess.check_output(['git', '-C', str(args.base_checkout),
        'rev-parse', 'HEAD'], text=True).strip()
    if actual != BASE_COMMIT:
        raise ValueError('Approved proof checkout differs from the exact reviewed v2 commit')
    base.relative_to(args.base_checkout.resolve())
    def check_approved_assets():
        for name, expected in MANIFESTS.items():
            manifest = checked_path(base, name)
            if sha(manifest) != expected:
                raise ValueError('Approved asset manifest differs: ' + name)
            key, count = ('required_paths', 452) if name.endswith(
                'support-first-required-assets.json') else (
                    'files', 356 if name.endswith('ci-pilot-assets.json') else 395)
            rows = read(manifest)[key]
            if len(rows) != count or len({r['path'] for r in rows}) != count:
                raise ValueError('Approved source manifest has wrong or duplicated coverage')
            for row in rows:
                path = checked_path(base, row['path'])
                if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
                    raise ValueError('Approved static source/input differs: ' + row['path'])
    check_approved_assets()
    operator_hashes = {name: sha(operator / name) for name in OPERATORS}
    bundle_validator_sha256 = sha(bundle_validator)
    commands = []

    def script(name, *items):
        command = [sys.executable, operator / name, *items]
        commands.append(list(map(str, command)))
        if not args.plan_only:
            run(command)

    def batch(items):
        """Separate processes and disjoint output roots; never shared imports."""
        batch_commands = [[sys.executable, operator / name, *arguments]
                          for name, arguments in items]
        commands.extend([list(map(str, c)) for c in batch_commands])
        if not args.plan_only:
            with ThreadPoolExecutor(max_workers=3) as pool:
                list(pool.map(run, batch_commands))

    common = ['--repo', args.repo, '--base-formal', base, '--store', store]
    stream = ['--fetch', '--stream-objects', '--bounded-nonobject-writes',
              '--min-free-mb', args.min_free_mb]
    supplement = store / f'core-run-{CORE[0]}/supplement-provenance.json'
    if not args.plan_only:
        if shutil.disk_usage(paper).free < 8 * 1024**3:
            raise ValueError('Aggregation requires at least 8 GiB free at start')
        # This restores proposed data only; the strict auditors bind every byte.
        run([sys.executable, base / 'catalogue/unpack_witnesses.py'], cwd=base)
    script('ingest_core.py', '--run-id', CORE[0], '--commit', CORE[1], *common)
    ingestion = [('ingest_ci.py', ['--run-id', RATIONAL[0], '--commit', RATIONAL[1],
           *common, *stream, '--core-supplement', supplement, '--require-all-402'])]
    for ident, commit in [THREE_D, *ND]:
        ingestion.append(('ingest_algebraic.py', ['--run-id', ident, '--commit', commit,
               *common, *stream, '--core-supplement', supplement]))
    # Linux hardlink creation changes inode ctime, which is a protected replay
    # identity. Serialize ingestions that link shared frozen base inputs.
    for name, arguments in ingestion:
        script(name, *arguments)
    for ident, _ in [THREE_D, *ND]:
        # --require-complete on this ingestor tests both kinds in a single run.
        # The final kind-specific publishers enforce the exact85/45 scope.
        if not args.plan_only:
            kind = '3d85' if ident == THREE_D[0] else 'nd45'
            report = read(store / f'algebraic-run-{ident}/cohort-validation-{kind}.json')
            if report['artifact_validation_failures'] or report['not_downloaded_artifact_ids']:
                raise ValueError('A final algebraic artifact failed or was not downloaded')
    if not args.plan_only:
        for ident, commit in [CORE, RATIONAL, THREE_D, *ND]:
            prefix = ('core-run-' if ident == CORE[0] else
                      'run-' if ident == RATIONAL[0] else 'algebraic-run-')
            metadata = read(store / f'{prefix}{ident}/run.json')
            if (metadata['head_sha'] != commit or metadata['status'] != 'completed'
                    or metadata['conclusion'] != 'success'):
                raise ValueError('Final proof run identity or success state changed')
    publication = [('publish_402.py', ['--base-formal', base, '--cohorts',
           store / f'run-{RATIONAL[0]}/cohort-validation.json',
           '--output-directory', portable / 'published-402', '--require-all-402']),
        ('publish_algebraic.py', ['--base-formal', base, '--kind', '3d85',
           '--cohorts', store / f'algebraic-run-{THREE_D[0]}/cohort-validation-3d85.json',
           '--approved-base', f'{THREE_D[0]}={base}', '--output-directory',
           portable / 'published-85', '--require-complete'])]
    nd_args = []
    for ident, _ in ND:
        nd_args.extend(['--approved-base', f'{ident}={base}'])
    publication.append(('publish_algebraic.py', ['--base-formal', base, '--kind', 'nd45',
           '--cohorts', *[store / f'algebraic-run-{ident}/cohort-validation-nd45.json'
                          for ident, _ in ND], *nd_args, '--output-directory',
           portable / 'published-45', '--require-complete']))
    batch(publication)
    # These processes only read already prepared roots and write disjoint
    # publication directories; they never create new shared-base hardlinks.
    validator_commands = [[sys.executable, bundle_validator, '--cohort',
        portable / folder] for folder in ['published-402', 'published-85', 'published-45']]
    commands.extend([list(map(str, c)) for c in validator_commands])
    if not args.plan_only:
        for command in validator_commands:
            run(command)
    if args.plan_only:
        print(json.dumps({'status': 'plan_only_no_downloads_or_replay',
            'approved_base': BASE_COMMIT, 'commands': commands}, indent=2))
        return
    if {name: sha(operator / name) for name in OPERATORS} != operator_hashes:
        raise ValueError('Reviewed operator implementation changed during aggregation')
    if sha(bundle_validator) != bundle_validator_sha256:
        raise ValueError('Reviewed portable validator changed during aggregation')
    check_approved_assets()
    cohorts = []; raw = {}; identities = set()
    for folder, kind, count in [('published-402', 'rational-402', 402),
                                ('published-85', 'algebraic-3d85', 85),
                                ('published-45', 'algebraic-nd45', 45)]:
        out = portable / folder; report = read(out / 'verified-catalogue.json')
        if (len(report['verified_records']) != count or report['missing_record_ids']
                or not report.get('complete', report.get('complete_402'))):
            raise ValueError('Final portable cohort is incomplete')
        report['publication_storage_mode'] = 'remote-strict-aggregation'
        write(out / 'verified-catalogue.json', report)
        for row in report['verified_records']:
            if row['record_id'] in identities:
                raise ValueError('The final 532 source IDs overlap')
            identities.add(row['record_id'])
        cohorts.append(dict(cohort_id=kind, relative_directory=folder,
            record_count=count, report=f'{folder}/verified-catalogue.json',
            report_sha256=sha(out / 'verified-catalogue.json'),
            source_bundle=f'{folder}/{report["proof_source_bundle"]}',
            source_bundle_sha256=report['proof_source_bundle_sha256'],
            source_manifest=f'{folder}/{report["proof_source_manifest"]}',
            source_manifest_sha256=report['proof_source_manifest_sha256'],
            raw_index=f'{folder}/{report["raw_artifact_index"]}',
            raw_index_sha256=report['raw_artifact_index_sha256']))
        for row in read(out / report['raw_artifact_index'])['artifacts']:
            key = (row['run_id'], row['artifact_id'])
            if key in raw and raw[key]['sha256'] != row['sha256']:
                raise ValueError('Conflicting original raw ZIP hashes')
            path = checked_path(paper, row['path'])
            if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
                raise ValueError('Original raw ZIP changed after strict publication')
            raw[key] = row
    if len(identities) != 532 or len(raw) != 33:
        raise ValueError('Expected 532 distinct records and 32 packing ZIPs plus one core ZIP')
    write(portable / 'raw-preservation-index.json', dict(
        schema='remote-original-lean-artifact-preservation-v1',
        path_base='paper', artifacts=[raw[key] for key in sorted(raw)],
        original_zip_count=33, byte_total=sum(r['bytes'] for r in raw.values()),
        release_uploaded=False))
    write(portable / 'operator-source-hashes.json', dict(
        schema='reviewed-lean-aggregation-operator-sources-v1', sources=operator_hashes,
        portable_validator=dict(path='formal/evidence_bundle.py',
            sha256=bundle_validator_sha256)))
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    commit = os.environ.get('GITHUB_SHA', '')
    if not run_id.isdecimal() or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Remote aggregation requires exact GitHub run/commit provenance')
    write(portable / 'remote-aggregation-provenance.json', dict(
        schema='remote-strict-lean-aggregation-v1',
        storage_mode='remote-strict-aggregation', repository=args.repo,
        created_utc=datetime.now(timezone.utc).isoformat(),
        aggregation_run_id=int(run_id), aggregation_commit=commit,
        approved_base_commit=BASE_COMMIT, approved_manifest_hashes=MANIFESTS,
        frozen_catalogue_commit=FREEZE, portable_cohorts=cohorts,
        operator_source_hashes='operator-source-hashes.json',
        operator_source_hashes_sha256=sha(portable / 'operator-source-hashes.json'),
        raw_preservation_index='raw-preservation-index.json',
        raw_preservation_index_sha256=sha(portable / 'raw-preservation-index.json'),
        complete_records=532, strict_replay_complete=True, kernel_reexecuted=False,
        raw_original_storage='separate remote raw-preservation artifact; no release upload',
        raw_preservation_restore_base='paper',
        trust_boundary='Source-bound build receipts, original Linux proof objects, all closure/source/log hashes and axioms are replayed by the reviewed auditors. No compiler is rerun; parser/generator and named-solid classification boundaries remain unchanged.'))
    # Upload a single directory without wildcards, preserving exact paper-relative
    # paths. Hardlinks avoid an additional raw-ZIP copy on the Ubuntu volume.
    preservation = store / 'raw-preservation'
    for row in raw.values():
        source = checked_path(paper, row['path'])
        destination = checked_path(preservation, row['path'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if sha(destination) != row['sha256']:
                raise ValueError('Raw preservation target already has differing bytes')
        else:
            os.link(source, destination)
        if sha(destination) != row['sha256']:
            raise ValueError('Raw preservation link differs from the final index')
    for name in ['raw-preservation-index.json', 'remote-aggregation-provenance.json',
                 'operator-source-hashes.json']:
        destination = preservation / name
        if destination.exists():
            if sha(destination) != sha(portable / name):
                raise ValueError('Raw preservation metadata collision')
        else:
            os.link(portable / name, destination)
    # The publishers' working replay JSONs can be much larger than the portable
    # bundle. Export only the canonical four files per cohort and three metadata
    # files, so a local reviewer does not need another full audit working tree.
    export = store / 'portable-export'
    exported = set()
    for folder in ['published-402', 'published-85', 'published-45']:
        report = read(portable / folder / 'verified-catalogue.json')
        names = ['verified-catalogue.json', report['proof_source_bundle'],
                 report['proof_source_manifest'], report['raw_artifact_index']]
        if len(set(names)) != 4 or any(Path(name).name != name for name in names):
            raise ValueError('Unexpected canonical portable output filenames')
        for name in names:
            exported.add(f'{folder}/{name}')
    exported.update(['raw-preservation-index.json',
                     'remote-aggregation-provenance.json', 'operator-source-hashes.json'])
    for name in exported:
        source = checked_path(portable, name); destination = checked_path(export, name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if sha(destination) != sha(source):
                raise ValueError('Portable export target contains differing bytes')
        else:
            os.link(source, destination)
    actual_exported = {p.relative_to(export).as_posix() for p in export.rglob('*') if p.is_file()}
    if actual_exported != exported or len(exported) != 15:
        raise ValueError('Portable export includes an unreviewed or missing member')
    print(json.dumps({'status': 'passed_strict_aggregation', 'records': 532,
        'original_raw_zips': 33, 'portable_root': str(export),
        'portable_files': len(exported)}), flush=True)


if __name__ == '__main__':
    main()
