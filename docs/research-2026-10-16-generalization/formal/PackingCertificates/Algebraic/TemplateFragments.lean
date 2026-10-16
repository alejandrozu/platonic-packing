import PackingCertificates.Algebraic.FragmentND

namespace PackingCertificates.Algebraic.TemplateFragments

open PackingCertificates.Rational
open scoped BigOperators

def antipodalItemCheck (t : TemplateData d k) (opposite : Fin k → Fin k)
    (degree : ℕ) (j : Fin k) : Bool :=
  decide (opposite (opposite j) = j) &&
  allFin d (fun a => decide ((t.coefficients j a).length ≤ degree) &&
    allFin degree (fun p => decide ((t.coefficients (opposite j) a).getD p.val 0 =
      -(t.coefficients j a).getD p.val 0)))

/-- An independently checked antipodal permutation proves coefficient sums
zero algebraically, without one enormous numerical sum over all vertices. -/
theorem centroidCheck_of_antipodal (t : TemplateData d k)
    (opposite : Fin k → Fin k) (degree : ℕ)
    (h : ∀ j, antipodalItemCheck t opposite degree j = true) :
    t.centroidCheck degree = true := by
  have hh : ∀ j, opposite (opposite j) = j ∧
      ∀ a, (t.coefficients j a).length ≤ degree ∧
        ∀ p : Fin degree, (t.coefficients (opposite j) a).getD p.val 0 =
          -(t.coefficients j a).getD p.val 0 := by
    intro j
    simpa only [antipodalItemCheck,Bool.and_eq_true,allFin_eq_true,decide_eq_true_eq] using h j
  let e : Fin k ≃ Fin k := ⟨opposite,opposite,fun j => (hh j).1,fun j => (hh j).1⟩
  have hs : ∀ a (p : Fin degree), (∑ j, (t.coefficients j a).getD p.val 0) = 0 := by
    intro a p
    have he := Equiv.sum_comp e (fun j => (t.coefficients j a).getD p.val 0)
    have hneg : (fun j => (t.coefficients (e j) a).getD p.val 0) =
        fun j => -(t.coefficients j a).getD p.val 0 := by
      funext j
      exact (hh j).2 a |>.2 p
    change (∑ j, (fun j => (t.coefficients (e j) a).getD p.val 0) j) =
      ∑ j, (t.coefficients j a).getD p.val 0 at he
    rw [hneg,Finset.sum_neg_distrib] at he
    linarith
  change (allFin k (fun j => allFin d (fun a =>
    decide ((t.coefficients j a).length ≤ degree))) &&
    allFin d (fun a => allFin degree (fun p =>
      decide ((∑ j, (t.coefficients j a).getD p.val 0) = 0)))) = true
  apply Bool.and_eq_true_iff.mpr
  constructor
  · apply allFin_eq_true.mpr
    intro j
    apply allFin_eq_true.mpr
    intro a
    simpa only [decide_eq_true_eq] using ((hh j).2 a).1
  · apply allFin_eq_true.mpr
    intro a
    apply allFin_eq_true.mpr
    intro p
    simpa only [decide_eq_true_eq] using hs a p

end PackingCertificates.Algebraic.TemplateFragments

#print axioms PackingCertificates.Algebraic.TemplateFragments.centroidCheck_of_antipodal
