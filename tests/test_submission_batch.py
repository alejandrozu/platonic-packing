"""Batch witnesses are replayed with real trusted certifiers, never submitted code."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from test_submission import ROOT, RECORD, body, submission
import submission_batch
import submission_runner
import submission_event_guard

URL = 'https://github.com/user-attachments/files/12345/native-witnesses.zip'
RECORD3 = json.loads((ROOT / 'records/cubincub/cubincub_n03.json').read_text(encoding='utf-8'))


def archive(candidates, extra=None):
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w', zipfile.ZIP_DEFLATED) as result:
        cases = []
        for index, record in enumerate(candidates):
            name = f'records/candidate-{index}.json'
            raw = json.dumps(record).encode()
            result.writestr('bank/' + name, raw)
            cases.append({'file': name, 'sha256': hashlib.sha256(raw).hexdigest()})
        result.writestr('bank/MANIFEST.json', json.dumps({'count': len(cases), 'cases': cases}))
        # Even executable-looking source and claimed certificate receipts are inert.
        result.writestr('bank/VERIFY.py', 'raise RuntimeError("Submitted code must never execute")')
        result.writestr('bank/record.certify.txt', 'CERTIFIED')
        result.writestr('bank/original/records/history.json', json.dumps(RECORD))
        for name, content in (extra or {}).items(): result.writestr(name, content)
    return data.getvalue()


class BatchSubmissionTests(unittest.TestCase):
    def run_batch(self, payload, records, mode='accept', raw_body=None):
        with tempfile.TemporaryDirectory(prefix='packing-batch-') as directory:
            root = Path(directory)
            for record in records:
                target = root / f'records/cubincub/cubincub_n{record["n"]:02d}.json'
                target.parent.mkdir(parents=True, exist_ok=True)
                previous = copy.deepcopy(record); previous['s_full'] += 0.02
                target.write_text(json.dumps(previous), encoding='utf-8')
            issue_body = raw_body or body(RECORD) + '\n\n### Batch archives\n\n' + URL
            event = {'action': 'labeled' if mode == 'accept' else 'opened', 'label': {'name': 'accepted'},
                     'issue': {'number': 321, 'html_url': 'https://example.invalid/issues/321',
                               'user': {'login': 'batch-contributor'}, 'body': issue_body}}
            event_file = root / 'event.json'; output = root / 'out'
            event_file.write_text(json.dumps(event), encoding='utf-8')

            def trusted_check(cmd, timeout):
                command = [cmd[0], '-X', 'utf8', str(ROOT / cmd[1]), *cmd[2:]]
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                        encoding='utf-8', timeout=timeout)
                return result.returncode, (result.stdout + result.stderr).strip()

            real_discover = submission_batch.discover
            with patch.object(submission, 'ROOT', str(root)), patch.object(submission, 'run', trusted_check), \
                    patch.object(submission_runner, 'discover', side_effect=lambda text, fields: real_discover(text, fields, downloader=lambda url: payload)), \
                    patch.object(sys, 'argv', ['check_submission.py', mode, str(event_file), str(output)]), \
                    patch.dict(os.environ, {'SUBMISSION_CAN_ACCEPT': '1'}):
                submission.main()
            result = json.loads((output / 'result.json').read_text(encoding='utf-8'))
            written = {path: json.loads((root / path).read_text(encoding='utf-8')) for path in result['records']}
            registry = json.loads((root / 'docs/community_records.json').read_text(encoding='utf-8')) if written else None
            originals = [json.loads((root / f'records/cubincub/cubincub_n{r["n"]:02d}.json').read_text(encoding='utf-8')) for r in records]
            return result, written, registry, originals, (output / 'comment.md').read_text(encoding='utf-8')

    def test_archive_replays_all_cases_rejects_2d_and_picks_best_certified_duplicate(self):
        worse = copy.deepcopy(RECORD); worse['s_full'] += 0.005
        unsupported = {'piece': 'square', 'container': 'square', 'n': 2, 's_full': 2,
                       'pieces': [[0, 0, 0], [1, 0, 0]]}
        overlap = copy.deepcopy(RECORD3); overlap['pieces'][1] = overlap['pieces'][0][:]
        invalid_smaller = copy.deepcopy(RECORD); invalid_smaller['s_full'] -= 0.1
        payload = archive([worse, RECORD, RECORD3, unsupported, overlap, invalid_smaller])
        result, written, registry, originals, comment = self.run_batch(payload, [RECORD, RECORD3])
        self.assertEqual(result['summary']['discovered'], 7)  # six ZIP witnesses and the inline specimen
        self.assertEqual(result['summary']['processed'], 7)
        self.assertEqual(result['summary']['accepted'], 2)
        self.assertEqual(result['summary']['rejected'], 3)
        self.assertEqual(result['summary']['skipped'], 2)  # exact duplicate and larger valid case
        self.assertFalse(result['complete'])
        self.assertIn('needs-fix', result['labels_add'])
        self.assertIn('not-certified', result['labels_add'])
        self.assertEqual(len(registry['entries']), 2)
        self.assertEqual(sorted(record['pieces'] for record in written.values()), sorted([RECORD['pieces'], RECORD3['pieces']]))
        self.assertTrue(all(path.startswith('records/community/') for path in written))
        self.assertEqual(originals[0]['s_full'], RECORD['s_full'] + 0.02)
        self.assertIn('7 candidates found; 7 processed', comment)
        self.assertIn('src/solids_exact.json', result['guard_paths'])
        self.assertIn('records/cubincub/cubincub_n03.json', result['guard_paths'])

    def test_inline_record_array_accepts_every_improvement_and_retains_each_author(self):
        first, second = copy.deepcopy(RECORD), copy.deepcopy(RECORD3)
        first.update(found_by='Original geometric author', credit='Original source credit',
                     certificate_refined_by='Independent certificate refiner',
                     source_refinement={'pieces_unchanged': True, 'type': 'wall-padding'})
        second.update(found_by='Second constructor', credit='Second original credit')
        second['pieces'][0][0] += 1e-9  # a distinct certified geometry, not a padding-only refinement
        text = body(RECORD)
        start = text.index('```json\n'); end = text.index('\n```', start)
        text = text[:start] + '```json\n' + json.dumps({'records': [first, second]}) + text[end:]
        result, written, registry, _, comment = self.run_batch(b'', [first, RECORD3], raw_body=text)
        self.assertEqual(result['summary']['accepted'], 2)
        self.assertTrue(result['complete'])
        values = {record['n']: record for record in written.values()}
        self.assertEqual(values[2]['found_by'], first['found_by'])
        self.assertEqual(values[2]['credit'], first['credit'])
        self.assertEqual(values[2]['certificate_refined_by'], first['certificate_refined_by'])
        self.assertEqual(values[2]['contribution']['kind'], 'wall_padding')
        self.assertFalse(values[2]['certificate_refinement']['new_nominal_construction'])
        self.assertEqual(values[3]['found_by'], second['found_by'])
        self.assertNotIn('certificate_refined_by', values[3])
        self.assertEqual(values[2]['pieces'], first['pieces'])
        self.assertEqual(values[3]['pieces'], second['pieces'])
        self.assertEqual(len(registry['entries']), 2)

    def test_manifest_controls_active_witnesses_not_historical_source_copies(self):
        rows, ignored = submission_batch.archive_records(archive([RECORD, RECORD3]), URL)
        self.assertEqual(len(rows), 2)
        self.assertEqual([row['object']['n'] for row in rows], [2, 3])
        self.assertGreaterEqual(ignored, 4)
        self.assertTrue(all('original/' not in row['source'] for row in rows))

    def test_inline_specimen_does_not_erase_identical_archived_original_credit_or_refinement_role(self):
        witness = {key: RECORD[key] for key in ('piece', 'container', 'n', 's_full', 'pieces')}
        witness.update(source_credit={'construction_and_original_certificate': 'Original cube constructor',
                                      'issue': 'https://example.invalid/original-construction'},
                       certificate_refined_by='Certificate refiner',
                       source_refinement={'pieces_unchanged': True, 'type': 'wall-padding'})
        inline = {key: witness[key] for key in ('piece', 'container', 'n', 's_full', 'pieces')}
        predecessor = copy.deepcopy(RECORD)
        predecessor.update(found_by='Original cube constructor', source={'issue': 'https://example.invalid/original-construction'})
        result, written, _, _, _ = self.run_batch(archive([witness]), [predecessor], raw_body=body(inline) + '\n\n' + URL)
        self.assertEqual(result['summary']['accepted'], 1)
        self.assertEqual(result['summary']['skipped'], 1)
        record = next(iter(written.values()))
        self.assertEqual(record['found_by'], 'Original cube constructor')
        self.assertEqual(record['certificate_refined_by'], 'Certificate refiner')
        self.assertEqual(record['source']['issue'], 'https://example.invalid/original-construction')
        self.assertEqual(record['contribution']['kind'], 'wall_padding')
        self.assertEqual(record['pieces'], inline['pieces'])

    def test_omitted_or_false_origin_cannot_steal_trusted_padding_authorship(self):
        predecessor = copy.deepcopy(RECORD)
        predecessor.update(found_by='Trusted original author', credit='Full trusted credit',
                           method='Trusted geometric method', source={'url': 'https://example.invalid/original'})
        submitted = {key: RECORD[key] for key in ('piece', 'container', 'n', 's_full', 'pieces')}
        submitted.update(found_by='Wrong claimant', credit='Wrong origin metadata', method='Wrong original method')
        result, written, _, _, _ = self.run_batch(b'', [predecessor], raw_body=body(submitted))
        record = next(iter(written.values()))
        self.assertEqual(record['found_by'], predecessor['found_by'])
        self.assertEqual(record['credit'], predecessor['credit'])
        self.assertEqual(record['method'], predecessor['method'])
        self.assertEqual(record['source'], predecessor['source'])
        self.assertEqual(record['certificate_refined_by'], 'Example contributor')
        self.assertTrue(record['certificate_refinement']['geometry_matched_exactly'])
        self.assertEqual(record['pieces'], submitted['pieces'])
        self.assertEqual(record['case_id'], 'cubincub_n02')
        self.assertEqual(record['record_id'], Path(next(iter(written))).stem)
        self.assertNotEqual(record['record_id'], record['case_id'])

    def test_explicit_centred_geometry_is_preserved_and_equivalent_quaternions_are_matched_exactly(self):
        predecessor = {'piece': 'cube', 'container': 'cube', 'n': 2, 's_full': 3.1,
                       'pieces': [[-.75, 0, 0, 1, 0, 0, 0], [.75, 0, 0, 1, 0, 0, 0]],
                       'found_by': 'Trusted centred constructor', 'credit': 'Trusted credit', 'method': 'Trusted method',
                       'source': {'url': 'https://example.invalid/centred'}}
        submitted = {key: copy.deepcopy(predecessor[key]) for key in ('piece', 'container', 'n', 's_full', 'pieces')}
        submitted['s_full'] = 3.0; submitted['container_center'] = [8, -4, 2]
        for piece in submitted['pieces']:
            for k in range(3): piece[k] += submitted['container_center'][k]
            piece[3] = -1e308
        result, written, _, _, _ = self.run_batch(b'', [predecessor], raw_body=body(submitted))
        self.assertEqual(result['summary']['certified'], 1)
        record = next(iter(written.values()))
        self.assertEqual(record['pieces'], submitted['pieces'])
        self.assertEqual(record['container_center'], submitted['container_center'])
        self.assertEqual(record['found_by'], predecessor['found_by'])
        self.assertTrue(record['certificate_refinement']['geometry_matched_exactly'])

    def test_false_unchanged_claim_is_not_used_to_classify_changed_geometry_as_padding(self):
        submitted = copy.deepcopy(RECORD)
        submitted['pieces'][0][0] += 1e-9
        submitted['found_by'] = 'New constructor'
        submitted['source_refinement'] = {'pieces_unchanged': True}
        result, written, _, _, _ = self.run_batch(b'', [RECORD], raw_body=body(submitted))
        record = next(iter(written.values()))
        self.assertEqual(record['contribution']['kind'], 'construction')
        self.assertNotIn('certificate_refined_by', record)
        self.assertEqual(record['found_by'], 'New constructor')

    def test_checked_matching_origin_is_found_even_when_another_geometry_is_the_current_best(self):
        with tempfile.TemporaryDirectory(prefix='packing-origin-') as directory:
            root = Path(directory)
            filename = root / 'records/external/original.json'
            filename.parent.mkdir(parents=True)
            original = copy.deepcopy(RECORD)
            original.update(found_by='Trusted earlier author', s_full=RECORD['s_full'] + .01)
            filename.write_text(json.dumps(original), encoding='utf-8')
            filename.with_suffix('.certify.txt').write_text('CERTIFIED', encoding='utf-8')
            registry = root / 'docs/external_records.json'; registry.parent.mkdir(parents=True)
            registry.write_text(json.dumps({'entries': [{'kind': 'coordinates', 'problem': 'cubincub', 'n': 2,
                                                         'file': 'records/external/original.json'}]}), encoding='utf-8')
            current = copy.deepcopy(RECORD); current['pieces'][0][0] += 1e-9
            row = {'rec': RECORD, 'pid': 'cubincub', 'current': current, 'current_file': 'records/another.json'}
            api = SimpleNamespace(ROOT=str(root), load_json=submission.load_json)
            predecessor, source = submission_runner.trusted_geometry_predecessor(api, row)
            self.assertEqual(predecessor['found_by'], 'Trusted earlier author')
            self.assertEqual(source, 'records/external/original.json')
            filename.with_suffix('.certify.txt').write_text('NOT CERTIFIED', encoding='utf-8')
            self.assertEqual(submission_runner.trusted_geometry_predecessor(api, row), (None, None))

    def test_large_scale_density_and_tiny_quaternion_proposals_do_not_overflow_or_underflow(self):
        submitted = {key: copy.deepcopy(RECORD[key]) for key in ('piece', 'container', 'n', 's_full', 'pieces')}
        submitted['s_full'] = 1e120
        for piece in submitted['pieces']: piece[3:] = [1e-300, 0, 0, 0]
        predecessor = copy.deepcopy(submitted); predecessor['s_full'] = 1e121
        result, written, _, _, _ = self.run_batch(b'', [predecessor], raw_body=body(submitted))
        self.assertEqual(result['summary']['accepted'], 1)
        record = next(iter(written.values()))
        self.assertEqual(record['density'], 0.0)  # physical density underflows safely; certification does not
        self.assertEqual(record['pieces'], submitted['pieces'])

    def test_check_mode_stale_body_state_and_labels_are_refused_before_mutation(self):
        event = {'issue': {'body': 'Reviewed packing'}}
        current = {'body': 'Reviewed packing', 'state': 'open', 'labels': [{'name': 'submission'}]}
        submission_event_guard.ensure_issue_current(event, current, 'check')
        for change in ({'body': 'Edited packing'}, {'state': 'closed'}, {'labels': []}, {'labels': [{'name': 'submission'}, {'name': 'accepted'}]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                submission_event_guard.ensure_issue_current(event, {**current, **change}, 'check')
        with self.assertRaises(ValueError):
            submission_event_guard.ensure_issue_current(event, current, 'accept')
        submission_event_guard.ensure_issue_current(event, {**current, 'labels': [{'name': 'submission'}, {'name': 'accepted'}]}, 'accept')

    def test_frames_outside_float_proposal_domain_are_rejected_before_checking(self):
        for change in ({'s_full': 1e151}, {'container_center': [1e151, 0, 0]},
                       {'pieces': [[1e151, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0]]}):
            candidate = copy.deepcopy(RECORD); candidate.update(change)
            with self.subTest(change=change), self.assertRaises(submission.Bad):
                submission.parse_object(candidate, {})

    def test_unsafe_zip_and_bad_manifest_hash_do_not_certify(self):
        with self.assertRaises(submission_batch.BatchError):
            submission_batch.archive_records(archive([RECORD], {'../outside.json': '{}'}), URL)
        source = io.BytesIO()
        with zipfile.ZipFile(source, 'w') as z:
            z.writestr('records/a.json', json.dumps(RECORD))
            z.writestr('MANIFEST.json', json.dumps({'count': 1, 'cases': [{'file': 'records/a.json', 'sha256': '0' * 64}]}))
        rows, _ = submission_batch.archive_records(source.getvalue(), URL)
        self.assertEqual(len(rows), 1)
        self.assertIn('SHA-256', rows[0]['error'])
        self.assertNotIn('object', rows[0])

    def test_redirect_and_archive_limit_guards_reject_unknown_hosts(self):
        self.assertFalse(submission_batch.allowed_download('http://github.com/user-attachments/files/1/a.zip'))
        self.assertFalse(submission_batch.allowed_download('https://github.com@localhost/a.zip'))
        self.assertFalse(submission_batch.allowed_download('https://example.org/a.zip'))
        with patch.object(submission_batch, 'MAX_RECORDS', 1), self.assertRaises(submission_batch.BatchError):
            submission_batch.archive_records(archive([RECORD, RECORD3]), URL)

    def test_deferred_batch_explicitly_reports_unchecked_candidates(self):
        with patch.object(submission_runner, 'MAX_SECONDS', -1):
            result, written, _, _, comment = self.run_batch(archive([RECORD3]), [RECORD, RECORD3], mode='check')
        self.assertEqual(result['summary']['discovered'], 2)
        self.assertEqual(result['summary']['processed'], 0)
        self.assertEqual(result['summary']['deferred'], 2)
        self.assertEqual(written, {})
        self.assertFalse(result['complete'])
        self.assertIn('needs-fix', result['labels_add'])


if __name__ == '__main__': unittest.main()
