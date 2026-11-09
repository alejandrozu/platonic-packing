import PackingOptimality.OffColumn
import PackingOptimality.LemmaF5

/-!
# Restricted Lemma F: the pivot inequality

Write `R = [c r; x M]` with the pivot `c = R p q > 0` outside column `j`, and let `Q` be the polar factor of the
minor (`NearAxis.polarQ`). Normalise the signs so that column `j` of `R` is nonnegative: `ν = r j ≥ 0` and
`y i = M i j ≥ 0`. Put `a = 1/(1 + c)`, `L = ‖r‖₁`, `ρ = L - ν`, `κ₁ = 1 + c - ρ` and let
`G i = 2 - |x i| - ‖M i‖₁` be the slack of row `i` of `R`. Then (`pivot_bound`)

`F_j(R) ≤ F_j(Q) - a · Ξ`,
`Ξ = ν (c (c + L) - 1) + Σᵢ (2 κ₁ max(x i, 0) (y i - a ν x i) - ν x i G i)`,

as soon as `a ν x i ≤ y i` for every `i`. The only estimate used is the triangle inequality for the rows of `Q`;
everything else is the orthogonality of the columns `q` and `j` and the unit length of column `q`.

So `Ξ ≥ 0` reduces `F_j(R) ≤ 1` to restricted Lemma F in one dimension less (`pivot_step`).

`Ξ ≥ 0` holds in particular (`pivot_caseA`) when
* `c` is the largest entry of row `p` in absolute value,
* every row `i` with `x i > 0` has `2 ν ≤ (2 κ₁ + ν) y i`, which holds when `y i ≥ ν` (row `p` is a row where
  column `j` is smallest) and `ρ ≤ c + ν/2` (row `p` is concentrated on its two largest entries).

The proof of this case bounds the slack of a row `i` with `x i > 0` through its orthogonality to row `p`.
-/

namespace PackingOptimality.Restricted

open NearAxis Matrix

variable {m : ℕ}

/-- The pivot quantity `Ξ`. -/
noncomputable def Xi (c : ℝ) (r x : Fin m → ℝ) (M : Matrix (Fin m) (Fin m) ℝ) (j : Fin m) : ℝ :=
  r j * (c * (c + l1 r) - 1) +
    ∑ i, (2 * (1 + c - (l1 r - r j)) * max (x i) 0 * (M i j - (1 - c) / sq2 x * r j * x i) -
      r j * x i * (2 - |x i| - rowL1 M i))

/-- One row of the pivot inequality: an exact identity up to the triangle-inequality bound `hw` on the row of `Q`. -/
lemma pivot_term (x y ν a c ρ mM wQ : ℝ) (hac : a * (1 + c) = 1) (hy : 0 ≤ y) (hY : a * ν * x ≤ y)
    (hw : wQ ≤ (y - a * ν * x) + (mM - y) + a * |x| * ρ) :
    y * (2 - |x| - mM) ≤ |y - a * ν * x| * (2 - wQ) + (1 - a * (ρ + ν)) * x * y
      - a * ν * (1 - a * (ρ + ν)) * x ^ 2
      - a * (2 * (1 + c - ρ) * max x 0 * (y - a * ν * x) - ν * x * (2 - |x| - mM)) := by
  have hY0 : 0 ≤ y - a * ν * x := by linarith
  rw [abs_of_nonneg hY0]
  have h1 : (y - a * ν * x) * (2 - (y - a * ν * x) - mM + y - a * |x| * ρ) ≤
      (y - a * ν * x) * (2 - wQ) := mul_le_mul_of_nonneg_left (by linarith) hY0
  rcases le_total 0 x with hx | hx
  · rw [abs_of_nonneg hx, max_eq_left hx] at *
    have e : (y - a * ν * x) * (2 - (y - a * ν * x) - mM + y - a * x * ρ) + (1 - a * (ρ + ν)) * x * y
        - a * ν * (1 - a * (ρ + ν)) * x ^ 2
        - a * (2 * (1 + c - ρ) * x * (y - a * ν * x) - ν * x * (2 - x - mM)) - y * (2 - x - mM) = 0 := by
      linear_combination (2 * x * (a * ν * x - y)) * hac
    linarith
  · rw [abs_of_nonpos hx, max_eq_right hx] at *
    have e : (y - a * ν * x) * (2 - (y - a * ν * x) - mM + y - a * -x * ρ) + (1 - a * (ρ + ν)) * x * y
        - a * ν * (1 - a * (ρ + ν)) * x ^ 2
        - a * (2 * (1 + c - ρ) * 0 * (y - a * ν * x) - ν * x * (2 - -x - mM)) - y * (2 - -x - mM) = 0 := by
      ring
    linarith

/-- Splitting off the entry `j` of an ℓ¹ norm. -/
lemma l1_split (v : Fin m → ℝ) (j : Fin m) : l1 v = |v j| + ∑ k ∈ Finset.univ.erase j, |v k| := by
  unfold l1
  exact (Finset.add_sum_erase _ _ (Finset.mem_univ j)).symm

