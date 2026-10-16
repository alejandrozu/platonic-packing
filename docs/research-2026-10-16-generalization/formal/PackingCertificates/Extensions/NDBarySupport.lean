import PackingCertificates.Extensions.NDSupport
import PackingCertificates.Barycentric

/-!
Support checking can also retain an existing sparse barycentric certificate
verbatim. This adapter changes only the computation proving pair separation;
all original source rotations, containment weights and canonical hulls remain.
-/
namespace PackingCertificates.Extensions.NDBarySupport
open PackingCertificates.Rational
open PackingCertificates.Extensions.NDSupport

def planeCheck {d n k l t : ℕ} (c : Barycentric.Certificate d n k l t)
    (model : TemplateModel d k) (i j : Fin n) : Bool :=
  let p := c.placement.separation i j
  decide (p.lower < p.upper) &&
    decide (upperSupport model p.normal (c.placement.rotation i) (c.placement.center i) ≤ p.lower) &&
    decide (p.upper ≤ lowerSupport model p.normal (c.placement.rotation j) (c.placement.center j))

theorem planeCheck_implies_vertex_check {d n k l t : ℕ}
    (c : Barycentric.Certificate d n k l t) (model : TemplateModel d k)
    (hm : model.vertices = c.placement.template) (i j : Fin n)
    (h : planeCheck c model i j = true) :
    Rational.planeCheck (c.placement.toCertificate.vertices i)
      (c.placement.toCertificate.vertices j) (c.placement.separation i j) = true := by
  simp only [planeCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  simp only [Rational.planeCheck, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq]
  refine ⟨⟨h.1.1, ?_⟩, ?_⟩
  · intro p
    have hb := (support_bounds model (c.placement.separation i j).normal
      (c.placement.rotation i) (c.placement.center i) p).2
    rw [hm] at hb
    exact hb.trans h.1.2
  · intro p
    have hb := (support_bounds model (c.placement.separation i j).normal
      (c.placement.rotation j) (c.placement.center j) p).1
    rw [hm] at hb
    exact h.2.trans hb

def pairRowCheck {d n k l t : ℕ} (c : Barycentric.Certificate d n k l t)
    (model : TemplateModel d k) (i : Fin n) : Bool :=
  allFin n (fun j => if i < j then planeCheck c model i j else true)

def checkPlacedFast {d n k l t : ℕ} (c : Barycentric.Certificate d n k l t)
    (model : TemplateModel d k) : Bool :=
  orthogonalCheck c.placement && allFin n (fun i => pairRowCheck c model i)

theorem checkPlacedFast_implies_checkPlaced {d n k l t : ℕ}
    (c : Barycentric.Certificate d n k l t) (model : TemplateModel d k)
    (hm : model.vertices = c.placement.template) (h : checkPlacedFast c model = true) :
    Rational.checkPlaced c.placement = true := by
  simp only [checkPlacedFast, Bool.and_eq_true, allFin_eq_true] at h
  simp only [Rational.checkPlaced, Rational.check, Bool.and_eq_true, allFin_eq_true,
    decide_eq_true_eq]
  refine ⟨h.1, ?_, ?_⟩
  · intro i p f
    exact Fin.elim0 f
  · intro i j
    by_cases hij : i < j
    · simp only [hij, if_true]
      apply planeCheck_implies_vertex_check c model hm i j
      simpa only [pairRowCheck, allFin_eq_true, hij, if_true] using (allFin_eq_true.mp (h.2 i) j)
    · simp [hij]

def check {d n k l t : ℕ} (c : Barycentric.Certificate d n k l t)
    (model : TemplateModel d k) : Bool :=
  checkPlacedFast c model && decide (0 < c.scale) &&
    allFin n (fun i => allFin k (fun p => c.vertexCheck i p))

theorem check_implies_barycentric_check {d n k l t : ℕ}
    (c : Barycentric.Certificate d n k l t) (model : TemplateModel d k)
    (hm : model.vertices = c.placement.template) (h : check c model = true) :
    Barycentric.check c = true := by
  simp only [check, Bool.and_eq_true] at h
  simp only [Barycentric.check, Bool.and_eq_true]
  exact ⟨⟨checkPlacedFast_implies_checkPlaced c model hm h.1.1, h.1.2⟩, h.2⟩

theorem check_sound {d n k l t : ℕ} (c : Barycentric.Certificate d n k l t)
    (model : TemplateModel d k) (hm : model.vertices = c.placement.template)
    (h : check c model = true) : Barycentric.Valid c :=
  Barycentric.check_sound c (check_implies_barycentric_check c model hm h)

#print axioms planeCheck_implies_vertex_check
#print axioms checkPlacedFast_implies_checkPlaced
#print axioms check_implies_barycentric_check
#print axioms check_sound
end PackingCertificates.Extensions.NDBarySupport
