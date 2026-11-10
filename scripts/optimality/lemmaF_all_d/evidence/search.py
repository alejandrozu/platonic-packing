"""Numerical evidence for restricted Lemma F in dimensions 3-16 (Paper IV, section "Numerical evidence").

For an orthogonal d x d matrix R put x = |column 0|, w_i = ||row i||_1 and F(R) = sum_i x_i (2 - w_i).
Restricted Lemma F: F(R) <= 1 whenever every w_i <= 2.  This is equivalent to s_d(2) = 2.

Experiments (one JSON line per run, appended to the output file):

  global   maximise F over restricted O(d)                                   (search for a counterexample)
  far      maximise F over restricted O(d) with max_i x_i^2 <= tau            (Hosono's far region, a profile in tau)
  free     maximise F over all of O(d) (unrestricted Lemma F)
  rc       maximise F over the remaining case of the induction: S = ||x||_1 >= 2 and every row has
           w_i - x_i >= 1, i.e. no entry of column 0 admits the near step   (where a counterexample would have to be)

Method: batched multi-start optimisation on SO(d).  R = R0 expm(A - A^T), Adam on A, |t| smoothed to
sqrt(t^2 + eps^2) - eps with eps annealed from 1e-2 to 1e-9, step size from 2e-2 to 6e-6, constraints by quadratic plus linear penalties whose
weight grows geometrically; every 200 steps R0 <- R and A <- 0.  Start families: Haar; signed permutations times
expm of a small skew matrix (near the equality set); block-diagonal [1] + R' with R' containing the flat row
(1/2,1/2,1/2,1/2) (the near-equality cases that refute the pivot inequality); near-uniform columns; sink columns
(one large entry); Hadamard-like flat matrices where they exist.  Every reported value is recomputed exactly in
float64 at the end, and a point counts only if its constraint violation is at most 1e-9 (rows) and 1e-7 (region).

Usage: python3 search.py <experiment> <d> <starts> <seed> [tau] >> results.jsonl
"""
import json, math, sys, time
import numpy as np
import torch

torch.set_default_dtype(torch.float64)


def haar(B, d, g):
    Z = torch.randn(B, d, d, generator=g)
    Q, Rr = torch.linalg.qr(Z)
    return Q * torch.sign(torch.diagonal(Rr, dim1=-2, dim2=-1)).unsqueeze(-2)


def skew(B, d, scale, g):
    A = torch.randn(B, d, d, generator=g) * scale.view(-1, 1, 1)
    return A - A.transpose(-1, -2)


def signed_perm(B, d, g):
    P = torch.zeros(B, d, d)
    for b in range(B):
        p = torch.randperm(d, generator=g)
        s = torch.randint(0, 2, (d,), generator=g) * 2 - 1
        P[b, torch.arange(d), p] = s.double()
    return P


def flat_block(d, g):
    """[1] + R' with a 4x4 block containing the flat row (1/2,1/2,1/2,1/2), rest random."""
    H = 0.5 * torch.tensor([[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]], dtype=torch.float64)
    R = torch.eye(d)
    if d >= 5:
        R[1:5, 1:5] = H
        if d > 5:
            R[5:, 5:] = haar(1, d - 5, g)[0]
    return R


def starts(B, d, g):
    fam = torch.arange(B) % 6
    R = haar(B, d, g)
    sc = torch.rand(B, generator=g) * 0.6 + 0.02
    near = signed_perm(B, d, g) @ torch.linalg.matrix_exp(skew(B, d, sc, g))
    R = torch.where((fam == 1).view(-1, 1, 1), near, R)
    fb = torch.stack([flat_block(d, g) for _ in range(B)]) @ torch.linalg.matrix_exp(skew(B, d, sc * 0.3, g))
    R = torch.where((fam == 2).view(-1, 1, 1), fb, R)
    # near-uniform and sink columns: complete a prescribed first column to an orthogonal matrix
    for b in range(B):
        if fam[b] in (3, 4):
            if fam[b] == 3:
                col = (1 + 0.4 * torch.randn(d, generator=g)).abs()
            else:
                col = 0.15 * torch.randn(d, generator=g).abs()
                col[0] = 0.6 + 0.35 * torch.rand(1, generator=g)
            col = col / col.norm()
            M = torch.cat([col.view(-1, 1), torch.randn(d, d - 1, generator=g)], 1)
            Q, Rr = torch.linalg.qr(M)
            Q = Q * torch.sign(torch.diagonal(Rr)).view(1, -1)
            R[b] = Q
        elif fam[b] == 5 and d % 4 == 0:
            Hm = torch.tensor([[1.0]])
            while Hm.shape[0] < d:
                if 2 * Hm.shape[0] <= d and (d % (2 * Hm.shape[0]) == 0):
                    Hm = torch.cat([torch.cat([Hm, Hm], 1), torch.cat([Hm, -Hm], 1)], 0)
                else:
                    break
            if Hm.shape[0] == d:
                R[b] = (Hm / math.sqrt(d)) @ torch.linalg.matrix_exp(skew(1, d, sc[b:b + 1] * 0.3, g))[0]
    return R


def sabs(t, eps):
    return torch.sqrt(t * t + eps * eps) - eps


