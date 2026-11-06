import PackingOptimality.PrismCube

/-!
# Prisms over a polygon with an inscribed circle, in a cube

`pprism nx ny ρ L` is the prism of height `L` over the polygon `{(u, v) | nxₖ u + nyₖ v ≤ ρ}` with unit normals
`(nxₖ, nyₖ)`: every regular polygon, with `ρ` its inradius. The disc of radius `ρ` lies in the polygon, which
is all the width argument needs (`pwidth`).

**Octagonal prisms of height 1** (`pr8incub_n02`): side `1 + √2`, already for one prism. Some coordinate of the
axis has `aᵢ² ≤ 1/3`; the width along it is at least `2ρ √(1 - aᵢ²) + |aᵢ| ≥ 2ρ` as long as
`|aᵢ| ≤ 4ρ/(4ρ² + 1)`, which for `ρ = (1 + √2)/2` is exactly `1/√2`. Two prisms stacked along an axis fit.
-/

namespace PackingOptimality.PrismCube

open Set CentreGeneral OctInCube
open scoped Pointwise RealInnerProductSpace

variable {m : ℕ}

noncomputable def pprism (nx ny : Fin m → ℝ) (ρ L : ℝ) : Set P3 :=
  {y | (∀ k, nx k * y 0 + ny k * y 1 ≤ ρ) ∧ |y 2| ≤ L / 2}

theorem pdot_le {nx ny : Fin m → ℝ} (hn : ∀ k, nx k ^ 2 + ny k ^ 2 = 1) (k : Fin m) (u v : ℝ) :
    nx k * u + ny k * v ≤ Real.sqrt (u ^ 2 + v ^ 2) := by
  have h : (nx k * u + ny k * v) ^ 2 ≤ u ^ 2 + v ^ 2 := by
    nlinarith [hn k, sq_nonneg (nx k * v - ny k * u)]
  exact (le_abs_self _).trans (Real.abs_le_sqrt h)

