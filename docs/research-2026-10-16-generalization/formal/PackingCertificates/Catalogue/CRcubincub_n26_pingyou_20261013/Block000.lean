import PackingCertificates.Catalogue.CRcubincub_n26_pingyou_20261013.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n26_pingyou_20261013
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_0 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (0 : Fin 26))) && decide (record.rotation (0 : Fin 26) = Cube.quaternionMatrix (record.quaternion (0 : Fin 26))) && decide (Cube.determinant3 (record.rotation (0 : Fin 26)) = 1)) = true := by decide +kernel

theorem gram_piece_0 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (0 : Fin 26) a) (record.toPlacement.rotation (0 : Fin 26) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_0 :
    AxisFast.cacheRowCheck record cache (0 : Fin 26) = true := by decide +kernel

theorem wall_row_0 : CubeFast.wallRowCheck record (0 : Fin 26) = true := by decide +kernel

theorem pair_row_0 :
    AxisFast.pairRowCheck record cache directions (0 : Fin 26) = true := by decide +kernel

theorem source_piece_1 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (1 : Fin 26))) && decide (record.rotation (1 : Fin 26) = Cube.quaternionMatrix (record.quaternion (1 : Fin 26))) && decide (Cube.determinant3 (record.rotation (1 : Fin 26)) = 1)) = true := by decide +kernel

theorem gram_piece_1 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (1 : Fin 26) a) (record.toPlacement.rotation (1 : Fin 26) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_1 :
    AxisFast.cacheRowCheck record cache (1 : Fin 26) = true := by decide +kernel

theorem wall_row_1 : CubeFast.wallRowCheck record (1 : Fin 26) = true := by decide +kernel

theorem pair_row_1 :
    AxisFast.pairRowCheck record cache directions (1 : Fin 26) = true := by decide +kernel

theorem source_piece_2 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (2 : Fin 26))) && decide (record.rotation (2 : Fin 26) = Cube.quaternionMatrix (record.quaternion (2 : Fin 26))) && decide (Cube.determinant3 (record.rotation (2 : Fin 26)) = 1)) = true := by decide +kernel

theorem gram_piece_2 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (2 : Fin 26) a) (record.toPlacement.rotation (2 : Fin 26) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_2 :
    AxisFast.cacheRowCheck record cache (2 : Fin 26) = true := by decide +kernel

theorem wall_row_2 : CubeFast.wallRowCheck record (2 : Fin 26) = true := by decide +kernel

theorem pair_row_2 :
    AxisFast.pairRowCheck record cache directions (2 : Fin 26) = true := by decide +kernel

theorem source_piece_3 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (3 : Fin 26))) && decide (record.rotation (3 : Fin 26) = Cube.quaternionMatrix (record.quaternion (3 : Fin 26))) && decide (Cube.determinant3 (record.rotation (3 : Fin 26)) = 1)) = true := by decide +kernel

theorem gram_piece_3 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (3 : Fin 26) a) (record.toPlacement.rotation (3 : Fin 26) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_3 :
    AxisFast.cacheRowCheck record cache (3 : Fin 26) = true := by decide +kernel

theorem wall_row_3 : CubeFast.wallRowCheck record (3 : Fin 26) = true := by decide +kernel

theorem pair_row_3 :
    AxisFast.pairRowCheck record cache directions (3 : Fin 26) = true := by decide +kernel

theorem source_piece_4 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (4 : Fin 26))) && decide (record.rotation (4 : Fin 26) = Cube.quaternionMatrix (record.quaternion (4 : Fin 26))) && decide (Cube.determinant3 (record.rotation (4 : Fin 26)) = 1)) = true := by decide +kernel

theorem gram_piece_4 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (4 : Fin 26) a) (record.toPlacement.rotation (4 : Fin 26) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_4 :
    AxisFast.cacheRowCheck record cache (4 : Fin 26) = true := by decide +kernel

theorem wall_row_4 : CubeFast.wallRowCheck record (4 : Fin 26) = true := by decide +kernel

theorem pair_row_4 :
    AxisFast.pairRowCheck record cache directions (4 : Fin 26) = true := by decide +kernel

#print axioms source_piece_0
#print axioms gram_piece_0
#print axioms cache_row_0
#print axioms wall_row_0
#print axioms pair_row_0
#print axioms source_piece_1
#print axioms gram_piece_1
#print axioms cache_row_1
#print axioms wall_row_1
#print axioms pair_row_1
#print axioms source_piece_2
#print axioms gram_piece_2
#print axioms cache_row_2
#print axioms wall_row_2
#print axioms pair_row_2
#print axioms source_piece_3
#print axioms gram_piece_3
#print axioms cache_row_3
#print axioms wall_row_3
#print axioms pair_row_3
#print axioms source_piece_4
#print axioms gram_piece_4
#print axioms cache_row_4
#print axioms wall_row_4
#print axioms pair_row_4
end PackingCertificates.Catalogue.CRcubincub_n26_pingyou_20261013
