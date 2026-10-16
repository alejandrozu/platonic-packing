import PackingCertificates.Core
import Mathlib.Analysis.Normed.Module.Basic
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
# Dimension-independent geometric continuation

These are geometric feasibility theorems, not convergence theorems for the
floating-point search. They do not assume that a polytope is tangential. The
ambient space can be any real normed vector space; finite dimensional Euclidean
space in any dimension is a special case.
-/

namespace PackingCertificates.Extensions

open Set
open scoped Pointwise

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Opening by a closed Euclidean/norm ball. The general erosion and Minkowski
sum definitions are those of the certificate core. -/
def ballOpening (P : Set E) (r : ℝ) : Set E :=
  minkowskiOpening P (Metric.closedBall (0 : E) r)

/-- Increasing the opening radius can only shrink the rounded shape. This
does not require convexity or finite dimension. -/
theorem ballOpening_antitone (P : Set E) {r R : ℝ}
    (hr : 0 ≤ r) (hrR : r ≤ R) :
    ballOpening P R ⊆ ballOpening P r := by
  have hR : 0 ≤ R := hr.trans hrR
  by_cases hR0 : R = 0
  · have hr0 : r = 0 := le_antisymm (hR0 ▸ hrR) hr
    subst r
    subst R
    exact Subset.rfl
  have hRp : 0 < R := lt_of_le_of_ne hR (Ne.symm hR0)
  let α : ℝ := r / R
  let β : ℝ := 1 - α
  have hα : 0 ≤ α := div_nonneg hr hR
  have hα1 : α ≤ 1 := (div_le_one hRp).mpr hrR
  have hβ : 0 ≤ β := sub_nonneg.mpr hα1
  have hαR : α * R = r := by
    dsimp [α]
    exact div_mul_cancel₀ _ hR0
  have hβR : β * R = R - r := by
    dsimp [β]
    rw [sub_mul, one_mul, hαR]
  rintro _ ⟨a, ha, b, hb, rfl⟩
  have hbNorm : ‖b‖ ≤ R := by simpa [dist_zero_right] using hb
  refine ⟨a + β • b, ?_, α • b, ?_, ?_⟩
  · intro w hw
    have hwNorm : ‖w‖ ≤ r := by simpa [dist_zero_right] using hw
    have hbw : ‖β • b + w‖ ≤ R := by
      calc
        ‖β • b + w‖ ≤ ‖β • b‖ + ‖w‖ := norm_add_le _ _
        _ = β * ‖b‖ + ‖w‖ := by rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg hβ]
        _ ≤ β * R + r := add_le_add (mul_le_mul_of_nonneg_left hbNorm hβ) hwNorm
        _ = R := by rw [hβR]; ring
    have hmem : β • b + w ∈ Metric.closedBall (0 : E) R := by
      simpa [dist_zero_right] using hbw
    simpa [add_assoc] using ha (β • b + w) hmem
  · have : ‖α • b‖ ≤ r := by
      calc
        ‖α • b‖ = α * ‖b‖ := by rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg hα]
        _ ≤ α * R := mul_le_mul_of_nonneg_left hbNorm hα
        _ = r := hαR
    simpa [dist_zero_right] using this
  · have hsum : β + α = 1 := by dsimp [β]; ring
    calc
      (a + β • b) + α • b = a + (β + α) • b := by rw [add_assoc, add_smul]
      _ = a + b := by rw [hsum, one_smul]

/-- Every stage of ball-opening continuation is contained in the target. -/
theorem ballOpening_subset (P : Set E) (r : ℝ) : ballOpening P r ⊆ P :=
  minkowskiOpening_subset P _

/-- The rigid endpoint of the rounded-body family is exactly the target. -/
theorem ballOpening_zero (P : Set E) : ballOpening P 0 = P := by
  apply Set.Subset.antisymm (ballOpening_subset P 0)
  intro x hx
  refine ⟨x, ?_, 0, by simp, by simp⟩
  intro b hb
  have hbNorm : ‖b‖ ≤ 0 := by simpa [dist_zero_right] using hb
  have hb0 : b = 0 := norm_eq_zero.mp (le_antisymm hbNorm (norm_nonneg b))
  simpa [hb0] using hx

/-- The inscribed-body blend used when homothetic erosion is unavailable. -/
def convexBlend (P B : Set E) (τ : ℝ) : Set E :=
  (1 - τ) • P + τ • B

theorem convexBlend_subset {P B : Set E} (hP : Convex ℝ P) (hB : B ⊆ P)
    {τ : ℝ} (hτ : 0 ≤ τ) (hτ1 : τ ≤ 1) : convexBlend P B τ ⊆ P :=
  convex_blend_subset hP hB _ _ (sub_nonneg.mpr hτ1) hτ (by ring)

