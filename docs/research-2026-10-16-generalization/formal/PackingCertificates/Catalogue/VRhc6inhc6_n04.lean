import PackingCertificates.Catalogue.VRhc6inhc6_n04.Source000
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Assemble000
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Source001
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Assemble001
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Source002
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Assemble002
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Source003
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Assemble003

-- Original source: records/hc6inhc6/hc6inhc6_n04.json
-- Original JSON SHA256: 0f31ede853c56e76a022fb76dd764b1059b81c64727b2b14552483d6f3810ec1
-- Canonical geometry SHA256: 668f2e176e56e11738722784a6286784151479f24820db13910bd627627b596e
-- Record identifier: hc6inhc6_n04
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.VRhc6inhc6_n04
open PackingCertificates.Rational

theorem source_checked : allFin 4 (fun i => Cayley.check (source i)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact source_piece_0
  · exact source_piece_1
  · exact source_piece_2
  · exact source_piece_3

theorem gram_checked_all : allFin 4 (fun i => allFin 6 (fun a => allFin 6 (fun b => decide (qdot (record.placement.rotation i a) (record.placement.rotation i b) = if a = b then 1 else 0)))) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact gram_piece_0
  · exact gram_piece_1
  · exact gram_piece_2
  · exact gram_piece_3

theorem pair_checked : allFin 4 (fun i => allFin 4 (fun j => if i < j then planeCheck (record.placement.toCertificate.vertices i) (record.placement.toCertificate.vertices j) (record.placement.separation i j) else true)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact pair_row_0
  · exact pair_row_1
  · exact pair_row_2
  · exact pair_row_3

theorem vertices_checked : allFin 4 (fun i => allFin 64 (fun p => record.vertexCheck i p)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact vertices_piece_0
  · exact vertices_piece_1
  · exact vertices_piece_2
  · exact vertices_piece_3

theorem source_valid : ∀ i, Cayley.Valid (source i) := by
  intro i
  exact Cayley.check_sound _ (allFin_eq_true.mp source_checked i)

theorem gram_checked : orthogonalCheck record.placement = true := gram_checked_all

theorem walls_checked :
    allFin 4 (fun i => allFin 64 (fun p => allFin 0 (fun f =>
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

theorem proper_orientation : ∀ i : Fin 4,
    Matrix.det (fun a b => (record.placement.rotation i a b : ℝ)) = 1 := by
  intro i
  exact Cayley.determinant_real (source i) (allFin_eq_true.mp source_checked i)

#print axioms source_valid
#print axioms packing
#print axioms proper_orientation
end PackingCertificates.Catalogue.VRhc6inhc6_n04
