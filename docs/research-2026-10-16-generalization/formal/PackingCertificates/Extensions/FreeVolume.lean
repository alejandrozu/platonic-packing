import PackingCertificates.Extensions.Clearance
import Mathlib.MeasureTheory.Measure.Lebesgue.Basic
import Mathlib.Tactic.FunProp
import Mathlib.Tactic.FinCases

/-!
# A certified translational free-volume lower bound

Particles are labelled and their orientations are fixed. A configuration is
one independent translation per particle, represented by `n*d` real scalar
coordinates. Wall and pair margins are checked at the reference packing;
feasibility of the translated configurations is derived, not assumed.

The result gives a measurable finite-inequality region of feasible pure
translations containing a box of product-coordinate Lebesgue volume
`(2*epsilon)^(n*d)`. This is not integration over orientations, does not
divide by `n!`, and includes no momentum, temperature, or interaction energy.
In particular it does not predict a physical free energy or phase transition.
The lower bound on the complete geometric feasible set uses monotonicity of
Lebesgue outer measure; its measurability is not assumed or asserted here.
-/

namespace PackingCertificates.Extensions.FreeVolume

open Set MeasureTheory
open PackingCertificates.Extensions.Clearance
open scoped BigOperators

/-- Flattening the particle and spatial indices fixes the measure convention. -/
abbrev Configuration (n d : ℕ) := (Fin n × Fin d) → ℝ

def displacementCube (n d : ℕ) (ε : ℝ) : Set (Configuration n d) :=
  Icc (fun _ => -ε) (fun _ => ε)

/-- Each particle's vertices receive the same translation, without deformation. -/
def translatedVertices {n d : ℕ} {k : Fin n → ℕ}
    (v : (i : Fin n) → Fin (k i) → Fin d → ℝ) (t : Configuration n d) :
    (i : Fin n) → Fin (k i) → Fin d → ℝ :=
  fun i p q => v i p q + t (i, q)

def feasibleTranslations {n d m : ℕ} {k : Fin n → ℕ}
    (v : (i : Fin n) → Fin (k i) → Fin d → ℝ)
    (a : Fin m → Fin d → ℝ) (b : Fin m → ℝ) : Set (Configuration n d) :=
  {t | (∀ i, vertexBody (translatedVertices v t i) ⊆ container (coordinateWalls a b)) ∧
    Pairwise (fun i j => Disjoint (vertexBody (translatedVertices v t i))
      (vertexBody (translatedVertices v t j)))}

/-- The input is explicit vertex/wall slack and one separating direction for
every ordered pair. No premise asserts geometric feasibility of a region. -/
structure TranslationClearance {n d m : ℕ} (k : Fin n → ℕ)
    (v : (i : Fin n) → Fin (k i) → Fin d → ℝ)
    (a : Fin m → Fin d → ℝ) (b : Fin m → ℝ) (ε : ℝ) where
  pairNormal : Fin n → Fin n → Fin d → ℝ
  leftBound : Fin n → Fin n → ℝ
  rightBound : Fin n → Fin n → ℝ
  wall_budget : ∀ i p f,
    coordinateProjection (a f) (v i p) + ε * normalL1 (a f) ≤ b f
  pair_budget : ∀ i j, i ≠ j →
    2 * ε * normalL1 (pairNormal i j) < rightBound i j - leftBound i j
  left_tests : ∀ i j, i ≠ j → ∀ p,
    coordinateProjection (pairNormal i j) (v i p) ≤ leftBound i j
  right_tests : ∀ i j, i ≠ j → ∀ q,
    rightBound i j ≤ coordinateProjection (pairNormal i j) (v j q)

/-- A finite collection of non-strict linear inequalities, with pair bounds
already shifted inward by the allotted directional error. -/
def certifiedTranslationRegion {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) : Set (Configuration n d) :=
  {t | (∀ i p f, coordinateProjection (a f) (translatedVertices v t i p) ≤ b f) ∧
    ∀ i j, i ≠ j →
      (∀ p, coordinateProjection (c.pairNormal i j) (translatedVertices v t i p) ≤
        c.leftBound i j + ε * normalL1 (c.pairNormal i j)) ∧
      (∀ q, c.rightBound i j - ε * normalL1 (c.pairNormal i j) ≤
        coordinateProjection (c.pairNormal i j) (translatedVertices v t j q))}

