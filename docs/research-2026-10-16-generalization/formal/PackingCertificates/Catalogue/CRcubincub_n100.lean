import PackingCertificates.Catalogue.CRcubincub_n100.Block000
import PackingCertificates.Catalogue.CRcubincub_n100.Block001
import PackingCertificates.Catalogue.CRcubincub_n100.Block002
import PackingCertificates.Catalogue.CRcubincub_n100.Block003
import PackingCertificates.Catalogue.CRcubincub_n100.Block004
import PackingCertificates.Catalogue.CRcubincub_n100.Block005
import PackingCertificates.Catalogue.CRcubincub_n100.Block006
import PackingCertificates.Catalogue.CRcubincub_n100.Block007
import PackingCertificates.Catalogue.CRcubincub_n100.Block008
import PackingCertificates.Catalogue.CRcubincub_n100.Block009
import PackingCertificates.Catalogue.CRcubincub_n100.Block010
import PackingCertificates.Catalogue.CRcubincub_n100.Block011
import PackingCertificates.Catalogue.CRcubincub_n100.Block012
import PackingCertificates.Catalogue.CRcubincub_n100.Block013
import PackingCertificates.Catalogue.CRcubincub_n100.Block014
import PackingCertificates.Catalogue.CRcubincub_n100.Block015
import PackingCertificates.Catalogue.CRcubincub_n100.Block016
import PackingCertificates.Catalogue.CRcubincub_n100.Block017
import PackingCertificates.Catalogue.CRcubincub_n100.Block018
import PackingCertificates.Catalogue.CRcubincub_n100.Block019

-- Original source: records/cubincub/cubincub_n100.json
-- Original JSON SHA256: b10dc00f36891f1238bce3ffd1bec64635a0bd219deee3e70ec7f8ab6951fc19
-- Record identifier: cubincub_n100
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.CRcubincub_n100
open PackingCertificates.Rational
open PackingCertificates.CubeFast

theorem source_pieces_checked : allFin 100 (fun i => decide (0 < Cube.quaternionNormSq (record.quaternion i)) && decide (record.rotation i = Cube.quaternionMatrix (record.quaternion i)) && decide (Cube.determinant3 (record.rotation i) = 1)) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact source_piece_0
  · exact source_piece_1
  · exact source_piece_2
  · exact source_piece_3
  · exact source_piece_4
  · exact source_piece_5
  · exact source_piece_6
  · exact source_piece_7
  · exact source_piece_8
  · exact source_piece_9
  · exact source_piece_10
  · exact source_piece_11
  · exact source_piece_12
  · exact source_piece_13
  · exact source_piece_14
  · exact source_piece_15
  · exact source_piece_16
  · exact source_piece_17
  · exact source_piece_18
  · exact source_piece_19
  · exact source_piece_20
  · exact source_piece_21
  · exact source_piece_22
  · exact source_piece_23
  · exact source_piece_24
  · exact source_piece_25
  · exact source_piece_26
  · exact source_piece_27
  · exact source_piece_28
  · exact source_piece_29
  · exact source_piece_30
  · exact source_piece_31
  · exact source_piece_32
  · exact source_piece_33
  · exact source_piece_34
  · exact source_piece_35
  · exact source_piece_36
  · exact source_piece_37
  · exact source_piece_38
  · exact source_piece_39
  · exact source_piece_40
  · exact source_piece_41
  · exact source_piece_42
  · exact source_piece_43
  · exact source_piece_44
  · exact source_piece_45
  · exact source_piece_46
  · exact source_piece_47
  · exact source_piece_48
  · exact source_piece_49
  · exact source_piece_50
  · exact source_piece_51
  · exact source_piece_52
  · exact source_piece_53
  · exact source_piece_54
  · exact source_piece_55
  · exact source_piece_56
  · exact source_piece_57
  · exact source_piece_58
  · exact source_piece_59
  · exact source_piece_60
  · exact source_piece_61
  · exact source_piece_62
  · exact source_piece_63
  · exact source_piece_64
  · exact source_piece_65
  · exact source_piece_66
  · exact source_piece_67
  · exact source_piece_68
  · exact source_piece_69
  · exact source_piece_70
  · exact source_piece_71
  · exact source_piece_72
  · exact source_piece_73
  · exact source_piece_74
  · exact source_piece_75
  · exact source_piece_76
  · exact source_piece_77
  · exact source_piece_78
  · exact source_piece_79
  · exact source_piece_80
  · exact source_piece_81
  · exact source_piece_82
  · exact source_piece_83
  · exact source_piece_84
  · exact source_piece_85
  · exact source_piece_86
  · exact source_piece_87
  · exact source_piece_88
  · exact source_piece_89
  · exact source_piece_90
  · exact source_piece_91
  · exact source_piece_92
  · exact source_piece_93
  · exact source_piece_94
  · exact source_piece_95
  · exact source_piece_96
  · exact source_piece_97
  · exact source_piece_98
  · exact source_piece_99

