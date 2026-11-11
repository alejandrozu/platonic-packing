#!/usr/bin/env python3
"""Closed forms of record scales from other people (25 Oct 2026, Alejandro: import the closed forms of issue #99 and cite
their source).

    python3 scripts/closed_forms_ext.py import RESULTS.tsv EXACT_TOUCH_DIR    # writes docs/closed_forms_external.json

RESULTS.tsv is cumulative (each zerogap-packing version contains the earlier ones), so an import replaces the file;
closed forms imported before keep their provenance (version and issue), new ones get the latest version's.
    python3 scripts/closed_forms_ext.py add TABLE.tsv ISSUE [DIGITS]   # closed forms from an issue's own table (record<TAB>form)

Hirotaka Nakano (konoha-ily2) solved the contact equations of catalogue records to ~117 digits and identified integer
polynomials for s (zerogap-packing, https://doi.org/10.5281/zenodo.23630728, issue #99). A closed form belongs to one
configuration, so each entry is bound to the record's source hash: the publisher uses it only while the record still
holds that packing, and only if its value agrees with the record's touching scale s_tight. Closed forms that come with
a submitted packing (the community record's closed_form_conjecture, issue #100) are used the same way, bound to that
packing. Expressions are evaluated by a small arithmetic parser (numbers, + - * / ^, parentheses, sqrt/√); nothing
from a contribution is executed."""
import ast, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'docs', 'closed_forms_external.json')
ZEROGAP = {'name': 'Hirotaka Nakano (konoha-ily2)', 'work': 'zerogap-packing v1.1.1',
           'doi': 'https://doi.org/10.5281/zenodo.23630728', 'issue': 'https://github.com/alejandrozu/platonic-packing/issues/99'}
# 11 Nov 2026: issue #112 (v1.2.0, imported from v1.4.0, which contains it) adds more; entries already imported from #99 keep their provenance
ZEROGAP_112 = dict(ZEROGAP, work='zerogap-packing v1.4.0', issue='https://github.com/alejandrozu/platonic-packing/issues/112')
_cache = None


def value(expr, dps=60):
    """mpmath value of a closed-form string such as '2*√2 + 4', '√(91√5/4 + 207/4)' or '(23 + 4√2)/7'"""
    import mpmath as mp
    mp.mp.dps = dps
    s = expr.replace('−', '-').replace('··', '**').replace('·', '*').replace('^', '**')   # the catalogue's notation too
    s = re.sub(r'(\d|\))\s*√', r'\1*√', s)                       # 2√2 -> 2*√2
    s = re.sub(r'√\s*(\d+(?:\.\d+)?)', r'sqrt(\1)', s)            # √5 -> sqrt(5)
    s = s.replace('√(', 'sqrt(').replace('√', 'sqrt')
    tree = ast.parse(s, mode='eval')

    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return mp.mpf(str(n.value))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            v = ev(n.operand); return -v if isinstance(n.op, ast.USub) else v
        if isinstance(n, ast.BinOp):
            a, b = ev(n.left), ev(n.right)
            ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b, ast.Div: lambda: a / b,
                   ast.Pow: lambda: a ** b}
            if type(n.op) in ops: return ops[type(n.op)]()
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'sqrt' and len(n.args) == 1 and not n.keywords:
            return mp.sqrt(ev(n.args[0]))
        raise ValueError(f'unsupported expression: {expr!r}')
    return ev(tree)


def pretty(expr):
    """the catalogue's notation: no '*' before a root ('2*√2 + 4' -> '2√2 + 4')"""
    return re.sub(r'(\d|\))\*√', r'\1√', expr.replace('**', '^')).replace('*', '·')


def load():
    global _cache
    if _cache is None:
        _cache = json.load(open(DATA)) if os.path.exists(DATA) else {'entries': {}}
    return _cache


