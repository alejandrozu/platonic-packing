import json, sys
from mpmath import mp, matrix, fabs, eye
mp.dps = 60
D = json.load(open(sys.argv[1])); key = sys.argv[2]
def polar(A):
    X = A.copy()
    for _ in range(80): X = (X + (X**-1).T) / 2
    return X
R = polar(matrix(D[key])); n = R.rows; p = D['p']; q = D['q']
orth = max(fabs(v) for v in (R * R.T - eye(n)))
w = [sum(fabs(R[i, k]) for k in range(n)) for i in range(n)]
x = [fabs(R[i, 0]) for i in range(n)]
S = sum(x); rests = [w[i] - x[i] for i in range(n)]
s = [1 if R[i, 0] >= 0 else -1 for i in range(n)]
Rn = matrix(n, n)
for i in range(n):
    for k in range(n): Rn[i, k] = s[i] * R[i, k]
t = 1 if Rn[p, q] >= 0 else -1
for i in range(n): Rn[i, q] *= t
c = Rn[p, q]; nu = Rn[p, 0]; L = w[p] - c
rows = [i for i in range(n) if i != p]; cols = [k for k in range(n) if k != q]
Q = matrix(n - 1, n - 1)
for ii, i in enumerate(rows):
    for kk, k in enumerate(cols): Q[ii, kk] = Rn[i, k] - Rn[i, q] * Rn[p, k] / (1 + c)
wQ = [sum(fabs(Q[i, k]) for k in range(n - 1)) for i in range(n - 1)]
def F(M, j): m = M.rows; return sum(fabs(M[i, j]) * (2 - sum(fabs(M[i, k]) for k in range(m))) for i in range(m))
FR = F(R, 0); FQ = F(Q, cols.index(0))
print('orth err %.1e' % float(orth), ' max row l1 - 2 = %.3e' % float(max(w) - 2), ' min rest - 1 = %.3e' % float(min(rests) - 1),
      ' S - 2 = %.4f' % float(S - 2))
print('unique argmin gap %.3e' % float(min(x[i] for i in range(n) if i != p) - x[p]),
      ' unique argmax gap %.3e' % float(c - max(fabs(Rn[p, k]) for k in range(1, n) if k != q)),
      ' L - (1+c) = %.3e' % float(L - 1 - c), ' max row l1 of Q - 2 = %.3e' % float(max(wQ) - 2))
print('nu = %.6e  F_j(R) = %.12f  F_j(Q) = %.12f  F_j(Q) - F_j(R) = %.6e' % (float(nu), float(FR), float(FQ), float(FQ - FR)))
