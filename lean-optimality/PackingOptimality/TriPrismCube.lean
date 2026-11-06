import PackingOptimality.PrismCube

/-!
# Triangular prisms in a cube

`tprism L` is the triangular prism with unit equilateral base (vertices `(0,0)`, `(0,1)`, `(√3/2, 1/2)` in the
first two coordinates) and lateral edges of length `L` along the third axis.

* **Height 3/2** (`pr3l15incub_n02`, `pr3l15incub_n03`): side `3/2`, already for one prism. Some coordinate of the
  axis has `aᵢ² ≥ 1/3`. Along that axis the prism spans `w + (3/2)|aᵢ|`, where `w` is the width of the base
  in the projected direction. Six vertex differences of the triangle lie at 60° steps, so `w ≥ (√3/2)√(1 - aᵢ²)`
  (`six_dirs`); and `(√3/2)√(1 - t²) + (3/2) t ≥ 3/2` for `t ≥ 1/2`. Three prisms fit at exactly `3/2`: their
  bases form a pinwheel of three unit triangles in a square of side `3/2`, each touching the other two.
* **Height 2** (`pr3l2incub_n02` … `pr3l2incub_n06`): side 2 for every `n` from 2 to 6. The widths give
  `|aᵢ| < 13/19` for every coordinate (`lt_13_19`). The box lemma then holds for the caps (`‖a‖₁ ≤ √3 < 2`) and for the three
  sides, where it reduces to `Σᵢ |bᵢ| (1 - |aᵢ|) ≤ √3/2` for unit `b ⊥ a` (`key3`). That inequality follows from
  Cauchy–Schwarz after adding a multiple of `Σ aᵢ bᵢ = 0`, with `Σᵢ |aᵢ| ≥ 115/71` and a sign argument.
  Six prisms fit at side exactly 2: in each half of the cube, three prisms whose bases form a strip of
  alternating triangles, along `y` in one half and along `z` in the other.
-/

namespace PackingOptimality.PrismCube

open Set CentreGeneral OctInCube
open scoped Pointwise RealInnerProductSpace

noncomputable def tprism (L : ℝ) : Set P3 :=
  {y | 0 ≤ y 0 ∧ y 0 ≤ Real.sqrt 3 * y 1 ∧ y 0 ≤ Real.sqrt 3 * (1 - y 1) ∧ |y 2| ≤ L / 2}

theorem s3 : Real.sqrt 3 * Real.sqrt 3 = 3 := sqrt3_sq
theorem s3p : 0 < Real.sqrt 3 := sqrt3_pos
theorem s3b : 1.732 < Real.sqrt 3 ∧ Real.sqrt 3 < 1.7321 := by
  constructor
  · rw [show (1.732 : ℝ) = Real.sqrt (1.732 ^ 2) by rw [Real.sqrt_sq (by norm_num)]]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  · rw [show (1.7321 : ℝ) = Real.sqrt (1.7321 ^ 2) by rw [Real.sqrt_sq (by norm_num)]]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)

theorem tmem {L a b z : ℝ} (h0 : 0 ≤ a) (h1 : a ≤ Real.sqrt 3 * b) (h2 : a ≤ Real.sqrt 3 * (1 - b))
    (hz : |z| ≤ L / 2) : pt a b z ∈ tprism L := by
  simp only [tprism, mem_setOf_eq, pt_zero, pt_one, pt_two]; exact ⟨h0, h1, h2, hz⟩

/-- The three base vertices are in the triangle. -/
theorem v0 {L z : ℝ} (hz : |z| ≤ L / 2) : pt 0 0 z ∈ tprism L := tmem le_rfl (by simp) (by simp [s3p.le]) hz
theorem v1 {L z : ℝ} (hz : |z| ≤ L / 2) : pt 0 1 z ∈ tprism L := tmem le_rfl (by simp [s3p.le]) (by simp) hz
theorem v2 {L z : ℝ} (hz : |z| ≤ L / 2) : pt (Real.sqrt 3 / 2) (1 / 2) z ∈ tprism L :=
  tmem (by positivity) (by linarith [s3p]) (by linarith [s3p]) hz

theorem le_of_sq_lt {x y : ℝ} (hx : 0 ≤ x) (h : y ^ 2 < x ^ 2) : y ≤ x := by
  by_contra hh; push Not at hh; nlinarith [mul_self_le_mul_self hx hh.le]

theorem sq3 (u : ℝ) : (Real.sqrt 3 * u) ^ 2 = 3 * u ^ 2 := by
  rw [mul_pow, Real.sq_sqrt (by norm_num)]

/-- **Six directions.** For every `(u₀, u₁)` some difference of two base vertices `d` has `⟨u, d⟩ ≥ 0` and
`⟨u, d⟩² ≥ (3/4)|u|²`. -/
theorem six_dirs (u0 u1 : ℝ) : ∃ p0 p1 q0 q1 : ℝ, (p0, p1) ∈ ({(0, 0), (0, 1), (Real.sqrt 3 / 2, 1 / 2)} : Set (ℝ × ℝ)) ∧
    (q0, q1) ∈ ({(0, 0), (0, 1), (Real.sqrt 3 / 2, 1 / 2)} : Set (ℝ × ℝ)) ∧
    0 ≤ u0 * (p0 - q0) + u1 * (p1 - q1) ∧ 3 / 4 * (u0 ^ 2 + u1 ^ 2) ≤ (u0 * (p0 - q0) + u1 * (p1 - q1)) ^ 2 := by
  have h3 := s3; have hp := s3p
  rcases le_or_gt (3 * u0 ^ 2) (u1 ^ 2) with ha | ha
  · rcases le_or_gt 0 u1 with hb | hb
    · exact ⟨0, 1, 0, 0, by simp, by simp, by simp; linarith, by simp; nlinarith⟩
    · exact ⟨0, 0, 0, 1, by simp, by simp, by simp; linarith, by simp; nlinarith⟩
  · rcases le_or_gt 0 u0 with hc | hc <;> rcases le_or_gt 0 u1 with hb | hb
    · have hl : u1 ≤ Real.sqrt 3 * u0 := le_of_sq_lt (by positivity) (by rw [sq3]; linarith)
      exact ⟨Real.sqrt 3 / 2, 1 / 2, 0, 0, by simp, by simp, by simp; nlinarith, by simp; nlinarith⟩
    · have hl : -u1 ≤ Real.sqrt 3 * u0 := le_of_sq_lt (by positivity) (by rw [sq3, neg_sq]; linarith)
      exact ⟨Real.sqrt 3 / 2, 1 / 2, 0, 1, by simp, by simp, by simp; nlinarith, by simp; nlinarith⟩
    · have hl : u1 ≤ -(Real.sqrt 3 * u0) := le_of_sq_lt (by nlinarith) (by rw [neg_sq, sq3]; linarith)
      exact ⟨0, 1, Real.sqrt 3 / 2, 1 / 2, by simp, by simp, by simp; nlinarith, by simp; nlinarith⟩
    · have hl : -u1 ≤ -(Real.sqrt 3 * u0) := le_of_sq_lt (by nlinarith) (by rw [neg_sq, neg_sq, sq3]; linarith)
      exact ⟨0, 0, Real.sqrt 3 / 2, 1 / 2, by simp, by simp, by simp; nlinarith, by simp; nlinarith⟩

