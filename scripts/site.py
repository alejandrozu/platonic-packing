#!/usr/bin/env python3
"""Build the polyhedrainpolyhedra.wiki website into site/ from web/ (templates, styles, scripts) and the records.

  site/index.html                 record explorer (families, atlas of problems, 3D viewer, tables, charts)
  site/constructions/index.html   every record with links to its JSON, exact certificate and float check on GitHub
  site/method/  certification/  contribute/  about/   article pages
  site/data/records.json          all records (7-decimal coordinates for the viewer) + the solid library
  site/assets/                    styles, scripts, icon;  CNAME, robots.txt, sitemap.xml, 404.html, .nojekyll

usage: python3 scripts/site.py [--fragment PATH]   (--fragment also writes a one-file explorer for a Claude artifact)
The site is deployed to the gh-pages branch by scripts/pages.sh (and by .github/workflows/site.yml on GitHub)."""
import json, os, sys, glob, re, html, shutil, datetime, math, hashlib
from fractions import Fraction
from urllib.parse import urlsplit
from pathlib import Path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
SOL = json.loads(Path(ROOT, 'src', 'solids.json').read_text(encoding='utf-8'))
REF = json.loads(Path(ROOT, 'docs', 'references.json').read_text(encoding='utf-8'))
EXTERNAL_PATH = os.path.join(ROOT, 'docs', 'external_records.json')
EXTERNAL = json.loads(Path(EXTERNAL_PATH).read_text(encoding='utf-8')) if os.path.exists(EXTERNAL_PATH) else {'entries': []}
COMMUNITY_PATH = Path(ROOT, 'docs', 'community_records.json')
COMMUNITY = json.loads(COMMUNITY_PATH.read_text(encoding='utf-8')) if COMMUNITY_PATH.exists() else {'entries': []}
WEB = os.path.join(ROOT, 'web')
OUT = os.path.join(ROOT, 'site')
REPO = 'https://github.com/alejandrozu/platonic-packing'
DOMAIN = 'polyhedrainpolyhedra.wiki'
HAS_DOMAIN = os.path.exists(os.path.join(WEB, 'CNAME'))     # web/CNAME switches the site to the custom domain
SITE_URL = f'https://{DOMAIN}/' if HAS_DOMAIN else 'https://alejandrozu.github.io/platonic-packing/'
from engine import FAM, PID
POLY = {3: 'triangular', 4: 'square', 5: 'pentagonal', 6: 'hexagonal', 8: 'octagonal', 12: 'dodecagonal'}
SITE_NMAX = int(os.environ.get('PP_SITE_NMAX', '100000'))   # optional cap on n shown (unset: all records)
FAMILY_GROUP = {'platonic': 'platonic', 'archimedean': 'archcat', 'catalan': 'archcat', 'prisms': 'prisms'}
FAMILY_NAME = {'platonic': 'Platonic', 'archimedean': 'Archimedean', 'catalan': 'Catalan', 'prisms': 'Prisms and antiprisms'}


def compare(s_full, ref, quantum=1e-5):
    s_full, ref = float(s_full), float(ref)
    quantum = max(1e-5, float(quantum))
    return 'better' if s_full < ref - quantum else ('equal' if s_full <= ref + quantum else 'behind')


def public_url(value):
    """Imported metadata is data; only ordinary public web URLs become links."""
    if not isinstance(value, str): return None
    try:
        u = urlsplit(value)
        return value if u.scheme in ('https', 'http') and u.hostname and not u.username and not u.password else None
    except ValueError:
        return None


def viewer_pieces(record):
    # Display coordinates may be rounded; certificate numbers stay untouched in
    # the downloadable witness. Recenter translated containers for this viewer.
    centre = record.get('container_center', [0, 0, 0])
    return [[round(float(Fraction(q[k]) - Fraction(centre[k])), 7) if k < 3 else float(q[k])
             for k in range(7)] for q in record['pieces']]


def src_code(src):
    return ('T' if 'trivial' in src.lower() else 'N' if 'Nakajima' in src else 'W' if 'Walsh' in src else
            'L' if 'Lin' in src else 'F' if 'Friedman' in src else 'X')


ELONG_H = {'l15': '1.5', 'l2': '2', 'l3': '3'}


