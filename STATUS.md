# Status and hand-off

_Last edited 10 Oct 2026, 20:25 Paris. Live numbers: [PROGRESS.md](PROGRESS.md) and [records/README.md](records/README.md),
both regenerated automatically every 90 minutes._

## Running now

The autonomous engine (`scripts/engine.py`, started by `scripts/run_forever.sh`) searches all nine problems for
n = 2…40 indefinitely:

| id | problem | id | problem |
|---|---|---|---|
| tetintet | tetrahedra in a tetrahedron | cubincub | cubes in a cube |
| octinoct | octahedra in an octahedron | cubinoct | cubes in an octahedron |
| icoinico | icosahedra in an icosahedron | octincub | octahedra in a cube |
| dodindod | dodecahedra in a dodecahedron | dodinico | dodecahedra in an icosahedron |
| | | icoindod | icosahedra in a dodecahedron |

* 2 worker processes (the machine has 2 cores), each restarted automatically if it exits.
* **Important:** the cloud machine that runs this is suspended a few minutes after the Claude session goes idle
  (found at 13:24 on 9 Oct: the engine had stopped at 12:11). The search therefore runs only while the session is
  kept active; it resumes exactly where it stopped (all state is on disk and the best packings are in git).
  GitHub Actions would make it independent of the session (offered to Alejandro, not set up).
* A publisher every 90 minutes: records (with exact certificates) for changed cases, `records/README.md`,
  `records/SUMMARY.csv`, `PROGRESS.md`, the README results table, `site/index.html`; then `git commit` + `git push`.
* Stop: `touch state/STOP`. Resume anywhere (also after the cloud machine is reclaimed): clone the repo and run
  `nohup setsid scripts/run_forever.sh > logs/supervisor.out 2>&1 &`. The archive (`state/best/`) is in git; the pools
  of alternative packings (`state/pool/`) are not, and refill by themselves.

## What changed on 10 Oct (evening)

1. **Search settings chosen by experiment** (19:14–20:14, EXPERIMENT_LOG.md): small "gentle" hops from the current
   best gave 46.9 new bests per CPU-hour against 19–27 for the old settings, harder shaking, a bigger container
   expansion, or three candidates per attempt. `state/policy.json` now selects gentle hops, 6% fresh runs, and sends
   30% of attempts to the 41 cases with published values. `scripts/experiment.py` repeats the comparison.
2. **Published values** (docs/references.json, Erich Friedman's Packing Center): only cubes in a cube and octahedra in
   a cube have them. Tables and the viewer show a "previous" column for those two problems.
3. **Published packings as starting points** (scripts/literature.py, docs/literature/): H. Lin's and Y. Nakajima's
   packings with public coordinates. Five values are now below the published ones, all exactly certified: octahedra in
   a cube n = 21, 24, 29, 30 and cubes in a cube n = 11 (n = 11, 21 and 24 refine Lin's packings; the record files say so).
4. **Viewer**: https://alejandrozu.github.io/platonic-packing/ (gh-pages branch, refreshed by every publish via
   scripts/pages.sh): slicing, colour by orientation, piece inspection, s(n) and increment charts.

## What changed on 9 Oct (second session)

1. **Basin hopping instead of restarts** (Alejandro's idea): from a tightened packing, relax (expand, soften, shake)
   until the relative arrangement of the pieces has changed by a target amount, then re-sharpen and re-tighten. Hops
   cost 0.5–5 s vs 20–60 s for a fresh run. Plus reinsert / ascend / descend moves (README, Method §4).
2. **Monotonicity is enforced**: s(n) ≤ s(n+1) holds in the archive after every write and in the certified records;
   the test suite checks both. (The final 9 Oct 08:00 records had one violation at the 13th digit, a clearance-rounding
   artifact, 14 vs 15 tetrahedra; intermediate snapshots had real ones.)
3. **Speed**: separating-axis hints (temporal coherence) in the kernel; vectorized Newton legalization (the 20-
   dodecahedra tightening went from 120 s, unconverged, to 25 s, converged and better); both checkers ≈ 5× faster
   with a provably safe shortcut for far-apart pairs.
4. **Scope**: nine problems up to n = 40. Lattice seeds: tetrahedron of edge 4 holds 34 tetrahedra, octahedron of edge
   4 holds 44 octahedra, cube grids k³.

## Things to look at next

* Compare cubes in a cube with the literature (`docs/references.json`: Friedman's catalogue to n = 17, Nakajima's
  12-cube record) and octahedra in a cube n = 21, 24 with Hyra-results. Cases where we are above the literature
  mean the search is not converged there; cases below would be new records (to double-check carefully).
* Optimality: none of the values is proven optimal (docs/MATH.md §8 lists approaches).
* Exact touching certificates for the conjectured closed forms.
* Add the remaining 16 mixed pairs if wanted (the engine handles any pair: add it to `PROBLEMS` in scripts/engine.py).

## Known caveats

* Closed forms in the tables are conjectures from 12-digit numerics (quadratic irrationalities with small
  coefficients, matched to 1e-11); larger-coefficient matches may be coincidences.
* Tightening is local; the engine's statistics (`state/best/*/nNN.json` → `stats`) show how much effort each case got.
* `s_full` in records includes 10⁻⁷ clearance; `s_tight` is the touching limit. Five-decimal displays are truncations.
