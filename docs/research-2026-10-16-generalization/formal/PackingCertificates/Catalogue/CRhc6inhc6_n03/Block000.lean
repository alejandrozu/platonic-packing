import PackingCertificates.Catalogue.CRhc6inhc6_n03.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRhc6inhc6_n03
open PackingCertificates.Rational

theorem source_piece_0 : Cayley.check (source (0 : Fin 3)) = true := by decide +kernel

theorem gram_piece_0 :
    allFin 6 (fun a => allFin 6 (fun b =>
      decide (qdot (record.placement.rotation (0 : Fin 3) a)
        (record.placement.rotation (0 : Fin 3) b) = if a = b then 1 else 0))) = true := by decide +kernel


theorem pair_row_0 :
    allFin 3 (fun j => if (0 : Fin 3) < j then
      planeCheck (record.placement.toCertificate.vertices (0 : Fin 3))
        (record.placement.toCertificate.vertices j)
        (record.placement.separation (0 : Fin 3) j) else true) = true := by decide +kernel

theorem vertex_0_0 :
    record.vertexCheck (0 : Fin 3) (0 : Fin 64) = true := by decide +kernel

theorem vertex_0_1 :
    record.vertexCheck (0 : Fin 3) (1 : Fin 64) = true := by decide +kernel

theorem vertex_0_2 :
    record.vertexCheck (0 : Fin 3) (2 : Fin 64) = true := by decide +kernel

theorem vertex_0_3 :
    record.vertexCheck (0 : Fin 3) (3 : Fin 64) = true := by decide +kernel

theorem vertex_0_4 :
    record.vertexCheck (0 : Fin 3) (4 : Fin 64) = true := by decide +kernel

theorem vertex_0_5 :
    record.vertexCheck (0 : Fin 3) (5 : Fin 64) = true := by decide +kernel

theorem vertex_0_6 :
    record.vertexCheck (0 : Fin 3) (6 : Fin 64) = true := by decide +kernel

theorem vertex_0_7 :
    record.vertexCheck (0 : Fin 3) (7 : Fin 64) = true := by decide +kernel

theorem vertex_0_8 :
    record.vertexCheck (0 : Fin 3) (8 : Fin 64) = true := by decide +kernel

theorem vertex_0_9 :
    record.vertexCheck (0 : Fin 3) (9 : Fin 64) = true := by decide +kernel

theorem vertex_0_10 :
    record.vertexCheck (0 : Fin 3) (10 : Fin 64) = true := by decide +kernel

theorem vertex_0_11 :
    record.vertexCheck (0 : Fin 3) (11 : Fin 64) = true := by decide +kernel

theorem vertex_0_12 :
    record.vertexCheck (0 : Fin 3) (12 : Fin 64) = true := by decide +kernel

theorem vertex_0_13 :
    record.vertexCheck (0 : Fin 3) (13 : Fin 64) = true := by decide +kernel

theorem vertex_0_14 :
    record.vertexCheck (0 : Fin 3) (14 : Fin 64) = true := by decide +kernel

theorem vertex_0_15 :
    record.vertexCheck (0 : Fin 3) (15 : Fin 64) = true := by decide +kernel

theorem vertex_0_16 :
    record.vertexCheck (0 : Fin 3) (16 : Fin 64) = true := by decide +kernel

theorem vertex_0_17 :
    record.vertexCheck (0 : Fin 3) (17 : Fin 64) = true := by decide +kernel

theorem vertex_0_18 :
    record.vertexCheck (0 : Fin 3) (18 : Fin 64) = true := by decide +kernel

theorem vertex_0_19 :
    record.vertexCheck (0 : Fin 3) (19 : Fin 64) = true := by decide +kernel

theorem vertex_0_20 :
    record.vertexCheck (0 : Fin 3) (20 : Fin 64) = true := by decide +kernel

theorem vertex_0_21 :
    record.vertexCheck (0 : Fin 3) (21 : Fin 64) = true := by decide +kernel

