# Lean formalization: geometric soundness of convex-packing certificates

This is the formal companion to the generalization paper. It formalizes the
dimension-independent geometric core and includes one fully instantiated exact
witness. It is intentionally narrower than formal verification of the entire
search implementation or of the live catalogue.

## Reproduce

The project pins Lean **4.31.0** and mathlib commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.
With [elan](https://github.com/leanprover/elan) installed, run in this directory:

```sh
lake update
lake exe cache get
lake build
lake env lean Audit.lean
```

`Audit.lean` prints each theorem's axioms. The sources contain no `sorry`,
`admit`, additional axioms, or `native_decide`. Ordinary mathlib dependencies
may use Lean's standard logical axioms (`propext`, `Classical.choice`, and
`Quot.sound`); these are reported in the audit, rather than hidden.

## Proven statements

All names below are in namespace `PackingCertificates`.

| Name | Kernel-checked mathematical statement |
|---|---|
| `hull_le_of_vertices_le`, `hull_ge_of_vertices_ge` | A linear inequality on a vertex set extends to its real convex hull. |
| `vertex_tests_imply_containment` | Finite vertex/face tests imply containment of the entire convex hull in the container's halfspaces. |
| `separating_vertex_tests_imply_disjoint` | Vertex projection bounds with a strictly positive gap imply disjoint closed convex hulls. |
| `finite_certificate_sound` | Finite wall and pair certificates imply full-body containment and pairwise disjointness; pieces can have different vertex counts. |
| `affine_placement_of_vertex_body` | Affine images commute with the convex-hull vertex representation. |
| `placed_outer_approximation` | Inclusion of a body in an outer approximation is preserved by placement. |
| `minkowskiOpening_subset` | `(P ⊖ K) ⊕ K ⊆ P` for arbitrary sets and structuring bodies. Choosing `K` as a ball gives rounded-body opening containment. |
| `minkowskiOpening_mono` | Body inclusion `P ⊆ Q` implies inclusion of their openings by the same `K`. This is not a monotonicity theorem in the radius. |
| `convex_blend_subset` | For convex `P` and `Q ⊆ P`, `a P + b Q ⊆ P` when `a,b ≥ 0` and `a+b=1`; apply to `Q=ρ B`, `a=1−τ`, `b=τ`. |
| `transported_packing` | An injective placement and a containing outer body transport a packing to another container. |
| `subpacking_sound` | Replacing each piece by a subset preserves containment and separation. |
| `nested_packing_sound` | Disjoint child packings inside disjoint parent pieces give a single packing indexed by parent/child pairs. |
| `Example.two_cube_certificate`, `Example.two_cube_packing` | Exact finite tests and geometric soundness for two unit cubes in a side-5/2 cube with a positive gap. |

The core works in any real vector space. Substituting `Fin d → ℝ` gives every
finite dimension, including the 3D–6D catalogue families.

## Scope and trust boundary

- The formal denotation of a supplied vertex list is its **real convex hull**.
  Relating a particular external solid definition to that list remains a
  separate geometric obligation.
- Positive-gap separation proves disjoint closed bodies, which is stronger than
  disjoint interiors. Touching optimal packings need a weak-separation/interior
  extension or an arbitrarily small outward container perturbation.
- Containment and separation inequalities must hold exactly in the Lean model.
  The supplied example discharges every such inequality with kernel-checked
  exact arithmetic. The archive's JSON parser, decimal/rational conversions,
  algebraic-number arithmetic, quaternion normalization and Python checker are
  **not** verified by these theorems.
- No theorem asserts that every live catalogue entry has been checked in Lean.
  Existing archive exact certificates and these Lean proofs are distinct
  verification layers. A per-record proof-producing importer is future work.
- The formalization does not prove optimizer convergence, completeness of a
  heuristic search, exhaustiveness of proposed separating axes, or global
  optimality of a reported construction.
- The concrete example is an interface regression witness, not a new record.

The paper can accurately claim a **Lean-checked certificate-soundness core**.
It cannot accurately claim that all numerical results, all implementation
code, or the live catalogue are Lean certified.
