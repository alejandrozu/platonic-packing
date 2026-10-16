import Mathlib.Tactic.FinCases
import PackingCertificates.Barycentric
import PackingCertificates.Cayley
import PackingCertificates.TemplateData

-- Exact source: records/c8inc8/c8inc8_n02.json
-- JSON SHA256: 49cdca29437b8e44a326c3b021db75cd017d5c9b211f45327a3a9c07c3fca110
-- Canonical geometry SHA256: 668f2e176e56e11738722784a6286784151479f24820db13910bd627627b596e
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.FRc8inc8_n02
open PackingCertificates.Rational

def rawSources : Array (Cayley.Certificate 4) := #[{ skew := ![![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]], signs := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)], inverse := ![![(1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (1 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (1 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (1 : ℚ)]], rotation := ![![(1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (1 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (1 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (1 : ℚ)]] },
  { skew := ![![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]], signs := ![(1 : ℚ), (1 : ℚ), (1 : ℚ), (1 : ℚ)], inverse := ![![(1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (1 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (1 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (1 : ℚ)]], rotation := ![![(1 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (1 : ℚ), (0 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (1 : ℚ), (0 : ℚ)], ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (1 : ℚ)]] }]
def rawCenters : Array (QPoint 4) := #[![(-1125900019432841/2251799813685248 : ℚ), (1125900019432841/2251799813685248 : ℚ), (1125900019432841/2251799813685248 : ℚ), (-1125900019432841/2251799813685248 : ℚ)],
  ![(-1125900019432841/2251799813685248 : ℚ), (1125900019432841/2251799813685248 : ℚ), (1125900019432841/2251799813685248 : ℚ), (1125900019432841/2251799813685248 : ℚ)]]
def allPlanes : Array (Array (QPlane 4)) := #[#[⟨![(0 : ℚ), (0 : ℚ), (0 : ℚ), (1 : ℚ)], (-112590217/2251799813685248 : ℚ), (112590217/2251799813685248 : ℚ)⟩],
  #[]]
def vertexIndices : Array (Array (Fin 6 → Fin 16)) := #[#[![15, 9, 0, 0, 0, 0],
  ![15, 9, 1, 0, 0, 0],
  ![15, 11, 9, 0, 0, 0],
  ![15, 11, 9, 1, 0, 0],
  ![15, 13, 9, 0, 0, 0],
  ![15, 13, 9, 1, 0, 0],
  ![15, 9, 0, 0, 0, 0],
  ![15, 9, 1, 0, 0, 0],
  ![15, 9, 8, 0, 0, 0],
  ![15, 9, 0, 0, 0, 0],
  ![15, 11, 9, 8, 0, 0],
  ![15, 11, 9, 0, 0, 0],
  ![15, 13, 9, 8, 0, 0],
  ![15, 13, 9, 0, 0, 0],
  ![15, 9, 8, 0, 0, 0],
  ![15, 9, 0, 0, 0, 0]],
  #[![15, 8, 0, 0, 0, 0],
  ![15, 9, 8, 0, 0, 0],
  ![15, 10, 8, 0, 0, 0],
  ![15, 11, 8, 0, 0, 0],
  ![15, 12, 8, 0, 0, 0],
  ![15, 13, 8, 0, 0, 0],
  ![15, 14, 8, 0, 0, 0],
  ![15, 8, 0, 0, 0, 0],
  ![15, 8, 0, 0, 0, 0],
  ![15, 9, 8, 0, 0, 0],
  ![15, 10, 8, 0, 0, 0],
  ![15, 11, 8, 0, 0, 0],
  ![15, 12, 8, 0, 0, 0],
  ![15, 13, 8, 0, 0, 0],
  ![15, 14, 8, 0, 0, 0],
  ![15, 8, 0, 0, 0, 0]]]
