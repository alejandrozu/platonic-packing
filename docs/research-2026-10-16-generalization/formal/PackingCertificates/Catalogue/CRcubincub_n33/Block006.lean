import PackingCertificates.Catalogue.CRcubincub_n33.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n33
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_30 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (30 : Fin 33))) && decide (record.rotation (30 : Fin 33) = Cube.quaternionMatrix (record.quaternion (30 : Fin 33))) && decide (Cube.determinant3 (record.rotation (30 : Fin 33)) = 1)) = true := by decide +kernel

theorem gram_piece_30 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (30 : Fin 33) a) (record.toPlacement.rotation (30 : Fin 33) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_30 :
    AxisFast.cacheRowCheck record cache (30 : Fin 33) = true := by decide +kernel

theorem wall_row_30 : CubeFast.wallRowCheck record (30 : Fin 33) = true := by decide +kernel

theorem pair_row_30 :
    AxisFast.pairRowCheck record cache directions (30 : Fin 33) = true := by decide +kernel

theorem source_piece_31 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (31 : Fin 33))) && decide (record.rotation (31 : Fin 33) = Cube.quaternionMatrix (record.quaternion (31 : Fin 33))) && decide (Cube.determinant3 (record.rotation (31 : Fin 33)) = 1)) = true := by decide +kernel

theorem gram_piece_31 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (31 : Fin 33) a) (record.toPlacement.rotation (31 : Fin 33) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_31 :
    AxisFast.cacheRowCheck record cache (31 : Fin 33) = true := by decide +kernel

theorem wall_row_31 : CubeFast.wallRowCheck record (31 : Fin 33) = true := by decide +kernel

theorem pair_row_31 :
    AxisFast.pairRowCheck record cache directions (31 : Fin 33) = true := by decide +kernel

theorem source_piece_32 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (32 : Fin 33))) && decide (record.rotation (32 : Fin 33) = Cube.quaternionMatrix (record.quaternion (32 : Fin 33))) && decide (Cube.determinant3 (record.rotation (32 : Fin 33)) = 1)) = true := by decide +kernel

theorem gram_piece_32 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (32 : Fin 33) a) (record.toPlacement.rotation (32 : Fin 33) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_32 :
    AxisFast.cacheRowCheck record cache (32 : Fin 33) = true := by decide +kernel

theorem wall_row_32 : CubeFast.wallRowCheck record (32 : Fin 33) = true := by decide +kernel

theorem pair_row_32 :
    AxisFast.pairRowCheck record cache directions (32 : Fin 33) = true := by decide +kernel

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
end PackingCertificates.Catalogue.CRcubincub_n33
