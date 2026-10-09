# Mathematical notes

This document explains what the records in this repository are, what is proven about them, what is only
conjectured, and how the constructions work. It is written to be read without running any code.

## 1. The problem

For Platonic solids A (the container) and B (the pieces) and an integer n ≥ 2, let

  s(A, B, n) = inf { s > 0 : n congruent copies of the unit-edge B, with pairwise disjoint interiors,
                              fit inside a copy of A with edge s }.

Pieces may be translated and rotated freely (reflections are never needed: every Platonic solid is achiral, i.e.
its mirror image is a rotated copy). The infimum is attained by compactness, so "smallest container" is
well defined. We write s_B(n) for the same-solid problem A = B. Erich Friedman's Packing Center tabulates
cubes in cubes (s_cube(n)), tetrahedra in cubes and octahedra in cubes; the same-solid problems for the
tetrahedron, octahedron, dodecahedron and icosahedron are, as far as we know, not tabulated anywhere.

Record ids follow Friedman's naming: `tetintet` (tetrahedra in a tetrahedron), `octinoct`, `icoinico`,
`dodindod`; mixed pairs are `<piece>in<container>`, e.g. `tetinico`.

### Elementary facts

* **Monotonicity.** s(A, B, n) ≤ s(A, B, n + 1): delete a piece. The search exploits this ("descend", §5).
* **Volume bound.** n·vol(B) ≤ s³·vol(A), so s(A, B, n) ≥ (n·vol B / vol A)^{1/3}; for A = B this is
  s_B(n) ≥ n^{1/3}. This is the only lower bound used in the tables, and it is far from the upper bounds.
* **Scaling.** If a container of edge s holds n pieces, so does every container of edge s' ≥ s (same centre,
  scaled up), so the feasible set of s is an interval [s(A, B, n), ∞).

**Nothing in this repository proves optimality.** Every number in `records/` is an *upper bound* backed by an
exact certificate (§4). For the cube, Friedman's catalogue lists s_cube(n) = 2 for 2 ≤ n ≤ 8, and the lower bound
for two cubes is classical; the analogous lower bounds for the other solids are open as far as we know, and our
results show they must differ: two copies of each non-cube solid fit in a container of edge **less than 2**
(§6).

## 2. The soft-to-rigid homotopy

Yohei Nakajima's method replaces each unit cube by a *rounded cube* and lowers the rounding radius from ½ (a ball)
to 0 (the cube) while inward pressure shrinks the container. The general form used here:

For a convex body P containing the ball B(0, ρ) (for a Platonic solid: the insphere, ρ = inradius), put

  S_r = (1 − r/ρ)·P ⊕ B(0, r),   0 ≤ r ≤ ρ.

**Lemma 1.** (a) S_ρ = B(0, ρ), S_0 = P. (b) S_r ⊆ P for all r. (c) r ≥ r' ⇒ S_r ⊆ S_{r'}.

*Proof.* (a) Immediate. (b) x ∈ S_r is x = (1 − t)p + r·b with p ∈ P, |b| ≤ 1, t = r/ρ, and r·b = t·(ρb) with
ρb ∈ B(0, ρ) ⊆ P, so x is a convex combination of two points of P. (c) For |u| = 1 the support function is
h_{S_r}(u) = (1 − r/ρ)h_P(u) + r = h_P(u) − (r/ρ)(h_P(u) − ρ), and h_P(u) ≥ ρ since B(0, ρ) ⊆ P. Hence
h_{S_r}(u) is non-increasing in r for every u, and convex bodies are ordered by their support functions. ∎

Consequences: (i) a packing of P's is a packing of S_r's for every r, so the optimal container for S_r is a lower
bound for the optimal container for P, increasing as r ↓ 0; (ii) the search path is monotone — as r decreases the
pieces only grow, so a jammed soft packing is "inflated" into a polytope packing rather than rearranged. For the
cube, (1 − 2r)·[−½, ½]³ ⊕ B(r) is exactly Nakajima's "cube of half-side ½ − r dilated by r".

**Lemma 2.** For convex bodies K, L and r ≥ 0, the signed distance satisfies
sd(K ⊕ B(r), L ⊕ B(r)) = sd(K, L) − 2r, where sd is the Euclidean distance when disjoint and minus the penetration
depth when overlapping. (The Minkowski difference of the rounded bodies is (K − L) ⊕ B(2r).)

So the pair energy (2r − sd_core)₊² used by the simulator is exactly the squared overlap depth of the soft
shapes, computed from their polytope cores (1 − r/ρ)P.

