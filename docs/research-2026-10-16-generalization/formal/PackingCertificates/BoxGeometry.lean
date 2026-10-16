import PackingCertificates.TemplateData
import Mathlib.Analysis.Convex.Combination
import Mathlib.Analysis.Convex.Segment
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-!
Dimension-independent identification of canonical hypercube vertex hulls with
their ordinary coordinate boxes.  Finite rational checks identify the actual
frozen 4D, 5D and 6D template arrays with every sign corner; no H=V assumption
or external geometric success flag is used.
-/

namespace PackingCertificates.BoxGeometry

open Set
open PackingCertificates.Rational
open scoped BigOperators

def unitBox (d : ℕ) : Set (RPoint d) :=
  {x | ∀ a, -(1 : ℝ)/2 ≤ x a ∧ x a ≤ 1/2}

def placedBox {d : ℕ} (c : RPoint d) (s : ℝ) : Set (RPoint d) :=
  {x | ∀ a, c a-s/2 ≤ x a ∧ x a ≤ c a+s/2}

/-- A positive scaling and translation of the canonical box is exactly the
ordinary coordinate box with the requested center and side length. -/
theorem image_unitBox {d : ℕ} (c : RPoint d) (s : ℝ) (hs : 0 < s) :
    (fun x : RPoint d => c+s • x) '' unitBox d = placedBox c s := by
  ext x
  constructor
  · rintro ⟨y, hy, rfl⟩ a
    have ha := hy a
    change c a-s/2 ≤ c a+s*y a ∧ c a+s*y a ≤ c a+s/2
    constructor <;> nlinarith
  · intro hx
    refine ⟨fun a => (x a-c a)/s, ?_, ?_⟩
    · intro a
      have ha := hx a
      constructor
      · apply (le_div_iff₀ hs).mpr
        linarith
      · apply (div_le_iff₀ hs).mpr
        linarith
    · funext a
      change c a+s*((x a-c a)/s) = x a
      rw [mul_div_cancel₀ _ (ne_of_gt hs)]
      ring

noncomputable def corner {d : ℕ} (b : Fin d → Bool) : RPoint d :=
  fun a => if b a then (1 : ℝ)/2 else -(1 : ℝ)/2

def qcorner {d : ℕ} (b : Fin d → Bool) : QPoint d :=
  fun a => if b a then (1 : ℚ)/2 else -(1 : ℚ)/2

/-- Index of a sign corner in the frozen lexicographic template ordering.
The modulus makes the total function's range bound immediate; the finite
coordinate checks below establish the actual indexing property. -/
def cornerIndex {d : ℕ} (b : Fin d → Bool) : Fin (2^d) :=
  ⟨(∑ a : Fin d, if b a then 0 else 2^(d-1-a.val)) % (2^d),
    Nat.mod_lt _ (pow_pos (by decide) d)⟩

theorem realPoint_qcorner {d : ℕ} (b : Fin d → Bool) :
    realPoint (qcorner b) = corner b := by
  funext a
  cases h : b a <;> norm_num [qcorner, corner, realPoint, h]

theorem range_corner (d : ℕ) :
    Set.range (@corner d) =
      Set.univ.pi (fun _ : Fin d => ({-(1 : ℝ)/2, 1/2} : Set ℝ)) := by
  classical
  ext x
  constructor
  · rintro ⟨b, rfl⟩ a _
    cases h : b a
    · exact Or.inl (by simp [corner, h])
    · exact Or.inr (by simp [corner, h])
  · intro hx
    let b : Fin d → Bool := fun a => decide (x a = (1 : ℝ)/2)
    refine ⟨b, ?_⟩
    funext a
    have ha := hx a (Set.mem_univ a)
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at ha
    by_cases hp : x a = (1 : ℝ)/2
    · have hb : b a = true := by simp [b, hp]
      simpa [corner, hb] using hp.symm
    · have hn : x a = -(1 : ℝ)/2 := ha.resolve_right hp
      have hb : b a = false := by exact decide_eq_false hp
      simpa [corner, hb] using hn.symm

theorem corner_hull_eq_unitBox (d : ℕ) :
    convexHull ℝ (Set.range (@corner d)) = unitBox d := by
  rw [range_corner, convexHull_pi]
  have h : convexHull ℝ ({-(1 : ℝ)/2, 1/2} : Set ℝ) =
      Set.Icc (-(1 : ℝ)/2) (1/2) := by
    rw [convexHull_pair, segment_eq_Icc (by norm_num)]
  simp only [h]
  ext x
  simp [unitBox, Set.mem_pi]

