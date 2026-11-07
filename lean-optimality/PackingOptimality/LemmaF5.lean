import PackingOptimality.LemmaF4
import PackingOptimality.LemmaF5Sphere

/-!
# Lemma F in dimension 5

`F_j(R) = Σᵢ |Rᵢⱼ| (2 - ‖row i‖₁) ≤ 1` for every orthogonal 5×5 matrix and every column `j`. Fix a column and
an entry `c` of it, and write `R = [c r; x M]` around it (`NearAxis.BlockOrth`), `ρ = ‖x‖₂ = √(1 - c²)`.

* **Near an axis**, `c² ≥ 3/4`: Hosono's polar-decomposition step (`NearAxis.near_region` with `m = 4`), which
  takes Lemma F in dimension 4 (`LemmaF4.lemmaF4`) as its hypothesis.
* **The band** `9/20 ≤ c² ≤ 3/4` (new). For each other column `k`, `ζ = (c rₖ, xᵢ Mᵢₖ)ᵢ` has zero sum, so
  `‖ζ‖₁ ≥ √2 ‖ζ‖₂ ≥ √2 ⟨|ζ|, |w|⟩` for any `‖w‖₂ ≤ 1`. The weight is the column `(rₖ, Mᵢₖ)` turned in the plane
  of `e₁` and `x` so that `x` goes to the fixed direction at angle `ψ ≈ 56°` from `e₁` (`cos ψ = 14/25`,
  `sin ψ = 207/250`):

    `w = (sin ψ · rₖ / ρ, Mᵢₖ + (c - cos ψ) xᵢ rₖ / ρ²)`,   `‖w‖₂² = 1 - (1 - cos²ψ - sin²ψ) rₖ² / ρ² ≤ 1`.

  Summed over `k` with the orthonormality of the rows, the weights give
  `Σₖ ⟨|ζ|, |w|⟩ ≥ c sin ψ ρ + T - (1 - c cos ψ) m₃ / ρ²` with `T = Σᵢ |xᵢ|`, `m₃ = Σᵢ |xᵢ|³`, and
  `F₁ ≤ 1` reduces to a one-dimensional bound for `λ T + m₃ / ρ²` on the sphere `‖x‖₂ = ρ`. That bound is
  `LemmaF5Sphere` (three values of `λ`, exact line certificates), interpolated in `λ` (`band_final`).
* **Far from the axes**, every `c² ≤ 9/20`: the 4D argument (`LemmaF4.far_core`) with five rows: the zero-sum
  bound with the column itself as weight, and the sphere bound `cs5`.

The proof uses no computer search beyond the generated line certificates, which Lean checks.
-/

set_option linter.unusedVariables false
set_option linter.unusedSimpArgs false

namespace PackingOptimality.LemmaF5

open NearAxis Matrix LemmaF4 LemmaF5Sphere

/-! ## A zero-sum vector against a weight vector -/

set_option maxHeartbeats 1000000 in
/-- A zero-sum vector of length 5 and a weight vector of norm at most `K`:
`(140/99) Σᵢ |zᵢ| |vᵢ| ≤ K Σᵢ |zᵢ|`. (`‖z‖₁² ≥ 2‖z‖₂²` for zero sum, Cauchy–Schwarz, and `140/99 ≤ √2`.) -/
theorem zs_bound (z0 z1 z2 z3 z4 v0 v1 v2 v3 v4 K : ℝ) (hK : 0 ≤ K)
    (hz : z0 + z1 + z2 + z3 + z4 = 0)
    (hv : v0 ^ 2 + v1 ^ 2 + v2 ^ 2 + v3 ^ 2 + v4 ^ 2 ≤ K ^ 2) :
    140 / 99 * (|z0| * |v0| + |z1| * |v1| + |z2| * |v2| + |z3| * |v3| + |z4| * |v4|) ≤
      K * (|z0| + |z1| + |z2| + |z3| + |z4|) := by
  have pz : ∀ u v : ℝ, 0 ≤ |u| * |v| + u * v := fun u v => by
    have := neg_le_abs (u * v); rw [abs_mul] at this; linarith
  have hX : 2 * (z0 ^ 2 + z1 ^ 2 + z2 ^ 2 + z3 ^ 2 + z4 ^ 2) ≤ (|z0| + |z1| + |z2| + |z3| + |z4|) ^ 2 := by
    have h2 : (z0 + z1 + z2 + z3 + z4) ^ 2 = 0 := by rw [hz]; ring
    nlinarith [pz z0 z1, pz z0 z2, pz z0 z3, pz z0 z4, pz z1 z2, pz z1 z3, pz z1 z4, pz z2 z3, pz z2 z4,
      pz z3 z4, sq_abs z0, sq_abs z1, sq_abs z2, sq_abs z3, sq_abs z4]
  have hY : (|z0| * |v0| + |z1| * |v1| + |z2| * |v2| + |z3| * |v3| + |z4| * |v4|) ^ 2 ≤
      (z0 ^ 2 + z1 ^ 2 + z2 ^ 2 + z3 ^ 2 + z4 ^ 2) * (v0 ^ 2 + v1 ^ 2 + v2 ^ 2 + v3 ^ 2 + v4 ^ 2) := by
    have e : (|z0| * |v0| + |z1| * |v1| + |z2| * |v2| + |z3| * |v3| + |z4| * |v4|) ^ 2 +
        ((|z0| * |v1| - |z1| * |v0|) ^ 2 + (|z0| * |v2| - |z2| * |v0|) ^ 2 + (|z0| * |v3| - |z3| * |v0|) ^ 2 +
          (|z0| * |v4| - |z4| * |v0|) ^ 2 + (|z1| * |v2| - |z2| * |v1|) ^ 2 + (|z1| * |v3| - |z3| * |v1|) ^ 2 +
          (|z1| * |v4| - |z4| * |v1|) ^ 2 + (|z2| * |v3| - |z3| * |v2|) ^ 2 + (|z2| * |v4| - |z4| * |v2|) ^ 2 +
          (|z3| * |v4| - |z4| * |v3|) ^ 2) =
        (|z0| ^ 2 + |z1| ^ 2 + |z2| ^ 2 + |z3| ^ 2 + |z4| ^ 2) *
          (|v0| ^ 2 + |v1| ^ 2 + |v2| ^ 2 + |v3| ^ 2 + |v4| ^ 2) := by ring
    simp only [sq_abs] at e
    nlinarith [sq_nonneg (|z0| * |v1| - |z1| * |v0|), sq_nonneg (|z0| * |v2| - |z2| * |v0|),
      sq_nonneg (|z0| * |v3| - |z3| * |v0|), sq_nonneg (|z0| * |v4| - |z4| * |v0|),
      sq_nonneg (|z1| * |v2| - |z2| * |v1|), sq_nonneg (|z1| * |v3| - |z3| * |v1|),
      sq_nonneg (|z1| * |v4| - |z4| * |v1|), sq_nonneg (|z2| * |v3| - |z3| * |v2|),
      sq_nonneg (|z2| * |v4| - |z4| * |v2|), sq_nonneg (|z3| * |v4| - |z4| * |v3|)]
  set X := |z0| + |z1| + |z2| + |z3| + |z4|
  set Y := |z0| * |v0| + |z1| * |v1| + |z2| * |v2| + |z3| * |v3| + |z4| * |v4|
  set Z := z0 ^ 2 + z1 ^ 2 + z2 ^ 2 + z3 ^ 2 + z4 ^ 2
  have hZ : 0 ≤ Z := by positivity
  have hX0 : 0 ≤ X := by positivity
  have hY0 : 0 ≤ Y := by positivity
  have h1 : Y ^ 2 ≤ Z * K ^ 2 := le_trans hY (mul_le_mul_of_nonneg_left hv hZ)
  have h2 : 2 * Y ^ 2 ≤ K ^ 2 * X ^ 2 := by nlinarith
  by_contra h
  push Not at h
  have h3 : (K * X) ^ 2 < (140 / 99 * Y) ^ 2 := by
    have := mul_nonneg hK hX0
    nlinarith
  nlinarith

