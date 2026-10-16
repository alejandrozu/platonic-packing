import Mathlib.Combinatorics.SimpleGraph.DegreeSum
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Real.Basic

/-!
# A finite support-query work bound

The actual ND support routine visits vertices with strictly increasing support
values. A fixed-direction query therefore scans each adjacency list at most
once. This proves the combinatorial part of its O(d(E+1)) arithmetic work
bound. It is not a proof of the Python implementation or an optimizer
convergence theorem. The graph is finite, simple and undirected, as required
of the polytope edge graph supplied to the search.
-/

namespace PackingCertificates.Extensions

open scoped BigOperators

/-- Strict improvement along all ordered pairs of a trace rules out a revisit.
The support kernel's positive-threshold acceptance implies this premise when
its computed fixed-direction values are finite. -/
theorem strictly_improving_trace_nodup {V : ℕ} (value : Fin V → ℝ)
    (trace : List (Fin V))
    (h : trace.Pairwise (fun a b => value a < value b)) : trace.Nodup := by
  exact h.imp (fun hab => fun heq => (ne_of_lt hab) (congrArg value heq))

/-- A fixed-direction support query can visit at most V vertices, including
its final vertex. Thus a strict-improvement trace cannot continue forever. -/
theorem support_trace_length_le_vertices {V : ℕ} (value : Fin V → ℝ)
    (trace : List (Fin V))
    (h : trace.Pairwise (fun a b => value a < value b)) : trace.length ≤ V := by
  have hn := strictly_improving_trace_nodup value trace h
  rw [← List.toFinset_card_of_nodup hn]
  exact (Finset.card_le_card trace.toFinset.subset_univ).trans_eq (by simp)

/-- The total number of neighbor entries examined in a strictly improving
trace is at most twice the number of undirected graph edges. -/
theorem support_neighbor_scans_le_twice_edges {V : ℕ}
    (G : SimpleGraph (Fin V)) [DecidableRel G.Adj]
    (value : Fin V → ℝ) (trace : List (Fin V))
    (h : trace.Pairwise (fun a b => value a < value b)) :
    (trace.map (fun v => G.degree v)).sum ≤ 2 * G.edgeFinset.card := by
  have hn := strictly_improving_trace_nodup value trace h
  rw [← List.sum_toFinset _ hn]
  calc
    ∑ v ∈ trace.toFinset, G.degree v ≤ ∑ v, G.degree v :=
      Finset.sum_le_sum_of_subset trace.toFinset.subset_univ
    _ = 2 * G.edgeFinset.card := G.sum_degrees_eq_twice_card_edges

/-- Including the initial vertex, at most 1+2E dot products are evaluated.
Each dot product uses d scalar multiplications and d accumulations in the
straight-line implementation. -/
theorem support_coordinate_products_bound {V : ℕ}
    (G : SimpleGraph (Fin V)) [DecidableRel G.Adj]
    (value : Fin V → ℝ) (trace : List (Fin V))
    (h : trace.Pairwise (fun a b => value a < value b)) (d : ℕ) :
    d * (1 + (trace.map (fun v => G.degree v)).sum) ≤ d * (1 + 2 * G.edgeFinset.card) := by
  exact Nat.mul_le_mul_left d (Nat.add_le_add_left
    (support_neighbor_scans_le_twice_edges G value trace h) 1)

end PackingCertificates.Extensions

#print axioms PackingCertificates.Extensions.strictly_improving_trace_nodup
#print axioms PackingCertificates.Extensions.support_trace_length_le_vertices
#print axioms PackingCertificates.Extensions.support_neighbor_scans_le_twice_edges
#print axioms PackingCertificates.Extensions.support_coordinate_products_bound