theorem vertex_0_22 :
    record.vertexCheck (0 : Fin 3) (22 : Fin 64) = true := by decide +kernel

theorem vertex_0_23 :
    record.vertexCheck (0 : Fin 3) (23 : Fin 64) = true := by decide +kernel

theorem vertex_0_24 :
    record.vertexCheck (0 : Fin 3) (24 : Fin 64) = true := by decide +kernel

theorem vertex_0_25 :
    record.vertexCheck (0 : Fin 3) (25 : Fin 64) = true := by decide +kernel

theorem vertex_0_26 :
    record.vertexCheck (0 : Fin 3) (26 : Fin 64) = true := by decide +kernel

theorem vertex_0_27 :
    record.vertexCheck (0 : Fin 3) (27 : Fin 64) = true := by decide +kernel

theorem vertex_0_28 :
    record.vertexCheck (0 : Fin 3) (28 : Fin 64) = true := by decide +kernel

theorem vertex_0_29 :
    record.vertexCheck (0 : Fin 3) (29 : Fin 64) = true := by decide +kernel

theorem vertex_0_30 :
    record.vertexCheck (0 : Fin 3) (30 : Fin 64) = true := by decide +kernel

theorem vertex_0_31 :
    record.vertexCheck (0 : Fin 3) (31 : Fin 64) = true := by decide +kernel

theorem vertex_0_32 :
    record.vertexCheck (0 : Fin 3) (32 : Fin 64) = true := by decide +kernel

theorem vertex_0_33 :
    record.vertexCheck (0 : Fin 3) (33 : Fin 64) = true := by decide +kernel

theorem vertex_0_34 :
    record.vertexCheck (0 : Fin 3) (34 : Fin 64) = true := by decide +kernel

theorem vertex_0_35 :
    record.vertexCheck (0 : Fin 3) (35 : Fin 64) = true := by decide +kernel

theorem vertex_0_36 :
    record.vertexCheck (0 : Fin 3) (36 : Fin 64) = true := by decide +kernel

theorem vertex_0_37 :
    record.vertexCheck (0 : Fin 3) (37 : Fin 64) = true := by decide +kernel

theorem vertex_0_38 :
    record.vertexCheck (0 : Fin 3) (38 : Fin 64) = true := by decide +kernel

theorem vertex_0_39 :
    record.vertexCheck (0 : Fin 3) (39 : Fin 64) = true := by decide +kernel

theorem vertex_0_40 :
    record.vertexCheck (0 : Fin 3) (40 : Fin 64) = true := by decide +kernel

theorem vertex_0_41 :
    record.vertexCheck (0 : Fin 3) (41 : Fin 64) = true := by decide +kernel

theorem vertex_0_42 :
    record.vertexCheck (0 : Fin 3) (42 : Fin 64) = true := by decide +kernel

theorem vertex_0_43 :
    record.vertexCheck (0 : Fin 3) (43 : Fin 64) = true := by decide +kernel

theorem vertex_0_44 :
    record.vertexCheck (0 : Fin 3) (44 : Fin 64) = true := by decide +kernel

theorem vertex_0_45 :
    record.vertexCheck (0 : Fin 3) (45 : Fin 64) = true := by decide +kernel

theorem vertex_0_46 :
    record.vertexCheck (0 : Fin 3) (46 : Fin 64) = true := by decide +kernel

theorem vertex_0_47 :
    record.vertexCheck (0 : Fin 3) (47 : Fin 64) = true := by decide +kernel

theorem vertex_0_48 :
    record.vertexCheck (0 : Fin 3) (48 : Fin 64) = true := by decide +kernel

theorem vertex_0_49 :
    record.vertexCheck (0 : Fin 3) (49 : Fin 64) = true := by decide +kernel

theorem vertex_0_50 :
    record.vertexCheck (0 : Fin 3) (50 : Fin 64) = true := by decide +kernel

theorem vertex_0_51 :
    record.vertexCheck (0 : Fin 3) (51 : Fin 64) = true := by decide +kernel

