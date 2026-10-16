import PackingCertificates.Algebraic.Template

/-!
Exact source interpretation of ND edge-ratio factors. Every frozen factor is
of the form (a+b√r) or √2(a+b√r). Its positive value is proved equal to the
inverse-square-root normalization used by the rescaled container template.
-/

namespace PackingCertificates.Algebraic.QuadraticScale

structure Spec where
  rootSpec : RootSpec
  radicand : ℚ
  a : ℚ
  b : ℚ
  timesSqrtTwo : Bool
  d0 : ℚ
  d1 : ℚ
  sqrtTwoInterval : Interval

def Spec.factor (s : Spec) : ℚ := if s.timesSqrtTwo then 2 else 1
def Spec.m0 (s : Spec) : ℚ := s.factor*(s.a*s.a+s.radicand*s.b*s.b)
def Spec.m1 (s : Spec) : ℚ := s.factor*2*s.a*s.b

noncomputable def Spec.mu (s : Spec) (hRoot : s.rootSpec.check = true) : ℝ :=
  ((s.a : ℝ)+(s.b : ℝ)*s.rootSpec.root hRoot) *
    (if s.timesSqrtTwo then Real.sqrt 2 else 1)

def Spec.muInterval (s : Spec) : Interval :=
  Interval.mul
    (Interval.add (Interval.point s.a) (Interval.mul (Interval.point s.b) s.rootSpec.interval))
    (if s.timesSqrtTwo then s.sqrtTwoInterval else Interval.point 1)

def Spec.check (s : Spec) : Bool :=
  decide (s.rootSpec.polynomial = [-s.radicand,0,1]) &&
  (decide (0 < s.rootSpec.interval.lo) &&
  (Interval.sqrtCheck (Interval.point 2) s.sqrtTwoInterval &&
  (decide (0 < s.muInterval.lo) &&
  (decide (s.m0*s.d0+s.radicand*s.m1*s.d1 = 1) &&
    decide (s.m0*s.d1+s.m1*s.d0 = 0)))))

theorem Spec.root_square (s : Spec) (hRoot : s.rootSpec.check = true)
    (hp : s.rootSpec.polynomial = [-s.radicand,0,1]) :
    (s.rootSpec.root hRoot)^2 = (s.radicand : ℝ) := by
  have hz := (s.rootSpec.root_property hRoot).2
  rw [hp] at hz
  simp only [Interval.eval,List.foldr_cons,List.foldr_nil,Rat.cast_neg,Rat.cast_zero,
    Rat.cast_one,mul_zero,add_zero,mul_one,zero_add] at hz
  nlinarith

theorem Spec.muInterval_sound (s : Spec) (hRoot : s.rootSpec.check = true)
    (hSqrt : Interval.sqrtCheck (Interval.point 2) s.sqrtTwoInterval = true) :
    s.muInterval.Contains (s.mu hRoot) := by
  apply Interval.mul_sound
  · exact Interval.add_sound (Interval.point_sound s.a)
      (Interval.mul_sound (Interval.point_sound s.b) (s.rootSpec.root_property hRoot).1)
  · by_cases h : s.timesSqrtTwo = true
    · simpa only [h,if_true] using
        (Interval.sqrtCheck_sound (show (Interval.point 2).Contains (2 : ℝ) by
          constructor <;> norm_num [Interval.Contains,Interval.point]) hSqrt)
    · simp only [Bool.not_eq_true] at h
      simp only [h,Bool.false_eq_true,if_false]
      constructor <;> norm_num [Interval.Contains,Interval.point]

theorem Spec.square_identity (s : Spec) (hRoot : s.rootSpec.check = true)
    (hα : (s.rootSpec.root hRoot)^2 = (s.radicand : ℝ)) :
    (s.mu hRoot)^2 = (s.m0 : ℝ)+(s.m1 : ℝ)*s.rootSpec.root hRoot := by
  let α := s.rootSpec.root hRoot
  have hbase : ((s.a : ℝ)+(s.b : ℝ)*α)^2 =
      ((s.a : ℝ)^2+(s.radicand : ℝ)*(s.b : ℝ)^2) +
        2*(s.a : ℝ)*(s.b : ℝ)*α := by
    calc
      _ = (s.a : ℝ)^2+2*(s.a : ℝ)*(s.b : ℝ)*α+(s.b : ℝ)^2*α^2 := by ring
      _ = _ := by rw [hα]; ring
  dsimp [α] at hbase
  have htwo : (Real.sqrt (2 : ℝ))^2 = 2 := Real.sq_sqrt (by norm_num)
  by_cases hb : s.timesSqrtTwo = true
  · simp only [Spec.mu,hb,if_true,mul_pow,htwo,hbase,Spec.m0,Spec.m1,Spec.factor,
      Rat.cast_mul,Rat.cast_add,Rat.cast_ofNat]
    ring
  · have hb' : s.timesSqrtTwo = false := Bool.eq_false_iff.mpr hb
    simp only [Spec.mu,hb',Bool.false_eq_true,if_false,mul_one,Spec.m0,Spec.m1,Spec.factor,
      Rat.cast_mul,Rat.cast_add,Rat.cast_one,Rat.cast_ofNat]
    nlinarith only [hbase]