def vertexWeights : Array (Array (Fin 6 → ℚ)) := #[#[![(75060031/1501200100970372 : ℚ), (1125900019432841/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (1125900019432841/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ)],
  ![(2251800038865341/4503600302911116 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(2251800038865341/4503600302911116 : ℚ), (112590217/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (1125900019432841/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (750599975425155/750600050485186 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(2251800038865341/4503600302911116 : ℚ), (112590217/2251800151455558 : ℚ), (562949953421312/1125900075727779 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(2251800038865341/4503600302911116 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]],
  #[![(75060031/1501200100970372 : ℚ), (1125900019432841/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(2251800038865341/4503600302911116 : ℚ), (112590217/2251800151455558 : ℚ), (2251800038865341/4503600302911116 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (750599975425155/750600050485186 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(75060031/1501200100970372 : ℚ), (562949953421312/1125900075727779 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ)],
  ![(2251800038865341/4503600302911116 : ℚ), (1125900019432841/2251800151455558 : ℚ), (75060031/1501200100970372 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]]]

def source (i : Fin 2) : Cayley.Certificate 4 :=
  rawSources.getD i.val {skew := 0, signs := 0, inverse := 0, rotation := 0}

def record : Barycentric.Certificate 4 2 16 16 6 where
  placement := {
    template := fun p => TemplateData.c8.getD p.val 0
    rotation := fun i => (source i).rotation
    center := fun i => rawCenters.getD i.val 0
    walls := Fin.elim0
    separation := fun i j => (allPlanes.getD i.val #[]).getD (j.val-i.val-1) ⟨0,0,0⟩ }
  containerVertices := fun p => TemplateData.c8.getD p.val 0
  scale := (1125900075727779/562949953421312 : ℚ)
  containerCenter := ![(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
  indices := fun i p => (vertexIndices.getD i.val #[]).getD p.val 0
  weights := fun i p => (vertexWeights.getD i.val #[]).getD p.val 0

def storedScale : ℚ := (1125900075727779/562949953421312 : ℚ)
def edgeRatio : ℚ := (1 : ℚ)

theorem edge_normalization : edgeRatio = 1 ∧ record.scale = storedScale * edgeRatio := by decide +kernel

theorem template_sizes : TemplateData.c8.size = 16 ∧
    TemplateData.c8.size = 16 := by decide +kernel

theorem input_sizes : rawSources.size = 2 ∧ rawCenters.size = 2 ∧
    allPlanes.size = 2 ∧ vertexIndices.size = 2 ∧ vertexWeights.size = 2 := by decide +kernel

theorem source_piece_0 : Cayley.check (source (0 : Fin 2)) = true := by decide +kernel

theorem gram_piece_0 :
    allFin 4 (fun a => allFin 4 (fun b =>
      decide (qdot (record.placement.rotation (0 : Fin 2) a)
        (record.placement.rotation (0 : Fin 2) b) = if a = b then 1 else 0))) = true := by decide +kernel


theorem pair_row_0 :
    allFin 2 (fun j => if (0 : Fin 2) < j then
      planeCheck (record.placement.toCertificate.vertices (0 : Fin 2))
        (record.placement.toCertificate.vertices j)
        (record.placement.separation (0 : Fin 2) j) else true) = true := by decide +kernel

theorem vertices_piece_0 :
    allFin 16 (fun p => record.vertexCheck (0 : Fin 2) p) = true := by decide +kernel

theorem source_piece_1 : Cayley.check (source (1 : Fin 2)) = true := by decide +kernel

theorem gram_piece_1 :
    allFin 4 (fun a => allFin 4 (fun b =>
      decide (qdot (record.placement.rotation (1 : Fin 2) a)
        (record.placement.rotation (1 : Fin 2) b) = if a = b then 1 else 0))) = true := by decide +kernel


theorem pair_row_1 :
    allFin 2 (fun j => if (1 : Fin 2) < j then
      planeCheck (record.placement.toCertificate.vertices (1 : Fin 2))
        (record.placement.toCertificate.vertices j)
        (record.placement.separation (1 : Fin 2) j) else true) = true := by decide +kernel

theorem vertices_piece_1 :
    allFin 16 (fun p => record.vertexCheck (1 : Fin 2) p) = true := by decide +kernel

theorem source_checked : allFin 2 (fun i => Cayley.check (source i)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact source_piece_0
  · exact source_piece_1

theorem gram_checked_all : allFin 2 (fun i => allFin 4 (fun a => allFin 4 (fun b => decide (qdot (record.placement.rotation i a) (record.placement.rotation i b) = if a = b then 1 else 0)))) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact gram_piece_0
  · exact gram_piece_1

theorem pair_checked : allFin 2 (fun i => allFin 2 (fun j => if i < j then planeCheck (record.placement.toCertificate.vertices i) (record.placement.toCertificate.vertices j) (record.placement.separation i j) else true)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact pair_row_0
  · exact pair_row_1

theorem vertices_checked : allFin 2 (fun i => allFin 16 (fun p => record.vertexCheck i p)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact vertices_piece_0
  · exact vertices_piece_1

theorem source_valid : ∀ i, Cayley.Valid (source i) := by
  intro i
  exact Cayley.check_sound _ (allFin_eq_true.mp source_checked i)

theorem gram_checked : orthogonalCheck record.placement = true := gram_checked_all

theorem walls_checked :
    allFin 2 (fun i => allFin 16 (fun p => allFin 0 (fun f =>
      decide (qdot (record.placement.toCertificate.walls f).normal
        (record.placement.toCertificate.vertices i p) ≤
          (record.placement.toCertificate.walls f).offset)))) = true := by
  apply allFin_eq_true.mpr
  intro i
  apply allFin_eq_true.mpr
  intro p
  apply allFin_eq_true.mpr
  intro f
  exact Fin.elim0 f

theorem rational_checked : Rational.check record.placement.toCertificate = true := by
  simp only [Rational.check, Bool.and_eq_true]
  exact ⟨walls_checked, pair_checked⟩

theorem placed_checked : checkPlaced record.placement = true := by
  simp only [checkPlaced, Bool.and_eq_true]
  exact ⟨gram_checked, rational_checked⟩

theorem scale_checked : decide (0 < record.scale) = true := by decide +kernel

theorem checked : Barycentric.check record = true := by
  simp only [Barycentric.check, Bool.and_eq_true]
  exact ⟨⟨placed_checked, scale_checked⟩, vertices_checked⟩

/-- Complete convex-polytope packing, assembled from kernel-checked fragments. -/
theorem packing : Barycentric.Valid record := Barycentric.check_sound record checked

theorem proper_orientation : ∀ i : Fin 2,
    Matrix.det (fun a b => (record.placement.rotation i a b : ℝ)) = 1 := by
  intro i
  exact Cayley.determinant_real (source i) (allFin_eq_true.mp source_checked i)

#print axioms source_valid
#print axioms packing
#print axioms proper_orientation
end PackingCertificates.Catalogue.FRc8inc8_n02
