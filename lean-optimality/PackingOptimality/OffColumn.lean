import PackingOptimality.LemmaFr

/-!
# Restricted Lemma F: the off-column step

The near-axis step (`Restricted.near_step`) pivots at an entry of the column `j` whose `F` is being bounded. This file
adds a second reduction that pivots **outside** column `j`.

Write `R = [c r; x M]` with the pivot `c = R p q > 0` at row `p` and a column `q ≠ j`, and let `Q` be the polar factor
of the minor `M` (`NearAxis.polarQ`). Column `j` of `R` survives in `Q`: its entries move to
`Q i j = M i j - x i * r j / (1 + c)`. Then (`offcol_step`)

`F_j(R) ≤ F_j(Q)`

provided the rows of `R` have ℓ¹ norm at most 2 and

* the pivot is large: `‖r‖₂² ≤ 1/4`, that is `c² ≥ 3/4`;
* `‖r‖₁ ≤ 1 + c` (automatic when row `p` has ℓ¹ norm at most 2 and `c ≥ 1/2`);
* the entry `r j` of row `p` in column `j` is small compared with the other entries of column `j`:
  `|r j| ≤ 2 (1 + c - ‖r‖₁) |M i j|` for every row `i` with `x i * M i j * r j > 0`.

With restricted Lemma F in dimension `m` this gives `F_j(R) ≤ 1`. The typical use (`offcol_at`): `p` is a row where
column `j` is smallest, and row `p` has an entry of size at least `√3/2` outside column `j`.

The proof is a term-by-term comparison (`term_bound`) together with the orthogonality of columns `q` and `j`,
`c r_j + Σᵢ xᵢ Mᵢⱼ = 0`.
-/

namespace PackingOptimality.Restricted

open NearAxis Matrix

variable {m : ℕ}

/-- `F` of the column `j` of `R = [c r; x M]` that passes through `r j` and `M · j`. -/
noncomputable def Gcol (c : ℝ) (r x : Fin m → ℝ) (M : Matrix (Fin m) (Fin m) ℝ) (j : Fin m) : ℝ :=
  |r j| * (2 - |c| - l1 r) + ∑ i, |M i j| * (2 - |x i| - rowL1 M i)

lemma sq2_le_l1_sq (v : Fin m → ℝ) : sq2 v ≤ l1 v ^ 2 := by
  have h := Finset.sum_sq_le_sq_sum_of_nonneg (s := Finset.univ) (f := fun i => |v i|)
    (fun i _ => abs_nonneg (v i))
  simpa [sq2, l1, sq_abs] using h

/-- A row of an orthogonal matrix has ℓ¹ norm at least 1. -/
lemma one_le_rowL1 {Q : Matrix (Fin m) (Fin m) ℝ} (hQ : Q * Qᵀ = 1) (i : Fin m) : 1 ≤ rowL1 Q i := by
  have h1 : sq2 (Q i) = 1 := by
    have := congrFun (congrFun hQ i) i
    simpa [Matrix.mul_apply, sq2, pow_two] using this
  have h2 := sq2_le_l1_sq (Q i)
  have h3 := l1_nonneg (Q i)
  unfold rowL1
  nlinarith

