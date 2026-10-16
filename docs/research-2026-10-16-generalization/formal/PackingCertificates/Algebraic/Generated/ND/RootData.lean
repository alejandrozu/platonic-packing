import PackingCertificates.Algebraic.RootSqrt

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.Generated.ND

def nd_root2 : RootSpec := ⟨[(-2 : ℚ), (0 : ℚ), (1 : ℚ)], ⟨((2116480447430499751252734943246140439044294856528969 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1058240223715249875626367471623070219522147428264485 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root2_checked : nd_root2.check = true := by decide +kernel

def nd_root5 : RootSpec := ⟨[(-5 : ℚ), (0 : ℚ), (1 : ℚ)], ⟨((3346449418546322664974573798948318809677335086456733 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1673224709273161332487286899474159404838667543228367 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root5_checked : nd_root5.check = true := by decide +kernel

def nd_root6 : RootSpec := ⟨[(-6 : ℚ), (0 : ℚ), (1 : ℚ)], ⟨((3665851668175735839308620192402334879571877847869373 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1832925834087867919654310096201167439785938923934687 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root6_checked : nd_root6.check = true := by decide +kernel

def nd_root7 : RootSpec := ⟨[(-7 : ℚ), (0 : ℚ), (1 : ℚ)], ⟨((3959572350045472962995615949992113326245837738208737 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1979786175022736481497807974996056663122918869104369 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root7_checked : nd_root7.check = true := by decide +kernel

def nd_root2_literal : QuadraticScale.Spec :=
  ⟨nd_root2, (2 : ℚ), 1, 0, false, 1, 0, ⟨((2116480447430499751252734943246140439044294856528969 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1058240223715249875626367471623070219522147428264485 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root2_literal_checked : nd_root2_literal.check = true := by decide +kernel
theorem nd_root2_is_sqrt : nd_root2.root nd_root2_checked = Real.sqrt (2 : ℝ) := by
  simpa [nd_root2_literal] using nd_root2_literal.root_eq_sqrt nd_root2_checked nd_root2_literal_checked

def nd_root5_literal : QuadraticScale.Spec :=
  ⟨nd_root5, (5 : ℚ), 1, 0, false, 1, 0, ⟨((2116480447430499751252734943246140439044294856528969 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1058240223715249875626367471623070219522147428264485 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root5_literal_checked : nd_root5_literal.check = true := by decide +kernel
theorem nd_root5_is_sqrt : nd_root5.root nd_root5_checked = Real.sqrt (5 : ℝ) := by
  simpa [nd_root5_literal] using nd_root5_literal.root_eq_sqrt nd_root5_checked nd_root5_literal_checked

def nd_root6_literal : QuadraticScale.Spec :=
  ⟨nd_root6, (6 : ℚ), 1, 0, false, 1, 0, ⟨((2116480447430499751252734943246140439044294856528969 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1058240223715249875626367471623070219522147428264485 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root6_literal_checked : nd_root6_literal.check = true := by decide +kernel
theorem nd_root6_is_sqrt : nd_root6.root nd_root6_checked = Real.sqrt (6 : ℝ) := by
  simpa [nd_root6_literal] using nd_root6_literal.root_eq_sqrt nd_root6_checked nd_root6_literal_checked

def nd_root7_literal : QuadraticScale.Spec :=
  ⟨nd_root7, (7 : ℚ), 1, 0, false, 1, 0, ⟨((2116480447430499751252734943246140439044294856528969 : ℚ) / 1496577676626844588240573268701473812127674924007424), ((1058240223715249875626367471623070219522147428264485 : ℚ) / 748288838313422294120286634350736906063837462003712)⟩⟩
theorem nd_root7_literal_checked : nd_root7_literal.check = true := by decide +kernel
theorem nd_root7_is_sqrt : nd_root7.root nd_root7_checked = Real.sqrt (7 : ℝ) := by
  simpa [nd_root7_literal] using nd_root7_literal.root_eq_sqrt nd_root7_checked nd_root7_literal_checked

end PackingCertificates.Algebraic.Generated.ND
