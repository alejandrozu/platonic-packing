# Importing and publishing source-bound CI evidence

From the paper output directory, run one metadata/download/validation pass:

```text
python ci-evidence/ingest_ci.py --run-id 38849574471 --commit 03d3fe6f155c15b2741f30d5626118bb34d1aadb --base-formal formal --fetch --core-supplement ci-evidence/core-run-38850021923/supplement-provenance.json
```

This command performs one pass and does not poll. Omit `--fetch` to replay already downloaded evidence offline. Add `--require-all-402` for the final completeness gate: partial coverage exits unsuccessfully. A downloaded or successfully uploaded GitHub artifact never counts by itself.

Use `--stream-objects` on either importer when disk space is limited. The preserved outer GitHub ZIP remains immutable; its nested ZIP is read in memory. Every inventory payload is hashed, but only sources, logs, receipts and other nonobjects are extracted. `.olean` existence, size and hash checks use the selected ZIP inventory, with no fallback to an older physical object. A fresh final hash of every referenced object/file and the raw archive is required before acceptance. The exact-SHA probe supplement remains separately recorded. The 34-record shard-0 replay was checked against extracted mode with identical proof hashes, declarations and import closures; altered and missing objects, including a missing ZIP object concealed by an older physical file, are regression-tested by `test_evidence_store.py`.

`--download-artifact-ids ID ...` limits new downloads to named artifacts; already downloaded shards are still independently replayed. `--min-free-mb 512` reserves that headroom before downloading and before extracting the estimated missing nonobject bytes. Cohort reports are preserved by SHA256 under `report-history/` before replacement. Resource-limited passes remain explicit and do not turn unfinished evidence into a proof.

The optional `--bounded-nonobject-writes` retains the same reserve while checking each next file and every write of at most 1 MiB, with a 64 KiB metadata margin and a free-space check after flushing. Generated report/history writes use the same bounded checks. This allows compressed text to fit without reserving the uncompressed sum of all files at once; conservative reservation remains the default.

Artifacts and GitHub API metadata are preserved under `run-<run-id>/artifacts/<artifact-id>/`. Each nested `evidence.zip` is checked against its complete path/size/SHA256 inventory. ZIP traversal, drive paths, backslashes, symlinks, case collisions, duplicate entries, missing entries, unlisted payloads and changed inventory bytes are rejected. GitHub's published artifact SHA256 is also checked when present.

In extracted mode, every shard gets a separate `validation/formal/` tree. All 402 immutable native inputs, witnesses and inventories are hardlinked from the local frozen base, while its Linux `.olean` files and logs are extracted into the isolated tree. Existing hardlinks are never opened for writing. The Windows working tree's source and object files are untouched.

The importer independently checks the complete pinned core receipt, all 18 source/object/log stage hashes, 51 audited declarations and 16 negative regression assertions. It then invokes the trusted local strict catalogue validator against the artifact tree, including every numerical Data/block/aggregate object, log, source, planned index partition, imported dependency map, frozen native input and witness hash. Python code from downloaded artifacts is retained but never executed. Failed/incomplete/export-only cases remain unverified.

The deterministic partition is independently recomputed: 24 shards for the original runner or 12 shards for the optimized support runner. A record may only count in its assigned shard. When several artifacts for one shard exist, the importer retains the independently validated one with the most successful records, then the newest creation time; all superseded artifacts remain named in the combined provenance.

If all selected shard core source/object maps are identical, the importer creates `combined/formal/` and replays all selected receipts together once more. If core objects differ, it combines only the independently validated per-shard rows, with explicit artifact and validation-root provenance. Cross-shard record duplicates are rejected. The final `cohort-validation.json` reports the exact missing IDs and sets `complete_402` only when the verified IDs equal the entire frozen eligible set.

In streamed mode the optional physical combined overlay is omitted: each shard is fully replayed in its own immutable ZIP-backed object environment. Shared core and extension object hashes are still compared, and cross-shard IDs remain disjoint. Publication exporters reopen the same object stores for fresh strict replay, then bundle only sources, logs and receipts. A public environment's `evidence_zip_path` may therefore be null; its `object_store` identifies the nested member and hashes inside the indexed permanent raw artifact.

The canceled original run retained two useful checkpoints, with 14 and 15 successful records. Its packager had omitted four probe files required by the recorded core receipt. The separate complete Linux core artifact from run `38850021923` supplied all four with exactly the older recorded source/object SHA256 values. This explicit cross-artifact repair allowed 29 records to pass strict replay; original raw ZIPs were left unchanged. A supplement never substitutes merely similar objects, Windows objects, changed sources, or an unrecorded dependency.

The frozen catalogue is `1abc63218db34cea95802aeb3b6d4a6b6fe1c61b`. Current verified totals come from the generated reports, not from a workflow's status alone.

