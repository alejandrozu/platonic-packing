import PackingCertificates.Algebraic.Template
import PackingCertificates.Algebraic.Placement
import PackingCertificates.Cube

/-!
Full exact-source algebraic polyhedral packing certificates.

Numerical interval endpoints enclose, and never replace, canonical real algebraic
vertices. Every placement is the exact rational source quaternion matrix, checked
proper and orthogonal. All placed vertices lie in the actual scaled container
vertex hull by checked Cramer certificates; every unordered pair has a strict
checked rational separating plane. Python's success flag is not a premise.
-/

namespace PackingCertificates.Algebraic.Packing

open PackingCertificates.Rational
open scoped BigOperators

structure Certificate (n k l b : ℕ) where
  piece : TemplateData 3 k
  container : TemplateData 3 l
  pieceRoot : piece.rootSpec.check = true
  containerRoot : container.rootSpec.check = true
  containerDegree : ℕ
  scale : ℚ
  containerCenter : QPoint 3
  quaternion : Fin n → Fin 4 → ℚ
  rotation : Fin n → Fin 3 → QPoint 3
  center : Fin n → QPoint 3
  placedIntervals : Fin n → Fin k → Fin 3 → Interval
  normalizedIntervals : Fin n → Fin k → Fin 3 → Interval
  basisIndices : Fin b → Fin 4 → Fin l
  basisDeterminants : Fin b → Interval
  basisAdjugates : Fin b → Fin 4 → Fin 4 → Interval
  vertexBasis : Fin n → Fin k → Fin b
  epsilon : Fin n → Fin k → ℚ
  separation : Fin n → Fin n → QPlane 3

namespace Certificate

noncomputable def placedVertex (c : Certificate n k l b) (i : Fin n) (p : Fin k) : RPoint 3 :=
  placementAffine (c.rotation i) (c.center i) (c.piece.vertex c.pieceRoot p)

noncomputable def normalizedVertex (c : Certificate n k l b) (i : Fin n) (p : Fin k) : RPoint 3 :=
  Placement.normalizedPoint c.scale c.containerCenter (c.placedVertex i p)

noncomputable def pieceBody (c : Certificate n k l b) (i : Fin n) : Set (RPoint 3) :=
  placementAffine (c.rotation i) (c.center i) '' vertexBody (c.piece.vertex c.pieceRoot)

noncomputable def containerBody (c : Certificate n k l b) : Set (RPoint 3) :=
  Placement.affineContainerMap c.containerCenter c.scale '' vertexBody (c.container.vertex c.containerRoot)

def sourceCheck (c : Certificate n k l b) : Bool :=
  decide (0 < c.scale) && allFin n (fun i =>
    decide (0 < Cube.quaternionNormSq (c.quaternion i)) &&
    (decide (c.rotation i = Cube.quaternionMatrix (c.quaternion i)) &&
    (decide (Cube.determinant3 (c.rotation i) = 1) &&
    allFin 3 (fun a => allFin 3 (fun z =>
      decide (qdot (c.rotation i a) (c.rotation i z) = if a = z then 1 else 0))))))

def templateCheck (c : Certificate n k l b) : Bool :=
  c.piece.normalizationCheck && (c.piece.verticesCheck &&
  (c.container.normalizationCheck && (c.container.verticesCheck &&
    c.container.centroidCheck c.containerDegree)))

def placedCheck (c : Certificate n k l b) (i : Fin n) (p : Fin k) : Bool :=
  allFin 3 (fun a => Interval.enclosesCheck
    (Placement.affineVertexInterval (c.rotation i) (c.center i) (c.piece.vertexIntervals p) a)
    (c.placedIntervals i p a)) &&
  allFin 3 (fun a => Interval.enclosesCheck
    (Placement.normalizedInterval c.scale c.containerCenter (c.placedIntervals i p) a)
    (c.normalizedIntervals i p a))

