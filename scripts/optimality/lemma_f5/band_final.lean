/-! ## The one-variable bound in `c` -/

theorem seg1 (c ρ : ℝ) (hl : 67 / 100 ≤ c) (hh : c ≤ 11225 / 14406) (hρ0 : 0 < ρ) (hρ2 : ρ ^ 2 = 1 - c ^ 2) :
    ρ * (15338317 / 7425000 - 6108137 / 3437500 * c) ≤ 2 - 2 * c := by
  have h1 := sub_nonneg.2 hl; have h2 := sub_nonneg.2 hh
  have P : 0 ≤ 4 * (1 - c) - (1 + c) * (15338317 / 7425000 - 6108137 / 3437500 * c) ^ 2 := by
    nlinarith [mul_nonneg h1 h2, mul_nonneg (mul_nonneg h1 h2) h1, mul_nonneg (mul_nonneg h1 h2) h2,
      mul_nonneg (mul_nonneg h1 h1) h1, mul_nonneg (mul_nonneg h2 h2) h2]
  have hc1 : 0 ≤ 1 - c := by linarith
  have hsq : (ρ * (15338317 / 7425000 - 6108137 / 3437500 * c)) ^ 2 ≤ (2 - 2 * c) ^ 2 := by
    have e : (ρ * (15338317 / 7425000 - 6108137 / 3437500 * c)) ^ 2 =
        (1 - c ^ 2) * (15338317 / 7425000 - 6108137 / 3437500 * c) ^ 2 := by rw [mul_pow, hρ2]
    rw [e]; nlinarith [mul_nonneg hc1 P]
  by_contra h
  push Not at h
  have := mul_pos (sub_pos.2 h) (by linarith : 0 < ρ * (15338317 / 7425000 - 6108137 / 3437500 * c) + (2 - 2 * c))
  nlinarith

theorem seg2 (c ρ : ℝ) (hl : 11225 / 14406 ≤ c) (hh : c ≤ 8661 / 10000) (hρ0 : 0 < ρ) (hρ2 : ρ ^ 2 = 1 - c ^ 2) :
    ρ * (14012927 / 6930000 - 21295267 / 12375000 * c) ≤ 2 - 2 * c := by
  have h1 := sub_nonneg.2 hl; have h2 := sub_nonneg.2 hh
  have P : 0 ≤ 4 * (1 - c) - (1 + c) * (14012927 / 6930000 - 21295267 / 12375000 * c) ^ 2 := by
    nlinarith [mul_nonneg h1 h2, mul_nonneg (mul_nonneg h1 h2) h1, mul_nonneg (mul_nonneg h1 h2) h2,
      mul_nonneg (mul_nonneg h1 h1) h1, mul_nonneg (mul_nonneg h2 h2) h2]
  have hc1 : 0 ≤ 1 - c := by linarith
  have hsq : (ρ * (14012927 / 6930000 - 21295267 / 12375000 * c)) ^ 2 ≤ (2 - 2 * c) ^ 2 := by
    have e : (ρ * (14012927 / 6930000 - 21295267 / 12375000 * c)) ^ 2 =
        (1 - c ^ 2) * (14012927 / 6930000 - 21295267 / 12375000 * c) ^ 2 := by rw [mul_pow, hρ2]
    rw [e]; nlinarith [mul_nonneg hc1 P]
  by_contra h
  push Not at h
  have := mul_pos (sub_pos.2 h) (by linarith : 0 < ρ * (14012927 / 6930000 - 21295267 / 12375000 * c) + (2 - 2 * c))
  nlinarith

set_option maxHeartbeats 2000000 in
/-- The band inequality from the three sphere bounds (rescaled to radius `ρ`), interpolated in `λ`, and the
one-variable bounds `seg1`, `seg2`. -/
theorem band_final (c ρ T m3 : ℝ) (hc : 0 < c) (hc1 : 9 / 20 ≤ c ^ 2) (hc2 : c ^ 2 ≤ 3 / 4) (hρ0 : 0 < ρ)
    (hρ2 : ρ ^ 2 = 1 - c ^ 2)
    (hA : 33 / 50 * ρ ^ 2 * T + m3 ≤ 187333 / 100000 * ρ ^ 3)
    (hB : 147 / 200 * ρ ^ 2 * T + m3 ≤ 7997 / 4000 * ρ ^ 3)
    (hC : 161 / 200 * ρ ^ 2 * T + m3 ≤ 6636 / 3125 * ρ ^ 3) :
    ρ ^ 2 * (2 * c + 2 * T - 2) ≤
      140 / 99 * (c * (207 / 250) * ρ ^ 3 + ρ ^ 2 * T - ρ ^ 2 * m3 - c * (c - 14 / 25) * m3) := by
  have hl : 67 / 100 ≤ c := by nlinarith
  have hh : c ≤ 8661 / 10000 := by nlinarith
  have z : (ρ ^ 2 + c ^ 2 - 1) * m3 = 0 := by rw [hρ2]; ring
  have hρ3 : 0 ≤ ρ ^ 2 := sq_nonneg ρ
  rcases le_total c (11225 / 14406) with hs | hs
  · have hα : 0 ≤ 1796 / 297 - 19208 / 2475 * c := by linarith
    have hβ : 0 ≤ 1568 / 225 * c - 1376 / 297 := by linarith
    have two := mul_le_mul_of_nonneg_left (seg1 c ρ hl hs hρ0 hρ2) hρ3
    linarith [mul_nonneg hα (sub_nonneg.2 hA), mul_nonneg hβ (sub_nonneg.2 hB)]
  · have hα : 0 ≤ 5470 / 693 - 4508 / 495 * c := by linarith
    have hβ : 0 ≤ 1372 / 165 * c - 4490 / 693 := by linarith
    have two := mul_le_mul_of_nonneg_left (seg2 c ρ hs hh hρ0 hρ2) hρ3
    linarith [mul_nonneg hα (sub_nonneg.2 hB), mul_nonneg hβ (sub_nonneg.2 hC)]

