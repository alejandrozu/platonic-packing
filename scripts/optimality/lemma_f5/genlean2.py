"""Emit Lean for a max-designated sphere certificate (optsphere2 pickle).

  {name}_core : s0 largest, others <= s0, sum of squares 1 (caps optional)  ->  sum (s^3 + lam s) <= U
  {name}      : general nonnegative s (caps optional), by a tournament for the largest coordinate
"""
import pickle, sys
from fractions import Fraction as Fr
from genlean import q


def line_lemma(nm, lam, lo, hi, L):
    out = []
    hyps = f'(s : ℝ) (hs : 0 ≤ s)' + (f' (hlo : {q(lo * lo)} ≤ s ^ 2)' if lo > 0 else '') + f' (hhi : s ^ 2 ≤ {q(hi * hi)})'
    out.append(f'theorem {nm} {hyps} :\n    s ^ 3 + {q(lam)} * s ≤ {q(L["al"])} + {q(L["be"])} * s ^ 2 := by')
    out.append(f'  have hh : s ≤ {q(hi)} := by nlinarith')
    if L['kind'] == 'tan':
        out.append(f'  have hu : s ≤ {q(L["u"])} := by linarith')
        out.append(f'  nlinarith [mul_nonneg (sq_nonneg (s - {q(L["t0"])})) (sub_nonneg.2 hu)]')
    else:
        out.append(f'  have ha : {q(L["a"])} ≤ s := by nlinarith')
        out.append(f'  have hu : {q(L["u"])} ≤ s := by linarith')
        out.append(f'  nlinarith [mul_nonneg (mul_nonneg (sub_nonneg.2 ha) (sub_nonneg.2 hh)) (sub_nonneg.2 hu)]')
    return out


def cases_lemma(nm, lam, ivals, lines):
    """s in [lo_0, hi_last] (as squares) -> disjunction over intervals."""
    k = len(ivals); out = []
    lo0, top = ivals[0][0], ivals[-1][1]
    disj = []
    for j, ((lo, hi), L) in enumerate(zip(ivals, lines)):
        parts = []
        if lo > 0: parts.append(f'{q(lo * lo)} ≤ s ^ 2')
        parts.append(f's ^ 2 ≤ {q(hi * hi)}')
        parts.append(f's ^ 3 + {q(lam)} * s ≤ {q(L["al"])} + {q(L["be"])} * s ^ 2')
        disj.append('(' + ' ∧ '.join(parts) + ')')
    hlo = f' (hlo : {q(lo0 * lo0)} ≤ s ^ 2)' if lo0 > 0 else ''
    out.append(f'theorem {nm}_cases (s : ℝ) (hs : 0 ≤ s){hlo} (hcap : s ^ 2 ≤ {q(top * top)}) :\n    ' + ' ∨\n    '.join(disj) + ' := by')
    if k == 1:
        args = 'hs' + (' hlo' if lo0 > 0 else '') + ' hcap'
        out.append(f'  exact ⟨{"hlo, " if lo0 > 0 else ""}hcap, {nm}_{0} s {args}⟩')
        return out
    for j in range(k):
        lo, hi = ivals[j]
        prevh = (f'h{j-1}' if j > 0 else ('hlo' if lo0 > 0 else None))
        wrap = lambda t, m: ('Or.inr <| ' * m) + t
        if j < k - 1:
            out.append(f'  rcases le_total (s ^ 2) {q(hi * hi)} with h{j} | h{j}')
            args = 'hs' + (f' {prevh}' if prevh else '') + f' h{j}'
            body = ([prevh] if prevh else []) + [f'h{j}', f'{nm}_{j} s {args}']
            out.append('  · exact ' + wrap(f'Or.inl ⟨{", ".join(body)}⟩', j))
        else:
            args = 'hs' + (f' {prevh}' if prevh else '') + ' hcap'
            body = ([prevh] if prevh else []) + ['hcap', f'{nm}_{j} s {args}']
            out.append('  exact ' + wrap(f'⟨{", ".join(body)}⟩', j))
    return out


