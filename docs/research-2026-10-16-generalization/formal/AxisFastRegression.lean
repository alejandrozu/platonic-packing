import PackingCertificates.AxisFast

/-! Regressions for the checked cache and checked direction-tag boundaries. -/
namespace PackingCertificates.AxisFast.Tests

open PackingCertificates.Rational
open PackingCertificates.Catalogue


def identityRows : Fin 3 → QPoint 3 := ![![1,0,0], ![0,1,0], ![0,0,1]]

def record : CubeRecord 2 where
  scale := 5/2
  containerCenter := ![0,0,0]
  quaternion := fun _ => ![1,0,0,0]
  rotation := fun _ => identityRows
  center := ![![-3/4,0,0], ![3/4,0,0]]
  separation := fun _ _ => ⟨![1,0,0],-1/4,1/4⟩

def cache : Cache 2 where
  lower := ![![-5/4,-1/2,-1/2], ![1/4,-1/2,-1/2]]
  upper := ![![-1/4,1/2,1/2], ![5/4,1/2,1/2]]

def directions : Directions 2 := fun _ _ => some (0,false)

example : check record cache directions = true := by decide +kernel

theorem complete_packing : record.Valid := check_sound record cache directions (by decide +kernel)

/-- Incorrect proposed cached bounds cannot pass, even when they would make
separation easier for an unchecked consumer. -/
def wrongCache : Cache 2 :=
  { cache with upper := ![![-3/4,1/2,1/2], ![5/4,1/2,1/2]] }
example : cacheRowCheck record wrongCache 0 = false := by decide +kernel
example : check record wrongCache directions = false := by decide +kernel

/-- The normal is x-directed; falsely tagging it as y-directed is rejected. -/
def falseAxisLabel : Directions 2 := fun _ _ => some (1,false)
example : check record cache falseAxisLabel = false := by decide +kernel

/-- A false sign on the otherwise correct axis is rejected too. -/
def falseAxisSign : Directions 2 := fun _ _ => some (0,true)
example : check record cache falseAxisSign = false := by decide +kernel

/-- Missing shortcut metadata takes the complete generic support path. -/
def noShortcut : Directions 2 := fun _ _ => none
example : check record cache noShortcut = true := by decide +kernel

#print axioms complete_packing
#print axioms PackingCertificates.AxisFast.check_sound

end PackingCertificates.AxisFast.Tests