def disp(s):
    if s.startswith('prism') and '_' in s:                     # elongated prism, e.g. prism6_l2
        base, tag = s.split('_')
        return f'{POLY[int(base[5:])]} prism of height {ELONG_H.get(tag, tag)}'
    for pre in ('antiprism', 'prism'):
        if s.startswith(pre) and s[len(pre):].isdigit(): return f'{POLY[int(s[len(pre):])]} {pre}'
    return s.replace('_', ' ')


def plural(s):
    w = disp(s)
    if ' prism of height ' in w: return w.replace(' prism of ', ' prisms of ')
    return w[:-6] + 'hedra' if w.endswith('hedron') else w + 's'


def ptitle(piece, container):
    c = disp(container); return f"{plural(piece)[0].upper() + plural(piece)[1:]} in {'an' if c[0] in 'aeiou' else 'a'} {c}"


def load():
    probs = {}
    files = glob.glob(os.path.join(ROOT, 'records', '*', '*_n[0-9][0-9].json')) + glob.glob(os.path.join(ROOT, 'records', '*', '*_n[0-9][0-9][0-9].json'))
    files += [os.path.join(ROOT, e['file']) for e in EXTERNAL['entries'] if e['kind'] == 'coordinates']
    files += [os.path.join(ROOT, e['file']) for e in COMMUNITY['entries']]
    for f in sorted(set(files)):
        r = json.loads(Path(f).read_text(encoding='utf-8')); pid = r['record_id'].split('_')[0]
        if pid not in FAM: continue
        if r.get('n', 0) > SITE_NMAX: continue
        cert = Path(f.replace('.json', '.certify.txt')).read_text(encoding='utf-8') if os.path.exists(f.replace('.json', '.certify.txt')) else ''
        vtxt = Path(f.replace('.json', '.verify.txt')).read_text(encoding='utf-8') if os.path.exists(f.replace('.json', '.verify.txt')) else ''
        p = probs.setdefault(pid, {'id': pid, 'piece': r['piece'], 'container': r['container'], 'rows': [], 'hasref': bool(REF.get(pid)),
                                   'family': FAM[pid], 'group': FAMILY_GROUP[FAM[pid]], 'title': ptitle(r['piece'], r['container']),
                                   'unit': 'edge' if SOL[r['piece']].get('unit', 'edge') == 'edge' else 'size'})
        ref = REF.get(pid, {}).get(str(r['n']))
        src = r.get('source') if isinstance(r.get('source'), dict) else {}
        contribution = r.get('contribution') if isinstance(r.get('contribution'), dict) else {}
        p['rows'].append({'n': r['n'], 'id': r['record_id'], 's': r['s_plus'], 'ref': ref[0] if ref else None, 'refsrc': ref[1] if ref else None,
                          'refcode': src_code(ref[1]) if ref else None, 'cmp': compare(r['s_full'], ref[0]) if ref else None,
                          'sf': r['s_full'], 'st': r.get('s_tight'), 'cf': r.get('closed_form_conjecture'),
                          'den': round(r['density'], 4), 'vlb': round(r['volume_lower_bound'], 5),
                          'move': (r.get('search') or {}).get('move'), 'derived': r.get('derived_from'), 'who': r.get('found_by'),
                          'issue': contribution.get('issue') or src.get('issue'), 'file': os.path.relpath(f, ROOT).replace(os.sep, '/'),
                          'refined_by': r.get('certificate_refined_by'), 'contribution_kind': contribution.get('kind'),
                          'source_url': public_url(src.get('url')), 'source_author': src.get('author'),
                          'source_derivation': src.get('derivation'), 'container_center': r.get('container_center', [0, 0, 0]),
                          'published_sf': src.get('published_s_full'), 'external': src.get('kind') == 'external',
                          'ok': 'CERTIFIED' in cert and 'NOT CERTIFIED' not in cert,
                          'ver': 'VALID' in vtxt and 'INVALID' not in vtxt,
                          'cert': [l for l in cert.splitlines() if l.startswith(('(', 'containment:', 'disjointness:'))],
                          'p': viewer_pieces(r)})
    for p in probs.values():
        # One best entry per n, independently of who discovered it. Existing
        # project records remain intact and available as alternate constructions.
        selected = []
        for n in sorted({r['n'] for r in p['rows']}):
            candidates = sorted([r for r in p['rows'] if r['n'] == n], key=lambda r: r['sf'])
            best = candidates[0]
            sources = [e for e in EXTERNAL['entries'] if e['problem'] == p['id'] and e['n'] == n
                       and isinstance(e.get('published_value'), (int, float)) and math.isfinite(e['published_value'])]
            published = min(sources, key=lambda e: e['published_value']) if sources else None
            if published:
                p['hasref'] = True
                quantum = max(1e-5, published.get('display_quantum', 1e-5))
                for cand in candidates:
                    cand.update(ref=published['published_value'], refsrc=published['author'],
                                refcode=src_code(published['author']), refurl=public_url(published['url']), ref_quantum=quantum,
                                cmp=compare(cand['sf'], published['published_value'], quantum))
            # A printed 5-decimal catalogue value is not a certifiable pose. Only
            # use it over available coordinates when the difference exceeds the
            # published rounding scale; never show other poses at its smaller s.
            if published and published['kind'] in ('catalogue', 'author_report') and published['published_value'] < best['sf'] - quantum:
                sf = published['published_value']
                display = f'{math.floor(sf * 1e5) / 1e5:.5f}+' if published.get('published_expression') else f'{sf:.5f}+'
                best = {'n': n, 'id': f'{p["id"]}_n{n:02d}_catalogue', 's': display, 'sf': sf, 'st': None,
                        'cf': None, 'den': round(n * SOL[p['piece']]['volume'] / SOL[p['container']]['volume'] / sf / sf / sf, 4),
                        'vlb': candidates[0]['vlb'], 'move': None, 'derived': None, 'who': published['author'],
                        'source_author': published['author'], 'source_url': public_url(published['url']), 'image_url': public_url(published.get('image_url')),
                        'published_sf': sf, 'external': True, 'source_only': True, 'value_precision': published['value_precision'],
                        'author_report': published['kind'] == 'author_report',
                        'published_expression': published.get('published_expression'),
                        'file': None, 'ok': False, 'ver': False, 'cert': [], 'p': [], 'issue': None,
                        'ref': sf, 'refsrc': published['author'], 'refcode': src_code(published['author']),
                        'refurl': public_url(published['url']), 'ref_quantum': quantum, 'cmp': 'equal'}
                best['alternatives'] = candidates
            else:
                best['alternatives'] = [r for r in candidates if r is not best]
            selected.append(best)
        p['rows'] = selected
    for pid, (pc, cc) in PID.items():                # problems without records yet
        if pid not in probs:
            probs[pid] = {'id': pid, 'piece': pc, 'container': cc, 'rows': [], 'hasref': bool(REF.get(pid)), 'family': FAM[pid],
                          'group': FAMILY_GROUP[FAM[pid]], 'title': ptitle(pc, cc), 'unit': 'edge' if SOL[pc].get('unit', 'edge') == 'edge' else 'size'}
    out = [probs[i] for i in PID if i in probs]
    for p in out:                                    # the families go to n = 100 since 14 Oct; the Platonic problems stay at 40
        p['nmax'] = max([40 if FAM[p['id']] == 'platonic' else 100, *[r['n'] for r in p['rows']]])
    solids = {k: {'V': v['V'], 'F': v['faces'], 'E': v['edges'], 'vol': v['volume']} for k, v in SOL.items()}
    ns = [r['n'] for p in out for r in p['rows']]
    return {'problems': out, 'solids': solids, 'nmin': min([2, *ns]), 'nmax': max([40, *ns]), 'repo': REPO,
            'external_checked_on': EXTERNAL.get('checked_on')}