theorem pdisk_mem {nx ny : Fin m → ℝ} (hn : ∀ k, nx k ^ 2 + ny k ^ 2 = 1) {ρ L : ℝ} (hρ : 0 ≤ ρ) (u v z : ℝ)
    (hz : |z| ≤ L / 2) :
    pt (ρ * u / Real.sqrt (u ^ 2 + v ^ 2)) (ρ * v / Real.sqrt (u ^ 2 + v ^ 2)) z ∈ pprism nx ny ρ L := by
  refine ⟨fun k => ?_, by simpa using hz⟩
  simp only [pt_zero, pt_one]
  rcases (Real.sqrt_nonneg (u ^ 2 + v ^ 2)).eq_or_lt with h0 | hpos
  · rw [← h0]; simp; exact hρ
  · have hd := pdot_le hn k u v
    have e : nx k * (ρ * u / Real.sqrt (u ^ 2 + v ^ 2)) + ny k * (ρ * v / Real.sqrt (u ^ 2 + v ^ 2)) =
        ρ / Real.sqrt (u ^ 2 + v ^ 2) * (nx k * u + ny k * v) := by field_simp
    rw [e]
    calc ρ / Real.sqrt (u ^ 2 + v ^ 2) * (nx k * u + ny k * v)
        ≤ ρ / Real.sqrt (u ^ 2 + v ^ 2) * Real.sqrt (u ^ 2 + v ^ 2) :=
          mul_le_mul_of_nonneg_left hd (div_nonneg hρ hpos.le)
      _ = ρ := by rw [div_mul_cancel₀ _ hpos.ne']

/-- Width of the prism along axis `i`: `2 ρ Uᵢ + L |aᵢ| ≤ s`. -/
theorem pwidth {nx ny : Fin m → ℝ} (hn : ∀ k, nx k ^ 2 + ny k ^ 2 = 1) {ρ L s : ℝ} (hρ : 0 ≤ ρ) (hL : 0 ≤ L)
    (hs : 0 ≤ s) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' pprism nx ny ρ L ⊆ s • cubeC) (i : Fin 3) :
    2 * ρ * U g i + L * |M g i 2| ≤ s := by
  have hz : |sgn (M g i 2) * (L / 2)| ≤ L / 2 := by
    rw [abs_mul, show |sgn (M g i 2)| = 1 by unfold sgn; split_ifs <;> norm_num, abs_of_nonneg (by linarith)]
    ring_nf; rfl
  have hz' : |-(sgn (M g i 2) * (L / 2))| ≤ L / 2 := by rw [abs_neg]; exact hz
  have p1 := pdisk_mem hn hρ (M g i 0) (M g i 1) _ hz
  have p2 := pdisk_mem hn hρ (-M g i 0) (-M g i 1) _ hz'
  have w := width_le hs g hg p1 p2 i
  simp only [pt_zero, pt_one, pt_two] at w
  have e1 : Real.sqrt ((-M g i 0) ^ 2 + (-M g i 1) ^ 2) = U g i := by rw [neg_sq, neg_sq]; rfl
  rw [e1, show Real.sqrt (M g i 0 ^ 2 + M g i 1 ^ 2) = U g i from rfl] at w
  have hq : (M g i 0 ^ 2 + M g i 1 ^ 2) / U g i = U g i := sq_div_sqrt _ _
  have e2 : M g i 0 * (ρ * M g i 0 / U g i - ρ * -M g i 0 / U g i) + M g i 1 * (ρ * M g i 1 / U g i - ρ * -M g i 1 / U g i) =
      2 * ρ * ((M g i 0 ^ 2 + M g i 1 ^ 2) / U g i) := by ring
  rw [e2, hq] at w
  have hsm := sgn_mul (M g i 2)
  nlinarith

/-- Stacked prisms: translates along the axis. -/
theorem pstack_inside {nx ny : Fin m → ℝ} {ρ L s z : ℝ} (hs : 0 < s) (hx : ∀ y : P3, y ∈ pprism nx ny ρ L → |y 0| ≤ s / 2)
    (hy : ∀ y : P3, y ∈ pprism nx ny ρ L → |y 1| ≤ s / 2) (hz : |z| + L / 2 ≤ s / 2) :
    tz z '' pprism nx ny ρ L ⊆ s • cubeC := by
  rintro _ ⟨y, hyK, rfl⟩
  apply mem_smul_of_coord hs
  intro i
  fin_cases i
  · simpa [tz_apply] using hx y hyK
  · simpa [tz_apply] using hy y hyK
  · simp only [tz_apply, Fin.reduceFinMk, PiLp.add_apply, pt_two]
    calc |z + y 2| ≤ |z| + |y 2| := abs_add_le _ _
      _ ≤ s / 2 := by linarith [hyK.2]

noncomputable def pstackPacking {nx ny : Fin m → ℝ} (ρ L s : ℝ) {n : ℕ} (z : Fin n → ℝ) (hs : 0 < s)
    (hx : ∀ y : P3, y ∈ pprism nx ny ρ L → |y 0| ≤ s / 2) (hy : ∀ y : P3, y ∈ pprism nx ny ρ L → |y 1| ≤ s / 2)
    (hz : ∀ i, |z i| + L / 2 ≤ s / 2) (hsep : ∀ i j, i < j → z i + L / 2 ≤ z j - L / 2) :
    Packing (pprism nx ny ρ L) cubeC s n :=
  Packing.of_separators (fun i => tz (z i)) (fun i => pstack_inside hs hx hy (hz i))
    (fun _ _ => EuclideanSpace.proj 2) (fun _ _ _ => proj_surjective 2) (fun i _ => z i + L / 2)
    (fun i j _ y hy => by
      have := (abs_le.mp hy.2).2
      show (pt 0 0 (z i) + y) 2 ≤ z i + L / 2
      simp only [PiLp.add_apply, pt_two]; linarith)
    (fun i j hij y hy => by
      have := (abs_le.mp hy.2).1
      have := hsep i j hij
      show z i + L / 2 ≤ (pt 0 0 (z j) + y) 2
      simp only [PiLp.add_apply, pt_two]; linarith)

/-! ## The regular octagonal prism -/

noncomputable def ρ8 : ℝ := (1 + Real.sqrt 2) / 2

noncomputable def ox : Fin 8 → ℝ := ![1, Real.sqrt 2 / 2, 0, -(Real.sqrt 2 / 2), -1, -(Real.sqrt 2 / 2), 0, Real.sqrt 2 / 2]
noncomputable def oy : Fin 8 → ℝ := ![0, Real.sqrt 2 / 2, 1, Real.sqrt 2 / 2, 0, -(Real.sqrt 2 / 2), -1, -(Real.sqrt 2 / 2)]

theorem s2sq : Real.sqrt 2 * Real.sqrt 2 = 2 := Real.mul_self_sqrt (by norm_num)

theorem o_unit (k : Fin 8) : ox k ^ 2 + oy k ^ 2 = 1 := by
  fin_cases k <;> simp [ox, oy] <;> nlinarith [s2sq]

theorem ρ8_pos : 0 < ρ8 := by unfold ρ8; positivity
theorem ρ8_sq : 4 * ρ8 ^ 2 = 3 + 2 * Real.sqrt 2 := by unfold ρ8; nlinarith [s2sq]
theorem two_ρ8 : 2 * ρ8 = 1 + Real.sqrt 2 := by unfold ρ8; ring
theorem s2b : 1.414 < Real.sqrt 2 ∧ Real.sqrt 2 < 1.4143 := by
  constructor
  · rw [show (1.414 : ℝ) = Real.sqrt (1.414 ^ 2) by rw [Real.sqrt_sq (by norm_num)]]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  · rw [show (1.4143 : ℝ) = Real.sqrt (1.4143 ^ 2) by rw [Real.sqrt_sq (by norm_num)]]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)