theorem vertex_0_52 :
    record.vertexCheck (0 : Fin 3) (52 : Fin 64) = true := by decide +kernel

theorem vertex_0_53 :
    record.vertexCheck (0 : Fin 3) (53 : Fin 64) = true := by decide +kernel

theorem vertex_0_54 :
    record.vertexCheck (0 : Fin 3) (54 : Fin 64) = true := by decide +kernel

theorem vertex_0_55 :
    record.vertexCheck (0 : Fin 3) (55 : Fin 64) = true := by decide +kernel

theorem vertex_0_56 :
    record.vertexCheck (0 : Fin 3) (56 : Fin 64) = true := by decide +kernel

theorem vertex_0_57 :
    record.vertexCheck (0 : Fin 3) (57 : Fin 64) = true := by decide +kernel

theorem vertex_0_58 :
    record.vertexCheck (0 : Fin 3) (58 : Fin 64) = true := by decide +kernel

theorem vertex_0_59 :
    record.vertexCheck (0 : Fin 3) (59 : Fin 64) = true := by decide +kernel

theorem vertex_0_60 :
    record.vertexCheck (0 : Fin 3) (60 : Fin 64) = true := by decide +kernel

theorem vertex_0_61 :
    record.vertexCheck (0 : Fin 3) (61 : Fin 64) = true := by decide +kernel

theorem vertex_0_62 :
    record.vertexCheck (0 : Fin 3) (62 : Fin 64) = true := by decide +kernel

theorem vertex_0_63 :
    record.vertexCheck (0 : Fin 3) (63 : Fin 64) = true := by decide +kernel

theorem vertices_piece_0 :
    allFin 64 (fun p => record.vertexCheck (0 : Fin 3) p) = true := by
  apply allFin_eq_true.mpr
  intro p
  fin_cases p
  · exact vertex_0_0
  · exact vertex_0_1
  · exact vertex_0_2
  · exact vertex_0_3
  · exact vertex_0_4
  · exact vertex_0_5
  · exact vertex_0_6
  · exact vertex_0_7
  · exact vertex_0_8
  · exact vertex_0_9
  · exact vertex_0_10
  · exact vertex_0_11
  · exact vertex_0_12
  · exact vertex_0_13
  · exact vertex_0_14
  · exact vertex_0_15
  · exact vertex_0_16
  · exact vertex_0_17
  · exact vertex_0_18
  · exact vertex_0_19
  · exact vertex_0_20
  · exact vertex_0_21
  · exact vertex_0_22
  · exact vertex_0_23
  · exact vertex_0_24
  · exact vertex_0_25
  · exact vertex_0_26
  · exact vertex_0_27
  · exact vertex_0_28
  · exact vertex_0_29
  · exact vertex_0_30
  · exact vertex_0_31
  · exact vertex_0_32
  · exact vertex_0_33
  · exact vertex_0_34
  · exact vertex_0_35
  · exact vertex_0_36
  · exact vertex_0_37
  · exact vertex_0_38
  · exact vertex_0_39
  · exact vertex_0_40
  · exact vertex_0_41
  · exact vertex_0_42
  · exact vertex_0_43
  · exact vertex_0_44
  · exact vertex_0_45
  · exact vertex_0_46
  · exact vertex_0_47
  · exact vertex_0_48
  · exact vertex_0_49
  · exact vertex_0_50
  · exact vertex_0_51
  · exact vertex_0_52
  · exact vertex_0_53
  · exact vertex_0_54
  · exact vertex_0_55
  · exact vertex_0_56
  · exact vertex_0_57
  · exact vertex_0_58
  · exact vertex_0_59
  · exact vertex_0_60
  · exact vertex_0_61
  · exact vertex_0_62
  · exact vertex_0_63


#print axioms source_piece_0
#print axioms gram_piece_0
#print axioms pair_row_0
#print axioms vertices_piece_0
end PackingCertificates.Catalogue.CRhc6inhc6_n03
