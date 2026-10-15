# Shape continuation for convex-polytope packing

This directory contains the proposed joint-author manuscript **Shape Continuation for Convex-Polytope Packing: Generalization and Lean-Verified Certificate Principles**, dated 16 October 2026, and its reproducibility materials.

Proposed authors: **Yohei Nakajima and Alejandro Zarzuelo Urdiales**. The author list is included at Alejandro's request for discussion with Yohei. This repository copy does not assert Yohei's approval of the manuscript, its author order, or a submission. It has not been submitted to arXiv or sent to him by the drafting agent. The accompanying commit supplies a public version timestamp, not a journal acceptance or priority adjudication.

## Read

- [Paper (PDF)](manuscript.pdf)
- [Editable LaTeX](manuscript.tex)
- [Lean sources, exact scope and reproduction](formal/README.md)
- [Actual Lean build and axiom audit](formal/verification.json)
- [Five native witnesses and complete source geometry](data/sources/records/)
- [Frozen per-case catalogue and provenance](data/catalogue-snapshot.csv)
- [Complete selected-site data, compressed](data/records.json.gz)
- [Reproduction of snapshot counts, benchmark and certificate checks](reproduce.py)
- [Scientific figure and generation code](figures/)
- [Source links and byte hashes](data/source-manifest.json)
- [Validation receipt](validation.json)

## Scientific scope

The paper explains the 3D non-tangential erosion/dilation path, the supported regular 4D–6D implementation, archive search moves, structured seeds, composition, exact witness checking, and community provenance. It cites Nakajima's arXiv paper, the three earlier DOI publications, primary packing literature, the repository's research notes and independent contributors.

The **Lean-checked certificate-soundness core** contains 15 audited theorems and one completely instantiated rational two-cube witness. It proves meaningful geometric results, but does **not** formally import the catalogue, verify the production JSON/parser/interval code, prove all rigid-placement representations, or prove optimality. See `formal/README.md` for the precise boundary.

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

For the formal project, with Lean's `elan`/Lake available:

```sh
cd formal
lake update
lake exe cache get
lake build
lake env lean Audit.lean
```

To regenerate the figure, install NumPy/Matplotlib and run `python figures/render_examples.py`. To compile the manuscript, run `tectonic manuscript.tex` from this directory, or use a LaTeX installation with `latexmk -pdf manuscript.tex`. The bibliography is embedded; no BibTeX step is needed. `arxiv-source.zip` contains only the LaTeX source and figure required for a later author-approved submission.

The actual local Lean verification reused installed Lean 4.31.0 and matching read-only mathlib object files; the compiler, dependency commit, source hashes, exit codes and theorem axiom report are recorded. No toolchain installation or claim of a fresh download is implied.

Source witnesses and copied upstream modules retain their original provenance and repository licensing. Figures were drawn from the frozen coordinates without altering positions, orientations or scale. Colors distinguish pieces, not computed orientation classes. AI tools are described in the manuscript's methodology section.
