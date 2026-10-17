# Twitter thread: polyhedra inside polyhedra

**PUBLISHED — 12 October 2026.** [Live thread](https://x.com/AlejandroZarUrd/status/2109430713577865667). [Publication receipt](twitter-publication/receipt.md). Condensed to five posts on 12 October 2026. Posts 1 and 2 retain the approved wording; only their numbering changes from /10 to /5. The rest is condensed into three posts, each below 2,000 literal characters including full URLs as well as below 2,000 X-weighted characters.

Published as one reply chain: 1 is the root; 2 replies to 1; 3 replies to 2; 4 replies to 3; 5 replies to 4. Posts 1–2 fit the ordinary 280-character limit. Posts 3–5 use the user's Premium long-post capability.

## Approved pictures and placement

| Post | Attachment | Purpose |
|---|---|---|
| 1 | [Nine-family overview](twitter-assets/01-nine-families.png) | Main announcement image, rendered from the frozen certified study archive |
| 4 | [Plateau and jump](twitter-assets/03-plateau-and-jump.png) | The marginal cost of another piece |
| 5 | [Dodecahedral shell](twitter-assets/02-dodecahedral-shell.png) | Actual poses and the 1 + 12 + 20 organization |

The three approved pictures are unchanged. [Alt text](twitter-assets/alt-text.md) and [scientific image checks](twitter-assets/qa-report.md) are included. [Mention evidence](research/twitter-mention-evidence-2026-10-12.md) substantiates the selected handles and their roles.

## Submitted posts

### Post 1 — 257 literal / 225 X-weighted characters

```text
1/5 Polyhedra inside polyhedra: 351 certified constructions, 9 families, n=2-40. Two new preprints.

Built on @yoheinakajima; packing discussions with @small_LM & @konoha_ily2.

https://doi.org/10.5281/zenodo.23306098
https://doi.org/10.5281/zenodo.23306126
```

### Post 2 — 181 literal / 181 X-weighted characters

```text
2/5 Five same-solid families, plus their duals. Pieces can translate and rotate. Scale means container edge / piece edge; volume-normalized density makes the mixed pairs comparable.
```

### Post 3 — 1429 literal / 1224 X-weighted characters

```text
3/5 How the construction works: start with balls, end with rigid polyhedra.

I generalized @yoheinakajima's soft-to-rigid cube method to other Platonic solids and containers. A scaled convex polyhedron thickened by a ball gives a nested family: it starts as the inscribed ball and grows into the full piece. Search compresses, sharpens and tightens the arrangement.

Jiggling expands, softens and reshuffles a candidate before tightening again. Its relative-center criterion distinguishes rearrangement from simply moving the whole cluster.

Haowei Lin (@AndyLin2001) and @TencentHunyuan's Hyra supplied reusable seeds and comparison witnesses. My 11-cube refinement starts from Lin's seed; the 12-cube result reproduces Nakajima's touching family with a different clearance convention.

A separate exact checker proves containment and pairwise separation for all 351 stored constructions. These are certified feasible upper bounds; most global optima remain open.

@keenanisalive @mathematics_inc @AlexKontorovich: I'd welcome your thoughts on the geometric optimization and constructive-proof side.

Methods:
https://doi.org/10.5281/zenodo.23306098
Nakajima's paper:
https://github.com/yoheinakajima/soft-to-rigid-packing/blob/efe7a920142350a4f0678633490c3e3dbed71fa0/paper/main.pdf
Hyra packing artifacts:
https://github.com/Tencent-Hunyuan/Hyra-results/tree/09b2d2e3c362c67a78f544c836bd8e4b54a05527/AI4Science/packing_records
```

### Post 4 — 1165 literal / 1133 X-weighted characters

```text
4/5 One extra piece can leave the container unchanged or force a major expansion in the best construction found.

Six to seven octahedra in an octahedron changes the archived edge from about 2 to 2.5: +25% in edge, +95.3% in container volume. Occupied volume falls from 75% to 44.8%.

For 29-33 dodecahedra in a dodecahedron, every record has exactly the same certified scale: 3.7470909531576. Density rises from 55.1% to 62.7% without increasing the container. Cubes 15-27 share another certified plateau.

Across families, the analysis distinguishes aligned scaffolds, repeated orientation domains, dispersed orientations and boundary accommodation. Comparing raw edge ratios alone misses structure: at 40 pieces, reversing the dodecahedron/icosahedron pair gives edge ratios 6.32472 and 2.74184, yet occupied volumes are close, 55.53% and 55.25%.

These are observed construction transitions, not a curve of proved optima. They identify reusable families, capacity limits and promising places to search for better successors.

Patterns and measurements:
https://doi.org/10.5281/zenodo.23306126
Data, code and certificates:
https://doi.org/10.5281/zenodo.23306130
```

### Post 5 — 1443 literal / 1311 X-weighted characters

```text
5/5 The 33-dodecahedron witness explains a plateau through a 1 + 12 + 20 shell structure.

One central piece, twelve inner centers in icosahedral directions, twenty outer centers in dodecahedral directions. Counts 29-32 retain the same core and omit outer pieces; each outer piece adds three near contacts.

The oddity: seven orientation components, 102 near contacts, but no aligned contact. At a 1-degree angle threshold and distance <=1e-4 piece edges, all 33 contact-connected orientation domains are singletons. Repeated orientations occupy separated sites, while differently oriented neighbors form the shell. Positional order and local alignment are different measurements.

Paper 2 develops 20 testable hypotheses about shell filling, complementary orientations, boundary accommodation and construction families, with tests for other solids, counts and configurations. The goal is to explain recurring geometry and guide future searches and optimality proofs.

Individual cube bounds have already moved through @konoha_ily2 and @small_LM's announcements. The frozen constructions and structural analysis remain reproducible.

Rotate the shell:
https://alejandrozu.github.io/platonic-packing/#dodindod_n33
Code:
https://github.com/alejandrozu/platonic-packing
Open archive:
https://doi.org/10.5281/zenodo.23306130
Cube announcements:
https://x.com/konoha_ily2/status/2109306733999120589
https://x.com/small_LM/status/2109345921465229780
```
