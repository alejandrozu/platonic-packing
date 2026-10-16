import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_90 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (90 : Fin 100))) && decide (record.rotation (90 : Fin 100) = Cube.quaternionMatrix (record.quaternion (90 : Fin 100))) && decide (Cube.determinant3 (record.rotation (90 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_90 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (90 : Fin 100) a) (record.toPlacement.rotation (90 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_90 :
    AxisFast.cacheRowCheck record cache (90 : Fin 100) = true := by decide +kernel

theorem wall_row_90 : CubeFast.wallRowCheck record (90 : Fin 100) = true := by decide +kernel

theorem pair_row_90 :
    AxisFast.pairRowCheck record cache directions (90 : Fin 100) = true := by decide +kernel

theorem source_piece_91 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (91 : Fin 100))) && decide (record.rotation (91 : Fin 100) = Cube.quaternionMatrix (record.quaternion (91 : Fin 100))) && decide (Cube.determinant3 (record.rotation (91 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_91 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (91 : Fin 100) a) (record.toPlacement.rotation (91 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_91 :
    AxisFast.cacheRowCheck record cache (91 : Fin 100) = true := by decide +kernel

theorem wall_row_91 : CubeFast.wallRowCheck record (91 : Fin 100) = true := by decide +kernel

theorem pair_row_91 :
    AxisFast.pairRowCheck record cache directions (91 : Fin 100) = true := by decide +kernel

theorem source_piece_92 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (92 : Fin 100))) && decide (record.rotation (92 : Fin 100) = Cube.quaternionMatrix (record.quaternion (92 : Fin 100))) && decide (Cube.determinant3 (record.rotation (92 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_92 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (92 : Fin 100) a) (record.toPlacement.rotation (92 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_92 :
    AxisFast.cacheRowCheck record cache (92 : Fin 100) = true := by decide +kernel

theorem wall_row_92 : CubeFast.wallRowCheck record (92 : Fin 100) = true := by decide +kernel

theorem pair_row_92 :
    AxisFast.pairRowCheck record cache directions (92 : Fin 100) = true := by decide +kernel

theorem source_piece_93 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (93 : Fin 100))) && decide (record.rotation (93 : Fin 100) = Cube.quaternionMatrix (record.quaternion (93 : Fin 100))) && decide (Cube.determinant3 (record.rotation (93 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_93 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (93 : Fin 100) a) (record.toPlacement.rotation (93 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_93 :
    AxisFast.cacheRowCheck record cache (93 : Fin 100) = true := by decide +kernel

theorem wall_row_93 : CubeFast.wallRowCheck record (93 : Fin 100) = true := by decide +kernel

theorem pair_row_93 :
    AxisFast.pairRowCheck record cache directions (93 : Fin 100) = true := by decide +kernel

theorem source_piece_94 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (94 : Fin 100))) && decide (record.rotation (94 : Fin 100) = Cube.quaternionMatrix (record.quaternion (94 : Fin 100))) && decide (Cube.determinant3 (record.rotation (94 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_94 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (94 : Fin 100) a) (record.toPlacement.rotation (94 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_94 :
    AxisFast.cacheRowCheck record cache (94 : Fin 100) = true := by decide +kernel

theorem wall_row_94 : CubeFast.wallRowCheck record (94 : Fin 100) = true := by decide +kernel

theorem pair_row_94 :
    AxisFast.pairRowCheck record cache directions (94 : Fin 100) = true := by decide +kernel

#print axioms source_piece_90
#print axioms gram_piece_90
#print axioms cache_row_90
#print axioms wall_row_90
#print axioms pair_row_90
#print axioms source_piece_91
#print axioms gram_piece_91
#print axioms cache_row_91
#print axioms wall_row_91
#print axioms pair_row_91
#print axioms source_piece_92
#print axioms gram_piece_92
#print axioms cache_row_92
#print axioms wall_row_92
#print axioms pair_row_92
#print axioms source_piece_93
#print axioms gram_piece_93
#print axioms cache_row_93
#print axioms wall_row_93
#print axioms pair_row_93
#print axioms source_piece_94
#print axioms gram_piece_94
#print axioms cache_row_94
#print axioms wall_row_94
#print axioms pair_row_94
end PackingCertificates.Catalogue.CRcubincub_n100
