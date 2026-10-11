# Polyhedral packing manuscript and encyclopedia review packet

Prepared **11 October 2026** for Alejandro Zarzuelo Urdiales. Scientific inputs are frozen at [`e15b496ae7306287e0e70bb5b14be79f5dfdde84`](https://github.com/alejandrozu/platonic-packing/tree/e15b496ae7306287e0e70bb5b14be79f5dfdde84). This package is for author review. No journal, preprint server, Wikipedia, Commons, or new website submission has been made.

## Read the two papers

| Paper | Purpose | Formats |
|---|---|---|
| **Certified finite packings of Platonic solids** | Scientific reconstruction of the construction and its development: Nakajima's starting point, generalized homotopy, geometry, tightening, jiggling, archive search, certification, experiments, failures, and results | [PDF](paper-1-methods.pdf), [Markdown](paper-1-methods.md), [LaTeX](paper-1-methods.tex) |
| **Finite polyhedral fits** | Dense cross-family analysis: jumps, plateaus, scale and volume increments, symmetry-correct orientations, contact graphs, operational grains, construction classes, and evidence for future proof targets | [PDF](paper-2-patterns.pdf), [Markdown](paper-2-patterns.md), [LaTeX](paper-2-patterns.tex) |

The dataset covers **nine ordered shape pairs**, every count from **2 to 40**, **351 constructions**, **7,371 pieces**, and **95,940 within-record piece pairs**. It contains a single piece species in each configuration. It does not contain all 25 Platonic pairs or two-species mixtures. Both papers distinguish the archived feasible upper bound from numerical touching estimates, conjectured formulas, and the unknown optimum.

## Findings worth reviewing first

- Dodecahedra in a dodecahedron at counts **29–33** share exactly the same stored certified scale, `3.7470909531576`. Both these feasible bounds and their orientation/contact structure can be inspected. This is not a proof of an optimal-scale plateau.
- The archived octahedron-in-octahedron scale jumps about **25% in edge length** from six to seven pieces, corresponding to about **95.3% in container volume**. The patterns paper interprets this as an archive capacity transition without asserting global infeasibility below it.
- Repeated orientation and a spatially connected orientation domain are different. At count 33, the dodecahedral example has seven orientation components under the stated angular criterion, while all 33 operational grains are singletons under the stated contact criterion.
- Raw edge ratios can mislead across dual mixed pairs. Volume-normalized scale and occupied fraction reveal much closer efficiencies than the raw edge lengths suggest.

The findings are numerical structural analyses of exactly feasible configurations. Physical grain growth and crystallization remain research motivations, requiring an appropriate physical model and further evidence.

## Visual material and reproducibility

Open [the frozen rotating explorer](packing-explorer.html) locally. It includes the nine-family dataset, rotation, slicing, and piece inspection, and links to immutable source coordinate files. Its displayed coordinates are rounded; exact certification applies to the full-precision originals. Three.js and fonts load from external CDNs. The existing public project viewer has not been changed or redeployed by this task.

The [analysis directory](analysis/README.md) includes a portable Python script, every metric, per-pair measurements, plateau intervals, largest jumps, descriptive correlations, input hashes, and three figure sets in PNG/SVG/PDF. Seven [STL models](models/) illustrate selected plateau, jump, and lattice examples; these are visualization meshes and were not uploaded anywhere. [MIT attribution for the reused explorer](LICENSE-viewer.txt) is preserved.

[Fresh verification](research/verification.json) reran **both checkers on all 351 records**, checked declared population against pose count, and recorded each input SHA-256. **351 passed, zero failed**. The original geometric regression suite also passed: 1,500 gradient cases, with maximum smooth discrepancy about `1.43e-9`. The [technical review](research/technical-review.md) and [geometry crosscheck](research/geometry-crosscheck.json) document symmetry invariance, group closure, and 3,082 separated-distance comparisons from 3,511 requests. Maximum distance disagreement was about `2e-15`; no contact classification differed at the three tested tolerances.

To rerun the data checks without changing the original research archive:

```bash
git clone https://github.com/alejandrozu/platonic-packing.git frozen-source
git -C frozen-source checkout e15b496ae7306287e0e70bb5b14be79f5dfdde84
python research/verify_snapshot.py --repo frozen-source --out verification-rerun.json
python analysis/analyze_records.py --repo frozen-source --out regenerated-analysis
```

Run those commands from this packet's directory; Python and Git must be available. Certificate replay uses the Python standard library. Structural analysis requires NumPy, and plotting additionally requires Matplotlib. Source environment versions and all thresholds are recorded in `analysis/analysis-metadata.json`. The full historical adaptive search was not rerun; its archive pools and runtime environment were not fully preserved.

Both PDFs were built with the already-installed Tectonic 0.17.0 and inspected after Poppler rendering. The built-in LaTeX compiler returned a platform-directory error, so native compilation is unverified. The editable LaTeX sources remain available; their figure guards and inline-data fallback allow a standalone text/plot preview if companion PNGs are unavailable. Build and review checks are recorded in [build-checks.json](research/build-checks.json).

## Wikipedia draft and next publication step

Read the [annotated Wikipedia draft](wikipedia-polyhedral-fits.md), or use the [clean MediaWiki source](wikipedia-polyhedral-fits.wiki). The working article title is **Packing polyhedra in polyhedral containers**; “polyhedral fits” is used descriptively, since established usage of that title has not been demonstrated. The draft covers finite and infinite problems, single-object inclusion, cubes, octahedra and tetrahedra in cubes, general polyhedral methods, shape-pair taxonomy, validation, and physical context. The separate editorial annex explains what evidence would be needed to include the new archive findings.

The literature check found existing related coverage in Wikipedia's *Packing problems* and *Tetrahedron packing* articles, rather than establishing that the subject has never been covered. New results cannot become encyclopedia facts through a GitHub upload alone: significant independent sources and careful treatment of primary research are needed. The rich repository viewer remains separate from the encyclopedia; portable STL and static figures could support a later, separately reviewed Wikimedia workflow.

The fastest recommended scholarly path is author review, a frozen reproducibility release, and **arXiv dissemination**, followed by peer review. arXiv endorsement and moderation apply; announcement is not guaranteed immediately, and **12 October 2026 is a listed deferred-mailing holiday**. **Experimental Mathematics** is the strongest apparent fit for the patterns paper; **Journal of Computational Geometry** is a fee-free alternative for an algorithmic geometry paper. The [verified literature and publication plan](research/literature-and-publication.md) gives sources, scope, current timing, and other options. [Public Twitter context](research/social-context.md) records the relevant replies and newer announced cube comparisons without treating them as independently checked geometry.

Before external submission, the author should confirm the name, affiliation, acknowledgments, AI-assistance statement, release version, scope, and venue. The historical software was developed with Claude under the author's direction; OpenAI Codex assisted this packet's source review, structural analysis, drafting, and checks. Human authorship and responsibility belong to the author who reviews and submits the work.
