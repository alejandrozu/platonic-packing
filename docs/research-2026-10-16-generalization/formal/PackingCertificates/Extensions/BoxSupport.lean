import PackingCertificates.Extensions.NDSupport

/-! Coordinate-wall support tests certify all vertices of a box-container
record at once. The conclusion uses the proved ContainerModel interface. -/
namespace PackingCertificates.Extensions.BoxSupport
open PackingCertificates.Rational
open PackingCertificates.Extensions.NDSupport
open scoped BigOperators

def axis {d : ℕ} (a : Fin d) : QPoint d := fun b => if b = a then 1 else 0

theorem qdot_axis {d : ℕ} (a : Fin d) (x : QPoint d) : qdot (axis a) x = x a := by
  simp [qdot, axis]

def wallRowCheck {d n k l : ℕ} (c : NDSupport.Certificate d n k l) (i : Fin n) : Bool :=
  allFin d (fun a =>
    decide (c.containerCenter a - c.scale/2 ≤ lowerSupport c.piece (axis a) (c.rotation i) (c.center i)) &&
    decide (upperSupport c.piece (axis a) (c.rotation i) (c.center i) ≤ c.containerCenter a + c.scale/2))

theorem wallRowCheck_implies_vertices {d n k l : ℕ} (c : NDSupport.Certificate d n k l)
    (ho : c.outer.containsCheck = fun center scale x =>
      allFin d (fun a => decide (|x a-center a| ≤ scale/2)))
    (i : Fin n) (h : wallRowCheck c i = true) :
    allFin k (fun p => NDSupport.vertexCheck c i p) = true := by
  apply allFin_eq_true.mpr
  intro p
  simp only [NDSupport.vertexCheck, ho, allFin_eq_true, decide_eq_true_eq]
  intro a
  have hh := allFin_eq_true.mp h a
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hh
  have hb := support_bounds c.piece (axis a) (c.rotation i) (c.center i) p
  rw [qdot_axis] at hb
  change |(qdot (c.rotation i a) (c.piece.vertices p) + c.center i a) - c.containerCenter a| ≤ c.scale/2
  exact abs_le.mpr ⟨by linarith [hh.1, hb.1], by linarith [hh.2, hb.2]⟩

#print axioms qdot_axis
#print axioms wallRowCheck_implies_vertices
end PackingCertificates.Extensions.BoxSupport
