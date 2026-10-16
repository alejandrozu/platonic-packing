# Lean verification of frozen convex-polytope packing certificates

This directory contains dimension-independent geometric soundness proofs, an
exact rational certificate checker, source-bound catalogue instances, and the
original two-cube regression example. Catalogue instances concern actual
recorded placements at their stored scales. They establish feasibility, not
optimizer correctness or global optimality.

**Final number of distinct catalogue records verified by Lean: 532 across all 140 frozen families.**
This comprises all 402 rational targets and 130 additional two-piece witnesses: 85 other 3D families and 45 other 4D–6D families. This count must come from successful, axiom-audited build
receipts. Exporting JSON, generating a Lean file, or passing a Python audit does
not establish Lean verification. Ordinary and fragmented proofs of the same
original record count once.

## Frozen scope and eligible targets

The snapshot is repository commit
`1abc63218db34cea95802aeb3b6d4a6b6fe1c61b`. Original input bytes, immutable URLs,
SHA256 hashes, and attribution are recorded in
[`catalogue/inputs/source-manifest.json`](catalogue/inputs/source-manifest.json).
There are **402 selected rational export targets**:

| Dimension | Eligible records | Families and piece counts |
|---|---:|---|
| 3 | 99 | Cube in cube, n = 2–100 |
| 4 | 195 | c8/c8, c16/c16, c24/c24, c16/c24, c24/c16; n = 2–40 |
| 5 | 62 | Hypercube/hypercube and orthoplex/orthoplex; n = 2–32 |
| 6 | 46 | Hypercube/hypercube and orthoplex/orthoplex; n = 2–24 |

All 303 selected higher-dimensional records have exact edge ratio `mu = 1`.
The container coordinate scale is the source `s_full * mu`. Placements and
scales are not perturbed.

The frozen catalogue contains 10,398 coordinate-backed records and six
source-only bounds. The 402 targets are a rational subset. Other unit-edge 3D
templates require algebraic coordinates. Other higher-dimensional cases may
need algebraic templates or irrational edge normalization, even when their
unscaled vertices are rational. They remain outside the rational importer;
the separate algebraic route below handles selected exact-coordinate witnesses.
Source-only bounds without witnesses have no catalogue packing proof here.

## What the kernel proves

`Rational.lean` defines finite, dimension-indexed rational certificates. Exact
row Gram identities establish orthogonality; Lean proves preservation of squared
Euclidean distances and identifies placed vertices with affine images of one
common template. A template denotes its **real convex hull**. Thus the conclusion
concerns whole congruent bodies, not independently perturbed vertex clouds.

Containment and separation extend finite arithmetic to full convex bodies. The
pair checker quantifies over **every unordered pair `i < j`**, requiring rational
projection bounds `lower < upper` and the necessary vertex inequalities. There
is no unverified distant-pair or circumradius shortcut. A missing plane defaults
to equal endpoints and fails the strict gap check. Floating point may propose
a direction; only the subsequently checked exact rational inequalities matter.

`Cube.lean` identifies the eight canonical corners with the ordinary side-one
cube, and identifies its scaled, translated container with six coordinate
walls. `Catalogue.lean` binds each cube's raw nonzero quaternion to the exact
matrix `H(q) / (q · q)` and checks determinant one. `CubeFast.lean` proves exact
support bounds for affine boxes in any finite dimension. Its cube checker uses
those bounds to imply every original vertex test, reducing repeated arithmetic
without weakening the geometric result.

`AxisFast.lean` additionally checks exact cached coordinate supports once per
piece. A signed-axis tag is accepted only after checking the full plane normal;
other planes retain the general support test. This reduces repeated arithmetic
while preserving every original source, rigidity, wall and pair obligation.

`BoxGeometry.lean` proves that the convex hull of all sign corners is the
coordinate box in every finite dimension. Kernel-checked finite coordinate and
corner-coverage checks identify the frozen c8, hc5, and hc6 arrays with ordinary
4D, 5D, and 6D unit hypercubes. A separate theorem identifies positive scaling
and translation with a coordinate box of the requested side length.

`Barycentric.lean` checks containment in the actual canonical container vertex
hull. Every placed vertex has a convex combination of scaled, translated
container vertices: all weights are nonnegative, sum to one, and give exact
equality in every coordinate. Sparse width is `d + 2`; repeated indices and
zero-weight padding are valid. This avoids assuming that an external halfspace
list is complete or equals the vertex hull. For c16, c24, op5, and op6, the
conclusion concerns the supplied canonical coordinate models.
`Extensions/NDIdentity.lean` additionally identifies the c16/op5/op6 arrays with
the standard convex hull of the positive and negative coordinate basis, and
c24 with the hull of all vectors with exactly two coordinates equal to +1 or
-1 and the other coordinates zero. These finite coordinate-model identities
do not separately prove all face, edge-length and regularity properties.

