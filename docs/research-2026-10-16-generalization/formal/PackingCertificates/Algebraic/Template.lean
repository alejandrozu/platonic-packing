import PackingCertificates.Algebraic.Root
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Rat.BigOperators
import Lean.Elab.Tactic.Omega

/-!+Exact canonical coordinate semantics and checked interval enclosures.

Every coordinate is the published rational polynomial at the uniquely isolated
root, optionally multiplied by the positive inverse square root specified by D.
An exporter may widen intervals, but cannot replace the exact real vertex.
-/

namespace PackingCertificates.Algebraic

open scoped BigOperators

theorem eval_eq_head_add (cs : List ℚ) (x : ℝ) :
    Interval.eval cs x = ((cs.headD 0 : ℚ) : ℝ) + x * Interval.eval cs.tail x := by
  cases cs <;> simp [Interval.eval]

theorem getD_tail_succ (cs : List ℚ) (i : ℕ) :
    cs.tail.getD i 0 = cs.getD (i+1) 0 := by
  cases cs <;> simp

/-- Coefficient cancellation certifies a centroid identity at every real root;
no algebraic-root reduction or numerical near-zero test is used. -/
theorem sum_eval_zero {k : ℕ} (r : ℕ) (cs : Fin k → List ℚ)
    (hlen : ∀ j, (cs j).length ≤ r)
    (hz : ∀ p < r, (∑ j, (cs j).getD p 0) = 0) (x : ℝ) :
    (∑ j, Interval.eval (cs j) x) = 0 := by
  induction r generalizing cs with
  | zero =>
    have he : ∀ j, cs j = [] := fun j =>
      List.eq_nil_of_length_eq_zero (Nat.eq_zero_of_le_zero (hlen j))
    simp [he,Interval.eval]
  | succ r ih =>
    have hs : (∑ j, Interval.eval (cs j) x) =
        (∑ j, ((((cs j).headD 0 : ℚ) : ℝ) + x * Interval.eval (cs j).tail x)) := by
      apply Finset.sum_congr rfl
      intro j _
      exact eval_eq_head_add (cs j) x
    rw [hs]
    rw [Finset.sum_add_distrib,← Finset.mul_sum]
    have hhead : (∑ j, (((cs j).getD 0 0 : ℚ) : ℝ)) = 0 := by
      have hq := congrArg (fun z : ℚ => (z : ℝ)) (hz 0 (by omega))
      simpa only [Rat.cast_sum,Rat.cast_zero] using hq
    have htail := ih (fun j => (cs j).tail)
      (fun j => by simp only [List.length_tail]; have hh := hlen j; omega)
      (fun p hp => by simp_rw [getD_tail_succ]; exact hz (p+1) (by omega))
    simpa only [List.headD_eq_getD,hhead,htail,zero_add,mul_zero]

structure TemplateData (d k : ℕ) where
  rootSpec : RootSpec
  coefficients : Fin k → Fin d → List ℚ
  normalizerPolynomial : Option (List ℚ)
  normalizerSqrtInterval : Interval
  vertexIntervals : Fin k → Fin d → Interval

namespace TemplateData

noncomputable def normalization (t : TemplateData d k)
    (hRoot : t.rootSpec.check = true) : ℝ :=
  match t.normalizerPolynomial with
  | none => 1
  | some p => 1 / Real.sqrt (Interval.eval p (t.rootSpec.root hRoot))

def normalizationInterval (t : TemplateData d k) : Interval :=
  match t.normalizerPolynomial with
  | none => Interval.point 1
  | some _ => Interval.reciprocal t.normalizerSqrtInterval

def normalizationCheck (t : TemplateData d k) : Bool :=
  match t.normalizerPolynomial with
  | none => true
  | some p =>
      Interval.sqrtCheck (Interval.evalInterval p t.rootSpec.interval)
        t.normalizerSqrtInterval && decide (0 < t.normalizerSqrtInterval.lo)

noncomputable def vertex (t : TemplateData d k)
    (hRoot : t.rootSpec.check = true) (j : Fin k) (a : Fin d) : ℝ :=
  t.normalization hRoot *
    Interval.eval (t.coefficients j a) (t.rootSpec.root hRoot)

def coordinateCheck (t : TemplateData d k) (j : Fin k) (a : Fin d) : Bool :=
  Interval.enclosesCheck
    (Interval.mul t.normalizationInterval
      (Interval.evalInterval (t.coefficients j a) t.rootSpec.interval))
    (t.vertexIntervals j a)

