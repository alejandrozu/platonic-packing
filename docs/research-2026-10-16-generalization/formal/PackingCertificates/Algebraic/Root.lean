import PackingCertificates.Algebraic.Interval
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.Topology.Algebra.Ring.Basic

/-!
Computable certificates for the unique real root in a rational interval.
Existence uses the intermediate value theorem. Uniqueness uses a checked
nonzero divided-difference interval, not an unverified root-counting oracle.
-/

namespace PackingCertificates.Algebraic

open Set

theorem eval_continuous (p : List ℚ) : Continuous (fun x : ℝ => Interval.eval p x) := by
  induction p with
  | nil => simpa only [Interval.eval,List.foldr_nil] using (continuous_const : Continuous (fun _ : ℝ => (0 : ℝ)))
  | cons c cs ih =>
    simpa only [Interval.eval,List.foldr_cons,Pi.add_def,Pi.mul_def,id_eq] using
      (continuous_const.add (continuous_id.mul ih))

structure RootSpec where
  polynomial : List ℚ
  interval : Interval

namespace RootSpec

def check (s : RootSpec) : Bool :=
  decide (s.interval.lo < s.interval.hi) &&
  ((decide (Interval.evalQ s.polynomial s.interval.lo < 0) &&
      decide (0 < Interval.evalQ s.polynomial s.interval.hi)) ||
   (decide (Interval.evalQ s.polynomial s.interval.hi < 0) &&
      decide (0 < Interval.evalQ s.polynomial s.interval.lo))) &&
  (decide (0 < (Interval.slopeInterval s.polynomial s.interval).lo) ||
    decide ((Interval.slopeInterval s.polynomial s.interval).hi < 0))

theorem check_sound (s : RootSpec) (h : s.check = true) :
    ∃! x : ℝ, s.interval.Contains x ∧ Interval.eval s.polynomial x = 0 := by
  have hh :
      (s.interval.lo < s.interval.hi ∧
        ((Interval.evalQ s.polynomial s.interval.lo < 0 ∧
          0 < Interval.evalQ s.polynomial s.interval.hi) ∨
         (Interval.evalQ s.polynomial s.interval.hi < 0 ∧
          0 < Interval.evalQ s.polynomial s.interval.lo))) ∧
      (0 < (Interval.slopeInterval s.polynomial s.interval).lo ∨
        (Interval.slopeInterval s.polynomial s.interval).hi < 0) := by
    simpa only [check,Bool.and_eq_true,Bool.or_eq_true,decide_eq_true_eq] using h
  have hlohi : (s.interval.lo : ℝ) ≤ s.interval.hi := by exact_mod_cast hh.1.1.le
  have hex : ∃ x : ℝ, s.interval.Contains x ∧ Interval.eval s.polynomial x = 0 := by
    rcases hh.1.2 with hp | hp
    · have ha : Interval.eval s.polynomial (s.interval.lo : ℝ) < 0 := by
        rw [Interval.eval_rat]
        exact_mod_cast hp.1
      have hb : 0 < Interval.eval s.polynomial (s.interval.hi : ℝ) := by
        rw [Interval.eval_rat]
        exact_mod_cast hp.2
      have hz : (0 : ℝ) ∈ Icc
          (Interval.eval s.polynomial (s.interval.lo : ℝ))
          (Interval.eval s.polynomial (s.interval.hi : ℝ)) := ⟨ha.le,hb.le⟩
      obtain ⟨x,hx,hzero⟩ := intermediate_value_Icc hlohi (eval_continuous s.polynomial).continuousOn hz
      exact ⟨x,hx,hzero⟩
    · have ha : Interval.eval s.polynomial (s.interval.hi : ℝ) < 0 := by
        rw [Interval.eval_rat]
        exact_mod_cast hp.1
      have hb : 0 < Interval.eval s.polynomial (s.interval.lo : ℝ) := by
        rw [Interval.eval_rat]
        exact_mod_cast hp.2
      have hz : (0 : ℝ) ∈ Icc
          (Interval.eval s.polynomial (s.interval.hi : ℝ))
          (Interval.eval s.polynomial (s.interval.lo : ℝ)) := ⟨ha.le,hb.le⟩
      obtain ⟨x,hx,hzero⟩ := intermediate_value_Icc' hlohi (eval_continuous s.polynomial).continuousOn hz
      exact ⟨x,hx,hzero⟩
  obtain ⟨x,hx⟩ := hex
  refine ⟨x,hx,?_⟩
  intro y hy
  have hs := Interval.slope_sound s.polynomial hy.1 hx.1
  have hsne : Interval.slope s.polynomial y x ≠ 0 := by
    rcases hh.2 with hp | hn
    · have hp' : (0 : ℝ) < (Interval.slopeInterval s.polynomial s.interval).lo := by exact_mod_cast hp
      exact ne_of_gt (hp'.trans_le hs.1)
    · have hn' : ((Interval.slopeInterval s.polynomial s.interval).hi : ℝ) < 0 := by exact_mod_cast hn
      exact ne_of_lt (hs.2.trans_lt hn')
  have hd := Interval.eval_sub_eval s.polynomial y x
  rw [hy.2,hx.2,sub_self] at hd
  exact sub_eq_zero.mp ((mul_eq_zero.mp hd.symm).resolve_right hsne)

noncomputable def root (s : RootSpec) (h : s.check = true) : ℝ :=
  Classical.choose (s.check_sound h).exists

theorem root_property (s : RootSpec) (h : s.check = true) :
    s.interval.Contains (s.root h) ∧ Interval.eval s.polynomial (s.root h) = 0 :=
  Classical.choose_spec (s.check_sound h).exists

theorem root_unique (s : RootSpec) (h : s.check = true) (x : ℝ)
    (hx : s.interval.Contains x ∧ Interval.eval s.polynomial x = 0) : x = s.root h :=
  (s.check_sound h).unique hx (s.root_property h)

#print axioms check_sound
#print axioms root_property
#print axioms root_unique

end RootSpec
end PackingCertificates.Algebraic
