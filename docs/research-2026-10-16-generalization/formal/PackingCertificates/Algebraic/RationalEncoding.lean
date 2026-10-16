import PackingCertificates.Algebraic.FragmentND

namespace PackingCertificates.Algebraic.RationalEncoding

theorem ratio_encoding (a : ℤ) (b : ℕ) : mkRat a b = (a : ℚ)/(b : ℚ) :=
  Rat.mkRat_eq_div a b

theorem signed_example : mkRat (Int.negSucc 2) 4 = (-3 : ℚ)/4 := by decide +kernel
theorem positive_example : mkRat (Int.ofNat 17) 256 = (17 : ℚ)/256 := by decide +kernel
theorem large_example : mkRat (Int.negSucc 1496577676626844588240573268701473812127674924007424)
    748288838313422294120286634350736906063837462003712 =
    (-1496577676626844588240573268701473812127674924007425 : ℚ)/
      748288838313422294120286634350736906063837462003712 := by decide +kernel

end PackingCertificates.Algebraic.RationalEncoding

#print axioms PackingCertificates.Algebraic.RationalEncoding.ratio_encoding
#print axioms PackingCertificates.Algebraic.RationalEncoding.signed_example
#print axioms PackingCertificates.Algebraic.RationalEncoding.positive_example
#print axioms PackingCertificates.Algebraic.RationalEncoding.large_example
