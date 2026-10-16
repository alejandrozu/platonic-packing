# Lean connections to materials models

This supplement connects exact finite packing certificates to two mathematical ingredients used in materials modelling: **a positive-volume region of allowed translations** and **a finite motif that repeats periodically without overlaps**. It formalizes sufficient geometric conditions. It does not formalize an experimental paper's conclusions, alloy energetics or a theory of crystallization.

The physical motivation and primary bibliography are in the [materials-science guide](https://polyhedrainpolyhedra.wiki/materials/) and its [source audit](MATERIALS_SCIENCE.md). The [existing generalization manuscript](research-2026-10-16-generalization/manuscript.pdf) includes the motivation and mathematical statements. This is a documented software and proof supplement, not a separate paper.

## From an exact witness to a region of feasible motion

A single valid arrangement specifies one point in configuration space. Materials models also ask how much nearby motion is possible. The relevant distinction is between finding one nonoverlapping pose and exhibiting a region in which many particles may move simultaneously.

Keep the original orientations fixed. Let there be $n$ labelled particles in dimension $d$, and write $t_{iq}$ for coordinate $q$ of particle $i$'s translation. For a positive tolerance $\varepsilon$, consider

$$B_\varepsilon=\{t:\ |t_{iq}|\leq\varepsilon\text{ for every }i,q\}.$$

The [clearance development](research-2026-10-16-generalization/formal/PackingCertificates/Extensions/Clearance.lean) supplies the error budgets. For a wall with normal $a_f$ and available slack $\delta_f$, require

$$\varepsilon\|a_f\|_1\leq\delta_f.$$

For each separating plane with normal $u_{ij}$ and gap $g_{ij}$, require

$$2\varepsilon\|u_{ij}\|_1<g_{ij}.$$

The factor two permits both particles to move towards one another. The sum of absolute normal coordinates is essential: signed components cannot cancel in a worst-case error bound. Each translated vertex moves by at most $\varepsilon$ in each coordinate, so the earlier theorem preserves containment and separation of the complete convex hulls. Pure translations also preserve each particle's shape and distances.

The new [FreeVolume.lean](research-2026-10-16-generalization/formal/PackingCertificates/Extensions/FreeVolume.lean) uses finite linear inequalities to define a measurable certified translation region. It contains $B_\varepsilon$ and is contained in the region of feasible whole-body arrangements. Product Lebesgue measure gives the exact box volume

$$\operatorname{Leb}(B_\varepsilon)=(2\varepsilon)^{nd}.$$

Thus a certificate satisfying the positive-clearance budgets provides a measurable feasible region of at least this volume. This is a lower bound on **labelled, fixed-orientation translational configuration volume** in the stated coordinate units. It is not merely a count of accepted sampled configurations.

A concrete regression checks two intervals, $[-2,-1]$ and $[1,2]$, inside $[-3,3]$. Each may translate independently by at most $1/4$. Explicit signed wall inequalities and both orders of the separating plane are checked in Lean, proving a measurable feasible region with volume at least $1/4>0$.

### Why simultaneous translations matter

[Haji-Akbari, Engel and Glotzer (2011), Section II.D](https://doi.org/10.1063/1.3651370) define single-particle free volume while holding the other particles fixed. They explicitly identify the product of independently computed single-particle volumes as a mean-field approximation. Collective motion contributes additional entropy in their tetrahedral phase study.

The certified box takes a different route: **every combination** of its allowed particle translations is safe. Its product volume is therefore the exact volume of a proven feasible subset, without assuming that the full configuration region factorizes. The bound can be conservative; correlated motion outside the box is not counted.

[van Anders et al. (2014), Section II](https://doi.org/10.1073/pnas.1418159111) write the configurational integral over both positions and orientations. Our orientations are fixed. For particles with nontrivial continuously variable orientations, as for 3D polyhedra, fixing all orientations selects a measure-zero slice of the unrestricted rotational space. Positive translational volume alone therefore does **not** give a positive bound for the full position-and-orientation partition function. Integrating a rotational neighbourhood, indistinguishability factors, momentum contributions and thermal normalization are separate tasks. No complete entropy, free-energy ranking or assembly probability is claimed here.

### When positivity cannot be inferred

An exactly fitting body can be feasible while having no translational freedom. The module includes a one-dimensional exact-fit regression: an interval confined to an identical interval has only the zero translation available, a set of Lebesgue measure zero. A feasible witness alone is therefore insufficient for a positive-volume conclusion. Uniform positive error budgets need sufficient wall slack as well as pair separation. We have not computed numerical free-volume bounds for all 532 catalogue witnesses.

## From a finite motif to a periodic packing

A crystal model commonly describes a finite motif and its lattice translations. [Torquato and Jiao (2009), Section I](https://doi.org/10.1103/PhysRevE.80.041104) distinguish lattice packings from periodic packings with multi-particle motifs. A periodic motif may contain several orientations; periodicity does not require every particle to have the same orientation.

Let the cell widths satisfy $L_q>0$ and define the open rectangular cell

$$F=\prod_{q=1}^d(0,L_q),\qquad \lambda(z)_q=L_qz_q,\quad z\in\mathbb Z^d.$$

Suppose every complete motif body $P_i$ lies in $F$ and the motif bodies are pairwise disjoint. The [PeriodicMotif.lean](research-2026-10-16-generalization/formal/PackingCertificates/Extensions/PeriodicMotif.lean) development proves that

$$\{P_i+\lambda(z): i\in\{1,\ldots,n\},\ z\in\mathbb Z^d\}$$

is pairwise disjoint and invariant as a family under each lattice translation. This is a genuine global packing conclusion, quantifying over every pair of integer cells.

Within a cell, the existing finite certificate proves separation. Across distinct cells, some integer coordinate differs by at least one. The corresponding translated open coordinate intervals are disjoint, separating the complete bodies. A certificate and strict finite vertex bounds provide an inspectable sufficient route to the cell-containment hypothesis; the proof concerns the full convex hulls, not just isolated vertices.

The development also transports the packing through an injective real-linear map, yielding lattice translates in a transformed cell. A general shear or anisotropic map can change particle shape: the conclusion concerns the transformed bodies. An isometry guarantees congruence to the original solids, and a common similarity preserves their shapes up to common scale. Injective linearity alone guarantees neither.

### What the periodic theorem does not assert

- The whole-body open-cell condition is sufficient and deliberately restrictive. General periodic packings may cross cell faces and then need checks against periodic images.
- A polyhedral catalogue container need not tile space. Enclosing a motif in a rectangular cell can introduce additional empty volume, so its original finite-container density is not automatically a periodic density.
- Periodicity and nonoverlap do not prove energetic or thermodynamic stability, assembly kinetics, force balance or a material property.
- This theorem does not automatically periodize every live construction or identify it with a named crystal structure.

## Relationship to established materials research

These are classical geometric and measure-theoretic ideas implemented within this project's Lean certificate framework. The contribution is a machine-checked implication from explicit certificate conditions to a safe configuration region or a repeatable motif; it is not a claim to have discovered free volume or periodic-cell modelling.

Finite-cluster studies such as [Teich et al. (2016)](https://doi.org/10.1073/pnas.1524875113) motivate examining boundary-compatible layers and particle counts. [Henzie et al. (2012)](https://doi.org/10.1038/nmat3178) demonstrate experimentally that faceted nanocrystals assemble into superstructures and that interactions can select different arrangements. [Cersonsky et al. (2018)](https://doi.org/10.1073/pnas.1720139115) establish why densest packing cannot replace thermodynamic assembly calculations. Our formal conclusions supply geometric inputs to such models, rather than verify those empirical results.

The distinction is especially important for alloys and conventional polycrystalline solids. The grains of a dense polycrystalline solid form a space-filling microstructure that evolves during coarsening, and boundary energies depend on atomic structure. [MacPherson and Srolovitz (2007)](https://doi.org/10.1038/nature05745) concern capillarity-driven coarsening; [Olmsted, Foiles and Holm (2009)](https://doi.org/10.1016/j.actamat.2009.04.007) concern atomistic boundary energies. Neither process follows from a rigid-particle nonoverlap certificate. Formalizing those theories would require additional definitions and physical assumptions.

## Inspecting and reproducing the proofs

The modules use the existing pinned Lean 4.31.0/mathlib project. The [combined build receipt](research-2026-10-16-generalization/formal/extension-materials-verification.json) records two successful compilation stages and 37 named axiom audits. Nine named regression groups cover positive examples and the boundary conditions that invalidate stronger conclusions. Source hashes, import dependencies, compiler logs and printed theorem axioms are retained in the formal supplement. The [formal guide](research-2026-10-16-generalization/formal/README.md) identifies the exact theorem names and reproduction commands.

The catalogue evidence remains **532 selected witnesses across 140 frozen families**. These generic implications add no catalogue records and make no claim that all live configurations have been formally imported or assigned a positive motion budget.
