import PackingCertificates.Core
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
# Quantitative clearance under coordinate perturbations

The dimension is an arbitrary natural number. A uniform coordinate error ε
changes projection along `a` by at most ε times `sum |a_i|`. Thus wall slack
at least this amount preserves containment; a separating gap strictly larger
than twice this amount preserves disjoint closed convex hulls.

The conclusions concern the convex hulls of the perturbed vertices. Arbitrary
vertex perturbations need not preserve rigidity or congruence. To apply these
results to rigid placements, the perturbed vertices must separately be shown
to be the vertices of those placements. No floating-point error model or
certificate parser is assumed here.
-/

namespace PackingCertificates.Extensions.Clearance

open Set
open scoped BigOperators

/-- Coordinate projection, as the linear functional required by the core. -/
noncomputable def coordinateProjection {d : ℕ} (a : Fin d → ℝ) :
    (Fin d → ℝ) →ₗ[ℝ] ℝ where
  toFun x := ∑ q, a q * x q
  map_add' x y := by simp only [Pi.add_apply, mul_add, Finset.sum_add_distrib]
  map_smul' t x := by
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply, Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro q _
    ring

/-- The dual norm appropriate to a uniform bound on individual coordinates. -/
noncomputable def normalL1 {d : ℕ} (a : Fin d → ℝ) : ℝ := ∑ q, |a q|

theorem normalL1_nonneg {d : ℕ} (a : Fin d → ℝ) : 0 ≤ normalL1 a :=
  Finset.sum_nonneg (fun _ _ => abs_nonneg _)

/-- A coordinate error bound gives an exact directional projection error.
The normal need not be a unit vector, nonzero, or have positive coordinates. -/
theorem projection_perturbation_bound {d : ℕ} (a x y : Fin d → ℝ)
    (ε : ℝ) (_hε : 0 ≤ ε) (herror : ∀ q, |y q - x q| ≤ ε) :
    |coordinateProjection a y - coordinateProjection a x| ≤ ε * normalL1 a := by
  rw [← map_sub]
  change |∑ q, a q * (y q - x q)| ≤ ε * ∑ q, |a q|
  calc
    |∑ q, a q * (y q - x q)| ≤ ∑ q, |a q * (y q - x q)| :=
      Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ q, |a q| * ε := by
      apply Finset.sum_le_sum
      intro q _
      rw [abs_mul]
      exact mul_le_mul_of_nonneg_left (herror q) (abs_nonneg _)
    _ = ε * ∑ q, |a q| := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro q _
      ring

/-- An affine placement written in coordinates. Rotations are a special case;
the error estimate below does not itself certify that either matrix is rigid. -/
noncomputable def affinePlacement {d e : ℕ}
    (r : Fin e → Fin d → ℝ) (c : Fin e → ℝ) (v : Fin d → ℝ) : Fin e → ℝ :=
  fun i => c i + coordinateProjection (r i) v

/-- A coordinate-wise translation error α and a matrix-entry error β give
the placed vertex budget α+βL when its canonical coordinate L1 norm is ≤L.
If both matrices separately satisfy the proper-rotation checks, this is a
rigid-pose perturbation bound. No orthogonality premise is needed for the
inequality itself, which also covers rectangular affine maps. -/
theorem affine_placement_coordinate_error {d e : ℕ}
    (r s : Fin e → Fin d → ℝ) (c z : Fin e → ℝ) (v : Fin d → ℝ)
    (α β L : ℝ) (_hα : 0 ≤ α) (hβ : 0 ≤ β)
    (hcenter : ∀ i, |z i - c i| ≤ α)
    (hmatrix : ∀ i j, |s i j - r i j| ≤ β)
    (hvertex : normalL1 v ≤ L) :
    ∀ i, |affinePlacement s z v i - affinePlacement r c v i| ≤ α + β * L := by
  have hcomm (a b : Fin d → ℝ) : coordinateProjection a b = coordinateProjection b a := by
    change (∑ q, a q * b q) = ∑ q, b q * a q
    apply Finset.sum_congr rfl
    intro q _
    exact mul_comm _ _
  intro i
  have hp := projection_perturbation_bound v (r i) (s i) β hβ (hmatrix i)
  change |z i + coordinateProjection (s i) v -
    (c i + coordinateProjection (r i) v)| ≤ α + β * L
  rw [hcomm (s i) v, hcomm (r i) v]
  calc
    |z i + coordinateProjection v (s i) - (c i + coordinateProjection v (r i))| =
        |(z i - c i) + (coordinateProjection v (s i) - coordinateProjection v (r i))| := by
          congr 1
          ring
    _ ≤ |z i - c i| + |coordinateProjection v (s i) - coordinateProjection v (r i)| :=
      abs_add_le _ _
    _ ≤ α + β * normalL1 v := add_le_add (hcenter i) hp
    _ ≤ α + β * L := add_le_add (le_refl α) (mul_le_mul_of_nonneg_left hvertex hβ)

