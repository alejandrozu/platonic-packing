import PackingCertificates.Rational
import Mathlib.Analysis.Convex.Combination

/-!
# Exact rational convex-combination containment certificates

Halfspace descriptions need not be identified with vertex hulls here. Each
placed template vertex is instead checked to be an explicit nonnegative
convex combination of vertices of the actual scaled and translated container.
The sparse width is an independent parameter; unused slots may have zero
weight. The checker covers every piece, vertex, weight and coordinate.
-/

namespace PackingCertificates.Barycentric

open Set
open PackingCertificates.Rational
open scoped BigOperators

structure Certificate (d n k l t : ℕ) where
  placement : PlacementCertificate d n k 0
  containerVertices : Fin l → QPoint d
  scale : ℚ
  containerCenter : QPoint d
  indices : Fin n → Fin k → Fin t → Fin l
  weights : Fin n → Fin k → Fin t → ℚ

def Certificate.scaledVertex {d n k l t : ℕ} (c : Certificate d n k l t)
    (j : Fin l) : QPoint d :=
  fun a => c.containerCenter a + c.scale * c.containerVertices j a

noncomputable def Certificate.containerBody {d n k l t : ℕ}
    (c : Certificate d n k l t) : Set (RPoint d) :=
  vertexBody (fun j => realPoint (c.scaledVertex j))

def Certificate.vertexCheck {d n k l t : ℕ} (c : Certificate d n k l t)
    (i : Fin n) (p : Fin k) : Bool :=
  allFin t (fun z => decide (0 ≤ c.weights i p z)) &&
  decide ((∑ z, c.weights i p z) = 1) &&
  allFin d (fun a => decide (c.placement.toCertificate.vertices i p a =
    ∑ z, c.weights i p z * c.scaledVertex (c.indices i p z) a))

/-- All geometric arithmetic is rational and kernel-reducible. -/
def check {d n k l t : ℕ} (c : Certificate d n k l t) : Bool :=
  checkPlaced c.placement && decide (0 < c.scale) &&
    allFin n (fun i => allFin k (fun p => c.vertexCheck i p))

theorem vertexCheck_sound {d n k l t : ℕ} (c : Certificate d n k l t)
    (i : Fin n) (p : Fin k) (h : c.vertexCheck i p = true) :
    realPoint (c.placement.toCertificate.vertices i p) ∈ c.containerBody := by
  simp only [Certificate.vertexCheck, Bool.and_eq_true, allFin_eq_true,
    decide_eq_true_eq] at h
  have hw : ∀ z : Fin t, 0 ≤ (c.weights i p z : ℝ) := by
    intro z
    exact_mod_cast h.1.1 z
  have hs : (∑ z : Fin t, (c.weights i p z : ℝ)) = 1 := by
    exact_mod_cast h.1.2
  have hm : (∑ z : Fin t, (c.weights i p z : ℝ) •
      realPoint (c.scaledVertex (c.indices i p z))) ∈ c.containerBody := by
    apply (convex_convexHull ℝ _).sum_mem (fun z _ => hw z) hs
    intro z _
    apply subset_convexHull ℝ
    exact ⟨c.indices i p z, rfl⟩
  have heq : realPoint (c.placement.toCertificate.vertices i p) =
      ∑ z : Fin t, (c.weights i p z : ℝ) •
        realPoint (c.scaledVertex (c.indices i p z)) := by
    ext a
    simp only [realPoint, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]
    exact_mod_cast h.2 a
  rw [heq]
  exact hm

/-- The semantic conclusions mention the actual scaled vertex hull, complete
placed template bodies, and squared Euclidean distances. No equivalence
between an external halfspace description and that hull is assumed. -/
def Valid {d n k l t : ℕ} (c : Certificate d n k l t) : Prop :=
  (0 < (c.scale : ℝ)) ∧
  (∀ i a b, realLinear (c.placement.rotation i a)
      (realPoint (c.placement.rotation i b)) = if a = b then (1 : ℝ) else 0) ∧
  (∀ i (x y : RPoint d),
    (∑ a, (placementAffine (c.placement.rotation i) (c.placement.center i) x a -
      placementAffine (c.placement.rotation i) (c.placement.center i) y a) ^ 2) =
      ∑ a, (x a - y a) ^ 2) ∧
  (∀ i, placementAffine (c.placement.rotation i) (c.placement.center i) ''
      vertexBody (fun p => realPoint (c.placement.template p)) ⊆ c.containerBody) ∧
  Pairwise (fun i j => Disjoint
    (placementAffine (c.placement.rotation i) (c.placement.center i) ''
      vertexBody (fun p => realPoint (c.placement.template p)))
    (placementAffine (c.placement.rotation j) (c.placement.center j) ''
      vertexBody (fun p => realPoint (c.placement.template p))))

theorem check_sound {d n k l t : ℕ} (c : Certificate d n k l t)
    (h : check c = true) : Valid c := by
  have hh : (checkPlaced c.placement = true ∧ 0 < c.scale) ∧
      ∀ i p, c.vertexCheck i p = true := by
    simpa only [check, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq] using h
  have hp := checkPlaced_sound c.placement hh.1.1
  refine ⟨?_, hp.1, ?_, ?_, hp.2.2⟩
  · exact_mod_cast hh.1.2
  · intro i x y
    exact checkPlaced_preserves_squared_distance c.placement hh.1.1 i x y
  · intro i
    rw [placement_body]
    apply convexHull_min
    · rintro _ ⟨p, rfl⟩
      exact vertexCheck_sound c i p (hh.2 i p)
    · exact convex_convexHull ℝ _

end PackingCertificates.Barycentric
