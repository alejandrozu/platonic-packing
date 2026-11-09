# Lemma F in every dimension: status of the attempt (9 Nov 2026)

Goal: prove the cube centre lemma, and with it `s_d(n) = 2` for `2 ≤ n ≤ 2^d`, in **every** dimension `d`.
Lean proofs exist for `d ≤ 5` (Paper I). Hosono proved `d = 6` with computer assistance. We know of no result for `d ≥ 7`.

Notation: `R` is an orthogonal `d × d` matrix, `x_i = |R_ij|` is its column `j`, `S = ‖x‖₁`, `w_i = ‖Rᵢ‖₁` and
`F_j(R) = Σᵢ xᵢ (2 − wᵢ)`. Lemma F says `F_j(R) ≤ 1`.

**Summary.** In Lean, the cube centre lemma in every dimension now follows from a single explicit inequality, the
*pivot conjecture* `Ξ ≥ 0` (§4), needed only in dimensions `d ≥ 6` (`centre_all_of_pivotConj`). The conjecture is
proved in every dimension when the pivot row is concentrated (`caseA_ok`). It is verified numerically in the
remaining (spread) case, but not proved there yet.

## 1. Only the restricted lemma is needed

A unit cube inside a cube of side `s < 2` has widths `‖Rᵢ‖₁ ≤ s < 2`. So the cube centre lemma needs Lemma F
only for matrices whose rows all have ℓ¹ norm at most 2 (**restricted Lemma F**, `Restricted.LemmaFr`). Conversely,
a matrix with all rows of ℓ¹ norm `< 2` and `F_j > 1` puts the container's centre outside one copy, and the point
reflection then gives two cubes in a cube of side `< 2`. So restricted Lemma F in dimension `d` is the statement
`s_d(2) = 2`.

## 2. Proved in Lean

All of these use only `propext`, `Classical.choice` and `Quot.sound`.

### 2.1 The near step (`LemmaFr.lean`)

* `centre_of_lemmaF_rows` (in `CentreGeneral.lean`): restricted Lemma F gives the cube centre lemma, in any dimension.
* `near_step`, `step_at`: **Hosono's near-axis step works in every dimension for the restricted lemma.** With all
  rows of `R` at most 2, the rows of the polar factor `Q` are at most 2 as well, so `NearAxis.lemmaK` applies
  without the hypothesis `m ≤ 4`. The step works at any entry `c = R i₀ j ≠ 0` with `‖R_{i₀}‖₁ − |c| ≤ 1`.
* `remaining_bound`: if no entry of column `j` qualifies, then `F_j(R) ≤ S − 1`.
* `lemmaFr_le_four`, `centre_le_four`: since `S ≤ √d ≤ 2` for `d ≤ 4`, **restricted Lemma F and the cube centre
  lemma hold for `d ≤ 4`**, with no computer search and no case split.

### 2.2 The off-column step (`OffColumn.lean`)

Pivot at a row `p` and a column `q ≠ j` instead of at column `j`. Write `R = [c r; x M]` around the pivot
`c = R p q > 0` and let `Q = M − x rᵀ/(1 + c)` be the polar factor of the minor. Column `j` survives in `Q`.

* `offcol_step`, `offcol_at`: if `p` is a row where column `j` is smallest and `R p q ² ≥ 3/4`, then
  `F_j(R) ≤ F_j(Q)`, so restricted Lemma F in dimension `d − 1` gives `F_j(R) ≤ 1`.
  This removes the "sink" configurations that maximise `F` in the remaining case of §2.1.

### 2.3 The pivot inequality (`PivotStep.lean`)

Normalise the signs so that column `j` is nonnegative and `c = R p q > 0` (`flipM`). Put `ν = R p j`, `y_i = M i j`,
`a = 1/(1 + c)`, `L = ‖r‖₁`, `ρ = L − ν` (the part of row `p` outside columns `j` and `q`), `κ₁ = 1 + c − ρ` and
`Gᵢ = 2 − wᵢ`. Define

`Ξ = ν (c (c + L) − 1) + Σᵢ ( 2 κ₁ max(xᵢ, 0) (yᵢ − a ν xᵢ) − ν xᵢ Gᵢ )`.

* `pivot_bound`: **`F_j(R) ≤ F_j(Q) − a Ξ`** whenever `a ν xᵢ ≤ yᵢ` for all `i`. The only estimate used is the
  triangle inequality for the rows of `Q`. The rest is the orthogonality of the columns `q` and `j` and
  `‖column q‖₂ = 1`.
