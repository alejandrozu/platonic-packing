import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_80 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (80 : Fin 100))) && decide (record.rotation (80 : Fin 100) = Cube.quaternionMatrix (record.quaternion (80 : Fin 100))) && decide (Cube.determinant3 (record.rotation (80 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_80 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (80 : Fin 100) a) (record.toPlacement.rotation (80 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_80 :
    AxisFast.cacheRowCheck record cache (80 : Fin 100) = true := by decide +kernel

theorem wall_row_80 : CubeFast.wallRowCheck record (80 : Fin 100) = true := by decide +kernel

theorem pair_row_80 :
    AxisFast.pairRowCheck record cache directions (80 : Fin 100) = true := by decide +kernel

theorem source_piece_81 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (81 : Fin 100))) && decide (record.rotation (81 : Fin 100) = Cube.quaternionMatrix (record.quaternion (81 : Fin 100))) && decide (Cube.determinant3 (record.rotation (81 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_81 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (81 : Fin 100) a) (record.toPlacement.rotation (81 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_81 :
    AxisFast.cacheRowCheck record cache (81 : Fin 100) = true := by decide +kernel

theorem wall_row_81 : CubeFast.wallRowCheck record (81 : Fin 100) = true := by decide +kernel

theorem pair_row_81 :
    AxisFast.pairRowCheck record cache directions (81 : Fin 100) = true := by decide +kernel

theorem source_piece_82 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (82 : Fin 100))) && decide (record.rotation (82 : Fin 100) = Cube.quaternionMatrix (record.quaternion (82 : Fin 100))) && decide (Cube.determinant3 (record.rotation (82 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_82 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (82 : Fin 100) a) (record.toPlacement.rotation (82 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_82 :
    AxisFast.cacheRowCheck record cache (82 : Fin 100) = true := by decide +kernel

theorem wall_row_82 : CubeFast.wallRowCheck record (82 : Fin 100) = true := by decide +kernel

theorem pair_row_82 :
    AxisFast.pairRowCheck record cache directions (82 : Fin 100) = true := by decide +kernel

theorem source_piece_83 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (83 : Fin 100))) && decide (record.rotation (83 : Fin 100) = Cube.quaternionMatrix (record.quaternion (83 : Fin 100))) && decide (Cube.determinant3 (record.rotation (83 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_83 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (83 : Fin 100) a) (record.toPlacement.rotation (83 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_83 :
    AxisFast.cacheRowCheck record cache (83 : Fin 100) = true := by decide +kernel

theorem wall_row_83 : CubeFast.wallRowCheck record (83 : Fin 100) = true := by decide +kernel

theorem pair_row_83 :
    AxisFast.pairRowCheck record cache directions (83 : Fin 100) = true := by decide +kernel

theorem source_piece_84 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (84 : Fin 100))) && decide (record.rotation (84 : Fin 100) = Cube.quaternionMatrix (record.quaternion (84 : Fin 100))) && decide (Cube.determinant3 (record.rotation (84 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_84 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (84 : Fin 100) a) (record.toPlacement.rotation (84 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_84 :
    AxisFast.cacheRowCheck record cache (84 : Fin 100) = true := by decide +kernel

theorem wall_row_84 : CubeFast.wallRowCheck record (84 : Fin 100) = true := by decide +kernel

theorem pair_row_84 :
    AxisFast.pairRowCheck record cache directions (84 : Fin 100) = true := by decide +kernel

#print axioms source_piece_80
#print axioms gram_piece_80
#print axioms cache_row_80
#print axioms wall_row_80
#print axioms pair_row_80
#print axioms source_piece_81
#print axioms gram_piece_81
#print axioms cache_row_81
#print axioms wall_row_81
#print axioms pair_row_81
#print axioms source_piece_82
#print axioms gram_piece_82
#print axioms cache_row_82
#print axioms wall_row_82
#print axioms pair_row_82
#print axioms source_piece_83
#print axioms gram_piece_83
#print axioms cache_row_83
#print axioms wall_row_83
#print axioms pair_row_83
#print axioms source_piece_84
#print axioms gram_piece_84
#print axioms cache_row_84
#print axioms wall_row_84
#print axioms pair_row_84
end PackingCertificates.Catalogue.CRcubincub_n100
