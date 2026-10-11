# Polyhedra in polyhedra packing: manuscripts, analysis, and reference article

Prepared **11 October 2026** by Alejandro Zarzuelo Urdiales. Scientific inputs are frozen at [`e15b496ae7306287e0e70bb5b14be79f5dfdde84`](https://github.com/alejandrozu/platonic-packing/tree/e15b496ae7306287e0e70bb5b14be79f5dfdde84). Everything in this packet is saved locally and in the project repository. No journal, preprint server, Wikipedia, Commons, or new website submission has been made.

## Papers

| Paper | Contents | Formats |
|---|---|---|
| **Certified finite packings of Platonic solids** | Construction and development: Nakajima's starting point, generalized homotopy, geometric distances, tightening, jiggling, archive search, exact certification, experiments, failures, and results | [PDF](paper-1-methods.pdf), [Markdown](paper-1-methods.md), [LaTeX](paper-1-methods.tex) |
| **Finite polyhedral fits** | Cross-family analysis of jumps, plateaus, volume-normalized scales, symmetry-reduced orientations, contacts, operational grains, and **20 testable hypotheses** | [PDF](paper-2-patterns.pdf), [Markdown](paper-2-patterns.md), [LaTeX](paper-2-patterns.tex) |

The papers have no draft watermark or front-matter tool credits. Computational tools are described within their methodology sections. The dataset covers nine ordered shape pairs, every count from 2 to 40, 351 constructions, 7,371 pieces, and 95,940 piece pairs. Each construction uses one particle species; the archive does not contain all 25 Platonic pairs or mixtures.

Paper 2's hypothesis section explains the observations and proposes tests for other shapes, counts, and conditions. The evidence distinguishes confirmed arrangements, measured descriptors, reusable constructions, and conjectures about optimal or near-optimal arrangements.

## Reference article and rotating constructions

Open **[Polyhedra in polyhedra packing](polyhedra-in-polyhedra-packing.html)** for the illustrated local article. It includes a slowly rotating construction, shape/count selectors, and two source-linked tables for counts 2–12: five identical-solid families and four distinct dual-solid families. The [Markdown article](wikipedia-polyhedral-fits.md) and [MediaWiki source](wikipedia-polyhedral-fits.wiki) contain the same text and tables, with a substantial cube-packing history and named, linked explanations of Nakajima's method and Zarzuelo Urdiales's generalization and analysis.

Tables use the best comparable results located in the cited sources. The attribution/precision key preserves the roles of Friedman, Walsh, Lin, Nakajima, and Zarzuelo Urdiales. Two superior external octahedra-in-cube entries, counts 11 and 12, have published diagrams but no located public pose files or originating manuscripts. Their diagrams and original catalogue are shown; no substitute 3D geometry is presented as their result. For the other seven families, no competing finite-container bounds were found in the targeted search, and the scope of that comparison remains explicit.

The [full explorer](packing-explorer.html) uses the full-precision stored poses, rotation, slicing, and immutable construction/certificate links. Its visual rendering is numerical; exact validity comes from the linked JSON and verifier. Three.js, MathJax, and fonts load from external CDNs. No existing public viewer has been redeployed by this task. [Viewer license attribution](LICENSE-viewer.txt) is retained.

Wikipedia supports neither arbitrary JavaScript nor this full application inside normal article wikitext. The HTML file is a local/repository article preview; the MediaWiki version links the external viewer. [Wikipedia editing notes](research/wikipedia-editing-notes.md) separately document source-weight, independent-review, and supported illustration considerations.

## The shell oddity and other findings

The 29–33 dodecahedron-in-dodecahedron constructions have the same certified scale, `3.7470909531576`. At 33 pieces, one central piece, 12 inner icosahedral positions, and 20 outer dodecahedral positions form a nested shell. The center and outer shell share an orientation; the inner shell supplies six antipodal orientation pairs. All 102 near contacts join dissimilar orientation classes, explaining why seven orientation components coexist with 33 singleton operational grains. Deleting only outer pieces accounts for the smaller plateau members and removes three contacts per deleted piece. This measured mechanism is reproduced in [hypothesis-evidence.json](research/hypothesis-evidence.json).

Other notable transitions include an approximately 25% edge/95.3% volume increase from six to seven octahedra in an octahedron, and close volume-normalized efficiencies when reversing the dodecahedron–icosahedron pair despite very different raw edge ratios. The hypotheses develop conditional explanations of capacity, shell completion, orientation interlocking, boundary accommodation, contact constraints, and how those mechanisms could extend beyond the sampled solids.

## Data and verification

The [analysis directory](analysis/README.md) includes all metrics, pair measurements, plateau intervals, jumps, correlations, input hashes, and three PNG/SVG/PDF figure sets. Seven [STL meshes](models/) illustrate selected constructions.

[Fresh verification](research/verification.json): **351 of 351 configurations passed** both exact and floating checkers, with declared population matching pose count. The original geometry suite passed 1,500 gradient cases. [Technical checks](research/technical-review.md) include proper-symmetry invariance and 3,082 separated-distance comparisons from 3,511 requests, with maximum disagreement about `2e-15` and no contact-classification differences. The new shell-evidence script reproduces its supplied JSON exactly. These checks establish stored feasibility and measurement consistency; the general optima remain unresolved.

From this packet's directory, with Python and Git installed:

```bash
git clone https://github.com/alejandrozu/platonic-packing.git frozen-source
git -C frozen-source checkout e15b496ae7306287e0e70bb5b14be79f5dfdde84
python research/verify_snapshot.py --repo frozen-source --out verification-rerun.json
python analysis/analyze_records.py --repo frozen-source --out regenerated-analysis
python research/hypothesis_evidence.py --repo frozen-source --analysis analysis --out hypothesis-rerun.json
```

Certificate replay and shell-evidence checks use the standard library. Structural analysis requires NumPy; plotting additionally requires Matplotlib. All source versions and thresholds are recorded. The full historical adaptive search was not repeated. PDFs were built with the existing Tectonic compiler and rendered for visual inspection; the built-in LaTeX compiler still returned a platform-directory error. [Build checks](research/build-checks.json) record the final PDF hashes and page counts.

## Rapid dissemination without relying on arXiv sponsorship

The [publication alternatives](research/dissemination-alternatives.md) confirm arXiv's two-submissions-per-calendar-month rule introduced on 1 October 2026. They compare routes that address the sponsorship and volume constraints:

- **Zenodo** is the fastest verified route to an archival DOI for the papers and frozen research package, without endorsement. Its CERN/OpenAIRE infrastructure provides durable citation and preservation.
- **HAL** offers a recognized academic manuscript archive with moderation normally taking a few days; its required affiliation metadata must be completed honestly, and independent-author handling remains a condition to confirm.
- **Preprints.org** accepts mathematics and technical/hypothesis papers, with typical screening of 24 working hours; screening is not mathematical peer review.
- **Experimental Mathematics** is the principal peer-review target for the patterns paper; **Journal of Computational Geometry** is a fee-free alternative for the methods paper. Review timing cannot be guaranteed.

The combination of a permanent archive and journal review gives both rapid access and an opportunity for independent recognition. Erich Friedman's Packing Center is the closest relevant catalogue analogue to OEIS for these real-valued finite packing records. Any external deposit, catalogue request, or journal submission remains a later action, outside this task's local/GitHub-only scope.
