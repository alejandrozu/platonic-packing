import PackingCertificates.BoxGeometry
import Mathlib.Analysis.Convex.Combination
import Mathlib.Algebra.BigOperators.Pi
import Mathlib.Algebra.BigOperators.Field

/-!
Support and containment geometry for canonical cross polytopes, with no bound
on dimension. These lemmas avoid a large rational barycentric witness for every
placed vertex while still concluding membership in the actual vertex hull.
-/
namespace PackingCertificates.Extensions.NDGeometry
open PackingCertificates
open PackingCertificates.Rational
open scoped BigOperators

noncomputable def crossVertex {d : ℕ} (i : Fin d × Bool) : RPoint d :=
  Pi.single i.1 (if i.2 then 1 else -1)

noncomputable def crossBody (d : ℕ) : Set (RPoint d) :=
  convexHull ℝ (Set.range (@crossVertex d))

noncomputable def signedBasis {d : ℕ} (x : RPoint d) (i : Fin d) : RPoint d :=
  Pi.single i (if 0 ≤ x i then 1 else -1)

theorem signedBasis_mem {d : ℕ} (x : RPoint d) (i : Fin d) :
    signedBasis x i ∈ crossBody d := by
  apply subset_convexHull ℝ
  refine ⟨(i, decide (0 ≤ x i)), ?_⟩
  simp [crossVertex, signedBasis]

theorem signedBasis_coefficient {d : ℕ} (x : RPoint d) (i : Fin d) :
    |x i| • signedBasis x i = Pi.single i (x i) := by
  classical
  ext a
  by_cases ha : a = i
  · subst a
    by_cases hi : 0 ≤ x i
    · simp [signedBasis, Pi.single_apply, hi, abs_of_nonneg hi]
    · simp [signedBasis, Pi.single_apply, hi, abs_of_neg (lt_of_not_ge hi)]
  · simp [signedBasis, Pi.single_apply, ha, Ne.symm ha]

theorem zero_mem_crossBody {d : ℕ} (hd : 0 < d) :
    (0 : RPoint d) ∈ crossBody d := by
  let i : Fin d := ⟨0, hd⟩
  have hp : crossVertex (i, true) ∈ crossBody d :=
    subset_convexHull ℝ _ ⟨(i, true), rfl⟩
  have hn : crossVertex (i, false) ∈ crossBody d :=
    subset_convexHull ℝ _ ⟨(i, false), rfl⟩
  have h := (convex_convexHull ℝ _ ) hp hn
    (show (0 : ℝ) ≤ 1/2 by norm_num) (show (0 : ℝ) ≤ 1/2 by norm_num)
    (show (1/2 : ℝ) + 1/2 = 1 by norm_num)
  have heq : (1/2 : ℝ) • crossVertex (i, true) +
      (1/2 : ℝ) • crossVertex (i, false) = 0 := by
    ext a
    classical
    by_cases ha : a = i
    · subst a
      norm_num [crossVertex]
    · simp [crossVertex, ha, Ne.symm ha]
  rw [heq] at h
  exact h

/-- The usual L1 test gives membership in the actual ±basis vertex hull in
every positive finite dimension. -/
theorem mem_crossBody_of_sum_abs_le {d : ℕ} (hd : 0 < d) (x : RPoint d)
    (hx : (∑ a, |x a|) ≤ 1) : x ∈ crossBody d := by
  classical
  let w : Fin (d+1) → ℝ := Fin.cases (1 - ∑ a, |x a|) (fun a => |x a|)
  let z : Fin (d+1) → RPoint d := Fin.cases 0 (signedBasis x)
  have hw : ∀ i, 0 ≤ w i := by
    intro i
    refine Fin.cases ?_ (fun a => ?_) i
    · exact sub_nonneg.mpr hx
    · exact abs_nonneg _
  have hs : (∑ i, w i) = 1 := by
    rw [Fin.sum_univ_succ]
    simp [w]
  have hz : ∀ i, z i ∈ crossBody d := by
    intro i
    refine Fin.cases ?_ (fun a => ?_) i
    · exact zero_mem_crossBody hd
    · exact signedBasis_mem x a
  have hm := (convex_convexHull ℝ (Set.range (@crossVertex d))).sum_mem
    (fun i _ => hw i) hs (fun i _ => hz i)
  have heq : (∑ i, w i • z i) = x := by
    rw [Fin.sum_univ_succ]
    simp only [w, z, Fin.cases_zero, smul_zero, Fin.cases_succ, zero_add]
    simp_rw [signedBasis_coefficient]
    exact Finset.univ_sum_single x
  rwa [heq] at hm

theorem mem_scaled_crossBody_of_sum_abs_le {d : ℕ} (hd : 0 < d)
    (c x : RPoint d) (s : ℝ) (hs : 0 < s)
    (hx : (∑ a, |x a - c a|) ≤ s) :
    x ∈ (fun y : RPoint d => c + s • y) '' crossBody d := by
  refine ⟨fun a => (x a-c a)/s, ?_, ?_⟩
  · apply mem_crossBody_of_sum_abs_le hd
    simp only [abs_div, abs_of_pos hs, ← Finset.sum_div]
    exact (div_le_one hs).mpr hx
  · funext a
    change c a + s * ((x a-c a)/s) = x a
    rw [mul_div_cancel₀ _ (ne_of_gt hs)]
    ring

def crossIndex {d : ℕ} (p : Fin d × Bool) : Fin (2*d) :=
  ⟨(2*p.1.val + if p.2 then 0 else 1) % (2*d),
    Nat.mod_lt _ (Nat.mul_pos (by decide)
      (lt_of_le_of_lt (Nat.zero_le p.1.val) p.1.isLt))⟩

