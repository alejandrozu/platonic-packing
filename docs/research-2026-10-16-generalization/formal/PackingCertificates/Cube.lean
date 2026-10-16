import PackingCertificates.Core
import Mathlib.Analysis.Convex.Combination
import Mathlib.Analysis.Convex.Segment
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-!
# Canonical unit-cube geometry

The vertices below denote the usual unit cube, rather than an unrelated finite
point set.  The convex hull is exactly the coordinate box.  The scale/translation
lemma identifies a side-`s` cube, centred at `c`, with its coordinate inequalities.
-/

noncomputable section

namespace PackingCertificates.Cube

abbrev Space := Fin 3 → ℝ

/-- The quaternion denominator.  A valid placement must reject zero quaternions. -/
def quaternionNormSq (q : Fin 4 → ℚ) : ℚ :=
  q 0 * q 0 + q 1 * q 1 + q 2 * q 2 + q 3 * q 3

/-- The exact homogeneous quaternion matrix divided by its squared norm.
This definition preserves the input quaternion even when it is not normalized.
The catalogue checker separately proves nonzero norm, orthogonality and `det=1`.
-/
def quaternionMatrix (q : Fin 4 → ℚ) : Fin 3 → Fin 3 → ℚ :=
  let w := q 0
  let x := q 1
  let y := q 2
  let z := q 3
  let n := quaternionNormSq q
  ![![(w*w+x*x-y*y-z*z)/n, 2*(x*y-w*z)/n, 2*(x*z+w*y)/n],
    ![2*(x*y+w*z)/n, (w*w-x*x+y*y-z*z)/n, 2*(y*z-w*x)/n],
    ![2*(x*z-w*y)/n, 2*(y*z+w*x)/n, (w*w-x*x-y*y+z*z)/n]]

/-- Explicit 3-by-3 determinant, used by the rational proper-rotation check. -/
def determinant3 (r : Fin 3 → Fin 3 → ℚ) : ℚ :=
  r 0 0 * (r 1 1 * r 2 2 - r 1 2 * r 2 1) -
  r 0 1 * (r 1 0 * r 2 2 - r 1 2 * r 2 0) +
  r 0 2 * (r 1 0 * r 2 1 - r 1 1 * r 2 0)

theorem determinant3_eq_det (r : Fin 3 → Fin 3 → ℚ) :
    determinant3 r = Matrix.det r := by
  rw [Matrix.det_fin_three]
  dsimp [determinant3]
  ring

theorem determinant3_real (r : Fin 3 → Fin 3 → ℚ) :
    Matrix.det (fun a b => (r a b : ℝ)) = (determinant3 r : ℝ) := by
  simp only [determinant3, Matrix.det_fin_three, Rat.cast_add, Rat.cast_sub, Rat.cast_mul]
  ring

def vertex (p : Fin 8) : Space :=
  ![![-1/2, -1/2, -1/2], ![-1/2, -1/2, 1/2],
    ![-1/2, 1/2, -1/2], ![-1/2, 1/2, 1/2],
    ![1/2, -1/2, -1/2], ![1/2, -1/2, 1/2],
    ![1/2, 1/2, -1/2], ![1/2, 1/2, 1/2]] p

def unitBox : Set Space := {x | ∀ a, -(1:ℝ)/2 ≤ x a ∧ x a ≤ 1/2}

theorem range_vertex :
    Set.range vertex = Set.univ.pi (fun _ : Fin 3 => ({-(1:ℝ)/2, 1/2} : Set ℝ)) := by
  ext x
  constructor
  · rintro ⟨p, rfl⟩ a _
    fin_cases p <;> fin_cases a <;> first | exact Or.inl rfl | exact Or.inr rfl
  · intro hx
    have h0 := hx 0 (Set.mem_univ 0)
    have h1 := hx 1 (Set.mem_univ 1)
    have h2 := hx 2 (Set.mem_univ 2)
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at h0 h1 h2
    rcases h0 with h0 | h0 <;> rcases h1 with h1 | h1 <;> rcases h2 with h2 | h2
    · exact ⟨0, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩
    · exact ⟨1, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩
    · exact ⟨2, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩
    · exact ⟨3, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩
    · exact ⟨4, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩
    · exact ⟨5, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩
    · exact ⟨6, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩
    · exact ⟨7, by funext a; fin_cases a; exact h0.symm; exact h1.symm; exact h2.symm⟩