def stats(data):
    rows = [r for p in data['problems'] for r in p['rows']]
    st = {'records': len(rows), 'certified': sum(1 for r in rows if r['ok']), 'problems': len(data['problems']),
          'cases': len(data['problems']) * (data['nmax'] - data['nmin'] + 1), 'solids': len(SOL), 'attempts': None,
          'contributed': sum(1 for r in rows if r.get('issue')),
          'source_only': sum(1 for r in rows if r.get('source_only')),
          'external': sum(1 for r in rows if r.get('external'))}
    try:                                              # attempts across all machines (main archive + remote totals)
        import engine
        tot = 0
        for f in glob.glob(os.path.join(ROOT, 'state', 'best', '*', 'n[0-9]*.json')):
            c = json.loads(Path(f).read_text(encoding='utf-8')); tot += engine.total_attempts(c.get('stats', {}))
        st['attempts'] = tot or None
    except Exception:
        pass
    return st


def cert_sentence(st):
    if st.get('source_only'):
        return (f"{st['certified']:,} selected coordinate constructions are certified exactly; "
                f"{st['source_only']} better published entries link to the original constructions and have no coordinates or local certificate. "
                "Their certified alternatives remain available in the viewer.")
    if st['records'] and st['certified'] == st['records']:
        return f"All {st['records']:,} records on this site are certified exactly."
    return f"{st['certified']:,} of the {st['records']:,} records on this site are certified exactly; the others are float-checked and waiting for their certificate."


