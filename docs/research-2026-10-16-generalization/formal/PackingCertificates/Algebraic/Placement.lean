import PackingCertificates.Rational
import PackingCertificates.Algebraic.Simplex

/-!
Rational rigid-map and container-normalization interval bounds. The template
vertices enclosed by these operations remain exact real algebraic vertices;
interval endpoints do not replace their geometry.
-/

namespace PackingCertificates.Algebraic.Placement

open PackingCertificates.Rational
open scoped BigOperators

def dotInterval {d : ℕ} (u : QPoint d) (vI : Fin d → Interval) : Interval :=
  Simplex.sumFiniteInterval (fun a => Interval.mul (Interval.point (u a)) (vI a))

theorem dotInterval_sound {d : ℕ} (u : QPoint d) (vI : Fin d → Interval)
    (v : RPoint d) (h : ∀ a, (vI a).Contains (v a)) :
    (dotInterval u vI).Contains (realLinear u v) := by
  have hh := Simplex.sumFiniteInterval_sound
    (fun a => Interval.mul (Interval.point (u a)) (vI a))
    (fun a => (u a : ℝ)*v a)
    (fun a => Interval.mul_sound (Interval.point_sound (u a)) (h a))
  simpa [dotInterval,realLinear] using hh

def affineVertexInterval {d : ℕ} (R : Fin d → QPoint d) (c : QPoint d)
    (vI : Fin d → Interval) : Fin d → Interval :=
  fun a => Interval.add (Interval.point (c a)) (dotInterval (R a) vI)

theorem affineVertexInterval_sound {d : ℕ} (R : Fin d → QPoint d)
    (c : QPoint d) (vI : Fin d → Interval) (v : RPoint d)
    (h : ∀ a, (vI a).Contains (v a)) :
    ∀ a, (affineVertexInterval R c vI a).Contains (placementAffine R c v a) := by
  intro a
  have hh := Interval.add_sound (Interval.point_sound (c a)) (dotInterval_sound (R a) vI v h)
  simpa [affineVertexInterval,placementAffine,realRotation,realPoint,add_comm] using hh

def normalizedInterval {d : ℕ} (s : ℚ) (cc : QPoint d)
    (pI : Fin d → Interval) : Fin d → Interval :=
  fun a => Interval.mul (Interval.point (1/s)) (Interval.sub (pI a) (Interval.point (cc a)))

noncomputable def normalizedPoint {d : ℕ} (s : ℚ) (cc : QPoint d) (p : RPoint d) : RPoint d :=
  fun a => (p a-(cc a : ℝ))/(s : ℝ)

/-- This enclosure is valid even at s=0 under the field's total division.
The geometric undo theorem below separately requires a nonzero scale. -/
theorem normalizedInterval_sound {d : ℕ} (s : ℚ) (cc : QPoint d)
    (pI : Fin d → Interval) (p : RPoint d)
    (h : ∀ a, (pI a).Contains (p a)) :
    ∀ a, (normalizedInterval s cc pI a).Contains (normalizedPoint s cc p a) := by
  intro a
  have hh := Interval.mul_sound (Interval.point_sound (1/s))
    (Interval.sub_sound (h a) (Interval.point_sound (cc a)))
  simpa [normalizedInterval,normalizedPoint,div_eq_mul_inv,mul_comm] using hh

def affineContainerMap {d : ℕ} (c : QPoint d) (s : ℚ) (x : RPoint d) : RPoint d :=
  realPoint c + (s : ℝ) • x

theorem normalization_undo {d : ℕ} (s : ℚ) (hs : s ≠ 0)
    (cc : QPoint d) (p : RPoint d) :
    affineContainerMap cc s (normalizedPoint s cc p) = p := by
  have hs' : (s : ℝ) ≠ 0 := by exact_mod_cast hs
  funext a
  change (cc a : ℝ)+(s : ℝ)*((p a-(cc a : ℝ))/(s : ℝ)) = p a
  rw [mul_div_cancel₀ _ hs']
  ring

theorem affineContainerMap_body {d k : ℕ} (c : QPoint d) (s : ℚ)
    (v : Fin k → RPoint d) :
    affineContainerMap c s '' vertexBody v =
      vertexBody (fun i => affineContainerMap c s (v i)) := by
  let f : RPoint d →ᵃ[ℝ] RPoint d :=
    ((s : ℝ) • (LinearMap.id : RPoint d →ₗ[ℝ] RPoint d)).toAffineMap +
      AffineMap.const ℝ _ (realPoint c)
  have h := affine_placement_of_vertex_body v f
  simpa [f,affineContainerMap,Function.comp_def,add_comm] using h

/-- Normalized containment of every vertex yields containment of the entire
piece hull in the affine image of the actual container hull. -/
theorem normalized_vertices_imply_containment {d k l : ℕ}
    (v : Fin k → RPoint d) (containerVertices : Fin l → RPoint d)
    (cc : QPoint d) (s : ℚ) (hs : s ≠ 0)
    (h : ∀ i, normalizedPoint s cc (v i) ∈ vertexBody containerVertices) :
    vertexBody v ⊆ affineContainerMap cc s '' vertexBody containerVertices := by
  have himage := affineContainerMap_body cc s containerVertices
  rw [himage]
  apply convexHull_min
  · rintro x ⟨i,rfl⟩
    have hi : v i ∈ affineContainerMap cc s '' vertexBody containerVertices :=
      ⟨normalizedPoint s cc (v i),h i,normalization_undo s hs cc (v i)⟩
    rwa [himage] at hi
  · exact convex_convexHull ℝ _

end PackingCertificates.Algebraic.Placement

#print axioms PackingCertificates.Algebraic.Placement.dotInterval_sound
#print axioms PackingCertificates.Algebraic.Placement.affineVertexInterval_sound
#print axioms PackingCertificates.Algebraic.Placement.normalizedInterval_sound
#print axioms PackingCertificates.Algebraic.Placement.normalization_undo
#print axioms PackingCertificates.Algebraic.Placement.affineContainerMap_body
#print axioms PackingCertificates.Algebraic.Placement.normalized_vertices_imply_containment