def placementCheck (c : Certificate n k l b) : Bool :=
  allFin n (fun i => allFin k (fun p => c.placedCheck i p))

def basisMatrixInterval (c : Certificate n k l b) (z : Fin b) : Fin 4 → Fin 4 → Interval :=
  Simplex.augmentedMatrixInterval (fun j => c.container.vertexIntervals (c.basisIndices z j))

def basisCheck (c : Certificate n k l b) : Bool :=
  allFin b (fun z => decide (Function.Injective (c.basisIndices z)) &&
    Simplex.basisCacheCheck (c.basisMatrixInterval z) (c.basisDeterminants z) (c.basisAdjugates z))

def rhsInterval (c : Certificate n k l b) (i : Fin n) (p : Fin k) : Fin 4 → Interval :=
  Simplex.augmentedRHSInterval (1-(l : ℚ)*c.epsilon i p) (c.normalizedIntervals i p)

def vertexContainmentCheck (c : Certificate n k l b) (i : Fin n) (p : Fin k) : Bool :=
  decide (0 ≤ c.epsilon i p) &&
  Simplex.correctedCramerCheck (c.basisDeterminants (c.vertexBasis i p))
    (c.basisAdjugates (c.vertexBasis i p)) (c.rhsInterval i p) (c.epsilon i p)

def containmentCheck (c : Certificate n k l b) : Bool :=
  allFin n (fun i => allFin k (fun p => c.vertexContainmentCheck i p))

def pairCheck (c : Certificate n k l b) (i j : Fin n) : Bool :=
  decide ((c.separation i j).lower < (c.separation i j).upper) &&
  (allFin k (fun p => decide ((Placement.dotInterval (c.separation i j).normal
      (c.placedIntervals i p)).hi ≤ (c.separation i j).lower)) &&
  allFin k (fun p => decide ((c.separation i j).upper ≤
    (Placement.dotInterval (c.separation i j).normal (c.placedIntervals j p)).lo)))

def pairsCheck (c : Certificate n k l b) : Bool :=
  allFin n (fun i => allFin n (fun j => if i < j then c.pairCheck i j else true))

def check (c : Certificate n k l b) : Bool :=
  c.sourceCheck && (c.templateCheck && (c.placementCheck &&
    (c.basisCheck && (c.containmentCheck && c.pairsCheck))))

theorem pieceBody_eq (c : Certificate n k l b) (i : Fin n) :
    c.pieceBody i = vertexBody (c.placedVertex i) :=
  affine_placement_of_vertex_body _ _

theorem placedCheck_sound (c : Certificate n k l b)
    (hTemplate : c.templateCheck = true) (i : Fin n) (p : Fin k)
    (h : c.placedCheck i p = true) :
    (∀ a, (c.placedIntervals i p a).Contains (c.placedVertex i p a)) ∧
    (∀ a, (c.normalizedIntervals i p a).Contains (c.normalizedVertex i p a)) := by
  have ht : c.piece.normalizationCheck = true ∧
      (c.piece.verticesCheck = true ∧ (c.container.normalizationCheck = true ∧
      (c.container.verticesCheck = true ∧ c.container.centroidCheck c.containerDegree = true))) := by
    simpa only [templateCheck,Bool.and_eq_true] using hTemplate
  have hh : (∀ a, Interval.enclosesCheck
      (Placement.affineVertexInterval (c.rotation i) (c.center i) (c.piece.vertexIntervals p) a)
      (c.placedIntervals i p a) = true) ∧
      (∀ a, Interval.enclosesCheck
      (Placement.normalizedInterval c.scale c.containerCenter (c.placedIntervals i p) a)
      (c.normalizedIntervals i p a) = true) := by
    simpa only [placedCheck,Bool.and_eq_true,allFin_eq_true] using h
  have hv := c.piece.vertices_sound c.pieceRoot ht.1 ht.2.1 p
  have hp : ∀ a, (c.placedIntervals i p a).Contains (c.placedVertex i p a) := by
    intro a
    exact Interval.enclosesCheck_sound
      (Placement.affineVertexInterval_sound (c.rotation i) (c.center i)
        (c.piece.vertexIntervals p) (c.piece.vertex c.pieceRoot p) hv a) (hh.1 a)
  refine ⟨hp,fun a => ?_⟩
  exact Interval.enclosesCheck_sound
    (Placement.normalizedInterval_sound c.scale c.containerCenter
      (c.placedIntervals i p) (c.placedVertex i p) hp a) (hh.2 a)

