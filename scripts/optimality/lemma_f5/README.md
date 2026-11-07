# Lemma F in dimension 5: certificate search and Lean generation

Lemma F (`Σᵢ |Rᵢⱼ| (2 − ‖row i‖₁) ≤ 1` for orthogonal R) in dimension 5 gives the cube centre lemma and the optimal
side 2 for 2 ≤ n ≤ 32 five-cubes in a five-cube. The Lean proof is `lean-optimality/PackingOptimality/LemmaF5.lean`
(hand-written) and `LemmaF5Sphere.lean` (generated here). See `docs/OPTIMALITY.md`, section 1.

**Sphere bounds.** The band and the far region reduce to bounds `Σᵢ (sᵢ³ + λ sᵢ) ≤ U` on the nonnegative unit sphere:
four coordinates at λ = 33/50, 147/200, 161/200, and five coordinates with `sᵢ² ≤ 9/20` at λ = 29/70.
A certificate fixes the largest coordinate `s₀` and cuts the ranges of `s₀` and of the others into intervals. On
each interval it gives a line `s³ + λ s ≤ α + β s²` with an exact factorization. Every choice of intervals is then a
linear program in the `sᵢ²`: `Σ sᵢ² = 1`, `sᵢ² ≤ s₀²`, interval bounds. Its maximum must be at most U.

| file | role |
|---|---|
| `gensphere.py` | line families (tangent `(s − t)²(u − s)`, chord `(s − a)(b − s)(s − u)`), exact rationals |
| `optsphere2.py` | random search over partitions; one LP per case (scipy HiGHS); writes a pickle |
| `certificates.json` | the chosen partitions and lines (exact), with their LP bounds |
| `genlean2.py`, `genlean.py` | Lean emitter: line lemmas, case lemmas, the case split, the tournament |
| `band_final.lean` | the λ interpolation and the two one-variable inequalities in c (from `seg.py`) |
| `gen_far5.py` | the far-region boilerplate of `LemmaF5.lean` (`pair5`, `far5_core`, `far5`) |
| `ident.py` | sympy check of the two polynomial identities used in `band_core` |
| `build.py` | regenerates `LemmaF5Sphere.lean` from `certificates.json` |

```
python3 scripts/optimality/lemma_f5/build.py
cd lean-optimality && lake build PackingOptimality.Penteracts
```

The search only proposes certificates; Lean checks every line lemma and every case.
