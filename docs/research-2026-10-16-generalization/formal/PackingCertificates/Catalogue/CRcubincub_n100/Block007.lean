import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_35 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (35 : Fin 100))) && decide (record.rotation (35 : Fin 100) = Cube.quaternionMatrix (record.quaternion (35 : Fin 100))) && decide (Cube.determinant3 (record.rotation (35 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_35 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (35 : Fin 100) a) (record.toPlacement.rotation (35 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_35 :
    AxisFast.cacheRowCheck record cache (35 : Fin 100) = true := by decide +kernel

theorem wall_row_35 : CubeFast.wallRowCheck record (35 : Fin 100) = true := by decide +kernel

theorem pair_row_35 :
    AxisFast.pairRowCheck record cache directions (35 : Fin 100) = true := by decide +kernel

theorem source_piece_36 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (36 : Fin 100))) && decide (record.rotation (36 : Fin 100) = Cube.quaternionMatrix (record.quaternion (36 : Fin 100))) && decide (Cube.determinant3 (record.rotation (36 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_36 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (36 : Fin 100) a) (record.toPlacement.rotation (36 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_36 :
    AxisFast.cacheRowCheck record cache (36 : Fin 100) = true := by decide +kernel

theorem wall_row_36 : CubeFast.wallRowCheck record (36 : Fin 100) = true := by decide +kernel

theorem pair_row_36 :
    AxisFast.pairRowCheck record cache directions (36 : Fin 100) = true := by decide +kernel

theorem source_piece_37 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (37 : Fin 100))) && decide (record.rotation (37 : Fin 100) = Cube.quaternionMatrix (record.quaternion (37 : Fin 100))) && decide (Cube.determinant3 (record.rotation (37 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_37 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (37 : Fin 100) a) (record.toPlacement.rotation (37 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_37 :
    AxisFast.cacheRowCheck record cache (37 : Fin 100) = true := by decide +kernel

theorem wall_row_37 : CubeFast.wallRowCheck record (37 : Fin 100) = true := by decide +kernel

theorem pair_row_37 :
    AxisFast.pairRowCheck record cache directions (37 : Fin 100) = true := by decide +kernel

theorem source_piece_38 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (38 : Fin 100))) && decide (record.rotation (38 : Fin 100) = Cube.quaternionMatrix (record.quaternion (38 : Fin 100))) && decide (Cube.determinant3 (record.rotation (38 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_38 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (38 : Fin 100) a) (record.toPlacement.rotation (38 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_38 :
    AxisFast.cacheRowCheck record cache (38 : Fin 100) = true := by decide +kernel

theorem wall_row_38 : CubeFast.wallRowCheck record (38 : Fin 100) = true := by decide +kernel

theorem pair_row_38 :
    AxisFast.pairRowCheck record cache directions (38 : Fin 100) = true := by decide +kernel

theorem source_piece_39 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (39 : Fin 100))) && decide (record.rotation (39 : Fin 100) = Cube.quaternionMatrix (record.quaternion (39 : Fin 100))) && decide (Cube.determinant3 (record.rotation (39 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_39 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (39 : Fin 100) a) (record.toPlacement.rotation (39 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_39 :
    AxisFast.cacheRowCheck record cache (39 : Fin 100) = true := by decide +kernel

theorem wall_row_39 : CubeFast.wallRowCheck record (39 : Fin 100) = true := by decide +kernel

theorem pair_row_39 :
    AxisFast.pairRowCheck record cache directions (39 : Fin 100) = true := by decide +kernel

#print axioms source_piece_35
#print axioms gram_piece_35
#print axioms cache_row_35
#print axioms wall_row_35
#print axioms pair_row_35
#print axioms source_piece_36
#print axioms gram_piece_36
#print axioms cache_row_36
#print axioms wall_row_36
#print axioms pair_row_36
#print axioms source_piece_37
#print axioms gram_piece_37
#print axioms cache_row_37
#print axioms wall_row_37
#print axioms pair_row_37
#print axioms source_piece_38
#print axioms gram_piece_38
#print axioms cache_row_38
#print axioms wall_row_38
#print axioms pair_row_38
#print axioms source_piece_39
#print axioms gram_piece_39
#print axioms cache_row_39
#print axioms wall_row_39
#print axioms pair_row_39
end PackingCertificates.Catalogue.CRcubincub_n100
