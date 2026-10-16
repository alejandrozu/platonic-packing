import PackingCertificates.Extensions.GenericDimension
import Mathlib.Analysis.InnerProductSpace.LinearMap
import Mathlib.Topology.Order.Compact
import Mathlib.Tactic.NormNum

/-!
# Support values of the inscribed-ball blend

`supportValue` is the genuine real supremum of the directional inner products.
Every public formula involving a body assumes it nonempty and compact. We prove
attainment from the extreme value theorem, rather than using the arbitrary real
supremum conventions for empty or unbounded sets. The ball maximum is constructed
explicitly, including zero directions. These results concern geometric support
extents, not derivatives, objective energies, convergence, or optimizer success.
-/

namespace PackingCertificates.Extensions.SupportIdentity

open Set
open scoped Pointwise RealInnerProductSpace

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- Real support supremum. The meaningful formulas below establish an attained
finite maximum under their explicit hypotheses. -/
noncomputable def supportValue (P : Set E) (u : E) : ℝ :=
  sSup ((fun x => ⟪u, x⟫) '' P)

/-- An attained directional maximum, used as an intermediate proved property. -/
def HasSupportAt (P : Set E) (u : E) (a : ℝ) : Prop :=
  ∃ p ∈ P, ⟪u, p⟫ = a ∧ ∀ x ∈ P, ⟪u, x⟫ ≤ a

theorem HasSupportAt.value_eq {P : Set E} {u : E} {a : ℝ}
    (h : HasSupportAt P u a) : supportValue P u = a := by
  rcases h with ⟨p, hp, hpa, hmax⟩
  apply le_antisymm
  · exact csSup_le ⟨_, ⟨p, hp, rfl⟩⟩ (by rintro _ ⟨x, hx, rfl⟩; exact hmax x hx)
  · exact hpa ▸ le_csSup ⟨a, by rintro _ ⟨x, hx, rfl⟩; exact hmax x hx⟩ ⟨p, hp, rfl⟩

