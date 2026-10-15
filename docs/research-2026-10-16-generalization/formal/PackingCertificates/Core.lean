import Mathlib.Analysis.Convex.Hull
import Mathlib.Data.Real.Basic

/-!
# Dimension-independent certificate soundness for convex packing

These proofs concern the geometric meaning of exact finite witnesses. They do
not verify a floating-point search, establish optimality, or import the site's
JSON files. A strictly positive separating gap gives disjoint closed bodies,
which is stronger than the disjoint-interior condition required for a packing.
-/

namespace PackingCertificates

open Set
open scoped Pointwise

variable {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- A finite vertex list denotes its real convex hull, not just its vertices. -/
def vertexBody {k : ℕ} (v : Fin k → E) : Set E :=
  convexHull ℝ (Set.range v)

/-- A closed halfspace, with the normal represented as a linear functional. -/
structure Halfspace (E : Type*) [AddCommGroup E] [Module ℝ E] where
  normal : E →ₗ[ℝ] ℝ
  offset : ℝ

/-- A finite intersection of closed halfspaces. -/
def container {m : ℕ} (walls : Fin m → Halfspace E) : Set E :=
  {x | ∀ f, (walls f).normal x ≤ (walls f).offset}

/-- Checking a linear inequality on every vertex checks the entire polytope. -/
theorem hull_le_of_vertices_le {s : Set E} (a : E →ₗ[ℝ] ℝ) (b : ℝ)
    (h : ∀ x ∈ s, a x ≤ b) :
    ∀ x ∈ convexHull ℝ s, a x ≤ b := by
  exact convexHull_min h ((convex_Iic b).linear_preimage a)

theorem hull_ge_of_vertices_ge {s : Set E} (a : E →ₗ[ℝ] ℝ) (b : ℝ)
    (h : ∀ x ∈ s, b ≤ a x) :
    ∀ x ∈ convexHull ℝ s, b ≤ a x := by
  exact convexHull_min h ((convex_Ici b).linear_preimage a)

/-- Finite vertex/face tests imply containment of the whole solid. -/
theorem vertex_tests_imply_containment {k m : ℕ}
    (v : Fin k → E) (walls : Fin m → Halfspace E)
    (h : ∀ i f, (walls f).normal (v i) ≤ (walls f).offset) :
    vertexBody v ⊆ container walls := by
  intro x hx f
  exact hull_le_of_vertices_le (walls f).normal (walls f).offset
    (by rintro _ ⟨i, rfl⟩; exact h i f) x hx

/-- A positive gap between vertex projections separates the full convex hulls. -/
theorem separating_vertex_tests_imply_disjoint {s t : Set E}
    (a : E →ₗ[ℝ] ℝ) (l u : ℝ) (gap : l < u)
    (left : ∀ x ∈ s, a x ≤ l) (right : ∀ y ∈ t, u ≤ a y) :
    Disjoint (convexHull ℝ s) (convexHull ℝ t) := by
  apply Set.disjoint_left.mpr
  intro x hx hy
  have hl := hull_le_of_vertices_le a l left x hx
  have hu := hull_ge_of_vertices_ge a u right x hy
  exact (not_lt_of_ge (le_trans hu hl)) gap

/-- Exact finite data and their finite inequalities. Different pieces may have
different numbers of vertices, and `E` is not restricted to dimension three. -/
structure FinitePackingCertificate {n m : ℕ} (k : Fin n → ℕ)
    (v : (i : Fin n) → Fin (k i) → E)
    (walls : Fin m → Halfspace E) where
  wall_tests : ∀ i p f, (walls f).normal (v i p) ≤ (walls f).offset
  pair_tests : ∀ i j, i ≠ j →
    ∃ (a : E →ₗ[ℝ] ℝ) (l u : ℝ), l < u ∧
      (∀ p, a (v i p) ≤ l) ∧ (∀ q, u ≤ a (v j q))

/-- Kernel-checked soundness of finite containment and separation certificates. -/
theorem finite_certificate_sound {n m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → E} {walls : Fin m → Halfspace E}
    (c : FinitePackingCertificate k v walls) :
    (∀ i, vertexBody (v i) ⊆ container walls) ∧
      Pairwise (fun i j => Disjoint (vertexBody (v i)) (vertexBody (v j))) := by
  constructor
  · intro i
    exact vertex_tests_imply_containment (v i) walls (c.wall_tests i)
  · intro i j hij
    obtain ⟨a, l, u, hgap, hl, hu⟩ := c.pair_tests i j hij
    exact separating_vertex_tests_imply_disjoint a l u hgap
      (by rintro _ ⟨p, rfl⟩; exact hl p)
      (by rintro _ ⟨q, rfl⟩; exact hu q)

/-- Affine placements commute with the vertex representation. In particular,
translations, positive scales and rotations fit this interface. -/
theorem affine_placement_of_vertex_body {F : Type*} [AddCommGroup F] [Module ℝ F]
    {k : ℕ} (v : Fin k → E) (f : E →ᵃ[ℝ] F) :
    f '' vertexBody v = vertexBody (f ∘ v) := by
  rw [vertexBody, f.image_convexHull]
  congr 1
  exact Set.range_comp f v |>.symm

omit [AddCommGroup E] [Module ℝ E] in
/-- An outer approximation remains an outer approximation after placement.
This is the inclusion step used by rounded/offset template certificates. -/
theorem placed_outer_approximation {F : Type*} {P Q : Set E}
    (h : P ⊆ Q) (f : E → F) : f '' P ⊆ f '' Q :=
  Set.image_mono h

/-- Erosion by a structuring body. Taking that body to be a radius-`r` ball
gives the inner parallel body used by the general rounded-body opening. -/
def erosion (P K : Set E) : Set E :=
  {x | ∀ b ∈ K, x + b ∈ P}

/-- Minkowski opening `(P ⊖ K) ⊕ K`. No tangency assumption is needed. -/
def minkowskiOpening (P K : Set E) : Set E :=
  erosion P K + K

omit [Module ℝ E] in
/-- Rounded opening cannot protrude outside the original body, in any
dimension and even without convexity assumptions. -/
theorem minkowskiOpening_subset (P K : Set E) :
    minkowskiOpening P K ⊆ P := by
  rintro _ ⟨a, ha, b, hb, rfl⟩
  exact ha b hb

omit [Module ℝ E] in
theorem minkowskiOpening_mono {P Q : Set E} (K : Set E) (h : P ⊆ Q) :
    minkowskiOpening P K ⊆ minkowskiOpening Q K := by
  rintro _ ⟨a, ha, b, hb, rfl⟩
  exact ⟨a, fun z hz => h (ha z hz), b, hb, rfl⟩

/-- Convex blending with an inscribed body stays inside the target body.
For `Q = ρ B`, `a = 1 - τ` and `b = τ`, this is the fundamental containment
fact for `H_τ = (1-τ) P + τ ρ B`, including non-tangential polyhedra. -/
theorem convex_blend_subset {P Q : Set E} (hP : Convex ℝ P) (hQ : Q ⊆ P)
    (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : a + b = 1) :
    a • P + b • Q ⊆ P := by
  rintro _ ⟨_, ⟨p, hp, rfl⟩, _, ⟨q, hq, rfl⟩, rfl⟩
  exact hP hp (hQ hq) ha hb hab

omit [AddCommGroup E] [Module ℝ E] in
/-- For one template, inclusion and an injective placement transport a packing
into a new ambient container. The positivity/injectivity of a scale or rigid
motion is a premise supplied by that placement, not assumed for arbitrary maps. -/
theorem transported_packing {F : Type*} {I : Type*}
    (pieces : I → Set E) (C : Set E) (D : Set F) (f : E → F)
    (injective : Function.Injective f)
    (inside : ∀ i, pieces i ⊆ C)
    (separate : Pairwise (fun i j => Disjoint (pieces i) (pieces j)))
    (outer : f '' C ⊆ D) :
    (∀ i, f '' pieces i ⊆ D) ∧
      Pairwise (fun i j => Disjoint (f '' pieces i) (f '' pieces j)) := by
  constructor
  · intro i
    exact (Set.image_mono (inside i)).trans outer
  · intro i j hij
    apply Set.disjoint_left.mpr
    rintro _ ⟨x, hx, rfl⟩ ⟨y, hy, heq⟩
    have hxy : y = x := injective heq
    exact Set.disjoint_left.mp (separate hij) hx (hxy ▸ hy)

omit [AddCommGroup E] [Module ℝ E] in
/-- Replacing each member of a packing by a subset cannot break containment or
separation. This is the soundness step for deleting pieces and nested layouts. -/
theorem subpacking_sound {I : Type*} (parent child : I → Set E) (C : Set E)
    (refines : ∀ i, child i ⊆ parent i)
    (inside : ∀ i, parent i ⊆ C)
    (separate : Pairwise (fun i j => Disjoint (parent i) (parent j))) :
    (∀ i, child i ⊆ C) ∧
      Pairwise (fun i j => Disjoint (child i) (child j)) := by
  constructor
  · intro i
    exact (refines i).trans (inside i)
  · intro i j hij
    exact (separate hij).mono (refines i) (refines j)

omit [AddCommGroup E] [Module ℝ E] in
/-- Full nested composition: any number of disjoint children in each parent,
with parents themselves disjoint, gives a single packing indexed by `I × J`.
Together with `transported_packing`, this certifies hierarchical placements. -/
theorem nested_packing_sound {I J : Type*} (parent : I → Set E)
    (child : I → J → Set E) (C : Set E)
    (inside_parent : ∀ i, parent i ⊆ C)
    (inside_child : ∀ i j, child i j ⊆ parent i)
    (parent_separate : Pairwise (fun i k => Disjoint (parent i) (parent k)))
    (child_separate : ∀ i, Pairwise (fun j l => Disjoint (child i j) (child i l))) :
    (∀ p : I × J, child p.1 p.2 ⊆ C) ∧
      Pairwise (fun p q : I × J => Disjoint (child p.1 p.2) (child q.1 q.2)) := by
  constructor
  · rintro ⟨i, j⟩
    exact (inside_child i j).trans (inside_parent i)
  · rintro ⟨i, j⟩ ⟨k, l⟩ hne
    by_cases hik : i = k
    · subst k
      apply child_separate i
      intro hjl
      exact hne (by cases hjl; rfl)
    · exact (parent_separate hik).mono (inside_child i j) (inside_child k l)

end PackingCertificates