theorem abs_term (x M w : ℝ) : |x| * (M * w) ≤ |x * M| * |w| := by
  rw [abs_mul, mul_assoc, ← abs_mul M w]
  exact mul_le_mul_of_nonneg_left (le_abs_self _) (abs_nonneg x)

/-- Rescaling a sphere bound: from `Σ (sᵢ³ + λ sᵢ) ≤ U` on the unit sphere to `λ ρ² Σ Xᵢ + Σ Xᵢ³ ≤ U ρ³` on the
sphere of radius `ρ`. -/
theorem scale4 (lam U ρ X0 X1 X2 X3 : ℝ) (hρ : 0 < ρ) (h0 : 0 ≤ X0) (h1 : 0 ≤ X1) (h2 : 0 ≤ X2)
    (h3 : 0 ≤ X3) (hX : X0 ^ 2 + X1 ^ 2 + X2 ^ 2 + X3 ^ 2 = ρ ^ 2)
    (H : ∀ s0 s1 s2 s3 : ℝ, 0 ≤ s0 → 0 ≤ s1 → 0 ≤ s2 → 0 ≤ s3 → s0 ^ 2 + s1 ^ 2 + s2 ^ 2 + s3 ^ 2 = 1 →
      (s0 ^ 3 + lam * s0) + (s1 ^ 3 + lam * s1) + (s2 ^ 3 + lam * s2) + (s3 ^ 3 + lam * s3) ≤ U) :
    lam * ρ ^ 2 * (X0 + X1 + X2 + X3) + (X0 * X0 ^ 2 + X1 * X1 ^ 2 + X2 * X2 ^ 2 + X3 * X3 ^ 2) ≤ U * ρ ^ 3 := by
  have hρ2 : ρ ^ 2 ≠ 0 := by positivity
  have h := H (X0 / ρ) (X1 / ρ) (X2 / ρ) (X3 / ρ) (by positivity) (by positivity) (by positivity)
    (by positivity) (by field_simp; linarith)
  have e : ∀ X : ℝ, (X / ρ) ^ 3 + lam * (X / ρ) = (X * X ^ 2 + lam * ρ ^ 2 * X) / ρ ^ 3 := fun X => by
    field_simp
  rw [e, e, e, e, ← add_div, ← add_div, ← add_div, div_le_iff₀ (by positivity)] at h
  linarith

/-! ## The band `9/20 ≤ c² ≤ 3/4` -/

