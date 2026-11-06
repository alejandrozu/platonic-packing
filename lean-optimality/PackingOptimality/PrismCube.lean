import PackingOptimality.OctInCube
import PackingOptimality.Patterns

/-!
# Prisms in a cube: width and box arguments

Two general tools for a cube container `s • cubeC` (the cube `[-s/2, s/2]³`), and their first applications.

* **Axis widths** (`width_le`). If `g '' K ⊆ s • cubeC`, every coordinate of `g p - g q` is at most `s` for
  `p, q ∈ K`. With well-chosen pairs this bounds the one-piece scale `s₁`, hence every `s(n)`.
* **Box centre lemma** (`centre_of_box`). Let `K` contain the open polytope `{y | ⟪β f, y⟫ < h f}`. For a
  placement `g`, the preimage `y` of the cube's centre satisfies, for every facet `f` and any points `vᵢ ∈ K`,
  `⟪β f, y⟫ ≤ (s/2) Σᵢ |bᵢ| + Σᵢ bᵢ (L vᵢ)ᵢ` with `b = L (β f)` and `L` the linear part. The translation of a
  piece inside a box is free coordinate by coordinate, so this bound is sharp for the best points `vᵢ`. If the
  right side is below `h f` for every facet, the centre lies in the interior of every placed piece; by the
  common-point lemma no two pieces fit.

**Dodecagonal prisms.** `dprism L` is the regular dodecagonal prism with unit edges and height `L`: the
dodecagon has inradius `r = (2 + √3)/2` and width `2r = 2 + √3` across flats. It contains the cylinder of
radius `r`; the points used below are on that cylinder.

* `pr12incub_n02`, `pr12incub_n03` (`L = 1`): side `2 + √3`. Widths force every coordinate of the axis above
  `1/2` in absolute value (the threshold is exactly `4r/(4r² + 1) = 1/2`); then the box lemma holds for the
  caps and the twelve sides.
* `pr12l15incub_n02` (`L = 3/2`): side `2 + √3`, already for one piece: the axis has a coordinate with
  `aᵢ² ≤ 1/3`, and the width along that axis is at least `2r √(1 - aᵢ²) + (3/2)|aᵢ| ≥ 2r`.
* `pr12l2incub_n02` (`L = 2`): side 4, by the box lemma with no width step.

The constructions stack the prisms along an axis.
-/

namespace PackingOptimality.PrismCube

open Set CentreGeneral OctInCube
open scoped Pointwise RealInnerProductSpace

/-! ## General tools -/

/-- The matrix of the linear part of a placement. -/
noncomputable abbrev M (g : P3 ≃ᵃⁱ[ℝ] P3) : Matrix (Fin 3) (Fin 3) ℝ := matOf g.linearIsometryEquiv

theorem lin_coord (g : P3 ≃ᵃⁱ[ℝ] P3) (y : P3) (i : Fin 3) :
    g.linearIsometryEquiv y i = M g i 0 * y 0 + M g i 1 * y 1 + M g i 2 * y 2 := by
  rw [matOf_apply, Fin.sum_univ_three]

theorem coord_img (g : P3 ≃ᵃⁱ[ℝ] P3) (y : P3) (i : Fin 3) :
    g y i = g 0 i + (M g i 0 * y 0 + M g i 1 * y 1 + M g i 2 * y 2) := by
  rw [affine_apply_eq g y, PiLp.add_apply, lin_coord]; ring

theorem cols (g : P3 ≃ᵃⁱ[ℝ] P3) (a b : Fin 3) :
    M g 0 a * M g 0 b + M g 1 a * M g 1 b + M g 2 a * M g 2 b = if a = b then 1 else 0 := by
  have h := congrFun (congrFun (matOf_orth g.linearIsometryEquiv) a) b
  simpa only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply, Fin.sum_univ_three] using h

theorem rows (g : P3 ≃ᵃⁱ[ℝ] P3) (i j : Fin 3) :
    M g i 0 * M g j 0 + M g i 1 * M g j 1 + M g i 2 * M g j 2 = if i = j then 1 else 0 := by
  have hAA : M g * Matrix.transpose (M g) = 1 := mul_eq_one_comm.mp (matOf_orth g.linearIsometryEquiv)
  have h := congrFun (congrFun hAA i) j
  simpa only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply, Fin.sum_univ_three] using h

theorem inner_pt (a b c : ℝ) (y : P3) : ⟪pt a b c, y⟫ = a * y 0 + b * y 1 + c * y 2 := by
  rw [inner_sum, Fin.sum_univ_three]; simp

/-- **Axis widths.** -/
theorem width_le {K : Set P3} {s : ℝ} (hs : 0 ≤ s) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' K ⊆ s • cubeC)
    {p q : P3} (hp : p ∈ K) (hq : q ∈ K) (i : Fin 3) :
    M g i 0 * (p 0 - q 0) + M g i 1 * (p 1 - q 1) + M g i 2 * (p 2 - q 2) ≤ s := by
  have h1 := abs_le.mp (coord_of_mem_smul hs (hg ⟨p, hp, rfl⟩) i)
  have h2 := abs_le.mp (coord_of_mem_smul hs (hg ⟨q, hq, rfl⟩) i)
  rw [coord_img] at h1 h2
  nlinarith [h1.1, h1.2, h2.1, h2.2]

