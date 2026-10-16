import PackingCertificates.Core
import Mathlib.LinearAlgebra.Pi
import Mathlib.Data.List.FinRange
import Mathlib.Data.Rat.Cast.Order
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-!
# Kernel-reducible exact rational packing certificates

The finite data are typed by dimension, piece count, vertex count and wall
count. The checker covers every vertex/wall inequality and every unordered
pair, so missing or duplicate input plane lists cannot silently skip a pair.
`by decide +kernel` evaluates exact rational arithmetic inside Lean's kernel;
this module does not use native decision procedures or additional axioms.
-/

namespace PackingCertificates.Rational

open Set
open scoped BigOperators

abbrev QPoint (d : ℕ) := Fin d → ℚ
abbrev RPoint (d : ℕ) := Fin d → ℝ

def qdot {d : ℕ} (a x : QPoint d) : ℚ := ∑ t, a t * x t

def realPoint {d : ℕ} (x : QPoint d) : RPoint d := fun t => (x t : ℝ)

noncomputable def realLinear {d : ℕ} (a : QPoint d) : RPoint d →ₗ[ℝ] ℝ :=
  ∑ t, (a t : ℝ) • LinearMap.proj t

theorem realLinear_realPoint {d : ℕ} (a x : QPoint d) :
    realLinear a (realPoint x) = (qdot a x : ℝ) := by
  simp [realLinear, realPoint, qdot, Rat.cast_sum, Rat.cast_mul]

structure QHalfspace (d : ℕ) where
  normal : QPoint d
  offset : ℚ

structure QPlane (d : ℕ) where
  normal : QPoint d
  lower : ℚ
  upper : ℚ

noncomputable def QHalfspace.toReal {d : ℕ} (h : QHalfspace d) : Halfspace (RPoint d) :=
  ⟨realLinear h.normal, (h.offset : ℝ)⟩

structure Certificate (d n k m : ℕ) where
  vertices : Fin n → Fin k → QPoint d
  walls : Fin m → QHalfspace d
  separation : Fin n → Fin n → QPlane d

/-- Kernel-reducible finite universal quantification. -/
def allFin (n : ℕ) (p : Fin n → Bool) : Bool := (List.finRange n).all p

theorem allFin_eq_true {n : ℕ} {p : Fin n → Bool} :
    allFin n p = true ↔ ∀ i, p i = true := by
  simp [allFin, List.all_eq_true]

def planeCheck {d k : ℕ} (v w : Fin k → QPoint d) (p : QPlane d) : Bool :=
  decide (p.lower < p.upper) &&
    allFin k (fun t => decide (qdot p.normal (v t) ≤ p.lower)) &&
    allFin k (fun t => decide (p.upper ≤ qdot p.normal (w t)))

/-- Strict positive gaps prove disjoint closed bodies, not merely disjoint
interiors. All arithmetic comparisons use exact rational numbers. -/
def check {d n k m : ℕ} (c : Certificate d n k m) : Bool :=
  allFin n (fun i => allFin k (fun p => allFin m
    (fun f => decide (qdot (c.walls f).normal (c.vertices i p) ≤ (c.walls f).offset)))) &&
  allFin n (fun i => allFin n (fun j =>
    if i < j then planeCheck (c.vertices i) (c.vertices j) (c.separation i j) else true))

theorem planeCheck_sound {d k : ℕ} {v w : Fin k → QPoint d} {p : QPlane d}
    (h : planeCheck v w p = true) :
    Disjoint (vertexBody (fun t => realPoint (v t)))
      (vertexBody (fun t => realPoint (w t))) := by
  simp only [planeCheck, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq] at h
  apply separating_vertex_tests_imply_disjoint (realLinear p.normal)
    (p.lower : ℝ) (p.upper : ℝ)
  · exact_mod_cast h.1.1
  · rintro _ ⟨t, rfl⟩
    rw [realLinear_realPoint]
    exact_mod_cast h.1.2 t
  · rintro _ ⟨t, rfl⟩
    rw [realLinear_realPoint]
    exact_mod_cast h.2 t

