"""Import the large-n study packings (largen workflow branches, checked out under DIR/<problem>/best/*.json) into the
archive: each is re-legalized and measured here (exact.certify) and kept only if smaller than the case's best.

    python3 scripts/import_largen.py DIR

The engine and the publisher ignore n > 40 until PP_NMAX is raised."""
import sys, json, glob, os, time; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'src'))
import numpy as np, engine, exact
R = sys.argv[1] if len(sys.argv) > 1 else 'largen-results'
tot = new = 0
for f in sorted(glob.glob(R + '/*/best/*.json')):
    b = json.load(open(f)); p, n = b['problem'], b['n']
    if n <= 40: continue
    pb = engine.problem(p)
    R_ = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in b['Q']]
    L, _, C0 = exact.certify(pb, np.array(b['C']), R_)
    s = pb.s_of_L(L); tot += 1
    with engine.locked():
        case = engine.load_case(p, n); cur = case['best']
        if cur and s >= cur['s'] - 1e-9: continue
        case['best'] = {'s': s, 'C': C0.tolist(), 'Q': b['Q'], 'src': {'move': 'largen-study', 'how': b.get('how')}, 't': time.time(), 'tightened': True}
        st = case['stats']; st['improvements'] += 1; st['last_improve'] = time.time()
        engine.save_case(case); new += 1
print('imported', new, 'of', tot)
