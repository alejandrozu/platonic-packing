#!/usr/bin/env python3
"""Contributions from other people, checked on every cycle (13 Oct 2026, Alejandro: "each time you merge a github
session, look also for contributions of others ... assign credit when they have beaten any of the constructions").

    python3 scripts/community_sync.py [--no-github]

1. GitHub: open issues labelled `submission` that the submission workflow has already certified as better than the
   record (labels `certified` + `new-record`) get the `accepted` label; the workflow then re-checks them exactly,
   writes the immutable community record with the submitter's credit (records/community, docs/community_records.json)
   and closes the issue. Other open contributions (new categories, other constructions, pull requests by other
   people) are only listed: they need a human decision.
2. Archive: every community packing (docs/community_records.json) that is smaller than the search archive's best is
   re-legalized here (as engine.harvest does) and becomes the archive's best with src move 'community' and its
   credit as lineage, so the search continues from it and every packing derived from it keeps the credit.
Contributor data is only parsed as numbers; nothing from an issue or archive is executed.
Prints one summary line (used in the 6-minute reports) and appends details to logs/community.log."""
import json, os, re, sys, time, hashlib, subprocess
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'src'))
import engine, exact

REPO = 'alejandrozu/platonic-packing'
OWNER = 'alejandrozu'
SEEN = os.path.join(engine.STATE, '.community_seen')
LOG = os.path.join(ROOT, 'logs', 'community.log')


def log(msg):
    with open(LOG, 'a') as f: f.write(time.strftime('%m-%d %H:%M:%S ') + msg + '\n')


def gh(args, data=None):
    r = subprocess.run(['gh', 'api'] + args, capture_output=True, text=True, timeout=60, input=data)
    if r.returncode: raise RuntimeError(r.stderr.strip()[:300])
    return json.loads(r.stdout) if r.stdout.strip() else None


def github_pass():
    accepted, pending = [], []
    issues = gh([f'repos/{REPO}/issues?state=open&per_page=100'])
    for it in issues:
        num, labels, user = it['number'], {l['name'] for l in it['labels']}, it['user']['login']
        if it.get('pull_request'):
            if user != OWNER: pending.append(f'PR #{num} by {user}')
            continue
        if 'submission' in labels:
            if {'certified', 'new-record'} <= labels and 'accepted' not in labels:
                gh(['-X', 'POST', f'repos/{REPO}/issues/{num}/labels', '-f', 'labels[]=accepted'])
                accepted.append(f'#{num} by {user}'); log(f'accepted issue #{num} by {user}: {it["title"][:120]}')
            elif 'accepted' not in labels and user != OWNER:
                state = 'not certified' if 'not-certified' in labels else 'needs fix' if 'needs-fix' in labels else \
                        'certified, no improvement' if 'certified' in labels else 'being checked'
                pending.append(f'#{num} by {user} ({state})')
        elif user != OWNER and labels & {'category', 'construction'}:
            pending.append(f'#{num} by {user} ({"new category" if "category" in labels else "other construction"})')
        elif user != OWNER:
            pending.append(f'#{num} by {user}')
    return accepted, pending


