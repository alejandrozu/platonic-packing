import PackingCertificates.Rational
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Field

/-!
Exact support-function checking in arbitrary finite dimension. The canonical
piece and container each carry a proved geometric interface. Numerical records
still provide and check their actual original rotations, centers and planes;
support bounds replace repeated transformed-vertex arithmetic without changing
the resulting full convex-hull packing statement.
-/
namespace PackingCertificates.Extensions.NDSupport

open PackingCertificates.Rational
open scoped BigOperators

def projection {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) (b : Fin d) : ℚ :=
  ∑ a, u a * r a b

theorem qdot_placement {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d)
    (c v : QPoint d) :
    qdot u (fun a => qdot (r a) v + c a) =
      qdot u c + ∑ b, projection u r b * v b := by
  unfold qdot projection
  simp only [mul_add, Finset.sum_add_distrib, Finset.mul_sum]
  rw [add_comm]
  congr 1
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro b _
  simp only [Finset.sum_mul, mul_assoc]

structure TemplateModel (d k : ℕ) where
  vertices : Fin k → QPoint d
  radius : QPoint d → ℚ
  radius_bound : ∀ u p, |qdot u (vertices p)| ≤ radius u

/-- A generic exact radius, useful for small centrally symmetric templates.
The support normal is transformed once before the finite template is scanned. -/
def finiteRadius {d k : ℕ} (v : Fin k → QPoint d) (hk : 0 < k) (u : QPoint d) : ℚ :=
  Finset.univ.sup' ⟨⟨0, hk⟩, Finset.mem_univ _⟩ (fun p => |qdot u (v p)|)

def finiteModel {d k : ℕ} (v : Fin k → QPoint d) (hk : 0 < k) : TemplateModel d k where
  vertices := v
  radius := finiteRadius v hk
  radius_bound u p := by
    exact Finset.le_sup' (f := fun p => |qdot u (v p)|) (Finset.mem_univ p)

/-- The side-one coordinate-box radius works in every dimension. -/
def boxRadius {d : ℕ} (u : QPoint d) : ℚ := (∑ a, |u a|) / 2

theorem boxRadius_bound {d : ℕ} (u v : QPoint d) (hv : ∀ a, |v a| ≤ 1/2) :
    |qdot u v| ≤ boxRadius u := by
  unfold qdot boxRadius
  calc
    |∑ a, u a * v a| ≤ ∑ a, |u a * v a| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ a, |u a| / 2 := by
      apply Finset.sum_le_sum
      intro a _
      rw [abs_mul]
      calc
        |u a| * |v a| ≤ |u a| * (1/2) := mul_le_mul_of_nonneg_left (hv a) (abs_nonneg _)
        _ = |u a| / 2 := by ring
    _ = (∑ a, |u a|) / 2 := (Finset.sum_div _ _ _).symm

def boxModel {d k : ℕ} (v : Fin k → QPoint d)
    (hv : ∀ p a, |v p a| ≤ 1/2) : TemplateModel d k where
  vertices := v
  radius := boxRadius
  radius_bound u p := boxRadius_bound u (v p) (hv p)

def crossRadius {d : ℕ} (hd : 0 < d) (u : QPoint d) : ℚ :=
  Finset.univ.sup' ⟨⟨0, hd⟩, Finset.mem_univ _⟩ (fun a => |u a|)

theorem le_crossRadius {d : ℕ} (hd : 0 < d) (u : QPoint d) (a : Fin d) :
    |u a| ≤ crossRadius hd u := by
  exact Finset.le_sup' (f := fun a => |u a|) (Finset.mem_univ a)

theorem crossRadius_nonneg {d : ℕ} (hd : 0 < d) (u : QPoint d) :
    0 ≤ crossRadius hd u :=
  (abs_nonneg (u ⟨0, hd⟩)).trans (le_crossRadius hd u ⟨0, hd⟩)

