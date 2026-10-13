# Part IV — The second phase: Archimedean, Catalan, prisms and antiprisms (12–13 October 2026)

This part records the second phase of the project. It covers everything from Alejandro's request on Monday 12 October at
16:53 to the end of the night search on Tuesday 13 October at 08:10, and the final publish and analysis after it. As in
Parts I–III, all times are Paris time (CEST). Chapter 18 and Appendix G are generated from the archive, the logs and the
record files by `scripts/report_phase2.py`; the other chapters were written from the session record and the code.

## 13. Summary of the second phase

On 12 October at 16:53 Alejandro asked to generalize the work to new families of solids, each packed only in itself:
* every **Archimedean** solid (13) and every **Catalan** solid (13);
* the regular **prisms and antiprisms** over the triangle, square, pentagon, hexagon, octagon and 12-gon, in themselves
  **and** in a cube;
* n = 2 to 40;
* the viewer organized into three families (Platonic, Archimedean/Catalan, prisms);
* the same resources as before (the cloud machine, the laptop and the "medium" GitHub Actions search);
* first one, then ten attempts on every case.

Four prism problems are Platonic problems in disguise. The engine never searched them, and their alias tabs in the
viewer were removed at his request at 18:04:
* the square prism with unit edges is the cube, so square prisms in a square prism and square prisms in a cube are
  both cubes in a cube;
* the triangular antiprism is the octahedron, so triangular antiprisms in a triangular antiprism and in a cube are
  octahedra in an octahedron and octahedra in a cube.

That left **46 new problems and 1,794 cases** (46 × 39): 13 Archimedean, 13 Catalan and 20 prism and antiprism
problems.

What came out of it:

* **The method was generalized** to solids without an insphere (the r-rounding, chapter 15.2). Contact geometry was made
  fast for solids with up to 120 vertices and 120 faces (Gauss-map pruning of the separating axis test). The engine
  learned families, sharding across machines and a minimum number of attempts per case.
* **The exact certifier was generalized** from ℚ(√2, √5) to any real number field. Every one of the 41 solids now has
  exact coordinates in a field of degree 1 to 8 (plus a common square-root scale for the snub solids and their duals),
  found by integer relation detection and proved by an exact self-check. `certify_general.py` proves containment and
  disjointness with rigorous interval arithmetic.
* **Every case has a certified record.** All 1,794 cases had a packing by 21:54 on 12 October. The final publish on 13
  October certified every record again after the night's improvements (chapter 18). All 351 Platonic records also pass
  the new certifier.
* **The night search** (13 Oct 01:38–08:10, cloud + laptop + GitHub Actions) made 16,016 attempts and 3,940
  improvements across 1,511 of the 1,794 cases. 1,201 cases ended with at least 10 attempts.
* **A website**, polyhedrainpolyhedra.wiki, was built (chapter 19). It has:
  * the explorer for all three families and an index of every construction;
  * method and certification pages linked to the code;
  * an in-browser checker and GitHub issue forms for submissions;
  * a GitHub workflow that certifies submitted packings exactly and records accepted ones with the contributor's
    credit.

## 14. Timeline of the second phase