def archive_pass():
    """Community packings smaller than the archive's best become the best (credited)."""
    seen = set(open(SEEN).read().split()) if os.path.exists(SEEN) else set()
    taken, new_seen = [], []
    entries = []
    for kind, fn in (('community', 'community_records.json'), ('literature', 'external_records.json')):
        reg = os.path.join(ROOT, 'docs', fn)
        if os.path.exists(reg): entries += [(kind, e) for e in json.load(open(reg)).get('entries', []) if e.get('file')]
    for kind, e in entries:
        fn = os.path.join(ROOT, e.get('file', ''))
        p, n = e.get('problem'), e.get('n')
        if p not in engine.PID or not os.path.exists(fn): continue
        key = hashlib.sha1(open(fn, 'rb').read()).hexdigest()[:16]
        if key in seen: continue
        new_seen.append(key)
        rec = json.load(open(fn))
        pieces = rec.get('pieces')
        if not isinstance(pieces, list) or len(pieces) != n: continue
        pb = engine.problem(p)
        cen = np.array(rec.get('container_center') or [0, 0, 0], float)
        C = (np.array([q[:3] for q in pieces], float) - cen) * pb.edge          # unit edge -> internal units
        Q = [list(map(float, q[3:7])) for q in pieces]
        R = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in Q]
        L, _, C0 = exact.certify(pb, C, R)                                      # legalize (no overlap at 1e-12)
        Lt, t = exact.tight_container(pb, C0, R)
        s = pb.s_of_L(Lt)
        con = rec.get('contribution') or {}
        # the contributor's credit first (21 Oct: a submitted found_by can describe the construction instead, e.g.
        # "trivial: subset of the 5x5x5 grid" in issue #98)
        credit = ((con.get('credit') if kind == 'community' else None) or rec.get('found_by') or con.get('credit')
                  or con.get('submitted_by') or e.get('author')
                  or ('community contribution' if kind == 'community' else 'published construction'))
        with engine.locked():
            case = engine.load_case(p, n); cur = case['best']
            if cur and s >= cur['s'] - 1e-9: continue
            src = {'move': kind, 'lineage': credit, 'issue': con.get('issue') or e.get('issue'),
                   'submitted_by': con.get('submitted_by'), 'record_file': e.get('file')}
            # a refinement of a catalogue packing keeps the original credit too (25 Oct, issue #100: the submitted
            # found_by is the seed record's, the contribution credit is the refiner's)
            seed = (rec.get('found_by') or '').split(' (')[0].strip()
            m = re.search(r'search started from the (?:published )?packing of (.+)\)\s*$', rec.get('found_by') or '')
            if kind == 'community' and m:                       # 28 Oct, issue #102: a search from someone else's packing
                src['started_from'] = m.group(1).strip()
            elif kind == 'community' and seed and con.get('credit') and seed != con['credit'].split(' (')[0].strip():
                src['refines'] = seed
            if kind == 'literature': src.update(source=credit, url=e.get('url'))
            case['best'] = {'s': s, 'C': (C0 + t).tolist(), 'Q': Q, 'src': src, 't': time.time(), 'tightened': False}
            st = case['stats']; st['improvements'] += 1; st['since'] = 0; st['last_improve'] = time.time()
            st['needs_tighten'] = True; st['fails'] = {}
            engine.save_case(case)
            engine.pool_insert(p, n, {'s': s, 'C': case['best']['C'], 'Q': Q, 'src': kind, 't': time.time(), 'lineage': credit})
            engine.enforce_monotone(p, log)
            with open(os.path.join(engine.STATE, 'attempts.jsonl'), 'a') as f:
                f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': n, 'move': kind, 'raw': s, 's': s,
                                    'best_before': cur['s'] if cur else None, 'improved': True, 'secs': 0, 'raw_secs': 0,
                                    'host': kind}) + '\n')
        taken.append((p, n, s, cur['s'] if cur else None, credit))
        log(f'archive: {p} n={n} {cur["s"] if cur else None} -> {s:.10f} from {credit} ({e.get("issue")})')
    if new_seen:
        with open(SEEN, 'a') as f: f.write('\n'.join(new_seen) + '\n')
    return taken


def main():
    acc, pend, err = [], [], None
    if '--no-github' not in sys.argv:
        try: acc, pend = github_pass()
        except Exception as e: err = str(e)[:120]
    taken = archive_pass()
    parts = [f'contributions: {len(acc)} accepted' + (f' ({", ".join(acc)})' if acc else ''),
             f'{len(taken)} contributed/published packings newly lead the archive']
    if pend: parts.append('waiting: ' + '; '.join(pend[:6]) + (' ...' if len(pend) > 6 else ''))
    if err: parts.append(f'GitHub check failed: {err}')
    print(', '.join(parts))


if __name__ == '__main__':
    main()
