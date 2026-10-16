import PackingCertificates.Catalogue.CRcubincub_n34.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n34
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_5 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (5 : Fin 34))) && decide (record.rotation (5 : Fin 34) = Cube.quaternionMatrix (record.quaternion (5 : Fin 34))) && decide (Cube.determinant3 (record.rotation (5 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_5 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (5 : Fin 34) a) (record.toPlacement.rotation (5 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_5 :
    AxisFast.cacheRowCheck record cache (5 : Fin 34) = true := by decide +kernel

theorem wall_row_5 : CubeFast.wallRowCheck record (5 : Fin 34) = true := by decide +kernel

theorem pair_row_5 :
    AxisFast.pairRowCheck record cache directions (5 : Fin 34) = true := by decide +kernel

theorem source_piece_6 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (6 : Fin 34))) && decide (record.rotation (6 : Fin 34) = Cube.quaternionMatrix (record.quaternion (6 : Fin 34))) && decide (Cube.determinant3 (record.rotation (6 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_6 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (6 : Fin 34) a) (record.toPlacement.rotation (6 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_6 :
    AxisFast.cacheRowCheck record cache (6 : Fin 34) = true := by decide +kernel

theorem wall_row_6 : CubeFast.wallRowCheck record (6 : Fin 34) = true := by decide +kernel

theorem pair_row_6 :
    AxisFast.pairRowCheck record cache directions (6 : Fin 34) = true := by decide +kernel

theorem source_piece_7 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (7 : Fin 34))) && decide (record.rotation (7 : Fin 34) = Cube.quaternionMatrix (record.quaternion (7 : Fin 34))) && decide (Cube.determinant3 (record.rotation (7 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_7 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (7 : Fin 34) a) (record.toPlacement.rotation (7 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_7 :
    AxisFast.cacheRowCheck record cache (7 : Fin 34) = true := by decide +kernel

theorem wall_row_7 : CubeFast.wallRowCheck record (7 : Fin 34) = true := by decide +kernel

theorem pair_row_7 :
    AxisFast.pairRowCheck record cache directions (7 : Fin 34) = true := by decide +kernel

theorem source_piece_8 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (8 : Fin 34))) && decide (record.rotation (8 : Fin 34) = Cube.quaternionMatrix (record.quaternion (8 : Fin 34))) && decide (Cube.determinant3 (record.rotation (8 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_8 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (8 : Fin 34) a) (record.toPlacement.rotation (8 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_8 :
    AxisFast.cacheRowCheck record cache (8 : Fin 34) = true := by decide +kernel

theorem wall_row_8 : CubeFast.wallRowCheck record (8 : Fin 34) = true := by decide +kernel

theorem pair_row_8 :
    AxisFast.pairRowCheck record cache directions (8 : Fin 34) = true := by decide +kernel

theorem source_piece_9 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (9 : Fin 34))) && decide (record.rotation (9 : Fin 34) = Cube.quaternionMatrix (record.quaternion (9 : Fin 34))) && decide (Cube.determinant3 (record.rotation (9 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_9 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (9 : Fin 34) a) (record.toPlacement.rotation (9 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_9 :
    AxisFast.cacheRowCheck record cache (9 : Fin 34) = true := by decide +kernel

theorem wall_row_9 : CubeFast.wallRowCheck record (9 : Fin 34) = true := by decide +kernel

theorem pair_row_9 :
    AxisFast.pairRowCheck record cache directions (9 : Fin 34) = true := by decide +kernel

#print axioms source_piece_5
#print axioms gram_piece_5
#print axioms cache_row_5
#print axioms wall_row_5
#print axioms pair_row_5
#print axioms source_piece_6
#print axioms gram_piece_6
#print axioms cache_row_6
#print axioms wall_row_6
#print axioms pair_row_6
#print axioms source_piece_7
#print axioms gram_piece_7
#print axioms cache_row_7
#print axioms wall_row_7
#print axioms pair_row_7
#print axioms source_piece_8
#print axioms gram_piece_8
#print axioms cache_row_8
#print axioms wall_row_8
#print axioms pair_row_8
#print axioms source_piece_9
#print axioms gram_piece_9
#print axioms cache_row_9
#print axioms wall_row_9
#print axioms pair_row_9
end PackingCertificates.Catalogue.CRcubincub_n34