## 3. Geometry used by the search (and why it is exact)

**Penetration depth.** For convex polytopes K, L, the penetration depth (smallest translation that separates
them) equals the distance from 0 to the boundary of the Minkowski difference K − L, i.e. the minimum over facet
normals u of K − L of h_K(u) + h_L(−u). Every facet normal of K − L is a face normal of K, minus a face normal of L,
or a cross product of an edge direction of K with an edge direction of L. Minimizing h_K(u) + h_L(−u) over that
finite set (both signs) therefore gives the exact depth: extra directions never go below it. This is the
separating-axis theorem with *asymmetric* projection intervals, which the tetrahedron (not centrally symmetric)
requires.

**Distance between disjoint polytopes.** The closest pair lies on a vertex–face, face–vertex or edge–edge feature
pair (degenerate pairs — parallel edges, parallel faces, vertex–edge — are covered by the edge–edge segment
distance or by an extreme point of the set of closest pairs). *Slab pruning:* if a unit vector u separates K below
L with gap g and D is any upper bound on the distance, then every closest pair (x, y) satisfies
u·x ≥ max_K u·z − (D − g) and u·y ≤ min_L u·z + (D − g), because
u·x ≥ u·y − |x − y| ≥ min_L u·z − D = max_K u·z + g − D (and symmetrically for y). Only features meeting these slabs are enumerated, and edge
pairs are skipped when the distance of their midpoints minus half their lengths cannot beat the current best.
`test/test_geom.js` certifies every computed distance by the KKT condition (the planes through the closest points
orthogonal to x − y support K and L).

**Gradients.** For a world-frame rotation vector ω of piece A, a point p rigidly attached to A moves by
ω × (p − c_A). The penetration depth along the active axis u is o = u·(p_a − p_b) with support points p_a, p_b;
by the envelope theorem its gradient is u·dp_a − u·dp_b + (p_a − p_b)·du, where du = ω × u for face axes and
du = σ(I − uuᵀ)dw/|w| with dw = (ω_A × a) × b + a × (ω_B × b) for an edge–edge axis w = a × b. The separated
distance has gradient ±n w.r.t. the centres and (p − c) × n w.r.t. the rotations. All are checked against finite
differences.

## 4. The certificate (what "certified" means)

`certify_exact.py` takes a record file — n poses (centre c_i, quaternion q_i), the container edge s_full — and
proves, using only the Python standard library and exact arithmetic:

**Theorem (checked per record).** The n sets P_i = c_i + R_i·B, with R_i = H(q_i)/|q_i|² and B the canonical
unit-edge piece, are pairwise disjoint and each lies in the interior of s_full·A.

*Ingredients.*
1. Every float in the file is an exact dyadic rational. For any rational q ≠ 0, H(q)/|q|² (the homogeneous
   quaternion matrix) is an exactly orthogonal rational matrix with determinant 1, so P_i is exactly congruent to B
   whatever rounding happened when the file was written.
2. Canonical coordinates: cube (±½)³; tetrahedron (√2/4)(±1, ±1, ±1) with an even number of minus signs;
   octahedron ±(√2/2)e_i; icosahedron ½(0, ±1, ±φ) and cyclic permutations; dodecahedron (φ/2)(±1, ±1, ±1) and
   (0, ±½, ±φ²/2) with cyclic permutations; φ = (1 + √5)/2. All lie in Q(√2, √5). `solids.py` derives the faces
   (planes through vertex triples that leave all vertices on one side), and checks exactly: all edges have squared
   length 1; V, E, F are 4/6/4, 8/12/6, 6/12/8, 20/30/12, 12/30/20; every edge lies on exactly two listed faces (so
   the list is complete: a closed surface); all faces are equidistant from the origin. Inradius² = 1/24, 1/4, 1/6,
   5/8 + 11√5/40, 7/24 + √5/8.
3. Exact signs in Q(√2, √5): write x = p + q√5 with p, q ∈ Q(√2). If p and q have the same sign, so does x;
   otherwise sign(x) = sign(p) if p² > 5q² and sign(q) otherwise (p² ≠ 5q² because √5 ∉ Q(√2)). Signs in Q(√2)
   are decided the same way with 2 in place of 5.
4. Containment: each vertex v of each P_i satisfies m_f·v < s_full·β_f for every face f of A, where
   {y : m_f·y ≤ β_f} are the exact face half-spaces of the unit-edge A. By convexity P_i ⊆ int(s_full·A).
