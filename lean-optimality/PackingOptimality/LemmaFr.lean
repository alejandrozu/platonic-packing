import PackingOptimality.LemmaF4
import PackingOptimality.CentreGeneral

/-!
# Restricted Lemma F: the near-axis step in every dimension

The cube centre lemma needs `F_j(R) = Σᵢ |Rᵢⱼ| (2 - ‖row i‖₁) ≤ 1` only for orthogonal matrices whose rows all have
ℓ¹ norm at most 2: a unit cube inside a cube of side `s < 2` has all its widths `‖row i‖₁ ≤ s`. Call this
**restricted Lemma F** (`LemmaFr d`).

For restricted Lemma F, Hosono's near-axis step (`NearAxis.near_identity`, `NearAxis.lemmaK`) works in **every**
dimension. The rows of the polar factor `Q` stay within ℓ¹ norm 2, so the hypothesis `m ≤ 4` of
`NearAxis.near_region` is not needed. The step applies at any entry `c = R i₀ j ≠ 0` whose row has
`‖row i₀‖₁ - |c| ≤ 1` (`near_step`, `step_at`).

If no entry of column `j` qualifies, then every row meeting column `j` has `‖row i‖₁ > 1 + |Rᵢⱼ|`, and
`F_j(R) ≤ ‖column j‖₁ - 1` (`remaining_bound`). Since `‖column j‖₁ ≤ √d`, this settles `d ≤ 4` at once
(`lemmaFr_le_four`). With `centre_of_lemmaFr` it gives the cube centre lemma in dimensions 1 to 4 without
any computer search or case split.

For `d ≥ 5` the induction `LemmaFr m → LemmaFr (m + 1)` reduces to the *remaining case*:
`‖column j‖₁ > 2` and every row meeting column `j` has `‖row i‖₁ > 1 + |Rᵢⱼ|` (`lemmaFr_succ`).
-/

namespace PackingOptimality.Restricted

open NearAxis Matrix

variable {m : ℕ}

/-- **Restricted Lemma F** in dimension `m`: `F_j(Q) ≤ 1` for orthogonal `Q` whose rows have ℓ¹ norm at most 2. -/
def LemmaFr (m : ℕ) : Prop :=
  ∀ Q : Matrix (Fin m) (Fin m) ℝ, Q * Qᵀ = 1 → (∀ i, rowL1 Q i ≤ 2) → ∀ j, Fcol Q j ≤ 1

/-- Lemma F implies restricted Lemma F. -/
theorem lemmaFr_of_lemmaF (h : LemmaF m) : LemmaFr m := fun Q hQ _ j => h Q hQ j

