import PackingCertificates.Algebraic.Placement
import PackingCertificates.Algebraic.QuadraticScale

/-!
Polynomial-size inverse-basis certificates over Q(√r).

The checker multiplies rational coefficient pairs, not real approximations.
After embedding at an actual root α²=r, its checked matrix inverse is an exact
real inverse. A common positive scale is handled by diagonal conjugation.
This avoids the factorial determinant checker for ND affine bases.
-/

namespace PackingCertificates.Algebraic.QuadraticInverse

open scoped BigOperators Matrix

abbrev PairQ := ℚ × ℚ

def product (r : ℚ) (x y : PairQ) : PairQ :=
  (x.1*y.1+r*x.2*y.2,x.1*y.2+x.2*y.1)

def embed (α : ℝ) (x : PairQ) : ℝ := (x.1 : ℝ)+(x.2 : ℝ)*α

noncomputable def embedAdd (α : ℝ) : PairQ →+ ℝ where
  toFun := embed α
  map_zero' := by simp [embed]
  map_add' x y := by simp only [embed,Prod.fst_add,Prod.snd_add,Rat.cast_add]; ring

theorem embed_product (r : ℚ) (α : ℝ) (hα : α^2 = (r : ℝ)) (x y : PairQ) :
    embed α (product r x y) = embed α x * embed α y := by
  simp only [embed,product,Rat.cast_add,Rat.cast_mul]
  rw [← hα]
  ring

def inverseCheck {k : ℕ} (r : ℚ)
    (A B : Matrix (Fin k) (Fin k) PairQ) : Bool :=
  decide (∀ i j, (∑ a, product r (A i a) (B a j)) = if i = j then (1,0) else (0,0))

def embedMatrix {k : ℕ} (α : ℝ) (A : Matrix (Fin k) (Fin k) PairQ) :
    Matrix (Fin k) (Fin k) ℝ := fun i j => embed α (A i j)

theorem inverseCheck_sound {k : ℕ} (r : ℚ) (α : ℝ) (hα : α^2 = (r : ℝ))
    (A B : Matrix (Fin k) (Fin k) PairQ) (h : inverseCheck r A B = true) :
    (embedMatrix α A) * (embedMatrix α B) = 1 := by
  have hh : ∀ i j, (∑ a, product r (A i a) (B a j)) =
      if i = j then (1,0) else (0,0) := of_decide_eq_true h
  ext i j
  rw [Matrix.mul_apply,Matrix.one_apply]
  change (∑ a, embed α (A i a)*embed α (B a j)) = if i = j then 1 else 0
  calc
    (∑ a, embed α (A i a)*embed α (B a j)) =
        ∑ a, embed α (product r (A i a) (B a j)) := by
      apply Finset.sum_congr rfl
      intro a _
      exact (embed_product r α hα _ _).symm
    _ = embed α (∑ a, product r (A i a) (B a j)) := by
      exact (map_sum (embedAdd α) _ _).symm
    _ = embed α (if i = j then (1,0) else (0,0)) := by rw [hh i j]
    _ = if i = j then (1 : ℝ) else 0 := by split_ifs <;> norm_num [embed]

def rowScale (d : ℕ) (scale : ℝ) : Matrix (Fin (d+1)) (Fin (d+1)) ℝ :=
  Matrix.diagonal (Fin.cases 1 (fun _ => scale))

theorem rowScale_inverse (d : ℕ) (scale : ℝ) (hscale : scale ≠ 0) :
    rowScale d scale * rowScale d scale⁻¹ = 1 := by
  have hf : (fun i : Fin (d+1) => Fin.cases 1 (fun _ => scale) i *
      Fin.cases 1 (fun _ => scale⁻¹) i) = fun _ => (1 : ℝ) := by
    funext i
    refine Fin.cases ?_ (fun _ => ?_) i
    · simp
    · simp [mul_inv_cancel₀ hscale]
  simpa only [rowScale,Matrix.diagonal_mul_diagonal,hf,Matrix.diagonal_one]

theorem augmentedMatrix_scale {d : ℕ} (v : Fin (d+1) → Fin d → ℝ) (scale : ℝ) :
    Simplex.augmentedMatrix (fun j a => scale*v j a) =
      rowScale d scale * Simplex.augmentedMatrix v := by
  ext i j
  rw [rowScale,Matrix.diagonal_mul]
  refine Fin.cases ?_ (fun a => ?_) i
  · simp [Simplex.augmentedMatrix]
  · simp [Simplex.augmentedMatrix]

noncomputable def scaledInverse {d : ℕ}
    (B : Matrix (Fin (d+1)) (Fin (d+1)) ℝ) (scale : ℝ) :
    Matrix (Fin (d+1)) (Fin (d+1)) ℝ := B * rowScale d scale⁻¹

theorem scaledInverse_sound {d : ℕ} (v : Fin (d+1) → Fin d → ℝ)
    (B : Matrix (Fin (d+1)) (Fin (d+1)) ℝ)
    (hB : Simplex.augmentedMatrix v * B = 1) (scale : ℝ) (hscale : scale ≠ 0) :
    Simplex.augmentedMatrix (fun j a => scale*v j a) * scaledInverse B scale = 1 := by
  rw [augmentedMatrix_scale,scaledInverse]
  calc
    (rowScale d scale * Simplex.augmentedMatrix v) * (B * rowScale d scale⁻¹) =
        rowScale d scale * (Simplex.augmentedMatrix v * B) * rowScale d scale⁻¹ := by
      simp only [Matrix.mul_assoc]
    _ = rowScale d scale * rowScale d scale⁻¹ := by rw [hB,Matrix.mul_one]
    _ = 1 := rowScale_inverse d scale hscale

