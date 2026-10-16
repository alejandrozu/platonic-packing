import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_30 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (30 : Fin 100))) && decide (record.rotation (30 : Fin 100) = Cube.quaternionMatrix (record.quaternion (30 : Fin 100))) && decide (Cube.determinant3 (record.rotation (30 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_30 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (30 : Fin 100) a) (record.toPlacement.rotation (30 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_30 :
    AxisFast.cacheRowCheck record cache (30 : Fin 100) = true := by decide +kernel

theorem wall_row_30 : CubeFast.wallRowCheck record (30 : Fin 100) = true := by decide +kernel

theorem pair_row_30 :
    AxisFast.pairRowCheck record cache directions (30 : Fin 100) = true := by decide +kernel

theorem source_piece_31 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (31 : Fin 100))) && decide (record.rotation (31 : Fin 100) = Cube.quaternionMatrix (record.quaternion (31 : Fin 100))) && decide (Cube.determinant3 (record.rotation (31 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_31 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (31 : Fin 100) a) (record.toPlacement.rotation (31 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_31 :
    AxisFast.cacheRowCheck record cache (31 : Fin 100) = true := by decide +kernel

theorem wall_row_31 : CubeFast.wallRowCheck record (31 : Fin 100) = true := by decide +kernel

theorem pair_row_31 :
    AxisFast.pairRowCheck record cache directions (31 : Fin 100) = true := by decide +kernel

theorem source_piece_32 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (32 : Fin 100))) && decide (record.rotation (32 : Fin 100) = Cube.quaternionMatrix (record.quaternion (32 : Fin 100))) && decide (Cube.determinant3 (record.rotation (32 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_32 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (32 : Fin 100) a) (record.toPlacement.rotation (32 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_32 :
    AxisFast.cacheRowCheck record cache (32 : Fin 100) = true := by decide +kernel

theorem wall_row_32 : CubeFast.wallRowCheck record (32 : Fin 100) = true := by decide +kernel

theorem pair_row_32 :
    AxisFast.pairRowCheck record cache directions (32 : Fin 100) = true := by decide +kernel

theorem source_piece_33 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (33 : Fin 100))) && decide (record.rotation (33 : Fin 100) = Cube.quaternionMatrix (record.quaternion (33 : Fin 100))) && decide (Cube.determinant3 (record.rotation (33 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_33 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (33 : Fin 100) a) (record.toPlacement.rotation (33 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_33 :
    AxisFast.cacheRowCheck record cache (33 : Fin 100) = true := by decide +kernel

theorem wall_row_33 : CubeFast.wallRowCheck record (33 : Fin 100) = true := by decide +kernel

theorem pair_row_33 :
    AxisFast.pairRowCheck record cache directions (33 : Fin 100) = true := by decide +kernel

theorem source_piece_34 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (34 : Fin 100))) && decide (record.rotation (34 : Fin 100) = Cube.quaternionMatrix (record.quaternion (34 : Fin 100))) && decide (Cube.determinant3 (record.rotation (34 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_34 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (34 : Fin 100) a) (record.toPlacement.rotation (34 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_34 :
    AxisFast.cacheRowCheck record cache (34 : Fin 100) = true := by decide +kernel

theorem wall_row_34 : CubeFast.wallRowCheck record (34 : Fin 100) = true := by decide +kernel

theorem pair_row_34 :
    AxisFast.pairRowCheck record cache directions (34 : Fin 100) = true := by decide +kernel

#print axioms source_piece_30
#print axioms gram_piece_30
#print axioms cache_row_30
#print axioms wall_row_30
#print axioms pair_row_30
#print axioms source_piece_31
#print axioms gram_piece_31
#print axioms cache_row_31
#print axioms wall_row_31
#print axioms pair_row_31
#print axioms source_piece_32
#print axioms gram_piece_32
#print axioms cache_row_32
#print axioms wall_row_32
#print axioms pair_row_32
#print axioms source_piece_33
#print axioms gram_piece_33
#print axioms cache_row_33
#print axioms wall_row_33
#print axioms pair_row_33
#print axioms source_piece_34
#print axioms gram_piece_34
#print axioms cache_row_34
#print axioms wall_row_34
#print axioms pair_row_34
end PackingCertificates.Catalogue.CRcubincub_n100
