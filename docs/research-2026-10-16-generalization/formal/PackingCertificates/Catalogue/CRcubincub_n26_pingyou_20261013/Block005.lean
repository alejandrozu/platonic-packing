import PackingCertificates.Catalogue.CRcubincub_n26_pingyou_20261013.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n26_pingyou_20261013
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_25 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (25 : Fin 26))) && decide (record.rotation (25 : Fin 26) = Cube.quaternionMatrix (record.quaternion (25 : Fin 26))) && decide (Cube.determinant3 (record.rotation (25 : Fin 26)) = 1)) = true := by decide +kernel

theorem gram_piece_25 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (25 : Fin 26) a) (record.toPlacement.rotation (25 : Fin 26) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_25 :
    AxisFast.cacheRowCheck record cache (25 : Fin 26) = true := by decide +kernel

theorem wall_row_25 : CubeFast.wallRowCheck record (25 : Fin 26) = true := by decide +kernel

theorem pair_row_25 :
    AxisFast.pairRowCheck record cache directions (25 : Fin 26) = true := by decide +kernel

#print axioms source_piece_25
#print axioms gram_piece_25
#print axioms cache_row_25
#print axioms wall_row_25
#print axioms pair_row_25
end PackingCertificates.Catalogue.CRcubincub_n26_pingyou_20261013
