# Verify the counterexamples to the pivot conjecture at 50-digit precision.
# For each matrix: re-orthogonalise (polar factor, mpmath), check rows l1 <= 2, unique smallest |R_i0| at row p,
# unique largest |R_pk| (k != 0) at column q, admissibility L <= 1 + c, and compute Xi and the exact F_0(Q) - F_0(R).
import json, sys
from mpmath import mp, matrix, mpf, sqrt, fabs, eye
mp.dps = 50
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'pivot_counterexamples.json'))
def polar(A):
    X = A.copy()
    for _ in range(60):  # Newton iteration X <- (X + X^{-T})/2
        X = (X + (X**-1).T) / 2
    return X
def F(R, j):
    n = R.rows; return sum(fabs(R[i, j]) * (2 - sum(fabs(R[i, k]) for k in range(n))) for i in range(n))
for key, piv in (('R5', 'pivot5'), ('R6', 'pivot6')):
    R = polar(matrix(D[key])); n = R.rows; p, q = D[piv]['p'], D[piv]['q']
    orth = max(fabs(x) for x in (R * R.T - eye(n)))
    w = [sum(fabs(R[i, k]) for k in range(n)) for i in range(n)]
    s = [1 if R[i, 0] >= 0 else -1 for i in range(n)]            # normalise column 0 to be >= 0
    Rn = matrix(n, n)
    for i in range(n):
        for k in range(n): Rn[i, k] = s[i] * R[i, k]
    t = 1 if Rn[p, q] >= 0 else -1
    for i in range(n): Rn[i, q] *= t
    x = [Rn[i, 0] for i in range(n)]
    assert all(x[i] > x[p] for i in range(n) if i != p), 'p is not the unique smallest row'
    assert all(fabs(Rn[p, k]) < Rn[p, q] for k in range(1, n) if k != q), 'q is not the unique largest entry'
    c = Rn[p, q]; nu = x[p]; L = w[p] - c; a = 1 / (1 + c); k1 = 1 + c - (L - nu)
    Xi = nu * (c * (c + L) - 1)
    for i in range(n):
        if i == p: continue
        z = Rn[i, q]; y = x[i]; G = 2 - w[i]
        Xi += 2 * k1 * max(z, 0) * (y - a * nu * z) - nu * z * G
    # polar factor Q of the minor (rows != p, columns != q)
    rows = [i for i in range(n) if i != p]; cols = [k for k in range(n) if k != q]
    Q = matrix(n - 1, n - 1)
    for ii, i in enumerate(rows):
        for kk, k in enumerate(cols): Q[ii, kk] = Rn[i, k] - Rn[i, q] * Rn[p, k] / (1 + c)
    jq = cols.index(0)
    print(key, 'orth err %.1e' % float(orth), ' max row l1 %.12f' % float(max(w)), ' admissible', L <= 1 + c,
          ' max row l1 of Q %.6f' % float(max(sum(fabs(Q[i, k]) for k in range(n - 1)) for i in range(n - 1))))
    print('   nu = %.10f  c = %.10f  Xi = %.10e   exact F(Q)-F(R) = %.10e' % (float(nu), float(c), float(Xi), float(F(Q, jq) - F(Rn, 0))))
