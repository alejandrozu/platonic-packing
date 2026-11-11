# Lemma F in every dimension: status of the attempt (9 Nov 2026)

Goal: prove the cube centre lemma, and with it `s_d(n) = 2` for `2 ≤ n ≤ 2^d`, in **every** dimension `d`.
Lean proofs exist for `d ≤ 5` (Paper I). Hosono proved `d = 6` with computer assistance. We know of no result for `d ≥ 7`.

Notation: `R` is an orthogonal `d × d` matrix, `x_i = |R_ij|` is its column `j`, `S = ‖x‖₁`, `w_i = ‖Rᵢ‖₁` and
`F_j(R) = Σᵢ xᵢ (2 − wᵢ)`. Lemma F says `F_j(R) ≤ 1`.

**Summary (updated 9 Nov 2026, third session).** Proved in Lean: restricted Lemma F for `d ≤ 5`, together with three
reduction steps that work in every dimension:
* the near step (§2.1);
* the off-column step (§2.2);
* the concentrated pivot (§2.3).

The induction leaves a remaining case. **The pivot inequality `Ξ ≥ 0` (formerly "the pivot conjecture") is false**,
both in general and inside the remaining case. **The exact pivot inequality `F_j(R) ≤ F_j(Q)` is false in d = 9.**
All counterexamples are verified at 50–60-digit precision (§3). So no single-pivot rule of the form "smallest row
of column j, largest entry of that row" can carry the induction through every dimension. In the counterexamples
`F_j` sits far below 1; only the induction step fails. The earlier Lean reduction `centre_all_of_pivotConj`
assumed the false statement, so it has been removed.

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
* (Removed: `PivotConj` and the theorems deriving Lemma F in every dimension from it. `PivotConj` is false, see §3.)
* `lemmaFr_succ4`, `RemainingCase4`: the induction step that uses every proved reduction (near step, off-column
  step, concentrated pivot, `S ≤ 2`). It leaves only the matrices where the smallest-row pivot is spread
  (`ρ > c + ν/2` and `c² < 3/4`).

## 3. The pivot inequality is false; so is its exact form in d = 9

`caseA_ok` proves `Ξ ≥ 0` when the pivot row is concentrated. For a spread pivot row it fails.

**Counterexamples to `Ξ ≥ 0`** (`pivot_counterexamples.json`, checked by `verify_pivot_cex.py` at 50 digits). In both,
row `p` is the unique smallest row of column `j = 0` and column `q` holds the unique largest entry of row `p`. The
pivot is admissible (`‖r‖₁ ≤ 1 + c`), every row of `R` and of `Q` has ℓ¹ norm below 2, and the matrices are
orthogonal to 50 digits.

| d | ν | c | Ξ | exact `F_j(Q) − F_j(R)` |
|---|---|---|---|---|
| 5 | 0.00513 | 0.5265 | −2.51·10⁻⁴ | +9.2·10⁻³ |
| 6 | 0.00300 | 0.5186 | −8.99·10⁻⁴ | +4.7·10⁻³ |

Both lie near the equality case `R₀ = [1] ⊕ R'` of Lemma F, where row `p` of `R'` is the flat row
`(½, ½, ½, ½)`. There the near step applies anyway, because the row `h` with `R_hj ≈ 1` has rest ≈ 0. My earlier
random and optimised tests never sampled these neighbourhoods. The mechanism: rows whose entries have mixed signs
relative to row `p` actually shrink under the pivot, while the triangle inequality in `pivot_bound` assumes they grow.

**Inside the remaining case it still fails.** Take a block matrix
`(4 × 4 block with the flat row and row l = (√3/2, −1/(2√3), −1/(2√3), −1/(2√3)))  ⊕  (b × b block carrying column j)`,
with `b ≥ 5` so that `S > 2` and every rest > 1 can hold. Reshape the flat row at order `√ν` and mix in column `j` at
order `ν` (`blockrc3.py`). Then every hypothesis of the remaining case holds, and in d = 9, 10, 16% of the samples
give `Ξ < 0`, with `Ξ/ν` down to `−0.62`.

**The exact pivot inequality also fails in d = 9** (`exact_pivot_counterexample_d9.json`, `verify_exact_pivot_cex.py`,
60 digits). Here `R` is strictly inside the remaining case: rows ≤ 2, `min rest − 1 = 0.087`, `S − 2 = 0.072`,
unique smallest row and unique largest entry, admissible, rows of `Q` ≤ 2. Yet
`F_j(Q) − F_j(R) = −1.26·10⁻⁸`, with `F_j(R) = 0.3166`. The margins are small (argmin gap `10⁻⁸`), but the effect
is first order in `ν`, so it is not a rounding artefact.

