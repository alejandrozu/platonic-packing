import PackingOptimality.Patterns

/-!
# Relations between the patterns, formalized

The pattern classes of `docs/PATTERNS.md` are linked by a few general implications. These are the ones
used by the optimality proofs and by the transfer web (`scripts/patterns/transfer.py`).

* **Transfer by inclusion** (`Packing.transfer_piece`, `Packing.transfer_container`). Composition with a single
  inner piece: if one copy of `K` fits in `t • K'`, every packing of `n` copies of `K'` in `s • C` gives `n`
  copies of `K` in `(s t) • C`; if one copy of `C'` fits in `λ • C`, every packing of `n` copies of `K` in
  `s • C'` gives one in `(λ s) • C`. These are `Packing.compose` with `m = 1` or `n = 1`.
* **Extremal lower bound + deletion = an optimal plateau** (`optimal_plateau_of_common_point`,
  `optimal_plateau_of_one_piece`). If every copy at a smaller scale contains a fixed point, or if no copy fits at
  a smaller scale at all, a packing of `N` pieces at scale `s` makes `s` optimal for every `n` from 2 (or 1) to
  `N`. Every optimality result for a plateau in the catalogue has this form.
-/

set_option linter.unusedSectionVars false

namespace PackingOptimality

open Set
open scoped Pointwise

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [FiniteDimensional ℝ E]
  [MeasurableSpace E] [BorelSpace E]

/-- **Transfer through the piece.** `s_{K in C}(n) ≤ t · s_{K' in C}(n)` when `K` fits in `t • K'`. -/
noncomputable def Packing.transfer_piece {K K' C : Set E} {s t : ℝ} {n : ℕ} (A : Packing K' C s n)
    (B : Packing K K' t 1) (ht : t ≠ 0) : Packing K C (s * t) n :=
  (Nat.mul_one n) ▸ A.compose B ht

/-- **Transfer through the container.** `s_{K in C}(n) ≤ λ · s_{K in C'}(n)` when `C'` fits in `λ • C`. -/
noncomputable def Packing.transfer_container {K C' C : Set E} {s l : ℝ} {n : ℕ} (A : Packing C' C l 1)
    (B : Packing K C' s n) (hs : s ≠ 0) : Packing K C (l * s) n :=
  (Nat.one_mul n) ▸ A.compose B hs

/-- **A common point gives an optimal plateau.** -/
theorem optimal_plateau_of_common_point {K C : Set E} {s : ℝ} {N : ℕ} (c : E)
    (h : ∀ t : ℝ, 0 ≤ t → t < s → ∀ g : E ≃ᵃⁱ[ℝ] E, g '' K ⊆ t • C → c ∈ interior (g '' K))
    (P : Packing K C s N) (n : ℕ) (hn2 : 2 ≤ n) (hnN : n ≤ N) :
    Nonempty (Packing K C s n) ∧ ∀ t : ℝ, 0 ≤ t → Packing K C t n → s ≤ t := by
  refine ⟨⟨P.restrict hnN⟩, fun t ht Q => ?_⟩
  by_contra hlt
  push Not at hlt
  exact no_packing_two_of_common_point c (fun g hg => h t ht hlt g hg) hn2 Q

/-- **A one-piece bound gives an optimal plateau.** -/
theorem optimal_plateau_of_one_piece {K C : Set E} {s : ℝ} {N : ℕ}
    (h : ∀ t : ℝ, 0 ≤ t → t < s → ∀ g : E ≃ᵃⁱ[ℝ] E, ¬ g '' K ⊆ t • C)
    (P : Packing K C s N) (n : ℕ) (hn1 : 1 ≤ n) (hnN : n ≤ N) :
    Nonempty (Packing K C s n) ∧ ∀ t : ℝ, 0 ≤ t → Packing K C t n → s ≤ t := by
  refine ⟨⟨P.restrict hnN⟩, fun t ht Q => ?_⟩
  by_contra hlt
  push Not at hlt
  exact h t ht hlt (Q.g ⟨0, hn1⟩) (Q.inside _)

end PackingOptimality
