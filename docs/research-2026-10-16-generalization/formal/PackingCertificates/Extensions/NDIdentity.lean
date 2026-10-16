import PackingCertificates.Extensions.NDGeometry

/-!
Identify the frozen orthoplex vertex arrays with the standard convex hull of
the positive and negative coordinate basis. This leaf module leaves every
previously pinned certificate dependency unchanged.
-/
namespace PackingCertificates.Extensions.NDIdentity
open PackingCertificates
open PackingCertificates.Rational
open PackingCertificates.Extensions.NDGeometry
open scoped BigOperators

theorem qtemplate_subset_crossBody {d k : ℕ} (hd : 0 < d)
    (v : Fin k → QPoint d) (h : ∀ i, (∑ a, |v i a|) ≤ 1) :
    vertexBody (fun i => realPoint (v i)) ⊆ crossBody d := by
  change convexHull ℝ (Set.range (fun i => realPoint (v i))) ⊆ crossBody d
  apply convexHull_min ?_ (convex_convexHull ℝ _)
  rintro _ ⟨i, rfl⟩
  apply mem_crossBody_of_sum_abs_le hd
  change (∑ a, |(v i a : ℝ)|) ≤ 1
  exact_mod_cast h i

theorem c16_l1 : ∀ i : Fin 8, (∑ a : Fin 4, |TemplateData.c16.getD i.val 0 a|) ≤ 1 := by
  decide +kernel

theorem op5_l1 : ∀ i : Fin 10, (∑ a : Fin 5, |TemplateData.op5.getD i.val 0 a|) ≤ 1 := by
  decide +kernel

theorem op6_l1 : ∀ i : Fin 12, (∑ a : Fin 6, |TemplateData.op6.getD i.val 0 a|) ≤ 1 := by
  decide +kernel

theorem c16_hull_eq :
    vertexBody (fun i : Fin 8 => realPoint (TemplateData.c16.getD i.val 0)) = crossBody 4 :=
  Set.Subset.antisymm (qtemplate_subset_crossBody (by decide) _ c16_l1) c16_body_contains

theorem op5_hull_eq :
    vertexBody (fun i : Fin 10 => realPoint (TemplateData.op5.getD i.val 0)) = crossBody 5 :=
  Set.Subset.antisymm (qtemplate_subset_crossBody (by decide) _ op5_l1) op5_body_contains

theorem op6_hull_eq :
    vertexBody (fun i : Fin 12 => realPoint (TemplateData.op6.getD i.val 0)) = crossBody 6 :=
  Set.Subset.antisymm (qtemplate_subset_crossBody (by decide) _ op6_l1) op6_body_contains

abbrev Root24Index := {p : (Fin 4 × Fin 4) × (Bool × Bool) // p.1.1 ≠ p.1.2}

def qroot24 (p : Root24Index) : QPoint 4 :=
  Pi.single p.val.1.1 (if p.val.2.1 then 1 else -1) +
    Pi.single p.val.1.2 (if p.val.2.2 then 1 else -1)

noncomputable def root24Body : Set (RPoint 4) :=
  convexHull ℝ (Set.range (fun p : Root24Index => realPoint (qroot24 p)))

theorem c24_within : ∀ i : Fin 24, ∃ p : Root24Index,
    TemplateData.c24.getD i.val 0 = qroot24 p := by
  decide +kernel

theorem c24_covers : ∀ p : Root24Index, ∃ i : Fin 24,
    TemplateData.c24.getD i.val 0 = qroot24 p := by
  decide +kernel

theorem c24_hull_eq :
    vertexBody (fun i : Fin 24 => realPoint (TemplateData.c24.getD i.val 0)) = root24Body := by
  have hr : Set.range (fun i : Fin 24 => realPoint (TemplateData.c24.getD i.val 0)) =
      Set.range (fun p : Root24Index => realPoint (qroot24 p)) := by
    apply Set.Subset.antisymm
    · rintro _ ⟨i, rfl⟩
      obtain ⟨p, hp⟩ := c24_within i
      exact ⟨p, congrArg realPoint hp.symm⟩
    · rintro _ ⟨p, rfl⟩
      obtain ⟨i, hi⟩ := c24_covers p
      exact ⟨i, congrArg realPoint hi⟩
  change convexHull ℝ (Set.range (fun i : Fin 24 => realPoint (TemplateData.c24.getD i.val 0))) =
    convexHull ℝ (Set.range (fun p : Root24Index => realPoint (qroot24 p)))
  rw [hr]

#print axioms qtemplate_subset_crossBody
#print axioms c16_l1
#print axioms op5_l1
#print axioms op6_l1
#print axioms c16_hull_eq
#print axioms op5_hull_eq
#print axioms op6_hull_eq
#print axioms c24_within
#print axioms c24_covers
#print axioms c24_hull_eq
end PackingCertificates.Extensions.NDIdentity
