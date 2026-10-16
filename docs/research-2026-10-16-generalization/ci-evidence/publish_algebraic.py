#!/usr/bin/env python3
"""Revalidate and publish environment-scoped 3D85/ND45 source/log evidence.

This does not upload anything. Compiled Linux objects remain in preserved raw
artifact ZIPs; the portable publication archive contains sources and logs only.
"""
import argparse
import hashlib
from collections import defaultdict
from pathlib import Path
import zipfile
import evidence_store

import ingest_ci as checked
import validate_algebraic as validator


def registry_name(kind):
    return 'generated3d-registry.json' if kind == '3d85' else 'generated-nd-pilots-registry.json'


def totals(rows):
    rows = list(rows)
    result = dict(records=len(rows), pieces=sum(r['n'] for r in rows),
                  unordered_pairs=sum(r['n'] * (r['n'] - 1) // 2 for r in rows))
    for key in ['piece_vertices', 'container_vertices', 'vertex_membership_tests']:
        if all(key in r for r in rows):
            result[key] = sum(r[key] for r in rows)
    return result


def record_metadata(root, original):
    proposal = checked.read(checked.under(root, original['proposal_path']))
    geometry = checked.read(checked.under(root, original['geometry_intervals_path']))
    key = original['container'] if original['dimension'] == 3 else 'container_' + original['problem']
    vertices = geometry['templates'][key]['vertex_count']
    result = {key: original[key] for key in ['record_id', 'dimension', 'piece', 'container', 'n',
              'source_path', 'source_sha256', 'source_freeze', 'proposal_path', 'proposal_sha256',
              'geometry_source_path', 'geometry_source_sha256', 'geometry_intervals_path',
              'geometry_intervals_sha256']}
    result.update(problem_family=original.get('problem', original['piece'] + ' in ' + original['container']),
                  piece_vertices=proposal['vertex_count'], template_vertices=proposal['vertex_count'] // original['n'],
                  container_vertices=vertices, vertex_membership_tests=proposal['vertex_count'],
                  unordered_pairs=proposal['pair_count'], source_credit=proposal.get('source_credit'))
    if proposal['pair_count'] != original['n'] * (original['n'] - 1) // 2:
        raise ValueError('Algebraic proposal does not cover every unordered piece pair')
    return result


def publish(base, cohorts, out, kind, require_complete=False, approved_bases=None):
    base = base.resolve(); out = out.resolve(); out.mkdir(parents=True, exist_ok=True)
    approved_bases = approved_bases or {}
    operator_reader_sha256=checked.sha(Path(evidence_store.__file__))
    paper = base.parent
    registry = checked.read(base / 'catalogue/algebraic' / registry_name(kind))
    target = {r['record_id']: r for r in registry['records']}
    expected_count = 85 if kind == '3d85' else 45
    if len(target) != expected_count or len(registry['records']) != expected_count:
        raise ValueError('Wrong authoritative bounded algebraic target registry')
    chosen = {}; environments = {}; source_cohorts = []; raw_artifacts = {}; cohort_snapshots = {}
    for source in cohorts:
        source = source.resolve(); data = source.read_bytes(); digest = hashlib.sha256(data).hexdigest()
        snapshot = out / 'working/cohort-inputs' / (digest + '.json')
        snapshot.parent.mkdir(parents=True, exist_ok=True); snapshot.write_bytes(data)
        cohort = checked.read(snapshot)
        if (cohort.get('schema') != 'github-algebraic-cohort-ingestion-v1' or
                cohort['frozen_catalogue_commit'] != checked.FREEZE or
                cohort['cohort_id'] != 'algebraic-' + kind or cohort['expected_record_count'] != expected_count):
            raise ValueError('Publication cohort identity/freeze mismatch')
        member = 'cohort-inputs/' + digest + '.json'; cohort_snapshots[member] = snapshot
        source_cohorts.append(dict(path=source.relative_to(paper).as_posix(), sha256=digest, archive_member=member))
        failures = {r['artifact_id']: r['error'] for r in cohort.get('artifact_validation_failures', [])}
        for directory in (source.parent / 'artifacts').glob('*'):
            archive = directory / 'github-artifact.zip'
            if not archive.is_file():
                continue
            metadata = checked.read(directory / 'github-artifact.json')
            # A combined workflow stores both kinds under one parent directory.
            if not metadata['name'].startswith('lean-algebraic-' + kind + '-shard-'):
                continue
            published = metadata.get('digest')
            if published and published.startswith('sha256:') and checked.sha(archive) != published[7:]:
                raise ValueError('Raw archive differs from its GitHub-published digest')
            item = dict(role='packing', cohort_id='algebraic-' + kind, run_id=cohort['run_id'],
                head_sha=cohort['run_head_sha'], artifact_id=metadata['id'], artifact_name=metadata['name'],
                path=archive.relative_to(paper).as_posix(), bytes=archive.stat().st_size,
                sha256=checked.sha(archive), github_published_digest=published,
                proposed_release_asset_name=f'lean-run-{cohort["run_id"]}-artifact-{metadata["id"]}.zip',
                current_validation_failure=failures.get(metadata['id']))
            core_path = directory / 'validation/formal/core-verification.json'
            if core_path.is_file():
                item['recorded_linux_toolchain'] = checked.read(core_path)['preflight']['lean_version_output']
            raw_artifacts[(cohort['run_id'], metadata['id'])] = item
        for provenance in cohort['validated_shards']:
            approved_base = approved_bases.get(int(provenance['run_id']))
            if approved_bases and approved_base is None:
                raise ValueError('No explicitly approved base for run ' + str(provenance['run_id']))
            approved_base = (approved_base or base).resolve()
            approved_registry = checked.read(approved_base / 'catalogue/algebraic' / registry_name(kind))
            if approved_registry != registry:
                raise ValueError('Approved version changes the frozen numerical target registry')
            ident = f'run-{provenance["run_id"]}-artifact-{provenance["artifact_id"]}'
            root = Path(provenance['validation_formal_root']).resolve()
            # The Windows validation overlay may deliberately live at a short
            # path; preserved raw archives stay beside this provenance file.
            archive_root = source.parent / 'artifacts' / str(provenance['artifact_id'])
            for name, key in [('github-artifact.zip', 'github_archive_sha256'), ('evidence.zip', 'evidence_zip_sha256')]:
                if name=='evidence.zip'and provenance.get('storage_mode')=='zip-streamed-objects':
                    if provenance['object_store']['nested_sha256']!=provenance[key]:raise ValueError('Streamed nested provenance changed')
                elif checked.sha(archive_root / name) != provenance[key]:
                    raise ValueError('Preserved original algebraic artifact changed')
            original = Path(provenance['validation_path'])
            if checked.sha(original) != provenance['validation_sha256']:
                raise ValueError('Original algebraic independent validation changed')
            original_result = checked.read(original)
            for item in original_result['receipt_inputs']:
                if checked.sha(checked.under(root, item['path'])) != item['sha256']:
                    raise ValueError('Original independently accepted algebraic receipt changed')
            with evidence_store.reopen(provenance)as root:
                checked.verify_core(approved_base, root)
                raw_artifacts[(provenance['run_id'], provenance['artifact_id'])]['recorded_linux_toolchain'] = (
                    checked.read(root / 'core-verification.json')['preflight']['lean_version_output'])
                fresh = validator.validate(approved_base, root, kind)
                if {r['record_id'] for r in fresh['verified_records']} != {
                        r['record_id'] for r in original_result['verified_records']}:
                    raise ValueError('Current independent replay changed accepted record scope')
            environments[ident] = dict(root=root, archive_root=archive_root, provenance=provenance,
                replay=fresh, approved_base=approved_base)
            for record in fresh['verified_records']:
                if record['record_id'] not in target or record['original_registry_row'] != target[record['record_id']]:
                    raise ValueError('Unexpected or changed frozen algebraic source record')
                rank = (provenance['artifact_created_at'], provenance['run_id'], provenance['artifact_id'])
                if record['record_id'] not in chosen or rank > chosen[record['record_id']][0]:
                    chosen[record['record_id']] = (rank, ident, record)
    groups = defaultdict(list)
    for _, ident, record in chosen.values():
        groups[ident].append(record)
    files = dict(cohort_snapshots); published = []; environment_rows = []

    def add(root, ident, value):
        if not value:
            return
        path = checked.under(root, value)
        if path.suffix == '.olean':
            return
        if not path.is_file():
            raise ValueError('Selected algebraic source/log/receipt missing: ' + value)
        name = f'environments/{ident}/formal/{value}'
        if name in files and checked.sha(files[name]) != checked.sha(path):
            raise ValueError('Publication namespace collision')
        files[name] = path

    for ident, records in sorted(groups.items()):
        env = environments[ident]; root = env['root']; prov = env['provenance']
        selected = {r['record_id'] for r in records}
        fresh = dict(env['replay'])
        fresh['verified_records'] = [dict(r, **record_metadata(root, r['original_registry_row']))
            for r in fresh['verified_records'] if r['record_id'] in selected]
        fresh['publication_metadata_derivation'] = ('Counts and family labels are derived from the same '
            'source-bound frozen proposals and template interval inputs; semantic evidence is unchanged.')
        fresh['verified_count'] = len(records)
        receipt_paths = {r['evidence']['receipt_path'] for r in records}
        fresh['receipt_inputs'] = [r for r in fresh['receipt_inputs'] if r['path'] in receipt_paths]
        replay_path = out / 'working' / ident / 'selected-replay.json'; checked.write(replay_path, fresh)
        files[f'environments/{ident}/independent-validation.json'] = replay_path
        core = checked.read(root / 'core-verification.json'); add(root, ident, 'core-verification.json')
        for stage in core['results']:
            for key in ['path', 'log']:
                add(root, ident, stage[key])
        add(root, ident, 'catalogue/algebraic/' + registry_name(kind))
        manifest_name = 'ci-pilot-assets.json' if kind == '3d85' else 'ci-nd45-assets.json'
        add(root, ident, 'catalogue/algebraic/' + manifest_name)
        version_manifest = checked.read(root / 'catalogue/algebraic' / manifest_name)
        helper_versions = []
        for asset in version_manifest['files']:
            if asset['path'].endswith('.py'):
                add(root, ident, asset['path'])
                helper_versions.append(dict(path=asset['path'], sha256=asset['sha256']))
        for helper in ['verify_core.py', 'verify_extensions.py']:
            add(root, ident, helper)
        for record in records:
            e = record['evidence']; original = record['original_registry_row']
            for key in ['generated_source_path', 'log_path', 'receipt_path', 'plan_manifest_path']:
                add(root, ident, e.get(key))
            for stage in e['steps']:
                add(root, ident, stage['path']); add(root, ident, stage['log'])
                for dependency in stage['imported_dependencies']:
                    add(root, ident, dependency['path'])
            # Retain the exact native/proposal/template inputs beside the proof.
            for key in ['proposal_path', 'geometry_source_path', 'geometry_intervals_path']:
                add(root, ident, original[key])
            add(root, ident, 'catalogue/algebraic/inputs/' + original['source_path'])
            compact = {key: e[key] for key in ['module', 'generated_source_path', 'generated_source_sha256',
                'olean_path', 'olean_sha256', 'log_path', 'log_sha256', 'receipt_path', 'receipt_sha256',
                'plan_manifest_path', 'plan_manifest_sha256', 'audited_theorems', 'axioms']}
            compact.update(environment_id=ident, proof_step_count=len(e['steps']),
                complete_validation_member=f'environments/{ident}/independent-validation.json')
            published.append(dict(record_metadata(root, original), evidence=compact))
        supplement = prov.get('exact_sha_core_supplement'); portable_supplement = None
        if supplement:
            portable_supplement = {key: supplement[key] for key in ['schema', 'source_provenance_sha256',
                'source_run_id', 'source_head_sha', 'source_artifact_id', 'raw_original_archive_changed', 'boundary']}
            portable_supplement['files'] = [{key: item[key] for key in ['path', 'sha256', 'was_missing',
                'older_recorded_sha256']} for item in supplement['files']]
            portable_supplement['donor_raw_artifact_index_key'] = f'run-{supplement["source_run_id"]}-artifact-{supplement["source_artifact_id"]}'
            portable_path = out / 'working' / ident / 'portable-core-supplement-provenance.json'
            checked.write(portable_path, portable_supplement)
            files[f'environments/{ident}/core-supplement-provenance.json'] = portable_path
            donor = checked.read(Path(supplement['source_provenance_path'])); archive = Path(donor['github_archive'])
            if checked.sha(archive) != donor['github_archive_sha256']:
                raise ValueError('Core supplement raw archive changed')
            raw_artifacts[(donor['run_id'], donor['artifact_id'])] = dict(role='complete_core_supplement',
                run_id=donor['run_id'], head_sha=donor['head_sha'], artifact_id=donor['artifact_id'],
                path=archive.relative_to(paper).as_posix(), bytes=archive.stat().st_size,
                sha256=donor['github_archive_sha256'], github_published_digest=donor.get('github_published_digest'),
                recorded_linux_toolchain=donor['linux_lean_version'],
                proposed_release_asset_name=f'lean-core-run-{donor["run_id"]}-artifact-{donor["artifact_id"]}.zip',
                supplement_provenance_member=f'environments/{ident}/core-supplement-provenance.json')
        environment_rows.append(dict(environment_id=ident, formal_prefix=f'environments/{ident}/formal',
            run_id=prov['run_id'], run_head_sha=prov['run_head_sha'], artifact_id=prov['artifact_id'],
            shard_index=prov['shard_index'],
            github_archive_path=(env['archive_root'] / 'github-artifact.zip').relative_to(paper).as_posix(),
            github_archive_sha256=prov['github_archive_sha256'],
            evidence_zip_path=None if prov.get('storage_mode')=='zip-streamed-objects'else(env['archive_root'] / 'evidence.zip').relative_to(paper).as_posix(),
            storage_mode=prov.get('storage_mode','extracted'),object_store=evidence_store.public_descriptor(prov),
            evidence_zip_sha256=prov['evidence_zip_sha256'], core_validation=prov['core_validation'],
            approved_publication_manifest_member=f'environments/{ident}/formal/catalogue/algebraic/{manifest_name}',
            approved_publication_manifest_sha256=fresh['publication_manifest_sha256'],
            approved_helper_versions=helper_versions,
            exact_sha_core_supplement=portable_supplement))
    archive = out / 'proof-sources-and-logs.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, path in sorted(files.items()):
            z.write(path, name)
    manifest = dict(schema='lean-catalogue-source-log-bundle-v1', archive=archive.name,
        archive_sha256=checked.sha(archive), files=[dict(path=name, bytes=path.stat().st_size,
        sha256=checked.sha(path)) for name, path in sorted(files.items())])
    manifest_path = out / 'proof-sources-and-logs-manifest.json'; checked.write(manifest_path, manifest)
    for item in raw_artifacts.values():
        item['permanent_download_url'] = ('https://github.com/alejandrozu/platonic-packing/releases/download/'
            'lean-frozen-catalogue-2026-10-16/' + item['proposed_release_asset_name'])
        item['selected_record_ids'] = sorted(r['record_id'] for r in published if
            (item['run_id'], item['artifact_id']) == (environments[r['evidence']['environment_id']]['provenance']['run_id'],
                environments[r['evidence']['environment_id']]['provenance']['artifact_id']))
    raw_path = out / 'raw-artifacts.json'
    checked.write(raw_path, dict(schema='preserved-lean-artifact-index-v1',
        artifacts=sorted(raw_artifacts.values(), key=lambda r: (r['run_id'], r['artifact_id'])),
        policy='Exact raw artifact ZIPs are retained for permanent release. This exporter performs no upload. '
            'Failed/superseded artifacts do not count as verified records.'))
    published.sort(key=lambda r: r['record_id']); complete = set(chosen) == set(target)
    eligible = [record_metadata(base, r) for r in target.values()]
    if checked.sha(Path(evidence_store.__file__))!=operator_reader_sha256:
        raise ValueError('Operator ZIP reader changed during publication replay')
    report = dict(schema='portable-source-bound-lean-catalogue-v1', cohort_id='algebraic-' + kind,
        expected_record_count=expected_count, frozen_catalogue_commit=checked.FREEZE,
        exporter_sha256=checked.sha(Path(__file__)), validator_sha256=checked.sha(Path(validator.__file__)),
        operator_reader_sha256=operator_reader_sha256,
        source_cohorts=source_cohorts, environments=environment_rows, verified_records=published,
        verified_totals=totals(published), eligible_totals=totals(eligible), missing_record_ids=sorted(set(target) - set(chosen)),
        complete=complete, proof_source_bundle=archive.name, proof_source_bundle_sha256=checked.sha(archive),
        proof_source_manifest=manifest_path.name, proof_source_manifest_sha256=checked.sha(manifest_path),
        raw_artifact_index=raw_path.name, raw_artifact_index_sha256=checked.sha(raw_path),
        reproduction='Extract each named environment separately; rebuild with the pinned Lean/mathlib and its '
            'archived source/native/proposal/template inputs. Compiled Linux objects remain only in preserved raw ZIPs.',
        trust_boundary='Kernel proofs certify source-linked exact normalized coordinate hulls and all piece pairs. '
            'Parser/generator correctness, named-solid classification and edge-unit conventions remain external boundaries.')
    checked.write(out / 'verified-catalogue.json', report)
    print(__import__('json').dumps(dict(cohort=kind, verified=len(published), eligible=expected_count,
        complete=complete, archive_files=len(files), report=str(out / 'verified-catalogue.json'))))
    if require_complete and not complete:
        raise SystemExit(1)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-formal', type=Path, required=True)
    p.add_argument('--cohorts', nargs='+', type=Path, required=True)
    p.add_argument('--kind', choices=['3d85', 'nd45'], required=True)
    p.add_argument('--output-directory', type=Path)
    p.add_argument('--approved-base', action='append', default=[], metavar='RUN_ID=FORMAL_DIRECTORY',
        help='Explicit approved helper/asset version for each input run; when supplied every run must be mapped')
    p.add_argument('--require-complete', action='store_true')
    args = p.parse_args()
    approved = {}
    for value in args.approved_base:
        try:
            run, directory = value.split('=', 1)
            run = int(run)
            if run <= 0 or run in approved or not directory:
                raise ValueError()
            approved[run] = Path(directory).resolve()
        except ValueError:
            p.error('approved-base must uniquely map a positive run ID to an explicit formal directory')
    out = args.output_directory or Path(__file__).resolve().parent / ('published-85' if args.kind == '3d85' else 'published-45')
    publish(args.base_formal, args.cohorts, out, args.kind, args.require_complete, approved)


if __name__ == '__main__':
    main()
