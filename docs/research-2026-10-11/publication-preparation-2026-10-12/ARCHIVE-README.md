# Polyhedral packing reproducibility archive, version 1

Prepared by Alejandro Zarzuelo Urdiales on 12 October 2026.

`frozen-source/` is the complete Git-tracked public source tree at e15b496ae7306287e0e70bb5b14be79f5dfdde84 from https://github.com/alejandrozu/platonic-packing.
`research-packet/` contains the two manuscripts, all measurement tables and figures, verification summaries and scripts,
seven STL illustrations, an interactive full-precision explorer, and the reference article in HTML/Markdown/MediaWiki.
The source records cover nine ordered shape pairs and n=2..40, with 351 configurations.

The computations establish stored feasibility and descriptive patterns. General global optima remain unresolved.
The article has not been submitted to Wikipedia. Its HTML viewer loads external libraries and fonts from CDNs.
Existing public records and sources are linked; two superior external octahedra-in-cube cases have source diagrams
but no located pose file and are not substituted with the author's inferior placement.

## Rights and attribution

The archived source and its associated documentation retain the MIT license in `frozen-source/LICENSE`,
with copyrights for Yohei Nakajima and Alejandro Zarzuelo. This compilation and the newly supplied research packet
are offered under MIT for the supplemental archive, except for upstream components carrying their own notices.
Imported Hyra construction files remain under Apache-2.0; their scoped notice and full license are provided in
`THIRD-PARTY-NOTICES.md` and `LICENSES/Hyra-upstream-LICENSE.txt`. The separately deposited manuscript records are also offered
under CC BY 4.0. Existing upstream license notices and source attribution must be retained.
External websites and referenced literature are links, not licensed reproductions of complete third-party works.

## Tools

Tools used: Claude (Anthropic) assisted computational development under the author's direction; Codex assisted source inspection, reproducibility checks, quantitative analysis, and manuscript drafting and exposition. Computational tools are described in the methodology. Alejandro Zarzuelo Urdiales is the human author responsible for the work; no AI system is listed as an author.

## Reproduce

From `research-packet/`, with Python and Git installed:

```sh
python research/verify_snapshot.py --repo ../frozen-source --out verification-rerun.json
python analysis/analyze_records.py --repo ../frozen-source --out regenerated-analysis
python research/hypothesis_evidence.py --repo ../frozen-source --analysis analysis --out hypothesis-rerun.json
```

Use the dependency versions described in the scripts and analysis metadata. Figures require matplotlib.
Geometry crosschecks additionally require Node.js. The archived exact checker uses the Python standard library.
No personal email, visa dossier, private account evidence, credentials, or unrelated local files are included.
