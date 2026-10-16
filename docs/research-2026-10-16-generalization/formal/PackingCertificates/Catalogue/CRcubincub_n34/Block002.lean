import PackingCertificates.Catalogue.CRcubincub_n34.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n34
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_10 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (10 : Fin 34))) && decide (record.rotation (10 : Fin 34) = Cube.quaternionMatrix (record.quaternion (10 : Fin 34))) && decide (Cube.determinant3 (record.rotation (10 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_10 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (10 : Fin 34) a) (record.toPlacement.rotation (10 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_10 :
    AxisFast.cacheRowCheck record cache (10 : Fin 34) = true := by decide +kernel

theorem wall_row_10 : CubeFast.wallRowCheck record (10 : Fin 34) = true := by decide +kernel

theorem pair_row_10 :
    AxisFast.pairRowCheck record cache directions (10 : Fin 34) = true := by decide +kernel

theorem source_piece_11 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (11 : Fin 34))) && decide (record.rotation (11 : Fin 34) = Cube.quaternionMatrix (record.quaternion (11 : Fin 34))) && decide (Cube.determinant3 (record.rotation (11 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_11 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (11 : Fin 34) a) (record.toPlacement.rotation (11 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_11 :
    AxisFast.cacheRowCheck record cache (11 : Fin 34) = true := by decide +kernel

theorem wall_row_11 : CubeFast.wallRowCheck record (11 : Fin 34) = true := by decide +kernel

theorem pair_row_11 :
    AxisFast.pairRowCheck record cache directions (11 : Fin 34) = true := by decide +kernel

theorem source_piece_12 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (12 : Fin 34))) && decide (record.rotation (12 : Fin 34) = Cube.quaternionMatrix (record.quaternion (12 : Fin 34))) && decide (Cube.determinant3 (record.rotation (12 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_12 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (12 : Fin 34) a) (record.toPlacement.rotation (12 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_12 :
    AxisFast.cacheRowCheck record cache (12 : Fin 34) = true := by decide +kernel

theorem wall_row_12 : CubeFast.wallRowCheck record (12 : Fin 34) = true := by decide +kernel

theorem pair_row_12 :
    AxisFast.pairRowCheck record cache directions (12 : Fin 34) = true := by decide +kernel

theorem source_piece_13 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (13 : Fin 34))) && decide (record.rotation (13 : Fin 34) = Cube.quaternionMatrix (record.quaternion (13 : Fin 34))) && decide (Cube.determinant3 (record.rotation (13 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_13 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (13 : Fin 34) a) (record.toPlacement.rotation (13 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_13 :
    AxisFast.cacheRowCheck record cache (13 : Fin 34) = true := by decide +kernel

theorem wall_row_13 : CubeFast.wallRowCheck record (13 : Fin 34) = true := by decide +kernel

theorem pair_row_13 :
    AxisFast.pairRowCheck record cache directions (13 : Fin 34) = true := by decide +kernel

theorem source_piece_14 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (14 : Fin 34))) && decide (record.rotation (14 : Fin 34) = Cube.quaternionMatrix (record.quaternion (14 : Fin 34))) && decide (Cube.determinant3 (record.rotation (14 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_14 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (14 : Fin 34) a) (record.toPlacement.rotation (14 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_14 :
    AxisFast.cacheRowCheck record cache (14 : Fin 34) = true := by decide +kernel

theorem wall_row_14 : CubeFast.wallRowCheck record (14 : Fin 34) = true := by decide +kernel

theorem pair_row_14 :
    AxisFast.pairRowCheck record cache directions (14 : Fin 34) = true := by decide +kernel

#print axioms source_piece_10
#print axioms gram_piece_10
#print axioms cache_row_10
#print axioms wall_row_10
#print axioms pair_row_10
#print axioms source_piece_11
#print axioms gram_piece_11
#print axioms cache_row_11
#print axioms wall_row_11
#print axioms pair_row_11
#print axioms source_piece_12
#print axioms gram_piece_12
#print axioms cache_row_12
#print axioms wall_row_12
#print axioms pair_row_12
#print axioms source_piece_13
#print axioms gram_piece_13
#print axioms cache_row_13
#print axioms wall_row_13
#print axioms pair_row_13
#print axioms source_piece_14
#print axioms gram_piece_14
#print axioms cache_row_14
#print axioms wall_row_14
#print axioms pair_row_14
end PackingCertificates.Catalogue.CRcubincub_n34