# ------------------------------------------------------------------ exact fields table (certification page)
ALPHA = {'x − 1': 'rational', 'x² − 2': '√2', 'x² − x − 1': 'φ = (1 + √5)/2', 'x² − 3': '√3',
         'x³ − x² − x − 1': 'the tribonacci constant', 'x⁴ − 2': '2<sup>1/4</sup>', 'x⁴ + 2x² − 2': '√(√3 − 1)',
         '5x⁴ − 5x² + 1': '1/(2 sin 36°)', '2x⁴ − 4x² + 1': '1/(2 sin 22.5°)', 'x⁴ − 4x² + 1': '1/(2 sin 15°)',
         'x⁶ − 4x⁴ − x³ + 4x² + 2x − 1': 'ξ with ξ³ − 2ξ = φ'}
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')


def poly_str(c):
    c = [int(x) for x in c]; terms = []
    for k in range(len(c) - 1, -1, -1):
        a = c[k]
        if a == 0: continue
        mag = abs(a); var = '' if k == 0 else 'x' if k == 1 else 'x' + str(k).translate(SUP)
        coef = str(mag) if (mag != 1 or k == 0) else ''
        terms.append(('−' if a < 0 else '+', coef + var))
    s = ('−' if terms[0][0] == '−' else '') + terms[0][1]
    for sg, t in terms[1:]: s += f' {sg} {t}'
    return s


def fields_table():
    from fractions import Fraction as Fr
    E = json.load(open(os.path.join(ROOT, 'src', 'solids_exact.json')))
    groups = {}
    for name, d in E.items():
        key = (poly_str(d['minpoly']), d['interval'][0])
        g = groups.setdefault(key, {'deg': len(d['minpoly']) - 1, 'solids': [], 'scaled': [],
                                     'alpha': float((Fr(d['interval'][0]) + Fr(d['interval'][1])) / 2)})
        (g['scaled'] if d['D'] else g['solids']).append(name)
    special = {('antiprism8',): '√(1 − 1/(4 cos² 22.5°))', ('antiprism12',): '√(1 − 1/(4 cos² 15°))'}
    rows = []
    for (poly, _), g in sorted(groups.items(), key=lambda kv: (kv[1]['deg'], kv[0][0])):
        names = g['solids'] + g['scaled']
        a = ALPHA.get(poly) or special.get(tuple(names), '')
        sol = ', '.join(disp(s) for s in g['solids'])
        if g['scaled']: sol += (', ' if sol else '') + ', '.join(disp(s) for s in g['scaled']) + ' (times λ = 1/√D)'
        if a == 'rational': aval = 'α = 1: rational coordinates'
        elif a: aval = f"α = {a} ≈ {g['alpha']:.6f}"
        else: aval = f"α ≈ {g['alpha']:.6f}"
        rows.append(f'<tr><td><span style="white-space:nowrap">{html.escape(poly)}</span><br><span class="mut">{aval}</span></td><td>{g["deg"]}</td>'
                    f'<td>{html.escape(sol)}</td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th>Minimal polynomial of α</th><th>Degree</th><th>Solids</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>')


# ------------------------------------------------------------------ constructions index
# 14 Oct (Alejandro): the same sub-groups as the columns of the records page
DUAL = {'cube': 'octahedron', 'octahedron': 'cube', 'dodecahedron': 'icosahedron', 'icosahedron': 'dodecahedron', 'tetrahedron': 'tetrahedron'}
SUBGROUPS = {'platonic': ['Self packings', 'Dual packings', 'Heterogeneous packings'], 'prisms': ['Prisms', 'Antiprisms', 'Elongated prisms']}


