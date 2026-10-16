import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_000
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_001
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_002
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_003
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_004
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_005
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_006
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex002_007

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.VRhc6inhc6_n04
open PackingCertificates.Rational

theorem vertices_piece_2 :
    allFin 64 (fun p => record.vertexCheck (2 : Fin 4) p) = true := by
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



#print axioms PackingCertificates.Catalogue.VRhc6inhc6_n04.vertices_piece_2
end PackingCertificates.Catalogue.VRhc6inhc6_n04
