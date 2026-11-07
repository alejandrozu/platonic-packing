# emit far5_core, pair5 and far5 (fin_cases over the column)
n=5
L=[]
L.append('''/-! ## Away from the axes: every `c² ≤ 9/20` -/

/-- For two columns `a ⊥ b` with `‖b‖ = 1`: `(140/99) Σᵢ |aᵢ| bᵢ² ≤ Σᵢ |aᵢ| |bᵢ|` (`zs_bound` with `zᵢ = aᵢbᵢ`,
`vᵢ = bᵢ`). -/
theorem pair5 (a0 a1 a2 a3 a4 b0 b1 b2 b3 b4 : ℝ) (hab : a0 * b0 + a1 * b1 + a2 * b2 + a3 * b3 + a4 * b4 = 0)
    (hb : b0 ^ 2 + b1 ^ 2 + b2 ^ 2 + b3 ^ 2 + b4 ^ 2 = 1) :
    140 / 99 * (|a0| * b0 ^ 2 + |a1| * b1 ^ 2 + |a2| * b2 ^ 2 + |a3| * b3 ^ 2 + |a4| * b4 ^ 2) ≤
      |a0| * |b0| + |a1| * |b1| + |a2| * |b2| + |a3| * |b3| + |a4| * |b4| := by
  have h := zs_bound (a0 * b0) (a1 * b1) (a2 * b2) (a3 * b3) (a4 * b4) b0 b1 b2 b3 b4 1 zero_le_one hab
    (by rw [one_pow]; linarith)
  have e : ∀ x y : ℝ, |x * y| * |y| = |x| * y ^ 2 := fun x y => by
    rw [abs_mul, mul_assoc, abs_mul_abs_self, sq]
  rw [e, e, e, e, e] at h
  simp only [abs_mul, one_mul] at h
  linarith
''')
cols='abcde'
args=' '.join(f'{c}{i}' for c in cols for i in range(n))
L.append('set_option maxHeartbeats 2000000 in')
L.append('/-- **Away from the axes.** If every entry of the column `a` has square at most `9/20`, then `F ≤ 1`. -/')
L.append(f'theorem far5_core ({args} : ℝ)')
for c in cols:
    L.append(f'    (h{c} : ' + ' + '.join(f'{c}{i} ^ 2' for i in range(n)) + ' = 1)')
for c in cols[1:]:
    L.append(f'    (ha{c} : ' + ' + '.join(f'a{i} * {c}{i}' for i in range(n)) + ' = 0)')
for i in range(n):
    L.append(f'    (r{i} : ' + ' + '.join(f'{c}{i} ^ 2' for c in cols) + ' = 1)')
L.append('    ' + ' '.join(f'(f{i} : a{i} ^ 2 ≤ 9 / 20)' for i in range(n)) + ' :')
L.append('    ' + ' +\n      '.join(f'|a{i}| * (2 - (' + ' + '.join(f'|{c}{i}|' for c in cols) + '))' for i in range(n)) + ' ≤ 1 := by')
for c in cols[1:]:
    L.append(f'  have p{c} := pair5 ' + ' '.join(f'a{i}' for i in range(n)) + ' ' + ' '.join(f'{c}{i}' for i in range(n)) + f' ha{c} h{c}')
L.append('  have hp := cs5 ' + ' '.join(f'|a{i}|' for i in range(n)) + ' ' + ' '.join('(abs_nonneg _)' for i in range(n)) + ' ' +
         ' '.join(f'(by rw [sq_abs]; exact f{i})' for i in range(n)) + ' (by simp only [sq_abs]; exact ha)')
L.append('''  have w : ∀ (x b c d e : ℝ), x ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 + e ^ 2 = 1 →
      |x| * b ^ 2 + |x| * c ^ 2 + |x| * d ^ 2 + |x| * e ^ 2 = |x| - |x| ^ 3 := fun x b c d e h => by
    have : |x| ^ 3 = |x| * x ^ 2 := by rw [pow_succ, sq_abs, mul_comm]
    rw [this]; linear_combination |x| * h''')
for i in range(n):
    L.append(f'  have w{i} := w a{i} b{i} c{i} d{i} e{i} r{i}')
for i in range(n):
    L.append(f'  have s{i} : |a{i}| * |a{i}| = a{i} ^ 2 := by rw [abs_mul_abs_self, sq]')
L.append('  linarith')
L.append('')
# far5 for a matrix
L.append('''theorem far5 (R : Matrix (Fin 5) (Fin 5) ℝ) (hR : R * Rᵀ = 1) (j : Fin 5) (hf : ∀ i, R i j ^ 2 ≤ 9 / 20) :
    Fcol R j ≤ 1 := by
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have row : ∀ i, R i 0 ^ 2 + R i 1 ^ 2 + R i 2 ^ 2 + R i 3 ^ 2 + R i 4 ^ 2 = 1 := fun i => by
    have h := congrFun (congrFun hR i) i
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_five, Matrix.one_apply_eq] at h
    linear_combination h
  have col : ∀ a b, R 0 a * R 0 b + R 1 a * R 1 b + R 2 a * R 2 b + R 3 a * R 3 b + R 4 a * R 4 b =
      if a = b then 1 else 0 := fun a b => by
    have h := congrFun (congrFun hR' a) b
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_five, Matrix.one_apply] at h
    exact h''')
for a in range(n):
    for b in range(a,n):
        L.append(f'  have c{a}{b} := col {a} {b}')
L.append('  simp only [Fin.reduceEq, ↓reduceIte] at ' + ' '.join(f'c{a}{b}' for a in range(n) for b in range(a,n)))
for i in range(n): L.append(f'  have r{i} := row {i}')
for i in range(n): L.append(f'  have hf{i} := hf {i}')
L.append('  simp only [Fcol, rowL1, l1, Fin.sum_univ_five]')
L.append('  fin_cases j')
def cc(a,b):  # name of col a b with a<=b, expression orientation
    return f'c{min(a,b)}{max(a,b)}'
for j in range(n):
    others=[k for k in range(n) if k!=j]
    order=[j]+others
    argv=' '.join(f'(R {i} {k})' for k in order for i in range(n))
    hs=' '.join(f'(by linear_combination {cc(k,k)})' for k in order)
    perp=' '.join(f'(by linear_combination {cc(j,k)})' for k in others)
    rows=' '.join(f'(by linear_combination r{i})' for i in range(n))
    hf=' '.join(f'hf{i}' for i in range(n))
    L.append(f'  · have := far5_core {argv}\n      {hs}\n      {perp}\n      {rows}\n      {hf}')
    L.append('    try simp only [Fin.zero_eta, Fin.mk_one, Fin.reduceFinMk, Fin.isValue]')
    L.append('    linarith')
L.append('')
open('far5.lean','w').write('\n'.join(L))
