# Related work: optimization formulations for packing polytopes, dense polyhedral packings, benchmarks, and certification

Compiled 2026-10-15 for the `platonic-packing` project (github.com/alejandrozu/platonic-packing).

The project packs n congruent copies of a polytope P into the smallest container C. The pieces move by continuous rigid motions. The pipeline is: soft-to-rigid growth, then basin hopping, then sequential-LP (SLP) tightening with per-pair separating hyperplanes, then exact rational/algebraic certification. This review covers four bodies of work: (i) the operations-research literature that writes non-overlap as explicit optimization constraints, which is what Vinicius Jameli was pointing to; (ii) physics work on dense packings of Platonic and Archimedean solids; (iii) published benchmark values; (iv) rigorous verification.

Every citation below was checked against a real web page. The page used is listed under each entry and in **Sources**. Anything checked only through a secondary source (a reference list or Wikipedia) or not checked at all is marked **[secondary]** or **[unverified]**.

---

## 0. Main findings

1. **The closest prior work is Berthold, Kamp, Mexi, Pokutta and Pólik (May 2026, arXiv:2605.04850).** It covers all 25 ordered Platonic-in-Platonic pairs for n ≤ 30 using off-the-shelf global MINLP (SCIP, FICO Xpress). Non-overlap is modelled with a Farkas-lemma certificate. The title ends "...New Models and Improved Solutions", so it is almost certainly Vinicius's "...and Improved Solutions". The project already registers its coordinate supplement (`docs/external_records.json`).
2. **The quasi-phi-function for two convex polytopes (Pankratov, Romanova & Chugay 2015; Romanova, Bennell, Stoyan & Pankratov, EJOR 2018) is mathematically our per-pair separating-plane constraint.** It uses auxiliary variables for the plane's normal angles and offset. Every vertex of piece i must lie on one side and every vertex of piece j on the other. The Kharkiv group solves the full nonlinear program with IPOPT, inside a decomposition scheme called LOFRT that keeps only nearby pairs. Our SLP is in effect a linearized trust-region version of that NLP, with exact certification added. This is the main thing to cite as "same formulation".
3. **LP-based compaction with separating constraints goes back to Li & Milenkovic (EJOR 1995)** and to Gomes & Oliveira's SA + LP hybrid (EJOR 2006). The truncated title "...and Linear Programming" most likely refers to the Gomes & Oliveira paper. In physics, the Torquato–Jiao SLP algorithm (PRE 2010) is the direct analogue for spheres.
4. **Global optimality is out of reach in this area, except for trivial cases.** Berthold et al. report dual bounds that improve on the volume bound only for n ≤ 2. Interval-arithmetic optimality proofs exist only for small 2D circle packings (n ≤ 33; Markót & Csendes, Markót). ∃ℝ-completeness results (Abrahamsen, Miltzow & Seiferth 2020) indicate that exact optima can need algebraic numbers of unbounded degree. This supports certifying feasible packings in a fixed field rather than claiming optimality.

---

## 1. Phi-functions and quasi-phi-functions (Stoyan / Romanova / Pankratov / Scheithauer / Chugay, Kharkiv and Dresden)

A phi-function Φ(u_i, u_j) is a continuous function of the placement parameters u = (translation, rotation) of two objects. It is positive when the objects are separated, zero when they touch, and negative when they overlap. Packing then becomes a nonlinear program with constraints Φ ≥ 0. A **quasi-phi-function** adds auxiliary variables, such as a separating plane, so that the constraint becomes Φ'(u_i, u_j, τ) ≥ 0 for some τ. This avoids the radicals and max/min nesting that exact phi-functions need.

**[1] Stoyan, Yu. G., Novozhilova, M. V., & Kartashov, A. V. (1996).** Mathematical model and method of searching for a local extremum for the non-convex oriented polygons allocation problem. *European Journal of Operational Research* 92(1), 193–210. https://iaorifors.com/paper/23651
- Places irregular, fixed-orientation polygons on a strip with defects. The model is continuous-variable only, built on Φ-functions and systems of linear inequalities. A local minimum is found from any feasible start by an exact active-set-type method.
- *Relation to our method:* This is the ancestor of "local optimization = active-set over the currently binding pairwise inequalities". Our constraint generation plus trust-region SLP is a modern version of the same idea, extended to rotations.

**[2] Stoyan, Yu. G., Gil, N. I., Scheithauer, G., Pankratov, A., & Magdalina, I. (2005).** Packing of convex polytopes into a parallelepiped. *Optimization* (Taylor & Francis), pp. 215–235. https://doi.org/10.1080/02331930500050681 (record: TU Dresden FIS). Volume and issue are not shown on the record; it is probably 54(2) **[unverified]**.
- An early 3D phi-function model for packing convex polytopes into a box of minimal height or volume. The abstract was not retrieved, so I could not confirm how orientations are handled **[unverified]**.
- *Relation to our method:* This is the first 3D polytope-in-box optimization model in this line of work and the benchmark source for later quasi-phi papers.

**[3] Stoyan, Yu. G., Romanova, T., & Scheithauer, G. (2005).** Mathematical modeling of interactions of primary geometric 3D objects. *Cybernetics and Systems Analysis* 41(3), 332–342. (TU Dresden FIS record; no DOI listed.)
- Phi-functions for basic 3D objects, including convex polyhedra, cylinders and spheres.

**[4] Bennell, J., Scheithauer, G., Stoyan, Y., & Romanova, T. (2010).** Tools of mathematical modeling of arbitrary object packing problems. *Annals of Operations Research* 179(1), 343–368. https://doi.org/10.1007/s10479-008-0456-5
- A tutorial and review of phi-functions. It covers their relationship to Minkowski sums and no-fit polygons and gives step-by-step derivations, including continuous rotation.
- *Relation to our method:* This is the best single reference for explaining why our separating-hyperplane constraint is a (quasi-)phi-function. It also links the formulation to the no-fit-polytope (Minkowski difference) view: for convex pieces with fixed rotation, the feasible relative placements are the complement of the convex set P_i ⊕ (−P_j).