/-- A closed wall tolerates equality between available slack and the error
budget. This statement allows signed, non-normalized wall coefficients. -/
theorem wall_margin_preserved {d : ℕ} (a x y : Fin d → ℝ)
    (b slack ε : ℝ) (hε : 0 ≤ ε)
    (hwall : coordinateProjection a x ≤ b - slack)
    (hbudget : ε * normalL1 a ≤ slack)
    (herror : ∀ q, |y q - x q| ≤ ε) : coordinateProjection a y ≤ b := by
  have h := (abs_le.mp (projection_perturbation_bound a x y ε hε herror)).2
  linarith

/-- Two independently perturbed vertex lists remain strictly separated when
the original directional gap exceeds both error budgets. The conclusion is
for the whole hulls, including their boundaries, rather than just vertices. -/
theorem separating_hulls_preserved {d k h : ℕ}
    (a : Fin d → ℝ) (v w : Fin k → Fin d → ℝ)
    (p q : Fin h → Fin d → ℝ) (l u ε : ℝ) (hε : 0 ≤ ε)
    (hgap : 2 * ε * normalL1 a < u - l)
    (hleft : ∀ i, coordinateProjection a (v i) ≤ l)
    (hright : ∀ j, u ≤ coordinateProjection a (p j))
    (hleft_error : ∀ i r, |w i r - v i r| ≤ ε)
    (hright_error : ∀ j r, |q j r - p j r| ≤ ε) :
    Disjoint (vertexBody w) (vertexBody q) := by
  apply separating_vertex_tests_imply_disjoint (coordinateProjection a)
    (l + ε * normalL1 a) (u - ε * normalL1 a)
  · linarith
  · rintro _ ⟨i, rfl⟩
    have hb := (abs_le.mp
      (projection_perturbation_bound a (v i) (w i) ε hε (hleft_error i))).2
    have hl := hleft i
    linarith
  · rintro _ ⟨j, rfl⟩
    have hb := (abs_le.mp
      (projection_perturbation_bound a (p j) (q j) ε hε (hright_error j))).1
    have hr := hright j
    linarith

/-- Coordinate normals packaged as the core's halfspace intersection. -/
noncomputable def coordinateWalls {d m : ℕ}
    (a : Fin m → Fin d → ℝ) (b : Fin m → ℝ) : Fin m → Halfspace (Fin d → ℝ) :=
  fun f => ⟨coordinateProjection (a f), b f⟩

/-- A finite packing certificate after perturbation. Each wall has its own
normal-dependent budget, and every pair can use its own separating normal. -/
noncomputable def perturbation_finite_certificate {d n m : ℕ}
    (k : Fin n → ℕ) (v w : (i : Fin n) → Fin (k i) → Fin d → ℝ)
    (a : Fin m → Fin d → ℝ) (b : Fin m → ℝ)
    (ε : ℝ) (hε : 0 ≤ ε)
    (herror : ∀ i p q, |w i p q - v i p q| ≤ ε)
    (hwalls : ∀ i p f,
      coordinateProjection (a f) (v i p) + ε * normalL1 (a f) ≤ b f)
    (hpairs : ∀ i j, i ≠ j →
      ∃ (normal : Fin d → ℝ) (l u : ℝ),
        2 * ε * normalL1 normal < u - l ∧
        (∀ p, coordinateProjection normal (v i p) ≤ l) ∧
        (∀ q, u ≤ coordinateProjection normal (v j q))) :
    FinitePackingCertificate k w (coordinateWalls a b) where
  wall_tests i p f := by
    change coordinateProjection (a f) (w i p) ≤ b f
    have hb := (abs_le.mp
      (projection_perturbation_bound (a f) (v i p) (w i p) ε hε (herror i p))).2
    have hw := hwalls i p f
    linarith
  pair_tests i j hij := by
    obtain ⟨normal, l, u, hgap, hl, hu⟩ := hpairs i j hij
    refine ⟨coordinateProjection normal, l + ε * normalL1 normal,
      u - ε * normalL1 normal, by linarith, ?_, ?_⟩
    · intro p
      have hb := (abs_le.mp
        (projection_perturbation_bound normal (v i p) (w i p) ε hε (herror i p))).2
      have hv := hl p
      linarith
    · intro q
      have hb := (abs_le.mp
        (projection_perturbation_bound normal (v j q) (w j q) ε hε (herror j q))).1
      have hv := hu q
      linarith