5. Disjointness: for each pair (i, j) a rational vector u (proposed by a floating-point separating-axis search,
   then rationalized) and the rational midpoint t of the two projection extremes are exhibited, and every vertex is
   checked: u·v < t for v ∈ P_i, u·v > t for v ∈ P_j. Floating point only proposes u; a bad proposal can only make
   the check fail.

Record files carry a clearance of 10⁻⁷ (minimum pair gap and wall gap), so `s_full` is slightly above the touching
limit `s_tight` reported by the tightening; the certificate is about `s_full`. For tetrahedral containers a wall
gap g costs about g/ρ ≈ 4.9g in edge length (ρ = 1/(2√6) ≈ 0.204), which is why Nakajima's 10⁻⁶ convention
was reduced to 10⁻⁷ here.

The checker is validated on external data: it certifies Nakajima's 12 cubes in a cube of side 2.9315185094797 and
the Hyra-results record of 21 unit octahedra in a cube of side 2.592849935818519, and it rejects deliberately broken
files (shrunk container, a piece pushed through its neighbour, coincident pieces, a piece outside).

## 5. How the upper bounds were found

1. **Soft-to-rigid search** (`src/sim.js`): random start, 5,000 steps compressing inscribed balls under pressure,
   45,000 steps lowering r linearly from ρ to 0, 3,000 rigid steps; heavy-ball descent with velocity cap and annealed
   noise (Nakajima's constants; pieces are scaled so the insphere has diameter 1, which makes those constants
   transfer to every solid). Then *legalization*: centres are scaled apart about their mean until the SAT test
   reports no overlap, and the smallest container over all translations is found by a 4-variable LP.
2. **Exact tightening** (`src/exact.py`): minimize the container size subject to (a) every vertex inside every
   container face and (b) for every nearby pair, a separating plane with all vertices of one piece on each side.
   Variables: centres, rotation increments (Rodrigues), container size, plane normals (tangent-plane coordinates)
   and offsets. Two solvers: SLSQP to convergence inside a trust region (Nakajima's scheme) and a sequential LP
   (one sparse HiGHS LP per round). Every round is re-legalized and accepted only if the *certified* size dropped.
   The LP variant is used as a cheap screen over the 6 best raw runs; SLSQP polishes the 2 most promising.
3. **Descend**: the best (n + 1)-packing minus each piece (ranked by the LP container size) is re-tightened;
   this fixed every case where n + 1 had beaten n.
4. **Lattice constructions** (`scripts/constructions.py`, §7) are added as candidates.
5. **Records** (`scripts/records.py`): the best certified packing per (A, B, n) gets ≥ 10⁻⁷ clearance, a record file,
   both checker outputs, a picture and a table row.

### 5b. Basin hopping (since 9 Oct)

The search now alternates local optimization (tightening) with perturbations from the archive, a monotonic basin-
hopping scheme. A perturbation expands the packing, replaces each piece P by the softer S_r ⊆ P (Lemma 1), and
diffuses the pieces at fixed container size until the relative arrangement has changed: with d_ij the centre distances
before and d'_ij during shaking, the change is Δ = RMS over neighbouring pairs of (d'_ij − d_ij), in piece edges, and
shaking continues (with growing noise and softness) until Δ reaches a random target in [0.04, 0.6]. Re-sharpening
then follows the same monotone homotopy as a fresh run (r → 0 under pressure), so the new packing is again a local
optimum, typically in a different basin. Monotonicity across n is enforced as an invariant of the archive (§1:
deleting a piece never needs a larger container).

## 6. Observations from the results

(All values: container edge / piece edge. "≈ x" marks a conjectured closed form: the touching limit `s_tight`
agrees with x to about 11 significant digits and x is a quadratic irrationality with small coefficients. This is
numerical evidence, not a proof; the exact certificate is for the slightly larger `s_full`.)

* **Two pieces fit in less than 2 for every non-cube solid**: tetrahedra ≈ 1.95356, octahedra ≈ 1.93312,
  icosahedra ≈ 1.96309, dodecahedra ≈ 1.98760 (touching limits), while two unit cubes need a cube of side 2. The pieces tilt so that
  each one uses a different "corner region" of the container. These values have no small closed form found.
* **Tetrahedra.** 3, 4, 5 → 2 (5 is the edge-2 subdivision with a tetrahedron in the octahedral hole, §7);
  6 ≈ (3 + √15)/3;
  8 → 1 + √2 (conj.); 13 → 2.97194, strictly below the lattice value 3; 14, 15 → 3 (edge-3 subdivision holds 15).