set_option maxHeartbeats 4000000 in
/-- **The band.** `F₁ ≤ 1` when `9/20 ≤ c² ≤ 3/4`, written with the 25 entries of `R = [c r; x M]` and the
orthonormality relations that are used. -/
theorem band_core (c r0 r1 r2 r3 x0 x1 x2 x3 m00 m01 m02 m03 m10 m11 m12 m13 m20 m21 m22 m23
    m30 m31 m32 m33 : ℝ)
    (hc : 0 < c) (hc1 : 9 / 20 ≤ c ^ 2) (hc2 : c ^ 2 ≤ 3 / 4)
    (col1 : c ^ 2 + x0 ^ 2 + x1 ^ 2 + x2 ^ 2 + x3 ^ 2 = 1)
    (row1 : c ^ 2 + r0 ^ 2 + r1 ^ 2 + r2 ^ 2 + r3 ^ 2 = 1)
    (p0 : c * r0 + x0 * m00 + x1 * m10 + x2 * m20 + x3 * m30 = 0)
    (p1 : c * r1 + x0 * m01 + x1 * m11 + x2 * m21 + x3 * m31 = 0)
    (p2 : c * r2 + x0 * m02 + x1 * m12 + x2 * m22 + x3 * m32 = 0)
    (p3 : c * r3 + x0 * m03 + x1 * m13 + x2 * m23 + x3 * m33 = 0)
    (k0 : r0 ^ 2 + m00 ^ 2 + m10 ^ 2 + m20 ^ 2 + m30 ^ 2 = 1)
    (k1 : r1 ^ 2 + m01 ^ 2 + m11 ^ 2 + m21 ^ 2 + m31 ^ 2 = 1)
    (k2 : r2 ^ 2 + m02 ^ 2 + m12 ^ 2 + m22 ^ 2 + m32 ^ 2 = 1)
    (k3 : r3 ^ 2 + m03 ^ 2 + m13 ^ 2 + m23 ^ 2 + m33 ^ 2 = 1)
    (w0 : x0 ^ 2 + m00 ^ 2 + m01 ^ 2 + m02 ^ 2 + m03 ^ 2 = 1)
    (w1 : x1 ^ 2 + m10 ^ 2 + m11 ^ 2 + m12 ^ 2 + m13 ^ 2 = 1)
    (w2 : x2 ^ 2 + m20 ^ 2 + m21 ^ 2 + m22 ^ 2 + m23 ^ 2 = 1)
    (w3 : x3 ^ 2 + m30 ^ 2 + m31 ^ 2 + m32 ^ 2 + m33 ^ 2 = 1)
    (q0 : c * x0 + r0 * m00 + r1 * m01 + r2 * m02 + r3 * m03 = 0)
    (q1 : c * x1 + r0 * m10 + r1 * m11 + r2 * m12 + r3 * m13 = 0)
    (q2 : c * x2 + r0 * m20 + r1 * m21 + r2 * m22 + r3 * m23 = 0)
    (q3 : c * x3 + r0 * m30 + r1 * m31 + r2 * m32 + r3 * m33 = 0) :
    c * (2 - c - (|r0| + |r1| + |r2| + |r3|)) +
      |x0| * (2 - |x0| - (|m00| + |m01| + |m02| + |m03|)) +
      |x1| * (2 - |x1| - (|m10| + |m11| + |m12| + |m13|)) +
      |x2| * (2 - |x2| - (|m20| + |m21| + |m22| + |m23|)) +
      |x3| * (2 - |x3| - (|m30| + |m31| + |m32| + |m33|)) ≤ 1 := by
  obtain ⟨ρ, hρ0, hρ2⟩ : ∃ ρ : ℝ, 0 < ρ ∧ ρ ^ 2 = 1 - c ^ 2 :=
    ⟨Real.sqrt (1 - c ^ 2), Real.sqrt_pos.2 (by nlinarith), Real.sq_sqrt (by nlinarith)⟩
  -- the weight of column k has norm at most ρ²
  have nrm : ∀ r ma mb mc md : ℝ, r ^ 2 + ma ^ 2 + mb ^ 2 + mc ^ 2 + md ^ 2 = 1 →
      c * r + x0 * ma + x1 * mb + x2 * mc + x3 * md = 0 →
      (207 / 250 * ρ * r) ^ 2 + (ρ ^ 2 * ma + (c - 14 / 25) * x0 * r) ^ 2 +
        (ρ ^ 2 * mb + (c - 14 / 25) * x1 * r) ^ 2 + (ρ ^ 2 * mc + (c - 14 / 25) * x2 * r) ^ 2 +
        (ρ ^ 2 * md + (c - 14 / 25) * x3 * r) ^ 2 ≤ (ρ ^ 2) ^ 2 := by
    intro r ma mb mc md hk hp
    have e : (207 / 250 * ρ * r) ^ 2 + (ρ ^ 2 * ma + (c - 14 / 25) * x0 * r) ^ 2 +
        (ρ ^ 2 * mb + (c - 14 / 25) * x1 * r) ^ 2 + (ρ ^ 2 * mc + (c - 14 / 25) * x2 * r) ^ 2 +
        (ρ ^ 2 * md + (c - 14 / 25) * x3 * r) ^ 2 = (ρ ^ 2) ^ 2 - 51 / 62500 * ρ ^ 2 * r ^ 2 := by
      linear_combination ρ ^ 4 * hk + 2 * ρ ^ 2 * (c - 14 / 25) * r * hp + (c - 14 / 25) ^ 2 * r ^ 2 * col1 -
        r ^ 2 * (ρ ^ 2 + (c - 14 / 25) ^ 2) * hρ2
    nlinarith [sq_nonneg (ρ * r)]
  -- the first weight entry, exactly
  have t0 : ∀ r : ℝ, |c * r| * |207 / 250 * ρ * r| = c * (207 / 250) * ρ * r ^ 2 := fun r => by
    rw [abs_mul, abs_mul, abs_mul, abs_of_pos hc, abs_of_pos hρ0, abs_of_pos (by norm_num : (0 : ℝ) < 207 / 250),
      ← sq_abs r]
    ring
  -- per column: zero sum against the weight, and the lower bound of the pairing
  have col : ∀ r ma mb mc md : ℝ, r ^ 2 + ma ^ 2 + mb ^ 2 + mc ^ 2 + md ^ 2 = 1 →
      c * r + x0 * ma + x1 * mb + x2 * mc + x3 * md = 0 →
      140 / 99 * (c * (207 / 250) * ρ * r ^ 2 + |x0| * (ma * (ρ ^ 2 * ma + (c - 14 / 25) * x0 * r)) +
        |x1| * (mb * (ρ ^ 2 * mb + (c - 14 / 25) * x1 * r)) + |x2| * (mc * (ρ ^ 2 * mc + (c - 14 / 25) * x2 * r)) +
        |x3| * (md * (ρ ^ 2 * md + (c - 14 / 25) * x3 * r))) ≤
      ρ ^ 2 * (c * |r| + |x0| * |ma| + |x1| * |mb| + |x2| * |mc| + |x3| * |md|) := by
    intro r ma mb mc md hk hp
    have Z := zs_bound (c * r) (x0 * ma) (x1 * mb) (x2 * mc) (x3 * md) (207 / 250 * ρ * r)
      (ρ ^ 2 * ma + (c - 14 / 25) * x0 * r) (ρ ^ 2 * mb + (c - 14 / 25) * x1 * r)
      (ρ ^ 2 * mc + (c - 14 / 25) * x2 * r) (ρ ^ 2 * md + (c - 14 / 25) * x3 * r) (ρ ^ 2) (by positivity)
      (by linear_combination hp) (nrm r ma mb mc md hk hp)
    rw [t0 r] at Z
    have a0 := abs_term x0 ma (ρ ^ 2 * ma + (c - 14 / 25) * x0 * r)
    have a1 := abs_term x1 mb (ρ ^ 2 * mb + (c - 14 / 25) * x1 * r)
    have a2 := abs_term x2 mc (ρ ^ 2 * mc + (c - 14 / 25) * x2 * r)
    have a3 := abs_term x3 md (ρ ^ 2 * md + (c - 14 / 25) * x3 * r)
    simp only [abs_mul, abs_of_pos hc] at Z a0 a1 a2 a3
    linarith
  have C0 := col r0 m00 m10 m20 m30 k0 p0
  have C1 := col r1 m01 m11 m21 m31 k1 p1
  have C2 := col r2 m02 m12 m22 m32 k2 p2
  have C3 := col r3 m03 m13 m23 m33 k3 p3
  -- summing the pairings over the columns
  set T := |x0| + |x1| + |x2| + |x3| with hT
  set m3 := |x0| * x0 ^ 2 + |x1| * x1 ^ 2 + |x2| * x2 ^ 2 + |x3| * x3 ^ 2 with hm3
  have S : (c * (207 / 250) * ρ * r0 ^ 2 + |x0| * (m00 * (ρ ^ 2 * m00 + (c - 14 / 25) * x0 * r0)) +
        |x1| * (m10 * (ρ ^ 2 * m10 + (c - 14 / 25) * x1 * r0)) + |x2| * (m20 * (ρ ^ 2 * m20 + (c - 14 / 25) * x2 * r0)) +
        |x3| * (m30 * (ρ ^ 2 * m30 + (c - 14 / 25) * x3 * r0))) +
      (c * (207 / 250) * ρ * r1 ^ 2 + |x0| * (m01 * (ρ ^ 2 * m01 + (c - 14 / 25) * x0 * r1)) +
        |x1| * (m11 * (ρ ^ 2 * m11 + (c - 14 / 25) * x1 * r1)) + |x2| * (m21 * (ρ ^ 2 * m21 + (c - 14 / 25) * x2 * r1)) +
        |x3| * (m31 * (ρ ^ 2 * m31 + (c - 14 / 25) * x3 * r1))) +
      (c * (207 / 250) * ρ * r2 ^ 2 + |x0| * (m02 * (ρ ^ 2 * m02 + (c - 14 / 25) * x0 * r2)) +
        |x1| * (m12 * (ρ ^ 2 * m12 + (c - 14 / 25) * x1 * r2)) + |x2| * (m22 * (ρ ^ 2 * m22 + (c - 14 / 25) * x2 * r2)) +
        |x3| * (m32 * (ρ ^ 2 * m32 + (c - 14 / 25) * x3 * r2))) +
      (c * (207 / 250) * ρ * r3 ^ 2 + |x0| * (m03 * (ρ ^ 2 * m03 + (c - 14 / 25) * x0 * r3)) +
        |x1| * (m13 * (ρ ^ 2 * m13 + (c - 14 / 25) * x1 * r3)) + |x2| * (m23 * (ρ ^ 2 * m23 + (c - 14 / 25) * x2 * r3)) +
        |x3| * (m33 * (ρ ^ 2 * m33 + (c - 14 / 25) * x3 * r3))) =
      c * (207 / 250) * ρ * (1 - c ^ 2) + ρ ^ 2 * (T - m3) - c * (c - 14 / 25) * m3 := by
    rw [hT, hm3]
    linear_combination (c * (207 / 250) * ρ) * row1 + ρ ^ 2 * |x0| * w0 + ρ ^ 2 * |x1| * w1 +
      ρ ^ 2 * |x2| * w2 + ρ ^ 2 * |x3| * w3 + (c - 14 / 25) * |x0| * x0 * q0 + (c - 14 / 25) * |x1| * x1 * q1 +
      (c - 14 / 25) * |x2| * x2 * q2 + (c - 14 / 25) * |x3| * x3 * q3
  -- the sphere bounds at the three nodes
  have hX : |x0| ^ 2 + |x1| ^ 2 + |x2| ^ 2 + |x3| ^ 2 = ρ ^ 2 := by
    simp only [sq_abs]; linarith
  have e3 : |x0| * |x0| ^ 2 + |x1| * |x1| ^ 2 + |x2| * |x2| ^ 2 + |x3| * |x3| ^ 2 = m3 := by
    simp only [sq_abs, hm3]
  have hA := scale4 _ _ ρ _ _ _ _ hρ0 (abs_nonneg x0) (abs_nonneg x1) (abs_nonneg x2) (abs_nonneg x3) hX sphA
  have hB := scale4 _ _ ρ _ _ _ _ hρ0 (abs_nonneg x0) (abs_nonneg x1) (abs_nonneg x2) (abs_nonneg x3) hX sphB
  have hC := scale4 _ _ ρ _ _ _ _ hρ0 (abs_nonneg x0) (abs_nonneg x1) (abs_nonneg x2) (abs_nonneg x3) hX sphC
  rw [e3, ← hT] at hA hB hC
  have hF := band_final c ρ T m3 hc hc1 hc2 hρ0 hρ2 hA hB hC
  -- assemble
  have hx : ∀ x : ℝ, |x| * |x| = x ^ 2 := fun x => by rw [abs_mul_abs_self, sq]
  have key : ρ ^ 2 * (c * (2 - c - (|r0| + |r1| + |r2| + |r3|)) +
      |x0| * (2 - |x0| - (|m00| + |m01| + |m02| + |m03|)) +
      |x1| * (2 - |x1| - (|m10| + |m11| + |m12| + |m13|)) +
      |x2| * (2 - |x2| - (|m20| + |m21| + |m22| + |m23|)) +
      |x3| * (2 - |x3| - (|m30| + |m31| + |m32| + |m33|)) - 1) ≤ 0 := by
    have g1 : ρ ^ 2 * (|x0| * |x0| + |x1| * |x1| + |x2| * |x2| + |x3| * |x3| + c ^ 2) = ρ ^ 2 := by
      rw [hx, hx, hx, hx]; linear_combination ρ ^ 2 * col1
    have g2 : c * (207 / 250) * ρ * (1 - c ^ 2) = c * (207 / 250) * ρ ^ 3 := by rw [← hρ2]; ring
    linarith
  by_contra h
  push Not at h
  have := mul_pos (pow_pos hρ0 2) (sub_pos.2 h)
  linarith

