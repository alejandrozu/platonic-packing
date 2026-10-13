# Historical construction audit — 13 October 2026

This audit separates numerical feasibility, source provenance and discovery priority. It does not certify global optimality or claim that the retrieved sources cover every prior construction.

## Prior work and scope

The problem class was studied before this project's October 2026 work. Berthold, Kamp, Mexi, Pokutta and Pólik reported a systematic optimization study of all 25 pairs of Platonic solids, considering 750 instances with one to 30 pieces. Their paper introduces a formulation using the Farkas lemma and general nonlinear solvers. The paper is dated 6 May 2026; its linked supplement's frozen results commit is dated 16 April 2026. These are documented publication and repository dates, not proof of the first discovery date for every matching construction. [Paper](https://arxiv.org/abs/2605.04850), [frozen supplement](https://github.com/DominikKamp/Packing/tree/27f71632d8655ae4b6a049410a401976748b94e3).

Consequently, claims that multi-piece packings were previously available only for cubes in cubes and octahedra in cubes, or that the other seven original families had no prior numerical constructions, must be withdrawn. The project's generalization of a soft-to-rigid search, its search moves, exact verification and community catalogue can be described on their own terms without claiming to have introduced the entire polyhedron-in-polyhedron problem class.

Older cubic constructions remain important. Friedman's catalogue attributes cubes n=9–10, 13, 14 and 28–33 to Erich Friedman (1998). Its current octahedra-in-cubes entries credit Ríain Walsh (June 2026) and Haowei Lin (July 2026). The available numerical solutions in Alexander Müller's 2015 cube benchmarks were checked for n=2–40; they did not improve the stronger retrieved cubic bounds. [Cubes catalogue](https://erich-friedman.github.io/packing/cubincub/), [octahedra catalogue](https://erich-friedman.github.io/packing/octincub/), [Müller benchmarks](https://github.com/muellan/packing/tree/62ef140900e53810975989dfb17d21fb4042e6a7/min-Cube/min-Cube(Cube)).

## Imported coordinates and units

All 724 directly available configurations with n=2–30 in the frozen Kamp supplement were imported. Every imported configuration passed both the project's floating-point checker and its exact certificate checker. The supplement contains 749 of the advertised 750 files: the n=28 icosahedra-in-cube configuration is absent. The catalogue fills this one gap with an explicitly derived subset of the published n=29 configuration, deleting one piece while retaining the same certified container, centers and rotations. It is labelled as a derivation and links to the actual n=29 source. Thus the 25 families each have 29 feasible baseline configurations, comprising 724 direct imports and one derived subset.

The source uses unit-circumradius pieces and reports the container circumradius R. The website reports container edge / piece edge. If c_p and c_c are the circumradii of the project's unit-edge piece and container, the conversion is s = R c_p / c_c. In particular, cubes in cubes have s = R, whereas octahedra in cubes have s = R sqrt(2/3). Comparing their raw circumradii directly would produce incorrect rankings. Source values are retained separately from the certified copies.

Each source container is aligned to the project's canonical solid by a proper rigid rotation; all its published outer vertices are checked. Piece rotations are fitted to the published mesh vertices and verified against every vertex, with discrepancies below 1e-12 in source units. The fitted quaternions use scalar-first ordering. A positive clearance is then added and checked exactly. These coordinate conventions and clearance changes do not constitute a new geometric discovery.

The exact checks prove feasibility of the specific saved coordinates: each piece is a congruent canonical solid, every vertex is inside the container, and each pair has a strictly separating plane. A feasible upper bound does not by itself prove optimality. Matching a previous numerical value also does not prove that two pose sets are identical.

## Comparison with the original nine-family archive

The archive snapshot used for this audit has 261 cases in the original nine families with n=2–30. Relative to the Kamp values, 165 archive bounds are lower, 88 match within a 1e-6 allowance for clearance and normalization, and eight published Kamp bounds are lower. This is a comparison with this particular supplement, not a count of world records; other historical sources can be better than both. The eight cases requiring an earlier feasible construction to be considered are:

| Family | n | Archive edge ratio | Kamp source edge ratio | Source |
|---|---:|---:|---:|---|
| cubinoct | 5 | 2.914213928033 | 2.912604270562 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l2/m3/n5/platonic_n5_m3_l2.txt) |
| cubinoct | 6 | 2.934353613624 | 2.931851663013 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l2/m3/n6/platonic_n6_m3_l2.txt) |
| cubinoct | 10 | 3.691812496085 | 3.674248435884 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l2/m3/n10/platonic_n10_m3_l2.txt) |
| octincub | 17 | 2.506598688338 | 2.499438482577 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l3/m2/n17/platonic_n17_m2_l3.txt) |
| dodinico | 6 | 3.637559824590 | 3.618034027832 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l4/m5/n6/platonic_n6_m5_l4.txt) |
| dodinico | 8 | 3.966580147418 | 3.965106142801 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l4/m5/n8/platonic_n8_m5_l4.txt) |
| dodindod | 14 | 3.000000179611 | 2.999820062747 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l5/m5/n14/platonic_n14_m5_l5.txt) |
| dodindod | 23 | 3.554882637201 | 3.539352041119 | [Published coordinates](https://github.com/DominikKamp/Packing/blob/27f71632d8655ae4b6a049410a401976748b94e3/platonic/l5/m5/n23/platonic_n23_m5_l5.txt) |

The source ratios in this table precede the added clearance. The saved certified copy has its own full-precision feasible bound. Selection and submission decisions must compare the actual certified copies with compatible units and precision.

## Reconstructions and tightening

The n=13 cube reconstruction published by @BuilderOfAgents on 9 October 2026 supplies full coordinates at a bound compatible with Friedman's three-decimal 1998 entry. The n=14 reconstruction matches Friedman's exact expression 2 + 7 sqrt(2)/10. The source explicitly presents these as rediscoveries rather than improvements over Friedman. Both coordinate files were imported and certified; their source and the historical attribution are retained separately. [Reconstruction repository](https://github.com/tronford/cubes-in-cube-n13/tree/1f0c75401b2da4850b7e9f14de7d7b9cbe5e461a).

Sam Scott's audit supplies tightened versions of Lin's cube n=11 and octahedron n=21,24 arrangements. It also reports that tightening Lin's n=12 coordinates reaches the same bound as Nakajima's n=12 result, with similar configurations after symmetry matching. This is evidence for separating original arrangement credit from later tightening or independent rediscovery; it should not be presented as a proven identity of every coordinate. The Scott coordinate files passed the local checks but were not lower than the project's current corresponding bounds. [Audit repository](https://github.com/shepard5/hyra-packing-audit/tree/c107fda33c2f02df83e9d549fb839b4fd5a7bfbc), [n=12 analysis](https://github.com/yoheinakajima/soft-to-rigid-packing/issues/1), [Lin's original files](https://github.com/Tencent-Hunyuan/Hyra-results/tree/09b2d2e3c362c67a78f544c836bd8e4b54a05527/AI4Science/packing_records/records).

## Remaining coordinate gaps

Friedman's n=33 cubic bound was reconstructed using a finite candidate set containing an axis-grid shell, 45-degree face cubes and a central cube. The resulting 33-piece configuration passed both checkers at s=3.7071072518978, reproducing the published expression 3 + 1/sqrt(2) within the standard positive clearance. The construction keeps Friedman's 1998 historical credit and explicitly identifies the project-generated reconstruction; it is not asserted to be the exact original pose set. The script `scripts/reconstruct_friedman_cube33.py` reproduces the reconstruction and checks.

No original full coordinate files were retrieved for Walsh's octahedra n=11,14,15,18,19,23, or Lin's octahedra n=12,13,17 catalogue entries. Their published bounds and attributions remain important. The source diagrams are evidence of published constructions, but images alone are not exact-coordinate certificates. If the viewer shows a higher available certified configuration for one of these cases, the interface must state that it is the available configuration and give the lower published bound separately. It must not imply that the displayed coordinates attain the catalogue bound.

All configurations with saved coordinates can use the same interactive viewer, transparency, orientation colors, wireframe container and controls. Original catalogue diagrams can remain source links rather than alternate visual treatments in the gallery.

The reproducible importer `scripts/import_kamp_platonic.py` parses published JSON mesh data without executing source HTML or JavaScript. It checks candidate files before replacement and merges imported registry entries without discarding other contributors or previously registered sources.
