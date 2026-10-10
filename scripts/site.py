#!/usr/bin/env python3
"""Build site/index.html from scripts/site_template.html: record tables (with published values where they exist), s(n)
chart and an interactive 3D viewer for inspecting each packing, with every record embedded.
usage: python3 scripts/site.py"""
import json, os, sys, glob, csv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
AB = {'tet': 'tetrahedron', 'cub': 'cube', 'oct': 'octahedron', 'dod': 'dodecahedron', 'ico': 'icosahedron'}
ORDER = ['tetintet', 'octinoct', 'icoinico', 'dodindod', 'cubincub', 'cubinoct', 'octincub', 'dodinico', 'icoindod']
REF = json.load(open(os.path.join(ROOT, 'docs', 'references.json')))


def compare(s_full, ref):
    s_full, ref = float(s_full), float(ref)
    return 'better' if s_full < ref - 1e-5 else ('equal' if s_full <= ref + 1e-5 else 'behind')


def src_code(src):
    return 'T' if 'trivial' in src else 'N' if 'Nakajima' in src else 'W' if 'Walsh' in src else 'L' if 'Lin' in src else 'F'


def load():
    probs = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'records', '*', '*_n[0-9][0-9].json'))):
        r = json.load(open(f)); pid = r['record_id'].split('_')[0]
        cert = open(f.replace('.json', '.certify.txt')).read() if os.path.exists(f.replace('.json', '.certify.txt')) else ''
        p = probs.setdefault(pid, {'id': pid, 'piece': r['piece'], 'container': r['container'], 'rows': [], 'hasref': bool(REF.get(pid))})
        ref = REF.get(pid, {}).get(str(r['n']))
        p['rows'].append({'n': r['n'], 's': r['s_plus'], 'ref': ref[0] if ref else None, 'refsrc': ref[1] if ref else None,
                          'refcode': src_code(ref[1]) if ref else None, 'cmp': compare(r['s_full'], ref[0]) if ref else None,
                          'sf': r['s_full'], 'st': r.get('s_tight'), 'cf': r.get('closed_form_conjecture'),
                          'den': round(r['density'], 4), 'vlb': round(r['volume_lower_bound'], 5),
                          'move': (r.get('search') or {}).get('move'), 'derived': r.get('derived_from'),
                          'file': os.path.relpath(f, ROOT),
                          'ok': 'CERTIFIED' in cert and 'NOT CERTIFIED' not in cert,
                          'cert': [l for l in cert.splitlines() if l.startswith('(')],
                          'p': [[round(x, 7) for x in q] for q in r['pieces']]})
    for p in probs.values(): p['rows'].sort(key=lambda r: r['n'])
    ids = [i for i in ORDER if i in probs] + sorted(i for i in probs if i not in ORDER)
    solids = {k: {'V': v['V'], 'F': v['faces'], 'E': v['edges'], 'vol': v['volume']} for k, v in SOL.items()}
    return {'problems': [probs[i] for i in ids], 'solids': solids, 'nmin': 2, 'nmax': 40,
            'repo': 'https://github.com/alejandrozu/platonic-packing'}


TEMPLATE = os.path.join(ROOT, 'scripts', 'site_template.html')

if __name__ == '__main__':
    import datetime
    data = load(); data['built'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    os.makedirs(os.path.join(ROOT, 'site'), exist_ok=True)
    page = open(TEMPLATE).read().replace('__DATA__', json.dumps(data, separators=(',', ':')).replace('</', '<\\/'))
    # site/index.html is a complete document (GitHub Pages, opening the file locally); the head part of the template
    # (title, fonts, styles) goes into <head>. `--fragment PATH` also writes the bare page for the Claude artifact.
    k = page.index('</style>') + len('</style>')
    html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + page[:k] + '\n</head>\n<body>\n' + page[k:] + '\n</body>\n</html>\n')
    out = os.path.join(ROOT, 'site', 'index.html'); open(out, 'w').write(html)
    if '--fragment' in sys.argv: open(sys.argv[sys.argv.index('--fragment') + 1], 'w').write(page)
    print(out, len(html) // 1024, 'KB', sum(len(p['rows']) for p in data['problems']), 'records')
