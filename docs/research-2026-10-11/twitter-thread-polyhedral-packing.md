# Twitter thread: polyhedra inside polyhedra

**LOCAL DRAFT — NOT POSTED.** Updated 12 October 2026 with the three published version DOI links supplied after public browser confirmation. This thread has not been posted, sent, or uploaded. The papers are preprints; this draft makes no claim of journal peer review or Wikipedia publication.

Published records: [methods preprint](https://doi.org/10.5281/zenodo.23306098), [patterns preprint](https://doi.org/10.5281/zenodo.23306126), and [reproducibility archive](https://doi.org/10.5281/zenodo.23306130). Each post includes its visible thread number. All authored text is ASCII, and the counts below treat each actual URL as one 23-character URL. All ten posts fit the ordinary 280-character limit. The rule follows [X's official counting documentation](https://docs.x.com/fundamentals/counting-characters), checked 12 October 2026. Attachments do not consume text characters in the official client. Check the final text in the composer after any editing.

## Copy-ready posts

### Post 1 (209/280)

```text
1/10 I've released two preprints on polyhedra inside polyhedra: 351 certified constructions, 9 Platonic-solid pairs, every count from 2 to 40. Methods: https://doi.org/10.5281/zenodo.23306098 Patterns: https://doi.org/10.5281/zenodo.23306126
```

### Post 2 (234/280)

```text
2/10 Five same-solid families, plus cube/octahedron and dodecahedron/icosahedron in both directions. Pieces can translate and rotate. Scale means container edge / piece edge; volume-normalized density makes the mixed pairs comparable.
```

### Post 3 (253/280)

```text
3/10 Built on Yohei Nakajima's soft-to-rigid cube method. I generalized the rounding to convex polyhedra: shrink the polyhedron and add a ball, then remove the rounding under compression. Perturbation and constrained tightening explore new arrangements.
```

### Post 4 (256/280)

```text
4/10 Every stored construction passed exact containment and separation checks, plus an independent floating-point checker: 351/351. These certify feasible upper bounds. They do not prove general optimality; numerical closed-form guesses remain conjectures.
```

### Post 5 (258/280)

```text
5/10 The curves have plateaus and sharp jumps. Six to seven octahedra in an octahedron increases the archived edge by 25% and container volume by 95.3%. For 29-33 dodecahedra, the certified scale stays exactly 3.7470909531576. These are construction results.
```

### Post 6 (259/280)

```text
6/10 The 33-dodecahedron witness has a 1+12+20 structure: one central piece, 12 inner centers in icosahedral directions, 20 outer centers in dodecahedral directions. Removing outer pieces explains the 29-33 plateau; each removed piece deletes 3 near contacts.
```

### Post 7 (251/280)

```text
7/10 The oddity: 7 orientation components, 102 near contacts, but no aligned contact. At 1 degree and distance <=1e-4 piece edges, all 33 contact-connected orientation domains are singletons. Ordered center shells need not mean locally aligned pieces.
```

### Post 8 (266/280)

```text
8/10 Paper 2 develops 20 testable hypotheses about shell filling, complementary orientations, boundary accommodation and construction families. Each separates measured evidence from predictions. These are geometric hypotheses, not claims of physical crystallization.
```

### Post 9 (249/280)

```text
9/10 Credit: my 11-cube refinement starts from Haowei Lin's seed; 12 cubes reproduce Nakajima's touching family. Ryan @small_LM has since announced smaller cube bounds at 34-36. The broader dataset is the point, alongside work by Friedman and Walsh.
```

### Post 10 (207/280)

```text
10/10 Explore the rotating constructions, inspect poses and certificates, or rerun the analysis. Code: https://github.com/alejandrozu/platonic-packing Viewer: https://alejandrozu.github.io/platonic-packing/ Reproducibility archive: https://doi.org/10.5281/zenodo.23306130
```

## Suggested existing attachments

These are suggestions only; no media was edited or uploaded. Use the existing files or source record images.

| Post | Attachment | Suggested alt text |
|---|---|---|
| 1 | `analysis/figure-1-scale-curves.png` | Nine finite polyhedral-packing families, each plotting container scale against counts 2 to 40. Solid curves are certified feasible upper bounds; dashed curves are volume lower bounds. |
| 5 | `analysis/figure-2-increments.png` | Relative container-edge increases when one polyhedron is added. The nine panels show pronounced expansion steps and intervals with nearly zero expansion. |
| 6 or 7 | Frozen `records/dodindod/dodindod_n33.png` | The certified 33-dodecahedron arrangement inside a dodecahedron, whose centers have a central piece, a twelve-piece inner shell, and a twenty-piece outer shell. The structural analysis distinguishes repeated orientations from aligned near contacts. |

For the shell post, the existing record image is an illustration of the actual arrangement; it is not an exploded shell diagram. Its source is [the frozen record image](https://github.com/alejandrozu/platonic-packing/blob/e15b496ae7306287e0e70bb5b14be79f5dfdde84/records/dodindod/dodindod_n33.png).

## Evidence behind the claims

- Dataset and proof scope: `research/verification.json`, the two papers, and source commit `e15b496ae7306287e0e70bb5b14be79f5dfdde84`.
- Jumps and plateaus: `analysis/largest-jumps.csv` and `analysis/plateaus.csv`. The dodecahedral scale equality is equality of certified stored upper bounds, not proof of equal optimal sizes.
- Shell organization and contact oddity: `research/hypothesis-evidence.md` and `research/hypothesis-evidence.json`. Orientation is compared modulo the solid's proper rotational symmetry. Near contacts are measured by Euclidean distance.
- Hypotheses: H1-H20 in Paper 2. The thread does not promote them to theorems, optimality proofs, or a physical crystallization result.
- External credit: `research/current-records.md` and `research/social-context.md`. The 11-cube improvement used Lin's seed; the 12-cube configuration reproduces Nakajima's touching family with different clearance. Ryan's [public announcement](https://x.com/small_LM/status/2109345921465229780) reports smaller cube bounds at counts 34-36 than the frozen local archive. It is an announcement rather than an independently rerun exact certificate. Friedman and Walsh remain credited for earlier benchmark constructions.

The JSON companion is an array of ten posts with text, weighted counts, and remaining character budgets. It is suitable for local review and subsequent approved posting; it does not itself post anything.
