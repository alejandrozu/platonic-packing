import PackingOptimality.PivotStep
import PackingOptimality.LemmaF5

/-!
# The facet step: Lemma F in every dimension from the facet lemma

Fix a column `j` of an orthogonal matrix `R` and put `x = |column j|`. The **value** of column `j` is
`V_j(R) = Σᵢ xᵢ (‖row i‖₁ − xᵢ)`, and `F_j(R) = 2 ‖x‖₁ − 1 − V_j(R)` (`Fcol_eq_colValue`). So Lemma F for column
`j` is a lower bound for `V_j`, and `V_j` depends only on the other columns, which form an orthonormal basis (a
*frame*) of `x^⊥` once the signs of the rows are normalised.

A row `p` is **aligned** if it has at most one nonzero entry outside column `j`. Geometrically, the unit cube
whose edge frame is given by the other columns then has a facet parallel to a facet of the simplex
`{ξ > 0, ⟨x, ξ⟩ = λ}`.

* `aligned_step`, `aligned_at`: **if row `p` is aligned, then Lemma F in dimension `m` gives `F_j(R) ≤ 1` in
  dimension `m + 1`**, in fact `F_j(R) ≤ 1 − 2(1 − |R p j|)(1 − |R p q|)`. The proof is an identity: the pivot
  `c = R p q` turns the minor into the polar factor `Q` with `M · j = c Q · j` and `x = −ν Q · j`.
* `FacetLemma d`: every frame can be replaced by one with an aligned row and no larger value.
* `lemmaF_succ_of_facet`, `lemmaF_of_facet_from`, `lemmaF_of_facet`: **the facet lemma in dimensions `6, …, d`
  gives Lemma F in dimension `d`**, starting from Lemma F in dimension 5 (`LemmaF5.lemmaF5`).
* `cube_plateau_of_facet`: the facet lemma in every dimension `≥ 6` gives `s_d(n) = 2` for all `2 ≤ n ≤ 2^d`
  in **every** dimension `d`; `lemmaF_all_of_facet` gives Lemma F in every dimension (`lemmaF_le_four` for `d ≤ 4`).
* Restricted versions: `aligned_step_r`, `aligned_at_r` (the polar factor's rows are no longer than those of `R`,
  so restricted Lemma F in dimension `m` suffices), `FacetLemmaR`, `lemmaFr_succ_of_facetR`, `lemmaFr_of_facetR`,
  `cube_plateau_of_facetR`: the restricted facet lemma in every dimension `≥ 6` also gives `s_d(n) = 2`.

The facet lemma itself is open for `d ≥ 4` (Paper IV). It holds in `d = 2` trivially and in `d = 3` by a
concavity argument on paper; numerically it holds in all tested dimensions.
-/

namespace PackingOptimality.Restricted

open NearAxis Matrix
open scoped Pointwise

variable {m : ℕ}

lemma l1_single {r : Fin m → ℝ} {j : Fin m} (hr : ∀ k, k ≠ j → r k = 0) : l1 r = |r j| := by
  unfold l1
  rw [Finset.sum_eq_single j (fun k _ hk => by rw [hr k hk, abs_zero])
    (fun h => absurd (Finset.mem_univ j) h)]

lemma sq2_single {r : Fin m → ℝ} {j : Fin m} (hr : ∀ k, k ≠ j → r k = 0) : sq2 r = r j ^ 2 := by
  unfold sq2
  rw [Finset.sum_eq_single j (fun k _ hk => by rw [hr k hk]; ring)
    (fun h => absurd (Finset.mem_univ j) h)]