`Cayley.lean` connects higher-dimensional matrices with their original skew
parameters and diagonal signs. Its finite checker verifies:

- `Sᵀ = -S`;
- diagonal signs in `{−1, +1}` with product one;
- the exact inverse witness `Ainv * (I - S) = I`;
- `R = diag(D) * Ainv * (I + S)`.

The soundness theorem identifies `Ainv` with Lean's matrix inverse and derives
determinant one, also for the actual real placement matrix. With the rational
Gram check, this establishes proper rigid placements. The generic determinant
argument avoids factorial-size determinant evaluation for every instance.

The original core also proves soundness of vertex/face and separating-plane
certificates, affine transport, outer approximation, Minkowski opening
containment and inclusion monotonicity, convex blends, subpackings, and nested
packings. `Example.lean` retains the exact two-unit-cubes example in a side-5/2
cube. It is a regression witness and is not counted as a catalogue record.

## Arbitrary dimension and computational cost

`Extensions/GenericDimension.lean` proves radius nesting and the exact zero-radius
endpoint for Euclidean-ball openings, nesting for convex blends with an inscribed
body, and preservation of feasible packings when pieces are replaced by the
corresponding contained bodies. The explicit corollaries quantify over every
`d : Nat` and use `EuclideanSpace R (Fin d)`, whose norm is Euclidean, rather than
the supremum norm on the default finite function space. The opening statements
also hold in arbitrary real normed vector spaces. They do not assume that every
facet is tangent to an inscribed sphere. Hardening an arbitrary soft packing need
not preserve feasibility, and optimizer convergence is not asserted.

`Extensions/Complexity.lean` proves that a strictly improving finite support-walk
trace has no repetitions, visits at most V vertices, and scans at most 2E graph
adjacency entries. With d coordinate products per dot product, this bounds one
support query by O(d(E+1)) arithmetic work. The manuscript derives conditional
per-step and per-simulation costs from the actual search loops, distinguishing
piece-pair enumeration, support queries, matrix work, solver sizes and exact
verification. It does not claim a formal execution-time proof of the Python
simulator. A dimension-general geometric theorem does not imply polynomial time
in dimension: the explicit vertex or facet counts can grow exponentially.

`Extensions/CayleyGeometry.lean` derives row orthogonality from the checked raw
Cayley formula and inverse witness in every finite dimension. This avoids
recomputing the same numerical Gram identities when a certificate selects that
proof route. `Extensions/NDGeometry.lean`, `NDModels.lean`, `NDSupport.lean` and
`BoxSupport.lean` provide exact support formulas and geometric containment routes
for the supplied box and orthoplex coordinate hulls. These routes establish the
same whole-body conclusion as the explicit-vertex or barycentric tests; a faster
proof route does not change the native packing.

## Algebraic-coordinate extension

[`catalogue/algebraic/README.md`](catalogue/algebraic/README.md) documents a separate
proof-producing route for exact algebraic canonical coordinates. Its Lean
interval/root modules define unique exact real roots and bound polynomial and
positive square-root expressions without replacing vertices by rational points.
The dimension-independent affine-basis theorem proves membership in the actual
container vertex hull using checked Cramer identities, a centred template and
nonnegative corrected barycentric weights. The record-level checker also proves
source-bound proper placements and strict separation of every unordered pair.

The algebraic manifest separates proposed witnesses from successfully compiled,
source-bound instances. Its completed records are additional to the rational
cohort reported above. The frozen parser, geometry naming and transcription are
audited external boundaries. Formal identification of every canonical hull with
its conventional named solid, including all unit-edge facts, is not claimed.
Root/normalizer semantics are proved. The separate `NDReferenceEdges` leaf
checks selected exact squared endpoint distances for twelve ND templates and
45 positive native conversion identities `mu² * edge_C² = edge_P²`.
Its binding report records the source indices and literal hashes. A separate
exact Python audit checks all 2,490 listed edges; adjacency and full regularity
classification remain outside these finite arithmetic proofs.
The current determinant-interval checker explicitly uses the Leibniz permutation
sum; its factorial dimension cost is stated separately from simulation runtime.
The higher-dimensional quadratic-coordinate route instead checks an explicitly
supplied inverse matrix over rational coefficient pairs. Its exact real
embedding, source edge-normalization factor and diagonal scaling are proved in
`Algebraic/QuadraticInverse.lean`, `QuadraticScale.lean` and `PackingND.lean`.
Inverse checking takes cubic arithmetic work in the affine-basis dimension;
proposing an inverse remains outside the kernel. Record counts still require
successful, source-bound individual build receipts.

