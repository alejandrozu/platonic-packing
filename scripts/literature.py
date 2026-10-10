#!/usr/bin/env python3
"""Import published packings (docs/literature/) into the search archive.

usage: python3 scripts/literature.py [--dry]

Each packing is converted to the engine's internal units, legalized (separating-axis test) and its tightest container
computed. It always joins the case's pool of starting points; it becomes the archived best when it beats ours, with
src = {'move': 'literature', 'source': ...}, and our previous best stays in the pool. From then on hops start from
both, and a new best for that case means beating the published packing."""
import json, os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import exact
import engine

LIT = os.path.join(ROOT, 'docs', 'literature')
SOURCES = [
    ('cubincub', 'hyra_cubincub_n11.json', 'H. Lin, July 2026 (Tencent-Hunyuan/Hyra-results)'),
    ('cubincub', 'hyra_cubincub_n12.json', 'H. Lin, July 2026 (Tencent-Hunyuan/Hyra-results)'),
    ('cubincub', 'nakajima_cubincub_n12.json', 'Y. Nakajima, Oct 2026 (soft-to-rigid-packing)'),
    ('octincub', 'hyra_octincub_n21.json', 'H. Lin, July 2026 (Tencent-Hunyuan/Hyra-results)'),
    ('octincub', 'hyra_octincub_n24.json', 'H. Lin, July 2026 (Tencent-Hunyuan/Hyra-results)'),
]


def load(p, fn):
    d = json.load(open(os.path.join(LIT, fn)))
    P = np.array(d['pieces'], float)
    cen = d.get('container_center')
    cen = np.full(3, cen[0] if len(cen) == 1 else 0) if cen and len(cen) == 1 else (np.array(cen) if cen else np.full(3, d['s_full'] / 2))
    pb = engine.problem(p)
    C = (P[:, :3] - cen) * pb.edge                          # unit-edge coordinates -> internal units, centred
    Q = [list(q / np.linalg.norm(q)) for q in P[:, 3:]]
    R = [exact.quat_to_R(np.array(q)) for q in Q]
    L, _, C0 = exact.certify(pb, C, R)                      # legal (no overlap) at tolerance 1e-12
    Lt, t = exact.tight_container(pb, C0, R)
    s = pb.s_of_L(Lt)
    return len(P), s, (C0 + t).tolist(), Q, d['s_full']


def main(dry=False):
    with engine.locked():
        for p, fn, src in SOURCES:
            n, s, C, Q, s_pub = load(p, fn)
            case = engine.load_case(p, n); cur = case['best']
            cand = {'s': s, 'C': C, 'Q': Q, 'src': 'literature', 'source': src, 't': time.time()}
            take = cur is None or s < cur['s'] - 1e-12
            print(f"{p} n={n:2d} {fn:28s} published {s_pub:.10f} -> tight {s:.10f} | ours {cur['s']:.10f} | "
                  f"{'IMPORT as best' if take else 'pool only'}")
            if dry: continue
            if cur: engine.pool_insert(p, n, {'s': cur['s'], 'C': cur['C'], 'Q': cur['Q'], 'src': 'ours', 't': time.time()})
            engine.pool_insert(p, n, cand)
            if take:
                case['best'] = {'s': s, 'C': C, 'Q': Q, 'src': {'move': 'literature', 'source': src, 'file': f'docs/literature/{fn}'},
                                't': time.time(), 'tightened': True}
                case['stats']['since'] = 0
                engine.save_case(case)
        if not dry:
            for p in {s[0] for s in SOURCES}: engine.enforce_monotone(p, print)


if __name__ == '__main__':
    main('--dry' in sys.argv)
