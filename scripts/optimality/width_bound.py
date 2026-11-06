#!/usr/bin/env python3
"""Axis-width bound for one piece in a cube: min over rotations of max_i (width of the piece along axis i).
A copy of the piece in a cube of side s has every axis width <= s, so s1 >= this bound (6 Nov 2026)."""
import json, os, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
def wb(piece, starts=300, seed=0):
    V = np.array(S[piece]['V'], float); rng = np.random.default_rng(seed); best = np.inf
    f = lambda rv: np.max(np.ptp(V @ Rotation.from_rotvec(rv).as_matrix().T, axis=0))
    for k in range(starts):
        r = minimize(f, Rotation.random(random_state=rng.integers(1 << 30)).as_rotvec(), method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 3000})
        best = min(best, r.fun)
    return best
if __name__ == '__main__':
    for p in sys.argv[1:]: print(p, f'{wb(p):.9f}')
