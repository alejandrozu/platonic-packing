import PackingCertificates.Extensions.NDModels
import PackingCertificates.Extensions.BoxSupport

namespace PackingCertificates.Extensions.NDSupportRegression
open PackingCertificates.Rational
open PackingCertificates.Extensions

/-- Two separated canonical four-dimensional cubes inside a larger cube. -/
def good : NDSupport.Certificate 4 2 16 16 where
  piece := NDModels.c8Piece
  outer := NDModels.c8Outer
  rotation := fun _ a b => if a = b then 1 else 0
  center := fun i a => if a = 0 then (if i = 0 then -(501/1000) else 501/1000) else 0
  separation := fun _ _ => ⟨BoxSupport.axis 0, -(1/2000), 1/2000⟩
  containerCenter := 0
  scale := 201/100

theorem good_checked : NDSupport.check good = true := by decide +kernel

theorem good_walls : ∀ i : Fin 2, BoxSupport.wallRowCheck good i = true := by decide +kernel

theorem good_packing : NDSupport.Valid good := NDSupport.check_sound good good_checked

theorem wrong_scale_rejected : NDSupport.check {good with scale := 1} = false := by decide +kernel

theorem wrong_wall_rejected : BoxSupport.wallRowCheck {good with scale := 1} 0 = false := by decide +kernel

theorem overlapping_pieces_rejected : NDSupport.check
    {good with center := fun _ a => if a = 0 then -(501/1000) else 0} = false := by decide +kernel

theorem distorted_piece_rejected : NDSupport.check
    {good with rotation := fun _ a b => if a = b then (if a = 0 then 2 else 1) else 0} = false := by decide +kernel

theorem false_separating_plane_rejected : NDSupport.check
    {good with separation := fun _ _ => ⟨0, -(1/2000), 1/2000⟩} = false := by decide +kernel

#print axioms good_checked
#print axioms good_walls
#print axioms good_packing
#print axioms wrong_scale_rejected
#print axioms wrong_wall_rejected
#print axioms overlapping_pieces_rejected
#print axioms distorted_piece_rejected
#print axioms false_separating_plane_rejected
end PackingCertificates.Extensions.NDSupportRegression