theorem base_mem {L p0 p1 z : ℝ} (hp : (p0, p1) ∈ ({(0, 0), (0, 1), (Real.sqrt 3 / 2, 1 / 2)} : Set (ℝ × ℝ)))
    (hz : |z| ≤ L / 2) : pt p0 p1 z ∈ tprism L := by
  simp only [Set.mem_insert_iff, Set.mem_singleton_iff, Prod.mk.injEq] at hp
  rcases hp with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
  · exact v0 hz
  · exact v1 hz
  · exact v2 hz

/-- **Width of the triangular prism along axis `i`.** -/
theorem twidth {L s : ℝ} (hL : 0 ≤ L) (hs : 0 ≤ s) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' tprism L ⊆ s • cubeC) (i : Fin 3) :
    ∃ w, 0 ≤ w ∧ 3 / 4 * (1 - M g i 2 ^ 2) ≤ w ^ 2 ∧ w + L * |M g i 2| ≤ s := by
  obtain ⟨p0, p1, q0, q1, hp, hq, hw0, hw⟩ := six_dirs (M g i 0) (M g i 1)
  have hz : |sgn (M g i 2) * (L / 2)| ≤ L / 2 := by
    rw [abs_mul, show |sgn (M g i 2)| = 1 by unfold sgn; split_ifs <;> norm_num, abs_of_nonneg (by linarith)]
    ring_nf; rfl
  have hz' : |-(sgn (M g i 2) * (L / 2))| ≤ L / 2 := by rw [abs_neg]; exact hz
  have w := width_le hs g hg (base_mem hp hz) (base_mem hq hz') i
  simp only [pt_zero, pt_one, pt_two] at w
  have hr := rows g i i; simp at hr
  refine ⟨_, hw0, ?_, ?_⟩
  · nlinarith
  · have hsm := sgn_mul (M g i 2)
    nlinarith

/-- `w + c t < c` with `w ≥ 0`, `w² ≥ (3/4)(1 - t²)` gives `(1 - t)((3/4)(1 + t) - c² (1 - t)) < 0`. -/
theorem tri_contra {t w c : ℝ} (hw0 : 0 ≤ w) (hw : 3 / 4 * (1 - t ^ 2) ≤ w ^ 2) (h : w + c * t < c) :
    (1 - t) * (3 / 4 * (1 + t) - c ^ 2 * (1 - t)) < 0 := by
  have h2 : w ^ 2 < (c - c * t) ^ 2 := pow_lt_pow_left₀ (by linarith) hw0 (by norm_num)
  have e : (1 - t) * (3 / 4 * (1 + t) - c ^ 2 * (1 - t)) = 3 / 4 * (1 - t ^ 2) - (c - c * t) ^ 2 := by ring
  rw [e]; linarith

/-! ## Height 3/2: one prism needs side 3/2 -/

theorem no_fit_t15 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 3 / 2) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' tprism (3 / 2) ⊆ s • cubeC) :
    False := by
  have c2 := col2 g
  have hex : ∃ i, 1 / 3 ≤ M g i 2 ^ 2 := by
    by_contra h; push Not at h; nlinarith [h 0, h 1, h 2]
  obtain ⟨i, hi⟩ := hex
  obtain ⟨w, hw0, hw, hws⟩ := twidth (by norm_num) hs g hg i
  rw [← sq_abs (M g i 2)] at hw hi
  have ht1 : |M g i 2| ≤ 1 := by
    have := rows g i i; simp at this; rw [abs_le]; constructor <;> nlinarith
  have h := tri_contra (c := 3 / 2) hw0 hw (by linarith)
  have hhalf : 1 / 2 < |M g i 2| := by nlinarith [abs_nonneg (M g i 2)]
  nlinarith [mul_nonneg (by linarith : (0 : ℝ) ≤ 1 - |M g i 2|) (by linarith : (0 : ℝ) ≤ 3 * |M g i 2| - 3 / 2)]

/-! ## Height 2: side 2 -/

theorem lt_13_19 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' tprism 2 ⊆ s • cubeC) (i : Fin 3) :
    |M g i 2| < 13 / 19 := by
  obtain ⟨w, hw0, hw, hws⟩ := twidth (by norm_num) hs g hg i
  rw [← sq_abs (M g i 2)] at hw
  have h := tri_contra (c := 2) hw0 hw (by linarith)
  have ht1 : |M g i 2| < 1 := by nlinarith
  nlinarith [abs_nonneg (M g i 2)]

/-- Cauchy–Schwarz in three variables. -/
theorem cs3 (x0 x1 x2 t0 t1 t2 : ℝ) :
    (x0 * t0 + x1 * t1 + x2 * t2) ^ 2 ≤ (x0 ^ 2 + x1 ^ 2 + x2 ^ 2) * (t0 ^ 2 + t1 ^ 2 + t2 ^ 2) := by
  have e : (x0 ^ 2 + x1 ^ 2 + x2 ^ 2) * (t0 ^ 2 + t1 ^ 2 + t2 ^ 2) - (x0 * t0 + x1 * t1 + x2 * t2) ^ 2 =
      (x0 * t1 - x1 * t0) ^ 2 + (x0 * t2 - x2 * t0) ^ 2 + (x1 * t2 - x2 * t1) ^ 2 := by ring
  nlinarith [sq_nonneg (x0 * t1 - x1 * t0), sq_nonneg (x0 * t2 - x2 * t0), sq_nonneg (x1 * t2 - x2 * t1)]