/-- More weight on an inscribed body produces a smaller blend. No assumption
that all original facets touch a common ball is used. -/
theorem convexBlend_antitone {P B : Set E} (hP : Convex ℝ P) (hB : B ⊆ P)
    {σ τ : ℝ} (hσ : 0 ≤ σ) (hστ : σ ≤ τ) (hτ1 : τ ≤ 1) :
    convexBlend P B τ ⊆ convexBlend P B σ := by
  by_cases hσ1 : σ = 1
  · have hτ : τ = 1 := le_antisymm hτ1 (hσ1 ▸ hστ)
    rw [hσ1, hτ]
  have hσlt : σ < 1 := lt_of_le_of_ne (hστ.trans hτ1) hσ1
  have hden : 0 < 1 - σ := sub_pos.mpr hσlt
  let a : ℝ := (1 - τ) / (1 - σ)
  have ha : 0 ≤ a := div_nonneg (sub_nonneg.mpr hτ1) hden.le
  have ha1 : a ≤ 1 := by
    apply (div_le_one hden).mpr
    linarith
  have haEq : (1 - σ) * a = 1 - τ := by
    dsimp [a]
    field_simp
  rintro _ ⟨_, ⟨p, hp, rfl⟩, _, ⟨b, hb, rfl⟩, rfl⟩
  refine ⟨(1 - σ) • (a • p + (1 - a) • b), ?_, σ • b, ⟨b, hb, rfl⟩, ?_⟩
  · exact ⟨_, hP hp (hB hb) ha (sub_nonneg.mpr ha1) (by ring), rfl⟩
  · have hbEq : (1 - σ) * (1 - a) + σ = τ := by nlinarith [haEq]
    calc
      (1 - σ) • (a • p + (1 - a) • b) + σ • b =
          ((1 - σ) * a) • p + (((1 - σ) * (1 - a) + σ) • b) := by
            rw [smul_add, smul_smul, smul_smul, add_assoc, ← add_smul]
      _ = (1 - τ) • p + τ • b := by rw [haEq, hbEq]

/-- Replacing the placed target pieces by any ball-opening stage preserves
containment and separation. Placements may differ for every piece. -/
theorem opening_preserves_packing {I : Type*} (P : Set E) (C : Set E)
    (f : I → E → E) (r : I → ℝ)
    (inside : ∀ i, f i '' P ⊆ C)
    (separate : Pairwise (fun i j => Disjoint (f i '' P) (f j '' P))) :
    (∀ i, f i '' ballOpening P (r i) ⊆ C) ∧
      Pairwise (fun i j => Disjoint (f i '' ballOpening P (r i))
        (f j '' ballOpening P (r j))) := by
  exact subpacking_sound (fun i => f i '' P) (fun i => f i '' ballOpening P (r i)) C
    (fun i => Set.image_mono (ballOpening_subset P (r i))) inside separate

/-- The dimension is an arbitrary natural number. `EuclideanSpace` carries
the Euclidean norm, so these are genuine Euclidean balls rather than the
sup-norm balls of the default function-space norm on `Fin d → ℝ`. -/
theorem euclidean_ball_continuation (d : ℕ)
    (P : Set (EuclideanSpace ℝ (Fin d))) :
    ballOpening P 0 = P ∧
      (∀ r : ℝ, ballOpening P r ⊆ P) ∧
      (∀ r R : ℝ, 0 ≤ r → r ≤ R → ballOpening P R ⊆ ballOpening P r) := by
  exact ⟨ballOpening_zero P, ballOpening_subset P,
    fun _ _ hr hrR => ballOpening_antitone P hr hrR⟩

/-- In every finite Euclidean dimension, every finite family of individually
placed softened pieces inherits a certified target packing's feasibility. -/
theorem euclidean_opening_preserves_packing (d n : ℕ)
    (P C : Set (EuclideanSpace ℝ (Fin d)))
    (f : Fin n → EuclideanSpace ℝ (Fin d) → EuclideanSpace ℝ (Fin d))
    (r : Fin n → ℝ) (inside : ∀ i, f i '' P ⊆ C)
    (separate : Pairwise (fun i j => Disjoint (f i '' P) (f j '' P))) :
    (∀ i, f i '' ballOpening P (r i) ⊆ C) ∧
      Pairwise (fun i j => Disjoint (f i '' ballOpening P (r i))
        (f j '' ballOpening P (r j))) := by
  exact opening_preserves_packing P C f r inside separate

end PackingCertificates.Extensions

#print axioms PackingCertificates.Extensions.ballOpening_antitone
#print axioms PackingCertificates.Extensions.ballOpening_zero
#print axioms PackingCertificates.Extensions.convexBlend_antitone
#print axioms PackingCertificates.Extensions.opening_preserves_packing
#print axioms PackingCertificates.Extensions.euclidean_ball_continuation
#print axioms PackingCertificates.Extensions.euclidean_opening_preserves_packing
