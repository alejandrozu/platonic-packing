import PackingCertificates.Catalogue
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Field

/-!
# Exact support bounds for affine cubes

For a side-one cube, the support function of a rational affine placement is
`u·c + (sum_b |sum_a u_a R_ab|)/2`. Checking this formula once per separating
plane avoids repeating the same arithmetic at all eight cube vertices.
All Boolean reductions remain kernel-checked exact rational arithmetic.
-/

namespace PackingCertificates.CubeFast

open PackingCertificates.Rational
open PackingCertificates.Catalogue
open scoped BigOperators

def projection {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) (b : Fin d) : ℚ :=
  ∑ a, u a * r a b

def radius {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) : ℚ :=
  (∑ b, |projection u r b|) / 2

def upperSupport {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) (c : QPoint d) : ℚ :=
  qdot u c + radius u r

def lowerSupport {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) (c : QPoint d) : ℚ :=
  qdot u c - radius u r

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

/-- Generic support bounds for any template point in the side-one coordinate
box, in every finite dimension. No rotation hypothesis is needed. -/
theorem support_bounds {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d)
    (c v : QPoint d) (hv : ∀ a, |v a| ≤ 1/2) :
    lowerSupport u r c ≤ qdot u (fun a => qdot (r a) v + c a) ∧
      qdot u (fun a => qdot (r a) v + c a) ≤ upperSupport u r c := by
  have hm (b : Fin d) : |projection u r b * v b| ≤ |projection u r b| / 2 := by
    rw [abs_mul]
    calc
      |projection u r b| * |v b| ≤ |projection u r b| * (1/2) :=
        mul_le_mul_of_nonneg_left (hv b) (abs_nonneg _)
      _ = |projection u r b| / 2 := by ring
  have ha : |∑ b, projection u r b * v b| ≤ radius u r := by
    calc
      |∑ b, projection u r b * v b| ≤ ∑ b, |projection u r b * v b| :=
        Finset.abs_sum_le_sum_abs _ _
      _ ≤ ∑ b, |projection u r b| / 2 := Finset.sum_le_sum (fun b _ => hm b)
      _ = radius u r := by unfold radius; rw [Finset.sum_div]
  have h := abs_le.mp ha
  rw [qdot_placement]
  unfold lowerSupport upperSupport
  constructor <;> linarith [h.1, h.2]

theorem cubeTemplate_bound (p : Fin 8) (a : Fin 3) : |cubeTemplate p a| ≤ (1/2 : ℚ) := by
  fin_cases p <;> fin_cases a <;> norm_num [cubeTemplate]

def fastPlaneCheck {n : ℕ} (r : CubeRecord n) (i j : Fin n) : Bool :=
  let p := r.separation i j
  decide (p.lower < p.upper) &&
    decide (upperSupport p.normal (r.rotation i) (r.center i) ≤ p.lower) &&
    decide (p.upper ≤ lowerSupport p.normal (r.rotation j) (r.center j))

def fastCheck {n : ℕ} (r : CubeRecord n) : Bool :=
  r.sourceCheck && orthogonalCheck r.toPlacement &&
    allFin n (fun i => allFin 6 (fun f =>
      decide (upperSupport (r.toPlacement.walls f).normal (r.rotation i) (r.center i) ≤
        (r.toPlacement.walls f).offset))) &&
    allFin n (fun i => allFin n (fun j =>
      if i < j then fastPlaneCheck r i j else true))

/-- The optimized formula implies every original exact vertex test, so it
inherits the original record theorem without weakening any geometric claim. -/
theorem fastCheck_implies_check {n : ℕ} (r : CubeRecord n) (h : fastCheck r = true) :
    r.check = true := by
  have hh : ((r.sourceCheck = true ∧ orthogonalCheck r.toPlacement = true) ∧
      ∀ i f, upperSupport (r.toPlacement.walls f).normal (r.rotation i) (r.center i) ≤
        (r.toPlacement.walls f).offset) ∧
      ∀ i j, (if i < j then fastPlaneCheck r i j else true) = true := by
    simpa only [fastCheck, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq] using h
  simp only [CubeRecord.check, checkPlaced, Rational.check, Bool.and_eq_true,
    allFin_eq_true, decide_eq_true_eq]
  refine ⟨hh.1.1.1, hh.1.1.2, ?_, ?_⟩
  · intro i p f
    exact (support_bounds (r.toPlacement.walls f).normal (r.rotation i) (r.center i)
      (cubeTemplate p) (cubeTemplate_bound p)).2.trans (hh.1.2 i f)
  · intro i j
    by_cases hij : i < j
    · simp only [hij, if_true, planeCheck, Bool.and_eq_true, allFin_eq_true,
        decide_eq_true_eq]
      have hp : (r.separation i j).lower < (r.separation i j).upper ∧
          upperSupport (r.separation i j).normal (r.rotation i) (r.center i) ≤
            (r.separation i j).lower ∧
          (r.separation i j).upper ≤
            lowerSupport (r.separation i j).normal (r.rotation j) (r.center j) := by
        have ht := hh.2 i j
        simpa only [hij, if_true, fastPlaneCheck, Bool.and_eq_true,
          decide_eq_true_eq, and_assoc] using ht
      refine ⟨⟨hp.1, ?_⟩, ?_⟩
      · intro p
        exact (support_bounds (r.separation i j).normal (r.rotation i) (r.center i)
          (cubeTemplate p) (cubeTemplate_bound p)).2.trans hp.2.1
      · intro p
        exact hp.2.2.trans (support_bounds (r.separation i j).normal (r.rotation j)
          (r.center j) (cubeTemplate p) (cubeTemplate_bound p)).1
    · simp [hij]
theorem fastCheck_sound {n : ℕ} (r : CubeRecord n) (h : fastCheck r = true) :
    r.Valid :=
  CubeRecord.check_sound r (fastCheck_implies_check r h)


/-- Row-sized computations permit bounded-memory verification of large
catalogue records. Their proofs can be checked separately and assembled. -/
def wallRowCheck {n : ℕ} (r : CubeRecord n) (i : Fin n) : Bool :=
  allFin 6 (fun f =>
    decide (upperSupport (r.toPlacement.walls f).normal (r.rotation i) (r.center i) ≤
      (r.toPlacement.walls f).offset))

def pairRowCheck {n : ℕ} (r : CubeRecord n) (i : Fin n) : Bool :=
  allFin n (fun j => if i < j then fastPlaneCheck r i j else true)

theorem fastCheck_of_rows {n : ℕ} (r : CubeRecord n)
    (hs : r.sourceCheck = true) (ho : orthogonalCheck r.toPlacement = true)
    (hw : ∀ i, wallRowCheck r i = true) (hp : ∀ i, pairRowCheck r i = true) :
    fastCheck r = true := by
  simp only [fastCheck, Bool.and_eq_true, allFin_eq_true]
  exact ⟨⟨⟨hs, ho⟩, fun i => allFin_eq_true.mp (hw i)⟩, fun i => allFin_eq_true.mp (hp i)⟩
end PackingCertificates.CubeFast