/-- The rows of the polar factor move by a rank-one term (as in `NearAxis.near_identity`). -/
theorem polar_row_le {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (i : Fin m) :
    rowL1 (polarQ c x M) i ≤ rowL1 M i + (1 - c) / sq2 x * |x i| * l1 r := by
  have ha : 0 ≤ (1 - c) / sq2 x := div_nonneg (sub_nonneg.mpr (block_c_le_one h hc)) (sq2_nonneg x)
  unfold rowL1 l1
  rw [Finset.mul_sum, ← Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro j _
  rw [polarQ_entry h hc]
  simpa [abs_mul, abs_of_nonneg ha] using abs_sub (M i j) ((1 - c) / sq2 x * x i * r j)

/-- `(1 - c)/‖x‖² = 1/(1 + c) ≤ 1`. -/
theorem coef_le_one {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (hx : 0 < sq2 x) : (1 - c) / sq2 x ≤ 1 := by
  rw [div_le_one hx]
  have h1 := h.col1
  have h2 := block_c_le_one h hc
  nlinarith

/-- **The near-axis step in every dimension.** Restricted Lemma F in dimension `m` gives `F_1(R) ≤ 1` for every
orthogonal `R = [c r; x M]` of size `m + 1` whose rows have ℓ¹ norm at most 2, as soon as `c > 0` and the rest of
its row has `‖r‖₁ ≤ 1`. -/
theorem near_step (hF : LemmaFr m) {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (hr : l1 r ≤ 1) (hrows : ∀ i, |x i| + rowL1 M i ≤ 2) :
    F1 c r x M ≤ 1 := by
  rcases (sq2_nonneg x).eq_or_lt with hx | hx
  · have hx0 : sq2 x = 0 := hx.symm
    have hc1 : c = 1 := by nlinarith [h.col1, block_c_le_one h hc]
    have hr0 : sq2 r = 0 := by rw [hc1] at h; nlinarith [h.row1]
    have hxv := eq_zero_of_sq2_eq_zero hx0
    have hrv := eq_zero_of_sq2_eq_zero hr0
    norm_num [F1, hc1, hxv, hrv, l1]
  · have hQ := polarQ_orth h hc hx
    have hQr : ∀ i, rowL1 (polarQ c x M) i ≤ 2 := fun i => by
      have h1 := polar_row_le h hc i
      have ha := coef_le_one h hc hx
      have ha0 : 0 ≤ (1 - c) / sq2 x := div_nonneg (sub_nonneg.mpr (block_c_le_one h hc)) hx.le
      have hl := l1_nonneg r
      have hal : (1 - c) / sq2 x * l1 r ≤ 1 := by nlinarith
      have hxa : (1 - c) / sq2 x * |x i| * l1 r ≤ |x i| := by
        have := mul_le_mul_of_nonneg_left hal (abs_nonneg (x i))
        linarith [show (1 - c) / sq2 x * |x i| * l1 r = |x i| * ((1 - c) / sq2 x * l1 r) by ring]
      linarith [hrows i]
    have hk := lemmaK x hQ hQr (hF _ hQ hQr)
    have hy : l1 ((polarQ c x M)ᵀ *ᵥ x) ≤ 1 := by
      rw [polarQ_transpose_x h hc hx, l1_neg]; exact hr
    have hp : 0 ≤ 2 * (1 - c) * (1 - l1 ((polarQ c x M)ᵀ *ᵥ x)) :=
      mul_nonneg (mul_nonneg (by norm_num) (sub_nonneg.mpr (block_c_le_one h hc))) (sub_nonneg.mpr hy)
    linarith [near_identity h hc hx]

/-- The near step at an entry `R i₀ j ≠ 0` of an orthogonal `(m+1) × (m+1)` matrix with rows of ℓ¹ norm at most 2,
when the rest of row `i₀` has ℓ¹ norm at most 1. -/
theorem step_at (hF : LemmaFr m) (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (hw : ∀ i, rowL1 R i ≤ 2) (i₀ j : Fin (m + 1)) (hne : R i₀ j ≠ 0)
    (hrest : rowL1 R i₀ - |R i₀ j| ≤ 1) : Fcol R j ≤ 1 := by
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have hB := LemmaF4.block_orth R hR hR' i₀ j
  rw [LemmaF4.Fcol_eq_F1 R i₀ j]
  have hr : l1 (fun k => R i₀ (j.succAbove k)) ≤ 1 := by
    have := LemmaF4.rowL1_split R i₀ j
    simp only [l1]; linarith
  have hrows : ∀ i, |R (i₀.succAbove i) j| +
      rowL1 (fun i k => R (i₀.succAbove i) (j.succAbove k)) i ≤ 2 := by
    intro i
    have h1 := LemmaF4.rowL1_split R (i₀.succAbove i) j
    have h2 := hw (i₀.succAbove i)
    simp only [rowL1, l1] at h1 h2 ⊢
    linarith
  rcases lt_or_gt_of_ne hne with hneg | hpos
  · -- flip the sign of the corner and of the rest of its row
    have hB' : BlockOrth (-R i₀ j) (-fun k => R i₀ (j.succAbove k)) (fun i => R (i₀.succAbove i) j)
        (fun i k => R (i₀.succAbove i) (j.succAbove k)) :=
      { col1 := by rw [neg_sq]; exact hB.col1
        row1 := by
          have := hB.row1
          simp only [sq2, Pi.neg_apply, neg_sq] at this ⊢
          exact this
        col1_perp := fun k => by
          have := hB.col1_perp k
          simp only [Pi.neg_apply]
          linarith
        rows := hB.rows }
    have hr' : l1 (-fun k => R i₀ (j.succAbove k)) ≤ 1 := by rw [l1_neg]; exact hr
    have := near_step hF hB' (by linarith) hr' hrows
    simpa [F1, l1, abs_neg] using this
  · exact near_step hF hB hpos hr hrows

/-- **The remaining case.** If every row meeting column `j` has `‖row i‖₁ > 1 + |Rᵢⱼ|`, then
`F_j(R) ≤ ‖column j‖₁ - 1` (for any matrix whose column `j` is a unit vector). -/
theorem remaining_bound {d : ℕ} (R : Matrix (Fin d) (Fin d) ℝ) (j : Fin d)
    (hcol : ∑ i, R i j ^ 2 = 1) (hrem : ∀ i, R i j ≠ 0 → 1 < rowL1 R i - |R i j|) :
    Fcol R j ≤ (∑ i, |R i j|) - 1 := by
  have hterm : ∀ i, |R i j| * (2 - rowL1 R i) ≤ |R i j| - R i j ^ 2 := by
    intro i
    by_cases h0 : R i j = 0
    · simp [h0]
    · have h1 := hrem i h0
      have h2 : 0 ≤ |R i j| := abs_nonneg _
      have h3 : |R i j| * (2 - rowL1 R i) ≤ |R i j| * (1 - |R i j|) :=
        mul_le_mul_of_nonneg_left (by linarith) h2
      nlinarith [sq_abs (R i j)]
  calc Fcol R j = ∑ i, |R i j| * (2 - rowL1 R i) := rfl
    _ ≤ ∑ i, (|R i j| - R i j ^ 2) := Finset.sum_le_sum fun i _ => hterm i
    _ = (∑ i, |R i j|) - 1 := by rw [Finset.sum_sub_distrib, hcol]

/-- `‖column‖₁ ≤ 2` for a unit column in dimension at most 4. -/
theorem col_l1_le_two {d : ℕ} (hd : d ≤ 4) (v : Fin d → ℝ) (hv : ∑ i, v i ^ 2 = 1) :
    ∑ i, |v i| ≤ 2 := by
  have h := l1_sq_le v
  simp only [l1, sq2] at h
  rw [hv] at h
  have hd' : (d : ℝ) ≤ 4 := by exact_mod_cast hd
  have h0 : 0 ≤ ∑ i, |v i| := Finset.sum_nonneg fun i _ => abs_nonneg _
  nlinarith

/-- The remaining case of the induction in dimension `d`, as a hypothesis. -/
def RemainingCase (d : ℕ) : Prop :=
  ∀ R : Matrix (Fin d) (Fin d) ℝ, R * Rᵀ = 1 → (∀ i, rowL1 R i ≤ 2) → ∀ j,
    (∀ i, R i j ≠ 0 → 1 < rowL1 R i - |R i j|) → 2 < ∑ i, |R i j| → Fcol R j ≤ 1

theorem col_sq {d : ℕ} (R : Matrix (Fin d) (Fin d) ℝ) (hR : R * Rᵀ = 1) (j : Fin d) :
    ∑ i, R i j ^ 2 = 1 := by
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have h := congrFun (congrFun hR' j) j
  simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply_eq] at h
  simpa [pow_two] using h

/-- **The induction step.** Restricted Lemma F in dimension `m`, together with the remaining case in dimension
`m + 1`, gives restricted Lemma F in dimension `m + 1`. -/
theorem lemmaFr_succ (hF : LemmaFr m) (hrem : RemainingCase (m + 1)) : LemmaFr (m + 1) := by
  intro R hR hw j
  by_cases hgood : ∃ i₀, R i₀ j ≠ 0 ∧ rowL1 R i₀ - |R i₀ j| ≤ 1
  · obtain ⟨i₀, hne, hrest⟩ := hgood
    exact step_at hF R hR hw i₀ j hne hrest
  · simp only [not_exists, not_and, not_le] at hgood
    by_cases hS : 2 < ∑ i, |R i j|
    · exact hrem R hR hw j hgood hS
    · have := remaining_bound R j (col_sq R hR j) hgood
      linarith

theorem remainingCase_le_four {d : ℕ} (hd : d ≤ 4) : RemainingCase d :=
  fun R hR _ j _ hS => absurd (col_l1_le_two hd (fun i => R i j) (col_sq R hR j)) (not_le.mpr hS)

theorem lemmaFr_zero : LemmaFr 0 := fun _ _ _ j => j.elim0

/-- **Restricted Lemma F for `d ≤ 4`**, from the all-dimension near step and the bound `F ≤ ‖column‖₁ - 1`. -/
theorem lemmaFr_le_four : ∀ d, d ≤ 4 → LemmaFr d
  | 0, _ => lemmaFr_zero
  | n + 1, hd => lemmaFr_succ (lemmaFr_le_four n (by omega)) (remainingCase_le_four hd)

/-! ## The cube centre lemma for `d ≤ 4` -/

open scoped Pointwise

/-- **The cube centre lemma for `d ≤ 4`, from restricted Lemma F.** A unit `d`-cube placed by any rigid motion inside
the cube `[0, s]^d`, `s < 2`, contains `(s/2, …, s/2)` in its interior. -/
theorem centre_le_four {d : ℕ} (hd : d ≤ 4) (s : ℝ) (hs0 : 0 ≤ s) (hs : s < 2)
    (g : EuclideanSpace ℝ (Fin d) ≃ᵃⁱ[ℝ] EuclideanSpace ℝ (Fin d)) (hg : g '' cube d ⊆ s • cube d) :
    (s / 2) • WithLp.toLp 2 (fun _ => (1 : ℝ)) ∈ interior (g '' cube d) :=
  CentreGeneral.centre_of_lemmaF_rows (lemmaFr_le_four d hd) s hs0 hs g hg

end PackingOptimality.Restricted