theorem compact_hasSupportAt {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    (u : E) : HasSupportAt P u (supportValue P u) := by
  obtain ⟨p, hp, hmax⟩ := hP.exists_isMaxOn hne
    (show ContinuousOn (fun x : E => ⟪u, x⟫) P from
      (continuous_const.inner continuous_id).continuousOn)
  have hm : HasSupportAt P u ⟪u, p⟫ := ⟨p, hp, rfl, hmax⟩
  rw [hm.value_eq]
  exact hm

theorem singleton_hasSupportAt (p u : E) : HasSupportAt ({p} : Set E) u ⟪u, p⟫ := by
  exact ⟨p, by simp, rfl, by
    intro x hx
    simpa only [mem_singleton_iff.mp hx] using (le_refl ⟪u, p⟫)⟩

theorem support_singleton (p u : E) : supportValue ({p} : Set E) u = ⟪u, p⟫ :=
  (singleton_hasSupportAt p u).value_eq

/-- The Euclidean ball maximum is attained in the direction of `u`; no
finite-dimensional compactness assumption is needed for this explicit maximum. -/
theorem closedBall_hasSupportAt (u : E) {ρ : ℝ} (hρ : 0 ≤ ρ) :
    HasSupportAt (Metric.closedBall (0 : E) ρ) u (ρ * ‖u‖) := by
  by_cases hu : u = 0
  · subst u
    refine ⟨0, ?_, by simp, ?_⟩
    · simpa only [Metric.mem_closedBall, dist_self] using hρ
    · intro x hx
      simp
  have hnu : 0 < ‖u‖ := norm_pos_iff.mpr hu
  have hcoef : 0 ≤ ρ / ‖u‖ := div_nonneg hρ hnu.le
  refine ⟨(ρ / ‖u‖) • u, ?_, ?_, ?_⟩
  · simp only [Metric.mem_closedBall, dist_zero_right, norm_smul,
      Real.norm_eq_abs, abs_of_nonneg hcoef]
    exact le_of_eq (div_mul_cancel₀ _ (ne_of_gt hnu))
  · rw [inner_smul_right, real_inner_self_eq_norm_mul_norm]
    field_simp
  · intro x hx
    have hxnorm : ‖x‖ ≤ ρ := by simpa only [Metric.mem_closedBall, dist_zero_right] using hx
    calc
      ⟪u, x⟫ ≤ ‖u‖ * ‖x‖ := real_inner_le_norm u x
      _ ≤ ‖u‖ * ρ := mul_le_mul_of_nonneg_left hxnorm (norm_nonneg u)
      _ = ρ * ‖u‖ := mul_comm _ _

theorem support_closedBall (u : E) {ρ : ℝ} (hρ : 0 ≤ ρ) :
    supportValue (Metric.closedBall (0 : E) ρ) u = ρ * ‖u‖ :=
  (closedBall_hasSupportAt u hρ).value_eq

theorem HasSupportAt.blend {P Q : Set E} {u : E} {a b τ : ℝ}
    (hP : HasSupportAt P u a) (hQ : HasSupportAt Q u b)
    (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) :
    HasSupportAt (convexBlend P Q τ) u ((1 - τ) * a + τ * b) := by
  rcases hP with ⟨p, hp, hpa, hPmax⟩
  rcases hQ with ⟨q, hq, hqb, hQmax⟩
  refine ⟨(1 - τ) • p + τ • q, ?_, ?_, ?_⟩
  · exact ⟨_, ⟨p, hp, rfl⟩, _, ⟨q, hq, rfl⟩, rfl⟩
  · simp only [inner_add_right, inner_smul_right, hpa, hqb]
  · rintro _ ⟨_, ⟨x, hx, rfl⟩, _, ⟨y, hy, rfl⟩, rfl⟩
    simp only [inner_add_right, inner_smul_right]
    exact add_le_add (mul_le_mul_of_nonneg_left (hPmax x hx) (sub_nonneg.mpr hτ1))
      (mul_le_mul_of_nonneg_left (hQmax y hy) hτ)

/-- Exact support identity for any nonempty compact body, convex or otherwise.
It applies to the same `convexBlend` used by the continuation geometry. -/
theorem support_ballBlend {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    (u : E) {τ ρ : ℝ} (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) (hρ : 0 ≤ ρ) :
    supportValue (convexBlend P (Metric.closedBall (0 : E) ρ) τ) u =
      (1 - τ) * supportValue P u + τ * ρ * ‖u‖ := by
  simpa only [mul_assoc] using
    ((compact_hasSupportAt hP hne u).blend (closedBall_hasSupportAt u hρ) hτ hτ1).value_eq

theorem support_ballBlend_unit {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    {u : E} (hu : ‖u‖ = 1) {τ ρ : ℝ}
    (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) (hρ : 0 ≤ ρ) :
    supportValue (convexBlend P (Metric.closedBall (0 : E) ρ) τ) u =
      (1 - τ) * supportValue P u + τ * ρ := by
  simpa only [hu, mul_one] using support_ballBlend hP hne u hτ hτ1 hρ

/-- Orthogonal images pull a support direction back by the inverse isometry.
This covers proper rotations and also orthogonal reflections. -/
theorem support_isometry_image (P : Set E) (R : E ≃ₗᵢ[ℝ] E) (u : E) :
    supportValue (R '' P) u = supportValue P (R.symm u) := by
  unfold supportValue
  congr 1
  ext a
  constructor
  · rintro ⟨_, ⟨x, hx, rfl⟩, rfl⟩
    refine ⟨x, hx, ?_⟩
    simpa only [R.apply_symm_apply] using (R.inner_map_map (R.symm u) x).symm
  · rintro ⟨x, hx, rfl⟩
    refine ⟨R x, ⟨x, hx, rfl⟩, ?_⟩
    simpa only [R.apply_symm_apply] using R.inner_map_map (R.symm u) x

/-- Two orientations retain exactly a factor `1 - τ` of their original
directional support difference; the common ball term cancels. -/
theorem orientation_support_difference {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    (R S : E ≃ₗᵢ[ℝ] E) (u : E) {τ ρ : ℝ}
    (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) (hρ : 0 ≤ ρ) :
    supportValue (convexBlend (R '' P) (Metric.closedBall (0 : E) ρ) τ) u -
      supportValue (convexBlend (S '' P) (Metric.closedBall (0 : E) ρ) τ) u =
      (1 - τ) * (supportValue P (R.symm u) - supportValue P (S.symm u)) := by
  rw [support_ballBlend (hP.image R.continuous) (hne.image R) u hτ hτ1 hρ,
    support_ballBlend (hP.image S.continuous) (hne.image S) u hτ hτ1 hρ,
    support_isometry_image, support_isometry_image]
  ring

theorem orientation_support_abs_difference {P : Set E} (hP : IsCompact P)
    (hne : P.Nonempty) (R S : E ≃ₗᵢ[ℝ] E) (u : E) {τ ρ : ℝ}
    (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) (hρ : 0 ≤ ρ) :
    |supportValue (convexBlend (R '' P) (Metric.closedBall (0 : E) ρ) τ) u -
      supportValue (convexBlend (S '' P) (Metric.closedBall (0 : E) ρ) τ) u| =
      (1 - τ) * |supportValue P (R.symm u) - supportValue P (S.symm u)| := by
  rw [orientation_support_difference hP hne R S u hτ hτ1 hρ, abs_mul,
    abs_of_nonneg (sub_nonneg.mpr hτ1)]

theorem ballBlend_one_orientation_independent {P : Set E} (hP : IsCompact P)
    (hne : P.Nonempty) (R : E ≃ₗᵢ[ℝ] E) (u : E) {ρ : ℝ} (hρ : 0 ≤ ρ) :
    supportValue (convexBlend (R '' P) (Metric.closedBall (0 : E) ρ) 1) u = ρ * ‖u‖ := by
  simpa using support_ballBlend (hP.image R.continuous) (hne.image R) u
    (by norm_num : (0 : ℝ) ≤ 1) (by norm_num : (1 : ℝ) ≤ 1) hρ

/-- Explicit arbitrary finite-dimensional specialization, using the Euclidean
norm rather than the default sup norm on a function space. -/
theorem euclidean_support_ballBlend (d : ℕ) {P : Set (EuclideanSpace ℝ (Fin d))}
    (hP : IsCompact P) (hne : P.Nonempty) (u : EuclideanSpace ℝ (Fin d))
    {τ ρ : ℝ} (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) (hρ : 0 ≤ ρ) :
    supportValue (convexBlend P (Metric.closedBall (0 : EuclideanSpace ℝ (Fin d)) ρ) τ) u =
      (1 - τ) * supportValue P u + τ * ρ * ‖u‖ :=
  support_ballBlend hP hne u hτ hτ1 hρ

/-- Rotating the whole blend and blending the rotated template have the same
support in every direction, because the Euclidean ball is isotropic. -/
theorem support_rotated_ballBlend {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    (R : E ≃ₗᵢ[ℝ] E) (u : E) {τ ρ : ℝ}
    (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) (hρ : 0 ≤ ρ) :
    supportValue (R '' convexBlend P (Metric.closedBall (0 : E) ρ) τ) u =
      supportValue (convexBlend (R '' P) (Metric.closedBall (0 : E) ρ) τ) u := by
  rw [support_isometry_image, support_ballBlend hP hne (R.symm u) hτ hτ1 hρ,
    support_ballBlend (hP.image R.continuous) (hne.image R) u hτ hτ1 hρ,
    support_isometry_image, R.symm.norm_map]

theorem zero_direction_regression {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    {τ ρ : ℝ} (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) (hρ : 0 ≤ ρ) :
    supportValue (convexBlend P (Metric.closedBall (0 : E) ρ) τ) 0 = 0 := by
  rw [support_ballBlend hP hne 0 hτ hτ1 hρ]
  have hm : HasSupportAt P (0 : E) 0 := by
    obtain ⟨p, hp⟩ := hne
    exact ⟨p, hp, by simp, by intro x hx; simp⟩
  simp [hm.value_eq]

theorem zero_radius_regression {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    (u : E) {τ : ℝ} (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) :
    supportValue (convexBlend P (Metric.closedBall (0 : E) 0) τ) u =
      (1 - τ) * supportValue P u := by
  simpa using support_ballBlend hP hne u hτ hτ1 (le_refl (0 : ℝ))

theorem zero_blend_regression {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    (u : E) {ρ : ℝ} (hρ : 0 ≤ ρ) :
    supportValue (convexBlend P (Metric.closedBall (0 : E) ρ) 0) u = supportValue P u := by
  simpa using support_ballBlend hP hne u (le_refl (0 : ℝ)) zero_le_one hρ

theorem one_blend_regression {P : Set E} (hP : IsCompact P) (hne : P.Nonempty)
    (u : E) {ρ : ℝ} (hρ : 0 ≤ ρ) :
    supportValue (convexBlend P (Metric.closedBall (0 : E) ρ) 1) u = ρ * ‖u‖ := by
  simpa using support_ballBlend hP hne u zero_le_one (le_refl (1 : ℝ)) hρ

/-- The (3,4) direction has Euclidean norm 5, guarding against accidental use
of the sup norm of ordinary function spaces. -/
def nonaxisDirection : EuclideanSpace ℝ (Fin 2) := WithLp.toLp 2 ![3, 4]

theorem nonaxis_direction_norm_regression : ‖nonaxisDirection‖ = 5 := by
  have hs : ‖nonaxisDirection‖ ^ 2 = 25 := by
    rw [EuclideanSpace.real_norm_sq_eq]
    norm_num [nonaxisDirection, Fin.sum_univ_two]
  nlinarith [norm_nonneg nonaxisDirection]

theorem nonaxis_ball_support_regression :
    supportValue (Metric.closedBall (0 : EuclideanSpace ℝ (Fin 2)) 2)
      nonaxisDirection = 10 := by
  rw [support_closedBall nonaxisDirection (by norm_num : (0 : ℝ) ≤ 2),
    nonaxis_direction_norm_regression]
  norm_num

/-- A negative radius gives an empty ball and invalidates the claimed radius
times norm expression: nonnegative radius is a substantive assumption. -/
theorem negative_radius_counterexample :
    supportValue (Metric.closedBall (0 : ℝ) (-1)) (1 : ℝ) ≠ (-1) * ‖(1 : ℝ)‖ := by
  rw [Metric.closedBall_eq_empty.mpr (by norm_num : (-1 : ℝ) < 0)]
  norm_num [supportValue]

/-- An asymmetric two-point template at τ=2 disproves extension beyond the
nonnegative blend-coefficient interval. The ball radius is valid and zero. -/
theorem outside_blend_interval_counterexample :
    supportValue (convexBlend ({(0 : ℝ), 1} : Set ℝ) (Metric.closedBall 0 0) 2) (1 : ℝ) ≠
      (1 - 2) * supportValue ({(0 : ℝ), 1} : Set ℝ) 1 + 2 * 0 * ‖(1 : ℝ)‖ := by
  have hP : HasSupportAt ({(0 : ℝ), 1} : Set ℝ) 1 1 := by
    refine ⟨1, by simp, by norm_num, ?_⟩
    intro x hx
    rcases hx with hx | hx
    · rcases hx with rfl
      norm_num
    · rcases hx with rfl
      norm_num
  have hB : HasSupportAt
      (convexBlend ({(0 : ℝ), 1} : Set ℝ) (Metric.closedBall 0 0) 2) 1 0 := by
    refine ⟨0, ?_, by norm_num, ?_⟩
    · refine ⟨0, ⟨0, by simp, by norm_num⟩, 0, ⟨0, by simp, by norm_num⟩, by norm_num⟩
    · rintro _ ⟨_, ⟨x, hx, rfl⟩, _, ⟨y, hy, rfl⟩, rfl⟩
      have hy0 : y = 0 := by simpa only [Metric.closedBall_zero, mem_singleton_iff] using hy
      subst y
      rcases hx with hx | hx
      · rcases hx with rfl
        norm_num
      · rcases hx with rfl
        norm_num
  rw [hP.value_eq, hB.value_eq]
  norm_num

end PackingCertificates.Extensions.SupportIdentity

#print axioms PackingCertificates.Extensions.SupportIdentity.HasSupportAt.value_eq
#print axioms PackingCertificates.Extensions.SupportIdentity.compact_hasSupportAt
#print axioms PackingCertificates.Extensions.SupportIdentity.support_singleton
#print axioms PackingCertificates.Extensions.SupportIdentity.closedBall_hasSupportAt
#print axioms PackingCertificates.Extensions.SupportIdentity.support_closedBall
#print axioms PackingCertificates.Extensions.SupportIdentity.HasSupportAt.blend
#print axioms PackingCertificates.Extensions.SupportIdentity.support_ballBlend
#print axioms PackingCertificates.Extensions.SupportIdentity.support_ballBlend_unit
#print axioms PackingCertificates.Extensions.SupportIdentity.support_isometry_image
#print axioms PackingCertificates.Extensions.SupportIdentity.orientation_support_difference
#print axioms PackingCertificates.Extensions.SupportIdentity.orientation_support_abs_difference
#print axioms PackingCertificates.Extensions.SupportIdentity.ballBlend_one_orientation_independent
#print axioms PackingCertificates.Extensions.SupportIdentity.euclidean_support_ballBlend

#print axioms PackingCertificates.Extensions.SupportIdentity.singleton_hasSupportAt
#print axioms PackingCertificates.Extensions.SupportIdentity.support_rotated_ballBlend
#print axioms PackingCertificates.Extensions.SupportIdentity.zero_direction_regression
#print axioms PackingCertificates.Extensions.SupportIdentity.zero_radius_regression
#print axioms PackingCertificates.Extensions.SupportIdentity.zero_blend_regression
#print axioms PackingCertificates.Extensions.SupportIdentity.one_blend_regression
#print axioms PackingCertificates.Extensions.SupportIdentity.nonaxis_direction_norm_regression
#print axioms PackingCertificates.Extensions.SupportIdentity.nonaxis_ball_support_regression
#print axioms PackingCertificates.Extensions.SupportIdentity.negative_radius_counterexample
#print axioms PackingCertificates.Extensions.SupportIdentity.outside_blend_interval_counterexample
