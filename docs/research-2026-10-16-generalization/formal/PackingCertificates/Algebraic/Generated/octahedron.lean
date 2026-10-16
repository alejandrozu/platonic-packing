import PackingCertificates.Algebraic.Generated.RootData

set_option maxRecDepth 0
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.Generated

def octahedron : TemplateData 3 6 where
  rootSpec := root1
  coefficients := ![![[(0 : ℚ), ((1 : ℚ) / 2)], [(0 : ℚ), (0 : ℚ)], [(0 : ℚ), (0 : ℚ)]], ![[(0 : ℚ), ((-1 : ℚ) / 2)], [(0 : ℚ), (0 : ℚ)], [(0 : ℚ), (0 : ℚ)]], ![[(0 : ℚ), (0 : ℚ)], [(0 : ℚ), ((1 : ℚ) / 2)], [(0 : ℚ), (0 : ℚ)]], ![[(0 : ℚ), (0 : ℚ)], [(0 : ℚ), ((-1 : ℚ) / 2)], [(0 : ℚ), (0 : ℚ)]], ![[(0 : ℚ), (0 : ℚ)], [(0 : ℚ), (0 : ℚ)], [(0 : ℚ), ((1 : ℚ) / 2)]], ![[(0 : ℚ), (0 : ℚ)], [(0 : ℚ), (0 : ℚ)], [(0 : ℚ), ((-1 : ℚ) / 2)]]]
  normalizerPolynomial := none
  normalizerSqrtInterval := ⟨(1 : ℚ), (1 : ℚ)⟩
  vertexIntervals := ![![⟨((132280027964406234453295933952790241335479250746291 : ℚ) / 187072209578355573530071658587684226515959365500928), ((529120111857624937813183735811909254180230425279285 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩], ![⟨((-529120111857624937813183735811909254180230425279285 : ℚ) / 748288838313422294120286634350736906063837462003712), ((-132280027964406234453295933952790241335479250746291 : ℚ) / 187072209578355573530071658587684226515959365500928)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩], ![⟨(0 : ℚ), (0 : ℚ)⟩, ⟨((132280027964406234453295933952790241335479250746291 : ℚ) / 187072209578355573530071658587684226515959365500928), ((529120111857624937813183735811909254180230425279285 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩], ![⟨(0 : ℚ), (0 : ℚ)⟩, ⟨((-529120111857624937813183735811909254180230425279285 : ℚ) / 748288838313422294120286634350736906063837462003712), ((-132280027964406234453295933952790241335479250746291 : ℚ) / 187072209578355573530071658587684226515959365500928)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩], ![⟨(0 : ℚ), (0 : ℚ)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩, ⟨((132280027964406234453295933952790241335479250746291 : ℚ) / 187072209578355573530071658587684226515959365500928), ((529120111857624937813183735811909254180230425279285 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩], ![⟨(0 : ℚ), (0 : ℚ)⟩, ⟨(0 : ℚ), (0 : ℚ)⟩, ⟨((-529120111857624937813183735811909254180230425279285 : ℚ) / 748288838313422294120286634350736906063837462003712), ((-132280027964406234453295933952790241335479250746291 : ℚ) / 187072209578355573530071658587684226515959365500928)⟩]]

theorem octahedron_normalization_checked : octahedron.normalizationCheck = true := by decide +kernel
theorem octahedron_vertices_checked : octahedron.verticesCheck = true := by decide +kernel
theorem octahedron_centroid_checked : octahedron.centroidCheck 2 = true := by decide +kernel
theorem octahedron_centered : (∑ j, octahedron.vertex root1_checked j) = 0 :=
  octahedron.centroid_sound 2 root1_checked octahedron_centroid_checked

theorem octahedron_vertices_enclosed (j : Fin 6) (a : Fin 3) :
    (octahedron.vertexIntervals j a).Contains (octahedron.vertex root1_checked j a) :=
  octahedron.vertices_sound root1_checked octahedron_normalization_checked octahedron_vertices_checked j a

end PackingCertificates.Algebraic.Generated
