import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_000
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_001
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_002
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_003
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_004
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_005
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_006
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex003_007

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.VRhc6inhc6_n04
open PackingCertificates.Rational

theorem vertices_piece_3 :
    allFin 64 (fun p => record.vertexCheck (3 : Fin 4) p) = true := by
  apply allFin_eq_true.mpr
  intro p
  fin_cases p
  · exact vertex_3_0
  · exact vertex_3_1
  · exact vertex_3_2
  · exact vertex_3_3
  · exact vertex_3_4
  · exact vertex_3_5
  · exact vertex_3_6
  · exact vertex_3_7
  · exact vertex_3_8
  · exact vertex_3_9
  · exact vertex_3_10
  · exact vertex_3_11
  · exact vertex_3_12
  · exact vertex_3_13
  · exact vertex_3_14
  · exact vertex_3_15
  · exact vertex_3_16
  · exact vertex_3_17
  · exact vertex_3_18
  · exact vertex_3_19
  · exact vertex_3_20
  · exact vertex_3_21
  · exact vertex_3_22
  · exact vertex_3_23
  · exact vertex_3_24
  · exact vertex_3_25
  · exact vertex_3_26
  · exact vertex_3_27
  · exact vertex_3_28
  · exact vertex_3_29
  · exact vertex_3_30
  · exact vertex_3_31
  · exact vertex_3_32
  · exact vertex_3_33
  · exact vertex_3_34
  · exact vertex_3_35
  · exact vertex_3_36
  · exact vertex_3_37
  · exact vertex_3_38
  · exact vertex_3_39
  · exact vertex_3_40
  · exact vertex_3_41
  · exact vertex_3_42
  · exact vertex_3_43
  · exact vertex_3_44
  · exact vertex_3_45
  · exact vertex_3_46
  · exact vertex_3_47
  · exact vertex_3_48
  · exact vertex_3_49
  · exact vertex_3_50
  · exact vertex_3_51
  · exact vertex_3_52
  · exact vertex_3_53
  · exact vertex_3_54
  · exact vertex_3_55
  · exact vertex_3_56
  · exact vertex_3_57
  · exact vertex_3_58
  · exact vertex_3_59
  · exact vertex_3_60
  · exact vertex_3_61
  · exact vertex_3_62
  · exact vertex_3_63



#print axioms PackingCertificates.Catalogue.VRhc6inhc6_n04.vertices_piece_3
end PackingCertificates.Catalogue.VRhc6inhc6_n04
