import PackingCertificates.Algebraic.QuadraticScale

namespace PackingCertificates.Algebraic.QuadraticScale

/-- The positively isolated quadratic primitive denotes the ordinary real
square root occurring literally in the frozen ND input expressions. -/
theorem Spec.root_eq_sqrt (s : Spec) (hRoot : s.rootSpec.check = true)
    (h : s.check = true) : s.rootSpec.root hRoot = Real.sqrt (s.radicand : ℝ) := by
  have hh : s.rootSpec.polynomial = [-s.radicand,0,1] ∧
      (0 < s.rootSpec.interval.lo ∧
      (Interval.sqrtCheck (Interval.point 2) s.sqrtTwoInterval = true ∧
      (0 < s.muInterval.lo ∧
      (s.m0*s.d0+s.radicand*s.m1*s.d1 = 1 ∧ s.m0*s.d1+s.m1*s.d0 = 0)))) := by
    simpa only [Spec.check,Bool.and_eq_true,decide_eq_true_eq] using h
  have hα := s.root_square hRoot hh.1
  have hlo : (0 : ℝ) < s.rootSpec.interval.lo := by exact_mod_cast hh.2.1
  have hpos := hlo.trans_le (s.rootSpec.root_property hRoot).1.1
  symm
  rw [← hα,Real.sqrt_sq_eq_abs,abs_of_pos hpos]

theorem Spec.mu_eq_sqrt_expression (s : Spec) (hRoot : s.rootSpec.check = true)
    (h : s.check = true) : s.mu hRoot =
      ((s.a : ℝ)+(s.b : ℝ)*Real.sqrt (s.radicand : ℝ)) *
        (if s.timesSqrtTwo then Real.sqrt 2 else 1) := by
  rw [Spec.mu,s.root_eq_sqrt hRoot h]

end PackingCertificates.Algebraic.QuadraticScale

#print axioms PackingCertificates.Algebraic.QuadraticScale.Spec.root_eq_sqrt