def lookup(record_id, src_hash, s, bsrc=None):
    """(closed form, provenance) for a record holding the packing with this source hash and touching scale s, or None"""
    e = load()['entries'].get(record_id)
    if e and e.get('hash') == src_hash:
        try:
            v = float(value(e['closed_form'], 30))
            if v <= s * (1 + 1e-9) and s - v <= 2e-6 * s:
                return pretty(e['closed_form']), e['provenance'], bool(e.get('already_in_catalogue'))
        except Exception:
            pass
    bsrc = bsrc or {}
    if bsrc.get('move') == 'community' and bsrc.get('record_file'):
        try:
            r = json.load(open(os.path.join(ROOT, bsrc['record_file'])))
            cf = r.get('closed_form_conjecture')
            v = float(value(cf, 30)) if isinstance(cf, str) and cf else None
            if v is not None and v <= s * (1 + 1e-9) and s - v <= 2e-6 * s:
                return pretty(cf), {'name': bsrc.get('lineage'), 'issue': bsrc.get('issue'),
                                    'digits': r.get('closed_form_digits'), 'with': 'the submitted packing'}, False
        except Exception:
            pass
    return None


def apply(rec, src_hash, s, bsrc):
    """put an external closed form into a record dict; True if the record changed"""
    if rec.get('derived_from'):           # the record holds the n + 1 packing minus one piece: check against its own scale
        s, bsrc = float(rec.get('s_tight') or s), None
    x = lookup(rec.get('record_id'), src_hash, s, bsrc)
    if not x: return False
    cf, prov, already = x
    if already:                                               # our own closed form, confirmed independently
        if rec.get('closed_form_confirmation') == prov: return False
        rec['closed_form_confirmation'] = prov; return True
    if rec.get('closed_form_conjecture') == cf and rec.get('closed_form_source') == prov: return False
    rec['closed_form_conjecture'] = cf; rec['closed_form_source'] = prov
    return True


def meta_of(record_id, src_hash, s, bsrc, cf_own):
    """the closed-form fields of a new record: (closed_form_conjecture, extra fields)"""
    x = lookup(record_id, src_hash, s, bsrc)
    if not x: return cf_own, {}
    cf, prov, already = x
    if already: return cf_own, {'closed_form_confirmation': prov}
    return cf, {'closed_form_source': prov}


def do_import(results, touch_dir, source=None):
    """source: the provenance of closed forms not imported before (default: the latest zerogap-packing version)"""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import csv, glob
    source = source or ZEROGAP_112
    before = {k: e for k, e in load()['entries'].items() if e.get('provenance', {}).get('doi') == ZEROGAP['doi']}
    exact = set()
    for t in glob.glob(os.path.join(touch_dir, 'summary*.tsv')):
        for row in csv.DictReader(open(t), delimiter='\t'):
            if row.get('status') == 'EXACT-VALID': exact.add(row['record'])
    out, stats = {}, {'rows': 0, 'closed': 0, 'new': 0, 'agree': 0, 'differ': [], 'value_mismatch': [], 'no_record': []}
    import mpmath as mp
    rows = []
    for row in csv.DictReader(open(results), delimiter='\t'):
        stats['rows'] += 1
        if (row.get('closed_form') or '').strip(): rows.append(row)
    # a row named after a contributor's own variant of a record (v1.2.0: 'cubindod_n45_glat_desc_desc', an improved
    # configuration that the catalogue accepted) belongs to the record of the same pair and n; when several rows reach
    # one record, the one whose value is closest below the record's touching scale is its configuration
    cand = {}
    for row in rows:
        stats['closed'] += 1
        rid0 = row['record']; m = re.match(r'^([a-z]+_n\d+)', rid0)
        rid = m.group(1) if m else rid0
        cand.setdefault(rid, []).append(row)
    stats['variant_rows'] = sum(1 for r in rows if not re.fullmatch(r'[a-z]+_n\d+', r['record']))
    for rid, rws in cand.items():
        p = rid.rsplit('_n', 1)[0]
        fn = os.path.join(ROOT, 'records', p, rid + '.json')
        if not os.path.exists(fn): stats['no_record'].append(rid); continue
        rec = json.load(open(fn)); st = float(rec['s_tight'])
        ok = []
        for row in rws:
            cf = row['closed_form'].strip(); v = value(cf, 130)
            # the closed form is the touching scale of the contact-solved configuration: at most the record's s_tight,
            # and within 2e-6 of it (submitted packings carry their clearance in the coordinates, ~1e-6 above it)
            if float(v) > st + 1e-9 * st or st - float(v) > 2e-6 * st or float(v) > rec['s_full']:
                stats['value_mismatch'].append((row['record'], cf, float(v), rec['s_tight'], rec['s_full'])); continue
            ok.append((st - float(v), row, cf, v))
        if not ok: continue
        _, row, cf, v = min(ok, key=lambda t: t[0])
        digits = int(row.get('digits') or 0)
        sv = mp.mpf(row['s'])
        agree_digits = int(-mp.log10(abs(v - sv) / sv)) if v != sv else 130
        ours = None if rec.get('closed_form_source') else rec.get('closed_form_conjecture')   # ours, not an imported one
        if ours:
            try: same = abs(value(ours, 50) - v) < mp.mpf(10) ** -40
            except Exception: same = False
            if same: stats['agree'] += 1
            else: stats['differ'].append((rid, ours, cf))
            if not same: continue
        else:
            stats['new'] += 1
        old = before.get(rid)
        base = {k: old['provenance'][k] for k in ZEROGAP} if old and old.get('closed_form') == cf else source
        out[rid] = {'hash': rec['source']['hash'], 'closed_form': cf, 'already_in_catalogue': bool(ours),
                    'provenance': dict(base, digits=min(digits, agree_digits),
                                       exact_touching_check=row['record'] in exact,
                                       **({'configuration': row['record']} if row['record'] != rid else {}))}
    for k, e in load()['entries'].items():      # closed forms added from an issue's own table (do_add) stay until a version has them
        if k not in out and e.get('provenance', {}).get('via') == 'issue table': out[k] = e
    save(out)
    return stats