/-- The rows of the polar factor, with the entry in column `j` kept exactly. -/
lemma polar_row_le_split {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (i j : Fin m) :
    rowL1 (polarQ c x M) i ≤ |polarQ c x M i j| + (rowL1 M i - |M i j|) +
      (1 - c) / sq2 x * |x i| * (l1 r - |r j|) := by
  have ha : 0 ≤ (1 - c) / sq2 x := div_nonneg (sub_nonneg.mpr (block_c_le_one h hc)) (sq2_nonneg x)
  have e1 := l1_split (polarQ c x M i) j
  have e2 := l1_split (M i) j
  have e3 := l1_split r j
  unfold rowL1
  rw [e1, e2, e3]
  have hk : ∑ k ∈ Finset.univ.erase j, |polarQ c x M i k| ≤
      ∑ k ∈ Finset.univ.erase j, (|M i k| + (1 - c) / sq2 x * |x i| * |r k|) := by
    apply Finset.sum_le_sum
    intro k _
    rw [polarQ_entry h hc]
    have := abs_sub (M i k) ((1 - c) / sq2 x * x i * r k)
    simpa [abs_mul, abs_of_nonneg ha, mul_assoc] using this
  rw [Finset.sum_add_distrib, ← Finset.mul_sum] at hk
  linarith

/-- **The pivot inequality** `F_j(R) ≤ F_j(Q) - a Ξ` (block form, column `j` normalised to be nonnegative). -/
theorem pivot_bound {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (hx : 0 < sq2 x) (j : Fin m) (hν : 0 ≤ r j)
    (hy : ∀ i, 0 ≤ M i j) (hY : ∀ i, (1 - c) / sq2 x * r j * x i ≤ M i j) :
    Gcol c r x M j ≤ Fcol (polarQ c x M) j - (1 - c) / sq2 x * Xi c r x M j := by
  set a := (1 - c) / sq2 x with ha_def
  have hc1 := block_c_le_one h hc
  have ha1 : a * (1 + c) = 1 := by
    rw [ha_def, div_mul_eq_mul_div, div_eq_one_iff_eq (ne_of_gt hx)]
    nlinarith [h.col1]
  set ν := r j with hν_def
  set L := l1 r with hL
  set Q := polarQ c x M with hQdef
  have hQe : ∀ i, Q i j = M i j - a * x i * ν := fun i => polarQ_entry h hc i j
  have hterm : ∀ i, M i j * (2 - |x i| - rowL1 M i) ≤
      |Q i j| * (2 - rowL1 Q i) + (1 - a * L) * (x i * M i j) - a * ν * (1 - a * L) * x i ^ 2
      - a * (2 * (1 + c - (L - ν)) * max (x i) 0 * (M i j - a * ν * x i) -
          ν * x i * (2 - |x i| - rowL1 M i)) := by
    intro i
    have hw := polar_row_le_split h hc i j
    rw [← hQdef, abs_of_nonneg (hy i), abs_of_nonneg hν, ← hL, ← ha_def] at hw
    have hQij : Q i j = M i j - a * ν * x i := by rw [hQe i]; ring
    rw [hQij] at hw ⊢
    have hY0 : 0 ≤ M i j - a * ν * x i := by linarith [hY i]
    rw [abs_of_nonneg hY0] at hw
    have := pivot_term (x i) (M i j) ν a c (L - ν) (rowL1 M i) (rowL1 Q i) ha1 (hy i)
      (hY i) (by linarith)
    have e : L - ν + ν = L := by ring
    rw [e] at this
    linarith
  have hsum := Finset.sum_le_sum fun i (_ : i ∈ Finset.univ) => hterm i
  rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib, Finset.sum_add_distrib] at hsum
  have hFQ : ∑ i, |Q i j| * (2 - rowL1 Q i) = Fcol Q j := rfl
  have horth : ∑ i, x i * M i j = -(c * ν) := by linarith [h.col1_perp j]
  have hsq : ∑ i, x i ^ 2 = 1 - c ^ 2 := by have := h.col1; simp only [sq2] at this; linarith
  have e1 : ∑ i, (1 - a * L) * (x i * M i j) = (1 - a * L) * -(c * ν) := by rw [← Finset.mul_sum, horth]
  have e2 : ∑ i, a * ν * (1 - a * L) * x i ^ 2 = a * ν * (1 - a * L) * (1 - c ^ 2) := by
    rw [← Finset.mul_sum, hsq]
  have e3 : ∑ i, a * (2 * (1 + c - (L - ν)) * max (x i) 0 * (M i j - a * ν * x i) -
      ν * x i * (2 - |x i| - rowL1 M i)) =
      a * ∑ i, (2 * (1 + c - (L - ν)) * max (x i) 0 * (M i j - a * ν * x i) -
      ν * x i * (2 - |x i| - rowL1 M i)) := by rw [Finset.mul_sum]
  rw [hFQ, e1, e2, e3] at hsum
  have hXi : Xi c r x M j = ν * (c * (c + L) - 1) +
      ∑ i, (2 * (1 + c - (L - ν)) * max (x i) 0 * (M i j - a * ν * x i) -
        ν * x i * (2 - |x i| - rowL1 M i)) := by
    simp only [Xi, ← hν_def, ← hL, ← ha_def]
  rw [hXi]
  unfold Gcol
  rw [abs_of_pos hc, abs_of_nonneg hν, ← hL]
  have hsum' : ∑ i, |M i j| * (2 - |x i| - rowL1 M i) = ∑ i, M i j * (2 - |x i| - rowL1 M i) :=
    Finset.sum_congr rfl fun i _ => by rw [abs_of_nonneg (hy i)]
  rw [hsum']
  -- the pivot row: ν (2 - c - L) = ν (1 - a L) - a ν (c (c + L) - 1) + ... (uses a (1 + c) = 1)
  have hpiv : ν * (2 - c - L) + (1 - a * L) * -(c * ν) - a * ν * (1 - a * L) * (1 - c ^ 2) =
      -(a * (ν * (c * (c + L) - 1))) := by
    linear_combination (-(ν * (L * a * c - L * a - L - 2 * c + 2))) * ha1
  linarith [hpiv, hsum]

/-- **The pivot step.** With restricted Lemma F in dimension `m`, `Ξ ≥ 0` gives `F_j(R) ≤ 1` (block form,
column `j` normalised to be nonnegative, rows of `R` of ℓ¹ norm at most 2, `‖r‖₁ ≤ 1 + c`). -/
theorem pivot_step (hF : LemmaFr m) {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (j : Fin m) (hrows : ∀ i, |x i| + rowL1 M i ≤ 2)
    (hrc : l1 r ≤ 1 + c) (hν : 0 ≤ r j) (hy : ∀ i, 0 ≤ M i j)
    (hY : ∀ i, (1 - c) / sq2 x * r j * x i ≤ M i j) (hXi : 0 < sq2 x → 0 ≤ Xi c r x M j) :
    Gcol c r x M j ≤ 1 := by
  have hc1 := block_c_le_one h hc
  rcases (sq2_nonneg x).eq_or_lt with hx | hx
  · have hx0 : sq2 x = 0 := hx.symm
    have hcc : c = 1 := by nlinarith [h.col1]
    have hr0 : sq2 r = 0 := by rw [hcc] at h; nlinarith [h.row1]
    have hxv := eq_zero_of_sq2_eq_zero hx0
    have hrv := eq_zero_of_sq2_eq_zero hr0
    have hM : M * Mᵀ = 1 := by
      have := block_mul_transpose h
      rw [hxv] at this
      simpa using this
    have hMr : ∀ i, rowL1 M i ≤ 2 := fun i => by
      have := hrows i; rw [hxv] at this; simpa using this
    have := hF M hM hMr j
    simpa [Gcol, Fcol, hxv, hrv] using this
  · have ha0 : 0 ≤ (1 - c) / sq2 x := div_nonneg (sub_nonneg.mpr hc1) hx.le
    have ha1 : (1 - c) / sq2 x * (1 + c) = 1 := by
      rw [div_mul_eq_mul_div, div_eq_one_iff_eq (ne_of_gt hx)]
      nlinarith [h.col1]
    have haL : (1 - c) / sq2 x * l1 r ≤ 1 := by nlinarith [l1_nonneg r]
    have hQ := polarQ_orth h hc hx
    have hQr : ∀ i, rowL1 (polarQ c x M) i ≤ 2 := fun i => by
      have h1 := polar_row_le h hc i
      have hxa : (1 - c) / sq2 x * |x i| * l1 r ≤ |x i| := by
        have := mul_le_mul_of_nonneg_left haL (abs_nonneg (x i))
        linarith [show (1 - c) / sq2 x * |x i| * l1 r = |x i| * ((1 - c) / sq2 x * l1 r) by ring]
      linarith [hrows i]
    have hb := pivot_bound h hc hx j hν hy hY
    have hFQ := hF _ hQ hQr j
    nlinarith [mul_nonneg ha0 (hXi hx)]

/-- **The concentrated case: `Ξ ≥ 0`.** Hypotheses (block form, column `j` nonnegative): row `p` is orthogonal to
the other rows, `c` is its largest entry, the rows of `R` have ℓ¹ norm at most 2, and every row `i` with
`x i > 0` has `2 ν ≤ (2 κ₁ + ν) y i`. -/
theorem pivot_caseA {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (hx : 0 < sq2 x) (j : Fin m)
    (hperp : ∀ i, c * x i + ∑ k, r k * M i k = 0) (hmax : ∀ k, |r k| ≤ c)
    (hrows : ∀ i, |x i| + rowL1 M i ≤ 2) (hν : 0 ≤ r j) (hy : ∀ i, 0 ≤ M i j)
    (hgood : ∀ i, 0 < x i → 2 * r j ≤ (2 * (1 + c - (l1 r - r j)) + r j) * M i j) :
    0 ≤ Xi c r x M j := by
  have hc1 := block_c_le_one h hc
  set a := (1 - c) / sq2 x with ha_def
  have ha0 : 0 ≤ a := div_nonneg (sub_nonneg.mpr hc1) hx.le
  have ha1 : a * (1 + c) = 1 := by
    rw [ha_def, div_mul_eq_mul_div, div_eq_one_iff_eq (ne_of_gt hx)]
    nlinarith [h.col1]
  set ν := r j with hν_def
  set L := l1 r with hL
  -- ρ = L - ν ≥ 0
  have hsplit := l1_split r j
  rw [← hL, ← hν_def, abs_of_nonneg hν] at hsplit
  have hrest0 : 0 ≤ ∑ k ∈ Finset.univ.erase j, |r k| := Finset.sum_nonneg fun k _ => abs_nonneg _
  have hρ : 0 ≤ L - ν := by linarith
  -- the pivot row term: c (c + L) ≥ c² + ‖r‖₂² = 1
  have hD : 0 ≤ ν * (c * (c + L) - 1) := by
    apply mul_nonneg hν
    have hcl : sq2 r ≤ c * L := by
      rw [hL]; unfold sq2 l1; rw [Finset.mul_sum]
      apply Finset.sum_le_sum; intro k _
      have := hmax k
      nlinarith [sq_abs (r k), abs_nonneg (r k)]
    nlinarith [h.row1]
  -- each row
  have hT : ∀ i, 0 ≤ 2 * (1 + c - (L - ν)) * max (x i) 0 * (M i j - a * ν * x i) -
      ν * x i * (2 - |x i| - rowL1 M i) := by
    intro i
    have hG : 0 ≤ 2 - |x i| - rowL1 M i := by linarith [hrows i]
    rcases le_or_gt (x i) 0 with hxi | hxi
    · rw [max_eq_right hxi]
      nlinarith [mul_nonneg (mul_nonneg hν (neg_nonneg.mpr hxi)) hG]
    · rw [max_eq_left hxi.le, abs_of_pos hxi]
      -- the slack of row i, from its orthogonality to row p
      have hp := hperp i
      have hs := Finset.add_sum_erase Finset.univ (fun k => r k * M i k) (Finset.mem_univ j)
      have hrest : ∑ k ∈ Finset.univ.erase j, r k * M i k = -(c * x i + ν * M i j) := by
        rw [← hν_def] at hs; linarith
      have hMsplit := l1_split (M i) j
      rw [abs_of_nonneg (hy i)] at hMsplit
      have hbound : c * x i + ν * M i j ≤ c * ∑ k ∈ Finset.univ.erase j, |M i k| := by
        have h1 : |∑ k ∈ Finset.univ.erase j, r k * M i k| ≤ ∑ k ∈ Finset.univ.erase j, |r k| * |M i k| := by
          simpa [abs_mul] using Finset.abs_sum_le_sum_abs (fun k => r k * M i k) (Finset.univ.erase j)
        have h2 : ∑ k ∈ Finset.univ.erase j, |r k| * |M i k| ≤ ∑ k ∈ Finset.univ.erase j, c * |M i k| :=
          Finset.sum_le_sum fun k _ => mul_le_mul_of_nonneg_right (hmax k) (abs_nonneg _)
        rw [← Finset.mul_sum] at h2
        rw [hrest, abs_neg] at h1
        have h3 : 0 ≤ c * x i + ν * M i j := by nlinarith [hy i]
        rw [abs_of_nonneg h3] at h1
        linarith
      have hcG : c * (2 - x i - rowL1 M i) ≤ 2 * c - 2 * c * x i - (c + ν) * M i j := by
        unfold rowL1; rw [hMsplit]
        have e : c * (2 - x i - (M i j + ∑ k ∈ Finset.univ.erase j, |M i k|)) =
            2 * c - c * x i - c * M i j - c * ∑ k ∈ Finset.univ.erase j, |M i k| := by ring
        rw [e]; linarith [hbound]
      have hg := hgood i hxi
      -- c · bracket ≥ 0
      have key : 0 ≤ c * (2 * (1 + c - (L - ν)) * (M i j - a * ν * x i) - ν * (2 - x i - rowL1 M i)) := by
        have e : c * (2 * (1 + c - (L - ν)) * (M i j - a * ν * x i) - ν * (2 - x i - rowL1 M i)) =
            c * (2 * (1 + c - (L - ν)) * M i j) - 2 * c * ν * x i * (a * (1 + c - (L - ν)))
              - ν * (c * (2 - x i - rowL1 M i)) := by ring
        rw [e]
        have h4 : a * (1 + c - (L - ν)) = 1 - a * (L - ν) := by linarith
        rw [h4]
        nlinarith [mul_nonneg (mul_nonneg (mul_nonneg hc.le hν) hxi.le) (mul_nonneg ha0 hρ),
          mul_nonneg hν (mul_nonneg hν (hy i)), mul_le_mul_of_nonneg_left hcG hν,
          mul_le_mul_of_nonneg_left hg hc.le]
      have hbr : 0 ≤ 2 * (1 + c - (L - ν)) * (M i j - a * ν * x i) - ν * (2 - x i - rowL1 M i) := by
        by_contra hneg
        simp only [not_le] at hneg
        linarith [mul_neg_of_pos_of_neg hc hneg, key]
      nlinarith [mul_nonneg hxi.le hbr]
  unfold Xi
  rw [← ha_def, ← hν_def, ← hL]
  have := Finset.sum_nonneg fun i (_ : i ∈ Finset.univ) => hT i
  linarith

/-! ## Sign normalisation -/

section Signs

variable {n : ℕ}

/-- `±1` according to the sign of `t` (`+1` at `0`). -/
noncomputable def sgn1 (t : ℝ) : ℝ := if t < 0 then -1 else 1

lemma sgn1_sq (t : ℝ) : sgn1 t * sgn1 t = 1 := by unfold sgn1; split_ifs <;> norm_num

lemma sgn1_abs (t : ℝ) : |sgn1 t| = 1 := by unfold sgn1; split_ifs <;> norm_num

lemma sgn1_mul (t : ℝ) : sgn1 t * t = |t| := by
  unfold sgn1; split_ifs with h
  · rw [abs_of_neg h]; ring
  · rw [abs_of_nonneg (not_lt.mp h)]; ring

/-- Flip the signs of some rows and columns. -/
def flipM (R : Matrix (Fin n) (Fin n) ℝ) (s t : Fin n → ℝ) : Matrix (Fin n) (Fin n) ℝ :=
  fun i k => s i * R i k * t k

lemma flipM_orth {R : Matrix (Fin n) (Fin n) ℝ} {s t : Fin n → ℝ} (hs : ∀ i, s i * s i = 1)
    (ht : ∀ k, t k * t k = 1) (hR : R * Rᵀ = 1) : flipM R s t * (flipM R s t)ᵀ = 1 := by
  ext i l
  have h := congrFun (congrFun hR i) l
  simp only [Matrix.mul_apply, Matrix.transpose_apply, flipM] at h ⊢
  have e : ∑ k, s i * R i k * t k * (s l * R l k * t k) = s i * s l * ∑ k, R i k * R l k := by
    rw [Finset.mul_sum]; apply Finset.sum_congr rfl; intro k _
    have := ht k
    linear_combination (s i * s l * R i k * R l k) * this
  rw [e, h]
  by_cases hil : i = l
  · subst hil; simp [hs i]
  · simp [Matrix.one_apply, hil]

lemma flipM_abs {R : Matrix (Fin n) (Fin n) ℝ} {s t : Fin n → ℝ} (hs : ∀ i, |s i| = 1)
    (ht : ∀ k, |t k| = 1) (i k : Fin n) : |flipM R s t i k| = |R i k| := by
  simp [flipM, abs_mul, hs i, ht k]

lemma flipM_rowL1 {R : Matrix (Fin n) (Fin n) ℝ} {s t : Fin n → ℝ} (hs : ∀ i, |s i| = 1)
    (ht : ∀ k, |t k| = 1) (i : Fin n) : rowL1 (flipM R s t) i = rowL1 R i := by
  unfold rowL1 l1; exact Finset.sum_congr rfl fun k _ => flipM_abs hs ht i k

lemma flipM_Fcol {R : Matrix (Fin n) (Fin n) ℝ} {s t : Fin n → ℝ} (hs : ∀ i, |s i| = 1)
    (ht : ∀ k, |t k| = 1) (j : Fin n) : Fcol (flipM R s t) j = Fcol R j := by
  unfold Fcol; exact Finset.sum_congr rfl fun i _ => by rw [flipM_abs hs ht, flipM_rowL1 hs ht]

end Signs

/-- `Ξ ≥ 0` for the pivot `(p, q)` and the column `q.succAbove j'` of `R` (when `‖x‖₂ > 0`). -/
def PivotOK (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (p q : Fin (m + 1)) (j' : Fin m) : Prop :=
  0 < sq2 (fun i => R (p.succAbove i) q) →
    0 ≤ Xi (R p q) (fun k => R p (q.succAbove k)) (fun i => R (p.succAbove i) q)
      (fun i k => R (p.succAbove i) (q.succAbove k)) j'

/-- **The concentrated pivot for matrices.** Let `R` be orthogonal of size `m + 1` with rows of ℓ¹ norm at most 2.
Let `p` be a row where column `j` is smallest in absolute value and `q ≠ j` a column holding the largest entry of
row `p`, `c = |R p q|`, `ν = |R p j|`. If the rest of row `p` is small, `‖row p‖₁ - c - ν ≤ c + ν/2`, then restricted
Lemma F in dimension `m` gives `F_j(R) ≤ 1`. -/
theorem pivot_at (hF : LemmaFr m) (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (hw : ∀ i, rowL1 R i ≤ 2) (p q j : Fin (m + 1)) (hqj : q ≠ j)
    (hmax : ∀ k, |R p k| ≤ |R p q|) (hmin : ∀ i, |R p j| ≤ |R i j|)
    (hconc : rowL1 R p - |R p q| - |R p j| ≤ |R p q| + |R p j| / 2) : Fcol R j ≤ 1 := by
  -- normalise: column j nonnegative, pivot positive
  set s : Fin (m + 1) → ℝ := fun i => sgn1 (R i j) with hs_def
  set t : Fin (m + 1) → ℝ := fun k => if k = q then sgn1 (s p * R p q) else 1 with ht_def
  have hs1 : ∀ i, s i * s i = 1 := fun i => sgn1_sq _
  have hsa : ∀ i, |s i| = 1 := fun i => sgn1_abs _
  have ht1 : ∀ k, t k * t k = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_sq]
  have hta : ∀ k, |t k| = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_abs]
  set R' := flipM R s t with hR'_def
  have hR'o : R' * R'ᵀ = 1 := flipM_orth hs1 ht1 hR
  have hR'o' : R'ᵀ * R' = 1 := mul_eq_one_comm.mp hR'o
  have habs : ∀ i k, |R' i k| = |R i k| := flipM_abs hsa hta
  have hrow : ∀ i, rowL1 R' i = rowL1 R i := flipM_rowL1 hsa hta
  have htj : t j = 1 := by simp [ht_def, hqj.symm]
  have hcolj : ∀ i, R' i j = |R i j| := fun i => by
    simp only [hR'_def, flipM, htj, mul_one, hs_def]; exact sgn1_mul _
  have hpq : R' p q = |R p q| := by
    have htq : t q = sgn1 (s p * R p q) := by simp [ht_def]
    show s p * R p q * t q = |R p q|
    rw [htq, mul_comm, sgn1_mul, abs_mul, hsa p, one_mul]
  rw [← flipM_Fcol hsa hta j]
  change Fcol R' j ≤ 1
  -- the pivot is nonzero
  have hc0 : 0 < |R p q| := by
    rcases (abs_nonneg (R p q)).eq_or_lt with h0 | h0
    · exfalso
      have hrow1 := LemmaF4.sum_rows R hR p p
      rw [if_pos rfl] at hrow1
      have : ∀ k, R p k = 0 := fun k => abs_eq_zero.mp (le_antisymm (h0 ▸ hmax k) (abs_nonneg _))
      simp [this] at hrow1
    · exact h0
  obtain ⟨j', rfl⟩ := Fin.exists_succAbove_eq hqj.symm
  have hB := LemmaF4.block_orth R' hR'o hR'o' p q
  rw [Fcol_eq_Gcol R' p q j']
  rw [hpq] at hB ⊢
  set c := |R p q| with hc_def
  set r : Fin m → ℝ := fun k => R' p (q.succAbove k) with hr_def
  set x : Fin m → ℝ := fun i => R' (p.succAbove i) q with hx_def
  set M : Matrix (Fin m) (Fin m) ℝ := fun i k => R' (p.succAbove i) (q.succAbove k) with hM_def
  have hsplit := LemmaF4.rowL1_split R' p q
  rw [hpq] at hsplit
  have hrowp : c + l1 r = rowL1 R p := by
    rw [← hrow p, hsplit, abs_of_pos hc0]; simp only [l1, hr_def]
  have hrows : ∀ i, |x i| + rowL1 M i ≤ 2 := by
    intro i
    have h1 := LemmaF4.rowL1_split R' (p.succAbove i) q
    have h2 := hw (p.succAbove i)
    rw [← hrow] at h2
    simp only [rowL1, l1, hx_def, hM_def] at h1 h2 ⊢
    linarith
  have hmax' : ∀ k, |r k| ≤ c := fun k => by simp only [hr_def]; rw [habs]; exact hmax _
  have hν : 0 ≤ r j' := by simp only [hr_def]; rw [hcolj]; exact abs_nonneg _
  have hνeq : r j' = |R p (q.succAbove j')| := by simp only [hr_def]; rw [hcolj]
  have hy : ∀ i, 0 ≤ M i j' := fun i => by simp only [hM_def]; rw [hcolj]; exact abs_nonneg _
  have hyeq : ∀ i, M i j' = |R (p.succAbove i) (q.succAbove j')| := fun i => by simp only [hM_def]; rw [hcolj]
  have hyν : ∀ i, r j' ≤ M i j' := fun i => by rw [hνeq, hyeq]; exact hmin _
  -- c (c + ‖r‖₁) ≥ 1, so c ≥ 1/2 and ‖r‖₁ ≤ 1 + c
  have hcl : sq2 r ≤ c * l1 r := by
    unfold sq2 l1; rw [Finset.mul_sum]
    apply Finset.sum_le_sum; intro k _
    have := hmax' k
    nlinarith [sq_abs (r k), abs_nonneg (r k)]
  have hrow1 := hB.row1
  have hwp : c + l1 r ≤ 2 := by rw [hrowp]; exact hw p
  have hrc : l1 r ≤ 1 + c := by nlinarith [l1_nonneg r]
  -- the coefficient a = (1 - c)/‖x‖² lies in [0, 1], and |x i| ≤ 1
  have hc1 := block_c_le_one hB hc0
  have hxi1 : ∀ i, |x i| ≤ 1 := fun i => by
    have h1 := hB.col1
    have h2 : x i ^ 2 ≤ sq2 x := by
      unfold sq2
      exact Finset.single_le_sum (f := fun k => x k ^ 2) (fun k _ => sq_nonneg _) (Finset.mem_univ i)
    have h3 : |x i| ^ 2 ≤ 1 := by rw [sq_abs]; nlinarith [sq_nonneg c]
    nlinarith [abs_nonneg (x i)]
  have ha01 : 0 ≤ (1 - c) / sq2 x ∧ (1 - c) / sq2 x ≤ 1 := by
    rcases (sq2_nonneg x).eq_or_lt with hx | hx
    · rw [← hx, div_zero]; norm_num
    · exact ⟨div_nonneg (sub_nonneg.mpr hc1) hx.le, coef_le_one hB hc0 hx⟩
  have hY : ∀ i, (1 - c) / sq2 x * r j' * x i ≤ M i j' := by
    intro i
    have h1 : (1 - c) / sq2 x * r j' * x i ≤ r j' := by
      have h2 : (1 - c) / sq2 x * x i ≤ 1 := by
        have := mul_le_mul ha01.2 (hxi1 i) (abs_nonneg _) zero_le_one
        have h3 := le_abs_self ((1 - c) / sq2 x * x i)
        rw [abs_mul, abs_of_nonneg ha01.1] at h3
        nlinarith
      nlinarith [mul_le_mul_of_nonneg_left h2 hν]
    linarith [hyν i]
  apply pivot_step hF hB hc0 j' hrows hrc hν hy hY
  intro hx
  -- the concentrated case
  have hperp : ∀ i, c * x i + ∑ k, r k * M i k = 0 := by
    intro i
    have h := LemmaF4.sum_rows R' hR'o p (p.succAbove i)
    rw [Fin.sum_univ_succAbove _ q, if_neg (Fin.succAbove_ne p i).symm, hpq] at h
    simpa [hr_def, hx_def, hM_def] using h
  apply pivot_caseA hB hc0 hx j' hperp hmax' hrows hν hy
  intro i _
  have hconc' : l1 r - r j' ≤ c + r j' / 2 := by
    have := hconc
    rw [← hrowp, ← hνeq] at this
    linarith
  have hk : 2 ≤ 2 * (1 + c - (l1 r - r j')) + r j' := by linarith
  nlinarith [hyν i, hy i]

/-- The pivot step for matrices: normalise the signs, then use `PivotOK` for the normalised matrix. -/
theorem pivot_at_gen (hF : LemmaFr m) (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (hw : ∀ i, rowL1 R i ≤ 2) (p q j : Fin (m + 1)) (hqj : q ≠ j)
    (hmax : ∀ k, |R p k| ≤ |R p q|) (hmin : ∀ i, |R p j| ≤ |R i j|)
    (hXi : ∀ R' : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ, R' * R'ᵀ = 1 → (∀ i k, |R' i k| = |R i k|) →
      (∀ i, 0 ≤ R' i j) → R' p q = |R p q| → ∀ j', q.succAbove j' = j → PivotOK R' p q j') :
    Fcol R j ≤ 1 := by
  -- normalise: column j nonnegative, pivot positive
  set s : Fin (m + 1) → ℝ := fun i => sgn1 (R i j) with hs_def
  set t : Fin (m + 1) → ℝ := fun k => if k = q then sgn1 (s p * R p q) else 1 with ht_def
  have hs1 : ∀ i, s i * s i = 1 := fun i => sgn1_sq _
  have hsa : ∀ i, |s i| = 1 := fun i => sgn1_abs _
  have ht1 : ∀ k, t k * t k = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_sq]
  have hta : ∀ k, |t k| = 1 := fun k => by simp only [ht_def]; split_ifs <;> simp [sgn1_abs]
  set R' := flipM R s t with hR'_def
  have hR'o : R' * R'ᵀ = 1 := flipM_orth hs1 ht1 hR
  have hR'o' : R'ᵀ * R' = 1 := mul_eq_one_comm.mp hR'o
  have habs : ∀ i k, |R' i k| = |R i k| := flipM_abs hsa hta
  have hrow : ∀ i, rowL1 R' i = rowL1 R i := flipM_rowL1 hsa hta
  have htj : t j = 1 := by simp [ht_def, hqj.symm]
  have hcolj : ∀ i, R' i j = |R i j| := fun i => by
    simp only [hR'_def, flipM, htj, mul_one, hs_def]; exact sgn1_mul _
  have hpq : R' p q = |R p q| := by
    have htq : t q = sgn1 (s p * R p q) := by simp [ht_def]
    show s p * R p q * t q = |R p q|
    rw [htq, mul_comm, sgn1_mul, abs_mul, hsa p, one_mul]
  rw [← flipM_Fcol hsa hta j]
  change Fcol R' j ≤ 1
  -- the pivot is nonzero
  have hc0 : 0 < |R p q| := by
    rcases (abs_nonneg (R p q)).eq_or_lt with h0 | h0
    · exfalso
      have hrow1 := LemmaF4.sum_rows R hR p p
      rw [if_pos rfl] at hrow1
      have : ∀ k, R p k = 0 := fun k => abs_eq_zero.mp (le_antisymm (h0 ▸ hmax k) (abs_nonneg _))
      simp [this] at hrow1
    · exact h0
  obtain ⟨j', rfl⟩ := Fin.exists_succAbove_eq hqj.symm
  have hB := LemmaF4.block_orth R' hR'o hR'o' p q
  rw [Fcol_eq_Gcol R' p q j']
  rw [hpq] at hB ⊢
  set c := |R p q| with hc_def
  set r : Fin m → ℝ := fun k => R' p (q.succAbove k) with hr_def
  set x : Fin m → ℝ := fun i => R' (p.succAbove i) q with hx_def
  set M : Matrix (Fin m) (Fin m) ℝ := fun i k => R' (p.succAbove i) (q.succAbove k) with hM_def
  have hsplit := LemmaF4.rowL1_split R' p q
  rw [hpq] at hsplit
  have hrowp : c + l1 r = rowL1 R p := by
    rw [← hrow p, hsplit, abs_of_pos hc0]; simp only [l1, hr_def]
  have hrows : ∀ i, |x i| + rowL1 M i ≤ 2 := by
    intro i
    have h1 := LemmaF4.rowL1_split R' (p.succAbove i) q
    have h2 := hw (p.succAbove i)
    rw [← hrow] at h2
    simp only [rowL1, l1, hx_def, hM_def] at h1 h2 ⊢
    linarith
  have hmax' : ∀ k, |r k| ≤ c := fun k => by simp only [hr_def]; rw [habs]; exact hmax _
  have hν : 0 ≤ r j' := by simp only [hr_def]; rw [hcolj]; exact abs_nonneg _
  have hνeq : r j' = |R p (q.succAbove j')| := by simp only [hr_def]; rw [hcolj]
  have hy : ∀ i, 0 ≤ M i j' := fun i => by simp only [hM_def]; rw [hcolj]; exact abs_nonneg _
  have hyeq : ∀ i, M i j' = |R (p.succAbove i) (q.succAbove j')| := fun i => by simp only [hM_def]; rw [hcolj]
  have hyν : ∀ i, r j' ≤ M i j' := fun i => by rw [hνeq, hyeq]; exact hmin _
  -- c (c + ‖r‖₁) ≥ 1, so c ≥ 1/2 and ‖r‖₁ ≤ 1 + c
  have hcl : sq2 r ≤ c * l1 r := by
    unfold sq2 l1; rw [Finset.mul_sum]
    apply Finset.sum_le_sum; intro k _
    have := hmax' k
    nlinarith [sq_abs (r k), abs_nonneg (r k)]
  have hrow1 := hB.row1
  have hwp : c + l1 r ≤ 2 := by rw [hrowp]; exact hw p
  have hrc : l1 r ≤ 1 + c := by nlinarith [l1_nonneg r]
  -- the coefficient a = (1 - c)/‖x‖² lies in [0, 1], and |x i| ≤ 1
  have hc1 := block_c_le_one hB hc0
  have hxi1 : ∀ i, |x i| ≤ 1 := fun i => by
    have h1 := hB.col1
    have h2 : x i ^ 2 ≤ sq2 x := by
      unfold sq2
      exact Finset.single_le_sum (f := fun k => x k ^ 2) (fun k _ => sq_nonneg _) (Finset.mem_univ i)
    have h3 : |x i| ^ 2 ≤ 1 := by rw [sq_abs]; nlinarith [sq_nonneg c]
    nlinarith [abs_nonneg (x i)]
  have ha01 : 0 ≤ (1 - c) / sq2 x ∧ (1 - c) / sq2 x ≤ 1 := by
    rcases (sq2_nonneg x).eq_or_lt with hx | hx
    · rw [← hx, div_zero]; norm_num
    · exact ⟨div_nonneg (sub_nonneg.mpr hc1) hx.le, coef_le_one hB hc0 hx⟩
  have hY : ∀ i, (1 - c) / sq2 x * r j' * x i ≤ M i j' := by
    intro i
    have h1 : (1 - c) / sq2 x * r j' * x i ≤ r j' := by
      have h2 : (1 - c) / sq2 x * x i ≤ 1 := by
        have := mul_le_mul ha01.2 (hxi1 i) (abs_nonneg _) zero_le_one
        have h3 := le_abs_self ((1 - c) / sq2 x * x i)
        rw [abs_mul, abs_of_nonneg ha01.1] at h3
        nlinarith
      nlinarith [mul_le_mul_of_nonneg_left h2 hν]
    linarith [hyν i]
  apply pivot_step hF hB hc0 j' hrows hrc hν hy hY
  intro hx
  have hok := hXi R' hR'o habs (fun i => by rw [hcolj]; exact abs_nonneg _) hpq j' rfl hx
  simp only [hpq] at hok
  exact hok


/-- The concentrated case of `PivotOK`, for a normalised matrix. -/
theorem caseA_ok (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (hw : ∀ i, rowL1 R i ≤ 2) (p q : Fin (m + 1)) (j' : Fin m) (hcol : ∀ i, 0 ≤ R i (q.succAbove j'))
    (hpq : 0 < R p q) (hmax : ∀ k, |R p k| ≤ R p q)
    (hmin : ∀ i, R p (q.succAbove j') ≤ R i (q.succAbove j'))
    (hconc : rowL1 R p - R p q - R p (q.succAbove j') ≤ R p q + R p (q.succAbove j') / 2) :
    PivotOK R p q j' := by
  intro hx
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have hB := LemmaF4.block_orth R hR hR' p q
  have hsplit := LemmaF4.rowL1_split R p q
  have hrowp : R p q + l1 (fun k => R p (q.succAbove k)) = rowL1 R p := by
    rw [hsplit, abs_of_pos hpq]; simp only [l1]
  have hrows : ∀ i, |R (p.succAbove i) q| + rowL1 (fun i k => R (p.succAbove i) (q.succAbove k)) i ≤ 2 := by
    intro i
    have h1 := LemmaF4.rowL1_split R (p.succAbove i) q
    have h2 := hw (p.succAbove i)
    simp only [rowL1, l1] at h1 h2 ⊢
    linarith
  have hperp : ∀ i, R p q * R (p.succAbove i) q +
      ∑ k, R p (q.succAbove k) * R (p.succAbove i) (q.succAbove k) = 0 := by
    intro i
    have h := LemmaF4.sum_rows R hR p (p.succAbove i)
    rw [Fin.sum_univ_succAbove _ q, if_neg (Fin.succAbove_ne p i).symm] at h
    exact h
  apply pivot_caseA hB hpq hx j' hperp (fun k => hmax _) hrows (hcol p) (fun i => hcol _)
  intro i _
  have hk : 2 ≤ 2 * (1 + R p q - (l1 (fun k => R p (q.succAbove k)) - R p (q.succAbove j'))) +
      R p (q.succAbove j') := by
    rw [← hrowp] at hconc; linarith
  have h1 := hmin (p.succAbove i)
  have h2 := hcol p
  nlinarith

/-- **The pivot conjecture** in dimension `m + 1`: `Ξ ≥ 0` for every normalised orthogonal matrix with rows of ℓ¹
norm at most 2, every row `p` where column `j = q.succAbove j'` is smallest and every column `q ≠ j` holding the
largest entry of row `p`. Numerically it holds with room to spare whenever row `p` is spread; `caseA_ok` proves
it when row `p` is concentrated. -/
def PivotConj (m : ℕ) : Prop :=
  ∀ R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ, R * Rᵀ = 1 → (∀ i, rowL1 R i ≤ 2) →
    ∀ p q (j' : Fin m), (∀ i, 0 ≤ R i (q.succAbove j')) → 0 < R p q → (∀ k, |R p k| ≤ R p q) →
      (∀ i, R p (q.succAbove j') ≤ R i (q.succAbove j')) → PivotOK R p q j'

/-- In dimension at least 5, the largest entry of the row where a column is smallest lies outside that column. -/
theorem exists_pivot (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1) (hw : ∀ i, rowL1 R i ≤ 2)
    (hm : 4 ≤ m) (j : Fin (m + 1)) :
    ∃ p q, (∀ i, |R p j| ≤ |R i j|) ∧ q ≠ j ∧ ∀ k, |R p k| ≤ |R p q| := by
  obtain ⟨p, -, hp⟩ := Finset.exists_min_image Finset.univ (fun i => |R i j|) Finset.univ_nonempty
  have hne : (Finset.univ.erase j).Nonempty := by
    exact ⟨j.succAbove ⟨0, by omega⟩, Finset.mem_erase.mpr ⟨Fin.succAbove_ne j _, Finset.mem_univ _⟩⟩
  obtain ⟨q, hq, hqmax⟩ := Finset.exists_max_image (Finset.univ.erase j) (fun k => |R p k|) hne
  have hqj : q ≠ j := (Finset.mem_erase.mp hq).1
  refine ⟨p, q, fun i => hp i (Finset.mem_univ i), hqj, fun k => ?_⟩
  by_cases hkj : k = j
  · subst hkj
    by_contra hlt
    simp only [not_le] at hlt
    -- every entry of row p is at most ν = |R p k|, so ν ≥ 1/2; then column k is too long
    have hall : ∀ l, |R p l| ≤ |R p k| := fun l => by
      by_cases hl : l = k
      · rw [hl]
      · exact (hqmax l (Finset.mem_erase.mpr ⟨hl, Finset.mem_univ l⟩)).trans hlt.le
    have hrow1 := LemmaF4.sum_rows R hR p p
    rw [if_pos rfl] at hrow1
    have h1 : (1 : ℝ) ≤ |R p k| * rowL1 R p := by
      rw [← hrow1]; unfold rowL1 l1; rw [Finset.mul_sum]
      apply Finset.sum_le_sum; intro l _
      have := hall l
      nlinarith [sq_abs (R p l), abs_nonneg (R p l)]
    have h2 := hw p
    have hν : (1 : ℝ) / 2 ≤ |R p k| := by nlinarith [abs_nonneg (R p k)]
    have hcol := col_sq R hR k
    have h3 : ∑ i, R i k ^ 2 ≥ ∑ _i : Fin (m + 1), (1 / 2 : ℝ) ^ 2 := by
      apply Finset.sum_le_sum; intro i _
      have := (hp i (Finset.mem_univ i))
      nlinarith [sq_abs (R i k), abs_nonneg (R i k)]
    simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul] at h3
    have hm' : (5 : ℝ) ≤ (m : ℝ) + 1 := by exact_mod_cast (by omega : 5 ≤ m + 1)
    push_cast at h3
    nlinarith
  · exact hqmax k (Finset.mem_erase.mpr ⟨hkj, Finset.mem_univ k⟩)

/-- **Restricted Lemma F in dimension `m + 1` from dimension `m` and the pivot conjecture** (`m ≥ 4`). -/
theorem lemmaFr_succ_of_pivotConj (hF : LemmaFr m) (hm : 4 ≤ m) (hP : PivotConj m) : LemmaFr (m + 1) := by
  intro R hR hw j
  obtain ⟨p, q, hmin, hqj, hmax⟩ := exists_pivot R hR hw hm j
  apply pivot_at_gen hF R hR hw p q j hqj hmax hmin
  intro R' hR'o habs hcol hpq j' hj'
  subst hj'
  have hrow : ∀ i, rowL1 R' i = rowL1 R i := fun i => by
    unfold rowL1 l1; exact Finset.sum_congr rfl fun k _ => habs i k
  apply hP R' hR'o (fun i => (hrow i).trans_le (hw i)) p q j' hcol
  · rw [hpq]
    rcases (abs_nonneg (R p q)).eq_or_lt with h0 | h0
    · exfalso
      have hrow1 := LemmaF4.sum_rows R hR p p
      rw [if_pos rfl] at hrow1
      have : ∀ k, R p k = 0 := fun k => abs_eq_zero.mp (le_antisymm (h0 ▸ hmax k) (abs_nonneg _))
      simp [this] at hrow1
    · exact h0
  · intro k; rw [hpq, habs]; exact hmax k
  · intro i
    have h1 := habs p (q.succAbove j'); have h2 := habs i (q.succAbove j')
    rw [abs_of_nonneg (hcol p)] at h1; rw [abs_of_nonneg (hcol i)] at h2
    rw [h1, h2]; exact hmin i

/-- Restricted Lemma F in dimension 5, from Lemma F in dimension 5 (`LemmaF5.lemmaF5`). -/
theorem lemmaFr_five : LemmaFr 5 := lemmaFr_of_lemmaF LemmaF5.lemmaF5

/-- **Restricted Lemma F in every dimension, from the pivot conjecture in dimensions 6 and up.** -/
theorem lemmaFr_all_of_pivotConj (hP : ∀ m, 5 ≤ m → PivotConj m) : ∀ d, LemmaFr d
  | 0 => lemmaFr_zero
  | n + 1 => by
    by_cases hn : n + 1 ≤ 4
    · exact lemmaFr_le_four (n + 1) hn
    · by_cases h5 : n + 1 = 5
      · rw [h5]; exact lemmaFr_five
      · exact lemmaFr_succ_of_pivotConj (lemmaFr_all_of_pivotConj hP n) (by omega) (hP n (by omega))

open scoped Pointwise in
/-- **The cube centre lemma in every dimension, from the pivot conjecture in dimensions 6 and up.** -/
theorem centre_all_of_pivotConj (hP : ∀ m, 5 ≤ m → PivotConj m) {d : ℕ} (s : ℝ) (hs0 : 0 ≤ s) (hs : s < 2)
    (g : EuclideanSpace ℝ (Fin d) ≃ᵃⁱ[ℝ] EuclideanSpace ℝ (Fin d)) (hg : g '' cube d ⊆ s • cube d) :
    (s / 2) • WithLp.toLp 2 (fun _ => (1 : ℝ)) ∈ interior (g '' cube d) :=
  CentreGeneral.centre_of_lemmaF_rows (lemmaFr_all_of_pivotConj hP d) s hs0 hs g hg

/-- The case left by the concentrated pivot, the off-column step, the near step and `‖column j‖₁ ≤ 2`:
every pair (row `p` where column `j` is smallest, column `q ≠ j` holding the largest entry of row `p`) has a
spread row `p` (`‖row p‖₁ - c - ν > c + ν/2`) and `c² < 3/4`. -/
def RemainingCase4 (d : ℕ) : Prop :=
  ∀ R : Matrix (Fin d) (Fin d) ℝ, R * Rᵀ = 1 → (∀ i, rowL1 R i ≤ 2) → ∀ j,
    (∀ i, R i j ≠ 0 → 1 < rowL1 R i - |R i j|) → 2 < ∑ i, |R i j| →
    (∀ p q, (∀ i, |R p j| ≤ |R i j|) → q ≠ j → (∀ k, |R p k| ≤ |R p q|) →
      |R p q| + |R p j| / 2 < rowL1 R p - |R p q| - |R p j| ∧ R p q ^ 2 < 3 / 4) →
    Fcol R j ≤ 1

/-- **The induction step with the concentrated pivot.** -/
theorem lemmaFr_succ4 (hF : LemmaFr m) (hrem : RemainingCase4 (m + 1)) : LemmaFr (m + 1) := by
  apply lemmaFr_succ hF
  intro R hR hw j hgood hS
  by_cases hpair : ∃ p q, (∀ i, |R p j| ≤ |R i j|) ∧ q ≠ j ∧ (∀ k, |R p k| ≤ |R p q|) ∧
      (rowL1 R p - |R p q| - |R p j| ≤ |R p q| + |R p j| / 2 ∨ 3 / 4 ≤ R p q ^ 2)
  · obtain ⟨p, q, hmin, hqj, hmax, hcase⟩ := hpair
    rcases hcase with hconc | hc
    · exact pivot_at hF R hR hw p q j hqj hmax hmin hconc
    · exact offcol_at hF R hR hw p q j hqj hc hmin
  · refine hrem R hR hw j hgood hS fun p q hmin hqj hmax => ?_
    by_contra hneg
    rw [not_and_or, not_lt, not_lt] at hneg
    exact hpair ⟨p, q, hmin, hqj, hmax, hneg⟩

end PackingOptimality.Restricted