| time | event |
|---|---|
| 12 Oct 16:53 | Alejandro asks for the Archimedean/Catalan and prism families, the three-family viewer, the same compute, and 1 then 10 attempts per case. |
| 17:15 | First commit of the phase: 36 new solids (`polyhedra.py`), the generalized simulator and kernel, the engine extended to 46 new problems. The search starts on the cloud machine. |
| 17:24 | 240 of 1,794 cases have a packing. |
| 17:31 | Records and viewer for the new families: float-verified records (`verify_general.py`) and the family selector. |
| 17:57 | Tightening gets a stop rule: large solids were running the sequential LP to its time limit for tiny gains. |
| 18:04 | Alejandro asks to drop the four prism problems that are Platonic problems, and whether the exact certifier is generalized. The four alias tabs are removed. |
| 18:08 | GitHub Actions run 1 is merged: 1,647 attempts, 1,091 new bests. Coverage jumps to 1,312. |
| 18:19 | The general exact certifier is committed. Exact number fields for all 41 solids. All 1,317 records of the new families published so far are certified. |
| 18:27, 18:46 | Attempts made on the laptop and in GitHub Actions now count toward the 10-attempt goal. The laptop reports per-host totals; Actions jobs report increments. |
| 18:30 | Viewer artifact version 22. |
| 19:14–19:35 | Coverage 1,530, then 1,622, then 1,646. The hourly publish certifies all 1,925 records (version 23 of the viewer). |
| ≈19:40–20:32 | The cloud machine pauses and restarts. The two cloud workers are down for about 50 minutes (no cloud attempt is logged between 19:39 and 20:32). GitHub Actions run 3 continues meanwhile. The 10-minute cycle restarts the supervisor at 20:32. |
| 20:41 | Coverage 1,711. 2,050 records, all certified (viewer version 24). |
| 20:49–21:24 | The link to the laptop drops on the longest bounded runs. The laptop is switched to a "fast mode": smallest cases, no fill phase. |
| 21:36 | Second restart of the cloud machine. Workers back within a minute. |
| 21:44 | Alejandro asks to finish the last cases, stop, and build polyhedrainpolyhedra.wiki with contribution routes and links to every construction. |
| 21:54 | The last cases (pentagonal hexecontahedra, n = 39 and 40) are filled: **1,794 of 1,794**. |
| 21:57 | `state/STOP`. Workers stop; no new Actions runs. |
| 22:12 | The website and the contribution pipeline are pushed, and the site is live on GitHub Pages. |
| 22:24 | Actions run 5 is merged (1,468 attempts, 497 new bests). |
| 22:31 | Final publish of the evening: 2,145 records (351 Platonic + 1,794), all certified exactly. |
| 22:35 | Alejandro: finish for the night, continue in the morning. Links point at the GitHub Pages address until the domain is set up. |
| 13 Oct 01:35 | Alejandro asks to resume on the laptop and with the medium GitHub search, only for the three new families, with a report every 6 minutes. He also asks for an opacity control for the pieces. Another agent is deploying the site to the domain. |
| 01:37–01:38 | Opacity slider pushed. Search restarted: cloud workers, laptop (bounded runs), Actions run 6. |
| 01:42–01:47 | The website agent pushes the domain configuration while the cycle is pushing a checkpoint. A pull with rebase resets the attempt log; the log is rebuilt and the commits merged (chapter 17). |
| 02:13 onwards | The website agent's pull requests (#3, #4, #8–#11) are merged into `main` alongside the search checkpoints. |
| 02:29–08:08 | Actions runs 6–12 merged hourly (between 1,367 and 1,795 attempts each). Reports every 6 minutes. |
| 03:04 | The laptop's fast mode is restricted to n ≤ 20. Its attempts per report go from about 16 to 187. |
| 06:54, 07:23 | Laptop cap lowered to n ≤ 14 for speed, then raised to n ≤ 17 for yield. |
| 07:37 | Alejandro: stop after run 12, update the report with a thorough analysis. |
| 08:08–08:10 | Run 12 merged (1,598 attempts, 221 new bests). Search stopped (`state/STOP`). |
| 08:10 onwards | Final publish: every improved record rebuilt and certified exactly. Then this part of the report. |

## 15. Generalizing the method

### 15.1 The solids

`polyhedra.py` builds the 36 non-Platonic solids in 60-digit arithmetic (mpmath):

* **Archimedean solids**:
  * the 11 non-snub solids from their classical coordinates (permutations and sign patterns);
  * the snub cube and the snub dodecahedron by Wythoff's construction, as the orbit of one point under the rotation
    group (O or I). The point is chosen by Newton's method so that the three Wythoff rotations move it by the same
    distance.
  * All are scaled to unit edge.
