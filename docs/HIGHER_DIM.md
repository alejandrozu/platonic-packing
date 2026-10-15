# Higher polytopes: packing regular polytopes in 4, 5 and 6 dimensions

_15 Oct 2026. Alejandro asked whether the method generalizes to 4D, 5D and 6D (the regular polytopes in themselves
and in their duals), how much effort that is compared with 3D, and what range of n is realistic. At 05:07 he extended
the scope to every piece–container pair of the same dimension._

## What was generalized

| Part | 3D (existing) | d dimensions (new) |
|---|---|---|
| Solids | `src/solids.json`, exact in number fields | `src/polytopes_nd.py` → `src/polytopes_nd.json`: 5-cell, tesseract, 16-cell, 24-cell, 120-cell, 600-cell; d-simplex, d-cube, d-orthoplex for d = 5, 6. Every coordinate exact in Q(√2, √3, √5, √7); facets checked exactly |
| Orientation | quaternion | rotation matrix in SO(d); increments are skew matrices (d(d−1)/2 parameters: 6, 10, 15) applied by the Cayley map |
| Overlap in the simulation | separating-axis theorem (face normals, edge × edge) | in d dimensions the candidate axes are normals to pairs of faces of complementary dimension: ~10⁵ per pair for the 120-cell. Instead every near pair tracks one axis u and improves it by projected super-gradient ascent on the gap g(u) = min u·y − max u·x (max over u = the signed distance). Support points by hill climbing on the edge graph |
| Separating planes (legality, tightening) | best SAT axis | `planes_lp`: for all near pairs at once, one block-diagonal LP (HiGHS) maximizing the gap with the linear normalization u·u₀ = 1, iterated. Exact to float precision even for face-to-face contacts |
| Tightening | sequential LP (`src/fastslp.py`) | `src/ndslp.py`: the same SLP with d-dimensional centres, skew rotation increments, and hyperplanes whose normals move in their (d−1)-dimensional tangent space |
| Simulator | `src/sim.js` (JavaScript) | `src/ndsim.py` (numba): same energy, schedule, heavy-ball integrator, hop / ascend / reinsert moves |
| Engine | `scripts/engine.py` | `scripts/engine_nd.py`: same archive rules (monotone s(n), pools, claims, sharding, export/harvest), archive `state/nd` |
| Certificate | `certify_general.py` | `certify_nd.py` (standard library only): exact polytope check (edges, all facets supporting and spanning, facet count), rational rotations D(I − S)⁻¹(I + S), containment and explicit rational separating hyperplanes, all by rigorous interval arithmetic |
| Site | 3D viewer | "Higher polytopes" tab: each packing drawn as its 3D slice x₄ = t (x₄, x₅, x₆ in 5D and 6D), with sliders and a sweep. Slices of disjoint pieces are disjoint convex polyhedra |

Problems: every ordered pair of regular polytopes of the same dimension, 6 × 6 = 36 in 4D, 3 × 3 = 9 in 5D, and 9 in 6D
(54 problems). Self packings and dual pairs are listed first.

## Cost compared with 3D

Benchmark: one GitHub runner (4 cores, 4 processes in parallel), `scripts/nd_bench.py`, raw data
`docs/data/nd_bench_2026-10-15.jsonl`. "Attempt" = one hop from a packing plus its tightening (the engine's usual
move), mean of two; the tightening has the engine's time limit of 30 + 4n seconds (190 s at n = 40).

| Problem | d | n | fresh + tighten (s) | attempt (s) | best s |
|---|---|---|---|---|---|
| dodecahedra | 3 | 20 | 13 | 9 | 3.41375 |
| icosahedra | 3 | 20 | 10 | 4 | 3.41983 |
| 24-cells | 4 | 20 | 24 | 24 | 2.82622 |
| 5-cells | 4 | 20 | 27 | 25 | 2.94969 |
| 600-cells | 4 | 20 | 44 | 41 | 2.94825 |
| tesseracts in a 16-cell | 4 | 20 | 21 | 30 | 4.75275 |
| 120-cells | 4 | 20 | 116 | 112 | 2.86679 |
| dodecahedra | 3 | 40 | 75 | 37 | 4.21482 |
| icosahedra | 3 | 40 | 17 | 21 | 4.13979 |
| cuboctahedra | 3 | 40 | 58 | 31 | 4.14801 |
| cubes in an octahedron | 3 | 40 | 36 | 48 | 5.25907 |
| 24-cells, 5-cells, 600-cells, 120-cells, tesseracts in a 16-cell | 4 | 40 | 104–201 | 127–197 (time limit) | |
| 5-simplices / 5-orthoplexes | 5 | 16 | 24–33 | 25–37 | |
| 5-dim, all three | 5 | 32 | 144–169 | 64–157 | |
| 6-simplices / 6-orthoplexes | 6 | 16 | 75–102 | 42–65 | |
| 6-dim, all three | 6 | 32 | 168–174 | 135–170 (time limit) | |

Reading it:

* **One attempt costs 3–6× a 3D attempt at the same n** (n = 20: 24–41 s against 4–9 s; the 120-cell, 600 vertices,
  ~15×). At n = 40 in 4D, and at n = 32 in 5D and 6D, the tightening uses its whole time limit, so an attempt costs
  ≥ 5× the 3D one and is not yet fully converged. The cost is in the linear programs: more variables per piece
  (10, 15, 21 against 6), more neighbours per piece, more vertices near each contact.
* **The search is harder**, not only slower. Random soft starts did not find the trivial grid of 32 5-cubes or of
  16–32 6-cubes at s = 2 (they reached 2.77 and 2.56). Exact constructions are therefore seeded (`engine_nd.py seed`:
  hypercube grids k^d), as in 3D.
* **What n means.** With 2 pieces per side at n = 2^d (16, 32, 64), n = 40 in 4D is already beyond "two per side",
  comparable with n ≈ 15–20 in 3D. Larger n would mostly add cases the available compute cannot search well.

## Decision

* n ranges: **4D n = 2–40, 5D n = 2–32, 6D n = 2–24** (54 problems, 1,890 cases; `NMAX_DIM` in `engine_nd.py`). These
  are a setting: they can be raised once the smaller cases have settled.
* Compute: from GitHub Actions run 4 (15 Oct 05:42) every one of the 18 search jobs runs one 4D/5D/6D worker next to
  three 3D workers (18 nD workers). With ~100–190 s per attempt that is ~400–650 nD attempts per hour, so the first
  filling pass (the ascend chain n = 2 … nmax of every problem) takes a few hours.
* Records: `scripts/publish_nd.py` (run by the publisher) writes `records/<id>/<id>_nNN.json` with 10⁻⁷ clearance and
  the exact certificate `…certify.txt`.

## Next improvements

1. Faster tightening at large n (the LPs dominate): fewer constraints per contact, a smaller rotation trust region,
   interior-point solves; the 120-cell problems would gain most.
2. More constructions: lattice and honeycomb cuts (the tesseract, 16-cell and 24-cell tile 4-space), as the crystal
   cuts did for 3D at large n.
3. Symmetric seeds (as `symfresh` in 3D).
