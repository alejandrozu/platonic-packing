# Published packings used as starting points

Only packings with public coordinates can be imported. They are loaded into the search archive by
`scripts/literature.py`, so the search starts from both our packing and the published one and has to beat the
published value to record an improvement. Records that are still the published packing say so in `found_by`.

| file | packing | source |
|---|---|---|
| hyra_cubincub_n11.json | 11 cubes in a cube, s = 2.8829529104956513 | H. Lin, July 2026, [Tencent-Hunyuan/Hyra-results](https://github.com/Tencent-Hunyuan/Hyra-results) `AI4Science/packing_records/records/cubincub_n11.json` (commit 09b2d2e), Apache License 2.0 |
| hyra_cubincub_n12.json | 12 cubes in a cube, s = 2.9327717687048653 | same repository, `cubincub_n12.json` |
| hyra_octincub_n21.json | 21 octahedra in a cube, s = 2.592849935818519 | same repository, `octincub_n21.json` |
| hyra_octincub_n24.json | 24 octahedra in a cube, s = 2.6331889674258844 | same repository, `octincub_n24.json` |
| nakajima_cubincub_n12.json | 12 cubes in a cube, s = 2.9315185094797 | Y. Nakajima, Oct 2026, [yoheinakajima/soft-to-rigid-packing](https://github.com/yoheinakajima/soft-to-rigid-packing) (MIT) |

Format of all five: `[x, y, z, qw, qx, qy, qz]` per unit-edge piece, container `[0, s]^3` (Hyra files) or
centred at `container_center` (Nakajima). The other published values (octahedra in a cube: R. Walsh's n = 2–11, 14–16,
18–20, 22, 23, 25–30 and H. Lin's n = 12, 13, 17; cubes in a cube: Friedman's n = 9, 10, 13, 14 and 28–33) are
shown on Erich Friedman's Packing Center as pictures only, without coordinates.