* `pivot_step`, `pivot_at_gen`: `Ξ ≥ 0` gives `F_j(R) ≤ 1` from restricted Lemma F in dimension `d − 1`.
* `exists_pivot`: for `d ≥ 5`, the row `p` where column `j` is smallest has its largest entry outside column `j`.
* `pivot_caseA`, `caseA_ok`, `pivot_at`: **`Ξ ≥ 0` in every dimension when row `p` is concentrated**, i.e. `p` is
  a row where column `j` is smallest, `c` is the largest entry of row `p`, and `ρ ≤ c + ν/2`. The proof has two
  parts. First, `c (c + L) ≥ 1` because `c` is the largest entry of a unit row. Second, each row with `xᵢ > 0` has
  `c Gᵢ ≤ 2c − 2c xᵢ − (c + ν) yᵢ`, from its orthogonality to row `p`.
* `lemmaFr_five`: restricted Lemma F in dimension 5, from Lemma F in dimension 5 (`LemmaF5.lemmaF5`). **The remaining
  case in `d = 5` is closed.**
* `PivotConj m`: `Ξ ≥ 0` for every normalised matrix of size `m + 1`, every row `p` where column `j` is smallest
  and every column `q ≠ j` holding the largest entry of row `p`.
* **`lemmaFr_all_of_pivotConj`, `centre_all_of_pivotConj`: if `PivotConj m` holds for all `m ≥ 5`, then restricted
  Lemma F and the cube centre lemma hold in every dimension.** Hence `s_d(n) = 2` for `2 ≤ n ≤ 2^d`.
* `lemmaFr_succ4`, `RemainingCase4`: the induction step that uses every proved reduction (near step, off-column
  step, concentrated pivot, `S ≤ 2`). It leaves only the matrices where the smallest-row pivot is spread
  (`ρ > c + ν/2` and `c² < 3/4`).

## 3. What is left: the pivot conjecture for a spread pivot row

`PivotConj` is open exactly when row `p` is spread: `ρ > c + ν/2` (by `caseA_ok`). Numerical evidence
(`scripts/optimality/lemmaF_all_d/`):

| test | d | result |
|---|---|---|
| exact `F_j(Q) − F_j(R)` for the smallest-row pivot, maximised by an optimiser over all restricted `R` (`exactD2.py`) | 4–8 | never below 0; the supremum 0 is attained only at axis-aligned rows |
| `F_j(Q) − F_j(R) − aΞ ≥ 0` (the identity of `pivot_bound`), random `R` (`checkX.py`) | 5–8 | holds in all samples |
| `min Ξ/ν`, random restricted `R` (`xiCheck.py`) | 6, 8, 10, 12, 14 | 0.062, 0.116, 0.210, 0.299, 0.341 (minimum at nearly axis-aligned rows, a concentrated case) |
| `min Ξ/ν` with a spread pivot row, `c ≤ 0.8`, optimiser (`minX2.py`) | 5, 6, 7, 8 | 0.416, 0.435, 0.496, 0.978 |
| `min Ξ/ν` with `ρ − c ≥ 0.5`, optimiser | 5, 6, 7 | 0.356, 0.482, 0.469 |

So in the open case `Ξ/ν` stays at least about 0.35, which is a wide margin. Attempts to build counterexamples
(spread pivot row, light rows with small positive `xᵢ` and `yᵢ ≈ ν`) all move back to a nearly axis-aligned pivot.

The difficulty is that single rows can have a negative term, with values down to `−0.15` found. Those terms are then
paid for by `ν (c (c + L) − 1)` and by the other rows. A proof therefore has to use the orthogonality between
different rows `i`, not only the orthogonality of each row with row `p`.

Region left after **every** proved step (`RemainingCase4`, refined by allowing the concentrated pivot and the
off-column step at any row, `regionW.py`): optimiser `sup F` = 0.43 (d = 5), 0.41 (d = 6), 0.50 (d = 7), far below 1.

### 3.1 Attacking the spread case (9 Nov 2026, second session)

**Averaging over pivot columns.** `pivot_bound` needs no argmax: any column `q ≠ j` with `R p q ≠ 0` gives
`F_j(R) ≤ F_j(Q^{(q)}) − a_q Ξ_q`, and the pivot is admissible (rows of `Q^{(q)}` at most 2) when
`c_q = |R p q| ≥ (w_p − 1)/2`. Weight `Ξ_q` by `c_q`:

* the terms `−ν xᵢ Gᵢ` combine through row orthogonality, `Σ_q R_pq R_iq = −ν yᵢ`, into `+ν² yᵢ Gᵢ ≥ 0`;
* the constants combine to `ν Σ_q c_q (c_q w_p − 1) = ν² (1 − ν w_p) ≥ 0`;
* the `κ₁` terms are `≥ 0` for admissible `q`.

So **if every nonzero entry of row `p` outside column `j` is an admissible pivot, some admissible `q` has `Ξ_q ≥ 0`**.
In closed form, `Σ_q c_q Ξ_q = ν²(1 − 2ν + F_j(R)) + (κ₁ terms)`.