theorem translated_hull_is_affine_translate {n d : ℕ} {k : Fin n → ℕ}
    (v : (i : Fin n) → Fin (k i) → Fin d → ℝ) (t : Configuration n d) (i : Fin n) :
    vertexBody (translatedVertices v t i) =
      (fun x : Fin d → ℝ => (fun q => t (i, q)) + x) '' vertexBody (v i) := by
  have h := affine_placement_of_vertex_body (v i)
    (AffineEquiv.constVAdd ℝ (Fin d → ℝ) (fun q => t (i, q))).toAffineMap
  calc
    vertexBody (translatedVertices v t i) =
        vertexBody ((AffineEquiv.constVAdd ℝ (Fin d → ℝ)
          (fun q => t (i, q))).toAffineMap ∘ v i) := by
      congr 1
      funext p q
      change v i p q + t (i, q) = t (i, q) + v i p q
      exact add_comm _ _
    _ = (fun x : Fin d → ℝ => (fun q => t (i, q)) + x) '' vertexBody (v i) := h.symm

/-- Pure translations preserve every pairwise squared Euclidean distance. -/
theorem translation_preserves_squared_distance {d : ℕ} (x y t : Fin d → ℝ) :
    (∑ q, ((x q + t q) - (y q + t q)) ^ 2) = ∑ q, (x q - y q) ^ 2 := by
  apply Finset.sum_congr rfl
  intro q _
  congr 1
  ring

theorem cube_coordinate_bound {n d : ℕ} {ε : ℝ} {t : Configuration n d}
    (ht : t ∈ displacementCube n d ε) (i : Fin n) (q : Fin d) : |t (i, q)| ≤ ε :=
  abs_le.mpr ⟨ht.1 (i, q), ht.2 (i, q)⟩

theorem displacement_cube_feasible {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) (hε : 0 ≤ ε) :
    displacementCube n d ε ⊆ feasibleTranslations v a b := by
  intro t ht
  apply finite_packing_perturbation_sound k v (translatedVertices v t) a b ε hε
  · intro i p q
    simpa [translatedVertices] using cube_coordinate_bound ht i q
  · exact c.wall_budget
  · intro i j hij
    exact ⟨c.pairNormal i j, c.leftBound i j, c.rightBound i j,
      c.pair_budget i j hij, c.left_tests i j hij, c.right_tests i j hij⟩

theorem displacement_cube_in_certified_region {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) (hε : 0 ≤ ε) :
    displacementCube n d ε ⊆ certifiedTranslationRegion c := by
  intro t ht
  have he (i : Fin n) (p : Fin (k i)) (q : Fin d) :
      |translatedVertices v t i p q - v i p q| ≤ ε := by
    simpa [translatedVertices] using cube_coordinate_bound ht i q
  constructor
  · intro i p f
    apply wall_margin_preserved (a f) (v i p) (translatedVertices v t i p)
      (b f) (ε * normalL1 (a f)) ε hε
    · have hw := c.wall_budget i p f
      linarith
    · exact le_refl _
    · exact he i p
  · intro i j hij
    constructor
    · intro p
      have hp := (abs_le.mp (projection_perturbation_bound (c.pairNormal i j)
        (v i p) (translatedVertices v t i p) ε hε (he i p))).2
      have hl := c.left_tests i j hij p
      linarith
    · intro q
      have hp := (abs_le.mp (projection_perturbation_bound (c.pairNormal i j)
        (v j q) (translatedVertices v t j q) ε hε (he j q))).1
      have hr := c.right_tests i j hij q
      linarith

theorem certified_region_feasible {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) :
    certifiedTranslationRegion c ⊆ feasibleTranslations v a b := by
  intro t ht
  apply finite_certificate_sound
  refine { wall_tests := ht.1, pair_tests := ?_ }
  intro i j hij
  exact ⟨coordinateProjection (c.pairNormal i j),
    c.leftBound i j + ε * normalL1 (c.pairNormal i j),
    c.rightBound i j - ε * normalL1 (c.pairNormal i j),
    by have h := c.pair_budget i j hij; linarith, (ht.2 i j hij).1, (ht.2 i j hij).2⟩

