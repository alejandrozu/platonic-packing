# Status and hand-off (9 Oct 2026, 08:00 Paris)

## Done

* **Method ported and validated.** Nakajima's soft-to-rigid cube packer generalized to every Platonic solid as piece
  and container (`src/geom.js`, `src/sim.js`, `src/exact.py`). Reproduces the cube behaviour (n ≤ 8 → 2,
  n = 9 → 2 + 1/√2) and is ~1.5–2.5× faster than the original on cubes.
* **Rigorous checking.** `certify_exact.py` (standard library, exact arithmetic in Q(√2, √5)) and `verify.py`
  (floats). Both certify two independent published records (Nakajima's 12 cubes, Hyra's 21 octahedra in a cube)
  and reject broken files. Test suite: `bash test/run_all.sh` (all passing).
* **Same-solid problems, n = 2…20, all certified**: `records/tetintet`, `records/octinoct`, `records/icoinico`,
  `records/dodindod` (76 records, table in `records/README.md`, data in `records/SUMMARY.csv`).
* Interactive results page (3D viewer, tables, s(n) chart) built from the records: `site/index.html`
  (also published privately as a Claude artifact, "Platonic Packing Records").

## Compute spent

About 1,770 search runs (budget ×1 = 53,000 steps each) on 2 CPU cores, roughly 6 hours wall time, plus tightening:
* same-solid, n = 2–12: 24 seeds each; n = 13–20: 24 seeds each (seeds 1–24), all with annealing ("improved" mode);
* cube-in-cube n = 2–12, 8 seeds (regression only).
Raw runs: `runs/<piece>_in_<container>/n<N>_improved_x1.jsonl`; tightened results: `results/tight.jsonl`
(SLSQP, descend, lattice) and `results/tight_slp.jsonl` (sequential-LP screen).

## Not done yet (in priority order)

1. **Mixed pairs (A ≠ B), n = 2…20** — 20 problems (e.g. tetrahedra in a cube, `tetincub`; octahedra in an
   icosahedron, `octinico`). The code supports them and was tested end to end (three mixed cases certified,
   including Q(√2, √5) arithmetic), but the sweep was not run. Queue file ready: `runs_queue4.txt`
   (seeds 1–4 for all 20 pairs, n = 2–20, plus cube-in-cube n = 13–20). Estimated ~5 h on 2 cores plus tightening.
   For `tetincub` and `octincub`, compare with Friedman's catalogue (values are in images on his pages; the Hyra
   repo has machine-readable records for octahedra n = 21, 24 only).
2. **Harder search for n ≥ 13** (same-solid). Budget ×3 runs (`node scripts/batch.js <piece> same <n> 1 24 3`)
   and more seeds; tetrahedra 16–20 and dodecahedra/icosahedra 15–20 are the least converged. A full `descend`
   pass from n = 20 down for all four problems was not completed.
3. **Exact touching certificates** for the conjectured closed forms (see docs/MATH.md §8).
4. **Lower bounds / optimality** for n = 2 and the plateau values (docs/MATH.md §8).
5. Rigid-control ablation (Nakajima showed soft-to-rigid beats rigid for cubes; not repeated here).

## How to resume

```bash
bash test/run_all.sh                                   # sanity
nohup scripts/runqueue.sh runs_queue4.txt logs/queue4.log &          # mixed-pair sweep (2 workers, idempotent)
python3 scripts/pipeline.py tighten 2 tetincub,octincub              # tighten selected problems (ids or piece names)
python3 scripts/pipeline.py descend tetincub,octincub                # n from n+1 minus one piece
python3 scripts/records.py tetincub octincub                          # records + checker outputs + pictures
python3 scripts/site.py                                               # rebuild site/index.html
```
`scripts/orchestrate.sh` runs the whole thing (phase 1 same-solid, phase 2 mixed) unattended. Everything is
idempotent: runs skip seeds already present, tightening skips runs already tightened, records rebuild only when the
underlying packing changed.

## Known caveats

* Closed forms in the tables are conjectures from 12-digit numerics (quadratic irrationalities with small
  coefficients, matched to 1e-11); several larger-coefficient matches (e.g. (149 + 67√5)/122) may be coincidences.
* Tightening is a local method: two runs of the same arrangement can tighten to slightly different values; the
  sequential-LP variant sometimes stops at a slightly worse point than SLSQP, so SLSQP is used for the final polish.
* `s_full` in records includes 10⁻⁷ clearance; `s_tight` is the touching limit. Five-decimal displays are
  truncations of `s_full`.
