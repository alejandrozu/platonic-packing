import PackingOptimality.Cubes
import PackingOptimality.NearAxis

/-!
# From Lemma F to the cube centre lemma, in every dimension

If `F_j(Q) = Σᵢ |Qᵢⱼ| (2 - ‖row i‖₁) ≤ 1` for every orthogonal `d × d` matrix and every column (`LemmaF d`),
then a unit `d`-cube placed by any rigid motion inside the cube `[0, s]^d` with `s < 2` contains the centre
`(s/2, …, s/2)` in its interior (`centre_of_lemmaF`). With `cube_plateau_of_centre_lemma` this gives side 2 for
every `2 ≤ n ≤ 2^d`.

The argument is `PROOF.md` §1 of Hosono's `problems/cubes-n-dim` (and `CubeCentre.centre3` in dimension 3):
- the image of the cube spans width `wᵢ = ‖row i‖₁` in coordinate `i`, so its centre is within `(s - wᵢ)/2` of
  `s/2`;
- pulled back by the isometry, the container's centre is within `Σᵢ |Qᵢⱼ| (s - wᵢ)/2 < F_j/2 ≤ 1/2` of the
  cube's centre along each axis `j`.
-/

namespace PackingOptimality.CentreGeneral

open scoped RealInnerProductSpace Pointwise
open Set NearAxis Matrix

variable {d : ℕ}

/-- The standard basis vector `e_k`. -/
noncomputable def eb (k : Fin d) : EuclideanSpace ℝ (Fin d) := EuclideanSpace.single k 1

/-- The matrix `(L e_k)_i` of a linear isometry. -/
noncomputable def matOf (L : EuclideanSpace ℝ (Fin d) ≃ₗᵢ[ℝ] EuclideanSpace ℝ (Fin d)) :
    Matrix (Fin d) (Fin d) ℝ := fun i k => L (eb k) i

theorem inner_sum (u v : EuclideanSpace ℝ (Fin d)) : ⟪u, v⟫ = ∑ i, u i * v i := by
  simp [PiLp.inner_apply, mul_comm]

theorem inner_eb (u : EuclideanSpace ℝ (Fin d)) (k : Fin d) : ⟪u, eb k⟫ = u k := by
  simp [eb, EuclideanSpace.inner_single_right]

theorem eb_apply (a b : Fin d) : (eb a : EuclideanSpace ℝ (Fin d)) b = if b = a then 1 else 0 := by
  simp [eb, PiLp.single_apply]

theorem matOf_symm_apply (L : EuclideanSpace ℝ (Fin d) ≃ₗᵢ[ℝ] EuclideanSpace ℝ (Fin d))
    (y : EuclideanSpace ℝ (Fin d)) (k : Fin d) : L.symm y k = ∑ i, matOf L i k * y i := by
  rw [← inner_eb (L.symm y) k, ← L.inner_map_map, L.apply_symm_apply, inner_sum]
  simp only [matOf, mul_comm]

theorem matOf_apply (L : EuclideanSpace ℝ (Fin d) ≃ₗᵢ[ℝ] EuclideanSpace ℝ (Fin d))
    (x : EuclideanSpace ℝ (Fin d)) (i : Fin d) : L x i = ∑ k, matOf L i k * x k := by
  have h1 : L x i = ⟪x, L.symm (eb i)⟫ := by
    rw [← inner_eb (L x) i, ← L.symm.inner_map_map, L.symm_apply_apply]
  have h2 : ∀ k, L.symm (eb i) k = matOf L i k := fun k => by
    rw [matOf_symm_apply]
    simp [eb_apply]
  rw [h1, inner_sum]
  simp only [h2, mul_comm]

theorem matOf_orth (L : EuclideanSpace ℝ (Fin d) ≃ₗᵢ[ℝ] EuclideanSpace ℝ (Fin d)) :
    (matOf L)ᵀ * matOf L = 1 := by
  ext a b
  have h := L.inner_map_map (eb a) (eb b)
  rw [inner_sum, inner_eb, eb_apply] at h
  simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply, matOf]
  rw [h]
  simp only [eq_comm]

theorem pos_part (a : ℝ) : a * (if 0 ≤ a then 1 else 0) = (a + |a|) / 2 := by
  split_ifs with h
  · rw [abs_of_nonneg h]; ring
  · rw [abs_of_neg (not_le.mp h)]; ring

theorem neg_part (a : ℝ) : a * (if 0 ≤ a then 0 else 1) = (a - |a|) / 2 := by
  split_ifs with h
  · rw [abs_of_nonneg h]; ring
  · rw [abs_of_neg (not_le.mp h)]; ring