* **Octahedra.** 3–6 → 2 (6 is the edge-2 lattice); 7, 8, 9 → 5/2; 10, 11 → 8/3; 12 → (6 + √6)/3 (conj.);
  16–19 → 3 (19 is the edge-3 lattice).
* **Icosahedra.** 3 → 2; 4 ≈ (11 − 3√5)/2; 5 ≈ √5; 6 ≈ (5 + 3√5)/5; 9 ≈ 16 − 6√5; 11 and 12 ≈ φ² = (3 + √5)/2,
  with the 12 pieces sitting in the 12 vertex regions of the container.
* **Dodecahedra.** 3, 4 → 2; 5, 6 ≈ √5; 7 ≈ (3 + 2√5)/3; 8 ≈ 7 − 2√5; 11, 12 ≈ 5 − √5; 14 → 3.
* Golden-ratio values appear only for the dodecahedron and icosahedron (field Q(√5)), and √2, √3, √6 only for the
  tetrahedron and octahedron, as the coordinate fields suggest.
* Plateaus (equal s for consecutive n, e.g. octahedra 7–9 and 16–19) are where a rigid lattice-like structure with
  spare room is optimal for several n; these are the cases most likely to be optimal and the first targets for
  lower-bound proofs.

The full table, with links to every record, is `records/README.md`; the numbers with all digits are in
`records/SUMMARY.csv`.

## 7. Constructions (exact, touching)

**Lemma 3 (a unit tetrahedron fits exactly in a unit octahedron).** In a unit-edge octahedron, opposite faces are
parallel at distance 2ρ_oct = 2/√6 = √(2/3), which is the height of a unit tetrahedron. Take one face F as the base;
the opposite face F' is F reflected through the centre, so the centroid of F' projects orthogonally onto the
centroid of F. The tetrahedron with base F and apex at the centroid of F' is therefore regular with unit edge, and
it lies in the octahedron (convex hull of points of the octahedron). It touches F' at one point and contains the
three edges of F.

**Tetrahedra.** Cut the edge-k tetrahedron by the planes parallel to its faces at integer distances (in the
k-subdivision). The pieces are C(k+2, 3) upright unit tetrahedra, C(k, 3) inverted unit tetrahedra and C(k+1, 3)
unit octahedra (volume check: k³ = C(k+2,3) + 4·C(k+1,3) + C(k,3), with vol(oct) = 4·vol(tet)). With Lemma 3, an
edge-k tetrahedron holds C(k+2,3) + C(k+1,3) + C(k,3) unit tetrahedra: 5 for k = 2, 15 for k = 3, 34 for k = 4.
In coordinates (canonical vertices V_0..V_3): upright tetrahedra centred at Σ m_i V_i with Σ m_i = k − 1, inverted
ones (= the canonical tetrahedron rotated 90° about a coordinate axis) centred at Σ m_i V_i with Σ m_i = k − 3, and
octahedral holes centred at Σ m_i V_i with Σ m_i = k − 2.

**Octahedra.** Write the unit octahedron as {|x| + |y| + |z| ≤ a}, a = √2/2. Copies centred at a·m for integer
vectors m with |m|₁ ≤ k − 1 and |m|₁ ≡ k − 1 (mod 2) lie in {|x| + |y| + |z| ≤ k·a}, the edge-k octahedron, and two
distinct centres are at L1-distance ≥ 2a, so interiors are disjoint. Count (2k³ + k)/3: 6 for k = 2, 19 for k = 3,
44 for k = 4.

These constructions give s_tet(15) ≤ 3 and s_oct(19) ≤ 3 with touching pieces; the record files contain them (or
better packings) with 10⁻⁷ clearance, which is why their certified s_full is 3.00000+ rather than exactly 3. They are
rigid under the tightening, and "descend" from them produced the 13- and 14-tetrahedron and 16–18-octahedron
records.

## 8. What would make these results stronger

* **Optimality proofs for small n.** For n = 2 the problem is a finite-dimensional optimization over two rigid
  motions; an interval branch-and-bound over SO(3)² × translations (with the exact separation test as the leaf
  check) could plausibly prove the n = 2 values. Plateau values (octahedra 7–9 at 5/2, 16–19 at 3; tetrahedra 3–5 at
  2) are the next natural targets.
* **Exact touching certificates.** For the conjectured closed forms, snapping the contact graph to exact algebraic
  coordinates and certifying the touching packing in Q(√2, √5) (or an extension) would prove s ≤ closed form.
* **More search.** The basin-hopping engine runs indefinitely on all nine problems up to n = 40 (STATUS.md); the
  other 16 mixed pairs are supported and can be added to the engine.