theorem basisCheck_sound (c : Certificate n k l b)
    (hTemplate : c.templateCheck = true) (h : c.basisCheck = true) (z : Fin b) :
    Function.Injective (c.basisIndices z) ∧
    (c.basisDeterminants z).Contains
      (Simplex.augmentedMatrix (fun j => c.container.vertex c.containerRoot (c.basisIndices z j))).det ∧
    (∀ i j, (c.basisAdjugates z i j).Contains
      ((Simplex.augmentedMatrix (fun j => c.container.vertex c.containerRoot (c.basisIndices z j))).adjugate i j)) := by
  have ht : c.piece.normalizationCheck = true ∧
      (c.piece.verticesCheck = true ∧ (c.container.normalizationCheck = true ∧
      (c.container.verticesCheck = true ∧ c.container.centroidCheck c.containerDegree = true))) := by
    simpa only [templateCheck,Bool.and_eq_true] using hTemplate
  have hz := (allFin_eq_true.mp h) z
  have hh : Function.Injective (c.basisIndices z) ∧
      Simplex.basisCacheCheck (c.basisMatrixInterval z) (c.basisDeterminants z) (c.basisAdjugates z) = true := by
    simpa only [Bool.and_eq_true,decide_eq_true_eq] using hz
  have hv := c.container.vertices_sound c.containerRoot ht.2.2.1 ht.2.2.2.1
  have hb := Simplex.basisCacheCheck_sound (c.basisMatrixInterval z)
    (Simplex.augmentedMatrix (fun j => c.container.vertex c.containerRoot (c.basisIndices z j)))
    (c.basisDeterminants z) (c.basisAdjugates z)
    (Simplex.augmentedMatrixInterval_sound _ _ (fun j a => hv (c.basisIndices z j) a)) hh.2
  exact ⟨hh.1,hb.1,hb.2⟩

theorem vertexContainment_sound (c : Certificate n k l b)
    (hTemplate : c.templateCheck = true) (hBasis : c.basisCheck = true)
    (i : Fin n) (p : Fin k) (hp : c.placedCheck i p = true)
    (h : c.vertexContainmentCheck i p = true) :
    c.normalizedVertex i p ∈ vertexBody (c.container.vertex c.containerRoot) := by
  have ht : c.piece.normalizationCheck = true ∧
      (c.piece.verticesCheck = true ∧ (c.container.normalizationCheck = true ∧
      (c.container.verticesCheck = true ∧ c.container.centroidCheck c.containerDegree = true))) := by
    simpa only [templateCheck,Bool.and_eq_true] using hTemplate
  have hh : 0 ≤ c.epsilon i p ∧ Simplex.correctedCramerCheck
      (c.basisDeterminants (c.vertexBasis i p)) (c.basisAdjugates (c.vertexBasis i p))
      (c.rhsInterval i p) (c.epsilon i p) = true := by
    simpa only [vertexContainmentCheck,Bool.and_eq_true,decide_eq_true_eq] using h
  have hb := c.basisCheck_sound hTemplate hBasis (c.vertexBasis i p)
  have hx := (c.placedCheck_sound hTemplate i p hp).2
  have hrhs := Simplex.augmentedRHSInterval_sound (1-(l : ℚ)*c.epsilon i p)
    (c.normalizedIntervals i p) (c.normalizedVertex i p) hx
  have hrhs' : ∀ a, (c.rhsInterval i p a).Contains
      (Simplex.augmentedRHS (1-(l : ℝ)*(c.epsilon i p : ℝ)) (c.normalizedVertex i p) a) := by
    simpa only [rhsInterval,Rat.cast_sub,Rat.cast_one,Rat.cast_mul,Rat.cast_natCast] using hrhs
  exact Simplex.interval_cramer_centered_hull_membership
    (c.container.vertex c.containerRoot)
    (c.container.centroid_sound c.containerDegree c.containerRoot ht.2.2.2.2)
    (c.basisIndices (c.vertexBasis i p)) hb.1 (c.epsilon i p) hh.1
    (c.normalizedVertex i p) _ _ _ hb.2.1 hb.2.2 hrhs' hh.2