## Exact numbers and source boundary

The importer preserves the production checker's numeric convention:

- An unquoted nonintegral JSON number is decoded to binary64 and then converted
  with `Fraction(float)` to that binary64 value's **exact rational**.
- JSON integers and rational strings retain their exact rational values.
- Printed decimals are not silently reinterpreted as exact decimal rationals.

Raw centres, quaternions, skew entries, diagonal signs, scales, canonical
templates, and container centres are compared with frozen sources by
[`catalogue/audit_source_bindings.py`](catalogue/audit_source_bindings.py).
The independent audit and export reports cover the 402 selected source bindings.
They are distinct from Lean build receipts.

The JSON parser, binary64 decoding, Python exporter, geometry import, SHA256
implementation, and JSON-to-Lean transcription remain outside the Lean kernel.
A source hash in a generated comment is provenance, not a kernel proof of JSON
decoding. Lean checks the exact literals it receives, their source-parameter
matrix identities, and their geometric implications. Published original bytes,
hashes, the independent source audit, exporters, and generated modules make the
external correspondence inspectable and reproducible.

No theorem verifies the archive's Python algebraic-number arithmetic, optimizer,
general certifier implementation, or every entry of the live evolving website.

## Reproduce

Use Lean 4.31.0 and the mathlib revision pinned by `lake-manifest.json`.
Keep the supplied publication files unchanged. Perform new builds in a separate
working copy of this `formal` directory; rebuilding creates local proof objects
and fresh receipts, which are not part of the published source tree.

The completed evidence lives in `ci-evidence/published-402/`,
`ci-evidence/published-85/` and `ci-evidence/published-45/`. Each has a portable
summary, a source/log ZIP and its byte-hash manifest. Every build environment
retains its own `environments/ENVIRONMENT_ID/formal/` namespace, core receipt,
numeric sources, logs and original plans. The environment-scoped
`catalogue/verified-module-manifest.json` is an index, not a flat runner manifest.

From this directory, validate and inspect a published environment:

```text
python evidence_bundle.py --cohort ci-evidence/published-402
python evidence_bundle.py --cohort ci-evidence/published-402 --extract ../proof-inspection --environment ENVIRONMENT_ID
```

Replace `ENVIRONMENT_ID` with an identifier from that cohort's
`verified-catalogue.json`. The same commands apply to the other two cohorts.
On Windows, choose a short writable work/extraction directory, for example
`C:/p`, because deeply named proof fragments can exceed legacy path limits.
The helper checks archive hashes, every member, semantic axiom audits and the
complete source/log/receipt closure. It rejects unsafe paths and differing
existing output bytes. It never merges environment roots or restores compiled
objects. Original object hashes remain provenance; objects from different
operating systems must not be substituted into an archived receipt.

Fresh rational-cohort verification regenerates local plans from the same
frozen JSON, avoiding reuse of platform-dependent object pins. In the separate
working copy, first install the pinned dependencies and build the core:

```text
lake exe cache get
lake build
python verify_core.py --mathlib-project .
python evidence_bundle.py --input-manifest catalogue/rational-witnesses-manifest.json --input-archive rational-witnesses.zip --embedded-manifest witness-manifest.json --extract catalogue
python catalogue/audit_source_bindings.py
python verify_extensions.py --mathlib-project . --modules PackingCertificates/Extensions/NDGeometry.lean PackingCertificates/Extensions/NDSupport.lean PackingCertificates/Extensions/NDModels.lean PackingCertificates/Extensions/BoxSupport.lean PackingCertificates/Extensions/CayleyGeometry.lean PackingCertificates/Extensions/NDSupportRegression.lean --output support225-generic-verification.json
python catalogue/run_support_ci_shard.py --mathlib-project . --scope all402 --block-size 8 --shard-count 12 --shard-index 0
```