def objective(R, eps, mu, exp, tau):
    a = sabs(R, eps)
    w = a.sum(-1)
    x = a[..., :, 0]
    F = (x * (2 - w)).sum(-1)
    pen = torch.relu(w - 2)
    viol = (pen ** 2).sum(-1) + 1e-2 * pen.sum(-1)
    if exp == "free":
        viol = torch.zeros_like(F)
    if exp == "far":
        v = torch.relu(R[..., :, 0] ** 2 - tau)
        viol = viol + (v ** 2).sum(-1) + 1e-2 * v.sum(-1)
    if exp == "rc4":
        # RC4: the remaining case, and the smallest row p of column 0 is spread with c^2 < 3/4 at its largest entry
        p = torch.argmin(x, dim=-1).detach()
        rowp = a[torch.arange(a.shape[0]), p]                  # smoothed |row p|
        others = rowp[..., 1:]
        c = others.max(-1).values
        nu = rowp[..., 0]
        rho = rowp.sum(-1) - c - nu
        v3 = torch.relu(c * c - 0.75 + 1e-4)
        v4 = torch.relu(c + nu / 2 - rho + 1e-4)
        viol = viol + v3 ** 2 + 1e-2 * v3 + v4 ** 2 + 1e-2 * v4
    if exp in ("rc", "rcS", "rc4"):
        v1 = torch.relu((tau if exp == "rcS" else 2) - x.sum(-1))
        v2 = torch.relu(1 - (w - x))
        viol = viol + v1 ** 2 + 1e-2 * v1 + (v2 ** 2).sum(-1) + 1e-2 * v2.sum(-1)
    return F, viol


def exact(R, exp, tau):
    R = R.detach().numpy()
    a = np.abs(R)
    w = a.sum(-1)
    x = a[:, :, 0]
    F = (x * (2 - w)).sum(-1)
    orth = np.abs(np.einsum("bij,bkj->bik", R, R) - np.eye(R.shape[1])).max(axis=(1, 2))
    ok = (w.max(-1) <= 2 + 1e-9) & (orth <= 1e-10)
    if exp == "free":
        ok = orth <= 1e-10
    if exp == "far":
        ok &= (R[:, :, 0] ** 2).max(-1) <= tau + 1e-7
    if exp in ("rc", "rcS", "rc4"):
        ok &= x.sum(-1) >= (tau if exp == "rcS" else 2) - 1e-7
        ok &= (w - x).min(-1) >= 1 - 1e-7
    if exp == "rc4":
        for b in range(R.shape[0]):
            if not ok[b]:
                continue
            for p in np.flatnonzero(x[b] <= x[b].min() + 1e-9):       # every smallest row
                rest = a[b, p, 1:]
                for q in np.flatnonzero(rest >= rest.max() - 1e-9):   # every largest entry outside column 0
                    c, nu = rest[q], a[b, p, 0]
                    rho = a[b, p].sum() - c - nu
                    if not (c * c < 0.75 and rho > c + nu / 2):
                        ok[b] = False
    return F, ok, x, w


def run(exp, d, B, seed, tau=None, steps=6000):
    g = torch.Generator().manual_seed(seed)
    R0 = starts(B, d, g)
    A = torch.zeros(B, d, d, requires_grad=True)
    opt = torch.optim.Adam([A], lr=0.02)
    t0 = time.time()
    for it in range(steps):
        frac = it / steps
        eps = 10 ** (-2 - 7 * frac)
        mu = 10 ** (1 + 5 * frac)
        S = A - A.transpose(-1, -2)
        R = R0 @ torch.linalg.matrix_exp(S)
        F, viol = objective(R, eps, mu, exp, tau)
        loss = (-F + mu * viol).sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
        if it % 200 == 199:
            with torch.no_grad():
                R0 = R0 @ torch.linalg.matrix_exp(A - A.transpose(-1, -2))
                R0, _ = torch.linalg.qr(R0)  # re-orthonormalise (columns may flip sign; F is invariant)
                A.zero_()
            opt = torch.optim.Adam([A], lr=0.02 * 10 ** (-3.5 * frac))
    with torch.no_grad():
        R = R0 @ torch.linalg.matrix_exp(A - A.transpose(-1, -2))
        R, _ = torch.linalg.qr(R)
    F, ok, x, w = exact(R, exp, tau)
    res = {"exp": exp, "d": d, "starts": B, "seed": seed, "tau": tau, "steps": steps,
           "feasible": int(ok.sum()), "time_s": round(time.time() - t0, 1)}
    if ok.any():
        Fo = np.where(ok, F, -np.inf)
        b = int(np.argmax(Fo))
        res.update({"maxF": float(F[b]), "argmax_maxcol": float(x[b].max()), "argmax_S": float(x[b].sum()),
                    "argmax_maxrow": float(w[b].max()), "argmax_minrest": float((w[b] - x[b]).min()),
                    "count_F_gt_1": int((Fo > 1 + 1e-12).sum()),
                    "top5": [float(v) for v in np.sort(Fo[np.isfinite(Fo)])[-5:][::-1]]})
        np.save(f"best_{exp}_d{d}_tau{tau}_s{seed}.npy", R[b].numpy())
    return res


if __name__ == "__main__":
    exp, d, B, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    tau = float(sys.argv[5]) if len(sys.argv) > 5 else None
    print(json.dumps(run(exp, d, B, seed, tau)), flush=True)
