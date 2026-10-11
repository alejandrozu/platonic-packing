# Finite polyhedral fits: discrete scale jumps, orientational domains, and contact structure in 351 certified constructions

**Alejandro Zarzuelo**
Research manuscript draft, 11 October 2026. Author name, affiliation, acknowledgments, and final venue formatting to be confirmed before submission. Computational analysis and drafting assistance: OpenAI Codex; the underlying search software was developed with Claude under the author's direction.

**Data and software:** [alejandrozu/platonic-packing](https://github.com/alejandrozu/platonic-packing). The data freeze is Git commit `e15b496ae7306287e0e70bb5b14be79f5dfdde84`. This manuscript reports that finite archive, rather than claiming a complete or continuously updated catalogue of the world's best packings.

## Abstract

Packing a finite number of congruent polyhedra inside a polyhedral container produces pronounced changes in required container size as the number of pieces increases. Some adjacent counts share a construction scale, while other additions require a substantial expansion. We study 351 certified constructions in nine ordered pairs of Platonic solids, with every count from 2 through 40. Five pairs use the same solid for pieces and container; four use mixed pairs. We distinguish the exact feasible scale of each archived construction, the numerically estimated touching limit, and a monotone feasible envelope obtained by deleting pieces from larger constructions. We analyze absolute and relative scale increments, occupied volume fraction, orientational similarity modulo the proper rotational symmetry group of the piece, and graphs of near contacts determined by Euclidean feature distances. Contact-connected orientational domains provide a precisely defined geometric proxy for grains, while avoiding a claim of physical crystallization. The archive exhibits long count plateaus, sharp expansion steps, aligned and dispersed orientations, and large differences between raw edge scale and volume-normalized efficiency. None of these observations establishes global optimality. Closed-form labels attached to numerical touching limits remain conjectures unless supported by an independent symbolic construction. The accompanying machine-readable tables, source hashes, scripts, and figures expose every calculation and provide a basis for experiments on confinement, orientational organization, and lower-bound proofs.

**Keywords:** finite packing; Platonic solid; convex polytope; confinement; contact graph; orientational order; certified upper bound.

## 1. Finite confinement as a distinct packing problem

The density of an infinite or periodic packing and the size of a container holding a prescribed finite number of pieces ask related but different questions. A finite container imposes a particular boundary shape and a fixed count. Its corners, faces, and edges can reward arrangements that do not extend periodically. Removing one piece can leave an extensive void without changing the arrangement's bounding scale; adding one piece can force a new layer, an altered orientation pattern, or a different contact structure. The resulting count-dependent curve is therefore a useful object in its own right.

This paper studies *polyhedral fits*: finite arrangements of congruent polyhedra with disjoint interiors inside a polyhedral container. The expression is descriptive. It is not used here to claim that a new mathematical subject has been established by consensus, nor to replace the established language of packing convex bodies. The practical aim is to place several familiar finite packing problems and less extensively tabulated shape pairs in a common framework with explicit geometry, common units, and comparable structural measurements.

A close experimental precedent is [Teich et al. (2016)](https://doi.org/10.1073/pnas.1524875113), who compressed clusters of Platonic solids with 4–60 pieces in spherical containers and studied density, layers, symmetry, and particularly dense counts. Their sphere boundary differs from the polyhedral boundaries here, so their count sequences are comparison material rather than predictions for this archive. General finite-container methods also precede the current project: [Egeblad et al. (2009)](https://doi.org/10.1016/j.comgeo.2008.06.003) treated translational packing of arbitrary polytopes, while [Romanova et al. (2018)](https://doi.org/10.1016/j.ejor.2018.01.025) treated continuous rotations in a cuboid-volume objective. The contribution evaluated here is the particular certified dataset and its structural measurements.

The underlying project generalizes a soft-to-rigid computational search from cubes to convex polyhedra. That procedure is documented in the companion methods paper and in the repository's `docs/FINAL_REPORT.md`. The present paper concentrates on the *arrangements found*: which counts require expansions, which share a scale, how the pieces orient, how contacts connect them, and which patterns justify further mathematical investigation. Methodological novelty and geometric novelty should be evaluated separately. A more general search can be useful even when a particular cube record is equaled or improved elsewhere.

The scope is nine ordered piece/container pairs, not all 25 pairs of the five Platonic solids and not all convex polyhedra. All arrangements use a single piece type within a given container. There are no records here of simultaneous mixtures of tetrahedra and cubes, or of other two-species mixtures. Reaching the same scale at two different *counts* is consequently an observation about one species at a time. Questions about jointly packing two *types* require a separate heterogeneous dataset.

## 2. Definitions, normalization, and evidence levels

### 2.1 The optimum and the archived construction

Let $A$ be a centered unit-edge container solid and $B$ a centered unit-edge piece solid. Define

\[
s^*_{A,B}(n)=\min\{s>0:\ \bigcup_{i=1}^n(c_i+R_iB)\subseteq sA,
\quad \operatorname{int}(c_i+R_iB)\cap\operatorname{int}(c_j+R_jB)=\varnothing\ (i\ne j)\},
\]

where $R_i\in SO(3)$. The feasible arrangements allow translations and proper rotations. The optimum is attained: a known finite feasible scale bounds the translations, rotations form a compact space, and the weak containment and non-overlap conditions persist under limits. Removing a piece immediately gives $s^*(n)\le s^*(n+1)$.

An archived feasible value is denoted $U_n$, corresponding to the record field `s_full`. An independently verified record establishes $s^*(n)\le U_n$. It does not establish equality. The record also contains `s_tight`, denoted $T_n$, a numerical touching-limit estimate from local tightening. Its twelve displayed decimal places are a computational output convention, not twelve independently proved digits of the optimum. A reported algebraic expression near $T_n$ remains a conjectural recognition of that numerical value.

The exact verifier interprets stored floating-point coordinates as exact dyadic rationals, and the homogeneous quaternion rotation formula maps each nonzero rational quaternion to an exactly orthogonal rational matrix. Combined with canonical solid coordinates in $\mathbb Q(\sqrt2,\sqrt5)$, containment and separating-plane signs can therefore be decided in exact arithmetic. The certificate concerns the stored construction at $U_n$, with positive clearance, rather than the inferred touching configuration at $T_n$. Floating-point calculations of angles, distances, and structural descriptors in this paper are a different evidence layer and are not promoted to exact theorems by the existence of a feasibility certificate.

### 2.2 Volume-normalized scale

If $V_A,V_B$ are the volumes of unit-edge solids, every feasible arrangement satisfies

\[
L_n=\left(\frac{nV_B}{V_A}\right)^{1/3}\le s^*(n)\le U_n.
\]

We use the occupied volume fraction $\eta_n=nV_B/(V_AU_n^3)$ and the normalized scale $\lambda_n=U_n/L_n=\eta_n^{-1/3}$. These are equivalent summaries of finite confinement efficiency. A value $\lambda=1$ would saturate the volume bound, leaving no void volume; a value $\lambda>1$ includes both voids and any limitations of the search. The relative linear gap to this lower bound is $100(\lambda-1)\%$. It is a bound gap, not a measured error relative to the unknown optimum.

Raw edge ratios are appropriate for describing a named shape pair, but can mislead across mixed pairs. A unit-edge dodecahedron has substantially more volume than a unit-edge icosahedron, and a unit-edge cube has more volume than a unit-edge octahedron. Reversing pieces and container consequently changes the volume bound even before orientation or packing organization enters. Comparisons between mixed pairs therefore report both $U$ and $\eta$, rather than treating a smaller edge ratio as automatically more efficient.

The common normalization also exposes a useful limitation. An occupied volume fraction from 2–40 pieces in a bounded solid is not an estimate of the asymptotic density of the same shape in unbounded space. Surface layers occupy a substantial share of the configurations, and the container and piece geometries can be specially matched. No extrapolated infinite-packing density is claimed.

### 2.3 Three meanings of a plateau

We distinguish an identical stored certified value, an identical certified envelope value, and a numerical touching plateau. Two `s_full` entries are identical only when their parsed binary floating-point values coincide; the hexadecimal representations are retained in the data table. In that case, both certified constructions exist at the same stated scale. This proves equality of the *reported upper bounds*, not equality of the optima.

For numerical touching plateaus we require $\max T_n-\min T_n\le10^{-8}$ over a contiguous count interval. The comparison uses the whole run's range, avoiding a chain of individually small increments whose total exceeds the threshold. Five-decimal table equality is insufficient: distinct sizes can round or truncate to the same display. Moreover, differing clearances can make equal touching estimates yield slightly different $U_n$ values.

The third object is a certified deletion envelope,

\[
E_n=\min_{m\ge n} U_m.
\]

Any selection of $n$ pieces from the feasible $m$-piece witness remains feasible at $U_m$, so $E_n$ is a valid monotone upper bound. Every envelope entry records its witness. A plateau in $E_n$ can be produced by deletion without showing that the independently optimized $n$-piece geometry is congruent to the larger arrangement. It is consequently a statement about available feasible scales, not a claim of a unique structural family.

### 2.4 Absolute and relative marginal costs

For $n\ge3$, define the absolute edge increment $\Delta U_n=U_n-U_{n-1}$, the relative edge increment $r_n=U_n/U_{n-1}-1$, and the relative container-volume increment $v_n=(U_n/U_{n-1})^3-1$. These three quantities answer different practical questions. An absolute change is expressed in piece-edge units; a relative change compares that change with the previous container; and $v_n$ measures the additional container volume incurred by an extra piece.

The exact density relation is

\[
\frac{\eta_n}{\eta_{n-1}}=\frac{n}{n-1}\left(\frac{U_{n-1}}{U_n}\right)^3.
\]

Density rises after adding a piece precisely when the relative container-volume expansion is smaller than $1/(n-1)$. On a constant-scale plateau, density increases in proportion to count; at an expansion step it can drop sharply. Thus an increasing size curve does not imply an increasing density curve. A supplementary count-scaled edge increment $a_n=(n-1)r_n$ compares changes with the $\sim1/[3(n-1)]$ relative growth of the elementary volume bound. This normalization is descriptive; finite discrete changes need not follow a smooth derivative.

## 3. Reproducible structural measurements

### 3.1 Frozen input and provenance

The analysis reads every `records/*/*_nNN.json` file in the frozen repository. It verifies that the declared piece count equals the pose-array length, checks recomputed density against the stored full-precision value, and requires all 39 counts for each of the nine families. The script also checks geometric distance calculations against known cube face, edge, and vertex separations. A SHA-256 manifest records the bytes of every analyzed record and of `src/solids.json`; the metadata includes the Git commit, Python and NumPy versions, thresholds, and a combined record-manifest hash. The full numerical tables are derived from the JSON values rather than from the rounded README or historical prose.

This distinction matters because the large project report preserves intermediate results and quotes earlier mathematical notes. For example, intermediate tetrahedral and octahedral plateau boundaries were subsequently improved. Historical text remains valuable for reconstructing the search, but the current coordinates and scale fields are the evidence for this analysis. Search provenance in a winning record describes the final accepted candidate, not necessarily the complete ancestry or all attempted constructions at that count.

An independent implementation cross-check compared 3,511 selected pair distances with the repository geometry kernel: the maximum absolute difference was approximately 2.0e-15 piece edges, with no contact classification differences at any of the three thresholds. The generated symmetry groups also passed a closure check to approximately 5.72e-16, and a representative-invariance check changed disorientation angles by at most approximately 2.21e-13 degrees. `research/geometry-crosscheck.json` records the tests. This sampled agreement supports the implementation, while the structural measurements retain their double-precision status.

### 3.2 Orientation modulo the solid's own symmetry

Quaternions are a representation of orientation, not a direct measure of geometrically different poses. The quaternions $q$ and $-q$ represent the same rotation. In addition, a solid can be unchanged by a nontrivial proper rotation. The proper symmetry group $G_B$ has order 12 for a tetrahedron, 24 for a cube or octahedron, and 60 for a dodecahedron or icosahedron.

We construct each group by mapping an ordered pair of non-collinear canonical vertices to every ordered pair with the same inner product. The resulting proper rotations are retained only when they map the entire vertex set to itself. Orthogonality, positive determinant, and the expected group cardinality are checked. This produces groups in the repository's coordinate convention, avoiding an accidental mismatch with a library's canonical orientation.

For orientations $R_i,R_j$, define the disorientation angle

\[
\theta_{ij}=\min_{g\in G_B}\cos^{-1}\left[\frac{\operatorname{tr}(R_i^TR_jg)-1}{2}\right].
\]

The argument is numerically clipped to $[-1,1]$. Minimizing over the symmetry representatives of both pieces reduces to this single-group minimum by cyclic invariance of trace and closure of $G_B$. This angle is invariant under a common rotation of the entire arrangement and under choosing another symmetry-equivalent representative for either piece. Using raw quaternion distance would incorrectly count several visually identical solid orientations as different.

We compute orientation graphs at 0.1°, 1°, and 5°. An edge joins any two pieces whose disorientation is at most the threshold, without a spatial-neighbor requirement. The connected components provide orientation-domain sizes, the largest-domain fraction, and normalized Shannon entropy

\[
H=-\frac{\sum_k p_k\log p_k}{\log n},\qquad p_k=|C_k|/n.
\]

Here $H=0$ for one orientation component and $H=1$ when every piece has a distinct component. Components use single linkage, so their full angular diameter may exceed the threshold through a chain. The maximum component diameter is therefore explicitly retained; the connected-component rule is not silently interpreted as pairwise uniformity. All component memberships are supplied for alternative clustering.

### 3.3 Contacts from actual Euclidean distance

Center proximity alone does not identify a contact, especially for anisotropic polyhedra. The separating-axis theorem gives a reliable overlap test, but the largest projection gap across the finite SAT axis set is generally only a lower bound on the Euclidean distance of two disjoint bodies. Treating that gap as the actual contact distance would introduce false edges.

We first reject pairs whose center distance exceeds twice the piece circumradius plus the largest threshold. A SAT lower bound provides a second rejection. Surviving pairs are measured with Euclidean feature enumeration: vertex projections onto face interiors and distances between every pair of edge segments. For disjoint convex polytopes a closest pair is attained on these features; endpoint-to-segment cases cover parallel and boundary degeneracies. The segment computation evaluates the interior stationary point when both parameters lie in the segments and all four endpoint projections. The minimum candidate distance is the distance used for the contact graph.

Near-contact graphs use thresholds $10^{-5},10^{-4},10^{-3}$ in piece-edge units. The central threshold $10^{-4}$ is substantially larger than the archive's nominal $10^{-7}$ clearance and is small relative to an edge. These are tolerance-defined near contacts in the slightly expanded certified construction, rather than exact contacts in an algebraic touching limit. For each graph we report edge count, mean degree $2|E|/n$, connected components, and isolated pieces. Wall proximity is measured separately as the minimum vertex-to-container-face-plane gap of each piece.

An interior piece with few or no near contacts can be a candidate rattler, but a static contact count does not prove a continuous feasible motion. Conversely, high contact degree does not prove collective rigidity: constraints can be redundant and contact geometry matters. A rigidity conclusion would require a motion or constraint-rank analysis that is outside the current calculations.

### 3.4 An operational grain proxy

For the central contact graph, keep only edges for which $\theta_{ij}\le1°$. Connected components of the resulting graph are called *operational grains* in this paper. This definition requires both spatial near contact and orientational similarity. Two distant pieces can share an orientation domain without belonging to the same grain, while two contacting pieces with different orientations belong to different grains.

The definition captures one geometrical feature suggested by a grain analogy, but a material grain usually requires positional crystalline order as well as a coherent orientation of that order. Piece orientation, lattice orientation, and thermodynamic phase are distinct. The records do not contain a temperature, interparticle interaction model, diffusion dynamics, lattice-order parameter, or grain-boundary energy. An operational grain is therefore a reproducible descriptor of a finite packing, not evidence that the packing represents an equilibrium crystal or reproduces a crystal-growth mechanism. The 0.1° and 5° alternatives expose sensitivity to the orientational criterion.

## 4. Quantitative results across the nine shape pairs

| Piece in container | U(2) | U(40) | Median density | Density at 40 | Highest density (n) | Median normalized scale |
|---|---|---|---|---|---|---|
| tetintet | 1.953565 | 4.055059 | 0.5670 | 0.5999 | 0.6250 (5) | 1.2082 |
| octinoct | 1.933120 | 3.955548 | 0.6316 | 0.6463 | 0.7500 (6) | 1.1655 |
| icoinico | 1.963086 | 4.107511 | 0.5318 | 0.5772 | 0.6687 (12) | 1.2343 |
| dodindod | 1.987598 | 4.176266 | 0.5360 | 0.5492 | 0.6272 (33) | 1.2311 |
| cubincub | 2.000000 | 4.000001 | 0.6094 | 0.6250 | 1.0000 (27) | 1.1795 |
| cubinoct | 2.414214 | 5.191942 | 0.5145 | 0.6063 | 0.6063 (40) | 1.2480 |
| octincub | 1.414214 | 3.245184 | 0.5558 | 0.5517 | 0.6919 (27) | 1.2163 |
| dodinico | 2.894427 | 6.324721 | 0.5157 | 0.5553 | 0.6797 (13) | 1.2470 |
| icoindod | 1.236068 | 2.741842 | 0.5205 | 0.5525 | 0.5760 (33) | 1.2432 |

Family identifiers name the piece first: `cubinoct` is cubes in an octahedron and `icoindod` is icosahedra in a dodecahedron. Each row contains 39 constructions, at every count from 2 to 40.

Figure 1 plots all certified edge scales with the elementary volume bounds. The largest raw scales occur in mixed pairs whose unit-edge pieces have larger volume than the unit-edge container. That observation is primarily dimensional. Occupied volume fraction and normalized scale are needed to evaluate how much confinement inefficiency remains after accounting for this volume difference.

Across the 351 records, there are 7,371 placed pieces and 95,940 distinct within-record piece pairs. All nine full-precision certified-scale curves are already non-decreasing. Consequently the deletion envelope changes none of their values. This independently confirms the final archive's monotonicity rather than assuming it from a rounded table.

Among same-solid families, octahedra have the highest median occupied volume fraction, 0.6316, followed by cubes at 0.6094, tetrahedra at 0.5670, dodecahedra at 0.5360, and icosahedra at 0.5318. These medians describe the sampled counts equally weighted. They are not asymptotic packing densities. The best single sampled cubic density is approximately 0.9999996 at n=27, reflecting the exact 3-by-3-by-3 tiling plus the record's positive-clearance enlargement. At n=40, the same-solid densities range from 0.5492 for dodecahedra to 0.6463 for octahedra.

For mixed pairs, the raw edge scales at n=40 range from 2.7418 for icosahedra in a dodecahedron to 6.3247 for dodecahedra in an icosahedron. Their densities, however, are much closer: 0.5525 and 0.5553. This is a concrete example of why edge ratios alone cannot rank different piece/container choices. Cubes in an octahedron reach density 0.6063 at n=40, whereas octahedra in a cube reach 0.5517. Reversal of a dual pair is therefore not a symmetry of the finite-fit objective under unit-edge normalization.

The source records carry 105 closed-form labels. They span 26 octahedral same-solid records, 25 cubic same-solid records, 17 dodecahedral same-solid records, and smaller numbers in the other families. These labels identify candidate algebraic scales near the numerical touching output; their frequency is not a count of independently proved optimum formulas.

The nine curves should not be averaged into a single universal law. Differences in rotational symmetry, inradius-to-circumradius ratio, face structure, and boundary compatibility act together. For same-solid problems the volume lower bound is always $n^{1/3}$, so the differences in normalized scale are particularly direct. For mixed pairs, changes in scale also reflect the piece/container volume ratio.

## 5. Plateaus, expansion steps, and finite-count organization

| Family | Identical certified U ranges | Numerical T ranges, tolerance 1e-8 |
|---|---|---|
| tetintet | 3–4 | 3–5 |
| octinoct | 3–6; 7–10; 17–19; 22–23; 27–29 | 3–6; 7–10; 11–12; 17–19; 22–23; 27–29 |
| icoinico | 11–12 | 11–12 |
| dodindod | 3–4; 11–12; 29–33 | 3–4; 5–6; 11–12; 29–33 |
| cubincub | 2–8; 9–10; 15–27 | 2–8; 9–10; 15–27; 28–32; 34–35; 39–40 |
| cubinoct | 3–4; 11–12 | 3–4; 11–12; 24–25 |
| octincub | 26–27 | 7–8; 26–27 |
| dodinico | 10–12 | 10–13 |
| icoindod | none | none |

The tetrahedral n=3–5 range illustrates the evidence distinction: the three touching estimates are exactly 2 in the recorded numerical output, but only n=3 and n=4 have identical certified U=2.0000006123725. The n=5 certified construction has U=2.000000734847. An explicit subdivision separately proves the touching construction exists at edge 2; the two certificate sizes differ because their clearances are imposed on different arrangements.

The dodecahedral n=29–33 range is stronger as a reported-scale plateau: all five records share exactly U=3.7470909531576. The occupied fraction rises from 0.551208 at n=29 to 0.627236 at n=33, a 13.7931% relative increase in density with no change in the certified container scale. The tentative expression (55+24 sqrt(5))/29 for its touching estimate remains unproved. Equal certified scales and a numerical algebraic guess are different claims.

For cubes, n=15–27 has exactly U=3.0000004000001 throughout, while n=28–32 is a numerical touching plateau with values near 3+1/sqrt(2), spanning approximately 1.275e-9. Its certified full scales differ, so it is not placed in the exact reported-scale column. In the mixed golden-ratio pair, dodecahedra in an icosahedron have equal numerical touching output at n=10–13, but identical U only at n=10–12. Icosahedra in a dodecahedron have no plateau meeting either criterion within the sampled counts.

| Family | Addition | Absolute edge increase | Relative edge increase | Container-volume increase | Density change |
|---|---|---|---|---|---|
| tetintet | 5 to 6 | 0.290995 | 14.550% | 50.308% | -0.1260 |
| octinoct | 6 to 7 | 0.500000 | 25.000% | 95.312% | -0.3020 |
| icoinico | 13 to 14 | 0.208785 | 7.433% | 23.996% | -0.0771 |
| dodindod | 4 to 5 | 0.236068 | 11.803% | 39.754% | -0.0528 |
| cubincub | 8 to 9 | 0.707107 | 35.355% | 147.985% | -0.5463 |
| cubinoct | 6 to 7 | 0.356671 | 12.155% | 41.077% | -0.0872 |
| octincub | 2 to 3 | 0.218780 | 15.470% | 53.960% | -0.0086 |
| dodinico | 13 to 14 | 0.531701 | 13.079% | 44.593% | -0.1735 |
| icoindod | 2 to 3 | 0.136966 | 11.081% | 37.062% | +0.0285 |

The largest relative edge step in the entire archive is the transition from eight to nine cubes: 35.3553%, corresponding to approximately 148.0% more container volume and a density loss of 0.5463. The second conspicuous cubic transition, from 27 to 28 pieces, increases the edge by 23.5702%, the volume by 88.6868%, and decreases density by 0.4504. These transitions occur immediately after complete integer cube grids, making grid capacity a concrete upper-bound construction mechanism; their exact global-optimality implications require separate lower bounds.

Octahedra in an octahedron change from six pieces at U=2.0000003674235 to seven at U=2.5000004286608, a 25.0% edge increase and 95.3125% volume increase. The density falls from approximately 0.7500 to 0.4480. At the same time the central contact graph changes from 15 edges, with mean degree 5, to only 5 edges, with mean degree about 1.429. One orientation component and one operational grain at n=6 become five orientation components and seven singleton grains at n=7. This is quantitative evidence that the archived winner changes organization at the capacity step, though it does not prove no denser seven-piece organization exists.

Dodecahedra in an icosahedron show a particularly clear mixed-pair change from n=13 to n=14: 13.0792% additional edge and 44.5932% additional volume. Density drops from 0.6797 to 0.5062, central contact edges from 42 to 24, and mean degree from approximately 6.462 to 3.429. Seven orientation components at n=13 become fourteen at n=14. Both arrangements nevertheless have only singleton operational grains at the 1-degree contact-and-angle criterion. A scale transition can therefore accompany a change in repeated orientations without producing contact-connected aligned domains.

A plateau offers a concrete way to distinguish count utilization from bounding scale. The larger-count construction can be pruned to smaller counts at the same scale, so unused capacity can be filled without enlarging the enclosing solid. This does not imply that every added piece occupies a pre-existing empty slot in the independently optimized smaller configuration. The archive may instead switch between different arrangements that happen to have a similar bounding size. Tracking that distinction requires comparing the full pose sets after optimal global alignment and piece matching; scale equality alone cannot do so.

A sharp expansion step is equally ambiguous mechanistically. It may indicate that a particular geometric family has reached capacity, or it may reveal that the search has not found a better family at the next count. The upper-bound curve is an empirical frontier of feasible examples. No lower bound in the present dataset forces its large jumps. The safest interpretation is that these counts expose useful *candidate* transitions in the archive, which can guide new searches or proof attempts.

For this reason, the strongest comparisons combine a jump with structural evidence: orientation-domain changes, changes in wall-supported pieces, contact-graph changes, and density loss. A discontinuity in only a rounded table is weak evidence. A large relative expansion, stable contact structure under tolerance changes, and an explicit construction mechanism would be much stronger. The accompanying tables make all of these checks possible without treating them as equivalent.

The useful practical question about an additional piece is often a volume question. A 10% edge expansion requires roughly 33.1% additional container volume. Conversely, a visually modest linear improvement of 1% produces approximately a 3% reduction in container volume. Edge ratios should therefore be accompanied by their cubic consequences when discussing capacity, material efficiency, or confinement.

## 6. Orientation distributions and contact-connected domains

| Family | Median orientation components | One orientation component | All pairwise angles <=1 degree | Every orientation distinct | Median operational grains | Median contact degree |
|---|---|---|---|---|---|---|
| tetintet | 15 | 2 | 2 | 1 | 21 | 3.905 |
| octinoct | 2 | 18 | 18 | 0 | 2 | 4.242 |
| icoinico | 7 | 10 | 10 | 3 | 10 | 3.739 |
| dodindod | 7 | 11 | 10 | 0 | 9 | 3.760 |
| cubincub | 1 | 22 | 22 | 0 | 1 | 4.000 |
| cubinoct | 19 | 5 | 5 | 3 | 20 | 3.714 |
| octincub | 13 | 8 | 8 | 6 | 13 | 4.000 |
| dodinico | 20 | 2 | 2 | 26 | 21 | 4.364 |
| icoindod | 21 | 1 | 1 | 24 | 21 | 3.926 |

Component and pairwise columns use the 1-degree disorientation threshold, and record counts are out of 39. Contact degree uses Euclidean distance <=1e-4 piece edges. A one-component count is a single-linkage result; the next column explicitly checks that every pair in the record lies within 1 degree. The difference for dodecahedra in a dodecahedron is a measured chain effect rather than a labeling ambiguity.

Cubes in a cube have 22 records whose pieces are all pairwise within 1 degree modulo cube symmetry. Octahedra in an octahedron have 18. In contrast, dodecahedra in an icosahedron have 26 records in which every piece is more than 1 degree from every other piece modulo dodecahedral symmetry; the reversed pair has 24 such records. All-distinct orientations thus occur frequently in both directions of this dual pair, while they are absent from the cube-in-cube and octahedron-in-octahedron records.

The distinction between orientation domains and operational grains is substantive. At n=33, the dodecahedron-in-dodecahedron record has seven orientation components, with a largest component of 21 pieces, but no contact-connected aligned pair at the central thresholds: all 33 operational grains are singletons. The contact graph itself has 102 edges. Repeated orientation, many contacts, and spatially connected alignment are therefore three different observations. The n=29 member of the same certified-scale plateau likewise has seven orientation components and 29 singleton grains.

At n=12, the icosahedron-in-icosahedron record is pairwise aligned modulo its 60-element symmetry group and has a connected 30-edge contact graph, mean degree 5. It is one operational grain with density approximately 0.6687. At n=15, icosahedra in a dodecahedron have two orientation components of sizes 14 and 1 and two operational grains with the same sizes; U=2.0000001715822 and the numerical touching estimate is 2. The smaller component should not be inferred to be a physical defect without an appropriate physical model.

For n=27 cubes in a cube, the central graph has 158 edges and mean degree approximately 11.704. Near contacts include face, edge, and vertex proximity. This explains why the degree exceeds the six face-neighbor count of a cubic grid: the graph records all Euclidean near contacts, not only face-sharing interfaces. A material or force-bearing contact graph would require a contact-area or mechanical criterion.

Threshold sensitivity is material. Only 217 of 351 records have identical contact edge sets at all three distance tolerances; because the graphs are nested, equality of edge counts guarantees equality of sets. Only 131 records have unchanged orientation-component counts at 0.1, 1, and 5 degrees; nested graphs again make unchanged counts a sufficient condition for unchanged component partitions. At the central thresholds, 117 records contain only singleton operational grains. These numbers preclude treating any one color partition as a threshold-free physical object. The complete memberships and edges permit sensitivity checks case by case.

It is tempting to divide all constructions into “same orientation” and “different orientations,” but the dataset supports a spectrum. A large orientation component can coexist with many individually tilted boundary pieces. Several repeated orientations can form interlocking domains. At the other extreme, a packing can have nearly one orientation component per piece while maintaining a well-connected contact network. These possibilities are geometrically different and are recorded by separate domain and grain statistics.

Orientation entropy is not an entropy of thermodynamic microstates. It measures only the distribution of component memberships under the chosen threshold. Nor does a uniform orientation imply a lattice. Translational regularity would have to be measured, for example by fitting lattice generators to center differences and checking residuals, or by a suitable positional order parameter. The current analysis therefore uses “aligned” for orientation organization and reserves “lattice” for an explicit construction with a translational rule.

Pairwise disorientation distributions are retained in `pair-metrics.csv`, together with center distances and the calculated near-pair Euclidean distances. This enables distributions conditioned on actual contacts, wall location, or component membership. An unconditioned pair distribution weighs distant pairs heavily at large $n$, while a contact-conditioned distribution probes local alignment. Their answers need not coincide. The domain and grain statistics intentionally keep those notions separate.

## 7. Construction mechanisms and candidate families

### 7.1 Integer subdivision and lattice scaffolds

Three constructions have explicit scales that are independent of numerical root recognition. An edge-$k$ cube admits the regular $k\times k\times k$ grid of unit cubes. Deleting pieces provides every count up to $k^3$ at the same scale. This explains the existence of broad cubic upper-bound plateaus, although it does not prove that a grid is optimal at every count on such a plateau. At the complete-grid counts $n=k^3$, the elementary volume lower bound is exactly $k$ and matches the symbolic tiling construction, proving $s^*_{\mathrm{cube},\mathrm{cube}}(k^3)=k$. In the sampled range this applies to n=8 and n=27. That elementary equality is independent of the small positive clearances of the stored records and of their numerical structural descriptors.

A tetrahedral edge subdivision produces $\binom{k+2}{3}$ upright unit tetrahedra, $\binom{k}{3}$ inverted unit tetrahedra, and $\binom{k+1}{3}$ unit octahedral holes. A unit regular tetrahedron fits into a unit regular octahedron: use one triangular face as the base and the centroid of the opposite face as the apex. The base edge is one and the opposite-face distance equals the tetrahedral height, so the tetrahedron is regular; convexity ensures containment. Inserting one tetrahedron into every octahedral hole gives

\[
N_{\mathrm{tet}}(k)=\binom{k+2}{3}+\binom{k+1}{3}+\binom{k}{3},
\]

which yields 5, 15, and 34 pieces at edges 2, 3, and 4. This is a construction, not a claim that all holes are filled to their full volume. The identity $k^3=\binom{k+2}{3}+4\binom{k+1}{3}+\binom{k}{3}$ checks the tetrahedral/octahedral subdivision volumes.

For an octahedron written as $|x|+|y|+|z|\le a$, $a=1/\sqrt2$, choose centers $a m$ with integer $m$, $|m|_1\le k-1$, and $|m|_1\equiv k-1\pmod2$. These aligned octahedra lie inside the edge-$k$ octahedron; the parity rule separates their interiors. The count $N_{\mathrm{oct}}(k)=(2k^3+k)/3$ gives 6, 19, and 44 at edges 2, 3, and 4. A repeated orientation is expected from the construction rule, but numerical winners near these counts can abandon that rule and improve the scale.

These scaffolds give reference capacities that are useful for interpreting the search. A certified improvement below an integer edge establishes that the corresponding explicit scaffold was not the best available construction at that count. It does not establish the global optimum of the improved arrangement.

### 7.2 Boundary accommodation and polyhedral duality

Tetrahedron, cube, octahedron, dodecahedron, and icosahedron differ in face type, number of faces, and available proper symmetries. The cube and octahedron form a dual pair, as do the dodecahedron and icosahedron. A piece with vertices directed toward a container's face regions and a piece whose faces align with those walls can accommodate confinement differently. This motivates the mixed pairs in the archive, but duality alone supplies no universal packing-size formula.

The dodecahedron and icosahedron use canonical coordinates containing the golden ratio. Low-complexity expressions involving $\sqrt5$ therefore have a natural geometric motivation in explicit constructions. Nevertheless, a high-coefficient quadratic expression recognized from a twelve-digit touching estimate can be accidental. The coefficient size, uniqueness among nearby candidate expressions, and exact solvability of the corresponding contact constraints should be considered before presenting it as a geometric law.

The boundary-accommodation interpretation is testable. One can compare the number of wall-supported pieces, orientation components, and contact constraints across adjacent counts, and then inspect whether repeated patterns are attached to particular faces, edges, or vertex regions. These measurements establish where a proposed mechanism acts; a visual resemblance alone does not establish that two constructions share the same mechanism.

### 7.3 Hybrids and dispersed arrangements

We propose a descriptive hierarchy of candidates: explicit lattice scaffolds; aligned arrangements without a demonstrated lattice; several repeated orientational domains; and dispersed arrangements with many distinct piece orientations. Boundary-adapted pieces can appear within any of these categories, so the categories do not form a disjoint mathematical classification. Contact-connected grains further distinguish a spatially coherent domain from separated pieces that happen to have the same orientation.

For future work, family membership should be supported by invariants or fitted rules: a center lattice with small residuals, an identifiable layered construction, a stable contact graph under small geometric perturbations, or a parameterized algebraic placement. The present dataset is large enough to motivate such a classification, but only contains one final winner per count. It does not contain the full distribution of competing families or the frequency with which they were reached. A single winner cannot establish that a family dominates the search landscape.

## 8. Correlations, optimality priorities, and limits of inference

Within-family correlations do not support a universal rule that more alignment or a larger operational grain yields higher density. For density versus largest orientation-component fraction, Spearman rho ranges from approximately -0.720 for icosahedra in a dodecahedron to +0.563 for cubes in a cube. Density versus largest operational-grain fraction ranges from approximately -0.768 for the former pair to +0.539 for the latter. Octahedra in an octahedron have a positive orientation association of about +0.307, while dodecahedra in a dodecahedron have about -0.542. Shape-pair dependence is clear in the selected archive.

Density and central contact mean degree have positive within-family rank correlations in all nine families, ranging from about +0.364 for octahedra in a cube to +0.892 for dodecahedra in an icosahedron. This is consistent with denser selected arrangements tending to exhibit more near contacts, but may also reflect piece-count effects and the changing proportion of boundary pieces. Relative edge increments correlate especially strongly with orientation entropy for cubes in a cube (rho about +0.832), while the corresponding tetrahedral coefficient is slightly negative (about -0.102). The complete coefficient table is included for reproducibility rather than for post-hoc selection of a universal mechanism.

The supplied within-family Spearman coefficients are descriptive rank comparisons. They use one selected final construction per count, so neighboring observations are dependent through deletion and insertion moves, and the piece count itself can influence both density and structural descriptors. No $p$-values, significance stars, causal interpretation, or general law about grains improving density is attached to these coefficients. Repeated independent searches at fixed counts, with a retained ensemble of feasible arrangements, would provide a more suitable test of such a hypothesis.

The volume lower bound remains loose for many cases. A numerically stable arrangement and a small rate of further improvement establish neither local rigidity nor global optimality. A long plateau can be a convenient target for a proof because one larger-count witness simultaneously provides several upper bounds; however, a proof for the beginning of the plateau still requires a matching lower bound at that count. Without it, the true optimum could be lower for some or all of the displayed counts.

We suggest selecting proof targets using explicit evidence rather than a claimed probability of optimality. Useful features include a low-complexity symbolic construction, an independently reproduced scale, a small gap to a valid problem-specific lower bound, a contact system whose exact geometry is tractable, and a finite case decomposition suitable for interval branch-and-bound. Small counts often reduce the dimensional burden, whereas lattice plateaus provide strong upper-bound witnesses. Neither feature replaces the lower-bound argument.

For numerical follow-up, large jumps with low density are natural targets for new basin searches, alternative scaffold seeds, and insertion moves. Candidate algebraic plateaus are natural targets for exact contact reconstruction. Orientation-dispersed winners are natural targets for testing whether constraints force the diversity or whether an aligned competitor exists. These are priorities for investigation, not rankings of demonstrated closeness to the unknown global optimum.

## 9. Relevance to grains and crystalline organization

Finite hard-particle packings provide a controlled geometric setting for investigating excluded volume, orientational compatibility, and boundary frustration. These ingredients also arise in models of anisotropic colloids and crystalline organization. The present archive is useful because each static arrangement is explicitly reconstructible and feasibility can be verified, allowing structural measurements to be repeated or replaced.

For comparison, [Khadilkar and Escobedo (2016)](https://doi.org/10.1039/C5SM02570B) studied hard polyhedral nanoparticles between parallel plates with a specified physical model, including ordered, buckled, plastic, and disordered structures near layer changes. That evidence supports the relevance of confinement to physical organization, while also specifying variables and a statistical model that the finite-fit archive does not include. The present discrete size jumps should not be labeled thermodynamic phase transitions without such additional evidence.

The connection to crystal formation is nevertheless a research motivation, not a result of these experiments. A physical prediction would require an interaction model, thermodynamic conditions, a sampling or dynamical process, and appropriate order parameters. A finite optimal or locally optimized packing need not be selected by kinetic growth; a physical grain boundary need not coincide with a connected component of similarly oriented particle shapes. In particular, an arrangement can exhibit positional crystalline order while individual particle orientations vary, or repeated particle orientations without any translational lattice.

A concrete bridge would use archived arrangements as candidate seeds or reference configurations in a specified hard-polyhedron simulation. One could compare equilibrium or growth-generated configurations with the finite-fit descriptors, measure positional and orientational order separately, and test whether confinement produces similar domain patterns. The difference between geometry and dynamics would then be measured rather than assumed. The operational grains defined here would remain one explicit observable among others.

## 10. Data availability and reproducibility

The original pose files, feasibility checkers, search programs, historical logs, and interactive viewer are available in the [repository](https://github.com/alejandrozu/platonic-packing). The viewer supports rotation, slicing, selection, and orientation coloring; it is a valuable aid to geometric inspection. Its visual orientation-color rule uses a vertex-set tolerance and need not coincide exactly with the symmetry-angle components defined here. Numerical values and component memberships in this paper are determined by the accompanying analysis script.

The supplementary directory contains `analyze_records.py`, `record-metrics.csv`, `family-summary.csv`, `pair-metrics.csv`, `plateaus.csv`, `largest-jumps.csv`, `descriptive-correlations.csv`, `geometry-details.json`, `source-manifest.csv`, and `analysis-metadata.json`. Run the script with `--repo` pointing to the frozen checkout and `--out` pointing to a new directory. NumPy is required; Matplotlib adds the figures. The geometric calculations use double precision, while exact feasibility is reproduced separately with the repository's standard-library checker.

A fresh independent rerun of the repository's exact arithmetic checker and floating-point checker passed all 351 frozen records, with zero failures; pose-count and schema checks also passed for every record. The detailed machine-readable result is `research/verification.json`, accompanied by per-record verification output. This rerun establishes feasibility of the archived constructions at `s_full`; it does not certify the floating-point structural descriptors or prove optimality. Later GitHub updates or later social-media claims require a new freeze and a new comparison; they are not silently merged into these curves. Archiving a tagged version or DOI-linked software/data release would improve long-term citation before a journal submission.

## Figure captions

![Figure 1: Scale curves and volume bounds for all nine families.](analysis/figure-1-scale-curves.png)

![Figure 2: Relative edge increments by count for all nine families.](analysis/figure-2-increments.png)

![Figure 3: Density, orientation domains, operational grains, and contact structure.](analysis/figure-3-structure.png)

**Figure 1.** Certified container-edge upper bounds for all nine shape pairs, $n=2,\ldots,40$. Dashed curves are the elementary volume lower bounds. A visible gap does not measure the error of the search: the true optimum is only constrained to lie between the two curves. Mixed-pair raw scales reflect different unit-edge volumes.

**Figure 2.** Relative edge increments when the piece count increases from $n-1$ to $n$, for $n=3,\ldots,40$. Near-zero bars identify numerical or exact reported-scale plateaus; large bars identify archive expansion steps. The increments use `s_full`; exact equality, numerical touching equality, and certified-envelope equality are tabulated separately.

**Figure 3.** Structural curves for all nine families: occupied volume fraction, largest orientation-component fraction at 1°, largest contact-connected operational-grain fraction at 1°, and mean near-contact degree at Euclidean distance $\le10^{-4}$ piece edges. Orientation and contact quantities are floating-point descriptors of the certified pose files. They do not establish crystallinity, rigidity, or optimality.

## References and source notes

The companion methods paper and repository source are primary descriptions of the project. External scholarly references are listed below after verification; source notes on the status of current numerical records are maintained separately to avoid conflating preprints, catalogues, social-media announcements, and proven optima.

1. E. G. Teich, G. van Anders, D. Klotsa, J. Dshemuchadse, and S. C. Glotzer, “Clusters of polyhedra in spherical confinement,” *PNAS* 113, E669–E678 (2016), [doi:10.1073/pnas.1524875113](https://doi.org/10.1073/pnas.1524875113). Direct finite-count precedent; the container is spherical, rather than polyhedral.
2. M. R. Khadilkar and F. A. Escobedo, “Phase behavior of polyhedral nanoparticles in parallel plate confinement,” *Soft Matter* 12, 1506–1516 (2016), [doi:10.1039/C5SM02570B](https://doi.org/10.1039/C5SM02570B). Physical context for layer transitions and frustration under confinement.
3. J. Egeblad, B. K. Nielsen, and M. Brazil, “Translational packing of arbitrary polytopes,” *Computational Geometry* 42, 269–288 (2009), [doi:10.1016/j.comgeo.2008.06.003](https://doi.org/10.1016/j.comgeo.2008.06.003). General polytope-container methodology restricted to translations.
4. T. Romanova, J. Bennell, Y. Stoyan, and A. Pankratov, “Packing of concave polyhedra with continuous rotations using nonlinear optimisation,” *European Journal of Operational Research* 268, 37–53 (2018), [doi:10.1016/j.ejor.2018.01.025](https://doi.org/10.1016/j.ejor.2018.01.025). Related freely rotating finite packing methodology with a cuboid-volume objective.
5. H. F. Callisaya and E. R. V. Kari, “Packing Polyhedra within Convex Sets,” *Trends in Computational and Applied Mathematics* 26, e01823 (2025; collection publication 2026), [doi:10.5540/tcam.2025.026.e01823](https://doi.org/10.5540/tcam.2025.026.e01823). A general separating-hyperplane formulation; its three-dimensional example uses a spherical container.
6. S. Torquato and Y. Jiao, “Dense packings of polyhedra: Platonic and Archimedean solids,” *Physical Review E* 80, 041104 (2009), [doi:10.1103/PhysRevE.80.041104](https://doi.org/10.1103/PhysRevE.80.041104). Periodic packing background; its organizing conjectures are not finite-container theorems.
7. E. R. Chen, M. Engel, and S. C. Glotzer, “Dense crystalline dimer packings of regular tetrahedra,” *Discrete & Computational Geometry* 44, 253 (2010), [doi:10.1007/s00454-010-9273-0](https://doi.org/10.1007/s00454-010-9273-0). A construction proved optimal within a stated parameterized family, illustrating the distinction from global optimality.
8. E. Friedman, [Packing Center](https://erich-friedman.github.io/packing/index.html), including [cubes in cubes](https://erich-friedman.github.io/packing/cubincub/), [tetrahedra in cubes](https://erich-friedman.github.io/packing/tetincub/), and [octahedra in cubes](https://erich-friedman.github.io/packing/octincub/), retrieved 11 October 2026. These are primary numerical record catalogues; rounded entries are not exact optimality proofs.
9. Y. Nakajima, [soft-to-rigid-packing](https://github.com/yoheinakajima/soft-to-rigid-packing), repository, retrieved 11 October 2026. Computational precursor of the present generalized search.
10. A. Zarzuelo, [platonic-packing](https://github.com/alejandrozu/platonic-packing), commit `e15b496ae7306287e0e70bb5b14be79f5dfdde84`, data and software, 11 October 2026.

Nearby work already investigates finite polyhedral clusters, general polytope packing, and confinement-induced organization. This manuscript's contribution is the certified polyhedral-container dataset and its explicitly reproducible structural analysis, not a claim to have introduced finite polyhedral packing.

## Appendix A. Complete numerical scale table

Values in this appendix are rounded for readability. The full-precision `s_full`, hexadecimal representations, touching estimates, densities, normalized scales, and envelope witnesses are in `record-metrics.csv`. Rounded equality in this table is not the criterion used to identify plateaus.

| n | tetintet | octinoct | icoinico | dodindod | cubincub | cubinoct | octincub | dodinico | icoindod |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 1.953565 | 1.933120 | 1.963086 | 1.987598 | 2.000000 | 2.414214 | 1.414214 | 2.894427 | 1.236068 |
| 3 | 2.000001 | 2.000000 | 2.000000 | 2.000000 | 2.000000 | 2.707107 | 1.632993 | 3.145624 | 1.373034 |
| 4 | 2.000001 | 2.000000 | 2.145898 | 2.000000 | 2.000000 | 2.707107 | 1.649916 | 3.375464 | 1.393447 |
| 5 | 2.000001 | 2.000000 | 2.236068 | 2.236068 | 2.000000 | 2.914214 | 1.757826 | 3.574901 | 1.533190 |
| 6 | 2.290995 | 2.000000 | 2.341641 | 2.236068 | 2.000000 | 2.934354 | 1.767767 | 3.637560 | 1.551316 |
| 7 | 2.381952 | 2.500000 | 2.449316 | 2.427051 | 2.000000 | 3.291025 | 1.791337 | 3.856416 | 1.668532 |
| 8 | 2.387427 | 2.500000 | 2.496617 | 2.527864 | 2.000000 | 3.414214 | 1.791337 | 3.966580 | 1.697790 |
| 9 | 2.615564 | 2.500000 | 2.582955 | 2.598882 | 2.707107 | 3.617605 | 1.885618 | 4.022064 | 1.771634 |
| 10 | 2.706304 | 2.500000 | 2.609893 | 2.705202 | 2.707107 | 3.691812 | 2.149366 | 4.065248 | 1.818215 |
| 11 | 2.799388 | 2.666667 | 2.618034 | 2.763932 | 2.881712 | 3.707107 | 2.230711 | 4.065248 | 1.867142 |
| 12 | 2.857605 | 2.666667 | 2.618034 | 2.763932 | 2.931515 | 3.707107 | 2.291026 | 4.065248 | 1.874620 |
| 13 | 2.915146 | 2.833334 | 2.809017 | 2.905573 | 2.976620 | 3.797374 | 2.339443 | 4.065248 | 1.904025 |
| 14 | 2.943005 | 2.943118 | 3.017802 | 3.000000 | 2.989950 | 3.915127 | 2.365476 | 4.596948 | 1.971077 |
| 15 | 2.988834 | 2.985332 | 3.048321 | 3.037436 | 3.000000 | 3.962663 | 2.429993 | 4.674811 | 2.000000 |
| 16 | 3.035381 | 2.994652 | 3.121305 | 3.102104 | 3.000000 | 4.000523 | 2.458658 | 4.792454 | 2.055106 |
| 17 | 3.089368 | 3.000000 | 3.196924 | 3.167740 | 3.000000 | 4.043966 | 2.506599 | 4.889163 | 2.090858 |
| 18 | 3.114666 | 3.000000 | 3.198213 | 3.215491 | 3.000000 | 4.048989 | 2.518754 | 4.971239 | 2.162159 |
| 19 | 3.187266 | 3.000000 | 3.311471 | 3.292183 | 3.000000 | 4.106581 | 2.552093 | 5.079367 | 2.203559 |
| 20 | 3.245809 | 3.166537 | 3.353710 | 3.349699 | 3.000000 | 4.322697 | 2.574181 | 5.157604 | 2.241766 |
| 21 | 3.298272 | 3.200001 | 3.407052 | 3.391486 | 3.000000 | 4.470616 | 2.589573 | 5.261428 | 2.283706 |
| 22 | 3.343401 | 3.250001 | 3.479548 | 3.444287 | 3.000000 | 4.593109 | 2.605693 | 5.322410 | 2.294592 |
| 23 | 3.382592 | 3.250001 | 3.552964 | 3.554883 | 3.000000 | 4.625766 | 2.622463 | 5.401953 | 2.348720 |
| 24 | 3.433884 | 3.363637 | 3.593990 | 3.578600 | 3.000000 | 4.707107 | 2.627923 | 5.474745 | 2.365414 |
| 25 | 3.489102 | 3.399830 | 3.609019 | 3.602376 | 3.000000 | 4.707107 | 2.636203 | 5.530873 | 2.392586 |
| 26 | 3.580913 | 3.428572 | 3.673286 | 3.637181 | 3.000000 | 4.745300 | 2.639866 | 5.615525 | 2.422444 |
| 27 | 3.616028 | 3.500001 | 3.700955 | 3.701302 | 3.000000 | 4.810537 | 2.639866 | 5.669858 | 2.444757 |
| 28 | 3.689632 | 3.500001 | 3.740700 | 3.733695 | 3.707107 | 4.844194 | 2.757318 | 5.739450 | 2.468239 |
| 29 | 3.711668 | 3.500001 | 3.773486 | 3.747091 | 3.707107 | 4.892432 | 2.828428 | 5.779179 | 2.475722 |
| 30 | 3.754128 | 3.600001 | 3.822556 | 3.747091 | 3.707107 | 4.919816 | 2.886590 | 5.848339 | 2.490704 |
| 31 | 3.823272 | 3.666667 | 3.856959 | 3.747091 | 3.707107 | 4.960974 | 2.934223 | 5.902533 | 2.509166 |
| 32 | 3.853842 | 3.692308 | 3.879286 | 3.747091 | 3.707107 | 4.998538 | 2.991467 | 5.949694 | 2.522169 |
| 33 | 3.892139 | 3.736843 | 3.896993 | 3.747091 | 3.766282 | 5.028439 | 3.034941 | 5.963712 | 2.536011 |
| 34 | 3.927574 | 3.788447 | 3.900160 | 3.911488 | 3.894428 | 5.052510 | 3.073740 | 5.988126 | 2.581152 |
| 35 | 3.952510 | 3.800001 | 3.936299 | 3.985653 | 3.894428 | 5.069745 | 3.089103 | 6.013972 | 2.627531 |
| 36 | 3.971367 | 3.854336 | 4.012314 | 4.021420 | 3.912282 | 5.089749 | 3.118592 | 6.140696 | 2.670962 |
| 37 | 3.998182 | 3.883761 | 4.047274 | 4.078725 | 3.926312 | 5.103246 | 3.153141 | 6.212957 | 2.686157 |
| 38 | 4.035552 | 3.916964 | 4.060300 | 4.120501 | 3.980774 | 5.136013 | 3.182379 | 6.269229 | 2.696559 |
| 39 | 4.046304 | 3.929591 | 4.069653 | 4.142217 | 4.000000 | 5.170028 | 3.232861 | 6.307366 | 2.728054 |
| 40 | 4.055059 | 3.955548 | 4.107511 | 4.176266 | 4.000001 | 5.191942 | 3.245184 | 6.324721 | 2.741842 |
