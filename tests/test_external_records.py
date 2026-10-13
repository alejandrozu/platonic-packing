"""Exercise the real website builder against the independent source registry.

No network or publication occurs. The imported poses have separate exact and
float-certifier receipts; this checks that the viewer chooses and credits them
without replacing catalogue-only animations with unrelated 3D coordinates.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('packing_site', ROOT / 'scripts/site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class ExternalRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = site.load()
        cls.problems = {p['id']: p for p in cls.data['problems']}
        cls.rows = [r for p in cls.data['problems'] for r in p['rows']]

    def row(self, pid, n):
        return next(r for r in self.problems[pid]['rows'] if r['n'] == n)

    def test_smaller_independent_cube_poses_are_selected_and_credited(self):
        for n, upper in [(34, 3.823), (35, 3.861), (36, 3.895)]:
            with self.subTest(n=n):
                row = self.row('cubincub', n)
                self.assertEqual(row['who'], 'Ryan Xu')
                self.assertTrue(row['external'])
                self.assertTrue(row['ok'])
                self.assertTrue(row['ver'])
                self.assertLess(row['sf'], upper)
                self.assertEqual(len(row['p']), n)
                self.assertIn('9535d65d84cc33f20f4e26329f8da12bdcef216e', row['source_url'])
                self.assertTrue(any(a['file'] == f'records/cubincub/cubincub_n{n:02d}.json' for a in row['alternatives']))

    def test_catalogue_best_has_no_fake_geometry_or_certificate(self):
        for pid, n, author in [('cubincub', 13, 'Erich Friedman'), ('cubincub', 33, 'Erich Friedman'),
                               ('octincub', 11, 'Ríain Walsh'), ('octincub', 12, 'Haowei Lin'),
                               ('octincub', 17, 'Haowei Lin'), ('octincub', 23, 'Ríain Walsh')]:
            with self.subTest(pid=pid, n=n):
                row = self.row(pid, n)
                self.assertEqual(row['who'], author)
                self.assertTrue(row['source_only'])
                self.assertEqual(row['p'], [])
                self.assertEqual(row['cert'], [])
                self.assertFalse(row['ok'])
                self.assertFalse(row['ver'])
                self.assertIsNone(row['file'])
                self.assertTrue(row['image_url'].startswith('https://erich-friedman.github.io/packing/'))
                self.assertTrue(all(a['ok'] and a['file'] and len(a['p']) == n for a in row['alternatives']))
                self.assertLess(row['sf'], min(a['sf'] for a in row['alternatives']) - 1e-5)

    def test_author_report_is_explicit_and_has_no_claimed_local_certificate(self):
        row = self.row('cubincub', 28)
        self.assertTrue(row['author_report'])
        self.assertTrue(row['source_only'])
        self.assertFalse(row['ok'])
        self.assertEqual(row['p'], [])
        self.assertIsNone(row['image_url'])
        self.assertEqual(row['who'], '紺葉 (@konoha_ily2)')
        self.assertEqual(row['source_url'], 'https://x.com/konoha_ily2/status/2109306733999120589')

    def test_every_original_record_remains_accessible(self):
        visible = {r['file'] for r in self.rows if r['file']}
        visible.update(a['file'] for r in self.rows for a in r.get('alternatives', []))
        original = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'records').glob('*/*_n[0-9][0-9].json')}
        self.assertTrue(original)
        self.assertEqual(original - visible, set())
        for p in self.data['problems']:
            self.assertEqual(len(p['rows']), len({r['n'] for r in p['rows']}))

    def test_selected_coordinates_are_smallest_of_available_coordinates(self):
        for row in self.rows:
            candidates = [row, *row.get('alternatives', [])]
            if row.get('source_only'):
                continue
            with self.subTest(id=row['id']):
                self.assertEqual(row['sf'], min(c['sf'] for c in candidates if c['file']))

    def test_frozen_sources_and_import_receipts_match_author_credit(self):
        for entry in site.EXTERNAL['entries']:
            if entry['kind'] != 'coordinates':
                continue
            with self.subTest(file=entry['file']):
                path = ROOT / entry['file']
                record = json.loads(path.read_text(encoding='utf-8'))
                source = record['source']
                self.assertEqual(record['found_by'], entry['author'])
                self.assertEqual(record['source']['url'], entry['url'])
                self.assertEqual(len(record['pieces']), entry['n'])
                self.assertIsNone(record['s_tight'])
                self.assertEqual(hashlib.sha256((ROOT / source['source_file']).read_bytes()).hexdigest(), source['sha256'])
                certificate = path.with_suffix('.certify.txt').read_text(encoding='utf-8')
                self.assertIn('CERTIFIED', certificate)
                self.assertNotIn('NOT CERTIFIED', certificate)
                self.assertIn('VALID', path.with_suffix('.verify.txt').read_text(encoding='utf-8'))
                self.assertNotIn('INVALID', path.with_suffix('.verify.txt').read_text(encoding='utf-8'))

    def test_summary_does_not_call_source_only_entries_certified(self):
        stats = site.stats(self.data)
        self.assertEqual(stats['source_only'], 12)
        self.assertEqual(stats['records'] - stats['certified'], stats['source_only'])
        summary = site.cert_sentence(stats)
        self.assertIn('no coordinates or local certificate', summary)


if __name__ == '__main__':
    unittest.main()