* **Catalan solids**: the canonical duals of the unit-edge Archimedean solids, reflected in their common midsphere. A face
  with unit normal m at distance h becomes the vertex (r<sub>m</sub><sup>2</sup>/h)·m. Every Catalan solid therefore has
  an insphere, and its size is fixed by the Archimedean solid it comes from. The measure for Catalan problems is the
  ratio of sizes of the same canonical solid.
* **Prisms and antiprisms**: the regular prisms over the 3-, 5-, 6-, 8- and 12-gon and the regular antiprisms over the
  4-, 5-, 6-, 8- and 12-gon, with all edges 1. The square prism and the triangular antiprism are the cube and the
  octahedron.
* **Faces** are derived from the convex hull and then checked:
  * vertex, edge and face counts, and Euler's formula;
  * equal edges (Archimedean solids, prisms, antiprisms) or equal face distances (Catalan solids);
  * planarity, and that every face plane supports the solid.
* **Output**: the floats go to `src/solids.json` (with the Platonic solids from `solids.py`) and 50-digit coordinates to
  `src/solids_hp.json`.

### 15.2 Soft shapes without an insphere: the r-rounding

Nakajima's shape (1 − r/ρ)·P ⊕ B(r) needs a ball touching every face. Platonic and Catalan solids have one. Archimedean
solids, prisms and antiprisms do not. For them the soft shape is the **r-rounding**:

  S_r = (P ⊖ B(r)) ⊕ B(r),

the union of all balls of radius r inside P.

* **Its core** P ⊖ B(r) = {x : n<sub>f</sub>·x ≤ h<sub>f</sub> − r} is again a polytope. Faces disappear from it at
  finitely many values of r, and between them every core vertex moves linearly: V(r) = V<sub>0</sub> + r·W.
* **Precomputed intervals**: `polyhedra.cores()` precomputes these intervals ("cores") on a grid of 240 values of r up to
  r<sub>cap</sub> = 0.49 in internal units, where every solid has inradius ½. The simulator reads the core for any r from these
  precomputed intervals.
* **Check tolerance**: the core check at the interval boundaries needed a tolerance of 10<sup>−7</sup>; 10<sup>−9</sup>
  failed at a boundary.
* **Same homotopy**: the r-rounding lies inside P and only grows as r decreases. For a solid with an insphere it equals
  Nakajima's shape, so the search follows one homotopy for all families. The difference is the start: without an
  insphere the r = 0.49 shape is a rounded body (for a prism, a rounded slab), not a ball.
* **In the code**:
  * `sim.js` uses the ball-only shortcut only for tangential solids with r ≥ 0.4999;
  * the default initial container is based on the piece volume for non-tangential pieces.

### 15.3 Contacts for large solids

Overlap depth between cores is computed by the separating axis test. The candidate axes are the face normals of both
pieces and the cross products of their edges. A truncated icosidodecahedron has 120 vertices and 180 edges, and a
disdyakis triacontahedron 120 faces, so testing every edge pair is expensive.

* **Gauss-map pruning** (Gregorius, GDC 2013). An edge pair gives a face of the Minkowski difference only if the arcs of
  the two edges on the sphere of normals intersect. The test on the four adjacent face normals is CBA·DBA < 0,
  ADC·BDC < 0, CBA·BDC > 0. Pruning keeps the test exact and removes most edge pairs.
* **When pruning is used**: `geom.js` decides per solid with a cost estimate (prune when nd²·nv·6 > 2·ne²·20, with nd edge directions, nv
  vertices and ne edges). Separated pairs get exact distances as before; overlapping pairs get the exact
  penetration depth.
* **Python side**: `src/exact.py` gained the same pruned axes. A vectorized NumPy version was slower than the per-pair
  loop for these sizes and was kept unused.
* **Agreement**: the pruned and unpruned tests give the same results on overlapping pairs and never misclassify a pair.
  On separated pairs their "gaps" differ, which is expected, because the pruned set is not meant to maximize the
  separation.

### 15.4 Containers with many faces