/-- **The aligned step** (block form). `R = [c r; x M]` is orthogonal with `c > 0`, and the rest `r` of the pivot
row is supported on the single entry `j`. Then Lemma F in dimension `m` gives `F_j(R) ≤ 1`. -/
theorem aligned_step (hF : LemmaF m) {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (j : Fin m) (hr : ∀ k, k ≠ j → r k = 0) :
    Gcol c r x M j ≤ 1 - 2 * (1 - |r j|) * (1 - c) := by
  have hc1 := block_c_le_one h hc
  have hl1 : l1 r = |r j| := l1_single hr
  have hsq : sq2 r = r j ^ 2 := sq2_single hr
  rcases (sq2_nonneg x).eq_or_lt with hx | hx
  · -- `x = 0`: then `c = 1`, `r = 0`, and `M` itself is orthogonal
    have hx0 : sq2 x = 0 := hx.symm
    have hcc : c = 1 := by nlinarith [h.col1]
    have hrj : r j = 0 := by
      have := h.row1
      rw [hcc, hsq] at this
      nlinarith
    have hxv := eq_zero_of_sq2_eq_zero hx0
    have hM : M * Mᵀ = 1 := by
      have := block_mul_transpose h
      rw [hxv] at this
      simpa using this
    have := hF M hM j
    simp only [Gcol, Fcol, hxv, hrj, hcc, Pi.zero_apply, abs_zero, abs_one, sub_zero, zero_mul, zero_add,
      sub_self, mul_zero, mul_one] at this ⊢
    linarith
  · set Q := polarQ c x M with hQdef
    have hQ : Q * Qᵀ = 1 := polarQ_orth h hc hx
    have hQ' : Qᵀ * Q = 1 := mul_eq_one_comm.mp hQ
    set ν := r j with hν
    have hν2 : c ^ 2 + ν ^ 2 = 1 := by have := h.row1; rw [hsq] at this; linarith
    have hxν : sq2 x = ν ^ 2 := by have := h.col1; linarith
    have hν0 : ν ^ 2 ≠ 0 := by rw [← hxν]; exact ne_of_gt hx
    -- `x = −ν Q·j`: `Qᵀ x = −r` and `r` is supported on `j`
    have hxQ : ∀ i, x i = -ν * Q i j := by
      intro i
      have e : x = Q *ᵥ (Qᵀ *ᵥ x) := by rw [Matrix.mulVec_mulVec, hQ, Matrix.one_mulVec]
      have hi := congrFun e i
      rw [polarQ_transpose_x h hc hx] at hi
      rw [hi]
      simp only [Matrix.mulVec, dotProduct, Pi.neg_apply]
      rw [Finset.sum_eq_single j (fun k _ hk => by rw [hr k hk]; ring)
        (fun h => absurd (Finset.mem_univ j) h)]
      ring
    -- `M·j = c Q·j`, and the other columns of `M` and `Q` agree
    have ha : (1 - c) / sq2 x * ν ^ 2 = 1 - c := by rw [hxν]; exact div_mul_cancel₀ (1 - c) hν0
    have hMj : ∀ i, M i j = c * Q i j := by
      intro i
      have e := polarQ_entry h hc i j
      rw [← hQdef, hxQ i] at e
      have e2 : M i j = Q i j * (1 - (1 - c) / sq2 x * ν ^ 2) := by
        linear_combination (-1 : ℝ) * e
      rw [e2, ha]
      ring
    have hMk : ∀ i k, k ≠ j → M i k = Q i k := by
      intro i k hk
      have e := polarQ_entry h hc i k
      rw [← hQdef, hr k hk] at e
      linarith
    have hrowM : ∀ i, rowL1 M i = rowL1 Q i - |Q i j| + c * |Q i j| := by
      intro i
      unfold rowL1 l1
      rw [← Finset.add_sum_erase _ _ (Finset.mem_univ j), ← Finset.add_sum_erase _ _ (Finset.mem_univ j)]
      have hs : ∑ k ∈ Finset.univ.erase j, |M i k| = ∑ k ∈ Finset.univ.erase j, |Q i k| :=
        Finset.sum_congr rfl fun k hk => by rw [hMk i k (Finset.ne_of_mem_erase hk)]
      rw [hs, hMj i, abs_mul, abs_of_pos hc]
      ring
    have hcol : ∑ i, Q i j ^ 2 = 1 := by
      have := congrFun (congrFun hQ' j) j
      simpa [Matrix.mul_apply, pow_two] using this
    have hFQ := hF Q hQ j
    unfold Fcol at hFQ
    have hterm : ∀ i, |M i j| * (2 - |x i| - rowL1 M i) =
        c * (|Q i j| * (2 - rowL1 Q i)) + c * (1 - c - |ν|) * Q i j ^ 2 := by
      intro i
      rw [hrowM i, hMj i, hxQ i, abs_mul, abs_mul, abs_of_pos hc, abs_neg, ← sq_abs (Q i j)]
      ring
    unfold Gcol
    rw [Finset.sum_congr rfl (fun i _ => hterm i), Finset.sum_add_distrib, ← Finset.mul_sum,
      ← Finset.mul_sum, hcol, abs_of_pos hc, hl1]
    have hν1 : |ν| ≤ 1 := by nlinarith [sq_abs ν, abs_nonneg ν]
    have hcF := mul_le_mul_of_nonneg_left hFQ hc.le
    nlinarith [sq_abs ν]

/-- **The aligned step for the restricted lemma** (block form). As `aligned_step`, but with the rows of `R` of ℓ¹
norm at most 2 and restricted Lemma F in dimension `m`. The rows of the polar factor are no longer than the rows of
`R`: `‖Q_i‖₁ = ‖R_i‖₁ − (|ν| + c − 1)|Q_ij|` and `|ν| + c ≥ 1`. -/
theorem aligned_step_r (hF : LemmaFr m) {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (j : Fin m) (hr : ∀ k, k ≠ j → r k = 0)
    (hrows : ∀ i, |x i| + rowL1 M i ≤ 2) :
    Gcol c r x M j ≤ 1 - 2 * (1 - |r j|) * (1 - c) := by
  have hc1 := block_c_le_one h hc
  have hl1 : l1 r = |r j| := l1_single hr
  have hsq : sq2 r = r j ^ 2 := sq2_single hr
  rcases (sq2_nonneg x).eq_or_lt with hx | hx
  · -- `x = 0`: then `c = 1`, `r = 0`, and `M` itself is orthogonal
    have hx0 : sq2 x = 0 := hx.symm
    have hcc : c = 1 := by nlinarith [h.col1]
    have hrj : r j = 0 := by
      have := h.row1
      rw [hcc, hsq] at this
      nlinarith
    have hxv := eq_zero_of_sq2_eq_zero hx0
    have hM : M * Mᵀ = 1 := by
      have := block_mul_transpose h
      rw [hxv] at this
      simpa using this
    have hMr : ∀ i, rowL1 M i ≤ 2 := fun i => by
      have := hrows i; rw [hxv] at this; simpa using this
    have := hF M hM hMr j
    simp only [Gcol, Fcol, hxv, hrj, hcc, Pi.zero_apply, abs_zero, abs_one, sub_zero, zero_mul, zero_add,
      sub_self, mul_zero, mul_one] at this ⊢
    linarith
  · set Q := polarQ c x M with hQdef
    have hQ : Q * Qᵀ = 1 := polarQ_orth h hc hx
    have hQ' : Qᵀ * Q = 1 := mul_eq_one_comm.mp hQ
    set ν := r j with hν
    have hν2 : c ^ 2 + ν ^ 2 = 1 := by have := h.row1; rw [hsq] at this; linarith
    have hxν : sq2 x = ν ^ 2 := by have := h.col1; linarith
    have hν0 : ν ^ 2 ≠ 0 := by rw [← hxν]; exact ne_of_gt hx
    -- `x = −ν Q·j`: `Qᵀ x = −r` and `r` is supported on `j`
    have hxQ : ∀ i, x i = -ν * Q i j := by
      intro i
      have e : x = Q *ᵥ (Qᵀ *ᵥ x) := by rw [Matrix.mulVec_mulVec, hQ, Matrix.one_mulVec]
      have hi := congrFun e i
      rw [polarQ_transpose_x h hc hx] at hi
      rw [hi]
      simp only [Matrix.mulVec, dotProduct, Pi.neg_apply]
      rw [Finset.sum_eq_single j (fun k _ hk => by rw [hr k hk]; ring)
        (fun h => absurd (Finset.mem_univ j) h)]
      ring
    -- `M·j = c Q·j`, and the other columns of `M` and `Q` agree
    have ha : (1 - c) / sq2 x * ν ^ 2 = 1 - c := by rw [hxν]; exact div_mul_cancel₀ (1 - c) hν0
    have hMj : ∀ i, M i j = c * Q i j := by
      intro i
      have e := polarQ_entry h hc i j
      rw [← hQdef, hxQ i] at e
      have e2 : M i j = Q i j * (1 - (1 - c) / sq2 x * ν ^ 2) := by
        linear_combination (-1 : ℝ) * e
      rw [e2, ha]
      ring
    have hMk : ∀ i k, k ≠ j → M i k = Q i k := by
      intro i k hk
      have e := polarQ_entry h hc i k
      rw [← hQdef, hr k hk] at e
      linarith
    have hrowM : ∀ i, rowL1 M i = rowL1 Q i - |Q i j| + c * |Q i j| := by
      intro i
      unfold rowL1 l1
      rw [← Finset.add_sum_erase _ _ (Finset.mem_univ j), ← Finset.add_sum_erase _ _ (Finset.mem_univ j)]
      have hs : ∑ k ∈ Finset.univ.erase j, |M i k| = ∑ k ∈ Finset.univ.erase j, |Q i k| :=
        Finset.sum_congr rfl fun k hk => by rw [hMk i k (Finset.ne_of_mem_erase hk)]
      rw [hs, hMj i, abs_mul, abs_of_pos hc]
      ring
    have hcol : ∑ i, Q i j ^ 2 = 1 := by
      have := congrFun (congrFun hQ' j) j
      simpa [Matrix.mul_apply, pow_two] using this
    have hνc : 1 ≤ |ν| + c := by nlinarith [sq_abs ν, abs_nonneg ν]
    have hQr : ∀ i, rowL1 Q i ≤ 2 := fun i => by
      have h1 := hrows i
      rw [hrowM i, hxQ i, abs_mul, abs_neg] at h1
      nlinarith [abs_nonneg (Q i j)]
    have hFQ := hF Q hQ hQr j
    unfold Fcol at hFQ
    have hterm : ∀ i, |M i j| * (2 - |x i| - rowL1 M i) =
        c * (|Q i j| * (2 - rowL1 Q i)) + c * (1 - c - |ν|) * Q i j ^ 2 := by
      intro i
      rw [hrowM i, hMj i, hxQ i, abs_mul, abs_mul, abs_of_pos hc, abs_neg, ← sq_abs (Q i j)]
      ring
    unfold Gcol
    rw [Finset.sum_congr rfl (fun i _ => hterm i), Finset.sum_add_distrib, ← Finset.mul_sum,
      ← Finset.mul_sum, hcol, abs_of_pos hc, hl1]
    have hν1 : |ν| ≤ 1 := by nlinarith [sq_abs ν, abs_nonneg ν]
    have hcF := mul_le_mul_of_nonneg_left hFQ hc.le
    nlinarith [sq_abs ν]

/-- A row `p` that is `±e_j`: then `F_j(R) = 1`. -/
theorem Fcol_le_one_of_axis_row {m : ℕ} (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (p j : Fin (m + 1)) (hrow : ∀ k, k ≠ j → R p k = 0) : Fcol R j ≤ 1 := by
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have hB := LemmaF4.block_orth R hR hR' p j
  have hr0 : ∀ k, R p (j.succAbove k) = 0 := fun k => hrow _ (Fin.succAbove_ne j k)
  have hsq : sq2 (fun k => R p (j.succAbove k)) = 0 := by simp [sq2, hr0]
  have hc2 : R p j ^ 2 = 1 := by have := hB.row1; linarith
  have hx0 : sq2 (fun i => R (p.succAbove i) j) = 0 := by have := hB.col1; linarith
  have hxv : ∀ i, R (p.succAbove i) j = 0 := fun i => congrFun (eq_zero_of_sq2_eq_zero hx0) i
  have hc1 : |R p j| = 1 := by nlinarith [sq_abs (R p j), abs_nonneg (R p j)]
  rw [LemmaF4.Fcol_eq_F1 R p j]
  simp [F1, l1, hr0, hxv, hc1]
  norm_num

/-- **The aligned step for matrices.** If row `p` of the orthogonal matrix `R` has no nonzero entry outside the
columns `j` and `q ≠ j`, then Lemma F in dimension `m` gives `F_j(R) ≤ 1` in dimension `m + 1`. -/
theorem aligned_at (hF : LemmaF m) (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (p q j : Fin (m + 1)) (hqj : q ≠ j) (hsupp : ∀ k, k ≠ j → k ≠ q → R p k = 0) : Fcol R j ≤ 1 := by
  by_cases h0 : R p q = 0
  · refine Fcol_le_one_of_axis_row R hR p j fun k hk => ?_
    by_cases hkq : k = q
    · rw [hkq]; exact h0
    · exact hsupp k hk hkq
  obtain ⟨j', rfl⟩ := Fin.exists_succAbove_eq hqj.symm
  -- normalise the sign of the pivot by flipping column `q`
  set t : Fin (m + 1) → ℝ := fun k => if k = q then sgn1 (R p q) else 1 with ht_def
  set s : Fin (m + 1) → ℝ := fun _ => 1 with hs_def
  have hs1 : ∀ i, s i * s i = 1 := fun i => by simp [hs_def]
  have hsa : ∀ i, |s i| = 1 := fun i => by simp [hs_def]
  have ht1 : ∀ k, t k * t k = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_sq]
  have hta : ∀ k, |t k| = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_abs]
  set R' := flipM R s t with hR'_def
  have hR'o : R' * R'ᵀ = 1 := flipM_orth hs1 ht1 hR
  have hR'' : R'ᵀ * R' = 1 := mul_eq_one_comm.mp hR'o
  rw [← flipM_Fcol hsa hta (q.succAbove j'), ← hR'_def, Fcol_eq_Gcol R' p q j']
  have hpq : R' p q = |R p q| := by
    simp [hR'_def, flipM, ht_def, hs_def]; rw [mul_comm]; exact sgn1_mul _
  have hc : 0 < R' p q := by rw [hpq]; exact abs_pos.mpr h0
  have hB := LemmaF4.block_orth R' hR'o hR'' p q
  have hsupp' : ∀ k, k ≠ j' → R' p (q.succAbove k) = 0 := by
    intro k hk
    have h1 : q.succAbove k ≠ q.succAbove j' := fun e => hk (Fin.succAbove_right_injective e)
    have h2 : q.succAbove k ≠ q := Fin.succAbove_ne q k
    simp [hR'_def, flipM, hsupp _ h1 h2]
  have key := aligned_step hF hB hc j' hsupp'
  have hrj : |R' p (q.succAbove j')| ≤ 1 := by
    have := hB.row1
    have hsq := sq2_single (r := fun k => R' p (q.succAbove k)) hsupp'
    rw [hsq] at this
    nlinarith [sq_abs (R' p (q.succAbove j')), abs_nonneg (R' p (q.succAbove j'))]
  have hc1 := block_c_le_one hB hc
  have : 0 ≤ 2 * (1 - |R' p (q.succAbove j')|) * (1 - R' p q) :=
    mul_nonneg (mul_nonneg (by norm_num) (by linarith)) (by linarith)
  linarith

/-- **The aligned step for matrices, restricted version.** Rows of `R` of ℓ¹ norm at most 2, row `p` supported on
the columns `j` and `q ≠ j`: restricted Lemma F in dimension `m` gives `F_j(R) ≤ 1`. -/
theorem aligned_at_r (hF : LemmaFr m) (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (hw : ∀ i, rowL1 R i ≤ 2) (p q j : Fin (m + 1)) (hqj : q ≠ j)
    (hsupp : ∀ k, k ≠ j → k ≠ q → R p k = 0) : Fcol R j ≤ 1 := by
  by_cases h0 : R p q = 0
  · refine Fcol_le_one_of_axis_row R hR p j fun k hk => ?_
    by_cases hkq : k = q
    · rw [hkq]; exact h0
    · exact hsupp k hk hkq
  obtain ⟨j', rfl⟩ := Fin.exists_succAbove_eq hqj.symm
  set t : Fin (m + 1) → ℝ := fun k => if k = q then sgn1 (R p q) else 1 with ht_def
  set s : Fin (m + 1) → ℝ := fun _ => 1 with hs_def
  have hs1 : ∀ i, s i * s i = 1 := fun i => by simp [hs_def]
  have hsa : ∀ i, |s i| = 1 := fun i => by simp [hs_def]
  have ht1 : ∀ k, t k * t k = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_sq]
  have hta : ∀ k, |t k| = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_abs]
  set R' := flipM R s t with hR'_def
  have hR'o : R' * R'ᵀ = 1 := flipM_orth hs1 ht1 hR
  have hR'' : R'ᵀ * R' = 1 := mul_eq_one_comm.mp hR'o
  have hw' : ∀ i, rowL1 R' i ≤ 2 := fun i => by rw [hR'_def, flipM_rowL1 hsa hta]; exact hw i
  rw [← flipM_Fcol hsa hta (q.succAbove j'), ← hR'_def, Fcol_eq_Gcol R' p q j']
  have hpq : R' p q = |R p q| := by
    simp [hR'_def, flipM, ht_def, hs_def]; rw [mul_comm]; exact sgn1_mul _
  have hc : 0 < R' p q := by rw [hpq]; exact abs_pos.mpr h0
  have hB := LemmaF4.block_orth R' hR'o hR'' p q
  have hsupp' : ∀ k, k ≠ j' → R' p (q.succAbove k) = 0 := by
    intro k hk
    have h1 : q.succAbove k ≠ q.succAbove j' := fun e => hk (Fin.succAbove_right_injective e)
    have h2 : q.succAbove k ≠ q := Fin.succAbove_ne q k
    simp [hR'_def, flipM, hsupp _ h1 h2]
  have hrows : ∀ i, |R' (p.succAbove i) q| + rowL1 (fun i k => R' (p.succAbove i) (q.succAbove k)) i ≤ 2 := by
    intro i
    have h1 := LemmaF4.rowL1_split R' (p.succAbove i) q
    have h2 := hw' (p.succAbove i)
    simp only [rowL1, l1] at h1 h2 ⊢
    linarith
  have key := aligned_step_r hF hB hc j' hsupp' hrows
  have hrj : |R' p (q.succAbove j')| ≤ 1 := by
    have := hB.row1
    have hsq := sq2_single (r := fun k => R' p (q.succAbove k)) hsupp'
    rw [hsq] at this
    nlinarith [sq_abs (R' p (q.succAbove j')), abs_nonneg (R' p (q.succAbove j'))]
  have hc1 := block_c_le_one hB hc
  have : 0 ≤ 2 * (1 - |R' p (q.succAbove j')|) * (1 - R' p q) :=
    mul_nonneg (mul_nonneg (by norm_num) (by linarith)) (by linarith)
  linarith

/-- The **value** of column `j`: `V_j(R) = Σᵢ |Rᵢⱼ| (‖row i‖₁ − |Rᵢⱼ|)`. -/
noncomputable def colValue {d : ℕ} (R : Matrix (Fin d) (Fin d) ℝ) (j : Fin d) : ℝ :=
  ∑ i, |R i j| * (rowL1 R i - |R i j|)

/-- `F_j(R) = 2 ‖column j‖₁ − 1 − V_j(R)` for orthogonal `R`. -/
theorem Fcol_eq_colValue {d : ℕ} (R : Matrix (Fin d) (Fin d) ℝ) (hR : R * Rᵀ = 1) (j : Fin d) :
    Fcol R j = 2 * (∑ i, |R i j|) - 1 - colValue R j := by
  have hc := col_sq R hR j
  have e : ∀ i, |R i j| * (2 - rowL1 R i) =
      2 * |R i j| - |R i j| * (rowL1 R i - |R i j|) - R i j ^ 2 := fun i => by
    rw [← sq_abs (R i j)]; ring
  unfold Fcol colValue
  rw [Finset.sum_congr rfl (fun i _ => e i), Finset.sum_sub_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, hc]
  ring

/-- **The facet lemma in dimension `d`**: for every orthogonal `R` and column `j` there is an orthogonal `R'` with
the same column `j` up to signs, no larger value `V_j`, and an aligned row (a row with no nonzero entry outside
column `j` and one further column `q`). Equivalently: among the largest cubes in the simplex
`{ξ > 0, ⟨|column j|, ξ⟩ = λ}` there is one with a facet parallel to a facet of the simplex. -/
def FacetLemma (d : ℕ) : Prop :=
  ∀ R : Matrix (Fin d) (Fin d) ℝ, R * Rᵀ = 1 → ∀ j, ∃ R' : Matrix (Fin d) (Fin d) ℝ, R' * R'ᵀ = 1 ∧
    (∀ i, |R' i j| = |R i j|) ∧ colValue R' j ≤ colValue R j ∧
    ∃ p q, q ≠ j ∧ ∀ k, k ≠ j → k ≠ q → R' p k = 0

/-- The facet lemma is trivial in dimension 2: every row is aligned. -/
theorem facetLemma_two : FacetLemma 2 := by
  intro R hR j
  refine ⟨R, hR, fun i => rfl, le_rfl, 0, if j = 0 then 1 else 0, ?_, ?_⟩
  · fin_cases j <;> simp
  · intro k hk hkq
    fin_cases j <;> fin_cases k <;> simp_all

/-- **The induction step.** Lemma F in dimension `m` and the facet lemma in dimension `m + 1` give Lemma F in
dimension `m + 1`. -/
theorem lemmaF_succ_of_facet (hF : LemmaF m) (hfac : FacetLemma (m + 1)) : LemmaF (m + 1) := by
  intro R hR j
  obtain ⟨R', hR', habs, hval, p, q, hqj, hsupp⟩ := hfac R hR j
  have h1 := aligned_at hF R' hR' p q j hqj hsupp
  rw [Fcol_eq_colValue R' hR' j] at h1
  rw [Fcol_eq_colValue R hR j]
  have : ∑ i, |R' i j| = ∑ i, |R i j| := Finset.sum_congr rfl fun i _ => habs i
  linarith

/-- The facet lemma in dimensions `k + 1, …, d` lifts Lemma F from dimension `k` to dimension `d`. -/
theorem lemmaF_of_facet_from {k : ℕ} (hk : LemmaF k) (hfac : ∀ d, k < d → FacetLemma d) :
    ∀ d, k ≤ d → LemmaF d := by
  intro d hd
  induction d, hd using Nat.le_induction with
  | base => exact hk
  | succ n hn ih => exact lemmaF_succ_of_facet ih (hfac (n + 1) (by omega))

/-- **Lemma F in every dimension `d ≥ 5` from the facet lemma in dimensions `6, …, d`.** -/
theorem lemmaF_of_facet (hfac : ∀ d, 5 < d → FacetLemma d) (d : ℕ) (hd : 5 ≤ d) : LemmaF d :=
  lemmaF_of_facet_from LemmaF5.lemmaF5 hfac d hd

/-- **The cube centre lemma in every dimension from the facet lemma** (dimensions `≤ 4` need nothing:
`centre_le_four`; dimension 5 is `LemmaF5.lemmaF5`). -/
theorem centre_of_facet (hfac : ∀ d, 5 < d → FacetLemma d) {d : ℕ} (s : ℝ) (hs0 : 0 ≤ s) (hs : s < 2)
    (g : EuclideanSpace ℝ (Fin d) ≃ᵃⁱ[ℝ] EuclideanSpace ℝ (Fin d)) (hg : g '' cube d ⊆ s • cube d) :
    (s / 2) • WithLp.toLp 2 (fun _ => (1 : ℝ)) ∈ interior (g '' cube d) := by
  rcases le_or_gt d 4 with h4 | h5
  · exact centre_le_four h4 s hs0 hs g hg
  · exact CentreGeneral.centre_of_lemmaF (lemmaF_of_facet hfac d (by omega)) s hs0 hs g hg

/-- **`s_d(n) = 2` for every `2 ≤ n ≤ 2^d` in every dimension, from the facet lemma in dimensions `≥ 6`.** -/
theorem cube_plateau_of_facet (hfac : ∀ d, 5 < d → FacetLemma d) {d : ℕ} (hd : d ≠ 0) {n : ℕ}
    (hn2 : 2 ≤ n) (hn : n ≤ 2 ^ d) :
    Nonempty (Packing (cube d) (cube d) 2 n) ∧ ∀ s : ℝ, 0 ≤ s → Packing (cube d) (cube d) s n → 2 ≤ s :=
  cube_plateau_of_centre_lemma hd (fun s hs0 hs g hg => centre_of_facet hfac s hs0 hs g hg) hn2 hn

/-- **The restricted facet lemma in dimension `d`**: as `FacetLemma`, for matrices whose rows have ℓ¹ norm at most
2, with `R'` of the same kind. -/
def FacetLemmaR (d : ℕ) : Prop :=
  ∀ R : Matrix (Fin d) (Fin d) ℝ, R * Rᵀ = 1 → (∀ i, rowL1 R i ≤ 2) → ∀ j, ∃ R' : Matrix (Fin d) (Fin d) ℝ,
    R' * R'ᵀ = 1 ∧ (∀ i, rowL1 R' i ≤ 2) ∧ (∀ i, |R' i j| = |R i j|) ∧ colValue R' j ≤ colValue R j ∧
    ∃ p q, q ≠ j ∧ ∀ k, k ≠ j → k ≠ q → R' p k = 0

/-- Restricted Lemma F in dimension `m` and the restricted facet lemma in dimension `m + 1` give restricted Lemma F
in dimension `m + 1`. -/
theorem lemmaFr_succ_of_facetR (hF : LemmaFr m) (hfac : FacetLemmaR (m + 1)) : LemmaFr (m + 1) := by
  intro R hR hw j
  obtain ⟨R', hR', hw', habs, hval, p, q, hqj, hsupp⟩ := hfac R hR hw j
  have h1 := aligned_at_r hF R' hR' hw' p q j hqj hsupp
  rw [Fcol_eq_colValue R' hR' j] at h1
  rw [Fcol_eq_colValue R hR j]
  have : ∑ i, |R' i j| = ∑ i, |R i j| := Finset.sum_congr rfl fun i _ => habs i
  linarith

/-- **Restricted Lemma F in every dimension `d ≥ 5` from the restricted facet lemma in dimensions `6, …, d`.** -/
theorem lemmaFr_of_facetR (hfac : ∀ d, 5 < d → FacetLemmaR d) (d : ℕ) (hd : 5 ≤ d) : LemmaFr d := by
  induction d, hd using Nat.le_induction with
  | base => exact lemmaFr_five
  | succ n hn ih => exact lemmaFr_succ_of_facetR ih (hfac (n + 1) (by omega))

/-- **`s_d(n) = 2` for every `2 ≤ n ≤ 2^d` in every dimension, from the restricted facet lemma in dimensions `≥ 6`.** -/
theorem cube_plateau_of_facetR (hfac : ∀ d, 5 < d → FacetLemmaR d) {d : ℕ} (hd : d ≠ 0) {n : ℕ}
    (hn2 : 2 ≤ n) (hn : n ≤ 2 ^ d) :
    Nonempty (Packing (cube d) (cube d) 2 n) ∧ ∀ s : ℝ, 0 ≤ s → Packing (cube d) (cube d) s n → 2 ≤ s := by
  refine cube_plateau_of_centre_lemma hd (fun s hs0 hs g hg => ?_) hn2 hn
  rcases le_or_gt d 4 with h4 | h5
  · exact centre_le_four h4 s hs0 hs g hg
  · exact CentreGeneral.centre_of_lemmaF_rows (lemmaFr_of_facetR hfac d (by omega)) s hs0 hs g hg

/-- **Lemma F for `d ≤ 4`** (unrestricted): rows of an orthogonal matrix of size at most 4 have ℓ¹ norm at most 2. -/
theorem lemmaF_le_four (d : ℕ) (hd : d ≤ 4) : LemmaF d :=
  fun Q hQ j => lemmaFr_le_four d hd Q hQ (fun i => rowL1_le_two hd hQ i) j

/-- **Lemma F in every dimension from the facet lemma in dimensions `≥ 6`.** -/
theorem lemmaF_all_of_facet (hfac : ∀ d, 5 < d → FacetLemma d) (d : ℕ) : LemmaF d := by
  rcases le_or_gt d 4 with h4 | h5
  · exact lemmaF_le_four d h4
  · exact lemmaF_of_facet hfac d (by omega)

end PackingOptimality.Restricted