theorem Spec.check_sound (s : Spec) (hRoot : s.rootSpec.check = true)
    (h : s.check = true) :
    0 < s.mu hRoot ∧
    1 / Real.sqrt (Interval.eval [s.d0,s.d1] (s.rootSpec.root hRoot)) = s.mu hRoot := by
  have hh : s.rootSpec.polynomial = [-s.radicand,0,1] ∧
      (0 < s.rootSpec.interval.lo ∧
      (Interval.sqrtCheck (Interval.point 2) s.sqrtTwoInterval = true ∧
      (0 < s.muInterval.lo ∧
      (s.m0*s.d0+s.radicand*s.m1*s.d1 = 1 ∧ s.m0*s.d1+s.m1*s.d0 = 0)))) := by
    simpa only [Spec.check,Bool.and_eq_true,decide_eq_true_eq] using h
  have hμI := s.muInterval_sound hRoot hh.2.2.1
  have hμ : 0 < s.mu hRoot := by
    have hl : (0 : ℝ) < s.muInterval.lo := by exact_mod_cast hh.2.2.2.1
    exact hl.trans_le hμI.1
  have hα := s.root_square hRoot hh.1
  have hsq := s.square_identity hRoot hα
  have he0 : (s.m0 : ℝ)*(s.d0 : ℝ)+(s.radicand : ℝ)*(s.m1 : ℝ)*(s.d1 : ℝ) = 1 := by
    exact_mod_cast hh.2.2.2.2.1
  have he1 : (s.m0 : ℝ)*(s.d1 : ℝ)+(s.m1 : ℝ)*(s.d0 : ℝ) = 0 := by
    exact_mod_cast hh.2.2.2.2.2
  let D := Interval.eval [s.d0,s.d1] (s.rootSpec.root hRoot)
  have hDexpr : D = (s.d0 : ℝ)+(s.d1 : ℝ)*s.rootSpec.root hRoot := by
    simp [D,Interval.eval,mul_comm]
  have hprod : (s.mu hRoot)^2*D = 1 := by
    rw [hsq,hDexpr]
    calc
      _ = ((s.m0 : ℝ)*(s.d0 : ℝ)+(s.radicand : ℝ)*(s.m1 : ℝ)*(s.d1 : ℝ)) +
          ((s.m0 : ℝ)*(s.d1 : ℝ)+(s.m1 : ℝ)*(s.d0 : ℝ))*s.rootSpec.root hRoot := by
        calc
          _ = (s.m0 : ℝ)*(s.d0 : ℝ) +
              ((s.m0 : ℝ)*(s.d1 : ℝ)+(s.m1 : ℝ)*(s.d0 : ℝ))*s.rootSpec.root hRoot +
              (s.m1 : ℝ)*(s.d1 : ℝ)*(s.rootSpec.root hRoot)^2 := by ring
          _ = _ := by rw [hα]; ring
      _ = 1 := by rw [he0,he1]; ring
  have hD : 0 < D := by
    by_contra hn
    have hnp : D ≤ 0 := le_of_not_gt hn
    have hm := mul_nonpos_of_nonneg_of_nonpos (sq_nonneg (s.mu hRoot)) hnp
    linarith
  have hsqrt : 0 < Real.sqrt D := Real.sqrt_pos.2 hD
  have hprodSq : (s.mu hRoot*Real.sqrt D)^2 = (1 : ℝ)^2 := by
    rw [mul_pow,Real.sq_sqrt hD.le,hprod]
    norm_num
  have heq : s.mu hRoot*Real.sqrt D = 1 := by
    rcases (sq_eq_sq_iff_eq_or_eq_neg.mp hprodSq) with he | he
    · exact he
    · have hp := mul_pos hμ hsqrt
      linarith
  refine ⟨hμ,?_⟩
  exact ((eq_div_iff (ne_of_gt hsqrt)).2 heq).symm

end PackingCertificates.Algebraic.QuadraticScale

#print axioms PackingCertificates.Algebraic.QuadraticScale.Spec.check_sound