def subgroup(p):
    pc, cc = p['piece'], p['container']
    if p['family'] == 'platonic':
        return 'Self packings' if pc == cc else 'Dual packings' if DUAL.get(pc) == cc else 'Heterogeneous packings'
    if p['family'] == 'prisms':
        return 'Antiprisms' if pc.startswith('antiprism') else 'Elongated prisms' if '_l' in pc else 'Prisms'
    return ''


def constructions(data):
    parts = []
    for fam in ('platonic', 'archimedean', 'catalan', 'prisms'):
        ps = [p for p in data['problems'] if p['family'] == fam]
        parts.append(f'<h2 id="{fam}">{FAMILY_NAME[fam]}</h2>')
        sub = None
        for p in sorted(ps, key=lambda q: SUBGROUPS.get(fam, ['']).index(subgroup(q))):
            if subgroup(p) != sub and fam in SUBGROUPS:
                sub = subgroup(p); parts.append(f'<h3 id="{fam}-{sub.lower().replace(" ", "-")}">{sub}</h3>')
            rows = []
            for r in p['rows']:
                rid = r.get('id') or f"{p['id']}_n{r['n']:02d}"; url = f"{REPO}/blob/main/{r['file']}" if r['file'] else r['source_url']
                coordinates = f'<a href="{url}">{html.escape(os.path.basename(r["file"]))}</a>' if r['file'] else f'<a href="{html.escape(url)}">published construction</a>'
                if r.get('source_url') and r['file']:
                    coordinates += f'<br><a href="{html.escape(r["source_url"])}">original source</a>'
                if r.get('alternatives'):
                    alternate = ''.join(f'<li><a href="{REPO}/blob/main/{a["file"]}">{html.escape(a["who"] or "project search")}: {a["s"]}</a> '
                                        f'(<a href="{REPO}/blob/main/{a["file"].replace(".json", ".certify.txt")}">certificate</a>)</li>' for a in r['alternatives'])
                    coordinates += f'<details><summary>Other certified constructions</summary><ul>{alternate}</ul></details>'
                rows.append(f'<tr><td class="n">{r["n"]}</td><td class="s">{r["s"]}</td>'
                            f'<td>{coordinates}</td>'
                            f'<td>{"<a href=\"" + url.replace(".json", ".certify.txt") + "\">certificate</a>" if r["ok"] else "source only" if r.get("source_only") else "pending"}</td>'
                            f'<td>{"<a href=\"" + url.replace(".json", ".verify.txt") + "\">float check</a>" if r["file"] else "—"}</td>'
                            f'<td><a href="../#{p["id"]}_n{r["n"]:02d}">{"source and alternatives" if r.get("source_only") else "view in 3D"}</a></td>'
                            f'<td class="mut">{html.escape(r["who"] or "")}</td></tr>')
            parts.append(f'<details id="{p["id"]}"><summary><b>{html.escape(p["title"])}</b> <span class="mut">{p["id"]}, {len(p["rows"])} records</span></summary>'
                         f'<div class="tablewrap"><table><thead><tr><th>n</th><th>s</th><th>Record file</th><th>Exact certificate</th><th>Float check</th><th>Viewer</th><th>Found by</th></tr></thead>'
                         f'<tbody>{"".join(rows)}</tbody></table></div>'
                         f'<p class="mut" style="font:13px var(--f-body)">Folder: <a href="{REPO}/tree/main/records/{p["id"]}">records/{p["id"]}</a></p></details>')
    return '\n'.join(parts)


# ------------------------------------------------------------------ page shell
NAV = [('', 'Records'), ('constructions/', 'All constructions'), ('method/', 'Method'), ('certification/', 'Certification'),
       ('contribute/', 'Contribute'), ('about/', 'About')]


