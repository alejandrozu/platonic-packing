import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_000
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_001
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_002
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_003
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_004
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_005
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_006
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex001_007

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.VRhc6inhc6_n04
open PackingCertificates.Rational

theorem vertices_piece_1 :
    allFin 64 (fun p => record.vertexCheck (1 : Fin 4) p) = true := by
  apply allFin_eq_true.mpr
  intro p
  fin_cases p
  · exact vertex_1_0
  · exact vertex_1_1
  · exact vertex_1_2
  · exact vertex_1_3
  · exact vertex_1_4
  · exact vertex_1_5
  · exact vertex_1_6
  · exact vertex_1_7
  · exact vertex_1_8
  · exact vertex_1_9
  · exact vertex_1_10
  · exact vertex_1_11
  · exact vertex_1_12
  · exact vertex_1_13
  · exact vertex_1_14
  · exact vertex_1_15
  · exact vertex_1_16
  · exact vertex_1_17
  · exact vertex_1_18
  · exact vertex_1_19
  · exact vertex_1_20
  · exact vertex_1_21
  · exact vertex_1_22
  · exact vertex_1_23
  · exact vertex_1_24
  · exact vertex_1_25
  · exact vertex_1_26
  · exact vertex_1_27
  · exact vertex_1_28
  · exact vertex_1_29
  · exact vertex_1_30
  · exact vertex_1_31
  · exact vertex_1_32
  · exact vertex_1_33
  · exact vertex_1_34
  · exact vertex_1_35
  · exact vertex_1_36
  · exact vertex_1_37
  · exact vertex_1_38
  · exact vertex_1_39
  · exact vertex_1_40
  · exact vertex_1_41
  · exact vertex_1_42
  · exact vertex_1_43
  · exact vertex_1_44
  · exact vertex_1_45
  · exact vertex_1_46
  · exact vertex_1_47
  · exact vertex_1_48
  · exact vertex_1_49
  · exact vertex_1_50
  · exact vertex_1_51
  · exact vertex_1_52
  · exact vertex_1_53
  · exact vertex_1_54
  · exact vertex_1_55
  · exact vertex_1_56
  · exact vertex_1_57
  · exact vertex_1_58
  · exact vertex_1_59
  · exact vertex_1_60
  · exact vertex_1_61
  · exact vertex_1_62
  · exact vertex_1_63



#print axioms PackingCertificates.Catalogue.VRhc6inhc6_n04.vertices_piece_1
end PackingCertificates.Catalogue.VRhc6inhc6_n04
