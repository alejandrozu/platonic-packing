# Component-specific licenses and attribution

The archive's default MIT license does not replace licenses attached to imported third-party components. The MIT copyrights of Yohei Nakajima and Alejandro Zarzuelo are retained in `frozen-source/LICENSE` and the viewer notice. Newly prepared manuscripts are also separately offered under CC BY 4.0 in their individual preprint records.

## Haowei Lin / Tencent-Hunyuan Hyra construction data

Source: [Tencent-Hunyuan/Hyra-results, commit 09b2d2e3c362c67a78f544c836bd8e4b54a05527](https://github.com/Tencent-Hunyuan/Hyra-results/tree/09b2d2e3c362c67a78f544c836bd8e4b54a05527).

Copyright (C) 2026 Tencent. The upstream repository licenses its Tencent-authored materials under Apache License 2.0, subject to the component notices in its LICENSE. The complete upstream LICENSE is copied **without alteration** to `LICENSES/Hyra-upstream-LICENSE.txt`; it includes Apache-2.0 terms and the upstream third-party attribution text. The pinned source has no separately named NOTICE file.

The following archived files contain the imported construction data:

- `frozen-source/docs/literature/hyra_cubincub_n11.json`
- `frozen-source/docs/literature/hyra_cubincub_n12.json`
- `frozen-source/docs/literature/hyra_octincub_n21.json`
- `frozen-source/docs/literature/hyra_octincub_n24.json`
- `frozen-source/test/fixtures/hyra_octahedra_in_cube_n21.json`

The first four are the imported literature records. The fifth is a local checker fixture derived from the octahedra-in-cube record: its serialization was compacted and `piece`, `container`, and `container_center` metadata added in the source project. This adaptation is explicitly identified here; the scientific source files in the archived frozen tree have not been edited during release preparation. Imported Apache-2.0 material is not relicensed as MIT.

The upstream license SHA-256 is `ece6c7026732f576af3a909a117b321c9e8cfd96fc4d56e5229ff1a288dae087`; its Git blob is `4298ab75c50138e427401b9402712d0b170508f6`.

## Viewer and other sources

The viewer and geometric-method lineage retain the Yohei Nakajima and Alejandro Zarzuelo MIT attribution. External catalogue diagrams, papers, profiles, and websites are referenced by links; their complete third-party media or papers are not copied into this new archive. CDN libraries/fonts used by the HTML files are loaded externally and remain subject to their own distribution licenses.
