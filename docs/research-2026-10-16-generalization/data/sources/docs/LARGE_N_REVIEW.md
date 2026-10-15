# Large n (41–100): where the time goes and how to mass-produce (14 Oct 2026)

Alejandro, 14 Oct 04:57: *"we want to actually increase the number of polyhedra up to 100 … we will need to find a
new better optimized way … research for as long as you may need, up to 4h"*. This is the study. All numbers are
measurements made today; the scripts are listed in each section.

## Summary

* **Large n is a construction problem first.** Cutting a dense crystal to the container gives a legal packing for
  every n at once, in 20–160 s per problem. New `crystal.py` finds the crystals (it reproduces the Betke–Henk lattice
  densities and the 207/208 truncated-tetrahedron dimer crystal); `crystal_cut.py` cuts them. At n ≤ 40 this already
  improved **146 records** in 26 problems (median −1.9%, up to −11%), and it seeded all **3,660 cases n = 41–100**.
* **Tightening is the bottleneck, and its LP is degenerate.** A tiny cost on the moves makes it converge 2–10× faster
  to the nearby optimum; the unregularized LP's vertex jumps are useful exploration from a loose start. Hence a new
  cheap move, **perturb** (expand 0.3–5%, displace, re-tighten, no simulation): 17 of 21 paired wins at n = 32–40
  against 11 for hops, 2.5× the wins and 1.4× the gain per CPU-hour.
* **The simulation is not where time can be saved**: a shorter quench loses (21 of 21 paired hops), a longer one
  gains a little.
* **20 jobs on GitHub Actions** (free for a public repository, 6× the hourly search) took 20 problems from n = 40
  toward 100 in 190 minutes; eight reached 100. The ascend chain plus crystal cut is a reliable first draft that
  hops then improve 32–89% of the time; 994 of its 1,014 packings beat the crystal-cut seeds and are in the archive,
  and 23 more n ≤ 40 records came from the new n ≥ 41 packings (minus pieces).
* **Recommendation:** raise `PP_NMAX` to 100; fill with the largen workflow (20 jobs, one night); then polish with the
  engine using the fast tightener and the perturb move on 20 jobs. Estimated one to two days of free compute for
  all 61 problems.

## 1. Where the time goes

**Production log since 13 Oct 15:08** (cloud attempts, all moves):

| n | median s / attempt | mean | records improved per attempt |
|---|---:|---:|---:|
| 1–8 | 1.1 | 2.1 | 2.3% |
| 9–16 | 3.7 | 8.4 | 6.7% |
| 17–24 | 4.7 | 8.1 | 12.5% |
| 25–32 | 7.8 | 15.0 | 16.2% |
| 33–40 | 12.6 | 23.9 | 18.7% |

At n = 31–40 a hop spends a median 6.8 s in the soft-to-rigid simulation and 6.7 s (mean 18.8 s, heavy tail)
in the tightener. The improvement rate *rises* with n: the large-n records are young.

**At n = 41–100** (the Actions study, section 5) one ascend step costs a median 8–142 s of simulation and
7–247 s of tightening per attempt, depending on the solid; the tightener ran into its 600-round cap in up to 86% of
the attempts (for the slowest solids the time limit stopped it first). Tightening is 60–90% of the time at large n, and the cost of a step grows from 16–360 s (n = 41–60) to
167–442 s (n = 81–100) of wall time with 4 attempts in parallel. Exact certification is not a bottleneck: 0.5 s for
70 triakis tetrahedra or 87 octagonal prisms, 5–9 s for 46–51 disdyakis triacontahedra or truncated icosidodecahedra (62 and 120 vertices).

## 2. Crystal cuts

For large n the cheapest good packings are pieces of a dense crystal cut to the container. Two new scripts:

* `scripts/crystal.py` finds dense **lattice** packings (K + Λ) and, for pieces without a centre of symmetry,
  **double lattices** (K + Λ together with the point-reflected copy −K + t + Λ, which is a rotated copy for achiral
  pieces) by direct optimisation. Two translates K and K + v overlap iff v lies inside the difference body K − K,
  whose facet normals are among the separating-axis candidates, so admissibility is max_u |u·v| / w(u) ≥ 1 for every
  lattice vector (w = width of K along u); SLSQP from random starts, LLL reduction between rounds, final check for all
  |m_i| ≤ 4. For prisms it also builds **columnar crystals** (straight stacks of the densest planar lattice or double
  lattice of the base polygon). It reproduces the published values: lattice densities of the cuboctahedron 0.9184
  (Betke–Henk 0.9183), rhombicuboctahedron 0.8758, truncated cube 0.9737, truncated tetrahedron 207/304, snub cube
  0.7877, truncated cuboctahedron 0.8494; the truncated-tetrahedron double lattice 207/208 = 0.99519 (Jiao–Torquato);
  the planar hexagon 1, octagon 0.9062, dodecagon 0.9282, triangle (double) 1, pentagon (double) 0.9213. All 51
  crystals are cached in `state/crystals/`.
