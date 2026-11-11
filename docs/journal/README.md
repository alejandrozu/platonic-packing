# Polyhedra in Polyhedra Journal

The Journal is an open-access editorial programme with an inaugural Q4 2026 issue in progress. New research articles require two independent expert reports and an unconflicted handling editor's acceptance decision. Alejandro Zarzuelo Urdiales is the editor and reviewer. The Journal is seeking additional editors; further appointments are listed after agreement. The founder's own papers still require independent handling and review. A named independent editorial board and completed reviews are not claimed at launch.

The launch research library indexes existing works. It does not retrospectively accept, peer review or republish them. Original venues, licenses, versions and review status remain visible on each paper page. It contains 14 research papers and eight datasets, software releases or construction resources. The three original Zenodo deposits are two preprints and one dataset.

## Sources and version boundaries

- `papers.json` contains the public bibliography, review labels, canonical sources, DOI scope, related construction links and publication metadata. Primary sources were checked on 9 November 2026.
- The JOATP article is *Certified architecture transfer from polyhedral packing catalogues to finite-cluster magnetic response*, accepted and published 27 October 2026, version 1.1. Its publisher records editorial review with AI assistance and expressly does not claim independent external referee review. The model is an **uncalibrated equilibrium model**. The DOI `10.5281/zenodo.23629684` is the original v1.0 supplement, not the v1.1 article DOI.
- `web/journal/downloads/cube-centre-2026-11-10.pdf`, `width-ball-2026-11-10.pdf` and `all-dimensions-2026-11-10.pdf` are the author versions of 10 November 2026 of Papers I, II and IV of the series (17, 22 and 23 pages). Their LaTeX sources are at commit `4842e61986` of the `papers-draft` branch (`docs/papers/`), and their SHA-256 hashes are recorded in `papers.json`.
- Until an issue is published, the papers in it are still subject to potential small revisions; the Journal page and the issue page say so at the top.
- `web/journal/downloads/patterns-2026-11-08.pdf` is an unchanged author-provided copy of the 21-page 8 November manuscript. Its SHA-256 is `919c2192fbb699f6db5217281e89aafbe02c2f549a7580dacc2af95f179c1dfb`. The earlier repository manuscript and its source remain paired in `docs/patterns-paper/`.
- The current generalization manuscript is sole-authored by Alejandro Zarzuelo Urdiales. Earlier proposed joint authorship is not presented as an agreed collaboration.
- Background periodic-packing and optimization papers are contextual sources. Their entries do not claim that they supplied finite-container catalogue coordinates.
- Construction repositories retain their contributor credit and are not labelled research papers. The scope excludes 2D packing.

## Editorial operation

The website's editorial policy explains screening, review, author responses, conflicts, acceptance, corrections, rights and fees. The GitHub paper form receives public editorial enquiries; it does not invoke packing-certification automation or accept a paper automatically. Authors should link a public manuscript and omit private information. Reviews and reviewer identities are made public only with consent.

The first accepted article must have a versioned editorial decision record, two actual independent reports and rights/author consent before the launch catalogue is extended to show accepted contents. A certificate checks its stated mathematical proposition; it is not independent scientific peer review.

Online publication is planned on acceptance, grouped into quarterly issues. The Q4 2026 issue remains in progress through 31 December. Printed editions are planned for academics and research libraries worldwide; the print-interest form is not an order. Pricing, availability and shipping terms must be settled before orders open. No ISSN, new article DOI, indexing, preservation service or distribution partnership is asserted without registration or an agreement.

## Maintenance

`scripts/journal.py` renders the index, issue, policy, article pages, citations and downloadable metadata. `scripts/site.py` supplies the existing page shell, navigation, assets and sitemap. New paper records belong in `papers.json`; publisher status changes need a checked primary source. Public metadata contains no private local paths, submission credentials or correspondence.

The cover is vector artwork from the frozen native `icoinico_n16` witness. `cover-provenance.json` records the source revision, geometry, camera and hashes. Its colours identify pieces for the illustration, not computed orientation-equivalence classes.

The unchanged cover generator and frozen input snapshots are in `cover/`. Run `render_cover.py --repo /absolute/path/to/platonic-packing` with Pillow and fontTools installed; the renderer uses the stated Windows Georgia and Segoe UI fonts. The published SVG contains outlined lettering and needs no installed fonts. The original generator's default checkout path belongs to its creation workspace, so supply `--repo` when reproducing elsewhere.

Standards informing the founding policy: [COPE/DOAJ/OASPA/WAME transparency principles](https://www.oaspa.org/resources/principles-of-transparency-and-best-practice-in-scholarly-publishing-version-5/) and [DOAJ application guidance](https://doaj.org/apply/guide/). These links are not endorsements or indexing claims.
