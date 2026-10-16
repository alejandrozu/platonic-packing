import PackingCertificates.Catalogue.CRhc6inhc6_n03.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRhc6inhc6_n03
open PackingCertificates.Rational

theorem source_piece_2 : Cayley.check (source (2 : Fin 3)) = true := by decide +kernel

theorem gram_piece_2 :
    allFin 6 (fun a => allFin 6 (fun b =>
      decide (qdot (record.placement.rotation (2 : Fin 3) a)
        (record.placement.rotation (2 : Fin 3) b) = if a = b then 1 else 0))) = true := by decide +kernel


theorem pair_row_2 :
    allFin 3 (fun j => if (2 : Fin 3) < j then
      planeCheck (record.placement.toCertificate.vertices (2 : Fin 3))
        (record.placement.toCertificate.vertices j)
        (record.placement.separation (2 : Fin 3) j) else true) = true := by decide +kernel

theorem vertex_2_0 :
    record.vertexCheck (2 : Fin 3) (0 : Fin 64) = true := by decide +kernel

theorem vertex_2_1 :
    record.vertexCheck (2 : Fin 3) (1 : Fin 64) = true := by decide +kernel

theorem vertex_2_2 :
    record.vertexCheck (2 : Fin 3) (2 : Fin 64) = true := by decide +kernel

theorem vertex_2_3 :
    record.vertexCheck (2 : Fin 3) (3 : Fin 64) = true := by decide +kernel

theorem vertex_2_4 :
    record.vertexCheck (2 : Fin 3) (4 : Fin 64) = true := by decide +kernel

theorem vertex_2_5 :
    record.vertexCheck (2 : Fin 3) (5 : Fin 64) = true := by decide +kernel

theorem vertex_2_6 :
    record.vertexCheck (2 : Fin 3) (6 : Fin 64) = true := by decide +kernel

theorem vertex_2_7 :
    record.vertexCheck (2 : Fin 3) (7 : Fin 64) = true := by decide +kernel

theorem vertex_2_8 :
    record.vertexCheck (2 : Fin 3) (8 : Fin 64) = true := by decide +kernel

theorem vertex_2_9 :
    record.vertexCheck (2 : Fin 3) (9 : Fin 64) = true := by decide +kernel

theorem vertex_2_10 :
    record.vertexCheck (2 : Fin 3) (10 : Fin 64) = true := by decide +kernel

theorem vertex_2_11 :
    record.vertexCheck (2 : Fin 3) (11 : Fin 64) = true := by decide +kernel

theorem vertex_2_12 :
    record.vertexCheck (2 : Fin 3) (12 : Fin 64) = true := by decide +kernel

theorem vertex_2_13 :
    record.vertexCheck (2 : Fin 3) (13 : Fin 64) = true := by decide +kernel

theorem vertex_2_14 :
    record.vertexCheck (2 : Fin 3) (14 : Fin 64) = true := by decide +kernel

theorem vertex_2_15 :
    record.vertexCheck (2 : Fin 3) (15 : Fin 64) = true := by decide +kernel

theorem vertex_2_16 :
    record.vertexCheck (2 : Fin 3) (16 : Fin 64) = true := by decide +kernel

theorem vertex_2_17 :
    record.vertexCheck (2 : Fin 3) (17 : Fin 64) = true := by decide +kernel

theorem vertex_2_18 :
    record.vertexCheck (2 : Fin 3) (18 : Fin 64) = true := by decide +kernel

theorem vertex_2_19 :
    record.vertexCheck (2 : Fin 3) (19 : Fin 64) = true := by decide +kernel

theorem vertex_2_20 :
    record.vertexCheck (2 : Fin 3) (20 : Fin 64) = true := by decide +kernel

theorem vertex_2_21 :
    record.vertexCheck (2 : Fin 3) (21 : Fin 64) = true := by decide +kernel

theorem vertex_2_22 :
    record.vertexCheck (2 : Fin 3) (22 : Fin 64) = true := by decide +kernel

