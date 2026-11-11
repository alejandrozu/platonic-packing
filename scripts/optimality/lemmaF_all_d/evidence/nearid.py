"""Near the equality set: minimise (1 - F_0(R))/theta^2 over R = expm(t A), t = 1e-3, A skew with ||A|| = 1, where
theta is the angle between column 0 and e_0.  Writes nearid.json."""
import json, math, sys
import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
rng = np.random.default_rng(3); out = {}
for d in range(3, 11):
    iu = np.triu_indices(d, 1); t = 1e-3
    def ratio(v):
        A = np.zeros((d, d)); A[iu] = v; A = A - A.T; A /= np.linalg.norm(A)
        R = expm(t * A); x = np.abs(R[:, 0]); w = np.abs(R).sum(1)
        th = math.acos(min(1.0, x[0]))
        return (1 - (x * (2 - w)).sum()) / th ** 2 if th > 1e-9 else 9.0
    best = 9.0
    for s in range(40):
        r = minimize(ratio, rng.normal(size=len(iu[0])), method='Nelder-Mead', options={'maxiter': 4000, 'xatol': 1e-9, 'fatol': 1e-12})
        best = min(best, r.fun)
    out[d] = best; print(d, best, flush=True)
json.dump(out, open('nearid.json', 'w'), indent=1)
