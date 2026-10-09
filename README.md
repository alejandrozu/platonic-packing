# platonic-packing

**How small can a Platonic solid be and still hold n unit copies of a Platonic solid?** This repository answers that,
with proofs of validity, for nine problems — each Platonic solid in a copy of itself, and the dual pairs (cubes in an
octahedron, octahedra in a cube, dodecahedra in an icosahedron, icosahedra in a dodecahedron) — for n = 2 to 40, using Yohei Nakajima's
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
_Auto-generated 2026-10-09 12:06 CEST from the running search; see [PROGRESS.md](PROGRESS.md) for search statistics._

### Same solid

| n | Tetrahedra in a tetrahedron | Octahedra in an octahedron | Icosahedra in an icosahedron | Dodecahedra in a dodecahedron | Cubes in a cube |
|---:|---|---|---|---|---|
| 2 | [1.95356+](records/tetintet/tetintet_n02.json) |  |  |  |  |
| 3 | [2.00000+](records/tetintet/tetintet_n03.json) |  |  |  |  |
| 4 | [2.00000+](records/tetintet/tetintet_n04.json) |  |  |  |  |
| 5 | [2.00000+](records/tetintet/tetintet_n05.json) |  |  |  |  |
| 6 | [2.29099+](records/tetintet/tetintet_n06.json) ≈ (3 + √15)/3 |  |  |  |  |
| 7 | [2.38195+](records/tetintet/tetintet_n07.json) |  |  |  |  |
| 8 | [2.41421+](records/tetintet/tetintet_n08.json) ≈ 1 + √2 |  |  |  |  |
| 9 | [2.65503+](records/tetintet/tetintet_n09.json) |  |  |  |  |
| 10 | [2.74153+](records/tetintet/tetintet_n10.json) |  |  |  |  |
| 11 | [2.88886+](records/tetintet/tetintet_n11.json) |  |  |  |  |
| 12 | [2.91844+](records/tetintet/tetintet_n12.json) |  |  |  |  |
| 13 | [2.97194+](records/tetintet/tetintet_n13.json) |  |  |  |  |
| 14 | [3.00000+](records/tetintet/tetintet_n14.json) |  |  |  |  |
| 15 | [3.00000+](records/tetintet/tetintet_n15.json) |  |  |  |  |
| 16 | [3.10703+](records/tetintet/tetintet_n16.json) |  |  |  |  |
| 17 | [3.11687+](records/tetintet/tetintet_n17.json) |  |  |  |  |
| 18 | [3.14314+](records/tetintet/tetintet_n18.json) |  |  |  |  |
| 19 | [3.24448+](records/tetintet/tetintet_n19.json) |  |  |  |  |
| 20 | [3.38073+](records/tetintet/tetintet_n20.json) |  |  |  |  |
| 21 | [4.00000+](records/tetintet/tetintet_n21.json) |  |  |  |  |
| 22 | [4.00000+](records/tetintet/tetintet_n22.json) |  |  |  |  |
| 23 | [4.00000+](records/tetintet/tetintet_n23.json) |  |  |  |  |
| 24 | [4.00000+](records/tetintet/tetintet_n24.json) |  |  |  |  |
| 25 | [4.00000+](records/tetintet/tetintet_n25.json) |  |  |  |  |
| 26 | [4.00000+](records/tetintet/tetintet_n26.json) |  |  |  |  |
| 27 | [4.00000+](records/tetintet/tetintet_n27.json) |  |  |  |  |
| 28 | [4.00000+](records/tetintet/tetintet_n28.json) |  |  |  |  |
| 29 | [4.00000+](records/tetintet/tetintet_n29.json) |  |  |  |  |
| 30 | [4.00000+](records/tetintet/tetintet_n30.json) |  |  |  |  |
| 31 | [4.00000+](records/tetintet/tetintet_n31.json) |  |  |  |  |
| 32 | [4.00000+](records/tetintet/tetintet_n32.json) |  |  |  |  |
| 33 | [4.00000+](records/tetintet/tetintet_n33.json) |  |  |  |  |
| 34 | [4.00000+](records/tetintet/tetintet_n34.json) |  |  |  |  |
| 35 | [4.00588+](records/tetintet/tetintet_n35.json) |  |  |  |  |
| 36 | [4.02362+](records/tetintet/tetintet_n36.json) |  |  |  |  |
| 37 | [4.04601+](records/tetintet/tetintet_n37.json) |  |  |  |  |
| 38 | [4.06715+](records/tetintet/tetintet_n38.json) |  |  |  |  |
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

