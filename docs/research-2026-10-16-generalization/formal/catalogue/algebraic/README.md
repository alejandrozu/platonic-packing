# Algebraic-coordinate catalogue certificates

This directory extends the rational catalogue pipeline to the exact canonical
coordinate hulls of the frozen three-dimensional Platonic, Archimedean, Catalan,
prism and antiprism inputs. An exported JSON file, generated Lean source, or
successful Python calculation does **not** count as a formal verification.
Only successful source-bound Lean receipts identify verified records.

## Frozen data and scope

The input freeze is `1abc63218db34cea95802aeb3b6d4a6b6fe1c61b` of
`alejandrozu/platonic-packing`. `input-manifest.json` lists 9,996 original native
record files outside the earlier 402 rational targets, with immutable URLs,
SHA256 digests and preserved native attribution. This includes 8,409 3D records
in 85 problem families and 1,587 additional higher-dimensional records. Six
source-only bounds without a selected coordinate witness are excluded.

The 3D exporter operates on the actual selected JSON's `s_full`, centres and
scalar-first quaternions. It never attaches those coordinates to a different,
historically smaller scale from the index. JSON integers remain exact integers;
decimal or exponent tokens first take their native Python binary64 value and
then become exactly `Fraction(value)`. Quoted rational strings retain their exact
rational meaning. All 8,409 frozen
3D source poses and scales are rational under those semantics.

The initial pilot is the minimum available coordinate-backed selected record in
each of the 85 3D problem families. It includes 3,464 placed vertices and 85
unordered pairs. Its proposal report is `export3d-report.json`; this is a
preparation report, not a Lean success report. Full exports use a separate
`export3d-all-report.json` so that the pilot registry remains stable.

A separate native higher-dimensional route selects one record from each of the
45 remaining 4D–6D families, comprising 9,666 placed vertices and 45 unordered
pairs. These preparation totals describe the selected inputs, not successful
builds. The two pilot cohorts together cover every family outside the ten-family
rational cohort; they do not cover every population in those families.

## Completed kernel evidence

The completed portable cohorts contain **85/85 selected 3D witnesses and 45/45 selected higher-dimensional witnesses**, one two-piece record per remaining frozen family. All 130 have successful source-bound, axiom-audited Lean evidence. Together with the 402 rational records, the verified set covers all 140 frozen families. The 9,866 coordinate-backed records outside this combined 532-record set remain outside this formal claim. Proposal/export reports below describe preparation; the authoritative proof reports are `../../ci-evidence/published-85/verified-catalogue.json` and `../../ci-evidence/published-45/verified-catalogue.json`.