/-! ## Away from the axes: every `c² ≤ 9/20` -/

/-- For two columns `a ⊥ b` with `‖b‖ = 1`: `(140/99) Σᵢ |aᵢ| bᵢ² ≤ Σᵢ |aᵢ| |bᵢ|` (`zs_bound` with `zᵢ = aᵢbᵢ`,
`vᵢ = bᵢ`). -/
theorem pair5 (a0 a1 a2 a3 a4 b0 b1 b2 b3 b4 : ℝ) (hab : a0 * b0 + a1 * b1 + a2 * b2 + a3 * b3 + a4 * b4 = 0)
    (hb : b0 ^ 2 + b1 ^ 2 + b2 ^ 2 + b3 ^ 2 + b4 ^ 2 = 1) :
    140 / 99 * (|a0| * b0 ^ 2 + |a1| * b1 ^ 2 + |a2| * b2 ^ 2 + |a3| * b3 ^ 2 + |a4| * b4 ^ 2) ≤
      |a0| * |b0| + |a1| * |b1| + |a2| * |b2| + |a3| * |b3| + |a4| * |b4| := by
  have h := zs_bound (a0 * b0) (a1 * b1) (a2 * b2) (a3 * b3) (a4 * b4) b0 b1 b2 b3 b4 1 zero_le_one hab
    (by rw [one_pow]; linarith)
  have e : ∀ x y : ℝ, |x * y| * |y| = |x| * y ^ 2 := fun x y => by
    rw [abs_mul, mul_assoc, abs_mul_abs_self, sq]
  rw [e, e, e, e, e] at h
  simp only [abs_mul, one_mul] at h
  linarith

