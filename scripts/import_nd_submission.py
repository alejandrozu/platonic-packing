#!/usr/bin/env python3
"""Import a higher-dimensional contribution checked by the nd-submission workflow (15 Oct 2026).

    python3 scripts/import_nd_submission.py ARTIFACT_DIR CONTRIBUTOR ISSUE

ARTIFACT_DIR holds results.json and the extracted record files (records in the format of records/<id>/: exact frame,
pieces [c, S, D], witnesses; see src/claim_nd.py). For every record that this repository's certify_nd.py CERTIFIED in
the workflow, the packing is converted to the archive's internal units, re-legalized here (every pair separated by a
hyperplane, tight container), and stored as the case's best if it beats the archive, with the contributor's credit
(src: move 'community', contributor, issue). Prints one line per record."""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.append(os.path.join(ROOT, 'scripts'))
import engine_nd as E


def rotation(S, Dg):
    d = len(Dg); M = np.zeros((d, d)); t = 0
    for a in range(d):
        for b in range(a + 1, d): M[a, b] = S[t]; M[b, a] = -S[t]; t += 1
    I = np.eye(d)
    return np.diag(Dg) @ np.linalg.solve(I - M, I + M)


def main(art, who, issue):
    import ndsim
    from fractions import Fraction
    res = json.load(open(os.path.join(art, 'results.json')))
    took = []
    for r in res:
        f = r['file'] if os.path.isabs(r['file']) else os.path.join(art, os.path.relpath(r['file'], 'sub'))
        if not r.get('certified'):
            print('not certified, skipped:', r['file']); continue
        rec = json.load(open(f)); pc, cc, n, d = rec['piece'], rec['container'], rec['n'], rec['dim']
        p = f'{pc}in{cc}'
        if p not in E.PID or n > E.nmax(p) or n < E.NMIN:
            print('not an archive case:', p, n); continue
        pb = E.problem(p); m = d * (d - 1) // 2
        cen = [float(Fraction(str(x))) if isinstance(x, str) else float(x) for x in rec.get('container_center', [0] * d)]
        C = np.array([[float(x) for x in q[:d]] for q in rec['pieces']]) - np.array(cen)
        R = np.array([rotation([float(x) for x in q[d:d + m]], [int(x) for x in q[d + m:d + m + d]]) for q in rec['pieces']])
        C = C * pb.scale                                       # exact frame -> internal units (piece inradius 1/2)
        lg = ndsim.legalize(pb, C, R)
        with E.locked():
            case = E.load_case(p, n); cur = case['best']
            line = f"{p} n={n}: contributed s_full {float(rec['s_full']):.10f}, re-legalized s {lg['s']:.10f}, archive {cur['s'] if cur else None:.10f}"
            if cur and lg['s'] >= cur['s'] - 1e-12:
                print(line, '-> not better'); continue
            C2, R2 = E.rnd(lg['C'], lg['R'])
            case['best'] = {'s': lg['s'], 'C': C2, 'R': R2, 't': __import__('time').time(), 'tightened': True,
                            'src': {'move': 'community', 'contributor': who, 'issue': int(issue)}}
            st = case['stats']; st['improvements'] += 1; st['since'] = 0; st['last_improve'] = case['best']['t']; st['needs_tighten'] = True
            E.save_case(case)
            E.pool_insert(p, n, {'s': lg['s'], 'C': C2, 'R': R2, 'src': 'community', 't': case['best']['t'], 'lineage': who})
            E.enforce_monotone(p, print)
            with open(os.path.join(E.STATE, 'attempts.jsonl'), 'a') as fa:
                fa.write(json.dumps({'t': round(case['best']['t']), 'p': p, 'n': n, 'move': 'community', 'raw': lg['s'], 's': lg['s'],
                                     'best_before': cur['s'] if cur else None, 'improved': True, 'secs': 0, 'raw_secs': 0,
                                     'host': f'issue-{issue}'}) + '\n')
        print(line, '-> NEW BEST, credited to', who); took.append((p, n))
    print(f'{len(took)} contributed packings entered the archive')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