The tightest container over translations is a linear program in four variables. For containers with more than 14 faces (20 of the 26
Archimedean and Catalan solids, and the octagonal and dodecagonal antiprisms), `sim.js` now solves it with a two-phase simplex method with Bland's rule
(`lpTranslation`) instead of enumerating vertex combinations. It checks the candidate translation, its negative and
zero.

### 15.5 Tightening and record files

* **Stop rule.** For large solids the sequential LP ran to its time limit for tiny gains. Tightening now stops when 50
  rounds gain less than 10<sup>−7</sup> of the container size (`acc[-51] − min(L, Ln) < 1e-7·L`).
* **Faster record files.** `src/claim.py` gained `make_claim_fast`:
  * it spreads the centres by Newton-like steps on the separating-axis gaps instead of a bisection;
  * it fits the container with HiGHS;
  * it gives every near pair and every wall a clearance of 10<sup>−7</sup> and rounds s up at the 13th decimal.
* **Float check.** `verify_general.py` is the float checker for any pair of solids (face normals plus Gauss-pruned edge
  axes).

### 15.6 The engine

* **Problems and families.** `scripts/engine.py` was extended to 55 problems in four families. The website agent later
  added the remaining 16 Platonic pairs to the table, making 71, but they are not searched.
* **Policy.** The policy file names the active families (`families`) and the attempt goal (`min_attempts`, 10).
* **The scheduler:**
  1. fills every empty case, ascending in n so that "ascend" can build n from n − 1;
  2. brings every case to `min_attempts`, fewest first;
  3. then spends effort where it pays most per piece.
* **Sharding.** Each machine prefers its own problems: `PP_SHARD` k/8 gives cloud workers 0–1, the laptop 2–3 and the
  four Actions jobs 4–7. This spreads the fill phase without coordination.
* **Remote attempt counts.** Exports carry per-case attempt counts:
  * the laptop reports its totals per host (replacing the previous total);
  * Actions jobs report increments.
  * `total_attempts` adds them to the local count, so the 10-attempt goal counts every machine.
* **Fast mode** (`PP_FAST`, chapter 16). The laptop skips the fill phase, re-tightens only small cases, and brings the
  smallest cases (n ≤ `PP_FAST_NMAX`) toward the attempt goal, fewest attempts first, then smallest n.

### 15.7 The general exact certifier

The Platonic certificate worked in ℚ(√2, √5). The new solids need other fields:
* the snub cube needs the tribonacci constant;
* the snub dodecahedron needs a root of x⁶ − 4x⁴ − x³ + 4x² + 2x − 1;
* the octagonal and dodecagonal antiprisms need fields of degree 8.

The general certifier has three layers:

* **`algebraic.py`** (standard library only). Real number fields ℚ(α) given by a minimal polynomial and an isolating
  rational interval, checked with a Sturm sequence:
  * exact arithmetic on coefficient vectors;
  * signs decided by interval evaluation, refining the interval by exact bisection until it excludes 0.
* **`scripts/exact_solids.py`.** For each solid it chooses the field. It then:
  * writes every 60-digit coordinate as a rational combination of powers of α with PSLQ (mpmath);
  * for the snubs and their duals, scales by λ = 1/√D with D in the field;
  * **proves the result** with an exact self-check in ℚ(α): planar supporting faces, a closed surface, all edges 1 or D,
    or an insphere;
  * requires the exact solid to match `src/solids.json` to 10<sup>−12</sup>.

  All 41 solids pass. Their fields have degrees 1 (cube), 2 (28 solids), 3 (2), 4 (6), 6 (2) and 8 (2); the full list
  is on the website's certification page.
* **`certify_general.py`** (standard library only):
  * rotations are R = H(q)/|q|², exactly orthogonal for the stored rational quaternions;
  * vertex enclosures use fixed-point intervals with 170 fractional bits and outward rounding;
  * containment: every vertex strictly inside every face half-space of s·C;
  * disjointness: for each near pair, the best six candidate axes (face normals and Gauss-pruned edge cross products)
    are rounded to rational vectors with denominators up to 10<sup>12</sup>, and one must strictly separate the two
    vertex sets on its interval enclosures;
  * far pairs are handled by an upper bound of the circumradius.

  Floating point only proposes, so a wrong proposal can only make a certificate fail.

