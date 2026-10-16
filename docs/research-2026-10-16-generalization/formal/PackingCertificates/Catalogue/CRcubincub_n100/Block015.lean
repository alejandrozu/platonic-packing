import PackingCertificates.Catalogue.CRcubincub_n100.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_piece_75 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (75 : Fin 100))) && decide (record.rotation (75 : Fin 100) = Cube.quaternionMatrix (record.quaternion (75 : Fin 100))) && decide (Cube.determinant3 (record.rotation (75 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_75 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (75 : Fin 100) a) (record.toPlacement.rotation (75 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_75 :
    AxisFast.cacheRowCheck record cache (75 : Fin 100) = true := by decide +kernel

theorem wall_row_75 : CubeFast.wallRowCheck record (75 : Fin 100) = true := by decide +kernel

theorem pair_row_75 :
    AxisFast.pairRowCheck record cache directions (75 : Fin 100) = true := by decide +kernel

theorem source_piece_76 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (76 : Fin 100))) && decide (record.rotation (76 : Fin 100) = Cube.quaternionMatrix (record.quaternion (76 : Fin 100))) && decide (Cube.determinant3 (record.rotation (76 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_76 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (76 : Fin 100) a) (record.toPlacement.rotation (76 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_76 :
    AxisFast.cacheRowCheck record cache (76 : Fin 100) = true := by decide +kernel

theorem wall_row_76 : CubeFast.wallRowCheck record (76 : Fin 100) = true := by decide +kernel

theorem pair_row_76 :
    AxisFast.pairRowCheck record cache directions (76 : Fin 100) = true := by decide +kernel

theorem source_piece_77 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (77 : Fin 100))) && decide (record.rotation (77 : Fin 100) = Cube.quaternionMatrix (record.quaternion (77 : Fin 100))) && decide (Cube.determinant3 (record.rotation (77 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_77 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (77 : Fin 100) a) (record.toPlacement.rotation (77 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_77 :
    AxisFast.cacheRowCheck record cache (77 : Fin 100) = true := by decide +kernel

theorem wall_row_77 : CubeFast.wallRowCheck record (77 : Fin 100) = true := by decide +kernel

theorem pair_row_77 :
    AxisFast.pairRowCheck record cache directions (77 : Fin 100) = true := by decide +kernel

theorem source_piece_78 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (78 : Fin 100))) && decide (record.rotation (78 : Fin 100) = Cube.quaternionMatrix (record.quaternion (78 : Fin 100))) && decide (Cube.determinant3 (record.rotation (78 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_78 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (78 : Fin 100) a) (record.toPlacement.rotation (78 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_78 :
    AxisFast.cacheRowCheck record cache (78 : Fin 100) = true := by decide +kernel

theorem wall_row_78 : CubeFast.wallRowCheck record (78 : Fin 100) = true := by decide +kernel

theorem pair_row_78 :
    AxisFast.pairRowCheck record cache directions (78 : Fin 100) = true := by decide +kernel

theorem source_piece_79 :
    (decide (0 < Cube.quaternionNormSq (record.quaternion (79 : Fin 100))) && decide (record.rotation (79 : Fin 100) = Cube.quaternionMatrix (record.quaternion (79 : Fin 100))) && decide (Cube.determinant3 (record.rotation (79 : Fin 100)) = 1)) = true := by decide +kernel

theorem gram_piece_79 :
    allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation (79 : Fin 100) a) (record.toPlacement.rotation (79 : Fin 100) b) = if a = b then 1 else 0))) = true := by decide +kernel

theorem cache_row_79 :
    AxisFast.cacheRowCheck record cache (79 : Fin 100) = true := by decide +kernel

theorem wall_row_79 : CubeFast.wallRowCheck record (79 : Fin 100) = true := by decide +kernel

theorem pair_row_79 :
    AxisFast.pairRowCheck record cache directions (79 : Fin 100) = true := by decide +kernel

#print axioms source_piece_75
#print axioms gram_piece_75
#print axioms cache_row_75
#print axioms wall_row_75
#print axioms pair_row_75
#print axioms source_piece_76
#print axioms gram_piece_76
#print axioms cache_row_76
#print axioms wall_row_76
#print axioms pair_row_76
#print axioms source_piece_77
#print axioms gram_piece_77
#print axioms cache_row_77
#print axioms wall_row_77
#print axioms pair_row_77
#print axioms source_piece_78
#print axioms gram_piece_78
#print axioms cache_row_78
#print axioms wall_row_78
#print axioms pair_row_78
#print axioms source_piece_79
#print axioms gram_piece_79
#print axioms cache_row_79
#print axioms wall_row_79
#print axioms pair_row_79
end PackingCertificates.Catalogue.CRcubincub_n100