theorem vertex_2_23 :
    record.vertexCheck (2 : Fin 3) (23 : Fin 64) = true := by decide +kernel

theorem vertex_2_24 :
    record.vertexCheck (2 : Fin 3) (24 : Fin 64) = true := by decide +kernel

theorem vertex_2_25 :
    record.vertexCheck (2 : Fin 3) (25 : Fin 64) = true := by decide +kernel

theorem vertex_2_26 :
    record.vertexCheck (2 : Fin 3) (26 : Fin 64) = true := by decide +kernel

theorem vertex_2_27 :
    record.vertexCheck (2 : Fin 3) (27 : Fin 64) = true := by decide +kernel

theorem vertex_2_28 :
    record.vertexCheck (2 : Fin 3) (28 : Fin 64) = true := by decide +kernel

theorem vertex_2_29 :
    record.vertexCheck (2 : Fin 3) (29 : Fin 64) = true := by decide +kernel

theorem vertex_2_30 :
    record.vertexCheck (2 : Fin 3) (30 : Fin 64) = true := by decide +kernel

theorem vertex_2_31 :
    record.vertexCheck (2 : Fin 3) (31 : Fin 64) = true := by decide +kernel

theorem vertex_2_32 :
    record.vertexCheck (2 : Fin 3) (32 : Fin 64) = true := by decide +kernel

theorem vertex_2_33 :
    record.vertexCheck (2 : Fin 3) (33 : Fin 64) = true := by decide +kernel

theorem vertex_2_34 :
    record.vertexCheck (2 : Fin 3) (34 : Fin 64) = true := by decide +kernel

theorem vertex_2_35 :
    record.vertexCheck (2 : Fin 3) (35 : Fin 64) = true := by decide +kernel

theorem vertex_2_36 :
    record.vertexCheck (2 : Fin 3) (36 : Fin 64) = true := by decide +kernel

theorem vertex_2_37 :
    record.vertexCheck (2 : Fin 3) (37 : Fin 64) = true := by decide +kernel

theorem vertex_2_38 :
    record.vertexCheck (2 : Fin 3) (38 : Fin 64) = true := by decide +kernel

theorem vertex_2_39 :
    record.vertexCheck (2 : Fin 3) (39 : Fin 64) = true := by decide +kernel

theorem vertex_2_40 :
    record.vertexCheck (2 : Fin 3) (40 : Fin 64) = true := by decide +kernel

theorem vertex_2_41 :
    record.vertexCheck (2 : Fin 3) (41 : Fin 64) = true := by decide +kernel

theorem vertex_2_42 :
    record.vertexCheck (2 : Fin 3) (42 : Fin 64) = true := by decide +kernel

theorem vertex_2_43 :
    record.vertexCheck (2 : Fin 3) (43 : Fin 64) = true := by decide +kernel

theorem vertex_2_44 :
    record.vertexCheck (2 : Fin 3) (44 : Fin 64) = true := by decide +kernel

theorem vertex_2_45 :
    record.vertexCheck (2 : Fin 3) (45 : Fin 64) = true := by decide +kernel

theorem vertex_2_46 :
    record.vertexCheck (2 : Fin 3) (46 : Fin 64) = true := by decide +kernel

theorem vertex_2_47 :
    record.vertexCheck (2 : Fin 3) (47 : Fin 64) = true := by decide +kernel

theorem vertex_2_48 :
    record.vertexCheck (2 : Fin 3) (48 : Fin 64) = true := by decide +kernel

theorem vertex_2_49 :
    record.vertexCheck (2 : Fin 3) (49 : Fin 64) = true := by decide +kernel

theorem vertex_2_50 :
    record.vertexCheck (2 : Fin 3) (50 : Fin 64) = true := by decide +kernel

theorem vertex_2_51 :
    record.vertexCheck (2 : Fin 3) (51 : Fin 64) = true := by decide +kernel

