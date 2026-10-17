# Literature, Wikipedia coverage, and publication routes

Research checked **11 October 2026**, Europe/Paris. This is an evidence register and publication plan for review. Nothing has been submitted to a journal, arXiv, Wikipedia, Commons, or a third-party repository. Dates below distinguish the date of the research from a website's crawl or upload date.

## The scientific scope

The relevant problem is the finite packing of congruent, rigid polyhedra in a specified polyhedral container, with translations and rotations permitted and interiors pairwise disjoint. The objective may be maximum common particle scale in a fixed container, minimum container scale for fixed particles, or maximum particle count at fixed scale. These objectives must not be silently interchanged.

This has substantial antecedents beyond cubes in cubes and octahedra in cubes. Generic computational methods for polytopes in polytope containers existed by 2009; freely rotating concave polyhedra in cuboids were studied by 2018. A new all-pairs Platonic-solid dataset or particular construction/search implementation can be valuable without being the first general formulation of polyhedral packing. The papers should identify the implementation and dataset contribution precisely. See [Egeblad, Nielsen and Brazil (2009)](https://www.sciencedirect.com/science/article/pii/S0925772108000576), [Romanova et al. (2018)](https://eprints.soton.ac.uk/418130/), and [Callisaya and Kari (2025/2026)](https://www.scielo.br/j/tcam/a/nbGY4xC4KMxq7XbYZTybvHj/?format=html&lang=en).

Do not conflate three research questions:

| Question | Boundary condition | What its result establishes |
|---|---|---|
| Finite fit | A finite number of particles must lie in a fixed-shape container | A feasible scale/count or a certified bound for that container |
| Infinite packing | An unbounded Euclidean arrangement, often studied through a periodic fundamental cell | Bulk packing density; a finite repeating cell is not a hard-walled container |
| Crystal formation or grain growth | A dynamical/statistical physical model with temperature, pressure, interactions, interfaces, or kinetics | Assembly, equilibrium, metastability, or growth under the model's conditions |

Optimized finite fits can motivate hypotheses about confinement, orientation, and crystalline motifs. Geometric feasibility alone does not show a structure forms spontaneously, minimizes physical free energy, or reproduces a metallurgical grain. Terms such as “grain” should be operationally defined as orientation domains if that is what the analysis measures. Physical grains are not automatically the rigid particles in a packing file.

## Direct finite-container evidence

### Record keeper: Erich Friedman's Packing Center

[The live index](https://erich-friedman.github.io/packing/index.html) lists **three** three-dimensional families: [cubes in cubes](https://erich-friedman.github.io/packing/cubincub/), [tetrahedra in cubes](https://erich-friedman.github.io/packing/tetincub/), and [octahedra in cubes](https://erich-friedman.github.io/packing/octincub/). Its respective update dates are 3 July, 18 July, and 3 July 2026. It is a useful primary community record, not a proof that listed configurations are globally optimal or an exhaustive survey of all polyhedral containers.

The cubes page labels its results “smallest known.” On 11 October 2026, selected listings were:

| Count | Listed containing-cube side, unit cubes | Credit shown |
|---:|---:|---|
| 9–10 | `2 + 1/sqrt(2)` | Erich Friedman, 1998 |
| 11 | `2.88295+` | Haowei Lin, July 2026 |
| 12 | `2.93277+` | Haowei Lin, July 2026 |
| 13 | `2.956+` | Erich Friedman, 1998 |
| 14 | `2 + 7*sqrt(2)/10` | Erich Friedman, 1998 |
| 28–33 | `3 + 1/sqrt(2)` | Erich Friedman, 1998 |

The page says the trivial construction is best known for other counts below 34. Do not describe a historical improvement as a current record without comparing the actual value, geometry normalization, and retrieval date. [Source: Cubes in Cubes](https://erich-friedman.github.io/packing/cubincub/).

The octahedra page lists 1–30, including two explicit count plateaus, 7–8 at `1.79133+` and 26–27 at `2.63986+`. It credits most entries to Ríain Walsh in June 2026 and the entries for 12, 13, 17, 21 and 24 to Haowei Lin in July 2026. These are useful examples of capacity increasing without an increase in the listed container side. The printed precision and `+` notation do not themselves certify exact equalities. [Source: Octahedra in Cubes](https://erich-friedman.github.io/packing/octincub/).

The tetrahedra page lists counts 1–30. It credits count 3, side `1`, to Achille Hui in February 2016; count 13 (`1.46398+`), 18 (`1.60258+`), and 19 (`1.62245+`) to Haowei Lin in July 2026; and the other nontrivial listed entries to Ríain Walsh in June or July 2026. The first two are called trivial. This page was retrieved successfully as HTML using PowerShell after the web reader failed. [Source: Tetrahedra in Cubes](https://erich-friedman.github.io/packing/tetincub/).

These pages concern **unit particles in a smallest containing cube**. A repository using unit volume, circumradius, diameter, or an insphere convention needs an explicit conversion before comparison. Screenshots alone cannot prove a strict numerical improvement or nonintersection.

### General container methods

**Jens Egeblad, Benny K. Nielsen, and Marcus Brazil.** “Translational packing of arbitrary polytopes.” *Computational Geometry* **42**(4), 269–288 (May 2009). DOI: [10.1016/j.comgeo.2008.06.003](https://doi.org/10.1016/j.comgeo.2008.06.003). [Publisher abstract](https://www.sciencedirect.com/science/article/pii/S0925772108000576); [institutional technical report](https://di.ku.dk/forskning/Publikationer/tekniske_rapporter/tekniske-rapporter-2008/08-06.pdf).

Scope: arbitrary dimension and polytope containers, including nonconvex objects; numerical three-dimensional examples in a rectangular parallelepiped. Its central operation minimizes overlap through an exact one-dimensional translation, used inside local and guided local search. Boundary: this is **translational** packing. It does not establish the optimal freely rotating fits for every Platonic-solid pair.

**Tatiana Romanova, Julia Bennell, Yuri Stoyan, and Alexander Pankratov.** “Packing of concave polyhedra with continuous rotations using nonlinear optimisation.” *European Journal of Operational Research* **268**(1), 37–53 (1 July 2018). DOI: [10.1016/j.ejor.2018.01.025](https://doi.org/10.1016/j.ejor.2018.01.025). [University repository and bibliographic record](https://eprints.soton.ac.uk/418130/).

Scope: a given collection of possibly nonidentical concave polyhedra in a cuboid whose volume is minimized, with continuous rotation, translation, and optional clearance. Uses quasi-phi functions and nonlinear programming, initial placements, and a compaction procedure. Boundary: an exact model with a numerical local-search algorithm is not a certificate that its computed solutions are globally optimal.

**Hector F. Callisaya and Elvis R. V. Kari.** “Packing Polyhedra within Convex Sets.” *Trends in Computational and Applied Mathematics* **26**, e01823 (issue year **2025**; publication in the SciELO collection **19 January 2026**). DOI: [10.5540/tcam.2025.026.e01823](https://doi.org/10.5540/tcam.2025.026.e01823). [Full article](https://www.scielo.br/j/tcam/a/nbGY4xC4KMxq7XbYZTybvHj/?format=html&lang=en).

Scope: congruent polytopes in bounded convex domains, a differentiable nonlinear model with separating hyperplanes, transformations, and multistart optimization. Its three-dimensional numerical example packs icosahedra in a **sphere**. It reports source code at `github.com/hector-fc/packpoly`. Boundary: the general formulation is relevant to polyhedral containers, but its spatial experiment is not an all-pairs polyhedron-in-polyhedron record table. Failure to find a feasible arrangement with a local solver is not proof of impossibility. History: received 24 June 2024; accepted 23 October 2025.

**Helmut Alt and Nadja Scharf.** “Approximating Smallest Containers for Packing Three-dimensional Convex Objects.” [arXiv:1601.04585](https://arxiv.org/abs/1601.04585), submitted 18 January 2016.

Scope: constant-ratio approximation algorithms for minimal-volume containers for several classes of convex objects, including convex polyhedra under rigid motions in cuboid or arbitrary convex containers. Boundary: approximation guarantees and the general computational difficulty do not furnish the exact best fit for a specific small count in a fixed Platonic-solid container.

### Nearby finite confinement and crystallization evidence

**Erin G. Teich, Greg van Anders, Daphne Klotsa, Julia Dshemuchadse, and Sharon C. Glotzer.** “Clusters of polyhedra in spherical confinement.” *Proceedings of the National Academy of Sciences* **113**(6), E669–E678 (2016; online 25 January). DOI: [10.1073/pnas.1524875113](https://doi.org/10.1073/pnas.1524875113). [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4760782/).

Scope: densest **found** clusters of Platonic solids with `N=4–60` in a spherical container, using Monte Carlo compression. Examines layers, symmetry, density profiles, and especially dense “magic-number” clusters. It found substantial commonality between spherical, icosahedral, and dodecahedral cluster structures and emphasizes the effects of the container. Boundary: these results directly justify looking for count-dependent structural transitions, but spherical confinement is different from the polyhedral containers studied here. “Magic numbers” do not imply universal count sequences for all shapes.

**Mihir R. Khadilkar and Fernando A. Escobedo.** “Phase behavior of polyhedral nanoparticles in parallel plate confinement.” *Soft Matter* **12**(5), 1506–1516 (2016; article online 10 December 2015). DOI: [10.1039/C5SM02570B](https://doi.org/10.1039/C5SM02570B). [PubMed bibliographic record and abstract](https://pubmed.ncbi.nlm.nih.gov/26659811/).

Scope: hard cubes, truncated cubes, cuboctahedra, and truncated octahedra between parallel walls, varying the wall separation to accommodate different numbers of layers. Reports ordered, buckled, plastic, and disordered structures and geometrical frustration near layer transitions. Boundary: a confined many-particle phase study is not a finite fit optimum.

**Nathan C. Huang, Rachael S. Skye, and Julia Dshemuchadse.** “Advancing the self-assembly of binary colloidal crystals of tetrahedra and octahedra with confinement.” *Molecular Systems Design & Engineering* **11**(1), 62–69 (**2026**; first published online **11 November 2025**). DOI: [10.1039/D5ME00092K](https://doi.org/10.1039/D5ME00092K). [Publisher paper](https://pubs.rsc.org/en/content/articlehtml/2026/me/d5me00092k); [author dataset, DOI 10.18126/tykw-5q20](https://acdc.alcf.anl.gov/mdf/detail/ebe16bf6-4c29-4f80-bbc8-0404c8fb015d-1.0/).

Scope: hard-particle Monte Carlo assembly of a 2:1 equal-edge tetrahedra–octahedra mixture in spherical and flat-wall confinement. Boundary: it supplies direct physical context for confinement and ordering, with a specified model. It does not validate the physical dynamics of a geometric fitting optimizer. Publisher-indexed HTML and the authors' [publication list](https://capecrystal.mse.cornell.edu/publications/) confirm the issue metadata.

## Infinite packing: useful background with explicit boundaries

**Salvatore Torquato and Yang Jiao.** “Dense packings of the Platonic and Archimedean solids.” *Nature* **460**, 876–879 (2009). DOI: [10.1038/nature08239](https://doi.org/10.1038/nature08239); [arXiv:0908.4107](https://arxiv.org/abs/0908.4107).

**Salvatore Torquato and Yang Jiao.** “Dense packings of polyhedra: Platonic and Archimedean solids.” *Physical Review E* **80**, 041104 (2009). DOI: [10.1103/PhysRevE.80.041104](https://doi.org/10.1103/PhysRevE.80.041104); [arXiv:0909.0940](https://arxiv.org/abs/0909.0940).

Both use an adaptive shrinking **periodic** cell. They connect dense packing to shape symmetry and distinguish lattice and nonlattice structures. Their central-symmetry organizing principle is presented as a **conjecture**, not a general finite-container theorem. In particular, their quoted tetrahedral densities are historical computational results, not a statement of the current global optimum. A periodic-cell method differs from fitting a finite number of particles against hard walls.

**Elizabeth R. Chen, Michael Engel, and Sharon C. Glotzer.** “Dense crystalline dimer packings of regular tetrahedra.” *Discrete & Computational Geometry* **44**, 253–280 (2010; online 17 July, issue September). DOI: [10.1007/s00454-010-9273-0](https://doi.org/10.1007/s00454-010-9273-0); [publisher metadata](https://link.springer.com/article/10.1007/s00454-010-9273-0); [arXiv:1001.0586](https://arxiv.org/abs/1001.0586).

Provides density `4000/4671 ≈ 0.856347` for a periodic tetrahedral dimer construction and proves maximal density **within its three-parameter family**. Boundary: family optimality is not global optimality, and bulk density is not a finite polyhedral fit record. This distinction is a useful template for separating proven construction facts from heuristic search claims.

**U. Betke and M. Henk.** “Densest lattice packings of 3-polytopes.” *Computational Geometry* **16**(3), 157–186 (2000). DOI: [10.1016/S0925-7721(00)00007-9](https://doi.org/10.1016/S0925-7721(00)00007-9). [Authors' institutional preprint abstract](https://math.ovgu.de/Forschung/Ver%C3%B6ffentlichungen/Preprints_%2BTechnical%2BReports%2B%28alte%2BVersion%29/Preprints/1999/99_18-p-2508.html).

Scope: an algorithm for densest **lattice** packings of arbitrary three-dimensional polytopes, applied to regular and Archimedean solids. Boundary: a lattice result constrains translates at lattice sites and does not cover all freely rotating arrangements or finite containers.

The 1959 article **T. Bakos, “Octahedra Inscribed in a Cube,”** *The Mathematical Gazette* **43**(343), 17–20, DOI [10.2307/3608867](https://doi.org/10.2307/3608867), studies inscription and intersections of four octahedra; it is **not** a nonoverlapping multiple-octahedra packing result. [Publisher extract](https://www.cambridge.org/core/journals/mathematical-gazette/article/abs/octahedra-inscribed-in-a-cube/9EFAE1C7B3F27B4A4680BBCC6CF9B1AE). The publisher's online date of November 2016 must not be mistaken for its publication year.

## Wikipedia coverage and an article strategy

On 11 October 2026, [Packing problems](https://en.wikipedia.org/wiki/Packing_problems) already had sections on Platonic solids in infinite space and on finite polyhedra in spheres, plus finite cuboid and sphere packing. [Tetrahedron packing](https://en.wikipedia.org/wiki/Tetrahedron_packing) and [Sphere packing in a cube](https://en.wikipedia.org/wiki/Sphere_packing_in_a_cube) exist. Direct URLs for `Cube_packing`, `Cube_packing_in_a_cube`, `Polyhedral_packing`, and `Polyhedral_fits` returned HTTP 404 in this check. This checks these titles; it is not proof that no relevant page exists under another name or language.

**Recommended working title: “Packing polyhedra in polyhedral containers.”** It clearly identifies the finite problem. “Polyhedral fits” was not found as established scholarly terminology in this pass. “Polyhedral packing” is also used for certain generalized Apollonian **circle** packings derived from polyhedral graphs; see [Domains of Convergence for Polyhedral Packings, arXiv:2109.01289](https://arxiv.org/abs/2109.01289). [Wikipedia's title policy](https://en.wikipedia.org/wiki/Wikipedia:Article_titles) favors names or descriptive titles grounded in reliable usage. This is an editorial recommendation, not a reservation of the title.

The new draft can include established definitions, historical literature, method categories, sourced examples, distinctions between numerical records and proofs, and a visualization plan. Novel trends derived from the user's dataset belong in the research paper. They should not be copied into an encyclopedia as accepted findings merely because the paper is posted to GitHub or arXiv.

[No original research](https://en.wikipedia.org/wiki/Wikipedia:No_original_research) requires published sources for claims and disallows new interpretations or synthesized conclusions that the sources do not make. Primary scientific papers may support cautious straightforward descriptions, but an entire article should not rest on them. Analytical or interpretive statements need secondary or tertiary support. A self-authored paper reporting the author's new results remains a primary source; self-publication does not make it an independent secondary source.

[Notability](https://en.wikipedia.org/wiki/Wikipedia:Notability) asks for significant treatment in reliable, independent sources, with secondary sources generally expected; separate-page status is not guaranteed. Broad packing theory has substantial coverage, but a narrower all-pairs finite-container article may need more independent coverage. A sourced expansion of **Packing problems** is an available alternative if a standalone draft is declined.

Useful independently authored survey/background candidates are **Gábor Fejes Tóth, “Packing and covering,” chapter 2 of the *Handbook of Discrete and Computational Geometry*, 3rd ed. (2017)** ([author-hosted chapter](https://www.csun.edu/~ctoth/Handbook/chap2.pdf), §2.2 covers bounded domains); **S. Torquato and F. H. Stillinger, “Jammed hard-particle packings: From Kepler to Bernal and beyond,” *Rev. Mod. Phys.* 82, 2633 (2010)** ([publisher](https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.82.2633?ft=1)); and **S. Torquato, “Perspective: Basic understanding of condensed phases of matter via packing models,” *J. Chem. Phys.* 149, 020901 (2018), DOI 10.1063/1.5036657** ([author preprint](https://arxiv.org/abs/1805.04468)). These cover the broader field; they do not supply independent analysis of the present dataset or establish narrow-topic notability on their own. Verify exact supporting sections before using any specific encyclopedic claim.

Because the proposed article is connected to the author's own work and business, [Wikipedia's conflict-of-interest guideline](https://en.wikipedia.org/wiki/Wikipedia:Conflict_of_interest) is relevant: disclose the connection, request independent review, and use [Articles for Creation](https://en.wikipedia.org/wiki/Wikipedia:Articles_for_creation) for a new article when eventually authorized. No Wikipedia editing is authorized in this stage; the current deliverable is a local/repository draft for the user's review.

### Rotatable visuals

[MediaWiki's 3D extension](https://www.mediawiki.org/wiki/Extension:3D) supports STL files and, with its viewer, interaction such as movement, panning and zooming. The documentation says it is deployed on Wikimedia projects, but this does not establish that an arbitrary repository HTML/JavaScript viewer can run inside Wikipedia. Plan static SVG/PNG figures with captions and portable STL geometry for a later Commons workflow; keep the richer parameterized interactive viewer in the repository. Current exact Wikipedia/Commons deployment, file-license details, and acceptance of each proposed model need verification at the later upload stage. No models were uploaded.

## Fast legitimate dissemination and publication

The **12 October update** selects direct Zenodo records for both papers and their frozen archive. The [verified platform rules](tonight-platform-rules.md) supersede the earlier Experimental Mathematics readiness recommendation: its publisher prohibits AI-generated manuscript first drafts, so the present papers are not compliant submissions there as written. JoCG and Discrete & Computational Geometry are candidates for a separate policy and submission check. The full decision table, checked on 11 October 2026, is in [Dissemination alternatives](dissemination-alternatives.md). Public availability, a DOI archive, and peer-reviewed acceptance are different outcomes.

arXiv's own [1 October 2026 announcement](https://www.linkedin.com/posts/arxiv_as-of-october-1-arxiv-is-updating-our-submission-activity-7511500706516836352-Of8s) confirms two submissions per submitter per calendar month across all categories. [Endorsement](https://info.arxiv.org/help/endorsement.html) also applies to first submissions or new categories. These are genuine obstacles; approved dissemination elsewhere should not wait for sponsorship.

[Zenodo](https://help.zenodo.org/docs/get-started/quickstart/) provides a direct publication workflow and DOI assignment, while its [policy](https://about.zenodo.org/policies/) permits depositors without an institutional restriction. Archive the exact coordinates, verifier, analysis, viewer, and source commit. HAL is an established manuscript alternative: [manual checks](https://doc.hal.science/en/check-of-deposits/) can take a few days, and are not scientific peer review. Its [required affiliation field](https://doc.hal.science/en/deposit_new/) needs honest completion; independent-author handling has not been confirmed.

[Experimental Mathematics](https://www.tandfonline.com/action/journalInformation?journalCode=uexm20&show=aimsScope) fits precise experimental conjectures and their supporting data topically, but the [current first-draft policy](https://authorservices.taylorandfrancis.com/editorial-policies/using-ai-in-your-research-and-manuscript-preparations/) prevents an as-is submission of these manuscripts. Its first-decision metric should not be read as time to reviewed acceptance. [JoCG](https://jocg.org/index.php/jocg/about) is a fee-free peer-reviewed geometric-method alternative for Paper 1, without a verified fast-turnaround promise.

[Preprints.org](https://www.preprints.org/instructions-for-authors) is a plausible fast mathematics fallback. [SSRN's MathRN](https://www.ssrn.com/index.cfm/en/prn/prn-research-paper-series/) is recognizable, but [processing](https://www.elsevier.support/ssrn/answer/ssrn-review-process) can take up to 10 business days. [OSF's generalist server](https://www.cos.io/blog/update-on-future-of-osf-preprints?hs_amp=true) remains suspended indefinitely and should not be recommended for a new manuscript.

No submission, DOI reservation, account creation, endorsement request, or catalogue outreach has been made outside GitHub. The publication recommendation is prepared for author review.

## Claim discipline for the two papers

Use **“feasible construction,” “best found in this search,” “improved upper bound on minimum container side,” “improved lower bound on maximum particle scale,”** or **“optimal within the specified family”** as applicable. Reserve **“globally optimal”** for matching rigorous lower/upper bounds or a complete certified proof. A numerical result can legitimately improve a bound without solving the problem.

Count jumps, apparent plateaus, orientation clusters, and construction families should be described with tolerances, scale normalization, sample coverage, missing cases, and search effort. Do not interpret failed optimization as proven infeasibility. Distinguish a structural plateau proved by a reusable construction from a repeated rounded numerical result. Include the validation method and machine-readable coordinates for each claimed improvement.

What remains unverified by this literature pass: a complete global record table for all 25 ordered Platonic-solid pairs; rigorous optimality of the user's fits; provenance of each historical user result; and independent secondary coverage of the user's new pattern analysis. No “first,” “world record,” or physical-grain claim follows from this bibliography alone.

## Additional references located during encyclopedia drafting

**Hallard T. Croft.** “On Maximal Regular Polyhedra Inscribed in a Regular Polyhedron.” *Proceedings of the London Mathematical Society* **s3-41**(2), 279–296 (1980). DOI: [10.1112/plms/s3-41.2.279](https://doi.org/10.1112/plms/s3-41.2.279).

**Moritz Firsching.** “Computing Maximal Copies of Polyhedra Contained in a Polyhedron.” *Experimental Mathematics* **24**(1), 98–105 (2015). DOI: [10.1080/10586458.2014.956374](https://doi.org/10.1080/10586458.2014.956374). [Author page](https://firsching.ch/papers/j002-computing-maximal-copies.html); [full paper](https://firsching.ch/assets/pdfs/ComputingMaximalCopies.pdf).

Boundary: these treat a **single** similar copy, not a finite collection. Firsching documents Croft's 14 solved cases among the 20 unequal ordered Platonic pairs, then supplies numerical configurations and conjectured algebraic optima for six remaining cases. It is particularly relevant to the containment section and a precedent for the proposed *Experimental Mathematics* venue.

**Gerhard Wäscher, Heike Haußner, and Holger Schumann.** “An improved typology of cutting and packing problems.” *European Journal of Operational Research* **183**(3), 1109–1130 (2007). DOI: [10.1016/j.ejor.2005.12.047](https://doi.org/10.1016/j.ejor.2005.12.047). [Publisher](https://www.sciencedirect.com/science/article/pii/S037722170600292X). Scope: general problem classification; does not independently establish a project-specific nine-pair taxonomy.

**Aline A. S. Leao, Franklina M. B. Toledo, José Fernando Oliveira, Maria Antónia Carravilla, and Ramón Alvarez-Valdés.** “Irregular packing problems: A review of mathematical models.” *European Journal of Operational Research* **282**(3), 803–822 (2020). DOI: [10.1016/j.ejor.2019.04.045](https://doi.org/10.1016/j.ejor.2019.04.045). [Publisher](https://www.sciencedirect.com/science/article/pii/S0377221719303820). Boundary: primarily a two-dimensional mathematical-model survey, with three-dimensional extensions discussed.

**Luiz J. P. Araújo, Ender Özcan, Jason A. D. Atkin, and Martin Baumers.** “Analysis of irregular three-dimensional packing problems in additive manufacturing: a new taxonomy and dataset.” *International Journal of Production Research* **57**(18), 5920–5934 (2019; online 16 October 2018). DOI: [10.1080/00207543.2018.1534016](https://doi.org/10.1080/00207543.2018.1534016). [Institutional record](https://nottingham-repository.worktribe.com/output/1190642/analysis-of-irregular-three-dimensional-packing-problems-in-additive-manufacturing-a-new-taxonomy-and-dataset). Scope: independently authored three-dimensional packing taxonomy and additive-manufacturing context.

**Y. Ma, Z. Chen, W. Hu, and W. Wang.** “Packing Irregular Objects in 3D Space via Hybrid Optimization.” *Computer Graphics Forum* **37**(5), 49–59 (2018). DOI: [10.1111/cgf.13490](https://doi.org/10.1111/cgf.13490). [Publisher](https://onlinelibrary.wiley.com/doi/10.1111/cgf.13490); [Eurographics paper](https://diglib.eg.org/bitstream/handle/10.1111/cgf13490/v37i5pp049-059.pdf). Scope: arbitrary-shape objects and containers, free rotations, hybrid continuous/combinatorial heuristic optimization. Additional prior evidence against a claim that generic freely rotating fitting began with the current project.

**Stefan Gottschalk, Ming C. Lin, and Dinesh Manocha.** “OBBTree: A Hierarchical Structure for Rapid Interference Detection.” *Proceedings of SIGGRAPH '96*, 171–180 (1996). [Paper](https://www.cs.cornell.edu/courses/cs667/2005sp/readings/gottschalk96.pdf). Scope: separating-axis tests and hierarchical oriented bounding boxes for rigid-model collision detection; a geometric ingredient, not a packing optimizer.

### Fresh primary claims supplied by the coordinating pass

The coordinator observed [small_LM's Twitter post](https://x.com/small_LM/status/2109345921465229780) reporting cube-in-cube candidates for `N=34,35,36` with scales `3.82288,3.86069,3.89443`, plus attribution discussion for `N=11,12`. It observed the [project author's reply](https://x.com/AlejandroZarUrd/status/2109347076312367133) about generalized improvements beyond cubes. This subagent's web-reader requests returned 403, so this register preserves the coordinator's observations as primary-source leads, **not verified current records**. Coordinates, normalization, feasibility certificates and dated comparison are still needed. The clean Wikipedia text intentionally excludes these fresh claims.