How it was tested:
* deliberately broken files (shrunk container, a pushed piece, coincident pieces, a piece outside) are rejected;
* at 18:19 all 1,317 records published so far certified;
* after the evening publish all 351 Platonic records were certified again by the general certifier (all pass), on top
  of their original certificates from `certify_exact.py`.

Three bugs found while building this:
* `sympy` was missing in the cloud machine (installed);
* `sturm_count` failed on the cube's degree-1 polynomial (`_trim` of an empty list, fixed);
* the core-check tolerance (15.2).

## 16. Compute and operations

* **The cloud machine** (2 cores) ran the supervisor (`run_forever.sh`): two workers plus a publisher every 90 minutes.
  The 10-minute cycle also started an hourly publish.
  * Attempt times varied widely: median 25 s in the fill phase and 13–19 s at night, with some late fill-phase ascents on
    large cases taking 150–270 s. So it made relatively few attempts, many of them on hard cases.
  * The machine paused and restarted twice on 12 October (≈19:40–20:32 and 21:36). Both times the next cycle restarted
    the supervisor, and the only loss was idle time.
* **The laptop** (Alejandro's computer, a 2-vCPU Linux workspace reached through the Claude desktop app) ran the engine
  in bounded runs: at most about 2.5 minutes per command, because background processes end when a command returns.
  * The 10- and 6-minute cycles chained two or three runs, exported the cases where the laptop beat the main archive,
    and imported them with `scripts/remote.py` (every packing is re-legalized on import).
  * Two problems shaped how it was used:
    * **Runs longer than about 160 s lost the link.** Run lengths were 75–120 s on 12 October and 85–110 s in the night,
      plus a 28-second hard stop (`laptop_run.sh` allows at most about 3 minutes per command).
    * **A single attempt on a large case outlasts a run.** The laptop's attempts were being killed at the deadline. From
      21:24 the laptop runs in fast mode on the smallest cases (from 03:04 on 13 October capped at n ≤ 20, later 14,
      then 17).
  * Its drive was full from 12 October 22:33: 0 bytes free at first, then 16 MB, out of 239 GB, from causes outside the
    project. Its exports were
    therefore written to one file overwritten every cycle. Its copy of the archive was kept as a shallow clone inside
    the Linux workspace, which has its own disk.
* **GitHub Actions "medium"**: 4 jobs × 4 workers × 50 minutes, dispatched by the cycle when the last run was at least
  55 minutes old. Each job starts from `main`, pushes its improvements to a branch, and the cycle harvests them after
  re-legalizing. Twelve runs were made in this phase (table in chapter 18).
* **Reporting**: a status message every 10 minutes on 12 October and every 6 minutes in the night. Each message gave
  coverage, attempts and new bests by machine and family, and the state of the Actions run.

## 17. Incidents and fixes

1. **Slow tightening of large solids**: SLP ran to its time limit for gains below 10<sup>−9</sup>. Fixed with the
   50-round stop rule (15.5).
2. **Laptop command timeouts**: bounded runs were shortened to 75–120 s. One stage upload failed and a retry worked.
3. **Remote attempt counts lost or zero**: the first export counted only attempts since the previous export, so
   attempts from earlier runs were lost, and one import showed zero. Replaced by per-host totals for the laptop and
   increments for Actions, then verified by a manual import.
4. **Cloud machine pauses** (twice on 12 October): the workers died with the machine. The cycle's supervisor check
   restarted them, and the incident cost about 50 minutes of cloud time.
5. **Laptop link drops** on runs near 160 s: the last run of each cycle was shortened.
6. **Laptop disk full**: on 12 October at 22:33 `git fetch` into the laptop's clone failed with an I/O error (0 bytes
   free). From then on the laptop's exports used a single overwritten file. The archive mirror moved to the Linux
   workspace, and no new files were written to the drive.
