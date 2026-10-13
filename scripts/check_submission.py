#!/usr/bin/env python3
"""Check (and, on acceptance, record) a packing submitted through a GitHub issue (template: submit-packing.yml).

  python3 scripts/check_submission.py check  EVENT.json OUTDIR   float check + exact certificate + comparison
  python3 scripts/check_submission.py accept EVENT.json OUTDIR   the same, then, if the packing is certified and
                                                                 beats (or fills) the record of a tracked problem,
                                                                 writes immutable records/community witnesses,
                                                                 registers them in docs/community_records.json,
                                                                 and appends records/CONTRIBUTIONS.md
Acceptance also requires SUBMISSION_CAN_ACCEPT=1, set by the workflow after repository-permission checks,
an accepted-label event, the submitter's credit and their checked publication permission.

EVENT.json is the GitHub event payload ($GITHUB_EVENT_PATH). Writes OUTDIR/comment.md (the reply to post) and
OUTDIR/result.json ({"labels_add": [...], "labels_remove": [...], "accepted": bool, "record": path or null}).
The issue text is only parsed as data (JSON and numbers); nothing from it is executed or passed to a shell."""
import json, os, re, sys, math, subprocess
from types import SimpleNamespace
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_json(path, data, indent=None):
    Path(path).write_text(json.dumps(data, indent=indent), encoding='utf-8')


def save_text(path, text):
    Path(path).write_text(text, encoding='utf-8')


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
SOL = load_json(os.path.join(ROOT, 'src', 'solids.json'))
EXACT = load_json(os.path.join(ROOT, 'src', 'solids_exact.json'))
from engine import PID, FAM
SITE = ('https://polyhedrainpolyhedra.wiki/' if os.path.exists(os.path.join(ROOT, 'web', 'CNAME'))
        else 'https://alejandrozu.github.io/platonic-packing/')
REPO = 'https://github.com/alejandrozu/platonic-packing'
MAX_N = 200
LABELS = {'Problem': 'problem', 'Number of pieces': 'n', 'Container scale s': 's', 'Packing': 'packing',
          'Credit': 'credit', 'How you found it': 'method', 'Permission': 'permission'}


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
    rec, pid = parse_object(obj, f)
    return rec, pid, f, ''


def finite_number(value):
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def parse_object(obj, f):
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
        if not (isinstance(p, list) and len(p) == 7 and all(finite_number(x) for x in p)):
            raise Bad(f'Piece {i + 1} is not a list of 7 finite numbers `[x, y, z, qw, qx, qy, qz]`.')
        if all(x == 0 for x in p[3:]): raise Bad(f'Piece {i + 1} has a zero quaternion.')
    s = obj.get('s_full', obj.get('s'))
    if s is None:
        try: s = float(f.get('s', '').strip())
        except ValueError: s = None
    if not (finite_number(s) and s > 0): raise Bad('No valid container scale: give `s_full` in the JSON or fill in **Container scale s**.')
    cc = obj.get('container_center', [0, 0, 0])
    if not (isinstance(cc, list) and len(cc) == 3 and all(finite_number(x) for x in cc)): raise Bad('`container_center` must be three finite numbers.')
    if 'n' in obj and (not isinstance(obj['n'], (int, float)) or isinstance(obj['n'], bool) or obj['n'] != len(pcs)):
        raise Bad('The JSON `n` must match the number of entries in `pieces`.')
    form_n = f.get('n', '').strip()
    if form_n and (not form_n.isdigit() or int(form_n) != len(pcs)):
        raise Bad('**Number of pieces** must match the number of entries in the packing.')
    pid = next((k for k, v in PID.items() if v == (piece, container)), None)
    rec = {'piece': piece, 'container': container, 'n': len(pcs), 's_full': s, 'pieces': pcs}
    if any(cc): rec['container_center'] = cc
    return rec, pid


def authorize_accept(event, fields):
    """The workflow sets this only after checking the actor's current repository permission."""
    if (os.environ.get('SUBMISSION_CAN_ACCEPT') != '1' or event.get('action') != 'labeled'
            or (event.get('label') or {}).get('name') != 'accepted'):
        raise Bad('Acceptance requires the `accepted` label from a maintainer with write, maintain or admin access. No record was written.')
    if not re.search(r'^\s*-\s+\[[xX]\]\s+[^\n]*\bMIT\b[^\n]*\blicen[cs]e\b', fields.get('permission', ''), re.M | re.I):
        raise Bad('The publication permission checkbox must be checked before a packing can be accepted. No record was written.')
    if not fields.get('credit', '').strip():
        raise Bad('Fill in **Credit** before this packing can be accepted. No record was written.')


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


def comparison_records(pid, n):
    """Best stored coordinate record, plus a separately sourced published value.

    Catalogue images and author reports cannot act as certified coordinates.
    Imported coordinates do act as the acceptance baseline when a checked local
    certificate is present, so beating a larger project file is not mislabelled.
    """
    if not pid:
        return None, None, None
    root = Path(ROOT).resolve()
    own_file = Path('records') / pid / f'{pid}_n{n:02d}.json'
    candidates = []
    if (root / own_file).exists():
        candidates.append((load_json(root / own_file), own_file.as_posix()))
    entries = []
    for registry in (root / 'docs/external_records.json', root / 'docs/community_records.json'):
        if registry.exists(): entries.extend(load_json(registry).get('entries', []))
    entries = [e for e in entries if e.get('problem') == pid and e.get('n') == n]
    for entry in entries:
        if entry.get('kind') != 'coordinates':
            continue
        path = (root / entry['file']).resolve()
        if not path.is_relative_to(root / 'records') or not path.exists():
            continue
        certificate = path.with_suffix('.certify.txt')
        if not certificate.exists():
            continue
        text = certificate.read_text(encoding='utf-8')
        if 'CERTIFIED' not in text or 'NOT CERTIFIED' in text:
            continue
        record = load_json(path)
        if record.get('n') != n or (record.get('piece'), record.get('container')) != PID[pid]:
            continue
        candidates.append((record, path.relative_to(root).as_posix()))
    current, filename = min(candidates, key=lambda candidate: candidate[0]['s_full']) if candidates else (None, None)
    published = [e for e in entries if finite_number(e.get('published_value'))]
    reference = min(published, key=lambda e: e['published_value']) if published else None
    return current, filename, reference


def main():
    from submission_runner import main as batch_main
    batch_main(SimpleNamespace(**globals()))


if __name__ == '__main__':
    main()