/-- Mixed signs: `|± f₀ ± f₁ ± f₂| ≥ 1/8` when every `fᵢ ∈ [3/16, 1/4]` and the signs are not all equal. -/
theorem mixed (f0 f1 f2 e0 e1 e2 : ℝ) (l0 : 3 / 16 ≤ f0) (l1 : 3 / 16 ≤ f1) (l2 : 3 / 16 ≤ f2)
    (u0 : f0 ≤ 1 / 4) (u1 : f1 ≤ 1 / 4) (u2 : f2 ≤ 1 / 4)
    (he0 : e0 = 1 ∨ e0 = -1) (he1 : e1 = 1 ∨ e1 = -1) (he2 : e2 = 1 ∨ e2 = -1)
    (hp : ¬ (e0 = 1 ∧ e1 = 1 ∧ e2 = 1)) (hm : ¬ (e0 = -1 ∧ e1 = -1 ∧ e2 = -1)) :
    1 / 64 ≤ (e0 * f0 + e1 * f1 + e2 * f2) ^ 2 := by
  rcases he0 with rfl | rfl <;> rcases he1 with rfl | rfl <;> rcases he2 with rfl | rfl <;>
    simp at hp hm <;> nlinarith

theorem f_lo (α : ℝ) (l : 1 / 4 ≤ α) (u : α ≤ 13 / 19) : 3 / 16 ≤ α - α ^ 2 := by nlinarith
theorem f_hi (α : ℝ) : α - α ^ 2 ≤ 1 / 4 := by nlinarith [sq_nonneg (α - 1 / 2)]
theorem sum_lo (α0 α1 α2 : ℝ) (hα : α0 ^ 2 + α1 ^ 2 + α2 ^ 2 = 1)
    (l0 : 1 / 4 ≤ α0) (l1 : 1 / 4 ≤ α1) (l2 : 1 / 4 ≤ α2) (u0 : α0 ≤ 13 / 19) (u1 : α1 ≤ 13 / 19)
    (u2 : α2 ≤ 13 / 19) : 115 / 71 ≤ α0 + α1 + α2 := by
  nlinarith [mul_nonneg (by linarith : (0 : ℝ) ≤ α0 - 1 / 4) (by linarith : (0 : ℝ) ≤ 13 / 19 - α0),
    mul_nonneg (by linarith : (0 : ℝ) ≤ α1 - 1 / 4) (by linarith : (0 : ℝ) ≤ 13 / 19 - α1),
    mul_nonneg (by linarith : (0 : ℝ) ≤ α2 - 1 / 4) (by linarith : (0 : ℝ) ≤ 13 / 19 - α2)]

theorem le_sqrt3_half {X : ℝ} (h0 : 0 ≤ X) (h : X ^ 2 ≤ 3 / 4) : X ≤ Real.sqrt 3 / 2 := by
  have h3 : (Real.sqrt 3 / 2) ^ 2 = 3 / 4 := by rw [div_pow, Real.sq_sqrt (by norm_num)]; norm_num
  by_contra hh; push Not at hh
  have : (Real.sqrt 3 / 2) ^ 2 < X ^ 2 := pow_lt_pow_left₀ hh (by positivity) (by norm_num)
  linarith

