import PackingCertificates.Algebraic.QuadraticInverse

/-! Exact reference endpoint literals and native edge-ratio factors.
This leaf does not establish adjacency, regularity, or equality with a full vertex array.
The accompanying generator binds these selected literals to frozen native JSON hashes.
-/
set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.NDReferenceEdges
open scoped BigOperators Matrix
open QuadraticInverse

def difference (x y : PairQ) : PairQ := (x.1-y.1,x.2-y.2)
def scalePair (q : ℚ) (x : PairQ) : PairQ := (q*x.1,q*x.2)
def distancePair {d : ℕ} (r : ℚ) (u v : Fin d → PairQ) : PairQ :=
  ∑ a, product r (difference (u a) (v a)) (difference (u a) (v a))

theorem embed_difference (α : ℝ) (x y : PairQ) :
    embed α (difference x y) = embed α x - embed α y := by
  simp only [embed,difference,Rat.cast_sub]; ring

theorem embed_scale (α : ℝ) (q : ℚ) (x : PairQ) :
    embed α (scalePair q x) = (q : ℝ)*embed α x := by
  simp only [embed,scalePair,Rat.cast_mul]; ring

theorem distancePair_sound {d : ℕ} (r : ℚ) (α : ℝ) (hα : α^2 = (r : ℝ))
    (u v : Fin d → PairQ) (e : PairQ) (h : distancePair r u v = e) :
    (∑ a, (embed α (u a)-embed α (v a))^2) = embed α e := by
  rw [← h,distancePair,show embed α = embedAdd α from rfl,map_sum]
  apply Finset.sum_congr rfl
  intro a _
  change _ = embed α (product r _ _)
  rw [embed_product r α hα,embed_difference,pow_two]
  rfl

noncomputable def nativeMu (m : PairQ) (timesTwo : Bool) : ℝ :=
  embed (Real.sqrt 5) m * (if timesTwo then Real.sqrt 2 else 1)

theorem native_ratio_sound (m ce pe : PairQ) (timesTwo : Bool)
    (h : scalePair (if timesTwo then 2 else 1)
      (product 5 (product 5 m m) ce) = pe) :
    (nativeMu m timesTwo)^2 * embed (Real.sqrt 5) ce = embed (Real.sqrt 5) pe := by
  have hs5 : (Real.sqrt 5)^2 = ((5 : ℚ) : ℝ) := by norm_num
  have he := congrArg (embed (Real.sqrt 5)) h
  rw [embed_scale,embed_product 5 _ hs5,embed_product 5 _ hs5] at he
  cases timesTwo
  · simpa [nativeMu,pow_two,mul_assoc] using he
  · have hs2 : (Real.sqrt 2)^2 = (2 : ℝ) := by norm_num
    simp only [ite_true,Rat.cast_ofNat] at he
    simp only [nativeMu,ite_true,mul_pow,hs2]
    nlinarith [he]


def c120_u : Fin 4 → PairQ := ![((1/2 : ℚ),(-1/2 : ℚ)),((-7/2 : ℚ),(3/2 : ℚ)),((1/2 : ℚ),(-1/2 : ℚ)),((1/2 : ℚ),(-1/2 : ℚ))]

def c120_v : Fin 4 → PairQ := ![((1/2 : ℚ),(-1/2 : ℚ)),((2 : ℚ),(-1 : ℚ)),((-3 : ℚ),(1 : ℚ)),((-3/2 : ℚ),(1/2 : ℚ))]

def c120_edge : PairQ := ((94 : ℚ),(-42 : ℚ))

theorem c120_edge_exact : distancePair 5 c120_u c120_v = c120_edge := by decide +kernel

theorem c120_reference_distance : (∑ a, (embed (Real.sqrt 5) (c120_u a)-embed (Real.sqrt 5) (c120_v a))^2) = embed (Real.sqrt 5) c120_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ c120_edge_exact

