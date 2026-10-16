# Lean verification of frozen convex-polytope packing certificates

This directory contains dimension-independent geometric soundness proofs, an
exact rational certificate checker, source-bound catalogue instances, and the
original two-cube regression example. Catalogue instances concern actual
recorded placements at their stored scales. They establish feasibility, not
optimizer correctness or global optimality.

**Final number of distinct catalogue records verified by Lean:
57.** This count must come from successful, axiom-audited build
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
unscaled vertices are rational. Those cases and source-only bounds without
witnesses remain outside this importer.

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
conclusion concerns the supplied canonical coordinate models; this extension
does not separately classify those models as regular polytopes.

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

The project pins Lean **4.31.0** and mathlib commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Python 3 is required for import and
generation. The ND exporter additionally uses NumPy/SciPy for untrusted simplex
or plane proposals, followed by exact rational checks. The cube exporter and
independent source audit use Python's standard library.

From this `formal` directory, with elan/lake and Python available:

```sh
lake update
lake exe cache get
lake build
lake env lean Audit.lean
python verify_core.py --mathlib-project .
python catalogue/unpack_witnesses.py
python catalogue/audit_source_bindings.py
python catalogue/run_chunked.py --mathlib-project . --timeout 1800 --manifest verified-module-manifest.json --receipt rebuilt-catalogue-verification.json
```

The supplied verified-module manifest rebuilds exactly the completed cohort.
The sequential runner supports both ordinary instances and instances split
across shared-data, arithmetic-block and aggregate modules. Every required
module must compile; its source and dependency hashes are recorded.
The default library build checks the generic library without automatically
building every catalogue instance. The separate core runner also checks the
negative regression certificates and writes a fresh build receipt.

To regenerate proposed witnesses after the unpacking and source audit above:

```sh
# Optional full regeneration; NumPy/SciPy are needed by the ND exporter.
python catalogue/export_cubes.py
python catalogue/export_nd.py
python catalogue/audit_source_bindings.py
python catalogue/generate_lean.py
python catalogue/generate_nd_lean.py
python catalogue/generate_fragmented_cubes.py
python catalogue/generate_axis_cubes.py
python catalogue/generate_fragmented_nd.py
```

Use the frozen inputs supplied here; an evolving website fetch is unnecessary.
Exporters write `witnesses/` and `witnesses_nd/`; their reports describe export
status only. The ordinary ND generator also writes canonical template
declarations. Fragmented generators preserve the data and separate source,
Gram, containment, and pair checks into smaller proofs. The final geometric
result is assembled from these checked proofs.

Build the support modules before the generated record modules:

```sh
lake build PackingCertificates.Core PackingCertificates.Rational PackingCertificates.Cube PackingCertificates.Catalogue PackingCertificates.Barycentric PackingCertificates.Cayley PackingCertificates.TemplateData PackingCertificates.BoxGeometry PackingCertificates.CubeFast PackingCertificates.Example
lake build PackingCertificates
lake env lean Audit.lean
```

Then compile generated modules and save separate receipts:

```sh
python catalogue/run_lean.py --mathlib-project . --workers 1 --timeout 1800 --manifest generated-fragmented-cube-modules.json --receipt lean-cube-verification.json
python catalogue/run_lean.py --mathlib-project . --workers 1 --timeout 1800 --manifest generated-fragmented-nd-modules.json --receipt lean-nd-verification.json
```

The runner includes this project's `.lake/build/lib/lean` and its cached
dependency build paths. `--mathlib-project` may instead name an existing project
with the same pinned compiled dependency tree. The runner prefers `lean` on
`PATH`; `--lean` can select its local path explicitly, for example
`--lean /path/to/lean`. The executable must match the pinned version.

For a smaller reproduction, generators accept `--max-n`; fragmented generators
also accept `--only` with original record IDs. Runner `--only` uses manifest IDs,
which carry the `fragmented_` prefix for fragmented modules. Fragmentation bounds
individual reductions, but large exact computations can still require
substantial memory and time.
The ND generator provides `--per-vertex` and `--per-pair` fallbacks when a row
or whole piece is too large for the available memory. The axis-cached cube
generator writes its own `generated-axis-cube-modules.json` manifest.

Failed, interrupted, pending, or timed-out modules are not verified records.
Only a successful compiler exit, produced `.olean`, and acceptable printed
axiom audit count toward the total. Manifests and receipts identify the exact
module, command, source hash, log hash, and outcome.

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
or the full catalogue. Algebraic-coordinate extensions remain future work.