def mark_svg():
    """Logo: an octahedron (piece) drawn inside a cube (container), oblique projection."""
    import math
    a, b = -0.52, 0.66
    def pr(v):
        x, y, z = v; x1 = math.cos(b) * x + math.sin(b) * z; z1 = -math.sin(b) * x + math.cos(b) * z
        return 16 + 9.6 * x1, 16 - 9.6 * (math.cos(a) * y - math.sin(a) * z1)
    cube = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    ce = [(i, j) for i in range(8) for j in range(i + 1, 8) if sum(cube[i][k] != cube[j][k] for k in range(3)) == 1]
    octv = [(0.92, 0, 0), (-0.92, 0, 0), (0, 0.92, 0), (0, -0.92, 0), (0, 0, 0.92), (0, 0, -0.92)]
    oe = [(i, j) for i in range(6) for j in range(i + 1, 6) if i // 2 != j // 2]
    d = lambda P, E: ' '.join(f'M{pr(P[i])[0]:.2f} {pr(P[i])[1]:.2f}L{pr(P[j])[0]:.2f} {pr(P[j])[1]:.2f}' for i, j in E)
    return d(cube, ce), d(octv, oe)


def content_version(path):
    """A changed resource gets a different cache key, independent of build time."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def asset_url(root, filename):
    source = Path(WEB, 'assets', filename)
    if not source.exists():
        source = Path(OUT, 'assets', filename)  # Generated assets, such as icon.svg.
    return f'{root}assets/{filename}?v={content_version(source)}'


def page(path, title, desc, body, active, scripts=(), styles=(), depth=1, root=None):
    root = root if root is not None else ('./' if depth == 0 else '../' * depth)
    cpath, opath = mark_svg()
    nav = ''.join(f'<a href="{root}{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    nav += f'<a href="{REPO}" rel="noopener">GitHub</a>'
    canon = SITE_URL + path
    records = Path(OUT, 'data', 'records.json')
    records_version = content_version(records) if records.exists() else ''
    return f'''<!doctype html>
<html lang="en" data-root="{root}" data-repo="{REPO}" data-records-version="{records_version}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#eef1f0">
<script>try{{const t=localStorage.getItem('ppr-theme');document.documentElement.dataset.theme=['light','dark'].includes(t)?t:(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}}catch(e){{}}</script>
<script src="{asset_url(root, 'theme.js')}" defer></script>
<link rel="icon" href="{asset_url(root, 'icon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=STIX+Two+Text:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{asset_url(root, 'style.css')}">
{''.join(f'<link rel="stylesheet" href="{asset_url(root, s)}">' for s in styles)}
</head>
<body>
<header class="top"><div class="in">
  <a class="mark" href="{root}"><svg viewBox="0 0 32 32" aria-hidden="true" fill="none" stroke-width="1.3" stroke-linecap="round"><path class="c" d="{cpath}"/><path class="p" d="{opath}"/></svg>Polyhedra in Polyhedra</a>
  <nav class="nav" aria-label="Site">{nav}</nav>
  <div class="theme-switch seg" role="group" aria-label="Colour theme"><button type="button" data-theme="light" aria-pressed="false">Light</button><button type="button" data-theme="dark" aria-pressed="false">Dark</button></div>
</div></header>
<main class="wrap{' record-page' if active == '' else ''}">
{body}
</main>
<footer class="foot"><div class="in">
  <p>Certified coordinate constructions and attributed published values, not optimality claims. Generalized packing method by Alejandro Zarzuelo Urdiales, building on Yohei Nakajima's soft-to-rigid cube-packing method. Code, records and certificates: <a href="{REPO}">{REPO.replace('https://', '')}</a>. Project code: MIT license; external constructions retain their source attribution.</p>
  <p>This site is updated and maintained by Alejandro Zarzuelo Urdiales.</p>
  <p>Built {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC{datetime.datetime.now().astimezone().strftime('%z')[:3]}</p>
</div></footer>
{''.join(s if s.startswith('<script') else f'<script src="{s if s.startswith("http") else asset_url(root, s)}"></script>' for s in scripts)}
</body>
</html>
'''


def toc(body):
    items = re.findall(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body)
    if not items: return ''
    links = ''.join(f'<a href="#{i}"{" class=\"sub\"" if lv == "3" else ""}>{re.sub("<[^>]+>", "", t)}</a>' for lv, i, t in items)
    return f'<nav class="toc" aria-label="On this page"><b>On this page</b>{links}</nav>'


def fill(tpl, vals, root):
    s = tpl.replace('{{ROOT}}', root).replace('{{REPO}}', REPO)
    for k, v in vals.items(): s = s.replace('{{' + k + '}}', v)
    if '{{TOC}}' in s: s = s.replace('{{TOC}}', toc(s))
    left = re.findall(r'\{\{[A-Z_]+\}\}', s)
    assert not left, f'unfilled placeholders {left}'
    return s


def write(rel, text):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(text)


def split_pieces(data):
    """14 Oct (n <= 100): the viewer coordinates move to one file per problem, data/pieces/<id>.json, loaded when the
    problem is opened; records.json keeps every value and only the coordinates of the row drawn as the thumbnail.
    Keys: the row id, and '<row id>|<alternative id>' for alternatives. Each problem carries 'pv', the hash of its file."""
    out = dict(data); out['lazy'] = True; out['problems'] = []
    for p in data['problems']:
        q = dict(p); pieces = {}; rows = []
        thumb = (next((r for r in p['rows'] if r['n'] == 6), None) or next((r for r in p['rows'] if r['n'] == 5), None)
                 or (p['rows'][0] if p['rows'] else None))
        for r in p['rows']:
            r2 = dict(r)
            if r.get('p'): pieces[r['id']] = r['p']
            if r is not thumb: r2.pop('p', None)
            if r.get('alternatives'):
                alts = []
                for a in r['alternatives']:
                    a2 = dict(a)
                    if a.get('p'): pieces[f"{r['id']}|{a.get('id')}"] = a['p']
                    a2.pop('p', None); alts.append(a2)
                r2['alternatives'] = alts
            rows.append(r2)
        q['rows'] = rows
        txt = json.dumps(pieces, separators=(',', ':'))
        q['pv'] = hashlib.sha1(txt.encode()).hexdigest()[:12]
        write(f"data/pieces/{p['id']}.json", txt)
        out['problems'].append(q)
    return out


def build(fragment=None):
    data = load(); st = stats(data); data['built'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    if os.path.isdir(OUT):
        for x in os.listdir(OUT):
            q = os.path.join(OUT, x); shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    os.makedirs(OUT, exist_ok=True)
    stats_sentence = (f"{st['records']:,} cases in {st['problems']} problems, with {st['source_only']} attributed source-only entries and certified alternatives."
                      if st.get('source_only') else
                      f"{st['records']:,} packings in {st['problems']} problems, every one certified in exact arithmetic."
                      if st['certified'] == st['records'] else
                      f"{st['records']:,} packings in {st['problems']} problems, {st['certified']:,} of them certified in exact arithmetic so far.")
    vals = {'SITE': SITE_URL.rstrip('/'), 'STATS_SENTENCE': stats_sentence, 'N_RECORDS': f"{st['records']:,}", 'N_PROBLEMS': str(st['problems']),
            'N_CASES': f"{st['cases']:,}", 'N_MIN': str(data['nmin']), 'N_MAX': str(data['nmax']),
            'N_SOLIDS': str(st['solids']), 'CERT_SENTENCE': cert_sentence(st),
            'N_ATTEMPTS': f"{st['attempts']:,}" if st['attempts'] else 'many thousands of',
            'FIELDS_TABLE': fields_table()}
    desc = ('Smallest known containers for n = 2–100 copies of Archimedean and Catalan solids, prisms and antiprisms '
            '(n = 2–40 for the Platonic solids), with exact-certified coordinates and attributed published constructions. '
            'Browse in 3D, check your own and submit it.')
    T3 = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'
    # assets
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    for f in os.listdir(os.path.join(WEB, 'assets')): shutil.copy(os.path.join(WEB, 'assets', f), os.path.join(OUT, 'assets', f))
    cpath, opath = mark_svg()
    write('assets/icon.svg', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" stroke-width="1.6" stroke-linecap="round">'
                             f'<rect width="32" height="32" rx="6" fill="#f8faf9"/><path d="{cpath}" stroke="#172024"/><path d="{opath}" stroke="#2c49a8"/></svg>')
    write('data/records.json', json.dumps(split_pieces(data), separators=(',', ':')))
    # pages
    home = fill(open(os.path.join(WEB, 'pages', 'home.html')).read(), vals, './')
    write('index.html', page('', 'Polyhedra in Polyhedra: record packings with proofs', desc, home, '', scripts=(T3, 'explorer.js'), styles=('explorer.css',), depth=0))
    arts = [('method', 'Method', 'How the packings are found: soft-to-rigid homotopy, r-rounding, separating axis contacts, basin hopping, tightening.'),
            ('certification', 'Certification', 'How every record is proved valid: exact solids in number fields, rational rotations, interval arithmetic and separating planes.'),
            ('contribute', 'Contribute', 'Check a packing in your browser, submit it for exact certification, propose a new category or share another construction.'),
            ('about', 'About', 'What Polyhedra in Polyhedra is, who made it, how to cite it.')]
    for slug, title, d in arts:
        body = fill(open(os.path.join(WEB, 'pages', slug + '.html')).read(), vals, '../')
        write(f'{slug}/index.html', page(f'{slug}/', f'{title}: Polyhedra in Polyhedra', d, body, f'{slug}/',
                                         scripts=((T3, 'contribute.js') if slug == 'contribute' else ())))
    cons = (f'<div class="doc"><article><h1>All constructions</h1><p class="lede">Every record, grouped by problem, with links to '
            f'the record file, its exact certificate and its float check on GitHub. Open a problem to see its {data["nmax"] - data["nmin"] + 1} values of n.</p>'
            f'<p>{cert_sentence(st)} The same files are in <a href="{REPO}/tree/main/records"><code>records/</code></a>; '
            f'<a href="{REPO}/blob/main/records/SUMMARY.csv">SUMMARY.csv</a> and <a href="{REPO}/blob/main/records/SUMMARY_families.csv">SUMMARY_families.csv</a> '
            f'list the project archive values; <a href="{REPO}/blob/main/docs/external_records.json">external_records.json</a> lists independent sources, '
            f'and <a href="../data/records.json">data/records.json</a> holds all selected values and alternatives shown on this site. '
            f'<a href="{REPO}/archive/refs/heads/main.zip">Download the whole repository</a>.</p>'
            + constructions(data) + '</article>' + '{{TOC}}' + '</div>')
    cons = fill(cons, vals, '../')
    write('constructions/index.html', page('constructions/', 'All constructions: Polyhedra in Polyhedra',
                                           'Every record packing with links to its coordinates, exact certificate and float check.', cons, 'constructions/',
                                           scripts=('<script>(function(){function o(){var d=document.getElementById(location.hash.slice(1));if(d&&d.tagName==="DETAILS"){d.open=true;d.scrollIntoView()}}addEventListener("hashchange",o);o()})()</script>',)))
    nf = ('<div class="doc"><article><h1>Not found</h1><p class="lede">There is no page at this address.</p>'
          '<p>Try the <a href="/">records</a>, <a href="/constructions/">all constructions</a> or the '
          '<a href="/contribute/">contribute page</a>. Record ids such as <code>cubincub_n12</code> open directly as <a href="/#cubincub_n12">/#cubincub_n12</a>.</p></article></div>')
    base = '/' if HAS_DOMAIN else '/platonic-packing/'
    nf = nf.replace('href="/', f'href="{base}')
    write('404.html', page('404.html', 'Not found: Polyhedra in Polyhedra', desc, nf, None, root=base))
    if os.path.exists(os.path.join(WEB, 'CNAME')):   # custom domain (added once its DNS points at GitHub Pages)
        write('CNAME', open(os.path.join(WEB, 'CNAME')).read().strip() + '\n')
    write('.nojekyll', '')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n')
    urls = ['', 'constructions/', 'method/', 'certification/', 'contribute/', 'about/']
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'  <url><loc>{SITE_URL}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    if fragment:                                       # one-file explorer for the Claude artifact
        cssx = open(os.path.join(WEB, 'assets', 'style.css')).read() + open(os.path.join(WEB, 'assets', 'explorer.css')).read()
        js = open(os.path.join(WEB, 'assets', 'explorer.js')).read()
        h = home.replace('href="./', f'href="{SITE_URL}')
        frag = (f'<title>Polyhedra in Polyhedra</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=STIX+Two+Text:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">\n'
                f'<style>{cssx}</style>\n<main class="wrap">{h}</main>\n'
                f'<script>window.PP_DATA = {json.dumps(data, separators=(",", ":")).replace("</", "<\\/")};</script>\n'
                f'<script src="{T3}"></script>\n<script>{js}</script>\n')
        frag = frag.replace('<html', '<html')
        open(fragment, 'w').write(frag)
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print(f'{OUT}: {size // 1024} KB, {st["records"]} records ({st["certified"]} certified), {st["problems"]} problems')


if __name__ == '__main__':
    build(sys.argv[sys.argv.index('--fragment') + 1] if '--fragment' in sys.argv else None)
