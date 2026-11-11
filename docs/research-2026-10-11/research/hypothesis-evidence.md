# Structural evidence accompanying Paper 2's hypotheses

This supplement records additional measurements from source commit `e15b496ae7306287e0e70bb5b14be79f5dfdde84`. The 351 pose files passed the separately reported exact feasibility verification. The measurements here are double-precision structural comparisons and do not prove exact touching geometry or global optimality.

## Dodecahedra in a dodecahedron, counts 29–33

The common certified scale is **3.7470909531576**. The 33-piece witness is organized as a central piece, a 12-piece inner shell, and a 20-piece outer shell.

| Property | Measured value |
|---|---|
| Central piece index | 23 |
| Inner shell radius | 2.227032828823202–2.227032828823275 |
| Outer shell radius | 3.849384528153525–3.849384528153609 |
| Inner shell direction fit | Dodecahedral face normals; dual icosahedral vertex directions |
| Maximum inner unit-direction residual | 2.5961 × 10⁻¹⁴ |
| Outer shell direction fit | Canonical dodecahedral vertices |
| Maximum outer unit-direction residual | 1.7514 × 10⁻¹⁴ |
| Orientation component sizes | 21, 2, 2, 2, 2, 2, 2 |
| Center–inner contacts | 12 |
| Inner–inner contacts | 30 |
| Inner–outer contacts | 60 |
| Outer–outer contacts | 0 |
| Center–outer contacts | 0 |
| Center contact degree | 12 |
| Every inner piece's contact degree | 11 |
| Every outer piece's contact degree | 3 |
| Center–inner and inner–outer disorientation | Approximately 36° |
| Inner–inner disorientation | Approximately 37.39881417029° |

The 21-member orientation component is the central piece plus the 20 outer pieces. The six other components are antipodal pairs on the inner shell. Consequently, the same-orientation pieces are spatially separated, while all near contacts join different orientations. All 33 operational grains are singletons at each of the 0.1°, 1°, and 5° criteria. The near-contact edge set is unchanged at distances 10⁻⁵, 10⁻⁴, and 10⁻³ piece edges. The 30 inner–inner contacts coincide with nearest-center pairs of the inner shell; the 60 inner–outer contacts coincide with nearest-center pairs between shells.

The smaller configurations match subsets of the 33-piece witness, with the following omitted piece indices. Indices are zero-based and refer to `dodindod_n33.json`.

| n | Omitted indices | Omitted shell | Maximum matched center distance |
|---|---|---|---|
| 29 | 1, 4, 13, 29 | Outer | 3.7923 × 10⁻¹⁴ |
| 30 | 1, 4, 29 | Outer | 3.5405 × 10⁻¹⁴ |
| 31 | 1, 29 | Outer | 3.7217 × 10⁻¹⁴ |
| 32 | 29 | Outer | 1.5596 × 10⁻¹⁴ |

The stored poses are not bitwise identical across these files. Their maximum matched coordinate difference, including quaternion coordinates, is below 3.2 × 10⁻¹⁴. The numerical subset relation explains the 90, 93, 96, 99, and 102 contact counts: each retained outer piece adds three edges to the unchanged 13-piece core. It also explains why wall-near counts rise from 16 to 20 and the largest orientation component from 17 to 21. The equal scale makes density grow by exactly 1/U³ per piece, approximately 0.0190072. These observations explain the archive plateau without claiming equality of the unknown optima.

## Icosahedra in a dodecahedron, count 15

The orientation partition has sizes 14 and 1. The singleton is piece index 11, centered within 2.4525 × 10⁻¹⁴ piece edges of the origin, with six near contacts. All 14 remaining pieces are wall-near at the central tolerance. Thus the orientation exception is an interior complementary piece in this witness, rather than a tilted peripheral piece. Hypothesis H10 tests whether its orientation is required by the surrounding arrangement.

## Reproduction

The script uses Python's standard library, the frozen archive, and the previously generated analysis files:

```text
python hypothesis_evidence.py --repo PATH_TO_FROZEN_REPOSITORY --analysis PATH_TO_ANALYSIS --out hypothesis-evidence.json
```

`hypothesis-evidence.json` includes source hashes, all shell indices, exact stored scale strings, contact classes, antipodal-pair residuals, pose matches, and relevant per-record metrics. Assertions require the expected 1 + 12 + 20 shell counts, direction residuals below 10⁻¹², the expected contact classes, agreement with nearest-shell pairs, and no contact within 5° of alignment. The input geometry and original records are preserved unchanged.