* `scripts/crystal_cut.py` cuts a crystal to the container: for a rotation R and a fractional offset o, every lattice
  site i has a smallest container scale s_i that holds its piece (max over container faces of (N_f·c_i + h_P(N_f))
  / (ρ_C off_f)); the n-th smallest s_i is the container needed for n pieces, for all n at once. Rotations: random,
  plus "aligned" ones that put a dense lattice plane parallel to a container face, spun about it; offsets on a 5³
  grid; then a local random refinement per n. A whole problem (all n ≤ 100) takes 20–160 s. Every cut packing is
  re-legalized and measured (`exact.certify`) before it is used.

**Result for n ≤ 40: 146 records improved** in 26 problems (median gain 1.9%, largest 11% (24 triangular prisms of height 3 in a cube, 3.9817 → 3.5424)). They are
the tiling and near-tiling cases: hexagonal prisms in a cube (n = 31–40 all fit in 3√3 = 5.196, records were
5.244–5.617), triangular prisms of heights 1.5 and 3 in a cube (n = 24: 3.9817 → 3.5424, −11%), octagonal prisms
in an octagonal prism (n = 20 and 21 fit in s = 3), 37–40 rhombicuboctahedra (all in 4.0938; n = 40 was 4.2229),
dodecagonal antiprisms in their own shape (n = 37–40, up to −5.7%), 5 dodecagonal antiprisms in a cube (4.6942 →
4.3176). For the other Archimedean and Catalan solids the cut is still 2–10% worse than the records at n ≤ 40, as the
boundary layer dominates; at n = 41–100 it competes (section 5).

## 3. Tightening

**Profile.** In the production tightener (sequential LP inside a trust region, `exact.solve(method='slp')`) a round
at n = 40 costs 0.1–0.14 s: 60–70% in the LP (HiGHS), the rest in Python loops over pairs (separating planes,
constraint selection, a dense Jacobian converted to sparse, legalization). A run needs 200–600 rounds (600 is the
cap); at n = 60 one run took 325 s.

**Vectorized tightener** (`src/fastslp.py`, same algorithm, same certification of every round): near pairs,
separating planes (`exact.pair_gaps_pruned`), constraint selection and a sparse Jacobian are array code, and the LP is
posed in the step. A round is 0.9–3× cheaper; after this the LP itself is 80% of the time.

**The LP is massively degenerate.** Only the container size is in the objective, so every other variable may sit
anywhere in its box; the simplex returns a vertex, which moves most pieces to their trust-region bounds. Adding a
tiny cost on the moves (`reg · Σ|Δc| + |Δφ|`, split variables) picks the smallest optimal step:

| start (perturbed record or Actions best) | exact SLP | fast, reg = 1e-4 |
|---|---|---|
| n = 35–40, 14 cases | 5.5–136 s, 47–600 rounds | 1.1–18 s, 21–152 rounds |
| 70 triakis tetrahedra | 117 s | 62 s (and a smaller s) |
| 80 octagonal prisms in a cube | 93 s | 9 s |
| 60–65 rhombic triacontahedra / cuboctahedra / truncated tetrahedra | 73–124 s | 13–14 s |

The regularized LP converges 3–10× faster **to the nearby optimum**. But the vertex jumps are also *exploration*:
from a loose start (the record expanded by 0.5–2% and its centres displaced by 0.3–1.5% of an edge) the
unregularized SLP **beat 11 of 14 records at n = 35–40** (e.g. 40 truncated cuboctahedra 4.1156 → 4.1088,
40 icosidodecahedra 4.0895 → 4.0841, 40 hexagonal antiprisms in a cube 5.3862 → 5.3818) and improved 5 of 7 Actions
bests at n = 60–80 (60 rhombic triacontahedra 4.7482 → 4.7385), while the regularized LP from the same starts stayed
at the record. Started from the regularized optimum instead, the unregularized LP finds little: the exploration
needs the slack of the loose start.

