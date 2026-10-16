import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_70 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (70 : Fin 100))) && decide (record.rotation (70 : Fin 100) = Cube.quaternionMatrix (record.quaternion (70 : Fin 100))) && decide (Cube.determinant3 (record.rotation (70 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_70 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (70 : Fin 100) a) (record.toPlacement.rotation (70 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_70 :
    AxisFast.cacheRowCheck record cache (70 : Fin 100) = true := by decide +kernel

theorem wall_row_70 : CubeFast.wallRowCheck record (70 : Fin 100) = true := by decide +kernel

theorem pair_row_70 :
    AxisFast.pairRowCheck record cache directions (70 : Fin 100) = true := by decide +kernel

theorem source_piece_71 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (71 : Fin 100))) && decide (record.rotation (71 : Fin 100) = Cube.quaternionMatrix (record.quaternion (71 : Fin 100))) && decide (Cube.determinant3 (record.rotation (71 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_71 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (71 : Fin 100) a) (record.toPlacement.rotation (71 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_71 :
    AxisFast.cacheRowCheck record cache (71 : Fin 100) = true := by decide +kernel

theorem wall_row_71 : CubeFast.wallRowCheck record (71 : Fin 100) = true := by decide +kernel

theorem pair_row_71 :
    AxisFast.pairRowCheck record cache directions (71 : Fin 100) = true := by decide +kernel

theorem source_piece_72 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (72 : Fin 100))) && decide (record.rotation (72 : Fin 100) = Cube.quaternionMatrix (record.quaternion (72 : Fin 100))) && decide (Cube.determinant3 (record.rotation (72 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_72 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (72 : Fin 100) a) (record.toPlacement.rotation (72 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_72 :
    AxisFast.cacheRowCheck record cache (72 : Fin 100) = true := by decide +kernel

theorem wall_row_72 : CubeFast.wallRowCheck record (72 : Fin 100) = true := by decide +kernel

theorem pair_row_72 :
    AxisFast.pairRowCheck record cache directions (72 : Fin 100) = true := by decide +kernel

theorem source_piece_73 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (73 : Fin 100))) && decide (record.rotation (73 : Fin 100) = Cube.quaternionMatrix (record.quaternion (73 : Fin 100))) && decide (Cube.determinant3 (record.rotation (73 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_73 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (73 : Fin 100) a) (record.toPlacement.rotation (73 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_73 :
    AxisFast.cacheRowCheck record cache (73 : Fin 100) = true := by decide +kernel

theorem wall_row_73 : CubeFast.wallRowCheck record (73 : Fin 100) = true := by decide +kernel

theorem pair_row_73 :
    AxisFast.pairRowCheck record cache directions (73 : Fin 100) = true := by decide +kernel

theorem source_piece_74 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (74 : Fin 100))) && decide (record.rotation (74 : Fin 100) = Cube.quaternionMatrix (record.quaternion (74 : Fin 100))) && decide (Cube.determinant3 (record.rotation (74 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_74 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (74 : Fin 100) a) (record.toPlacement.rotation (74 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_74 :
    AxisFast.cacheRowCheck record cache (74 : Fin 100) = true := by decide +kernel

theorem wall_row_74 : CubeFast.wallRowCheck record (74 : Fin 100) = true := by decide +kernel

theorem pair_row_74 :
    AxisFast.pairRowCheck record cache directions (74 : Fin 100) = true := by decide +kernel

#print axioms source_piece_70
#print axioms gram_piece_70
#print axioms cache_row_70
#print axioms wall_row_70
#print axioms pair_row_70
#print axioms source_piece_71
#print axioms gram_piece_71
#print axioms cache_row_71
#print axioms wall_row_71
#print axioms pair_row_71
#print axioms source_piece_72
#print axioms gram_piece_72
#print axioms cache_row_72
#print axioms wall_row_72
#print axioms pair_row_72
#print axioms source_piece_73
#print axioms gram_piece_73
#print axioms cache_row_73
#print axioms wall_row_73
#print axioms pair_row_73
#print axioms source_piece_74
#print axioms gram_piece_74
#print axioms cache_row_74
#print axioms wall_row_74
#print axioms pair_row_74
end PackingCertificates.Catalogue.CRcubincub_n100
