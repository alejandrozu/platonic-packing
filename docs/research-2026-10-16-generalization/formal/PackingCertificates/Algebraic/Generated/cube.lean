import PackingCertificates.Algebraic.Generated.RootData

set_option maxRecDepth 0
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.Generated

def cube : TemplateData 3 8 where
  rootSpec := root0
  coefficients := ![![[((1 : ℚ) / 2)], [((1 : ℚ) / 2)], [((1 : ℚ) / 2)]], ![[((1 : ℚ) / 2)], [((1 : ℚ) / 2)], [((-1 : ℚ) / 2)]], ![[((1 : ℚ) / 2)], [((-1 : ℚ) / 2)], [((1 : ℚ) / 2)]], ![[((1 : ℚ) / 2)], [((-1 : ℚ) / 2)], [((-1 : ℚ) / 2)]], ![[((-1 : ℚ) / 2)], [((1 : ℚ) / 2)], [((1 : ℚ) / 2)]], ![[((-1 : ℚ) / 2)], [((1 : ℚ) / 2)], [((-1 : ℚ) / 2)]], ![[((-1 : ℚ) / 2)], [((-1 : ℚ) / 2)], [((1 : ℚ) / 2)]], ![[((-1 : ℚ) / 2)], [((-1 : ℚ) / 2)], [((-1 : ℚ) / 2)]]]
  normalizerPolynomial := none
  normalizerSqrtInterval := ⟨(1 : ℚ), (1 : ℚ)⟩
  vertexIntervals := ![![⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩], ![⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩], ![⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩], ![⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩], ![⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩], ![⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩], ![⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((1 : ℚ) / 2), ((1 : ℚ) / 2)⟩], ![⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩, ⟨((-1 : ℚ) / 2), ((-1 : ℚ) / 2)⟩]]

theorem cube_normalization_checked : cube.normalizationCheck = true := by decide +kernel
theorem cube_vertices_checked : cube.verticesCheck = true := by decide +kernel
theorem cube_centroid_checked : cube.centroidCheck 1 = true := by decide +kernel
theorem cube_centered : (∑ j, cube.vertex root0_checked j) = 0 :=
  cube.centroid_sound 1 root0_checked cube_centroid_checked

theorem cube_vertices_enclosed (j : Fin 8) (a : Fin 3) :
    (cube.vertexIntervals j a).Contains (cube.vertex root0_checked j a) :=
  cube.vertices_sound root0_checked cube_normalization_checked cube_vertices_checked j a

end PackingCertificates.Algebraic.Generated