/-- **Box centre lemma.** -/
theorem centre_of_box {ι : Type*} [Finite ι] (β : ι → P3) (h : ι → ℝ) {K : Set P3}
    (hK : ∀ y : P3, (∀ f, ⟪β f, y⟫ < h f) → y ∈ K) {s : ℝ} (hs : 0 ≤ s) (g : P3 ≃ᵃⁱ[ℝ] P3)
    (hg : g '' K ⊆ s • cubeC)
    (hv : ∀ f, ∃ v : Fin 3 → P3, (∀ i, v i ∈ K) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (β f) i| +
        ∑ i, g.linearIsometryEquiv (β f) i * g.linearIsometryEquiv (v i) i < h f) :
    (0 : P3) ∈ interior (g '' K) := by
  set L := g.linearIsometryEquiv with hL
  obtain ⟨y, hy⟩ : ∃ y, y = g.symm 0 := ⟨_, rfl⟩
  have hgy : g y = 0 := by rw [hy]; exact g.apply_symm_apply 0
  have hLy : ∀ i, L y i = -g 0 i := by
    intro i
    have := congrArg (fun z : P3 => z i) (affine_apply_eq g y)
    simp only [hgy, PiLp.add_apply, PiLp.zero_apply] at this
    rw [← hL] at this; linarith
  have key : ∀ f, ⟪β f, y⟫ < h f := by
    intro f
    obtain ⟨v, hvK, hlt⟩ := hv f
    have e : ⟪β f, y⟫ = ∑ i, L (β f) i * (-g 0 i) := by
      rw [← L.inner_map_map, inner_sum]
      exact Finset.sum_congr rfl fun i _ => by rw [hLy, mul_comm]
    have bnd : ∀ i, L (β f) i * (-g 0 i) ≤ s / 2 * |L (β f) i| + L (β f) i * L (v i) i := by
      intro i
      have hc := coord_of_mem_smul hs (hg ⟨v i, hvK i, rfl⟩) i
      have hgv : g (v i) i = L (v i) i + g 0 i := by
        have := congrArg (fun z : P3 => z i) (affine_apply_eq g (v i)); simpa [← hL] using this
      rw [hgv] at hc
      have h1 : -(L (β f) i * (L (v i) i + g 0 i)) ≤ |L (β f) i| * (s / 2) := by
        calc -(L (β f) i * (L (v i) i + g 0 i)) ≤ |L (β f) i * (L (v i) i + g 0 i)| := neg_le_abs _
          _ = |L (β f) i| * |L (v i) i + g 0 i| := abs_mul _ _
          _ ≤ |L (β f) i| * (s / 2) := mul_le_mul_of_nonneg_left hc (abs_nonneg _)
      nlinarith
    have hsum := Finset.sum_le_sum fun i (_ : i ∈ Finset.univ) => bnd i
    rw [Finset.sum_add_distrib, ← Finset.mul_sum] at hsum
    rw [e]; linarith
  let U : Set P3 := {z | ∀ f, ⟪β f, z⟫ < h f}
  have hUo : IsOpen U := by
    have : U = ⋂ f, {z | ⟪β f, z⟫ < h f} := by ext z; simp [U]
    rw [this]
    exact isOpen_iInter_of_finite fun f => isOpen_lt (by fun_prop) continuous_const
  have himg : IsOpen (g '' U) := by simpa using g.toHomeomorph.isOpenMap U hUo
  have hsub : g '' U ⊆ g '' K := image_mono fun z hz => hK z hz
  exact interior_maximal hsub himg ⟨y, key, hgy⟩

theorem sum3 (f : Fin 3 → ℝ) : ∑ i, f i = f 0 + f 1 + f 2 := Fin.sum_univ_three f

/-! ## The regular dodecagonal prism -/

noncomputable def r12 : ℝ := (2 + Real.sqrt 3) / 2

noncomputable def nx : Fin 12 → ℝ :=
  ![1, Real.sqrt 3 / 2, 1 / 2, 0, -1 / 2, -(Real.sqrt 3 / 2), -1, -(Real.sqrt 3 / 2), -1 / 2, 0, 1 / 2,
    Real.sqrt 3 / 2]
noncomputable def ny : Fin 12 → ℝ :=
  ![0, 1 / 2, Real.sqrt 3 / 2, 1, Real.sqrt 3 / 2, 1 / 2, 0, -1 / 2, -(Real.sqrt 3 / 2), -1,
    -(Real.sqrt 3 / 2), -1 / 2]

theorem n_unit (k : Fin 12) : nx k ^ 2 + ny k ^ 2 = 1 := by
  fin_cases k <;> simp [nx, ny] <;> nlinarith [sqrt3_sq]

/-- The regular dodecagonal prism with unit edges and height `L`, centred at the origin, axis `e₂`. -/
noncomputable def dprism (L : ℝ) : Set P3 := {y | (∀ k, nx k * y 0 + ny k * y 1 ≤ r12) ∧ |y 2| ≤ L / 2}

theorem r12_pos : 0 < r12 := by unfold r12; positivity
theorem r12_sq : 4 * r12 ^ 2 = 8 * r12 - 1 := by unfold r12; nlinarith [sqrt3_sq]
theorem r12_bounds : 1.866 < r12 ∧ r12 < 1.867 := by
  have h1 : (1.732 : ℝ) < Real.sqrt 3 := by
    rw [show (1.732 : ℝ) = Real.sqrt (1.732 ^ 2) by rw [Real.sqrt_sq (by norm_num)]]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  have h2 : Real.sqrt 3 < 1.734 := by
    rw [show (1.734 : ℝ) = Real.sqrt (1.734 ^ 2) by rw [Real.sqrt_sq (by norm_num)]]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  unfold r12; constructor <;> linarith

/-- `nx·u + ny·v ≤ √(u² + v²)`. -/
theorem dot_le (k : Fin 12) (u v : ℝ) : nx k * u + ny k * v ≤ Real.sqrt (u ^ 2 + v ^ 2) := by
  have h : (nx k * u + ny k * v) ^ 2 ≤ u ^ 2 + v ^ 2 := by
    nlinarith [n_unit k, sq_nonneg (nx k * v - ny k * u)]
  exact (le_abs_self _).trans (Real.abs_le_sqrt h)