**What this means.** In every counterexample `F_j(R)` is far below 1 (0.32 in d = 9), so Lemma F is not in danger.
Only the induction step "pivot at the smallest row" fails, and only where `F` has a lot of slack. A proof for all
dimensions therefore has to treat spread configurations by a direct bound, or use a strengthened (quantitative)
induction hypothesis that leaves room below 1. The pivot steps remain useful near the extremal configurations.

### 3.1 Attacking the spread case (9 Nov 2026, second session; superseded in part by §3)

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
`O(‖small part of row p‖₂²)`, so the cost is quadratic. In random tests the average over admissible `q` was always
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

1. **A quantitative induction hypothesis.** The numerics give the sharp band profile
   `F_j(R) ≤ 1 − (m + √(1 − m²) − 1)²`, with `m` the largest entry of column `j` (`m ≥ 1/√2`), with no violation in
   d = 3–8 (`bandind.py`). Combined with Hosono's near-step identity, which uses Lemma F on *all* columns of `Q`
   (`lemmaK`), the naive inductive inequality fails in about 1% of cases (`bandind.py`). It does show where slack is
   lost: the triangle inequality and the `E` term of `lemmaK`.
2. **A direct bound for spread configurations.** Show `F_j(R) ≤ 1` directly when the smallest row of column `j` is spread.
   The numerics give `F ≲ 0.5` there (`regionW.py`, `rcB.py`), and the induction is only needed elsewhere.
3. Block pivots (`Q = M − A (I + C)⁻¹ B` is orthogonal for any block size) for clusters of near-minimal rows.

## 7. The frame formulation and the cube-in-simplex picture (10 Nov 2026)

Decision: no separate d = 6 effort. Work goes into the statement for every dimension. A counterexample search
(`cexsearch.py`, d = 7, 9, 12, 16) found no restricted matrix with `F > 1`; the value 1 is reached only at
axis-aligned columns.

### 7.1 Frame formulation (unrestricted Lemma F)

Normalise column `j` to `v ≥ 0`. The other columns form a `d × (d−1)` matrix `C` whose columns are an orthonormal
basis of `v^⊥`. Its rows `r_i` have Gram matrix `I − vvᵀ`. Put `Value(C) = Σ_i v_i ‖r_i‖₁`. Then

`Lemma F  ⟺  Value(C) ≥ 2(S − 1)`,  `S = ‖v‖₁`.

### 7.2 Geometric meaning: the largest cube in an orthocentric simplex

A unit `(d−1)`-cube with edge frame `C` fits strictly inside the simplex
`Δ_λ(v) = {ξ > 0 : ⟨v, ξ⟩ = λ}` (vertices `(λ/v_i) e_i`) if and only if `λ > Value(C)/2`. So:

**Lemma F in dimension `d` ⟺ the largest `(d−1)`-cube inside the simplex with vertices `t_i e_i` has side at most
`1 / (Σ_i 1/t_i − 1/h)`, where `h = (Σ_i t_i⁻²)^(−1/2)` is the distance from the origin to the simplex.**

Conjecture H says the bound with the Helmert value is attained, by a cube with a facet inside the facet of the
simplex opposite its farthest vertex, and recursively so. For a triangle this is the classical fact that the largest
square in a triangle has a side on a side of the triangle, and the formula gives the known value `0.4641·e` for the
equilateral triangle.

Equivalent forms, each checked against the algebra:
* mixed volumes: `V(Δ[n−1], □) ≥ vol(Δ)` for every unit cube `□`, `n = d − 1` (for a simplex this is equivalent to
  "no translate of `□` fits strictly inside");
* chords: `Σ_k 1/L_k ≥ 1`, where `L_k` is the longest chord of `Δ_{S−1}(v)` in the direction of the `k`-th frame vector;
* averaged over the columns `j`, Lemma F is the identity `Σ_j (1 − F_j) = Σ_i (w_i − 1)²`.

### 7.3 The frame step (new inequality, numerically tight, not yet in Lean)

Remove row `p` (`ν = v_p`, `a = √(1−ν²)`) by rotating `ℝ^{d−1}` in the plane of `r_p` and `e_q` so that `r_p` becomes
`a e_q`, then delete row `p` and column `q`. This gives a frame `C''` for `v' = v_{≠p}/a`. If
`‖r_p‖₁ ≤ a + 2|C_pq|`, then

`Value(C) ≥ a · Value(C'') + 2 v_p |C_pq|`.   (∗)

Derivation: write `r_i = s_i + β_i û` with `û = r_p/a`, `β_i = −ν v_i/a`. The per-row triangle inequality gives the
lower bound `−κ s_iq − b_i(1 − c' + ρ')` for every sign of `s_iq`, and `Σ_i v_i s_iq = 0` removes the first term.
`star.py`: 97,617 cases inside the domain, minimum of LHS − RHS = `6·10⁻¹⁰`; outside the domain it fails.

