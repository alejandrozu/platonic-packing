import PackingCertificates.Catalogue.CRcubincub_n28_pingyou_20261013.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n28_pingyou_20261013
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_20 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (20 : Fin 28))) && decide (record.rotation (20 : Fin 28) = Cube.quaternionMatrix (record.quaternion (20 : Fin 28))) && decide (Cube.determinant3 (record.rotation (20 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_20 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (20 : Fin 28) a) (record.toPlacement.rotation (20 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_20 :
    AxisFast.cacheRowCheck record cache (20 : Fin 28) = true := by decide +kernel

theorem wall_row_20 : CubeFast.wallRowCheck record (20 : Fin 28) = true := by decide +kernel

theorem pair_row_20 :
    AxisFast.pairRowCheck record cache directions (20 : Fin 28) = true := by decide +kernel

theorem source_piece_21 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (21 : Fin 28))) && decide (record.rotation (21 : Fin 28) = Cube.quaternionMatrix (record.quaternion (21 : Fin 28))) && decide (Cube.determinant3 (record.rotation (21 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_21 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (21 : Fin 28) a) (record.toPlacement.rotation (21 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_21 :
    AxisFast.cacheRowCheck record cache (21 : Fin 28) = true := by decide +kernel

theorem wall_row_21 : CubeFast.wallRowCheck record (21 : Fin 28) = true := by decide +kernel

theorem pair_row_21 :
    AxisFast.pairRowCheck record cache directions (21 : Fin 28) = true := by decide +kernel

theorem source_piece_22 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (22 : Fin 28))) && decide (record.rotation (22 : Fin 28) = Cube.quaternionMatrix (record.quaternion (22 : Fin 28))) && decide (Cube.determinant3 (record.rotation (22 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_22 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (22 : Fin 28) a) (record.toPlacement.rotation (22 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_22 :
    AxisFast.cacheRowCheck record cache (22 : Fin 28) = true := by decide +kernel

theorem wall_row_22 : CubeFast.wallRowCheck record (22 : Fin 28) = true := by decide +kernel

theorem pair_row_22 :
    AxisFast.pairRowCheck record cache directions (22 : Fin 28) = true := by decide +kernel

theorem source_piece_23 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (23 : Fin 28))) && decide (record.rotation (23 : Fin 28) = Cube.quaternionMatrix (record.quaternion (23 : Fin 28))) && decide (Cube.determinant3 (record.rotation (23 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_23 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (23 : Fin 28) a) (record.toPlacement.rotation (23 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_23 :
    AxisFast.cacheRowCheck record cache (23 : Fin 28) = true := by decide +kernel

theorem wall_row_23 : CubeFast.wallRowCheck record (23 : Fin 28) = true := by decide +kernel

theorem pair_row_23 :
    AxisFast.pairRowCheck record cache directions (23 : Fin 28) = true := by decide +kernel

theorem source_piece_24 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (24 : Fin 28))) && decide (record.rotation (24 : Fin 28) = Cube.quaternionMatrix (record.quaternion (24 : Fin 28))) && decide (Cube.determinant3 (record.rotation (24 : Fin 28)) = 1)) = true := by decide +kernel

theorem gram_piece_24 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (24 : Fin 28) a) (record.toPlacement.rotation (24 : Fin 28) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_24 :
    AxisFast.cacheRowCheck record cache (24 : Fin 28) = true := by decide +kernel

theorem wall_row_24 : CubeFast.wallRowCheck record (24 : Fin 28) = true := by decide +kernel

theorem pair_row_24 :
    AxisFast.pairRowCheck record cache directions (24 : Fin 28) = true := by decide +kernel

#print axioms source_piece_20
#print axioms gram_piece_20
#print axioms cache_row_20
#print axioms wall_row_20
#print axioms pair_row_20
#print axioms source_piece_21
#print axioms gram_piece_21
#print axioms cache_row_21
#print axioms wall_row_21
#print axioms pair_row_21
#print axioms source_piece_22
#print axioms gram_piece_22
#print axioms cache_row_22
#print axioms wall_row_22
#print axioms pair_row_22
#print axioms source_piece_23
#print axioms gram_piece_23
#print axioms cache_row_23
#print axioms wall_row_23
#print axioms pair_row_23
#print axioms source_piece_24
#print axioms gram_piece_24
#print axioms cache_row_24
#print axioms wall_row_24
#print axioms pair_row_24
end PackingCertificates.Catalogue.CRcubincub_n28_pingyou_20261013
