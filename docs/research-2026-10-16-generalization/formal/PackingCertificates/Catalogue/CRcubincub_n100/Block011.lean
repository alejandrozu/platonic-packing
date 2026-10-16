import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_55 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (55 : Fin 100))) && decide (record.rotation (55 : Fin 100) = Cube.quaternionMatrix (record.quaternion (55 : Fin 100))) && decide (Cube.determinant3 (record.rotation (55 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_55 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (55 : Fin 100) a) (record.toPlacement.rotation (55 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_55 :
    AxisFast.cacheRowCheck record cache (55 : Fin 100) = true := by decide +kernel

theorem wall_row_55 : CubeFast.wallRowCheck record (55 : Fin 100) = true := by decide +kernel

theorem pair_row_55 :
    AxisFast.pairRowCheck record cache directions (55 : Fin 100) = true := by decide +kernel

theorem source_piece_56 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (56 : Fin 100))) && decide (record.rotation (56 : Fin 100) = Cube.quaternionMatrix (record.quaternion (56 : Fin 100))) && decide (Cube.determinant3 (record.rotation (56 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_56 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (56 : Fin 100) a) (record.toPlacement.rotation (56 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_56 :
    AxisFast.cacheRowCheck record cache (56 : Fin 100) = true := by decide +kernel

theorem wall_row_56 : CubeFast.wallRowCheck record (56 : Fin 100) = true := by decide +kernel

theorem pair_row_56 :
    AxisFast.pairRowCheck record cache directions (56 : Fin 100) = true := by decide +kernel

theorem source_piece_57 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (57 : Fin 100))) && decide (record.rotation (57 : Fin 100) = Cube.quaternionMatrix (record.quaternion (57 : Fin 100))) && decide (Cube.determinant3 (record.rotation (57 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_57 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (57 : Fin 100) a) (record.toPlacement.rotation (57 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_57 :
    AxisFast.cacheRowCheck record cache (57 : Fin 100) = true := by decide +kernel

theorem wall_row_57 : CubeFast.wallRowCheck record (57 : Fin 100) = true := by decide +kernel

theorem pair_row_57 :
    AxisFast.pairRowCheck record cache directions (57 : Fin 100) = true := by decide +kernel

theorem source_piece_58 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (58 : Fin 100))) && decide (record.rotation (58 : Fin 100) = Cube.quaternionMatrix (record.quaternion (58 : Fin 100))) && decide (Cube.determinant3 (record.rotation (58 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_58 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (58 : Fin 100) a) (record.toPlacement.rotation (58 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_58 :
    AxisFast.cacheRowCheck record cache (58 : Fin 100) = true := by decide +kernel

theorem wall_row_58 : CubeFast.wallRowCheck record (58 : Fin 100) = true := by decide +kernel

theorem pair_row_58 :
    AxisFast.pairRowCheck record cache directions (58 : Fin 100) = true := by decide +kernel

theorem source_piece_59 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (59 : Fin 100))) && decide (record.rotation (59 : Fin 100) = Cube.quaternionMatrix (record.quaternion (59 : Fin 100))) && decide (Cube.determinant3 (record.rotation (59 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_59 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (59 : Fin 100) a) (record.toPlacement.rotation (59 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_59 :
    AxisFast.cacheRowCheck record cache (59 : Fin 100) = true := by decide +kernel

theorem wall_row_59 : CubeFast.wallRowCheck record (59 : Fin 100) = true := by decide +kernel

theorem pair_row_59 :
    AxisFast.pairRowCheck record cache directions (59 : Fin 100) = true := by decide +kernel

#print axioms source_piece_55
#print axioms gram_piece_55
#print axioms cache_row_55
#print axioms wall_row_55
#print axioms pair_row_55
#print axioms source_piece_56
#print axioms gram_piece_56
#print axioms cache_row_56
#print axioms wall_row_56
#print axioms pair_row_56
#print axioms source_piece_57
#print axioms gram_piece_57
#print axioms cache_row_57
#print axioms wall_row_57
#print axioms pair_row_57
#print axioms source_piece_58
#print axioms gram_piece_58
#print axioms cache_row_58
#print axioms wall_row_58
#print axioms pair_row_58
#print axioms source_piece_59
#print axioms gram_piece_59
#print axioms cache_row_59
#print axioms wall_row_59
#print axioms pair_row_59
end PackingCertificates.Catalogue.CRcubincub_n100