/-- One octagonal prism of height 1 needs a cube of side `1 + √2`. -/
theorem no_fit_o1 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2 * ρ8) (g : P3 ≃ᵃⁱ[ℝ] P3)
    (hg : g '' pprism ox oy ρ8 1 ⊆ s • cubeC) : False := by
  have c2 := col2 g
  have hex : ∃ i, M g i 2 ^ 2 ≤ 1 / 3 := by
    by_contra h; push Not at h; nlinarith [h 0, h 1, h 2]
  obtain ⟨i, hi⟩ := hex
  have w := pwidth o_unit ρ8_pos.le (by norm_num) hs g hg i
  have hU := U_sq g i
  have hU0 := U_nonneg g i
  have hr := ρ8_pos
  have hr2 := ρ8_sq
  have hb := s2b
  rw [← sq_abs (M g i 2)] at hU hi
  have h := width_contra (c := 1) hr (abs_nonneg _) hU0 hU (by linarith)
  have ht : |M g i 2| ≤ 58 / 100 := by nlinarith [abs_nonneg (M g i 2)]
  have h3 : 0 < 4 * ρ8 * 1 - |M g i 2| * (4 * ρ8 ^ 2 + 1 ^ 2) := by
    rw [hr2]; unfold ρ8; nlinarith [abs_nonneg (M g i 2)]
  nlinarith [mul_nonneg (abs_nonneg (M g i 2)) h3.le]

theorem o_box {y : P3} (hy : y ∈ pprism ox oy ρ8 1) : |y 0| ≤ (1 + Real.sqrt 2) / 2 ∧ |y 1| ≤ (1 + Real.sqrt 2) / 2 := by
  have h0 := hy.1 0; have h2 := hy.1 2; have h4 := hy.1 4; have h6 := hy.1 6
  simp [ox, oy] at h0 h2 h4 h6
  unfold ρ8 at h0 h2 h4 h6
  exact ⟨abs_le.mpr ⟨by linarith, by linarith⟩, abs_le.mpr ⟨by linarith, by linarith⟩⟩

/-- **Two octagonal prisms of height 1 in a cube: side `1 + √2` is optimal** (one prism already needs it). -/
theorem pr8incub_n02 : Nonempty (Packing (pprism ox oy ρ8 1) cubeC (1 + Real.sqrt 2) 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (pprism ox oy ρ8 1) cubeC s 2 → 1 + Real.sqrt 2 ≤ s := by
  have hb := s2b
  refine ⟨⟨pstackPacking ρ8 1 (1 + Real.sqrt 2) ![-1 / 2, 1 / 2] (by positivity)
    (fun y hy => (o_box hy).1) (fun y hy => (o_box hy).2)
    (fun i => by fin_cases i <;> simp <;> norm_num <;> linarith)
    (fun i j hij => by fin_cases i <;> fin_cases j <;> simp at hij ⊢ <;> norm_num)⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  rw [← two_ρ8] at h
  exact no_fit_o1 hs h (P.g 0) (P.inside 0)

end PackingOptimality.PrismCube
