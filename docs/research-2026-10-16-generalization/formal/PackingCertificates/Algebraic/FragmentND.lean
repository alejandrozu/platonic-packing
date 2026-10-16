import PackingCertificates.Algebraic.PackingND

/-! Small proof assembly interfaces. All numerical premises are exact kernel
checks of the original `PackingND.Certificate`; no arithmetic is delegated. -/

namespace PackingCertificates.Algebraic.FragmentND

open PackingCertificates.Rational
open PackingCertificates.Algebraic.PackingND
open scoped BigOperators

def rangeCheck {n : ℕ} (lo len : ℕ) (h : lo + len ≤ n)
    (f : Fin n → Bool) : Bool :=
  allFin len (fun j => f ⟨lo + j.val, by omega⟩)

theorem rangeCheck_sound {n lo len : ℕ} {h : lo + len ≤ n}
    {f : Fin n → Bool} (hc : rangeCheck lo len h f = true)
    (i : Fin n) (hl : lo ≤ i.val) (hu : i.val < lo + len) : f i = true := by
  have hi : i.val - lo < len := by omega
  have hj := (allFin_eq_true.mp hc) (⟨i.val-lo,hi⟩ : Fin len)
  have he : (⟨lo+(i.val-lo),by omega⟩ : Fin n) = i := by
    apply Fin.ext
    change lo+(i.val-lo) = i.val
    omega
  simpa only [he] using hj

def sourcePieceCheck (c : Certificate d n k l b) (i : Fin n) : Bool :=
  PackingCertificates.Cayley.check (c.cayley i) &&
    (decide (c.rotation i = (c.cayley i).rotation) &&
    allFin d (fun a => allFin d (fun z =>
      decide (qdot (c.rotation i a) (c.rotation i z) = if a = z then 1 else 0))))

theorem sourceCheck_of_pieces (c : Certificate d n k l b)
    (hs : 0 < c.scale) (h : ∀ i, sourcePieceCheck c i = true) :
    c.sourceCheck = true := by
  simp only [Certificate.sourceCheck,Bool.and_eq_true,decide_eq_true_eq]
  exact ⟨hs,allFin_eq_true.mpr h⟩

def basisItemCheck (c : Certificate d n k l b) (z : Fin b) : Bool :=
  decide (Function.Injective (c.basisIndices z)) &&
    (QuadraticInverse.inverseCheck c.radicand (c.basisRawMatrix z) (c.basisInverses z) &&
    (decide (0 < c.container.normalizationInterval.lo) &&
    allFin (d+1) (fun i => allFin (d+1) (fun j => Interval.enclosesCheck
      (QuadraticInverse.scaledInverseInterval c.container.rootSpec.interval
        (c.basisInverses z) c.container.normalizationInterval i j)
      (c.basisInverseIntervals z i j)))))

theorem basisCheck_of_items (c : Certificate d n k l b)
    (h : ∀ z, basisItemCheck c z = true) : c.basisCheck = true :=
  allFin_eq_true.mpr h

theorem placementCheck_of_vertices (c : Certificate d n k l b)
    (h : ∀ i p, c.placedCheck i p = true) : c.placementCheck = true :=
  allFin_eq_true.mpr (fun i => allFin_eq_true.mpr (h i))

theorem containmentCheck_of_vertices (c : Certificate d n k l b)
    (h : ∀ i p, c.vertexContainmentCheck i p = true) : c.containmentCheck = true :=
  allFin_eq_true.mpr (fun i => allFin_eq_true.mpr (h i))

def pairLeftCheck (c : Certificate d n k l b) (i j : Fin n) (p : Fin k) : Bool :=
  decide ((Placement.dotInterval (c.separation i j).normal
    (c.placedIntervals i p)).hi ≤ (c.separation i j).lower)

def pairRightCheck (c : Certificate d n k l b) (i j : Fin n) (p : Fin k) : Bool :=
  decide ((c.separation i j).upper ≤
    (Placement.dotInterval (c.separation i j).normal (c.placedIntervals j p)).lo)

theorem pairCheck_of_vertices (c : Certificate d n k l b) (i j : Fin n)
    (hg : (c.separation i j).lower < (c.separation i j).upper)
    (hl : ∀ p, pairLeftCheck c i j p = true)
    (hr : ∀ p, pairRightCheck c i j p = true) : c.pairCheck i j = true := by
  simp only [Certificate.pairCheck,Bool.and_eq_true,decide_eq_true_eq]
  exact ⟨hg,allFin_eq_true.mpr hl,allFin_eq_true.mpr hr⟩

theorem pairsCheck_of_pairs (c : Certificate d n k l b)
    (h : ∀ i j, i < j → c.pairCheck i j = true) : c.pairsCheck = true := by
  apply allFin_eq_true.mpr
  intro i
  apply allFin_eq_true.mpr
  intro j
  by_cases hij : i < j
  · simpa only [hij,if_true] using h i j hij
  · simp only [hij,if_false]

end PackingCertificates.Algebraic.FragmentND

#print axioms PackingCertificates.Algebraic.FragmentND.rangeCheck_sound
#print axioms PackingCertificates.Algebraic.FragmentND.sourceCheck_of_pieces
#print axioms PackingCertificates.Algebraic.FragmentND.basisCheck_of_items
#print axioms PackingCertificates.Algebraic.FragmentND.placementCheck_of_vertices
#print axioms PackingCertificates.Algebraic.FragmentND.containmentCheck_of_vertices
#print axioms PackingCertificates.Algebraic.FragmentND.pairCheck_of_vertices
#print axioms PackingCertificates.Algebraic.FragmentND.pairsCheck_of_pairs
