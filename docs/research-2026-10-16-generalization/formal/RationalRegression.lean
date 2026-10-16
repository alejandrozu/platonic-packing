import PackingCertificates.Rational

namespace PackingCertificates.Rational.Tests

def template : Fin 8 → QPoint 3 :=
  ![![-1/2,-1/2,-1/2], ![-1/2,-1/2,1/2], ![-1/2,1/2,-1/2], ![-1/2,1/2,1/2],
    ![1/2,-1/2,-1/2], ![1/2,-1/2,1/2], ![1/2,1/2,-1/2], ![1/2,1/2,1/2]]

def identityRows : Fin 3 → QPoint 3 := ![![1,0,0], ![0,1,0], ![0,0,1]]
def good : PlacementCertificate 3 2 8 6 where
  template := template
  rotation := fun _ => identityRows
  center := ![![-3/4,0,0], ![3/4,0,0]]
  walls := ![⟨![1,0,0],5/4⟩,⟨![0,1,0],5/4⟩,⟨![0,0,1],5/4⟩,
             ⟨![-1,0,0],5/4⟩,⟨![0,-1,0],5/4⟩,⟨![0,0,-1],5/4⟩]
  separation := fun _ _ => ⟨![1,0,0],-1/4,1/4⟩
example : checkPlaced good = true := by decide +kernel
def good_geometric_packing := checkPlaced_sound good (by decide +kernel)

def overlap : PlacementCertificate 3 2 8 6 :=
  { good with center := fun _ => ![0,0,0] }
example : checkPlaced overlap = false := by decide +kernel

def nonorthogonal : PlacementCertificate 3 2 8 6 :=
  { good with rotation := fun _ => ![![2,0,0], ![0,1,0], ![0,0,1]] }
example : checkPlaced nonorthogonal = false := by decide +kernel

def missingPlane : PlacementCertificate 3 2 8 6 :=
  { good with separation := fun _ _ => ⟨![0,0,0],-1/4,1/4⟩ }
example : checkPlaced missingPlane = false := by decide +kernel

def protrudes : PlacementCertificate 3 2 8 6 :=
  { good with walls := fun _ => ⟨![1,0,0],1/4⟩ }
example : checkPlaced protrudes = false := by decide +kernel

#print axioms PackingCertificates.Rational.realLinear_realPoint
#print axioms PackingCertificates.Rational.check_sound
#print axioms PackingCertificates.Rational.checkPlaced_sound
#print axioms PackingCertificates.Rational.checkPlaced_preserves_dotProduct
#print axioms PackingCertificates.Rational.checkPlaced_preserves_squared_distance
#print axioms good_geometric_packing
end PackingCertificates.Rational.Tests



