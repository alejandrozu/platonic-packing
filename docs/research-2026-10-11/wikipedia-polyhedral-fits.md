# Packing polyhedra in polyhedral containers

**Wikipedia review draft — 11 October 2026. Not submitted.** The article text below contains established background and clearly identified numerical catalogues. The accompanying `.wiki` file is clean MediaWiki source. The extensive editorial annex after the article is planning material and must not be pasted into an encyclopedia article.

The requested phrase **“Polyhedral fits”** is preserved in the filenames and review packet. A descriptive article title is used because this research pass did not establish that the phrase is accepted scholarly terminology. Title and redirect choices remain subject to independent Wikipedia review.

---
**Packing polyhedra in polyhedral containers** is a class of finite [packing problems](https://en.wikipedia.org/wiki/packing_problems) in which three-dimensional [polyhedra](https://en.wikipedia.org/wiki/polyhedron) are placed inside another polyhedron without overlapping interiors. Depending on the formulation, the objective is to maximize the size or number of the packed objects, or to minimize the dimensions or volume of the container. The objects may be congruent copies of one shape or a collection of different shapes. Allowable motions can be restricted to translations, to a finite set of orientations, or can include arbitrary rotations.[1](#reference-1)[2](#reference-2)

These problems are related to geometric [optimization](https://en.wikipedia.org/wiki/optimization), three-dimensional nesting, and containment of one polyhedron in another. They differ from packing in infinite space: a finite container has walls whose geometry affects feasible arrangements. They also differ from a physical assembly problem, which requires a model of particle interactions and statistical or dynamical behavior in addition to a geometrical configuration.[3](#reference-3)[4](#reference-4)

## Formulation

For a fixed particle polyhedron $P$, container polyhedron $C$, and positive integer $N$, a freely rotating congruent packing consists of copies

$$
P_i=t_i+R_iP,\qquad i=1,\ldots,N,
$$

where $t_i$ is a translation and $R_i$ is a rotation. Each copy must be contained in the container, and the interiors of distinct copies must be disjoint:

$$
P_i\subseteq C,\qquad \operatorname{int}(P_i)\cap\operatorname{int}(P_j)=\varnothing\quad(i\ne j).
$$

This convention permits contact at faces, edges, or vertices. A version with a positive clearance imposes additional distance constraints. Continuous rotations, containment, nonoverlap, and prescribed minimum distances appear in mathematical programming formulations for polyhedral packing.[5](#reference-5)

Three related objectives are common. A fixed-size item problem asks how many copies can fit. A fixed-count problem maximizes their common scale in a fixed container. A container minimization problem fixes the objects and optimizes the containing shape's permitted dimensions. The distinction between output maximization and input minimization is part of general cutting-and-packing classification.[1](#reference-1)

For example, with unit-edge particles and a container whose shape is fixed but whose edge scale $s$ varies, define

$$
s_{C,P}(N)=\inf\{s>0:N\text{ congruent copies of }P\text{ fit in }sC\}.
$$

In this notation, a feasible arrangement at scale $s$ establishes an upper bound on the minimum container scale. If instead the container is fixed and the particles' common scale is maximized, a feasible arrangement establishes a lower bound on that maximum. Thus the direction of an improved bound depends on the objective.

## Scale, density, and elementary bounds

For $N$ congruent particles of volume $V(P)$ contained without overlap in $C$, their packing fraction is

$$
\phi=\frac{NV(P)}{V(C)}.
$$

The total particle volume cannot exceed the container volume. For a uniformly scaled three-dimensional container this gives the necessary bound

$$
s_{C,P}(N)\geq\left(\frac{NV(P)}{V(C)}\right)^{1/3}.
$$

The volume comparison gives a bound rather than a placement: unused regions can remain because of particle shape, orientation, or the boundary. Congruent-polyhedron formulations use this distinction between a volume bound and a geometrically feasible packing.[6](#reference-6)

For identical unit-edge cubes, an $m\times m\times m$ grid is a packing of $m^3$ cubes in a cube of edge $m$. Its density is one, so the grid meets the volume bound for those counts. For a general count, deleting cubes gives the elementary upper bound $\lceil N^{1/3}\rceil$. This bound does not restrict the cubes to grid arrangements in the optimization problem.

The normalization of a record is part of the problem definition. Unit edge, unit volume, unit circumradius, and unit inradius describe different particle sizes. A container-edge ratio is a length measure, whereas density depends on volume and therefore on the cube of scale. Numerical values for different particle shapes are not comparable unless the normalization and objective are specified.

## Particle and container representation

A convex polyhedron can be described by its vertices or by half-spaces bounded by its face planes. If

$$
C=\{x:a_f\cdot x\leq b_f\text{ for every face }f\},
$$

then a convex particle is contained in $C$ precisely when its vertices satisfy all the container inequalities. Convexity ensures that their convex hull is contained as well. A single-particle containment formulation can combine these linear inequalities with constraints preserving pairwise vertex distances under a common scale.[7](#reference-7)

For two convex polyhedra, nonoverlap can be tested using a separating plane. Separating-axis collision tests compare projections onto candidate directions. The candidates for polyhedra include face-normal directions and directions formed from pairs of edge directions. Such tests are also used in oriented-bounding-box hierarchies for interference detection between complex rigid models.[8](#reference-8)

For nonconvex objects, a single separating plane need not describe disjointness. Methods may instead use convex decomposition, detailed intersection calculations, or other geometric representations. Translational polytope search can handle nonconvex objects and holes, while nonlinear polyhedral models can incorporate collections of convex components.[2](#reference-2)[5](#reference-5)

## One polyhedron inside another

The case $N=1$ is a containment problem, involving both orientation and scale. It has a history distinct from the packing of several particles. Hallard T. Croft studied maximal regular polyhedra inside regular polyhedra in 1980. Among the twenty ordered pairs of different Platonic solids, his treatment resolved fourteen cases. Firsching's 2015 study considered arbitrary pairs through quadratic optimization and supplied numerical configurations and conjectured exact algebraic solutions for the remaining six Platonic cases.[9](#reference-9)[7](#reference-7)

Inscription is not the same as a packing of multiple objects. Several polyhedra inscribed in one container can overlap. For example, Bakos's 1959 discussion of octahedra inscribed in a cube concerns configurations and their common intersection; it does not establish a nonoverlapping packing of four octahedra.[10](#reference-10)

## Shape-pair families

Particle and container roles are ordered: cubes in an octahedron and octahedra in a cube are different problems. Among the five Platonic solids, a simple selection of related pairs consists of the five same-solid problems and the four directions between distinct dual solids. This selection is not an exhaustive classification of polyhedral packing: arbitrary pairs, mixed particles, and other convex or nonconvex polyhedra are also possible.[7](#reference-7)[2](#reference-2)

| Particle | Container | Relation defining the pair |
|---|---|---|
| Tetrahedron | Tetrahedron | Same solid |
| Cube | Cube | Same solid |
| Octahedron | Octahedron | Same solid |
| Dodecahedron | Dodecahedron | Same solid |
| Icosahedron | Icosahedron | Same solid |
| Cube | Octahedron | Distinct dual solids |
| Octahedron | Cube | Distinct dual solids |
| Dodecahedron | Icosahedron | Distinct dual solids |
| Icosahedron | Dodecahedron | Distinct dual solids |

The tetrahedron is self-dual. Geometric duality exchanges faces and vertices, but it does not identify the multiple-particle packing problems in opposite directions. Single-object studies also use polar reciprocity under appropriate conditions; extending such relations to a finite collection requires attention to the complete nonoverlap and containment constraints.[7](#reference-7)

### Cubes in cubes

Packing freely oriented equal cubes in a containing cube includes arrangements that depart from the elementary cubic grid. Erich Friedman's online packing catalogue records a construction for nine or ten unit cubes with containing edge $2+1/\sqrt{2}$, attributed to Friedman in 1998. It also lists a common construction size $3+1/\sqrt{2}$ for counts twenty-eight through thirty-three. The catalogue describes its values as smallest known sizes.[11](#reference-11)

A smallest-known numerical entry differs from a proved minimum. A record table can improve when another feasible configuration is found. Equal listed sizes for several counts can describe the capacity of a construction; the equality of true optima requires lower-bound evidence as well as feasible placements.

Some problems described as cube packing have different objectives. Fan, Zhang and Ye's 2008 cube-packing paper, for example, allows unequal axis-parallel small cubes and optimizes the sum of their edge lengths. Its packing function is therefore different from the minimum containing edge for a prescribed number of congruent freely oriented cubes.[12](#reference-12)

### Octahedra in cubes

Friedman's octahedron-in-cube catalogue records equal unit octahedra in a containing cube, with entries for counts one through thirty at the time of retrieval. Its printed entries include a common side of approximately 1.79133 for seven or eight octahedra and approximately 2.63986 for twenty-six or twenty-seven octahedra. The entries are numerical smallest-known constructions, and their rounding should not be interpreted as an exact optimality theorem.[13](#reference-13)

This finite problem is distinct from the lattice packing of octahedra throughout space. A bulk lattice's repeating unit does not have the same constraints as a cubical box with walls.

### Tetrahedra in cubes

The packing catalogue also includes tetrahedra in cubes. It lists a containing cube of edge one for three unit tetrahedra, attributed to Achille Hui in February 2016, and numerical entries through thirty particles. Consequently, finite packing in cubes is not limited to cubes and octahedra.[14](#reference-14)

Regular tetrahedra lack central symmetry, introducing geometric distinctions from centrally symmetric particles. This distinction also appears in the study of bulk tetrahedral packings, including constructions using pairs of tetrahedra.[15](#reference-15)

## Computational methods

### Constructive and optimization approaches

A construction provides explicit positions and orientations, sometimes with a scale given by a formula. Numerical search can instead start from trial placements and adjust the objects or container. In general irregular nesting, mathematical models employ continuous, discrete, mixed-integer, nonlinear, or constraint-programming representations. These choices affect permissible orientations and how geometry is enforced. The major survey by Leao and colleagues primarily concerns two-dimensional nesting, with discussion of extensions to three dimensions.[16](#reference-16)

Egeblad, Nielsen and Brazil's method uses translations that minimize overlap volume, combined with local search and guided local search to leave local minima. Romanova and colleagues model continuously rotating concave polyhedra with quasi-phi functions, using initial-placement and compaction procedures. Callisaya and Kari use separating hyperplanes and nonlinear optimization for congruent objects in convex sets, with multistart initialization.[2](#reference-2)[5](#reference-5)[6](#reference-6)

The distinction between an exact mathematical model and an exact global solution is essential. A nonlinear formulation may express the geometry without approximation while a local solver returns one feasible configuration or local minimum. Failure of that solver to find a configuration does not, by itself, establish infeasibility.

General approximation algorithms have also been developed for finding small-volume containers for three-dimensional convex objects under different allowed motions and container classes. Their approximation guarantees address a different question from computing an exact small-count optimum for one fixed pair of regular solids.[17](#reference-17)

### Numerical results and proof

Several levels of result should be distinguished: a rendered picture, a numerical placement passing a tolerance-based check, a placement verified by exact or rigorously bounded arithmetic, and a globally optimal solution. Verification of one placement addresses feasibility. Global optimality additionally excludes every better placement allowed by the problem definition.

Algebraic reconstruction can turn a numerically suggested single-polyhedron configuration into an exact candidate by solving its contact equations and identifying algebraic values. This still requires distinguishing the exact configuration from a proof that no larger configuration exists.[7](#reference-7) Similarly, a tetrahedral dimer study proves maximum density within a specified parameter family; its family result does not imply optimality over all possible packings.[18](#reference-18)

For reproducibility, a geometric result can specify the canonical particle and container, scale convention, translations, rotations, and contact or separating-plane information. A picture is an illustration of these data: its projection, perspective, and hidden surfaces are not the nonoverlap constraints themselves.

## Finite confinement and infinite packing

In infinite-space packing, density describes an arrangement extending without a containing wall. A lattice packing places identically oriented translates at lattice sites. More general periodic packings can have several particles and orientations per repeating cell, while unrestricted packings need not be periodic.[3](#reference-3)

Torquato and Jiao's adaptive shrinking cell method adjusts particle placements and a periodic fundamental cell. It was applied to dense packings of Platonic and Archimedean solids and led to conjectures relating central symmetry to lattice optimality. The periodic boundary condition is integral to the method; a cell's sides are not the walls of a finite fit problem.[15](#reference-15)[19](#reference-19)

Betke and Henk developed an algorithm for densest lattice packings of three-dimensional polytopes. Such lattice optimization is valuable background, but its restricted arrangement class does not establish optimality for freely rotating finite particles in a prescribed container.[20](#reference-20)

Confinement can change structural preferences. Teich and colleagues generated dense clusters of Platonic solids containing four to sixty particles in spherical containers. The clusters showed layers, different symmetries, and particularly dense particle counts termed magic numbers. Some icosahedral and dodecahedral clusters resembled sphere clusters, illustrating the importance of the container in the investigated size range. These results concern spherical confinement rather than an interchangeable family of polyhedral walls.[21](#reference-21)

## Orientation, contacts, and count dependence

Unlike spheres, nonspherical particles have rotational degrees of freedom. Their packings can be compared by density and by structural order, rather than density alone. Reviews of hard-particle packing distinguish equilibrium phases, jammed configurations, and different forms of order.[22](#reference-22)

Positions, relative orientations, and contacts describe different aspects of an arrangement. Face-to-face alignment can aid local dense packing, but a container can favor an overall cluster shape with other contacts. The spherical-confinement study found a trade-off between tight local alignment and the shape of the complete cluster; its especially dense counts did not share one universal structural rule.[21](#reference-21)

A count-dependent record table is therefore more than a list of densities, but numerical regularities require careful interpretation. Repeated rounded scales may reflect the precision of reporting. A single construction accommodating several counts establishes those feasible scales, without proving that all corresponding optima coincide. Deleting a particle from any feasible arrangement gives a feasible arrangement for the preceding count; this elementary observation concerns the optimization problem, whereas a numerical search's independently found entries can fail to attain the best available construction.

Layer transitions also occur in physical models of confined particles. Khadilkar and Escobedo studied cubes and several truncated or related shapes between parallel hard walls. Changing the wall separation produced several ordered and disordered phases, including frustrated structures near a layer transition. The relevant variable there is a physical confinement width, rather than solely the particle count in a fixed-shape finite container.[23](#reference-23)

## Relationship to crystallization

Hard-particle packing models provide a geometric setting for examining material structure, but a densest construction and an assembled crystal are different results. Physical studies specify conditions and mechanisms under which order develops; finite fitting specifies the admissible shapes, movements, and boundary.[4](#reference-4)

Huang, Skye and Dshemuchadse investigated self-assembly of an equal-edge tetrahedron–octahedron mixture using hard-particle Monte Carlo simulations. Their spherical and flat-wall confinement study concerns a two-component system and a specified statistical model. It supplies an example of confinement affecting assembly, rather than establishing that every optimized polyhedral fit is a crystal-growth pathway.[24](#reference-24)

## Applications and broader nesting problems

Finite three-dimensional packing has applications in arranging manufactured parts in a build volume. Araújo and colleagues reviewed classifications relevant to additive manufacturing and introduced a dataset for irregular three-dimensional packing. Practical instances can involve arbitrary shapes, heterogeneous objects, orientation constraints, and manufacturing considerations beyond the congruent regular-polyhedron problem.[25](#reference-25)

Ma and colleagues' hybrid optimization work allows objects and containers of arbitrary shapes with free rotations. This broader setting emphasizes that a regular-polyhedron catalogue is a well-defined special class within three-dimensional packing, rather than the entire subject.[26](#reference-26)

## See also

* [Packing problems](https://en.wikipedia.org/wiki/Packing_problems)
* [Tetrahedron packing](https://en.wikipedia.org/wiki/Tetrahedron_packing)
* [Sphere packing in a cube](https://en.wikipedia.org/wiki/Sphere_packing_in_a_cube)
* [Platonic solid](https://en.wikipedia.org/wiki/Platonic_solid)
* [Convex polytope](https://en.wikipedia.org/wiki/Convex_polytope)
* [Bin packing problem](https://en.wikipedia.org/wiki/Bin_packing_problem)
* [Tetrahedral-octahedral honeycomb](https://en.wikipedia.org/wiki/Tetrahedral-octahedral_honeycomb)
* [Discrete geometry](https://en.wikipedia.org/wiki/Discrete_geometry)

## References

<a id="reference-1"></a>
1. Wäscher, Haußner, Schumann. [An improved typology of cutting and packing problems](https://doi.org/10.1016/j.ejor.2005.12.047). European Journal of Operational Research 183, 1109–1130 (2007).

<a id="reference-2"></a>
2. Egeblad, Nielsen, Brazil. [Translational packing of arbitrary polytopes](https://www.sciencedirect.com/science/article/pii/S0925772108000576). Computational Geometry 42, 269–288 (2009).

<a id="reference-3"></a>
3. Fejes Tóth. [Packing and covering, in Handbook of Discrete and Computational Geometry](https://www.csun.edu/~ctoth/Handbook/chap2.pdf).  ,  (2017).

<a id="reference-4"></a>
4. Torquato. [Perspective: Basic understanding of condensed phases of matter via packing models](https://doi.org/10.1063/1.5036657). The Journal of Chemical Physics 149, 020901 (2018).

<a id="reference-5"></a>
5. Romanova, Bennell, Stoyan, Pankratov. [Packing of concave polyhedra with continuous rotations using nonlinear optimisation](https://eprints.soton.ac.uk/418130/). European Journal of Operational Research 268, 37–53 (2018).

<a id="reference-6"></a>
6. Callisaya, Kari. [Packing Polyhedra within Convex Sets](https://www.scielo.br/j/tcam/a/nbGY4xC4KMxq7XbYZTybvHj/?format=html&lang=en). Trends in Computational and Applied Mathematics 26, e01823 (2025).

<a id="reference-7"></a>
7. Firsching. [Computing Maximal Copies of Polyhedra Contained in a Polyhedron](https://firsching.ch/assets/pdfs/ComputingMaximalCopies.pdf). Experimental Mathematics 24, 98–105 (2015).

<a id="reference-8"></a>
8. Gottschalk, Lin, Manocha. [OBBTree: A Hierarchical Structure for Rapid Interference Detection](https://www.cs.cornell.edu/courses/cs667/2005sp/readings/gottschalk96.pdf). Proceedings of SIGGRAPH '96 , 171–180 (1996).

<a id="reference-9"></a>
9. Croft. [On Maximal Regular Polyhedra Inscribed in a Regular Polyhedron](https://doi.org/10.1112/plms/s3-41.2.279). Proceedings of the London Mathematical Society s3-41, 279–296 (1980).

<a id="reference-10"></a>
10. Bakos. [Octahedra Inscribed in a Cube](https://doi.org/10.2307/3608867). The Mathematical Gazette 43, 17–20 (1959).

<a id="reference-11"></a>
11. Friedman. [Cubes in Cubes](https://erich-friedman.github.io/packing/cubincub/).  ,  ().

<a id="reference-12"></a>
12. Fan, Zhang, Ye. [A Cube-Packing Problem](https://combinatorialpress.com/article/ars/Volume%20087/volume-87-paper-27.pdf). Ars Combinatoria 87, 353–358 (2008).

<a id="reference-13"></a>
13. Friedman. [Octahedra in Cubes](https://erich-friedman.github.io/packing/octincub/).  ,  ().

<a id="reference-14"></a>
14. Friedman. [Tetrahedra in Cubes](https://erich-friedman.github.io/packing/tetincub/).  ,  ().

<a id="reference-15"></a>
15. Torquato, Jiao. [Dense packings of polyhedra: Platonic and Archimedean solids](https://doi.org/10.1103/PhysRevE.80.041104). Physical Review E 80, 041104 (2009).

<a id="reference-16"></a>
16. Leao, Toledo, Oliveira, Carravilla, Alvarez-Valdés. [Irregular packing problems: A review of mathematical models](https://www.sciencedirect.com/science/article/pii/S0377221719303820). European Journal of Operational Research 282, 803–822 (2020).

<a id="reference-17"></a>
17. Alt, Scharf. [Approximating Smallest Containers for Packing Three-dimensional Convex Objects](https://arxiv.org/abs/1601.04585).  ,  (2016).

<a id="reference-18"></a>
18. Chen, Engel, Glotzer. [Dense crystalline dimer packings of regular tetrahedra](https://doi.org/10.1007/s00454-010-9273-0). Discrete & Computational Geometry 44, 253–280 (2010).

<a id="reference-19"></a>
19. Torquato, Jiao. [Dense packings of the Platonic and Archimedean solids](https://doi.org/10.1038/nature08239). Nature 460, 876–879 (2009).

<a id="reference-20"></a>
20. Betke, Henk. [Densest lattice packings of 3-polytopes](https://doi.org/10.1016/S0925-7721(00)00007-9). Computational Geometry 16, 157–186 (2000).

<a id="reference-21"></a>
21. Teich, van Anders, Klotsa, Dshemuchadse, Glotzer. [Clusters of polyhedra in spherical confinement](https://doi.org/10.1073/pnas.1524875113). Proceedings of the National Academy of Sciences 113, E669–E678 (2016).

<a id="reference-22"></a>
22. Torquato, Stillinger. [Jammed hard-particle packings: From Kepler to Bernal and beyond](https://doi.org/10.1103/RevModPhys.82.2633). Reviews of Modern Physics 82, 2633 (2010).

<a id="reference-23"></a>
23. Khadilkar, Escobedo. [Phase behavior of polyhedral nanoparticles in parallel plate confinement](https://doi.org/10.1039/C5SM02570B). Soft Matter 12, 1506–1516 (2016).

<a id="reference-24"></a>
24. Huang, Skye, Dshemuchadse. [Advancing the self-assembly of binary colloidal crystals of tetrahedra and octahedra with confinement](https://pubs.rsc.org/en/content/articlehtml/2026/me/d5me00092k). Molecular Systems Design & Engineering 11, 62–69 (2026).

<a id="reference-25"></a>
25. Araújo, Özcan, Atkin, Baumers. [Analysis of irregular three-dimensional packing problems in additive manufacturing: a new taxonomy and dataset](https://nottingham-repository.worktribe.com/output/1190642/analysis-of-irregular-three-dimensional-packing-problems-in-additive-manufacturing-a-new-taxonomy-and-dataset). International Journal of Production Research 57, 5920–5934 (2019).

<a id="reference-26"></a>
26. Ma, Chen, Hu, Wang. [Packing Irregular Objects in 3D Space via Hybrid Optimization](https://onlinelibrary.wiley.com/doi/10.1111/cgf.13490). Computer Graphics Forum 37, 49–59 (2018).


## External links

* [Erich's Packing Center](https://erich-friedman.github.io/packing/index.html)

---

## Editorial annex — outside the proposed article

### Review status and source boundaries

This is a source-grounded starting draft, not a prediction that Wikipedia will accept a new page. It includes established literature on general packing methods, a nine-pair mathematical grouping of Platonic-solid problems, and examples from Erich Friedman's primary community catalogue. The nine rows describe particle/container pairs. They do not assert that a project-origin nine-family taxonomy is the field's accepted classification or that the project's records have already been independently reviewed.

The proposed article remains relatively rich in primary research references. That is suitable for fact-checking the research packet but needs careful editorial review before Wikipedia submission. The broad field has substantial scholarly treatment; the narrower proposed finite-container scope still needs a persuasive rationale for a separate page and sufficient secondary coverage. A review paper can be secondary for older research while primary for the author's own new claims. Its role must be assessed claim by claim.

[Wikipedia's no-original-research policy](https://en.wikipedia.org/wiki/Wikipedia:No_original_research) disallows novel analyses and synthesized conclusions that the cited sources do not state. A researcher's GitHub repository, code, Twitter thread, or self-authored preprint does not convert the researcher's new interpretation into an independent secondary account. Publication of the two requested papers can document and expose the results to review; it does not automatically make every new finding eligible for encyclopedic inclusion.

[The notability guideline](https://en.wikipedia.org/wiki/Wikipedia:Notability) requires significant treatment in reliable independent sources for a standalone topic, generally with secondary sources. If that narrower scope is not supported, independently sourced improvements to the existing **Packing problems** article may be more appropriate. Neither route has been submitted here.

### How the project can be incorporated later

The [project repository](https://github.com/alejandrozu/platonic-packing) is the reproducibility source for the two companion manuscripts. The audited snapshot used in this review packet is `e15b496ae7306287e0e70bb5b14be79f5dfdde84`. Its nine classes are the five same-solid families plus cubes in octahedra, octahedra in cubes, dodecahedra in icosahedra, and icosahedra in dodecahedra. The project atlas covers counts 2–40 for those pairs. These facts locate the research material; the clean encyclopedia draft does not reproduce its unpublished record table or claim independent endorsement of the dataset.

Potential future additions require different kinds of evidence:

| Proposed addition | Evidence needed before article inclusion |
|---|---|
| Description of the generalized soft-to-rigid procedure | A reputably published method description; secondary treatment for interpretation or significance |
| Claimed numerical improvement | Clearly defined normalization, feasible coordinates, verification, comparator and date; appropriate reliable publication |
| Equality of optimal scales across several counts | Mathematical lower bounds plus matching constructions, or cautious wording that only a construction/numerical plateau is known |
| An orientation-domain pattern | A defined symmetry-aware metric and published analysis; independent secondary interpretation for the encyclopedia |
| Family believed close to optimal | Explicit conjectural status and evidence, without promoting a local optimum to a theorem |
| Relevance to physical grains or crystal formation | A specified physical model or experiment and supporting published research, separate from geometrical feasibility |

The project's exact certificates concern the stored, slightly enlarged containing scale with clearance. A visually or numerically inferred touching-limit scale is a distinct quantity. Any later table must show which scale has been verified and whether “optimal” means within a construction family or among all permitted arrangements. New evidence should be incorporated without erasing earlier attribution or silently changing a normalization.

The two papers should carry the project's new structural analysis: orientation clustering, count jumps, relative and absolute scale increments, plateau capacities, and comparisons of construction families. The encyclopedia should summarize this only to the extent that reliable sources support it, with weight proportionate to its independent coverage. A proposed relation between a geometric orientation cluster and a physical grain should remain an explicit hypothesis until a physical study supports it.

### Fresh record claims and changing comparators

The coordinating research pass observed a [Twitter post by small_LM](https://x.com/small_LM/status/2109345921465229780) reporting cube-in-cube candidates at counts 34, 35 and 36 with scales 3.82288, 3.86069 and 3.89443, and discussing attribution for counts 11 and 12. The [author's reply](https://x.com/AlejandroZarUrd/status/2109347076312367133) emphasizes the generalized project's scope beyond cubes. These are primary claims located by the coordinator; this subagent's web-reader requests returned 403. They are retained as leads for provenance and comparator checking, not inserted as independently verified global records.

A current record statement needs the actual coordinates and consistent scale conventions. Friedman's catalogue and a fresh social-media post may legitimately describe different stages of a changing record history. The papers can report a historical contribution and an improved certified bound even when another researcher later supplies a better construction. Do not equate publication speed, follower response, or repetition of a claim with proof.

### Visualizations and the future article

The local/repository interactive atlas is appropriate for examining rotations, wall contacts, and orientations. For the future article, prioritize a small set of static SVG or PNG figures illustrating explicitly sourced configurations: an elementary cubic grid, an off-grid cube example, an octahedral example, and a single-polyhedron inclusion. Each figure needs a caption giving shapes, count, scale convention, and the result's status. Pictures can clarify already sourced geometry without announcing a new research conclusion.

[MediaWiki's allowed-HTML documentation](https://www.mediawiki.org/wiki/Help:HTML_in_wikitext) does not offer arbitrary script or iframe embedding in normal article wikitext. The repository's custom JavaScript viewer should therefore be an external resource if independently judged appropriate, not an embedded script pasted into the page. [The 3D extension](https://www.mediawiki.org/wiki/Extension:3D) documents STL support and a viewer for panning, zooming, and movement. A later Commons workflow may provide rotatable mesh illustrations, subject to verified deployment, licensing and file requirements; it does not reproduce the repository's full parameterized interface.

No image, mesh, script, paper, or text has been posted to Wikipedia or Commons. The `.wiki` file includes no unlicensed image embeds, invented Commons filenames, broken model references, categories implying acceptance, or advertising copy. Proposed external links must earn their place through encyclopedic usefulness rather than project promotion.

### Conflict of interest and eventual review

The user is an author of the work and has described a business interest in the article. [Wikipedia's conflict-of-interest guideline](https://en.wikipedia.org/wiki/Wikipedia:Conflict_of_interest) recommends disclosure, independent assessment, and the Articles for Creation route for new affected articles. That connection does not disqualify subject expertise, but it makes an independently reviewed submission important. The draft includes no career or business claims.

The eventual reviewer should examine the scope, sources, title, amount of primary sourcing, current-record wording, and whether the nine-pair table is useful in an encyclopedia. Mathematical definitions and routine inequalities may be retained when helpful, while a proposed novel taxonomy or analysis should remain in the research papers. The exact order and depth of sections can change after this review; density of detail is not itself evidence of notability.

Before any later submission, replace weak source placements with precise page/section references where possible and confirm all live links. Huang and colleagues' article first appeared online on 11 November 2025 and is assigned to the 2026 issue, volume 11(1), pages 62–69; the citation uses the issue year. Ma and colleagues' article is in volume 37(5), pages 49–59 (2018), and includes four authors. A separate source register provides retrieval dates, publication routes, and the explicit claim boundaries used in this packet: [literature-and-publication.md](research/literature-and-publication.md).
