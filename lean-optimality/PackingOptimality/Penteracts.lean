import PackingOptimality.LemmaF5
import PackingOptimality.CentreGeneral

/-!
# 5-cubes in a 5-cube, n = 2, …, 32: side 2 is optimal

Lemma F in dimension 5 (`LemmaF5.lemmaF5`) gives the cube centre lemma in dimension 5
(`CentreGeneral.centre_of_lemmaF`): a unit 5-cube inside a 5-cube of side `s < 2` contains the centre. So any
two such cubes share an interior point, and the 2×2×2×2×2 grid gives side 2 for every `2 ≤ n ≤ 32`.

The result s₅(2) = 2 was first proved by Hiroaki Hosono (wand125) with a computer-assisted far region (a
spectral certificate). The proof here is checked by Lean: Hosono's near-axis step (ported in `NearAxis`), a new
rotated-weight bound for the band `9/20 ≤ c² ≤ 3/4`, and the elementary far region, with line certificates that
Lean verifies case by case.
-/

namespace PackingOptimality

open Set
open scoped Pointwise

/-- **The cube centre lemma in dimension 5.** -/
theorem centre5 (s : ℝ) (hs0 : 0 ≤ s) (hs : s < 2)
    (g : EuclideanSpace ℝ (Fin 5) ≃ᵃⁱ[ℝ] EuclideanSpace ℝ (Fin 5)) (hg : g '' cube 5 ⊆ s • cube 5) :
    (s / 2) • WithLp.toLp 2 (fun _ => (1 : ℝ)) ∈ interior (g '' cube 5) :=
  CentreGeneral.centre_of_lemmaF LemmaF5.lemmaF5 s hs0 hs g hg

/-- **5-cubes in a 5-cube, 2 ≤ n ≤ 32: side 2 is optimal.** -/
theorem hc5inhc5_plateau {n : ℕ} (hn2 : 2 ≤ n) (hn : n ≤ 32) :
    Nonempty (Packing (cube 5) (cube 5) 2 n) ∧ ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s n → 2 ≤ s :=
  cube_plateau_of_centre_lemma (d := 5) (by norm_num) centre5 hn2 hn

theorem hc5inhc5_n02 : Nonempty (Packing (cube 5) (cube 5) 2 2) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 2 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n03 : Nonempty (Packing (cube 5) (cube 5) 2 3) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 3 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n04 : Nonempty (Packing (cube 5) (cube 5) 2 4) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 4 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n05 : Nonempty (Packing (cube 5) (cube 5) 2 5) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 5 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n06 : Nonempty (Packing (cube 5) (cube 5) 2 6) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 6 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n07 : Nonempty (Packing (cube 5) (cube 5) 2 7) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 7 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n08 : Nonempty (Packing (cube 5) (cube 5) 2 8) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 8 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n09 : Nonempty (Packing (cube 5) (cube 5) 2 9) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 9 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n10 : Nonempty (Packing (cube 5) (cube 5) 2 10) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 10 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n11 : Nonempty (Packing (cube 5) (cube 5) 2 11) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 11 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n12 : Nonempty (Packing (cube 5) (cube 5) 2 12) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 12 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n13 : Nonempty (Packing (cube 5) (cube 5) 2 13) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 13 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n14 : Nonempty (Packing (cube 5) (cube 5) 2 14) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 14 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n15 : Nonempty (Packing (cube 5) (cube 5) 2 15) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 15 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n16 : Nonempty (Packing (cube 5) (cube 5) 2 16) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 16 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n17 : Nonempty (Packing (cube 5) (cube 5) 2 17) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 17 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n18 : Nonempty (Packing (cube 5) (cube 5) 2 18) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 18 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n19 : Nonempty (Packing (cube 5) (cube 5) 2 19) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 19 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n20 : Nonempty (Packing (cube 5) (cube 5) 2 20) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 20 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n21 : Nonempty (Packing (cube 5) (cube 5) 2 21) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 21 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n22 : Nonempty (Packing (cube 5) (cube 5) 2 22) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 22 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n23 : Nonempty (Packing (cube 5) (cube 5) 2 23) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 23 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n24 : Nonempty (Packing (cube 5) (cube 5) 2 24) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 24 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n25 : Nonempty (Packing (cube 5) (cube 5) 2 25) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 25 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n26 : Nonempty (Packing (cube 5) (cube 5) 2 26) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 26 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n27 : Nonempty (Packing (cube 5) (cube 5) 2 27) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 27 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n28 : Nonempty (Packing (cube 5) (cube 5) 2 28) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 28 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n29 : Nonempty (Packing (cube 5) (cube 5) 2 29) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 29 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n30 : Nonempty (Packing (cube 5) (cube 5) 2 30) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 30 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)
theorem hc5inhc5_n31 : Nonempty (Packing (cube 5) (cube 5) 2 31) ∧
    ∀ s : ℝ, 0 ≤ s → Packing (cube 5) (cube 5) s 31 → 2 ≤ s := hc5inhc5_plateau (by norm_num) (by norm_num)

end PackingOptimality
