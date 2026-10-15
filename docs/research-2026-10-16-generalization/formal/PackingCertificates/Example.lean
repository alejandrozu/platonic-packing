import PackingCertificates.Core
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# A completely instantiated exact witness

Two axis-aligned unit cubes, centred at `(-3/4,0,0)` and `(3/4,0,0)`, fit
inside the cube `[-5/4,5/4]^3`. Their separating gap along the first axis is
`1/2`. All 96 vertex/face inequalities and both ordered pair certificates
are discharged by exact arithmetic. This deliberately simple example tests
the formal interface; it makes no record or optimality claim.
-/

noncomputable section

namespace PackingCertificates.Example

abbrev Space := Fin 3 → ℝ

def cubeVertex (p : Fin 8) : Space :=
  ![![-1/2, -1/2, -1/2], ![-1/2, -1/2, 1/2],
    ![-1/2, 1/2, -1/2], ![-1/2, 1/2, 1/2],
    ![1/2, -1/2, -1/2], ![1/2, -1/2, 1/2],
    ![1/2, 1/2, -1/2], ![1/2, 1/2, 1/2]] p

def placedCube (i : Fin 2) (p : Fin 8) : Space :=
  cubeVertex p + if i = 0 then ![-3/4, 0, 0] else ![3/4, 0, 0]

def coord (i : Fin 3) : Space →ₗ[ℝ] ℝ := LinearMap.proj i

def cubeWalls : Fin 6 → Halfspace Space :=
  ![⟨coord 0, 5/4⟩, ⟨coord 1, 5/4⟩, ⟨coord 2, 5/4⟩,
    ⟨-coord 0, 5/4⟩, ⟨-coord 1, 5/4⟩, ⟨-coord 2, 5/4⟩]

theorem two_cube_certificate :
    FinitePackingCertificate (fun _ : Fin 2 => 8) placedCube cubeWalls := by
  constructor
  · intro i p f
    fin_cases i <;> fin_cases p <;> fin_cases f <;>
      norm_num [cubeWalls, coord, placedCube, cubeVertex, LinearMap.proj_apply, Matrix.cons_val_two, Matrix.vecHead, Matrix.vecTail]
  · intro i j hij
    fin_cases i <;> fin_cases j
    · exact False.elim (hij rfl)
    · refine ⟨coord 0, -1/4, 1/4, by norm_num, ?_, ?_⟩
      · intro p
        fin_cases p <;>
          norm_num [coord, placedCube, cubeVertex, LinearMap.proj_apply, Matrix.cons_val_two, Matrix.vecHead, Matrix.vecTail]
      · intro p
        fin_cases p <;>
          norm_num [coord, placedCube, cubeVertex, LinearMap.proj_apply, Matrix.cons_val_two, Matrix.vecHead, Matrix.vecTail]
    · refine ⟨-coord 0, -1/4, 1/4, by norm_num, ?_, ?_⟩
      · intro p
        fin_cases p <;>
          norm_num [coord, placedCube, cubeVertex, LinearMap.proj_apply, Matrix.cons_val_two, Matrix.vecHead, Matrix.vecTail]
      · intro p
        fin_cases p <;>
          norm_num [coord, placedCube, cubeVertex, LinearMap.proj_apply, Matrix.cons_val_two, Matrix.vecHead, Matrix.vecTail]
    · exact False.elim (hij rfl)

/-- Entire closed cubes, not just their corner lists, are contained and disjoint. -/
theorem two_cube_packing :
    (∀ i, vertexBody (placedCube i) ⊆ container cubeWalls) ∧
      Pairwise (fun i j => Disjoint (vertexBody (placedCube i))
        (vertexBody (placedCube j))) :=
  finite_certificate_sound two_cube_certificate

end PackingCertificates.Example