/-- A point on the cylinder of radius `r`, in the direction `(u, v)` (the origin's axis if `(u, v) = 0`). -/
theorem disk_mem {L : ℝ} (u v z : ℝ) (hz : |z| ≤ L / 2) :
    pt (r12 * u / Real.sqrt (u ^ 2 + v ^ 2)) (r12 * v / Real.sqrt (u ^ 2 + v ^ 2)) z ∈ dprism L := by
  refine ⟨fun k => ?_, by simpa using hz⟩
  simp only [pt_zero, pt_one]
  rcases (Real.sqrt_nonneg (u ^ 2 + v ^ 2)).eq_or_lt with h0 | hpos
  · rw [← h0]; simp; exact r12_pos.le
  · have hd := dot_le k u v
    have e : nx k * (r12 * u / Real.sqrt (u ^ 2 + v ^ 2)) + ny k * (r12 * v / Real.sqrt (u ^ 2 + v ^ 2)) =
        r12 / Real.sqrt (u ^ 2 + v ^ 2) * (nx k * u + ny k * v) := by
      field_simp
    rw [e]
    calc r12 / Real.sqrt (u ^ 2 + v ^ 2) * (nx k * u + ny k * v)
        ≤ r12 / Real.sqrt (u ^ 2 + v ^ 2) * Real.sqrt (u ^ 2 + v ^ 2) :=
          mul_le_mul_of_nonneg_left hd (div_nonneg r12_pos.le hpos.le)
      _ = r12 := by rw [div_mul_cancel₀ _ hpos.ne']

/-- The midpoint `-r nₖ` of the facet opposite facet `k`. -/
theorem side_mem {L : ℝ} (hL : 0 ≤ L) (k : Fin 12) : pt (-(r12 * nx k)) (-(r12 * ny k)) 0 ∈ dprism L := by
  refine ⟨fun l => ?_, by simp; linarith⟩
  simp only [pt_zero, pt_one]
  have h : nx l * nx k + ny l * ny k ≥ -1 := by
    nlinarith [n_unit k, n_unit l, sq_nonneg (nx l + nx k), sq_nonneg (ny l + ny k)]
  nlinarith [r12_pos]

/-- `(u² + v²)/√(u² + v²) = √(u² + v²)`, also when both vanish. -/
theorem sq_div_sqrt (u v : ℝ) : (u ^ 2 + v ^ 2) / Real.sqrt (u ^ 2 + v ^ 2) = Real.sqrt (u ^ 2 + v ^ 2) := by
  rcases (Real.sqrt_nonneg (u ^ 2 + v ^ 2)).eq_or_lt with h0 | hpos
  · rw [← h0]; simp
  · rw [div_eq_iff hpos.ne', Real.mul_self_sqrt (by positivity)]

theorem sqrt_sq_eq (u v : ℝ) : Real.sqrt (u ^ 2 + v ^ 2) ^ 2 = u ^ 2 + v ^ 2 :=
  Real.sq_sqrt (by positivity)

/-- The radial coordinate of row `i`. -/
noncomputable def U (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) : ℝ := Real.sqrt (M g i 0 ^ 2 + M g i 1 ^ 2)

theorem U_sq (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) : U g i ^ 2 = 1 - M g i 2 ^ 2 := by
  have := rows g i i; simp at this
  rw [U, sqrt_sq_eq]; nlinarith

theorem U_nonneg (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) : 0 ≤ U g i := Real.sqrt_nonneg _

/-- Row `i` applied to the cylinder point in direction `±(Mᵢ₀, Mᵢ₁)` at height `z`. -/
theorem row_disk (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) (σ z : ℝ) :
    M g i 0 * (r12 * (σ * M g i 0) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) +
      M g i 1 * (r12 * (σ * M g i 1) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) + M g i 2 * z =
    σ * r12 * ((M g i 0 ^ 2 + M g i 1 ^ 2) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) + M g i 2 * z := by
  ring

theorem sqrt_sigma (u v σ : ℝ) (hσ : σ ^ 2 = 1) :
    Real.sqrt ((σ * u) ^ 2 + (σ * v) ^ 2) = Real.sqrt (u ^ 2 + v ^ 2) := by
  congr 1; nlinarith

/-- The cylinder point in direction `σ (Mᵢ₀, Mᵢ₁)` (`σ = ±1`) at height `z`, as seen by row `i`:
`σ r Uᵢ + aᵢ z`. -/
theorem row_disk' (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) {σ : ℝ} (hσ : σ ^ 2 = 1) (z : ℝ) :
    M g i 0 * (r12 * (σ * M g i 0) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) +
      M g i 1 * (r12 * (σ * M g i 1) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) + M g i 2 * z =
    σ * r12 * U g i + M g i 2 * z := by
  rw [row_disk, sqrt_sigma _ _ _ hσ, sq_div_sqrt]; rfl

/-- The cylinder point used for row `i`. -/
noncomputable def dpt (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) (σ z : ℝ) : P3 :=
  pt (r12 * (σ * M g i 0) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2))
    (r12 * (σ * M g i 1) / Real.sqrt ((σ * M g i 0) ^ 2 + (σ * M g i 1) ^ 2)) z

theorem dpt_mem {L : ℝ} (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) (σ : ℝ) {z : ℝ} (hz : |z| ≤ L / 2) :
    dpt g i σ z ∈ dprism L := disk_mem _ _ _ hz

theorem row_dpt (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) {σ : ℝ} (hσ : σ ^ 2 = 1) (z : ℝ) :
    M g i 0 * dpt g i σ z 0 + M g i 1 * dpt g i σ z 1 + M g i 2 * dpt g i σ z 2 = σ * r12 * U g i + M g i 2 * z := by
  simp only [dpt, pt_zero, pt_one, pt_two]; exact row_disk' g i hσ z

/-- The sign of a real, as `±1`. -/
noncomputable def sgn (x : ℝ) : ℝ := if 0 ≤ x then 1 else -1

theorem sgn_sq (x : ℝ) : sgn x ^ 2 = 1 := by unfold sgn; split_ifs <;> norm_num
theorem sgn_mul (x : ℝ) : sgn x * x = |x| := by
  unfold sgn; split_ifs with h
  · rw [abs_of_nonneg h]; ring
  · rw [abs_of_neg (not_le.mp h)]; ring

/-- Width of the dodecagonal prism along axis `i`: `2 r Uᵢ + L |aᵢ| ≤ s`. -/
theorem dwidth {L s : ℝ} (hL : 0 ≤ L) (hs : 0 ≤ s) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' dprism L ⊆ s • cubeC) (i : Fin 3) :
    2 * r12 * U g i + L * |M g i 2| ≤ s := by
  have hz : |sgn (M g i 2) * (L / 2)| ≤ L / 2 := by
    rw [abs_mul, show |sgn (M g i 2)| = 1 by unfold sgn; split_ifs <;> norm_num, abs_of_nonneg (by linarith)]
    ring_nf; rfl
  have hz' : |-(sgn (M g i 2) * (L / 2))| ≤ L / 2 := by rw [abs_neg]; exact hz
  have w := width_le hs g hg (dpt_mem g i 1 hz) (dpt_mem g i (-1) hz') i
  have e1 := row_dpt g i (σ := 1) (by norm_num) (sgn (M g i 2) * (L / 2))
  have e2 := row_dpt g i (σ := -1) (by norm_num) (-(sgn (M g i 2) * (L / 2)))
  have hsm := sgn_mul (M g i 2)
  nlinarith

/-! ## The facets, for the box lemma -/

/-- Facet normals: twelve sides (`inl k`) and the two caps (`inr true` up, `inr false` down). -/
noncomputable def dβ : Fin 12 ⊕ Bool → P3
  | Sum.inl k => pt (nx k) (ny k) 0
  | Sum.inr true => pt 0 0 1
  | Sum.inr false => pt 0 0 (-1)

noncomputable def dh (L : ℝ) : Fin 12 ⊕ Bool → ℝ
  | Sum.inl _ => r12
  | Sum.inr _ => L / 2

theorem dK (L : ℝ) : ∀ y : P3, (∀ f, ⟪dβ f, y⟫ < dh L f) → y ∈ dprism L := by
  intro y hy
  refine ⟨fun k => ?_, ?_⟩
  · have := hy (Sum.inl k); simp only [dβ, dh, inner_pt] at this; linarith
  · have h1 := hy (Sum.inr true); have h2 := hy (Sum.inr false)
    simp only [dβ, dh, inner_pt] at h1 h2
    rw [abs_le]; constructor <;> linarith

/-- Image of a facet normal: coordinate `i` of `L (dβ f)`. -/
theorem Lβ_side (g : P3 ≃ᵃⁱ[ℝ] P3) (k : Fin 12) (i : Fin 3) :
    g.linearIsometryEquiv (dβ (Sum.inl k)) i = M g i 0 * nx k + M g i 1 * ny k := by
  rw [lin_coord]; simp [dβ]

theorem Lβ_up (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) : g.linearIsometryEquiv (dβ (Sum.inr true)) i = M g i 2 := by
  rw [lin_coord]; simp [dβ]

theorem Lβ_down (g : P3 ≃ᵃⁱ[ℝ] P3) (i : Fin 3) : g.linearIsometryEquiv (dβ (Sum.inr false)) i = -M g i 2 := by
  rw [lin_coord]; simp [dβ]

/-- `(Σ |xᵢ|)² ≤ 3 Σ xᵢ²`. -/
theorem l1_sq (x y z : ℝ) : (|x| + |y| + |z|) ^ 2 ≤ 3 * (x ^ 2 + y ^ 2 + z ^ 2) := by
  nlinarith [sq_abs x, sq_abs y, sq_abs z, sq_nonneg (|x| - |y|), sq_nonneg (|y| - |z|), sq_nonneg (|x| - |z|)]

/-- Side facets with the common point `-r nₖ`: the bound is `(s/2)‖b‖₁ - r`, below `r` once `s < 2r`. -/
theorem side_common {L s : ℝ} (hL : 0 ≤ L) (hs : 0 ≤ s) (hs2 : s < 2 * r12) (g : P3 ≃ᵃⁱ[ℝ] P3) (k : Fin 12) :
    ∃ v : Fin 3 → P3, (∀ i, v i ∈ dprism L) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (dβ (Sum.inl k)) i| +
        ∑ i, g.linearIsometryEquiv (dβ (Sum.inl k)) i * g.linearIsometryEquiv (v i) i < dh L (Sum.inl k) := by
  refine ⟨fun _ => pt (-(r12 * nx k)) (-(r12 * ny k)) 0, fun _ => side_mem hL k, ?_⟩
  simp only [sum3, Lβ_side]
  simp only [lin_coord, pt_zero, pt_one, pt_two, dh]
  have c00 := cols g 0 0; have c11 := cols g 1 1; have c01 := cols g 0 1
  simp at c00 c11 c01
  have hn := n_unit k
  have e : (M g 0 0 * nx k + M g 0 1 * ny k) ^ 2 + (M g 1 0 * nx k + M g 1 1 * ny k) ^ 2 +
      (M g 2 0 * nx k + M g 2 1 * ny k) ^ 2 = 1 := by
    linear_combination (nx k) ^ 2 * c00 + 2 * nx k * ny k * c01 + (ny k) ^ 2 * c11 + hn
  have key : ∀ i : Fin 3, (M g i 0 * nx k + M g i 1 * ny k) *
      (M g i 0 * -(r12 * nx k) + M g i 1 * -(r12 * ny k) + M g i 2 * 0) =
      -r12 * (M g i 0 * nx k + M g i 1 * ny k) ^ 2 := fun i => by ring
  rw [key 0, key 1, key 2]
  have hb := l1_sq (M g 0 0 * nx k + M g 0 1 * ny k) (M g 1 0 * nx k + M g 1 1 * ny k)
    (M g 2 0 * nx k + M g 2 1 * ny k)
  have e3 : -r12 * (M g 0 0 * nx k + M g 0 1 * ny k) ^ 2 + -r12 * (M g 1 0 * nx k + M g 1 1 * ny k) ^ 2 +
      -r12 * (M g 2 0 * nx k + M g 2 1 * ny k) ^ 2 = -r12 := by linear_combination (-r12) * e
  set X := |M g 0 0 * nx k + M g 0 1 * ny k| + |M g 1 0 * nx k + M g 1 1 * ny k| + |M g 2 0 * nx k + M g 2 1 * ny k|
  have hX0 : 0 ≤ X := by positivity
  have hX : X < 2 := by nlinarith
  have hr := r12_pos
  have : s / 2 * X < 2 * r12 := by nlinarith
  linarith


theorem two_r12 : 2 * r12 = 2 + Real.sqrt 3 := by unfold r12; ring

theorem col2 (g : P3 ≃ᵃⁱ[ℝ] P3) : M g 0 2 ^ 2 + M g 1 2 ^ 2 + M g 2 2 ^ 2 = 1 := by
  have := cols g 2 2; simp at this; nlinarith

theorem sq_abs' (x : ℝ) : |x| ^ 2 = x ^ 2 := sq_abs x

/-! ## Height 1: side `2 + √3` -/

/-- The squared width inequality: `2 r U + c t < 2 r` with `U² = 1 - t²` gives `t (4 r c - t (4 r² + c²)) < 0`. -/
theorem width_contra {r t U c : ℝ} (hr : 0 < r) (ht0 : 0 ≤ t) (hU0 : 0 ≤ U) (hU : U ^ 2 = 1 - t ^ 2)
    (h1 : 2 * r * U + c * t < 2 * r) : t * (4 * r * c - t * (4 * r ^ 2 + c ^ 2)) < 0 := by
  have h1' : 0 ≤ 2 * r * U := by positivity
  have h2 : (2 * r * U) ^ 2 < (2 * r - c * t) ^ 2 := pow_lt_pow_left₀ (by linarith) h1' (by norm_num)
  have h4 : (2 * r * U) ^ 2 = 4 * r ^ 2 * (1 - t ^ 2) := by rw [mul_pow, hU]; ring
  have e : t * (4 * r * c - t * (4 * r ^ 2 + c ^ 2)) = 4 * r ^ 2 * (1 - t ^ 2) - (2 * r - c * t) ^ 2 := by ring
  rw [e]; linarith

/-- Widths force `|aᵢ| > 1/2` for every coordinate of the axis. -/
theorem half_lt {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2 * r12) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' dprism 1 ⊆ s • cubeC)
    (i : Fin 3) : 1 / 2 < |M g i 2| := by
  by_contra hc
  push Not at hc
  have w := dwidth (L := 1) (by norm_num) hs g hg i
  have hU := U_sq g i
  rw [← sq_abs (M g i 2)] at hU
  have h := width_contra (c := 1) r12_pos (abs_nonneg _) (U_nonneg g i) hU (by linarith)
  have hr2 := r12_sq
  have : 0 ≤ |M g i 2| * (4 * r12 * 1 - |M g i 2| * (4 * r12 ^ 2 + 1 ^ 2)) := by
    rw [show 4 * r12 * 1 - |M g i 2| * (4 * r12 ^ 2 + 1 ^ 2) = 4 * r12 * (1 - 2 * |M g i 2|) by
      rw [one_pow, hr2]; ring]
    exact mul_nonneg (abs_nonneg _) (mul_nonneg (by linarith [r12_pos]) (by linarith))
  linarith

/-- The cap estimate `|aᵢ| (1 - Uᵢ) ≤ (71/170) aᵢ²` when `aᵢ² ≤ 1/2`. -/
theorem cap_term (a u : ℝ) (hu0 : 0 ≤ u) (hu : u ^ 2 = 1 - a ^ 2) (ha : a ^ 2 ≤ 1 / 2) :
    |a| * (1 - u) ≤ 71 / 170 * a ^ 2 := by
  have hu7 : 7 / 10 ≤ u := by nlinarith
  have hu1 : u ≤ 1 := by nlinarith
  have ha7 : |a| ≤ 71 / 100 := by
    have : |a| ^ 2 ≤ 1 / 2 := by rw [sq_abs]; exact ha
    nlinarith [abs_nonneg a]
  have e : |a| * (1 - u) * (1 + u) = |a| * a ^ 2 := by rw [mul_assoc]; congr 1; nlinarith
  have h0 : 0 ≤ |a| * (1 - u) := mul_nonneg (abs_nonneg a) (by linarith)
  nlinarith [abs_nonneg a, sq_nonneg a]

theorem cap_d1 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2 * r12) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' dprism 1 ⊆ s • cubeC)
    (b : Bool) : ∃ v : Fin 3 → P3, (∀ i, v i ∈ dprism 1) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (dβ (Sum.inr b)) i| +
        ∑ i, g.linearIsometryEquiv (dβ (Sum.inr b)) i * g.linearIsometryEquiv (v i) i < dh 1 (Sum.inr b) := by
  have hh := fun i => half_lt hs hs2 g hg i
  have c2 := col2 g
  -- every aᵢ² ≤ 1/2
  have hsq : ∀ i, M g i 2 ^ 2 ≤ 1 / 2 := by
    have q : ∀ i, 1 / 4 < M g i 2 ^ 2 := fun i => by
      have := hh i; have := sq_abs (M g i 2); nlinarith [abs_nonneg (M g i 2)]
    intro i; fin_cases i <;> simp <;> nlinarith [q 0, q 1, q 2]
  have ct := fun i => cap_term (M g i 2) (U g i) (U_nonneg g i) (U_sq g i) (hsq i)
  have hr := r12_pos
  have hrb := r12_bounds
  have hz : ∀ z : ℝ, |z| = 1 / 2 → |z| ≤ 1 / 2 := fun z h => h.le
  cases b
  · -- the lower cap `-y₂ ≤ 1/2`: points at height `1/2`
    refine ⟨fun i => dpt g i (sgn (M g i 2)) (1 / 2), fun i => dpt_mem g i _ (by norm_num), ?_⟩
    simp only [sum3, Lβ_down]
    simp only [lin_coord, row_dpt g _ (sgn_sq _), dh]
    have e : ∀ i, -M g i 2 * (sgn (M g i 2) * r12 * U g i + M g i 2 * (1 / 2)) =
        -(r12 * (|M g i 2| * U g i)) - M g i 2 ^ 2 / 2 := fun i => by
      rw [← sgn_mul (M g i 2)]; ring
    rw [e 0, e 1, e 2]
    simp only [abs_neg]
    have hS : s / 2 * (|M g 0 2| + |M g 1 2| + |M g 2 2|) ≤ r12 * (|M g 0 2| + |M g 1 2| + |M g 2 2|) :=
      mul_le_mul_of_nonneg_right (by linarith) (by positivity)
    nlinarith [ct 0, ct 1, ct 2]
  · refine ⟨fun i => dpt g i (-sgn (M g i 2)) (-(1 / 2)), fun i => dpt_mem g i _ (by norm_num), ?_⟩
    have hs' : ∀ i, (-sgn (M g i 2)) ^ 2 = 1 := fun i => by rw [neg_sq]; exact sgn_sq _
    simp only [sum3, Lβ_up]
    simp only [lin_coord, row_dpt g _ (hs' _), dh]
    have e : ∀ i, M g i 2 * (-sgn (M g i 2) * r12 * U g i + M g i 2 * -(1 / 2)) =
        -(r12 * (|M g i 2| * U g i)) - M g i 2 ^ 2 / 2 := fun i => by
      rw [← sgn_mul (M g i 2)]; ring
    rw [e 0, e 1, e 2]
    have hS : s / 2 * (|M g 0 2| + |M g 1 2| + |M g 2 2|) ≤ r12 * (|M g 0 2| + |M g 1 2| + |M g 2 2|) :=
      mul_le_mul_of_nonneg_right (by linarith) (by positivity)
    nlinarith [ct 0, ct 1, ct 2]

/-- **Centre lemma, height 1.** A dodecagonal prism of height 1 inside a cube of side `s < 2 + √3` contains
the cube's centre in its interior. -/
theorem centre_d1 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2 * r12) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' dprism 1 ⊆ s • cubeC) :
    (0 : P3) ∈ interior (g '' dprism 1) := by
  refine centre_of_box dβ (dh 1) (dK 1) hs g hg fun f => ?_
  rcases f with k | b
  · exact side_common (by norm_num) hs hs2 g k
  · exact cap_d1 hs hs2 g hg b

/-! ## Height 3/2: one piece already needs side `2 + √3` -/

theorem no_fit_l15 {s : ℝ} (hs : 0 ≤ s) (hs2 : s < 2 * r12) (g : P3 ≃ᵃⁱ[ℝ] P3)
    (hg : g '' dprism (3 / 2) ⊆ s • cubeC) : False := by
  have c2 := col2 g
  have hex : ∃ i, M g i 2 ^ 2 ≤ 1 / 3 := by
    by_contra h
    push Not at h
    nlinarith [h 0, h 1, h 2]
  obtain ⟨i, hi⟩ := hex
  have w := dwidth (L := 3 / 2) (by norm_num) hs g hg i
  have hU := U_sq g i
  have hU0 := U_nonneg g i
  have hr := r12_pos
  have hr2 := r12_sq
  have hrb := r12_bounds
  rw [← sq_abs (M g i 2)] at hU hi
  have h := width_contra (c := 3 / 2) hr (abs_nonneg _) hU0 hU (by linarith)
  have ht58 : |M g i 2| ≤ 58 / 100 := by nlinarith [abs_nonneg (M g i 2)]
  have h3 : 0 < 4 * r12 * (3 / 2) - |M g i 2| * (4 * r12 ^ 2 + (3 / 2) ^ 2) := by
    rw [hr2]; nlinarith [abs_nonneg (M g i 2)]
  nlinarith [mul_nonneg (abs_nonneg (M g i 2)) h3.le]

/-! ## Height 2: side 4 -/

theorem side_d2 {s : ℝ} (hs : 0 ≤ s) (hs4 : s < 4) (g : P3 ≃ᵃⁱ[ℝ] P3) (k : Fin 12) :
    ∃ v : Fin 3 → P3, (∀ i, v i ∈ dprism 2) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (dβ (Sum.inl k)) i| +
        ∑ i, g.linearIsometryEquiv (dβ (Sum.inl k)) i * g.linearIsometryEquiv (v i) i < dh 2 (Sum.inl k) := by
  set b : Fin 3 → ℝ := fun i => M g i 0 * nx k + M g i 1 * ny k with hb
  refine ⟨fun i => dpt g i (-sgn (b i)) 0, fun i => dpt_mem g i _ (by norm_num), ?_⟩
  have hs' : ∀ i, (-sgn (b i)) ^ 2 = 1 := fun i => by rw [neg_sq]; exact sgn_sq _
  simp only [sum3, Lβ_side]
  simp only [lin_coord, row_dpt g _ (hs' _), dh]
  have e1 : ∀ i, (M g i 0 * nx k + M g i 1 * ny k) * (-sgn (b i) * r12 * U g i + M g i 2 * 0) =
      -(r12 * (|b i| * U g i)) := fun i => by
    rw [← sgn_mul (b i)]; simp only [hb]; ring
  rw [e1 0, e1 1, e1 2]
  have c00 := cols g 0 0; have c11 := cols g 1 1; have c01 := cols g 0 1
  simp at c00 c11 c01
  have hn := n_unit k
  have e : b 0 ^ 2 + b 1 ^ 2 + b 2 ^ 2 = 1 := by
    simp only [hb]
    linear_combination (nx k) ^ 2 * c00 + 2 * nx k * ny k * c01 + (ny k) ^ 2 * c11 + hn
  -- `|bᵢ| ≤ Uᵢ`
  have hbU : ∀ i, b i ^ 2 ≤ U g i * U g i := fun i => by
    rw [← sq, U, sqrt_sq_eq]; simp only [hb]
    nlinarith [sq_nonneg (M g i 0 * ny k - M g i 1 * nx k)]
  have hbU' : ∀ i, b i ^ 2 ≤ |b i| * U g i := fun i => by
    have h1 : |b i| ≤ U g i := by
      have := hbU i; rw [← sq_abs] at this; nlinarith [abs_nonneg (b i), U_nonneg g i]
    rw [← sq_abs]; nlinarith [abs_nonneg (b i)]
  have hl := l1_sq (b 0) (b 1) (b 2)
  have hr := r12_pos
  have hrb := r12_bounds
  have hX0 : 0 ≤ |b 0| + |b 1| + |b 2| := by positivity
  have hX : |b 0| + |b 1| + |b 2| < r12 := by nlinarith
  have hS : s / 2 * (|b 0| + |b 1| + |b 2|) ≤ 2 * (|b 0| + |b 1| + |b 2|) :=
    mul_le_mul_of_nonneg_right (by linarith) hX0
  nlinarith [hbU' 0, hbU' 1, hbU' 2]

/-- `Uᵢ ≥ (7/10)(|aⱼ| + |aₖ|)`. -/
theorem U_ge (u x y : ℝ) (hu0 : 0 ≤ u) (hu : u ^ 2 = x ^ 2 + y ^ 2) : 7 / 10 * (|x| + |y|) ≤ u := by
  have h : (7 / 10 * (|x| + |y|)) ^ 2 ≤ u ^ 2 := by
    rw [hu]; nlinarith [sq_abs x, sq_abs y, sq_nonneg (|x| - |y|)]
  nlinarith [abs_nonneg x, abs_nonneg y]

set_option maxHeartbeats 1000000 in
theorem cap_d2 {s : ℝ} (hs : 0 ≤ s) (hs4 : s < 4) (g : P3 ≃ᵃⁱ[ℝ] P3) (b : Bool) :
    ∃ v : Fin 3 → P3, (∀ i, v i ∈ dprism 2) ∧
      s / 2 * ∑ i, |g.linearIsometryEquiv (dβ (Sum.inr b)) i| +
        ∑ i, g.linearIsometryEquiv (dβ (Sum.inr b)) i * g.linearIsometryEquiv (v i) i < dh 2 (Sum.inr b) := by
  have c2 := col2 g
  have q0 := U_sq g 0; have q1 := U_sq g 1; have q2 := U_sq g 2
  have u0 := U_ge _ (M g 1 2) (M g 2 2) (U_nonneg g 0) (by linarith)
  have u1 := U_ge _ (M g 0 2) (M g 2 2) (U_nonneg g 1) (by linarith)
  have u2 := U_ge _ (M g 0 2) (M g 1 2) (U_nonneg g 2) (by linarith)
  have hr := r12_pos
  have hrb := r12_bounds
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
  have hpos : 0 ≤ 7 / 10 * r12 * (S + 1) - 2 := by
    have := mul_le_mul_of_nonneg_left (show (2 : ℝ) ≤ S + 1 by linarith) hr.le
    linarith [hrb.1]
  have hq : 0 ≤ (S - 1) * (7 / 10 * r12 * (S + 1) - 2) := mul_nonneg (by linarith) hpos
  have e1 : (S - 1) * (7 / 10 * r12 * (S + 1) - 2) = 7 / 10 * r12 * (S ^ 2 - 1) - 2 * S + 2 := by ring
  rw [e1] at hq
  have hrs := mul_le_mul_of_nonneg_left hsum hr.le
  have e2 : r12 * (7 / 10 * (S ^ 2 - 1)) = 7 / 10 * r12 * (S ^ 2 - 1) := by ring
  rw [e2] at hrs
  have key : 2 * S - r12 * (|M g 0 2| * U g 0 + |M g 1 2| * U g 1 + |M g 2 2| * U g 2) ≤ 2 := by
    linarith
  have hlt : s / 2 * S < 2 * S := mul_lt_mul_of_pos_right (by linarith) (by linarith)
  cases b
  · refine ⟨fun i => dpt g i (sgn (M g i 2)) 1, fun i => dpt_mem g i _ (by norm_num), ?_⟩
    simp only [sum3, Lβ_down]
    simp only [lin_coord, row_dpt g _ (sgn_sq _), dh]
    have e : ∀ i, -M g i 2 * (sgn (M g i 2) * r12 * U g i + M g i 2 * 1) =
        -(r12 * (|M g i 2| * U g i)) - M g i 2 ^ 2 := fun i => by
      rw [← sgn_mul (M g i 2)]; ring
    rw [e 0, e 1, e 2]
    simp only [abs_neg]
    rw [← hSdef]
    linarith
  · refine ⟨fun i => dpt g i (-sgn (M g i 2)) (-1), fun i => dpt_mem g i _ (by norm_num), ?_⟩
    have hs' : ∀ i, (-sgn (M g i 2)) ^ 2 = 1 := fun i => by rw [neg_sq]; exact sgn_sq _
    simp only [sum3, Lβ_up]
    simp only [lin_coord, row_dpt g _ (hs' _), dh]
    have e : ∀ i, M g i 2 * (-sgn (M g i 2) * r12 * U g i + M g i 2 * -1) =
        -(r12 * (|M g i 2| * U g i)) - M g i 2 ^ 2 := fun i => by
      rw [← sgn_mul (M g i 2)]; ring
    rw [e 0, e 1, e 2]
    rw [← hSdef]
    linarith

/-- **Centre lemma, height 2.** A dodecagonal prism of height 2 inside a cube of side `s < 4` contains the
cube's centre in its interior. -/
theorem centre_d2 {s : ℝ} (hs : 0 ≤ s) (hs4 : s < 4) (g : P3 ≃ᵃⁱ[ℝ] P3) (hg : g '' dprism 2 ⊆ s • cubeC) :
    (0 : P3) ∈ interior (g '' dprism 2) := by
  refine centre_of_box dβ (dh 2) (dK 2) hs g hg fun f => ?_
  rcases f with k | b
  · exact side_d2 hs hs4 g k
  · exact cap_d2 hs hs4 g b


/-! ## Constructions: prisms stacked along the axis -/

noncomputable def tz (z : ℝ) : P3 ≃ᵃⁱ[ℝ] P3 := AffineIsometryEquiv.constVAdd ℝ P3 (pt 0 0 z)

theorem tz_apply (z : ℝ) (y : P3) : tz z y = pt 0 0 z + y := rfl

theorem stack_inside {L s z : ℝ} (hs : 0 < s) (hr : r12 ≤ s / 2) (hz : |z| + L / 2 ≤ s / 2) :
    tz z '' dprism L ⊆ s • cubeC := by
  rintro _ ⟨y, ⟨hk, hy2⟩, rfl⟩
  apply mem_smul_of_coord hs
  intro i
  fin_cases i
  · have h0 := hk 0; have h6 := hk 6
    simp [nx, ny] at h0 h6
    simp only [tz_apply, Fin.zero_eta, PiLp.add_apply, pt_zero, zero_add]
    rw [abs_le]; constructor <;> linarith
  · have h3 := hk 3; have h9 := hk 9
    simp [nx, ny] at h3 h9
    simp only [tz_apply, Fin.mk_one, PiLp.add_apply, pt_one, zero_add]
    rw [abs_le]; constructor <;> linarith
  · simp only [tz_apply, Fin.reduceFinMk, PiLp.add_apply, pt_two]
    calc |z + y 2| ≤ |z| + |y 2| := abs_add_le _ _
      _ ≤ s / 2 := by linarith

/-- `n` dodecagonal prisms stacked along the axis at heights `z i`. -/
noncomputable def stackPacking (L s : ℝ) {n : ℕ} (z : Fin n → ℝ) (hs : 0 < s) (hr : r12 ≤ s / 2)
    (hz : ∀ i, |z i| + L / 2 ≤ s / 2) (hsep : ∀ i j, i < j → z i + L / 2 ≤ z j - L / 2) :
    Packing (dprism L) cubeC s n :=
  Packing.of_separators (fun i => tz (z i)) (fun i => stack_inside hs hr (hz i))
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

theorem r_le : r12 ≤ (2 + Real.sqrt 3) / 2 := by unfold r12; rfl

/-- **Two and three dodecagonal prisms of height 1 in a cube: side `2 + √3` is optimal.** -/
theorem pr12incub_n03 : Nonempty (Packing (dprism 1) cubeC (2 + Real.sqrt 3) 3) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (dprism 1) cubeC s 3 → 2 + Real.sqrt 3 ≤ s := by
  have hrb := r12_bounds
  refine ⟨⟨stackPacking 1 (2 + Real.sqrt 3) ![-1, 0, 1] (by positivity) (by rw [← two_r12]; linarith)
    (fun i => by rw [← two_r12]; fin_cases i <;> simp <;> linarith)
    (fun i j hij => by fin_cases i <;> fin_cases j <;> simp at hij ⊢ <;> norm_num)⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  rw [← two_r12] at h
  exact no_packing_two_of_common_point (0 : P3) (fun g hg => centre_d1 hs h g hg) (by norm_num) P

theorem pr12incub_n02 : Nonempty (Packing (dprism 1) cubeC (2 + Real.sqrt 3) 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (dprism 1) cubeC s 2 → 2 + Real.sqrt 3 ≤ s := by
  refine ⟨⟨(pr12incub_n03.1.some).restrict (by norm_num)⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  rw [← two_r12] at h
  exact no_packing_two_of_common_point (0 : P3) (fun g hg => centre_d1 hs h g hg) le_rfl P

/-- **Two dodecagonal prisms of height 3/2 in a cube: side `2 + √3` is optimal** (one prism already needs
it). -/
theorem pr12l15incub_n02 : Nonempty (Packing (dprism (3 / 2)) cubeC (2 + Real.sqrt 3) 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (dprism (3 / 2)) cubeC s 2 → 2 + Real.sqrt 3 ≤ s := by
  have hrb := r12_bounds
  refine ⟨⟨stackPacking (3 / 2) (2 + Real.sqrt 3) ![-3 / 4, 3 / 4] (by positivity) (by rw [← two_r12]; linarith)
    (fun i => by rw [← two_r12]; fin_cases i <;> simp <;> norm_num <;> linarith)
    (fun i j hij => by fin_cases i <;> fin_cases j <;> simp at hij ⊢ <;> norm_num)⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  rw [← two_r12] at h
  exact no_fit_l15 hs h (P.g 0) (P.inside 0)

/-- **Two dodecagonal prisms of height 2 in a cube: side 4 is optimal.** -/
theorem pr12l2incub_n02 : Nonempty (Packing (dprism 2) cubeC 4 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (dprism 2) cubeC s 2 → 4 ≤ s := by
  have hrb := r12_bounds
  refine ⟨⟨stackPacking 2 4 ![-1, 1] (by norm_num) (by linarith)
    (fun i => by fin_cases i <;> simp <;> norm_num)
    (fun i j hij => by fin_cases i <;> fin_cases j <;> simp at hij ⊢ <;> norm_num)⟩, fun s hs P => ?_⟩
  by_contra h
  push Not at h
  exact no_packing_two_of_common_point (0 : P3) (fun g hg => centre_d2 hs h g hg) le_rfl P

end PackingOptimality.PrismCube
