import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_40 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (40 : Fin 100))) && decide (record.rotation (40 : Fin 100) = Cube.quaternionMatrix (record.quaternion (40 : Fin 100))) && decide (Cube.determinant3 (record.rotation (40 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_40 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (40 : Fin 100) a) (record.toPlacement.rotation (40 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_40 :
    AxisFast.cacheRowCheck record cache (40 : Fin 100) = true := by decide +kernel

theorem wall_row_40 : CubeFast.wallRowCheck record (40 : Fin 100) = true := by decide +kernel

theorem pair_row_40 :
    AxisFast.pairRowCheck record cache directions (40 : Fin 100) = true := by decide +kernel

theorem source_piece_41 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (41 : Fin 100))) && decide (record.rotation (41 : Fin 100) = Cube.quaternionMatrix (record.quaternion (41 : Fin 100))) && decide (Cube.determinant3 (record.rotation (41 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_41 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (41 : Fin 100) a) (record.toPlacement.rotation (41 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_41 :
    AxisFast.cacheRowCheck record cache (41 : Fin 100) = true := by decide +kernel

theorem wall_row_41 : CubeFast.wallRowCheck record (41 : Fin 100) = true := by decide +kernel

theorem pair_row_41 :
    AxisFast.pairRowCheck record cache directions (41 : Fin 100) = true := by decide +kernel

theorem source_piece_42 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (42 : Fin 100))) && decide (record.rotation (42 : Fin 100) = Cube.quaternionMatrix (record.quaternion (42 : Fin 100))) && decide (Cube.determinant3 (record.rotation (42 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_42 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (42 : Fin 100) a) (record.toPlacement.rotation (42 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_42 :
    AxisFast.cacheRowCheck record cache (42 : Fin 100) = true := by decide +kernel

theorem wall_row_42 : CubeFast.wallRowCheck record (42 : Fin 100) = true := by decide +kernel

theorem pair_row_42 :
    AxisFast.pairRowCheck record cache directions (42 : Fin 100) = true := by decide +kernel

theorem source_piece_43 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (43 : Fin 100))) && decide (record.rotation (43 : Fin 100) = Cube.quaternionMatrix (record.quaternion (43 : Fin 100))) && decide (Cube.determinant3 (record.rotation (43 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_43 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (43 : Fin 100) a) (record.toPlacement.rotation (43 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_43 :
    AxisFast.cacheRowCheck record cache (43 : Fin 100) = true := by decide +kernel

theorem wall_row_43 : CubeFast.wallRowCheck record (43 : Fin 100) = true := by decide +kernel

theorem pair_row_43 :
    AxisFast.pairRowCheck record cache directions (43 : Fin 100) = true := by decide +kernel

theorem source_piece_44 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (44 : Fin 100))) && decide (record.rotation (44 : Fin 100) = Cube.quaternionMatrix (record.quaternion (44 : Fin 100))) && decide (Cube.determinant3 (record.rotation (44 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_44 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (44 : Fin 100) a) (record.toPlacement.rotation (44 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_44 :
    AxisFast.cacheRowCheck record cache (44 : Fin 100) = true := by decide +kernel

theorem wall_row_44 : CubeFast.wallRowCheck record (44 : Fin 100) = true := by decide +kernel

theorem pair_row_44 :
    AxisFast.pairRowCheck record cache directions (44 : Fin 100) = true := by decide +kernel

#print axioms source_piece_40
#print axioms gram_piece_40
#print axioms cache_row_40
#print axioms wall_row_40
#print axioms pair_row_40
#print axioms source_piece_41
#print axioms gram_piece_41
#print axioms cache_row_41
#print axioms wall_row_41
#print axioms pair_row_41
#print axioms source_piece_42
#print axioms gram_piece_42
#print axioms cache_row_42
#print axioms wall_row_42
#print axioms pair_row_42
#print axioms source_piece_43
#print axioms gram_piece_43
#print axioms cache_row_43
#print axioms wall_row_43
#print axioms pair_row_43
#print axioms source_piece_44
#print axioms gram_piece_44
#print axioms cache_row_44
#print axioms wall_row_44
#print axioms pair_row_44
end PackingCertificates.Catalogue.CRcubincub_n100
