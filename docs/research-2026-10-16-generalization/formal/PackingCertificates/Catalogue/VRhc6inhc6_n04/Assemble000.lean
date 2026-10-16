import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_000
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_001
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_002
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_003
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_004
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_005
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_006
import PackingCertificates.Catalogue.VRhc6inhc6_n04.Vertex000_007

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.VRhc6inhc6_n04
open PackingCertificates.Rational

theorem vertices_piece_0 :
    allFin 64 (fun p => record.vertexCheck (0 : Fin 4) p) = true := by
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



#print axioms PackingCertificates.Catalogue.VRhc6inhc6_n04.vertices_piece_0
end PackingCertificates.Catalogue.VRhc6inhc6_n04
