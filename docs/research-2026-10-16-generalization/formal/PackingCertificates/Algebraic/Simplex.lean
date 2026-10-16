import PackingCertificates.Core
import PackingCertificates.Algebraic.Interval
import Mathlib.Analysis.Convex.Combination
import Mathlib.LinearAlgebra.Matrix.Adjugate
import Mathlib.Algebra.BigOperators.Pi
import Mathlib.Tactic.FieldSimp

/-!
# Affine-basis correction certificates for algebraic containers

A small Cramer system corrects a uniform baseline weight on every container
vertex. The corrected weights can have much larger positive margins than a
sparse barycentric witness, while still proving membership in the exact
container vertex hull. No regularity or tangency assumption is used.
-/

namespace PackingCertificates.Algebraic.Simplex

open scoped BigOperators Matrix

variable {E : Type*} [AddCommGroup E] [Module ℝ E]

def baselineWeights {m k : ℕ} (ι : Fin k → Fin m) (ε : ℝ)
    (t : Fin k → ℝ) (j : Fin m) : ℝ :=
  ε + ∑ i, if ι i = j then t i else 0

theorem baselineWeights_at {m k : ℕ} (ι : Fin k → Fin m)
    (hι : Function.Injective ι) (ε : ℝ) (t : Fin k → ℝ) (i : Fin k) :
    baselineWeights ι ε t (ι i) = ε + t i := by
  unfold baselineWeights
  congr 1
  have hsum : (∑ j, if ι j = ι i then t j else 0) =
      (if ι i = ι i then t i else 0) := by
    apply Finset.sum_eq_single i
    · intro j _ hji
      have hne : ι j ≠ ι i := fun hij => hji (hι hij)
      simp [hne]
    · simp
  simpa using hsum

theorem baselineWeights_nonnegative {m k : ℕ} (ι : Fin k → Fin m)
    (hι : Function.Injective ι) (ε : ℝ) (hε : 0 ≤ ε) (t : Fin k → ℝ)
    (ht : ∀ i, 0 ≤ ε + t i) : ∀ j, 0 ≤ baselineWeights ι ε t j := by
  intro j
  by_cases hj : ∃ i, ι i = j
  · obtain ⟨i,rfl⟩ := hj
    rw [baselineWeights_at ι hι]
    exact ht i
  · have hzero : ∀ i, ι i ≠ j := by simpa using hj
    simpa [baselineWeights,hzero] using hε

theorem baselineWeights_sum {m k : ℕ} (ι : Fin k → Fin m) (ε : ℝ)
    (t : Fin k → ℝ) :
    (∑ j, baselineWeights ι ε t j) = (m : ℝ)*ε + ∑ i, t i := by
  simp only [baselineWeights, Finset.sum_add_distrib]
  rw [Finset.sum_comm]
  simp [nsmul_eq_mul]

theorem baselineWeights_vector_sum {m k : ℕ} (v : Fin m → E)
    (ι : Fin k → Fin m) (ε : ℝ) (t : Fin k → ℝ) :
    (∑ j, baselineWeights ι ε t j • v j) =
      ε • (∑ j, v j) + ∑ i, t i • v (ι i) := by
  simp only [baselineWeights, add_smul, Finset.sum_add_distrib,
    Finset.sum_smul, ite_smul, zero_smul]
  rw [Finset.sum_comm, ← Finset.smul_sum]
  simp

theorem centered_hull_membership {m k : ℕ} (v : Fin m → E)
    (hcenter : (∑ j, v j) = 0) (ι : Fin k → Fin m)
    (hι : Function.Injective ι) (ε : ℝ) (hε : 0 ≤ ε) (t : Fin k → ℝ)
    (ht : ∀ i, 0 ≤ ε + t i)
    (hmass : (∑ i, t i) = 1-(m : ℝ)*ε) (x : E)
    (hpoint : (∑ i, t i • v (ι i)) = x) :
    x ∈ vertexBody v := by
  have hnonneg := baselineWeights_nonnegative ι hι ε hε t ht
  have hsum : (∑ j, baselineWeights ι ε t j) = 1 := by
    rw [baselineWeights_sum,hmass]
    ring
  have heq : (∑ j, baselineWeights ι ε t j • v j) = x := by
    rw [baselineWeights_vector_sum,hcenter,smul_zero,zero_add,hpoint]
  have hmem := (convex_convexHull ℝ (Set.range v)).sum_mem
    (fun j _ => hnonneg j) hsum
    (fun j _ => subset_convexHull ℝ (Set.range v) ⟨j,rfl⟩)
  rwa [heq] at hmem