Repeat the final command with shard indices 1 through 11 to cover all 402
targets; run one shard at a time unless sufficient memory is available.
`--only RECORD_ID` selects a smaller explicit test. The driver writes its fresh
plans, status and receipts under `catalogue/ci-support/shard-XX/`, including
ordinary, support-based and fragmented proof routes as needed. It checks every
required source, arithmetic block and aggregate. It does not rewrite the
immutable `ci-evidence/published-*` archives. `--memory-mb` and `--timeout`
control resources, not the mathematical checks.

The extra algebraic targets have a bounded shared input archive: 130 selected
native witnesses, 130 proposed certificates, exact geometry data, target
registries and public target-selection metadata. The full background native
and exported-witness collections are not included. Restore these inputs and
regenerate their reference transcriptions in the separate working copy:

```text
python evidence_bundle.py --input-manifest catalogue/algebraic/pilot-inputs-and-proposals-manifest.json --extract .
python catalogue/algebraic/geometry_intervals.py --lean
python catalogue/algebraic/nd_geometry.py
python catalogue/algebraic/generate_3d.py
python catalogue/algebraic/generate_nd_pilots.py
python catalogue/algebraic/generate_fragmented_nd_pilots.py
python catalogue/algebraic/run_ci_pilots.py --write-assets
python catalogue/algebraic/run_ci_nd45.py --write-assets
python catalogue/algebraic/run_ci_pilots.py --mathlib-project . --shard-count 8 --shard-index 0
python catalogue/algebraic/run_ci_nd45.py --mathlib-project . --shard-count 12 --shard-index 0
```

Repeat the 3D driver for indices 1 through 7, and the ND driver for indices 1
through 11. Their source-bound runners generate bounded numerical proof modules
and require complete imported-source/object receipts and the actual final
semantic declarations. New receipts are written under their local `ci/` and
`ci-nd45/` directories. The reference monolithic files are transcriptions;
their generation alone does not establish verification. The archived source
snapshots preserve the exact original proof route and plan even when a fresh
rerun chooses a different checked fragmentation.

After restoring the shared ND inputs above, reproduce the separate reference-edge
audit and the source-bound Lean leaf in the working copy:

```text
python catalogue/nd-edge-scale-audit.py --output catalogue/rebuilt-nd-edge-scale-audit.json
python catalogue/generate_nd_reference_edges.py --check
python verify_extensions.py --mathlib-project . --modules PackingCertificates/Algebraic/Interval.lean PackingCertificates/Algebraic/Root.lean PackingCertificates/Algebraic/Template.lean PackingCertificates/Algebraic/Simplex.lean PackingCertificates/Algebraic/Placement.lean PackingCertificates/Algebraic/QuadraticScale.lean PackingCertificates/Algebraic/QuadraticInverse.lean PackingCertificates/Algebraic/NDReferenceEdges.lean --output catalogue/rebuilt-nd-reference-edge-lean-verification.json
```

The first command is an exact Python audit. The final command checks the Lean
leaf and its generic dependencies and writes a new build receipt; keep the two
reports distinct. `--check` checks the leaf's frozen literal rendering and
refreshes its source-binding metadata only in this separate working copy.

The generic dimension and complexity statements can also be rebuilt after
their support dependencies above:

```text
python verify_extensions.py --mathlib-project . --modules PackingCertificates/Extensions/GenericDimension.lean PackingCertificates/Extensions/Complexity.lean PackingCertificates/Extensions/NDIdentity.lean --output rebuilt-method-verification.json
```

A compatible, already compiled mathlib project may replace `.` in
`--mathlib-project`; `--lean` selects an explicit executable of the pinned
version. NumPy/SciPy are required by numerical export and some source-binding
helpers; archive validation and unpacking use only Python's standard library. No evolving
website fetch is required. Failed, pending or timed-out builds never count as
verified records; only complete successful kernel builds with the required
source and axiom audits qualify.

## Axioms and mathematical limits

The sources use no `sorry`, `admit`, additional axioms, or `native_decide`.
Finite instance conditions use **`by decide +kernel`**. Tactics and exact
arithmetic produce terms checked by Lean's kernel. Ordinary mathlib proofs may
use the standard logical axioms **`propext`, `Classical.choice`, `Quot.sound`**;
the audits report them. Numerical export flags never replace proof terms.

The result establishes **feasibility at the exact recorded scale**. Positive
separation gaps prove disjoint closed bodies, stronger than disjoint interiors;
wall containment may be weak. Touching packings require a corresponding
weak-separation/interior argument or a separately justified perturbation. No
theorem proves heuristic convergence, search completeness, global optimality,
or the full catalogue. Algebraic-coordinate instances require their own
completed source-bound build receipts, separately from the rational cohort.
