# Contributing to Polyhedra in Polyhedra

The [website](https://polyhedrainpolyhedra.wiki/) is built from this repository. Contributions go through public GitHub issues or pull requests so that witnesses, source credit and review can be inspected.

The archive currently covers 86 three-dimensional problems: all 25 ordered Platonic-solid pairs, 13 Archimedean and 13 Catalan self-packing families, and 35 prism/antiprism problems including elongated prisms. It also covers every ordered pair of regular polytopes of the same dimension in 4D (36 problems), 5D (9) and 6D (9). The current search ranges are n = 2–100 in 3D, 2–40 in 4D, 2–32 in 5D and 2–24 in 6D. The live tables show available records.

## Submit a 3D packing

1. Use the [contribution page](https://polyhedrainpolyhedra.wiki/contribute/) to paste native JSON, run the local floating-point check and open a pre-filled [packing issue](../../issues/new?template=submit-packing.yml). Review and submit that issue on GitHub. The browser checker supports 1–200 congruent copies of a convex piece in a convex container from the 3D solid library.
2. The [submission workflow](.github/workflows/submission.yml) runs `verify_general.py` and `certify_general.py` independently, compares each candidate with the current certified coordinate record, and reports the outcome. A published bound without available coordinates is reported separately. Editing an open issue runs the check again.
3. A maintainer may apply `accepted` to review and recheck eligible improvements. Accepted witnesses are written immutably under `records/community/`, with credit and checker logs, registered in `docs/community_records.json`, and recorded in [records/CONTRIBUTIONS.md](records/CONTRIBUTIONS.md). The site is rebuilt. Batches with unresolved or deferred candidates remain open.

Use complete records with `piece`, `container`, `n`, `s_full` and `pieces`. Each 3D piece row is `[x, y, z, qw, qx, qy, qz]`: a nonzero scalar-first quaternion rotates the canonical piece, then its centre translates it. `container_center` is optional; otherwise the container is at the origin. The container is `s_full` times its canonical shape. Geometry and normalization are defined in `src/solids.json`, high-precision coordinates in `src/solids_hp.json`, and exact definitions in `src/solids_exact.json`. Elongated prisms use their base edge as the unit; Catalan solids use their canonical dual size.

The browser pass is diagnostic. The exact certifier must establish strictly positive wall and pairwise separation margins using the final full-precision witness. Preserve coordinates and `s_full`, rather than rounded table labels. A clearance near 1e-7 piece edges is a common setting, not a fixed required minimum. Smaller positive gaps can certify. `src/claim.py` builds clearance and rounds the container outward; merely enlarging the container does not separate touching pieces.

### 3D batches

Supply a JSON array of full records, `{"records": [...]}`, or GitHub user-attachment ZIP links in the packing form's **Batch archives** field. Every record needs its own piece, container, n, s_full and pieces. Put native JSON under `records/` or `witnesses/`. A top-level `MANIFEST.json` can select records with `{"cases": [{"file": "records/example.json", "sha256": "..."}]}`; `witness` / `witness_sha256` entries are also supported.

Limits: 2,000 candidates, eight ZIPs, 64 MiB compressed and 256 MiB expanded per ZIP, 8 MiB per witness, and 12,000 ZIP entries. Source/history members are ignored and submitted code is never executed. Each candidate receives its own outcome. The workflow artifact contains complete JSON/CSV results and checker logs even when the issue comment is abbreviated. A batch has a 70-minute checking budget; a deferred witness has not yet certified and needs later review or a smaller resubmission.

### Credit and record comparisons

Give the original author/team, method, source URL, any prior packing used as a seed, and publication permission. Preserve per-record `found_by` and `credit`. If only the certificate or wall padding changes, retain the original construction author and supply `certificate_refined_by` separately. Identify derived constructions, including deletion, nesting and further search, with their lineage. The [method page](https://polyhedrainpolyhedra.wiki/method/) documents the generalized search and its sources.

Automatic 3D acceptance needs a tracked case and `s_full` strictly below the current certified coordinate record by more than 1e-12, or a case with no coordinate record. Equal-scale alternatives, historical reconstructions, lower bounds and proofs remain welcome through the construction form. A feasible witness proves an upper bound on minimum container size; optimality needs a matching lower bound or an independent proof. A certificate refinement is distinct from discovery of new piece geometry.

## Submit a 4D, 5D or 6D packing

The nD route is separate from the 3D browser checker and accepted-label automation.

1. Open a [construction issue](../../issues/new?template=other-construction.yml) or pull request with native nD JSON, contributor credit, method, sources and publication permission. For a batch, attach a ZIP to GitHub and give its SHA-256 checksum.
2. Check native records locally with `python3 certify_nd.py my-record.json`. This exact checker uses Python's standard library plus the repository's `multiquad.py` and `src/polytopes_nd.json`.
3. A maintainer dispatches [.github/workflows/nd_submission.yml](.github/workflows/nd_submission.yml) with the GitHub attachment URL, expected SHA-256 and issue number. It certifies every native record separately and saves results/logs in an artifact. Submitted scripts are not executed.
4. The maintainer reviews the results and imports eligible strict improvements with `python3 scripts/import_nd_submission.py ARTIFACT_DIR CONTRIBUTOR ISSUE`. The importer converts the native frame to search units, re-legalizes, compares against the current archive and preserves contributor/issue credit. `scripts/publish_nd.py` then writes the public witness and a fresh exact certificate. The case must belong to a tracked problem within its current n range.

### Native nD format

Use `dim`, `piece`, `container`, `n`, `s_full`, `mu`, `pieces` and `planes`, with optional `container_center`. Keys in 4D are `c5`, `c8`, `c16`, `c24`, `c120`, `c600`; in 5D `sx5`, `hc5`, `op5`; in 6D `sx6`, `hc6`, `op6`. Piece and container must have the same dimension.

A piece row contains d centre coordinates, d(d−1)/2 upper-triangular entries of a skew matrix S in row order, and d signs D. The signs are ±1 with an even number of minus signs. The exact rotation is `R = diag(D) (I - S)^-1 (I + S)`. This is a native rational rotation parameterization, not an arbitrary floating matrix or a quaternion.

The container is `container_center + s_full * mu * C`, with canonical C from `src/polytopes_nd.json`. Required `mu = edge(P)/edge(C)` is checked exactly, so `s_full` is container edge / piece edge even for canonical polytopes with different edge lengths. Plane rows `[i, j, u_1, ..., u_d, t]` use zero-based indices and require `u.x < t` on piece i and `u.x > t` on piece j. Supply each pair's witness unless the certifier's circumscribed-ball test already separates it. Numerical parameters may be JSON numbers or rational strings such as `"1/2"`.

A complete, certified two-tesseract example and the 3D example are on the [contribution page](https://polyhedrainpolyhedra.wiki/contribute/#format-nd). See `src/claim_nd.py` for constructing a native record from numerical centre and rotation arrays, including its internal-unit conversion. Screenshots of the site's 3D sections are useful context; verification needs the full-dimensional data.

## Propose a category or share another construction

Use [Propose a new category](../../issues/new?template=new-category.yml) for a new 3D convex piece/container pair, or [Share another construction](../../issues/new?template=other-construction.yml) for alternatives, proofs, historical sources and nD proposals. Include exact geometry or a construction, normalization, dimension, n range and references. New categories require maintainer review and search/verifier support. The current model uses congruent copies of one convex piece in one convex container; mixed-piece and nonconvex problems need an explicit extension. Planar packings and curved containers are outside this archive's scope.

## Code and geometry

Pull requests are welcome. The repository checks are in `test/run_all.sh` and `.github/workflows/site-tests.yml`; Node ≥ 18 and Python ≥ 3.10 with NumPy, SciPy and mpmath are used by the general code. The nD search also uses numba. Consult the relevant test/workflow for its dependencies.

To add a 3D solid:

1. Define it in `polyhedra.py`; run `python3 polyhedra.py` to generate the floating/high-precision geometry and rounding cores.
2. Give its number field and exact construction in `scripts/exact_solids.py`; run `python3 scripts/exact_solids.py <name>` and require the exact self-check to pass.
3. Register its problem(s) in `PROBLEMS` / the family lists of `scripts/engine.py`.
4. Run the relevant geometry, certification and site checks. Maintainer search/publication use `scripts/run_forever.sh` and `scripts/publish.py`.

For nD geometry, use `src/polytopes_nd.py` and register the same-dimension problem in `scripts/engine_nd.py`. Adding a polytope also requires appropriate exact verification support in `certify_nd.py`, including facet checks; registering a name alone is insufficient. Maintainer publication uses `scripts/publish_nd.py`.

## The website

Sources are in `web/` and `scripts/site.py`. To build and preview from a repository checkout:

```bash
python3 scripts/site.py
python3 -m http.server -d site 8000
# Open http://localhost:8000
```

Pushes to `main` touching the paths listed in the [site workflow](.github/workflows/site.yml) rebuild and deploy the site. Full record/certificate data are needed for a complete catalogue build. Keep source changes separate from generated `site/` output.