/-- The core of the side inequality. -/
theorem key3core (α0 α1 α2 t0 t1 t2 e0 e1 e2 : ℝ) (hα : α0 ^ 2 + α1 ^ 2 + α2 ^ 2 = 1)
    (l0 : 1 / 4 ≤ α0) (l1 : 1 / 4 ≤ α1) (l2 : 1 / 4 ≤ α2) (u0 : α0 ≤ 13 / 19) (u1 : α1 ≤ 13 / 19) (u2 : α2 ≤ 13 / 19)
    (ht0 : 0 ≤ t0) (ht1 : 0 ≤ t1) (ht2 : 0 ≤ t2) (ht : t0 ^ 2 + t1 ^ 2 + t2 ^ 2 = 1)
    (he0 : e0 = 1 ∨ e0 = -1) (he1 : e1 = 1 ∨ e1 = -1) (he2 : e2 = 1 ∨ e2 = -1)
    (horth : e0 * α0 * t0 + e1 * α1 * t1 + e2 * α2 * t2 = 0) :
    (1 - α0) * t0 + (1 - α1) * t1 + (1 - α2) * t2 ≤ Real.sqrt 3 / 2 := by
  obtain ⟨P, hP⟩ : ∃ P, P = e0 * (α0 - α0 ^ 2) + e1 * (α1 - α1 ^ 2) + e2 * (α2 - α2 ^ 2) := ⟨_, rfl⟩
  obtain ⟨X, hX⟩ : ∃ X, X = (1 - α0) * t0 + (1 - α1) * t1 + (1 - α2) * t2 := ⟨_, rfl⟩
  rw [← hX]
  have hX0 : 0 ≤ X := by
    have := mul_nonneg (by linarith : (0 : ℝ) ≤ 1 - α0) ht0
    have := mul_nonneg (by linarith : (0 : ℝ) ≤ 1 - α1) ht1
    have := mul_nonneg (by linarith : (0 : ℝ) ≤ 1 - α2) ht2
    linarith
  have ee0 : e0 ^ 2 = 1 := by rcases he0 with rfl | rfl <;> norm_num
  have ee1 : e1 ^ 2 = 1 := by rcases he1 with rfl | rfl <;> norm_num
  have ee2 : e2 ^ 2 = 1 := by rcases he2 with rfl | rfl <;> norm_num
  -- Cauchy–Schwarz with `xᵢ = (1 - αᵢ) - P eᵢ αᵢ`
  have hXx : X = ((1 - α0) - P * e0 * α0) * t0 + ((1 - α1) - P * e1 * α1) * t1 + ((1 - α2) - P * e2 * α2) * t2 := by
    rw [hX]; linear_combination P * horth
  have hcs := cs3 ((1 - α0) - P * e0 * α0) ((1 - α1) - P * e1 * α1) ((1 - α2) - P * e2 * α2) t0 t1 t2
  rw [← hXx, ht, mul_one] at hcs
  have hxx : ((1 - α0) - P * e0 * α0) ^ 2 + ((1 - α1) - P * e1 * α1) ^ 2 + ((1 - α2) - P * e2 * α2) ^ 2 =
      4 - 2 * (α0 + α1 + α2) - P ^ 2 := by
    linear_combination (2 * P) * hP + P ^ 2 * α0 ^ 2 * ee0 + P ^ 2 * α1 ^ 2 * ee1 + P ^ 2 * α2 ^ 2 * ee2 +
      (P ^ 2 + 1) * hα
  rw [hxx] at hcs
  -- `Σ αᵢ ≥ 115/71`
  have hS := sum_lo α0 α1 α2 hα l0 l1 l2 u0 u1 u2
  have f0 := f_lo α0 l0 u0; have f1 := f_lo α1 l1 u1; have f2 := f_lo α2 l2 u2
  have g0 := f_hi α0; have g1 := f_hi α1; have g2 := f_hi α2
  have tpos : 0 < α0 * t0 + α1 * t1 + α2 * t2 := by
    by_contra h; push Not at h
    have a0 := mul_nonneg (by linarith : (0 : ℝ) ≤ α0) ht0
    have a1 := mul_nonneg (by linarith : (0 : ℝ) ≤ α1) ht1
    have a2 := mul_nonneg (by linarith : (0 : ℝ) ≤ α2) ht2
    have z0 : α0 * t0 = 0 := by linarith
    have z1 : α1 * t1 = 0 := by linarith
    have z2 : α2 * t2 = 0 := by linarith
    have : t0 = 0 := by
      rcases mul_eq_zero.mp z0 with h | h
      · linarith
      · exact h
    have : t1 = 0 := by
      rcases mul_eq_zero.mp z1 with h | h
      · linarith
      · exact h
    have : t2 = 0 := by
      rcases mul_eq_zero.mp z2 with h | h
      · linarith
      · exact h
    subst_vars; norm_num at ht
  have hp : ¬ (e0 = 1 ∧ e1 = 1 ∧ e2 = 1) := by
    rintro ⟨rfl, rfl, rfl⟩; linarith
  have hm : ¬ (e0 = -1 ∧ e1 = -1 ∧ e2 = -1) := by
    rintro ⟨rfl, rfl, rfl⟩; linarith
  have hP2 := mixed _ _ _ e0 e1 e2 f0 f1 f2 g0 g1 g2 he0 he1 he2 hp hm
  rw [← hP] at hP2
  have hX2 : X ^ 2 ≤ 3 / 4 := by linarith
  exact le_sqrt3_half hX0 hX2

/-- `x = sgn x · |x|`. -/
theorem sgn_abs (x : ℝ) : sgn x * |x| = x := by
  unfold sgn; split_ifs with h
  · rw [abs_of_nonneg h]; ring
  · rw [abs_of_neg (not_le.mp h)]; ring

theorem sgn_cases (x : ℝ) : sgn x = 1 ∨ sgn x = -1 := by unfold sgn; split_ifs <;> simp

/-- **The side inequality** for unit `b ⊥ a` with `|aᵢ| < 13/19`. -/
theorem key3 (a b : Fin 3 → ℝ) (ha : a 0 ^ 2 + a 1 ^ 2 + a 2 ^ 2 = 1) (hb : b 0 ^ 2 + b 1 ^ 2 + b 2 ^ 2 = 1)
    (hab : a 0 * b 0 + a 1 * b 1 + a 2 * b 2 = 0) (h : ∀ i, |a i| < 13 / 19) :
    |b 0| + |b 1| + |b 2| ≤ Real.sqrt 3 / 2 + (|a 0| * |b 0| + |a 1| * |b 1| + |a 2| * |b 2|) := by
  have sa : ∀ i, |a i| ^ 2 = a i ^ 2 := fun i => sq_abs _
  have sb : ∀ i, |b i| ^ 2 = b i ^ 2 := fun i => sq_abs _
  have q : ∀ j, a j ^ 2 < (13 / 19) ^ 2 := fun j => by
    have := h j; rw [← sa]; nlinarith [abs_nonneg (a j)]
  have q0 := q 0; have q1 := q 1; have q2 := q 2
  have l16 : 1 / 16 ≤ a 0 ^ 2 ∧ 1 / 16 ≤ a 1 ^ 2 ∧ 1 / 16 ≤ a 2 ^ 2 :=
    ⟨by nlinarith, by nlinarith, by nlinarith⟩
  have hl : ∀ i, 1 / 4 ≤ |a i| := by
    intro i
    have : 1 / 16 ≤ |a i| ^ 2 := by
      rw [sa]; fin_cases i
      · exact l16.1
      · exact l16.2.1
      · exact l16.2.2
    nlinarith [abs_nonneg (a i)]
  have hor : (sgn (a 0) * sgn (b 0)) * |a 0| * |b 0| + (sgn (a 1) * sgn (b 1)) * |a 1| * |b 1| +
      (sgn (a 2) * sgn (b 2)) * |a 2| * |b 2| = 0 := by
    have e : ∀ i, (sgn (a i) * sgn (b i)) * |a i| * |b i| = a i * b i := fun i => by
      rw [← sgn_abs (a i), ← sgn_abs (b i)]
      rw [show sgn (sgn (a i) * |a i|) = sgn (a i) by rw [sgn_abs], show sgn (sgn (b i) * |b i|) = sgn (b i) by
        rw [sgn_abs], abs_mul, abs_mul]
      rcases sgn_cases (a i) with h1 | h1 <;> rcases sgn_cases (b i) with h2 | h2 <;> rw [h1, h2] <;> simp
    rw [e 0, e 1, e 2]; exact hab
  have hcase : ∀ x y : ℝ, (sgn x * sgn y = 1) ∨ (sgn x * sgn y = -1) := fun x y => by
    rcases sgn_cases x with h1 | h1 <;> rcases sgn_cases y with h2 | h2 <;> rw [h1, h2] <;> norm_num
  have k := key3core (|a 0|) (|a 1|) (|a 2|) (|b 0|) (|b 1|) (|b 2|) _ _ _ (by rw [sa, sa, sa]; exact ha)
    (hl 0) (hl 1) (hl 2) (h 0).le (h 1).le (h 2).le (abs_nonneg _) (abs_nonneg _) (abs_nonneg _)
    (by rw [sb, sb, sb]; exact hb) (hcase _ _) (hcase _ _) (hcase _ _) hor
  linarith