/-- An entirely finite rational characterization of a vertex enumeration
containing exactly the sign corners, with repetitions allowed. -/
theorem template_hull_eq_box {d k : ℕ} (v : Fin k → QPoint d)
    (within : ∀ i a, v i a = -(1 : ℚ)/2 ∨ v i a = 1/2)
    (covers : ∀ b : Fin d → Bool, ∃ i, ∀ a, v i a = qcorner b a) :
    vertexBody (fun i => realPoint (v i)) = unitBox d := by
  classical
  have hr : Set.range (fun i => realPoint (v i)) = Set.range (@corner d) := by
    ext x
    constructor
    · rintro ⟨i, rfl⟩
      let b : Fin d → Bool := fun a => decide (v i a = (1 : ℚ)/2)
      have hv : v i = qcorner b := by
        funext a
        by_cases hp : v i a = (1 : ℚ)/2
        · have hb : b a = true := by simp [b, hp]
          simpa [qcorner, hb] using hp
        · have hn : v i a = -(1 : ℚ)/2 := (within i a).resolve_right hp
          have hb : b a = false := by exact decide_eq_false hp
          simpa [qcorner, hb] using hn
      refine ⟨b, ?_⟩
      change corner b = realPoint (v i)
      rw [hv, realPoint_qcorner]
    · rintro ⟨b, rfl⟩
      obtain ⟨i, hi⟩ := covers b
      have hv : v i = qcorner b := funext hi
      refine ⟨i, ?_⟩
      change realPoint (v i) = corner b
      rw [hv, realPoint_qcorner]
  rw [vertexBody, hr]
  exact corner_hull_eq_unitBox d

theorem c8_within : ∀ i : Fin 16, ∀ a : Fin 4,
    TemplateData.c8.getD i.val 0 a = -(1 : ℚ)/2 ∨
    TemplateData.c8.getD i.val 0 a = 1/2 := by decide +kernel

theorem c8_index : ∀ b : Fin 4 → Bool, ∀ a : Fin 4,
    TemplateData.c8.getD (cornerIndex b).val 0 a = qcorner b a := by decide +kernel

theorem c8_covers (b : Fin 4 → Bool) : ∃ i : Fin 16, ∀ a : Fin 4,
    TemplateData.c8.getD i.val 0 a = qcorner b a := ⟨cornerIndex b, c8_index b⟩

theorem hc5_within : ∀ i : Fin 32, ∀ a : Fin 5,
    TemplateData.hc5.getD i.val 0 a = -(1 : ℚ)/2 ∨
    TemplateData.hc5.getD i.val 0 a = 1/2 := by decide +kernel

theorem hc5_index : ∀ b : Fin 5 → Bool, ∀ a : Fin 5,
    TemplateData.hc5.getD (cornerIndex b).val 0 a = qcorner b a := by decide +kernel

theorem hc5_covers (b : Fin 5 → Bool) : ∃ i : Fin 32, ∀ a : Fin 5,
    TemplateData.hc5.getD i.val 0 a = qcorner b a := ⟨cornerIndex b, hc5_index b⟩

theorem hc6_within : ∀ i : Fin 64, ∀ a : Fin 6,
    TemplateData.hc6.getD i.val 0 a = -(1 : ℚ)/2 ∨
    TemplateData.hc6.getD i.val 0 a = 1/2 := by decide +kernel

theorem hc6_index : ∀ b : Fin 6 → Bool, ∀ a : Fin 6,
    TemplateData.hc6.getD (cornerIndex b).val 0 a = qcorner b a := by decide +kernel

theorem hc6_covers (b : Fin 6 → Bool) : ∃ i : Fin 64, ∀ a : Fin 6,
    TemplateData.hc6.getD i.val 0 a = qcorner b a := ⟨cornerIndex b, hc6_index b⟩

theorem c8_body :
    vertexBody (fun i : Fin 16 => realPoint (TemplateData.c8.getD i.val 0)) =
      unitBox 4 := template_hull_eq_box _ c8_within c8_covers

theorem hc5_body :
    vertexBody (fun i : Fin 32 => realPoint (TemplateData.hc5.getD i.val 0)) =
      unitBox 5 := template_hull_eq_box _ hc5_within hc5_covers

theorem hc6_body :
    vertexBody (fun i : Fin 64 => realPoint (TemplateData.hc6.getD i.val 0)) =
      unitBox 6 := template_hull_eq_box _ hc6_within hc6_covers

#print axioms corner_hull_eq_unitBox
#print axioms image_unitBox
#print axioms template_hull_eq_box
#print axioms c8_body
#print axioms hc5_body
#print axioms hc6_body

end PackingCertificates.BoxGeometry