With Lemma F for `v'`, (∗) closes the induction when `v_p (a − |C_pq|) ≤ (1 − a)(1 − v_p)`. Iterating (∗) gives
`Value(C) ≥ 2 Σ_t v_{p_t} |pivot_t|`, and the Helmert value is exactly the case where every pivot equals its
Gram–Schmidt residual.

In an adversarial search (`rules.py`, d = 5, 6, 8) the rule "best row" always closed the induction, and
"largest `v_p`" failed only once, slightly, next to an axis-aligned `v`. The rules "smallest `v_p`" and "most
concentrated row" fail, in line with §3.

### 7.4 Structure of minimisers (proved on paper)

Rotating two frame vectors in their plane (a Givens rotation of two columns of `C`) changes each affected term to
`A|cos(θ − φ)|`, which is concave between sign changes. So a minimiser of `Value` cannot sit strictly between
kinks of any pair: **at a minimiser the zero patterns of the columns of `C` are pairwise distinct**. In `d = 3`
this forces an axis-aligned row, and (∗) with `|C_pq| = a` then proves Lemma F in 3D in a few lines.

### 7.5 What is still missing

The **facet lemma**: a largest cube in `Δ(v)` can be taken with a facet parallel to a facet of the simplex
(equivalently, some minimiser of `Value` has an axis-aligned row). With it, (∗) proves Conjecture H and Lemma F in
every dimension by induction. The concavity argument of §7.4 gives it for `d = 3` only. For `d ≥ 4` it yields
single zero entries, not a full row. The pairwise bound `⟨|r_i|, |r_l|⟩ ≥ v_i v_l` alone is too weak (`lp.py`).

### 7.6 The facet lemma in d = 4: true numerically, but not a local statement

`locmin.py` (12 random `v`, 40 local descents each, d = 4):

* in every instance the global minimum of `Value` equals the Helmert value to 6 digits, and (except one numerical
  tie next to an axis-aligned `v`) the minimiser has an axis-aligned row. So the facet lemma holds numerically in 4D;
* each `v` has between 3 and 15 distinct local minima, and **most instances have local minima with no aligned row**
  (3 or 4 zero entries spread over different rows). Their excess over the Helmert value is sometimes tiny:
  `7·10⁻⁴`, `4·10⁻³`.

Consequences:
1. No local argument (first- or second-order conditions, the concavity of §7.4) can prove the facet lemma. A proof
   has to compare non-aligned vertex configurations with the Helmert configuration globally.
2. A proof of the facet lemma in d = 4 does not lift by itself. The induction step (∗) needs an aligned row at the
   global minimiser **in each dimension**, and the induction hypothesis (Lemma F one dimension down) says nothing
   about where the minimiser in the next dimension sits.

A candidate global mechanism (`flag.py`): with `v` sorted decreasingly and `β_k(c) = Σ_{i≥k} (sgn(c_k) v_i c_i)⁺`,
numerically `Σ_j max_{k≥2} β_k(c_j) ≥ H(v)/2` for every frame, with equality at the Helmert frame (d = 3–7, weak
optimiser). This is slightly stronger than Conjecture H and is not proved.

## 8. Literature check (10 Nov 2026)