theorem gram_pieces_checked : allFin 100 (fun i => allFin 3 (fun a => allFin 3 (fun b => decide (qdot (record.toPlacement.rotation i a) (record.toPlacement.rotation i b) = if a = b then 1 else 0)))) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact gram_piece_0
  · exact gram_piece_1
  · exact gram_piece_2
  · exact gram_piece_3
  · exact gram_piece_4
  · exact gram_piece_5
  · exact gram_piece_6
  · exact gram_piece_7
  · exact gram_piece_8
  · exact gram_piece_9
  · exact gram_piece_10
  · exact gram_piece_11
  · exact gram_piece_12
  · exact gram_piece_13
  · exact gram_piece_14
  · exact gram_piece_15
  · exact gram_piece_16
  · exact gram_piece_17
  · exact gram_piece_18
  · exact gram_piece_19
  · exact gram_piece_20
  · exact gram_piece_21
  · exact gram_piece_22
  · exact gram_piece_23
  · exact gram_piece_24
  · exact gram_piece_25
  · exact gram_piece_26
  · exact gram_piece_27
  · exact gram_piece_28
  · exact gram_piece_29
  · exact gram_piece_30
  · exact gram_piece_31
  · exact gram_piece_32
  · exact gram_piece_33
  · exact gram_piece_34
  · exact gram_piece_35
  · exact gram_piece_36
  · exact gram_piece_37
  · exact gram_piece_38
  · exact gram_piece_39
  · exact gram_piece_40
  · exact gram_piece_41
  · exact gram_piece_42
  · exact gram_piece_43
  · exact gram_piece_44
  · exact gram_piece_45
  · exact gram_piece_46
  · exact gram_piece_47
  · exact gram_piece_48
  · exact gram_piece_49
  · exact gram_piece_50
  · exact gram_piece_51
  · exact gram_piece_52
  · exact gram_piece_53
  · exact gram_piece_54
  · exact gram_piece_55
  · exact gram_piece_56
  · exact gram_piece_57
  · exact gram_piece_58
  · exact gram_piece_59
  · exact gram_piece_60
  · exact gram_piece_61
  · exact gram_piece_62
  · exact gram_piece_63
  · exact gram_piece_64
  · exact gram_piece_65
  · exact gram_piece_66
  · exact gram_piece_67
  · exact gram_piece_68
  · exact gram_piece_69
  · exact gram_piece_70
  · exact gram_piece_71
  · exact gram_piece_72
  · exact gram_piece_73
  · exact gram_piece_74
  · exact gram_piece_75
  · exact gram_piece_76
  · exact gram_piece_77
  · exact gram_piece_78
  · exact gram_piece_79
  · exact gram_piece_80
  · exact gram_piece_81
  · exact gram_piece_82
  · exact gram_piece_83
  · exact gram_piece_84
  · exact gram_piece_85
  · exact gram_piece_86
  · exact gram_piece_87
  · exact gram_piece_88
  · exact gram_piece_89
  · exact gram_piece_90
  · exact gram_piece_91
  · exact gram_piece_92
  · exact gram_piece_93
  · exact gram_piece_94
  · exact gram_piece_95
  · exact gram_piece_96
  · exact gram_piece_97
  · exact gram_piece_98
  · exact gram_piece_99