So tightening becomes two tools:
* **fast tightening** for every attempt (reg = 1e-4), and when an attempt lands within 0.3% of the best, the
  unregularized LP from the same raw start as well;
* a new move **perturb** (expand + displace the best, unregularized SLP, no simulation), a cheap polisher.

Paired test, 21 cases at n = 32–40 in 12 problems, each case once with every method from the same record:

| method | wins | CPU s | wins per CPU-hour | log-gain per CPU-hour |
|---|---:|---:|---:|---:|
| hop + exact SLP (production) | 11 | 1,102 | 36 | 0.018 |
| hop + fast two-speed tightener | 12 | 1,475 | 29 | 0.018 |
| perturb (expand 0.5–2%) | 17 | 677 | 90 | 0.026 |

Perturbation size (229 tries on random problems at n = 28–40, records that had been tightened before):

| expand / displacement | wins | s per try | wins per CPU-hour | log-gain per CPU-hour | largest gain |
|---|---:|---:|---:|---:|---:|
| small, 0.2–0.6% / 0.1–0.4% | 37 / 56 | 12 | 196 | 0.009 | 0.05% |
| medium, 0.5–2% / 0.3–1.5% | 34 / 56 | 20 | 108 | 0.031 | 0.17% |
| large, 2–5% / 1.5–4% | 17 / 57 | 12 | 92 | 0.106 | 0.44% |
| medium, displacing only one cluster (a quarter of the pieces) | 27 / 60 | 15 | 112 | 0.034 | 0.21% |

Small kicks win most often, large ones gain the most; the engine draws the expansion log-uniformly from 0.3–5%.
(On records just made by crystal cuts, which had never been tightened, every variant gained far more, up to 6%;
those 51 tries are excluded above.)

Both are in `scripts/engine.py` behind policy switches (`tightener: fast`, move weight `perturb`), not yet active.
An LP that hung for 15 minutes (24 rhombic dodecahedra at exactly s = 3.5) also showed that every LP needs a time
limit; that fix is live.

## 4. The simulation

A hop at n = 31–40 spends ~7 s in the soft-to-rigid simulation; at n = 41–100 the Actions study measured a median
8–142 s per ascend, depending on the solid, against 7–247 s of tightening.

**Shorter quench? No.** Paired hops from the same records (laptop, n = 35–39, 6 problems): the morph length
4000 + 150n gave the lowest raw size in 21 of 21 triples against 4000 + 50n and a fixed 4000 (median raw gap to the
record 0.12% vs 0.20% vs 0.28%) for only 25–40% more time; doubling it to 4000 + 300n lowered the raw gap further
(0.15% vs 0.20%, lower in 21 of 24 pairs) for 20–35% more time. The step count is not where large n can be saved;
if anything a slower quench pays.

**Per-step cost.** Each step costs O(n²) cheap distance tests plus a GJK/SAT test for each touching pair (~6n) and
n·F·n_v wall tests. At n ≤ 100 the distance tests are ~15% of a step, so cell lists or BVHs (HPMC) give little; the
real multipliers would be a compiled/vectorized pair kernel (2–5×) or a batched GPU soft phase (10–100×, large
engineering cost; the 2025–26 square-packing records came from such batches).

## 5. Twenty problems from n = 41 to 100 on GitHub Actions

`scripts/largen_bench.py` via `.github/workflows/largen.yml`: 20 problems in parallel (one 4-CPU job each,
190 minutes), starting from the n = 40 record. For n = 41, 42, …: three ascend attempts (insert a piece into the
best (n − 1)-packing at its largest hole, hop, tighten) and the tightened crystal cut compete; then a descend sweep
(monotone s(n)) and hops at random n until the time is up. 1,014 packings came back; all were re-legalized here, and the 994
that beat the crystal-cut seed of their case replaced it in the archive (n > 40 is ignored by the engine and the site until `PP_NMAX` is raised), and the descend
rule then improved **23 records at n ≤ 40** from them (e.g. 40 truncated tetrahedra 4.0073 → 3.9710, from the 41-piece
packing).

