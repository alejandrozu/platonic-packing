"""Conjecture H and the largest cube in a simplex: numerical tests in dimensions 3-16 (Paper IV).

For a unit vector v >= 0 in R^d and an orthonormal basis (frame) C of v^perp (a d x (d-1) matrix) put
Value(C) = sum_i v_i ||row_i(C)||_1.  Lemma F (unrestricted) is Value(C) >= 2(||v||_1 - 1) for every frame.
Conjecture H: the minimum of Value over frames is the Helmert value
    H(v) = 2 sum_{k>=2} v_k sqrt(A_k / A_{k+1}),   v sorted decreasingly, A_k = v_1^2 + ... + v_{k-1}^2.
Geometrically, a unit (d-1)-cube fits in the simplex {xi > 0, <v, xi> = lam} iff lam > Value(C)/2 for its frame C.

For each family of v, minimise Value over frames from many starts (random frames, and perturbed Helmert frames),
by Adam on SO(d-1) with |t| smoothed to sqrt(t^2+eps^2)-eps, eps annealed to 1e-9, and report the smallest value
found (recomputed exactly) against H(v) and 2(S-1).

Usage: python3 frames.py <d> <starts> <seed> >> frames.jsonl
"""
import json, math, sys, time
import numpy as np
import torch

torch.set_default_dtype(torch.float64)


def helmert_value(v):
    w = np.sort(v)[::-1]
    A = np.concatenate([[0.0], np.cumsum(w ** 2)])  # A[k] = w_0^2 + ... + w_{k-1}^2
    return 2 * sum(w[k] * math.sqrt(A[k] / A[k + 1]) for k in range(1, len(w)))


def helmert_frame(v):
    d = len(v)
    order = np.argsort(-v)
    w = v[order]
    cols = []
    for k in range(1, d):
        b = np.zeros(d)
        b[k] = (w[:k] ** 2).sum()
        b[:k] = -w[k] * w[:k]
        b /= np.linalg.norm(b)
        cols.append(b)
    C = np.zeros((d, d - 1))
    C[order, :] = np.array(cols).T
    return C


def families(d, rng):
    fams = []
    fams.append(("uniform", np.ones(d)))
    for t in range(3):
        fams.append((f"random{t}", np.abs(rng.normal(size=d))))
    for t in range(2):
        fams.append((f"sparse{t}", np.abs(rng.normal(size=d)) ** 3))
    for c in (0.9, 0.7, 0.5):
        v = np.full(d, math.sqrt((1 - c * c) / (d - 1)))
        v[0] = c
        fams.append((f"sink{c}", v))
    fams.append(("geometric0.8", 0.8 ** np.arange(d)))
    if d >= 3:
        v = np.full(d, math.sqrt((1 - 2 * 0.36) / (d - 2)))
        v[:2] = 0.6
        fams.append(("two0.6", v))
    return [(n, v / np.linalg.norm(v)) for n, v in fams]


def value(C, v, eps):
    a = torch.sqrt(C * C + eps * eps) - eps
    return (a.sum(-1) * v).sum(-1)


def minimise(v, B, g, steps=4000):
    d = len(v)
    n = d - 1
    vt = torch.tensor(v)
    # starts: half random frames, half perturbed Helmert frames
    Z = torch.randn(B, d, d, generator=g)
    Z[:, :, 0] = vt
    Q, Rr = torch.linalg.qr(Z)
    Q = Q * torch.sign(torch.diagonal(Rr, dim1=-2, dim2=-1)).unsqueeze(-2)
    C0 = Q[:, :, 1:].clone()
    Hf = torch.tensor(helmert_frame(v))
    half = B // 2
    E = torch.randn(half, n, n, generator=g) * 0.05
    E = E - E.transpose(-1, -2)
    C0[:half] = Hf @ torch.linalg.matrix_exp(E)
    A = torch.zeros(B, n, n, requires_grad=True)
    opt = torch.optim.Adam([A], lr=0.02)
    for it in range(steps):
        frac = it / steps
        eps = 10 ** (-2 - 7 * frac)
        C = C0 @ torch.linalg.matrix_exp(A - A.transpose(-1, -2))
        loss = value(C, vt, eps).sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
        if it % 200 == 199:
            with torch.no_grad():
                C0 = C0 @ torch.linalg.matrix_exp(A - A.transpose(-1, -2))
                C0, _ = torch.linalg.qr(C0)
                A.zero_()
            opt = torch.optim.Adam([A], lr=0.02 * 10 ** (-3.5 * frac))
    with torch.no_grad():
        C = C0 @ torch.linalg.matrix_exp(A - A.transpose(-1, -2))
        C, _ = torch.linalg.qr(C)
    C = C.numpy()
    perp = np.abs(np.einsum("bij,i->bj", C, v)).max(-1)
    orth = np.abs(np.einsum("bij,bik->bjk", C, C) - np.eye(n)).max(axis=(1, 2))
    vals = (np.abs(C).sum(-1) * v).sum(-1)
    ok = (perp < 1e-10) & (orth < 1e-10)
    vals = np.where(ok, vals, np.inf)
    b = int(np.argmin(vals))
    rows_aligned = int(((np.abs(C[b]) > 1e-4).sum(-1) == 1).sum())  # rows with one nonzero entry: a facet-parallel cube
    return float(vals[b]), int(ok.sum()), rows_aligned, C[b]


if __name__ == "__main__":
    d, B, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = np.random.default_rng(seed)
    g = torch.Generator().manual_seed(seed)
    for name, v in families(d, rng):
        t0 = time.time()
        best, nok, aligned, C = minimise(v, B, g)
        H = helmert_value(v)
        print(json.dumps({"d": d, "family": name, "starts": B, "seed": seed, "feasible": nok,
                          "helmert": H, "min_found": best, "gap": best - H, "lemmaF_bound": 2 * (v.sum() - 1),
                          "aligned_rows_at_min": aligned, "v": [float(t) for t in v],
                          "time_s": round(time.time() - t0, 1)}), flush=True)