set_option maxHeartbeats 2000000 in
/-- **Away from the axes.** If every entry of the column `a` has square at most `9/20`, then `F ≤ 1`. -/
theorem far5_core (a0 a1 a2 a3 a4 b0 b1 b2 b3 b4 c0 c1 c2 c3 c4 d0 d1 d2 d3 d4 e0 e1 e2 e3 e4 : ℝ)
    (ha : a0 ^ 2 + a1 ^ 2 + a2 ^ 2 + a3 ^ 2 + a4 ^ 2 = 1)
    (hb : b0 ^ 2 + b1 ^ 2 + b2 ^ 2 + b3 ^ 2 + b4 ^ 2 = 1)
    (hc : c0 ^ 2 + c1 ^ 2 + c2 ^ 2 + c3 ^ 2 + c4 ^ 2 = 1)
    (hd : d0 ^ 2 + d1 ^ 2 + d2 ^ 2 + d3 ^ 2 + d4 ^ 2 = 1)
    (he : e0 ^ 2 + e1 ^ 2 + e2 ^ 2 + e3 ^ 2 + e4 ^ 2 = 1)
    (hab : a0 * b0 + a1 * b1 + a2 * b2 + a3 * b3 + a4 * b4 = 0)
    (hac : a0 * c0 + a1 * c1 + a2 * c2 + a3 * c3 + a4 * c4 = 0)
    (had : a0 * d0 + a1 * d1 + a2 * d2 + a3 * d3 + a4 * d4 = 0)
    (hae : a0 * e0 + a1 * e1 + a2 * e2 + a3 * e3 + a4 * e4 = 0)
    (r0 : a0 ^ 2 + b0 ^ 2 + c0 ^ 2 + d0 ^ 2 + e0 ^ 2 = 1)
    (r1 : a1 ^ 2 + b1 ^ 2 + c1 ^ 2 + d1 ^ 2 + e1 ^ 2 = 1)
    (r2 : a2 ^ 2 + b2 ^ 2 + c2 ^ 2 + d2 ^ 2 + e2 ^ 2 = 1)
    (r3 : a3 ^ 2 + b3 ^ 2 + c3 ^ 2 + d3 ^ 2 + e3 ^ 2 = 1)
    (r4 : a4 ^ 2 + b4 ^ 2 + c4 ^ 2 + d4 ^ 2 + e4 ^ 2 = 1)
    (f0 : a0 ^ 2 ≤ 9 / 20) (f1 : a1 ^ 2 ≤ 9 / 20) (f2 : a2 ^ 2 ≤ 9 / 20) (f3 : a3 ^ 2 ≤ 9 / 20) (f4 : a4 ^ 2 ≤ 9 / 20) :
    |a0| * (2 - (|a0| + |b0| + |c0| + |d0| + |e0|)) +
      |a1| * (2 - (|a1| + |b1| + |c1| + |d1| + |e1|)) +
      |a2| * (2 - (|a2| + |b2| + |c2| + |d2| + |e2|)) +
      |a3| * (2 - (|a3| + |b3| + |c3| + |d3| + |e3|)) +
      |a4| * (2 - (|a4| + |b4| + |c4| + |d4| + |e4|)) ≤ 1 := by
  have pb := pair5 a0 a1 a2 a3 a4 b0 b1 b2 b3 b4 hab hb
  have pc := pair5 a0 a1 a2 a3 a4 c0 c1 c2 c3 c4 hac hc
  have pd := pair5 a0 a1 a2 a3 a4 d0 d1 d2 d3 d4 had hd
  have pe := pair5 a0 a1 a2 a3 a4 e0 e1 e2 e3 e4 hae he
  have hp := cs5 |a0| |a1| |a2| |a3| |a4| (abs_nonneg _) (abs_nonneg _) (abs_nonneg _) (abs_nonneg _) (abs_nonneg _) (by rw [sq_abs]; exact f0) (by rw [sq_abs]; exact f1) (by rw [sq_abs]; exact f2) (by rw [sq_abs]; exact f3) (by rw [sq_abs]; exact f4) (by simp only [sq_abs]; exact ha)
  have w : ∀ (x b c d e : ℝ), x ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 + e ^ 2 = 1 →
      |x| * b ^ 2 + |x| * c ^ 2 + |x| * d ^ 2 + |x| * e ^ 2 = |x| - |x| ^ 3 := fun x b c d e h => by
    have : |x| ^ 3 = |x| * x ^ 2 := by rw [pow_succ, sq_abs, mul_comm]
    rw [this]; linear_combination |x| * h
  have w0 := w a0 b0 c0 d0 e0 r0
  have w1 := w a1 b1 c1 d1 e1 r1
  have w2 := w a2 b2 c2 d2 e2 r2
  have w3 := w a3 b3 c3 d3 e3 r3
  have w4 := w a4 b4 c4 d4 e4 r4
  have s0 : |a0| * |a0| = a0 ^ 2 := by rw [abs_mul_abs_self, sq]
  have s1 : |a1| * |a1| = a1 ^ 2 := by rw [abs_mul_abs_self, sq]
  have s2 : |a2| * |a2| = a2 ^ 2 := by rw [abs_mul_abs_self, sq]
  have s3 : |a3| * |a3| = a3 ^ 2 := by rw [abs_mul_abs_self, sq]
  have s4 : |a4| * |a4| = a4 ^ 2 := by rw [abs_mul_abs_self, sq]
  linarith