| problem | reached n | s(60) | s(80) | s(100) | steps won by the cut | cut vs best ascend (median) |
|---|---:|---:|---:|---:|---:|---:|
| ap5incub | 100 | 5.3808 | 5.7381 | 6.1531 | 3 / 60 | +3.2% |
| ap8inap8 | 85 | 4.5625 | 5.0000 | — | 6 / 45 | +1.2% |
| cboincbo | 100 | 4.6783 | 5.0000 | 5.3953 | 2 / 60 | +2.2% |
| ditindit | 89 | 4.7941 | 5.2250 | — | 0 / 49 | +1.3% |
| dtcindtc | 68 | 4.7800 | — | — | 0 / 28 | +1.5% |
| ktoinkto | 100 | 4.5843 | 4.9554 | 5.4563 | 3 / 60 | +1.5% |
| kttinktt | 100 | 4.5756 | 5.0384 | 5.4006 | 0 / 60 | +2.7% |
| pr3incub | 100 | 3.2792 | 3.7750 | 3.9589 | 26 / 60 | +0.1% |
| pr5inpr5 | 100 | 4.4342 | 5.0000 | 5.1152 | 16 / 60 | +0.9% |
| pr6l2incub | 100 | 7.7321 | 8.0000 | 9.4326 | 15 / 60 | +0.0% |
| pr8incub | 100 | 7.2426 | 8.2426 | 9.0000 | 8 / 60 | +3.3% |
| rcoinrco | 90 | 4.7760 | 5.1595 | — | 6 / 50 | +1.3% |
| rdoinrdo | 92 | 4.6667 | 5.0000 | — | 16 / 52 | +0.1% |
| ridinrid | 76 | 4.7532 | — | — | 1 / 36 | +1.9% |
| rtcinrtc | 96 | 4.7482 | 5.2025 | — | 0 / 56 | +1.7% |
| sncinsnc | 78 | 4.7609 | — | — | 0 / 38 | +1.4% |
| tcointco | 84 | 4.6988 | 5.0897 | — | 1 / 44 | +1.8% |
| tidintid | 76 | 4.7133 | — | — | 3 / 36 | +2.0% |
| tocintoc | 90 | 4.6667 | 5.0000 | — | 11 / 50 | +1.0% |
| tteintte | 90 | 4.3440 | 4.7480 | — | 1 / 50 | +4.1% |

* **Speed.** Eight problems reached n = 100 within 190 minutes (octagonal prisms in a cube in two hours); the four
  slowest solids (rhombicosidodecahedron, snub cube, truncated icosidodecahedron, disdyakis triacontahedron) reached 68–78.
* **The cut** won 0–43% of the steps: often for prisms and space-filling solids (triangular prisms in a cube 26 of
  60, rhombic dodecahedra 16 of 52, pentagonal prisms 16 of 60), rarely for the other Archimedean and Catalan
  solids, where it is a median 1–4% behind the ascend chain at n ≤ 100.
* **The chain is only a first draft.** Hops on the finished n = 41–100 packings won **75–89%** of the time for
  four Archimedean, Catalan and antiprism problems (20–84 hops each) and 32–57% for three prism problems; after 464
  hops octagonal prisms in a cube were down to 12.5%. Large-n cases need polishing time after the fill, exactly as
  the young n ≤ 40 cases did.
* **Densities** at the largest n reached are 0.55–0.75 (n = 40 records: 0.48–0.64), still far below the bulk
  crystals (0.77–1.0): the boundary dominates up to n = 100.

## 6. What the literature does at large n

* **Equal spheres in a cube** (Gensane 2004; Joós 2015): for n in the hundreds and thousands the best known packings
  are cut from the cubic close packing, with spheres removed and layers translated into the freed space; random-start
  searches were too coarse to find them. Large n is a constructive problem: crystal plus defects.
* **Densest lattice packings of polytopes** (Betke & Henk 2000) and dense non-lattice packings (Torquato & Jiao 2009;
  the truncated-tetrahedron dimer crystal 207/208, Jiao & Torquato 2011): the crystals that `crystal.py` recomputes.
* **Hard-particle Monte Carlo** (HPMC, Anderson et al. 2016) scales to millions of polyhedra with local moves,
  cell lists and BVHs: the per-move cost is O(neighbours), not O(n).
* **sparrow** (Gardeyn & Wauters 2025, 2D strip packing): fixed-size separation with local relocation by sampling and
  guided-local-search weights; it is the state of the art at hundreds of items. Our earlier bake-off (13 Oct) found
  its compress half weaker than hops at n ≤ 40; at n ≥ 60 a local version (move one piece against its neighbours
  only) is the natural next experiment.

## 7. Recommended pipeline for n ≤ 100

Everything below exists in the repository; switching it on is a policy and environment change.

1. **Seed every case with crystal cuts** (minutes for all 61 problems): `PP_NMAX=100 python3 scripts/crystal_cut.py
   P 100 --insert`. Done today for n = 41–100 (the archive holds these packings; the engine and the publisher ignore
   n > 40 until `PP_NMAX` is raised).