theorem cache_checked : allFin 100 (fun i => AxisFast.cacheRowCheck record cache i) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact cache_row_0
  · exact cache_row_1
  · exact cache_row_2
  · exact cache_row_3
  · exact cache_row_4
  · exact cache_row_5
  · exact cache_row_6
  · exact cache_row_7
  · exact cache_row_8
  · exact cache_row_9
  · exact cache_row_10
  · exact cache_row_11
  · exact cache_row_12
  · exact cache_row_13
  · exact cache_row_14
  · exact cache_row_15
  · exact cache_row_16
  · exact cache_row_17
  · exact cache_row_18
  · exact cache_row_19
  · exact cache_row_20
  · exact cache_row_21
  · exact cache_row_22
  · exact cache_row_23
  · exact cache_row_24
  · exact cache_row_25
  · exact cache_row_26
  · exact cache_row_27
  · exact cache_row_28
  · exact cache_row_29
  · exact cache_row_30
  · exact cache_row_31
  · exact cache_row_32
  · exact cache_row_33
  · exact cache_row_34
  · exact cache_row_35
  · exact cache_row_36
  · exact cache_row_37
  · exact cache_row_38
  · exact cache_row_39
  · exact cache_row_40
  · exact cache_row_41
  · exact cache_row_42
  · exact cache_row_43
  · exact cache_row_44
  · exact cache_row_45
  · exact cache_row_46
  · exact cache_row_47
  · exact cache_row_48
  · exact cache_row_49
  · exact cache_row_50
  · exact cache_row_51
  · exact cache_row_52
  · exact cache_row_53
  · exact cache_row_54
  · exact cache_row_55
  · exact cache_row_56
  · exact cache_row_57
  · exact cache_row_58
  · exact cache_row_59
  · exact cache_row_60
  · exact cache_row_61
  · exact cache_row_62
  · exact cache_row_63
  · exact cache_row_64
  · exact cache_row_65
  · exact cache_row_66
  · exact cache_row_67
  · exact cache_row_68
  · exact cache_row_69
  · exact cache_row_70
  · exact cache_row_71
  · exact cache_row_72
  · exact cache_row_73
  · exact cache_row_74
  · exact cache_row_75
  · exact cache_row_76
  · exact cache_row_77
  · exact cache_row_78
  · exact cache_row_79
  · exact cache_row_80
  · exact cache_row_81
  · exact cache_row_82
  · exact cache_row_83
  · exact cache_row_84
  · exact cache_row_85
  · exact cache_row_86
  · exact cache_row_87
  · exact cache_row_88
  · exact cache_row_89
  · exact cache_row_90
  · exact cache_row_91
  · exact cache_row_92
  · exact cache_row_93
  · exact cache_row_94
  · exact cache_row_95
  · exact cache_row_96
  · exact cache_row_97
  · exact cache_row_98
  · exact cache_row_99

theorem walls_checked : allFin 100 (fun i => CubeFast.wallRowCheck record i) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact wall_row_0
  · exact wall_row_1
  · exact wall_row_2
  · exact wall_row_3
  · exact wall_row_4
  · exact wall_row_5
  · exact wall_row_6
  · exact wall_row_7
  · exact wall_row_8
  · exact wall_row_9
  · exact wall_row_10
  · exact wall_row_11
  · exact wall_row_12
  · exact wall_row_13
  · exact wall_row_14
  · exact wall_row_15
  · exact wall_row_16
  · exact wall_row_17
  · exact wall_row_18
  · exact wall_row_19
  · exact wall_row_20
  · exact wall_row_21
  · exact wall_row_22
  · exact wall_row_23
  · exact wall_row_24
  · exact wall_row_25
  · exact wall_row_26
  · exact wall_row_27
  · exact wall_row_28
  · exact wall_row_29
  · exact wall_row_30
  · exact wall_row_31
  · exact wall_row_32
  · exact wall_row_33
  · exact wall_row_34
  · exact wall_row_35
  · exact wall_row_36
  · exact wall_row_37
  · exact wall_row_38
  · exact wall_row_39
  · exact wall_row_40
  · exact wall_row_41
  · exact wall_row_42
  · exact wall_row_43
  · exact wall_row_44
  · exact wall_row_45
  · exact wall_row_46
  · exact wall_row_47
  · exact wall_row_48
  · exact wall_row_49
  · exact wall_row_50
  · exact wall_row_51
  · exact wall_row_52
  · exact wall_row_53
  · exact wall_row_54
  · exact wall_row_55
  · exact wall_row_56
  · exact wall_row_57
  · exact wall_row_58
  · exact wall_row_59
  · exact wall_row_60
  · exact wall_row_61
  · exact wall_row_62
  · exact wall_row_63
  · exact wall_row_64
  · exact wall_row_65
  · exact wall_row_66
  · exact wall_row_67
  · exact wall_row_68
  · exact wall_row_69
  · exact wall_row_70
  · exact wall_row_71
  · exact wall_row_72
  · exact wall_row_73
  · exact wall_row_74
  · exact wall_row_75
  · exact wall_row_76
  · exact wall_row_77
  · exact wall_row_78
  · exact wall_row_79
  · exact wall_row_80
  · exact wall_row_81
  · exact wall_row_82
  · exact wall_row_83
  · exact wall_row_84
  · exact wall_row_85
  · exact wall_row_86
  · exact wall_row_87
  · exact wall_row_88
  · exact wall_row_89
  · exact wall_row_90
  · exact wall_row_91
  · exact wall_row_92
  · exact wall_row_93
  · exact wall_row_94
  · exact wall_row_95
  · exact wall_row_96
  · exact wall_row_97
  · exact wall_row_98
  · exact wall_row_99

