#!/usr/bin/env python3
"""Closed forms of record scales from other people (25 Oct 2026, Alejandro: import the closed forms of issue #99 and cite
their source).

    python3 scripts/closed_forms_ext.py import RESULTS.tsv EXACT_TOUCH_DIR    # writes docs/closed_forms_external.json

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
_cache = None


def value(expr, dps=60):
    """mpmath value of a closed-form string such as '2*√2 + 4', '√(91√5/4 + 207/4)' or '(23 + 4√2)/7'"""
    import mpmath as mp
    mp.mp.dps = dps
    s = expr.replace('−', '-').replace('^', '**')
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
    return re.sub(r'(\d|\))\*√', r'\1√', expr).replace('*', '·')


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


def do_import(results, touch_dir):
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import csv, glob
    exact = set()
    for t in glob.glob(os.path.join(touch_dir, 'summary*.tsv')):
        for row in csv.DictReader(open(t), delimiter='\t'):
            if row.get('status') == 'EXACT-VALID': exact.add(row['record'])
    out, stats = {}, {'rows': 0, 'closed': 0, 'new': 0, 'agree': 0, 'differ': [], 'value_mismatch': [], 'no_record': []}
    for row in csv.DictReader(open(results), delimiter='\t'):
        stats['rows'] += 1
        rid, cf = row['record'], (row.get('closed_form') or '').strip()
        if not cf: continue
        stats['closed'] += 1
        p = rid.rsplit('_n', 1)[0]
        fn = os.path.join(ROOT, 'records', p, rid + '.json')
        if not os.path.exists(fn): stats['no_record'].append(rid); continue
        rec = json.load(open(fn))
        v = value(cf, 130); digits = int(row.get('digits') or 0)
        import mpmath as mp
        sv = mp.mpf(row['s'])
        agree_digits = int(-mp.log10(abs(v - sv) / sv)) if v != sv else 130
        # the closed form is the touching scale of the contact-solved configuration: at most the record's s_tight, and
        # within 2e-6 of it (submitted packings carry their clearance in the coordinates, ~1e-6 above the touching value)
        st = float(rec['s_tight'])
        if float(v) > st + 1e-9 * st or st - float(v) > 2e-6 * st or float(v) > rec['s_full']:
            stats['value_mismatch'].append((rid, cf, float(v), rec['s_tight'], rec['s_full'])); continue
        ours = rec.get('closed_form_conjecture')
        if ours:
            try: same = abs(value(ours, 50) - v) < mp.mpf(10) ** -40
            except Exception: same = False
            if same: stats['agree'] += 1
            else: stats['differ'].append((rid, ours, cf))
            if not same: continue
        else:
            stats['new'] += 1
        out[rid] = {'hash': rec['source']['hash'], 'closed_form': cf, 'already_in_catalogue': bool(ours),
                    'provenance': dict(ZEROGAP, digits=min(digits, agree_digits),
                                       exact_touching_check=rid in exact)}
    json.dump({'about': 'Closed forms of record scales from other people (scripts/closed_forms_ext.py); each entry is bound '
                        'to the record packing it was computed for (source hash).',
               'entries': out}, open(DATA, 'w'), indent=1, ensure_ascii=False)
    return stats


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'import':
        st = do_import(sys.argv[2], sys.argv[3])
        print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in st.items()}))
        for k in ('differ', 'value_mismatch', 'no_record'):
            for x in st[k][:20]: print(k, x)
    else:
        print(__doc__)
