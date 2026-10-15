# Independently published constructions

The site includes the smallest available construction from the project archive and this source registry, regardless of its author. Original project records are preserved, and the viewer's **Construction** selector keeps certified alternatives accessible.

The registry is [`docs/external_records.json`](../../external_records.json), checked on 13 October 2026 for the site's current range, n = 2–40. It is a record of the sources checked, not a proof of optimality or an assertion that every possible source has been exhausted.

## Coordinate sources

| Author | Construction | Frozen original source |
|---|---|---|
| Ryan Xu (@small_LM) | Cubes in a cube, n = 34, 35, 36 | [square_packing, commit 9535d65](https://github.com/ry-xu/square_packing/blob/9535d65d84cc33f20f4e26329f8da12bdcef216e/cube_packing_records.json) |
| Haowei Lin / Tencent Hunyuan | Cubes in a cube, n = 11, 12; octahedra in a cube, n = 21, 24 | [Hyra-results, commit 09b2d2e](https://github.com/Tencent-Hunyuan/Hyra-results/tree/09b2d2e3c362c67a78f544c836bd8e4b54a05527/AI4Science/packing_records/records) |
| Yohei Nakajima | Cubes in a cube, n = 12 | [soft-to-rigid-packing, commit efe7a92](https://github.com/yoheinakajima/soft-to-rigid-packing/blob/efe7a920142350a4f0678633490c3e3dbed71fa0/claims/cubincub_n12/cubincub_n12.json) |
| T. Berthold, D. Kamp, G. Mexi, S. Pokutta and I. Polik | Octahedra in a cube, n = 17 | [Packing, commit 27f7163](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l3/m2/n17/platonic_n17_m2_l3.html) |

`scripts/import_external_records.py` freezes each original file with its commit and SHA-256, converts it to canonical unit-edge coordinates, adds 1e-7 pair and wall clearance, and runs both `verify.py` and `certify_exact.py`. The resulting copies and checker receipts are in [`records/external/`](../../../records/external/). All nine copies pass both checks.

The original published scale is retained separately. A source may have more or less clearance than the site's convention; normalizing clearance or translating the whole construction can therefore slightly change the last digits of the certified scale. This is **not** attributed as a new geometric discovery. Imported records retain their original authors and methods, and no new touching-limit claim is assigned to them.

The Berthold–Kamp et al. supplement normalizes the inner octahedron to unit circumradius and supplies a Plotly mesh. Its opposite vertex pairs determine three orthogonal directions. The importer fits these directions to the canonical octahedron, checks every reconstructed vertex against the source within 1e-12 source units, and divides centers by sqrt(2) to obtain unit edges. The reported outer circumradius is converted to container-edge / piece-edge scale by multiplying by sqrt(2/3).

## Sources without downloadable coordinates

[Erich Friedman's cubes-in-cubes catalogue](https://erich-friedman.github.io/packing/cubincub/) and [octahedra-in-cubes catalogue](https://erich-friedman.github.io/packing/octincub/) credit constructions to Erich Friedman, Ríain Walsh and Haowei Lin. When a catalogue construction is smaller than every available coordinate construction by more than its printed rounding scale, the viewer links its original animation and marks it **published source**. It has no pose list, JSON coordinate file or local certificate. The original animations are served by the Packing Center; they are not copied into, or relicensed as artwork of, this project.

The reported n = 28 cube result, s = 3.66600+, by [紺葉 (@konoha_ily2)](https://x.com/konoha_ily2/status/2109306733999120589) is marked **author report**. The post claims an exact certificate, but no downloadable poses or certificate were found in that conversation for local verification. The site makes no claim to have certified it. A certified alternative remains available.

Published expressions such as Friedman's 3 + 1/sqrt(2) are retained at their mathematical scale; other catalogue numbers retain their printed precision. Charts label the mixture of touching limits, full coordinate-source scales and reported estimates.

## Submission comparisons

The browser checker and GitHub submission checker compare against the best **certified coordinate construction**, including imported ones. Source-only published values and author reports are additional references; they never masquerade as certified coordinate baselines. A submission that improves an available coordinate record while remaining above a smaller reported result is labelled accordingly, rather than being called an improvement over that reported result.

Original source provenance is retained here. The project MIT licence does not transfer authorship or relicense external artwork. Hyra-results carries its upstream Apache-2.0 licence; Nakajima's repository carries MIT. Numeric geometry from the other supplements is attributed to its original source, without copying their search programs.