theorem far5 (R : Matrix (Fin 5) (Fin 5) ℝ) (hR : R * Rᵀ = 1) (j : Fin 5) (hf : ∀ i, R i j ^ 2 ≤ 9 / 20) :
    Fcol R j ≤ 1 := by
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have row : ∀ i, R i 0 ^ 2 + R i 1 ^ 2 + R i 2 ^ 2 + R i 3 ^ 2 + R i 4 ^ 2 = 1 := fun i => by
    have h := congrFun (congrFun hR i) i
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_five, Matrix.one_apply_eq] at h
    linear_combination h
  have col : ∀ a b, R 0 a * R 0 b + R 1 a * R 1 b + R 2 a * R 2 b + R 3 a * R 3 b + R 4 a * R 4 b =
      if a = b then 1 else 0 := fun a b => by
    have h := congrFun (congrFun hR' a) b
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_five, Matrix.one_apply] at h
    exact h
  have c00 := col 0 0
  have c01 := col 0 1
  have c02 := col 0 2
  have c03 := col 0 3
  have c04 := col 0 4
  have c11 := col 1 1
  have c12 := col 1 2
  have c13 := col 1 3
  have c14 := col 1 4
  have c22 := col 2 2
  have c23 := col 2 3
  have c24 := col 2 4
  have c33 := col 3 3
  have c34 := col 3 4
  have c44 := col 4 4
  simp only [Fin.reduceEq, ↓reduceIte] at c00 c01 c02 c03 c04 c11 c12 c13 c14 c22 c23 c24 c33 c34 c44
  have r0 := row 0
  have r1 := row 1
  have r2 := row 2
  have r3 := row 3
  have r4 := row 4
  have hf0 := hf 0
  have hf1 := hf 1
  have hf2 := hf 2
  have hf3 := hf 3
  have hf4 := hf 4
  simp only [Fcol, rowL1, l1, Fin.sum_univ_five]
  fin_cases j
  · have := far5_core (R 0 0) (R 1 0) (R 2 0) (R 3 0) (R 4 0) (R 0 1) (R 1 1) (R 2 1) (R 3 1) (R 4 1) (R 0 2) (R 1 2) (R 2 2) (R 3 2) (R 4 2) (R 0 3) (R 1 3) (R 2 3) (R 3 3) (R 4 3) (R 0 4) (R 1 4) (R 2 4) (R 3 4) (R 4 4)
      (by linear_combination c00) (by linear_combination c11) (by linear_combination c22) (by linear_combination c33) (by linear_combination c44)
      (by linear_combination c01) (by linear_combination c02) (by linear_combination c03) (by linear_combination c04)
      (by linear_combination r0) (by linear_combination r1) (by linear_combination r2) (by linear_combination r3) (by linear_combination r4)
      hf0 hf1 hf2 hf3 hf4
    try simp only [Fin.zero_eta, Fin.mk_one, Fin.reduceFinMk, Fin.isValue]
    linarith
  · have := far5_core (R 0 1) (R 1 1) (R 2 1) (R 3 1) (R 4 1) (R 0 0) (R 1 0) (R 2 0) (R 3 0) (R 4 0) (R 0 2) (R 1 2) (R 2 2) (R 3 2) (R 4 2) (R 0 3) (R 1 3) (R 2 3) (R 3 3) (R 4 3) (R 0 4) (R 1 4) (R 2 4) (R 3 4) (R 4 4)
      (by linear_combination c11) (by linear_combination c00) (by linear_combination c22) (by linear_combination c33) (by linear_combination c44)
      (by linear_combination c01) (by linear_combination c12) (by linear_combination c13) (by linear_combination c14)
      (by linear_combination r0) (by linear_combination r1) (by linear_combination r2) (by linear_combination r3) (by linear_combination r4)
      hf0 hf1 hf2 hf3 hf4
    try simp only [Fin.zero_eta, Fin.mk_one, Fin.reduceFinMk, Fin.isValue]
    linarith
  · have := far5_core (R 0 2) (R 1 2) (R 2 2) (R 3 2) (R 4 2) (R 0 0) (R 1 0) (R 2 0) (R 3 0) (R 4 0) (R 0 1) (R 1 1) (R 2 1) (R 3 1) (R 4 1) (R 0 3) (R 1 3) (R 2 3) (R 3 3) (R 4 3) (R 0 4) (R 1 4) (R 2 4) (R 3 4) (R 4 4)
      (by linear_combination c22) (by linear_combination c00) (by linear_combination c11) (by linear_combination c33) (by linear_combination c44)
      (by linear_combination c02) (by linear_combination c12) (by linear_combination c23) (by linear_combination c24)
      (by linear_combination r0) (by linear_combination r1) (by linear_combination r2) (by linear_combination r3) (by linear_combination r4)
      hf0 hf1 hf2 hf3 hf4
    try simp only [Fin.zero_eta, Fin.mk_one, Fin.reduceFinMk, Fin.isValue]
    linarith
  · have := far5_core (R 0 3) (R 1 3) (R 2 3) (R 3 3) (R 4 3) (R 0 0) (R 1 0) (R 2 0) (R 3 0) (R 4 0) (R 0 1) (R 1 1) (R 2 1) (R 3 1) (R 4 1) (R 0 2) (R 1 2) (R 2 2) (R 3 2) (R 4 2) (R 0 4) (R 1 4) (R 2 4) (R 3 4) (R 4 4)
      (by linear_combination c33) (by linear_combination c00) (by linear_combination c11) (by linear_combination c22) (by linear_combination c44)
      (by linear_combination c03) (by linear_combination c13) (by linear_combination c23) (by linear_combination c34)
      (by linear_combination r0) (by linear_combination r1) (by linear_combination r2) (by linear_combination r3) (by linear_combination r4)
      hf0 hf1 hf2 hf3 hf4
    try simp only [Fin.zero_eta, Fin.mk_one, Fin.reduceFinMk, Fin.isValue]
    linarith
  · have := far5_core (R 0 4) (R 1 4) (R 2 4) (R 3 4) (R 4 4) (R 0 0) (R 1 0) (R 2 0) (R 3 0) (R 4 0) (R 0 1) (R 1 1) (R 2 1) (R 3 1) (R 4 1) (R 0 2) (R 1 2) (R 2 2) (R 3 2) (R 4 2) (R 0 3) (R 1 3) (R 2 3) (R 3 3) (R 4 3)
      (by linear_combination c44) (by linear_combination c00) (by linear_combination c11) (by linear_combination c22) (by linear_combination c33)
      (by linear_combination c04) (by linear_combination c14) (by linear_combination c24) (by linear_combination c34)
      (by linear_combination r0) (by linear_combination r1) (by linear_combination r2) (by linear_combination r3) (by linear_combination r4)
      hf0 hf1 hf2 hf3 hf4
    try simp only [Fin.zero_eta, Fin.mk_one, Fin.reduceFinMk, Fin.isValue]
    linarith