theorem pairCheck_sound (c : Certificate n k l b)
    (hTemplate : c.templateCheck = true) (i j : Fin n)
    (hi : ∀ p, c.placedCheck i p = true) (hj : ∀ p, c.placedCheck j p = true)
    (h : c.pairCheck i j = true) : Disjoint (c.pieceBody i) (c.pieceBody j) := by
  have hh : (c.separation i j).lower < (c.separation i j).upper ∧
      ((∀ p, (Placement.dotInterval (c.separation i j).normal (c.placedIntervals i p)).hi ≤
        (c.separation i j).lower) ∧
      (∀ p, (c.separation i j).upper ≤
        (Placement.dotInterval (c.separation i j).normal (c.placedIntervals j p)).lo)) := by
    simpa only [pairCheck,Bool.and_eq_true,allFin_eq_true,decide_eq_true_eq] using h
  rw [c.pieceBody_eq i,c.pieceBody_eq j]
  apply separating_vertex_tests_imply_disjoint (realLinear (c.separation i j).normal)
    ((c.separation i j).lower : ℝ) ((c.separation i j).upper : ℝ)
  · exact_mod_cast hh.1
  · rintro _ ⟨p,rfl⟩
    have hs := Placement.dotInterval_sound (c.separation i j).normal
      (c.placedIntervals i p) (c.placedVertex i p)
      (c.placedCheck_sound hTemplate i p (hi p)).1
    have hu : ((Placement.dotInterval (c.separation i j).normal (c.placedIntervals i p)).hi : ℝ) ≤
        (c.separation i j).lower := by exact_mod_cast hh.2.1 p
    exact hs.2.trans hu
  · rintro _ ⟨p,rfl⟩
    have hs := Placement.dotInterval_sound (c.separation i j).normal
      (c.placedIntervals j p) (c.placedVertex j p)
      (c.placedCheck_sound hTemplate j p (hj p)).1
    have hl : ((c.separation i j).upper : ℝ) ≤
        (Placement.dotInterval (c.separation i j).normal (c.placedIntervals j p)).lo := by
      exact_mod_cast hh.2.2 p
    exact hl.trans hs.1

def Valid (c : Certificate n k l b) : Prop :=
  0 < (c.scale : ℝ) ∧
  (∀ i, 0 < Cube.quaternionNormSq (c.quaternion i) ∧
    c.rotation i = Cube.quaternionMatrix (c.quaternion i) ∧ Cube.determinant3 (c.rotation i) = 1) ∧
  (∀ i a z, realLinear (c.rotation i a) (realPoint (c.rotation i z)) =
    if a = z then (1 : ℝ) else 0) ∧
  (∀ i, c.pieceBody i ⊆ c.containerBody) ∧
  Pairwise (fun i j => Disjoint (c.pieceBody i) (c.pieceBody j))

