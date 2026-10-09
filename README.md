# platonic-packing

**How small can a Platonic solid be and still hold n unit copies of a Platonic solid?** This repository answers that,
with proofs of validity, for the four same-solid problems (tetrahedra in a tetrahedron, octahedra in an octahedron,
icosahedra in an icosahedron, dodecahedra in a dodecahedron) and every n from 2 to 20, using Yohei Nakajima's
*soft-to-rigid* method: start every piece as its inscribed sphere, then sharpen it into the solid while inward
pressure shrinks the container. Every packing is **certified in exact arithmetic over Q(√2, √5)**.

It generalizes [`yoheinakajima/soft-to-rigid-packing`](https://github.com/yoheinakajima/soft-to-rigid-packing)
(unit cubes in a cube; his 12-cube record 2.9315185094797) from cubes to all five Platonic solids, as pieces and as
containers.

* **Read first:** [docs/MATH.md](docs/MATH.md) — the problem, the homotopy lemma, why the geometry is exact, what the
  certificate proves, the lattice constructions, observations, and what is *not* proven.
* **Records:** [records/README.md](records/README.md) (tables with links), [records/SUMMARY.csv](records/SUMMARY.csv)
  (all digits), one folder per problem with record files, checker outputs and pictures.
* **State of the work and next steps:** [STATUS.md](STATUS.md); chronological log: [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md).
* **Interactive viewer:** open [site/index.html](site/index.html) in a browser (3D view of every record, tables, s(n) chart).

## Results: s = container edge ÷ piece edge, n = 2…40

Nine problems: each Platonic solid in a copy of itself, and the dual pairs (cubes in an octahedron, octahedra in a cube,
dodecahedra in an icosahedron, icosahedra in a dodecahedron). Each entry is the smallest container found so far, as
certified (10⁻⁷ clearance, truncated to 5 decimals), linking to its record file. "≈ x" is a *conjectured* closed form
(touching limit agrees with x to ~11 digits; small integers omitted); ✱ marks a value below the best previously
published one (cubes in a cube: Friedman's catalogue and later records; octahedra in a cube: Hyra-results). s(n) is
non-decreasing in n by construction. The search is still running and this table is regenerated automatically.

<!-- RESULTS:START -->
_Auto-generated 2026-10-09 12:02 CEST from the running search; see [PROGRESS.md](PROGRESS.md) for search statistics._

### Same solid

| n | Tetrahedra in a tetrahedron | Octahedra in an octahedron | Icosahedra in an icosahedron | Dodecahedra in a dodecahedron | Cubes in a cube |
|---:|---|---|---|---|---|
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |
| 6 |  |  |  |  |  |
| 7 |  |  |  |  |  |
| 8 |  |  |  |  |  |
| 9 |  |  |  |  |  |
| 10 |  |  |  |  |  |
| 11 |  |  |  |  |  |
| 12 |  |  |  |  |  |
| 13 |  |  |  |  |  |
| 14 |  |  |  |  |  |
| 15 |  |  |  |  |  |
| 16 |  |  |  |  |  |
| 17 |  |  |  |  |  |
| 18 |  |  |  |  |  |
| 19 |  |  |  |  |  |
| 20 |  |  |  |  |  |
| 21 |  |  |  |  |  |
| 22 |  |  |  |  |  |
| 23 |  |  |  |  |  |
| 24 |  |  |  |  |  |
| 25 |  |  |  |  |  |
| 26 |  |  |  |  |  |
| 27 |  |  |  |  |  |
| 28 |  |  |  |  |  |
| 29 |  |  |  |  |  |
| 30 |  |  |  |  |  |
| 31 |  |  |  |  |  |
| 32 |  |  |  |  |  |
| 33 |  |  |  |  |  |
| 34 |  |  |  |  |  |
| 35 |  |  |  |  |  |
| 36 |  |  |  |  |  |
| 37 |  |  |  |  |  |
| 38 |  |  |  |  |  |
| 39 |  |  |  |  |  |
| 40 |  |  |  |  |  |

### Duals

| n | Cubes in an octahedron | Octahedra in a cube | Dodecahedra in an icosahedron | Icosahedra in a dodecahedron |
|---:|---|---|---|---|
| 2 | [2.70710+](records/cubinoct/cubinoct_n02.json) ≈ (4 + √2)/2 |  |  |  |
| 3 | [2.73922+](records/cubinoct/cubinoct_n03.json) |  |  |  |
| 4 | [2.91436+](records/cubinoct/cubinoct_n04.json) |  |  |  |
| 5 | [2.91436+](records/cubinoct/cubinoct_n05.json) |  |  |  |
| 6 | [2.97542+](records/cubinoct/cubinoct_n06.json) |  |  |  |
| 7 | [3.51403+](records/cubinoct/cubinoct_n07.json) |  |  |  |
| 8 |  |  |  |  |
| 9 |  |  |  |  |
| 10 |  |  |  |  |
| 11 |  |  |  |  |
| 12 |  |  |  |  |
| 13 |  |  |  |  |
| 14 |  |  |  |  |
| 15 |  |  |  |  |
| 16 |  |  |  |  |
| 17 |  |  |  |  |
| 18 |  |  |  |  |
| 19 |  |  |  |  |
| 20 |  |  |  |  |
| 21 |  |  |  |  |
| 22 |  |  |  |  |
| 23 |  |  |  |  |
| 24 |  |  |  |  |
| 25 |  |  |  |  |
| 26 |  |  |  |  |
| 27 |  |  |  |  |
| 28 |  |  |  |  |
| 29 |  |  |  |  |
| 30 |  |  |  |  |
| 31 |  |  |  |  |
| 32 |  |  |  |  |
| 33 |  |  |  |  |
| 34 |  |  |  |  |
| 35 |  |  |  |  |
| 36 |  |  |  |  |
| 37 |  |  |  |  |
| 38 |  |  |  |  |
| 39 |  |  |  |  |
| 40 |  |  |  |  |
<!-- RESULTS:END -->

Upper bounds only — none of these is proven optimal (see [docs/MATH.md](docs/MATH.md) §1 and §8). Highlights:
two copies of every non-cube solid fit in a container of edge **< 2** (two cubes need exactly 2); 15 tetrahedra fit
in a tetrahedron of edge 3 and 19 octahedra in an octahedron of edge 3 (exact lattice constructions, §7), yet 13
tetrahedra fit in 2.97194; 12 icosahedra fit in an icosahedron of edge ≈ φ²; 11–12 dodecahedra in ≈ 5 − √5.

Check any record yourself (standard library only):

```bash
python3 certify_exact.py records/dodindod/dodindod_n07.json    # exact proof: containment + a separating plane per pair
python3 verify.py        records/dodindod/dodindod_n07.json    # floating-point separating-axis check
```

## What is measured

`s(A, B, n)` = (edge of the container A) / (edge of each piece B) for the smallest container found, pieces free to
translate and rotate, interiors disjoint. Record ids follow Erich Friedman's naming (`cubincub` = cubes in cube):
`tet`, `cub`, `oct`, `dod`, `ico`, so `dodindod_n07` is 7 dodecahedra in a dodecahedron.

Every record is an **upper bound with a proof**: the record file lists the pieces, and `certify_exact.py` proves in
exact arithmetic that they are pairwise disjoint unit-edge copies of B inside `s_full · A`. Nothing here proves
optimality (the only general lower bound used is the volume bound `s ≥ (n·vol B / vol A)^{1/3}`).

## Method

### 1. Soft shapes (the homotopy)

For a convex solid P whose inscribed ball B(0, ρ) is centred at the origin (true for every Platonic solid), let

  S_r = (1 − r/ρ)·P ⊕ B(0, r),   0 ≤ r ≤ ρ,

a shrunken copy of P dilated by a ball of radius r. For the cube (ρ = ½) this is exactly Nakajima's rounded cube
("a cube of half-side ½ − r dilated by r").

**Lemma 1.** (a) S_ρ = B(0, ρ) and S_0 = P. (b) S_r ⊆ P for every r. (c) S_r ⊆ S_r' whenever r ≥ r'
(sharpening only grows the shape).

*Proof.* (a) is immediate. (b) A point of S_r is x = (1 − t)p + r·b with p ∈ P, |b| ≤ 1, t = r/ρ. Write
r·b = t·(ρb); since ρb ∈ B(0, ρ) ⊆ P, x is a convex combination of two points of P. (c) The support function is
h_{S_r}(u) = (1 − r/ρ) h_P(u) + r = h_P(u) − (r/ρ)(h_P(u) − ρ) for unit u, and h_P(u) ≥ ρ because B(0, ρ) ⊆ P;
so h_{S_r}(u) is non-increasing in r, and convex bodies are ordered by their support functions. ∎

So a packing of n copies of P in a container is also a packing of n copies of every S_r, and the smallest container
for S_r grows monotonically from the ball problem (r = ρ) to the polytope problem (r = 0). The search follows that
path: it never has to "undo" anything, it only has to make room.

**Lemma 2.** For convex K, L and r ≥ 0: dist(K ⊕ B(r), L ⊕ B(r)) = dist(K, L) − 2r when the cores are disjoint,
and the penetration depth of the rounded bodies is the penetration depth of the cores plus 2r. (The Minkowski
difference of the rounded bodies is that of the cores dilated by B(2r).) Hence the pair energy
(2r − sd_core)₊², with sd_core the signed distance of the cores, is the squared overlap depth of the soft shapes.

### 2. Dynamics (`src/sim.js`, `src/geom.js`)

As in the original: energy = Σ pairs (2r − sd_core)₊² + Σ walls (violation)₊² + μ·(container size); heavy-ball
descent on centres, quaternions and container size with a velocity cap and annealed noise; 5,000 steps compressing
balls, 45,000 steps lowering r linearly from ρ to 0, 3,000 steps of rigid settling (budget ×1). Pieces are scaled
internally so the inscribed ball has diameter 1, which lets every solid use Nakajima's tuned constants unchanged.

`sd_core` and its analytic gradient w.r.t. both centres and both rotation vectors:
* **overlapping cores** — exact penetration depth by the separating-axis theorem over face normals of both pieces
  and cross products of their edge directions (these contain every facet normal of the Minkowski difference, so the
  minimum projected overlap *is* the penetration depth); handles non-centrally-symmetric solids (tetrahedron);
* **disjoint cores** — exact Euclidean distance by feature enumeration (vertex–face, face–vertex, edge–edge),
  pruned by a slab argument: if u separates the cores with gap g and D ≥ dist, the closest points lie within D − g
  of the two support planes, so only features meeting those slabs are examined.

The container is a scaled copy of any Platonic solid, {x : N_f·x ≤ (L/2)} for its unit face normals N_f; the wall
term uses the support function of S_r in each N_f.

### 3. Legalization, exact tightening, record files

* `legalize`: scale centres apart until no pair overlaps, then the smallest container over all translations
  (a 4-variable LP).
* `src/exact.py`: SLSQP minimizing the container size with hard constraints — every vertex inside every container
  face, and a separating plane (2 tangent-plane parameters + offset) for each nearby pair — with an analytic
  Jacobian, trust regions, and re-legalization after every round (a round is accepted only if the *certified*
  size decreased). This is Nakajima's `exact3.py` generalized to arbitrary polytopes.
* `descend`: removing a piece from a valid (n+1)-packing gives a valid n-packing; the best (n+1)-packings are
  stripped of each piece in turn and re-tightened.
* `src/claim.py`: centres are spread until every pair is ≥ 10⁻⁷ apart, the container is fitted with ≥ 10⁻⁷ wall
  clearance, and `s_full` is rounded up at the 13th decimal (Nakajima used 10⁻⁶; for a tetrahedral container that
  shifts the 5th decimal, because a wall gap g costs g / inradius ≈ 4.9 g in edge length).

## Rigor: what is checked, and how

`solids.py` builds the five unit-edge solids with coordinates in Q(√2, √5) (exact; e.g. the dodecahedron uses
φ/2 = (1 + √5)/4) and **derives** their faces by brute force over vertex triples, then verifies exactly: all edges
have length 1, the V/E/F counts and Euler's formula, each face loop is an edge cycle on a supporting plane, and all
faces are equidistant from the centre (exact inradius² = 1/24, 1/4, 1/6, 5/8 + 11√5/40, 7/24 + √5/8).

`certify_exact.py <record>` (standard library only) then proves, with no rounding anywhere:

1. each piece is exactly congruent to the canonical solid (rotation H(q)/|q|² from the stored quaternion,
   exactly orthogonal for any rational q ≠ 0);
2. **containment**: every vertex of every piece is strictly inside every face half-space of `s_full · A`;
3. **disjointness**: for every pair, an explicit rational vector u with max over A of u·x < min over B of u·x.

Signs of elements a + b√2 + c√5 + d√10 are decided exactly (write p + q√5 with p, q ∈ Q(√2); compare p² with 5q²
in Q(√2)). Floating point only *proposes* the planes u, so a bad proposal can make certification fail, never pass.

`verify.py` is the same check in floating point (separating-axis test), in the style of the original `verify.py`.

Test suite (`bash test/run_all.sh`):
* 1,500 random pairs over all 25 solid pairs: every separated distance satisfies the exact optimality (KKT) conditions,
  every penetration depth is minimal over 12,000 random directions and is removed by translating that far,
  and every analytic gradient matches finite differences (max error ~1e-9);
* the tightening Jacobian matches central differences for every solid (~1e-9);
* **independent records certify**: Nakajima's 12 cubes in a cube (2.9315185094797) and the Hyra-results record of
  21 unit octahedra in a cube (2.592849935818519) both pass `certify_exact.py`;
* deliberately broken files (container shrunk 3·10⁻⁵, a piece pushed 10⁻⁴ through its neighbour, coincident pieces,
  a piece outside) are rejected by both checkers;
* exact field arithmetic is checked against 80-digit decimals on 3,000 random elements, including near-cancellations.

Regression against known cube results with the generalized code: n = 2…8 → exactly 2, n = 9 → 2 + 1/√2 = 2.70711
(Friedman's value).

## Record file format

`records/<id>/<id>_nNN.json` (same schema as Nakajima's and the Hyra-results claim files, plus a few fields):
`piece`, `container`, `n`, `s_full` (certified container edge), `s_plus` (5-decimal display), `s_tight` (touching
limit from tightening), `closed_form_conjecture`, `volume_lower_bound`, `density`, `clearance`, `search` (seed,
mode, parent for descended packings), and `pieces`: one `[x, y, z, qw, qx, qy, qz]` per piece — a unit-edge copy of
the canonical solid (coordinates in `solids.py` and docs/MATH.md §4) rotated by the scalar-first quaternion and centred
at (x, y, z). The container is `s_full` × the canonical unit-edge container solid, centred at the origin, in its
canonical orientation (`container_center` overrides the centre, e.g. (s/2, s/2, s/2) for Friedman-style [0, s]³ cubes).
Next to each record: `.certify.txt`, `.verify.txt` (checker outputs) and `.png`.

## Reproduce

```bash
python3 solids.py src/solids.json                       # exact solids, self-check, float export
bash test/run_all.sh                                    # tests
node scripts/batch.js tetrahedron same 7 1 8 1 improved # 8 runs: 7 tetrahedra in a tetrahedron (budget x1)
node scripts/batch.js octahedron icosahedron 5 1 8      # mixed pair: 5 octahedra in an icosahedron
python3 scripts/pipeline.py tighten 3                   # exact tightening of the best runs
python3 scripts/pipeline.py descend                     # n from n+1 minus a piece
python3 scripts/constructions.py                        # exact lattice packings (15 tetrahedra, 19 octahedra in edge 3)
python3 scripts/records.py                              # record files + checker outputs + pictures + tables
python3 scripts/site.py                                 # site/index.html
python3 certify_exact.py records/tetintet/tetintet_n07.json
```

`scripts/orchestrate.sh` runs everything unattended; `scripts/runqueue.sh <queue>` runs a queue file with two workers.
All steps are idempotent (see STATUS.md).

Requirements: Node ≥ 18; Python ≥ 3.10 with NumPy, SciPy (search/tightening), matplotlib (pictures), mpmath
(closed-form hints). The checkers need only the Python standard library.

## Layout

```
solids.py            exact solids (Q(√2, √5)), derived faces, self-check
verify.py            float checker          certify_exact.py   exact checker (proof)
src/geom.js          signed distances + gradients     src/sim.js   soft-to-rigid dynamics
src/exact.py         SLSQP tightening, legalization   src/claim.py record files with clearance
scripts/             batch runner, queue runner, pipeline (tighten/descend), constructions, records, figures, site
docs/MATH.md         mathematical notes: lemmas, certificate, constructions, observations, open questions
STATUS.md            what is done, what is not, how to resume
records/<id>/        record files, checker outputs, pictures, per-problem README table; records/SUMMARY.csv
runs/                raw search output (one JSON line per run)      results/tight.jsonl  tightened runs
test/                test suite and external fixtures
```

## Credit

Method and original code: Yohei Nakajima, *Twelve unit cubes in a cube of side 2.9315: soft-to-rigid packing*,
v1.0.0, Zenodo, 2026, doi:10.5281/zenodo.23248095 (MIT). This repository adapts its simulator, tightening and
checker design to general convex polytopes; see `LICENSE`. External test fixture: Tencent-Hunyuan/Hyra-results.
