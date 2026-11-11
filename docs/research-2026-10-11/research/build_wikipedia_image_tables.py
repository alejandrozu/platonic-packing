"""Build source-linked image tables in the local Markdown and MediaWiki draft.

No upload or publication is performed. Without --commons-map, MediaWiki image
slots are hidden comments with public preview links. Optional map format:
{"files": {"tetintet_n02": {"filename": "Actual uploaded file.png"}}}
Every supplied filename is checked through the public Commons API for existence,
matching file bytes, and a free license before ordinary File markup is emitted.
The two source-catalogue diagrams also require rights_evidence_url in the map.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

SAME = [('tetintet', 'Tetrahedra in tetrahedron'), ('cubincub', 'Cubes in cube'),
        ('octinoct', 'Octahedra in octahedron'), ('dodindod', 'Dodecahedra in dodecahedron'),
        ('icoinico', 'Icosahedra in icosahedron')]
DUAL = [('cubinoct', 'Cubes in octahedron'), ('octincub', 'Octahedra in cube'),
        ('dodinico', 'Dodecahedra in icosahedron'), ('icoindod', 'Icosahedra in dodecahedron')]
GITHUB = 'https://github.com/alejandrozu/platonic-packing/blob/docs/polyhedral-fit-papers-2026-10-11/docs/research-2026-10-11/'
ATLAS = 'https://alejandrozu.github.io/platonic-packing/#'
METHODS = 'https://doi.org/10.5281/zenodo.23306098'
PATTERNS = 'https://doi.org/10.5281/zenodo.23306126'
DATA = 'https://doi.org/10.5281/zenodo.23306130'
SOURCE_ONLY = {'octincub_n11', 'octincub_n12'}

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def attribution_code(c):
    if c['problem'] == 'cubincub':
        return 'G' if c['n'] <= 8 else 'F/Z' if c['n'] <= 10 else 'L→Z' if c['n'] == 11 else 'N/Z'
    if c['problem'] == 'octincub':
        return 'W/Z' if c['n'] <= 10 else 'W' if c['n'] == 11 else 'L'
    return 'Z'

def short_credit(c):
    return {'G': 'Grid', 'F/Z': 'Friedman / Zarzuelo Urdiales',
            'L→Z': 'Lin → Zarzuelo Urdiales', 'N/Z': 'Nakajima / Zarzuelo Urdiales',
            'W/Z': 'Walsh / Zarzuelo Urdiales', 'W': 'Walsh', 'L': 'Lin',
            'Z': 'Zarzuelo Urdiales'}[attribution_code(c)]

def table_matches(text, wiki=False):
    pattern = r'^\{\| class="wikitable"[^\n]*\n.*?^\|\}' if wiki else r'^\| n \|[^\n]*\n(?:\|[^\n]*\n)+'
    return list(re.finditer(pattern, text, re.M | re.S if wiki else re.M))

def replace_tables(text, tables, wiki=False):
    matches = table_matches(text, wiki)
    if len(matches) != 2:
        raise RuntimeError(f'Expected two result tables; found {len(matches)}')
    for match, table in reversed(list(zip(matches, tables))):
        text = text[:match.start()] + table + ('' if wiki else '\n') + text[match.end():]
    return text

def non_table_text(text, wiki=False):
    text = re.sub(r'<!-- PACKING_INFOBOX_START -->.*?<!-- PACKING_INFOBOX_END -->\s*', '', text, flags=re.S)
    text = re.sub(r'<!-- PACKING_(?:SAME|DUAL)_SOURCE_NOTE_START -->.*?<!-- PACKING_(?:SAME|DUAL)_SOURCE_NOTE_END -->\s*', '', text, flags=re.S)
    text = re.sub(r"^(?:\*\*|''')(?:Attribution and precision key|Precision and construction evidence)\.(?:\*\*|''').*$", '', text, flags=re.M)
    text = text.replace('The attribution key identifies those differences and the provenance of imported or reproduced constructions.', 'The per-table source notes identify the construction origins and the provenance of imported or reproduced results.')
    text = re.sub(r'<math>s\^\'\'\(n\)\\le s\^\'\'\(n\+1\)</math>', '<math>s^*(n)\\\\le s^*(n+1)</math>', text)
    for match in reversed(table_matches(text, wiki)):
        text = text[:match.start()] + '<RESULT_TABLE>' + text[match.end():]
    return re.sub(r'\s+', ' ', text).strip()

def add_source_notes(text, wiki=False):
    """Put a compact attribution note below each table, never in result cells."""
    text = re.sub(r'<!-- PACKING_(?:SAME|DUAL)_SOURCE_NOTE_START -->.*?<!-- PACKING_(?:SAME|DUAL)_SOURCE_NOTE_END -->\s*', '', text, flags=re.S)
    def link(label, url):
        return f'[{url} {label}]' if wiki else f'[{label}]({url})'
    zarzuelo = link('Zarzuelo Urdiales', METHODS)
    friedman = link('Friedman', 'https://erich-friedman.github.io/packing/cubincub/')
    lin = link('Lin', 'https://github.com/Tencent-Hunyuan/Hyra-results/tree/09b2d2e3c362c67a78f544c836bd8e4b54a05527/AI4Science/packing_records')
    nakajima = link('Nakajima', 'https://github.com/yoheinakajima/soft-to-rigid-packing/blob/efe7a920142350a4f0678633490c3e3dbed71fa0/paper/main.pdf')
    walsh = link('Walsh', 'https://erich-friedman.github.io/packing/octincub/')
    lin_oct = link('Lin', 'https://erich-friedman.github.io/packing/octincub/')
    same = f'<small>Construction sources: {zarzuelo} for all non-cube columns and the refinements/reproductions below. Cubes: n=2–8, grid; n=9–10, {friedman}; n=11, {lin} seed, refined; n=12, {nakajima} family, reproduced.</small>'
    dual = f'<small>Construction sources: {zarzuelo} for cubes in octahedra and both dodecahedron–icosahedron directions. Octahedra in cubes: n=2–11, {walsh} (n=2–10 independently certified here); n=12, {lin_oct}.</small>'
    for match, kind, note in reversed(list(zip(table_matches(text,wiki), ['SAME','DUAL'], [same,dual]))):
        if wiki:
            note = '<div class="mw-collapsible mw-collapsed">\n<small>Construction attribution</small>\n<div class="mw-collapsible-content">\n' + note + '\n</div>\n</div>'
        block = f'\n\n<!-- PACKING_{kind}_SOURCE_NOTE_START -->\n{note}\n<!-- PACKING_{kind}_SOURCE_NOTE_END -->\n'
        text = text[:match.end()].rstrip('\n') + block + text[match.end():]
    return text

def rewrite_precision_key(text, wiki=False):
    prefix = "'''Precision and construction evidence.'''" if wiki else '**Precision and construction evidence.**'
    paragraph = prefix + ' A plus sign marks a truncated source decimal. Exact stored scales and feasibility certificates are available through the construction links; numerical touching estimates and rounded catalogue reports are separate evidence. The source notes distinguish original constructions, seed refinements, and independently certified reproductions.'
    pattern = r"^(?:\*\*|''')(?:Attribution and precision key|Precision and construction evidence)\.(?:\*\*|''').*$"
    text, count = re.subn(pattern, lambda _:paragraph, text, flags=re.M)
    assert count == 1
    return text.replace('The attribution key identifies those differences and the provenance of imported or reproduced constructions.', 'The per-table source notes identify the construction origins and the provenance of imported or reproduced results.')

def verify_commons_mapping(mapping_path, image_assets, packet):
    """Read-only verification; no Commons request is made without a supplied map."""
    if not mapping_path:
        return {}
    mapping = load(mapping_path).get('files', {})
    unknown = set(mapping) - set(image_assets)
    if unknown:
        raise ValueError(f'Unknown image record IDs: {sorted(unknown)}')
    verified = {}
    for record_id, item in mapping.items():
        if not isinstance(item, dict) or not item.get('filename'):
            raise ValueError('Each mapped record requires an actual filename object.')
        filename = item['filename'].removeprefix('File:')
        if any(character in filename for character in '[]|\n\r'):
            raise ValueError('Invalid Commons filename.')
        if record_id in SOURCE_ONLY and not re.match(r'^https?://', item.get('rights_evidence_url', '')):
            raise ValueError('Catalogue diagrams require independent free-license permission evidence.')
        query = urlencode({'action':'query', 'format':'json', 'prop':'imageinfo',
                           'titles':'File:' + filename, 'iiprop':'url|sha1|extmetadata'})
        request = Request('https://commons.wikimedia.org/w/api.php?' + query,
                          headers={'User-Agent':'PolyhedralPackingDraftVerifier/1.0 (read-only file verification)'})
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        pages = list(result.get('query', {}).get('pages', {}).values())
        if len(pages) != 1 or 'missing' in pages[0] or not pages[0].get('imageinfo'):
            raise ValueError(f'Commons file does not exist: {filename}')
        info = pages[0]['imageinfo'][0]
        local_sha1 = hashlib.sha1((packet/image_assets[record_id]['local_path']).read_bytes()).hexdigest()
        remote_sha1 = info.get('sha1', '')
        if not re.fullmatch(r'[0-9a-f]{40}', remote_sha1):
            remote_sha1 = format(int(remote_sha1, 36), '040x')
        if local_sha1 != remote_sha1:
            raise ValueError(f'Commons file does not match the prepared image bytes: {filename}')
        metadata = info.get('extmetadata', {})
        license_name = html.unescape(metadata.get('LicenseShortName', {}).get('value', ''))
        license_url = html.unescape(metadata.get('LicenseUrl', {}).get('value', ''))
        free = license_name in {'CC BY 4.0', 'CC BY-SA 4.0', 'CC0', 'Public domain'} or 'creativecommons.org/publicdomain/' in license_url
        if not free:
            raise ValueError(f'Commons free-license verification failed: {filename}')
        verified[record_id] = {'filename':filename, 'file_page_url':info.get('descriptionurl'),
                               'sha1':remote_sha1, 'license':license_name,
                               'license_url':license_url,
                               'rights_evidence_url':item.get('rights_evidence_url')}
    return verified

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--commons-map', type=Path)
    args = parser.parse_args()
    packet = args.packet.resolve()
    registry = load(packet/'research/current-records.json')
    cases = {(c['problem'], c['n']):c for c in registry['cases']}
    expected = {(family,n) for family,_ in SAME+DUAL for n in range(2,13)}
    assert set(cases) == expected and len(cases) == 99
    thumbnails = load(packet/'wikipedia-assets/table-thumbnails/thumbnail-manifest.json')
    original_assets = thumbnails['assets']
    thumbnail_assets = original_assets if isinstance(original_assets, dict) else {a['recordID']:a for a in original_assets}
    diagrams = {a['record_id']:a for a in load(packet/'wikipedia-assets/source-diagrams/manifest.json')['assets']}
    image_assets = {}
    for c in cases.values():
        rid = c['recordID']
        if rid in SOURCE_ONLY:
            d = diagrams[rid]
            assert not c.get('configURL') and c['reportedSourceImageURL'] == d['original_source']
            item = {'local_path':'wikipedia-assets/source-diagrams/'+d['png'],
                    'alt_text':f"Original catalogue diagram of {c['n']} octahedra in a cube, credited to {d['credited_construction_author']}.",
                    'image_link_target':d['original_source'], 'sha256':d['png_sha256'],
                    'source_only':True, 'rights':'Unconfirmed source-catalogue copyright; no free-license claim.',
                    'rights_evidence':None, 'construction_author':d['credited_construction_author']}
        else:
            t = thumbnail_assets[rid]
            assert c.get('configURL') and t['constructionURL'] == c['configURL']
            item = {'local_path':'wikipedia-assets/table-thumbnails/'+t['filename'],
                    'alt_text':t['alt_text'], 'image_link_target':ATLAS+rid,
                    'sha256':t['sha256'], 'source_only':False,
                    'rights':'CC BY 4.0', 'rights_evidence':thumbnails['licenseURL'],
                    'illustration_author':thumbnails['author'], 'construction_attribution':c['attribution']}
        assert sha256(packet/item['local_path']) == item['sha256'], f'Image hash mismatch: {rid}'
        item['preview_url'] = GITHUB+item['local_path']
        image_assets[rid] = item
    hero = thumbnails.get('infobox_hero') or thumbnails.get('hero')
    if not hero:
        hero = thumbnail_assets.get('hero-dodindod-n33')
    assert hero and hero['filename'] == 'hero-dodindod-n33.png'
    image_assets['hero-dodindod-n33'] = {'local_path':'wikipedia-assets/table-thumbnails/'+hero['filename'],
        'alt_text':hero['alt_text'], 'image_link_target':ATLAS+'dodindod_n33',
        'sha256':hero['sha256'], 'source_only':False, 'rights':'CC BY 4.0',
        'rights_evidence':thumbnails['licenseURL'], 'illustration_author':thumbnails['author']}
    image_assets['hero-dodindod-n33']['preview_url'] = GITHUB+image_assets['hero-dodindod-n33']['local_path']
    assert sha256(packet/image_assets['hero-dodindod-n33']['local_path']) == hero['sha256']
    verified = verify_commons_mapping(args.commons_map, image_assets, packet)

    def wiki_image(rid):
        item = image_assets[rid]
        alt = item['alt_text'].replace('|','&#124;').replace(']','&#93;')
        if rid in verified:
            filename = verified[rid]['filename']
            size = 'upright=1.1' if rid == 'hero-dodindod-n33' else '140px'
            return f'[[File:{filename}|frameless|{size}|alt={alt}]]'
        comment = f'<!-- packing-image {rid}: local={item["local_path"]}; image-link-target={item["image_link_target"]}; alt={alt}; Commons file not uploaded -->'
        return comment+f'[{item["preview_url"]} Image preview]'

    def cell(c, wiki=False):
        rid = c['recordID']; item = image_assets[rid]
        source = c.get('paperURL') or c['sourceURL']
        value = c['displayValue']
        if wiki:
            prefix = wiki_image(rid) + f'<br />[{source} {value}]<br /><small>'
            links = [f'[{source} source]']
            links += [f'[{item["image_link_target"]} 3D]', f'[{c["configURL"]} construction]'] if c.get('configURL') else [f'[{c["reportedSourceImageURL"]} diagram]',f'[{c["sourceURL"]} catalogue]']
            return prefix+' · '.join(links)+'</small>'
        image = f'[![{item["alt_text"]}]({item["local_path"]})]({item["image_link_target"]})'
        prefix = image + f'<br>[{value}]({source})<br>'
        links = [f'[source]({source})']
        links += [f'[3D]({item["image_link_target"]})', f'[construction]({c["configURL"]})'] if c.get('configURL') else [f'[diagram]({c["reportedSourceImageURL"]})',f'[catalogue]({c["sourceURL"]})']
        return prefix + ' · '.join(links)

    def table(families, wiki=False):
        if wiki:
            caption = 'Identical Platonic particle and container solids' if families == SAME else 'Distinct dual Platonic particle and container solids'
            out = ['{| class="wikitable"', '|+ '+caption+'; container edge / unit particle edge', '! scope="col" | n']
            out += ['! scope="col" | '+label for _,label in families]
            for n in range(2,13):
                out += ['|-', f'! scope="row" | {n}']
                out += ['| style="text-align:center;" | '+cell(cases[(family,n)],True) for family,_ in families]
            out.append('|}')
            return '\n'.join(out)
        out = ['| n | '+' | '.join(label for _,label in families)+' |', '|---:|'+'---|'*len(families)]
        for n in range(2,13):
            out.append('| '+str(n)+' | '+' | '.join(cell(cases[(family,n)]) for family,_ in families)+' |')
        return '\n'.join(out)

    md_path, wiki_path = packet/'wikipedia-polyhedral-fits.md', packet/'wikipedia-polyhedral-fits.wiki'
    before_md, before_wiki = md_path.read_text(encoding='utf-8'), wiki_path.read_text(encoding='utf-8')
    # Original/corrected cells must agree with the source register before replacement.
    for c in cases.values():
        source = c.get('paperURL') or c['sourceURL']
        assert f'[{c["displayValue"]}]({source})' in before_md, c['recordID']
    md = replace_tables(before_md, [table(SAME),table(DUAL)])
    wiki = replace_tables(before_wiki, [table(SAME,True),table(DUAL,True)], True)
    md = rewrite_precision_key(add_source_notes(md))
    wiki = rewrite_precision_key(add_source_notes(wiki,True),True)
    # Restore the one mathematical asterisk damaged by an earlier emphasis converter.
    bad_math = "<math>s^''(n)\\le s^''(n+1)</math>"
    wiki = wiki.replace(bad_math, '<math>s^*(n)\\le s^*(n+1)</math>')
    hero_item = image_assets['hero-dodindod-n33']
    hero_comment = ('<!-- packing-image hero-dodindod-n33: local='+hero_item['local_path']+
                    '; image-link-target='+hero_item['image_link_target']+
                    '; alt='+hero_item['alt_text']+'; Commons file not uploaded -->')
    hero_image = wiki_image('hero-dodindod-n33') if 'hero-dodindod-n33' in verified else hero_comment
    infobox = '\n'.join([
        '<!-- PACKING_INFOBOX_START -->', '{{Infobox', '| title = Finite polyhedral packing',
        '| image = '+hero_image, '| caption = 33 dodecahedra in a dodecahedron',
        '| label1 = Objects', '| data1 = Regular polyhedra',
        '| label2 = Motions', '| data2 = Translation and rotation',
        '| label3 = Objective', '| data3 = Minimum enclosing scale',
        '| label4 = Tables', '| data4 = 2–12 pieces',
        '| label5 = Theory', '| data5 = [https://doi.org/10.1017/CBO9780511546587 Finite packing] · [https://doi.org/10.1016/S0010-4485(01)00109-9 3D layout]',
        '| label6 = Evidence', f'| data6 = [{DATA} Data and certificates]',
        '| label7 = Software', '| data7 = [https://github.com/alejandrozu/platonic-packing Construction repository]',
        '}}', '<!-- PACKING_INFOBOX_END -->', ''])
    wiki = re.sub(r'<!-- PACKING_INFOBOX_START -->.*?<!-- PACKING_INFOBOX_END -->\s*', '', wiki, flags=re.S)
    lead = "'''Polyhedra in polyhedra packing'''"
    assert wiki.count(lead) == 1
    wiki = wiki.replace(lead, infobox+'\n'+lead, 1)
    wiki = re.sub(r'\n{3,}', '\n\n', wiki)
    assert non_table_text(before_md) == non_table_text(md)
    assert non_table_text(before_wiki, True) == non_table_text(wiki, True)
    reference_count = len(re.findall(r'<a id="reference-\d+"', before_md))
    hypothesis_count = len(re.findall(r'^\* \*\*H\d+:', before_md, re.M))
    assert len(re.findall(r'<a id="reference-\d+"', md)) == reference_count
    assert len(set(re.findall(r'<ref name="(r\d+)">',wiki))) == reference_count
    assert len(re.findall(r'^\* \*\*H\d+:', md, re.M)) == hypothesis_count
    assert len(re.findall(r"^\* '''H\d+:", wiki, re.M)) == hypothesis_count
    assert len(table_matches(md)) == len(table_matches(wiki,True)) == 2
    assert len(re.findall(r'^! scope="row" \| ',wiki,re.M)) == 22
    assert len(re.findall(r'^! scope="col" \| ',wiki,re.M)) == 11
    assert not re.search(r'<math[^>]*>[^<]*\'\'[^<]*</math>',wiki)
    assert len(re.findall(r'\[!\[',md)) == 99
    for c in cases.values():
        source = c.get('paperURL') or c['sourceURL']; value = c['displayValue']; rid = c['recordID']
        assert f'[{value}]({source})' in md and f'[{source} {value}]' in wiki
        assert image_assets[rid]['image_link_target'] in md and image_assets[rid]['image_link_target'] in wiki
        if c.get('configURL'):
            assert c['configURL'] in md and c['configURL'] in wiki
        else:
            assert ATLAS+rid not in '\n'.join(m.group() for m in table_matches(md))
    md_path.write_text(md,encoding='utf-8')
    wiki_path.write_text(wiki,encoding='utf-8')
    for rid, asset in image_assets.items():
        asset['commons_eligibility'] = 'EXCLUDED pending free-license permission' if rid in SOURCE_ONLY else 'Author-rendered CC BY 4.0 image; local only, not uploaded'
        asset['native_image_click_target'] = verified[rid]['file_page_url'] if rid in verified else None
        asset['explicit_inspection_link_target'] = asset['image_link_target']
        if rid != 'hero-dodindod-n33':
            case = next(c for c in cases.values() if c['recordID'] == rid)
            asset['construction_attribution_code'] = attribution_code(case)
            asset['construction_attribution'] = case['attribution']
    md_table_text = '\n'.join(m.group() for m in table_matches(md))
    wiki_table_text = '\n'.join(m.group() for m in table_matches(wiki,True))
    assert '<sup>' not in md_table_text + wiki_table_text
    assert all(name not in re.sub(r'<!--.*?-->', '', wiki_table_text, flags=re.S) for name in ['Zarzuelo Urdiales','Friedman','Nakajima'])
    assert md.count('<!-- PACKING_SAME_SOURCE_NOTE_START -->') == md.count('<!-- PACKING_DUAL_SOURCE_NOTE_START -->') == 1
    assert wiki.count('<!-- PACKING_SAME_SOURCE_NOTE_START -->') == wiki.count('<!-- PACKING_DUAL_SOURCE_NOTE_START -->') == 1
    plan = {'date':'2026-10-12', 'publication_status':'Local draft only; no Commons upload performed by this builder.',
            'source_commit':thumbnails['source_commit'], 'table_cells':99,
            'table_image_counts':{'author_rendered_cc_by_4':97,'source_catalogue_rights_unconfirmed':2},
            'additional_infobox_hero':1, 'verified_existing_commons_files':verified,
            'default_wikitext':'Hidden per-image slot comment plus public image-preview link; no invented File transclusion.',
            'visible_credit_location':'One compact source note below each result table; no per-cell names or superscript codes.',
            'optional_map_format':{'files':{'recordID':{'filename':'Actual existing Commons filename', 'rights_evidence_url':'Required for the two external diagrams'}}},
            'verification_requirements':['Existing public Commons file','Exact local image SHA-1 match','Free-license metadata','Separate permission evidence for source-only catalogue diagrams'],
            'assets':image_assets}
    (packet/'research/wikipedia-commons-image-plan.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    audit = {'status':'PASS','date':'2026-10-12','table_count':2,'table_cell_count':99,
             'population_range':[2,12],'same_solid_columns':5,'dual_solid_columns':4,
             'source_register_parity':True,'all_display_values_preserved':True,
             'all_attribution_codes_preserved_in_metadata':True,'all_source_and_inspection_links_preserved':True,
             'visible_credit_location':'Compact source note below each table',
             'per_table_source_note_count':2,'per_cell_visible_name_or_code_count':0,
             'verified_png_count':100,'author_rendered_table_pngs':97,'external_source_only_table_pngs':2,
             'source_only_cells_use_original_diagram_not_archive_pose':True,
             'markdown_static_clickable_images':99,'mediawiki_image_slots':100,
             'live_file_transclusions':len(verified),'commons_upload_performed':False,
             'infobox_count':wiki.count('{{Infobox\n'),'native_infobox_template':True,
             'column_headers_have_scope':True,'row_headers_have_scope':True,
             'reference_count':reference_count,'hypothesis_count':hypothesis_count,
             'prose_preserved_except_requested_precision_and_source_note_updates':True,
             'mathematical_asterisk_repaired':bad_math in before_wiki,
             'markdown_sha256':sha256(md_path),'mediawiki_sha256':sha256(wiki_path)}
    (packet/'research/wikipedia-image-table-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    notes = '''# Image-table integration and future Commons mapping

The local Markdown draft shows all 99 static PNG images before each value and its inspection/source links. Construction attribution occupies one small source note below each table. Individual cells contain no author-name line or superscript attribution code; internal provenance codes remain in the image plan. Clicking the 97 rendered archive images opens the individual rotatable construction. The two superior source-only octahedron entries use first-frame images of their original catalogue GIFs and link the original GIF, preserving the original geometry and attribution.

The MediaWiki source uses ordinary `wikitable` result tables, captions, scoped row and column headers, the generic `{{Infobox}}` template with separate image and caption parameters, `<math>`, standard citation templates, and `{{reflist}}`. Its table image slots are hidden comments and preview links while no Commons filename is available; the infobox image parameter is a hidden pending-file comment. No image has been uploaded by this builder and no missing File name is invented.

The 97 author-rendered table images and the additional infobox hero are prepared under CC BY 4.0, with author, source-coordinate hashes, and image hashes in the plan. The two catalogue images are EXCLUDED from Commons preparation pending independent free-license permission; they receive no CC BY claim. Their original diagram links remain in the article tables.

Run `python research/build_wikipedia_image_tables.py --packet .` from the output directory to rebuild idempotently. After a separate, authorized Commons upload, supply `--commons-map path/to/actual-files.json` with `files` entries keyed by record ID and actual filenames. The builder checks the existing public file, exact byte hash, and free-license metadata. External diagrams additionally require a rights-evidence URL. A verified table image uses standard `[[File:...|frameless|140px|alt=...]]` markup; the infobox uses `frameless|upright=1.1|alt=...`. Images retain their default File-page licensing link, with separate 3D or original-diagram links for inspection. No upload or publication occurs in either mode.

The current reference definitions, numeric table values, internal provenance codes, and original inspection links are retained. Source credits occupy collapsible per-table notes; the separate precision paragraph distinguishes certified scales, touching estimates, rounded catalogue reports, and reproductions. The shorter research reference links the established literature and gives one generalization credit. The full earlier reference preserves the detailed methodology and twenty hypotheses separately.
'''
    (packet/'research/wikipedia-image-integration-notes.md').write_text(notes,encoding='utf-8')
    print(json.dumps(audit,indent=2))

if __name__ == '__main__':
    main()
