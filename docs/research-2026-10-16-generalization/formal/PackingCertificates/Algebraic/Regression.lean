import PackingCertificates.Algebraic.Root
import PackingCertificates.Algebraic.Simplex

/-!
Kernel regression tests for the certificate trust boundary. Invalid root
brackets, square-root bounds, outward enclosures and affine-basis caches must
be rejected, even when a numerical proposal would be convenient.
-/
namespace PackingCertificates.Algebraic.Regression
open PackingCertificates.Algebraic

theorem root_brackets :
    RootSpec.check ⟨[-2, 0, 1], ⟨1, 2⟩⟩ = true ∧
    RootSpec.check ⟨[-2, 0, 1], ⟨2, 3⟩⟩ = false ∧
    RootSpec.check ⟨[-2, 0, 1], ⟨2, 1⟩⟩ = false ∧
    RootSpec.check ⟨[0, -1, 0, 1], ⟨-2, 2⟩⟩ = false := by
  decide +kernel

theorem square_root_enclosures :
    Interval.sqrtCheck ⟨2, 2⟩ ⟨1, 2⟩ = true ∧
    Interval.sqrtCheck ⟨2, 2⟩ ⟨3/2, 2⟩ = false ∧
    Interval.sqrtCheck ⟨2, 2⟩ ⟨-2, -1⟩ = false := by
  decide +kernel

theorem outward_enclosures :
    Interval.enclosesCheck ⟨1, 2⟩ ⟨0, 3⟩ = true ∧
    Interval.enclosesCheck ⟨1, 2⟩ ⟨3/2, 2⟩ = false ∧
    Interval.enclosesCheck ⟨1, 2⟩ ⟨1, 3/2⟩ = false := by
  decide +kernel

theorem quotient_signs :
    Simplex.sameSignCheck ⟨1, 2⟩ ⟨0, 3⟩ = true ∧
    Simplex.sameSignCheck ⟨-2, -1⟩ ⟨-3, 0⟩ = true ∧
    Simplex.sameSignCheck ⟨-1, 1⟩ ⟨1, 2⟩ = false ∧
    Simplex.sameSignCheck ⟨1, 2⟩ ⟨-2, -1⟩ = false := by
  decide +kernel

def identityInterval : Matrix (Fin 1) (Fin 1) Interval :=
  fun _ _ => Interval.point 1
def zeroInterval : Matrix (Fin 1) (Fin 1) Interval :=
  fun _ _ => Interval.point 0

theorem basis_caches :
    Simplex.basisCacheCheck identityInterval (Interval.point 1) identityInterval = true ∧
    Simplex.basisCacheCheck identityInterval (Interval.point 2) identityInterval = false ∧
    Simplex.basisCacheCheck identityInterval (Interval.point 1) zeroInterval = false := by
  decide +kernel

theorem corrected_weights :
    Simplex.correctedCramerCheck (Interval.point 1) identityInterval
      (fun _ : Fin 1 => Interval.point 1) 0 = true ∧
    Simplex.correctedCramerCheck (Interval.point 1) identityInterval
      (fun _ : Fin 1 => Interval.point (-1)) 0 = false := by
  decide +kernel

#print axioms root_brackets
#print axioms square_root_enclosures
#print axioms outward_enclosures
#print axioms quotient_signs
#print axioms basis_caches
#print axioms corrected_weights
end PackingCertificates.Algebraic.Regression
