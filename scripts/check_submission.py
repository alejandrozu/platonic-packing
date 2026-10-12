#!/usr/bin/env python3
"""Check (and, on acceptance, record) a packing submitted through a GitHub issue (template: submit-packing.yml).

  python3 scripts/check_submission.py check  EVENT.json OUTDIR   float check + exact certificate + comparison
  python3 scripts/check_submission.py accept EVENT.json OUTDIR   the same, then, if the packing is certified and
                                                                 beats (or fills) the record of a tracked problem,
                                                                 writes records/<id>/<id>_nNN.{json,certify.txt,verify.txt}
                                                                 and appends records/CONTRIBUTIONS.md

EVENT.json is the GitHub event payload ($GITHUB_EVENT_PATH). Writes OUTDIR/comment.md (the reply to post) and
OUTDIR/result.json ({"labels_add": [...], "labels_remove": [...], "accepted": bool, "record": path or null}).
The issue text is only parsed as data (JSON and numbers); nothing from it is executed or passed to a shell."""
import json, os, re, sys, math, subprocess, datetime, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
EXACT = json.load(open(os.path.join(ROOT, 'src', 'solids_exact.json')))
from engine import PID, FAM
SITE = 'https://polyhedrainpolyhedra.wiki/'
REPO = 'https://github.com/alejandrozu/platonic-packing'
MAX_N = 200
LABELS = {'Problem': 'problem', 'Number of pieces': 'n', 'Container scale s': 's', 'Packing': 'packing',
          'Credit': 'credit', 'How you found it': 'method'}


class Bad(Exception):
    pass


def sections(body):
    out, cur = {}, None
    for line in (body or '').replace('\r\n', '\n').split('\n'):
        m = re.match(r'^###\s+(.*?)\s*$', line)
        if m: cur = LABELS.get(m.group(1)); out[cur] = []; continue
        if cur: out[cur].append(line)
    res = {}
    for k, v in out.items():
        if not k: continue
        t = '\n'.join(v).strip()
        res[k] = '' if t == '_No response_' else t
    return res


def parse(body):
    f = sections(body)
    txt = f.get('packing', '')
    m = re.search(r'```(?:json)?\s*\n(.*?)\n```', txt, re.S)
    if m: txt = m.group(1)
    if not txt.strip(): raise Bad('The **Packing** field is empty.')
    try: obj = json.loads(txt)
    except json.JSONDecodeError as e: raise Bad(f'The **Packing** field is not valid JSON ({e.msg} at line {e.lineno}, column {e.colno}).')
    if isinstance(obj, list): obj = {'pieces': obj}
    if not isinstance(obj, dict) or not isinstance(obj.get('pieces'), list): raise Bad('The packing needs a `pieces` list with one `[x, y, z, qw, qx, qy, qz]` per piece.')
    prob = (f.get('problem') or '').strip().strip('`')
    piece, container = obj.get('piece'), obj.get('container')
    if not (piece and container):
        if prob in PID: piece, container = PID[prob]
        else:
            m = re.match(r'^\s*([a-z0-9_]+)\s+in\s+([a-z0-9_]+)\s*$', prob)
            if m: piece, container = m.group(1), m.group(2)
    if not (isinstance(piece, str) and isinstance(container, str)): raise Bad('Say which solids these are: give `piece` and `container` in the JSON, or a problem id such as `ktoinkto`.')
    for nm in (piece, container):
        if nm not in SOL or nm not in EXACT: raise Bad(f'`{nm}` is not a solid of the library (src/solids.json).')
    pcs = obj['pieces']
    if not 1 <= len(pcs) <= MAX_N: raise Bad(f'The packing has {len(pcs)} pieces; the checker takes 1 to {MAX_N}.')
    for i, p in enumerate(pcs):
        if not (isinstance(p, list) and len(p) == 7 and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in p)):
            raise Bad(f'Piece {i + 1} is not a list of 7 finite numbers `[x, y, z, qw, qx, qy, qz]`.')
        if all(x == 0 for x in p[3:]): raise Bad(f'Piece {i + 1} has a zero quaternion.')
    s = obj.get('s_full', obj.get('s'))
    if s is None:
        try: s = float(f.get('s', '').strip())
        except ValueError: s = None
    if not (isinstance(s, (int, float)) and math.isfinite(s) and s > 0): raise Bad('No valid container scale: give `s_full` in the JSON or fill in **Container scale s**.')
    cc = obj.get('container_center', [0, 0, 0])
    if not (isinstance(cc, list) and len(cc) == 3 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in cc)): raise Bad('`container_center` must be three numbers.')
    pid = next((k for k, v in PID.items() if v == (piece, container)), None)
    rec = {'piece': piece, 'container': container, 'n': len(pcs), 's_full': s, 'pieces': pcs}
    if any(cc): rec['container_center'] = cc
    note = ''
    if f.get('n', '').strip().isdigit() and int(f['n']) != len(pcs): note = f'The form says n = {f["n"].strip()}, but the packing has {len(pcs)} pieces; {len(pcs)} is used.'
    return rec, pid, f, note