**[5] Pankratov, A. V., Romanova, T. E., & Chugay, A. M. (2015).** Optimal packing of convex polytopes using quasi-phi-functions. *Problems of Mechanical Engineering* 18(2), 55–64. https://journals.uran.ua/jme/article/view/46687/42874
- Packs convex polytopes into a cuboid of minimal volume, with continuous rotations and optional minimum distances ρ. The quasi-phi-function for two polytopes is a separating plane with auxiliary variables (two normal angles and an offset μ). It is the minimum of the plane's value over the vertices of P_i and the negated value over the vertices of P_j, so it is nonnegative exactly when the plane separates the pieces. Starting points come from homothetic growth of spheres. The local solver is LOFRT-3D (a decomposition that keeps only nearby pairs) running IPOPT. Instances have 7, 12, 25 and 98 polytopes.
- *Relation to our method:* **This is the same constraint system as our SLP.** The differences are that we use a tangent-plane update for the normal instead of spherical angles (which avoids a pole singularity), Cayley rather than Euler rotations, LP steps (HiGHS) inside trust regions instead of a full IPOPT NLP, and exact rational certification. Two things worth borrowing: (a) the "adjusted" quasi-phi-function with a minimum distance ρ > 0, which, used in a final polishing pass, leaves a known slack for rational rounding of the rotations; (b) their sphere-homothety starting points, which are a cheap alternative to soft-to-rigid growth that could seed the archive.

**[6] Stoyan, Y., Romanova, T., Pankratov, A., & Chugay, A. (2015).** Optimized object packings using quasi-phi-functions. In G. Fasano & J. D. Pintér (eds.), *Optimized Packings with Applications*, Springer Optimization and Its Applications, pp. 265–293. https://doi.org/10.1007/978-3-319-18899-7_13
- Introduces quasi-phi-functions for 2D and 3D objects. It formulates packing as an NLP solved through feasible starting points plus smaller subproblems. Examples: ellipses in a minimal rectangle; cuboids, spheres, spherocylinders and spherocones in a minimal-height cuboid.

**[7] Stoyan, Y., Pankratov, A., & Romanova, T. (2016).** Cutting and packing problems for irregular objects with continuous rotations: mathematical modelling and non-linear optimization. *Journal of the Operational Research Society* 67(5), 786–800. https://ideas.repec.org/a/pal/jorsoc/v67y2016i5p786-800.html. The DOI appears to be 10.1057/jors.2015.94 **[unverified; seen only in a mirror URL]**.
- Exact NLP using phi-functions for 2D objects bounded by arcs and line segments, with continuous rotations, in rectangular and circular containers. It is solved as a sequence of NLP subproblems with generated feasible subregions, which reduces the inequality count.

**[8] Romanova, T., Bennell, J., Stoyan, Y., & Pankratov, A. (2018).** Packing of concave polyhedra with continuous rotations using nonlinear optimisation. *European Journal of Operational Research* 268(1), 37–53. https://doi.org/10.1016/j.ejor.2018.01.025
- Arbitrary (possibly concave) polyhedra, written as unions of convex parts, are packed into a cuboid of minimal volume, with continuous rotations and minimum distances. The model is an exact NLP using adjusted, radical-free quasi-phi-functions. It is solved with a fast starting-point algorithm and a compaction procedure that splits the problem into a sequence of smaller NLPs with fewer inequalities.
- *Relation to our method:* This is the flagship 3D paper of the school and the right citation for "continuous-rotation polyhedron packing as NLP with separating planes". Their compaction-by-decomposition plays the role of our trust-region SLP with constraint generation. The convex-decomposition handling would carry over directly if we added non-convex pieces such as Kepler–Poinsot solids.

**[9] Stoian, Y. E., Chugay, A. M., Pankratov, A. V., & Romanova, T. E. (2018).** Two approaches to modeling and solving the packing problem for convex polytopes. *Cybernetics and Systems Analysis* 54(4), 585–593. https://doi.org/10.1007/s10559-018-0059-3
- Compares phi-function and quasi-phi-function NLP models, and the solution strategies tailored to each, for packing convex polytopes into a cuboid of minimal volume with continuous rotations.
- *Relation to our method:* Gives a direct argument for the separating-plane (quasi-phi) form over the exact phi-function, which is the choice we also made.

Also relevant from this school:
- **Stoyan & Chugay (2012)**, "Mathematical modeling of the interaction of non-oriented convex polytopes", *Cybernetics and Systems Analysis* 48, 837–845. Phi-functions for rotatable convex polytopes. **[secondary: reference list of Stoyan & Chugay 2018]**
- **Stoyan & Chugay (2018)**, "Packing convex homothetic polytopes into a cuboid", *J. Mechanical Engineering* 21(2). Uses starting points, fast local search and an exhaustive search over local minima, on 10–500 polytopes. https://journals.uran.ua/jme/article/view/135431/132323
- **Stoyan, Pankratov & Romanova (2016)**, "Quasi-phi-functions and optimal packing of ellipses", *J. Global Optimization* 65, 283–307. https://doi.org/10.1007/s10898-015-0331-2
- **Sofronova, M. S. (2007)**, CSc thesis, "Mathematical modeling of the placement of convex n-dimensional polytopes in an n-dimensional parallelepiped" (supervisor N. I. Gil, IPMash NASU, Kharkiv). It claims the first Φ-functions for n-polytopes. https://uacademic.info/en/document/0407U003084. *This is the only optimization-formulation work I found that treats polytopes in dimension n > 3, which is relevant to our 4D–6D cases.* Whether it allows rotations is unclear **[unverified]**.

---

## 2. Separating hyperplanes, NLP and global MINLP outside the phi-function school

**[10] Berthold, T., Kamp, D., Mexi, G., Pokutta, S., & Pólik, I. (2026).** Out-of-the-box global optimization for packing problems: new models and improved solutions. arXiv:2605.04850. https://arxiv.org/pdf/2605.04850
- Uses off-the-shelf global NLP solvers (SCIP 10.0.0 and FICO Xpress 9.8.0) on circle problems, ellipse problems (an S-lemma model), regular m-gons in regular ℓ-gons, and **Platonic solids in Platonic solids: all 5×5 pairs, n ≤ 30, 750 instances.** Rotations use three ZYX Euler angles. Containment requires every rotated vertex to satisfy each outer face inequality scaled by R. Non-overlap uses Farkas multipliers: for each pair there are 2|F| multipliers λ ≥ 0, one per face of each solid, that sum to 1, whose weighted normals cancel, and whose weighted offsets are ≥ 0. The paper notes that at most three positive multipliers per element and pair are needed. Runs were a 5,000 s multistart followed by a 10,000 s solve. The base model found feasible solutions for 429 of 750 instances. Median gaps are 14.5–33.3%, and **dual bounds improve on the volume bound R_min = (n·V_m/V_ℓ)^{1/3} only for n ≤ 2.** The only Platonic value in the tables is 11 cubes in a cube, R = 2.89445 against Friedman's 2.91210. All other results are in the supplement at github.com/DominikKamp/Packing.
- *Relation to our method:* This attacks the same problem family. By Farkas duality, their multiplier certificate is the dual form of our explicit separating hyperplane: the face multipliers certify that the two systems of face inequalities have no common interior point. Our approach is local but exact-certified, theirs is global but in practice heuristic. Their gaps show no optimality claims are within reach at n ≥ 3. Euler angles give gimbal-lock and nonconvex trigonometric terms; Cayley parameters are polynomial. Their claim that Friedman's page now carries their results is consistent with the project registry. **Note:** for 11 cubes, H. Lin's 2.88295 (July 2026), registered in the project, already beats their 2.89445.

