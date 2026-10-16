import PackingCertificates.Algebraic.Packing

/-! Bounded exact arithmetic proofs for the unchanged 3D certificate. -/
namespace PackingCertificates.Algebraic.Fragment3D
open PackingCertificates.Rational (allFin allFin_eq_true)
open PackingCertificates.Algebraic.Packing

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

def basisItemCheck (c : Certificate n k l b) (z : Fin b) : Bool :=
  decide (Function.Injective (c.basisIndices z)) &&
    Simplex.basisCacheCheck (c.basisMatrixInterval z) (c.basisDeterminants z) (c.basisAdjugates z)

theorem basisCheck_of_items (c : Certificate n k l b)
    (h : ∀ z, basisItemCheck c z = true) : c.basisCheck = true :=
  allFin_eq_true.mpr h

theorem placementCheck_of_vertices (c : Certificate n k l b)
    (h : ∀ i p, c.placedCheck i p = true) : c.placementCheck = true :=
  allFin_eq_true.mpr (fun i => allFin_eq_true.mpr (h i))

theorem containmentCheck_of_vertices (c : Certificate n k l b)
    (h : ∀ i p, c.vertexContainmentCheck i p = true) : c.containmentCheck = true :=
  allFin_eq_true.mpr (fun i => allFin_eq_true.mpr (h i))

def pairLeftCheck (c : Certificate n k l b) (i j : Fin n) (p : Fin k) : Bool :=
  decide ((Placement.dotInterval (c.separation i j).normal
    (c.placedIntervals i p)).hi ≤ (c.separation i j).lower)

def pairRightCheck (c : Certificate n k l b) (i j : Fin n) (p : Fin k) : Bool :=
  decide ((c.separation i j).upper ≤
    (Placement.dotInterval (c.separation i j).normal (c.placedIntervals j p)).lo)

theorem pairCheck_of_vertices (c : Certificate n k l b) (i j : Fin n)
    (hg : (c.separation i j).lower < (c.separation i j).upper)
    (hl : ∀ p, pairLeftCheck c i j p = true)
    (hr : ∀ p, pairRightCheck c i j p = true) : c.pairCheck i j = true := by
  simp only [Certificate.pairCheck,Bool.and_eq_true,decide_eq_true_eq]
  exact ⟨hg,allFin_eq_true.mpr hl,allFin_eq_true.mpr hr⟩

theorem pairsCheck_of_pairs (c : Certificate n k l b)
    (h : ∀ i j, i < j → c.pairCheck i j = true) : c.pairsCheck = true := by
  apply allFin_eq_true.mpr
  intro i
  apply allFin_eq_true.mpr
  intro j
  by_cases hij : i < j
  · simpa only [hij,if_true] using h i j hij
  · simp only [hij,if_false]

#print axioms rangeCheck_sound
#print axioms basisCheck_of_items
#print axioms placementCheck_of_vertices
#print axioms containmentCheck_of_vertices
#print axioms pairCheck_of_vertices
#print axioms pairsCheck_of_pairs
end PackingCertificates.Algebraic.Fragment3D