/-- The term-by-term comparison behind the off-column step, for one row `i`.
Here `y = M i j`, `x = x i`, `ρ = r j`, `a = 1/(1+c)`, `κ = 1 - a ‖r‖₁`, `w = ‖Q i‖₁`, `mM = ‖M i‖₁`,
and `ε = ±1` is the sign of `ρ`. -/
lemma term_bound (x y ρ a κ w mM L ε : ℝ) (hε : ε = 1 ∨ ε = -1) (hερ : 0 ≤ ε * ρ) (ha : 0 ≤ a)
    (hκ : κ = 1 - a * L) (hκ0 : 0 ≤ κ) (hw1 : 1 ≤ w) (hw2 : w ≤ 2) (hm : w ≤ mM + a * |x| * L)
    (hmin : 0 < x * y * ρ → a * |ρ| ≤ 2 * κ * |y|) :
    |y| * (2 - |x| - mM) ≤ |y - a * x * ρ| * (2 - w) + κ * (x * y * ε) := by
  have hεε : ε * ε = 1 := by rcases hε with h | h <;> simp [h]
  have hερ' : ε * ρ = |ρ| := by
    rcases hε with h | h
    · subst h; rw [one_mul] at hερ ⊢; exact (abs_of_nonneg hερ).symm
    · subst h; rw [neg_one_mul] at hερ ⊢; rw [abs_of_nonpos (by linarith)]
  have hy := abs_nonneg y
  have hxa := abs_nonneg x
  -- step 1: replace ‖M i‖₁ by ‖Q i‖₁
  have h1 : |y| * (2 - |x| - mM) ≤ |y| * (2 - w) - κ * (|x| * |y|) := by
    have : |y| * (2 - |x| - mM) ≤ |y| * (2 - |x| - (w - a * |x| * L)) :=
      mul_le_mul_of_nonneg_left (by linarith) hy
    rw [hκ]; nlinarith
  -- step 2: compare |y| with |Q i j| = |y - a x ρ|
  have h2 : (|y| - |y - a * x * ρ|) * (2 - w) ≤ κ * (|x| * |y| + x * y * ε) := by
    rcases le_or_gt (x * y * ε) 0 with hs | hs
    · -- y and -a x ρ have the same sign, so |Q i j| ≥ |y|
      have hprod : 0 ≤ y * (-(a * x * ρ)) := by
        have : y * (-(a * x * ρ)) = -a * (x * y * ε) * (ε * ρ) := by
          linear_combination (a * x * y * ρ) * hεε
        rw [this]
        have := mul_nonneg (mul_nonneg ha (neg_nonneg.mpr hs)) hερ
        linarith
      have hge : |y| ≤ |y - a * x * ρ| :=
        sq_le_sq.mp (by nlinarith [hprod, sq_nonneg (a * x * ρ)])
      have hxy : 0 ≤ |x| * |y| + x * y * ε := by
        have : |x * y * ε| = |x| * |y| := by
          rw [abs_mul, abs_mul]; rcases hε with h | h <;> simp [h]
        have := neg_abs_le (x * y * ε)
        linarith
      have : (|y| - |y - a * x * ρ|) * (2 - w) ≤ 0 :=
        mul_nonpos_of_nonpos_of_nonneg (by linarith) (by linarith)
      linarith [mul_nonneg hκ0 hxy]
    · -- x y ε > 0, so |x| |y| = x y ε
      have hxy : |x| * |y| = x * y * ε := by
        rw [← abs_mul]
        have : x * y = (x * y * ε) * ε := by linear_combination (-(x * y)) * hεε
        rw [this, abs_mul, abs_of_pos hs]
        rcases hε with h | h <;> simp [h]
      have htri : |y| - |y - a * x * ρ| ≤ a * |x| * |ρ| := by
        have := abs_sub_abs_le_abs_sub y (y - a * x * ρ)
        have h' : |y - (y - a * x * ρ)| = a * |x| * |ρ| := by
          rw [show y - (y - a * x * ρ) = a * x * ρ by ring, abs_mul, abs_mul, abs_of_nonneg ha]
        linarith
      have hmin' : a * |ρ| ≤ 2 * κ * |y| := by
        rcases eq_or_lt_of_le (abs_nonneg ρ) with h0 | h0
        · rw [← h0, mul_zero]; exact mul_nonneg (mul_nonneg (by norm_num) hκ0) hy
        · apply hmin
          have : x * y * ρ = (x * y * ε) * (ε * ρ) := by linear_combination (-(x * y * ρ)) * hεε
          rw [this, hερ']; exact mul_pos hs h0
      have hpos : 0 ≤ a * |x| * |ρ| := mul_nonneg (mul_nonneg ha hxa) (abs_nonneg ρ)
      have h3 : (|y| - |y - a * x * ρ|) * (2 - w) ≤ a * |x| * |ρ| := by
        rcases le_total (|y| - |y - a * x * ρ|) 0 with hn | hn
        · nlinarith
        · nlinarith
      have h4 : a * |x| * |ρ| ≤ 2 * κ * (|x| * |y|) := by
        have := mul_le_mul_of_nonneg_left hmin' hxa
        nlinarith
      rw [← hxy]; linarith
  nlinarith

/-- **The off-column step** (block form). `R = [c r; x M]` is orthogonal with the pivot `c > 0` outside column `j`,
the rows of `R` other than the pivot row have ℓ¹ norm at most 2, `‖r‖₁ ≤ 1 + c`, `‖r‖₂² ≤ 1/4`, and `|r j|` is
at most `2 (1 + c - ‖r‖₁) |M i j|` whenever `x i M i j r j > 0`. Then restricted Lemma F in dimension `m` gives
`F_j(R) ≤ 1`. -/
theorem offcol_step (hF : LemmaFr m) {c : ℝ} {r x : Fin m → ℝ} {M : Matrix (Fin m) (Fin m) ℝ}
    (h : BlockOrth c r x M) (hc : 0 < c) (j : Fin m) (hrows : ∀ i, |x i| + rowL1 M i ≤ 2)
    (hrc : l1 r ≤ 1 + c) (hr2 : 4 * sq2 r ≤ 1)
    (hmin : ∀ i, 0 < x i * M i j * r j → |r j| ≤ 2 * (1 + c - l1 r) * |M i j|) :
    Gcol c r x M j ≤ 1 := by
  have hc1 := block_c_le_one h hc
  rcases (sq2_nonneg x).eq_or_lt with hx | hx
  · -- c = 1: then x = 0, r = 0 and M itself is orthogonal
    have hx0 : sq2 x = 0 := hx.symm
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
  · set a := (1 - c) / sq2 x with ha_def
    have ha1 : a * (1 + c) = 1 := by
      rw [ha_def, div_mul_eq_mul_div, div_eq_one_iff_eq (ne_of_gt hx)]
      nlinarith [h.col1]
    have ha0 : 0 ≤ a := div_nonneg (sub_nonneg.mpr hc1) hx.le
    set L := l1 r with hL
    have hL0 : 0 ≤ L := l1_nonneg r
    have haL : a * L ≤ 1 := by nlinarith
    set κ := 1 - a * L with hκ
    have hκ0 : 0 ≤ κ := by linarith
    set Q := polarQ c x M with hQdef
    have hQ : Q * Qᵀ = 1 := polarQ_orth h hc hx
    have hQr : ∀ i, rowL1 Q i ≤ 2 := fun i => by
      have h1 := polar_row_le h hc i
      have hxa : a * |x i| * L ≤ |x i| := by
        have := mul_le_mul_of_nonneg_left haL (abs_nonneg (x i))
        linarith [show a * |x i| * L = |x i| * (a * L) by ring]
      linarith [hrows i]
    have hFQ : Fcol Q j ≤ 1 := hF Q hQ hQr j
    have hQe : ∀ i, Q i j = M i j - a * x i * r j := fun i => polarQ_entry h hc i j
    -- the sign of r j
    obtain ⟨ε, hε, hερ⟩ : ∃ ε : ℝ, (ε = 1 ∨ ε = -1) ∧ 0 ≤ ε * r j := by
      rcases le_total 0 (r j) with h0 | h0
      · exact ⟨1, Or.inl rfl, by linarith⟩
      · exact ⟨-1, Or.inr rfl, by linarith⟩
    have hερ' : ε * r j = |r j| := by
      rcases hε with h' | h'
      · subst h'; rw [one_mul] at hερ ⊢; exact (abs_of_nonneg hερ).symm
      · subst h'; rw [neg_one_mul] at hερ ⊢; rw [abs_of_nonpos (by linarith)]
    have hterm : ∀ i, |M i j| * (2 - |x i| - rowL1 M i) ≤
        |Q i j| * (2 - rowL1 Q i) + κ * (x i * M i j * ε) := by
      intro i
      rw [hQe i]
      refine term_bound (x i) (M i j) (r j) a κ (rowL1 Q i) (rowL1 M i) L ε hε hερ ha0 rfl hκ0
        (one_le_rowL1 hQ i) (hQr i) ?_ ?_
      · have := polar_row_le h hc i
        linarith
      · intro hp
        have h1 := hmin i hp
        have h2 : a * (2 * (1 + c - L)) = 2 * κ := by
          rw [hκ]; linear_combination 2 * ha1
        calc a * |r j| ≤ a * (2 * (1 + c - L) * |M i j|) := mul_le_mul_of_nonneg_left h1 ha0
          _ = 2 * κ * |M i j| := by rw [← h2]; ring
    have hsum : ∑ i, |M i j| * (2 - |x i| - rowL1 M i) ≤ Fcol Q j + κ * ε * (∑ i, x i * M i j) := by
      calc ∑ i, |M i j| * (2 - |x i| - rowL1 M i)
          ≤ ∑ i, (|Q i j| * (2 - rowL1 Q i) + κ * (x i * M i j * ε)) :=
            Finset.sum_le_sum fun i _ => hterm i
        _ = Fcol Q j + κ * ε * (∑ i, x i * M i j) := by
            rw [Finset.sum_add_distrib, Finset.mul_sum]
            congr 1
            apply Finset.sum_congr rfl; intro i _; ring
    have horth : ∑ i, x i * M i j = -(c * r j) := by linarith [h.col1_perp j]
    rw [horth] at hsum
    -- the pivot row: ‖r‖₁ ≥ 2 ‖r‖₂² = 2 (1 - c²)
    have hLs : 2 * sq2 r ≤ L := by
      have h1 := sq2_le_l1_sq r
      have h2 := sq2_nonneg r
      rw [← hL] at h1
      nlinarith
    have hrow1 := h.row1
    have hpiv : |r j| * (2 - |c| - L) - κ * c * |r j| ≤ 0 := by
      rw [abs_of_pos hc]
      have hk : 2 - c - L - κ * c = 2 * (1 - c) - a * L := by
        rw [hκ]
        have : a * c = 1 - a := by linarith
        linear_combination L * this
      have hge : 2 * (1 - c) ≤ a * L := by
        have h3 : 2 * (1 - c) * (1 + c) ≤ L := by nlinarith
        have h4 : 2 * (1 - c) = a * (2 * (1 - c) * (1 + c)) := by linear_combination (-(2 * (1 - c))) * ha1
        rw [h4]; exact mul_le_mul_of_nonneg_left h3 ha0
      have : |r j| * (2 - c - L) - κ * c * |r j| = |r j| * (2 - c - L - κ * c) := by ring
      rw [this, hk]
      exact mul_nonpos_of_nonneg_of_nonpos (abs_nonneg _) (by linarith)
    have hκε : κ * ε * -(c * r j) = -(κ * c * |r j|) := by rw [← hερ']; ring
    unfold Gcol
    rw [hκε] at hsum
    linarith

/-- Column `j = q.succAbove j'` of `R`, written in the blocks of the pivot `(p, q)`. -/
theorem Fcol_eq_Gcol (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (p q : Fin (m + 1)) (j : Fin m) :
    Fcol R (q.succAbove j) = Gcol (R p q) (fun k => R p (q.succAbove k)) (fun i => R (p.succAbove i) q)
      (fun i k => R (p.succAbove i) (q.succAbove k)) j := by
  unfold Fcol Gcol
  rw [Fin.sum_univ_succAbove _ p]
  simp only [LemmaF4.rowL1_split R _ q]
  simp only [l1, rowL1]
  ring_nf

/-- **The off-column step for matrices.** Let `R` be orthogonal of size `m + 1` with rows of ℓ¹ norm at most 2, let
`p` be a row where column `j` is smallest in absolute value, and let `q ≠ j` be a column with `R p q ^ 2 ≥ 3/4`.
Then restricted Lemma F in dimension `m` gives `F_j(R) ≤ 1`. -/
theorem offcol_at (hF : LemmaFr m) (R : Matrix (Fin (m + 1)) (Fin (m + 1)) ℝ) (hR : R * Rᵀ = 1)
    (hw : ∀ i, rowL1 R i ≤ 2) (p q j : Fin (m + 1)) (hqj : q ≠ j) (hc : 3 / 4 ≤ R p q ^ 2)
    (hmin : ∀ i, |R p j| ≤ |R i j|) : Fcol R j ≤ 1 := by
  obtain ⟨j', rfl⟩ := Fin.exists_succAbove_eq hqj.symm
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have hB := LemmaF4.block_orth R hR hR' p q
  rw [Fcol_eq_Gcol R p q j']
  have hsplit := LemmaF4.rowL1_split R p q
  have hrowp : |R p q| + l1 (fun k => R p (q.succAbove k)) ≤ 2 := by
    have := hw p; simp only [rowL1, l1] at hsplit this ⊢; linarith
  have hrows : ∀ i, |R (p.succAbove i) q| + rowL1 (fun i k => R (p.succAbove i) (q.succAbove k)) i ≤ 2 := by
    intro i
    have h1 := LemmaF4.rowL1_split R (p.succAbove i) q
    have h2 := hw (p.succAbove i)
    simp only [rowL1, l1] at h1 h2 ⊢
    linarith
  have hc34 : 3 / 4 ≤ |R p q| := by nlinarith [sq_abs (R p q), abs_nonneg (R p q)]
  have hr2 : 4 * sq2 (fun k => R p (q.succAbove k)) ≤ 1 := by have := hB.row1; nlinarith
  have hrc : l1 (fun k => R p (q.succAbove k)) ≤ 1 + |R p q| := by linarith
  have hmin' : ∀ i, |R p (q.succAbove j')| ≤
      2 * (1 + |R p q| - l1 (fun k => R p (q.succAbove k))) * |R (p.succAbove i) (q.succAbove j')| := by
    intro i
    have h1 := hmin (p.succAbove i)
    have h2 : 1 ≤ 2 * (1 + |R p q| - l1 (fun k => R p (q.succAbove k))) := by linarith
    calc |R p (q.succAbove j')| ≤ |R (p.succAbove i) (q.succAbove j')| := h1
      _ ≤ _ := le_mul_of_one_le_left (abs_nonneg _) h2
  have hne : R p q ≠ 0 := by
    intro h0; rw [h0] at hc; norm_num at hc
  rcases lt_or_gt_of_ne hne with hneg | hpos
  · have hB' : BlockOrth (-R p q) (-fun k => R p (q.succAbove k)) (fun i => R (p.succAbove i) q)
        (fun i k => R (p.succAbove i) (q.succAbove k)) :=
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
    have habs : |R p q| = -R p q := abs_of_neg hneg
    have := offcol_step hF hB' (by linarith) j' hrows
      (by rw [l1_neg]; linarith)
      (by simpa [sq2, neg_sq] using hr2)
      (fun i _ => by simpa [l1_neg, habs] using hmin' i)
    simpa [Gcol, l1_neg, abs_neg] using this
  · have habs : |R p q| = R p q := abs_of_pos hpos
    exact offcol_step hF hB hpos j' hrows (by linarith) hr2
      (fun i _ => by simpa [habs] using hmin' i)

/-- The case left by the near step, the off-column step at a smallest row, and `‖column j‖₁ ≤ 2`. -/
def RemainingCase2 (d : ℕ) : Prop :=
  ∀ R : Matrix (Fin d) (Fin d) ℝ, R * Rᵀ = 1 → (∀ i, rowL1 R i ≤ 2) → ∀ j,
    (∀ i, R i j ≠ 0 → 1 < rowL1 R i - |R i j|) → 2 < ∑ i, |R i j| →
    (∀ p, (∀ i, |R p j| ≤ |R i j|) → ∀ q, q ≠ j → R p q ^ 2 < 3 / 4) → Fcol R j ≤ 1

/-- **The induction step with both reductions.** Restricted Lemma F in dimension `m`, together with
`RemainingCase2 (m + 1)`, gives restricted Lemma F in dimension `m + 1`. -/
theorem lemmaFr_succ2 (hF : LemmaFr m) (hrem : RemainingCase2 (m + 1)) : LemmaFr (m + 1) := by
  apply lemmaFr_succ hF
  intro R hR hw j hgood hS
  by_cases hoff : ∃ p q, (∀ i, |R p j| ≤ |R i j|) ∧ q ≠ j ∧ 3 / 4 ≤ R p q ^ 2
  · obtain ⟨p, q, hmin, hqj, hc⟩ := hoff
    exact offcol_at hF R hR hw p q j hqj hc hmin
  · refine hrem R hR hw j hgood hS fun p hp q hqj => ?_
    by_contra hc
    exact hoff ⟨p, q, hp, hqj, not_lt.mp hc⟩

end PackingOptimality.Restricted