/-- Facets: `inl 0, 1, 2` the sides, `inr true/false` the caps. -/
noncomputable def tβ : Fin 3 ⊕ Bool → P3
  | Sum.inl 0 => pt (-1) 0 0
  | Sum.inl 1 => pt (1 / 2) (-(Real.sqrt 3 / 2)) 0
  | Sum.inl 2 => pt (1 / 2) (Real.sqrt 3 / 2) 0
  | Sum.inr true => pt 0 0 1
  | Sum.inr false => pt 0 0 (-1)

noncomputable def th (L : ℝ) : Fin 3 ⊕ Bool → ℝ
  | Sum.inl 0 => 0
  | Sum.inl 1 => 0
  | Sum.inl 2 => Real.sqrt 3 / 2
  | Sum.inr _ => L / 2

/-- The vertex opposite each side. -/
noncomputable def topp : Fin 3 → ℝ × ℝ
  | 0 => (Real.sqrt 3 / 2, 1 / 2)
  | 1 => (0, 1)
  | 2 => (0, 0)

theorem tK (L : ℝ) : ∀ y : P3, (∀ f, ⟪tβ f, y⟫ < th L f) → y ∈ tprism L := by
  intro y hy
  have h0 := hy (Sum.inl 0); have h1 := hy (Sum.inl 1); have h2 := hy (Sum.inl 2)
  have h3 := hy (Sum.inr true); have h4 := hy (Sum.inr false)
  simp only [tβ, th, inner_pt] at h0 h1 h2 h3 h4
  refine ⟨by linarith, by linarith, by linarith, ?_⟩
  rw [abs_le]; constructor <;> linarith

theorem topp_mem {L z : ℝ} (j : Fin 3) (hz : |z| ≤ L / 2) : pt (topp j).1 (topp j).2 z ∈ tprism L := by
  fin_cases j
  · exact v2 hz
  · exact v1 hz
  · exact v0 hz

/-- The side normal `(β₀, β₁)` of side `j` and the gap `h - ⟨β, opposite vertex⟩ = √3/2`. -/
theorem side_data (j : Fin 3) : ∃ c d : ℝ, tβ (Sum.inl j) = pt c d 0 ∧ c ^ 2 + d ^ 2 = 1 ∧
    c * (topp j).1 + d * (topp j).2 = th 2 (Sum.inl j) - Real.sqrt 3 / 2 := by
  fin_cases j
  · exact ⟨-1, 0, rfl, by norm_num, by simp [topp, th]⟩
  · exact ⟨1 / 2, -(Real.sqrt 3 / 2), rfl, by nlinarith [s3], by simp [topp, th]⟩
  · exact ⟨1 / 2, Real.sqrt 3 / 2, rfl, by nlinarith [s3], by simp [topp, th]⟩

set_option maxHeartbeats 1000000 in
theorem side_t2 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' tprism 2 ⊆ s • cubeC) (j : Fin 3) :
    ∃ v : Fin 3 → P3, (∀ i, v i ∈ tprism 2) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (tβ (Sum.inl j)) i| +
        ∑ i, g.linearIsometryEquiv (tβ (Sum.inl j)) i * g.linearIsometryEquiv (v i) i < th 2 (Sum.inl j) := by
  obtain ⟨c, d, hβ, hcd, hgap⟩ := side_data j
  set b : Fin 3 → ℝ := fun i => M g i 0 * c + M g i 1 * d with hbdef
  have hLb : ∀ i, g.linearIsometryEquiv (tβ (Sum.inl j)) i = b i := fun i => by
    rw [hβ, lin_coord]; simp [hbdef]
  refine ⟨fun i => pt (topp j).1 (topp j).2 (-(sgn (M g i 2 * b i))), fun i => topp_mem j ?_, ?_⟩
  · rw [abs_neg]; rcases sgn_cases (M g i 2 * b i) with h | h <;> rw [h] <;> norm_num
  simp only [sum3, hLb, lin_coord, pt_zero, pt_one, pt_two]
  have c00 := cols g 0 0; have c11 := cols g 1 1; have c01 := cols g 0 1
  have c02 := cols g 0 2; have c12 := cols g 1 2; have c22 := cols g 2 2
  simp at c00 c11 c01 c02 c12 c22
  have hb1 : b 0 ^ 2 + b 1 ^ 2 + b 2 ^ 2 = 1 := by
    simp only [hbdef]; linear_combination c ^ 2 * c00 + 2 * c * d * c01 + d ^ 2 * c11 + hcd
  have hab : M g 0 2 * b 0 + M g 1 2 * b 1 + M g 2 2 * b 2 = 0 := by
    simp only [hbdef]; linear_combination c * c02 + d * c12
  have ha1 : M g 0 2 ^ 2 + M g 1 2 ^ 2 + M g 2 2 ^ 2 = 1 := by linear_combination c22
  -- the in-plane part sums to `⟨β, opposite vertex⟩`
  have hin : b 0 * (M g 0 0 * (topp j).1 + M g 0 1 * (topp j).2) + b 1 * (M g 1 0 * (topp j).1 + M g 1 1 * (topp j).2) +
      b 2 * (M g 2 0 * (topp j).1 + M g 2 1 * (topp j).2) = c * (topp j).1 + d * (topp j).2 := by
    simp only [hbdef]
    linear_combination (c * (topp j).1) * c00 + (c * (topp j).2 + d * (topp j).1) * c01 + (d * (topp j).2) * c11
  have hz : ∀ i, b i * (M g i 2 * -sgn (M g i 2 * b i)) = -(|M g i 2| * |b i|) := fun i => by
    rw [← abs_mul, ← sgn_mul (M g i 2 * b i)]; ring
  have expand : ∀ i, b i * (M g i 0 * (topp j).1 + M g i 1 * (topp j).2 + M g i 2 * -sgn (M g i 2 * b i)) =
      b i * (M g i 0 * (topp j).1 + M g i 1 * (topp j).2) + b i * (M g i 2 * -sgn (M g i 2 * b i)) := fun i => by ring
  rw [expand 0, expand 1, expand 2, hz 0, hz 1, hz 2]
  have hk := key3 (fun i => M g i 2) b ha1 hb1 hab (fun i => lt_13_19 hs hs2 g hg i)
  have hX0 : 0 < |b 0| + |b 1| + |b 2| := by
    by_contra hh; push Not at hh
    have : |b 0| = 0 := by linarith [abs_nonneg (b 0), abs_nonneg (b 1), abs_nonneg (b 2)]
    have : |b 1| = 0 := by linarith [abs_nonneg (b 0), abs_nonneg (b 1), abs_nonneg (b 2)]
    have : |b 2| = 0 := by linarith [abs_nonneg (b 0), abs_nonneg (b 1), abs_nonneg (b 2)]
    simp_all
  have hlt : s / 2 * (|b 0| + |b 1| + |b 2|) < |b 0| + |b 1| + |b 2| := by nlinarith
  linarith

