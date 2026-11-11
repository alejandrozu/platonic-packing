# platonic-packing

**How small can a Platonic solid be and still hold n unit copies of a Platonic solid?** This repository answers that,
with proofs of validity, for nine problems — each Platonic solid in a copy of itself, and the dual pairs (cubes in an
octahedron, octahedra in a cube, dodecahedra in an icosahedron, icosahedra in a dodecahedron) — for n = 2 to 40, using Yohei Nakajima's
*soft-to-rigid* method: start every piece as its inscribed sphere, then sharpen it into the solid while inward
pressure shrinks the container. Every packing is **certified in exact arithmetic** (over Q(√2, √3, √5, √7) for the Platonic records; record numbers may be given exactly in that field, see `multiquad.py`).

**Website: [https://alejandrozu.github.io/platonic-packing/](https://alejandrozu.github.io/platonic-packing/)** (moving to polyhedrainpolyhedra.wiki): every record in 3D, the method, the
certificates, and a page to [check and submit your own packings](https://alejandrozu.github.io/platonic-packing/contribute/)
(see [CONTRIBUTING.md](CONTRIBUTING.md)).

**Since 12 Oct 2026 the project also covers every Archimedean and Catalan solid packed in itself, and the regular
prisms and antiprisms (triangular to dodecagonal) packed in themselves and in a cube**: 55 problems and 2,145 cases in
all, every one with a packing certified exactly by `certify_general.py` (number fields, rational rotations, interval
arithmetic). Their tables are in [records/families.md](records/families.md); the method is described on the
[website](https://alejandrozu.github.io/platonic-packing/method/). The rest of this README describes the original nine Platonic
problems.

**Since 15 Oct 2026: the 25 Platonic problems go to n = 100** like the other families (n = 41–100 were first filled by
nested packings, `scripts/compose3d.py`: a packing of one solid inside each piece of another, scales multiply, then
searched). **Related work** (the separating-plane / quasi-phi-function optimization literature, dense polyhedral
packings, benchmarks, certification): [docs/RELATED_WORK.md](docs/RELATED_WORK.md).

**Since 15 Oct 2026: higher polytopes.** Every pair of regular polytopes of the same dimension, piece in container:
5-cell, tesseract, 16-cell, 24-cell, 120-cell and 600-cell in 4D (36 problems, n ≤ 40), simplex, hypercube and
orthoplex in 5D and 6D (9 problems each, n ≤ 32 and n ≤ 24): 54 problems, 1,890 cases. The d-dimensional method
(simulator `src/ndsim.py`, tightening `src/ndslp.py`, engine `scripts/engine_nd.py`), the exact certificate
(`certify_nd.py`), the cost study against 3D and the chosen n ranges are in [docs/HIGHER_DIM.md](docs/HIGHER_DIM.md);
tables in [records/higher.md](records/higher.md); the website draws each packing as 3D slices.

It generalizes [`yoheinakajima/soft-to-rigid-packing`](https://github.com/yoheinakajima/soft-to-rigid-packing)
(unit cubes in a cube; his 12-cube record 2.9315185094797) from cubes to all five Platonic solids, as pieces and as
containers.

* **Complete report of the project (9–11 Oct 2026):** [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md) — everything that
  was tried, every result (including what did not work), incidents, lessons, and data appendices.
* **Read first:** [docs/MATH.md](docs/MATH.md) — the problem, the homotopy lemma, why the geometry is exact, what the
  certificate proves, the lattice constructions, observations, and what is *not* proven.
* **Records:** [records/README.md](records/README.md) (tables with links), [records/SUMMARY.csv](records/SUMMARY.csv)
  (all digits), one folder per problem with record files, checker outputs and pictures.
* **State of the work and next steps:** [STATUS.md](STATUS.md); chronological log: [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md).
* **Interactive viewer:** [the website](https://alejandrozu.github.io/platonic-packing/) (built from `web/` by `scripts/site.py`).

## Generalization paper and Lean evidence

[The manuscript](docs/research-2026-10-16-generalization/manuscript.pdf) and [source/evidence guide](docs/research-2026-10-16-generalization/README.md) describe the arbitrary-dimensional geometric generalization and computational cost bounds. Lean verifies **532 source-bound witnesses across all 140 families of the frozen catalogue**: all 402 selected rational certificates, plus one two-piece witness from each of the other 130 families. The package retains immutable input hashes, numerical proof sources, logs and separate construction/refinement attribution. These are feasibility proofs for the selected frozen witnesses; global optimality and the entire changing live archive remain outside that claim.

The formal library also proves exact support and orientation identities for the softened bodies, and quantitative coordinate/pose error budgets that preserve a packing under sufficient wall and pair clearances. These are conditional analytic guarantees; they do not assert numerical tolerance radii for every record or optimizer convergence. See the [formal scope and reproduction guide](docs/research-2026-10-16-generalization/formal/README.md#quantitative-clearance-and-exact-support).

The [materials-science guide](https://polyhedrainpolyhedra.wiki/materials/) connects packing geometry to crystallization, confinement, grains, optical response, porous structures and granular mechanics through 25 primary studies. The [source audit](docs/MATERIALS_SCIENCE.md) distinguishes established physical results from proposed uses of this catalogue. A separate [Lean supplement](docs/MATERIALS_FORMALIZATION.md) explains certified translational configuration volume and sufficient conditions for periodic repetition, including their assumptions and limits as materials models.

## Results: s = container edge ÷ piece edge, n = 2…40

Nine problems: each Platonic solid in a copy of itself, and the dual pairs (cubes in an octahedron, octahedra in a cube,
dodecahedra in an icosahedron, icosahedra in a dodecahedron). Each entry is the smallest container found so far, as
certified (10⁻⁷ clearance, truncated to 5 decimals), linking to its record file. "≈ x" is a *conjectured* closed form
(touching limit agrees with x to ~11 digits; small integers omitted); ✱ marks a value below the best previously
published one (cubes in a cube: Friedman's catalogue and later records; octahedra in a cube: Hyra-results). s(n) is
non-decreasing in n by construction. The search is still running and this table is regenerated automatically.

<!-- RESULTS:START -->
_Auto-generated 2026-11-11 18:10 CET from the running search; see [PROGRESS.md](PROGRESS.md) for search statistics._

### Same solid

| n | Tetrahedra in a tetrahedron | Octahedra in an octahedron | Icosahedra in an icosahedron | Dodecahedra in a dodecahedron | Cubes in a cube | previous |
|---:|---|---|---|---|---|---|
| 2 | [1.95356+](records/tetintet/tetintet_n02.json) | [1.93311+](records/octinoct/octinoct_n02.json) | [1.96308+](records/icoinico/icoinico_n02.json) | [1.98759+](records/dodindod/dodindod_n02.json) | [2.00000+](records/cubincub/cubincub_n02.json) | 2.00000 T |
| 3 | [2.00000+](records/tetintet/tetintet_n03.json) | [2.00000+](records/octinoct/octinoct_n03.json) | [2.00000+](records/icoinico/icoinico_n03.json) | [2.00000+](records/dodindod/dodindod_n03.json) | [2.00000+](records/cubincub/cubincub_n03.json) | 2.00000 T |
| 4 | [2.00000+](records/tetintet/tetintet_n04.json) | [2.00000+](records/octinoct/octinoct_n04.json) | [2.14589+](records/icoinico/icoinico_n04.json) ≈ (11 - 3√5)/2 | [2.00000+](records/dodindod/dodindod_n04.json) | [2.00000+](records/cubincub/cubincub_n04.json) | 2.00000 T |
| 5 | [2.00000+](records/tetintet/tetintet_n05.json) | [2.00000+](records/octinoct/octinoct_n05.json) | [2.23606+](records/icoinico/icoinico_n05.json) ≈ √5 | [2.23606+](records/dodindod/dodindod_n05.json) ≈ √5 | [2.00000+](records/cubincub/cubincub_n05.json) | 2.00000 T |
| 6 | [2.29099+](records/tetintet/tetintet_n06.json) ≈ (3 + √15)/3 | [2.00000+](records/octinoct/octinoct_n06.json) | [2.34164+](records/icoinico/icoinico_n06.json) ≈ (5 + 3√5)/5 | [2.23606+](records/dodindod/dodindod_n06.json) ≈ √5 | [2.00000+](records/cubincub/cubincub_n06.json) | 2.00000 T |
| 7 | [2.38195+](records/tetintet/tetintet_n07.json) | [2.50000+](records/octinoct/octinoct_n07.json) ≈ 5/2 | [2.44931+](records/icoinico/icoinico_n07.json) ≈ (149 + 67√5)/122 | [2.42705+](records/dodindod/dodindod_n07.json) ≈ (3 + 3√5)/4 | [2.00000+](records/cubincub/cubincub_n07.json) | 2.00000 T |
| 8 | [2.38742+](records/tetintet/tetintet_n08.json) ≈ (4 + √10)/3 | [2.50000+](records/octinoct/octinoct_n08.json) ≈ 5/2 | [2.49661+](records/icoinico/icoinico_n08.json) ≈ (81 + 33√5)/62 | [2.52786+](records/dodindod/dodindod_n08.json) ≈ 7 - 2√5 | [2.00000+](records/cubincub/cubincub_n08.json) | 2.00000 T |
| 9 | [2.61556+](records/tetintet/tetintet_n09.json) | [2.50000+](records/octinoct/octinoct_n09.json) ≈ 5/2 | [2.58295+](records/icoinico/icoinico_n09.json) ≈ 127√5/271 + 416/271 | [2.59888+](records/dodindod/dodindod_n09.json) ≈ (35 + 32√5)/41 | [2.70710+](records/cubincub/cubincub_n09.json) ≈ (4 + √2)/2 | 2.70711 F |
| 10 | [2.70630+](records/tetintet/tetintet_n10.json) | [2.50000+](records/octinoct/octinoct_n10.json) ≈ 5/2 | [2.60989+](records/icoinico/icoinico_n10.json) ≈ 71/88 + (3√(-118 + 53√5) + 70√5)/88 | [2.70520+](records/dodindod/dodindod_n10.json) ≈ (101 + 25√5)/58 | [2.70710+](records/cubincub/cubincub_n10.json) ≈ (4 + √2)/2 | 2.70711 F |
| 11 | [2.79826+](records/tetintet/tetintet_n11.json) | [2.66666+](records/octinoct/octinoct_n11.json) ≈ 8/3 | [2.61803+](records/icoinico/icoinico_n11.json) ≈ (3 + √5)/2 | [2.76393+](records/dodindod/dodindod_n11.json) ≈ 5 - √5 | [2.88171+](records/cubincub/cubincub_n11.json) ✱ | 2.88295 L |
| 12 | [2.85760+](records/tetintet/tetintet_n12.json) | [2.66666+](records/octinoct/octinoct_n12.json) ≈ 8/3 | [2.61803+](records/icoinico/icoinico_n12.json) ≈ (3 + √5)/2 | [2.76393+](records/dodindod/dodindod_n12.json) ≈ 5 - √5 | [2.93151+](records/cubincub/cubincub_n12.json) | 2.93152 N |
| 13 | [2.91514+](records/tetintet/tetintet_n13.json) | [2.83333+](records/octinoct/octinoct_n13.json) ≈ 17/6 | [2.80901+](records/icoinico/icoinico_n13.json) ≈ (9 + √5)/4 | [2.90557+](records/dodindod/dodindod_n13.json) ≈ 19/5 - 2√(5)/5 | [2.95614+](records/cubincub/cubincub_n13.json) ≈ √(-2 + 4√2)/2 + 2 | 2.95600 F |
| 14 | [2.94300+](records/tetintet/tetintet_n14.json) | [2.94311+](records/octinoct/octinoct_n14.json) | [3.01780+](records/icoinico/icoinico_n14.json) ≈ 1/7 + 9√(5)/7 | [2.99979+](records/dodindod/dodindod_n14.json) | [2.98994+](records/cubincub/cubincub_n14.json) ≈ 7√2/10 + 2 | 2.98995 F |
| 15 | [2.98883+](records/tetintet/tetintet_n15.json) | [2.98533+](records/octinoct/octinoct_n15.json) | [3.04832+](records/icoinico/icoinico_n15.json) | [3.03743+](records/dodindod/dodindod_n15.json) ≈ 223/242 + 229√5/242 | [3.00000+](records/cubincub/cubincub_n15.json) | 3.00000 T |
| 16 | [3.03538+](records/tetintet/tetintet_n16.json) | [2.99465+](records/octinoct/octinoct_n16.json) | [3.12130+](records/icoinico/icoinico_n16.json) | [3.10210+](records/dodindod/dodindod_n16.json) | [3.00000+](records/cubincub/cubincub_n16.json) | 3.00000 T |
| 17 | [3.08936+](records/tetintet/tetintet_n17.json) | [3.00000+](records/octinoct/octinoct_n17.json) | [3.19692+](records/icoinico/icoinico_n17.json) | [3.16774+](records/dodindod/dodindod_n17.json) ≈ 6/5 + 22√(5)/25 | [3.00000+](records/cubincub/cubincub_n17.json) | 3.00000 T |
| 18 | [3.11466+](records/tetintet/tetintet_n18.json) ≈ 251704511789/6577993305 - 6027514273√654/4385328870 | [3.00000+](records/octinoct/octinoct_n18.json) | [3.19821+](records/icoinico/icoinico_n18.json) ≈ (24 + 5√5)/11 | [3.21549+](records/dodindod/dodindod_n18.json) ≈ (53 + 18√5)/29 | [3.00000+](records/cubincub/cubincub_n18.json) | 3.00000 T |
| 19 | [3.18717+](records/tetintet/tetintet_n19.json) | [3.00000+](records/octinoct/octinoct_n19.json) | [3.31147+](records/icoinico/icoinico_n19.json) | [3.29218+](records/dodindod/dodindod_n19.json) | [3.00000+](records/cubincub/cubincub_n19.json) | 3.00000 T |
| 20 | [3.24321+](records/tetintet/tetintet_n20.json) | [3.16653+](records/octinoct/octinoct_n20.json) | [3.35370+](records/icoinico/icoinico_n20.json) | [3.34969+](records/dodindod/dodindod_n20.json) | [3.00000+](records/cubincub/cubincub_n20.json) | 3.00000 T |
| 21 | [3.29827+](records/tetintet/tetintet_n21.json) | [3.20000+](records/octinoct/octinoct_n21.json) ≈ 16/5 | [3.40705+](records/icoinico/icoinico_n21.json) | [3.39148+](records/dodindod/dodindod_n21.json) ≈ -6 + 21√(5)/5 | [3.00000+](records/cubincub/cubincub_n21.json) | 3.00000 T |
| 22 | [3.34340+](records/tetintet/tetintet_n22.json) | [3.25000+](records/octinoct/octinoct_n22.json) ≈ 13/4 | [3.47954+](records/icoinico/icoinico_n22.json) | [3.44428+](records/dodindod/dodindod_n22.json) | [3.00000+](records/cubincub/cubincub_n22.json) | 3.00000 T |
| 23 | [3.38259+](records/tetintet/tetintet_n23.json) | [3.25000+](records/octinoct/octinoct_n23.json) ≈ 13/4 | [3.55296+](records/icoinico/icoinico_n23.json) | [3.53929+](records/dodindod/dodindod_n23.json) | [3.00000+](records/cubincub/cubincub_n23.json) | 3.00000 T |
| 24 | [3.43388+](records/tetintet/tetintet_n24.json) | [3.36363+](records/octinoct/octinoct_n24.json) ≈ 37/11 | [3.59398+](records/icoinico/icoinico_n24.json) | [3.57860+](records/dodindod/dodindod_n24.json) | [3.00000+](records/cubincub/cubincub_n24.json) | 3.00000 T |
| 25 | [3.48910+](records/tetintet/tetintet_n25.json) | [3.39983+](records/octinoct/octinoct_n25.json) | [3.60901+](records/icoinico/icoinico_n25.json) | [3.60237+](records/dodindod/dodindod_n25.json) | [3.00000+](records/cubincub/cubincub_n25.json) | 3.00000 T |
| 26 | [3.58091+](records/tetintet/tetintet_n26.json) | [3.42857+](records/octinoct/octinoct_n26.json) ≈ 24/7 | [3.67328+](records/icoinico/icoinico_n26.json) ≈ 50545/36502 + 37359√5/36502 | [3.63718+](records/dodindod/dodindod_n26.json) | [3.00000+](records/cubincub/cubincub_n26.json) | 3.00000 T |
| 27 | [3.61602+](records/tetintet/tetintet_n27.json) | [3.50000+](records/octinoct/octinoct_n27.json) ≈ 7/2 | [3.70095+](records/icoinico/icoinico_n27.json) | [3.70130+](records/dodindod/dodindod_n27.json) ≈ √(10√5 + 50)/5 + 2 | [3.00000+](records/cubincub/cubincub_n27.json) | 3.00000 T |
| 28 | [3.68963+](records/tetintet/tetintet_n28.json) | [3.50000+](records/octinoct/octinoct_n28.json) ≈ 7/2 | [3.74070+](records/icoinico/icoinico_n28.json) | [3.73369+](records/dodindod/dodindod_n28.json) | [3.66599+](records/cubincub/cubincub_n28.json) ✱ | 3.70711 F |
| 29 | [3.71166+](records/tetintet/tetintet_n29.json) | [3.50000+](records/octinoct/octinoct_n29.json) ≈ 7/2 | [3.77348+](records/icoinico/icoinico_n29.json) | [3.74709+](records/dodindod/dodindod_n29.json) ≈ (55 + 24√5)/29 | [3.70710+](records/cubincub/cubincub_n29.json) ≈ √2/2 + 3 | 3.70711 F |
| 30 | [3.75412+](records/tetintet/tetintet_n30.json) | [3.60000+](records/octinoct/octinoct_n30.json) ≈ 18/5 | [3.82215+](records/icoinico/icoinico_n30.json) | [3.74709+](records/dodindod/dodindod_n30.json) ≈ (55 + 24√5)/29 | [3.70710+](records/cubincub/cubincub_n30.json) ≈ √2/2 + 3 | 3.70711 F |
| 31 | [3.82327+](records/tetintet/tetintet_n31.json) | [3.66666+](records/octinoct/octinoct_n31.json) ≈ 11/3 | [3.85695+](records/icoinico/icoinico_n31.json) | [3.74709+](records/dodindod/dodindod_n31.json) ≈ (55 + 24√5)/29 | [3.70710+](records/cubincub/cubincub_n31.json) ≈ √2/2 + 3 | 3.70711 F |
| 32 | [3.85384+](records/tetintet/tetintet_n32.json) | [3.69230+](records/octinoct/octinoct_n32.json) ≈ 48/13 | [3.87928+](records/icoinico/icoinico_n32.json) | [3.74709+](records/dodindod/dodindod_n32.json) ≈ (55 + 24√5)/29 | [3.70710+](records/cubincub/cubincub_n32.json) ≈ √2/2 + 3 | 3.70711 F |
| 33 | [3.89213+](records/tetintet/tetintet_n33.json) | [3.73684+](records/octinoct/octinoct_n33.json) ≈ 71/19 | [3.89699+](records/icoinico/icoinico_n33.json) | [3.74709+](records/dodindod/dodindod_n33.json) ≈ (55 + 24√5)/29 | [3.70710+](records/cubincub/cubincub_n33.json) ≈ √2/2 + 3 | 3.70711 F |
| 34 | [3.92757+](records/tetintet/tetintet_n34.json) | [3.78844+](records/octinoct/octinoct_n34.json) | [3.90016+](records/icoinico/icoinico_n34.json) | [3.91148+](records/dodindod/dodindod_n34.json) | [3.82287+](records/cubincub/cubincub_n34.json) ≈ √7/2 + 5/2 |  |
| 35 | [3.95251+](records/tetintet/tetintet_n35.json) | [3.80000+](records/octinoct/octinoct_n35.json) ≈ 19/5 | [3.93598+](records/icoinico/icoinico_n35.json) | [3.98565+](records/dodindod/dodindod_n35.json) | [3.86068+](records/cubincub/cubincub_n35.json) |  |
| 36 | [3.97133+](records/tetintet/tetintet_n36.json) | [3.85433+](records/octinoct/octinoct_n36.json) | [4.01231+](records/icoinico/icoinico_n36.json) | [4.02142+](records/dodindod/dodindod_n36.json) | [3.89442+](records/cubincub/cubincub_n36.json) |  |
| 37 | [3.99814+](records/tetintet/tetintet_n37.json) | [3.88376+](records/octinoct/octinoct_n37.json) | [4.04727+](records/icoinico/icoinico_n37.json) | [4.07872+](records/dodindod/dodindod_n37.json) | [3.92218+](records/cubincub/cubincub_n37.json) |  |
| 38 | [4.03555+](records/tetintet/tetintet_n38.json) | [3.91696+](records/octinoct/octinoct_n38.json) | [4.06030+](records/icoinico/icoinico_n38.json) | [4.12050+](records/dodindod/dodindod_n38.json) | [3.98077+](records/cubincub/cubincub_n38.json) |  |
| 39 | [4.04630+](records/tetintet/tetintet_n39.json) | [3.92959+](records/octinoct/octinoct_n39.json) | [4.06965+](records/icoinico/icoinico_n39.json) | [4.14221+](records/dodindod/dodindod_n39.json) | [4.00000+](records/cubincub/cubincub_n39.json) |  |
| 40 | [4.05505+](records/tetintet/tetintet_n40.json) | [3.95554+](records/octinoct/octinoct_n40.json) | [4.10751+](records/icoinico/icoinico_n40.json) | [4.17626+](records/dodindod/dodindod_n40.json) | [4.00000+](records/cubincub/cubincub_n40.json) |  |
| 41 | [4.09742+](records/tetintet/tetintet_n41.json) | [3.98271+](records/octinoct/octinoct_n41.json) | [4.14142+](records/icoinico/icoinico_n41.json) | [4.21499+](records/dodindod/dodindod_n41.json) | [4.00000+](records/cubincub/cubincub_n41.json) |  |
| 42 | [4.12193+](records/tetintet/tetintet_n42.json) | [3.99011+](records/octinoct/octinoct_n42.json) | [4.16979+](records/icoinico/icoinico_n42.json) | [4.21790+](records/dodindod/dodindod_n42.json) | [4.00000+](records/cubincub/cubincub_n42.json) |  |
| 43 | [4.19277+](records/tetintet/tetintet_n43.json) | [3.99415+](records/octinoct/octinoct_n43.json) | [4.22139+](records/icoinico/icoinico_n43.json) | [4.23606+](records/dodindod/dodindod_n43.json) | [4.00000+](records/cubincub/cubincub_n43.json) |  |
| 44 | [4.23486+](records/tetintet/tetintet_n44.json) | [3.99516+](records/octinoct/octinoct_n44.json) | [4.22140+](records/icoinico/icoinico_n44.json) | [4.30785+](records/dodindod/dodindod_n44.json) | [4.00000+](records/cubincub/cubincub_n44.json) |  |
| 45 | [4.25822+](records/tetintet/tetintet_n45.json) | [4.06337+](records/octinoct/octinoct_n45.json) | [4.22518+](records/icoinico/icoinico_n45.json) | [4.31860+](records/dodindod/dodindod_n45.json) | [4.00000+](records/cubincub/cubincub_n45.json) |  |
| 46 | [4.31061+](records/tetintet/tetintet_n46.json) | [4.08152+](records/octinoct/octinoct_n46.json) | [4.22914+](records/icoinico/icoinico_n46.json) | [4.35527+](records/dodindod/dodindod_n46.json) | [4.00000+](records/cubincub/cubincub_n46.json) |  |
| 47 | [4.32750+](records/tetintet/tetintet_n47.json) | [4.12718+](records/octinoct/octinoct_n47.json) | [4.23471+](records/icoinico/icoinico_n47.json) | [4.39501+](records/dodindod/dodindod_n47.json) | [4.00000+](records/cubincub/cubincub_n47.json) |  |
| 48 | [4.34979+](records/tetintet/tetintet_n48.json) | [4.17799+](records/octinoct/octinoct_n48.json) | [4.23599+](records/icoinico/icoinico_n48.json) | [4.42640+](records/dodindod/dodindod_n48.json) | [4.00000+](records/cubincub/cubincub_n48.json) |  |
| 49 | [4.39412+](records/tetintet/tetintet_n49.json) | [4.20328+](records/octinoct/octinoct_n49.json) | [4.31556+](records/icoinico/icoinico_n49.json) | [4.43648+](records/dodindod/dodindod_n49.json) | [4.00000+](records/cubincub/cubincub_n49.json) |  |
| 50 | [4.42260+](records/tetintet/tetintet_n50.json) | [4.26187+](records/octinoct/octinoct_n50.json) | [4.35081+](records/icoinico/icoinico_n50.json) | [4.51902+](records/dodindod/dodindod_n50.json) | [4.00000+](records/cubincub/cubincub_n50.json) |  |
| 51 | [4.55550+](records/tetintet/tetintet_n51.json) | [4.27622+](records/octinoct/octinoct_n51.json) | [4.38989+](records/icoinico/icoinico_n51.json) | [4.52823+](records/dodindod/dodindod_n51.json) | [4.00000+](records/cubincub/cubincub_n51.json) |  |
| 52 | [4.57953+](records/tetintet/tetintet_n52.json) | [4.30860+](records/octinoct/octinoct_n52.json) | [4.41909+](records/icoinico/icoinico_n52.json) | [4.55249+](records/dodindod/dodindod_n52.json) | [4.00000+](records/cubincub/cubincub_n52.json) |  |
| 53 | [4.58025+](records/tetintet/tetintet_n53.json) | [4.35345+](records/octinoct/octinoct_n53.json) | [4.45184+](records/icoinico/icoinico_n53.json) | [4.56601+](records/dodindod/dodindod_n53.json) | [4.00000+](records/cubincub/cubincub_n53.json) |  |
| 54 | [4.60028+](records/tetintet/tetintet_n54.json) | [4.37499+](records/octinoct/octinoct_n54.json) | [4.46651+](records/icoinico/icoinico_n54.json) | [4.58196+](records/dodindod/dodindod_n54.json) | [4.00000+](records/cubincub/cubincub_n54.json) |  |
| 55 | [4.60738+](records/tetintet/tetintet_n55.json) | [4.41617+](records/octinoct/octinoct_n55.json) | [4.47570+](records/icoinico/icoinico_n55.json) | [4.60857+](records/dodindod/dodindod_n55.json) | [4.00000+](records/cubincub/cubincub_n55.json) |  |
| 56 | [4.62839+](records/tetintet/tetintet_n56.json) | [4.46148+](records/octinoct/octinoct_n56.json) | [4.52087+](records/icoinico/icoinico_n56.json) | [4.62073+](records/dodindod/dodindod_n56.json) | [4.00000+](records/cubincub/cubincub_n56.json) |  |
| 57 | [4.68135+](records/tetintet/tetintet_n57.json) | [4.49088+](records/octinoct/octinoct_n57.json) | [4.59490+](records/icoinico/icoinico_n57.json) | [4.71361+](records/dodindod/dodindod_n57.json) | [4.00000+](records/cubincub/cubincub_n57.json) |  |
| 58 | [4.72397+](records/tetintet/tetintet_n58.json) | [4.49853+](records/octinoct/octinoct_n58.json) | [4.61748+](records/icoinico/icoinico_n58.json) | [4.71488+](records/dodindod/dodindod_n58.json) | [4.00000+](records/cubincub/cubincub_n58.json) |  |
| 59 | [4.72397+](records/tetintet/tetintet_n59.json) | [4.49932+](records/octinoct/octinoct_n59.json) | [4.67600+](records/icoinico/icoinico_n59.json) | [4.71510+](records/dodindod/dodindod_n59.json) | [4.00000+](records/cubincub/cubincub_n59.json) |  |
| 60 | [4.72397+](records/tetintet/tetintet_n60.json) | [4.50000+](records/octinoct/octinoct_n60.json) ≈ 9/2 | [4.71183+](records/icoinico/icoinico_n60.json) | [4.72445+](records/dodindod/dodindod_n60.json) | [4.00000+](records/cubincub/cubincub_n60.json) |  |
| 61 | [4.81164+](records/tetintet/tetintet_n61.json) | [4.55199+](records/octinoct/octinoct_n61.json) | [4.73395+](records/icoinico/icoinico_n61.json) | [4.73770+](records/dodindod/dodindod_n61.json) | [4.00000+](records/cubincub/cubincub_n61.json) |  |
| 62 | [4.81223+](records/tetintet/tetintet_n62.json) | [4.59144+](records/octinoct/octinoct_n62.json) | [4.78006+](records/icoinico/icoinico_n62.json) | [4.76997+](records/dodindod/dodindod_n62.json) | [4.00000+](records/cubincub/cubincub_n62.json) |  |
| 63 | [4.82639+](records/tetintet/tetintet_n63.json) | [4.59910+](records/octinoct/octinoct_n63.json) | [4.81168+](records/icoinico/icoinico_n63.json) | [4.81788+](records/dodindod/dodindod_n63.json) | [4.00000+](records/cubincub/cubincub_n63.json) |  |
| 64 | [4.83517+](records/tetintet/tetintet_n64.json) | [4.60850+](records/octinoct/octinoct_n64.json) | [4.83935+](records/icoinico/icoinico_n64.json) | [4.84672+](records/dodindod/dodindod_n64.json) | [4.00000+](records/cubincub/cubincub_n64.json) |  |
| 65 | [4.85878+](records/tetintet/tetintet_n65.json) | [4.61155+](records/octinoct/octinoct_n65.json) | [4.87083+](records/icoinico/icoinico_n65.json) | [4.85833+](records/dodindod/dodindod_n65.json) | [4.63467+](records/cubincub/cubincub_n65.json) |  |
| 66 | [4.86501+](records/tetintet/tetintet_n66.json) | [4.66610+](records/octinoct/octinoct_n66.json) | [4.90592+](records/icoinico/icoinico_n66.json) | [4.90375+](records/dodindod/dodindod_n66.json) | [4.67553+](records/cubincub/cubincub_n66.json) |  |
| 67 | [4.93415+](records/tetintet/tetintet_n67.json) | [4.73830+](records/octinoct/octinoct_n67.json) | [4.92431+](records/icoinico/icoinico_n67.json) | [5.00000+](records/dodindod/dodindod_n67.json) ≈ 5 | [4.67553+](records/cubincub/cubincub_n67.json) |  |
| 68 | [4.95474+](records/tetintet/tetintet_n68.json) | [4.76981+](records/octinoct/octinoct_n68.json) | [4.95617+](records/icoinico/icoinico_n68.json) | [5.00000+](records/dodindod/dodindod_n68.json) ≈ 5 | [4.67553+](records/cubincub/cubincub_n68.json) |  |
| 69 | [4.98487+](records/tetintet/tetintet_n69.json) | [4.77435+](records/octinoct/octinoct_n69.json) | [4.96011+](records/icoinico/icoinico_n69.json) | [5.00000+](records/dodindod/dodindod_n69.json) ≈ 5 | [4.70710+](records/cubincub/cubincub_n69.json) ≈ √2/2 + 4 |  |
| 70 | [4.98851+](records/tetintet/tetintet_n70.json) | [4.80718+](records/octinoct/octinoct_n70.json) | [4.98423+](records/icoinico/icoinico_n70.json) | [5.00000+](records/dodindod/dodindod_n70.json) ≈ 5 | [4.70710+](records/cubincub/cubincub_n70.json) ≈ √2/2 + 4 |  |
| 71 | [5.08148+](records/tetintet/tetintet_n71.json) | [4.82653+](records/octinoct/octinoct_n71.json) | [5.02102+](records/icoinico/icoinico_n71.json) | [5.00000+](records/dodindod/dodindod_n71.json) ≈ 5 | [4.70710+](records/cubincub/cubincub_n71.json) ≈ √2/2 + 4 |  |
| 72 | [5.08148+](records/tetintet/tetintet_n72.json) | [4.84705+](records/octinoct/octinoct_n72.json) | [5.03899+](records/icoinico/icoinico_n72.json) | [5.00000+](records/dodindod/dodindod_n72.json) ≈ 5 | [4.70710+](records/cubincub/cubincub_n72.json) ≈ √2/2 + 4 |  |
| 73 | [5.10986+](records/tetintet/tetintet_n73.json) | [4.86683+](records/octinoct/octinoct_n73.json) | [5.04048+](records/icoinico/icoinico_n73.json) | [5.00000+](records/dodindod/dodindod_n73.json) ≈ 5 | [4.70710+](records/cubincub/cubincub_n73.json) ≈ √2/2 + 4 |  |
| 74 | [5.12660+](records/tetintet/tetintet_n74.json) | [4.91956+](records/octinoct/octinoct_n74.json) | [5.05823+](records/icoinico/icoinico_n74.json) | [5.00000+](records/dodindod/dodindod_n74.json) ≈ 5 | [4.81098+](records/cubincub/cubincub_n74.json) |  |
| 75 | [5.13469+](records/tetintet/tetintet_n75.json) | [4.92539+](records/octinoct/octinoct_n75.json) | [5.08445+](records/icoinico/icoinico_n75.json) | [5.00000+](records/dodindod/dodindod_n75.json) | [4.82287+](records/cubincub/cubincub_n75.json) |  |
| 76 | [5.15013+](records/tetintet/tetintet_n76.json) | [4.93004+](records/octinoct/octinoct_n76.json) | [5.10744+](records/icoinico/icoinico_n76.json) | [5.02285+](records/dodindod/dodindod_n76.json) | [4.84057+](records/cubincub/cubincub_n76.json) |  |
| 77 | [5.16130+](records/tetintet/tetintet_n77.json) | [4.93383+](records/octinoct/octinoct_n77.json) | [5.14358+](records/icoinico/icoinico_n77.json) | [5.17082+](records/dodindod/dodindod_n77.json) | [4.85021+](records/cubincub/cubincub_n77.json) |  |
| 78 | [5.21556+](records/tetintet/tetintet_n78.json) | [4.94130+](records/octinoct/octinoct_n78.json) | [5.15833+](records/icoinico/icoinico_n78.json) | [5.18262+](records/dodindod/dodindod_n78.json) | [4.85875+](records/cubincub/cubincub_n78.json) |  |
| 79 | [5.22912+](records/tetintet/tetintet_n79.json) | [4.94214+](records/octinoct/octinoct_n79.json) | [5.17569+](records/icoinico/icoinico_n79.json) | [5.19314+](records/dodindod/dodindod_n79.json) | [4.88561+](records/cubincub/cubincub_n79.json) ≈ 4√2/3 + 3 |  |
| 80 | [5.25146+](records/tetintet/tetintet_n80.json) | [4.94656+](records/octinoct/octinoct_n80.json) | [5.18772+](records/icoinico/icoinico_n80.json) | [5.19553+](records/dodindod/dodindod_n80.json) | [4.89442+](records/cubincub/cubincub_n80.json) |  |
| 81 | [5.26321+](records/tetintet/tetintet_n81.json) | [4.94932+](records/octinoct/octinoct_n81.json) | [5.19416+](records/icoinico/icoinico_n81.json) | [5.19966+](records/dodindod/dodindod_n81.json) | [4.92133+](records/cubincub/cubincub_n81.json) |  |
| 82 | [5.33428+](records/tetintet/tetintet_n82.json) | [4.95091+](records/octinoct/octinoct_n82.json) | [5.19485+](records/icoinico/icoinico_n82.json) | [5.20098+](records/dodindod/dodindod_n82.json) | [5.00000+](records/cubincub/cubincub_n82.json) ≈ 5 |  |
| 83 | [5.34864+](records/tetintet/tetintet_n83.json) | [4.95357+](records/octinoct/octinoct_n83.json) | [5.24043+](records/icoinico/icoinico_n83.json) | [5.20720+](records/dodindod/dodindod_n83.json) | [5.00000+](records/cubincub/cubincub_n83.json) ≈ 5 |  |
| 84 | [5.35932+](records/tetintet/tetintet_n84.json) | [4.95636+](records/octinoct/octinoct_n84.json) | [5.25858+](records/icoinico/icoinico_n84.json) | [5.20720+](records/dodindod/dodindod_n84.json) | [5.00000+](records/cubincub/cubincub_n84.json) ≈ 5 |  |
| 85 | [5.38024+](records/tetintet/tetintet_n85.json) | [4.96844+](records/octinoct/octinoct_n85.json) | [5.26024+](records/icoinico/icoinico_n85.json) | [5.21881+](records/dodindod/dodindod_n85.json) | [5.00000+](records/cubincub/cubincub_n85.json) ≈ 5 |  |
| 86 | [5.40581+](records/tetintet/tetintet_n86.json) | [5.00000+](records/octinoct/octinoct_n86.json) | [5.36695+](records/icoinico/icoinico_n86.json) | [5.22005+](records/dodindod/dodindod_n86.json) | [5.00000+](records/cubincub/cubincub_n86.json) ≈ 5 |  |
| 87 | [5.40951+](records/tetintet/tetintet_n87.json) | [5.00000+](records/octinoct/octinoct_n87.json) | [5.38051+](records/icoinico/icoinico_n87.json) | [5.38079+](records/dodindod/dodindod_n87.json) | [5.00000+](records/cubincub/cubincub_n87.json) ≈ 5 |  |
| 88 | [5.46375+](records/tetintet/tetintet_n88.json) | [5.00000+](records/octinoct/octinoct_n88.json) | [5.39474+](records/icoinico/icoinico_n88.json) | [5.38141+](records/dodindod/dodindod_n88.json) | [5.00000+](records/cubincub/cubincub_n88.json) ≈ 5 |  |
| 89 | [5.46919+](records/tetintet/tetintet_n89.json) | [5.00000+](records/octinoct/octinoct_n89.json) | [5.43467+](records/icoinico/icoinico_n89.json) | [5.40149+](records/dodindod/dodindod_n89.json) | [5.00000+](records/cubincub/cubincub_n89.json) ≈ 5 |  |
| 90 | [5.47141+](records/tetintet/tetintet_n90.json) | [5.17559+](records/octinoct/octinoct_n90.json) | [5.45100+](records/icoinico/icoinico_n90.json) | [5.47213+](records/dodindod/dodindod_n90.json) ≈ 1 + 2√5 | [5.00000+](records/cubincub/cubincub_n90.json) ≈ 5 |  |
| 91 | [5.50766+](records/tetintet/tetintet_n91.json) | [5.17693+](records/octinoct/octinoct_n91.json) | [5.46106+](records/icoinico/icoinico_n91.json) | [5.47213+](records/dodindod/dodindod_n91.json) ≈ 1 + 2√5 | [5.00000+](records/cubincub/cubincub_n91.json) ≈ 5 |  |
| 92 | [5.55117+](records/tetintet/tetintet_n92.json) | [5.21049+](records/octinoct/octinoct_n92.json) | [5.47950+](records/icoinico/icoinico_n92.json) | [5.47213+](records/dodindod/dodindod_n92.json) ≈ 1 + 2√5 | [5.00000+](records/cubincub/cubincub_n92.json) ≈ 5 |  |
| 93 | [5.56229+](records/tetintet/tetintet_n93.json) | [5.21682+](records/octinoct/octinoct_n93.json) | [5.49320+](records/icoinico/icoinico_n93.json) | [5.47958+](records/dodindod/dodindod_n93.json) | [5.00000+](records/cubincub/cubincub_n93.json) ≈ 5 |  |
| 94 | [5.60469+](records/tetintet/tetintet_n94.json) | [5.27412+](records/octinoct/octinoct_n94.json) | [5.49995+](records/icoinico/icoinico_n94.json) | [5.54882+](records/dodindod/dodindod_n94.json) | [5.00000+](records/cubincub/cubincub_n94.json) ≈ 5 |  |
| 95 | [5.60974+](records/tetintet/tetintet_n95.json) | [5.33333+](records/octinoct/octinoct_n95.json) ≈ 16/3 | [5.61540+](records/icoinico/icoinico_n95.json) | [5.56796+](records/dodindod/dodindod_n95.json) | [5.00000+](records/cubincub/cubincub_n95.json) ≈ 5 |  |
| 96 | [5.61831+](records/tetintet/tetintet_n96.json) | [5.33333+](records/octinoct/octinoct_n96.json) ≈ 16/3 | [5.61798+](records/icoinico/icoinico_n96.json) | [5.56885+](records/dodindod/dodindod_n96.json) | [5.00000+](records/cubincub/cubincub_n96.json) ≈ 5 |  |
| 97 | [5.63280+](records/tetintet/tetintet_n97.json) | [5.33333+](records/octinoct/octinoct_n97.json) ≈ 16/3 | [5.61803+](records/icoinico/icoinico_n97.json) | [5.57984+](records/dodindod/dodindod_n97.json) | [5.00000+](records/cubincub/cubincub_n97.json) ≈ 5 |  |
| 98 | [5.63280+](records/tetintet/tetintet_n98.json) | [5.33333+](records/octinoct/octinoct_n98.json) ≈ 16/3 | [5.61803+](records/icoinico/icoinico_n98.json) | [5.58487+](records/dodindod/dodindod_n98.json) | [5.00000+](records/cubincub/cubincub_n98.json) ≈ 5 |  |
| 99 | [5.63816+](records/tetintet/tetintet_n99.json) | [5.33333+](records/octinoct/octinoct_n99.json) ≈ 16/3 | [5.61803+](records/icoinico/icoinico_n99.json) | [5.61801+](records/dodindod/dodindod_n99.json) | [5.00000+](records/cubincub/cubincub_n99.json) ≈ 5 |  |
| 100 | [5.66124+](records/tetintet/tetintet_n100.json) | [5.33333+](records/octinoct/octinoct_n100.json) | [5.66666+](records/icoinico/icoinico_n100.json) ≈ 17/3 | [5.61801+](records/dodindod/dodindod_n100.json) | [5.00000+](records/cubincub/cubincub_n100.json) ≈ 5 |  |

### Duals

| n | Cubes in an octahedron | Octahedra in a cube | previous | Dodecahedra in an icosahedron | Icosahedra in a dodecahedron |
|---:|---|---|---|---|---|
| 2 | [2.41421+](records/cubinoct/cubinoct_n02.json) ≈ 1 + √2 | [1.41421+](records/octincub/octincub_n02.json) ≈ √2 | 1.41421 W | [2.89442+](records/dodinico/dodinico_n02.json) ≈ (10 + 2√5)/5 | [1.23606+](records/icoindod/icoindod_n02.json) ≈ -1 + √5 |
| 3 | [2.70710+](records/cubinoct/cubinoct_n03.json) ≈ (4 + √2)/2 | [1.63299+](records/octincub/octincub_n03.json) ≈ (2√6)/3 | 1.63299 W | [3.14562+](records/dodinico/dodinico_n03.json) | [1.37303+](records/icoindod/icoindod_n03.json) |
| 4 | [2.70710+](records/cubinoct/cubinoct_n04.json) ≈ (4 + √2)/2 | [1.64991+](records/octincub/octincub_n04.json) ≈ (7√2)/6 | 1.64991 W | [3.37546+](records/dodinico/dodinico_n04.json) | [1.39344+](records/icoindod/icoindod_n04.json) ≈ (-7 + 5√5)/3 |
| 5 | [2.91260+](records/cubinoct/cubinoct_n05.json) | [1.75782+](records/octincub/octincub_n05.json) | 1.75782 W | [3.57490+](records/dodinico/dodinico_n05.json) | [1.53319+](records/icoindod/icoindod_n05.json) |
| 6 | [2.93185+](records/cubinoct/cubinoct_n06.json) ≈ 1 + √(√3 + 2) | [1.76776+](records/octincub/octincub_n06.json) ≈ (5√2)/4 | 1.76776 W | [3.61803+](records/dodinico/dodinico_n06.json) ≈ √5/2 + 5/2 | [1.55131+](records/icoindod/icoindod_n06.json) |
| 7 | [3.29102+](records/cubinoct/cubinoct_n07.json) | [1.79133+](records/octincub/octincub_n07.json) ≈ 19√2/15 | 1.79133 W | [3.85641+](records/dodinico/dodinico_n07.json) | [1.66853+](records/icoindod/icoindod_n07.json) |
| 8 | [3.41421+](records/cubinoct/cubinoct_n08.json) ≈ 2 + √2 | [1.79133+](records/octincub/octincub_n08.json) ≈ 19√2/15 | 1.79133 W | [3.96508+](records/dodinico/dodinico_n08.json) | [1.69778+](records/icoindod/icoindod_n08.json) |
| 9 | [3.61760+](records/cubinoct/cubinoct_n09.json) | [1.88561+](records/octincub/octincub_n09.json) ≈ (4√2)/3 | 1.88561 W | [4.02206+](records/dodinico/dodinico_n09.json) | [1.77163+](records/icoindod/icoindod_n09.json) |
| 10 | [3.66667+](records/cubinoct/cubinoct_n10.json) | [2.14936+](records/octincub/octincub_n10.json) ≈ 1801√2/1185 | 2.14936 W | [4.06524+](records/dodinico/dodinico_n10.json) ≈ (25 + 7√5)/10 | [1.81821+](records/icoindod/icoindod_n10.json) |
| 11 | [3.70710+](records/cubinoct/cubinoct_n11.json) ≈ (6 + √2)/2 | [2.19539+](records/octincub/octincub_n11.json) | 2.19540 W | [4.06524+](records/dodinico/dodinico_n11.json) ≈ (25 + 7√5)/10 | [1.86714+](records/icoindod/icoindod_n11.json) |
| 12 | [3.70710+](records/cubinoct/cubinoct_n12.json) ≈ (6 + √2)/2 | [2.29102+](records/octincub/octincub_n12.json) | 2.25949 L | [4.06524+](records/dodinico/dodinico_n12.json) ≈ (25 + 7√5)/10 | [1.87422+](records/icoindod/icoindod_n12.json) |
| 13 | [3.79737+](records/cubinoct/cubinoct_n13.json) | [2.33663+](records/octincub/octincub_n13.json) ✱ | 2.33667 L | [4.06524+](records/dodinico/dodinico_n13.json) ≈ (25 + 7√5)/10 | [1.90402+](records/icoindod/icoindod_n13.json) |
| 14 | [3.90429+](records/cubinoct/cubinoct_n14.json) | [2.35702+](records/octincub/octincub_n14.json) | 2.35702 W | [4.59694+](records/dodinico/dodinico_n14.json) | [1.97107+](records/icoindod/icoindod_n14.json) |
| 15 | [3.95305+](records/cubinoct/cubinoct_n15.json) | [2.41967+](records/octincub/octincub_n15.json) ✱ | 2.41976 W | [4.67481+](records/dodinico/dodinico_n15.json) | [2.00000+](records/icoindod/icoindod_n15.json) |
| 16 | [4.00052+](records/cubinoct/cubinoct_n16.json) | [2.45865+](records/octincub/octincub_n16.json) ✱ | 2.46211 W | [4.79245+](records/dodinico/dodinico_n16.json) | [2.05510+](records/icoindod/icoindod_n16.json) |
| 17 | [4.02915+](records/cubinoct/cubinoct_n17.json) | [2.48024+](records/octincub/octincub_n17.json) | 2.47487 L | [4.88916+](records/dodinico/dodinico_n17.json) | [2.09085+](records/icoindod/icoindod_n17.json) |
| 18 | [4.04898+](records/cubinoct/cubinoct_n18.json) | [2.48099+](records/octincub/octincub_n18.json) ✱ | 2.48257 W | [4.97123+](records/dodinico/dodinico_n18.json) | [2.16215+](records/icoindod/icoindod_n18.json) |
| 19 | [4.10658+](records/cubinoct/cubinoct_n19.json) | [2.55209+](records/octincub/octincub_n19.json) | 2.52683 W | [5.07936+](records/dodinico/dodinico_n19.json) | [2.20355+](records/icoindod/icoindod_n19.json) |
| 20 | [4.32269+](records/cubinoct/cubinoct_n20.json) | [2.57418+](records/octincub/octincub_n20.json) ✱ | 2.57792 W | [5.15760+](records/dodinico/dodinico_n20.json) | [2.24176+](records/icoindod/icoindod_n20.json) |
| 21 | [4.47061+](records/cubinoct/cubinoct_n21.json) | [2.58891+](records/octincub/octincub_n21.json) ✱ | 2.59285 L | [5.26142+](records/dodinico/dodinico_n21.json) | [2.28370+](records/icoindod/icoindod_n21.json) |
| 22 | [4.59310+](records/cubinoct/cubinoct_n22.json) | [2.60569+](records/octincub/octincub_n22.json) ✱ | 2.60591 W | [5.32240+](records/dodinico/dodinico_n22.json) | [2.29459+](records/icoindod/icoindod_n22.json) |
| 23 | [4.62576+](records/cubinoct/cubinoct_n23.json) | [2.62246+](records/octincub/octincub_n23.json) | 2.61533 W | [5.40195+](records/dodinico/dodinico_n23.json) | [2.34871+](records/icoindod/icoindod_n23.json) |
| 24 | [4.70710+](records/cubinoct/cubinoct_n24.json) ≈ √2/2 + 4 | [2.62792+](records/octincub/octincub_n24.json) ✱ | 2.63319 L | [5.47474+](records/dodinico/dodinico_n24.json) | [2.36541+](records/icoindod/icoindod_n24.json) |
| 25 | [4.70710+](records/cubinoct/cubinoct_n25.json) ≈ √2/2 + 4 | [2.63620+](records/octincub/octincub_n25.json) ✱ | 2.63622 W | [5.53087+](records/dodinico/dodinico_n25.json) | [2.39258+](records/icoindod/icoindod_n25.json) |
| 26 | [4.70710+](records/cubinoct/cubinoct_n26.json) ≈ √2/2 + 4 | [2.63986+](records/octincub/octincub_n26.json) ≈ 28√2/15 | 2.63986 W | [5.61552+](records/dodinico/dodinico_n26.json) | [2.42244+](records/icoindod/icoindod_n26.json) |
| 27 | [4.81053+](records/cubinoct/cubinoct_n27.json) | [2.63986+](records/octincub/octincub_n27.json) ≈ 28√2/15 | 2.63986 W | [5.66985+](records/dodinico/dodinico_n27.json) | [2.44475+](records/icoindod/icoindod_n27.json) |
| 28 | [4.82842+](records/cubinoct/cubinoct_n28.json) | [2.75731+](records/octincub/octincub_n28.json) ✱ | 2.75738 W | [5.73945+](records/dodinico/dodinico_n28.json) | [2.46823+](records/icoindod/icoindod_n28.json) |
| 29 | [4.89243+](records/cubinoct/cubinoct_n29.json) | [2.82842+](records/octincub/octincub_n29.json) ≈ 2√2 ✱ | 2.85384 W | [5.77917+](records/dodinico/dodinico_n29.json) | [2.47572+](records/icoindod/icoindod_n29.json) |
| 30 | [4.91981+](records/cubinoct/cubinoct_n30.json) | [2.88658+](records/octincub/octincub_n30.json) ✱ | 2.89186 W | [5.84833+](records/dodinico/dodinico_n30.json) | [2.49070+](records/icoindod/icoindod_n30.json) |
| 31 | [4.96097+](records/cubinoct/cubinoct_n31.json) | [2.93422+](records/octincub/octincub_n31.json) |  | [5.90253+](records/dodinico/dodinico_n31.json) | [2.50914+](records/icoindod/icoindod_n31.json) |
| 32 | [4.99853+](records/cubinoct/cubinoct_n32.json) | [2.99146+](records/octincub/octincub_n32.json) |  | [5.94969+](records/dodinico/dodinico_n32.json) | [2.52216+](records/icoindod/icoindod_n32.json) |
| 33 | [5.02843+](records/cubinoct/cubinoct_n33.json) | [3.03494+](records/octincub/octincub_n33.json) |  | [5.96371+](records/dodinico/dodinico_n33.json) | [2.53601+](records/icoindod/icoindod_n33.json) |
| 34 | [5.05251+](records/cubinoct/cubinoct_n34.json) | [3.07374+](records/octincub/octincub_n34.json) |  | [5.98812+](records/dodinico/dodinico_n34.json) | [2.58115+](records/icoindod/icoindod_n34.json) |
| 35 | [5.06974+](records/cubinoct/cubinoct_n35.json) | [3.08910+](records/octincub/octincub_n35.json) |  | [6.01397+](records/dodinico/dodinico_n35.json) | [2.62753+](records/icoindod/icoindod_n35.json) |
| 36 | [5.08974+](records/cubinoct/cubinoct_n36.json) | [3.11859+](records/octincub/octincub_n36.json) |  | [6.14069+](records/dodinico/dodinico_n36.json) | [2.67096+](records/icoindod/icoindod_n36.json) |
| 37 | [5.10324+](records/cubinoct/cubinoct_n37.json) | [3.15314+](records/octincub/octincub_n37.json) |  | [6.21295+](records/dodinico/dodinico_n37.json) | [2.68581+](records/icoindod/icoindod_n37.json) |
| 38 | [5.13601+](records/cubinoct/cubinoct_n38.json) | [3.18237+](records/octincub/octincub_n38.json) |  | [6.26922+](records/dodinico/dodinico_n38.json) | [2.69655+](records/icoindod/icoindod_n38.json) |
| 39 | [5.17002+](records/cubinoct/cubinoct_n39.json) | [3.23286+](records/octincub/octincub_n39.json) |  | [6.30736+](records/dodinico/dodinico_n39.json) | [2.72805+](records/icoindod/icoindod_n39.json) |
| 40 | [5.19194+](records/cubinoct/cubinoct_n40.json) | [3.24518+](records/octincub/octincub_n40.json) |  | [6.32472+](records/dodinico/dodinico_n40.json) | [2.74184+](records/icoindod/icoindod_n40.json) |
| 41 | [5.21960+](records/cubinoct/cubinoct_n41.json) | [3.29094+](records/octincub/octincub_n41.json) |  | [6.34609+](records/dodinico/dodinico_n41.json) | [2.75334+](records/icoindod/icoindod_n41.json) |
| 42 | [5.23444+](records/cubinoct/cubinoct_n42.json) | [3.30790+](records/octincub/octincub_n42.json) |  | [6.39497+](records/dodinico/dodinico_n42.json) | [2.79183+](records/icoindod/icoindod_n42.json) |
| 43 | [5.27348+](records/cubinoct/cubinoct_n43.json) | [3.32591+](records/octincub/octincub_n43.json) |  | [6.43814+](records/dodinico/dodinico_n43.json) | [2.80895+](records/icoindod/icoindod_n43.json) |
| 44 | [5.27349+](records/cubinoct/cubinoct_n44.json) | [3.33882+](records/octincub/octincub_n44.json) |  | [6.47795+](records/dodinico/dodinico_n44.json) | [2.83489+](records/icoindod/icoindod_n44.json) |
| 45 | [5.62314+](records/cubinoct/cubinoct_n45.json) | [3.35546+](records/octincub/octincub_n45.json) |  | [6.54512+](records/dodinico/dodinico_n45.json) | [2.85393+](records/icoindod/icoindod_n45.json) |
| 46 | [5.63141+](records/cubinoct/cubinoct_n46.json) | [3.38464+](records/octincub/octincub_n46.json) |  | [6.56306+](records/dodinico/dodinico_n46.json) | [2.88406+](records/icoindod/icoindod_n46.json) |
| 47 | [5.66356+](records/cubinoct/cubinoct_n47.json) | [3.39126+](records/octincub/octincub_n47.json) |  | [6.60566+](records/dodinico/dodinico_n47.json) | [2.89596+](records/icoindod/icoindod_n47.json) |
| 48 | [5.67251+](records/cubinoct/cubinoct_n48.json) | [3.41386+](records/octincub/octincub_n48.json) |  | [6.61803+](records/dodinico/dodinico_n48.json) | [2.91933+](records/icoindod/icoindod_n48.json) |
| 49 | [5.85997+](records/cubinoct/cubinoct_n49.json) | [3.43046+](records/octincub/octincub_n49.json) |  | [6.62063+](records/dodinico/dodinico_n49.json) | [2.94019+](records/icoindod/icoindod_n49.json) |
| 50 | [5.86875+](records/cubinoct/cubinoct_n50.json) | [3.43064+](records/octincub/octincub_n50.json) |  | [6.64468+](records/dodinico/dodinico_n50.json) | [2.94823+](records/icoindod/icoindod_n50.json) |
| 51 | [5.89026+](records/cubinoct/cubinoct_n51.json) | [3.44003+](records/octincub/octincub_n51.json) |  | [6.64774+](records/dodinico/dodinico_n51.json) | [2.97207+](records/icoindod/icoindod_n51.json) |
| 52 | [5.90152+](records/cubinoct/cubinoct_n52.json) | [3.44999+](records/octincub/octincub_n52.json) |  | [6.66380+](records/dodinico/dodinico_n52.json) | [2.99335+](records/icoindod/icoindod_n52.json) |
| 53 | [5.98563+](records/cubinoct/cubinoct_n53.json) | [3.48839+](records/octincub/octincub_n53.json) |  | [6.66812+](records/dodinico/dodinico_n53.json) | [2.99714+](records/icoindod/icoindod_n53.json) |
| 54 | [6.05501+](records/cubinoct/cubinoct_n54.json) | [3.48839+](records/octincub/octincub_n54.json) |  | [6.67170+](records/dodinico/dodinico_n54.json) | [3.01843+](records/icoindod/icoindod_n54.json) |
| 55 | [6.05501+](records/cubinoct/cubinoct_n55.json) | [3.48839+](records/octincub/octincub_n55.json) |  | [6.72803+](records/dodinico/dodinico_n55.json) | [3.03097+](records/icoindod/icoindod_n55.json) |
| 56 | [6.05501+](records/cubinoct/cubinoct_n56.json) | [3.48839+](records/octincub/octincub_n56.json) |  | [6.86953+](records/dodinico/dodinico_n56.json) | [3.04006+](records/icoindod/icoindod_n56.json) |
| 57 | [6.05501+](records/cubinoct/cubinoct_n57.json) | [3.48839+](records/octincub/octincub_n57.json) |  | [7.02913+](records/dodinico/dodinico_n57.json) | [3.04325+](records/icoindod/icoindod_n57.json) |
| 58 | [6.12372+](records/cubinoct/cubinoct_n58.json) | [3.48839+](records/octincub/octincub_n58.json) |  | [7.08980+](records/dodinico/dodinico_n58.json) | [3.07123+](records/icoindod/icoindod_n58.json) |
| 59 | [6.14690+](records/cubinoct/cubinoct_n59.json) | [3.48839+](records/octincub/octincub_n59.json) |  | [7.14427+](records/dodinico/dodinico_n59.json) | [3.09613+](records/icoindod/icoindod_n59.json) |
| 60 | [6.16724+](records/cubinoct/cubinoct_n60.json) | [3.48839+](records/octincub/octincub_n60.json) |  | [7.16996+](records/dodinico/dodinico_n60.json) | [3.09731+](records/icoindod/icoindod_n60.json) |
| 61 | [6.16724+](records/cubinoct/cubinoct_n61.json) | [3.48839+](records/octincub/octincub_n61.json) |  | [7.25164+](records/dodinico/dodinico_n61.json) | [3.16285+](records/icoindod/icoindod_n61.json) |
| 62 | [6.16724+](records/cubinoct/cubinoct_n62.json) | [3.48839+](records/octincub/octincub_n62.json) |  | [7.28549+](records/dodinico/dodinico_n62.json) | [3.18154+](records/icoindod/icoindod_n62.json) |
| 63 | [6.16725+](records/cubinoct/cubinoct_n63.json) | [3.48839+](records/octincub/octincub_n63.json) |  | [7.32427+](records/dodinico/dodinico_n63.json) | [3.18311+](records/icoindod/icoindod_n63.json) |
| 64 | [6.16725+](records/cubinoct/cubinoct_n64.json) | [3.48839+](records/octincub/octincub_n64.json) |  | [7.36280+](records/dodinico/dodinico_n64.json) | [3.19209+](records/icoindod/icoindod_n64.json) |
| 65 | [6.16725+](records/cubinoct/cubinoct_n65.json) | [3.75596+](records/octincub/octincub_n65.json) |  | [7.39811+](records/dodinico/dodinico_n65.json) | [3.23121+](records/icoindod/icoindod_n65.json) |
| 66 | [6.21736+](records/cubinoct/cubinoct_n66.json) | [3.76881+](records/octincub/octincub_n66.json) |  | [7.46543+](records/dodinico/dodinico_n66.json) | [3.24707+](records/icoindod/icoindod_n66.json) |
| 67 | [6.21991+](records/cubinoct/cubinoct_n67.json) | [3.76927+](records/octincub/octincub_n67.json) |  | [7.48505+](records/dodinico/dodinico_n67.json) | [3.27954+](records/icoindod/icoindod_n67.json) |
| 68 | [6.27063+](records/cubinoct/cubinoct_n68.json) | [3.76927+](records/octincub/octincub_n68.json) |  | [7.48827+](records/dodinico/dodinico_n68.json) | [3.29509+](records/icoindod/icoindod_n68.json) |
| 69 | [6.28588+](records/cubinoct/cubinoct_n69.json) | [3.77112+](records/octincub/octincub_n69.json) |  | [7.57613+](records/dodinico/dodinico_n69.json) | [3.32327+](records/icoindod/icoindod_n69.json) |
| 70 | [6.31356+](records/cubinoct/cubinoct_n70.json) | [3.77123+](records/octincub/octincub_n70.json) ≈ (8√2)/3 |  | [7.59604+](records/dodinico/dodinico_n70.json) | [3.32588+](records/icoindod/icoindod_n70.json) |
| 71 | [6.34388+](records/cubinoct/cubinoct_n71.json) | [3.77123+](records/octincub/octincub_n71.json) ≈ (8√2)/3 |  | [7.59882+](records/dodinico/dodinico_n71.json) | [3.33352+](records/icoindod/icoindod_n71.json) |
| 72 | [6.34388+](records/cubinoct/cubinoct_n72.json) | [3.77123+](records/octincub/octincub_n72.json) ≈ (8√2)/3 |  | [7.64848+](records/dodinico/dodinico_n72.json) | [3.35448+](records/icoindod/icoindod_n72.json) |
| 73 | [6.35147+](records/cubinoct/cubinoct_n73.json) | [3.77123+](records/octincub/octincub_n73.json) ≈ (8√2)/3 |  | [7.67516+](records/dodinico/dodinico_n73.json) | [3.35450+](records/icoindod/icoindod_n73.json) |
| 74 | [6.35147+](records/cubinoct/cubinoct_n74.json) | [3.82483+](records/octincub/octincub_n74.json) |  | [7.68093+](records/dodinico/dodinico_n74.json) | [3.42676+](records/icoindod/icoindod_n74.json) |
| 75 | [6.36851+](records/cubinoct/cubinoct_n75.json) | [3.87309+](records/octincub/octincub_n75.json) |  | [7.74867+](records/dodinico/dodinico_n75.json) | [3.43211+](records/icoindod/icoindod_n75.json) |
| 76 | [6.36851+](records/cubinoct/cubinoct_n76.json) | [3.87517+](records/octincub/octincub_n76.json) |  | [7.78875+](records/dodinico/dodinico_n76.json) | [3.44638+](records/icoindod/icoindod_n76.json) |
| 77 | [6.36851+](records/cubinoct/cubinoct_n77.json) | [3.90959+](records/octincub/octincub_n77.json) |  | [7.86495+](records/dodinico/dodinico_n77.json) | [3.46954+](records/icoindod/icoindod_n77.json) |
| 78 | [6.36851+](records/cubinoct/cubinoct_n78.json) | [3.93854+](records/octincub/octincub_n78.json) |  | [7.88490+](records/dodinico/dodinico_n78.json) | [3.48096+](records/icoindod/icoindod_n78.json) |
| 79 | [6.36851+](records/cubinoct/cubinoct_n79.json) | [3.96865+](records/octincub/octincub_n79.json) |  | [7.91400+](records/dodinico/dodinico_n79.json) | [3.48703+](records/icoindod/icoindod_n79.json) |
| 80 | [6.39629+](records/cubinoct/cubinoct_n80.json) | [3.99367+](records/octincub/octincub_n80.json) |  | [7.93759+](records/dodinico/dodinico_n80.json) | [3.48703+](records/icoindod/icoindod_n80.json) |
| 81 | [6.41149+](records/cubinoct/cubinoct_n81.json) | [4.02321+](records/octincub/octincub_n81.json) |  | [7.94869+](records/dodinico/dodinico_n81.json) | [3.48789+](records/icoindod/icoindod_n81.json) |
| 82 | [6.41149+](records/cubinoct/cubinoct_n82.json) | [4.03904+](records/octincub/octincub_n82.json) |  | [7.97765+](records/dodinico/dodinico_n82.json) | [3.50008+](records/icoindod/icoindod_n82.json) |
| 83 | [6.44465+](records/cubinoct/cubinoct_n83.json) | [4.05349+](records/octincub/octincub_n83.json) |  | [8.00561+](records/dodinico/dodinico_n83.json) | [3.50257+](records/icoindod/icoindod_n83.json) |
| 84 | [6.44465+](records/cubinoct/cubinoct_n84.json) | [4.08063+](records/octincub/octincub_n84.json) |  | [8.01460+](records/dodinico/dodinico_n84.json) | [3.50626+](records/icoindod/icoindod_n84.json) |
| 85 | [6.68668+](records/cubinoct/cubinoct_n85.json) | [4.08248+](records/octincub/octincub_n85.json) ≈ 5√6/3 |  | [8.06634+](records/dodinico/dodinico_n85.json) | [3.51123+](records/icoindod/icoindod_n85.json) |
| 86 | [6.68668+](records/cubinoct/cubinoct_n86.json) | [4.08248+](records/octincub/octincub_n86.json) ≈ 5√6/3 |  | [8.10154+](records/dodinico/dodinico_n86.json) | [3.51577+](records/icoindod/icoindod_n86.json) |
| 87 | [6.68668+](records/cubinoct/cubinoct_n87.json) | [4.08248+](records/octincub/octincub_n87.json) ≈ 5√6/3 |  | [8.10309+](records/dodinico/dodinico_n87.json) | [3.53163+](records/icoindod/icoindod_n87.json) |
| 88 | [6.73175+](records/cubinoct/cubinoct_n88.json) | [4.08248+](records/octincub/octincub_n88.json) ≈ 5√6/3 |  | [8.13935+](records/dodinico/dodinico_n88.json) | [3.57462+](records/icoindod/icoindod_n88.json) |
| 89 | [6.93699+](records/cubinoct/cubinoct_n89.json) | [4.08248+](records/octincub/octincub_n89.json) ≈ 5√6/3 |  | [8.15072+](records/dodinico/dodinico_n89.json) | [3.58747+](records/icoindod/icoindod_n89.json) |
| 90 | [6.93699+](records/cubinoct/cubinoct_n90.json) | [4.08248+](records/octincub/octincub_n90.json) |  | [8.18610+](records/dodinico/dodinico_n90.json) | [3.59167+](records/icoindod/icoindod_n90.json) |
| 91 | [6.94958+](records/cubinoct/cubinoct_n91.json) | [4.08248+](records/octincub/octincub_n91.json) |  | [8.19376+](records/dodinico/dodinico_n91.json) | [3.59167+](records/icoindod/icoindod_n91.json) |
| 92 | [6.96911+](records/cubinoct/cubinoct_n92.json) | [4.10095+](records/octincub/octincub_n92.json) |  | [8.21187+](records/dodinico/dodinico_n92.json) | [3.62229+](records/icoindod/icoindod_n92.json) |
| 93 | [6.96911+](records/cubinoct/cubinoct_n93.json) | [4.10303+](records/octincub/octincub_n93.json) |  | [8.24003+](records/dodinico/dodinico_n93.json) | [3.62229+](records/icoindod/icoindod_n93.json) |
| 94 | [7.02054+](records/cubinoct/cubinoct_n94.json) | [4.10303+](records/octincub/octincub_n94.json) |  | [8.31216+](records/dodinico/dodinico_n94.json) | [3.63875+](records/icoindod/icoindod_n94.json) |
| 95 | [7.02054+](records/cubinoct/cubinoct_n95.json) | [4.11199+](records/octincub/octincub_n95.json) |  | [8.31302+](records/dodinico/dodinico_n95.json) | [3.63875+](records/icoindod/icoindod_n95.json) |
| 96 | [7.02054+](records/cubinoct/cubinoct_n96.json) | [4.11417+](records/octincub/octincub_n96.json) |  | [8.33228+](records/dodinico/dodinico_n96.json) | [3.66610+](records/icoindod/icoindod_n96.json) |
| 97 | [7.02207+](records/cubinoct/cubinoct_n97.json) | [4.11509+](records/octincub/octincub_n97.json) |  | [8.35992+](records/dodinico/dodinico_n97.json) | [3.66610+](records/icoindod/icoindod_n97.json) |
| 98 | [7.02943+](records/cubinoct/cubinoct_n98.json) | [4.22628+](records/octincub/octincub_n98.json) |  | [8.35992+](records/dodinico/dodinico_n98.json) | [3.67233+](records/icoindod/icoindod_n98.json) |
| 99 | [7.02943+](records/cubinoct/cubinoct_n99.json) | [4.23011+](records/octincub/octincub_n99.json) |  | [8.35992+](records/dodinico/dodinico_n99.json) | [3.67978+](records/icoindod/icoindod_n99.json) |
| 100 | [7.02943+](records/cubinoct/cubinoct_n100.json) | [4.24270+](records/octincub/octincub_n100.json) |  | [8.35992+](records/dodinico/dodinico_n100.json) | [3.71647+](records/icoindod/icoindod_n100.json) |

previous: F = E. Friedman, W = R. Walsh, L = H. Lin, N = Y. Nakajima, T = trivial grid packing; source dates and attribution are in docs/references.json. ✱ = more than the printed precision below a registered reference (usually 1e-5; 1e-3 for cube n=13). These search-archive tables do not include all external or community candidates; the website selects across all three registries.

**Cubes in a cube vs published values** (n = 2–33): better at 11, 28; equal at 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33; behind at none.

**Octahedra in a cube vs published values** (n = 2–30): better at 13, 15, 16, 18, 20, 21, 22, 24, 25, 28, 29, 30; equal at 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 26, 27; behind at 12 (+1.40%), 17 (+0.22%), 19 (+1.00%), 23 (+0.27%).
<!-- RESULTS:END -->

Mostly upper bounds: the 85 records proven optimal in Lean (for example 2–8 cubes in a cube, 2–32 five-cubes in a five-cube) are listed in [docs/OPTIMALITY.md](docs/OPTIMALITY.md); see also [docs/MATH.md](docs/MATH.md) §1 and §8. Highlights:
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
