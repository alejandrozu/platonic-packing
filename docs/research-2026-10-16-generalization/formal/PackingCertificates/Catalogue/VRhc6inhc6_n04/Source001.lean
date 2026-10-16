import PackingCertificates.Catalogue.VRhc6inhc6_n04.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.VRhc6inhc6_n04
open PackingCertificates.Rational

theorem source_piece_1 : Cayley.check (source (1 : Fin 4)) = true := by decide +kernel

theorem gram_piece_1 :
    allFin 6 (fun a => allFin 6 (fun b =>
      decide (qdot (record.placement.rotation (1 : Fin 4) a)
        (record.placement.rotation (1 : Fin 4) b) = if a = b then 1 else 0))) = true := by decide +kernel


theorem pair_row_1 :
    allFin 4 (fun j => if (1 : Fin 4) < j then
      planeCheck (record.placement.toCertificate.vertices (1 : Fin 4))
        (record.placement.toCertificate.vertices j)
        (record.placement.separation (1 : Fin 4) j) else true) = true := by decide +kernel


#print axioms PackingCertificates.Catalogue.VRhc6inhc6_n04.source_piece_1
#print axioms PackingCertificates.Catalogue.VRhc6inhc6_n04.gram_piece_1
#print axioms PackingCertificates.Catalogue.VRhc6inhc6_n04.pair_row_1
end PackingCertificates.Catalogue.VRhc6inhc6_n04
