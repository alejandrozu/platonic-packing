# Polyhedra in polyhedra packing: manuscripts, analysis, and reference article

Prepared **11 October 2026** by Alejandro Zarzuelo Urdiales. Scientific inputs are frozen at [`e15b496ae7306287e0e70bb5b14be79f5dfdde84`](https://github.com/alejandrozu/platonic-packing/tree/e15b496ae7306287e0e70bb5b14be79f5dfdde84). Everything in this packet is saved locally and in the project repository. On 12 October 2026, the author approved and published the two preprints and reproducibility dataset on Zenodo. The approved [five-post X thread](https://x.com/AlejandroZarUrd/status/2109430713577865667) was also published and verified on 12 October. No journal, HAL, Wikipedia, Commons or new website submission was made.

## Papers

| Paper | Contents | Formats |
|---|---|---|
| **Certified finite packings of Platonic solids** | Construction and development: Nakajima's starting point, generalized homotopy, geometric distances, tightening, jiggling, archive search, exact certification, experiments, failures, and results | [PDF](paper-1-methods.pdf), [Markdown](paper-1-methods.md), [LaTeX](paper-1-methods.tex) |
| **Finite polyhedral fits** | Cross-family analysis of jumps, plateaus, volume-normalized scales, symmetry-reduced orientations, contacts, operational grains, and **20 testable hypotheses** | [PDF](paper-2-patterns.pdf), [Markdown](paper-2-patterns.md), [LaTeX](paper-2-patterns.tex) |

The papers have no draft watermark or front-matter tool credits. Computational tools are described within their methodology sections. The dataset covers nine ordered shape pairs, every count from 2 to 40, 351 constructions, 7,371 pieces, and 95,940 piece pairs. Each construction uses one particle species; the archive does not contain all 25 Platonic pairs or mixtures.

Paper 2's hypothesis section explains the observations and proposes tests for other shapes, counts, and conditions. The evidence distinguishes confirmed arrangements, measured descriptors, reusable constructions, and conjectures about optimal or near-optimal arrangements.

## Wikipedia-style research reference and rotating constructions

The current [illustrated preview](wikipedia-article-preview.html) is a shorter offsite reference for a human writer. Its [editable Markdown](wikipedia-polyhedral-fits.md) and [MediaWiki source](wikipedia-polyhedral-fits.wiki) contain the same article and two visual tables. The prose was reduced from approximately 5,346 to 1,259 words (76.45%), excluding the tables and bibliography. There are 34 concept links and 23 cited sources. The independently authored finite-packing monograph by Böröczky and 3D-layout survey by Cagan, Shimada and Yin are added, with fuller coverage of the established handbook, engineering, and physical-review literature.

Both rendered result tables, all 99 values and static images, every source/construction link, full stored geometry and orientation colours are unchanged. Complete construction attribution is available in collapsible notes below each table and in the inspection view. A concise methods paragraph credits the generalization of Nakajima's continuation procedure. The top-right overview remains static and now emphasizes the problem and established theory.

The full earlier version, including detailed methodology and twenty hypotheses, is preserved as [Markdown](wikipedia-full-reference.md), [MediaWiki source](wikipedia-full-reference.wiki), and [interactive preview](wikipedia-full-reference.html). Neither paper nor the frozen Zenodo release has been changed.

The new independent sources cover the established subject and methods; they are not independent secondary reviews of the 2026 atlas or its record claims. These generated files are reference material, not evidence of human authorship or Wikipedia acceptance. English Wikipedia's [LLM-writing guideline](https://en.wikipedia.org/wiki/Wikipedia:Writing_articles_with_large_language_models) requires an independently human-written submission outside its narrow exceptions. A receiving editor can use the original sources, figures and verified data when preparing that submission. No Wikipedia page or Commons media has been saved or uploaded.

The [preservation audit](research/wikipedia-short-reference-audit.json) confirms that both visual tables and embedded construction data are identical. [Wikipedia's native renderer](research/wikipedia-short-native-render-check.json) checked one infobox, two tables and all 23 references without citation or Lua/template errors. The rendered table blocks are byte-identical; comparisons of source blocks normalize line endings. [Short-revision notes](research/wikipedia-short-reference-notes.md) distinguish review sources from original research and describe the editable files.

The two [24-second rotating illustrations](wikipedia-assets/README.md) and the [full explorer](packing-explorer.html) remain available. The two source-only octahedra-in-cube catalogue diagrams retain their original attribution and remain excluded from Commons preparation pending permission. Native article markup uses supported templates and links; the repository preview supplies the interactive rotation. [Viewer license attribution](LICENSE-viewer.txt) is retained.

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

The [12 October verified platform rules](research/tonight-platform-rules.md) update the earlier [publication alternatives](research/dissemination-alternatives.md) and confirm arXiv's two-submissions-per-calendar-month rule introduced on 1 October 2026. They compare routes that address the sponsorship and volume constraints:

- **Zenodo** is the fastest verified route to an archival DOI for the papers and frozen research package, without endorsement. Its CERN/OpenAIRE infrastructure provides durable citation and preservation.
- **HAL** offers a recognized academic manuscript archive with moderation normally taking a few days; its required affiliation metadata must be completed honestly, and independent-author handling remains a condition to confirm.
- **Preprints.org** accepts mathematics and technical/hypothesis papers, with typical screening of 24 working hours; screening is not mathematical peer review.
- **Journal of Computational Geometry** is a fee-free geometric-method candidate; **Discrete & Computational Geometry** is another packing/geometry candidate. **Experimental Mathematics is not ready for these AI-drafted manuscripts under its publisher's current first-draft restriction.** Journal acceptance and timing remain editorial decisions.

The combination of a permanent archive and journal review gives both rapid access and an opportunity for independent recognition. Erich Friedman's Packing Center is the closest relevant catalogue analogue to OEIS for these real-valued finite packing records. Any external deposit, catalogue request, or journal submission remains a later action, outside this task's local/GitHub-only scope.

A [public author-profile register](research/public-author-profile.md) verifies prior research deposits and dated institutional evidence. Three approved Zenodo records are now published: the [methods preprint](https://doi.org/10.5281/zenodo.23306098), [patterns preprint](https://doi.org/10.5281/zenodo.23306126), and [reproducibility dataset](https://doi.org/10.5281/zenodo.23306130), including the rotating article. All seven public downloads match their approved hashes. Zenodo receipts and the [published X thread receipts](twitter-publication/receipt.md) are saved with the packet. Private account, enrollment, and legal-dossier evidence are kept locally and excluded from the release.