def c16_u : Fin 4 → PairQ := ![((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def c16_v : Fin 4 → PairQ := ![((0 : ℚ),(0 : ℚ)),((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def c16_edge : PairQ := ((2 : ℚ),(0 : ℚ))

theorem c16_edge_exact : distancePair 5 c16_u c16_v = c16_edge := by decide +kernel

theorem c16_reference_distance : (∑ a, (embed (Real.sqrt 5) (c16_u a)-embed (Real.sqrt 5) (c16_v a))^2) = embed (Real.sqrt 5) c16_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ c16_edge_exact

def c24_u : Fin 4 → PairQ := ![((1 : ℚ),(0 : ℚ)),((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def c24_v : Fin 4 → PairQ := ![((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def c24_edge : PairQ := ((2 : ℚ),(0 : ℚ))

theorem c24_edge_exact : distancePair 5 c24_u c24_v = c24_edge := by decide +kernel

theorem c24_reference_distance : (∑ a, (embed (Real.sqrt 5) (c24_u a)-embed (Real.sqrt 5) (c24_v a))^2) = embed (Real.sqrt 5) c24_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ c24_edge_exact

def c5_u : Fin 4 → PairQ := ![((3/2 : ℚ),(1/10 : ℚ)),((-1/2 : ℚ),(1/10 : ℚ)),((-1/2 : ℚ),(1/10 : ℚ)),((-1/2 : ℚ),(1/10 : ℚ))]

def c5_v : Fin 4 → PairQ := ![((-1/2 : ℚ),(1/10 : ℚ)),((3/2 : ℚ),(1/10 : ℚ)),((-1/2 : ℚ),(1/10 : ℚ)),((-1/2 : ℚ),(1/10 : ℚ))]

def c5_edge : PairQ := ((8 : ℚ),(0 : ℚ))

theorem c5_edge_exact : distancePair 5 c5_u c5_v = c5_edge := by decide +kernel

theorem c5_reference_distance : (∑ a, (embed (Real.sqrt 5) (c5_u a)-embed (Real.sqrt 5) (c5_v a))^2) = embed (Real.sqrt 5) c5_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ c5_edge_exact

def c600_u : Fin 4 → PairQ := ![((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ))]

def c600_v : Fin 4 → PairQ := ![((1/4 : ℚ),(1/4 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((-1/4 : ℚ),(1/4 : ℚ)),((0 : ℚ),(0 : ℚ))]

def c600_edge : PairQ := ((3/2 : ℚ),(-1/2 : ℚ))

theorem c600_edge_exact : distancePair 5 c600_u c600_v = c600_edge := by decide +kernel

theorem c600_reference_distance : (∑ a, (embed (Real.sqrt 5) (c600_u a)-embed (Real.sqrt 5) (c600_v a))^2) = embed (Real.sqrt 5) c600_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ c600_edge_exact

def c8_u : Fin 4 → PairQ := ![((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ))]

def c8_v : Fin 4 → PairQ := ![((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((-1/2 : ℚ),(0 : ℚ))]

def c8_edge : PairQ := ((1 : ℚ),(0 : ℚ))

theorem c8_edge_exact : distancePair 5 c8_u c8_v = c8_edge := by decide +kernel

theorem c8_reference_distance : (∑ a, (embed (Real.sqrt 5) (c8_u a)-embed (Real.sqrt 5) (c8_v a))^2) = embed (Real.sqrt 5) c8_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ c8_edge_exact

def hc5_u : Fin 5 → PairQ := ![((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ))]

def hc5_v : Fin 5 → PairQ := ![((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((-1/2 : ℚ),(0 : ℚ))]

def hc5_edge : PairQ := ((1 : ℚ),(0 : ℚ))

theorem hc5_edge_exact : distancePair 5 hc5_u hc5_v = hc5_edge := by decide +kernel

theorem hc5_reference_distance : (∑ a, (embed (Real.sqrt 5) (hc5_u a)-embed (Real.sqrt 5) (hc5_v a))^2) = embed (Real.sqrt 5) hc5_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ hc5_edge_exact

def hc6_u : Fin 6 → PairQ := ![((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ))]

def hc6_v : Fin 6 → PairQ := ![((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((1/2 : ℚ),(0 : ℚ)),((-1/2 : ℚ),(0 : ℚ))]

def hc6_edge : PairQ := ((1 : ℚ),(0 : ℚ))

theorem hc6_edge_exact : distancePair 5 hc6_u hc6_v = hc6_edge := by decide +kernel

theorem hc6_reference_distance : (∑ a, (embed (Real.sqrt 5) (hc6_u a)-embed (Real.sqrt 5) (hc6_v a))^2) = embed (Real.sqrt 5) hc6_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ hc6_edge_exact

def op5_u : Fin 5 → PairQ := ![((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def op5_v : Fin 5 → PairQ := ![((0 : ℚ),(0 : ℚ)),((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def op5_edge : PairQ := ((2 : ℚ),(0 : ℚ))

theorem op5_edge_exact : distancePair 5 op5_u op5_v = op5_edge := by decide +kernel

theorem op5_reference_distance : (∑ a, (embed (Real.sqrt 5) (op5_u a)-embed (Real.sqrt 5) (op5_v a))^2) = embed (Real.sqrt 5) op5_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ op5_edge_exact

def op6_u : Fin 6 → PairQ := ![((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def op6_v : Fin 6 → PairQ := ![((0 : ℚ),(0 : ℚ)),((1 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ)),((0 : ℚ),(0 : ℚ))]

def op6_edge : PairQ := ((2 : ℚ),(0 : ℚ))

theorem op6_edge_exact : distancePair 5 op6_u op6_v = op6_edge := by decide +kernel

theorem op6_reference_distance : (∑ a, (embed (Real.sqrt 5) (op6_u a)-embed (Real.sqrt 5) (op6_v a))^2) = embed (Real.sqrt 5) op6_edge :=
  distancePair_sound 5 _ (by norm_num) _ _ _ op6_edge_exact

def sx5_u : Fin 5 → PairQ := ![((4/5 : ℚ),(1/30 : ℚ)),((-1/5 : ℚ),(1/30 : ℚ)),((-1/5 : ℚ),(1/30 : ℚ)),((-1/5 : ℚ),(1/30 : ℚ)),((-1/5 : ℚ),(1/30 : ℚ))]

def sx5_v : Fin 5 → PairQ := ![((-1/5 : ℚ),(1/30 : ℚ)),((4/5 : ℚ),(1/30 : ℚ)),((-1/5 : ℚ),(1/30 : ℚ)),((-1/5 : ℚ),(1/30 : ℚ)),((-1/5 : ℚ),(1/30 : ℚ))]

def sx5_edge : PairQ := ((2 : ℚ),(0 : ℚ))

theorem sx5_edge_exact : distancePair 6 sx5_u sx5_v = sx5_edge := by decide +kernel

theorem sx5_reference_distance : (∑ a, (embed (Real.sqrt 6) (sx5_u a)-embed (Real.sqrt 6) (sx5_v a))^2) = embed (Real.sqrt 6) sx5_edge :=
  distancePair_sound 6 _ (by norm_num) _ _ _ sx5_edge_exact

def sx6_u : Fin 6 → PairQ := ![((5/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ))]

def sx6_v : Fin 6 → PairQ := ![((-1/6 : ℚ),(1/42 : ℚ)),((5/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ)),((-1/6 : ℚ),(1/42 : ℚ))]

def sx6_edge : PairQ := ((2 : ℚ),(0 : ℚ))

theorem sx6_edge_exact : distancePair 7 sx6_u sx6_v = sx6_edge := by decide +kernel

theorem sx6_reference_distance : (∑ a, (embed (Real.sqrt 7) (sx6_u a)-embed (Real.sqrt 7) (sx6_v a))^2) = embed (Real.sqrt 7) sx6_edge :=
  distancePair_sound 7 _ (by norm_num) _ _ _ sx6_edge_exact

def c120inc120_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem c120inc120_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c120inc120_n02_m c120inc120_n02_m) ((94 : ℚ),(-42 : ℚ))) = ((94 : ℚ),(-42 : ℚ)) := by decide +kernel

theorem c120inc120_n02_edge_ratio : (nativeMu c120inc120_n02_m false)^2 * embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) = embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) := native_ratio_sound _ _ _ _ c120inc120_n02_coefficient_identity

theorem c120inc120_n02_mu_positive : 0 < nativeMu c120inc120_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c120inc120_n02_m := by
    norm_num [c120inc120_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c120inc16_n02_m : PairQ := ((7/2 : ℚ),(-3/2 : ℚ))

theorem c120inc16_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c120inc16_n02_m c120inc16_n02_m) ((2 : ℚ),(0 : ℚ))) = ((94 : ℚ),(-42 : ℚ)) := by decide +kernel

theorem c120inc16_n02_edge_ratio : (nativeMu c120inc16_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) := native_ratio_sound _ _ _ _ c120inc16_n02_coefficient_identity

theorem c120inc16_n02_mu_positive : 0 < nativeMu c120inc16_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c120inc16_n02_m := by
    norm_num [c120inc16_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c120inc24_n02_m : PairQ := ((7/2 : ℚ),(-3/2 : ℚ))

theorem c120inc24_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c120inc24_n02_m c120inc24_n02_m) ((2 : ℚ),(0 : ℚ))) = ((94 : ℚ),(-42 : ℚ)) := by decide +kernel

theorem c120inc24_n02_edge_ratio : (nativeMu c120inc24_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) := native_ratio_sound _ _ _ _ c120inc24_n02_coefficient_identity

theorem c120inc24_n02_mu_positive : 0 < nativeMu c120inc24_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c120inc24_n02_m := by
    norm_num [c120inc24_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c120inc5_n02_m : PairQ := ((7/4 : ℚ),(-3/4 : ℚ))

theorem c120inc5_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c120inc5_n02_m c120inc5_n02_m) ((8 : ℚ),(0 : ℚ))) = ((94 : ℚ),(-42 : ℚ)) := by decide +kernel

theorem c120inc5_n02_edge_ratio : (nativeMu c120inc5_n02_m true)^2 * embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) := native_ratio_sound _ _ _ _ c120inc5_n02_coefficient_identity

theorem c120inc5_n02_mu_positive : 0 < nativeMu c120inc5_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c120inc5_n02_m := by
    norm_num [c120inc5_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c120inc600_n02_m : PairQ := ((-4 : ℚ),(2 : ℚ))

theorem c120inc600_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c120inc600_n02_m c120inc600_n02_m) ((3/2 : ℚ),(-1/2 : ℚ))) = ((94 : ℚ),(-42 : ℚ)) := by decide +kernel

theorem c120inc600_n02_edge_ratio : (nativeMu c120inc600_n02_m false)^2 * embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) = embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) := native_ratio_sound _ _ _ _ c120inc600_n02_coefficient_identity

theorem c120inc600_n02_mu_positive : 0 < nativeMu c120inc600_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c120inc600_n02_m := by
    norm_num [c120inc600_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c120inc8_n02_m : PairQ := ((7 : ℚ),(-3 : ℚ))

theorem c120inc8_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c120inc8_n02_m c120inc8_n02_m) ((1 : ℚ),(0 : ℚ))) = ((94 : ℚ),(-42 : ℚ)) := by decide +kernel

theorem c120inc8_n02_edge_ratio : (nativeMu c120inc8_n02_m false)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) := native_ratio_sound _ _ _ _ c120inc8_n02_coefficient_identity

theorem c120inc8_n02_mu_positive : 0 < nativeMu c120inc8_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c120inc8_n02_m := by
    norm_num [c120inc8_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c16inc120_n02_m : PairQ := ((7/4 : ℚ),(3/4 : ℚ))

theorem c16inc120_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c16inc120_n02_m c16inc120_n02_m) ((94 : ℚ),(-42 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c16inc120_n02_edge_ratio : (nativeMu c16inc120_n02_m true)^2 * embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c16inc120_n02_coefficient_identity

theorem c16inc120_n02_mu_positive : 0 < nativeMu c16inc120_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c16inc120_n02_m := by
    norm_num [c16inc120_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c16inc5_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem c16inc5_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c16inc5_n02_m c16inc5_n02_m) ((8 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c16inc5_n02_edge_ratio : (nativeMu c16inc5_n02_m false)^2 * embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c16inc5_n02_coefficient_identity

theorem c16inc5_n02_mu_positive : 0 < nativeMu c16inc5_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c16inc5_n02_m := by
    norm_num [c16inc5_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c16inc600_n02_m : PairQ := ((1/2 : ℚ),(1/2 : ℚ))

theorem c16inc600_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c16inc600_n02_m c16inc600_n02_m) ((3/2 : ℚ),(-1/2 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c16inc600_n02_edge_ratio : (nativeMu c16inc600_n02_m true)^2 * embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c16inc600_n02_coefficient_identity

theorem c16inc600_n02_mu_positive : 0 < nativeMu c16inc600_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c16inc600_n02_m := by
    norm_num [c16inc600_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c16inc8_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem c16inc8_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c16inc8_n02_m c16inc8_n02_m) ((1 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c16inc8_n02_edge_ratio : (nativeMu c16inc8_n02_m true)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c16inc8_n02_coefficient_identity

theorem c16inc8_n02_mu_positive : 0 < nativeMu c16inc8_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c16inc8_n02_m := by
    norm_num [c16inc8_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c24inc120_n02_m : PairQ := ((7/4 : ℚ),(3/4 : ℚ))

theorem c24inc120_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c24inc120_n02_m c24inc120_n02_m) ((94 : ℚ),(-42 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c24inc120_n02_edge_ratio : (nativeMu c24inc120_n02_m true)^2 * embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c24inc120_n02_coefficient_identity

theorem c24inc120_n02_mu_positive : 0 < nativeMu c24inc120_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c24inc120_n02_m := by
    norm_num [c24inc120_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c24inc5_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem c24inc5_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c24inc5_n02_m c24inc5_n02_m) ((8 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c24inc5_n02_edge_ratio : (nativeMu c24inc5_n02_m false)^2 * embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c24inc5_n02_coefficient_identity

theorem c24inc5_n02_mu_positive : 0 < nativeMu c24inc5_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c24inc5_n02_m := by
    norm_num [c24inc5_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c24inc600_n02_m : PairQ := ((1/2 : ℚ),(1/2 : ℚ))

theorem c24inc600_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c24inc600_n02_m c24inc600_n02_m) ((3/2 : ℚ),(-1/2 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c24inc600_n02_edge_ratio : (nativeMu c24inc600_n02_m true)^2 * embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c24inc600_n02_coefficient_identity

theorem c24inc600_n02_mu_positive : 0 < nativeMu c24inc600_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c24inc600_n02_m := by
    norm_num [c24inc600_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c24inc8_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem c24inc8_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c24inc8_n02_m c24inc8_n02_m) ((1 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c24inc8_n02_edge_ratio : (nativeMu c24inc8_n02_m true)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c24inc8_n02_coefficient_identity

theorem c24inc8_n02_mu_positive : 0 < nativeMu c24inc8_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c24inc8_n02_m := by
    norm_num [c24inc8_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c5inc120_n02_m : PairQ := ((7/2 : ℚ),(3/2 : ℚ))

theorem c5inc120_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c5inc120_n02_m c5inc120_n02_m) ((94 : ℚ),(-42 : ℚ))) = ((8 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c5inc120_n02_edge_ratio : (nativeMu c5inc120_n02_m true)^2 * embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) = embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c5inc120_n02_coefficient_identity

theorem c5inc120_n02_mu_positive : 0 < nativeMu c5inc120_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c5inc120_n02_m := by
    norm_num [c5inc120_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c5inc16_n02_m : PairQ := ((2 : ℚ),(0 : ℚ))

theorem c5inc16_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c5inc16_n02_m c5inc16_n02_m) ((2 : ℚ),(0 : ℚ))) = ((8 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c5inc16_n02_edge_ratio : (nativeMu c5inc16_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c5inc16_n02_coefficient_identity

theorem c5inc16_n02_mu_positive : 0 < nativeMu c5inc16_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c5inc16_n02_m := by
    norm_num [c5inc16_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c5inc24_n02_m : PairQ := ((2 : ℚ),(0 : ℚ))

theorem c5inc24_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c5inc24_n02_m c5inc24_n02_m) ((2 : ℚ),(0 : ℚ))) = ((8 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c5inc24_n02_edge_ratio : (nativeMu c5inc24_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c5inc24_n02_coefficient_identity

theorem c5inc24_n02_mu_positive : 0 < nativeMu c5inc24_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c5inc24_n02_m := by
    norm_num [c5inc24_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c5inc5_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem c5inc5_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c5inc5_n02_m c5inc5_n02_m) ((8 : ℚ),(0 : ℚ))) = ((8 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c5inc5_n02_edge_ratio : (nativeMu c5inc5_n02_m false)^2 * embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c5inc5_n02_coefficient_identity

theorem c5inc5_n02_mu_positive : 0 < nativeMu c5inc5_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c5inc5_n02_m := by
    norm_num [c5inc5_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c5inc600_n02_m : PairQ := ((1 : ℚ),(1 : ℚ))

theorem c5inc600_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c5inc600_n02_m c5inc600_n02_m) ((3/2 : ℚ),(-1/2 : ℚ))) = ((8 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c5inc600_n02_edge_ratio : (nativeMu c5inc600_n02_m true)^2 * embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) = embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c5inc600_n02_coefficient_identity

theorem c5inc600_n02_mu_positive : 0 < nativeMu c5inc600_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c5inc600_n02_m := by
    norm_num [c5inc600_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c5inc8_n02_m : PairQ := ((2 : ℚ),(0 : ℚ))

theorem c5inc8_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c5inc8_n02_m c5inc8_n02_m) ((1 : ℚ),(0 : ℚ))) = ((8 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c5inc8_n02_edge_ratio : (nativeMu c5inc8_n02_m true)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c5inc8_n02_coefficient_identity

theorem c5inc8_n02_mu_positive : 0 < nativeMu c5inc8_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c5inc8_n02_m := by
    norm_num [c5inc8_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c600inc120_n02_m : PairQ := ((1 : ℚ),(1/2 : ℚ))

theorem c600inc120_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c600inc120_n02_m c600inc120_n02_m) ((94 : ℚ),(-42 : ℚ))) = ((3/2 : ℚ),(-1/2 : ℚ)) := by decide +kernel

theorem c600inc120_n02_edge_ratio : (nativeMu c600inc120_n02_m false)^2 * embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) = embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) := native_ratio_sound _ _ _ _ c600inc120_n02_coefficient_identity

theorem c600inc120_n02_mu_positive : 0 < nativeMu c600inc120_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c600inc120_n02_m := by
    norm_num [c600inc120_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c600inc16_n02_m : PairQ := ((-1/4 : ℚ),(1/4 : ℚ))

theorem c600inc16_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c600inc16_n02_m c600inc16_n02_m) ((2 : ℚ),(0 : ℚ))) = ((3/2 : ℚ),(-1/2 : ℚ)) := by decide +kernel

theorem c600inc16_n02_edge_ratio : (nativeMu c600inc16_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) := native_ratio_sound _ _ _ _ c600inc16_n02_coefficient_identity

theorem c600inc16_n02_mu_positive : 0 < nativeMu c600inc16_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c600inc16_n02_m := by
    norm_num [c600inc16_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c600inc24_n02_m : PairQ := ((-1/4 : ℚ),(1/4 : ℚ))

theorem c600inc24_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c600inc24_n02_m c600inc24_n02_m) ((2 : ℚ),(0 : ℚ))) = ((3/2 : ℚ),(-1/2 : ℚ)) := by decide +kernel

theorem c600inc24_n02_edge_ratio : (nativeMu c600inc24_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) := native_ratio_sound _ _ _ _ c600inc24_n02_coefficient_identity

theorem c600inc24_n02_mu_positive : 0 < nativeMu c600inc24_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c600inc24_n02_m := by
    norm_num [c600inc24_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c600inc5_n02_m : PairQ := ((-1/8 : ℚ),(1/8 : ℚ))

theorem c600inc5_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c600inc5_n02_m c600inc5_n02_m) ((8 : ℚ),(0 : ℚ))) = ((3/2 : ℚ),(-1/2 : ℚ)) := by decide +kernel

theorem c600inc5_n02_edge_ratio : (nativeMu c600inc5_n02_m true)^2 * embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) := native_ratio_sound _ _ _ _ c600inc5_n02_coefficient_identity

theorem c600inc5_n02_mu_positive : 0 < nativeMu c600inc5_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c600inc5_n02_m := by
    norm_num [c600inc5_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c600inc600_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem c600inc600_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c600inc600_n02_m c600inc600_n02_m) ((3/2 : ℚ),(-1/2 : ℚ))) = ((3/2 : ℚ),(-1/2 : ℚ)) := by decide +kernel

theorem c600inc600_n02_edge_ratio : (nativeMu c600inc600_n02_m false)^2 * embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) = embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) := native_ratio_sound _ _ _ _ c600inc600_n02_coefficient_identity

theorem c600inc600_n02_mu_positive : 0 < nativeMu c600inc600_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c600inc600_n02_m := by
    norm_num [c600inc600_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c600inc8_n02_m : PairQ := ((-1/2 : ℚ),(1/2 : ℚ))

theorem c600inc8_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c600inc8_n02_m c600inc8_n02_m) ((1 : ℚ),(0 : ℚ))) = ((3/2 : ℚ),(-1/2 : ℚ)) := by decide +kernel

theorem c600inc8_n02_edge_ratio : (nativeMu c600inc8_n02_m false)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) := native_ratio_sound _ _ _ _ c600inc8_n02_coefficient_identity

theorem c600inc8_n02_mu_positive : 0 < nativeMu c600inc8_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c600inc8_n02_m := by
    norm_num [c600inc8_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c8inc120_n02_m : PairQ := ((7/4 : ℚ),(3/4 : ℚ))

theorem c8inc120_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c8inc120_n02_m c8inc120_n02_m) ((94 : ℚ),(-42 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c8inc120_n02_edge_ratio : (nativeMu c8inc120_n02_m false)^2 * embed (Real.sqrt 5) ((94 : ℚ),(-42 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c8inc120_n02_coefficient_identity

theorem c8inc120_n02_mu_positive : 0 < nativeMu c8inc120_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c8inc120_n02_m := by
    norm_num [c8inc120_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def c8inc16_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem c8inc16_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c8inc16_n02_m c8inc16_n02_m) ((2 : ℚ),(0 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c8inc16_n02_edge_ratio : (nativeMu c8inc16_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c8inc16_n02_coefficient_identity

theorem c8inc16_n02_mu_positive : 0 < nativeMu c8inc16_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c8inc16_n02_m := by
    norm_num [c8inc16_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c8inc24_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem c8inc24_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c8inc24_n02_m c8inc24_n02_m) ((2 : ℚ),(0 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c8inc24_n02_edge_ratio : (nativeMu c8inc24_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c8inc24_n02_coefficient_identity

theorem c8inc24_n02_mu_positive : 0 < nativeMu c8inc24_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c8inc24_n02_m := by
    norm_num [c8inc24_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c8inc5_n02_m : PairQ := ((1/4 : ℚ),(0 : ℚ))

theorem c8inc5_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 c8inc5_n02_m c8inc5_n02_m) ((8 : ℚ),(0 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c8inc5_n02_edge_ratio : (nativeMu c8inc5_n02_m true)^2 * embed (Real.sqrt 5) ((8 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c8inc5_n02_coefficient_identity

theorem c8inc5_n02_mu_positive : 0 < nativeMu c8inc5_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c8inc5_n02_m := by
    norm_num [c8inc5_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def c8inc600_n02_m : PairQ := ((1/2 : ℚ),(1/2 : ℚ))

theorem c8inc600_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 c8inc600_n02_m c8inc600_n02_m) ((3/2 : ℚ),(-1/2 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem c8inc600_n02_edge_ratio : (nativeMu c8inc600_n02_m false)^2 * embed (Real.sqrt 5) ((3/2 : ℚ),(-1/2 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ c8inc600_n02_coefficient_identity

theorem c8inc600_n02_mu_positive : 0 < nativeMu c8inc600_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) c8inc600_n02_m := by
    norm_num [c8inc600_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def hc5inop5_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem hc5inop5_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 hc5inop5_n02_m hc5inop5_n02_m) ((2 : ℚ),(0 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem hc5inop5_n02_edge_ratio : (nativeMu hc5inop5_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ hc5inop5_n02_coefficient_identity

theorem hc5inop5_n02_mu_positive : 0 < nativeMu hc5inop5_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) hc5inop5_n02_m := by
    norm_num [hc5inop5_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def hc5insx5_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem hc5insx5_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 hc5insx5_n02_m hc5insx5_n02_m) ((2 : ℚ),(0 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem hc5insx5_n02_edge_ratio : (nativeMu hc5insx5_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ hc5insx5_n02_coefficient_identity

theorem hc5insx5_n02_mu_positive : 0 < nativeMu hc5insx5_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) hc5insx5_n02_m := by
    norm_num [hc5insx5_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def hc6inop6_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem hc6inop6_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 hc6inop6_n02_m hc6inop6_n02_m) ((2 : ℚ),(0 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem hc6inop6_n02_edge_ratio : (nativeMu hc6inop6_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ hc6inop6_n02_coefficient_identity

theorem hc6inop6_n02_mu_positive : 0 < nativeMu hc6inop6_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) hc6inop6_n02_m := by
    norm_num [hc6inop6_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def hc6insx6_n02_m : PairQ := ((1/2 : ℚ),(0 : ℚ))

theorem hc6insx6_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 hc6insx6_n02_m hc6insx6_n02_m) ((2 : ℚ),(0 : ℚ))) = ((1 : ℚ),(0 : ℚ)) := by decide +kernel

theorem hc6insx6_n02_edge_ratio : (nativeMu hc6insx6_n02_m true)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ hc6insx6_n02_coefficient_identity

theorem hc6insx6_n02_mu_positive : 0 < nativeMu hc6insx6_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) hc6insx6_n02_m := by
    norm_num [hc6insx6_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def op5inhc5_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem op5inhc5_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 op5inhc5_n02_m op5inhc5_n02_m) ((1 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem op5inhc5_n02_edge_ratio : (nativeMu op5inhc5_n02_m true)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ op5inhc5_n02_coefficient_identity

theorem op5inhc5_n02_mu_positive : 0 < nativeMu op5inhc5_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) op5inhc5_n02_m := by
    norm_num [op5inhc5_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def op5insx5_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem op5insx5_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 op5insx5_n02_m op5insx5_n02_m) ((2 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem op5insx5_n02_edge_ratio : (nativeMu op5insx5_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ op5insx5_n02_coefficient_identity

theorem op5insx5_n02_mu_positive : 0 < nativeMu op5insx5_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) op5insx5_n02_m := by
    norm_num [op5insx5_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def op6inhc6_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem op6inhc6_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 op6inhc6_n02_m op6inhc6_n02_m) ((1 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem op6inhc6_n02_edge_ratio : (nativeMu op6inhc6_n02_m true)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ op6inhc6_n02_coefficient_identity

theorem op6inhc6_n02_mu_positive : 0 < nativeMu op6inhc6_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) op6inhc6_n02_m := by
    norm_num [op6inhc6_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def op6insx6_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem op6insx6_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 op6insx6_n02_m op6insx6_n02_m) ((2 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem op6insx6_n02_edge_ratio : (nativeMu op6insx6_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ op6insx6_n02_coefficient_identity

theorem op6insx6_n02_mu_positive : 0 < nativeMu op6insx6_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) op6insx6_n02_m := by
    norm_num [op6insx6_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def sx5inhc5_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem sx5inhc5_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 sx5inhc5_n02_m sx5inhc5_n02_m) ((1 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem sx5inhc5_n02_edge_ratio : (nativeMu sx5inhc5_n02_m true)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ sx5inhc5_n02_coefficient_identity

theorem sx5inhc5_n02_mu_positive : 0 < nativeMu sx5inhc5_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) sx5inhc5_n02_m := by
    norm_num [sx5inhc5_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def sx5inop5_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem sx5inop5_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 sx5inop5_n02_m sx5inop5_n02_m) ((2 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem sx5inop5_n02_edge_ratio : (nativeMu sx5inop5_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ sx5inop5_n02_coefficient_identity

theorem sx5inop5_n02_mu_positive : 0 < nativeMu sx5inop5_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) sx5inop5_n02_m := by
    norm_num [sx5inop5_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def sx5insx5_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem sx5insx5_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 sx5insx5_n02_m sx5insx5_n02_m) ((2 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem sx5insx5_n02_edge_ratio : (nativeMu sx5insx5_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ sx5insx5_n02_coefficient_identity

theorem sx5insx5_n02_mu_positive : 0 < nativeMu sx5insx5_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) sx5insx5_n02_m := by
    norm_num [sx5insx5_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def sx6inhc6_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem sx6inhc6_n02_coefficient_identity : scalePair (if true then 2 else 1) (product 5 (product 5 sx6inhc6_n02_m sx6inhc6_n02_m) ((1 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem sx6inhc6_n02_edge_ratio : (nativeMu sx6inhc6_n02_m true)^2 * embed (Real.sqrt 5) ((1 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ sx6inhc6_n02_coefficient_identity

theorem sx6inhc6_n02_mu_positive : 0 < nativeMu sx6inhc6_n02_m true := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) sx6inhc6_n02_m := by
    norm_num [sx6inhc6_n02_m,embed] <;> nlinarith

  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))

def sx6inop6_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem sx6inop6_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 sx6inop6_n02_m sx6inop6_n02_m) ((2 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem sx6inop6_n02_edge_ratio : (nativeMu sx6inop6_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ sx6inop6_n02_coefficient_identity

theorem sx6inop6_n02_mu_positive : 0 < nativeMu sx6inop6_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) sx6inop6_n02_m := by
    norm_num [sx6inop6_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

def sx6insx6_n02_m : PairQ := ((1 : ℚ),(0 : ℚ))

theorem sx6insx6_n02_coefficient_identity : scalePair (if false then 2 else 1) (product 5 (product 5 sx6insx6_n02_m sx6insx6_n02_m) ((2 : ℚ),(0 : ℚ))) = ((2 : ℚ),(0 : ℚ)) := by decide +kernel

theorem sx6insx6_n02_edge_ratio : (nativeMu sx6insx6_n02_m false)^2 * embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) = embed (Real.sqrt 5) ((2 : ℚ),(0 : ℚ)) := native_ratio_sound _ _ _ _ sx6insx6_n02_coefficient_identity

theorem sx6insx6_n02_mu_positive : 0 < nativeMu sx6insx6_n02_m false := by
  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num
  have hp := Real.sqrt_nonneg (5 : ℝ)
  have hm : 0 < embed (Real.sqrt 5) sx6insx6_n02_m := by
    norm_num [sx6insx6_n02_m,embed] <;> nlinarith

  simpa [nativeMu] using hm

end PackingCertificates.Algebraic.NDReferenceEdges

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6_edge_exact

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6_reference_distance

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc120_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc120_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc120_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc16_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc16_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc16_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc24_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc24_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc24_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc600_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc600_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc600_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc8_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc8_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c120inc8_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc120_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc120_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc120_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc600_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc600_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc600_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc8_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc8_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c16inc8_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc120_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc120_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc120_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc600_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc600_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc600_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc8_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc8_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c24inc8_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc120_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc120_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc120_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc16_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc16_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc16_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc24_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc24_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc24_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc600_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc600_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc600_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc8_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc8_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c5inc8_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc120_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc120_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc120_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc16_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc16_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc16_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc24_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc24_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc24_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc600_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc600_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc600_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc8_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc8_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c600inc8_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc120_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc120_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc120_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc16_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc16_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc16_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc24_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc24_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc24_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc600_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc600_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.c8inc600_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5inop5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5inop5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5inop5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5insx5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5insx5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc5insx5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6inop6_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6inop6_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6inop6_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6insx6_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6insx6_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.hc6insx6_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5inhc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5inhc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5inhc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5insx5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5insx5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op5insx5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6inhc6_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6inhc6_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6inhc6_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6insx6_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6insx6_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.op6insx6_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5inhc5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5inhc5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5inhc5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5inop5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5inop5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5inop5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5insx5_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5insx5_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx5insx5_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6inhc6_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6inhc6_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6inhc6_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6inop6_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6inop6_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6inop6_n02_mu_positive

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6insx6_n02_coefficient_identity

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6insx6_n02_edge_ratio

#print axioms PackingCertificates.Algebraic.NDReferenceEdges.sx6insx6_n02_mu_positive