theorem vertexBody_eq_unitBox : vertexBody vertex = unitBox := by
  rw [vertexBody, range_vertex, convexHull_pi]
  have h : convexHull ℝ ({-(1:ℝ)/2, 1/2} : Set ℝ) = Set.Icc (-(1:ℝ)/2) (1/2) := by
    rw [convexHull_pair, segment_eq_Icc (by norm_num)]
  simp only [h]
  ext x
  simp [unitBox, Set.mem_pi]

def placedBox (c : Space) (s : ℝ) : Set Space :=
  {x | ∀ a, c a - s/2 ≤ x a ∧ x a ≤ c a + s/2}

def coord (a : Fin 3) : Space →ₗ[ℝ] ℝ := LinearMap.proj a

/-- Positive-coordinate faces first, then negative-coordinate faces. -/
def walls (c : Space) (s : ℝ) : Fin 6 → Halfspace Space :=
  ![⟨coord 0, c 0 + s/2⟩, ⟨coord 1, c 1 + s/2⟩, ⟨coord 2, c 2 + s/2⟩,
    ⟨-coord 0, -c 0 + s/2⟩, ⟨-coord 1, -c 1 + s/2⟩, ⟨-coord 2, -c 2 + s/2⟩]

theorem container_walls (c : Space) (s : ℝ) :
    container (walls c s) = placedBox c s := by
  ext x
  constructor
  · intro hx
    have hp0 : x 0 ≤ c 0 + s/2 := hx 0
    have hp1 : x 1 ≤ c 1 + s/2 := hx 1
    have hp2 : x 2 ≤ c 2 + s/2 := hx 2
    have hn0 : -x 0 ≤ -c 0 + s/2 := hx 3
    have hn1 : -x 1 ≤ -c 1 + s/2 := hx 4
    have hn2 : -x 2 ≤ -c 2 + s/2 := hx 5
    intro a
    fin_cases a <;> dsimp <;> constructor <;> linarith
  · intro hx f
    have h0 := hx 0
    have h1 := hx 1
    have h2 := hx 2
    fin_cases f
    · change x 0 ≤ c 0 + s/2
      exact h0.2
    · change x 1 ≤ c 1 + s/2
      exact h1.2
    · change x 2 ≤ c 2 + s/2
      exact h2.2
    · change -x 0 ≤ -c 0 + s/2
      linarith [h0.1]
    · change -x 1 ≤ -c 1 + s/2
      linarith [h1.1]
    · change -x 2 ≤ -c 2 + s/2
      linarith [h2.1]

theorem image_unitBox (c : Space) (s : ℝ) (hs : 0 < s) :
    (fun x : Space => c + s • x) '' unitBox = placedBox c s := by
  ext x
  constructor
  · rintro ⟨y, hy, rfl⟩ a
    have ha := hy a
    change c a - s / 2 ≤ c a + s * y a ∧ c a + s * y a ≤ c a + s / 2
    constructor <;> nlinarith
  · intro hx
    refine ⟨fun a => (x a - c a) / s, ?_, ?_⟩
    · intro a
      have ha := hx a
      constructor
      · apply (le_div_iff₀ hs).mpr
        linarith
      · apply (div_le_iff₀ hs).mpr
        linarith
    · funext a
      change c a + s * ((x a - c a) / s) = x a
      rw [mul_div_cancel₀ _ (ne_of_gt hs)]
      ring

theorem image_vertexBody (c : Space) (s : ℝ) (hs : 0 < s) :
    (fun x : Space => c + s • x) '' vertexBody vertex = placedBox c s := by
  rw [vertexBody_eq_unitBox]
  exact image_unitBox c s hs

theorem container_walls_eq_image (c : Space) (s : ℝ) (hs : 0 < s) :
    container (walls c s) =
      (fun x : Space => c + s • x) '' vertexBody vertex := by
  rw [container_walls, image_vertexBody c s hs]

end PackingCertificates.Cube