def emit(name, lam, n, big, small, U, cap=None, doc=''):
    """big/small: lists of (lo, hi, line).  cap: optional rational bound on every s_i^2 (else 1)."""
    lam = Fr(lam); out = []
    for j, (lo, hi, L) in enumerate(big): out += line_lemma(f'{name}B_{j}', lam, lo, hi, L) + ['']
    for j, (lo, hi, L) in enumerate(small): out += line_lemma(f'{name}S_{j}', lam, lo, hi, L) + ['']
    out += cases_lemma(f'{name}B', lam, [(a, b) for a, b, _ in big], [L for _, _, L in big]) + ['']
    out += cases_lemma(f'{name}S', lam, [(a, b) for a, b, _ in small], [L for _, _, L in small]) + ['']
    bl, bh, sh = big[0][0], big[-1][1], small[-1][1]
    g = lambda v: f'({v} ^ 3 + {q(lam)} * {v})'
    vs = [f's{i}' for i in range(n)]
    tot = ' + '.join(g(v) for v in vs)
    ssum = ' + '.join(f'{v} ^ 2' for v in vs)
    capc = f' (cap : ∀ t : ℝ, t = t → True)' if False else ''
    # core
    hyps = ' '.join(f'(h{i} : 0 ≤ s{i})' for i in range(n))
    ords = ' '.join(f'(o{i} : s{i} ≤ s0)' for i in range(1, n))
    capsh = (' ' + ' '.join(f'(c{i} : s{i} ^ 2 ≤ {q(cap)})' for i in range(n))) if cap is not None else ''
    out.append('set_option maxHeartbeats 0 in')
    out.append(f'theorem {name}_core ({" ".join(vs)} : ℝ) {hyps}\n    {ords}{capsh}\n    (hs : {ssum} = 1) :\n    {tot} ≤ {q(U)} := by')
    for i in range(1, n):
        out.append(f'  have q{i} : s{i} ^ 2 ≤ s0 ^ 2 := by nlinarith')
    out.append(f'  have b0 : {q(bl * bl)} ≤ s0 ^ 2 := by nlinarith')
    out.append(f'  have t0 : s0 ^ 2 ≤ {q(bh * bh)} := by nlinarith')
    for i in range(1, n):
        out.append(f'  have t{i} : s{i} ^ 2 ≤ {q(sh * sh)} := by nlinarith')
    kb, ks = len(big), len(small)
    def pat(i, ivals, last):
        pats = []
        for j, (lo, hi) in enumerate(ivals):
            names = ([f'a{i}_{j}'] if lo > 0 else []) + [f'b{i}_{j}', f'f{i}_{j}']
            pats.append('⟨' + ', '.join(names) + '⟩')
        return ' | '.join(pats)
    bivals = [(a, b) for a, b, _ in big]; sivals = [(a, b) for a, b, _ in small]
    out.append(f'  have F0 := {name}B_cases s0 h0 b0 t0')
    for i in range(1, n):
        out.append(f'  have F{i} := {name}S_cases s{i} h{i} t{i}')
    for i in range(n):
        out.append(f'  have e{i} := sq_nonneg s{i}')
    keep = ' '.join(['hs'] + [f'q{i}' for i in range(1, n)] + [f'e{i}' for i in range(n)] + [f'F{i}' for i in range(n)])
    out.append(f'  clear * - {keep}')
    for i in range(n):
        out.append(f'  generalize s{i} ^ 2 = Q{i} at *')
        out.append(f'  generalize s{i} ^ 3 = C{i} at *')
    lines = [f'rcases F0 with ' + pat(0, bivals, True)]
    for i in range(1, n):
        lines.append(f'rcases F{i} with ' + pat(i, sivals, True))
    out.append('  ' + ' <;>\n  '.join(lines) + ' <;>\n  linarith')
    out.append('')
    # general, by tournament
    hyps = ' '.join(f'(h{i} : 0 ≤ s{i})' for i in range(n))
    out.append('set_option maxHeartbeats 0 in')
    if doc: out.append(f'/-- {doc} -/')
    out.append(f'theorem {name} ({" ".join(vs)} : ℝ) {hyps}{capsh}\n    (hs : {ssum} = 1) :\n    {tot} ≤ {q(U)} := by')
    def tour(i, m, ind):
        p = ' ' * ind
        if i == n:
            perm = [m] + [j for j in range(n) if j != m]
            args = ' '.join(f's{j}' for j in perm) + ' ' + ' '.join(f'h{j}' for j in perm)
            args += ' ' + ' '.join('(by linarith)' for _ in range(n - 1))
            if cap is not None: args += ' ' + ' '.join(f'c{j}' for j in perm)
            args += ' (by linarith)'
            return [p + f'have := {name}_core {args}', p + 'linarith']
        res = [p + f'rcases le_total s{i} s{m} with w{i} | w{i}']
        a = tour(i + 1, m, ind + 2); a[0] = p + '· ' + a[0].lstrip()
        b = tour(i + 1, i, ind + 2); b[0] = p + '· ' + b[0].lstrip()
        return res + a + b
    out += tour(1, 0, 2)
    out.append('')
    return '\n'.join(out)


if __name__ == '__main__':
    import pickle
    pkl, name, lam, n, U = sys.argv[1], sys.argv[2], Fr(sys.argv[3]), int(sys.argv[4]), Fr(sys.argv[5])
    cap = Fr(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6] != '-' else None
    w, (bb, sb, bt, st, arg, big, small) = pickle.load(open(pkl, 'rb'))
    print(f'-- LP bound {float(w)} <= U = {float(U)}', file=sys.stderr)
    assert w <= U - 1e-7
    print(emit(name, lam, n, big, small, U, cap))
