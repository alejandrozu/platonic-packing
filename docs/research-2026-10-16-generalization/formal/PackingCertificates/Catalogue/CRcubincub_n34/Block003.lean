import PackingCertificates.Catalogue.CRcubincub_n34.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n34
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_15 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (15 : Fin 34))) && decide (record.rotation (15 : Fin 34) = Cube.quaternionMatrix (record.quaternion (15 : Fin 34))) && decide (Cube.determinant3 (record.rotation (15 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_15 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (15 : Fin 34) a) (record.toPlacement.rotation (15 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_15 :
    AxisFast.cacheRowCheck record cache (15 : Fin 34) = true := by decide +kernel

theorem wall_row_15 : CubeFast.wallRowCheck record (15 : Fin 34) = true := by decide +kernel

theorem pair_row_15 :
    AxisFast.pairRowCheck record cache directions (15 : Fin 34) = true := by decide +kernel

theorem source_piece_16 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (16 : Fin 34))) && decide (record.rotation (16 : Fin 34) = Cube.quaternionMatrix (record.quaternion (16 : Fin 34))) && decide (Cube.determinant3 (record.rotation (16 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_16 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (16 : Fin 34) a) (record.toPlacement.rotation (16 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_16 :
    AxisFast.cacheRowCheck record cache (16 : Fin 34) = true := by decide +kernel

theorem wall_row_16 : CubeFast.wallRowCheck record (16 : Fin 34) = true := by decide +kernel

theorem pair_row_16 :
    AxisFast.pairRowCheck record cache directions (16 : Fin 34) = true := by decide +kernel

theorem source_piece_17 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (17 : Fin 34))) && decide (record.rotation (17 : Fin 34) = Cube.quaternionMatrix (record.quaternion (17 : Fin 34))) && decide (Cube.determinant3 (record.rotation (17 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_17 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (17 : Fin 34) a) (record.toPlacement.rotation (17 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_17 :
    AxisFast.cacheRowCheck record cache (17 : Fin 34) = true := by decide +kernel

theorem wall_row_17 : CubeFast.wallRowCheck record (17 : Fin 34) = true := by decide +kernel

theorem pair_row_17 :
    AxisFast.pairRowCheck record cache directions (17 : Fin 34) = true := by decide +kernel

theorem source_piece_18 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (18 : Fin 34))) && decide (record.rotation (18 : Fin 34) = Cube.quaternionMatrix (record.quaternion (18 : Fin 34))) && decide (Cube.determinant3 (record.rotation (18 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_18 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (18 : Fin 34) a) (record.toPlacement.rotation (18 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_18 :
    AxisFast.cacheRowCheck record cache (18 : Fin 34) = true := by decide +kernel

theorem wall_row_18 : CubeFast.wallRowCheck record (18 : Fin 34) = true := by decide +kernel

theorem pair_row_18 :
    AxisFast.pairRowCheck record cache directions (18 : Fin 34) = true := by decide +kernel

theorem source_piece_19 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (19 : Fin 34))) && decide (record.rotation (19 : Fin 34) = Cube.quaternionMatrix (record.quaternion (19 : Fin 34))) && decide (Cube.determinant3 (record.rotation (19 : Fin 34)) = 1)) = true := by decide +kernel

theorem gram_piece_19 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (19 : Fin 34) a) (record.toPlacement.rotation (19 : Fin 34) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_19 :
    AxisFast.cacheRowCheck record cache (19 : Fin 34) = true := by decide +kernel

theorem wall_row_19 : CubeFast.wallRowCheck record (19 : Fin 34) = true := by decide +kernel

theorem pair_row_19 :
    AxisFast.pairRowCheck record cache directions (19 : Fin 34) = true := by decide +kernel

#print axioms source_piece_15
#print axioms gram_piece_15
#print axioms cache_row_15
#print axioms wall_row_15
#print axioms pair_row_15
#print axioms source_piece_16
#print axioms gram_piece_16
#print axioms cache_row_16
#print axioms wall_row_16
#print axioms pair_row_16
#print axioms source_piece_17
#print axioms gram_piece_17
#print axioms cache_row_17
#print axioms wall_row_17
#print axioms pair_row_17
#print axioms source_piece_18
#print axioms gram_piece_18
#print axioms cache_row_18
#print axioms wall_row_18
#print axioms pair_row_18
#print axioms source_piece_19
#print axioms gram_piece_19
#print axioms cache_row_19
#print axioms wall_row_19
#print axioms pair_row_19
end PackingCertificates.Catalogue.CRcubincub_n34
