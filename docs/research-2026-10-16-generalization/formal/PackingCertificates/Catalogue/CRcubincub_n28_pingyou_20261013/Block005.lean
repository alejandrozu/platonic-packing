import PackingCertificates.Catalogue.CRcubincub_n28_pingyou_20261013.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n28_pingyou_20261013
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_25 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (25 : Fin 28))) && decide (record.rotation (25 : Fin 28) = Cube.quaternionMatrix (record.quaternion (25 : Fin 28))) && decide (Cube.determinant3 (record.rotation (25 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_25 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (25 : Fin 28) a) (record.toPlacement.rotation (25 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_25 :
    AxisFast.cacheRowCheck record cache (25 : Fin 28) = true := by decide +kernel

theorem wall_row_25 : CubeFast.wallRowCheck record (25 : Fin 28) = true := by decide +kernel

theorem pair_row_25 :
    AxisFast.pairRowCheck record cache directions (25 : Fin 28) = true := by decide +kernel

theorem source_piece_26 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (26 : Fin 28))) && decide (record.rotation (26 : Fin 28) = Cube.quaternionMatrix (record.quaternion (26 : Fin 28))) && decide (Cube.determinant3 (record.rotation (26 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_26 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (26 : Fin 28) a) (record.toPlacement.rotation (26 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_26 :
    AxisFast.cacheRowCheck record cache (26 : Fin 28) = true := by decide +kernel

theorem wall_row_26 : CubeFast.wallRowCheck record (26 : Fin 28) = true := by decide +kernel

theorem pair_row_26 :
    AxisFast.pairRowCheck record cache directions (26 : Fin 28) = true := by decide +kernel

theorem source_piece_27 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (27 : Fin 28))) && decide (record.rotation (27 : Fin 28) = Cube.quaternionMatrix (record.quaternion (27 : Fin 28))) && decide (Cube.determinant3 (record.rotation (27 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_27 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (27 : Fin 28) a) (record.toPlacement.rotation (27 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_27 :
    AxisFast.cacheRowCheck record cache (27 : Fin 28) = true := by decide +kernel

theorem wall_row_27 : CubeFast.wallRowCheck record (27 : Fin 28) = true := by decide +kernel

theorem pair_row_27 :
    AxisFast.pairRowCheck record cache directions (27 : Fin 28) = true := by decide +kernel

#print axioms source_piece_25
#print axioms gram_piece_25
#print axioms cache_row_25
#print axioms wall_row_25
#print axioms pair_row_25
#print axioms source_piece_26
#print axioms gram_piece_26
#print axioms cache_row_26
#print axioms wall_row_26
#print axioms pair_row_26
#print axioms source_piece_27
#print axioms gram_piece_27
#print axioms cache_row_27
#print axioms wall_row_27
#print axioms pair_row_27
end PackingCertificates.Catalogue.CRcubincub_n28_pingyou_20261013
