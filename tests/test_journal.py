"""Scientific status, source identity and stable journal navigation boundaries."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import journal


class JournalTests(unittest.TestCase):
    def test_cover_source_and_artwork_bytes_match_the_provenance(self):
        provenance=json.loads((ROOT/'docs/journal/cover-provenance.json').read_text(encoding='utf8'))
        paths={'q4-2026-cover.svg':'web/assets/journal-cover-q4-2026.svg',
               'q4-2026-cover.png':'web/assets/journal-cover-q4-2026.png',
               'render_cover.py':'docs/journal/cover/render_cover.py',
               'icoinico_n16.json':'docs/journal/cover/icoinico_n16.json',
               'icosahedron-geometry.json':'docs/journal/cover/icosahedron-geometry.json'}
        for name,path in paths.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),provenance['files'][name])

    def test_launch_cannot_silently_claim_peer_review_acceptance(self):
        data = journal.load_catalogue(ROOT)
        self.assertEqual(data['issue']['accepted_articles'], 0)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'docs/journal').mkdir(parents=True)
            data['papers'][0]['accepted_by_journal'] = True
            (root/'docs/journal/papers.json').write_text(json.dumps(data), encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'independently accepted'):
                journal.load_catalogue(root)

    def test_desktop_version_is_immutable_and_the_joatp_doi_is_not_reassigned(self):
        data = journal.load_catalogue(ROOT)
        papers = {p['id']:p for p in data['papers']}
        patterns = papers['patterns-2026-11-08']
        pdf = ROOT/'web/journal/downloads/patterns-2026-11-08.pdf'
        self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(), patterns['pdf_sha256'])
        self.assertEqual(patterns['pages'], 21)
        joatp = papers['architecture-transfer']
        self.assertNotIn('doi', joatp)
        self.assertIn('no independent external referee review', joatp['review_status'])
        self.assertIn('uncalibrated', joatp['summary'])
        self.assertIn('23629684', joatp['related_links'][0]['url'])
        self.assertIn('konoha-ily2', joatp['record_lineage'])
        self.assertIn('Zarzuelo Urdiales, Alejandro', journal.bibtex(patterns))

    def test_rejects_unsafe_links_and_preserves_source_attribution(self):
        for value in ('javascript:alert(1)','http://example.org/','https://user:password@example.org/','/local'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                journal.web_url(value)
        item = dict(id='test',title='<script>x</script> & {title}',authors=['A & B'],
                    group='project',kind='Preprint',date='2026',summary='<img src=x>',
                    url='https://example.org/',review_status='Preprint')
        self.assertNotIn('<script>',journal.card(item))
        self.assertIn(r'\{title\}',journal.bibtex(item))
        item['date']='Undated'
        self.assertNotIn('year =',journal.bibtex(item))

    def test_all_catalogue_entries_have_individual_pages_and_citations(self):
        data=journal.load_catalogue(ROOT)
        def page(path,title,desc,body,active,**kwargs):
            return '<html><head></head><body>'+body+'</body></html>'
        def fill(body,values,root):
            return body.replace('{{ROOT}}',root).replace('{{REPO}}','https://github.com/alejandrozu/platonic-packing').replace('{{TOC}}','')
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)
            urls=journal.build_journal(ROOT,out,'https://github.com/alejandrozu/platonic-packing',
                'https://polyhedrainpolyhedra.wiki/',page,fill)
            self.assertEqual(len(urls),len(data['papers'])+3)
            for item in data['papers']:
                content=(out/'journal/articles'/item['id']/'index.html').read_text(encoding='utf8')
                self.assertIn(journal.esc(item['review_status']),content)
                self.assertTrue((out/'journal/citations'/(item['id']+'.bib')).is_file())
                if item['group'] in ('project','literature','background'):
                    self.assertIn('citation_author',content)
                    self.assertIn('application/ld+json',content)
                else:
                    self.assertNotIn('citation_title',content)
            self.assertTrue((out/'journal/downloads/patterns-2026-11-08.pdf').is_file())
            self.assertIn('is in progress',(out/'journal/issues/2026-q4/index.html').read_text(encoding='utf8'))


if __name__=='__main__':
    unittest.main()
