import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_65 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (65 : Fin 100))) && decide (record.rotation (65 : Fin 100) = Cube.quaternionMatrix (record.quaternion (65 : Fin 100))) && decide (Cube.determinant3 (record.rotation (65 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_65 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (65 : Fin 100) a) (record.toPlacement.rotation (65 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_65 :
    AxisFast.cacheRowCheck record cache (65 : Fin 100) = true := by decide +kernel

theorem wall_row_65 : CubeFast.wallRowCheck record (65 : Fin 100) = true := by decide +kernel

theorem pair_row_65 :
    AxisFast.pairRowCheck record cache directions (65 : Fin 100) = true := by decide +kernel

theorem source_piece_66 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (66 : Fin 100))) && decide (record.rotation (66 : Fin 100) = Cube.quaternionMatrix (record.quaternion (66 : Fin 100))) && decide (Cube.determinant3 (record.rotation (66 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_66 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (66 : Fin 100) a) (record.toPlacement.rotation (66 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_66 :
    AxisFast.cacheRowCheck record cache (66 : Fin 100) = true := by decide +kernel

theorem wall_row_66 : CubeFast.wallRowCheck record (66 : Fin 100) = true := by decide +kernel

theorem pair_row_66 :
    AxisFast.pairRowCheck record cache directions (66 : Fin 100) = true := by decide +kernel

theorem source_piece_67 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (67 : Fin 100))) && decide (record.rotation (67 : Fin 100) = Cube.quaternionMatrix (record.quaternion (67 : Fin 100))) && decide (Cube.determinant3 (record.rotation (67 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_67 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (67 : Fin 100) a) (record.toPlacement.rotation (67 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_67 :
    AxisFast.cacheRowCheck record cache (67 : Fin 100) = true := by decide +kernel

theorem wall_row_67 : CubeFast.wallRowCheck record (67 : Fin 100) = true := by decide +kernel

theorem pair_row_67 :
    AxisFast.pairRowCheck record cache directions (67 : Fin 100) = true := by decide +kernel

theorem source_piece_68 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (68 : Fin 100))) && decide (record.rotation (68 : Fin 100) = Cube.quaternionMatrix (record.quaternion (68 : Fin 100))) && decide (Cube.determinant3 (record.rotation (68 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_68 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (68 : Fin 100) a) (record.toPlacement.rotation (68 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_68 :
    AxisFast.cacheRowCheck record cache (68 : Fin 100) = true := by decide +kernel

theorem wall_row_68 : CubeFast.wallRowCheck record (68 : Fin 100) = true := by decide +kernel

theorem pair_row_68 :
    AxisFast.pairRowCheck record cache directions (68 : Fin 100) = true := by decide +kernel

theorem source_piece_69 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (69 : Fin 100))) && decide (record.rotation (69 : Fin 100) = Cube.quaternionMatrix (record.quaternion (69 : Fin 100))) && decide (Cube.determinant3 (record.rotation (69 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_69 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (69 : Fin 100) a) (record.toPlacement.rotation (69 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_69 :
    AxisFast.cacheRowCheck record cache (69 : Fin 100) = true := by decide +kernel

theorem wall_row_69 : CubeFast.wallRowCheck record (69 : Fin 100) = true := by decide +kernel

theorem pair_row_69 :
    AxisFast.pairRowCheck record cache directions (69 : Fin 100) = true := by decide +kernel

#print axioms source_piece_65
#print axioms gram_piece_65
#print axioms cache_row_65
#print axioms wall_row_65
#print axioms pair_row_65
#print axioms source_piece_66
#print axioms gram_piece_66
#print axioms cache_row_66
#print axioms wall_row_66
#print axioms pair_row_66
#print axioms source_piece_67
#print axioms gram_piece_67
#print axioms cache_row_67
#print axioms wall_row_67
#print axioms pair_row_67
#print axioms source_piece_68
#print axioms gram_piece_68
#print axioms cache_row_68
#print axioms wall_row_68
#print axioms pair_row_68
#print axioms source_piece_69
#print axioms gram_piece_69
#print axioms cache_row_69
#print axioms wall_row_69
#print axioms pair_row_69
end PackingCertificates.Catalogue.CRcubincub_n100