### 4. Basin hopping: the autonomous engine (`scripts/engine.py`)

Restarting every run from random balls wastes most of the time on reaching a dense packing. The engine instead keeps
an archive of the best packing and up to six distinct good packings for every (problem, n), and repeatedly applies
one of these moves to a case, chosen by a scheduler (least effort per piece first, every missing n filled first):

* **hop** (55%): take the best (or a pool) packing, expand it by 1–5%, soften the pieces to S_r (r = 6–20% of the
  inradius; by Lemma 1 they shrink inside their rigid shapes), and shake them at fixed container size until the
  *relative arrangement* has changed by at least a random target of 0.04–0.6 piece edges, measured as the RMS change
  of the distances between neighbouring pieces (noise and softness escalate every 400 steps until it has). For larger
  n, 60% of hops shake only a cluster of 3 to n/3 neighbouring pieces. Then re-sharpen under pressure and settle.
* **reinsert** (12%): remove 1–3 random pieces and put them back into the largest holes, re-sharpen.
* **fresh** (13%): a full soft-to-rigid run from random balls (keeps diversity).
* **ascend** (10%): the best (n−1)-packing plus one piece in its largest hole, re-sharpened.
* **descend** (10%): the best (n+1)-packing minus the piece whose removal lets the container shrink most (LP).

A raw result is tightened only if it is within the case's gate of the best (the gate adapts to how much tightening
typically gains for that case), with a sequential-LP tightener (one sparse HiGHS LP per trust-region round, with an
optimistic early abort) and an SLSQP polish for n ≤ 14. A hop costs 0.5–5 s instead of 20–60 s for a fresh run.

**Monotonicity is an invariant, not a hope.** s(n) ≤ s(n+1) always holds mathematically (delete a piece). The archive
enforces it on every write: whenever the best n-packing is worse than the best (n+1)-packing, the (n+1)-packing minus
one piece (same container, so never larger; LP refit) replaces it and the case is queued for re-tightening. Records
enforce it once more on the certified sizes (`scripts/publish.py`), and the test suite checks it.

The engine runs unattended (`scripts/run_forever.sh`): two workers restart themselves if they exit, and a publisher
rebuilds the records, tables, PROGRESS.md and the site, then commits and pushes, every 90 minutes.

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

The current search (all nine problems, n = 2–40):

```bash
nohup setsid scripts/run_forever.sh > logs/supervisor.out 2>&1 &   # start (resumes from state/best)
python3 scripts/engine.py status                                   # current table
python3 scripts/engine.py check                                    # archive invariants (monotone s(n))
python3 scripts/publish.py --no-push                               # rebuild records, tables, site now
touch state/STOP                                                   # stop gracefully
```

The original batch pipeline (still works):

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

`scripts/runqueue.sh <queue>` runs a queue file with two workers. All steps are idempotent (see STATUS.md).

Requirements: Node ≥ 18; Python ≥ 3.10 with NumPy, SciPy (search/tightening), matplotlib (pictures), mpmath
(closed-form hints). The checkers need only the Python standard library.

## Layout

```
solids.py            exact solids (Q(√2, √5)), derived faces, self-check
verify.py            float checker          certify_exact.py   exact checker (proof)
src/geom.js          signed distances + gradients     src/sim.js   soft-to-rigid dynamics
src/exact.py         SLSQP tightening, legalization   src/claim.py record files with clearance
scripts/engine.py    autonomous basin-hopping search with a monotone archive (state/best, state/pool)
scripts/publish.py   records + tables + PROGRESS.md + site + git push; scripts/run_forever.sh supervisor
src/server.js        JSON-lines compute server used by the engine (fresh runs and hops)
scripts/             also: batch runner, queue runner, pipeline (tighten/descend), constructions, figures, site
state/best/          the archive: best packing per (problem, n), internal units, with search statistics
PROGRESS.md          search statistics, regenerated by every publish
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