The publication includes the bounded 130-witness input/proposal archive, not the full local `input-manifest.json` or background witness tree. Use the parent [`formal/README.md`](../../README.md#reproduce) for reconstruction from the packaged ZIPs; the full-inventory commands below describe the separate research workspace.

## Formal meaning

The new Lean modules live in `PackingCertificates/Algebraic/`:

- `Interval.lean` proves rational interval arithmetic, checked outward widening,
  square-root bounds from exact rational squares, and Horner evaluation.
- `Root.lean` proves existence and uniqueness of each canonical real root from
  exact opposite endpoint signs and a nonzero divided-difference interval. The
  56 3D templates use 13 shared root specifications. No external root-counting
  oracle is trusted.
- `Template.lean` defines the actual real canonical vertex as the source
  polynomial at that unique root, optionally divided by the positive square
  root of its source `D` polynomial. Intervals enclose that exact vertex; they
  do not replace it with a rational point. Exact coefficient cancellation also
  proves that all canonical vertices sum to zero.
- `Simplex.lean` proves a dimension-independent Cramer certificate for membership
  in the actual container vertex hull. A uniform nonnegative baseline weight on
  every container vertex and corrections on an injective affine basis give a
  convex combination with exact total mass and coordinates. Cached determinant
  and adjugate interval bounds are themselves checked against the actual basis.
- `Placement.lean` proves that rational interval transforms enclose the exact
  real rigid placement and its exact container-normalized point. Membership of
  all normalized vertices implies containment of the whole piece hull.
- `Packing.lean` combines these checks. Every raw quaternion-to-matrix relation,
  proper determinant and row Gram identity is checked exactly. The resulting
  maps preserve squared Euclidean distances for **all real points**. Every
  placed vertex has a checked container-hull membership witness, and every
  unordered pair has a strict rational separating plane. Therefore the actual
  closed placed bodies are contained and pairwise disjoint.
- `QuadraticScale.lean`, `QuadraticInverse.lean` and `PackingND.lean` handle
  native higher-dimensional templates in quadratic number fields. A supplied
  affine-basis inverse is checked exactly as rational coefficient pairs and
  transported to the real coordinates. Diagonal scaling retains the original
  positive algebraic edge factor; the source's exact expression for that factor
  is audited separately. Checked raw Cayley data define proper rotations, and
  the final theorem proves actual container-hull containment and all pairwise
  separations.

Bounded proof fragments split basis caches, placed vertices and separating-plane
checks into separate kernel computations. A final theorem assembles complete
coverage of the original certificate. The independent source audit rejects
missing or repeated fragment indices and re-renders every generated source from
the immutable original data. Fragmenting a proof does not modify a placement,
scale, canonical coordinate or mathematical conclusion.

The geometric conclusions concern the exact frozen canonical coordinate hulls.
They do not additionally prove the conventional named-solid classification or
all edge/face normalization facts from scratch. The frozen geometry file, JSON
parser and deterministic exporter/transcription remain an explicit audited
boundary. Native credits and complete original public inputs are preserved.

The audited declarations use only the usual Lean/mathlib axioms `propext`,
`Classical.choice` and `Quot.sound`. Numerical instance proofs use
`decide +kernel`; they do not use `native_decide`, `sorry`, proof axioms for
floating-point output, or an assumption that Python's result is correct.

## Reproduction

Run from the `formal` directory with Python, pinned Lean 4.31.0, and the pinned
mathlib revision from the parent formal project. SciPy is needed only when
regenerating numerical proposals; it is not trusted by the proof checker.

```text
python catalogue/algebraic/inventory_templates.py
python catalogue/algebraic/fetch_inputs.py --workers 8
python catalogue/algebraic/geometry_intervals.py --lean
python catalogue/algebraic/export_3d.py
python catalogue/algebraic/generate_3d.py
python catalogue/algebraic/run_verified.py --mathlib-project PATH_TO_PINNED_MATHLIB_PROJECT --only tetintet_n02_pingyou_20261013 --receipt catalogue/algebraic/tet2-verification.json
```

`run_verified.py` rebuilds the transitive local extension dependencies, checks
the successful pinned direct-core receipt, snapshots imported source/object
hashes, validates original native scale/poses against the proposals, requires the
prescribed semantic `.valid` declaration, and records its axiom audit and log.
Use `--resume` with the same receipt to reuse only matching successful stages and
unchanged imported dependencies. Large instances use the bounded fragment
generators and corresponding `run_verified_fragmented_3d.py` or
`run_verified_fragmented_nd.py` runners. The CI entry points are
`run_ci_pilots.py` for the eight 3D shards and `run_ci_nd45.py` for the twelve ND
shards. Each worker retains complete source, object, log and dependency receipts;
the portable publication keeps source/log archives with separate environment
namespaces, while the raw build ZIPs preserve the original objects.

The full 8,409-record 3D preparation can be resumed independently:

```text
python catalogue/algebraic/export_3d.py --all --resume
python catalogue/algebraic/generate_3d.py --all
python catalogue/algebraic/run_verified.py --registry catalogue/algebraic/generated3d-all-registry.json --mathlib-project PATH_TO_PINNED_MATHLIB_PROJECT --receipt catalogue/algebraic/full3d-verification.json --resume
```

Of the 1,587 ND records outside the rational cohort, the 45 selected witnesses
are included in the completed formal set; the other 1,542 remain outside it.
The 3D exporter does not certify ND records. A long preparation or proof run may be
partial; inspect the receipt's exact verified/unverified record lists rather
than inferring coverage from a directory size or a target count.