theorem vertex_2_52 :
    record.vertexCheck (2 : Fin 3) (52 : Fin 64) = true := by decide +kernel

theorem vertex_2_53 :
    record.vertexCheck (2 : Fin 3) (53 : Fin 64) = true := by decide +kernel

theorem vertex_2_54 :
    record.vertexCheck (2 : Fin 3) (54 : Fin 64) = true := by decide +kernel

theorem vertex_2_55 :
    record.vertexCheck (2 : Fin 3) (55 : Fin 64) = true := by decide +kernel

theorem vertex_2_56 :
    record.vertexCheck (2 : Fin 3) (56 : Fin 64) = true := by decide +kernel

theorem vertex_2_57 :
    record.vertexCheck (2 : Fin 3) (57 : Fin 64) = true := by decide +kernel

theorem vertex_2_58 :
    record.vertexCheck (2 : Fin 3) (58 : Fin 64) = true := by decide +kernel

theorem vertex_2_59 :
    record.vertexCheck (2 : Fin 3) (59 : Fin 64) = true := by decide +kernel

theorem vertex_2_60 :
    record.vertexCheck (2 : Fin 3) (60 : Fin 64) = true := by decide +kernel

theorem vertex_2_61 :
    record.vertexCheck (2 : Fin 3) (61 : Fin 64) = true := by decide +kernel

theorem vertex_2_62 :
    record.vertexCheck (2 : Fin 3) (62 : Fin 64) = true := by decide +kernel

theorem vertex_2_63 :
    record.vertexCheck (2 : Fin 3) (63 : Fin 64) = true := by decide +kernel

theorem vertices_piece_2 :
    allFin 64 (fun p => record.vertexCheck (2 : Fin 3) p) = true := by
  apply allFin_eq_true.mpr
  intro p
  fin_cases p
  · exact vertex_2_0
  · exact vertex_2_1
  · exact vertex_2_2
  · exact vertex_2_3
  · exact vertex_2_4
  · exact vertex_2_5
  · exact vertex_2_6
  · exact vertex_2_7
  · exact vertex_2_8
  · exact vertex_2_9
  · exact vertex_2_10
  · exact vertex_2_11
  · exact vertex_2_12
  · exact vertex_2_13
  · exact vertex_2_14
  · exact vertex_2_15
  · exact vertex_2_16
  · exact vertex_2_17
  · exact vertex_2_18
  · exact vertex_2_19
  · exact vertex_2_20
  · exact vertex_2_21
  · exact vertex_2_22
  · exact vertex_2_23
  · exact vertex_2_24
  · exact vertex_2_25
  · exact vertex_2_26
  · exact vertex_2_27
  · exact vertex_2_28
  · exact vertex_2_29
  · exact vertex_2_30
  · exact vertex_2_31
  · exact vertex_2_32
  · exact vertex_2_33
  · exact vertex_2_34
  · exact vertex_2_35
  · exact vertex_2_36
  · exact vertex_2_37
  · exact vertex_2_38
  · exact vertex_2_39
  · exact vertex_2_40
  · exact vertex_2_41
  · exact vertex_2_42
  · exact vertex_2_43
  · exact vertex_2_44
  · exact vertex_2_45
  · exact vertex_2_46
  · exact vertex_2_47
  · exact vertex_2_48
  · exact vertex_2_49
  · exact vertex_2_50
  · exact vertex_2_51
  · exact vertex_2_52
  · exact vertex_2_53
  · exact vertex_2_54
  · exact vertex_2_55
  · exact vertex_2_56
  · exact vertex_2_57
  · exact vertex_2_58
  · exact vertex_2_59
  · exact vertex_2_60
  · exact vertex_2_61
  · exact vertex_2_62
  · exact vertex_2_63


#print axioms source_piece_2
#print axioms gram_piece_2
#print axioms pair_row_2
#print axioms vertices_piece_2
end PackingCertificates.Catalogue.CRhc6inhc6_n03
