"""Exercise the real website builder against the independent source registry.

No network or publication occurs. The imported poses have separate exact and
float-certifier receipts; this checks that the viewer chooses and credits them
without replacing catalogue-only animations with unrelated 3D coordinates.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('packing_site', ROOT / 'scripts/site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class ExternalRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live_data = site.load()
        # Selection tests use a controlled project baseline. The autonomous
        # search can legitimately beat today's external records tomorrow;
        # that must not make a successful record update fail CI.
        cls.fixture = tempfile.TemporaryDirectory(prefix='packing-external-selection-')
        fixture_root = Path(cls.fixture.name)
        coordinate_files = [
            'cubincub/cubincub_n11_hyra.json', 'cubincub/cubincub_n12_hyra.json',
            'cubincub/cubincub_n12_nakajima.json', 'cubincub/cubincub_n34_ryxu.json',
            'cubincub/cubincub_n35_ryxu.json', 'cubincub/cubincub_n36_ryxu.json',
            'octincub/octincub_n17_kamp.json', 'octincub/octincub_n21_hyra.json',
            'octincub/octincub_n24_hyra.json',
        ]
        entries, cases = [], set()
        for relative in coordinate_files:
            relative = 'records/external/' + relative
            path = ROOT / relative
            record = json.loads(path.read_text(encoding='utf-8'))
            pid, n = record['record_id'].split('_')[0], record['n']
            cases.add((pid, n))
            entries.append({'problem': pid, 'n': n, 'kind': 'coordinates', 'file': relative,
                            'published_value': record['source']['published_s_full'],
                            'author': record['found_by'], 'url': record['source']['url']})
            for suffix in ('.json', '.certify.txt', '.verify.txt'):
                target = fixture_root / Path(relative).with_suffix(suffix)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path.with_suffix(suffix), target)
        catalogue = [('cubincub', 13, 2.95600, 'Erich Friedman'),
                     ('cubincub', 33, 3.7071067811865475, 'Erich Friedman'),
                     ('octincub', 11, 2.19540, 'Ríain Walsh'),
                     ('octincub', 12, 2.25949, 'Haowei Lin'),
                     ('octincub', 17, 2.47487, 'Haowei Lin'),
                     ('octincub', 23, 2.61533, 'Ríain Walsh')]
        for pid, n, value, author in catalogue:
            cases.add((pid, n))
            url = f'https://erich-friedman.github.io/packing/{pid}/'
            entries.append({'problem': pid, 'n': n, 'kind': 'catalogue', 'published_value': value,
                            'author': author, 'url': url, 'image_url': url + 'fixture.gif',
                            'value_precision': 'controlled published-source fixture'})
        cases.add(('cubincub', 28))
        entries.append({'problem': 'cubincub', 'n': 28, 'kind': 'author_report', 'published_value': 3.666,
                        'author': '紺葉 (@konoha_ily2)', 'url': 'https://x.com/konoha_ily2/status/2109306733999120589',
                        'image_url': None, 'value_precision': 'controlled author-report fixture'})
        for pid, n in cases:
            relative = f'records/{pid}/{pid}_n{n:02d}.json'
            baseline = json.loads((ROOT / relative).read_text(encoding='utf-8'))
            published = [e['published_value'] for e in entries if e['problem'] == pid and e['n'] == n]
            baseline['s_full'] = max(baseline['s_full'], *published) + 0.2
            baseline['s_plus'] = f'{baseline["s_full"]:.5f}+'
            baseline['s_tight'] = None
            target = fixture_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(baseline), encoding='utf-8')
            # Only selection/status is exercised here. The imported geometry has
            # real checker receipts; the controlled larger baseline is a fixture.
            target.with_suffix('.certify.txt').write_text('CERTIFIED\n', encoding='utf-8')
            target.with_suffix('.verify.txt').write_text('VALID\n', encoding='utf-8')
        with patch.object(site, 'ROOT', str(fixture_root)), patch.object(site, 'EXTERNAL', {'entries': entries}), patch.object(site, 'COMMUNITY', {'entries': []}):
            cls.data = site.load()
        cls.problems = {p['id']: p for p in cls.data['problems']}
        cls.rows = [r for p in cls.data['problems'] for r in p['rows']]

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

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
        rows = [r for p in self.live_data['problems'] for r in p['rows']]
        visible = {r['file'] for r in rows if r['file']}
        visible.update(a['file'] for r in rows for a in r.get('alternatives', []))
        original = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'records').glob('*/*_n[0-9][0-9].json')}
        self.assertTrue(original)
        self.assertEqual(original - visible, set())
        for p in self.live_data['problems']:
            self.assertEqual(len(p['rows']), len({r['n'] for r in p['rows']}))

    def test_selected_coordinates_are_smallest_of_available_coordinates(self):
        for row in [r for p in self.live_data['problems'] for r in p['rows']]:
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
        stats = site.stats(self.live_data)
        rows = [r for p in self.live_data['problems'] for r in p['rows']]
        source_only = sum(bool(r.get('source_only')) for r in rows)
        self.assertEqual(stats['source_only'], source_only)
        self.assertEqual(stats['certified'], sum(bool(r['ok']) for r in rows))
        self.assertGreaterEqual(stats['records'] - stats['certified'], stats['source_only'])
        summary = site.cert_sentence(stats)
        if source_only:
            self.assertIn('no coordinates or local certificate', summary)
        else:
            self.assertIn('certified exactly', summary)

    def test_all_platonic_combinations_are_registered(self):
        names = ('tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron')
        pairs = {(p['piece'], p['container']) for p in self.live_data['problems'] if p['family'] == 'platonic'}
        self.assertEqual(pairs, {(a, b) for a in names for b in names})

    def test_truncated_catalogue_value_is_not_a_finer_bound(self):
        self.assertEqual(site.compare(2.956147020837, 2.956, .001), 'equal')
        with patch.object(site, 'ROOT', self.fixture.name), patch.object(site, 'COMMUNITY', {'entries': []}), patch.object(site, 'EXTERNAL', {
            'entries': [{'problem': 'cubincub', 'n': 13, 'published_value': 2.956, 'kind': 'catalogue',
                         'author': 'Erich Friedman', 'url': 'https://erich-friedman.github.io/packing/cubincub/',
                         'display_quantum': .001, 'value_precision': 'three decimal truncation'}]}):
            path = Path(self.fixture.name) / 'records/cubincub/cubincub_n13.json'
            saved = path.read_text(encoding='utf-8')
            r = json.loads(saved); r['s_full'] = 2.956147020837
            try:
                path.write_text(json.dumps(r), encoding='utf-8')
                data = site.load()
            finally:
                path.write_text(saved, encoding='utf-8')
        selected = next(r for p in data['problems'] if p['id'] == 'cubincub' for r in p['rows'] if r['n'] == 13)
        self.assertFalse(selected.get('source_only', False))
        self.assertEqual(selected['cmp'], 'equal')

    def test_translated_container_is_recentered_only_for_display(self):
        native = {'container_center': ['1/4', 2, -3], 'pieces': [['5/4', 4, -2, 1, 0, 0, 0]]}
        self.assertEqual(site.viewer_pieces(native), [[1, 2, 1, 1, 0, 0, 0]])
        self.assertEqual(native['pieces'][0][0], '5/4')

    def test_imported_source_urls_allow_only_public_web_links(self):
        for unsafe in ('javascript:alert(1)', 'data:text/html,x', 'https://user:secret@example.com/a', 'file:///C:/test'):
            self.assertIsNone(site.public_url(unsafe))
        self.assertEqual(site.public_url('https://example.com/a#proof'), 'https://example.com/a#proof')

    def test_accepted_piece_counts_expand_the_visible_table_range(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            for n in (1, 41):
                r = json.loads((ROOT / 'records/cubincub/cubincub_n13.json').read_text(encoding='utf-8'))
                r.update(n=n, record_id=f'cubincub_n{n:02d}', pieces=[r['pieces'][0]] * n)
                p = root / f'records/cubincub/cubincub_n{n:02d}.json'
                p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(r), encoding='utf-8')
            with patch.object(site, 'ROOT', dirname), patch.object(site, 'COMMUNITY', {'entries': []}), patch.object(site, 'EXTERNAL', {'entries': []}):
                data = site.load()
        self.assertEqual((data['nmin'], data['nmax']), (1, 41))


if __name__ == '__main__':
    unittest.main()
