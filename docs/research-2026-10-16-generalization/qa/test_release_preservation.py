"""Small no-network release safety and final-package-layout regressions.

Fixtures are deliberately retained. They contain dummy bytes, not proof evidence.
The layout case exercises the actual main driver until the authenticated artifact
check, mocking only validators/GitHub because no real release should be performed.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import ast
import hashlib
import importlib.util
import json
import stat
import sys
import tempfile
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def main():
    source = ROOT / 'ci-evidence/release_from_preservation.py'
    ast.parse(source.read_text(encoding='utf8'))
    driver = load('release_driver_regression', source)
    metadata = load('raw_metadata_regression', ROOT / 'ci-evidence/verify_raw_github_metadata.py')
    fixture_root = Path(tempfile.mkdtemp(prefix='release-preservation-', dir=ROOT / 'qa'))
    results = []

    def archive_case(label, alter=None, collision=False):
        paper = fixture_root / label; ci = paper / 'ci-evidence'; ci.mkdir(parents=True)
        for name in driver.METADATA: (ci / name).write_bytes(b'{}')
        rows = []; values = []
        for i in range(33):
            value = f'original-{i}'.encode()
            name = f'ci-evidence/raw-test/artifact-{i}/github-artifact.zip'
            rows.append(dict(path=name, bytes=len(value), sha256=hashlib.sha256(value).hexdigest()))
            values.append((name, value))
        entries = values + [(name, b'{}') for name in driver.METADATA]
        if alter: entries = alter(entries, rows)
        archive = paper / 'preservation.zip'
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with zipfile.ZipFile(archive, 'w') as z:
                for name, value in entries: z.writestr(name, value)
        if collision:
            existing = paper / rows[0]['path']; existing.parent.mkdir(parents=True)
            existing.write_bytes(b'KEEP-CONFLICT')
        try:
            driver.restore_exact(archive, paper, rows, driver.METADATA, metadata.safe_path, 0)
            assert label == 'positive'
            assert all(driver.sha(paper / r['path']) == r['sha256'] for r in rows)
            outcome = 'accepted_exact33'
        except (ValueError, FileExistsError) as error:
            assert label != 'positive', error
            outcome = type(error).__name__ + ': ' + str(error)
            if collision: assert existing.read_bytes() == b'KEEP-CONFLICT'
        results.append(dict(case=label, passed=True, result=outcome))

    archive_case('positive')
    archive_case('existing_conflict', collision=True)
    archive_case('unsafe_path', lambda entries, rows: entries + [('../escape.zip', b'no')])
    archive_case('missing_member', lambda entries, rows: entries[1:])
    archive_case('duplicate_member', lambda entries, rows: entries + [entries[0]])
    archive_case('wrong_metadata', lambda entries, rows:
        [(name, b'[]' if name == driver.METADATA[0] else value) for name, value in entries])

    def corrupt(entries, rows):
        rows[0]['sha256'] = '0' * 64
        return entries
    archive_case('wrong_raw_hash', corrupt)

    def symlink(entries, rows):
        entry = zipfile.ZipInfo(entries[0][0]); entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        return [(entry, entries[0][1]), *entries[1:]]
    archive_case('symlink_entry', symlink)
    with patch.object(driver, 'api', return_value={'object': {'type': 'commit', 'sha': 'a' * 40}}):
        driver.require_current_main('a' * 40)
        try:
            driver.require_current_main('b' * 40)
            raise AssertionError('Wrong main was accepted')
        except ValueError:
            pass
    results.append(dict(case='current_main_commit_guard', passed=True))

    # Actual published layout: operators and metadata at root ci-evidence;
    # the three portable cohorts under formal/ci-evidence. There is no old-layout
    # root ci-evidence/published-* directory that could hide this regression.
    checkout = fixture_root / 'final-checkout'; paper = checkout / 'paper'
    ci = paper / 'ci-evidence'; ci.mkdir(parents=True)
    rows = [dict(run_id=1, artifact_id=i + 1, path=f'ci-evidence/raw-{i}.zip',
                 bytes=1, sha256='c' * 64) for i in range(33)]
    (ci / 'raw-preservation-index.json').write_text(json.dumps({'artifacts': rows}))
    (ci / 'remote-aggregation-provenance.json').write_text(json.dumps(
        {'aggregation_run_id': 7, 'aggregation_commit': 'b' * 40}))
    for name in ['operator-source-hashes.json', 'raw-github-metadata-verification.json']:
        (ci / name).write_text('{}')
    for name in ['release_from_preservation.py', 'verify_raw_github_metadata.py']:
        (ci / name).write_text('# fixture only\n')
    for name in driver.COHORTS:
        folder = paper / 'formal/ci-evidence' / name; folder.mkdir(parents=True)
        (folder / 'verified-catalogue.json').write_text(json.dumps({'raw_artifact_index': 'raw-artifacts.json'}))
        (folder / 'raw-artifacts.json').write_text('{}')
        assert not (ci / name).exists()
    visited = []

    def portable(folder):
        visited.append(folder)
        assert folder.parent == paper / 'formal/ci-evidence'
        return json.loads((folder / 'verified-catalogue.json').read_text()), {}

    def remote(actual_paper, bundle, cohorts):
        assert actual_paper == paper
        assert set(cohorts) == set(driver.COHORTS)
        assert all((ci / name).is_file() for name in [*driver.METADATA,
                                                   'raw-github-metadata-verification.json'])
        assert all(folder.parent == paper / 'formal/ci-evidence' for folder, report in cohorts.values())
        return {'mode': 'remote-strict-aggregation', 'raw_artifacts': 33}

    class BeforeDownload(Exception):
        pass

    modules = {'_release_portable_validator': SimpleNamespace(verify_portable_cohort=portable),
               '_release_package_validator': SimpleNamespace(validate_remote_publication=remote),
               '_release_raw_metadata': metadata}
    def fake_api(endpoint):
        if endpoint.endswith('/git/ref/heads/main'):
            return {'object': {'type': 'commit', 'sha': 'a' * 40}}
        return {'size_in_bytes': 123}
    arguments = ['release_from_preservation.py', '--paper', str(paper), '--checkout', str(checkout),
        '--final-main-commit', 'a' * 40, '--preservation-artifact-id', '99',
        '--preservation-artifact-sha256', 'c' * 64]
    with patch.object(sys, 'argv', arguments), \
         patch.object(driver.subprocess, 'check_output', return_value='a' * 40 + '\n'), \
         patch.object(driver, 'api', side_effect=fake_api), \
         patch.object(driver, 'load', side_effect=lambda name, path: modules[name]), \
         patch.object(metadata, 'check_api_metadata', side_effect=BeforeDownload):
        try:
            driver.main()
            raise AssertionError('Test should stop before any download')
        except BeforeDownload:
            pass
    assert visited == [paper / 'formal/ci-evidence' / name for name in driver.COHORTS]
    results.append(dict(case='final_package_formal_cohorts_root_metadata_layout', passed=True,
        boundary='Real main-path selection through the API guard; dummy validator results, no proof claim'))
    receipt = dict(status='passed_static_archive_regressions', driver_sha256=driver.sha(source),
        tests=results, test_root=str(fixture_root), test_files_retained=True,
        no_network=True, no_release_uploaded=True, no_compiler=True)
    (ROOT / 'qa/release-preservation-regressions.json').write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'status': receipt['status'], 'passed': len(results),
        'driver_sha256': receipt['driver_sha256'], 'no_network': True}))


if __name__ == '__main__':
    main()