/-- Mass is row zero; the d spatial coordinates are successor rows. -/
def augmentedMatrix {d : ℕ} (v : Fin (d+1) → Fin d → ℝ) :
    Matrix (Fin (d+1)) (Fin (d+1)) ℝ :=
  fun a j => Fin.cases 1 (fun b => v j b) a

def augmentedRHS {d : ℕ} (mass : ℝ) (x : Fin d → ℝ) : Fin (d+1) → ℝ :=
  Fin.cases mass x

noncomputable def cramerWeights {k : ℕ}
    (A : Matrix (Fin k) (Fin k) ℝ) (b : Fin k → ℝ) : Fin k → ℝ :=
  A.det⁻¹ • A.cramer b

theorem cramerWeights_solution {k : ℕ}
    (A : Matrix (Fin k) (Fin k) ℝ) (b : Fin k → ℝ) (hdet : A.det ≠ 0) :
    A *ᵥ cramerWeights A b = b := by
  rw [cramerWeights, Matrix.mulVec_smul, Matrix.mulVec_cramer,
    smul_smul,inv_mul_cancel₀ hdet,one_smul]

theorem augmented_solution_mass {d : ℕ} (v : Fin (d+1) → Fin d → ℝ)
    (t : Fin (d+1) → ℝ) (mass : ℝ) (x : Fin d → ℝ)
    (h : augmentedMatrix v *ᵥ t = augmentedRHS mass x) : (∑ i, t i) = mass := by
  have hh := congrFun h 0
  simpa [augmentedMatrix, augmentedRHS, Matrix.mulVec, dotProduct] using hh

theorem augmented_solution_point {d : ℕ} (v : Fin (d+1) → Fin d → ℝ)
    (t : Fin (d+1) → ℝ) (mass : ℝ) (x : Fin d → ℝ)
    (h : augmentedMatrix v *ᵥ t = augmentedRHS mass x) :
    (∑ i, t i • v i) = x := by
  funext a
  have hh := congrFun h a.succ
  simpa [augmentedMatrix,augmentedRHS,Matrix.mulVec,dotProduct,
    Finset.sum_apply,Pi.smul_apply,smul_eq_mul,mul_comm] using hh

theorem cramer_centered_hull_membership {d m : ℕ}
    (v : Fin m → Fin d → ℝ) (hcenter : (∑ j, v j) = 0)
    (ι : Fin (d+1) → Fin m) (hι : Function.Injective ι)
    (ε : ℝ) (hε : 0 ≤ ε) (x : Fin d → ℝ)
    (hdet : (augmentedMatrix (fun i => v (ι i))).det ≠ 0)
    (hweights : ∀ i, 0 ≤ ε +
      cramerWeights (augmentedMatrix (fun i => v (ι i)))
        (augmentedRHS (1-(m : ℝ)*ε) x) i) : x ∈ vertexBody v := by
  let A := augmentedMatrix (fun i => v (ι i))
  let b := augmentedRHS (1-(m : ℝ)*ε) x
  have hsolution := cramerWeights_solution A b hdet
  exact centered_hull_membership v hcenter ι hι ε hε _ hweights
    (augmented_solution_mass _ _ _ _ hsolution) x
    (augmented_solution_point _ _ _ _ hsolution)

def sumInterval {α : Type*} (l : List α) (a : α → Interval) : Interval :=
  l.foldr (fun i z => Interval.add (a i) z) (Interval.point 0)

def prodInterval {α : Type*} (l : List α) (a : α → Interval) : Interval :=
  l.foldr (fun i z => Interval.mul (a i) z) (Interval.point 1)

