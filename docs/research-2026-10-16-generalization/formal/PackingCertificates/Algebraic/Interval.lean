import Mathlib.Data.Rat.Cast.Order
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
Exact rational interval enclosures for real algebraic-coordinate certificates.
Intervals denote real values; their endpoints remain computable rationals.
An invalid interval contains no real number, rather than creating an axiom.
-/

namespace PackingCertificates.Algebraic

structure Interval where
  lo : ℚ
  hi : ℚ
  deriving DecidableEq

namespace Interval

def Contains (a : Interval) (x : ℝ) : Prop := (a.lo : ℝ) ≤ x ∧ x ≤ a.hi

def point (x : ℚ) : Interval := ⟨x,x⟩
def neg (a : Interval) : Interval := ⟨-a.hi,-a.lo⟩
def add (a b : Interval) : Interval := ⟨a.lo+b.lo,a.hi+b.hi⟩
def sub (a b : Interval) : Interval := add a (neg b)
def mul (a b : Interval) : Interval :=
  ⟨min (min (a.lo*b.lo) (a.lo*b.hi)) (min (a.hi*b.lo) (a.hi*b.hi)),
   max (max (a.lo*b.lo) (a.lo*b.hi)) (max (a.hi*b.lo) (a.hi*b.hi))⟩

def reciprocal (a : Interval) : Interval := ⟨1/a.hi,1/a.lo⟩

theorem point_sound (x : ℚ) : (point x).Contains (x : ℝ) := ⟨le_rfl,le_rfl⟩

theorem neg_sound {a : Interval} {x : ℝ} (hx : a.Contains x) :
    (neg a).Contains (-x) := by
  simpa only [Contains, neg, Rat.cast_neg] using
    And.intro (neg_le_neg hx.2) (neg_le_neg hx.1)

theorem add_sound {a b : Interval} {x y : ℝ}
    (hx : a.Contains x) (hy : b.Contains y) : (add a b).Contains (x+y) := by
  simpa only [Contains, add, Rat.cast_add] using
    And.intro (add_le_add hx.1 hy.1) (add_le_add hx.2 hy.2)

theorem sub_sound {a b : Interval} {x y : ℝ}
    (hx : a.Contains x) (hy : b.Contains y) : (sub a b).Contains (x-y) := by
  simpa only [sub, sub_eq_add_neg] using add_sound hx (neg_sound hy)

/-- Rectangle endpoint bounds imply product bounds; no positivity of the
intervals themselves is assumed. -/
theorem product_bounds {a b c d x y low high : ℝ}
    (hx : a ≤ x ∧ x ≤ b) (hy : c ≤ y ∧ y ≤ d)
    (hlac : low ≤ a*c) (hlad : low ≤ a*d)
    (hlbc : low ≤ b*c) (hlbd : low ≤ b*d)
    (huac : a*c ≤ high) (huad : a*d ≤ high)
    (hubc : b*c ≤ high) (hubd : b*d ≤ high) :
    low ≤ x*y ∧ x*y ≤ high := by
  constructor
  · by_cases hx0 : 0 ≤ x
    · have hxy : x*c ≤ x*y := mul_le_mul_of_nonneg_left hy.1 hx0
      by_cases hc0 : 0 ≤ c
      · exact hlac.trans ((mul_le_mul_of_nonneg_right hx.1 hc0).trans hxy)
      · exact hlbc.trans ((mul_le_mul_of_nonpos_right hx.2 (le_of_lt (lt_of_not_ge hc0))).trans hxy)
    · have hxy : x*d ≤ x*y :=
        mul_le_mul_of_nonpos_left hy.2 (le_of_lt (lt_of_not_ge hx0))
      by_cases hd0 : 0 ≤ d
      · exact hlad.trans ((mul_le_mul_of_nonneg_right hx.1 hd0).trans hxy)
      · exact hlbd.trans ((mul_le_mul_of_nonpos_right hx.2 (le_of_lt (lt_of_not_ge hd0))).trans hxy)
  · by_cases hx0 : 0 ≤ x
    · have hxy : x*y ≤ x*d := mul_le_mul_of_nonneg_left hy.2 hx0
      by_cases hd0 : 0 ≤ d
      · exact hxy.trans ((mul_le_mul_of_nonneg_right hx.2 hd0).trans hubd)
      · exact hxy.trans ((mul_le_mul_of_nonpos_right hx.1 (le_of_lt (lt_of_not_ge hd0))).trans huad)
    · have hxy : x*y ≤ x*c :=
        mul_le_mul_of_nonpos_left hy.1 (le_of_lt (lt_of_not_ge hx0))
      by_cases hc0 : 0 ≤ c
      · exact hxy.trans ((mul_le_mul_of_nonneg_right hx.2 hc0).trans hubc)
      · exact hxy.trans ((mul_le_mul_of_nonpos_right hx.1 (le_of_lt (lt_of_not_ge hc0))).trans huac)