def verticesCheck (t : TemplateData d k) : Bool :=
  (List.finRange k).all fun j => (List.finRange d).all fun a => t.coordinateCheck j a

def centroidCheck (t : TemplateData d k) (r : ℕ) : Bool :=
  ((List.finRange k).all fun j => (List.finRange d).all fun a =>
    decide ((t.coefficients j a).length ≤ r)) &&
  ((List.finRange d).all fun a => (List.finRange r).all fun p =>
    decide ((∑ j, (t.coefficients j a).getD p 0) = 0))

theorem centroid_sound (t : TemplateData d k) (r : ℕ)
    (hRoot : t.rootSpec.check = true) (h : t.centroidCheck r = true) :
    (∑ j, t.vertex hRoot j) = 0 := by
  have hh :
      ((List.finRange k).all fun j => (List.finRange d).all fun a =>
        decide ((t.coefficients j a).length ≤ r)) = true ∧
      ((List.finRange d).all fun a => (List.finRange r).all fun p =>
        decide ((∑ j, (t.coefficients j a).getD p 0) = 0)) = true := by
    simpa only [centroidCheck,Bool.and_eq_true] using h
  funext a
  simp only [Finset.sum_apply,Pi.zero_apply,vertex,← Finset.mul_sum]
  have hlen : ∀ j, (t.coefficients j a).length ≤ r := by
    intro j
    exact of_decide_eq_true (List.all_eq_true.mp
      (List.all_eq_true.mp hh.1 j (List.mem_finRange j)) a (List.mem_finRange a))
  have hz : ∀ p < r, (∑ j, (t.coefficients j a).getD p 0) = 0 := by
    intro p hp
    exact of_decide_eq_true (List.all_eq_true.mp
      (List.all_eq_true.mp hh.2 a (List.mem_finRange a)) ⟨p,hp⟩ (List.mem_finRange _))
  rw [sum_eval_zero r (fun j => t.coefficients j a) hlen hz,mul_zero]

theorem normalization_sound (t : TemplateData d k)
    (hRoot : t.rootSpec.check = true) (h : t.normalizationCheck = true) :
    t.normalizationInterval.Contains (t.normalization hRoot) ∧
      0 < t.normalization hRoot := by
  cases hp : t.normalizerPolynomial with
  | none => simp [normalizationInterval,normalization,hp,Interval.point,Interval.Contains]
  | some p =>
    have hh : Interval.sqrtCheck (Interval.evalInterval p t.rootSpec.interval)
        t.normalizerSqrtInterval = true ∧ 0 < t.normalizerSqrtInterval.lo := by
      simpa only [normalizationCheck,hp,Bool.and_eq_true,decide_eq_true_eq] using h
    have hv := Interval.eval_sound p (t.rootSpec.root_property hRoot).1
    have hs := Interval.sqrtCheck_sound hv hh.1
    have hlo : (0 : ℝ) < t.normalizerSqrtInterval.lo := by exact_mod_cast hh.2
    have hsp : 0 < Real.sqrt (Interval.eval p (t.rootSpec.root hRoot)) :=
      hlo.trans_le hs.1
    constructor
    · simpa only [normalizationInterval,normalization,hp] using
        Interval.reciprocal_sound hs hh.2
    · simpa only [normalization,hp] using one_div_pos.mpr hsp

theorem coordinate_sound (t : TemplateData d k)
    (hRoot : t.rootSpec.check = true) (hNorm : t.normalizationCheck = true)
    (j : Fin k) (a : Fin d) (h : t.coordinateCheck j a = true) :
    (t.vertexIntervals j a).Contains (t.vertex hRoot j a) := by
  apply Interval.enclosesCheck_sound (Interval.mul_sound
    (t.normalization_sound hRoot hNorm).1
    (Interval.eval_sound (t.coefficients j a) (t.rootSpec.root_property hRoot).1)) h

theorem vertices_sound (t : TemplateData d k)
    (hRoot : t.rootSpec.check = true) (hNorm : t.normalizationCheck = true)
    (h : t.verticesCheck = true) (j : Fin k) (a : Fin d) :
    (t.vertexIntervals j a).Contains (t.vertex hRoot j a) := by
  have hj : j ∈ List.finRange k := List.mem_finRange j
  have ha : a ∈ List.finRange d := List.mem_finRange a
  exact t.coordinate_sound hRoot hNorm j a
    (List.all_eq_true.mp (List.all_eq_true.mp h j hj) a ha)

#print axioms normalization_sound
#print axioms vertices_sound
#print axioms centroid_sound

end TemplateData
end PackingCertificates.Algebraic
