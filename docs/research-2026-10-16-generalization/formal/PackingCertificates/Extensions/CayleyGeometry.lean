import PackingCertificates.Cayley
import PackingCertificates.Rational
import Mathlib.Tactic.NoncommRing

/-!
Proper Euclidean Cayley placements in every finite dimension. Source-checking
an inverse and the Cayley formula is enough to derive orthogonality; a second
large numerical Gram reduction is unnecessary. No claim about optimizer
convergence or the floating-point matrix implementation is made.
-/
namespace PackingCertificates.Extensions.CayleyGeometry
open PackingCertificates
open PackingCertificates.Rational
open scoped BigOperators

theorem rotation_mul_transpose {d : ℕ}
    (s ai r : Cayley.QMatrix d) (signs : Fin d → ℚ)
    (hskew : s.transpose = -s)
    (hsigns : ∀ i, signs i = 1 ∨ signs i = -1)
    (hinv : ai * (1-s) = 1)
    (hrot : r = Matrix.diagonal signs * ai * (1+s)) :
    r * r.transpose = 1 := by
  have htA : (1-s).transpose = 1+s := by
    rw [Matrix.transpose_sub, Matrix.transpose_one, hskew]
    simp
  have htB : (1+s).transpose = 1-s := by
    rw [Matrix.transpose_add, Matrix.transpose_one, hskew]
    simp [sub_eq_add_neg]
  have hcomm : (1+s)*(1-s) = (1-s)*(1+s) := by noncomm_ring
  have hti : (1+s)*ai.transpose = 1 := by
    have h := congrArg Matrix.transpose hinv
    simpa only [Matrix.transpose_mul, Matrix.transpose_one, htA] using h
  have hc : (ai*(1+s))*(ai*(1+s)).transpose = 1 := by
    rw [Matrix.transpose_mul, htB]
    calc
      ai*(1+s)*((1-s)*ai.transpose) = ai*((1+s)*(1-s))*ai.transpose := by
        simp only [Matrix.mul_assoc]
      _ = ai*((1-s)*(1+s))*ai.transpose := by rw [hcomm]
      _ = (ai*(1-s))*((1+s)*ai.transpose) := by simp only [Matrix.mul_assoc]
      _ = 1 := by rw [hinv, hti, mul_one]
  have hd : Matrix.diagonal signs * Matrix.diagonal signs = 1 := by
    rw [Matrix.diagonal_mul_diagonal]
    have hv : (fun i => signs i * signs i) = (fun _ => (1 : ℚ)) := by
      funext i
      rcases hsigns i with hi | hi <;> simp [hi]
    change Matrix.diagonal (fun i => signs i * signs i) = 1
    rw [hv]
    exact Matrix.diagonal_one
  have hr : r = Matrix.diagonal signs * (ai*(1+s)) := by
    rw [hrot, Matrix.mul_assoc]
  have hdt : (Matrix.diagonal signs).transpose = Matrix.diagonal signs := by
    ext i j
    by_cases hij : i = j
    · subst j
      simp
    · simp [Matrix.transpose_apply, Matrix.diagonal_apply, hij, Ne.symm hij]
  rw [hr, Matrix.transpose_mul, hdt]
  calc
    Matrix.diagonal signs * (ai*(1+s)) *
        ((ai*(1+s)).transpose * Matrix.diagonal signs) =
        Matrix.diagonal signs * ((ai*(1+s))*(ai*(1+s)).transpose) *
          Matrix.diagonal signs := by simp only [Matrix.mul_assoc]
    _ = 1 := by rw [hc, mul_one, hd]

theorem check_row_gram {d : ℕ} (c : Cayley.Certificate d) (h : Cayley.check c = true) :
    ∀ a b, qdot (c.rotation a) (c.rotation b) = if a = b then 1 else 0 := by
  have hh := h
  simp only [Cayley.check, Bool.and_eq_true, decide_eq_true_eq] at hh
  have hm := rotation_mul_transpose c.skew c.inverse c.rotation c.signs
    hh.1.1.1.1 hh.1.1.1.2 hh.1.2 hh.2
  intro a b
  have hab := congrFun (congrFun hm a) b
  simpa only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply, qdot] using hab

theorem check_real_row_gram {d : ℕ} (c : Cayley.Certificate d) (h : Cayley.check c = true) :
    ∀ a b, realLinear (c.rotation a) (realPoint (c.rotation b)) =
      if a = b then (1 : ℝ) else 0 := by
  intro a b
  rw [realLinear_realPoint]
  have hr := check_row_gram c h a b
  by_cases hab : a = b
  · simp only [hab, if_true] at hr ⊢
    exact_mod_cast hr
  · simp only [hab, if_false] at hr ⊢
    exact_mod_cast hr

/-- The checked raw Cayley placement is a proper Euclidean rotation in every
dimension, with both determinant and dot-product conclusions. -/
theorem check_proper_euclidean {d : ℕ} (c : Cayley.Certificate d)
    (h : Cayley.check c = true) :
    Matrix.det (fun a b => (c.rotation a b : ℝ)) = 1 ∧
    ∀ x y : RPoint d,
      (∑ a, realRotation c.rotation x a * realRotation c.rotation y a) =
        ∑ a, x a*y a := by
  exact ⟨Cayley.determinant_real c h,
    realRotation_preserves_dotProduct c.rotation (check_real_row_gram c h)⟩

#print axioms rotation_mul_transpose
#print axioms check_row_gram
#print axioms check_real_row_gram
#print axioms check_proper_euclidean
end PackingCertificates.Extensions.CayleyGeometry