7. **Concurrent pushes with the website agent** (13 Oct 01:43):
   * The agent pushed the domain configuration while the cycle's checkpoint was being pushed, so the push was rejected.
   * Resolving it with `git pull --rebase --autostash` failed halfway: "unable to create file state/attempts.jsonl: File
     exists", because the workers were appending to it.
   * The working copy of the attempt log was left with one line, and a worker then wrote a second.
   * Repair:
     * the workers were frozen (SIGSTOP);
     * the two new lines and one new best were saved;
     * the log was restored from HEAD plus the autostash commit, and the saved lines were appended (64,325 lines, times
       monotone);
     * the archive check passed;
     * the domain commit was merged and the workers resumed.
   * Since then `scripts/cycle.sh` and `scripts/publish.py` fetch and **merge** `origin/main` before pushing, and never
     rebase or reset while workers write `state/`.
   * A side effect during the repair: a `pkill -f` pattern matched the repairing shell itself and froze it. The next
     shell continued.
8. **Report windows off by one second**: improvements written in the same second as a 6-minute report's boundary were
   counted in the next report (harvest lines use rounded times). Totals were unaffected. The boundary was moved one
   second later.
9. **Hourly publish slows the cloud**: rebuilding and certifying several hundred improved records takes 20–60 minutes
   on the same two cores. The cloud's attempt counts dropped in those windows. The final publish was split into two
   processes, one for the prism family.

## 18. Results and analysis

The tables below are generated from the archive and the final record files. A short reading of them follows at the end
of the chapter (18.x).

<!-- DATA -->

### 18.x Reading the data

**How the cases were filled.**
* Speed: 262 cases had a packing at 17:30, 1,378 at 18:30 and all 1,794 at 21:54.
* Who filled them: GitHub Actions supplied 955 first packings, the cloud workers 456 and the laptop 383. Most of the
  Actions share came from run 1: coverage went from 414 at 18:00 to 1,312 when it was merged at 18:08.
* What set the pace at the end: the large n of heavy solids, where one attempt can take minutes. The last problems
  completed were the pentagonal hexecontahedra (21:54), disdyakis dodecahedra (21:34), hexagonal antiprisms in a cube
  (21:32), and octagonal prisms in a cube, truncated icosahedra and deltoidal icositetrahedra (21:23).
* Why the first hours look perfect: in the fill phase almost every attempt is a new best, because any packing of an
  empty case is one. This is why the cloud's hourly table shows as many new bests as attempts before 20:00.

**Where the records come from.**
* By machine: the final records were found on GitHub Actions in 1,098 cases (61%), on the laptop in 392 (22%) and on
  the cloud workers in 304 (17%).
* By move:
  * hops produced 1,016 final records (57%) and ascents 352;
  * fresh runs 132, re-tightenings 102, reinsertions 52 and descents 34;
  * 106 records are *monotone*: an (n + 1)-packing minus one piece, so s(n) ≤ s(n + 1), usually equal. The plateaus of
    s(n) come from these and from genuine plateaus.
* Success rates on the cloud:
  * ascend 74% (inflated by the fill phase);
  * hop 53%, re-tightening 45%, reinsertion 31%, fresh 18%, descend 9%.
* Qualitatively this is as in the Platonic phase (Appendix C): hops and ascents do most of the work, fresh runs rarely
  win and descents mostly confirm. The order of the success rates differs: there, re-tightening had by far the highest
  rate.

**Diminishing returns.**
* The yield of the GitHub Actions runs fell overall: 66 new bests per 100 attempts in run 1 (fill phase), 33–44 in runs
  2–5, 30 in run 6, 20–26 in runs 7–11, and 14 in run 12.
* Over the night the cloud converted 38% of its attempts into new bests, the laptop 25% and Actions 23%. The cloud's
  higher rate comes mostly from its hops (426 new bests from 806 hops at night) on the least-attempted cases of its
  shard.
* By morning the search was in the refinement regime for most cases.