theorem cap_t2 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2) (g : P3 ≃ᵃⁱ[ℝ] P3) (bb : Bool) :
    ∃ v : Fin 3 → P3, (∀ i, v i ∈ tprism 2) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (tβ (Sum.inr bb)) i| +
        ∑ i, g.linearIsometryEquiv (tβ (Sum.inr bb)) i * g.linearIsometryEquiv (v i) i < th 2 (Sum.inr bb) := by
  have c22 := cols g 2 2; simp at c22
  have hl := l1_sq (M g 0 2) (M g 1 2) (M g 2 2)
  have hX0 : 0 ≤ |M g 0 2| + |M g 1 2| + |M g 2 2| := by positivity
  have hX : |M g 0 2| + |M g 1 2| + |M g 2 2| < 2 := by nlinarith
  have hS : s / 2 * (|M g 0 2| + |M g 1 2| + |M g 2 2|) < 2 := by nlinarith
  cases bb
  · refine ⟨fun _ => pt 0 0 1, fun _ => v0 (by norm_num), ?_⟩
    simp only [sum3, tβ, th, lin_coord, pt_zero, pt_one, pt_two]
    simp only [mul_zero, zero_add, mul_one, mul_neg, abs_neg]
    nlinarith
  · refine ⟨fun _ => pt 0 0 (-1), fun _ => v0 (by norm_num), ?_⟩
    simp only [sum3, tβ, th, lin_coord, pt_zero, pt_one, pt_two]
    simp only [mul_zero, zero_add, mul_one, mul_neg]
    nlinarith

/-- **Centre lemma for the triangular prism of height 2.** Inside a cube of side `s < 2` it contains the centre. -/
theorem centre_t2 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' tprism 2 ⊆ s • cubeC) :
    (0 : P3) ∈ interior (g '' tprism 2) := by
  refine centre_of_box tβ (th 2) (tK 2) hs g hg fun f => ?_
  rcases f with j | bb
  · exact side_t2 hs hs2 g hg j
  · exact cap_t2 hs hs2 g bb


/-! ## Constructions -/

theorem tri_facts {L : ℝ} {y : P3} (hy : y ∈ tprism L) :
    0 ≤ y 0 ∧ y 0 ≤ Real.sqrt 3 * y 1 ∧ y 0 ≤ Real.sqrt 3 * (1 - y 1) ∧ |y 2| ≤ L / 2 ∧
    0 ≤ y 1 ∧ y 1 ≤ 1 ∧ y 0 ≤ Real.sqrt 3 / 2 := by
  obtain ⟨h0, h1, h2, h3⟩ := hy
  have hp := s3p
  refine ⟨h0, h1, h2, h3, ?_, ?_, by linarith⟩
  · by_contra h; push Not at h; nlinarith
  · by_contra h; push Not at h; nlinarith

/-- The linear map with matrix `A`. -/
noncomputable def linM (A : Fin 3 → Fin 3 → ℝ) : P3 →ₗ[ℝ] P3 where
  toFun y := pt (A 0 0 * y 0 + A 0 1 * y 1 + A 0 2 * y 2) (A 1 0 * y 0 + A 1 1 * y 1 + A 1 2 * y 2)
    (A 2 0 * y 0 + A 2 1 * y 1 + A 2 2 * y 2)
  map_add' x y := by ext i; fin_cases i <;> simp <;> ring
  map_smul' r y := by ext i; fin_cases i <;> simp <;> ring

theorem linM_apply (A : Fin 3 → Fin 3 → ℝ) (y : P3) : linM A y =
    pt (A 0 0 * y 0 + A 0 1 * y 1 + A 0 2 * y 2) (A 1 0 * y 0 + A 1 1 * y 1 + A 1 2 * y 2)
      (A 2 0 * y 0 + A 2 1 * y 1 + A 2 2 * y 2) := rfl

/-- `(y₀, y₁, y₂) ↦ (-y₀, y₂, y₁)`, `(y₀, y₂, y₁)`, `(-y₀, y₁, y₂)`, `(y₁, y₀, y₂)` and the identity. -/
def Aa : Fin 3 → Fin 3 → ℝ := ![![-1, 0, 0], ![0, 0, 1], ![0, 1, 0]]
def Ab : Fin 3 → Fin 3 → ℝ := ![![1, 0, 0], ![0, 0, 1], ![0, 1, 0]]
def Ad : Fin 3 → Fin 3 → ℝ := ![![-1, 0, 0], ![0, 1, 0], ![0, 0, 1]]
def As : Fin 3 → Fin 3 → ℝ := ![![0, 1, 0], ![1, 0, 0], ![0, 0, 1]]
def Ai : Fin 3 → Fin 3 → ℝ := ![![1, 0, 0], ![0, 1, 0], ![0, 0, 1]]

theorem inner3' (u y : P3) : ⟪u, y⟫ = u 0 * y 0 + u 1 * y 1 + u 2 * y 2 := by
  rw [CentreGeneral.inner_sum, Fin.sum_univ_three]

