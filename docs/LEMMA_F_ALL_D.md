# Lemma F in every dimension: status of the attempt (9 Nov 2026)

Goal: prove the cube centre lemma, and with it `s_d(n) = 2` for `2 ≤ n ≤ 2^d`, in **every** dimension `d`.
Lean proofs exist for `d ≤ 5` (Paper I). Hosono proved `d = 6` with computer assistance. We know of no result for `d ≥ 7`.

Notation: `R` is an orthogonal `d × d` matrix, `x_i = |R_ij|` is its column `j`, `S = ‖x‖₁`, and
`F_j(R) = Σᵢ xᵢ (2 − ‖Rᵢ‖₁)`. Lemma F says `F_j(R) ≤ 1`.

## 1. Only the restricted lemma is needed

A unit cube inside a cube of side `s < 2` has widths `‖Rᵢ‖₁ ≤ s < 2`. So the cube centre lemma needs Lemma F
only for matrices whose rows all have ℓ¹ norm at most 2 (**restricted Lemma F**, `Restricted.LemmaFr`). Conversely,
a matrix with all rows of ℓ¹ norm `< 2` and `F_j > 1` puts the container's centre outside one copy, and the point
reflection then gives two cubes in a cube of side `< 2`. So restricted Lemma F in dimension `d` is the statement
`s_d(2) = 2`.

## 2. Proved in Lean (`lean-optimality/PackingOptimality/LemmaFr.lean`)

* `centre_of_lemmaF_rows` (in `CentreGeneral.lean`): restricted Lemma F gives the cube centre lemma, in any dimension.
* `near_step`, `step_at`: **Hosono's near-axis step works in every dimension for the restricted lemma.** With all
  rows of `R` at most 2, the rows of the polar factor `Q` are at most 2 as well (`‖Qᵢ‖₁ ≤ ‖Mᵢ‖₁ + |xᵢ|‖r‖₁/(1+c)`),
  so `NearAxis.lemmaK` applies without the hypothesis `m ≤ 4`. The step works at **any** entry `c = R i₀ j ≠ 0`
  whose row has `‖R_{i₀}‖₁ − |c| ≤ 1`. It does not need `c` to be large.
* `remaining_bound`: if no entry of column `j` qualifies, then `F_j(R) ≤ S − 1`.
* `lemmaFr_succ`: restricted Lemma F in dimension `m`, plus the *remaining case* in dimension `m + 1`, gives
  restricted Lemma F in dimension `m + 1`.
* `lemmaFr_le_four`, `centre_le_four`: since `S ≤ √d ≤ 2` for `d ≤ 4`, the remaining case is empty, and
  **restricted Lemma F and the cube centre lemma hold for `d ≤ 4`**. The proof has no computer search and no case
  split. It replaces the 3D minimiser argument and the 4D far region (81 cases) of Paper I.

All of these use only `propext`, `Classical.choice` and `Quot.sound`.

## 3. What is left: the remaining case

**Remaining case in dimension `d`:** `R` orthogonal with all rows `≤ 2`; every row `i` with `xᵢ ≠ 0` has
`‖Rᵢ‖₁ > 1 + xᵢ`; and `S > 2`. Show `F_j(R) ≤ 1`. Equivalently, `Σᵢ xᵢ(‖Rᵢ‖₁ − xᵢ − 1) ≥ S − 2`.

Numerical supremum of `F` in the remaining case (penalty method, 200 restarts, `remaining.py`):

| d | 5 | 6 | 7 | 8 |
|---|---|---|---|---|
| sup F | 0.723 | 0.786 | 0.824 | 0.848 |

The maximisers have the same shape. One "sink" row holds a large entry `c` of the column and has ℓ¹ norm exactly 2.
The other rows have small entries and row norms just above `1 + xᵢ`. In every run the maximiser sits at the boundary
`S = 2`. The margin shrinks with `d`, roughly like `1/d`, so a proof for all `d` must be sharp near `c² ≈ 1 − 1/d`.
It must also use the row bound 2 on the sink row, which is active at the maximiser.

## 4. The Helmert conjecture (would give the unrestricted Lemma F in every dimension)

**Reformulation.** Take `v = |column j|` (signs can be absorbed), and let `b₂, …, b_d` be the other columns, an
orthonormal basis of `v^⊥`. Then

`Lemma F  ⟺  Σ_k Σ_i vᵢ |b_k(i)| ≥ 2(‖v‖₁ − 1)` for every orthonormal basis `(b_k)` of `v^⊥`.

**The Helmert basis.** Sort `v₁ ≥ … ≥ v_d` and let `A_k = v₁² + … + v_{k−1}²`. The vectors
`b_k ∝ A_k e_k − v_k (v₁, …, v_{k−1}, 0, …)` form an orthonormal basis of `v^⊥` with
`Σ_k ‖v ∘ b_k‖₁ = 2 Σ_{k≥2} v_k √(A_k / A_{k+1})`.
Put `a_k = √A_k`. Each term of `v_k(1 − √(A_k/A_{k+1})) = v_k(a_{k+1} − a_k)/a_{k+1}` is at most `a_{k+1} − a_k`, and
these telescope to `1 − v₁`. So the **Helmert value is always at least `2(‖v‖₁ − 1)`**.

**Conjecture H.** For every unit `v ≥ 0`, the Helmert basis minimises `Σ_k ‖v ∘ b_k‖₁` over orthonormal bases of
`v^⊥`. Conjecture H implies Lemma F, unrestricted, in every dimension.

Evidence (`helmert.py`, `helmert2.py`): local optimisation from random and perturbed starts never went below the
Helmert value in any test. That covers 40 random vectors with 25 restarts each for `d = 3–7`, and sink-shaped,
two-large-entry and geometric vectors with 30 restarts each for `d = 6, 8, 10`. For the uniform vector the optimum
found equals the Helmert value in `d = 5` and is within 0.07 of it, above it, for `d ≤ 12` (`uniform.py`).

## 5. Two obstructions

* **No convex certificate works for `d ≥ 6`.** Replacing the orthonormal basis by any isotropic measure on the
  sphere of `v^⊥` (the convex relaxation behind every zero-sum or Cauchy–Schwarz bound) is false from `d = 6` on.
  For uniform `v`, the measure uniform on the vectors `(e_a − e_b)/√2` gives `(d−1)√(2/d) < 2(√d − 1)` when
  `d ≥ 6`. A proof must use the fact that the basis is orthonormal. This is why the far-region bound of Paper I
  stops working at `d = 6`: at the uniform column it gives `(2−√2)√d − 1 + √2/√d`, which is `1.012` for `d = 6`.
* **The positive-part strengthening is false.** `Σᵢ xᵢ max(2 − ‖Rᵢ‖₁, 0) ≤ 1` would have repaired the near step
  without the row restriction. An 8×8 orthogonal matrix gives `1.0112`
  (`scripts/optimality/lemmaF_all_d/fplus_counterexample_d8.json`, orthogonality error `7·10⁻¹⁶`). Lemma F holds
  for that matrix (`0.656`), but this route is closed. The restriction to rows `≤ 2` in §2 is what makes the near
  step work.

## 6. Next steps

1. Close the remaining case in `d = 5`. That gives a short new Lean proof of the 5D centre lemma, without the
   1174-case band certificate.
2. Then `d = 6`, which would be the first Lean proof there (Hosono's is computer-assisted).
3. For all `d`: either prove Conjecture H (an induction that removes the smallest coordinate, mirroring the
   recursive structure of the Helmert basis), or prove the remaining case directly with an argument sharp to
   `O(1/d)` near the sink configurations.
