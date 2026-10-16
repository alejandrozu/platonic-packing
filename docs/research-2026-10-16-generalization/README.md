# Shape continuation for convex-polytope packing

This directory contains the proposed joint-author manuscript **Shape Continuation for Convex-Polytope Packing: Generalization and Lean-Verified Catalogue Certificates**, dated 16 October 2026, and its reproducibility materials.

Proposed authors: **Yohei Nakajima and Alejandro Zarzuelo Urdiales**. The author list is included at Alejandro's request for discussion with Yohei. This repository copy does not assert Yohei's approval of the manuscript, its author order, or a submission. It has not been submitted to arXiv or sent to him by the drafting agent. The accompanying commit supplies a public version timestamp, not a journal acceptance or priority adjudication.

## Read

- [Paper (PDF)](manuscript.pdf)
- [Editable LaTeX](manuscript.tex)
- [Lean sources, exact scope and reproduction](formal/README.md)
- [Actual Lean build and axiom audit](formal/verification.json)
- [Geometric continuation in every finite dimension](formal/PackingCertificates/Extensions/GenericDimension.lean)
- [Quantitative wall, pair and rigid-pose error budgets](formal/PackingCertificates/Extensions/Clearance.lean)
- [Exact support identity and orientation attenuation](formal/PackingCertificates/Extensions/SupportIdentity.lean)
- [Combined analytic proof build and 36 axiom audits](formal/extension-clearance-support-verification.json)
- [Formal support-query complexity bounds](formal/PackingCertificates/Extensions/Complexity.lean)
- [Orthoplex and 24-cell coordinate-hull identities](formal/PackingCertificates/Extensions/NDIdentity.lean)
- [Algebraic-coordinate certificate method and completed coverage](formal/catalogue/algebraic/README.md)
- [Per-record Lean coverage and precise limits](formal/catalogue/coverage.md)
- [Hash-matched verified catalogue manifest](formal/catalogue/verified-catalogue.json)
- [Frozen rational-cohort input manifest](formal/catalogue/inputs/source-manifest.json)
- [Five native witnesses and complete source geometry](data/sources/records/)
- [Frozen per-case catalogue and provenance](data/catalogue-snapshot.csv)
- [Complete selected-site data, compressed](data/records.json.gz)
- [Reproduction of snapshot counts, benchmark and certificate checks](reproduce.py)
- [Scientific figure and generation code](figures/)
- [Source links and byte hashes](data/source-manifest.json)
- [Validation receipt](validation.json)

## Scientific scope

The paper explains the 3D non-tangential erosion/dilation path, the supported regular 4D–6D implementation, archive search moves, structured seeds, composition, exact witness checking, and community provenance. It cites Nakajima's arXiv paper, the three earlier DOI publications, primary packing literature, the repository's research notes and independent contributors.

The new geometric theorems apply in every finite Euclidean dimension, without regularity or facet tangency assumptions. The paper separates that result from the dimensions supported by the numerical search and from optimizer convergence. It derives per-step and finite-budget simulation bounds in piece count, dimension, vertices, edges and facets. Lean proves the finite support-walk bounds used in that analysis; the whole simulator's execution time is not formally verified.

Two further Lean modules establish quantitative perturbation guarantees and the exact support-function identity behind the blend. Coordinate error at most `epsilon` changes a projection by at most `epsilon * sum(abs(normal))`; sufficient wall slack and a strict pair-gap budget preserve the complete hull packing. An affine-pose lemma supplies `epsilon = alpha + beta * L` from translation and matrix-entry errors and a canonical-vertex L1 bound. Rigid congruence still requires proper pose matrices. The support identity and its exact `1 - tau` orientation factor apply to every nonempty compact template in a real inner-product space, including every finite Euclidean dimension. The combined receipt contains 36 audited declarations, including 14 named endpoint and counterexample regression groups. These are generic conditional theorems; no numerical tolerance radius is asserted for every catalogue record, and no energy-gradient or optimization-performance result is inferred.

The Lean extension verifies **532 actual frozen catalogue records across all 140 problem families in dimensions 3–6**: all 402 selected rational certificates (99 cube-in-cube and 303 higher-dimensional records), plus one two-piece witness from each of the other 130 families (85 in 3D and 45 in 4D–6D). The proofs cover 11,056 rigid pieces, 163,900 placed vertices and every one of 235,592 unordered pairs. They establish source-bound proper rotations, preservation of squared Euclidean distances, whole-body containment and pairwise separation. The original two-cube example remains a regression test. This verifies selected witnesses in every frozen family, not all 10,398 coordinate records or the changing live bests. Original construction credits remain in the portable manifests. See `formal/README.md` for the trust boundary and reproduction commands.