**What the night changed.**
* Scope: 1,502 of the 1,794 records improved between the evening publish (12 Oct 22:31) and the end (433 Archimedean,
  447 Catalan, 622 prism problems).
* Typical size: median improvement 0.38% (Catalan) to 0.91% (prisms), means 0.9–2.0%.
* The large improvements (10–32%) are all cases whose evening record was weak:
  * dodecagonal antiprisms (n = 11–15, evening value 4.436 inherited from larger n) and dodecagonal prisms (n = 13–15,
    evening value 3.732) became exactly 3;
  * small cases became lattice-like packings: 5 and 6 triangular prisms fit in a triangular prism of edge 2, and 20
    and 21 truncated tetrahedra in a truncated tetrahedron of edge 3.
* From the first packing of each case to its final record, s fell by a median of 0.7% (Catalan), 0.9% (Archimedean)
  and 1.7% (prisms), and by up to 48% (prisms).

**Exact values and plateaus.**
* 177 records match a closed form to about 11 digits (a conjecture about the arrangement, not a proof of optimality).
* Container of edge 2: in 21 of the 36 same-shape problems a container of twice the size holds 3–4 copies. It holds 6
  rhombic dodecahedra, triakis octahedra, triangular prisms and hexagonal prisms (density 6/8 = 0.75). The rhombic
  dodecahedron and the triangular and hexagonal prisms tile space.
* Container of edge 3, same-solid problems: 21 truncated tetrahedra (density 21/27 = 0.778), 19 truncated cubes and 19
  triakis octahedra (0.704), 18 cuboctahedra, 17 triangular prisms, 16 octagonal
  prisms, and 15 dodecagonal prisms, dodecagonal antiprisms and octagonal antiprisms. These are visibly layered arrangements, and the long runs of
  integer values are plateaus of s(n).
* Container of edge 4: 40 truncated cubes and 40 dodecagonal prisms (density 0.625).
* The densest records of the phase:
  * 4 triakis tetrahedra in a triakis tetrahedron of size 5/3 (density 4/(5/3)³ = 0.864; s(2) = s(3) = s(4) = 5/3);
  * 23 truncated cubes (0.794) and 22 truncated cubes (0.776);
  * 21 truncated tetrahedra (0.778).

**Density at n = 40.**
* Medians: 0.557 for the Archimedean problems, 0.532 for the Catalan problems and 0.585 for the prism problems.
* Highest: triakis tetrahedra (0.629), and truncated cubes and dodecagonal prisms (0.625).
* Space-filling solids are far from 1:
  * truncated octahedra and rhombic dodecahedra tile space, yet their n = 40 records reach only 0.569 and 0.558;
  * part of the gap is the boundary (40 pieces in a container of the same shape);
  * part of it is search difficulty. A lattice construction for these two would be a direct test.
* Lowest, and an outlier: dodecagonal antiprisms in a dodecagonal antiprism (0.450). This is the clearest weakness in
  the data:
  * from n = 18 to n = 39 every record has s = 4.43608, mostly monotone copies of a larger packing, and the density falls
    to 0.21 at n = 18;
  * yet 15 pieces fit at s = 3.
  * Very flat pieces (the 12-gon antiprism with unit edges is about 3.86 wide and 0.86 tall) do not suit a homotopy that
    starts from rounded bodies of comparable size. Layer and column constructions, seeded into the archive like the
    Platonic lattice constructions, would very likely improve all of n = 16–39 at once.
  * The same applies, less severely, to dodecagonal prisms (s = 2 + √3 for every n from 17 to 32) and octagonal antiprisms.

**Prisms in themselves and in a cube.** At large n the two containers reach similar densities (for example 0.593
against 0.597 for 40 triangular prisms). At small n either can win:
* 4 dodecagonal prisms stack into a cube of edge 4 at density 0.70;
* the dodecagonal prism's own shape does better at n = 40 (0.625 against 0.562).

**Certificates.**
* All 1,794 records of the three families pass `certify_general.py`, and the 351 Platonic records pass both certifiers.
* Cost: 22 minutes for all of them. Median 0.1 s per record; longest 31 s (39 truncated icosidodecahedra, each with
  120 vertices).
