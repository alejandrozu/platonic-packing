import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_45 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (45 : Fin 100))) && decide (record.rotation (45 : Fin 100) = Cube.quaternionMatrix (record.quaternion (45 : Fin 100))) && decide (Cube.determinant3 (record.rotation (45 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_45 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (45 : Fin 100) a) (record.toPlacement.rotation (45 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_45 :
    AxisFast.cacheRowCheck record cache (45 : Fin 100) = true := by decide +kernel

theorem wall_row_45 : CubeFast.wallRowCheck record (45 : Fin 100) = true := by decide +kernel

theorem pair_row_45 :
    AxisFast.pairRowCheck record cache directions (45 : Fin 100) = true := by decide +kernel

theorem source_piece_46 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (46 : Fin 100))) && decide (record.rotation (46 : Fin 100) = Cube.quaternionMatrix (record.quaternion (46 : Fin 100))) && decide (Cube.determinant3 (record.rotation (46 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_46 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (46 : Fin 100) a) (record.toPlacement.rotation (46 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_46 :
    AxisFast.cacheRowCheck record cache (46 : Fin 100) = true := by decide +kernel

theorem wall_row_46 : CubeFast.wallRowCheck record (46 : Fin 100) = true := by decide +kernel

theorem pair_row_46 :
    AxisFast.pairRowCheck record cache directions (46 : Fin 100) = true := by decide +kernel

theorem source_piece_47 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (47 : Fin 100))) && decide (record.rotation (47 : Fin 100) = Cube.quaternionMatrix (record.quaternion (47 : Fin 100))) && decide (Cube.determinant3 (record.rotation (47 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_47 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (47 : Fin 100) a) (record.toPlacement.rotation (47 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_47 :
    AxisFast.cacheRowCheck record cache (47 : Fin 100) = true := by decide +kernel

theorem wall_row_47 : CubeFast.wallRowCheck record (47 : Fin 100) = true := by decide +kernel

theorem pair_row_47 :
    AxisFast.pairRowCheck record cache directions (47 : Fin 100) = true := by decide +kernel

theorem source_piece_48 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (48 : Fin 100))) && decide (record.rotation (48 : Fin 100) = Cube.quaternionMatrix (record.quaternion (48 : Fin 100))) && decide (Cube.determinant3 (record.rotation (48 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_48 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (48 : Fin 100) a) (record.toPlacement.rotation (48 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_48 :
    AxisFast.cacheRowCheck record cache (48 : Fin 100) = true := by decide +kernel

theorem wall_row_48 : CubeFast.wallRowCheck record (48 : Fin 100) = true := by decide +kernel

theorem pair_row_48 :
    AxisFast.pairRowCheck record cache directions (48 : Fin 100) = true := by decide +kernel

theorem source_piece_49 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (49 : Fin 100))) && decide (record.rotation (49 : Fin 100) = Cube.quaternionMatrix (record.quaternion (49 : Fin 100))) && decide (Cube.determinant3 (record.rotation (49 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_49 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (49 : Fin 100) a) (record.toPlacement.rotation (49 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_49 :
    AxisFast.cacheRowCheck record cache (49 : Fin 100) = true := by decide +kernel

theorem wall_row_49 : CubeFast.wallRowCheck record (49 : Fin 100) = true := by decide +kernel

theorem pair_row_49 :
    AxisFast.pairRowCheck record cache directions (49 : Fin 100) = true := by decide +kernel

#print axioms source_piece_45
#print axioms gram_piece_45
#print axioms cache_row_45
#print axioms wall_row_45
#print axioms pair_row_45
#print axioms source_piece_46
#print axioms gram_piece_46
#print axioms cache_row_46
#print axioms wall_row_46
#print axioms pair_row_46
#print axioms source_piece_47
#print axioms gram_piece_47
#print axioms cache_row_47
#print axioms wall_row_47
#print axioms pair_row_47
#print axioms source_piece_48
#print axioms gram_piece_48
#print axioms cache_row_48
#print axioms wall_row_48
#print axioms pair_row_48
#print axioms source_piece_49
#print axioms gram_piece_49
#print axioms cache_row_49
#print axioms wall_row_49
#print axioms pair_row_49
end PackingCertificates.Catalogue.CRcubincub_n100
