import PackingCertificates.Extensions.NDGeometry
import PackingCertificates.Extensions.NDSupport

namespace PackingCertificates.Extensions.NDModels
open PackingCertificates
open PackingCertificates.Rational
open PackingCertificates.Extensions.NDGeometry
open PackingCertificates.Extensions.NDSupport
open scoped BigOperators

theorem realPoint_translate_scale {d : ℕ} (c v : QPoint d) (s : ℚ) :
    realPoint (fun a => c a+s*v a) = realPoint c+(s : ℝ) • realPoint v := by
  ext a
  simp [realPoint, Rat.cast_add, Rat.cast_mul]

def crossContainer {d l : ℕ} (hd : 0 < d) (v : Fin l → QPoint d)
    (covers : ∀ p : Fin d × Bool, ∃ i, v i = qcrossVertex p) : ContainerModel d l where
  vertices := v
  containsCheck c s x := decide ((∑ a, |x a-c a|) ≤ s)
  containsCheck_sound c s x hs h := q_l1_contains hd v covers c x s hs (of_decide_eq_true h)

def boxContainer {d l : ℕ} (v : Fin l → QPoint d)
    (hbody : vertexBody (fun i => realPoint (v i)) = BoxGeometry.unitBox d) :
    ContainerModel d l where
  vertices := v
  containsCheck c s x := allFin d (fun a => decide (|x a-c a| ≤ s/2))
  containsCheck_sound c s x hs h := by
    have hsR : (0 : ℝ) < s := by exact_mod_cast hs
    unfold scaledBody
    simp_rw [realPoint_translate_scale]
    rw [← image_vertexBody_scale (fun i => realPoint (v i)), hbody,
      BoxGeometry.image_unitBox _ _ hsR]
    intro a
    have ha : |x a-c a| ≤ s/2 := of_decide_eq_true (allFin_eq_true.mp h a)
    have hR : |(x a : ℝ)-(c a : ℝ)| ≤ (s : ℝ)/2 := by exact_mod_cast ha
    change (c a : ℝ)-(s : ℝ)/2 ≤ (x a : ℝ) ∧ (x a : ℝ) ≤ (c a : ℝ)+(s : ℝ)/2
    constructor <;> linarith [(abs_le.mp hR).1, (abs_le.mp hR).2]

def c8Piece : TemplateModel 4 16 := boxModel
  (fun p => TemplateData.c8.getD p.val 0) (by decide +kernel)
def hc5Piece : TemplateModel 5 32 := boxModel
  (fun p => TemplateData.hc5.getD p.val 0) (by decide +kernel)
def hc6Piece : TemplateModel 6 64 := boxModel
  (fun p => TemplateData.hc6.getD p.val 0) (by decide +kernel)
def c16Piece : TemplateModel 4 8 := crossModel (by decide)
  (fun p => TemplateData.c16.getD p.val 0) (by decide +kernel)
def op5Piece : TemplateModel 5 10 := crossModel (by decide)
  (fun p => TemplateData.op5.getD p.val 0) (by decide +kernel)
def op6Piece : TemplateModel 6 12 := crossModel (by decide)
  (fun p => TemplateData.op6.getD p.val 0) (by decide +kernel)
def c24Piece : TemplateModel 4 24 := finiteModel
  (fun p => TemplateData.c24.getD p.val 0) (by decide)

def c8Outer : ContainerModel 4 16 := boxContainer _ BoxGeometry.c8_body
def hc5Outer : ContainerModel 5 32 := boxContainer _ BoxGeometry.hc5_body
def hc6Outer : ContainerModel 6 64 := boxContainer _ BoxGeometry.hc6_body
def c16Outer : ContainerModel 4 8 := crossContainer (by decide)
  (fun p => TemplateData.c16.getD p.val 0)
  (fun p => ⟨crossIndex p, funext (c16_index p)⟩)
def op5Outer : ContainerModel 5 10 := crossContainer (by decide)
  (fun p => TemplateData.op5.getD p.val 0)
  (fun p => ⟨crossIndex p, funext (op5_index p)⟩)
def op6Outer : ContainerModel 6 12 := crossContainer (by decide)
  (fun p => TemplateData.op6.getD p.val 0)
  (fun p => ⟨crossIndex p, funext (op6_index p)⟩)

#print axioms crossContainer
#print axioms boxContainer
#print axioms c8Piece
#print axioms hc6Piece
#print axioms c16Piece
#print axioms op6Piece
#print axioms c24Piece
#print axioms c16Outer
#print axioms hc6Outer
#print axioms op6Outer
end PackingCertificates.Extensions.NDModels