/-! ## The band for a matrix -/

set_option maxHeartbeats 2000000 in
theorem band_block {c : ℝ} {r x : Fin 4 → ℝ} {M : Matrix (Fin 4) (Fin 4) ℝ} (h : BlockOrth c r x M)
    (hk : ∀ k, r k ^ 2 + ∑ i, M i k ^ 2 = 1) (hq : ∀ i, c * x i + ∑ k, r k * M i k = 0)
    (hc : 0 < c) (hc1 : 9 / 20 ≤ c ^ 2) (hc2 : c ^ 2 ≤ 3 / 4) : F1 c r x M ≤ 1 := by
  have col1 := h.col1
  have row1 := h.row1
  simp only [sq2, Fin.sum_univ_four] at col1 row1
  have p0 := h.col1_perp 0; have p1 := h.col1_perp 1; have p2 := h.col1_perp 2; have p3 := h.col1_perp 3
  have w0 := h.rows 0 0; have w1 := h.rows 1 1; have w2 := h.rows 2 2; have w3 := h.rows 3 3
  have k0 := hk 0; have k1 := hk 1; have k2 := hk 2; have k3 := hk 3
  have q0 := hq 0; have q1 := hq 1; have q2 := hq 2; have q3 := hq 3
  simp only [Fin.sum_univ_four, if_pos rfl] at p0 p1 p2 p3 w0 w1 w2 w3 k0 k1 k2 k3 q0 q1 q2 q3
  have := band_core c (r 0) (r 1) (r 2) (r 3) (x 0) (x 1) (x 2) (x 3) (M 0 0) (M 0 1) (M 0 2) (M 0 3)
    (M 1 0) (M 1 1) (M 1 2) (M 1 3) (M 2 0) (M 2 1) (M 2 2) (M 2 3) (M 3 0) (M 3 1) (M 3 2) (M 3 3)
    hc hc1 hc2 (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith)
    (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith)
    (by linarith) (by linarith) (by linarith) (by linarith) (by linarith)
  simp only [F1, l1, rowL1, Fin.sum_univ_four, abs_of_pos hc]
  linarith