def embeddingInterval (a : Interval) (x : PairQ) : Interval :=
  Interval.add (Interval.point x.1) (Interval.mul (Interval.point x.2) a)

theorem embeddingInterval_sound (a : Interval) (α : ℝ) (h : a.Contains α) (x : PairQ) :
    (embeddingInterval a x).Contains (embed α x) :=
  Interval.add_sound (Interval.point_sound x.1) (Interval.mul_sound (Interval.point_sound x.2) h)

def scaledInverseInterval {d : ℕ} (a : Interval)
    (B : Matrix (Fin (d+1)) (Fin (d+1)) PairQ) (scaleI : Interval)
    (i j : Fin (d+1)) : Interval :=
  Interval.mul (embeddingInterval a (B i j))
    (Fin.cases (Interval.point 1) (fun _ => Interval.reciprocal scaleI) j)

theorem scaledInverseInterval_sound {d : ℕ} (a : Interval) (α : ℝ) (hα : a.Contains α)
    (B : Matrix (Fin (d+1)) (Fin (d+1)) PairQ) (scaleI : Interval) (scale : ℝ)
    (hscale : scaleI.Contains scale) (hpos : 0 < scaleI.lo) (i j : Fin (d+1)) :
    (scaledInverseInterval a B scaleI i j).Contains
      (scaledInverse (fun i j => embed α (B i j)) scale i j) := by
  rw [scaledInverse,rowScale,Matrix.mul_diagonal]
  apply Interval.mul_sound (embeddingInterval_sound a α hα (B i j))
  refine Fin.cases ?_ (fun _ => ?_) j
  · simpa using Interval.point_sound 1
  · simpa only [Fin.cases_succ,one_div] using Interval.reciprocal_sound hscale hpos

def weightsCheck {k : ℕ} (BI : Matrix (Fin k) (Fin k) Interval)
    (bI : Fin k → Interval) (ε : ℚ) : Bool :=
  decide (∀ j, 0 ≤ (Interval.add (Interval.point ε)
    (Simplex.cramerInterval BI bI j)).lo)

theorem weightsCheck_sound {k : ℕ} (BI : Matrix (Fin k) (Fin k) Interval)
    (B : Matrix (Fin k) (Fin k) ℝ) (bI : Fin k → Interval) (b : Fin k → ℝ)
    (hB : ∀ i j, (BI i j).Contains (B i j))
    (hb : ∀ i, (bI i).Contains (b i)) (ε : ℚ) (h : weightsCheck BI bI ε = true) :
    ∀ j, 0 ≤ (ε : ℝ) + (B *ᵥ b) j := by
  have hh : ∀ j, 0 ≤ (Interval.add (Interval.point ε) (Simplex.cramerInterval BI bI j)).lo :=
    of_decide_eq_true h
  intro j
  have hs := Simplex.sumFiniteInterval_sound
    (fun a => Interval.mul (BI j a) (bI a))
    (fun a => B j a * b a) (fun a => Interval.mul_sound (hB j a) (hb a))
  have hs' := Interval.add_sound (Interval.point_sound ε) hs
  have hl : (0 : ℝ) ≤ (Interval.add (Interval.point ε) (Simplex.cramerInterval BI bI j)).lo := by
    exact_mod_cast hh j
  exact hl.trans hs'.1

theorem inverse_centered_hull_membership {d m : ℕ}
    (v : Fin m → Fin d → ℝ) (hcenter : (∑ j, v j) = 0)
    (ι : Fin (d+1) → Fin m) (hι : Function.Injective ι)
    (ε : ℚ) (hε : 0 ≤ ε) (x : Fin d → ℝ)
    (B : Matrix (Fin (d+1)) (Fin (d+1)) ℝ)
    (hB : Simplex.augmentedMatrix (fun i => v (ι i)) * B = 1)
    (BI : Matrix (Fin (d+1)) (Fin (d+1)) Interval) (bI : Fin (d+1) → Interval)
    (hBI : ∀ i j, (BI i j).Contains (B i j))
    (hb : ∀ i, (bI i).Contains (Simplex.augmentedRHS (1-(m : ℝ)*(ε : ℝ)) x i))
    (h : weightsCheck BI bI ε = true) : x ∈ vertexBody v := by
  let b := Simplex.augmentedRHS (1-(m : ℝ)*(ε : ℝ)) x
  have hsolution : Simplex.augmentedMatrix (fun i => v (ι i)) *ᵥ (B *ᵥ b) = b := by
    rw [Matrix.mulVec_mulVec,hB,Matrix.one_mulVec]
  exact Simplex.centered_hull_membership v hcenter ι hι ε (by exact_mod_cast hε) (B *ᵥ b)
    (weightsCheck_sound BI B bI b hBI hb ε h)
    (Simplex.augmented_solution_mass _ _ _ _ hsolution) x
    (Simplex.augmented_solution_point _ _ _ _ hsolution)

end PackingCertificates.Algebraic.QuadraticInverse

#print axioms PackingCertificates.Algebraic.QuadraticInverse.inverseCheck_sound
#print axioms PackingCertificates.Algebraic.QuadraticInverse.scaledInverse_sound
#print axioms PackingCertificates.Algebraic.QuadraticInverse.inverse_centered_hull_membership
