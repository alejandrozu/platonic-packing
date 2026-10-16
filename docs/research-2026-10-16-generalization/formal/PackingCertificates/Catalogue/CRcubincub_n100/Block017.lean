import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_85 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (85 : Fin 100))) && decide (record.rotation (85 : Fin 100) = Cube.quaternionMatrix (record.quaternion (85 : Fin 100))) && decide (Cube.determinant3 (record.rotation (85 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_85 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (85 : Fin 100) a) (record.toPlacement.rotation (85 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_85 :
    AxisFast.cacheRowCheck record cache (85 : Fin 100) = true := by decide +kernel

theorem wall_row_85 : CubeFast.wallRowCheck record (85 : Fin 100) = true := by decide +kernel

theorem pair_row_85 :
    AxisFast.pairRowCheck record cache directions (85 : Fin 100) = true := by decide +kernel

theorem source_piece_86 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (86 : Fin 100))) && decide (record.rotation (86 : Fin 100) = Cube.quaternionMatrix (record.quaternion (86 : Fin 100))) && decide (Cube.determinant3 (record.rotation (86 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_86 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (86 : Fin 100) a) (record.toPlacement.rotation (86 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_86 :
    AxisFast.cacheRowCheck record cache (86 : Fin 100) = true := by decide +kernel

theorem wall_row_86 : CubeFast.wallRowCheck record (86 : Fin 100) = true := by decide +kernel

theorem pair_row_86 :
    AxisFast.pairRowCheck record cache directions (86 : Fin 100) = true := by decide +kernel

theorem source_piece_87 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (87 : Fin 100))) && decide (record.rotation (87 : Fin 100) = Cube.quaternionMatrix (record.quaternion (87 : Fin 100))) && decide (Cube.determinant3 (record.rotation (87 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_87 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (87 : Fin 100) a) (record.toPlacement.rotation (87 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_87 :
    AxisFast.cacheRowCheck record cache (87 : Fin 100) = true := by decide +kernel

theorem wall_row_87 : CubeFast.wallRowCheck record (87 : Fin 100) = true := by decide +kernel

theorem pair_row_87 :
    AxisFast.pairRowCheck record cache directions (87 : Fin 100) = true := by decide +kernel

theorem source_piece_88 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (88 : Fin 100))) && decide (record.rotation (88 : Fin 100) = Cube.quaternionMatrix (record.quaternion (88 : Fin 100))) && decide (Cube.determinant3 (record.rotation (88 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_88 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (88 : Fin 100) a) (record.toPlacement.rotation (88 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_88 :
    AxisFast.cacheRowCheck record cache (88 : Fin 100) = true := by decide +kernel

theorem wall_row_88 : CubeFast.wallRowCheck record (88 : Fin 100) = true := by decide +kernel

theorem pair_row_88 :
    AxisFast.pairRowCheck record cache directions (88 : Fin 100) = true := by decide +kernel

theorem source_piece_89 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (89 : Fin 100))) && decide (record.rotation (89 : Fin 100) = Cube.quaternionMatrix (record.quaternion (89 : Fin 100))) && decide (Cube.determinant3 (record.rotation (89 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_89 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (89 : Fin 100) a) (record.toPlacement.rotation (89 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_89 :
    AxisFast.cacheRowCheck record cache (89 : Fin 100) = true := by decide +kernel

theorem wall_row_89 : CubeFast.wallRowCheck record (89 : Fin 100) = true := by decide +kernel

theorem pair_row_89 :
    AxisFast.pairRowCheck record cache directions (89 : Fin 100) = true := by decide +kernel

#print axioms source_piece_85
#print axioms gram_piece_85
#print axioms cache_row_85
#print axioms wall_row_85
#print axioms pair_row_85
#print axioms source_piece_86
#print axioms gram_piece_86
#print axioms cache_row_86
#print axioms wall_row_86
#print axioms pair_row_86
#print axioms source_piece_87
#print axioms gram_piece_87
#print axioms cache_row_87
#print axioms wall_row_87
#print axioms pair_row_87
#print axioms source_piece_88
#print axioms gram_piece_88
#print axioms cache_row_88
#print axioms wall_row_88
#print axioms pair_row_88
#print axioms source_piece_89
#print axioms gram_piece_89
#print axioms cache_row_89
#print axioms wall_row_89
#print axioms pair_row_89
end PackingCertificates.Catalogue.CRcubincub_n100
