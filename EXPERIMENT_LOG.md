# Experiment log

Chronological record (2026, Europe/Paris time). "Budget ×1" = 5,000 compress + 45,000 morph + 3,000 settle steps.
Machine: 2 CPU cores, Node 22, Python 3.13.

## 9 Oct, 01:40–02:30 — Port and validation

- Located `yoheinakajima/soft-to-rigid-packing` (12 unit cubes in a cube of side 2.9315185094797). Read `sim3.js`,
  `exact3.py`, `verify.py`, `certify_exact.py`.
- Exact solids (`solids.py`): unit-edge coordinates in Q(√2) / Q(√5); faces derived from vertex triples; exact checks of
  edges, counts, Euler, insphere. Inradii² 1/24, 1/4, 1/6, 5/8 + 11√5/40, 7/24 + √5/8 (match the closed forms).
- Geometry kernel (`src/geom.js`): SAT penetration (asymmetric intervals, so the tetrahedron works), exact separated
  distance by slab-pruned feature enumeration, analytic gradients. Test: 1,500 random pairs over all 25 solid pairs,
  0 failures (KKT-certified distances, minimal penetrations, gradients to 1.4e-9).
- Simulator (`src/sim.js`) on cubes vs the original `sim3.js`, same seeds: n = 8 → 2.000000 for both (seeds 1, 2);
  n = 9 → 2.7421 / 2.8284 (ours) vs 2.8284 / 2.7541 (original). Same behaviour, ~1.5× faster.
- Exact tightening (`src/exact.py`) with analytic Jacobian (checked against central differences, ~1e-9 for every
  solid). First tightenings snap onto exact values: 4 tetrahedra → 2, 3 dodecahedra → 2, 4 octahedra → 2.
- Checkers: `verify.py` (float SAT) and `certify_exact.py` (exact). Both certify Nakajima's n = 12 cube claim and the
  Hyra-results record of 21 unit-edge octahedra in a cube (2.592849935818519) — which also confirms that "unit" means
  unit edge in that catalogue. Both reject a container shrunk by 3e-6 and a piece pushed 3e-6 into a neighbour.

## 9 Oct, 01:55–02:35 — Screen, X-in-X, n = 2–12, 8 seeds, budget ×1 (+ cube regression)

- Cube regression: n = 2…8 → exactly 2; n = 9 → 2.70711 = 2 + 1/√2 (2 of 8 seeds); n = 10–12 not at the catalogue
  values with 8 seeds (expected: Nakajima needed many seeds for those).
- First observations: two copies fit in a container of edge < 2 for every non-cube solid (tetrahedron 1.95356,
  octahedron 1.93312, icosahedron 1.96309, dodecahedron 1.98760), unlike cubes where s(2) = 2.
- Non-monotone screen values (e.g. 9 tetrahedra 2.866 but 10 tetrahedra 2.817) → more seeds, and the `descend`
  step (n from n + 1 minus one piece).

## 9 Oct, 02:30 — Scope from Alejandro

n = 2…20, smallest Platonic container A for n unit Platonic B; first the four A = B ≠ cube cases, then the rest;
one record per solution.

## 9 Oct, 02:35–03:10 — Infrastructure for the full scope

- Kernel speed-up (tighter slab after vertex–face tests, bounding-sphere rejection of edge pairs, allocation-free
  segment distance): identical trajectories, ~1.6× faster on dodecahedra.
- Exact arithmetic extended to Q(√2, √5) (sign via p + q√5, p, q ∈ Q(√2)); 3,000 random elements checked against
  80-digit decimals, plus near-cancellation cases. Mixed pairs now certify (e.g. 4 tetrahedra in an icosahedron of
  edge 1.00125, Q(√2, √5)).
- Tightening: constraint pruning to what the trust region can reach, plane offsets relative to the pair midpoint,
  vectorized Jacobian, stop after 3 non-improving rounds.
- Lattice constructions (`scripts/constructions.py`): tetrahedron of edge 3 holds 15 unit tetrahedra (10 upright,
  1 inverted, 4 in the octahedral holes), edge 2 holds 5; octahedron of edge 3 holds 19 unit octahedra, edge 2 holds 6.
  All certify at exactly s = 2 or 3 (touching) and are rigid under tightening. The search had found 3.008–3.12 for
  13–15 tetrahedra, so these constructions matter.
- Faster exact checker: face derivation prescreened in floats, completeness proven exactly (every edge on exactly two
  faces); all five solids build in 0.8 s.

## 9 Oct, 03:10–07:50 — Same-solid sweep to n = 20

- Queue 3: n = 13–20 seeds 1–16, n = 2–12 seeds 9–16, all n seeds 17–24 (budget ×1). Total raw runs ≈ 1,770.
- Tightening reorganized: a sequential-LP variant (one sparse HiGHS LP per trust-region round) is 2–20× faster than
  SLSQP but sometimes stops at a slightly worse point (tetrahedra n = 9: 2.76695 vs 2.76643; icosahedra n = 13:
  2.83362 vs 2.83354), so it is used as a screen over the 6 best raw runs and SLSQP polishes the 2 best.
  Raw ranking is a poor predictor of tightened ranking (dodecahedra n = 13: raw 3.0001 → 2.968 beat raw 2.987 → 2.980).
- Descend (n from n + 1 minus a piece) fixed every non-monotone case: 17 dodecahedra 3.2122 → 3.1985 (later 3.1677
  from a new seed), 7 octahedra 2.6029 → 5/2, 17 tetrahedra 3.1635 → 3.1169, 9 tetrahedra 2.766 → 2.655.
- Clearance in record files reduced from 1e-6 to 1e-7 (tetrahedral containers: wall gap g costs ≈ 4.9 g in edge).
- 13 tetrahedra: 2.97194 < 3, below the edge-3 lattice construction.
- Stopped at 07:50 on request; mixed pairs not started (STATUS.md).

## 9 Oct, 11:40–12:20 — Engine rework (Alejandro's requests)

- Timing per phase (budget ×1): compressing balls 0.4–0.5 s; the 45,000-step morph 18 s; the rigid settle 2–8 s.
  Restarting from scratch is the waste, so the search moved to basin hopping from the archive (README Method §4).
- Hop smoke tests from the best packings: small hops (minDiff 0.05) return to the best basin (12 dodecahedra raw
  2.76393 = best), larger ones explore (raw 2.99–3.80); focused hops (5-piece cluster) stay closer (18 icosahedra:
  raw 3.328 vs 3.357 for a global hop of the same size).
- Kernel: separating-axis hints, identical results on 731 hinted re-evaluations. Legalization: Newton steps on the
  scale factor instead of 60-step bisection; SLP tightening of 20 dodecahedra 120 s (not converged, 3.4078) →
  24.5 s (converged, 3.3951).
- Archive seeded from all earlier tightened runs (results/*.jsonl) plus lattice constructions; dodecahedra n = 19
  improved to 3.30068 by a pool member; monotone rule filled cubes in a cube 2–39 and lattice-derived cases at once.
- First 3 minutes with two workers: ~40 attempts, every new dual problem filled from n = 2 upward by ascend moves,
  monotone fixes applied (e.g. 4 octahedra in a cube set from 5 minus a piece). Archive check ok, no errors.
- 12:03: launched `scripts/run_forever.sh` (unattended).
- 13:24: check-in found the machine had been suspended at ~12:11 (uptime 0 min, processes gone; files intact).
  Restarted; the session is now kept active with 10-minute heartbeats so the engine keeps running.
