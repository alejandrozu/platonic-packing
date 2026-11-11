"""Closed forms and small computations for Paper IV; writes closed_forms.json.

1. Hosono's spectral bound at the uniform column, q_d = (d-1) sqrt(2/d) - 2 (sqrt d - 1).  It is also the value of the
   isotropic relaxation of Lemma F at the uniform column (measure uniform on (e_a - e_b)/sqrt 2), so both fail from d = 6.
2. The largest n-cube in the regular n-simplex of unit edge (n = d - 1): the value predicted by Conjecture H,
   sigma_n = 1 / (sqrt 2 * sum_{k=2}^{n+1} sqrt(1 - 1/k)); the bound given by Lemma F, 1 / (sqrt 2 (d - sqrt d));
   and the volume bound vol(simplex)^(1/n) = (sqrt(n+1) / (n! 2^(n/2)))^(1/n).
3. Near the equality set: (1 - F_j)/theta_j^2 for R = P expm(t A), theta_j the angle between column j and the nearest
   axis, over random skew A (t = 1e-3); and the same for rotations in one coordinate plane (exactly (sigma-1)^2/theta^2).
4. The averaged identity sum_j (1 - F_j(R)) = sum_i (w_i - 1)^2, checked on random orthogonal matrices.
"""
import json, math
import numpy as np
from scipy.linalg import expm
from scipy.stats import special_ortho_group

out = {"spectral_uniform": {}, "regular_simplex": {}, "near_identity": {}, "averaged_identity_max_error": {}}
for d in range(2, 33):
    out["spectral_uniform"][d] = (d - 1) * math.sqrt(2 / d) - 2 * (math.sqrt(d) - 1)
for n in range(1, 32):
    d = n + 1
    H_unif = (2 / math.sqrt(d)) * sum(math.sqrt((k - 1) / k) for k in range(2, d + 1))
    sigma = 1 / (math.sqrt(2) * sum(math.sqrt(1 - 1 / k) for k in range(2, n + 2)))
    assert abs(sigma - math.sqrt(2) / (math.sqrt(d) * H_unif)) < 1e-14
    lemF = 1 / (math.sqrt(2) * (d - math.sqrt(d)))
    vol = (math.sqrt(n + 1) / (math.factorial(n) * 2 ** (n / 2))) ** (1 / n)
    out["regular_simplex"][n] = {"conjecture_H": sigma, "lemmaF_bound": lemF, "volume_bound": vol, "helmert_value_uniform": H_unif}

rng = np.random.default_rng(1)


def F(R, j):
    w = np.abs(R).sum(1)
    return (np.abs(R[:, j]) * (2 - w)).sum()


for d in range(3, 17):
    worst = 9.0
    for _ in range(4000):
        A = rng.normal(size=(d, d))
        A = A - A.T
        A /= np.linalg.norm(A)
        R = expm(1e-3 * A)
        for j in range(d):
            th = math.acos(min(1.0, np.abs(R[:, j]).max()))
            if th > 1e-6:
                worst = min(worst, (1 - F(R, j)) / th ** 2)
    out["near_identity"][d] = worst
    err = 0.0
    for _ in range(200):
        R = special_ortho_group.rvs(d, random_state=rng)
        w = np.abs(R).sum(1)
        err = max(err, abs(sum(1 - F(R, j) for j in range(d)) - ((w - 1) ** 2).sum()))
    out["averaged_identity_max_error"][d] = err
th = 1e-3
out["near_identity_plane_rotation"] = (math.cos(th) + math.sin(th) - 1) ** 2 / th ** 2
json.dump(out, open("closed_forms.json", "w"), indent=1)
print({d: round(v, 5) for d, v in out["spectral_uniform"].items() if d <= 10})
print({n: round(v["conjecture_H"], 5) for n, v in out["regular_simplex"].items() if n <= 8})
print({d: round(v, 4) for d, v in out["near_identity"].items()})
print(max(out["averaged_identity_max_error"].values()))
