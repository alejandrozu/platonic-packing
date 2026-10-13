"""Submission checks run real certifiers; acceptance writes only an isolated temporary record tree.

Run: python -X utf8 -m unittest discover -s tests -p test_submission.py -v
No GitHub API, issue, comment, git push or live record is touched.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('submission', ROOT / 'scripts/check_submission.py')
submission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(submission)
RECORD = json.loads((ROOT / 'records/cubincub/cubincub_n02.json').read_text(encoding='utf-8'))


def body(record, permission=True):
    return '\n\n'.join([
        '### Problem\n\ncubincub', f'### Number of pieces\n\n{len(record["pieces"])}',
        f'### Container scale s\n\n{record["s_full"]}',
        '### Packing\n\n```json\n' + json.dumps(record) + '\n```',
        '### Credit\n\nExample contributor', '### How you found it\n\nFixture method',
        '### Permission\n\n- [' + ('x' if permission else ' ') + '] It may be published under the MIT license.'
    ])


class SubmissionTests(unittest.TestCase):
    def evaluate(self, record=None, mode='check', authorized=False, permission=True, current=None, raw_body=None):
        with tempfile.TemporaryDirectory(prefix='packing-submission-') as directory:
            root = Path(directory)
            if current:
                target = root / 'records/cubincub/cubincub_n02.json'
                target.parent.mkdir(parents=True)
                target.write_text(json.dumps(current), encoding='utf-8')
            event = {
                'action': 'labeled' if mode == 'accept' else 'opened', 'label': {'name': 'accepted'},
                'sender': {'login': 'example-maintainer'},
                'issue': {'number': 123, 'html_url': 'https://example.invalid/issues/123',
                          'user': {'login': 'example-contributor'}, 'body': raw_body or body(record or RECORD, permission)}
            }
            event_file, output = root / 'event.json', root / 'out'
            event_file.write_text(json.dumps(event), encoding='utf-8')

            def real_certifier(cmd, timeout):
                # ROOT redirects record writes to the fixture, while certifiers still read their real solid library.
                command = [cmd[0], '-X', 'utf8', str(ROOT / cmd[1]), *cmd[2:]]
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
                return result.returncode, (result.stdout + result.stderr).strip()

            with patch.object(submission, 'ROOT', str(root)), patch.object(submission, 'run', real_certifier), \
                    patch.object(sys, 'argv', ['check_submission.py', mode, str(event_file), str(output)]), \
                    patch.dict(os.environ, {'SUBMISSION_CAN_ACCEPT': '1' if authorized else ''}):
                submission.main()
            result = json.loads((output / 'result.json').read_text(encoding='utf-8'))
            comment = (output / 'comment.md').read_text(encoding='utf-8')
            accepted_file = root / 'records/cubincub/cubincub_n02.json'
            accepted = json.loads(accepted_file.read_text(encoding='utf-8')) if result['accepted'] else None
            cert = accepted_file.with_suffix('.certify.txt').read_text(encoding='utf-8') if accepted else None
            log = (root / 'records/CONTRIBUTIONS.md').read_text(encoding='utf-8') if accepted else None
            return result, comment, accepted, cert, log

    def test_existing_record_is_exactly_certified_and_compared(self):
        result, comment, accepted, *_ = self.evaluate(current=RECORD)
        self.assertEqual(result['labels_add'], ['certified'])
        self.assertFalse(result['accepted'])
        self.assertIn('VALID', comment)
        self.assertIn('CERTIFIED', comment)
        self.assertIn('equal', comment)
        self.assertIsNone(accepted)

    def test_overlap_is_rejected_by_real_float_and_exact_checks(self):
        record = copy.deepcopy(RECORD)
        record['pieces'][1] = record['pieces'][0][:]
        result, comment, *_ = self.evaluate(record)
        self.assertEqual(result['labels_add'], ['not-certified'])
        self.assertIn('FAIL pair', comment)
        self.assertIn('NOT CERTIFIED', comment)
        self.assertFalse(result['accepted'])

    def test_malformed_fields_fail_before_certification(self):
        changes = [{'s_full': True}, {'container_center': [0, 0]}, {'container_center': [False, 0, 0]},
                   {'n': 3}, {'pieces': [[0, 0, 0, 0, 0, 0, 0]]}]
        for change in changes:
            record = copy.deepcopy(RECORD)
            record.update(change)
            with self.subTest(change=change), patch.object(submission, 'run', side_effect=AssertionError('Must not certify')):
                with self.assertRaises(submission.Bad):
                    submission.parse(body(record))

    def test_acceptance_without_maintainer_authorization_is_rejected(self):
        result, comment, accepted, *_ = self.evaluate(mode='accept')
        self.assertEqual(result['labels_add'], ['needs-fix'])
        self.assertIn('maintainer', comment)
        self.assertFalse(result['accepted'])
        self.assertIsNone(accepted)

    def test_acceptance_requires_publication_permission(self):
        result, comment, *_ = self.evaluate(mode='accept', authorized=True, permission=False)
        self.assertFalse(result['accepted'])
        self.assertIn('permission checkbox', comment)

    def test_authorized_better_record_keeps_credit_certificate_and_history(self):
        previous = copy.deepcopy(RECORD)
        previous['s_full'] += 0.01
        previous['found_by'] = 'Previous contributor'
        result, comment, record, cert, log = self.evaluate(mode='accept', authorized=True, current=previous)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['labels_add'], ['certified', 'new-record'])
        self.assertEqual(record['found_by'], 'Example contributor')
        self.assertEqual(record['method'], 'Fixture method')
        self.assertEqual(record['source']['submitted_by'], 'example-contributor')
        self.assertEqual(record['previous_record']['found_by'], 'Previous contributor')
        self.assertEqual(record['pieces'], RECORD['pieces'])
        self.assertIn('CERTIFIED', cert)
        self.assertIn('Example contributor', log)
        self.assertIn('Accepted and recorded', comment)

    def test_authorized_equal_record_is_not_overwritten(self):
        result, comment, accepted, *_ = self.evaluate(mode='accept', authorized=True, current=RECORD)
        self.assertFalse(result['accepted'])
        self.assertIsNone(accepted)
        self.assertIn('Not recorded', comment)

    def test_valid_untracked_pair_is_certified_for_manual_category_review(self):
        record = {'piece': 'tetrahedron', 'container': 'cube', 'n': 2, 's_full': 4,
                  'pieces': [[-1, 0, 0, 1, 0, 0, 0], [1, 0, 0, 1, 0, 0, 0]]}
        result, comment, *_ = self.evaluate(record)
        self.assertEqual(result['labels_add'], ['certified'])
        self.assertFalse(result['accepted'])
        self.assertIn('Propose the category', comment)


if __name__ == '__main__':
    unittest.main()