theorem orthM (A : Fin 3 → Fin 3 → ℝ) (hA : A = Aa ∨ A = Ab ∨ A = Ad ∨ A = As ∨ A = Ai) :
    ∀ x y : P3, ⟪linM A x, linM A y⟫ = ⟪x, y⟫ := by
  intro x y
  rw [inner3', inner3', linM_apply, linM_apply]
  rcases hA with rfl | rfl | rfl | rfl | rfl <;> simp [Aa, Ab, Ad, As, Ai] <;> ring

/-- A placement: linear part `A`, then translation by `c`. -/
noncomputable def place (A : Fin 3 → Fin 3 → ℝ) (hA : A = Aa ∨ A = Ab ∨ A = Ad ∨ A = As ∨ A = Ai) (c : P3) :
    P3 ≃ᵃⁱ[ℝ] P3 :=
  ((LinearMap.isometryOfInner (linM A) (orthM A hA)).toLinearIsometryEquiv rfl).toAffineIsometryEquiv.trans
    (AffineIsometryEquiv.constVAdd ℝ P3 c)

theorem place_apply (A : Fin 3 → Fin 3 → ℝ) (hA) (c y : P3) : place A hA c y = c + linM A y := rfl

/-- The functional `c₀ x₀ + c₁ x₁ + c₂ x₂`. -/
noncomputable def lf (c0 c1 c2 : ℝ) : P3 →L[ℝ] ℝ :=
  c0 • EuclideanSpace.proj 0 + c1 • EuclideanSpace.proj 1 + c2 • EuclideanSpace.proj 2

theorem lf_apply (c0 c1 c2 : ℝ) (x : P3) : lf c0 c1 c2 x = c0 * x 0 + c1 * x 1 + c2 * x 2 := rfl

theorem lf_surj {c0 c1 c2 : ℝ} (h : c0 ≠ 0 ∨ c1 ≠ 0 ∨ c2 ≠ 0) : Function.Surjective (lf c0 c1 c2) := by
  intro t
  rcases h with h | h | h
  · exact ⟨pt (t / c0) 0 0, by rw [lf_apply]; simp; field_simp⟩
  · exact ⟨pt 0 (t / c1) 0, by rw [lf_apply]; simp; field_simp⟩
  · exact ⟨pt 0 0 (t / c2), by rw [lf_apply]; simp; field_simp⟩

/-! ### Six prisms of height 2 in the cube of side 2 -/

theorem hAa : Aa = Aa ∨ Aa = Ab ∨ Aa = Ad ∨ Aa = As ∨ Aa = Ai := Or.inl rfl
theorem hAb : Ab = Aa ∨ Ab = Ab ∨ Ab = Ad ∨ Ab = As ∨ Ab = Ai := Or.inr (Or.inl rfl)
theorem hAd : Ad = Aa ∨ Ad = Ab ∨ Ad = Ad ∨ Ad = As ∨ Ad = Ai := Or.inr (Or.inr (Or.inl rfl))
theorem hAs : As = Aa ∨ As = Ab ∨ As = Ad ∨ As = As ∨ As = Ai := Or.inr (Or.inr (Or.inr (Or.inl rfl)))
theorem hAi : Ai = Aa ∨ Ai = Ab ∨ Ai = Ad ∨ Ai = As ∨ Ai = Ai := Or.inr (Or.inr (Or.inr (Or.inr rfl)))

/-- Pieces 0–2: along `y` in the half `x ≤ 0`; pieces 3–5: along `z` in the half `x ≥ 0`. -/
noncomputable def g6 : Fin 6 → P3 ≃ᵃⁱ[ℝ] P3 := ![
  place Aa hAa (pt 0 0 (-1)), place Ab hAb (pt (-(Real.sqrt 3 / 2)) 0 (-1 / 2)), place Aa hAa (pt 0 0 0),
  place Ai hAi (pt 0 (-1) 0), place Ad hAd (pt (Real.sqrt 3 / 2) (-1 / 2) 0), place Ai hAi (pt 0 0 0)]

theorem g6_apply (i : Fin 6) (y : P3) : g6 i y = pt
    (![-y 0, y 0 - Real.sqrt 3 / 2, -y 0, y 0, Real.sqrt 3 / 2 - y 0, y 0] i)
    (![y 2, y 2, y 2, y 1 - 1, y 1 - 1 / 2, y 1] i)
    (![y 1 - 1, y 1 - 1 / 2, y 1, y 2, y 2, y 2] i) := by
  ext k
  fin_cases i <;> fin_cases k <;> simp [g6, place_apply, linM_apply, Aa, Ab, Ad, Ai] <;> ring

theorem g6_inside (i : Fin 6) : g6 i '' tprism 2 ⊆ (2 : ℝ) • cubeC := by
  rintro _ ⟨y, hy, rfl⟩
  obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := tri_facts hy
  have hz := abs_le.mp h3
  have hp := s3p; have hb := s3b
  apply mem_smul_of_coord (by norm_num)
  rw [g6_apply]
  intro k
  fin_cases i <;> fin_cases k <;> simp <;> rw [abs_le] <;> constructor <;> norm_num at hz ⊢ <;> linarith

/-- The separating functionals. -/
noncomputable def f6 (i j : Fin 6) : P3 →L[ℝ] ℝ :=
  if i = 0 ∧ j = 1 then lf (-1) 0 (Real.sqrt 3) else
  if i = 0 ∧ j = 2 then lf 0 0 1 else
  if i = 1 ∧ j = 2 then lf 1 0 (Real.sqrt 3) else
  if i = 3 ∧ j = 4 then lf 1 (Real.sqrt 3) 0 else
  if i = 3 ∧ j = 5 then lf 0 1 0 else
  if i = 4 ∧ j = 5 then lf (-1) (Real.sqrt 3) 0 else lf 1 0 0

theorem f6_surj (i j : Fin 6) : Function.Surjective (f6 i j) := by
  unfold f6
  split_ifs <;> apply lf_surj <;> simp

