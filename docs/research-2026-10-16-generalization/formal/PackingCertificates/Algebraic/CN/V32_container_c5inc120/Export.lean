import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Data
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0000
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0001
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0002
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0003
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0004
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0005
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0006
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0007
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0008
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0009
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0010
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0011
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0012
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0013
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0014
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0015
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0016
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0017
import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Vertices0018

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.Generated.ND.Records.FastCanonical
open PackingCertificates.Rational
open PackingCertificates.Algebraic.FragmentND
open PackingCertificates.Algebraic.TemplateFragments

theorem container_c5inc120_point_checked (j : Fin 600) :
    (allFin 4 (container_c5inc120.coordinateCheck j) && (antipodalItemCheck container_c5inc120 container_c5inc120_opposite 2 j && container_c5inc120_shapeCheck j)) = true := by
  by_cases h288 : j.val < 288
  · by_cases h128 : j.val < 128
    · by_cases h64 : j.val < 64
      · by_cases h32 : j.val < 32
        · exact rangeCheck_sound container_c5inc120_vertices_range_0 j (by omega) (by omega)
        · exact rangeCheck_sound container_c5inc120_vertices_range_1 j (by omega) (by omega)
      · by_cases h96 : j.val < 96
        · exact rangeCheck_sound container_c5inc120_vertices_range_2 j (by omega) (by omega)
        · exact rangeCheck_sound container_c5inc120_vertices_range_3 j (by omega) (by omega)
    · by_cases h192 : j.val < 192
      · by_cases h160 : j.val < 160
        · exact rangeCheck_sound container_c5inc120_vertices_range_4 j (by omega) (by omega)
        · exact rangeCheck_sound container_c5inc120_vertices_range_5 j (by omega) (by omega)
      · by_cases h224 : j.val < 224
        · exact rangeCheck_sound container_c5inc120_vertices_range_6 j (by omega) (by omega)
        · by_cases h256 : j.val < 256
          · exact rangeCheck_sound container_c5inc120_vertices_range_7 j (by omega) (by omega)
          · exact rangeCheck_sound container_c5inc120_vertices_range_8 j (by omega) (by omega)
  · by_cases h448 : j.val < 448
    · by_cases h352 : j.val < 352
      · by_cases h320 : j.val < 320
        · exact rangeCheck_sound container_c5inc120_vertices_range_9 j (by omega) (by omega)
        · exact rangeCheck_sound container_c5inc120_vertices_range_10 j (by omega) (by omega)
      · by_cases h384 : j.val < 384
        · exact rangeCheck_sound container_c5inc120_vertices_range_11 j (by omega) (by omega)
        · by_cases h416 : j.val < 416
          · exact rangeCheck_sound container_c5inc120_vertices_range_12 j (by omega) (by omega)
          · exact rangeCheck_sound container_c5inc120_vertices_range_13 j (by omega) (by omega)
    · by_cases h512 : j.val < 512
      · by_cases h480 : j.val < 480
        · exact rangeCheck_sound container_c5inc120_vertices_range_14 j (by omega) (by omega)
        · exact rangeCheck_sound container_c5inc120_vertices_range_15 j (by omega) (by omega)
      · by_cases h544 : j.val < 544
        · exact rangeCheck_sound container_c5inc120_vertices_range_16 j (by omega) (by omega)
        · by_cases h576 : j.val < 576
          · exact rangeCheck_sound container_c5inc120_vertices_range_17 j (by omega) (by omega)
          · exact rangeCheck_sound container_c5inc120_vertices_range_18 j (by omega) (by omega)

theorem container_c5inc120_vertices_checked : container_c5inc120.verticesCheck = true := by
  change allFin 600 (fun j => allFin 4 (container_c5inc120.coordinateCheck j)) = true
  apply allFin_eq_true.mpr
  intro j
  exact (Bool.and_eq_true_iff.mp (container_c5inc120_point_checked j)).1

theorem container_c5inc120_centroid_checked : container_c5inc120.centroidCheck 2 = true :=
  centroidCheck_of_antipodal container_c5inc120 container_c5inc120_opposite 2 (fun j =>
    (Bool.and_eq_true_iff.mp ((Bool.and_eq_true_iff.mp (container_c5inc120_point_checked j)).2)).1)

theorem container_c5inc120_row_sizes : allFin 600 container_c5inc120_shapeCheck = true :=
  allFin_eq_true.mpr (fun j => (Bool.and_eq_true_iff.mp ((Bool.and_eq_true_iff.mp (container_c5inc120_point_checked j)).2)).2)

#print axioms container_c5inc120_normalization_checked
#print axioms container_c5inc120_vertices_checked
#print axioms container_c5inc120_centroid_checked
#print axioms container_c5inc120_row_sizes
end PackingCertificates.Algebraic.Generated.ND.Records.FastCanonical