/-- Every successful finite rational certificate denotes a genuine packing
of its real convex-hull bodies in its real halfspace container. -/
theorem check_sound {d n k m : ℕ} (c : Certificate d n k m)
    (h : check c = true) :
    (∀ i, vertexBody (fun p => realPoint (c.vertices i p)) ⊆
      container (fun f => (c.walls f).toReal)) ∧
    Pairwise (fun i j => Disjoint (vertexBody (fun p => realPoint (c.vertices i p)))
      (vertexBody (fun p => realPoint (c.vertices j p)))) := by
  simp only [check, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq] at h
  constructor
  · intro i
    apply vertex_tests_imply_containment
    intro p f
    change realLinear (c.walls f).normal (realPoint (c.vertices i p)) ≤ _
    rw [realLinear_realPoint]
    change (qdot (c.walls f).normal (c.vertices i p) : ℝ) ≤ ((c.walls f).offset : ℝ)
    exact_mod_cast h.1 i p f
  · intro i j hij
    rcases lt_or_gt_of_ne hij with hl | hr
    · exact planeCheck_sound (by simpa [hl] using h.2 i j)
    · exact (planeCheck_sound (by simpa [hr] using h.2 j i)).symm


/-- A finite rational affine placement of one canonical template. Exact
orthogonality is checked rather than trusting the exporter or a floating-point
quaternion-to-matrix conversion. -/
structure PlacementCertificate (d n k m : ℕ) where
  template : Fin k → QPoint d
  rotation : Fin n → Fin d → QPoint d
  center : Fin n → QPoint d
  walls : Fin m → QHalfspace d
  separation : Fin n → Fin n → QPlane d

def PlacementCertificate.toCertificate {d n k m : ℕ}
    (c : PlacementCertificate d n k m) : Certificate d n k m where
  vertices i p a := qdot (c.rotation i a) (c.template p) + c.center i a
  walls := c.walls
  separation := c.separation

def orthogonalCheck {d n k m : ℕ} (c : PlacementCertificate d n k m) : Bool :=
  allFin n (fun i => allFin d (fun a => allFin d (fun b =>
    decide (qdot (c.rotation i a) (c.rotation i b) = if a = b then 1 else 0))))

def checkPlaced {d n k m : ℕ} (c : PlacementCertificate d n k m) : Bool :=
  orthogonalCheck c && check c.toCertificate

noncomputable def realRotation {d : ℕ} (r : Fin d → QPoint d) :
    RPoint d →ₗ[ℝ] RPoint d :=
  LinearMap.pi (fun a => realLinear (r a))

noncomputable def placementAffine {d : ℕ} (r : Fin d → QPoint d) (t : QPoint d) :
    RPoint d →ᵃ[ℝ] RPoint d :=
  (realRotation r).toAffineMap + AffineMap.const ℝ _ (realPoint t)

theorem placementAffine_realPoint {d : ℕ} (r : Fin d → QPoint d) (t x : QPoint d) :
    placementAffine r t (realPoint x) =
      realPoint (fun a => qdot (r a) x + t a) := by
  ext a
  simp [placementAffine, realRotation, realPoint, realLinear_realPoint]

theorem placement_body {d n k m : ℕ} (c : PlacementCertificate d n k m) (i : Fin n) :
    placementAffine (c.rotation i) (c.center i) ''
        vertexBody (fun p => realPoint (c.template p)) =
      vertexBody (fun p => realPoint (c.toCertificate.vertices i p)) := by
  rw [affine_placement_of_vertex_body]
  congr 1
  funext p
  exact placementAffine_realPoint _ _ _