theorem mul_sound {a b : Interval} {x y : ℝ}
    (hx : a.Contains x) (hy : b.Contains y) : (mul a b).Contains (x*y) := by
  have ql00 : (mul a b).lo ≤ a.lo*b.lo := (min_le_left _ _).trans (min_le_left _ _)
  have ql01 : (mul a b).lo ≤ a.lo*b.hi := (min_le_left _ _).trans (min_le_right _ _)
  have ql10 : (mul a b).lo ≤ a.hi*b.lo := (min_le_right _ _).trans (min_le_left _ _)
  have ql11 : (mul a b).lo ≤ a.hi*b.hi := (min_le_right _ _).trans (min_le_right _ _)
  have qu00 : a.lo*b.lo ≤ (mul a b).hi := (le_max_left _ _).trans (le_max_left _ _)
  have qu01 : a.lo*b.hi ≤ (mul a b).hi := (le_max_right _ _).trans (le_max_left _ _)
  have qu10 : a.hi*b.lo ≤ (mul a b).hi := (le_max_left _ _).trans (le_max_right _ _)
  have qu11 : a.hi*b.hi ≤ (mul a b).hi := (le_max_right _ _).trans (le_max_right _ _)
  apply product_bounds hx hy
  · exact_mod_cast ql00
  · exact_mod_cast ql01
  · exact_mod_cast ql10
  · exact_mod_cast ql11
  · exact_mod_cast qu00
  · exact_mod_cast qu01
  · exact_mod_cast qu10
  · exact_mod_cast qu11

theorem reciprocal_sound {a : Interval} {x : ℝ} (hx : a.Contains x)
    (hpos : 0 < a.lo) : (reciprocal a).Contains (1/x) := by
  have hlo : (0 : ℝ) < a.lo := by exact_mod_cast hpos
  have hxp : 0 < x := hlo.trans_le hx.1
  have h1 := one_div_le_one_div_of_le hxp hx.2
  have h2 := one_div_le_one_div_of_le hlo hx.1
  simpa only [Contains, reciprocal, Rat.cast_div, Rat.cast_one] using And.intro h1 h2

/-- Candidate square-root endpoints are checked by exact rational squares.
This also supplies inverse-square-root normalization through `reciprocal`. -/
def sqrtCheck (a b : Interval) : Bool :=
  decide (0 ≤ a.lo) && decide (0 ≤ b.lo) && decide (0 ≤ b.hi) &&
  decide (b.lo*b.lo ≤ a.lo) && decide (a.hi ≤ b.hi*b.hi)