theorem sumInterval_sound {α : Type*} (l : List α) (a : α → Interval)
    (x : α → ℝ) (h : ∀ i ∈ l, (a i).Contains (x i)) :
    (sumInterval l a).Contains ((l.map x).sum) := by
  induction l with
  | nil => simp [sumInterval,Interval.Contains,Interval.point]
  | cons i l ih =>
    exact Interval.add_sound (h i (by simp)) (ih (fun j hj => h j (by simp [hj])))

theorem prodInterval_sound {α : Type*} (l : List α) (a : α → Interval)
    (x : α → ℝ) (h : ∀ i ∈ l, (a i).Contains (x i)) :
    (prodInterval l a).Contains ((l.map x).prod) := by
  induction l with
  | nil => simp [prodInterval,Interval.Contains,Interval.point]
  | cons i l ih =>
    exact Interval.mul_sound (h i (by simp)) (ih (fun j hj => h j (by simp [hj])))

def sumFiniteInterval {α : Type*} [Fintype α] [DecidableEq α]
    (a : α → Interval) : Interval := ⟨∑ i, (a i).lo, ∑ i, (a i).hi⟩

def prodFiniteInterval {k : ℕ} (a : Fin k → Interval) : Interval :=
  prodInterval (List.finRange k) a

theorem sumFiniteInterval_sound {α : Type*} [Fintype α] [DecidableEq α]
    (a : α → Interval) (x : α → ℝ) (h : ∀ i, (a i).Contains (x i)) :
    (sumFiniteInterval a).Contains (∑ i, x i) := by
  constructor
  · change ((∑ i, (a i).lo : ℚ) : ℝ) ≤ ∑ i, x i
    push_cast
    exact Finset.sum_le_sum (fun i _ => (h i).1)
  · change (∑ i, x i) ≤ ((∑ i, (a i).hi : ℚ) : ℝ)
    push_cast
    exact Finset.sum_le_sum (fun i _ => (h i).2)

theorem prodFiniteInterval_sound {k : ℕ}
    (a : Fin k → Interval) (x : Fin k → ℝ) (h : ∀ i, (a i).Contains (x i)) :
    (prodFiniteInterval a).Contains (∏ i, x i) := by
  have hh := prodInterval_sound (List.finRange k) a x (fun i _ => h i)
  have heq : ((List.finRange k).map x).prod = ∏ i, x i := by
    simpa using (List.prod_toFinset x (List.nodup_finRange k)).symm
  rwa [heq] at hh

/-- A computable enclosure of the Leibniz determinant. For the 3D affine
basis this is a 4 by 4 determinant; the theorem itself is dimension general. -/
def detInterval {k : ℕ} (A : Matrix (Fin k) (Fin k) Interval) : Interval :=
  sumFiniteInterval (fun σ : Equiv.Perm (Fin k) =>
    Interval.mul (Interval.point (((σ.sign : ℤ) : ℚ)))
      (prodFiniteInterval (fun i => A (σ i) i)))