theorem continuous_translated_projection {n d : ℕ} (normal x : Fin d → ℝ)
    (i : Fin n) : Continuous
      (fun t : Configuration n d => coordinateProjection normal (fun q => x q + t (i, q))) := by
  change Continuous (fun t : Configuration n d => ∑ q, normal q * (x q + t (i, q)))
  fun_prop

theorem certified_region_isClosed {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) : IsClosed (certifiedTranslationRegion c) := by
  simp only [certifiedTranslationRegion, setOf_and, setOf_forall]
  apply IsClosed.inter
  · apply isClosed_iInter
    intro i
    apply isClosed_iInter
    intro p
    apply isClosed_iInter
    intro f
    exact isClosed_le (continuous_translated_projection (a f) (v i p) i) continuous_const
  · apply isClosed_iInter
    intro i
    apply isClosed_iInter
    intro j
    apply isClosed_iInter
    intro hij
    apply IsClosed.inter
    · apply isClosed_iInter
      intro p
      exact isClosed_le
        (continuous_translated_projection (c.pairNormal i j) (v i p) i) continuous_const
    · apply isClosed_iInter
      intro q
      exact isClosed_le continuous_const
        (continuous_translated_projection (c.pairNormal i j) (v j q) j)

theorem certified_region_measurable {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) : MeasurableSet (certifiedTranslationRegion c) :=
  (certified_region_isClosed c).measurableSet

/-- Exact product-coordinate volume. `ofReal` correctly clips negative side
lengths to zero; empty-dimensional configurations retain volume one. -/
theorem displacement_cube_volume (n d : ℕ) (ε : ℝ) :
    volume (displacementCube n d ε) = ENNReal.ofReal (2 * ε) ^ (n * d) := by
  rw [displacementCube, Real.volume_Icc_pi]
  simp [sub_neg_eq_add, ← two_mul]

theorem certified_region_volume_lower_bound {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) (hε : 0 ≤ ε) :
    ENNReal.ofReal (2 * ε) ^ (n * d) ≤ volume (certifiedTranslationRegion c) := by
  rw [← displacement_cube_volume n d ε]
  exact measure_mono (displacement_cube_in_certified_region c hε)

theorem certified_region_positive_volume {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) (hε : 0 < ε) :
    0 < volume (certifiedTranslationRegion c) := by
  have hp : 0 < ENNReal.ofReal (2 * ε) ^ (n * d) :=
    ENNReal.pow_pos (ENNReal.ofReal_pos.mpr (mul_pos (by norm_num) hε)) _
  exact hp.trans_le (certified_region_volume_lower_bound c hε.le)

/-- The complete feasible set contains the certified measurable region.
No measurability assumption on that larger set is needed for this monotone
outer-measure bound. -/
theorem feasible_translation_outer_volume_lower_bound {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) (hε : 0 ≤ ε) :
    ENNReal.ofReal (2 * ε) ^ (n * d) ≤ volume (feasibleTranslations v a b) :=
  (certified_region_volume_lower_bound c hε).trans (measure_mono (certified_region_feasible c))

/-- The bridge can be stated entirely with a measurable feasible subset,
without making a measurability claim about the full configuration set. -/
theorem exists_positive_measurable_feasible_region {n d m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → Fin d → ℝ}
    {a : Fin m → Fin d → ℝ} {b : Fin m → ℝ} {ε : ℝ}
    (c : TranslationClearance k v a b ε) (hε : 0 < ε) :
    ∃ S : Set (Configuration n d), MeasurableSet S ∧ S ⊆ feasibleTranslations v a b ∧
      ENNReal.ofReal (2 * ε) ^ (n * d) ≤ volume S ∧ 0 < volume S :=
  ⟨certifiedTranslationRegion c, certified_region_measurable c, certified_region_feasible c,
    certified_region_volume_lower_bound c hε.le, certified_region_positive_volume c hε⟩

