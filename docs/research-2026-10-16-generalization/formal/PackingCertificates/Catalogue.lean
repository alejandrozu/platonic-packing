import PackingCertificates.Rational
import PackingCertificates.Cube

/-! Actual cube catalogue records: exact source placements and complete checks.
The JSON-to-Lean exporter is outside the kernel; its exact values and source
hashes are published. No theorem in this file trusts Python's success flag.
-/

namespace PackingCertificates.Catalogue

open PackingCertificates.Rational
open scoped BigOperators

def cubeTemplate : Fin 8 → QPoint 3 :=
  ![![-1/2, -1/2, -1/2], ![-1/2, -1/2, 1/2],
    ![-1/2, 1/2, -1/2], ![-1/2, 1/2, 1/2],
    ![1/2, -1/2, -1/2], ![1/2, -1/2, 1/2],
    ![1/2, 1/2, -1/2], ![1/2, 1/2, 1/2]]

theorem cubeTemplate_real : (fun p => realPoint (cubeTemplate p)) = Cube.vertex := by
  funext p a
  fin_cases p <;> fin_cases a <;> norm_num [cubeTemplate, realPoint, Cube.vertex]

theorem cubeTemplate_body : vertexBody (fun p => realPoint (cubeTemplate p)) = Cube.unitBox := by
  rw [cubeTemplate_real, Cube.vertexBody_eq_unitBox]

def cubeWalls (c : QPoint 3) (s : ℚ) : Fin 6 → QHalfspace 3 :=
  ![⟨![1,0,0], c 0 + s/2⟩, ⟨![0,1,0], c 1 + s/2⟩, ⟨![0,0,1], c 2 + s/2⟩,
    ⟨![-1,0,0], -c 0 + s/2⟩, ⟨![0,-1,0], -c 1 + s/2⟩, ⟨![0,0,-1], -c 2 + s/2⟩]

theorem cubeWalls_real (c : QPoint 3) (s : ℚ) :
    (fun f => (cubeWalls c s f).toReal) = Cube.walls (realPoint c) (s : ℝ) := by
  funext f
  fin_cases f <;> simp [cubeWalls, QHalfspace.toReal, realLinear, Cube.walls,
    Cube.coord, realPoint, Fin.sum_univ_succ]
  all_goals
    ext x
    simp

theorem cubeWalls_container (c : QPoint 3) (s : ℚ) :
    container (fun f => (cubeWalls c s f).toReal) =
      Cube.placedBox (realPoint c) (s : ℝ) := by
  rw [cubeWalls_real, Cube.container_walls]

structure CubeRecord (n : ℕ) where
  scale : ℚ
  containerCenter : QPoint 3
  quaternion : Fin n → Fin 4 → ℚ
  rotation : Fin n → Fin 3 → QPoint 3
  center : Fin n → QPoint 3
  separation : Fin n → Fin n → QPlane 3

def CubeRecord.toPlacement {n : ℕ} (r : CubeRecord n) : PlacementCertificate 3 n 8 6 where
  template := cubeTemplate
  rotation := r.rotation
  center := r.center
  walls := cubeWalls r.containerCenter r.scale
  separation := r.separation

def CubeRecord.sourceCheck {n : ℕ} (r : CubeRecord n) : Bool :=
  decide (0 < r.scale) && allFin n (fun i =>
    decide (0 < Cube.quaternionNormSq (r.quaternion i)) &&
    decide (r.rotation i = Cube.quaternionMatrix (r.quaternion i)) &&
    decide (Cube.determinant3 (r.rotation i) = 1))

def CubeRecord.check {n : ℕ} (r : CubeRecord n) : Bool :=
  r.sourceCheck && checkPlaced r.toPlacement

/-- Claims concern the ordinary side-one cube, the supplied raw quaternion,
and the ordinary side-`scale` container; no perturbed vertex list is substituted.
Row Gram identities supply exact Euclidean orthogonality, and `det=1` verifies
proper orientation. Every pair and wall is checked by `checkPlaced`.
-/
def CubeRecord.Valid {n : ℕ} (r : CubeRecord n) : Prop :=
  (0 < (r.scale : ℝ)) ∧
  (∀ i, 0 < Cube.quaternionNormSq (r.quaternion i) ∧
    r.rotation i = Cube.quaternionMatrix (r.quaternion i) ∧
    Cube.determinant3 (r.rotation i) = 1) ∧
  (∀ i a b, realLinear (r.rotation i a) (realPoint (r.rotation i b)) =
    if a = b then (1 : ℝ) else 0) ∧
  (∀ i (x y : RPoint 3),
    (∑ a, (placementAffine (r.rotation i) (r.center i) x a -
      placementAffine (r.rotation i) (r.center i) y a) ^ 2) =
      ∑ a, (x a - y a) ^ 2) ∧
  (∀ i, placementAffine (r.rotation i) (r.center i) '' Cube.unitBox ⊆
    Cube.placedBox (realPoint r.containerCenter) (r.scale : ℝ)) ∧
  Pairwise (fun i j => Disjoint
    (placementAffine (r.rotation i) (r.center i) '' Cube.unitBox)
    (placementAffine (r.rotation j) (r.center j) '' Cube.unitBox))

theorem CubeRecord.check_sound {n : ℕ} (r : CubeRecord n) (h : r.check = true) :
    r.Valid := by
  have hh : r.sourceCheck = true ∧ checkPlaced r.toPlacement = true := by
    simpa only [CubeRecord.check, Bool.and_eq_true] using h
  have hs := hh.1
  simp only [CubeRecord.sourceCheck, Bool.and_eq_true, allFin_eq_true, decide_eq_true_eq] at hs
  have hp := checkPlaced_sound r.toPlacement hh.2
  have ht : vertexBody (fun p => realPoint (r.toPlacement.template p)) = Cube.unitBox :=
    cubeTemplate_body
  have hw : container (fun f => (r.toPlacement.walls f).toReal) =
      Cube.placedBox (realPoint r.containerCenter) (r.scale : ℝ) :=
    cubeWalls_container _ _
  refine ⟨by exact_mod_cast hs.1, ?_, hp.1, ?_, ?_, ?_⟩
  · intro i
    exact ⟨(hs.2 i).1.1, (hs.2 i).1.2, (hs.2 i).2⟩
  · intro i x y
    exact checkPlaced_preserves_squared_distance r.toPlacement hh.2 i x y
  · intro i
    have hi := hp.2.1 i
    rw [ht, hw] at hi
    exact hi
  · intro i j hij
    have hi := hp.2.2 hij
    rw [ht] at hi
    exact hi

end PackingCertificates.Catalogue