**[11] Peralta, J., Andretta, M., & Oliveira, J. F. (2018).** Solving irregular strip packing problems with free rotations using separation lines. *Pesquisa Operacional* 38(2), 195–214. https://doi.org/10.1590/0101-7438.2018.038.02.0195 (arXiv:1707.07177)
- A 2D NLP in which each pair of convex parts is separated by a line. The line is anchored to a point on one edge of a polygon and has its own rotation angle. Polygons and lines both rotate freely. Every vertex of one piece lies on one side of the line and every vertex of the other on the other side. The model is solved with IPOPT, starting from a bottom-left layout with four orientations. It uses far fewer variables than earlier models.
- *Relation to our method:* This is the 2D twin of our per-pair hyperplane model, from the São Paulo (ICMC-USP) and Porto group, and is probably close to Vinicius's own background. One idea to borrow is anchoring the separator to a face or edge of one piece. In 3D, the separating-axis theorem says a separating normal can always be chosen from the face normals of either piece or the cross products of an edge of each. That gives a finite candidate set for initializing or re-seeding hyperplanes after basin-hopping kicks.

**[12] Cherri, L. H., Cherri, A. C., & Soler, E. M. (2018).** Mixed integer quadratically-constrained programming model to solve the irregular strip packing problem with continuous rotations. *Journal of Global Optimization* 72, 89–107. https://doi.org/10.1007/s10898-018-0638-x
- An MIQCP with a reference point plus a rotation per piece, symmetry-breaking constraints, and exact solution by global solvers. A companion CNMAC 2017 abstract by the same authors uses the title "Mathematical model to the irregular strip packing problem with continuous rotations" (https://proceedings.sbmac.org.br/sbmac/article/view/2000) and uses COUENNE, SCIP and BARON.
- *Relation to our method:* An exact global route for small 2D instances. Its symmetry-breaking constraints (ordering of reference points) are worth adding to any global or MIP experiment on small n.

**[13] Kallrath, J. (2017).** Packing ellipsoids into volume-minimizing rectangular boxes. *Journal of Global Optimization* 67(1), 151–185. https://doi.org/10.1007/s10898-015-0348-6
- Arbitrary orientations, with rotation-matrix entries as variables. **Separating hyperplanes are constructed to keep ellipsoids apart.** Global solvers in GAMS find feasible points for up to 100 ellipsoids; gaps below 10⁻⁴ were reached only for two-ellipsoid cases.
- See also **Kallrath (2009)**, "Cutting circles and polygons from area-minimizing rectangles", *J. Global Optimization* 43(2–3), 299–328, https://doi.org/10.1007/s10898-007-9274-6. Its instances are in MINLPLib (`kall_*`).
- *Relation to our method:* Another separating-hyperplane formulation with full rotations. It confirms that global solvers stall well before n ≈ 10 on such models.

**[14] Birgin, E. G., Lobato, R. D., & Martínez, J. M. (2016).** Packing ellipsoids by nonlinear optimization. *Journal of Global Optimization* 65(4), 709–743. https://doi.org/10.1007/s10898-015-0395-z (preprint: https://www.ime.usp.br/~egbirgin/publications/blmar.pdf)
- Differentiable NLP models for ellipsoids in **n dimensions**. There are two non-overlap models: transformation-based, and **separating-hyperplane-based** (boundary points plus multipliers define a supporting separating hyperplane). There are also containment models for ellipsoids and half-spaces. The method is a multistart with Algencan, an augmented-Lagrangian solver.
- *Relation to our method:* A dimension-independent separating-hyperplane NLP, relevant to our 4D–6D work. Algencan is an alternative local solver if the SLP stalls on degenerate contacts.

**[15] Rocha, P., Rodrigues, R., Gomes, A. M., Toledo, F. M. B., & Andretta, M. (2014).** Circle covering representation for nesting problems with continuous rotations. *Preprints of the 19th IFAC World Congress*, Cape Town, pp. 5235–5240. https://skoge.folk.ntnu.no/prost/proceedings/ifac2014/media/files/1663.pdf
- Pieces are approximated by circles centred on their medial axis. An NLP with continuous rotation is solved with Algencan. Infeasible layouts are repaired by an LP compaction and separation step, which adds up to 3% to the length. A follow-up is Rocha et al., "Constraint aggregation in non-linear programming models for nesting problems", LNEMS (2016), https://doi.org/10.1007/978-3-319-20430-7_22.
- *Relation to our method:* Close in spirit to soft-to-rigid, which also starts from a smooth proxy (our Minkowski-rounded pieces) and then hardens. They report the same need for a final LP repair step.

---

## 3. LP compaction and separation, and MIP models for nesting

**[16] Li, Z., & Milenkovic, V. (1995).** Compaction and separation algorithms for non-convex polygons and their applications. *European Journal of Operational Research* 84(3), 539–561. https://www.iaorifors.com/paper/22061
- A position-based model in which "forces" form a linear objective and locally linearized non-overlap is enforced by LP. Translational compaction was about 100 times faster than physical simulation. Optimal separation of overlapping polygons is NP-complete, but an LP gives an efficient local separation.
- *Relation to our method:* **This is the origin of "LP over positions with locally fixed separating constraints"**, which is exactly our SLP step. Their *separation LP* (minimum total displacement that removes overlaps) could serve as a cheap repair step after basin-hopping kicks, instead of re-running the soft simulation.

**[17] Gomes, A. M., & Oliveira, J. F. (2006).** Solving irregular strip packing problems by hybridising simulated annealing and linear programming. *European Journal of Operational Research* 171(3), 811–829. https://ideas.repec.org/a/eee/ejores/v171y2006i3p811-829.html
- Simulated annealing over placement sequences, combined with LP-based compaction and separation models built on no-fit polygons (the "SAHA" approach).
- *Relation to our method:* The same architecture as our pipeline: a global stochastic search over discrete structure, with an LP local "polish" in which each pair's separating constraint is fixed from the current configuration.

**[18] Imamichi, T., Yagiura, M., & Nagamochi, H. (2007).** An iterated local search algorithm based on nonlinear programming for the irregular strip packing problem. Technical Report 2007-009, Dept. Applied Mathematics & Physics, Kyoto University. https://www.amp.i.kyoto-u.ac.jp/tecrep/abst/2007/2007-009.html. The journal version is believed to be in *Discrete Optimization* (2009) **[unverified]**.
- An NLP that minimizes total overlap (penetration) to separate polygons, plus a move that swaps two polygons into their minimum-overlap positions, all inside an iterated local search.
- *Relation to our method:* Overlap-penalty minimization is the 2D counterpart of our soft phase. The **swap move** (exchange two pieces, then re-minimize overlap) is a cheap perturbation we do not use yet. For congruent pieces it becomes "swap orientation plus position class", which matters for mixed-orientation cube constructions.

**[19] Fischetti, M., & Luzzi, I. (2009).** Mixed-integer programming models for nesting problems. *Journal of Heuristics* 15, 201–226. https://doi.org/10.1007/s10732-008-9088-9
- An MIP for translational nesting. The free region around each pair's no-fit polygon is split into convex slices, with binaries selecting the active slice.
- *Relation to our method:* With rotations fixed, convex pieces separate exactly when the relative position lies outside the convex set P_i ⊕ (−P_j). Choosing *which facet* of that set is active is our hyperplane choice. A Fischetti–Luzzi-style MIP over facet choices would give **globally optimal translations for a fixed set of orientations** at small n. Examples are cubes restricted to axis-aligned and 45°-tilted orientations, the family behind Friedman's 2 + 1/√2 and 2 + 7√2/10 constructions. It could also certify that no better layout exists within such an orientation class.

**[20] Cherri, L. H., Mundim, L. R., Andretta, M., Toledo, F. M. B., Oliveira, J. F., & Carravilla, M. A. (2016).** Robust mixed-integer linear programming models for the irregular strip packing problem. *European Journal of Operational Research* 253(3), 570–583. https://doi.org/10.1016/j.ejor.2016.03.009
- Two MIPs: DTM (direct trigonometry) and NFP-CM (convex decomposition plus no-fit polygons). It is the first MIP variant to allow piece rotations, from a finite set.

**[21] Lastra-Díaz, J. J., & Ortuño, M. T. (2024).** Mixed-integer programming models for irregular strip packing based on vertical slices and feasibility cuts. *European Journal of Operational Research* 313(1), 69–91. https://doi.org/10.1016/j.ejor.2023.08.009 (arXiv:2206.00032)
- The NFP-CM-VS models: a vertical-slice convex decomposition of the feasible relative-placement space, plus valid inequalities and symmetry breaking. They give the first proven optima within one hour for ten instances, up to 27 pieces.
- *Relation to our method:* The current state of the art for exact translational MIPs. It sets realistic expectations: proven optimality reaches roughly 20–30 pieces in 2D with translations only.

**[22] Egeblad, J., Nielsen, B. K., & Odgaard, A. (2007).** Fast neighborhood search for two- and three-dimensional nesting problems. *European Journal of Operational Research* 183(3), 1249–1266. https://doi.org/10.1016/j.ejor.2005.11.063. Also **Egeblad, J., Nielsen, B. K., & Brazil, M. (2009)**, "Translational packing of arbitrary polytopes", *Computational Geometry: Theory and Applications* 42(4), 269–288 **[secondary: reference list in Stoyan & Chugay 2018]**.
- Guided local search that minimizes overlap volume, using *exact one-dimensional translations along coordinate axes*. The 2009 paper extends this to arbitrary polytopes. I believe it covers general dimension d, but did not confirm this from the abstract **[unverified]**.
- *Relation to our method:* Exact 1D minimization of overlap along an axis is a cheap, dimension-independent move for basin hopping, and is useful in 4D–6D. It handles translations only.

**Surveys** (context only):
- **Bennell & Oliveira (2008)**, The geometry of nesting problems: a tutorial. *EJOR* 184(2), 397–415. https://ideas.repec.org/a/eee/ejores/v184y2008i2p397-415.html. Covers no-fit polygons, phi-functions and direct trigonometry.
- **[23] Leao, A. A. S., Toledo, F. M. B., Oliveira, J. F., Carravilla, M. A., & Alvarez-Valdés, R. (2020).** Irregular packing problems: a review of mathematical models. *EJOR* 282(3), 803–822. https://doi.org/10.1016/j.ejor.2019.04.045. Reviews the MIP and NLP models above under a common notation. **This is the single best entry point to "formulate it as an optimization problem".**
- **Wäscher, Haußner & Schumann (2007)**, An improved typology of cutting and packing problems. *EJOR* 183(3), 1109–1130. https://ideas.repec.org/a/eee/ejores/v183y2007i3p1109-1130.html

---

## 4. Dense packings of Platonic and Archimedean solids (physics and discrete geometry)

**[24] Torquato, S., & Jiao, Y. (2009).** Dense packings of the Platonic and Archimedean solids. *Nature* 460, 876–879. https://doi.org/10.1038/nature08239. With the long version: **Torquato & Jiao (2009)**, Dense packings of polyhedra: Platonic and Archimedean solids, *Phys. Rev. E* 80, 041104, https://doi.org/10.1103/PhysRevE.80.041104.
- The **Adaptive Shrinking Cell (ASC)** method: particles plus a deformable periodic cell, with density as the objective. It conjectures that centrally symmetric Platonic and Archimedean solids pack densest as Bravais lattices. Reported densities: octahedra 18/19 ≈ 0.947, dodecahedra (5+√5)/8 ≈ 0.9045, icosahedra ≈ 0.8364. Their tetrahedron value of about 0.823 was later superseded.
- *Relation to our method:* ASC is "shrink the container while particles relax", the same idea as our shrinking container. The infinite-space densities give **large-n asymptotics**: s_C ≈ (n·V_P / (φ·V_C(1)))^{1/3}. This is a heuristic sanity check for our n ≈ 99 results, not a bound.

**[25] Torquato, S., & Jiao, Y. (2010).** Robust algorithm to generate a diverse class of dense disordered and ordered sphere packings via linear programming. *Phys. Rev. E* 82(6), 061302. https://doi.org/10.1103/PhysRevE.82.061302 (arXiv:1008.2747)
- For spheres, the ASC objective and non-overlap constraints linearize exactly, so ASC is solved by **sequential linear programming**. The variables are particle displacements and a symmetric strain of the cell. Only pairs inside an "influence sphere" are constrained. Runs cover dimensions 2–6.
- *Relation to our method:* **The closest SLP analogue in physics.** Their influence-sphere cutoff is our near-pair constraint generation, and their cell strain is our container-size variable. They also find that the cutoff radius controls how far a step can move (disorder versus density), which matches our trust-region tuning.

**[26] Haji-Akbari, A., Engel, M., Keys, A. S., Zheng, X., Petschek, R. G., Palffy-Muhoray, P., & Glotzer, S. C. (2009).** Disordered, quasicrystalline and crystalline phases of densely packed tetrahedra. *Nature* 462, 773–777. https://doi.org/10.1038/nature08641
- Thermodynamic (Monte Carlo) compression of hard tetrahedra. They form a dodecagonal quasicrystal (φ = 0.8324 after compression), and an 82-tetrahedron periodic approximant reaches 0.8503 (value from Wikipedia).

**[27] Kallus, Y., Elser, V., & Gravel, S. (2010).** Dense periodic packings of tetrahedra with small repeating units. *Discrete & Computational Geometry* 44(2), 245–252. https://doi.org/10.1007/s00454-010-9254-3
- A 4-tetrahedron unit cell with φ = 100/117 ≈ 0.8547.

**[28] Chen, E. R., Engel, M., & Glotzer, S. C. (2010).** Dense crystalline dimer packings of regular tetrahedra. *Discrete & Computational Geometry* 44(2), 253–280. https://doi.org/10.1007/s00454-010-9273-0 (arXiv:1001.0586) **[secondary: Wikipedia reference list]**
- A dimer-based family with φ = 4000/4671 ≈ 0.856347, the densest known tetrahedron packing. Torquato & Jiao's analytic 6-parameter family (arXiv:1005.0011) reaches the same value.

**[29] Gravel, S., & Elser, V. (2008).** Divide and concur: a general approach to constraint satisfaction. *Phys. Rev. E* 78(3), 036706. https://doi.org/10.1103/PhysRevE.78.036706. With **Kallus, Y., Elser, V., & Gravel, S. (2010)**, Method for dense packing discovery, *Phys. Rev. E* 82(5), 056707, https://doi.org/10.1103/PhysRevE.82.056707.
- Divide and concur (D&C) gives each pairwise non-overlap constraint its own replica variables, enforces "concur" (replicas agree) as a second constraint, and iterates the **difference map** between the two projections. The periodic version adds cell vectors to the search. Polytopes are handled through their vertices plus a rigidity constraint. Results include lattice sphere packings up to 14D and a **4-simplex packing with φ = 128/219 ≈ 0.5845**.
- *Relation to our method:* A different global search that is projection-based and does not use gradients. The per-pair projection is "nearest non-overlapping pair", which is closely related to our separating-plane update. It is a candidate replacement for basin hopping when the archive stagnates. The 4-simplex result is the natural infinite-space reference for our **5-cell** cases.

Also relevant:
- **Gravel, Elser & Kallus (2011)**, Upper bound on the packing density of regular tetrahedra and octahedra. *DCG* 46(4), 799–818, https://doi.org/10.1007/s00454-010-9304-x **[secondary: Wikipedia]**. Bounds the tetrahedron density below 1 by only about 2.6×10⁻²⁵, which shows that density upper bounds are useless as container lower bounds.
- **Lagarias, J. C., & Zong, C. (2012)**, Mysteries in packing regular tetrahedra. *Notices of the AMS*, December 2012 (vol. 59, no. 11, starting p. 1540, inferred from the PDF URL https://www.ams.org/notices/201211/rtx121101540p.pdf **[secondary; page range unverified]**). Historical and expository; won the 2015 Conant Prize.
- **Chen, E. R., Klotsa, D., Engel, M., Damasceno, P. F., & Glotzer, S. C. (2014)**, Complexity in surfaces of densest packings for families of polyhedra. *Phys. Rev. X* 4(1), 011024, https://doi.org/10.1103/PhysRevX.4.011024. Gives densest packings across families that interpolate between Platonic, Archimedean and Catalan solids (more than 55,000 shapes). *This is the infinite-space reference for our Archimedean and Catalan families.*
- **Teich, E. G., van Anders, G., Klotsa, D., Dshemuchadse, J., & Glotzer, S. C. (2016)**, Clusters of polyhedra in spherical confinement. *PNAS* 113(6) **[secondary: Wikipedia "Packing problems"; DOI not verified]**. Dense clusters of up to 60 Platonic solids in a **spherical container** (from the AIChE 2016 abstract). *This is the only finite-container Platonic-solid study from physics that I found. A sphere container would be a natural addition to our container list, with published comparison values.*

---

## 5. Certification and rigorous verification

**[30] Markót, M. Cs., & Csendes, T. (2005).** A new verified optimization technique for the "packing circles in a unit square" problems. *SIAM Journal on Optimization* 16(1), 193–219. https://doi.org/10.1137/S1052623403425617 (authors confirmed from the reference list of their 2006 paper)
- Interval branch-and-bound with an interval version of an elimination procedure. The remaining regions are represented as reliably computed polygons. It **proves optimality for n = 28, 29, 30** circles in a square.
- Follow-ups: **Markót & Csendes (2006)**, A reliable area reduction technique for solving circle packing problems, *Computing* 77, 147–162, https://doi.org/10.1007/s00607-005-0155-x. **Markót (2021)**, Improved interval methods for solving circle packing problems in the unit square, *J. Global Optimization* 81(3), 773–803, https://doi.org/10.1007/s10898-021-01086-z, which proves **n = 31, 32, 33** with 13–61 CPU hours each.
- *Relation to our method:* We certify *feasibility* exactly, using rational rotations, rational hyperplanes, and arithmetic in Q(√2,√3,√5,√7). These papers show what *optimality* certification costs even for 2D circles: n ≈ 30 is the frontier. For our problems, interval B&B could plausibly prove only tiny cases, such as whether 9 or 10 cubes need s = 2 + 1/√2, or the 2D square analogues.

**[31] Abrahamsen, M., Miltzow, T., & Seiferth, N. (2020).** Framework for ∃ℝ-completeness of two-dimensional packing problems. *Proc. 61st IEEE FOCS*, 1014–1021. https://doi.org/10.1109/FOCS46700.2020.00098 (arXiv:2004.07558)
- Many 2D packing variants are ∃ℝ-complete, both with translations only and with **arbitrary rigid motions** (translations plus rotations). Theorem 21 (arXiv v3) states that for algebraic extensions F₁ ⊊ F₂ of ℚ, there are instances that have a solution over F₂ but none over F₁. With translations only and polygonal pieces, some variants are in NP.
- *Relation to our method:* This is the theoretical reason exact optimal packings cannot in general be certified in a fixed field such as Q(√2,√3,√5,√7). It supports our approach of certifying a slightly relaxed packing (positive slack, rounded to rationals) and treating optimality claims separately.

---

## 6. Benchmarks we can compare against

### 6a. Sources and conventions

| Source | Coverage (piece, container, n) | Size convention | Notes |
|---|---|---|---|
| **E. Friedman, Erich's Packing Center**: "Cubes in Cubes" (`.../packing/cubincub/`) and "Octahedra in Cubes" (`.../packing/octincub/`) at https://erich-friedman.github.io/packing/ | Cubes in a cube, n = 2–33; octahedra in a cube, n = 2–30 (contributors include E. Friedman 1998, R. Walsh June 2026, H. Lin July 2026) | **s = container edge / piece edge** | I could **not re-fetch** the site (permission prompt timed out). The values in 6b are those already registered in the project (`docs/external_records.json`, checked 2026-10-13). The project audit says these are the only two of the nine Platonic-cube/octahedron problems with catalogue values. |
| **Berthold, Kamp, Mexi, Pokutta & Pólik 2026** [10] (supplement: github.com/DominikKamp/Packing) | All 25 ordered Platonic pairs, n ≤ 30 (750 instances; feasible solutions for 429 in the base model) | **Inner pieces have unit circumradius; the objective is the outer circumradius R.** Convert to edge ratio with s = R·ρ_P/ρ_C, where ρ = circumradius/edge: tet 0.612372, oct 0.707107, cube 0.866025, ico 0.951057, dod 1.401259. For same-type pairs s = R. | The paper table gives only one 3D value: 11 cubes in a cube, R = s = 2.89445 (previous 2.91210, Friedman). The supplement was not fetched here (permission timeout); the project has already imported 724 cases. |
| **Friedman, "Packing unit squares in squares: a survey and new results"**, *Electronic J. Combinatorics* Dynamic Survey DS7 (version of 14 Aug 2009; 2023 corrigendum). https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS7 | 2D analogue: n unit squares in a square, n ≤ 100, with rotations | s(n) = container side / unit square side | Optimal for n = 2, 3, 5, 6, 7, 8, 10, 14, 15, 24, 35 and squares. Useful as a 2D test bed for the SLP and certification code. |
| Infinite-space densest known packings [24, 26–28, 29] | φ_max for tet 4000/4671 ≈ 0.8563, oct 18/19 ≈ 0.9474, dod (5+√5)/8 ≈ 0.9045, ico ≈ 0.8364, 4-simplex ≥ 128/219 ≈ 0.5845 (lattice) | density | Only for **heuristic large-n asymptotics**, s ≈ (n·V_P/(φ·V_C(1)))^{1/3}; not a bound. |
| Teich et al. 2016 (PNAS) | Platonic solids in a sphere, up to about 60 | sphere radius (convention not checked) | Possible new container class; values not extracted. |
| Hypercubes in hypercubes; 4D–6D regular polytopes in containers | — | — | **No published finite-container table found.** Beyond trivial grids (s = k for n ≤ k^d), our 4D–6D values appear to be first results. The only related optimization formulation found is Sofronova's (2007) n-dimensional Φ-function thesis. |

### 6b. Registered catalogue values (from the project registry; container edge / piece edge)

**Cubes in a cube**

| n | s | Source as registered |
|---|---|---|
| 2–8 | 2 | trivial 2×2×2 grid |
| 9, 10 | 2 + 1/√2 ≈ 2.70711 | E. Friedman 1998 |
| 11 | 2.88295 | H. Lin, July 2026 (on Friedman's page). Earlier values: 2.91210 (Friedman 1998, per [10]); 2.89445 (Berthold et al., May 2026). The registry also lists a 2.88172 tightening by S. Scott (coordinates only). |
| 12 | 2.93277 | H. Lin, July 2026 (Friedman's page). Y. Nakajima's soft-to-rigid gives 2.93152 (Oct 2026). |
| 13 | 2.956+ | E. Friedman 1998 (three decimals shown) |
| 14 | 2 + 7√2/10 ≈ 2.98995 | E. Friedman 1998 |
| 15–27 | 3 | trivial 3×3×3 grid |
| 28–33 | 3 + 1/√2 ≈ 3.70711 | E. Friedman 1998. Coordinate witnesses (not catalogue values) exist for n = 28 (3.66600, konoha-ily2) and n = 34–36 (Ryan Xu: 3.82288, 3.86069, 3.89443). |

**Octahedra in a cube** (catalogue values with 5 decimals)

| n | s | n | s | n | s |
|---|---|---|---|---|---|
| 2 | √2 ≈ 1.41421 (Walsh) | 12 | 2.25949 (Lin) | 22 | 2.60591 (Walsh) |
| 3 | 1.63299 (Walsh) | 13 | 2.33667 (Lin) | 23 | 2.61533 (Walsh) |
| 4 | 1.64991 (Walsh) | 14 | 2.35702 (Walsh) | 24 | 2.63319 (Lin; tightened 2.62793) |
| 5 | 1.75782 (Walsh) | 15 | 2.41976 (Walsh) | 25 | 2.63622 (Walsh) |
| 6 | 1.76776 (Walsh) | 16 | 2.46211 (Walsh) | 26 | 2.63986 (Walsh) |
| 7 | 1.79133 (Walsh) | 17 | 2.47487 (Lin) | 27 | 2.63986 (Walsh) |
| 8 | 1.79133 (Walsh) | 18 | 2.48257 (Walsh) | 28 | 2.75738 (Walsh) |
| 9 | 1.88561 (Walsh) | 19 | 2.52683 (Walsh) | 29 | 2.85384 (Walsh) |
| 10 | 2.14936 (Walsh) | 20 | 2.57792 (Walsh) | 30 | 2.89186 (Walsh) |
| 11 | 2.19540 (Walsh) | 21 | 2.59285 (Lin; tightened 2.59119) | | |

**Squares in a square (2D analogue, DS7 2009 version):** s(1) = 1; s(2–4) = 2; s(5) = 2 + 1/√2 ≈ 2.7071 (optimal); s(6–9) = 3 (optimal); s(10) = 3 + 1/√2 ≈ 3.7071 (optimal, Stromquist); s(11) ≤ 3.8771; s(12), s(13) ≤ 4; s(14–16) = 4 (optimal); s(17) ≤ 4.6756; s(18) ≤ (7+√7)/2 ≈ 4.8229; s(19) ≤ 3 + 4√2/3 ≈ 4.8857; s(20) ≤ 5. Later improvements may appear on Friedman's web page; not checked. The 2D pattern "k + 1/√2 for one more than a perfect square" corresponds to the 3D cube values for n = 9, 10 and 28–33.

---

## 7. Likely matches for Vinicius's Zotero titles

| Truncated title | Most likely paper | Confidence |
|---|---|---|
| "...for the non-convex oriented polygons allocation problem" | Stoyan, Novozhilova & Kartashov (1996), "Mathematical model and method of searching for a local extremum for the non-convex oriented polygons allocation problem", *EJOR* 92(1), 193–210 [1] | **High** (exact phrase) |
| "...the irregular strip packing problem with continuous rotations" | Cherri, Cherri & Soler (2018), "Mixed integer quadratically-constrained programming model to solve the irregular strip packing problem with continuous rotations", *J. Global Optim.* 72, 89–107 [12]. Same authors' CNMAC 2017 abstract "Mathematical model to the irregular strip packing problem with continuous rotations" also fits. | **High** that it is one of these two; JOGO more likely |
| "...and Improved Solutions" | Berthold, Kamp, Mexi, Pokutta & Pólik (2026), "Out-of-the-Box Global Optimization for Packing Problems: New Models and Improved Solutions", arXiv:2605.04850 [10] | **High** (exact suffix and on-topic; recent) |
| "...and Linear Programming" | Gomes & Oliveira (2006), "Solving irregular strip packing problems by hybridising simulated annealing and linear programming", *EJOR* 171(3) [17] | **Medium.** Fits the suffix and the nesting cluster. Torquato & Jiao (2010) "...via Linear Programming" [25] does not fit "and". |
| "...lar optimization" | **Not identified.** No packing paper with a "-lar optimization" ending turned up. If the truncation actually hides "...near optimization"/"...nonlinear optimisation", the best candidates are Romanova et al. (2018) "...using nonlinear optimisation" [8] and Birgin, Lobato & Martínez (2016) "Packing ellipsoids by nonlinear optimization" [14]. | Low |
| "...and Packing Problems" | **Not identified.** Plausible: Wäscher, Haußner & Schumann (2007), "An improved typology of cutting and packing problems", *EJOR* 183(3); or Dyckhoff (1990), "A typology of cutting and packing problems" (not checked). | Low |
| "multi-time packing schedules" | **Not identified.** Several searches found no packing or nesting paper with this phrase. It may come from scheduling or "time-dependent packing" work rather than geometric packing. | — |

The quickest way to settle the unidentified ones is to ask Vinicius for the full titles or DOIs.

---

## 8. Short list of things to borrow (prioritized)

1. **Positioning:** describe our local optimizer as "SLP on the quasi-phi-function (separating-plane) model of Pankratov–Romanova–Stoyan [5, 8, 9]", following Li–Milenkovic-style LP compaction [16] and Torquato–Jiao SLP [25]. The new parts are exact certification, soft-to-rigid initialization, and dimensions 4–6.
2. **Slack for certification:** add a final pass with the "adjusted" quasi-phi minimum distance ρ > 0 [5, 8], i.e. require a gap of at least ε. This turns rational rounding of the Cayley parameters and hyperplanes into a guaranteed-feasible step.
3. **Repair after perturbation:** use a Li–Milenkovic separation LP (minimal displacement to remove overlaps) [16], or the Imamichi overlap-NLP with swap moves [18], as a cheap repair inside basin hopping.
4. **Hyperplane seeding:** pick initial separating normals from the separating-axis candidate set (face normals of either piece and edge×edge cross products), in the spirit of Peralta et al.'s anchored separation lines [11].
5. **Exact optima within an orientation class:** fix orientations and solve a Fischetti–Luzzi / NFP-CM style MIP over Minkowski-difference facets [19–21] for small n. This gives proven-optimal translations within that class.
6. **Compare and report:** compare all 25 Platonic pairs against [10] after converting with s = R·ρ_P/ρ_C. State that no optimality claims exist in the literature for n ≥ 3 apart from trivial grid cases, and that interval B&B optimality proofs [30] top out at about 30 circles in 2D.
7. **Extensions with external comparison values:** spherical containers (Teich et al. 2016), and the 2D squares-in-square analogue (DS7) as a regression test.

---

## Sources (pages actually consulted)

- Stoyan, Novozhilova & Kartashov 1996: https://iaorifors.com/paper/23651
- Stoyan, Gil, Scheithauer, Pankratov & Magdalina 2005: https://fis.tu-dresden.de/portal/en/publications/packing-of-convex-polytopes-into-a-parallelepiped(0b482946-19cf-43bb-a269-7ac7570f6ca6).html
- Stoyan, Romanova & Scheithauer 2005: https://fis.tu-dresden.de/portal/en/publications/mathematical-modeling-of-interactions-of-primary-geometric-3d-objects(fb9283df-c94d-4722-b023-49b95fccf7fa).html
- Bennell, Scheithauer, Stoyan & Romanova 2010: https://ideas.repec.org/a/spr/annopr/v179y2010i1p343-36810.1007-s10479-008-0456-5.html
- Pankratov, Romanova & Chugay 2015: https://journals.uran.ua/jme/article/view/46687/42874
- Stoyan, Romanova, Pankratov & Chugay 2015 (chapter): https://ideas.repec.org/h/spr/spochp/978-3-319-18899-7_13.html
- Stoyan, Pankratov & Romanova 2016 (JORS): https://ideas.repec.org/a/pal/jorsoc/v67y2016i5p786-800.html
- Stoyan, Pankratov & Romanova 2016 (JOGO, ellipses): https://unpaywall.org/10.1007%2FS10898-015-0331-2
- Romanova, Bennell, Stoyan & Pankratov 2018: https://ideas.repec.org/a/eee/ejores/v268y2018i1p37-53.html
- Stoian, Chugay, Pankratov & Romanova 2018: https://link.springer.com/article/10.1007/s10559-018-0059-3
- Stoyan & Chugay 2018 (and its reference list): https://journals.uran.ua/jme/article/view/135431/132323
- Sofronova 2007 thesis: https://uacademic.info/en/document/0407U003084
- Berthold, Kamp, Mexi, Pokutta & Pólik 2026: https://arxiv.org/pdf/2605.04850
- Peralta, Andretta & Oliveira 2018: https://www.scielo.br/j/pope/a/RcXzqWKwBnL7QhcgkgNyZPv/?lang=en
- Cherri, Cherri & Soler 2018 (JOGO): https://link.springer.com/10.1007/s10898-018-0638-x ; CNMAC abstract: https://proceedings.sbmac.org.br/sbmac/article/view/2000
- Kallrath 2017: https://ideas.repec.org/a/spr/jglopt/v67y2017i1d10.1007_s10898-015-0348-6.html ; Kallrath 2009: https://www.minlplib.org/kall_circlespolygons_c1p12.html
- Birgin, Lobato & Martínez 2016: https://repositorio.usp.br/item/002737473 ; preprint https://www.ime.usp.br/~egbirgin/publications/blmar.pdf
- Rocha et al. 2014: https://skoge.folk.ntnu.no/prost/proceedings/ifac2014/media/files/1663.pdf ; Rocha et al. 2016: https://repositorio.usp.br/item/002762829
- Li & Milenkovic 1995: https://www.iaorifors.com/paper/22061
- Gomes & Oliveira 2006: https://ideas.repec.org/a/eee/ejores/v171y2006i3p811-829.html
- Imamichi, Yagiura & Nagamochi 2007: https://www.amp.i.kyoto-u.ac.jp/tecrep/abst/2007/2007-009.html
- Fischetti & Luzzi 2009: https://unpaywall.org/10.1007%2FS10732-008-9088-9
- Cherri et al. 2016: https://ideas.repec.org/a/eee/ejores/v253y2016i3p570-583.html
- Lastra-Díaz & Ortuño 2024: https://docta.ucm.es/entities/publication/1c16e6ce-7737-4b8f-84eb-f2a30f505331/full ; arXiv https://arxiv.org/abs/2206.00032v1
- Egeblad, Nielsen & Odgaard 2007: https://ideas.repec.org/a/eee/ejores/v183y2007i3p1249-1266.html ; https://hjemmesider.diku.dk/~benny/publications/sort_date.html
- Bennell & Oliveira 2008: https://ideas.repec.org/a/eee/ejores/v184y2008i2p397-415.html
- Leao et al. 2020: https://ideas.repec.org/a/eee/ejores/v282y2020i3p803-822.html
- Wäscher, Haußner & Schumann 2007: https://ideas.repec.org/a/eee/ejores/v183y2007i3p1109-1130.html
- Torquato & Jiao 2009 (Nature): https://ideas.repec.org/a/nat/nature/v460y2009i7257d10.1038_nature08239.html ; PRE 2009: https://arxiv.org/abs/0909.0940 ; 4-particle family: https://ar5iv.arxiv.org/html/1005.0011
- Torquato & Jiao 2010 (SLP): https://ar5iv.arxiv.org/html/1008.2747 ; https://collaborate.princeton.edu/en/publications/robust-algorithm-to-generate-a-diverse-class-of-dense-disordered-/
- Haji-Akbari et al. 2009: https://ideas.repec.org/a/nat/nature/v462y2009i7274d10.1038_nature08641.html
- Kallus, Elser & Gravel 2010 (DCG): https://www.lassp.cornell.edu/bibcite/reference/2373 ; Method for dense packing discovery: https://www.lassp.cornell.edu/bibcite/reference/2369 and https://ar5iv.arxiv.org/html/1003.3301
- Gravel & Elser 2008: https://www.lassp.cornell.edu/bibcite/reference/2378 ; https://ar5iv.arxiv.org/html/0801.0222
- Tetrahedron packing (Chen–Engel–Glotzer, Gravel–Elser–Kallus, Lagarias–Zong citations): https://en.wikipedia.org/wiki/Tetrahedron_packing
- Lagarias & Zong prize note: https://www.cms.org.cn/home/news/news_details/id/743.html
- Chen, Klotsa, Engel, Damasceno & Glotzer 2014: https://doaj.org/article/230b91da8f2f45afb1afa26426a81c65
- Teich et al. 2016: https://proceedings.aiche.org/conferences/aiche-annual-meeting/2016/proceeding/paper/678h-clusters-polyhedra-spherical-confinement ; citation via https://en.wikipedia.org/wiki/Packing_problems
- Markót & Csendes 2005: https://searchworks.jioinstitute.edu.in/articles/asx__18491379 ; authors via https://www.inf.u-szeged.hu/~csendes/intpoly.pdf ; Markót & Csendes 2006: https://unpaywall.org/10.1007%2FS00607-005-0155-X ; Markót 2021: https://ideas.repec.org/a/spr/jglopt/v81y2021i3d10.1007_s10898-021-01086-z.html
- Abrahamsen, Miltzow & Seiferth 2020: https://researchprofiles.ku.dk/en/publications/framework-for-er-completeness-of-two-dimensional-packing-problems/ ; https://arxiv.org/html/2004.07558v3
- Friedman DS7: https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS7 ; https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS7/html_1
- Project registry (benchmark values in 6b): `docs/external_records.json`, `docs/references.json`

**Blocked or not retrieved** (permission prompt timed out or robots.txt), so not used directly: https://erich-friedman.github.io/packing/ ; https://github.com/DominikKamp/Packing ; https://www.ams.org/notices/201211/rtx121101540p.pdf ; https://arxiv.org/abs/1003.3301 ; https://arxiv.org/abs/0801.0222 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC8550790 ; https://epubs.siam.org/doi/10.1137/S1052623403425617 (robots). arXiv:2609.26627 ("Dense packing of tetrahedra in cylinders") came back as an empty PDF, so its content is unknown.