**The problem itself.** `s_n(2) = 2` for `n ≥ 3` is posed as open in Hosono's issue #21
(<https://github.com/wand125/square-packing/issues/21>). His README says no proof exists in the literature for any
`n ≥ 3`, and Friedman's survey and *Cubes in Cubes* page give no lower bound for two cubes. Hosono proved
`n ≤ 6` with computer assistance; this repository has `n ≤ 5` in Lean.

**Our formulations.** No prior statement was found of Lemma F in every dimension (restricted or unrestricted),
of Conjecture H (§4), of the cube-in-simplex form (§7.2), or of the facet lemma (§7.5).

**Classical special cases of the cube-in-simplex form.** The simplices with vertices `t_i e_i` are the orthocentric
simplices with interior orthocentre; in the plane these are the acute triangles.

* `d = 3`: the largest square in a triangle. The equilateral value `(2√3 − 3)·e` is the Helmert value. Conway and
  Guy, *The Book of Numbers* (1996), p. 206, treat the placements of the largest square, for the equilateral and
  Calabi triangles.
* `d = 4`, uniform `v`: **H. T. Croft, "On maximal regular polyhedra inscribed in a regular polyhedron",
  Proc. London Math. Soc. (3) 41 (1980) 279–296.** It solves the largest cube in a regular tetrahedron: side
  `1/(1 + (2/3)√3 + (1/2)√6) = 0.29590654` for edge 1. Firsching (arXiv:1407.0683, Exp. Math.,
  doi:10.1080/10586458.2014.956374) lists it among the 14 cases Croft proved and confirms it numerically. This
  equals the Helmert prediction exactly: for `v = (½, ½, ½, ½)`, `H = √½ + √⅔ + √¾`. The cube fits iff
  `λ > H/2`, and the edge is `e = 2√2 λ`, so `side/e = 1/(√2 H) = 1/(1 + √6/2 + 2/√3)`.
  **So Conjecture H is a theorem for the regular tetrahedron (Croft).** The face-on-face cube attains the
  optimum, so the facet lemma holds there too. Croft's paper itself was not read (paywalled). Its method is the
  natural template for the 4D facet lemma.

**Not found.** The largest `n`-cube in a regular `n`-simplex for `n ≥ 4`; `ℓ¹`-minimal orthonormal bases of the
sum-zero hyperplane (Conjecture H for uniform `v`).

## 9. Every dimension reduced to the facet lemma, in Lean (10 Nov 2026)

`FacetStep.lean` (standard axioms only):

* `aligned_step`, `aligned_at`: if row `p` of an orthogonal `R` has no nonzero entry outside columns `j` and
  `q ≠ j`, then Lemma F in dimension `d − 1` gives `F_j(R) ≤ 1 − 2(1 − |R_pj|)(1 − |R_pq|)`. The pivot turns the
  minor into its polar factor `Q` with `M·j = c Q·j` and `x = −ν Q·j` exactly, so the step loses nothing.
* `colValue`, `Fcol_eq_colValue`: `F_j(R) = 2‖column j‖₁ − 1 − V_j(R)` with `V_j(R) = Σᵢ |R_ij|(‖row i‖₁ − |R_ij|)`.
* `FacetLemma d`: every orthogonal `R` and column `j` admit an orthogonal `R'` with the same `|column j|`,
  `V_j(R') ≤ V_j(R)` and an aligned row. `facetLemma_two`: trivial for `d = 2`.
* `lemmaF_succ_of_facet`, `lemmaF_of_facet`: Lemma F in dimension 5 and the facet lemma in dimensions `6, …, d`
  give Lemma F in dimension `d`.
* `centre_of_facet`, `cube_plateau_of_facet`: **the facet lemma in every dimension `≥ 6` gives the cube centre lemma
  and `s_d(n) = 2` for all `2 ≤ n ≤ 2^d`, in every dimension.**

Conjecture H implies the facet lemma (the Helmert frame has an aligned row, at the smallest entry of `v`). So the
chain is Conjecture H ⇒ facet lemma ⇒ (Lean) Lemma F ⇒ (Lean) `s_d(2) = 2`.

## 10. Restricted aligned step; the evidence campaign (10 Nov 2026)

**Lean** (`FacetStep.lean`, commit 5832d6c232, CI passed; all 157 audited declarations use standard axioms only):
at an aligned row the polar factor never lengthens a row, `‖Q_i‖₁ = w_i − (|ν| + c − 1)|Q_ij| ≤ w_i`, so restricted
Lemma F one dimension down suffices (`aligned_step_r`, `aligned_at_r`). With `FacetLemmaR`, `lemmaFr_of_facetR` and
`cube_plateau_of_facetR`, the restricted facet lemma in dimensions ≥ 6 also gives `s_d(n) = 2` in every dimension.
`lemmaF_le_four`, `lemmaF_all_of_facet`: Lemma F for `d ≤ 4`, and in every dimension from the facet lemma.

**On paper:** Conjecture H in dimension `d` gives Lemma F in dimension `d` directly (`Val ≥ H ≥ 2(S − 1)`).
Conjecture H holds for `d = 3` (facet lemma in 3D + the inscribed square on the shortest side is the largest).

**Numerics** (`evidence/`, commit 5c9e0344b8; Paper IV §6):
* global search, restricted and unrestricted, `d = 3–32`: the largest `F` is 1, only at axis-aligned columns;
* far region: the profile `Φ_d(τ)` does not depend on `d` (spread `5.5·10⁻⁴`); for `τ ≥ 1/2` it is the plane rotation,
  below `1/2` its values are attained by blocks of size 3, 4 (and in dimension ≤ 6); Hosono's d = 4 value 0.845 reproduced;
* remaining case RC(d): the largest `F` found grows, `1 − F ≈ 1.1/d` (0.730 at d = 5, 0.954 at d = 24), always at the
  boundary `S = 2`, with one entry near 1 and `d − 1` entries of order `1/d`; so `F ≤ S − 1` is asymptotically sharp
  on RC and a direct bound there must use `S − 2` or the rows. RC4(d): 0.678 (d = 5) to 0.942 (d = 24). With `S ≥ 2.1`,
  2.25, 2.5, 3 the values drop (d = 16: 0.883, 0.815, 0.689, 0.382);
* Conjecture H, `d = 3–12`, 11 vectors each: no frame below the Helmert value (smallest difference `2.6·10⁻¹⁷`);
  the best frame has an aligned row in 98 of 110 cases (all for `d ≤ 7`).
