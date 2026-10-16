The 85-record pilot build is separate from the 402 rational certificates and
from the full 8,409-record 3D proposal export. Generated proposals do not count
as Lean-verified records.

Publication assets are explicitly listed, with byte sizes and SHA-256 hashes,
in `ci-pilot-assets.json`. Copy these 353 files relative to the formal directory,
preserving their bytes, and also copy the manifest itself. The list includes
the 85 source JSON files, their 85 proposals and 85 Lean modules, all 56 exact
canonical templates, root data, generic proofs, regression tests, and builders.
It does not include the full proposal/input directories. The nested paper
`.gitattributes` must continue to disable text conversion.

For CI, use eight shard indices 0–7 with workflow `max-parallel: 6`. Each Linux
worker needs Lean 4.31.0 and the already-built mathlib revision pinned by
`lake-manifest.json`. Compile the direct core first:

```sh
python verify_core.py --mathlib-project . --memory-mb 8192 --timeout 900
python catalogue/algebraic/run_ci_pilots.py \
  --mathlib-project . --shard-index "$SHARD_INDEX" --shard-count 8 \
  --memory-mb 8192 --timeout 1800 --job-budget-seconds 19800
```

The deterministic scheduling plan has shard sizes 9, 10, 11, 11, 11, 11, 11,
11. The integer workload estimate only schedules jobs; it is not a runtime
theorem. Every worker compiles shared generic proofs and the needed canonical
templates once. Later records can reuse those modules only when the recorded
source, object, log, axiom audit, and every transitive local import still match.
The malformed-certificate regression is included in every record's build order
and its successful stage is reused on the same conditions.

Always upload the worker's `catalogue/algebraic/ci/shard-NN` directory, including
on job failure. `evidence.zip` includes an explicit SHA inventory, the exact
source/geometry/render-bound record receipts, matching Linux proof objects and
logs, and the direct-core receipt. Failed or timed-out records remain marked
unverified. A worker succeeds only when every assigned record has a successful
kernel receipt and its prescribed semantic declaration was audited.

Read-only preflight without a compiler:

```sh
python catalogue/algebraic/run_ci_pilots.py --plan-only
python catalogue/algebraic/run_verified.py --mathlib-project . --plan-only
```

The parser/generator implementation remains an explicit trust boundary.
Independent checks bind exact binary64/rational source poses and scale, raw
quaternions, all unordered pairs, exact canonical coordinate polynomials,
isolating intervals and normalization, and the byte-for-byte generated Lean
source. The kernel establishes packing for those transcribed exact objects;
the classification of every named template as the intended regular solid is
not silently promoted to a proved theorem.