/-- **The band.** If some entry of column `j` has square between `9/20` and `3/4`, then `F_j ≤ 1`. -/
theorem band5 (R : Matrix (Fin 5) (Fin 5) ℝ) (hR : R * Rᵀ = 1) (i₀ j : Fin 5)
    (hc1 : 9 / 20 ≤ R i₀ j ^ 2) (hc2 : R i₀ j ^ 2 ≤ 3 / 4) : Fcol R j ≤ 1 := by
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have hB := block_orth (m := 4) R hR hR' i₀ j
  rw [Fcol_eq_F1 (m := 4) R i₀ j]
  have hk : ∀ k, R i₀ (j.succAbove k) ^ 2 + ∑ i, R (i₀.succAbove i) (j.succAbove k) ^ 2 = 1 := fun k => by
    have h := sum_cols R hR' (j.succAbove k) (j.succAbove k)
    rw [Fin.sum_univ_succAbove _ i₀, if_pos rfl] at h
    simp only [pow_two]; exact h
  have hq : ∀ i, R i₀ j * R (i₀.succAbove i) j +
      ∑ k, R i₀ (j.succAbove k) * R (i₀.succAbove i) (j.succAbove k) = 0 := fun i => by
    have h := sum_rows R hR i₀ (i₀.succAbove i)
    rw [Fin.sum_univ_succAbove _ j, if_neg (Fin.succAbove_ne i₀ i).symm] at h
    exact h
  rcases lt_or_gt_of_ne (show R i₀ j ≠ 0 by rintro h; rw [h] at hc1; norm_num at hc1) with hneg | hpos
  · -- flip the sign of the corner and of the rest of its row
    have hB' : BlockOrth (-R i₀ j) (-fun k => R i₀ (j.succAbove k)) (fun i => R (i₀.succAbove i) j)
        (fun i k => R (i₀.succAbove i) (j.succAbove k)) :=
      { col1 := by rw [neg_sq]; exact hB.col1
        row1 := by
          have := hB.row1
          simp only [sq2, Pi.neg_apply, neg_sq] at this ⊢
          exact this
        col1_perp := fun k => by
          have := hB.col1_perp k
          simp only [Pi.neg_apply]
          linarith
        rows := hB.rows }
    have := band_block hB' (fun k => by simp only [Pi.neg_apply, neg_sq]; exact hk k)
      (fun i => by
        have := hq i
        simp only [Pi.neg_apply, neg_mul, Finset.sum_neg_distrib]
        linarith)
      (by linarith) (by rw [neg_sq]; exact hc1) (by rw [neg_sq]; exact hc2)
    simpa [F1, l1, abs_neg] using this
  · exact band_block hB hk hq hpos hc1 hc2

/-! ## Near an axis -/

/-- **Near an axis (Hosono).** If some entry of column `j` has square at least `3/4`, then `F_j ≤ 1`. -/
theorem near5 (R : Matrix (Fin 5) (Fin 5) ℝ) (hR : R * Rᵀ = 1) (i₀ j : Fin 5) (hc : 3 / 4 ≤ R i₀ j ^ 2) :
    Fcol R j ≤ 1 := by
  have hR' : Rᵀ * R = 1 := mul_eq_one_comm.mp hR
  have hB := block_orth (m := 4) R hR hR' i₀ j
  rw [Fcol_eq_F1 (m := 4) R i₀ j]
  have hs : ((4 : ℕ) : ℝ) * sq2 (fun i => R (i₀.succAbove i) j) ≤ 1 := by
    have := hB.col1; push_cast; linarith
  rcases lt_or_gt_of_ne (show R i₀ j ≠ 0 by rintro h; rw [h] at hc; norm_num at hc) with hneg | hpos
  · have hB' : BlockOrth (-R i₀ j) (-fun k => R i₀ (j.succAbove k)) (fun i => R (i₀.succAbove i) j)
        (fun i k => R (i₀.succAbove i) (j.succAbove k)) :=
      { col1 := by rw [neg_sq]; exact hB.col1
        row1 := by
          have := hB.row1
          simp only [sq2, Pi.neg_apply, neg_sq] at this ⊢
          exact this
        col1_perp := fun k => by
          have := hB.col1_perp k
          simp only [Pi.neg_apply]
          linarith
        rows := hB.rows }
    have := near_region (m := 4) (by norm_num) lemmaF4 hB' (by linarith) hs
    simpa [F1, l1, abs_neg] using this
  · exact near_region (m := 4) (by norm_num) lemmaF4 hB hpos hs

/-! ## Lemma F in dimension 5 -/

/-- **Lemma F in dimension 5.** For every orthogonal 5×5 matrix and every column `j`,
`Σᵢ |Rᵢⱼ| (2 - ‖row i‖₁) ≤ 1`. -/
theorem lemmaF5 : LemmaF 5 := by
  intro R hR j
  by_cases h : ∃ i, 3 / 4 ≤ R i j ^ 2
  · obtain ⟨i₀, hi⟩ := h
    exact near5 R hR i₀ j hi
  · push Not at h
    by_cases h' : ∃ i, 9 / 20 ≤ R i j ^ 2
    · obtain ⟨i₀, hi⟩ := h'
      exact band5 R hR i₀ j hi (h i₀).le
    · push Not at h'
      exact far5 R hR j fun i => (h' i).le

end PackingOptimality.LemmaF5
