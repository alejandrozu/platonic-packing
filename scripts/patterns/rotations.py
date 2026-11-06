"""Relative-orientation spectrum (rotational patterns), 3D records.

For each record with 2-8 orientation classes, the relative rotation between two classes a, b is
R_a^-1 R_b modulo the piece's proper symmetries: the smallest rotation angle over g in G+ of R_a^-1 R_b g, with its
axis. The angle is called rational when theta/360 deg is within 3e-6 of p/q with q <= 24 (e.g. 45, 60, 36, 30, 15
degrees). Output: docs/patterns/rotations3d.json (per record: angles, rational flags, axes) and a summary.
"""
import json, os, sys, glob, collections
from fractions import Fraction
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'scripts', 'patterns'))
import symmetry
from features import SOL, quat_to_R, orient_classes


def angle_axis(M):
    c = np.clip((np.trace(M) - 1) / 2, -1, 1); th = np.degrees(np.arccos(c))
    w = np.array([M[2, 1] - M[1, 2], M[0, 2] - M[2, 0], M[1, 0] - M[0, 1]])
    ax = w / np.linalg.norm(w) if np.linalg.norm(w) > 1e-9 else None
    return th, ax


def rational(th, qmax=24, tol=3e-6):
    f = Fraction(th / 360).limit_denominator(qmax)
    return (abs(float(f) - th / 360) < tol, f)


def main():
    out = []; G = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'records', '*', '*_n*.json'))):
        try: d = json.load(open(f))
        except Exception: continue
        if not isinstance(d, dict) or 'pieces' not in d or d.get('dim', 3) != 3: continue
        piece = d['piece']
        if piece not in SOL: continue
        if piece not in G: G[piece] = [g for g in symmetry.sym_group(piece) if np.linalg.det(g) > 0]
        P = np.array(d['pieces'], float); R = [quat_to_R(q) for q in P[:, 3:7]]
        oc = orient_classes(R, G[piece], 1e-3)
        if not (2 <= len(oc) <= 8): continue
        reps = [R[c[0]] for c in oc]
        angs = []
        for a in range(len(reps)):
            for b in range(a + 1, len(reps)):
                M0 = reps[a].T @ reps[b]
                best = min((angle_axis(M0 @ g) for g in G[piece]), key=lambda x: x[0])
                ok, fr = rational(best[0])
                angs.append({'theta': round(float(best[0]), 6), 'rational': bool(ok), 'turn': str(fr) if ok else None,
                             'axis': None if best[1] is None else np.round(best[1], 4).tolist()})
        out.append({'record_id': d['record_id'], 'piece': piece, 'container': d['container'], 'n': d['n'],
                    'classes': [len(c) for c in oc], 'relative': angs})
    json.dump(out, open(os.path.join(ROOT, 'docs', 'patterns', 'rotations3d.json'), 'w'))
    allang = [a for r in out for a in r['relative']]
    rat = [a for a in allang if a['rational']]
    turns = collections.Counter(a['turn'] for a in rat)
    full = sum(1 for r in out if r['relative'] and all(a['rational'] for a in r['relative']))
    irr = collections.Counter(round(a['theta'], 3) for a in allang if not a['rational'] and a['theta'] > 0.5)
    summ = {'records': len(out), 'pairs': len(allang), 'rational_pairs': len(rat), 'records_all_rational': full,
            'top_turns': [(t, c, round(float(Fraction(t)) * 360, 3)) for t, c in turns.most_common(15)],
            'recurring_irrational': [(t, c) for t, c in irr.most_common(10) if c >= 5]}
    json.dump(summ, open(os.path.join(ROOT, 'docs', 'patterns', 'rotations_summary.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
