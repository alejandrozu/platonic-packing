"""Emit Lean for a sphere certificate (gensphere): line lemmas, per-coordinate case lemma, final inequality."""
import pickle, sys, math
from fractions import Fraction as Fr
from gensphere import certify


def q(x):
    x = Fr(x)
    if x.denominator == 1: return f'({x.numerator} : ℝ)' if x.numerator >= 0 else f'(({x.numerator}) : ℝ)'
    return f'({x.numerator} / {x.denominator} : ℝ)' if x.numerator >= 0 else f'((-{-x.numerator}) / {x.denominator} : ℝ)'


def emit(name, lam, n, breaks, picks, U, cap=None, doc=''):
    lam = Fr(lam); out = []
    ivals = list(zip(breaks[:-1], breaks[1:]))
    for j, ((lo, hi), L) in enumerate(zip(ivals, picks)):
        al, be = L['al'], L['be']
        hyps = f'(s : ℝ) (hs : 0 ≤ s)' + (f' (hlo : {q(lo * lo)} ≤ s ^ 2)' if lo > 0 else '') + f' (hhi : s ^ 2 ≤ {q(hi * hi)})'
        out.append(f'theorem {name}_line{j} {hyps} :\n    s ^ 3 + {q(lam)} * s ≤ {q(al)} + {q(be)} * s ^ 2 := by')
        out.append(f'  have hh : s ≤ {q(hi)} := by nlinarith')
        if L['kind'] == 'tan':
            out.append(f'  have hu : s ≤ {q(L["u"])} := by linarith')
            out.append(f'  nlinarith [mul_nonneg (sq_nonneg (s - {q(L["t0"])})) (sub_nonneg.2 hu)]')
        else:
            out.append(f'  have ha : {q(L["a"])} ≤ s := by nlinarith')
            out.append(f'  have hb : s ≤ {q(L["b"])} := by linarith')
            out.append(f'  have hu : {q(L["u"])} ≤ s := by linarith')
            out.append(f'  nlinarith [mul_nonneg (mul_nonneg (sub_nonneg.2 ha) (sub_nonneg.2 hb)) (sub_nonneg.2 hu)]')
        out.append('')
    # case lemma
    k = len(ivals)
    disj = []
    for j, ((lo, hi), L) in enumerate(zip(ivals, picks)):
        parts = []
        if lo > 0: parts.append(f'{q(lo * lo)} ≤ s ^ 2')
        if j < k - 1: parts.append(f's ^ 2 ≤ {q(hi * hi)}')
        parts.append(f's ^ 3 + {q(lam)} * s ≤ {q(L["al"])} + {q(L["be"])} * s ^ 2')
        disj.append('(' + ' ∧ '.join(parts) + ')')
    top = ivals[-1][1]
    out.append(f'theorem {name}_cases (s : ℝ) (hs : 0 ≤ s) (hcap : s ^ 2 ≤ {q(top * top)}) :\n    ' + ' ∨\n    '.join(disj) + ' := by')
    for j in range(k):
        lo, hi = ivals[j]
        wrap = lambda t, m: ('Or.inr <| ' * m) + t
        if j < k - 1:
            out.append(f'  rcases le_total (s ^ 2) {q(hi * hi)} with h{j} | h{j}')
            args = 'hs' + (f' h{j-1}' if lo > 0 else '') + f' h{j}'
            body = ([f'h{j-1}'] if lo > 0 else []) + [f'h{j}', f'{name}_line{j} s {args}']
            out.append('  · exact ' + wrap(f'Or.inl ⟨{", ".join(body)}⟩', j))
        else:
            args = 'hs' + (f' h{j-1}' if lo > 0 else '') + ' hcap'
            body = ([f'h{j-1}'] if lo > 0 else []) + [f'{name}_line{j} s {args}']
            out.append('  exact ' + wrap(f'⟨{", ".join(body)}⟩', j))
    out.append('')
    vs = [f's{i}' for i in range(n)]
    hyps = ' '.join(f'(h{i} : 0 ≤ s{i})' for i in range(n))
    caps = ' '.join(f'(c{i} : s{i} ^ 2 ≤ {q(top * top)})' for i in range(n))
    ssum = ' + '.join(f's{i} ^ 2' for i in range(n))
    tot = ' + '.join(f'(s{i} ^ 3 + {q(lam)} * s{i})' for i in range(n))
    out.append(f'set_option maxHeartbeats 0 in')
    if doc: out.append(f'/-- {doc} -/')
    out.append(f'theorem {name} ({" ".join(vs)} : ℝ) {hyps}\n    {caps}\n    (hs : {ssum} = 1) :\n    {tot} ≤ {q(U)} := by')
    for i in range(n): out.append(f'  have e{i} := sq_nonneg s{i}')
    rc = ' <;>\n  '.join(f'rcases {name}_cases s{i} h{i} c{i} with ' + ' | '.join(
        ('⟨' + ', '.join(([f'a{i}_{j}'] if ivals[j][0] > 0 else []) + ([f'b{i}_{j}'] if j < k - 1 else []) + [f'f{i}_{j}']) + '⟩') for j in range(k))
        for i in range(n))
    out.append('  ' + rc + ' <;>\n  linarith')
    out.append('')
    return '\n'.join(out)


if __name__ == '__main__':
    pkl, name, lam, n, U = sys.argv[1], sys.argv[2], Fr(sys.argv[3]), int(sys.argv[4]), Fr(sys.argv[5])
    best = pickle.load(open(pkl, 'rb'))
    w, (br, tg, picks, arg) = best
    print(f'-- certified LP bound {float(w)} <= U = {float(U)}', file=sys.stderr)
    assert w <= U
    print(emit(name, lam, n, br, picks, U))