theorem crossRadius_bound {d : ℕ} (hd : 0 < d) (u v : QPoint d)
    (hv : (∑ a, |v a|) ≤ 1) : |qdot u v| ≤ crossRadius hd u := by
  unfold qdot
  calc
    |∑ a, u a * v a| ≤ ∑ a, |u a * v a| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ a, crossRadius hd u * |v a| := by
      apply Finset.sum_le_sum
      intro a _
      rw [abs_mul]
      exact mul_le_mul_of_nonneg_right (le_crossRadius hd u a) (abs_nonneg _)
    _ = crossRadius hd u * ∑ a, |v a| := (Finset.mul_sum _ _ _).symm
    _ ≤ crossRadius hd u * 1 := mul_le_mul_of_nonneg_left hv (crossRadius_nonneg hd u)
    _ = crossRadius hd u := mul_one _

def crossModel {d k : ℕ} (hd : 0 < d) (v : Fin k → QPoint d)
    (hv : ∀ p, (∑ a, |v p a|) ≤ 1) : TemplateModel d k where
  vertices := v
  radius := crossRadius hd
  radius_bound u p := crossRadius_bound hd u (v p) (hv p)

def upperSupport {d k : ℕ} (m : TemplateModel d k) (u : QPoint d)
    (r : Fin d → QPoint d) (c : QPoint d) : ℚ :=
  qdot u c + m.radius (projection u r)

def lowerSupport {d k : ℕ} (m : TemplateModel d k) (u : QPoint d)
    (r : Fin d → QPoint d) (c : QPoint d) : ℚ :=
  qdot u c - m.radius (projection u r)

theorem support_bounds {d k : ℕ} (m : TemplateModel d k) (u : QPoint d)
    (r : Fin d → QPoint d) (c : QPoint d) (p : Fin k) :
    lowerSupport m u r c ≤ qdot u (fun a => qdot (r a) (m.vertices p) + c a) ∧
      qdot u (fun a => qdot (r a) (m.vertices p) + c a) ≤ upperSupport m u r c := by
  have hb := abs_le.mp (m.radius_bound (projection u r) p)
  rw [qdot_placement]
  change -m.radius (projection u r) ≤
      ∑ a, projection u r a * m.vertices p a ∧
    (∑ a, projection u r a * m.vertices p a) ≤
      m.radius (projection u r) at hb
  unfold lowerSupport upperSupport
  constructor <;> linarith [hb.1, hb.2]

noncomputable def scaledBody {d l : ℕ} (vertices : Fin l → QPoint d)
    (center : QPoint d) (scale : ℚ) : Set (RPoint d) :=
  vertexBody (fun j => realPoint (fun a => center a + scale * vertices j a))

structure ContainerModel (d l : ℕ) where
  vertices : Fin l → QPoint d
  containsCheck : QPoint d → ℚ → QPoint d → Bool
  containsCheck_sound : ∀ center scale x, 0 < scale → containsCheck center scale x = true →
    realPoint x ∈ scaledBody vertices center scale

structure Certificate (d n k l : ℕ) where
  piece : TemplateModel d k
  outer : ContainerModel d l
  rotation : Fin n → Fin d → QPoint d
  center : Fin n → QPoint d
  separation : Fin n → Fin n → QPlane d
  containerCenter : QPoint d
  scale : ℚ

def Certificate.placement {d n k l : ℕ} (c : Certificate d n k l) :
    PlacementCertificate d n k 0 where
  template := c.piece.vertices
  rotation := c.rotation
  center := c.center
  walls := Fin.elim0
  separation := c.separation

noncomputable def Certificate.containerBody {d n k l : ℕ} (c : Certificate d n k l) :
    Set (RPoint d) := scaledBody c.outer.vertices c.containerCenter c.scale

def planeCheck {d n k l : ℕ} (c : Certificate d n k l) (i j : Fin n) : Bool :=
  let p := c.separation i j
  decide (p.lower < p.upper) &&
    decide (upperSupport c.piece p.normal (c.rotation i) (c.center i) ≤ p.lower) &&
    decide (p.upper ≤ lowerSupport c.piece p.normal (c.rotation j) (c.center j))