When the unchanged strict replay and publication run on a remote aggregation runner, retain the three portable cohort directories under `formal/ci-evidence/published-402`, `formal/ci-evidence/published-85` and `formal/ci-evidence/published-45`. Retain the accompanying `remote-aggregation-provenance.json`, `operator-source-hashes.json` and `raw-preservation-index.json` under the paper's root `ci-evidence/` directory. After downloading those publication outputs, independently check their original artifact identities from the local computer:

```text
python ci-evidence/verify_raw_github_metadata.py --paper .
```

The resulting `raw-github-metadata-verification.json` binds all three current raw indices to exact GitHub artifact/run IDs, commits, byte sizes and published SHA256 values. A missing published digest is a failure. Raw ZIPs present locally are also hashed; absent ZIPs are explicitly recorded as not locally hashed. This receipt checks the completed aggregation run against GitHub too. The publication package requires these four provenance/receipt files whenever a cohort carries the remote aggregation marker, and checks the exact operator versions and portable output hashes. Remote aggregation replays source-bound evidence; it does not rerun the Lean kernel. Permanent raw-archive preservation is a separate release operation after the final main commit.

The manual `lean-evidence-release.yml` workflow performs that final preservation operation on a fresh runner. Supply the exact reviewed current main commit and the aggregation raw-preservation artifact's ID and GitHub-published SHA256. The reviewed `release_from_preservation.py` authenticates the successful aggregation, restores and freshly hashes all 33 original worker ZIPs, checks the three committed portable cohorts, and invokes `archive_release.py`. It rejects changed main heads, conflicting assets and incomplete evidence. The permanent release is `lean-frozen-catalogue-2026-10-16`; its upload receipt checks server sizes and digests. This operation publishes proof evidence on GitHub only.

Top-level cohort rows may be compact: `full_evidence_ref` points to the complete per-artifact independent report and its SHA256. All source/object/log/receipt/plan hashes are preserved; the large proof-step and import arrays stay in those full reports. `compact_cohort.py` migrates an older top report only after checking every record against its pinned full report, preserving the original top report in history. Publication always replays the full reports and receipts afresh.

For the additional algebraic cohorts, run one pass of `ingest_algebraic.py` with the combined workflow's exact run and commit. It accepts artifact names `lean-algebraic-3d85-shard-N` and `lean-algebraic-nd45-shard-N`. It independently checks the authoritative 85/45 registries, deterministic shard assignments, raw source poses and scales, exact canonical root/normalization data, generated reference and fragment bytes, all basis/vertex/pair partitions, every imported source/object/log hash and prescribed semantic audit. Downloaded Python is never executed. Deep Windows validation overlays use a shorter persistent path under `Documents/Codex/lean-ci/`; the preserved raw ZIPs and provenance remain together in this directory.

The publication exporters repeat strict validation and produce the same portable schema:

```text
python ci-evidence/publish_402.py --base-formal formal --cohorts ci-evidence/run-38845845777/cohort-validation.json ci-evidence/run-38849574471/cohort-validation.json --require-all-402
python ci-evidence/publish_algebraic.py --base-formal formal --kind 3d85 --cohorts ci-evidence/algebraic-run-RUN/cohort-validation-3d85.json --require-complete
python ci-evidence/publish_algebraic.py --base-formal formal --kind nd45 --cohorts ci-evidence/algebraic-run-RUN/cohort-validation-nd45.json --require-complete
```

Outputs are `published-402`, `published-85` and `published-45`. Each contains a compact `verified-catalogue.json`, a manifest-backed `proof-sources-and-logs.zip`, and a `raw-artifacts.json` provenance index. Full receipts, independent validation rows, native inputs and numeric proof sources are retained under separate `environments/<id>/formal/` archive roots. The portable ZIP contains no compiled objects. Raw artifact ZIPs retain those Linux objects and are indexed for permanent GitHub release storage. These exporters perform no upload.

For algebraic artifacts made with different approved asset versions, repeat `--approved-base RUN_ID=FORMAL_DIRECTORY` on the algebraic publisher. Once mappings are supplied every run must have one, and its numerical target registry must remain unchanged. The replay isolates Python module caches between versions. The exact asset manifest and helper source hashes are archived separately in each environment; an old version never silently falls back to the working helper version.

`audit_object_cache.py` is a read-only diagnostic for reconstructible `.olean` cache copies. It checks raw member/source hashes, filesystem identities and complete hardlink groups, and can produce a compact dry-run plan. It has no deletion operation. `stream_old_checkpoints.py` first replays an older extracted checkpoint through immutable ZIP-backed objects without changing its raw archive. These utilities do not add verified records or relax publication gates.

Validate or unpack a portable archive with `formal/evidence_bundle.py --cohort DIRECTORY`. Final paper/package gates require the exact complete target ID sets. Partial reports remain explicitly incomplete. These are feasibility proofs for source-linked coordinate hulls; parser/generator correctness, optimizer correctness, optimality, and named-solid classification or edge-unit conventions that were not separately proved remain outside the kernel claim.