2. **Fill by ascend chains on GitHub Actions**, one job per problem (`.github/workflows/largen.yml`, 20 jobs at a
   time, 4 CPUs each): at each n, three insertions into the best (n − 1)-packing compete with the cut; the best goes
   on. Then import the results (`scripts/import_largen.py`: every packing re-legalized here, kept only if smaller).
3. **Polish with the engine** at `PP_NMAX=100`, policy `tightener: fast`, move `perturb` weighted like hops at
   n > 40 (0.2–0.3), hops, cascades from n ± 1; every case to 10 attempts, then by the usual effort score.
4. **Compute**: GitHub allows 20 concurrent jobs of up to 6 h (4 CPUs each) on public repositories, free: up to
   480 job-hours (1,920 CPU-hours) a day, 6× the hourly search's 4 jobs × 50 min × 24 runs = 80 job-hours.
5. **Publish** as now: exact certification takes 0.5–9 s per packing at n = 50–90 (`certify_general.py`), so
   n ≤ 100 adds about an hour of certification; the site needs `PP_NMAX` and its chart axes widened.

**Cost.** With today's settings the fill n = 41–100 takes 2–3.5 hours of one 4-CPU job for most problems and
6–9 hours for the four slowest solids: about 240 job-hours for all 61 problems, 12 hours on 20 concurrent jobs. The
fast tightener should roughly halve that (tightening is 60–90% of a step and 2–10× faster). Polishing 3,660 new cases
to 10 attempts each at 1–3 minutes per attempt is another ~1,000–1,800 CPU-hours, about a day of the 20 jobs.
So n ≤ 100 for every problem is a matter of one to two days of free GitHub compute, not weeks.

## 8. Tried and set aside

* **Hierarchical (product) constructions**, s(ab) ≤ s(a)·s(b) by substituting a packing of b containers into each
  of a container-shaped blocks: for the 36 self-packing problems the bound at n = 60–100 is 15–35% worse than a
  density extrapolation of the n = 40 records; only special cases (8 × 8 triangular prisms = 4³, 10 × 10 truncated
  tetrahedra) are competitive.
* **Generic 3D lattices for prisms**: the densest 3D lattice of a prism is degenerate (any shear of the stacking is
  as dense); the optimiser often returned a sheared stacking whose cut is poor (40 hexagonal prisms in a cube 6.07
  vs 5.196 for straight stacks). Hence the columnar crystals.
* **Shorter morph** (section 4).

## Sources

* U. Betke, M. Henk, *Densest lattice packings of 3-polytopes*, Comput. Geom. 16 (2000): [arXiv math/9909172](https://arxiv.org/abs/math/9909172)
* S. Torquato, Y. Jiao, *Dense packings of the Platonic and Archimedean solids*, Nature 460 (2009): [arXiv 0908.4107](https://arxiv.org/abs/0908.4107); *Dense packings of polyhedra: Platonic and Archimedean solids*, PRE 80 (2009): [arXiv 0909.0940](https://arxiv.org/abs/0909.0940)
* Y. Jiao, S. Torquato, *A packing of truncated tetrahedra that nearly fills all of space and its melting properties*, J. Chem. Phys. 135 (2011): [arXiv 1107.2300](https://arxiv.org/abs/1107.2300)
* J. de Graaf, R. van Roij, M. Dijkstra, *Dense regular packings of irregular nonconvex particles*, PRL 107 (2011): [arXiv 1107.0603](https://arxiv.org/abs/1107.0603)
* A. Gensane, *Dense packings of equal spheres in a cube*, Electron. J. Combin. 11 (2004): [R33](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v11i1r33)
* A. Joós, *On limits of dense packing of equal spheres in a cube*, Electron. J. Combin. 22 (2015): [arXiv 1503.07933](https://arxiv.org/abs/1503.07933)
* J. A. Anderson, M. E. Irrgang, S. C. Glotzer, *Scalable Metropolis Monte Carlo for simulation of hard shapes*, Comput. Phys. Commun. 204 (2016): [arXiv 1509.04692](https://arxiv.org/abs/1509.04692)
* J. Gardeyn, T. Wauters, sparrow, 2D irregular strip packing (2025): [arXiv 2509.13329](https://arxiv.org/abs/2509.13329), [code](https://github.com/JeroenGar/sparrow)
* Earlier study in this repository: [docs/SEARCH_METHODS_REVIEW.md](SEARCH_METHODS_REVIEW.md)