/-! Quantitative and boundary regressions, audited as named propositions. -/

theorem zero_radius_has_zero_volume :
    volume (displacementCube 1 1 0) = 0 := by
  norm_num [displacement_cube_volume]

theorem negative_radius_has_zero_volume :
    volume (displacementCube 1 1 (-1)) = 0 ∧ ¬ (0 : ℝ) < -1 := by
  norm_num [displacement_cube_volume]

theorem signed_translation_bound (ε : ℝ) (hε : 0 ≤ ε) (t : Configuration 1 2)
    (ht : t ∈ displacementCube 1 2 ε) :
    |coordinateProjection (fun q : Fin 2 => if q = 0 then 1 else -1)
      (fun q => t (0, q))| ≤ 2 * ε := by
  have hp := projection_perturbation_bound
    (fun q : Fin 2 => if q = 0 then 1 else -1) (fun _ => 0)
    (fun q => t (0, q)) ε hε (fun q => by simpa using cube_coordinate_bound ht 0 q)
  norm_num [coordinateProjection, normalL1, Fin.sum_univ_two] at hp ⊢
  nlinarith [hp]

def twoIntervalVertices : (i : Fin 2) → Fin 2 → Fin 1 → ℝ :=
  fun i p _ => if i = 0 then (if p = 0 then -2 else -1) else (if p = 0 then 1 else 2)

def twoIntervalNormals : Fin 2 → Fin 1 → ℝ :=
  fun f _ => if f = 0 then 1 else -1

/-- Both ordered pairs have genuine separating-plane checks. The normal is
reversed for the second particle, so each ordered first particle is the left
side in its own projection direction. -/
noncomputable def twoIntervalClearance : TranslationClearance (fun _ : Fin 2 => 2)
    twoIntervalVertices twoIntervalNormals (fun _ => 3) (1/4) where
  pairNormal := fun i _ _ => if i = 0 then 1 else -1
  leftBound := fun _ _ => -1
  rightBound := fun _ _ => 1
  wall_budget := by
    intro i p f
    fin_cases i <;> fin_cases p <;> fin_cases f <;>
      norm_num [coordinateProjection, normalL1, twoIntervalVertices, twoIntervalNormals]
  pair_budget := by
    intro i j hij
    fin_cases i <;> fin_cases j <;> norm_num [normalL1] at *
  left_tests := by
    intro i j hij p
    fin_cases i <;> fin_cases j <;> fin_cases p <;>
      norm_num [coordinateProjection, twoIntervalVertices] at *
  right_tests := by
    intro i j hij q
    fin_cases i <;> fin_cases j <;> fin_cases q <;>
      norm_num [coordinateProjection, twoIntervalVertices] at *

/-- Two intervals [-2,-1] and [1,2] in [-3,3] admit independent coordinate
translations of radius 1/4. Their two-dimensional displacement box has volume
1/4, providing a positive-volume example with nonvacuous pair separation. -/
theorem two_interval_positive_free_volume :
    ∃ S : Set (Configuration 2 1), MeasurableSet S ∧
      S ⊆ feasibleTranslations twoIntervalVertices twoIntervalNormals (fun _ => 3) ∧
      (1/4 : ENNReal) ≤ volume S ∧ 0 < volume S := by
  obtain ⟨S, hm, hs, hv, hp⟩ := exists_positive_measurable_feasible_region
    twoIntervalClearance (by norm_num : (0 : ℝ) < 1/4)
  refine ⟨S, hm, hs, ?_, hp⟩
  have heq : ENNReal.ofReal (2 * (1/4 : ℝ)) ^ (2 * 1) = (1/4 : ENNReal) := by
    rw [← ENNReal.ofReal_pow (by norm_num)]
    norm_num [ENNReal.ofReal_div_of_pos]
  rwa [heq] at hv

def exactFitVertices : (i : Fin 1) → Fin 2 → Fin 1 → ℝ :=
  fun _ p _ => if p = 0 then -1 else 1

def exactFitNormals : Fin 2 → Fin 1 → ℝ :=
  fun f _ => if f = 0 then 1 else -1