/-- In every finite dimension, the wall and pair error budgets preserve
containment and pairwise disjointness of every complete perturbed hull. -/
theorem finite_packing_perturbation_sound {d n m : ℕ}
    (k : Fin n → ℕ) (v w : (i : Fin n) → Fin (k i) → Fin d → ℝ)
    (a : Fin m → Fin d → ℝ) (b : Fin m → ℝ)
    (ε : ℝ) (hε : 0 ≤ ε)
    (herror : ∀ i p q, |w i p q - v i p q| ≤ ε)
    (hwalls : ∀ i p f,
      coordinateProjection (a f) (v i p) + ε * normalL1 (a f) ≤ b f)
    (hpairs : ∀ i j, i ≠ j →
      ∃ (normal : Fin d → ℝ) (l u : ℝ),
        2 * ε * normalL1 normal < u - l ∧
        (∀ p, coordinateProjection normal (v i p) ≤ l) ∧
        (∀ q, u ≤ coordinateProjection normal (v j q))) :
    (∀ i, vertexBody (w i) ⊆ container (coordinateWalls a b)) ∧
      Pairwise (fun i j => Disjoint (vertexBody (w i)) (vertexBody (w j))) :=
  finite_certificate_sound
    (perturbation_finite_certificate k v w a b ε hε herror hwalls hpairs)

/-! Small kernel-checked regressions for the quantitative boundary cases. -/

/-- Signed normals must be measured by sum of absolute values, not their
signed sum. Here ε=1, the signed sum is zero, but the projection error is 2. -/
theorem signed_normal_cancellation_is_unsafe :
    ¬ |coordinateProjection (fun i : Fin 2 => if i = 0 then 1 else -1)
      (fun i => if i = 0 then 1 else -1) -
      coordinateProjection (fun i : Fin 2 => if i = 0 then 1 else -1)
        (fun _ => 0)| ≤ (0 : ℝ) := by
  norm_num [coordinateProjection, Fin.sum_univ_two]

/-- Available wall slack may be used exactly, including a negative normal. -/
theorem exact_wall_budget_safe (y : Fin 1 → ℝ)
    (he : ∀ r, |y r - 0| ≤ (1 : ℝ) / 4) :
    coordinateProjection (fun _ : Fin 1 => -(2 : ℝ)) y ≤ 1 / 2 := by
  apply wall_margin_preserved (fun _ => -2) (fun _ => 0) y
    (1/2) (1/2) (1/4) (by norm_num)
  · norm_num [coordinateProjection]
  · norm_num [normalL1]
  · exact he

/-- A smaller wall budget can let a perturbed vertex leave the container. -/
theorem insufficient_wall_budget_is_unsafe :
    coordinateProjection (fun _ : Fin 1 => (1 : ℝ)) (fun _ => (0 : ℝ)) ≤ 1/2 ∧
    (∀ _r : Fin 1, |(1 : ℝ) - 0| ≤ 1) ∧
    (1/2 : ℝ) < 1 * normalL1 (fun _ : Fin 1 => (1 : ℝ)) ∧
    ¬ coordinateProjection (fun _ : Fin 1 => (1 : ℝ)) (fun _ => (1 : ℝ)) ≤ 1/2 := by
  norm_num [coordinateProjection, normalL1]

