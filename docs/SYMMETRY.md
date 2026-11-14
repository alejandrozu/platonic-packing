# More symmetric packings in the same container

_14 November 2026. Alejandro Zarzuelo's idea; tool and runs with Claude (Anthropic)._

**The idea.** Many records have pieces that are nearly symmetric with the container. Some sit almost nested in a
corner, almost centred on a face or an edge, or almost on a mirror plane, but not exactly. Such a piece can often be
moved onto the symmetric placement without making the container any larger. The pieces near the corners and sides
should be the easiest to move; the interior ones are more constrained.

**What was done.** The container is held fixed at the record's exact size (`s_full`). The pieces are moved one at a
time, outermost first, onto symmetric placements. A move is kept only if the whole packing stays legal with the
record's clearances: every pair at least 10⁻⁷ apart and every piece at least 10⁻⁷ inside every face. Every result is
then checked by `verify.py` and proved valid in exact arithmetic by `certify_exact.py`, exactly like the records.
The symmetrized packings are in [records/symmetric/](../records/symmetric/README.md), and the records themselves are
unchanged.

## Method ([scripts/symmetrize.py](../scripts/symmetrize.py))

**Symmetric placements.** A placement is symmetric when some symmetry of the container, other than the identity,
maps the piece onto itself. The candidate symmetry groups K are the stabilizers of the container's vertices, edge
midpoints and face centres, their rotation subgroups, single mirror planes and cyclic subgroups, largest first.

**The nearest symmetric placement.** Take a piece at (c, R) whose orientation is close to being K-symmetric (within
25°). Let φ(h) be the symmetry of the piece with R⁻¹hR ≈ φ(h). The nearest K-symmetric placement is the group average

  c* = (1/|K|) Σ h c,  R* = polar((1/|K|) Σ h R φ(h)ᵀ),

which satisfies h c* = c* and h R* = R* φ(h) exactly whenever φ is a homomorphism.

**Where the piece goes.** On an axis (a vertex, edge or face direction), the piece is first pushed as deep as it
goes: fully nested in the corner, or against the edge or the face. If that is not legal, it goes as close as possible
to where it was, within 0.35 edge lengths. On a mirror plane it is placed at the projection, or a little away from it.

**Measures.**
- A piece's *stabilizer* is the set of container symmetries that map it onto itself. Its order is 1 for a generic
  piece, 2 on a mirror plane, and for an icosahedral container 4 on an edge, 6 on a face, 10 in a corner and 120 at
  the centre.
- The *packing group* is the set of container symmetries that map the whole packing onto itself.

## Results (all 2,475 Platonic records, n = 2–100)

- 586 packings changed, 1,599 piece moves.
- Pieces on symmetric placements, over all records: 19,832 → 21,280 of 126,225.
- The packing group grew in 13 records, for example:
  - 15 icosahedra in a dodecahedron: 6 → 24
  - 11 octahedra in a cube and 15 and 21 octahedra in a dodecahedron: 1 → 6
  - 18 tetrahedra in a tetrahedron, 11 cubes in a cube and 28 octahedra in a tetrahedron: 1 → 3

All 586 symmetrized packings fit the record's container. The exact certificates are listed in
[records/symmetric/README.md](../records/symmetric/README.md).

| problem | packings changed | pieces on symmetric placements (all n) | pieces (all n) |
|---|---|---|---|
| cubes in a tetrahedron | 68 | 95 → 342 | 5,049 |
| dodecahedra in a dodecahedron | 45 | 718 → 915 | 5,049 |
| icosahedra in an icosahedron | 46 | 368 → 510 | 5,049 |
| cubes in a cube | 21 | 4,159 → 4,285 | 5,049 |
| dodecahedra in an icosahedron | 30 | 56 → 167 | 5,049 |
| octahedra in an octahedron | 43 | 1,449 → 1,527 | 5,049 |
| cubes in an octahedron | 39 | 1,176 → 1,246 | 5,049 |
| cubes in a dodecahedron | 28 | 960 → 1,026 | 5,049 |
| octahedra in a tetrahedron | 37 | 1,987 → 2,052 | 5,049 |
| icosahedra in a tetrahedron | 31 | 388 → 443 | 5,049 |
| tetrahedra in a tetrahedron | 36 | 857 → 906 | 5,049 |
| dodecahedra in a tetrahedron | 29 | 537 → 585 | 5,049 |
| octahedra in a cube | 24 | 886 → 923 | 5,049 |
| cubes in an icosahedron | 19 | 138 → 173 | 5,049 |
| icosahedra in an octahedron | 21 | 2,419 → 2,454 | 5,049 |
| the other 10 problems | 69 | 3,639 → 3,726 | 50,490 |

**Examples.** Coloured pieces are mapped onto themselves by the container; darker means more symmetries. The
container is the same size on both sides.

- 96 icosahedra in an icosahedron: 0 → 20 pieces on symmetric placements.
  ![](symmetry/icoinico_n96.png)
- 65 cubes in a cube: 5 → 32 (corner and face cubes aligned).
  ![](symmetry/cubincub_n65.png)
- 77 dodecahedra in a dodecahedron: 2 → 19.
  ![](symmetry/dodindod_n77.png)
- 15 icosahedra in a dodecahedron: the packing group grows from 6 to 24 (the centre piece becomes fully symmetric).
  ![](symmetry/icoindod_n15.png)
- 11 octahedra in a cube: packing group 1 → 6.
  ![](symmetry/octincub_n11.png)

## What does not move: jammed packings

20 icosahedra in an icosahedron shows the limit.
- All 20 pieces are already within 0.1° of the container's orientation.
- Two pieces are only 0.03 edge lengths from being fully nested in a corner.
- Their neighbours block them: nesting either piece would need an overlap of about 0.015.

Only one piece of this record could be nested. Letting the neighbourhood relax by SLSQP at the same container size
(`pull_sym`, `pull_local` in the same script) brought one more piece within 10⁻⁶ of a symmetric placement, but not
onto it.

Most records are tight: the container is held by a rigid core of contacts, and at the record's size only the loose
pieces (rattlers and outer pieces with slack) can move. More symmetry for the jammed ones needs a new search: the
tightening constrained to a symmetry group from the start, with the record's size as the bound to beat. The linear
form of those constraints is already in `solve_sym` (centres in the fixed subspace, rotation increments in the
fixed subspace of the conjugation action).

## Reproduce

```bash
python3 scripts/symmetrize.py --all OUTDIR            # all Platonic records (about 30 minutes)
python3 scripts/symmetrize.py records/icoinico/icoinico_n96.json out.json
python3 verify.py out.json && python3 certify_exact.py out.json
python3 scripts/symmetrize.py --summary               # records/symmetric/SUMMARY.csv and README.md
python3 scripts/symmetry_figure.py RECORD.json SYMMETRIZED.json out.png
```