theorem sqrtCheck_sound {a b : Interval} {x : ℝ}
    (hx : a.Contains x) (h : sqrtCheck a b = true) : b.Contains (Real.sqrt x) := by
  simp only [sqrtCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  have ha : (0 : ℝ) ≤ a.lo := by exact_mod_cast h.1.1.1.1
  have hb0 : (0 : ℝ) ≤ b.lo := by exact_mod_cast h.1.1.1.2
  have hb1 : (0 : ℝ) ≤ b.hi := by exact_mod_cast h.1.1.2
  have hlow : (b.lo : ℝ)*(b.lo : ℝ) ≤ a.lo := by exact_mod_cast h.1.2
  have hhigh : (a.hi : ℝ) ≤ (b.hi : ℝ)*(b.hi : ℝ) := by exact_mod_cast h.2
  have hsq := Real.sq_sqrt (ha.trans hx.1)
  have hn := Real.sqrt_nonneg x
  constructor <;> nlinarith [hx.1,hx.2]

/-- Widening a computed interval is safe, including outward fixed-point
rounding proposed by an external exporter. -/
def enclosesCheck (inner outer : Interval) : Bool :=
  decide (outer.lo ≤ inner.lo) && decide (inner.hi ≤ outer.hi)

theorem enclosesCheck_sound {inner outer : Interval} {x : ℝ}
    (hx : inner.Contains x) (h : enclosesCheck inner outer = true) : outer.Contains x := by
  simp only [enclosesCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  have hlo : (outer.lo : ℝ) ≤ inner.lo := by exact_mod_cast h.1
  have hhi : (inner.hi : ℝ) ≤ outer.hi := by exact_mod_cast h.2
  exact ⟨hlo.trans hx.1,hx.2.trans hhi⟩

def eval (coeffs : List ℚ) (x : ℝ) : ℝ :=
  coeffs.foldr (fun (c : ℚ) (z : ℝ) => (c : ℝ)+x*z) 0

def evalQ (coeffs : List ℚ) (x : ℚ) : ℚ :=
  coeffs.foldr (fun c z => c+x*z) 0

def evalInterval (coeffs : List ℚ) (x : Interval) : Interval :=
  coeffs.foldr (fun c z => add (point c) (mul x z)) (point 0)

theorem eval_sound (coeffs : List ℚ) {a : Interval} {x : ℝ} (hx : a.Contains x) :
    (evalInterval coeffs a).Contains (eval coeffs x) := by
  induction coeffs with
  | nil => simp [eval,evalInterval,point,Contains]
  | cons c cs ih => exact add_sound (point_sound c) (mul_sound hx ih)

theorem eval_rat (coeffs : List ℚ) (x : ℚ) : eval coeffs (x : ℝ) = (evalQ coeffs x : ℝ) := by
  induction coeffs with
  | nil => simp [eval,evalQ]
  | cons c cs ih =>
    change (c : ℝ)+(x : ℝ)*eval cs (x : ℝ) = ((c+x*evalQ cs x : ℚ) : ℝ)
    rw [ih]
    push_cast
    rfl

/-- Bivariate divided difference, defined without division and valid even at
x=y. A definite interval sign proves local root uniqueness. -/
def slope : List ℚ → ℝ → ℝ → ℝ
  | [],_,_ => 0
  | _::cs,x,y => eval cs x+y*slope cs x y

def slopeInterval : List ℚ → Interval → Interval
  | [],_ => point 0
  | _::cs,a => add (evalInterval cs a) (mul a (slopeInterval cs a))

theorem slope_sound (coeffs : List ℚ) {a : Interval} {x y : ℝ}
    (hx : a.Contains x) (hy : a.Contains y) :
    (slopeInterval coeffs a).Contains (slope coeffs x y) := by
  induction coeffs with
  | nil => simp [slope,slopeInterval,point,Contains]
  | cons c cs ih => exact add_sound (eval_sound cs hx) (mul_sound hy ih)

theorem eval_sub_eval (coeffs : List ℚ) (x y : ℝ) :
    eval coeffs x-eval coeffs y = (x-y)*slope coeffs x y := by
  induction coeffs with
  | nil => simp [eval,slope]
  | cons c cs ih =>
    change ((c : ℝ)+x*eval cs x)-((c : ℝ)+y*eval cs y) =
      (x-y)*(eval cs x+y*slope cs x y)
    calc
      _ = (x-y)*eval cs x+y*(eval cs x-eval cs y) := by ring
      _ = (x-y)*eval cs x+y*((x-y)*slope cs x y) := by rw [ih]
      _ = _ := by ring

#print axioms mul_sound
#print axioms sqrtCheck_sound
#print axioms eval_sound
#print axioms eval_sub_eval

end Interval
end PackingCertificates.Algebraic