theorem planeCheck_implies_vertex_check {d n k l : ℕ} (c : Certificate d n k l)
    (i j : Fin n) (h : planeCheck c i j = true) :
    Rational.planeCheck (c.placement.toCertificate.vertices i)
      (c.placement.toCertificate.vertices j) (c.separation i j) = true := by
  simp only [planeCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  simp only [Rational.planeCheck, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq]
  refine ⟨⟨h.1.1, ?_⟩, ?_⟩
  · intro p
    exact (support_bounds c.piece (c.separation i j).normal (c.rotation i) (c.center i) p).2.trans h.1.2
  · intro p
    exact h.2.trans (support_bounds c.piece (c.separation i j).normal (c.rotation j) (c.center j) p).1

def pairRowCheck {d n k l : ℕ} (c : Certificate d n k l) (i : Fin n) : Bool :=
  allFin n (fun j => if i < j then planeCheck c i j else true)

def vertexCheck {d n k l : ℕ} (c : Certificate d n k l) (i : Fin n) (p : Fin k) : Bool :=
  c.outer.containsCheck c.containerCenter c.scale (c.placement.toCertificate.vertices i p)

def checkPlacedFast {d n k l : ℕ} (c : Certificate d n k l) : Bool :=
  orthogonalCheck c.placement && allFin n (fun i => pairRowCheck c i)

theorem checkPlacedFast_implies_checkPlaced {d n k l : ℕ} (c : Certificate d n k l)
    (h : checkPlacedFast c = true) : Rational.checkPlaced c.placement = true := by
  simp only [checkPlacedFast, Bool.and_eq_true, allFin_eq_true] at h
  simp only [Rational.checkPlaced, Rational.check, Bool.and_eq_true, allFin_eq_true,
    decide_eq_true_eq]
  refine ⟨h.1, ?_, ?_⟩
  · intro i p f
    exact Fin.elim0 f
  · intro i j
    by_cases hij : i < j
    · simp only [hij, if_true]
      apply planeCheck_implies_vertex_check c i j
      simpa only [pairRowCheck, allFin_eq_true, hij, if_true] using (allFin_eq_true.mp (h.2 i) j)
    · simp [hij]

def check {d n k l : ℕ} (c : Certificate d n k l) : Bool :=
  checkPlacedFast c && decide (0 < c.scale) &&
    allFin n (fun i => allFin k (fun p => vertexCheck c i p))

def Valid {d n k l : ℕ} (c : Certificate d n k l) : Prop :=
  (0 < (c.scale : ℝ)) ∧
  (∀ i a b, realLinear (c.rotation i a) (realPoint (c.rotation i b)) =
    if a = b then (1 : ℝ) else 0) ∧
  (∀ i (x y : RPoint d),
    (∑ a, (placementAffine (c.rotation i) (c.center i) x a -
      placementAffine (c.rotation i) (c.center i) y a) ^ 2) = ∑ a, (x a-y a) ^ 2) ∧
  (∀ i, placementAffine (c.rotation i) (c.center i) ''
    vertexBody (fun p => realPoint (c.piece.vertices p)) ⊆ c.containerBody) ∧
  Pairwise (fun i j => Disjoint
    (placementAffine (c.rotation i) (c.center i) '' vertexBody (fun p => realPoint (c.piece.vertices p)))
    (placementAffine (c.rotation j) (c.center j) '' vertexBody (fun p => realPoint (c.piece.vertices p))))

theorem check_sound {d n k l : ℕ} (c : Certificate d n k l) (h : check c = true) : Valid c := by
  have hh : (checkPlacedFast c = true ∧ 0 < c.scale) ∧
      ∀ i p, vertexCheck c i p = true := by
    simpa only [check, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq] using h
  have hc := checkPlacedFast_implies_checkPlaced c hh.1.1
  have hp := Rational.checkPlaced_sound c.placement hc
  refine ⟨?_, hp.1, ?_, ?_, hp.2.2⟩
  · exact_mod_cast hh.1.2
  · intro i x y
    exact checkPlaced_preserves_squared_distance c.placement hc i x y
  · intro i
    change placementAffine (c.placement.rotation i) (c.placement.center i) ''
      vertexBody (fun p => realPoint (c.placement.template p)) ⊆ c.containerBody
    rw [placement_body]
    apply convexHull_min
    · rintro _ ⟨p, rfl⟩
      exact c.outer.containsCheck_sound c.containerCenter c.scale _ hh.1.2 (hh.2 i p)
    · exact convex_convexHull ℝ _

#print axioms finiteModel
#print axioms boxRadius_bound
#print axioms crossRadius_bound
#print axioms support_bounds
#print axioms planeCheck_implies_vertex_check
#print axioms checkPlacedFast_implies_checkPlaced
#print axioms check_sound
end PackingCertificates.Extensions.NDSupport
