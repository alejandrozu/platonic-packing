import PackingCertificates.Core
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
# From a strictly enclosed finite motif to a periodic packing

The motif consists of complete sets, including the full convex bodies denoted
by the certificate core. Every piece lies strictly inside one open rectangular
cell, and distinct pieces in the motif are disjoint. Integer translates of that
cell are proved disjoint, rather than assuming global non-overlap. The core's
nested-packing theorem then proves disjointness of every pair of copies.

Strict whole-body enclosure is a sufficient, restrictive hypothesis. Motifs
crossing a cell face need additional neighbor-image checks; general polyhedral
containers need not tile space, and enclosing one in a box can lower density.
Injective linear transport can give skew cells and can deform the pieces.
An isometry guarantees congruence; injectivity alone does not.
No density optimality, tiling, crystallization dynamics,
or interaction-energy claim is made here. The proofs use coordinates only;
the Euclidean-space corollary makes the ambient dimension explicit.
-/

namespace PackingCertificates.Extensions.PeriodicMotif

open Set

/-- Open rectangular cell in coordinate space. -/
def openCell {d : ℕ} (width : Fin d → ℝ) : Set (Fin d → ℝ) :=
  {x | ∀ k, 0 < x k ∧ x k < width k}

/-- Lattice vector with integer coefficients in the rectangular basis. -/
def latticeVector {d : ℕ} (width : Fin d → ℝ) (z : Fin d → ℤ) : Fin d → ℝ :=
  fun k => width k * (z k : ℝ)

/-- Translation by an integer lattice vector. -/
def shift {d : ℕ} (width : Fin d → ℝ) (z : Fin d → ℤ) (x : Fin d → ℝ) : Fin d → ℝ :=
  x + latticeVector width z

/-- One complete piece in one translated cell. The index distinguishes both
the integer cell and the piece in its motif. -/
def periodicPiece {d : ℕ} {I : Type*} (width : Fin d → ℝ)
    (pieces : I → Set (Fin d → ℝ)) (p : (Fin d → ℤ) × I) : Set (Fin d → ℝ) :=
  shift width p.1 '' pieces p.2

theorem shift_injective {d : ℕ} (width : Fin d → ℝ) (z : Fin d → ℤ) :
    Function.Injective (shift width z) := by
  intro x y h
  exact add_right_cancel h

theorem shift_add {d : ℕ} (width : Fin d → ℝ) (z t : Fin d → ℤ) (x : Fin d → ℝ) :
    shift width z (shift width t x) = shift width (z + t) x := by
  funext k
  simp only [shift, latticeVector, Pi.add_apply, Int.cast_add]
  ring

/-- The lattice translations permute the indexed family of copies, so the
packing constructed below is periodic by an actual integer-translation action. -/
theorem periodic_piece_shift {d : ℕ} {I : Type*} (width : Fin d → ℝ)
    (pieces : I → Set (Fin d → ℝ)) (z t : Fin d → ℤ) (i : I) :
    shift width t '' periodicPiece width pieces (z, i) =
      periodicPiece width pieces (t + z, i) := by
  unfold periodicPiece
  rw [Set.image_image]
  congr 1
  funext x
  exact shift_add width t z x

/-- Positive side lengths are precisely what makes the open cell nonempty.
This includes the vacuous zero-dimensional case. -/
theorem openCell_nonempty_iff {d : ℕ} (width : Fin d → ℝ) :
    (openCell width).Nonempty ↔ ∀ k, 0 < width k := by
  constructor
  · rintro ⟨x, hx⟩ k
    exact (hx k).1.trans (hx k).2
  · intro hw
    refine ⟨fun k => width k / 2, ?_⟩
    intro k
    constructor <;> linarith [hw k]

/-- Distinct integer cells cannot share a point: in a coordinate where their
indices differ, the integer gap is at least one whole positive cell width. -/
theorem translated_cells_disjoint {d : ℕ} (width : Fin d → ℝ)
    (hw : ∀ k, 0 < width k) :
    Pairwise (fun z t : Fin d → ℤ =>
      Disjoint (shift width z '' openCell width) (shift width t '' openCell width)) := by
  intro z t hzt
  obtain ⟨k, hk⟩ := Function.ne_iff.mp hzt
  apply Set.disjoint_left.mpr
  rintro _ ⟨x, hx, rfl⟩ ⟨y, hy, hyx⟩
  have heq : y k + width k * (t k : ℝ) = x k + width k * (z k : ℝ) :=
    congrFun hyx k
  rcases lt_or_gt_of_ne hk with hlt | hgt
  · have hstep : ((z k + 1 : ℤ) : ℝ) ≤ (t k : ℝ) :=
      Int.cast_le.mpr (Int.add_one_le_iff.mpr hlt)
    norm_num only [Int.cast_add, Int.cast_one] at hstep
    have hmul := mul_le_mul_of_nonneg_left hstep (hw k).le
    have hupper := (hx k).2
    have hlower := (hy k).1
    nlinarith
  · have hstep : ((t k + 1 : ℤ) : ℝ) ≤ (z k : ℝ) :=
      Int.cast_le.mpr (Int.add_one_le_iff.mpr hgt)
    norm_num only [Int.cast_add, Int.cast_one] at hstep
    have hmul := mul_le_mul_of_nonneg_left hstep (hw k).le
    have hupper := (hy k).2
    have hlower := (hx k).1
    nlinarith

