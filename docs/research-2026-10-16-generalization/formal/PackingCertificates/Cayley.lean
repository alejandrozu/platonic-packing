import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.Rat.Cast.Order
import Mathlib.Data.Real.Basic

/-!
# Exact source binding and proper orientation for Cayley placements

A rational matrix supplied by an untrusted exporter is tied to its original
skew-symmetric Cayley parameters by checking an explicit inverse and the full
matrix identity. Determinant one is proved generically, rather than evaluating
the factorial-size determinant formula independently for every record.
-/

namespace PackingCertificates.Cayley

open scoped BigOperators

abbrev QMatrix (d : ℕ) := Matrix (Fin d) (Fin d) ℚ

structure Certificate (d : ℕ) where
  skew : QMatrix d
  signs : Fin d → ℚ
  inverse : QMatrix d
  rotation : QMatrix d

/-- The diagonal sign changes permit all Cayley charts used by the catalogue.
The explicit inverse makes the check finite exact rational arithmetic.
-/
def check {d : ℕ} (c : Certificate d) : Bool :=
  decide (c.skew.transpose = -c.skew) &&
  decide (∀ i, c.signs i = 1 ∨ c.signs i = -1) &&
  decide (∏ i, c.signs i = 1) &&
  decide (c.inverse * (1 - c.skew) = 1) &&
  decide (c.rotation = Matrix.diagonal c.signs * c.inverse * (1 + c.skew))

/-- The exact signed Cayley expression; inverse is Lean's matrix inverse. -/
noncomputable def expression {d : ℕ} (s : QMatrix d) (signs : Fin d → ℚ) :
    QMatrix d :=
  Matrix.diagonal signs * (1 - s)⁻¹ * (1 + s)

def Valid {d : ℕ} (c : Certificate d) : Prop :=
  c.skew.transpose = -c.skew ∧
  (∀ i, c.signs i = 1 ∨ c.signs i = -1) ∧
  (∏ i, c.signs i = 1) ∧
  c.inverse = (1 - c.skew)⁻¹ ∧
  c.rotation = expression c.skew c.signs ∧
  Matrix.det c.rotation = 1

theorem determinant_one {d : ℕ} (s ai r : QMatrix d) (signs : Fin d → ℚ)
    (hskew : s.transpose = -s) (hprod : ∏ i, signs i = 1)
    (hinverse : ai * (1 - s) = 1)
    (hrotation : r = Matrix.diagonal signs * ai * (1 + s)) :
    Matrix.det r = 1 := by
  have htranspose : (1 - s).transpose = 1 + s := by
    rw [Matrix.transpose_sub, Matrix.transpose_one, hskew]
    simp
  have hdet : Matrix.det (1 + s) = Matrix.det (1 - s) := by
    rw [← htranspose, Matrix.det_transpose]
  have hinvdet : Matrix.det ai * Matrix.det (1 - s) = 1 := by
    rw [← Matrix.det_mul, hinverse, Matrix.det_one]
  rw [hrotation, Matrix.det_mul, Matrix.det_mul, Matrix.det_diagonal, hprod,
    one_mul, hdet]
  exact hinvdet

theorem check_sound {d : ℕ} (c : Certificate d) (h : check c = true) :
    Valid c := by
  have hh := h
  simp only [check, Bool.and_eq_true, decide_eq_true_eq] at hh
  have hskew := hh.1.1.1.1
  have hsigns := hh.1.1.1.2
  have hprod := hh.1.1.2
  have hinv := hh.1.2
  have hrot := hh.2
  have hinverse : c.inverse = (1 - c.skew)⁻¹ :=
    (Matrix.inv_eq_left_inv hinv).symm
  refine ⟨hskew, hsigns, hprod, hinverse, ?_, ?_⟩
  · rw [expression, ← hinverse]
    exact hrot
  · exact determinant_one c.skew c.inverse c.rotation c.signs hskew hprod hinv hrot

/-- The orientation assertion applies to the actual real placement matrix. -/
theorem determinant_real {d : ℕ} (c : Certificate d) (h : check c = true) :
    Matrix.det (fun i j => (c.rotation i j : ℝ)) = 1 := by
  have hd := (check_sound c h).2.2.2.2.2
  have hc := Rat.cast_det (F := ℝ) c.rotation
  rw [hd] at hc
  have hmap : (fun i j => (c.rotation i j : ℝ)) =
      c.rotation.map (fun q => (q : ℝ)) := by
    funext i j
    rfl
  rw [hmap]
  simpa only [Rat.cast_one] using hc.symm

end PackingCertificates.Cayley
