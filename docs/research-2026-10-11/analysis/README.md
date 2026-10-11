# Reproducible analysis for Paper 2

Input freeze: `alejandrozu/platonic-packing`, Git commit `e15b496ae7306287e0e70bb5b14be79f5dfdde84`, 11 October 2026. The analysis comprises **351 record files, 7,371 pieces, and 95,940 within-record piece pairs**. `source-manifest.csv` contains the SHA-256 and byte size of each input record and of `src/solids.json`.

From a Python environment with NumPy and optional Matplotlib:

```powershell
python analyze_records.py --repo PATH_TO_FROZEN_REPOSITORY --out PATH_TO_NEW_ANALYSIS_DIRECTORY
```

The tables were calculated with Python 3.12.14 and NumPy 2.3.5. Figures were generated with Matplotlib 3.11.2 and NumPy 2.5.4; the plotted numbers are the already computed table values. `analysis-metadata.json` records those versions, thresholds, source commit, and a combined record-manifest hash. No stochastic operation enters this analysis. CSV presentation can vary slightly across Python/NumPy versions without a material change in calculated values; verify structural classifications near thresholds before comparing regenerated tables.

## Files and meanings

| File | Contents |
|---|---|
| `analyze_records.py` | Portable input-to-table analysis, plus optional scientific plotting |
| `record-metrics.csv` | All 351 scale, density, increment, orientation, contact, and grain descriptors |
| `family-summary.csv` | Nine family summaries, each over 39 counts |
| `pair-metrics.csv` | 95,940 symmetry-reduced disorientation angles, center distances, and near-pair feature distances |
| `plateaus.csv` | Exact stored-scale, exact deletion-envelope, and numerical touching plateau intervals |
| `largest-jumps.csv` | Three largest relative edge increments per family |
| `descriptive-correlations.csv` | Within-family Spearman correlations, with no independence or significance claim |
| `geometry-details.json` | Per-record orientation memberships, near-contact edges/degrees/components, and operational-grain memberships |
| `source-manifest.csv` | Input bytes and SHA-256 hashes |
| `analysis-metadata.json` | Reproducibility metadata and certificate-report reference |
| `figure-1-scale-curves.*` | All nine scale curves and volume lower bounds |
| `figure-2-increments.*` | Relative edge increments for all counts n=3–40 |
| `figure-3-structure.*` | Density, orientation-domain fraction, operational-grain fraction, and mean contact degree |

Each figure is supplied as PNG, SVG, and PDF. SVG/PDF preserve vector geometry and editable text. The PNGs were visually inspected for readable axes, labels, legends, and uncropped content.

## Scientific conventions

- `s_full` is the feasible construction's certified scale, an **upper bound** on the optimum. `s_tight` is the locally estimated numerical touching scale. Closed-form labels are source conjectures.
- The volume bound is `(n V_piece / V_container)^(1/3)`. Density is `n V_piece / (V_container s_full^3)`. Normalized scale equals density to the power `-1/3`.
- The deletion envelope uses the smallest certified scale among all records of the same family with at least n pieces, retaining the witness identifier. All nine raw full-scale curves were monotone already, so the envelope changes zero values.
- Exact reported-scale plateau equality uses parsed floating-point equality, retaining `s_full_hex`; numerical touching plateaus use a whole-interval range at most `1e-8`. Neither proves equality of optimal scales.
- Orientation disorientation minimizes rotation angle over the piece's **proper** symmetry group: tetrahedron 12, cube/octahedron 24, dodecahedron/icosahedron 60. Groups are generated in the input geometry's coordinate convention.
- Orientation components are single-linkage components at 0.1, 1, and 5 degrees. Their maximum diameters are stored. A one-component result is separate from the explicit all-pairwise-aligned test at 1 degree.
- Near contacts use actual Euclidean vertex-face and segment-segment feature distances at `1e-5`, `1e-4`, and `1e-3` piece edges. SAT projection gaps only reject distant candidates. SAT gaps are not used as the actual contact distance.
- Pair distance cells are empty when a center-radius or SAT lower bound excludes the pair from the largest contact threshold. They do not represent a missing distance that was required for any classification. `minimum_near_pair_distance` is conditional on near candidates, rather than the all-pair minimum.
- An operational grain is a connected component after retaining central near-contact edges with disorientation at most the chosen angular threshold. The central choice is `1e-4` piece edges and 1 degree. This is a geometric proxy and does not establish positional crystallinity or a physical grain.
- Contact counts include face, edge, and vertex proximity. They are not counts of force-bearing contacts, contact area, or independent constraints.
- Correlations concern selected final winners across counts. Count dependence, selection, and shared search ancestry prevent a causal or independent-sample interpretation.

The accompanying `research/verification.json` reports a fresh exact and floating-point verifier rerun: **351 passes and zero failures** for the frozen archive, with schema checks also passed. Exact feasibility does not make these double-precision structural descriptors exact, nor does it establish global optimality.

## Notable checks

The script checks all expected counts, pose-array lengths, and stored density consistency. It reconstructs every solid's proper symmetry group and validates its order and orthogonal positive-determinant matrices. Euclidean distance self-checks include displaced cube face, edge, and vertex cases. All 217 records with unchanged contact edge counts across the distance thresholds have unchanged edge sets, because those graphs are nested. All 131 records with unchanged orientation-component counts across the angular thresholds have unchanged component partitions for the same reason.

An independent sampled geometry cross-check in `research/geometry-crosscheck.json` compared 3,511 pair distances with the repository's geometry kernel: maximum absolute difference approximately 2.0e-15 piece edges and zero differences in contact classifications at the three tolerances. Symmetry-group closure and representative invariance were also checked. The whole-range numerical plateau rule was exercised on a nonmonotone synthetic sequence and regenerated; all 58 reported plateau intervals were unchanged by that correction.
