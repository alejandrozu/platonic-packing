# Scientific rotating packing illustrations

These local assets were rendered from the actual frozen full-precision configurations at source commit **e15b496ae7306287e0e70bb5b14be79f5dfdde84**. They have not been uploaded to Commons; no Wikimedia filename is reserved or assumed.

| Illustration | Animation | Poster | Provenance |
|---|---|---|---|
| Twelve cubes in a cube | cube-in-cube-n12-rotation.gif | cube-in-cube-n12-poster.png | cube-in-cube-n12-manifest.json |
| Thirty-three dodecahedra in a dodecahedron | dodecahedron-in-dodecahedron-n33-rotation.gif | dodecahedron-in-dodecahedron-n33-poster.png | dodecahedron-in-dodecahedron-n33-manifest.json |

Each GIF is **512 × 512 pixels**, with **48 frames at 500 ms**, completing a slow rotation in **24 seconds** and looping continuously. Each decodes to **12,582,912 frame pixels**, below the requested 100-million-frame-pixel threshold. The manifests record the checked frame inventory, timing, output hashes, source hashes, and numerical containment of the vertices actually rendered.

**Creator and license:** Alejandro Zarzuelo Urdiales; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The cube specimen reproduces **Yohei Nakajima's twelve-cube touching family** with Zarzuelo Urdiales's smaller positive-clearance convention. The original soft-to-rigid method/software lineage remains credited to Nakajima for both illustrations.

The dodecahedral colors indicate **shell class**: gray central particle, ochre twelve-particle inner shell, and translucent blue-gray twenty-particle outer shell. They do not indicate orientation components or physical grains. The illustrations show feasible stored constructions and do not claim global optimality.

These are scientific polygon renderings, without image-generation models or invented placements. The standalone renderer is included as render_rotating_packings.py. In the original workspace it can reproduce either asset with:

    python outputs/wikipedia-assets/render_rotating_packings.py cubincub_n12
    python outputs/wikipedia-assets/render_rotating_packings.py dodindod_n33

It requires the frozen source tree under work/repository, the source-hash CSV under outputs/analysis, and Matplotlib, NumPy, and Pillow. The script does not execute the unrelated social-figure generator.