theorem smul_cube_coord {s : ℝ} (hs : 0 ≤ s) {y : EuclideanSpace ℝ (Fin d)} (hy : y ∈ s • cube d) (i : Fin d) :
    0 ≤ y i ∧ y i ≤ s := by
  obtain ⟨x, hx, rfl⟩ := Set.mem_smul_set.mp hy
  simp only [PiLp.smul_apply, smul_eq_mul]
  exact ⟨mul_nonneg hs (hx i).1, mul_le_of_le_one_right hs (hx i).2⟩

/-- **Lemma F for matrices with rows of ℓ¹ norm at most 2 gives the cube centre lemma**, in any dimension. Only
such matrices occur: the rows of a unit cube placed in a cube of side `s < 2` have ℓ¹ norm at most `s`. -/
theorem centre_of_lemmaF_rows
    (hF : ∀ Q : Matrix (Fin d) (Fin d) ℝ, Q * Qᵀ = 1 → (∀ i, rowL1 Q i ≤ 2) → ∀ j, Fcol Q j ≤ 1)
    (s : ℝ) (hs0 : 0 ≤ s) (hs : s < 2)
    (g : EuclideanSpace ℝ (Fin d) ≃ᵃⁱ[ℝ] EuclideanSpace ℝ (Fin d)) (hg : g '' cube d ⊆ s • cube d) :
    (s / 2) • WithLp.toLp 2 (fun _ => (1 : ℝ)) ∈ interior (g '' cube d) := by
  set L := g.linearIsometryEquiv with hLdef
  set A := matOf L with hA
  set m : EuclideanSpace ℝ (Fin d) := (s / 2) • WithLp.toLp 2 (fun _ => (1 : ℝ)) with hm
  have hgx : ∀ x, g x = L x + g 0 := fun x => by have := g.map_vadd 0 x; simpa using this
  have hAt : Aᵀ * A = 1 := matOf_orth L
  have hAA : A * Aᵀ = 1 := mul_eq_one_comm.mp hAt
  have col : ∀ a b, ∑ i, A i a * A i b = if a = b then 1 else 0 := fun a b => by
    have h := congrFun (congrFun hAt a) b
    simpa only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply] using h
  -- each coordinate of the image of a point of the cube lies in `[0, s]`
  have vert : ∀ t : Fin d → ℝ, (∀ k, 0 ≤ t k ∧ t k ≤ 1) → ∀ i,
      0 ≤ ∑ k, A i k * t k + g 0 i ∧ ∑ k, A i k * t k + g 0 i ≤ s := by
    intro t ht i
    have hmem : g (WithLp.toLp 2 t) ∈ s • cube d := hg ⟨_, fun k => by simpa using ht k, rfl⟩
    have := smul_cube_coord hs0 hmem i
    rw [hgx, PiLp.add_apply, matOf_apply] at this
    simpa using this
  -- the centre of the image is within `(s - wᵢ)/2` of `s/2`
  have bnd : ∀ i, |s / 2 - (g 0 i + (∑ k, A i k) / 2)| ≤ (s - ∑ k, |A i k|) / 2 := by
    intro i
    have up := (vert (fun k => if 0 ≤ A i k then 1 else 0) (fun k => by split_ifs <;> norm_num) i).2
    have lo := (vert (fun k => if 0 ≤ A i k then 0 else 1) (fun k => by split_ifs <;> norm_num) i).1
    simp only [pos_part, neg_part, ← Finset.sum_div, Finset.sum_add_distrib, Finset.sum_sub_distrib] at up lo
    rw [abs_le]; constructor <;> linarith
  -- the preimage of the centre
  obtain ⟨x, hx⟩ : ∃ x, x = g.symm m := ⟨_, rfl⟩
  have hgxm : g x = m := by rw [hx]; exact g.apply_symm_apply m
  have hLx : L x = m - g 0 := by rw [← hgxm, hgx x, add_sub_cancel_right]
  have hxk : ∀ k, x k = ∑ i, A i k * (s / 2 - g 0 i) := by
    intro k
    have h1 : x = L.symm (m - g 0) := by rw [← hLx, L.symm_apply_apply]
    rw [h1, matOf_symm_apply]
    simp [hm, hA]
  have key : ∀ k, |x k - 1 / 2| < 1 / 2 := by
    intro k
    set dd : Fin d → ℝ := fun i => s / 2 - (g 0 i + (∑ l, A i l) / 2) with hdd
    -- `x_k - 1/2 = Σᵢ A_ik dᵢ`, by orthonormality of the columns
    have e1 : x k - 1 / 2 = ∑ i, A i k * dd i := by
      have hcs : ∑ i, A i k * (∑ l, A i l) = 1 := by
        simp only [Finset.mul_sum]
        rw [Finset.sum_comm]
        simp only [col k, Finset.sum_ite_eq, Finset.mem_univ, if_true]
      rw [hxk k]
      simp only [hdd, mul_sub, mul_add, Finset.sum_sub_distrib, Finset.sum_add_distrib, mul_div_assoc',
        ← Finset.sum_div, hcs]
      ring
    have e2 : |∑ i, A i k * dd i| ≤ ∑ i, |A i k| * ((s - ∑ l, |A i l|) / 2) := by
      calc |∑ i, A i k * dd i| ≤ ∑ i, |A i k * dd i| := Finset.abs_sum_le_sum_abs _ _
        _ ≤ ∑ i, |A i k| * ((s - ∑ l, |A i l|) / 2) := by
          apply Finset.sum_le_sum; intro i _
          rw [abs_mul]; exact mul_le_mul_of_nonneg_left (bnd i) (abs_nonneg _)
    have hrows : ∀ i, rowL1 A i ≤ 2 := fun i => by
      have h1 := abs_nonneg (s / 2 - (g 0 i + (∑ k, A i k) / 2))
      have h2 := bnd i
      simp only [rowL1, l1]
      linarith
    have hFk := hF A hAA hrows k
    have hF' : ∑ i, |A i k| * (2 - ∑ l, |A i l|) ≤ 1 := by simpa [Fcol, rowL1, l1] using hFk
    -- `Σᵢ |A_ik| ≥ Σᵢ A_ik² = 1`
    have hsum : 1 ≤ ∑ i, |A i k| := by
      have hc := col k k; rw [if_pos rfl] at hc
      calc (1 : ℝ) = ∑ i, A i k * A i k := hc.symm
        _ ≤ ∑ i, |A i k| := by
          apply Finset.sum_le_sum; intro i _
          have hle : A i k * A i k ≤ 1 := by
            rw [← hc]
            exact Finset.single_le_sum (f := fun i => A i k * A i k) (fun j _ => mul_self_nonneg _)
              (Finset.mem_univ i)
          have ha1 : |A i k| ≤ 1 := by
            nlinarith [abs_nonneg (A i k), abs_mul_abs_self (A i k)]
          calc A i k * A i k = |A i k| * |A i k| := (abs_mul_abs_self _).symm
            _ ≤ |A i k| * 1 := mul_le_mul_of_nonneg_left ha1 (abs_nonneg _)
            _ = |A i k| := mul_one _
    have e3 : ∑ i, |A i k| * ((s - ∑ l, |A i l|) / 2) =
        (∑ i, |A i k| * (2 - ∑ l, |A i l|) - (2 - s) * ∑ i, |A i k|) / 2 := by
      rw [Finset.mul_sum, ← Finset.sum_sub_distrib, Finset.sum_div]
      apply Finset.sum_congr rfl; intro i _; ring
    rw [e1]
    have : 0 < (2 - s) * ∑ i, |A i k| := mul_pos (by linarith) (by linarith)
    linarith
  have hU : ∀ k, 0 < x k ∧ x k < 1 := fun k => by
    obtain ⟨h1, h2⟩ := abs_lt.mp (key k)
    exact ⟨by linarith, by linarith⟩
  -- the open cube maps onto an open subset of the image that contains the centre
  let U : Set (EuclideanSpace ℝ (Fin d)) := {y | ∀ k, 0 < y k ∧ y k < 1}
  have hUo : IsOpen U := by
    have : U = ⋂ i, ((fun y : EuclideanSpace ℝ (Fin d) => y i) ⁻¹' Ioo 0 1) := by ext y; simp [U]
    rw [this]
    exact isOpen_iInter_of_finite fun i => isOpen_Ioo.preimage ((EuclideanSpace.proj (𝕜 := ℝ) i).continuous)
  have himg : IsOpen (g '' U) := by simpa using g.toHomeomorph.isOpenMap U hUo
  have hsub : g '' U ⊆ g '' cube d := image_mono fun y hy k => ⟨(hy k).1.le, (hy k).2.le⟩
  exact interior_maximal hsub himg ⟨x, hU, hgxm⟩

/-- **Lemma F gives the cube centre lemma**, in any dimension. -/
theorem centre_of_lemmaF (hF : LemmaF d) (s : ℝ) (hs0 : 0 ≤ s) (hs : s < 2)
    (g : EuclideanSpace ℝ (Fin d) ≃ᵃⁱ[ℝ] EuclideanSpace ℝ (Fin d)) (hg : g '' cube d ⊆ s • cube d) :
    (s / 2) • WithLp.toLp 2 (fun _ => (1 : ℝ)) ∈ interior (g '' cube d) :=
  centre_of_lemmaF_rows (fun Q hQ _ j => hF Q hQ j) s hs0 hs g hg

end PackingOptimality.CentreGeneral