def run(cmd, timeout):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return 99, f'timed out after {timeout} s'


POLY = {3: 'triangular', 4: 'square', 5: 'pentagonal', 6: 'hexagonal', 8: 'octagonal', 12: 'dodecagonal'}


def disp(s):
    for pre in ('antiprism', 'prism'):
        if s.startswith(pre) and s[len(pre):].isdigit(): return f'{POLY[int(s[len(pre):])]} {pre}'
    return s.replace('_', ' ')


def plural(s):
    w = disp(s); return w[:-6] + 'hedra' if w.endswith('hedron') else w + 's'


def main():
    mode, event_path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    ev = json.load(open(event_path)); issue = ev['issue']
    url, number, user = issue['html_url'], issue['number'], (issue.get('user') or {}).get('login', '')
    result = {'labels_add': [], 'labels_remove': [], 'accepted': False, 'record': None}
    lines = []
    try:
        rec, pid, f, note = parse(issue.get('body') or '')
    except Bad as e:
        lines += ['### Could not check this submission', '', str(e), '',
                  f'Edit the issue to fix it and the check runs again. The [contribute page]({SITE}contribute/) checks a packing in your browser and fills in this form.']
        result['labels_add'] = ['needs-fix']; result['labels_remove'] = ['certified', 'not-certified', 'new-record']
        open(os.path.join(outdir, 'comment.md'), 'w').write('\n'.join(lines) + '\n'); json.dump(result, open(os.path.join(outdir, 'result.json'), 'w')); return
    n, s = rec['n'], rec['s_full']
    tmp = os.path.join(outdir, 'submission.json'); json.dump(rec, open(tmp, 'w'))
    vcode, vout = run([sys.executable, 'verify_general.py', tmp], 900)
    ccode, cout = run([sys.executable, 'certify_general.py', tmp], 3000)
    certified = ccode == 0 and 'NOT CERTIFIED' not in cout and 'CERTIFIED' in cout
    cur = None
    if pid:
        fn = os.path.join(ROOT, 'records', pid, f'{pid}_n{n:02d}.json')
        if os.path.exists(fn): cur = json.load(open(fn))
    beats = certified and pid and (cur is None or s < cur['s_full'] - 1e-12)
    c = disp(rec['container'])
    title = f'{n} {plural(rec["piece"]) if n > 1 else disp(rec["piece"])} in {"an" if c[0] in "aeiou" else "a"} {c}'
    head = ('✅ Certified: new record' if beats and cur else '✅ Certified: fills an empty case' if beats else
            '✅ Certified' if certified else '❌ Not certified')
    lines += [f'### {head}', '', '| | |', '|---|---|', f'| Packing | {title}' + (f' (`{pid}_n{n:02d}`)' if pid else ' (not a tracked problem yet)') + ' |',
              f'| Submitted s | `{s!r}` |']
    if cur:
        d = s - cur['s_full']
        lines.append(f'| Current record | `{cur["s_full"]!r}`, found by {cur.get("found_by", "?")} ([{pid}_n{n:02d}]({REPO}/blob/main/records/{pid}/{pid}_n{n:02d}.json)) |')
        lines.append(f'| Difference | {d:+.3e} ({("smaller, better" if certified else "smaller") if d < 0 else "larger" if d > 0 else "equal"}) |')
    elif pid: lines.append('| Current record | none yet |')
    lines += ['', '<details><summary>Float check (verify_general.py)</summary>', '', '```', vout[-3000:], '```', '</details>', '',
              '<details open><summary>Exact certificate (certify_general.py)</summary>', '', '```', cout[-6000:], '```', '</details>', '']
    if note: lines += [note, '']
    if not certified:
        lines += ['The packing is not proved valid yet. Pieces must not touch: leave a small positive clearance (about 1e-7) between '
                  'pieces and from every wall, and round s up. Edit the issue and the check runs again.']
    elif not pid:
        lines += ['This pair of solids is not a tracked problem yet, so the packing stays here as a reference. '
                  f'[Propose the category]({REPO}/issues/new?template=new-category.yml) to have it tracked.']
    elif not beats:
        lines += ['Valid, but it does not beat the current record. Thanks for checking it!']
    elif mode == 'check':
        lines += ['A maintainer can accept it by adding the `accepted` label; the record file is then written with your credit and the site is rebuilt.']
    result['labels_add'] = ['certified'] + (['new-record'] if beats else []) if certified else ['not-certified']
    result['labels_remove'] = [l for l in ('certified', 'not-certified', 'new-record', 'needs-fix') if l not in result['labels_add']]

    if mode == 'accept':
        if not beats:
            lines += ['', '**Not recorded:** only certified packings that beat or fill the record of a tracked problem are written to the records.']
        else:
            credit = (f.get('credit') or user or 'anonymous').strip().splitlines()[0][:120]
            method = (f.get('method') or '').strip()[:2000]
            vp, vc = SOL[rec['piece']]['volume'], SOL[rec['container']]['volume']
            rid = f'{pid}_n{n:02d}'; folder = os.path.join(ROOT, 'records', pid); os.makedirs(folder, exist_ok=True)
            wall = re.search(r'min wall gap ([0-9.eE+-]+)', vout); pair = re.search(r'min pair separation ([0-9.eE+-]+)', vout)
            out = {'problem': f'min/{rec["piece"]}_in_{rec["container"]}', 'piece': rec['piece'], 'container': rec['container'], 'n': n,
                   's': math.floor(s * 1e5) / 1e5, 's_plus': f'{math.floor(s * 1e5) / 1e5:.5f}+', 's_full': s,
                   'measure': ('edge length of the container divided by the edge length of the pieces' if SOL[rec['piece']].get('unit', 'edge') == 'edge'
                               else 'linear size of the container divided by the linear size of the pieces (same canonical solid)'),
                   'clearance': {'min_pair_gap': float(pair.group(1)) if pair else None, 'min_wall_gap': float(wall.group(1)) if wall else None},
                   'format': '[x, y, z, qw, qx, qy, qz] per piece: a copy of the canonical piece solid (src/solids.json, 50-digit coordinates in '
                             'src/solids_hp.json) rotated by the scalar-first quaternion q and centred at (x, y, z); container = s_full x canonical '
                             'container solid, centred at the origin (or container_center), canonical orientation',
                   'method': method or 'submitted packing', 'date': datetime.date.today().isoformat(), 'pieces': rec['pieces'],
                   'record_id': rid, 'title': title, 'family': FAM[pid],
                   'source': {'issue': url, 'submitted_by': user}, 's_tight': None, 'closed_form_conjecture': None,
                   'volume_lower_bound': (n * vp / vc) ** (1 / 3), 'density': n * vp / (s ** 3 * vc),
                   'found_by': credit, 'credit': f'{credit}, submitted in {url}',
                   'certificate': 'exact certificate: certify_general.py (src/solids_exact.json)'}
            if 'container_center' in rec: out['container_center'] = rec['container_center']
            if cur: out['previous_record'] = {k: cur.get(k) for k in ('s_full', 'found_by', 'date')}
            base = os.path.join(folder, rid)
            json.dump(out, open(base + '.json', 'w'), indent=1)
            open(base + '.certify.txt', 'w').write(cout + '\n'); open(base + '.verify.txt', 'w').write(vout + '\n')
            log = os.path.join(ROOT, 'records', 'CONTRIBUTIONS.md')
            if not os.path.exists(log):
                open(log, 'w').write('# Contributed records\n\nPackings submitted through GitHub issues, certified exactly and accepted. '
                                     'Newest last.\n\n| date | record | s | previous | credit | issue |\n|---|---|---|---|---|---|\n')
            open(log, 'a').write(f'| {out["date"]} | [{rid}]({pid}/{rid}.json) | {s!r} | {repr(cur["s_full"]) if cur else "none"} | '
                                 f'{credit.replace("|", "/")} | [#{number}]({url}) |\n')
            result['accepted'] = True; result['record'] = os.path.relpath(base + '.json', ROOT)
            lines += ['', f'**Accepted and recorded** as [`{rid}`]({REPO}/blob/main/records/{pid}/{rid}.json), credited to {credit}. '
                          f'It appears on [the site]({SITE}#{rid}) after the rebuild.']
            if n < 40 and pid:
                worse = []
                for m in range(2, n):
                    fm = os.path.join(ROOT, 'records', pid, f'{pid}_n{m:02d}.json')
                    if os.path.exists(fm) and json.load(open(fm))['s_full'] > s: worse.append(m)
                if worse: lines += ['', f'Note: the records for n = {", ".join(map(str, worse))} are now larger than this one; removing pieces from this packing would improve them.']
    open(os.path.join(outdir, 'comment.md'), 'w').write('\n'.join(lines) + '\n')
    json.dump(result, open(os.path.join(outdir, 'result.json'), 'w'))


if __name__ == '__main__':
    main()