/-- A full-dimensional 1D interval exactly filling its interval container is
feasible, but its entire allowed translation set has volume zero. A single
feasible witness therefore does not imply positive translational free volume. -/
theorem exact_fit_witness_has_zero_free_volume :
    (0 : Configuration 1 1) ∈ feasibleTranslations exactFitVertices exactFitNormals (fun _ => 1) ∧
    volume (feasibleTranslations exactFitVertices exactFitNormals (fun _ => 1)) = 0 := by
  constructor
  · apply finite_certificate_sound
    refine { wall_tests := ?_, pair_tests := ?_ }
    · intro i p f
      fin_cases i; fin_cases p <;> fin_cases f <;>
        norm_num [coordinateWalls, translatedVertices, exactFitVertices, exactFitNormals,
          coordinateProjection]
    · intro i j hij
      exact (hij (Subsingleton.elim i j)).elim
  · have hs : feasibleTranslations exactFitVertices exactFitNormals (fun _ => 1) ⊆
        ({0} : Set (Configuration 1 1)) := by
      intro t ht
      have hv (p : Fin 2) : translatedVertices exactFitVertices t 0 p ∈
          vertexBody (translatedVertices exactFitVertices t 0) :=
        (subset_convexHull ℝ _) (Set.mem_range.mpr ⟨p, rfl⟩)
      have hr := ht.1 0 (hv 1) 0
      have hl := ht.1 0 (hv 0) 1
      change coordinateProjection (exactFitNormals 0) (translatedVertices exactFitVertices t 0 1) ≤ 1 at hr
      change coordinateProjection (exactFitNormals 1) (translatedVertices exactFitVertices t 0 0) ≤ 1 at hl
      norm_num [exactFitNormals, exactFitVertices, translatedVertices, coordinateProjection] at hr hl
      have hzero : t = 0 := by
        funext r
        rcases r with ⟨i, q⟩
        fin_cases i
        fin_cases q
        change t (0, 0) = 0
        linarith
      exact Set.mem_singleton_iff.mpr hzero
    apply le_antisymm
    · calc
        volume (feasibleTranslations exactFitVertices exactFitNormals (fun _ => 1)) ≤
            volume ({0} : Set (Configuration 1 1)) := measure_mono hs
        _ = 0 := measure_singleton _
    · exact bot_le

end PackingCertificates.Extensions.FreeVolume

#print axioms PackingCertificates.Extensions.FreeVolume.translated_hull_is_affine_translate
#print axioms PackingCertificates.Extensions.FreeVolume.translation_preserves_squared_distance
#print axioms PackingCertificates.Extensions.FreeVolume.cube_coordinate_bound
#print axioms PackingCertificates.Extensions.FreeVolume.displacement_cube_feasible
#print axioms PackingCertificates.Extensions.FreeVolume.displacement_cube_in_certified_region
#print axioms PackingCertificates.Extensions.FreeVolume.certified_region_feasible
#print axioms PackingCertificates.Extensions.FreeVolume.continuous_translated_projection
#print axioms PackingCertificates.Extensions.FreeVolume.certified_region_isClosed
#print axioms PackingCertificates.Extensions.FreeVolume.certified_region_measurable
#print axioms PackingCertificates.Extensions.FreeVolume.displacement_cube_volume
#print axioms PackingCertificates.Extensions.FreeVolume.certified_region_volume_lower_bound
#print axioms PackingCertificates.Extensions.FreeVolume.certified_region_positive_volume
#print axioms PackingCertificates.Extensions.FreeVolume.feasible_translation_outer_volume_lower_bound
#print axioms PackingCertificates.Extensions.FreeVolume.exists_positive_measurable_feasible_region
#print axioms PackingCertificates.Extensions.FreeVolume.zero_radius_has_zero_volume
#print axioms PackingCertificates.Extensions.FreeVolume.negative_radius_has_zero_volume
#print axioms PackingCertificates.Extensions.FreeVolume.signed_translation_bound
#print axioms PackingCertificates.Extensions.FreeVolume.two_interval_positive_free_volume
#print axioms PackingCertificates.Extensions.FreeVolume.exact_fit_witness_has_zero_free_volume
