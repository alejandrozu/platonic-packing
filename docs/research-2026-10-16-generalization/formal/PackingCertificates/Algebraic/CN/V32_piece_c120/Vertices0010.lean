import PackingCertificates.Algebraic.CN.V32_piece_c120.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.Generated.ND.Records.FastCanonical
open PackingCertificates.Rational
open PackingCertificates.Algebraic.FragmentND
open PackingCertificates.Algebraic.TemplateFragments

theorem piece_c120_vertices_range_10 : rangeCheck 320 32 (by decide)
    (fun j => allFin 4 (piece_c120.coordinateCheck j) &&
      (antipodalItemCheck piece_c120 piece_c120_opposite 2 j && piece_c120_shapeCheck j)) = true := by decide +kernel

#print axioms piece_c120_vertices_range_10
end PackingCertificates.Algebraic.Generated.ND.Records.FastCanonical
