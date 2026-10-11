# Article provenance and numerical review

Independent review on 11 October 2026 of wikipedia-polyhedral-fits.md, wikipedia-polyhedral-fits.wiki, and polyhedra-in-polyhedra-packing.html, against research/current-records.json, the frozen source configurations, and the analysis evidence.

## Table and construction checks

- Both article formats contain the requested two tables, with all 99 cases: five same-solid and four ordered dual-solid problems for every count from 2 through 12.
- All 99 Markdown displays and all 99 MediaWiki displays agree with the selected-source register. Their construction or diagram anchors agree with the selected case and population.
- All 99 embedded HTML provenance objects agree with the register's value, display, attribution, source URL, configuration URL, and source-image URL.
- Origin codes retain elementary grid credit, Friedman's 1998 constructions and Zarzuelo's reproductions, Lin-to-Zarzuelo refinement at eleven cubes, Nakajima's origin and Zarzuelo's reproduction at twelve cubes, Walsh's octahedron constructions, and Lin's winning twelve-octahedron listing.
- Winning external octahedron-in-cube cases 11 and 12 are **2.19540+** (Walsh) and **2.25949+** (Lin). They have no selected coordinate file. The article supplies their actual catalogue and diagram links, without calling a different local configuration the winning geometry.
- The source-only viewer takes precedence over the archive candidate. Its diagram URLs are absolute: https://erich-friedman.github.io/packing/octincub/11.gif and https://erich-friedman.github.io/packing/octincub/12.gif; both returned HTTP 200.
- The twelve-cube narrative explicitly credits reproduction of Nakajima's touching family and explains the reduced clearance. It does not claim a new geometric record from that clearance change.

## Link and visualization checks

The existing public atlas supports the table's exact record-ID hash links and contains all 97 coordinate-backed table targets. Its stored container scales agree exactly with the frozen files. Its rendering poses are the same poses rounded to seven decimals, with maximum component difference \(5\times10^{-8}\); the separately linked coordinate files preserve full precision. This rendering precision is not used as a feasibility certificate.

All local article HTML reference fragments resolve to existing IDs. The manuscript links use the actual **docs/polyhedral-fit-papers-2026-10-11** branch and the **docs/research-2026-10-11/** directory. No nonexistent earlier branch remains. Nakajima's pinned paper PDF link is accessible. His DOI **10.5281/zenodo.23248095** resolves; Zenodo's API identifies its resource type as **Software**, its author as Yohei Nakajima, its release date as 8 October 2026, and its license as MIT. The article describes a paper and software release and makes no claim of peer-reviewed publication for that DOI.

## Observations underlying the hypotheses

The quantitative article discussion agrees with the corresponding CSV and hypothesis-evidence.json:

- Octahedra in an octahedron: six pieces at 2.0000003674235, density approximately 0.7500, fifteen near-contact edges; seven at 2.5000004286608, density approximately 0.4480, five edges. The resulting approximately 25% edge and 95.3125% volume increases are correct.
- The family counts are correct: 22 cube-in-cube and 18 octahedron-in-octahedron records are pairwise aligned at one degree; the ordered dodecahedron–icosahedron directions have 26 and 24 all-distinct records.
- Twelve icosahedra in an icosahedron have thirty near contacts and one operational grain.
- Fifteen icosahedra in a dodecahedron have orientation components of sizes 14 and 1. The singleton is numerically central, with center radius approximately 2.45e-14 and six near contacts.
- Dodecahedra in a dodecahedron at counts 29–33 share the identical stored scale 3.7470909531576. Their endpoint densities are 0.5512077223305983 and 0.627236373686543; their contact-edge counts are 90 and 102.
- The thirty-three-piece arrangement has one center, twelve inner centers, and twenty outer centers. Direction-fit residuals are approximately 2.60e-14 and 1.75e-14. Its orientation-component sizes are 21 and six pairs. Its 102 near contacts divide into 12 central–inner, 30 inner–inner, and 60 inner–outer edges, with disorientations approximately 36 degrees or 37.398814 degrees. All operational grains are singletons because the contacts cross orientation classes.
- The smaller plateau witnesses omit outer-shell particles, with matched poses agreeing to approximately 3e-14. Each omitted outer piece removes three near contacts. This supports the proposed occupancy mechanism while remaining a numerical structural comparison.
- The forty-particle dual-direction scale and density examples, and the reported Spearman extrema of approximately −0.720 and +0.563, agree with the source analysis.

The text attributes the interpretations to the pattern manuscript and distinguishes plausible mechanisms from global optimality, exact contact identities, and physical crystallization dynamics.

## Editorial repair identified

The original table insertion omitted a legend for its superscript origin codes and a precise explanation of the plus notation. This was reported to the coordinating agent and repaired.

The final Markdown, MediaWiki, and rendered HTML now contain the attribution and precision key. It correctly defines G, F, W, L, N, and Z; describes F/Z and W/Z as externally attributed results with separately certified placements agreeing at printed precision rather than identical poses; preserves L→Z search lineage and N/Z reproduction credit; explains truncated plus notation; distinguishes stored JSON scales from source-only reports; and states that originating coordinates and manuscripts were not located for the winning external octahedron counts 11 and 12.

The complete mechanical comparison was rerun after the repair and HTML rebuild: all 99 cells in each article format and all 99 embedded provenance cases still agree, and no table, URL-fragment, source-selection, branch-link, or encoding discrepancies were found. The observed numbers and their hypothesis interpretations remain consistent with the evidence.

**Final verdict: passed the scoped provenance and numerical review.** No actionable failure remains within this review's scope. This verdict verifies the local article's agreement with its cited primary data and dated comparator register; it does not certify exhaustive worldwide record status, future Wikipedia acceptance, or global optimality.
