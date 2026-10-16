import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_60 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (60 : Fin 100))) && decide (record.rotation (60 : Fin 100) = Cube.quaternionMatrix (record.quaternion (60 : Fin 100))) && decide (Cube.determinant3 (record.rotation (60 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_60 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (60 : Fin 100) a) (record.toPlacement.rotation (60 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_60 :
    AxisFast.cacheRowCheck record cache (60 : Fin 100) = true := by decide +kernel

theorem wall_row_60 : CubeFast.wallRowCheck record (60 : Fin 100) = true := by decide +kernel

theorem pair_row_60 :
    AxisFast.pairRowCheck record cache directions (60 : Fin 100) = true := by decide +kernel

theorem source_piece_61 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (61 : Fin 100))) && decide (record.rotation (61 : Fin 100) = Cube.quaternionMatrix (record.quaternion (61 : Fin 100))) && decide (Cube.determinant3 (record.rotation (61 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_61 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (61 : Fin 100) a) (record.toPlacement.rotation (61 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_61 :
    AxisFast.cacheRowCheck record cache (61 : Fin 100) = true := by decide +kernel

theorem wall_row_61 : CubeFast.wallRowCheck record (61 : Fin 100) = true := by decide +kernel

theorem pair_row_61 :
    AxisFast.pairRowCheck record cache directions (61 : Fin 100) = true := by decide +kernel

theorem source_piece_62 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (62 : Fin 100))) && decide (record.rotation (62 : Fin 100) = Cube.quaternionMatrix (record.quaternion (62 : Fin 100))) && decide (Cube.determinant3 (record.rotation (62 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_62 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (62 : Fin 100) a) (record.toPlacement.rotation (62 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_62 :
    AxisFast.cacheRowCheck record cache (62 : Fin 100) = true := by decide +kernel

theorem wall_row_62 : CubeFast.wallRowCheck record (62 : Fin 100) = true := by decide +kernel

theorem pair_row_62 :
    AxisFast.pairRowCheck record cache directions (62 : Fin 100) = true := by decide +kernel

theorem source_piece_63 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (63 : Fin 100))) && decide (record.rotation (63 : Fin 100) = Cube.quaternionMatrix (record.quaternion (63 : Fin 100))) && decide (Cube.determinant3 (record.rotation (63 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_63 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (63 : Fin 100) a) (record.toPlacement.rotation (63 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_63 :
    AxisFast.cacheRowCheck record cache (63 : Fin 100) = true := by decide +kernel

theorem wall_row_63 : CubeFast.wallRowCheck record (63 : Fin 100) = true := by decide +kernel

theorem pair_row_63 :
    AxisFast.pairRowCheck record cache directions (63 : Fin 100) = true := by decide +kernel

theorem source_piece_64 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (64 : Fin 100))) && decide (record.rotation (64 : Fin 100) = Cube.quaternionMatrix (record.quaternion (64 : Fin 100))) && decide (Cube.determinant3 (record.rotation (64 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_64 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (64 : Fin 100) a) (record.toPlacement.rotation (64 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_64 :
    AxisFast.cacheRowCheck record cache (64 : Fin 100) = true := by decide +kernel

theorem wall_row_64 : CubeFast.wallRowCheck record (64 : Fin 100) = true := by decide +kernel

theorem pair_row_64 :
    AxisFast.pairRowCheck record cache directions (64 : Fin 100) = true := by decide +kernel

#print axioms source_piece_60
#print axioms gram_piece_60
#print axioms cache_row_60
#print axioms wall_row_60
#print axioms pair_row_60
#print axioms source_piece_61
#print axioms gram_piece_61
#print axioms cache_row_61
#print axioms wall_row_61
#print axioms pair_row_61
#print axioms source_piece_62
#print axioms gram_piece_62
#print axioms cache_row_62
#print axioms wall_row_62
#print axioms pair_row_62
#print axioms source_piece_63
#print axioms gram_piece_63
#print axioms cache_row_63
#print axioms wall_row_63
#print axioms pair_row_63
#print axioms source_piece_64
#print axioms gram_piece_64
#print axioms cache_row_64
#print axioms wall_row_64
#print axioms pair_row_64
end PackingCertificates.Catalogue.CRcubincub_n100