/-- A strict gap larger than two coordinate budgets separates the entire
perturbed point hulls for every independently chosen perturbation. -/
theorem strict_pair_budget_safe (w q : Fin 1 → Fin 1 → ℝ)
    (hw : ∀ i r, |w i r - 0| ≤ (1 : ℝ))
    (hq : ∀ i r, |q i r - 3| ≤ (1 : ℝ)) :
    Disjoint (vertexBody w) (vertexBody q) := by
  apply separating_hulls_preserved (fun _ => (1 : ℝ))
    (fun _ _ => 0) w (fun _ _ => 3) q 0 3 1 (by norm_num)
  · norm_num [normalL1]
  · intro i; norm_num [coordinateProjection]
  · intro i; norm_num [coordinateProjection]
  · exact hw
  · exact hq

/-- At a gap of exactly 2ε, two point hulls can meet after admissible errors:
original points 0 and 2 both move to 1, so strict disjointness fails. -/
theorem equality_pair_budget_is_unsafe :
    (2 : ℝ) - 0 = 2 * 1 * normalL1 (fun _ : Fin 1 => (1 : ℝ)) ∧
    (∀ _r : Fin 1, |(1 : ℝ) - 0| ≤ 1) ∧
    (∀ _r : Fin 1, |(1 : ℝ) - 2| ≤ 1) ∧
    ¬ Disjoint (vertexBody (fun _ : Fin 1 => fun _ : Fin 1 => (1 : ℝ)))
      (vertexBody (fun _ : Fin 1 => fun _ : Fin 1 => (1 : ℝ))) := by
  refine ⟨by norm_num [normalL1], by intro r; norm_num, by intro r; norm_num, ?_⟩
  intro hd
  have hm : (fun _ : Fin 1 => (1 : ℝ)) ∈
      vertexBody (fun _ : Fin 1 => fun _ : Fin 1 => (1 : ℝ)) := by
    exact (subset_convexHull ℝ _) (Set.mem_range.mpr ⟨0, rfl⟩)
  exact Set.disjoint_left.mp hd hm hm

/-- Zero coordinate error recovers the geometric conclusion of any original
finite certificate, without a stronger margin assumption. -/
theorem zero_error_recovers_packing {d n m : ℕ} {k : Fin n → ℕ}
    (v w : (i : Fin n) → Fin (k i) → Fin d → ℝ)
    (walls : Fin m → Halfspace (Fin d → ℝ))
    (c : FinitePackingCertificate k v walls)
    (herror : ∀ i p q, |w i p q - v i p q| ≤ (0 : ℝ)) :
    (∀ i, vertexBody (w i) ⊆ container walls) ∧
      Pairwise (fun i j => Disjoint (vertexBody (w i)) (vertexBody (w j))) := by
  have hwv : w = v := by
    funext i p q
    have h := abs_le.mp (herror i p q)
    linarith
  rw [hwv]
  exact finite_certificate_sound c

end PackingCertificates.Extensions.Clearance

#print axioms PackingCertificates.Extensions.Clearance.normalL1_nonneg
#print axioms PackingCertificates.Extensions.Clearance.projection_perturbation_bound
#print axioms PackingCertificates.Extensions.Clearance.affine_placement_coordinate_error
#print axioms PackingCertificates.Extensions.Clearance.wall_margin_preserved
#print axioms PackingCertificates.Extensions.Clearance.separating_hulls_preserved
#print axioms PackingCertificates.Extensions.Clearance.perturbation_finite_certificate
#print axioms PackingCertificates.Extensions.Clearance.finite_packing_perturbation_sound
#print axioms PackingCertificates.Extensions.Clearance.signed_normal_cancellation_is_unsafe
#print axioms PackingCertificates.Extensions.Clearance.exact_wall_budget_safe
#print axioms PackingCertificates.Extensions.Clearance.insufficient_wall_budget_is_unsafe
#print axioms PackingCertificates.Extensions.Clearance.strict_pair_budget_safe
#print axioms PackingCertificates.Extensions.Clearance.equality_pair_budget_is_unsafe
#print axioms PackingCertificates.Extensions.Clearance.zero_error_recovers_packing
