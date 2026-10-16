import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_95 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (95 : Fin 100))) && decide (record.rotation (95 : Fin 100) = Cube.quaternionMatrix (record.quaternion (95 : Fin 100))) && decide (Cube.determinant3 (record.rotation (95 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_95 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (95 : Fin 100) a) (record.toPlacement.rotation (95 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_95 :
    AxisFast.cacheRowCheck record cache (95 : Fin 100) = true := by decide +kernel

theorem wall_row_95 : CubeFast.wallRowCheck record (95 : Fin 100) = true := by decide +kernel

theorem pair_row_95 :
    AxisFast.pairRowCheck record cache directions (95 : Fin 100) = true := by decide +kernel

theorem source_piece_96 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (96 : Fin 100))) && decide (record.rotation (96 : Fin 100) = Cube.quaternionMatrix (record.quaternion (96 : Fin 100))) && decide (Cube.determinant3 (record.rotation (96 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_96 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (96 : Fin 100) a) (record.toPlacement.rotation (96 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_96 :
    AxisFast.cacheRowCheck record cache (96 : Fin 100) = true := by decide +kernel

theorem wall_row_96 : CubeFast.wallRowCheck record (96 : Fin 100) = true := by decide +kernel

theorem pair_row_96 :
    AxisFast.pairRowCheck record cache directions (96 : Fin 100) = true := by decide +kernel

theorem source_piece_97 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (97 : Fin 100))) && decide (record.rotation (97 : Fin 100) = Cube.quaternionMatrix (record.quaternion (97 : Fin 100))) && decide (Cube.determinant3 (record.rotation (97 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_97 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (97 : Fin 100) a) (record.toPlacement.rotation (97 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_97 :
    AxisFast.cacheRowCheck record cache (97 : Fin 100) = true := by decide +kernel

theorem wall_row_97 : CubeFast.wallRowCheck record (97 : Fin 100) = true := by decide +kernel

theorem pair_row_97 :
    AxisFast.pairRowCheck record cache directions (97 : Fin 100) = true := by decide +kernel

theorem source_piece_98 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (98 : Fin 100))) && decide (record.rotation (98 : Fin 100) = Cube.quaternionMatrix (record.quaternion (98 : Fin 100))) && decide (Cube.determinant3 (record.rotation (98 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_98 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (98 : Fin 100) a) (record.toPlacement.rotation (98 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_98 :
    AxisFast.cacheRowCheck record cache (98 : Fin 100) = true := by decide +kernel

theorem wall_row_98 : CubeFast.wallRowCheck record (98 : Fin 100) = true := by decide +kernel

theorem pair_row_98 :
    AxisFast.pairRowCheck record cache directions (98 : Fin 100) = true := by decide +kernel

theorem source_piece_99 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (99 : Fin 100))) && decide (record.rotation (99 : Fin 100) = Cube.quaternionMatrix (record.quaternion (99 : Fin 100))) && decide (Cube.determinant3 (record.rotation (99 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_99 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (99 : Fin 100) a) (record.toPlacement.rotation (99 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_99 :
    AxisFast.cacheRowCheck record cache (99 : Fin 100) = true := by decide +kernel

theorem wall_row_99 : CubeFast.wallRowCheck record (99 : Fin 100) = true := by decide +kernel

theorem pair_row_99 :
    AxisFast.pairRowCheck record cache directions (99 : Fin 100) = true := by decide +kernel

#print axioms source_piece_95
#print axioms gram_piece_95
#print axioms cache_row_95
#print axioms wall_row_95
#print axioms pair_row_95
#print axioms source_piece_96
#print axioms gram_piece_96
#print axioms cache_row_96
#print axioms wall_row_96
#print axioms pair_row_96
#print axioms source_piece_97
#print axioms gram_piece_97
#print axioms cache_row_97
#print axioms wall_row_97
#print axioms pair_row_97
#print axioms source_piece_98
#print axioms gram_piece_98
#print axioms cache_row_98
#print axioms wall_row_98
#print axioms pair_row_98
#print axioms source_piece_99
#print axioms gram_piece_99
#print axioms cache_row_99
#print axioms wall_row_99
#print axioms pair_row_99
end PackingCertificates.Catalogue.CRcubincub_n100