def save(entries):
    json.dump({'about': 'Closed forms of record scales from other people (scripts/closed_forms_ext.py); each entry is bound '
                        'to the record packing it was computed for (source hash).',
               'entries': entries}, open(DATA, 'w'), indent=1, ensure_ascii=False)


def mp_eps():
    import mpmath as mp
    return mp.mpf(10) ** -40


def do_add(table, issue, digits):
    """Closed forms listed in an issue's own table (TSV: record, closed form), for records the RESULTS.tsv of a zerogap
    version does not have yet: the same value check, digits as the author states them, bound to the current record"""
    entries = dict(load()['entries'])
    stats = {'rows': 0, 'new': 0, 'agree': 0, 'differ': [], 'value_mismatch': [], 'no_record': []}
    src = dict(ZEROGAP, work='zerogap-packing (method); values from the issue',
               issue=f'https://github.com/alejandrozu/platonic-packing/issues/{issue}')
    for line in open(table):
        if not line.strip() or line.startswith('#'): continue
        rid, cf = [x.strip() for x in line.rstrip('\n').split('\t')[:2]]
        stats['rows'] += 1
        fn = os.path.join(ROOT, 'records', rid.rsplit('_n', 1)[0], rid + '.json')
        if not os.path.exists(fn): stats['no_record'].append(rid); continue
        rec = json.load(open(fn)); st = float(rec['s_tight']); v = value(cf, 130)
        if float(v) > st + 1e-9 * st or st - float(v) > 2e-6 * st or float(v) > rec['s_full']:
            stats['value_mismatch'].append((rid, cf, float(v), rec['s_tight'], rec['s_full'])); continue
        ours = None if rec.get('closed_form_source') else rec.get('closed_form_conjecture')
        if ours:
            try: same = abs(value(ours, 50) - v) < mp_eps()
            except Exception: same = False
            if not same: stats['differ'].append((rid, ours, cf)); continue
            stats['agree'] += 1
        else:
            stats['new'] += 1
        entries[rid] = {'hash': rec['source']['hash'], 'closed_form': cf, 'already_in_catalogue': bool(ours),
                        'provenance': dict(src, digits=digits, via='issue table', exact_touching_check=False)}
    save(entries)
    return stats


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'import':
        st = do_import(sys.argv[2], sys.argv[3])
        print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in st.items()}))
        for k in ('differ', 'value_mismatch', 'no_record'):
            for x in st[k][:20]: print(k, x)
    elif len(sys.argv) >= 4 and sys.argv[1] == 'add':
        st = do_add(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 0)
        print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in st.items()}))
        for k in ('differ', 'value_mismatch', 'no_record'):
            for x in st[k][:20]: print(k, x)
    else:
        print(__doc__)
