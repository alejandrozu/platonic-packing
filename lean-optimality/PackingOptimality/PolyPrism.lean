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


/-! ## The box lemma for `pprism` -/

noncomputable def pβ (nx ny : Fin m → ℝ) : Fin m ⊕ Bool → P3
  | Sum.inl k => pt (nx k) (ny k) 0
  | Sum.inr true => pt 0 0 1
  | Sum.inr false => pt 0 0 (-1)

noncomputable def ph (ρ L : ℝ) : Fin m ⊕ Bool → ℝ
  | Sum.inl _ => ρ
  | Sum.inr _ => L / 2

theorem pK (nx ny : Fin m → ℝ) (ρ L : ℝ) : ∀ y : P3, (∀ f, ⟪pβ nx ny f, y⟫ < ph ρ L f) → y ∈ pprism nx ny ρ L := by
  intro y hy
  refine ⟨fun k => ?_, ?_⟩
  · have := hy (Sum.inl k); simp only [pβ, ph, inner_pt] at this; linarith
  · have h1 := hy (Sum.inr true); have h2 := hy (Sum.inr false)
    simp only [pβ, ph, inner_pt] at h1 h2
    rw [abs_le]; constructor <;> linarith

/-- The cylinder point of row `i` for `pprism`. -/
noncomputable def ppt (ρ : ℝ) (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) (σ z : ℝ) : P3 :=
  pt (ρ * (σ * M g i 0) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2))
    (ρ * (σ * M g i 1) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) z

theorem row_ppt (ρ : ℝ) (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) {σ : ℝ} (hσ : σ ^ 2 = 1) (z : ℝ) :
    M g i 0 * ppt ρ g i σ z 0 + M g i 1 * ppt ρ g i σ z 1 + M g i 2 * ppt ρ g i σ z 2 = σ * ρ * U g i + M g i 2 * z := by
  simp only [ppt, pt_zero, pt_one, pt_two]
  have e : M g i 0 * (ρ * (σ * M g i 0) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) +
      M g i 1 * (ρ * (σ * M g i 1) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) + M g i 2 * z =
      σ * ρ * ((M g i 0 ^ 2 + M g i 1 ^ 2) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) + M g i 2 * z := by ring
  rw [e, sqrt_sigma _ _ _ hσ, sq_div_sqrt]; rfl

