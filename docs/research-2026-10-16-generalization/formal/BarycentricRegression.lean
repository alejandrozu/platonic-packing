import PackingCertificates.Barycentric

namespace PackingCertificates.Barycentric.Tests

open PackingCertificates.Rational

def simplexVertex (p : Fin 7) : QPoint 6 :=
  fun a => if p.val = a.val + 1 then 1 else 0

def identityRows : Fin 6 → QPoint 6 := fun a b => if a = b then 1 else 0

def good : Certificate 6 1 7 7 1 where
  placement := {
    template := simplexVertex
    rotation := fun _ => identityRows
    center := fun _ _ => 0
    walls := Fin.elim0
    separation := fun _ _ => ⟨fun _ => 0, 0, 1⟩ }
  containerVertices := simplexVertex
  scale := 1
  containerCenter := fun _ => 0
  indices := fun _ p _ => p
  weights := fun _ _ _ => 1

example : check good = true := by decide +kernel

theorem good_sound : Valid good := check_sound good (by decide +kernel)

def negativeWeight : Certificate 6 1 7 7 1 :=
  { good with weights := fun _ _ _ => -1 }
example : check negativeWeight = false := by decide +kernel

def wrongMass : Certificate 6 1 7 7 1 :=
  { good with weights := fun _ _ _ => 2 }
example : check wrongMass = false := by decide +kernel

def wrongVertex : Certificate 6 1 7 7 1 :=
  { good with indices := fun _ _ _ => 0 }
example : check wrongVertex = false := by decide +kernel

def zeroScale : Certificate 6 1 7 7 1 := { good with scale := 0 }
example : check zeroScale = false := by decide +kernel

def protrudes : Certificate 6 1 7 7 1 :=
  { good with placement := { good.placement with center := fun _ _ => 1 } }
example : check protrudes = false := by decide +kernel

#print axioms PackingCertificates.Barycentric.vertexCheck_sound
#print axioms PackingCertificates.Barycentric.check_sound
#print axioms good_sound

end PackingCertificates.Barycentric.Tests
