# Contributing to Polyhedra in Polyhedra

Everything on [the website](https://alejandrozu.github.io/platonic-packing/) (moving to polyhedrainpolyhedra.wiki) is built from this repository, and every
contribution goes through a public GitHub issue or pull request.

## Submit a better packing

1. Check it in your browser on the [contribute page](https://alejandrozu.github.io/platonic-packing/contribute/): paste the JSON,
   press **Check packing**, then **Submit on GitHub**. This opens the
   [Submit a packing](../../issues/new?template=submit-packing.yml) form already filled in.
2. The [submission workflow](.github/workflows/submission.yml) runs `verify_general.py` (floating point) and
   `certify_general.py` (exact proof) on it and comments with the result and the comparison with the current record.
   Editing the issue runs the check again.
3. A maintainer accepts certified packings that beat (or fill) a record by adding the `accepted` label. The workflow
   then writes `records/<id>/<id>_nNN.json` with your credit, its certificate and float check, logs it in
   [records/CONTRIBUTIONS.md](records/CONTRIBUTIONS.md), rebuilds the site and closes the issue.

Format: the same JSON as the record files, `{"piece", "container", "n", "s_full", "pieces": [[x, y, z, qw, qx, qy, qz], ...]}`,
with pieces that are copies of the canonical solids of `src/solids.json` (rotated by the scalar-first quaternion, then
centred at (x, y, z)) and the container `s_full` times the canonical container solid centred at the origin. Pieces may
not touch: leave a small positive clearance (about 1e-7) and round `s_full` up. `src/claim.py` shows how.

## Propose a new category or share another construction

Use the [Propose a new category](../../issues/new?template=new-category.yml) or
[Share another construction](../../issues/new?template=other-construction.yml) forms (also on the contribute page).

## Code

Pull requests are welcome. Run the tests with `bash test/run_all.sh` (Node ≥ 18, Python ≥ 3.10 with NumPy, SciPy,
mpmath). To add a solid:

1. define it in `polyhedra.py` and run `python3 polyhedra.py` (writes `src/solids.json` with faces, checks and the
   r-rounding cores, and `src/solids_hp.json`);
2. give its number field in `scripts/exact_solids.py` and run `python3 scripts/exact_solids.py <name>` (writes the
   exact coordinates to `src/solids_exact.json`, proved by an exact self-check);
3. add the problem to `PROBLEMS` / the family lists in `scripts/engine.py`;
4. run the search (`scripts/run_forever.sh`) and publish (`python3 scripts/publish.py`).

## The website

Sources are in `web/` (pages, styles, scripts) and `scripts/site.py`. Preview locally:

```bash
python3 scripts/site.py && python3 -m http.server -d site 8000   # then open http://localhost:8000
```

Pushes to `main` that touch `web/`, `scripts/site.py` or `records/` rebuild and deploy the site
([site workflow](.github/workflows/site.yml)).