Generic rows also have small entries (`0 < c_q < (w_p − 1)/2`). Leaving them out of the average leaves the cross term
`S3 = Σ_{small q} R_pq Σ_{i≠p} R_iq Gᵢ`. Writing `R_iq = Q_iq + a zᵢ R_pq` for one admissible pivot and applying
restricted Lemma F to `Q` (with `0 ≤ Gᵢ ≤ G^Q_i`) shows that the small entries cost only
`O(‖small part of row p‖₂²)`, so the cost is quadratic. Numerically the average over admissible `q` is always
`≥ 0` (`avgq.py`, `avgq2.py`, d = 5–10). The quadratic cost is not yet absorbed in general when `ν` is tiny.

**Stress test in high dimension.** A heuristic count suggests many rows `i` with `yᵢ ≈ ν`, a small positive entry
in column `q` and `Gᵢ ≈ 1` could pile up per-row deficits of order `√n` against the fixed surplus `ν (c w_p − 1)`.
Explicit constructions (`construct3.py`, `construct4.py`) show why this fails. To share the pivot direction, the
parts of these rows outside the pivot block must form a simplex (`Σ oᵢ = 0`). That forces each of them to have
ℓ¹ norm about 2, which kills the slack `Gᵢ` the deficit needed. Every feasible structured instance had `Ξ/ν ≥ 1.1`.

**Consequence for a proof.** The protection is a *global* orthogonality effect among the rows meeting column `q`,
not a row-by-row one. This explains why every per-row bracket bound fails and why the isotropic relaxation (§5) fails.
A proof has to carry global information: either restricted Lemma F applied to the columns of `Q` (as in the
small-entry bound above), or a 2 × 2 block pivot.

## 4. The Helmert conjecture (would give the unrestricted Lemma F in every dimension)

**Reformulation.** Take `v = |column j|` (signs can be absorbed), and let `b₂, …, b_d` be the other columns, an
orthonormal basis of `v^⊥`. Then

`Lemma F  ⟺  Σ_k Σ_i vᵢ |b_k(i)| ≥ 2(‖v‖₁ − 1)` for every orthonormal basis `(b_k)` of `v^⊥`.

**The Helmert basis.** Sort `v₁ ≥ … ≥ v_d` and let `A_k = v₁² + … + v_{k−1}²`. The vectors
`b_k ∝ A_k e_k − v_k (v₁, …, v_{k−1}, 0, …)` form an orthonormal basis of `v^⊥` with
`Σ_k ‖v ∘ b_k‖₁ = 2 Σ_{k≥2} v_k √(A_k / A_{k+1})`, which is always at least `2(‖v‖₁ − 1)` (telescoping).

**Conjecture H.** For every unit `v ≥ 0`, the Helmert basis minimises `Σ_k ‖v ∘ b_k‖₁`. Conjecture H implies
Lemma F, unrestricted, in every dimension. Local optimisation never went below the Helmert value in any test
(`helmert.py`, `helmert2.py`, `uniform.py`).

## 5. Two obstructions

* **No convex certificate works for `d ≥ 6`.** Replacing the orthonormal basis by any isotropic measure on the
  sphere of `v^⊥` is false from `d = 6` on: for uniform `v`, the measure uniform on `(e_a − e_b)/√2` gives
  `(d−1)√(2/d) < 2(√d − 1)`. A proof must use the fact that the basis is orthonormal. The induction of §2 does.
* **The positive-part strengthening is false.** `Σᵢ xᵢ max(2 − wᵢ, 0) ≤ 1` fails for an 8×8 orthogonal matrix
  (`1.0112`, `fplus_counterexample_d8.json`), so the restriction to rows `≤ 2` in §1 is essential.

## 6. Next steps

1. Prove `Ξ ≥ 0` for a spread pivot row. Two routes look plausible. One is a bound on the light rows with
   `xᵢ > 0` and `yᵢ ≈ ν` using the column identities `Σᵢ xᵢ Mᵢ = −c r'` and `Σᵢ yᵢ Mᵢ = −ν r'`. The other is a
   two-row (2 × 2 block) pivot for configurations where two near-minimal rows share their two large columns, as in
   the extremal examples of `regionW.py`. The block pivot is available in every size. For orthogonal
   `R = [C B; A M]` with a `k × k` block `C` and `I + C` invertible, `Q = M − A (I + C)⁻¹ B` is orthogonal
   (checked numerically). For `k = 1` this is the polar factor used above.
2. A weaker statement also suffices: `Ξ ≥ 0` for *some* admissible pivot row `b`, not necessarily the smallest one.
   The block-form `pivot_step` only needs `a y_b xᵢ ≤ yᵢ` for all `i`, together with `‖r‖₁ ≤ 1 + c`.
3. Any proof of `PivotConj m` for `m ≥ 5` plugs into `centre_all_of_pivotConj` directly. A proof for `m = 5`
   alone gives `d = 6` through `lemmaFr_succ_of_pivotConj lemmaFr_five`.
