import PackingCertificates.Cayley

namespace PackingCertificates.Cayley.Tests

def nontrivial : Certificate 4 where
  skew := ![![0,1/2,0,0], ![-1/2,0,0,0], ![0,0,0,0], ![0,0,0,0]]
  signs := ![-1,-1,1,1]
  inverse := ![![4/5,2/5,0,0], ![-2/5,4/5,0,0], ![0,0,1,0], ![0,0,0,1]]
  rotation := ![![-3/5,-4/5,0,0], ![4/5,-3/5,0,0], ![0,0,1,0], ![0,0,0,1]]

theorem nontrivial_passes : check nontrivial = true := by decide +kernel

theorem nontrivial_sound : Valid nontrivial := check_sound nontrivial nontrivial_passes

def wrongInverse : Certificate 4 := {nontrivial with inverse := 0}

theorem wrong_inverse_rejected : check wrongInverse = false := by decide +kernel

def oddSign : Certificate 4 := {nontrivial with signs := ![-1,1,1,1]}

theorem odd_sign_rejected : check oddSign = false := by decide +kernel

def changedRotation : Certificate 4 := {nontrivial with rotation := 1}

theorem changed_rotation_rejected : check changedRotation = false := by decide +kernel

end PackingCertificates.Cayley.Tests

#print axioms PackingCertificates.Cayley.determinant_one
#print axioms PackingCertificates.Cayley.check_sound
#print axioms PackingCertificates.Cayley.determinant_real
#print axioms PackingCertificates.Cayley.Tests.nontrivial_passes
#print axioms PackingCertificates.Cayley.Tests.nontrivial_sound
#print axioms PackingCertificates.Cayley.Tests.wrong_inverse_rejected
#print axioms PackingCertificates.Cayley.Tests.odd_sign_rejected
#print axioms PackingCertificates.Cayley.Tests.changed_rotation_rejected
