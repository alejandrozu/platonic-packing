import PackingCertificates.Catalogue.CRcubincub_n34.Block000
import PackingCertificates.Catalogue.CRcubincub_n34.Block001
import PackingCertificates.Catalogue.CRcubincub_n34.Block002
import PackingCertificates.Catalogue.CRcubincub_n34.Block003
import PackingCertificates.Catalogue.CRcubincub_n34.Block004
import PackingCertificates.Catalogue.CRcubincub_n34.Block005
import PackingCertificates.Catalogue.CRcubincub_n34.Block006

-- Original source: records/cubincub/cubincub_n34.json
-- Original JSON SHA256: f388cc5d3289c957c73e8b9cdf9a6d48da63a6997396332e697126b8c1e5a15c
-- Record identifier: cubincub_n34
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n34
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_pieces_checked : allFin 34 (fun i => decide (0 < Cube.quaternionNormSq (record.quaternion i)) && decide (record.rotation i = Cube.quaternionMatrix (record.quaternion i)) && decide (Cube.determinant3 (record.rotation i) = 1)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact source_piece_0
  · exact source_piece_1
  · exact source_piece_2
  · exact source_piece_3
  · exact source_piece_4
  · exact source_piece_5
  · exact source_piece_6
  · exact source_piece_7
  · exact source_piece_8
  · exact source_piece_9
  · exact source_piece_10
  · exact source_piece_11
  · exact source_piece_12
  · exact source_piece_13
  · exact source_piece_14
  · exact source_piece_15
  · exact source_piece_16
  · exact source_piece_17
  · exact source_piece_18
  · exact source_piece_19
  · exact source_piece_20
  · exact source_piece_21
  · exact source_piece_22
  · exact source_piece_23
  · exact source_piece_24
  · exact source_piece_25
  · exact source_piece_26
  · exact source_piece_27
  · exact source_piece_28
  · exact source_piece_29
  · exact source_piece_30
  · exact source_piece_31
  · exact source_piece_32
  · exact source_piece_33

theorem gram_pieces_checked : allFin 34 (fun i => allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation i a) (record.toPlacement.rotation i b) = if a = b then 1 else 0)))) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact gram_piece_0
  · exact gram_piece_1
  · exact gram_piece_2
  · exact gram_piece_3
  · exact gram_piece_4
  · exact gram_piece_5
  · exact gram_piece_6
  · exact gram_piece_7
  · exact gram_piece_8
  · exact gram_piece_9
  · exact gram_piece_10
  · exact gram_piece_11
  · exact gram_piece_12
  · exact gram_piece_13
  · exact gram_piece_14
  · exact gram_piece_15
  · exact gram_piece_16
  · exact gram_piece_17
  · exact gram_piece_18
  · exact gram_piece_19
  · exact gram_piece_20
  · exact gram_piece_21
  · exact gram_piece_22
  · exact gram_piece_23
  · exact gram_piece_24
  · exact gram_piece_25
  · exact gram_piece_26
  · exact gram_piece_27
  · exact gram_piece_28
  · exact gram_piece_29
  · exact gram_piece_30
  · exact gram_piece_31
  · exact gram_piece_32
  · exact gram_piece_33

theorem cache_checked : allFin 34 (fun i => AxisFast.cacheRowCheck record cache i) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact cache_row_0
  · exact cache_row_1
  · exact cache_row_2
  · exact cache_row_3
  · exact cache_row_4
  · exact cache_row_5
  · exact cache_row_6
  · exact cache_row_7
  · exact cache_row_8
  · exact cache_row_9
  · exact cache_row_10
  · exact cache_row_11
  · exact cache_row_12
  · exact cache_row_13
  · exact cache_row_14
  · exact cache_row_15
  · exact cache_row_16
  · exact cache_row_17
  · exact cache_row_18
  · exact cache_row_19
  · exact cache_row_20
  · exact cache_row_21
  · exact cache_row_22
  · exact cache_row_23
  · exact cache_row_24
  · exact cache_row_25
  · exact cache_row_26
  · exact cache_row_27
  · exact cache_row_28
  · exact cache_row_29
  · exact cache_row_30
  · exact cache_row_31
  · exact cache_row_32
  · exact cache_row_33

theorem walls_checked : allFin 34 (fun i => CubeFast.wallRowCheck record i) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact wall_row_0
  · exact wall_row_1
  · exact wall_row_2
  · exact wall_row_3
  · exact wall_row_4
  · exact wall_row_5
  · exact wall_row_6
  · exact wall_row_7
  · exact wall_row_8
  · exact wall_row_9
  · exact wall_row_10
  · exact wall_row_11
  · exact wall_row_12
  · exact wall_row_13
  · exact wall_row_14
  · exact wall_row_15
  · exact wall_row_16
  · exact wall_row_17
  · exact wall_row_18
  · exact wall_row_19
  · exact wall_row_20
  · exact wall_row_21
  · exact wall_row_22
  · exact wall_row_23
  · exact wall_row_24
  · exact wall_row_25
  · exact wall_row_26
  · exact wall_row_27
  · exact wall_row_28
  · exact wall_row_29
  · exact wall_row_30
  · exact wall_row_31
  · exact wall_row_32
  · exact wall_row_33

theorem pairs_checked : allFin 34 (fun i => AxisFast.pairRowCheck record cache directions i) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact pair_row_0
  · exact pair_row_1
  · exact pair_row_2
  · exact pair_row_3
  · exact pair_row_4
  · exact pair_row_5
  · exact pair_row_6
  · exact pair_row_7
  · exact pair_row_8
  · exact pair_row_9
  · exact pair_row_10
  · exact pair_row_11
  · exact pair_row_12
  · exact pair_row_13
  · exact pair_row_14
  · exact pair_row_15
  · exact pair_row_16
  · exact pair_row_17
  · exact pair_row_18
  · exact pair_row_19
  · exact pair_row_20
  · exact pair_row_21
  · exact pair_row_22
  · exact pair_row_23
  · exact pair_row_24
  · exact pair_row_25
  · exact pair_row_26
  · exact pair_row_27
  · exact pair_row_28
  · exact pair_row_29
  · exact pair_row_30
  · exact pair_row_31
  · exact pair_row_32
  · exact pair_row_33

theorem scale_checked : decide (0 < record.scale) = true := by decide +kernel

theorem source_checked : record.sourceCheck = true := by
  simp only [CubeRecord.sourceCheck, Bool.and_eq_true]
  exact ⟨scale_checked, source_pieces_checked⟩

theorem gram_checked : orthogonalCheck record.toPlacement = true := gram_pieces_checked

theorem axis_checked : AxisFast.check record cache directions = true :=
  AxisFast.check_of_rows record cache directions source_checked gram_checked
    (allFin_eq_true.mp cache_checked)
    (allFin_eq_true.mp walls_checked) (allFin_eq_true.mp pairs_checked)

theorem checked : record.check = true :=
  CubeFast.fastCheck_implies_check record
    (AxisFast.check_implies_fastCheck record cache directions axis_checked)

/-- Complete actual catalogue packing, assembled from separately compiled
kernel-checked arithmetic blocks. No numerical test is silently omitted. -/
theorem packing : record.Valid := AxisFast.check_sound record cache directions axis_checked

#print axioms source_checked
#print axioms axis_checked
#print axioms checked
#print axioms packing
end PackingCertificates.Catalogue.CRcubincub_n34