set_option maxHeartbeats 4000000 in
noncomputable def pack6 : Packing (tprism 2) cubeC 2 6 :=
  Packing.of_separators g6 g6_inside f6 (fun i j _ => f6_surj i j) (fun _ _ => 0)
    (fun i j hij y hy => by
      obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := tri_facts hy
      have hz := abs_le.mp h3
      have hp := s3p
      rw [g6_apply]
      fin_cases i <;> fin_cases j <;> simp at hij <;> simp [f6, lf_apply] <;> nlinarith)
    (fun i j hij y hy => by
      obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := tri_facts hy
      have hz := abs_le.mp h3
      have hp := s3p
      rw [g6_apply]
      fin_cases i <;> fin_cases j <;> simp at hij <;> simp [f6, lf_apply] <;> nlinarith)

/-- **Triangular prisms of height 2 in a cube: side 2 is optimal for every `n` from 2 to 6.** -/
theorem pr3l2incub (n : ℕ) (hn2 : 2 ≤ n) (hn6 : n ≤ 6) : Nonempty (Packing (tprism 2) cubeC 2 n) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism 2) cubeC s n → 2 ≤ s := by
  refine ⟨⟨pack6.restrict hn6⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  exact no_packing_two_of_common_point (0 : P3) (fun g hg => centre_t2 hs h g hg) hn2 P

theorem pr3l2incub_n02 : Nonempty (Packing (tprism 2) cubeC 2 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism 2) cubeC s 2 → 2 ≤ s := pr3l2incub 2 le_rfl (by norm_num)
theorem pr3l2incub_n03 : Nonempty (Packing (tprism 2) cubeC 2 3) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism 2) cubeC s 3 → 2 ≤ s := pr3l2incub 3 (by norm_num) (by norm_num)
theorem pr3l2incub_n04 : Nonempty (Packing (tprism 2) cubeC 2 4) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism 2) cubeC s 4 → 2 ≤ s := pr3l2incub 4 (by norm_num) (by norm_num)
theorem pr3l2incub_n05 : Nonempty (Packing (tprism 2) cubeC 2 5) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism 2) cubeC s 5 → 2 ≤ s := pr3l2incub 5 (by norm_num) (by norm_num)
theorem pr3l2incub_n06 : Nonempty (Packing (tprism 2) cubeC 2 6) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism 2) cubeC s 6 → 2 ≤ s := pr3l2incub 6 (by norm_num) le_rfl

/-! ### Three prisms of height 3/2 in the cube of side 3/2: a pinwheel -/

noncomputable def aw : ℝ := (Real.sqrt 3 - 1) / 2

noncomputable def g3 : Fin 3 → P3 ≃ᵃⁱ[ℝ] P3 := ![
  place Ai hAi (pt (-3 / 4) (aw - 3 / 4) 0), place As hAs (pt (aw - 3 / 4) (-3 / 4) 0),
  place Ad hAd (pt (3 / 4) (-1 / 4) 0)]

theorem g3_apply (i : Fin 3) (y : P3) : g3 i y = pt
    (![y 0 - 3 / 4, y 1 + aw - 3 / 4, 3 / 4 - y 0] i) (![y 1 + aw - 3 / 4, y 0 - 3 / 4, y 1 - 1 / 4] i) (y 2) := by
  ext k
  fin_cases i <;> fin_cases k <;> simp [g3, place_apply, linM_apply, Ai, As, Ad] <;> ring

theorem g3_inside (i : Fin 3) : g3 i '' tprism (3 / 2) ⊆ (3 / 2 : ℝ) • cubeC := by
  rintro _ ⟨y, hy, rfl⟩
  obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := tri_facts hy
  have hz := abs_le.mp h3
  have hp := s3p; have hb := s3b
  apply mem_smul_of_coord (by norm_num)
  rw [g3_apply]
  intro k
  fin_cases i <;> fin_cases k <;> simp [aw] <;> rw [abs_le] <;> constructor <;> norm_num at hz ⊢ <;> linarith

noncomputable def f3 (i j : Fin 3) : P3 →L[ℝ] ℝ :=
  if i = 0 ∧ j = 1 then lf (Real.sqrt 3) (-1) 0 else lf 1 (Real.sqrt 3) 0

noncomputable def c3 (i j : Fin 3) : ℝ :=
  if i = 0 ∧ j = 1 then (9 - 5 * Real.sqrt 3) / 4 else (3 - Real.sqrt 3) / 4

theorem f3_surj (i j : Fin 3) : Function.Surjective (f3 i j) := by
  unfold f3; split_ifs
  · exact lf_surj (Or.inl s3p.ne')
  · exact lf_surj (Or.inl (by norm_num))

set_option maxHeartbeats 4000000 in
noncomputable def pack3 : Packing (tprism (3 / 2)) cubeC (3 / 2) 3 :=
  Packing.of_separators g3 g3_inside f3 (fun i j _ => f3_surj i j) c3
    (fun i j hij y hy => by
      obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := tri_facts hy
      have hp := s3p; have h33 := s3
      rw [g3_apply]
      fin_cases i <;> fin_cases j <;> simp at hij <;> simp [f3, c3, lf_apply, aw] <;> nlinarith)
    (fun i j hij y hy => by
      obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := tri_facts hy
      have hp := s3p; have h33 := s3
      rw [g3_apply]
      fin_cases i <;> fin_cases j <;> simp at hij <;> simp [f3, c3, lf_apply, aw] <;> nlinarith)

/-- **Triangular prisms of height 3/2 in a cube: side 3/2 is optimal for `n = 1, 2, 3`.** -/
theorem pr3l15incub (n : ℕ) (hn1 : 1 ≤ n) (hn3 : n ≤ 3) : Nonempty (Packing (tprism (3 / 2)) cubeC (3 / 2) n) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism (3 / 2)) cubeC s n → 3 / 2 ≤ s := by
  refine ⟨⟨pack3.restrict hn3⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  exact no_fit_t15 hs h (P.g ⟨0, hn1⟩) (P.inside _)

theorem pr3l15incub_n02 : Nonempty (Packing (tprism (3 / 2)) cubeC (3 / 2) 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism (3 / 2)) cubeC s 2 → 3 / 2 ≤ s := pr3l15incub 2 (by norm_num) (by norm_num)
theorem pr3l15incub_n03 : Nonempty (Packing (tprism (3 / 2)) cubeC (3 / 2) 3) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (tprism (3 / 2)) cubeC s 3 → 3 / 2 ≤ s := pr3l15incub 3 (by norm_num) le_rfl

end PackingOptimality.PrismCube
