import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_50 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (50 : Fin 100))) && decide (record.rotation (50 : Fin 100) = Cube.quaternionMatrix (record.quaternion (50 : Fin 100))) && decide (Cube.determinant3 (record.rotation (50 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_50 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (50 : Fin 100) a) (record.toPlacement.rotation (50 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_50 :
    AxisFast.cacheRowCheck record cache (50 : Fin 100) = true := by decide +kernel

theorem wall_row_50 : CubeFast.wallRowCheck record (50 : Fin 100) = true := by decide +kernel

theorem pair_row_50 :
    AxisFast.pairRowCheck record cache directions (50 : Fin 100) = true := by decide +kernel

theorem source_piece_51 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (51 : Fin 100))) && decide (record.rotation (51 : Fin 100) = Cube.quaternionMatrix (record.quaternion (51 : Fin 100))) && decide (Cube.determinant3 (record.rotation (51 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_51 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (51 : Fin 100) a) (record.toPlacement.rotation (51 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_51 :
    AxisFast.cacheRowCheck record cache (51 : Fin 100) = true := by decide +kernel

theorem wall_row_51 : CubeFast.wallRowCheck record (51 : Fin 100) = true := by decide +kernel

theorem pair_row_51 :
    AxisFast.pairRowCheck record cache directions (51 : Fin 100) = true := by decide +kernel

theorem source_piece_52 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (52 : Fin 100))) && decide (record.rotation (52 : Fin 100) = Cube.quaternionMatrix (record.quaternion (52 : Fin 100))) && decide (Cube.determinant3 (record.rotation (52 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_52 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (52 : Fin 100) a) (record.toPlacement.rotation (52 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_52 :
    AxisFast.cacheRowCheck record cache (52 : Fin 100) = true := by decide +kernel

theorem wall_row_52 : CubeFast.wallRowCheck record (52 : Fin 100) = true := by decide +kernel

theorem pair_row_52 :
    AxisFast.pairRowCheck record cache directions (52 : Fin 100) = true := by decide +kernel

theorem source_piece_53 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (53 : Fin 100))) && decide (record.rotation (53 : Fin 100) = Cube.quaternionMatrix (record.quaternion (53 : Fin 100))) && decide (Cube.determinant3 (record.rotation (53 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_53 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (53 : Fin 100) a) (record.toPlacement.rotation (53 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_53 :
    AxisFast.cacheRowCheck record cache (53 : Fin 100) = true := by decide +kernel

theorem wall_row_53 : CubeFast.wallRowCheck record (53 : Fin 100) = true := by decide +kernel

theorem pair_row_53 :
    AxisFast.pairRowCheck record cache directions (53 : Fin 100) = true := by decide +kernel

theorem source_piece_54 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (54 : Fin 100))) && decide (record.rotation (54 : Fin 100) = Cube.quaternionMatrix (record.quaternion (54 : Fin 100))) && decide (Cube.determinant3 (record.rotation (54 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_54 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (54 : Fin 100) a) (record.toPlacement.rotation (54 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_54 :
    AxisFast.cacheRowCheck record cache (54 : Fin 100) = true := by decide +kernel

theorem wall_row_54 : CubeFast.wallRowCheck record (54 : Fin 100) = true := by decide +kernel

theorem pair_row_54 :
    AxisFast.pairRowCheck record cache directions (54 : Fin 100) = true := by decide +kernel

#print axioms source_piece_50
#print axioms gram_piece_50
#print axioms cache_row_50
#print axioms wall_row_50
#print axioms pair_row_50
#print axioms source_piece_51
#print axioms gram_piece_51
#print axioms cache_row_51
#print axioms wall_row_51
#print axioms pair_row_51
#print axioms source_piece_52
#print axioms gram_piece_52
#print axioms cache_row_52
#print axioms wall_row_52
#print axioms pair_row_52
#print axioms source_piece_53
#print axioms gram_piece_53
#print axioms cache_row_53
#print axioms wall_row_53
#print axioms pair_row_53
#print axioms source_piece_54
#print axioms gram_piece_54
#print axioms cache_row_54
#print axioms wall_row_54
#print axioms pair_row_54
end PackingCertificates.Catalogue.CRcubincub_n100
