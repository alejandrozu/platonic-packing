"""Changing deployed assets/data invalidates their browser-cache keys."""
import hashlib
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('versioned_site', ROOT / 'scripts/site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class PageLinks(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.assets = {}
        self.scripts = []
        self.records_version = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.records_version = attrs.get('data-records-version')
        url = attrs.get('src') if tag == 'script' else attrs.get('href') if tag == 'link' else None
        if tag == 'script' and url:
            self.scripts.append(url)
        if url and '/assets/' in url:
            self.assets[Path(urlparse(url).path).name] = url


class CacheVersionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='packing-cache-versions-')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.web, self.output = self.root / 'web', self.root / 'site'
        (self.web / 'assets').mkdir(parents=True)
        (self.output / 'assets').mkdir(parents=True)
        (self.output / 'data').mkdir(parents=True)
        for filename in ('theme.js', 'style.css', 'explorer.js', 'explorer.css', 'contribute.js'):
            (self.web / 'assets' / filename).write_bytes(f'original {filename}\n'.encode())
        (self.output / 'assets/icon.svg').write_bytes(b'<svg/>')
        self.records = self.output / 'data/records.json'
        self.records.write_bytes(b'{"records":[{"s":3.9}]}')
        self.web_patch, self.output_patch = patch.object(site, 'WEB', str(self.web)), patch.object(site, 'OUT', str(self.output))
        self.web_patch.start(); self.output_patch.start()
        self.addCleanup(self.web_patch.stop); self.addCleanup(self.output_patch.stop)

    def page(self, script='explorer.js', styles=('explorer.css',), depth=1):
        return PageLinks(site.page('test/', 'Test', 'Test', '<p>Test</p>', '',
                                  scripts=('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js', script),
                                  styles=styles, depth=depth))

    def test_all_local_assets_have_stable_content_versions_on_both_page_depths(self):
        for depth in (0, 1):
            with self.subTest(depth=depth):
                links = self.page(depth=depth)
                self.assertEqual(set(links.assets), {'theme.js', 'style.css', 'icon.svg', 'explorer.css', 'explorer.js'})
                for filename, url in links.assets.items():
                    self.assertEqual(len(parse_qs(urlparse(url).query)['v'][0]), 16)
                    self.assertTrue(url.startswith('./assets/' if depth == 0 else '../assets/'))
                self.assertEqual(links.assets, self.page(depth=depth).assets)
                self.assertIn('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js', links.scripts)

    def test_changing_each_asset_changes_its_own_url(self):
        for filename in ('theme.js', 'style.css', 'explorer.js', 'explorer.css', 'icon.svg'):
            with self.subTest(filename=filename):
                before = self.page().assets
                path = (self.output if filename == 'icon.svg' else self.web) / 'assets' / filename
                path.write_bytes(path.read_bytes() + b'changed\n')
                after = self.page().assets
                self.assertNotEqual(before[filename], after[filename])
                self.assertEqual({k: v for k, v in before.items() if k != filename},
                                 {k: v for k, v in after.items() if k != filename})

    def test_data_version_matches_written_bytes_and_changes_on_record_updates(self):
        before = self.page()
        self.assertEqual(before.records_version, hashlib.sha256(self.records.read_bytes()).hexdigest()[:16])
        self.records.write_bytes(b'{"records":[{"s":3.82}]}')
        after = self.page()
        self.assertNotEqual(before.records_version, after.records_version)
        self.assertEqual(after.records_version, hashlib.sha256(self.records.read_bytes()).hexdigest()[:16])
        self.assertEqual(before.assets, after.assets)

    def test_contribution_client_gets_the_same_data_version(self):
        explorer, contribute = self.page(), self.page(script='contribute.js', styles=())
        self.assertEqual(explorer.records_version, contribute.records_version)
        self.assertIn('contribute.js', contribute.assets)
        self.assertEqual(explorer.assets['theme.js'], contribute.assets['theme.js'])
        self.assertEqual(explorer.assets['style.css'], contribute.assets['style.css'])


if __name__ == '__main__':
    unittest.main()
