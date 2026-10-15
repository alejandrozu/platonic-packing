# Community construction and certificate batch, 13 October 2026

1306 certified coordinate improvements were selected against commit `874e51620c79cc16fd81bc07212112a207e5121e` and available external certified coordinates.

- 47 different nominal-bound constructions: finite classical honeycomb and subdivision patches.
- Four different triangular-subdivision configurations at an unchanged nominal side 2, with smaller positive-clearance certificates.
- 1255 wall-padding refinements: inherited pieces and orientations are unchanged. Discovery attribution is preserved; PingYou Ltd is credited separately for certificate refinement.

102 submitted cases were omitted because newer certified coordinates were already better.

A smaller certified container is an upper bound. Exact feasibility certification is not a proof of global optimality. Published source-only bounds remain separately attributed when no poses are available.

[Construction submission and publication permission](https://github.com/alejandrozu/platonic-packing/issues/6) · [Wall-padding submission and publication permission](https://github.com/alejandrozu/platonic-packing/issues/7)

Source archives, SHA-256 values, exact witness bindings and current comparisons appear in `batch-receipt.json` and in each record’s `contribution` field. Geometry numbers are not rounded during import.

## Reproduce the data-only replay

Use Python with NumPy; run these without Python’s `-O` flag. The importer uses this repository’s trusted certifier, never submitted executable code. `prepare` checks the disclosed archive hashes and extracts JSON only, with path and size limits. The replay validates canonical solids, inherited poses and all exact geometric inequalities. It also runs the current floating checker.

```sh
python scripts/import_community_batch.py prepare --archive-dir /path/to/scratch
python scripts/import_community_batch.py audit --archive-dir /path/to/scratch
python scripts/import_community_batch.py replay --archive-dir /path/to/scratch --workers 4
```

The audit uses the checkout’s current records and certified external baselines. It skips witnesses already superseded there. To reproduce the original 1,306-case selection, start from the baseline commit recorded above. `stage` is an explicit local-writing step after successful replay; the script does not publish, comment, label issues or push.

## Candidate storage

The checked contributions are stored under `records/community/` and registered in `docs/community_records.json`. They are coordinate candidates only, separate from historical published-reference bounds. Original search records remain intact; selection compares all available certified candidates by scale. Separate storage also prevents an automated search export from replacing community results.