theorem pairs_checked : allFin 100 (fun i => AxisFast.pairRowCheck record cache directions i) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
  · exact pair_row_0
  · exact pair_row_1
  · exact pair_row_2
  · exact pair_row_3
  · exact pair_row_4
  · exact pair_row_5
  · exact pair_row_6
  · exact pair_row_7
  · exact pair_row_8
  · exact pair_row_9
  · exact pair_row_10
  · exact pair_row_11
  · exact pair_row_12
  · exact pair_row_13
  · exact pair_row_14
  · exact pair_row_15
  · exact pair_row_16
  · exact pair_row_17
  · exact pair_row_18
  · exact pair_row_19
  · exact pair_row_20
  · exact pair_row_21
  · exact pair_row_22
  · exact pair_row_23
  · exact pair_row_24
  · exact pair_row_25
  · exact pair_row_26
  · exact pair_row_27
  · exact pair_row_28
  · exact pair_row_29
  · exact pair_row_30
  · exact pair_row_31
  · exact pair_row_32
  · exact pair_row_33
  · exact pair_row_34
  · exact pair_row_35
  · exact pair_row_36
  · exact pair_row_37
  · exact pair_row_38
  · exact pair_row_39
  · exact pair_row_40
  · exact pair_row_41
  · exact pair_row_42
  · exact pair_row_43
  · exact pair_row_44
  · exact pair_row_45
  · exact pair_row_46
  · exact pair_row_47
  · exact pair_row_48
  · exact pair_row_49
  · exact pair_row_50
  · exact pair_row_51
  · exact pair_row_52
  · exact pair_row_53
  · exact pair_row_54
  · exact pair_row_55
  · exact pair_row_56
  · exact pair_row_57
  · exact pair_row_58
  · exact pair_row_59
  · exact pair_row_60
  · exact pair_row_61
  · exact pair_row_62
  · exact pair_row_63
  · exact pair_row_64
  · exact pair_row_65
  · exact pair_row_66
  · exact pair_row_67
  · exact pair_row_68
  · exact pair_row_69
  · exact pair_row_70
  · exact pair_row_71
  · exact pair_row_72
  · exact pair_row_73
  · exact pair_row_74
  · exact pair_row_75
  · exact pair_row_76
  · exact pair_row_77
  · exact pair_row_78
  · exact pair_row_79
  · exact pair_row_80
  · exact pair_row_81
  · exact pair_row_82
  · exact pair_row_83
  · exact pair_row_84
  · exact pair_row_85
  · exact pair_row_86
  · exact pair_row_87
  · exact pair_row_88
  · exact pair_row_89
  · exact pair_row_90
  · exact pair_row_91
  · exact pair_row_92
  · exact pair_row_93
  · exact pair_row_94
  · exact pair_row_95
  · exact pair_row_96
  · exact pair_row_97
  · exact pair_row_98
  · exact pair_row_99

theorem scale_checked : decide (0 < record.scale) = true := by decide +kernel

theorem source_checked : record.sourceCheck = true := by
  simp only [CubeRecord.sourceCheck, Bool.and_eq_true]
  exact ⟨scale_checked, source_pieces_checked⟩

theorem gram_checked : orthogonalCheck record.toPlacement = true := gram_pieces_checked

theorem axis_checked : AxisFast.check record cache directions = true :=
  AxisFast.check_of_rows record cache directions source_checked gram_checked
    (allFin_eq_true.mp cache_checked)
    (allFin_eq_true.mp walls_checked) (allFin_eq_true.mp pairs_checked)

theorem checked : record.check = true :=
  CubeFast.fastCheck_implies_check record
    (AxisFast.check_implies_fastCheck record cache directions axis_checked)

/-- Complete actual catalogue packing, assembled from separately compiled
kernel-checked arithmetic blocks. No numerical test is silently omitted. -/
theorem packing : record.Valid := AxisFast.check_sound record cache directions axis_checked

#print axioms source_checked
#print axioms axis_checked
#print axioms checked
#print axioms packing
end PackingCertificates.Catalogue.CRcubincub_n100