theorem check_sound (c : Certificate n k l b) (h : c.check = true) : c.Valid := by
  have hh : c.sourceCheck = true ∧ (c.templateCheck = true ∧ (c.placementCheck = true ∧
      (c.basisCheck = true ∧ (c.containmentCheck = true ∧ c.pairsCheck = true)))) := by
    simpa only [check,Bool.and_eq_true] using h
  have hs : 0 < c.scale ∧ ∀ i, 0 < Cube.quaternionNormSq (c.quaternion i) ∧
      (c.rotation i = Cube.quaternionMatrix (c.quaternion i) ∧
      (Cube.determinant3 (c.rotation i) = 1 ∧ ∀ a z,
        qdot (c.rotation i a) (c.rotation i z) = if a = z then 1 else 0)) := by
    simpa only [sourceCheck,Bool.and_eq_true,allFin_eq_true,decide_eq_true_eq] using hh.1
  have hp : ∀ i p, c.placedCheck i p = true := by
    simpa only [placementCheck,allFin_eq_true] using hh.2.2.1
  have hc : ∀ i p, c.vertexContainmentCheck i p = true := by
    simpa only [containmentCheck,allFin_eq_true] using hh.2.2.2.2.1
  have hpair : ∀ i j, (if i < j then c.pairCheck i j else true) = true := by
    simpa only [pairsCheck,allFin_eq_true] using hh.2.2.2.2.2
  refine ⟨by exact_mod_cast hs.1,?_,?_,?_,?_⟩
  · intro i
    exact ⟨(hs.2 i).1,(hs.2 i).2.1,(hs.2 i).2.2.1⟩
  · intro i a z
    rw [realLinear_realPoint]
    have hg := (hs.2 i).2.2.2 a z
    by_cases haz : a = z
    · simp only [haz,if_true] at hg ⊢
      exact_mod_cast hg
    · simp only [haz,if_false] at hg ⊢
      exact_mod_cast hg
  · intro i
    rw [c.pieceBody_eq i]
    apply Placement.normalized_vertices_imply_containment
      (c.placedVertex i) (c.container.vertex c.containerRoot) c.containerCenter c.scale (ne_of_gt hs.1)
    intro p
    exact c.vertexContainment_sound hh.2.1 hh.2.2.2.1 i p (hp i p) (hc i p)
  · intro i j hij
    rcases lt_or_gt_of_ne hij with hl | hr
    · exact c.pairCheck_sound hh.2.1 i j (hp i) (hp j) (by simpa [hl] using hpair i j)
    · exact (c.pairCheck_sound hh.2.1 j i (hp j) (hp i) (by simpa [hr] using hpair j i)).symm

theorem proper_rotation (c : Certificate n k l b) (h : c.check = true) (i : Fin n) :
    Matrix.det (fun a z => (c.rotation i a z : ℝ)) = 1 := by
  rw [Cube.determinant3_real]
  have hd := ((c.check_sound h).2.1 i).2.2
  exact_mod_cast hd

/-- The common source placement preserves actual squared Euclidean distance
for all real points, not merely its finite set of algebraic vertices. -/
theorem preserves_squared_distance (c : Certificate n k l b) (h : c.check = true)
    (i : Fin n) (x y : RPoint 3) :
    (∑ a, (placementAffine (c.rotation i) (c.center i) x a -
      placementAffine (c.rotation i) (c.center i) y a) ^ 2) =
      ∑ a, (x a-y a)^2 := by
  have hdiff : placementAffine (c.rotation i) (c.center i) x -
      placementAffine (c.rotation i) (c.center i) y = realRotation (c.rotation i) (x-y) := by
    simp [placementAffine,map_sub]
  have hd := realRotation_preserves_dotProduct (c.rotation i)
    ((c.check_sound h).2.2.1 i) (x-y) (x-y)
  simpa only [← hdiff,Pi.sub_apply,pow_two] using hd

end Certificate
end PackingCertificates.Algebraic.Packing

#print axioms PackingCertificates.Algebraic.Packing.Certificate.check_sound
#print axioms PackingCertificates.Algebraic.Packing.Certificate.proper_rotation
#print axioms PackingCertificates.Algebraic.Packing.Certificate.preserves_squared_distance