/-- A whole-body motif packing in one open cell gives a global periodic
packing. No assumption about pairs of pieces in different cells is supplied:
their disjointness is derived from the positive-width integer lattice. -/
theorem periodic_packing {d : ℕ} {I : Type*} (width : Fin d → ℝ)
    (hw : ∀ k, 0 < width k) (pieces : I → Set (Fin d → ℝ))
    (inside : ∀ i, pieces i ⊆ openCell width)
    (separate : Pairwise (fun i j => Disjoint (pieces i) (pieces j))) :
    Pairwise (fun p q : (Fin d → ℤ) × I =>
      Disjoint (periodicPiece width pieces p) (periodicPiece width pieces q)) := by
  have local_separate : ∀ z : Fin d → ℤ, Pairwise (fun i j : I =>
      Disjoint (shift width z '' pieces i) (shift width z '' pieces j)) := by
    intro z i j hij
    apply Set.disjoint_left.mpr
    rintro _ ⟨x, hx, rfl⟩ ⟨y, hy, hyx⟩
    have hyx' := shift_injective width z hyx
    exact Set.disjoint_left.mp (separate hij) hx (hyx' ▸ hy)
  exact (nested_packing_sound
    (fun z => shift width z '' openCell width)
    (fun z i => shift width z '' pieces i) Set.univ
    (fun _ => Set.subset_univ _)
    (fun z i => Set.image_mono (inside i))
    (translated_cells_disjoint width hw) local_separate).2

/-- Direct bridge from the existing finite vertex/plane certificate checker.
The extra hypothesis encloses its entire certified container in the open cell.
Every translated piece is its full real convex hull. -/
theorem certificate_periodic_packing {d n m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → (Fin d → ℝ)}
    {walls : Fin m → Halfspace (Fin d → ℝ)}
    (c : FinitePackingCertificate k v walls) (width : Fin d → ℝ)
    (hw : ∀ k, 0 < width k) (container_inside : container walls ⊆ openCell width) :
    Pairwise (fun p q : (Fin d → ℤ) × Fin n =>
      Disjoint (periodicPiece width (fun i => vertexBody (v i)) p)
        (periodicPiece width (fun i => vertexBody (v i)) q)) := by
  have hs := finite_certificate_sound c
  exact periodic_packing width hw (fun i => vertexBody (v i))
    (fun i => (hs.1 i).trans container_inside) hs.2

/-- An injective linear map transports the complete periodic packing into a
possibly skew lattice. It generally deforms the solids as well as the cell. -/
theorem linear_periodic_packing {d : ℕ} {I E : Type*}
    [AddCommGroup E] [Module ℝ E]
    (width : Fin d → ℝ) (hw : ∀ k, 0 < width k)
    (pieces : I → Set (Fin d → ℝ)) (inside : ∀ i, pieces i ⊆ openCell width)
    (separate : Pairwise (fun i j => Disjoint (pieces i) (pieces j)))
    (L : (Fin d → ℝ) →ₗ[ℝ] E) (hL : Function.Injective L) :
    Pairwise (fun p q : (Fin d → ℤ) × I =>
      Disjoint (L '' periodicPiece width pieces p) (L '' periodicPiece width pieces q)) := by
  exact (transported_packing (periodicPiece width pieces) Set.univ Set.univ L hL
    (fun _ => Set.subset_univ _)
    (periodic_packing width hw pieces inside separate) (Set.subset_univ _)).2

/-- The transported image has translation vector `L(latticeVector width z)`;
this is a lattice statement, rather than only an arbitrary injective-set image. -/
theorem linear_image_piece {d : ℕ} {I E : Type*} [AddCommGroup E] [Module ℝ E]
    (width : Fin d → ℝ) (pieces : I → Set (Fin d → ℝ))
    (L : (Fin d → ℝ) →ₗ[ℝ] E) (z : Fin d → ℤ) (i : I) :
    L '' periodicPiece width pieces (z, i) =
      (fun x => L x + L (latticeVector width z)) '' pieces i := by
  unfold periodicPiece
  rw [Set.image_image]
  congr 1
  funext x
  exact L.map_add _ _

/-- Explicit Euclidean-space version in every finite dimension. Coordinate
conversion is linear and injective, and does not alter the underlying points. -/
theorem euclidean_periodic_packing {d : ℕ} {I : Type*}
    (width : Fin d → ℝ) (hw : ∀ k, 0 < width k)
    (pieces : I → Set (Fin d → ℝ)) (inside : ∀ i, pieces i ⊆ openCell width)
    (separate : Pairwise (fun i j => Disjoint (pieces i) (pieces j))) :
    Pairwise (fun p q : (Fin d → ℤ) × I =>
      Disjoint ((WithLp.toLp 2 : (Fin d → ℝ) → EuclideanSpace ℝ (Fin d)) ''
        periodicPiece width pieces p)
        ((WithLp.toLp 2 : (Fin d → ℝ) → EuclideanSpace ℝ (Fin d)) ''
          periodicPiece width pieces q)) := by
  exact linear_periodic_packing width hw pieces inside separate
    (WithLp.linearEquiv 2 ℝ (Fin d → ℝ)).symm.toLinearMap
    (WithLp.toLp_injective 2)

/-- A nonpositive width collapses the proposed open cell to the empty set. -/
theorem nonpositive_width_empty_regression {d : ℕ} (width : Fin d → ℝ)
    (k : Fin d) (hk : width k ≤ 0) : openCell width = ∅ := by
  apply Set.eq_empty_iff_forall_notMem.mpr
  intro x hx
  have hl := (hx k).1
  have hu := (hx k).2
  linarith

/-- A unit one-dimensional cell has the expected strictly interior motif. -/
theorem one_dimensional_positive_regression :
    (openCell (fun _ : Fin 1 => (1 : ℝ))).Nonempty :=
  (openCell_nonempty_iff _).mpr (by intro k; norm_num)

/-- Omitting cell containment really permits overlap: a length-two closed
interval and its unit translate share the point 3/2, inside both intervals. -/
theorem missing_containment_overlap_regression :
    ¬ Disjoint
      (shift (fun _ : Fin 1 => (1 : ℝ)) (fun _ => (0 : ℤ)) ''
        {x : Fin 1 → ℝ | 0 ≤ x 0 ∧ x 0 ≤ 2})
      (shift (fun _ : Fin 1 => (1 : ℝ)) (fun _ => (1 : ℤ)) ''
        {x : Fin 1 → ℝ | 0 ≤ x 0 ∧ x 0 ≤ 2}) := by
  intro hd
  apply (Set.disjoint_left.mp hd) (a := fun _ : Fin 1 => (3 / 2 : ℝ))
  · refine ⟨fun _ => (3 / 2 : ℝ), by norm_num, ?_⟩
    funext k
    norm_num [shift, latticeVector]
  · refine ⟨fun _ => (1 / 2 : ℝ), by norm_num, ?_⟩
    funext k
    norm_num [shift, latticeVector]

/-- A positive rectangular basis has distinct integer lattice vectors. -/
theorem latticeVector_injective {d : ℕ} (width : Fin d → ℝ)
    (hw : ∀ k, 0 < width k) : Function.Injective (latticeVector width) := by
  intro z t h
  funext k
  have heq : width k * (z k : ℝ) = width k * (t k : ℝ) := congrFun h k
  have hcast : (z k : ℝ) = (t k : ℝ) := mul_left_cancel₀ (ne_of_gt (hw k)) heq
  exact Int.cast_injective hcast

/-- Strict tests on every vertex enclose the full real convex hull in the
open cell, so the periodic construction remains a finite-check procedure. -/
theorem vertex_body_inside_openCell {d k : ℕ} (width : Fin d → ℝ)
    (v : Fin k → (Fin d → ℝ))
    (inside_vertices : ∀ p j, 0 < v p j ∧ v p j < width j) :
    vertexBody v ⊆ openCell width := by
  intro x hx j
  exact convexHull_min
    (by rintro _ ⟨p, rfl⟩; exact inside_vertices p j)
    ((convex_Ioo (0 : ℝ) (width j)).linear_preimage (LinearMap.proj j)) hx

/-- A source certificate's pair planes and strict cell tests on its finite
vertex lists imply the complete infinite periodic packing. Its original
container can have any polyhedral shape; no tiling property is assumed. -/
theorem vertex_certificate_periodic_packing {d n m : ℕ} {k : Fin n → ℕ}
    {v : (i : Fin n) → Fin (k i) → (Fin d → ℝ)}
    {walls : Fin m → Halfspace (Fin d → ℝ)}
    (c : FinitePackingCertificate k v walls) (width : Fin d → ℝ)
    (hw : ∀ j, 0 < width j)
    (inside_vertices : ∀ i p j, 0 < v i p j ∧ v i p j < width j) :
    Pairwise (fun p q : (Fin d → ℤ) × Fin n =>
      Disjoint (periodicPiece width (fun i => vertexBody (v i)) p)
        (periodicPiece width (fun i => vertexBody (v i)) q)) :=
  periodic_packing width hw (fun i => vertexBody (v i))
    (fun i => vertex_body_inside_openCell width (v i) (inside_vertices i))
    (finite_certificate_sound c).2

/-- A genuine basis change is bijective, hence gives a full lattice in the
new ambient vector space. It can deform both the cell and the pieces. -/
theorem basis_periodic_packing {d : ℕ} {I E : Type*}
    [AddCommGroup E] [Module ℝ E]
    (width : Fin d → ℝ) (hw : ∀ k, 0 < width k)
    (pieces : I → Set (Fin d → ℝ)) (inside : ∀ i, pieces i ⊆ openCell width)
    (separate : Pairwise (fun i j => Disjoint (pieces i) (pieces j)))
    (L : (Fin d → ℝ) ≃ₗ[ℝ] E) :
    Pairwise (fun p q : (Fin d → ℤ) × I =>
      Disjoint (L '' periodicPiece width pieces p) (L '' periodicPiece width pieces q)) :=
  linear_periodic_packing width hw pieces inside separate L.toLinearMap L.injective

/-- A closed interval strictly inside its unit cell yields infinitely many
disjoint complete interval copies, rather than only a point-set example. -/
theorem interval_motif_periodic_regression :
    Pairwise (fun p q : (Fin 1 → ℤ) × Fin 1 =>
      Disjoint
        (periodicPiece (fun _ => (1 : ℝ))
          (fun _ => {x : Fin 1 → ℝ | (1 / 4 : ℝ) ≤ x 0 ∧ x 0 ≤ 3 / 4}) p)
        (periodicPiece (fun _ => (1 : ℝ))
          (fun _ => {x : Fin 1 → ℝ | (1 / 4 : ℝ) ≤ x 0 ∧ x 0 ≤ 3 / 4}) q)) := by
  apply periodic_packing (fun _ => (1 : ℝ)) (by intro k; norm_num)
  · intro i x hx k
    have hk : k = 0 := Subsingleton.elim k 0
    subst k
    constructor <;> linarith [hx.1, hx.2]
  · intro i j hij
    exact False.elim (hij (Subsingleton.elim i j))

end PackingCertificates.Extensions.PeriodicMotif

#print axioms PackingCertificates.Extensions.PeriodicMotif.shift_injective
#print axioms PackingCertificates.Extensions.PeriodicMotif.shift_add
#print axioms PackingCertificates.Extensions.PeriodicMotif.periodic_piece_shift
#print axioms PackingCertificates.Extensions.PeriodicMotif.openCell_nonempty_iff
#print axioms PackingCertificates.Extensions.PeriodicMotif.translated_cells_disjoint
#print axioms PackingCertificates.Extensions.PeriodicMotif.periodic_packing
#print axioms PackingCertificates.Extensions.PeriodicMotif.certificate_periodic_packing
#print axioms PackingCertificates.Extensions.PeriodicMotif.linear_periodic_packing
#print axioms PackingCertificates.Extensions.PeriodicMotif.linear_image_piece
#print axioms PackingCertificates.Extensions.PeriodicMotif.euclidean_periodic_packing
#print axioms PackingCertificates.Extensions.PeriodicMotif.nonpositive_width_empty_regression
#print axioms PackingCertificates.Extensions.PeriodicMotif.one_dimensional_positive_regression
#print axioms PackingCertificates.Extensions.PeriodicMotif.missing_containment_overlap_regression

#print axioms PackingCertificates.Extensions.PeriodicMotif.latticeVector_injective
#print axioms PackingCertificates.Extensions.PeriodicMotif.vertex_body_inside_openCell
#print axioms PackingCertificates.Extensions.PeriodicMotif.vertex_certificate_periodic_packing
#print axioms PackingCertificates.Extensions.PeriodicMotif.basis_periodic_packing
#print axioms PackingCertificates.Extensions.PeriodicMotif.interval_motif_periodic_regression
