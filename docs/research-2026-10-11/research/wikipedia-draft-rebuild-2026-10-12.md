# Wikipedia draft rebuild — 12 October 2026

**Status: draft, saved locally and in the existing GitHub documentation branch. No Wikipedia or Commons submission.** The working title is **Polyhedra in polyhedra packing**.

The [Markdown draft](../wikipedia-polyhedral-fits.md) and [MediaWiki source](../wikipedia-polyhedral-fits.wiki) were revised together. The [complete visual preview](../wikipedia-article-preview.html) presents the article with a Wikipedia-style reading layout and a rotating construction. The existing [reference article and full atlas](../polyhedra-in-polyhedra-packing.html) also retain all counts 2–40. The in-chat version collapses long sections for reading, while leaving both results tables open.

## Changes

- Expanded finite cube-in-cube history, with grid constructions, Friedman's dated records, Lin's coordinate artifacts, Nakajima's method, and Zarzuelo Urdiales's refinement and generalization. Related unequal-cube, parallel, infinite-tiling and passage problems are distinguished.
- Added the independently published Januszewski–Zielonka non-blocking cube theorem, with its actual parallel-packing scope: [Archiv der Mathematik, DOI 10.1007/s13366-023-00710-1](https://doi.org/10.1007/s13366-023-00710-1).
- Explained the nested rounding continuation, geometric kernels, tightening, relative-center jiggling criterion, reusable seeds, cross-count inheritance and separate exact feasibility certification.
- Named and linked Yohei Nakajima and Alejandro Zarzuelo Urdiales at the relevant methodological and analytical contributions. The two author's manuscripts and the dataset now use their published version DOIs.
- Expanded plateaus, scale jumps, volume-normalized density, orientation classes, contact-connected domains, shell filling and candidate construction families. The 1 + 12 + 20 dodecahedral shell and its 102 nonaligned near contacts have a detailed attributed explanation.
- Included all twenty conditional hypotheses from the Patterns preprint, with tests and the distinction between stored observations and proposed generalizations.
- Preserved two tables containing all **99** source-linked cells: five identical-solid families and four distinct dual directions, each at **n = 2–12**. Values, credits, individual visualization targets, and coordinate links are retained.

## Comparison scope and checks

The live [cube catalogue](https://erich-friedman.github.io/packing/cubincub/) and [octahedra-in-cube catalogue](https://erich-friedman.github.io/packing/octincub/) were rechecked on 12 October. No changes to the retrieved n = 2–12 comparison entries were identified. This is a best-retrieved sourced comparison, with source precision and clearance conventions retained; it is not an exhaustive claim of current world records.

Walsh's eleven-octahedron and Lin's twelve-octahedron catalogue entries remain better than the corresponding local atlas constructions. Their cells link the original diagrams. The new preview shows an original-diagram link for those selections, because public coordinates were not located; it does not substitute the worse archived geometry.

The article has **35** defined references, **707** words of cube history, **1,007** words of methodology and **6,542** words including references and tables. Independent checks found no undefined Markdown citation anchors or MediaWiki named references, no changed table values, and no incorrect algebra in the density-step identity. The twenty hypothesis summaries were checked against the published Patterns paper.

The new preview contains 100 stored configurations (the 99 table specimens and the 33-dodecahedron shell), 726 particles and 8,052 rendered vertices. All source hashes match the frozen input manifest, all displayed particle vertices pass numerical containment, and full stored pose precision is retained. Exact certification remains the property of the linked construction files, rather than of a visual impression. See [preview audit](wikipedia-preview-audit.json).

## Rotating illustrations and Wikipedia presentation

Two [licensed animation assets](../wikipedia-assets/README.md) are prepared: twelve cubes in a cube and thirty-three dodecahedra in a dodecahedron. Each uses 48 actual-pose views at 500 milliseconds per frame, giving a 24-second loop. Each has a static poster and source/hash/licensing manifest. Colours in the shell illustration encode positional shells, not orientation classes. The cube illustration retains Nakajima's construction attribution.

The interactive figure is a local companion preview. Ordinary Wikipedia article wikitext cannot embed arbitrary JavaScript or custom iframes. Animated images are a portable option after a later licensed Commons upload; the [MediaWiki 3D extension](https://www.mediawiki.org/wiki/Extension:3D) also supports STL viewing. These animations decode to 12,582,912 frame pixels each, below the GIF thumbnail limit described by the [Manual of Style for images](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Images). No Commons filenames or deployed 3D availability are assumed.

## Editorial status

Fresh searches did not identify a standalone English Wikipedia page devoted to finite congruent cubes-in-cubes or octahedra-in-cubes packing; [Packing problems](https://en.wikipedia.org/wiki/Packing_problems) remains the relevant general coverage. The working title is descriptive rather than a claim that a new term has become standard.

Recent method and analysis statements are expressly attributed to the preprints. Archival DOI publication makes the sources citable but does not supply independent secondary coverage or peer review. Wikipedia's [reliable-sources guidance on scholarship](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources#Scholarship), [no-original-research policy](https://en.wikipedia.org/wiki/Wikipedia:No_original_research) and [conflict-of-interest guidance](https://en.wikipedia.org/wiki/Wikipedia:Conflict_of_interest) remain relevant to a future editor's source selection and weighting. Detailed source assessment stays in the [separate editing notes](wikipedia-editing-notes.md), rather than being repeated throughout the article.

No action in this rebuild submits the article, uploads media, changes a published Zenodo record, merges the documentation branch or contacts an editor.
