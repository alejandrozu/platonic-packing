"""Convert the editable local reference to MediaWiki markup; never submit it.

The image-table blocks and infobox are kept from the accompanying reference file.
Citation metadata is supplied separately. This is a format conversion, not a
claim of human authorship, source reliability, or Wikipedia acceptance.
"""
from pathlib import Path
import argparse, json, re
from urllib.parse import unquote

LINK = re.compile(r'\[([^\]\n]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)')
TABLE_MD = re.compile(r'^\| n \|[^\n]*\n(?:\|[^\n]*\n)+', re.M)
TABLE_WIKI = re.compile(r'^\{\| class="wikitable"[^\n]*\n.*?^\|\}', re.M | re.S)

def convert(packet):
    md = (packet / 'wikipedia-polyhedral-fits.md').read_text(encoding='utf-8')
    original = (packet / 'wikipedia-full-reference.wiki').read_text(encoding='utf-8')
    metadata = json.loads((packet / 'research/wikipedia-citation-metadata.json').read_text(encoding='utf-8'))
    tables = TABLE_WIKI.findall(original)
    assert len(tables) == len(TABLE_MD.findall(md)) == 2
    infobox = re.search(r'<!-- PACKING_INFOBOX_START -->.*?<!-- PACKING_INFOBOX_END -->', original, re.S).group()
    infobox = re.sub(r'\| label3 = Atlas\n\| data3 = .*', '| label3 = Objective\n| data3 = Minimum enclosing scale', infobox)
    infobox = re.sub(r'\| label4 = Counts\n\| data4 = .*', '| label4 = Tables\n| data4 = 2–12 pieces', infobox)
    infobox = re.sub(r'\| label5 = Papers\n\| data5 = .*', '| label5 = Theory\n| data5 = [https://doi.org/10.1017/CBO9780511546587 Finite packing] · [https://doi.org/10.1016/S0010-4485(01)00109-9 3D layout]', infobox)
    seen = set()
    def inline(text):
        protected = []
        def math(m):
            protected.append('<math>' + m.group(1) + '</math>')
            return f'POLYMATH{len(protected)-1}TOKEN'
        text = re.sub(r'\$([^$\n]+)\$', math, text)
        def ref(m):
            n = m.group(1)
            assert n == m.group(2) and n in metadata
            if n in seen:
                return f'<ref name="r{n}" />'
            seen.add(n)
            return f'<ref name="r{n}">{metadata[n]}</ref>'
        text = re.sub(r'\[(\d+)\]\(#reference-(\d+)\)', ref, text)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r"'''\1'''", text)
        text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r"''\1''", text)
        def link(m):
            label, url = m.groups()
            if url.startswith('https://en.wikipedia.org/wiki/'):
                title = unquote(url.split('/wiki/', 1)[1]).replace('_', ' ')
                return '[[' + title + ('|' + label if label != title else '') + ']]'
            return '[' + url + ' ' + label + ']'
        text = LINK.sub(link, text)
        text = re.sub(r'POLYMATH(\d+)TOKEN', lambda m: protected[int(m.group(1))], text)
        return text
    article = md.split('## References\n', 1)[0]
    external = md.split('## External links\n', 1)[1]
    lines = article.splitlines()
    result = ['<!-- Offsite research reference, revised 12 October 2026. No Wikipedia submission. -->', '', infobox, '']
    i = 0
    table_index = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('# '):
            i += 1
            continue
        if line == '$$':
            formula = []
            i += 1
            while lines[i] != '$$':
                formula.append(lines[i])
                i += 1
            result.extend(['<math display="block">', *formula, '</math>'])
        elif line.startswith('| n |'):
            while i < len(lines) and lines[i].startswith('|'):
                i += 1
            result.append(tables[table_index])
            table_index += 1
            continue
        elif line.startswith('<small>Construction sources:'):
            result.extend(['<div class="mw-collapsible mw-collapsed">', '<small>Construction attribution</small>', '<div class="mw-collapsible-content">', inline(line), '</div>', '</div>'])
        else:
            heading = re.match(r'^(#{2,3}) (.+)$', line)
            if heading:
                marks = '=' * len(heading.group(1))
                result.append(marks + ' ' + heading.group(2) + ' ' + marks)
            else:
                result.append(inline(line))
        i += 1
    result.extend(['== References ==', '', '{{reflist}}', '', '== External links ==', ''])
    result.extend(inline(line) for line in external.splitlines())
    wiki = '\n'.join(result).strip() + '\n'
    assert TABLE_WIKI.findall(wiki) == tables
    assert len(re.findall(r'^! scope="row" \| ', wiki, re.M)) == 22
    assert len(re.findall(r'<ref name="r\d+">', wiki)) == len(seen)
    assert not re.search(r'<math[^>]*>[^<]*\'\'[^<]*</math>', wiki)
    assert not re.search(r'POLYMATH\d+TOKEN|__\w+__', wiki)
    (packet / 'wikipedia-polyhedral-fits.wiki').write_text(wiki, encoding='utf-8')
    return {'references': len(seen), 'table_blocks_preserved': True, 'native_wikilinks': len(re.findall(r'\[\[', wiki)), 'submission_performed': False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(convert(args.packet.resolve()), indent=2))