/-- Sides, when `κ √3 ≤ 2ρ` and `s/2 < κ`: `(s/2)‖b‖₁ - ρ Σ |bᵢ| Uᵢ < ρ`. -/
theorem pside {nx ny : Fin m → ℝ} (hn : ∀ k, nx k ^ 2 + ny k ^ 2 = 1) {ρ L s κ : ℝ} (hρ : 0 < ρ) (hL : 0 ≤ L)
    (hsκ : s / 2 < κ) (hκ : 0 ≤ κ) (hκρ : κ ^ 2 * 3 ≤ (2 * ρ) ^ 2) (g : P3 ≃ᵃⁱ[ℝ] P3) (k : Fin m) :
    ∃ v : Fin 3 → P3, (∀ i, v i ∈ pprism nx ny ρ L) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (pβ nx ny (Sum.inl k)) i| +
        ∑ i, g.linearIsometryEquiv (pβ nx ny (Sum.inl k)) i * g.linearIsometryEquiv (v i) i < ph ρ L (Sum.inl k) := by
  set b : Fin 3 → ℝ := fun i => M g i 0 * nx k + M g i 1 * ny k with hb
  refine ⟨fun i => ppt ρ g i (-sgn (b i)) 0, fun i => pdisk_mem hn hρ.le _ _ _ (by simp; linarith), ?_⟩
  have hs' : ∀ i, (-sgn (b i)) ^ 2 = 1 := fun i => by rw [neg_sq]; exact sgn_sq _
  have hLb : ∀ i, g.linearIsometryEquiv (pβ nx ny (Sum.inl k)) i = b i := fun i => by
    rw [lin_coord]; simp [pβ, hb]
  simp only [sum3, hLb]
  simp only [lin_coord, row_ppt ρ g _ (hs' _), ph]
  have e1 : ∀ i, b i * (-sgn (b i) * ρ * U g i + M g i 2 * 0) = -(ρ * (|b i| * U g i)) := fun i => by
    rw [← sgn_mul (b i)]; ring
  rw [e1 0, e1 1, e1 2]
  have c00 := cols g 0 0; have c11 := cols g 1 1; have c01 := cols g 0 1
  simp at c00 c11 c01
  have hnk := hn k
  have e : b 0 ^ 2 + b 1 ^ 2 + b 2 ^ 2 = 1 := by
    simp only [hb]
    linear_combination (nx k) ^ 2 * c00 + 2 * nx k * ny k * c01 + (ny k) ^ 2 * c11 + hnk
  have hbU' : ∀ i, b i ^ 2 ≤ |b i| * U g i := fun i => by
    have hbU : b i ^ 2 ≤ U g i * U g i := by
      rw [← sq, U, sqrt_sq_eq]; simp only [hb]
      nlinarith [sq_nonneg (M g i 0 * ny k - M g i 1 * nx k)]
    have h1 : |b i| ≤ U g i := by
      rw [← sq_abs] at hbU; nlinarith [abs_nonneg (b i), U_nonneg g i]
    rw [← sq_abs]; nlinarith [abs_nonneg (b i)]
  have hl := l1_sq (b 0) (b 1) (b 2)
  set X := |b 0| + |b 1| + |b 2| with hX
  have hX0 : 0 ≤ X := by positivity
  have hXpos : 0 < X := by
    by_contra h; push Not at h
    have h0 : |b 0| = 0 := by linarith [abs_nonneg (b 0), abs_nonneg (b 1), abs_nonneg (b 2)]
    have h1 : |b 1| = 0 := by linarith [abs_nonneg (b 0), abs_nonneg (b 1), abs_nonneg (b 2)]
    have h2 : |b 2| = 0 := by linarith [abs_nonneg (b 0), abs_nonneg (b 1), abs_nonneg (b 2)]
    rw [abs_eq_zero] at h0 h1 h2; rw [h0, h1, h2] at e; norm_num at e
  have hκX : κ * X ≤ 2 * ρ := by
    have : (κ * X) ^ 2 ≤ (2 * ρ) ^ 2 := by nlinarith [sq_nonneg κ]
    nlinarith [mul_nonneg hκ hX0]
  have hlt : s / 2 * X < κ * X := mul_lt_mul_of_pos_right hsκ hXpos
  have h0 := mul_le_mul_of_nonneg_left (hbU' 0) hρ.le
  have h1 := mul_le_mul_of_nonneg_left (hbU' 1) hρ.le
  have h2 := mul_le_mul_of_nonneg_left (hbU' 2) hρ.le
  have eρ : ρ * b 0 ^ 2 + ρ * b 1 ^ 2 + ρ * b 2 ^ 2 = ρ := by linear_combination ρ * e
  linarith

/-- Caps, when `κ = L` and `L ≤ (7/5) ρ`: `(s/2) S - ρ Σ |aᵢ| Uᵢ - L/2 < L/2`. -/
theorem pcap {nx ny : Fin m → ℝ} (hn : ∀ k, nx k ^ 2 + ny k ^ 2 = 1) {ρ L s : ℝ} (hρ : 0 < ρ) (hL : 0 ≤ L)
    (hsL : s / 2 < L) (hLρ : L ≤ 7 / 5 * ρ) (g : P3 ≃ᵃⁱ[ℝ] P3) (b : Bool) :
    ∃ v : Fin 3 → P3, (∀ i, v i ∈ pprism nx ny ρ L) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (pβ nx ny (Sum.inr b)) i| +
        ∑ i, g.linearIsometryEquiv (pβ nx ny (Sum.inr b)) i * g.linearIsometryEquiv (v i) i <
          ph (m := m) ρ L (Sum.inr b) := by
  have c2 := col2 g
  have q0 := U_sq g 0; have q1 := U_sq g 1; have q2 := U_sq g 2
  have u0 := U_ge _ (M g 1 2) (M g 2 2) (U_nonneg g 0) (by linarith)
  have u1 := U_ge _ (M g 0 2) (M g 2 2) (U_nonneg g 1) (by linarith)
  have u2 := U_ge _ (M g 0 2) (M g 1 2) (U_nonneg g 2) (by linarith)
  have a0 := abs_nonneg (M g 0 2); have a1 := abs_nonneg (M g 1 2); have a2 := abs_nonneg (M g 2 2)
  have s0 := sq_abs (M g 0 2); have s1 := sq_abs (M g 1 2); have s2 := sq_abs (M g 2 2)
  set S := |M g 0 2| + |M g 1 2| + |M g 2 2| with hSdef
  have hP : S ^ 2 = 1 + 2 * (|M g 0 2| * |M g 1 2| + |M g 0 2| * |M g 2 2| + |M g 1 2| * |M g 2 2|) := by
    have : S ^ 2 = |M g 0 2| ^ 2 + |M g 1 2| ^ 2 + |M g 2 2| ^ 2 +
        2 * (|M g 0 2| * |M g 1 2| + |M g 0 2| * |M g 2 2| + |M g 1 2| * |M g 2 2|) := by rw [hSdef]; ring
    rw [this, s0, s1, s2, c2]
  have hS0 : 0 ≤ S := by positivity
  have hS1 : 1 ≤ S := by nlinarith [mul_nonneg a0 a1, mul_nonneg a0 a2, mul_nonneg a1 a2]
  have m0 := mul_le_mul_of_nonneg_left u0 a0
  have m1 := mul_le_mul_of_nonneg_left u1 a1
  have m2 := mul_le_mul_of_nonneg_left u2 a2
  have hsum : 7 / 10 * (S ^ 2 - 1) ≤ |M g 0 2| * U g 0 + |M g 1 2| * U g 1 + |M g 2 2| * U g 2 := by
    rw [hP]; linarith
  have hpos : 0 ≤ 7 / 10 * ρ * (S + 1) - L := by
    have := mul_le_mul_of_nonneg_left (show (2 : ℝ) ≤ S + 1 by linarith) hρ.le
    linarith
  have hq : 0 ≤ (S - 1) * (7 / 10 * ρ * (S + 1) - L) := mul_nonneg (by linarith) hpos
  have e1 : (S - 1) * (7 / 10 * ρ * (S + 1) - L) = 7 / 10 * ρ * (S ^ 2 - 1) - L * S + L := by ring
  rw [e1] at hq
  have hrs := mul_le_mul_of_nonneg_left hsum hρ.le
  have e2 : ρ * (7 / 10 * (S ^ 2 - 1)) = 7 / 10 * ρ * (S ^ 2 - 1) := by ring
  rw [e2] at hrs
  have key : L * S - ρ * (|M g 0 2| * U g 0 + |M g 1 2| * U g 1 + |M g 2 2| * U g 2) ≤ L := by linarith
  have hlt : s / 2 * S < L * S := mul_lt_mul_of_pos_right hsL (by linarith)
  have hz : |L / 2| ≤ L / 2 := by rw [abs_of_nonneg (by linarith)]
  have hz' : |-(L / 2)| ≤ L / 2 := by rw [abs_neg]; exact hz
  cases b
  · refine ⟨fun i => ppt ρ g i (sgn (M g i 2)) (L / 2), fun i => pdisk_mem hn hρ.le _ _ _ hz, ?_⟩
    have hLb : ∀ i, g.linearIsometryEquiv (pβ nx ny (Sum.inr false)) i = -M g i 2 := fun i => by
      rw [lin_coord]; simp [pβ]
    simp only [sum3, hLb]
    simp only [lin_coord, row_ppt ρ g _ (sgn_sq _), ph]
    have e : ∀ i, -M g i 2 * (sgn (M g i 2) * ρ * U g i + M g i 2 * (L / 2)) =
        -(ρ * (|M g i 2| * U g i)) - L / 2 * M g i 2 ^ 2 := fun i => by
      rw [← sgn_mul (M g i 2)]; ring
    rw [e 0, e 1, e 2]
    simp only [abs_neg]
    rw [← hSdef]
    have eL : L / 2 * M g 0 2 ^ 2 + L / 2 * M g 1 2 ^ 2 + L / 2 * M g 2 2 ^ 2 = L / 2 := by
      linear_combination (L / 2) * c2
    linarith
  · refine ⟨fun i => ppt ρ g i (-sgn (M g i 2)) (-(L / 2)), fun i => pdisk_mem hn hρ.le _ _ _ hz', ?_⟩
    have hs' : ∀ i, (-sgn (M g i 2)) ^ 2 = 1 := fun i => by rw [neg_sq]; exact sgn_sq _
    have hLb : ∀ i, g.linearIsometryEquiv (pβ nx ny (Sum.inr true)) i = M g i 2 := fun i => by
      rw [lin_coord]; simp [pβ]
    simp only [sum3, hLb]
    simp only [lin_coord, row_ppt ρ g _ (hs' _), ph]
    have e : ∀ i, M g i 2 * (-sgn (M g i 2) * ρ * U g i + M g i 2 * -(L / 2)) =
        -(ρ * (|M g i 2| * U g i)) - L / 2 * M g i 2 ^ 2 := fun i => by
      rw [← sgn_mul (M g i 2)]; ring
    rw [e 0, e 1, e 2]
    rw [← hSdef]
    have eL : L / 2 * M g 0 2 ^ 2 + L / 2 * M g 1 2 ^ 2 + L / 2 * M g 2 2 ^ 2 = L / 2 := by
      linear_combination (L / 2) * c2
    linarith

/-- **Box centre lemma for prisms over a polygon**, with `s/2 < L`, `L √3 ≤ 2ρ` and `L ≤ (7/5)ρ`. -/
theorem pcentre {nx ny : Fin m → ℝ} (hn : ∀ k, nx k ^ 2 + ny k ^ 2 = 1) {ρ L s : ℝ} (hρ : 0 < ρ) (hL : 0 ≤ L)
    (hs : 0 ≤ s) (hsL : s / 2 < L) (h3 : L ^ 2 * 3 ≤ (2 * ρ) ^ 2) (h7 : L ≤ 7 / 5 * ρ) (g : P3 ≃ᵃⁱ[ℝ] P3)
    (hg : g '' pprism nx ny ρ L ⊆ s • cubeC) : (0 : P3) ∈ interior (g '' pprism nx ny ρ L) := by
  refine centre_of_box (pβ nx ny) (ph ρ L) (pK nx ny ρ L) hs g hg fun f => ?_
  rcases f with k | b
  · exact pside hn hρ hL hsL hL h3 g k
  · exact pcap hn hρ hL hsL h7 g b

/-! ## The regular hexagonal prism of height 1: side 2 -/

noncomputable def hx : Fin 6 → ℝ := ![1, 1 / 2, -1 / 2, -1, -1 / 2, 1 / 2]
noncomputable def hy : Fin 6 → ℝ := ![0, Real.sqrt 3 / 2, Real.sqrt 3 / 2, 0, -(Real.sqrt 3 / 2), -(Real.sqrt 3 / 2)]

theorem h_unit (k : Fin 6) : hx k ^ 2 + hy k ^ 2 = 1 := by
  fin_cases k <;> simp [hx, hy] <;> nlinarith [sqrt3_sq]

theorem h_box {y : P3} (hyK : y ∈ pprism hx hy (Real.sqrt 3 / 2) 1) : |y 0| ≤ 1 ∧ |y 1| ≤ 1 := by
  have h0 := hyK.1 0; have h1 := hyK.1 1; have h2 := hyK.1 2; have h3 := hyK.1 3
  have h4 := hyK.1 4; have h5 := hyK.1 5
  simp [hx, hy] at h0 h1 h2 h3 h4 h5
  have hp := sqrt3_pos
  have hb : Real.sqrt 3 < 2 := by nlinarith [sqrt3_sq]
  refine ⟨abs_le.mpr ⟨by linarith, by linarith⟩, abs_le.mpr ⟨?_, ?_⟩⟩
  · -- `√3 y ≥ -√3` from facets 4 and 5
    have : Real.sqrt 3 * (-1) ≤ Real.sqrt 3 * y 1 := by nlinarith
    exact le_of_mul_le_mul_left this hp
  · have : Real.sqrt 3 * y 1 ≤ Real.sqrt 3 * 1 := by nlinarith
    exact le_of_mul_le_mul_left this hp

/-- **Two hexagonal prisms of height 1 in a cube: side 2 is optimal.** -/
theorem pr6incub_n02 : Nonempty (Packing (pprism hx hy (Real.sqrt 3 / 2) 1) cubeC 2 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (pprism hx hy (Real.sqrt 3 / 2) 1) cubeC s 2 → 2 ≤ s := by
  have hp := sqrt3_pos
  have h33 := sqrt3_sq
  refine ⟨⟨pstackPacking (Real.sqrt 3 / 2) 1 2 ![-1 / 2, 1 / 2] (by norm_num)
    (fun y hy => by simpa using (h_box hy).1) (fun y hy => by simpa using (h_box hy).2)
    (fun i => by fin_cases i <;> simp <;> norm_num)
    (fun i j hij => by fin_cases i <;> fin_cases j <;> simp at hij ⊢ <;> norm_num)⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  exact no_packing_two_of_common_point (0 : P3)
    (fun g hg => pcentre h_unit (by positivity) (by norm_num) hs (by linarith) (by nlinarith) (by nlinarith) g hg)
    le_rfl P

end PackingOptimality.PrismCube