An additional algebraic-coordinate route defines exact real vertices using isolated roots and checked interval enclosures. It proves actual container-hull membership through affine-basis certificates and retains irrational edge normalization. The higher-dimensional quadratic-coordinate route checks supplied exact inverse matrices in cubic arithmetic work per basis, avoiding a factorial determinant expansion. Its manifests distinguish prepared witnesses from successful source-bound kernel builds.

The kernel checks the supplied exact literals and their geometric consequences. JSON parsing and source transcription have a separate audit; the optimizer, production interval implementation and global optimality are outside this verification. Lean identifies the hypercube templates with coordinate boxes, the orthoplex arrays with the convex hull of the signed coordinate vectors, and the 24-cell array with the convex hull of vectors having two signed nonzero unit coordinates. A further leaf checks selected exact reference-edge distances for twelve higher-dimensional templates and all 45 additional witnesses' positive edge-conversion identities. A separate exact Python audit checks all 2,490 listed edges. Complete named-solid, face and edge-adjacency classification remains outside the formal proof. The new Lean interval library is separate from the production Python certifier.

The expanded computational freeze is commit `1abc63218db34cea95802aeb3b6d4a6b6fe1c61b`, with site data version `538e4f4362be3be9`. It has 140 problems, 10,404 populated cases, 10,398 selected coordinate witnesses marked exact-certified, and six source-only bounds. These counts include imported and community constructions. They are not a count of new world records or Lean-certified numerical cases.

The historical Round-D cohort has 40 cases, 1,824 valid attempts, and 40,751.5 summed per-attempt elapsed seconds. “Worker-hours” are summed elapsed wall-clock intervals, not measured CPU utilization or total campaign duration. References/pools evolved between attempts. The manuscript therefore reports a descriptive internal comparison, not a causal continuation ablation.

## Earlier DOI publications

1. [Original methods paper](https://doi.org/10.5281/zenodo.23306098).
2. [Patterns and structural analysis](https://doi.org/10.5281/zenodo.23306126).
3. [Original 351-construction data/software release](https://doi.org/10.5281/zenodo.23306130).

The third is a dataset/software release, not a third research article. All three retain their original scope and freeze; none identifies the enlarged October 15 archive retrospectively.

## Reproduce

The data/certificate checks require only Python's standard library:

```sh
python reproduce.py
```

This verifies the compressed source hash, all packaged upstream-source hashes, the catalogue counts, the declared Round-D aggregation, and reruns the exact checkers on all five examples. It writes a separate `reproduction-report.json`; it does not overwrite the original build receipt.

For the generic formal library, with Lean's `elan`/Lake available:

```sh
cd formal
lake exe cache get
lake build
lake env lean Audit.lean
```

The default library build excludes individual catalogue instance modules, whose exact arithmetic can be expensive. Completed evidence is compressed under `formal/ci-evidence/published-402`, `published-85` and `published-45`. Run `python formal/evidence_bundle.py --cohort formal/ci-evidence/published-402` to validate a cohort, or add `--extract proof-inspection --environment ENVIRONMENT_ID` to inspect one immutable build namespace. The module manifest is an environment-scoped index. Fresh reruns regenerate local plans and receipts from frozen inputs in a separate working copy; `formal/README.md` gives the pinned core/support build, full 402-record shard driver and 85/45 algebraic driver commands. Unpacking inputs or sources alone does not establish verification.

To regenerate the figure, install NumPy/Matplotlib and run `python figures/render_examples.py`. To compile the manuscript, run `tectonic manuscript.tex` from this directory, or use a LaTeX installation with `latexmk -pdf manuscript.tex`. The bibliography is embedded; no BibTeX step is needed. `arxiv-source.zip` contains only the LaTeX source and figure required for a later author-approved submission.

The actual local Lean verification reused installed Lean 4.31.0 and matching read-only mathlib object files; the compiler, dependency commit, source hashes, exit codes and theorem axiom report are recorded. No toolchain installation or claim of a fresh download is implied.

Source witnesses and copied upstream modules retain their original provenance and repository licensing. Figures were drawn from the frozen coordinates without altering positions, orientations or scale. Colors distinguish pieces, not computed orientation classes. AI tools are described in the manuscript's methodology section.
