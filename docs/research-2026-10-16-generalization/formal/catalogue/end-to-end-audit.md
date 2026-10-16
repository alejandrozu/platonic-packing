# End-to-end certificate audit

Audit date: 16 October 2026. Frozen catalogue commit:
`1abc63218db34cea95802aeb3b6d4a6b6fe1c61b`.

This is an independent read-through of `export_cubes.py`, `export_nd.py`,
`generate_lean.py`, `generate_nd_lean.py`, and their Lean semantic wrappers.
The complete source-binding audit is recorded in `end-to-end-source-audit.json`.
The portable standard-library reproducer is `audit_source_bindings.py`:
`python catalogue/audit_source_bindings.py` from the `formal` directory (or pass
its absolute path from any directory).
Successful Python export or this audit is **not** a Lean compilation receipt.
The final verified-record count must come from successful, axiom-audited Lean
builds of the generated modules.

## Source-binding result

All **402** selected source records passed the independent bounded audit:

| Dimension | Records | Selected families |
|---|---:|---|
| 3 | 99 | Cube in cube, n = 2 through 100 |
| 4 | 195 | c8/c8, c16/c16, c24/c24, c16/c24, c24/c16 |
| 5 | 62 | Hypercube/hypercube and orthoplex/orthoplex |
| 6 | 46 | Hypercube/hypercube and orthoplex/orthoplex |

For every record, the audit compared source bytes against the frozen input
inventory hash, compared the exported source path and source hash, and checked
piece count, dimension, container centre, and every piece centre. Cube raw
quaternions were compared coordinate by coordinate. Higher-dimensional raw
skew entries and diagonal signs were reconstructed from the original placement
layout and compared coordinate by coordinate. All seven selected canonical
higher-dimensional template arrays were compared against the frozen geometry
file; the listed template edge lengths were also checked exactly in Python.

The audit preserved the production numeric semantics: JSON integer literals
remain exact integers; decimal or exponent literals are read as binary64 and
then converted to that value's exact rational; rational strings retain their
exact rational value. It did not reinterpret unquoted decimals as exact decimal
rationals. No source placement or scale was perturbed.

All 303 higher-dimensional records have exact edge ratio `mu = 1`. Their
exported scale equals the source `s_full * mu`, and their piece and container
templates have matching exact squared edge lengths. No unit mismatch was
found in this selected subset. General non-unit edge-ratio claims remain
outside this subset.

## Geometric and implementation findings

1. **Whole bodies are certified.** `Rational.check_sound` extends finite
   inequalities to real convex hulls. `placement_body` connects the checked
   world vertices to affine images of one common template. Orthogonality and
   squared Euclidean distance preservation are derived in Lean, so separate
   perturbed vertex clouds cannot substitute for congruent pieces.
2. **The cube is identified geometrically.** `Cube.vertexBody_eq_unitBox` and
   the scale/translation and six-wall lemmas connect the canonical eight
   corners, ordinary unit cube, and ordinary container of side `s_full`.
3. **Every pair is covered.** The checker quantifies over every `i < j` and
   checks an explicit rational separating plane. It uses no unformalized
   circumradius or distant-pair shortcut. Reverse ordered pairs follow by
   symmetry. The audit confirmed exactly the complete ordered list of
   unordered pair keys for all 402 exports.
4. **Higher-dimensional containment uses the actual vertex hull.**
   `Barycentric.vertexCheck` checks nonnegative weights, weight sum one, and
   every coordinate of each placed vertex's convex combination. Containment
   is in the convex hull of the scaled, translated canonical container
   vertices; it does not assume that an external halfspace list is complete.
5. **Sparse support and padding are harmless.** Repeated indices and zero
   weights are legitimate convex combinations. The audit checked all index
   bounds, support widths, row counts, nonnegative weights, and weight sums.
   Missing weight rows default to zero and fail the required weight sum.
6. **The total-index implementation does not skip obligations.** For
   `i < j`, the array index `j-i-1` selects the intended triangular plane
   entry. An absent plane defaults to equal endpoints and fails the strict
   gap check. Missing rotations fail orthogonality, and missing Cayley source
   data fail the sign-product or inverse checks. Checked outer-array lengths
   prevent unnoticed truncation of the source placement list.
7. **Cayley placements retain their raw parameters.** The finite source
   checker verifies skew symmetry, signs in `{−1,+1}` with product one, an
   explicit inverse of `I-S`, and the full matrix equality. Its soundness
   theorem identifies that inverse with Lean's matrix inverse and proves
   determinant one generically, including for the actual real matrix.
8. **The verification claim concerns feasibility.** Positive separating gaps
   prove disjoint closed bodies, stronger than disjoint interiors. Wall
   containment may be weak. Neither condition proves that the reported scale
   is globally minimal.

No source-binding or geometric soundness defect was found in the inspected
architecture or the 402 exported source bindings.

## Remaining trust boundaries

- The JSON parser, input download/inventory process, Python exporter, and
  JSON-to-Lean transcription are not verified Lean programs. Their source
  correspondence was checked independently and hashes are published, but
  a SHA256 comment is not itself a kernel proof of JSON decoding.
- Lean verifies the explicitly supplied canonical coordinate models. The cube
  and the 4D, 5D and 6D hypercube templates have explicit unit-box identification
  theorems. For the orthoplex and 24-cell families, there is not yet a separate
  Lean classification theorem identifying the coordinate hull as the named
  regular polytope, nor a verification of every metadata convention.
- Source scale conversion and shape labels require the provenance check
  above. Generated assertions for canonical array sizes and the raw
  `s_full * mu` scale equality strengthen this correspondence; they do not
  replace a verified parser or a regular-polytope classification theorem.
- This selected rational subset does not cover the full frozen catalogue,
  algebraic 3D templates, irrational higher-dimensional templates, or the
  six source-only bounds without coordinate witnesses.
- Each record is Lean verified only after its own generated module actually
  compiles and the printed theorem axioms contain no unexpected axioms.
  Planned, exported, generated, pending, failed, or timed-out modules must
  never be counted as verified records.
- No result verifies optimizer convergence, search completeness, the Python
  certifier implementation, the live evolving catalogue, or global optimality.

## Suggested paper wording

After the build receipts establish the final count, use:

> We instantiate the formal certificate checker on N frozen catalogue
> records in dimensions 3–6. For each instance, Lean checks the exact rational
> placements, congruence-preserving transformations, whole-body containment,
> and separation of every pair. Cubes and higher-dimensional hypercubes are
> identified with ordinary unit boxes; other higher-dimensional conclusions
> concern the supplied canonical coordinate models. All instance proofs are checked by Lean's kernel using
> exact arithmetic. Source parsing and transcription remain outside the
> kernel and are covered by published hashes and a separate source-binding
> audit. The results certify feasibility at the recorded scales, not global
> optimality.

Replace `N` with the actual successful build count. State **402** only if all
99 cube modules and all 303 higher-dimensional modules have completed
successfully. Prefer the audited record count and explicit trust boundary to
a headline claim that the entire catalogue or search software is verified.
