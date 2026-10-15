# How to search much more efficiently: literature review, our own data, and a bake-off (13 Oct 2026)

This note records a three-hour study done after the second phase stopped (13 Oct 2026, 08:10). It has four parts:
what the literature on 2D and 3D packing does, what our own 69,000 logged attempts say about what works, a direct
bake-off of new moves against the production moves, and the recommendations that follow.

**Short answer.** The bake-off (7,869 attempts, 63 CPU-hours on GitHub Actions and the cloud machine)
found a clear winner for *discovery*: **symmetric seeding** — the soft-to-rigid start run inside a random cyclic
symmetry of the container, then tightened freely. Across all 20 prism and antiprism problems it gives 3.3× the gain
per CPU-hour of the production hop and 1.9× that of fresh starts, and it found the best packing in 21 of the 31 cases
that improved by more than 0.1% (13× the hop's gain per CPU-hour in round A). It broke the dodecagonal-antiprism
plateau by up to 21.6% and found exact structures (12 pentagonal prisms at φ², 8 truncated octahedra at 2.5). It is
not universal: on the young Archimedean and Catalan records plain hops from the record are still 2–3× better per
CPU-hour, and nothing beat the mature Platonic records. The efficient search is therefore symmetric seeding inside
an adaptive portfolio that spends CPU where the measured gain per second is highest (section 4). Two literature
ideas lost clearly in our setting: fixed-size "squeeze" separation used as a polisher, and Nakajima's quarter
start. As a by-product, **127 records improved** (median −1.05%, all certified exactly), 79 of them through symmetric
starts.

## 1. What our own data says (69,195 logged attempts, 123 CPU-hours on the cloud machine)

Source: `state/attempts.jsonl` (every cloud attempt of both phases; the laptop and GitHub Actions only report the
attempts that set a record, so they enter only through the record origins). Script:
`docs/search_review/logstats.py`.

| move | attempts | improved | rate | s / attempt | improvements / CPU-h |
|---|---:|---:|---:|---:|---:|
| hop (from the best or a pool packing) | 34,269 | 2,588 | 7.6% | 7.3 | 35 |
| ascend (from the n−1 record) | 8,384 | 1,022 | 12.2% | 8.8 | 44 |
| reinsert (1–3 pieces into holes) | 6,858 | 429 | 6.3% | 6.4 | 35 |
| fresh (random start) | 6,861 | 127 | 1.9% | 7.8 | 6 |
| descend (from the n+1 record) | 5,766 | 112 | 1.9% | 2.0 | 33 |
| tighten (re-tighten a flagged record) | 394 | 216 | 55% | 16.7 | 118 |

Findings:

1. **Almost all progress is local.** 58% of the final records come from hops, and hops from the record itself
   succeed 8.8% of the time against 4.0% from pool packings. Small hops win: an arrangement change below 0.06 piece
   edges succeeds 12% of the time, above 0.25 edges 0.7%. Focused hops (only a cluster shaken) succeed 9.3% against
   5.5% for global ones. The search is, in effect, a local search around each record.
2. **It saturates.** The chance that the next attempt improves a case is 20% right after an improvement and falls to
   1.4% after 40–80 failures and 0.26% after 80. Improvements also shrink (median relative gain 7e-4 right after an
   improvement, 1.4e-4 after 10+ failures). After ~10 attempts per case the production moves mostly polish the basin
   they are in.
3. **Fresh starts are the only source of new basins, and they are weak.** 1.3% success in the first phase, 0.8% for
   n ≥ 29, 6 improvements per CPU-hour against 35–44 for the local moves; but when a fresh start does win, its gain is
   5–10 times larger than a hop's (mean 8e-3).
4. **A quarter of the compute ends in the gate.** 46% of all attempts are discarded after the soft phase (raw size
   more than the case's gate above the record) and never tightened: 25% of all CPU time. The soft-phase size
   predicts the final size only moderately (Spearman 0.56; 0.73 for fresh starts). The bake-off (section 3) shows
   that a different gate would not recover much.
5. **Cross-n information is valuable.** Ascend succeeds 7.9% of the time when the n−1 record has improved since the
   case's own last improvement, against 3.7% otherwise; descend 2.9% against 1.4%. 141 final records (7%) are just
   the (n+1)-record minus one piece: in those cases every direct search at n lost to a trivial deletion.
6. **Our records are almost never symmetric.** Testing every symmetry of the container (tolerance 1e-3 edges):
   91% of all 2,145 records have no symmetry at all, and the share with any symmetry is 35% for n ≤ 8, 7% for
   n = 9–16, 2% for n = 17–28 and 1% for n = 29–40. For n ≥ 9 the median record maps 0% of its pieces onto pieces
   under any non-trivial container symmetry, so this is not a matter of a few rattlers. By contrast 69% of the
   best-known packings of N ≤ 40 circles in a square, and 64% in a circle, have non-trivial symmetry (Packomania).
   Either symmetric optima are rare for these solids, or our unbiased search essentially never reaches them. The
   bake-off (section 3) answers this for prisms and antiprisms: it is the second.

## 2. What the literature does

Three separate reviews (2D packing; 3D polyhedra; global optimisation and search allocation) read the primary
sources. The condensed lessons, with the evidence that supports each:

### 2.1 Optimise feasibility at a fixed size, not "energy + pressure"
* **sparrow** (Gardeyn & Wauters 2025, the current state of the art for 2D irregular strip packing) never puts the
  container size in the energy. It fixes the strip, removes all overlap ("separate"), then shrinks by 0.1% (explore)
  or 0.05%→0.001% (compress, always from the best feasible). Escapes come from **guided-local-search pair weights**
  (a colliding pair's weight ×(1.2 + 0.8·overlap/max) per round, ×0.95 otherwise) and from **relocating a colliding
  piece to the best of many sampled poses anywhere in the container**. It matched or beat every best-known benchmark
  solution, some by wide margins.
* **Lai, Hao et al.** (PBTS, IJOC 2023: 156 improved circle-in-square and 66 sphere-in-cube records; IDTS 2022;
  HAMSP 2025) use the same pattern: fixed size, threshold acceptance tuned to a fixed acceptance ratio, hybrid
  perturbations, and an "optima-exploitation" step that squeezes slightly *below* the best size and repairs with tiny
  kicks. Their ablation calls that step crucial.
* **Egeblad et al.** (2007, 2D and 3D nesting): GLS over pair-overlap features, exact 1D minimisation of the overlap
  along a translation or rotation.
* A square-packing calibration (Daniel, n = 292) found that loosening the container 2% before a soft squeeze *lost*
  the starting arrangement — our hop expands by 1–5% before shaking.

### 2.2 Symmetry is the biggest known accelerator for small n
* Point-group-constrained random starts (PyXtal): LJ38 ground state found 278 times in 10,000 symmetric starts and
  0 times in 10,000 unconstrained ones; LJ55 73 vs 0.
* Symmetrisation inside basin hopping (Oakley, Wales & Johnston 2013): 9× to over 100× faster on multi-funnel
  clusters (LJ38, LJ75, LJ98).
* AIRSS (random structure search) uses random symmetric starts as its default because it "dramatically reduces" the
  number of attempts.
* AlphaEvolve's 11-hexagons-in-a-hexagon construction was improved by hand by making it exactly symmetric
  (3.931 → 3.9245).
* Packomania: 64–69% of circle records with N ≤ 40 are symmetric; the commonest group is a single mirror, then C2;
  the full container group is rare.

### 2.3 Populations and recombination
* Population basin hopping (Grosso, Locatelli & Schoen): a child replaces its *most similar* population member if
  better (dissimilarity = sorted distances from the centre); 10/10 successes where monotonic basin hopping had 7/50
  (LJ98) and 5/500 (Morse M79).
* Cut-and-splice crossover (Deaven & Ho): cut two parents by the same random plane, join halves, relax. Combinatorial
  swaps beat continuous displacement in the unequal-circles contest won by Addis, Locatelli & Schoen, who also removed
  the rattlers during optimisation and reinserted them afterwards.
* Growth from N−1 explains about 75% of Lennard-Jones global minima; the rest need rearrangement (our ascend/descend).

### 2.4 Projection methods
* Divide-and-concur / RRR (Elser, Gravel, Kallus): a feasibility search in replica space with adaptive pair weights;
  on disks in a square (n = 2–200) it matched 143 of 197 records and improved 38; it found the tetrahedron dimer
  packing 15/100 times. Untested on polyhedra in a finite container: high potential, high cost.

### 2.5 Throughput and allocation
* The 2025–26 square-packing records came from tens of thousands of cheap GPU annealing chains followed by a separate
  SLP / contact-Newton polish (about one record-basin hit per 40 minutes at n = 55); "surgery" seeds (delete, graft)
  produced the n = 108 gain.
* Max-k-armed bandits (Streeter & Smith), ALNS operator weights, successive halving / Hyperband: allocate effort by
  the probability of beating the best, not by average quality.
* AlphaEvolve's "packing in a dilate" problem is exactly ours (cubes: improved 11 cubes 2.912 → 2.8945). The evolved
  program is a large, well-tuned operator portfolio (slip and shear planes, rigid sub-cluster moves, "quantum leaps",
  orientation snapping, structured starts, periodic squeezes) inside simulated annealing; nothing exotic.
  ImprovEvolve (2026) evolved generate/improve/perturb functions inside monotonic basin hopping, with a perturbation
  strength restarted on a geometric schedule every round, and set several hexagon records.
* Global MINLP solvers (Berthold, Kamp, Mexi, Pokutta & Pólik 2026; all 750 Platonic-in-Platonic cases n ≤ 30) give
  feasible solutions, but with median optimality gaps of 14–33% (their lower bounds beat the volume bound only for
  n ≤ 2): useful seeds and baselines, not a competitive search for n up to 40.

### 2.6 Yohei Nakajima's latest work
* *When does hardening help?* (5,200 packings, 67 instances): the soft-to-rigid path wins when the compressed balls
  land near the optimum's "scaffold" (scaffold fidelity predicts the hardening gap, ρ = −0.56 to −0.76); a good
  scaffold transplanted under the morph reaches the good basin 8/8 times; starting the morph nearly rigid ("quarter")
  matched or beat the full ball-to-shape path in every case tested.
* *quantum-harden-packing*: sample scaffolds on a discretised contact graph with a QUBO solver (quantum or classical)
  and warm-start the hardening from them. No results yet.
* In his soft-to-rigid repository he suggests a noise schedule that peaks at orientation lock-in rather than
  decaying to zero before it.
* Lesson for us: the scaffold (which contact graph the balls settle into) decides the basin; generating *better
  scaffolds* (symmetric, lattice-like, combinatorially sampled) is where the leverage is.

## 3. Bake-off

Code: `scripts/bench_methods.py` (methods), `src/sim.js` (`symmetrize`, `squeeze`), `.github/workflows/bench.yml`
(GitHub Actions, 6 jobs × 4 cores × 40 min per round). Raw results: `docs/search_review/bench/`. Every attempt is
tightened fully with the production tightener (no gate, no early abort), so every method is judged on the final
size it reaches and on the CPU time it costs. "Gain" is log(record / s) when the attempt beats the record, else 0.

Methods:

* **fresh** — the production random start (balls → soft-to-rigid → legalize).
* **symfresh** (new) — the same, but during the soft phase the configuration is held symmetric under a random
  cyclic subgroup ⟨g⟩ of the container's symmetry group: the pieces form orbits of |g| copies (c = g c₀,
  R = g R₀ m, with m a mirror symmetry of the piece when g is improper) plus up to a few pieces on the fixed axis or
  plane of g. The symmetry is imposed by projection after every step; the tightening afterwards is free, so the
  result need not stay symmetric.
* **symfresh25** — symfresh starting the morph at softness 0.25 (Nakajima's "quarter" start).
* **hop** — the production "gentle" hop from the record (or a pool packing).
* **squeeze** (new) — fixed-size separation in the style of sparrow / HAMSP: the record's container shrunk by
  0.1–1%, overlap removed at fixed size by weighted overlap descent with guided-local-search pair weights and
  relocation of the worst piece to the best of 300 sampled poses.

### Round A: 24 cases of the three new families, n = 9–30 (1,364 attempts, ~16 CPU-hours)

| method | attempts | beat the record | mean s | gain / CPU-h | gains > 0.1% / CPU-h |
|---|---:|---:|---:|---:|---:|
| fresh | 271 | 11.1% | 48 | 0.080 | 7.1 |
| hop | 273 | 38.8% | 24 | 0.039 | 13.1 |
| squeeze | 274 | 40.1% | 49 | 0.0014 | 0 |
| **symfresh** | 273 | 13.2% | 49 | **0.310** | 8.8 |
| symfresh25 | 273 | 9.2% | 52 | 0.073 | 6.0 |

By family (excluding the two dodecagonal-antiprism cases, whose records were known to be weak):

| family | fresh | hop | squeeze | symfresh | symfresh25 |
|---|---:|---:|---:|---:|---:|
| Archimedean, gain / CPU-h | 0.017 | **0.050** | 0.0003 | 0.014 | 0.023 |
| Catalan, gain / CPU-h | 0.022 | **0.031** | 0.002 | 0.014 | 0.025 |
| prisms & antiprisms, gain / CPU-h | 0.043 | 0.039 | 0.001 | **0.527** | 0.049 |

Largest single gains (all symmetric starts): 21 dodecagonal antiprisms in themselves 4.43609 → 3.67457 (−17.2%),
9 of them 2.92616 → 2.61027 (−10.8%), 12 pentagonal prisms in themselves 2.77208 → 2.61803 = φ² (−5.6%, found
twice, both times under a 5-fold axis), 24 octagonal antiprisms in a cube −2.4%, 27 pentagonal prisms in a cube
−1.5%, 18 octagonal prisms in a cube −1.3%. A follow-up on the dodecagonal-antiprism plateau (s = 4.43609 for every
n = 18–39) found n = 18 → −21.6% and n = 30 → −5.0% within 11 symmetric attempts; hop and fresh found nothing there.

Other observations:

* **squeeze** "beats" the record 40% of the time, but its mean gain is 5e-5 and it never gained more than 0.1%:
  it is a polisher, and the records are already polished (re-running the tightener on the 24 records changes them
  by at most 1e-4, usually 0). As a search move it is the worst of the five.
* **Nakajima's quarter start** loses to the full ball-to-shape path overall (0.073 vs 0.310) and draws on
  Archimedean and Catalan cases.
* **Gate.** 90% of hop wins had a soft-phase size within 0.19% of the record; only 10% of hops land more than 0.5%
  above it, and they cost 1% of hop time, so the hop gate is not a lever. For fresh and symmetric starts the
  production gate (skip tightening when the soft-phase size is > 3% above the record) skips 42–53% of the
  attempts, saves about 18% of their time and loses 12–14% of their wins: roughly neutral. The 25% of production
  time spent on gated attempts is the price of the soft phase, not waste that a different gate would recover.
* On these young cases (≈10 attempts each) hop still beats the record 39% of the time: the new families are far
  from converged, and plain hops remain the most efficient polisher there.

### Round B: mature Platonic cases, n = 8–14 (3,588 attempts, ~16 CPU-hours)

Five Platonic-in-itself problems at n = 8–14, whose records come from hundreds of attempts and from the literature.
Nobody beats them, except one symfresh25 attempt that took 13 cubes in a cube from 2.97662 to 2.956145 (the known
2.956+ structure). Re-finding the record is about equally likely from fresh and symmetric starts (median gap to the
record 5.0% fresh, 6.0% symfresh); symmetric starts re-found the 10- and 11-cube records, which fresh starts missed.
Symmetry is not a universal accelerator for these solids: it pays where the optimum is a symmetric stack (prisms,
antiprisms) and is neutral elsewhere.

### Round C: large n (33–39) of the new families, and mature Platonic cases n = 12–20 (699 attempts, ~16 CPU-hours)

Adds **symchain** = a symmetric start followed by three hops from its result.

| | fresh | hop | symfresh | symchain |
|---|---:|---:|---:|---:|
| new families, n = 33–39: beat the record | 5.9% | **78.5%** | 4.7% | 11.2% |
| new families, n = 33–39: gain / CPU-h | 0.0028 | **0.020** | 0.0079 | 0.0079 |
| new families, n = 33–39: mean s per attempt | 112 | 76 | 94 | 319 |
| mature Platonic n = 12–20: beat the record | 0 / 85 | 0 / 80 | 0 / 90 | 1 / 91 |

At n = 33–39 the new-family records are so young that hops from them succeed 78% of the time; there plain hops are
2.5× better per CPU-hour than any start, and symmetric starts are still 2.8× better than fresh ones. The
symmetric advantage on prisms is concentrated at n ≤ 30 and on plateaus; at n = 33–39 it shows up only through
symchain (33 octagonal prisms in a cube −1.2%). Chaining hops onto a symmetric start does not change its efficiency.
The mature Platonic records were not beaten by anything (one symchain improvement of 2e-4 on 12 icosahedra in a
dodecahedron).

### Round D: all 20 prism and antiprism problems, n = 6–28 (1,824 attempts, ~11 CPU-hours)

Two random n for each of the 20 problems (40 cases).

| | fresh | hop | symfresh |
|---|---:|---:|---:|
| beat the record | 11.7% | 32.9% | 14.1% |
| gain / CPU-h, all | 0.29 | 0.17 | **0.55** |
| gain / CPU-h, in themselves | 0.20 | 0.29 | **0.44** |
| gain / CPU-h, in a cube | 0.35 | 0.09 | **0.61** |
| cases where it found the best (of 31 improved by > 0.1%) | 5 | 5 | **21** |

### Small n of the Archimedean and Catalan solids (n = 5–8, 12 cases, 114 attempts, local)

Hops beat the record most often (10.5%), but the one large gain came from a symmetric start: 8 truncated octahedra
in a truncated octahedron 2.56966 → exactly 2.5 (found twice, under a 3-fold axis with two pieces on it).

### By-product: new records

Every attempt that beat a record was merged into the archive (re-legalized by `engine.harvest`) and certified
exactly by the usual pipeline: **127 records improved** (92 prisms/antiprisms, 18 Archimedean, 15 Catalan,
2 Platonic; median gain 1.05%), 79 of them from symmetric starts (directly or by deleting a piece from a symmetric
n+1 record), 33 from hops, 14 from fresh starts. Largest: dodecagonal antiprisms in themselves n = 18
4.43609 → 3.47818 (−21.6%), n = 19–22 → 3.56680 (−19.6%), n = 9 −10.8%, n = 16 → exactly 3 (−10.2%);
dodecagonal antiprisms in a cube n = 18 −10.3%; 10 dodecagonal prisms in a cube −8.5%; 6 hexagonal prisms in a cube
−8.2%; 12 pentagonal prisms in themselves → φ² = 2.61803 (−5.6%); 8 truncated octahedra in themselves → 2.5
(−2.7%); 13 cubes in a cube 2.97662 → 2.956145 (the known structure).

## 4. Recommendations

### The winner: symmetric seeding inside an adaptive, family-aware portfolio

No single method from the literature wins everywhere, and the bake-off says why: the moves differ by an order of
magnitude in gain per CPU-hour, and the ranking flips between families. The efficient search is therefore:

1. **Symmetric seeding as a standing move (the discovery engine).** On prisms and antiprisms it produced 3.3×
   (round D, all 20 problems) to 13× (round A) the gain per CPU-hour of hops and 1.9–12× that of fresh starts, and
   it is the only move that broke the
   dodecagonal-antiprism plateau (up to −21.6%) and found exact closed forms such as 12 pentagonal prisms at φ².
   Elsewhere it matches fresh starts as a source of new basins (and it re-found the 10-, 11- and 13-cube structures).
   It replaces most of the fresh starts.
2. **Hops from the record stay the polisher.** On the young Archimedean and Catalan cases hops are still 2–3×
   better per CPU-hour than any start, and at n = 33–39 they beat the record 78% of the time: those cases simply
   need more hops. Small (arrangement change < 0.06 edges) and focused hops from the record are the best of them.
3. **Allocate CPU by measured gain per CPU-second, per (family, case, move).** A discounted bandit (Thompson
   sampling on the log-gain per second, prior = the family statistics above) chooses the move and the case. Add the
   cascade (an improvement at n raises ascend at n+1 and descend at n−1, which double their success) and the streak
   effect (gain per CPU-hour is 35× higher right after an improvement than after 80 failures). Plateaus in s(n)
   (equal records for 4+ consecutive n: ap12, pr12, pr8, ap8) are a cheap weakness detector: give them symmetric
   starts first.
4. **Drop what lost.** The fixed-size squeeze as a polisher (no gain above 0.1% in 274 attempts) and Nakajima's
   quarter start (a quarter of the full path's gain per CPU-hour) do not enter the portfolio.

### Engineering that multiplies it

5. **Orbit-reduced symmetric simulation.** Simulate only orbit representatives (pair classes fall by |g|): the soft
   phase, 64% of a symmetric attempt, becomes 2–4× cheaper.
6. **Richer symmetry.** Enumerate the container's subgroups (dihedral and mirror groups, not only cyclic ones) and
   the orbit types with special positions whose orientation is compatible with the stabiliser; learn the weights
   per family (5-fold axes for pentagonal prisms, 2- and 4-fold axes for the cube container). Add **symmetric
   ascend** (add a whole orbit to the (n − |g|)-record) and **symmetrise-and-retighten** for near-symmetric records.
7. **Throughput.** The soft phase is embarrassingly parallel; the 2025–26 square-packing records came from 10⁴–10⁵
   cheap GPU chains followed by a separate polish. A batched (GPU or vectorised) soft phase is the largest raw
   multiplier left (10–100×), at the largest engineering cost.

### Research bets (not yet worth production time)

* RRR / divide-and-concur at fixed size (best finite-packing evidence in the literature, untested on polyhedra).
* A full sparrow explore/compress loop with sampled relocation (our squeeze was only its compress half).
* Cut-and-splice crossover between pool members, with the soft-to-rigid morph as the repair step.
* Scaffold sampling (Nakajima's QUBO idea): symmetric seeding is a cheap version of "start from a good scaffold";
  a discrete lattice/contact-graph sampler is the general one.
* An LLM-evolved perturb/improve loop (ImprovEvolve style) scored over many cases at once.


## Sources

* sparrow: Gardeyn & Wauters, arXiv 2509.13329, https://arxiv.org/abs/2509.13329 ; code https://github.com/JeroenGar/sparrow
* PBTS (Lai, Hao, Xiao, Glover, IJOC 2023): https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalJOC2023.pdf
* IDTS (Lai et al., EJOR 2022): https://leria-info.univ-angers.fr/~jinkao.hao/papers/Laietal2021EJOR.pdf
* HAMSP (Lai et al., COR 2025): https://leria-info.univ-angers.fr/%7Ejinkao.hao/papers/LaietalCOR2025.pdf
* Egeblad, Nielsen & Odgaard, EJOR 2007: https://ideas.repec.org/a/eee/ejores/v183y2007i3p1249-1266.html
* Square-packing methods survey (2026): https://jlevy.github.io/squares/papers/square-packing-methods-survey.html ; https://kingbird.myphotos.cc/packing/squares_in_squares.html
* PyXtal symmetric starts: https://arxiv.org/abs/1911.11123 ; AIRSS: https://arxiv.org/abs/1101.3987
* Oakley, Wales & Johnston, symmetrisation in basin hopping (PCCP 2013): https://pubs.rsc.org/en/content/articlehtml/2013/cp/c3cp44332a
* Population basin hopping (Grosso, Locatelli & Schoen): https://optimization-online.org/wp-content/uploads/2005/02/1056.pdf
* Addis, Locatelli & Schoen, unequal circles: https://optimization-online.org/wp-content/uploads/2006/03/1343.pdf
* Deaven & Ho, cut-and-splice GA: https://arxiv.org/abs/mtrl-th/9506004
* Gravel & Elser, divide and concur: https://arxiv.org/abs/0801.0222 ; Kallus, Elser & Gravel: https://arxiv.org/abs/1003.3301
* Torquato & Jiao, adaptive shrinking cell: https://arxiv.org/abs/0909.0940 ; SLP: https://arxiv.org/abs/1008.2747
* Chen, Engel & Glotzer, tetrahedra: https://arxiv.org/abs/1001.0586
* Streeter & Smith, max k-armed bandit: https://www.cs.ubc.ca/~hutter/EARG.shtml/earg/papers06/mstreeter_cp_2006.pdf ; Hyperband: https://arxiv.org/abs/1603.06560
* AlphaEvolve: https://arxiv.org/abs/2506.13131 ; Mathematical exploration and discovery at scale: https://arxiv.org/abs/2511.02864 ; problems repository: https://github.com/google-deepmind/alphaevolve_repository_of_problems
* ImprovEvolve: https://arxiv.org/abs/2602.10233 ; ShinkaEvolve: https://arxiv.org/abs/2509.19349
* Berthold, Kamp, Mexi, Pokutta & Pólik 2026: https://arxiv.org/abs/2605.04850 ; data https://github.com/DominikKamp/Packing
* Packomania: http://www.packomania.com/ ; Friedman's Packing Center: https://erich-friedman.github.io/packing/
* Nakajima: https://github.com/yoheinakajima/soft-to-rigid-packing ; https://yoheinakajima.github.io/when-hardening-helps/ ; https://github.com/yoheinakajima/quantum-harden-packing ; https://x.com/yoheinakajima/status/2108709889602388252

