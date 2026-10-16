import PackingCertificates.Algebraic.CN.V32_container_c5inc120.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.Generated.ND.Records.FastCanonical
open PackingCertificates.Rational
open PackingCertificates.Algebraic.FragmentND
open PackingCertificates.Algebraic.TemplateFragments

theorem container_c5inc120_vertices_range_13 : rangeCheck 416 32 (by decide)
    (fun j => allFin 4 (container_c5inc120.coordinateCheck j) &&
      (antipodalItemCheck container_c5inc120 container_c5inc120_opposite 2 j && container_c5inc120_shapeCheck j)) = true := by decide +kernel

#print axioms container_c5inc120_vertices_range_13
end PackingCertificates.Algebraic.Generated.ND.Records.FastCanonical