* 112,799 near pairs were separated by explicit rational planes.

**Attempts.** The machines made about 21,800 attempts on the three families in this phase:
* 15,372 in GitHub Actions, from the per-run log;
* 4,291 on the laptop, from its per-host total;
* 2,106 on the cloud.

The archive's own counter shows 13,122 for Actions, lower mainly because remote counts were only recorded from 18:27,
after run 1.
1,201 of the 1,794 cases reached the goal of 10 attempts. The remaining 593 are all in the shards of the cloud (388) and
the laptop (205), spread over every n (156 with n ≤ 10, 111 with n 11–20, 157 with n 21–30, 169 with n 31–40). The
Actions jobs, sixteen workers on four shards, brought their own shards to the goal first.

**Next steps suggested by the data.**
1. Seed layer and lattice constructions for the flat pieces (dodecagonal and octagonal prisms and antiprisms) and for
   the space-filling solids (truncated octahedra, rhombic dodecahedra, triangular and hexagonal prisms).
2. Finish the 10-attempt goal on the remaining 593 cases. They are the cloud's and the laptop's shards, so rebalancing
   the shards would let the Actions jobs take them.
3. Look for published results for any of the 46 problems. None were searched for in this phase, so the tables have no
   "previous" column for the new families.
4. Use the website's submission pipeline to collect independent packings, which would be the first external check of
   these values.

## 19. The website: polyhedrainpolyhedra.wiki

Built on 12 October (21:44–22:37) from `web/` by `scripts/site.py` and deployed to the `gh-pages` branch by
`scripts/pages.sh` and by `.github/workflows/site.yml` on every push that changes the site or the records.

* **Records**: the explorer.
  * Three families, and an atlas of the problems in which each tile is a drawing of a real packing from the archive.
  * The 3D viewer (three.js) with slicing, colouring by orientation class, piece inspection, spread and an opacity
    slider (added 13 Oct 01:37).
  * The record table with the proof status, and the s(n) and increment charts.
* **All constructions**: every record with links to its JSON file, exact certificate and float check on GitHub.
* **Method** and **Certification**: the method and the certificate, linked to every source file. They include the table
  of number fields of all 41 solids, generated from `src/solids_exact.json`.
* **Contribute**:
  * a checker that runs the separating axis test in the browser on a pasted packing of any pair of the 41 solids, with
    a 3D preview;
  * "Submit on GitHub", which pre-fills the *Submit a packing* issue form;
  * forms to propose a new category or share another construction.
* **The submission workflow** (`.github/workflows/submission.yml` with `scripts/check_submission.py`) runs on every
  submission issue:
  * the float check and the exact certificate, the comparison with the current record, a reply on the issue, and
    labels;
  * when a maintainer adds `accepted`, it writes the record with the contributor's credit, rebuilds the site and closes
    the issue.
  * It was tested end to end on a scratch copy of the repository.
* **About**: history, credits, citation and licence.

From 01:42 on 13 October the site was developed further in parallel by the agent deploying the domain, through a
direct push (`web/CNAME`) and pull requests #3, #4 and #8–#11 on GitHub:
* `web/CNAME` for polyhedrainpolyhedra.wiki;
* viewer themes and layout controls;
* tests of the submission forms;
* independent and community records with provenance;
* certified historical baselines for all 25 Platonic pairs;
* versioned assets.

Those changes were merged into `main` alongside the search checkpoints, after the incident in chapter 17.

## Appendix G. Every record of the three families (final)

One table per problem.
* "s (certified)" links to the record file. It is the certified container size truncated to five decimals.
* "touching limit" is the size of the tightened packing before the 10<sup>−7</sup> clearance is added.
* "machine / move" says where and how the packing in the record was found:
  * *monotone* is the (n + 1)-packing minus one piece;
  * *tighten* is a re-tightening of a stored packing.

<!-- APPENDIX -->