/-- A successful placed certificate proves exact orthogonality of every real
matrix and certifies the full affine images of a single common template. It
therefore cannot certify arbitrarily perturbed, separately exported vertices.
Proper orientation (determinant +1) and identification of the canonical
external shape are additional record-level geometric claims. -/
theorem checkPlaced_sound {d n k m : ℕ} (c : PlacementCertificate d n k m)
    (h : checkPlaced c = true) :
    (∀ i a b, realLinear (c.rotation i a) (realPoint (c.rotation i b)) =
      if a = b then (1 : ℝ) else 0) ∧
    (∀ i, placementAffine (c.rotation i) (c.center i) ''
        vertexBody (fun p => realPoint (c.template p)) ⊆
      container (fun f => (c.walls f).toReal)) ∧
    Pairwise (fun i j => Disjoint
      (placementAffine (c.rotation i) (c.center i) ''
        vertexBody (fun p => realPoint (c.template p)))
      (placementAffine (c.rotation j) (c.center j) ''
        vertexBody (fun p => realPoint (c.template p)))) := by
  have hh : orthogonalCheck c = true ∧ check c.toCertificate = true := by
    simpa only [checkPlaced, Bool.and_eq_true] using h
  have ho := hh.1
  simp only [orthogonalCheck, allFin_eq_true, decide_eq_true_eq] at ho
  have hs := check_sound c.toCertificate hh.2
  constructor
  · intro i a b
    rw [realLinear_realPoint]
    have hq := ho i a b
    by_cases hab : a = b
    · simp only [hab, if_true] at hq ⊢
      exact_mod_cast hq
    · simp only [hab, if_false] at hq ⊢
      exact_mod_cast hq
  · constructor
    · intro i
      rw [placement_body]
      exact hs.1 i
    · intro i j hij
      rw [placement_body, placement_body]
      exact hs.2 hij

/-- In a finite square matrix, exact row orthonormality also implies column
orthonormality; consequently the real linear placement preserves the Euclidean
dot product. This avoids the sup norm on the default function-space instance. -/
theorem realRotation_preserves_dotProduct {d : ℕ} (r : Fin d → QPoint d)
    (h : ∀ a b, realLinear (r a) (realPoint (r b)) =
      if a = b then (1 : ℝ) else 0) (x y : RPoint d) :
    (∑ a, realRotation r x a * realRotation r y a) = ∑ a, x a * y a := by
  let A : Matrix (Fin d) (Fin d) ℝ := fun a b => (r a b : ℝ)
  have hrows : A * A.transpose = 1 := by
    ext a b
    simpa [A, Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply,
      realLinear, realPoint] using h a b
  have hcols : A.transpose * A = 1 := mul_eq_one_comm.mp hrows
  have happ (z : RPoint d) : realRotation r z = A.mulVec z := by
    ext a
    simp [realRotation, realLinear, A, Matrix.mulVec, dotProduct]
  rw [happ x, happ y]
  change dotProduct (A.mulVec x) (A.mulVec y) = dotProduct x y
  rw [Matrix.dotProduct_mulVec, Matrix.vecMul_mulVec, hcols, Matrix.vecMul_one]

theorem checkPlaced_preserves_dotProduct {d n k m : ℕ}
    (c : PlacementCertificate d n k m) (h : checkPlaced c = true) (i : Fin n)
    (x y : RPoint d) :
    (∑ a, realRotation (c.rotation i) x a * realRotation (c.rotation i) y a) =
      ∑ a, x a * y a :=
  realRotation_preserves_dotProduct (c.rotation i) ((checkPlaced_sound c h).1 i) x y

/-- The translated placements preserve squared Euclidean distances exactly. -/
theorem checkPlaced_preserves_squared_distance {d n k m : ℕ}
    (c : PlacementCertificate d n k m) (h : checkPlaced c = true) (i : Fin n)
    (x y : RPoint d) :
    (∑ a, (placementAffine (c.rotation i) (c.center i) x a -
      placementAffine (c.rotation i) (c.center i) y a) ^ 2) =
      ∑ a, (x a - y a) ^ 2 := by
  have hdiff : placementAffine (c.rotation i) (c.center i) x -
      placementAffine (c.rotation i) (c.center i) y =
      realRotation (c.rotation i) (x - y) := by
    simp [placementAffine, map_sub]
  have hd := checkPlaced_preserves_dotProduct c h i (x-y) (x-y)
  simpa only [← hdiff, Pi.sub_apply, pow_two] using hd
end PackingCertificates.Rational