def qcrossVertex {d : ℕ} (p : Fin d × Bool) : QPoint d :=
  Pi.single p.1 (if p.2 then 1 else -1)

theorem realPoint_qcrossVertex {d : ℕ} (p : Fin d × Bool) :
    realPoint (qcrossVertex p) = crossVertex p := by
  classical
  ext a
  by_cases ha : a = p.1 <;> cases hb : p.2 <;>
    simp [realPoint, qcrossVertex, crossVertex, ha, hb]

theorem crossBody_subset_template {d k : ℕ} (v : Fin k → QPoint d)
    (covers : ∀ p : Fin d × Bool, ∃ i, v i = qcrossVertex p) :
    crossBody d ⊆ vertexBody (fun i => realPoint (v i)) := by
  apply convexHull_mono
  rintro _ ⟨p, rfl⟩
  obtain ⟨i, hi⟩ := covers p
  refine ⟨i, ?_⟩
  change realPoint (v i) = crossVertex p
  rw [hi, realPoint_qcrossVertex]

theorem c16_index : ∀ p : Fin 4 × Bool, ∀ a : Fin 4,
    TemplateData.c16.getD (crossIndex p).val 0 a = qcrossVertex p a := by decide +kernel

theorem op5_index : ∀ p : Fin 5 × Bool, ∀ a : Fin 5,
    TemplateData.op5.getD (crossIndex p).val 0 a = qcrossVertex p a := by decide +kernel

theorem op6_index : ∀ p : Fin 6 × Bool, ∀ a : Fin 6,
    TemplateData.op6.getD (crossIndex p).val 0 a = qcrossVertex p a := by decide +kernel

theorem c16_body_contains : crossBody 4 ⊆
    vertexBody (fun i : Fin 8 => realPoint (TemplateData.c16.getD i.val 0)) :=
  crossBody_subset_template _ (fun p => ⟨crossIndex p, funext (c16_index p)⟩)

theorem op5_body_contains : crossBody 5 ⊆
    vertexBody (fun i : Fin 10 => realPoint (TemplateData.op5.getD i.val 0)) :=
  crossBody_subset_template _ (fun p => ⟨crossIndex p, funext (op5_index p)⟩)

theorem op6_body_contains : crossBody 6 ⊆
    vertexBody (fun i : Fin 12 => realPoint (TemplateData.op6.getD i.val 0)) :=
  crossBody_subset_template _ (fun p => ⟨crossIndex p, funext (op6_index p)⟩)

theorem image_vertexBody_scale {d k : ℕ} (v : Fin k → RPoint d)
    (c : RPoint d) (s : ℝ) :
    (fun x : RPoint d => c+s • x) '' vertexBody v =
      vertexBody (fun i => c+s • v i) := by
  let f : RPoint d →ᵃ[ℝ] RPoint d :=
    (s • (LinearMap.id : RPoint d →ₗ[ℝ] RPoint d)).toAffineMap +
      AffineMap.const ℝ _ c
  have h := affine_placement_of_vertex_body v f
  simpa [f, Function.comp_def, add_comm] using h

theorem scaled_cross_template_contains {d k : ℕ} (hd : 0 < d)
    (v : Fin k → QPoint d)
    (covers : ∀ p : Fin d × Bool, ∃ i, v i = qcrossVertex p)
    (c x : RPoint d) (s : ℝ) (hs : 0 < s)
    (hx : (∑ a, |x a-c a|) ≤ s) :
    x ∈ vertexBody (fun i => c+s • realPoint (v i)) := by
  have h := mem_scaled_crossBody_of_sum_abs_le hd c x s hs hx
  have hi := Set.image_mono (crossBody_subset_template v covers)
    (f := fun y : RPoint d => c+s • y) h
  rwa [image_vertexBody_scale] at hi

/-- A small exact-rational L1 test certifies the actual scaled canonical
container hull; it does not treat an unproved facet description as a hull. -/
theorem q_l1_contains {d k : ℕ} (hd : 0 < d) (v : Fin k → QPoint d)
    (covers : ∀ p : Fin d × Bool, ∃ i, v i = qcrossVertex p)
    (c x : QPoint d) (s : ℚ) (hs : 0 < s)
    (hx : (∑ a, |x a-c a|) ≤ s) :
    realPoint x ∈ vertexBody
      (fun i => realPoint (fun a => c a+s*v i a)) := by
  have hsR : (0 : ℝ) < s := by exact_mod_cast hs
  have hxR : (∑ a, |(x a : ℝ)-(c a : ℝ)|) ≤ (s : ℝ) := by exact_mod_cast hx
  have h := scaled_cross_template_contains hd v covers (realPoint c) (realPoint x)
    (s : ℝ) hsR hxR
  have heq : (fun i => realPoint c + (s : ℝ) • realPoint (v i)) =
      (fun i => realPoint (fun a => c a+s*v i a)) := by
    funext i a
    simp [realPoint, Rat.cast_add, Rat.cast_mul]
  rw [heq] at h
  exact h

#print axioms signedBasis_coefficient
#print axioms zero_mem_crossBody
#print axioms mem_crossBody_of_sum_abs_le
#print axioms mem_scaled_crossBody_of_sum_abs_le
#print axioms c16_body_contains
#print axioms op5_body_contains
#print axioms op6_body_contains
#print axioms image_vertexBody_scale
#print axioms scaled_cross_template_contains
#print axioms q_l1_contains
end PackingCertificates.Extensions.NDGeometry
