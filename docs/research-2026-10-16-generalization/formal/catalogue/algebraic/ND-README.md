# Remaining ND family certificates

`generated-nd-pilots-registry.json` prepares the minimum coordinate-backed frozen
selected witness in each of the 45 remaining 4D–6D problem families. Preparation
includes 9,666 placed vertices, 45 unordered pairs and 1,918 affine-basis caches.
These are target counts, not counts of successful Lean builds. Verified coverage
is recorded only in successful source-bound receipts.

The native coordinates remain exact. JSON integer pose/scale tokens remain exact
integers; decimal or exponent tokens mean their binary64 values converted to
exact rational numbers. Every Cayley skew parameter,
diagonal sign, centre and `s_full` is preserved. The actual native `mu` string is
preserved and proved equal to its real radical expression; no decimal substitute
is used for an algebraic edge ratio.

## Proof route

The 12 raw canonical ND templates use coordinates in `Q(√r)`, with
`r ∈ {2,5,6,7}`; rational templates have a zero radical coefficient. Four checked
positively isolated roots are formally identified with the ordinary real square
roots. Every native edge ratio has the form `a+b√r` or `√2(a+b√r)`, with `b=0`
when the container's primitive root differs from √5. Exact rational coefficient
identities and a positive interval bound prove `mu = 1/√D(√r)`, for a linear
polynomial `D`. The container template absorbs this positive factor, while the
certificate's outer scale stays exactly the rational source `s_full`.

`PackingCertificates/Algebraic/QuadraticScale.lean` proves that normalization
identity. `RootSqrt.lean` links its root semantics to literal real square roots.

For each affine basis, the exporter supplies a matrix inverse whose entries are
pairs of rational coefficients. `QuadraticInverse.inverseCheck` verifies
`A B = I` by coefficient arithmetic, in cubic matrix-operation count. A proved
embedding at the exact real root transfers that identity to real matrices.
Diagonal scaling transfers the raw inverse to the actual `mu`-scaled container.
Thus higher-dimensional caches do not use a factorial determinant expansion.

Checked interval matrix/vector products prove that all corrected barycentric
weights are nonnegative. Their exact real mass and coordinate identities follow
from the proved matrix inverse. The dimension-independent centered convex-hull
theorem therefore proves membership in the actual container vertex hull.

`PackingND.lean` combines the inverse-basis membership checks with source-linked
Cayley rotations, exact Gram identities, proper orientation and a strict plane
for every unordered pair. The source rotations preserve squared Euclidean
distances for all real points. The conclusion concerns complete placed hulls,
including all faces and interiors.

## Reproduction

From the parent `formal` directory:

```text
python catalogue/algebraic/nd_geometry.py
python catalogue/algebraic/export_nd_pilots.py
python catalogue/algebraic/generate_nd_pilots.py
python catalogue/algebraic/run_verified_nd.py --mathlib-project PATH_TO_PINNED_MATHLIB_PROJECT --only c5inc5_n02 --receipt catalogue/algebraic/nd-first-verification.json
```

Omit `--only` for all 45 targets. The runner inherits strict transitive source and
object closure receipts and also checks native Cayley parameters, exact literal
edge ratios, raw canonical geometry coefficients, full pair coverage and exact
generated Lean bytes. A successful ND receipt additionally requires both
`.native_mu_binding` and `.native_mu_literal` axiom audits beside the actual
packing `.valid` declaration.

Generated numerical assets explicitly use CRLF bytes on every platform and have
Git text normalization disabled. Original native inputs are preserved byte for
byte. The usual JSON/parser/transcription boundary is explicit and audited;
Python or SciPy output does not become a mathematical premise. The proof modules
use the standard Lean/mathlib axioms only, and numerical checks use
`decide +kernel`.

Large instances can be split into independently checked data/proof blocks. The
unfragmented sources and original source-bound registry remain the reference
transcription; a fragment runner must attest the same native geometry, poses,
normalization and complete numerical tests.