theorem detInterval_sound {k : ℕ}
    (AI : Matrix (Fin k) (Fin k) Interval) (A : Matrix (Fin k) (Fin k) ℝ)
    (h : ∀ i j, (AI i j).Contains (A i j)) : (detInterval AI).Contains A.det := by
  rw [Matrix.det_apply']
  apply sumFiniteInterval_sound
  intro σ
  apply Interval.mul_sound
  · simpa using Interval.point_sound (((σ.sign : ℤ) : ℚ))
  · exact prodFiniteInterval_sound _ _ (fun i => h (σ i) i)

/-- Cofactor enclosures may be widened and cached once for the container.
Per-point Cramer numerators then need only k interval products and a sum. -/
def adjugateInterval {k : ℕ} (AI : Matrix (Fin k) (Fin k) Interval)
    (i j : Fin k) : Interval :=
  detInterval (AI.updateRow j (fun a => Interval.point (if a = i then 1 else 0)))

theorem adjugateInterval_sound {k : ℕ}
    (AI : Matrix (Fin k) (Fin k) Interval) (A : Matrix (Fin k) (Fin k) ℝ)
    (h : ∀ i j, (AI i j).Contains (A i j)) (i j : Fin k) :
    (adjugateInterval AI i j).Contains (A.adjugate i j) := by
  rw [Matrix.adjugate_apply]
  apply detInterval_sound
  intro a b
  by_cases ha : a = j
  · subst a
    by_cases hb : b = i
    · simpa [Matrix.updateRow_self,Pi.single_apply,hb] using Interval.point_sound 1
    · simpa [Matrix.updateRow_self,Pi.single_apply,hb] using Interval.point_sound 0
  · simpa [Matrix.updateRow_ne ha] using h a b

def cramerInterval {k : ℕ} (HI : Matrix (Fin k) (Fin k) Interval)
    (bI : Fin k → Interval) (j : Fin k) : Interval :=
  sumFiniteInterval (fun a => Interval.mul (HI j a) (bI a))

theorem cramerInterval_sound {k : ℕ}
    (A : Matrix (Fin k) (Fin k) ℝ) (b : Fin k → ℝ)
    (HI : Matrix (Fin k) (Fin k) Interval) (bI : Fin k → Interval)
    (hH : ∀ i j, (HI i j).Contains (A.adjugate i j))
    (hb : ∀ i, (bI i).Contains (b i)) (j : Fin k) :
    (cramerInterval HI bI j).Contains (A.cramer b j) := by
  rw [Matrix.cramer_eq_adjugate_mulVec]
  change (cramerInterval HI bI j).Contains (∑ a, A.adjugate j a * b a)
  exact sumFiniteInterval_sound _ _ (fun a => Interval.mul_sound (hH j a) (hb a))

def sameSignCheck (den num : Interval) : Bool :=
  ((decide (0 < den.lo)) && decide (0 ≤ num.lo)) ||
    ((decide (den.hi < 0)) && decide (num.hi ≤ 0))

theorem sameSignCheck_sound {den num : Interval} {D N : ℝ}
    (hD : den.Contains D) (hN : num.Contains N)
    (h : sameSignCheck den num = true) : D ≠ 0 ∧ 0 ≤ N/D := by
  simp only [sameSignCheck,Bool.or_eq_true,Bool.and_eq_true,decide_eq_true_eq] at h
  rcases h with hp | hn
  · have hdp : (0 : ℝ) < den.lo := by exact_mod_cast hp.1
    have hnp : (0 : ℝ) ≤ num.lo := by exact_mod_cast hp.2
    exact ⟨ne_of_gt (hdp.trans_le hD.1), div_nonneg (hnp.trans hN.1)
      (hdp.le.trans hD.1)⟩
  · have hdn : ((den.hi : ℚ) : ℝ) < 0 := by exact_mod_cast hn.1
    have hnn : ((num.hi : ℚ) : ℝ) ≤ 0 := by exact_mod_cast hn.2
    exact ⟨ne_of_lt (hD.2.trans_lt hdn), div_nonneg_of_nonpos
      (hN.2.trans hnn) (hD.2.trans hdn.le)⟩

theorem corrected_cramer_eq {k : ℕ} (A : Matrix (Fin k) (Fin k) ℝ)
    (b : Fin k → ℝ) (ε : ℝ) (j : Fin k) (hdet : A.det ≠ 0) :
    ε + cramerWeights A b j = ((A.updateCol j b).det + ε*A.det)/A.det := by
  simp only [cramerWeights,Pi.smul_apply,smul_eq_mul,Matrix.cramer_apply]
  field_simp
  ring

theorem corrected_cramer_nonnegative {k : ℕ}
    (A : Matrix (Fin k) (Fin k) ℝ) (b : Fin k → ℝ) (ε : ℝ) (j : Fin k)
    {den num : Interval} (hD : den.Contains A.det)
    (hN : num.Contains ((A.updateCol j b).det + ε*A.det))
    (h : sameSignCheck den num = true) :
    A.det ≠ 0 ∧ 0 ≤ ε + cramerWeights A b j := by
  have hh := sameSignCheck_sound hD hN h
  exact ⟨hh.1, by rw [corrected_cramer_eq A b ε j hh.1]; exact hh.2⟩

def correctedNumeratorInterval {k : ℕ} (DI : Interval)
    (HI : Matrix (Fin k) (Fin k) Interval) (bI : Fin k → Interval)
    (ε : ℚ) (j : Fin k) : Interval :=
  Interval.add (cramerInterval HI bI j) (Interval.mul (Interval.point ε) DI)

theorem correctedNumeratorInterval_sound {k : ℕ}
    (A : Matrix (Fin k) (Fin k) ℝ) (b : Fin k → ℝ) (DI : Interval)
    (HI : Matrix (Fin k) (Fin k) Interval) (bI : Fin k → Interval) (ε : ℚ)
    (hD : DI.Contains A.det)
    (hH : ∀ i j, (HI i j).Contains (A.adjugate i j))
    (hb : ∀ i, (bI i).Contains (b i)) (j : Fin k) :
    (correctedNumeratorInterval DI HI bI ε j).Contains
      ((A.updateCol j b).det + (ε : ℝ)*A.det) := by
  rw [← Matrix.cramer_apply]
  exact Interval.add_sound (cramerInterval_sound A b HI bI hH hb j)
    (Interval.mul_sound (Interval.point_sound ε) hD)

def correctedCramerCheck {k : ℕ} (DI : Interval)
    (HI : Matrix (Fin k) (Fin k) Interval) (bI : Fin k → Interval) (ε : ℚ) : Bool :=
  decide (∀ j, sameSignCheck DI (correctedNumeratorInterval DI HI bI ε j) = true)

theorem correctedCramerCheck_sound {k : ℕ}
    (A : Matrix (Fin k) (Fin k) ℝ) (b : Fin k → ℝ) (DI : Interval)
    (HI : Matrix (Fin k) (Fin k) Interval) (bI : Fin k → Interval) (ε : ℚ)
    (hD : DI.Contains A.det)
    (hH : ∀ i j, (HI i j).Contains (A.adjugate i j))
    (hb : ∀ i, (bI i).Contains (b i))
    (h : correctedCramerCheck DI HI bI ε = true) :
    ∀ j, A.det ≠ 0 ∧ 0 ≤ (ε : ℝ) + cramerWeights A b j := by
  have hh : ∀ j, sameSignCheck DI (correctedNumeratorInterval DI HI bI ε j) = true :=
    of_decide_eq_true h
  intro j
  exact corrected_cramer_nonnegative A b ε j hD
    (correctedNumeratorInterval_sound A b DI HI bI ε hD hH hb j) (hh j)

def augmentedMatrixInterval {d : ℕ} (vI : Fin (d+1) → Fin d → Interval) :
    Matrix (Fin (d+1)) (Fin (d+1)) Interval :=
  fun a j => Fin.cases (Interval.point 1) (fun b => vI j b) a

theorem augmentedMatrixInterval_sound {d : ℕ}
    (vI : Fin (d+1) → Fin d → Interval) (v : Fin (d+1) → Fin d → ℝ)
    (h : ∀ j a, (vI j a).Contains (v j a)) :
    ∀ a j, (augmentedMatrixInterval vI a j).Contains (augmentedMatrix v a j) := by
  intro a j
  refine Fin.cases ?_ (fun b => ?_) a
  · simpa [augmentedMatrixInterval,augmentedMatrix] using Interval.point_sound 1
  · exact h j b

def augmentedRHSInterval {d : ℕ} (mass : ℚ) (xI : Fin d → Interval) : Fin (d+1) → Interval :=
  Fin.cases (Interval.point mass) xI

theorem augmentedRHSInterval_sound {d : ℕ} (mass : ℚ) (xI : Fin d → Interval)
    (x : Fin d → ℝ) (h : ∀ a, (xI a).Contains (x a)) :
    ∀ a, (augmentedRHSInterval mass xI a).Contains (augmentedRHS (mass : ℝ) x a) := by
  intro a
  refine Fin.cases ?_ (fun b => ?_) a
  · exact Interval.point_sound mass
  · exact h b

/-- A reusable outward-rounded determinant/adjugate cache is checked against
the actual interval matrix, so its entries cannot be merely asserted. -/
def basisCacheCheck {k : ℕ} (AI : Matrix (Fin k) (Fin k) Interval)
    (DI : Interval) (HI : Matrix (Fin k) (Fin k) Interval) : Bool :=
  Interval.enclosesCheck (detInterval AI) DI &&
    decide (∀ i j, Interval.enclosesCheck (adjugateInterval AI i j) (HI i j) = true)

theorem basisCacheCheck_sound {k : ℕ}
    (AI : Matrix (Fin k) (Fin k) Interval) (A : Matrix (Fin k) (Fin k) ℝ)
    (DI : Interval) (HI : Matrix (Fin k) (Fin k) Interval)
    (hA : ∀ i j, (AI i j).Contains (A i j))
    (h : basisCacheCheck AI DI HI = true) :
    DI.Contains A.det ∧ ∀ i j, (HI i j).Contains (A.adjugate i j) := by
  have hh : Interval.enclosesCheck (detInterval AI) DI = true ∧
      (∀ i j, Interval.enclosesCheck (adjugateInterval AI i j) (HI i j) = true) := by
    simpa only [basisCacheCheck,Bool.and_eq_true,decide_eq_true_eq] using h
  exact ⟨Interval.enclosesCheck_sound (detInterval_sound AI A hA) hh.1,
    fun i j => Interval.enclosesCheck_sound (adjugateInterval_sound AI A hA i j) (hh.2 i j)⟩

/-- End-to-end geometric meaning of checked interval Cramer bounds: the exact
real point belongs to the exact algebraic container hull, in any dimension. -/
theorem interval_cramer_centered_hull_membership {d m : ℕ}
    (v : Fin m → Fin d → ℝ) (hcenter : (∑ j, v j) = 0)
    (ι : Fin (d+1) → Fin m) (hι : Function.Injective ι)
    (ε : ℚ) (hε : 0 ≤ ε) (x : Fin d → ℝ)
    (DI : Interval) (HI : Matrix (Fin (d+1)) (Fin (d+1)) Interval)
    (bI : Fin (d+1) → Interval)
    (hD : DI.Contains (augmentedMatrix (fun i => v (ι i))).det)
    (hH : ∀ i j, (HI i j).Contains ((augmentedMatrix (fun i => v (ι i))).adjugate i j))
    (hb : ∀ i, (bI i).Contains (augmentedRHS (1-(m : ℝ)*(ε : ℝ)) x i))
    (h : correctedCramerCheck DI HI bI ε = true) : x ∈ vertexBody v := by
  have hh := correctedCramerCheck_sound (augmentedMatrix (fun i => v (ι i)))
    (augmentedRHS (1-(m : ℝ)*(ε : ℝ)) x) DI HI bI ε hD hH hb h
  apply cramer_centered_hull_membership v hcenter ι hι ε
    (by exact_mod_cast hε) x (hh 0).1
  exact fun i => (hh i).2

end PackingCertificates.Algebraic.Simplex

#print axioms PackingCertificates.Algebraic.Simplex.centered_hull_membership
#print axioms PackingCertificates.Algebraic.Simplex.cramerWeights_solution
#print axioms PackingCertificates.Algebraic.Simplex.cramer_centered_hull_membership
#print axioms PackingCertificates.Algebraic.Simplex.detInterval_sound
#print axioms PackingCertificates.Algebraic.Simplex.corrected_cramer_nonnegative
#print axioms PackingCertificates.Algebraic.Simplex.adjugateInterval_sound
#print axioms PackingCertificates.Algebraic.Simplex.correctedCramerCheck_sound
#print axioms PackingCertificates.Algebraic.Simplex.basisCacheCheck_sound
#print axioms PackingCertificates.Algebraic.Simplex.interval_cramer_centered_hull_membership
