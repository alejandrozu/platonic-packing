# Which records are optimal?

_13 November 2026._ A record gives an upper bound: its packing fits in a container of scale s. It is **optimal**
when no packing of the same n pieces fits in a smaller container. This file tracks which low-n records are
proven optimal in Lean, which are proven elsewhere with computer assistance, and which have strong numerical
evidence.
Machine-readable list: [`optimality.json`](optimality.json). Lean proofs: [`lean-optimality/`](../lean-optimality).

## 1. Proven in Lean

| Record | Optimal side | Argument | Lean theorem |
|---|---|---|---|
| 8 cubes in a cube (`cubincub_n08`) | 2 | volume bound + 2×2×2 grid | `cubincub_n08` |
| 27 cubes in a cube (`cubincub_n27`) | 3 | volume bound + 3×3×3 grid | `cubincub_n27` |
| 64 cubes in a cube (`cubincub_n64`) | 4 | volume bound + 4×4×4 grid | `cubincub_n64` |
| 16 tesseracts in a tesseract (`c8inc8_n16`) | 2 | volume bound + grid | `c8inc8_n16` |
| 32 5-cubes in a 5-cube (`hc5inhc5_n32`) | 2 | volume bound + grid | `hc5inhc5_n32` |
| 8 triangular prisms in a triangular prism (`pr3inpr3_n08`) | 2 | volume bound + tiling | `pr3inpr3_n08` |
| 27 triangular prisms in a triangular prism (`pr3inpr3_n27`) | 3 | volume bound + tiling | `pr3inpr3_n27` |
| 64 triangular prisms in a triangular prism (`pr3inpr3_n64`) | 4 | volume bound + tiling | `pr3inpr3_n64` |
| 2 cubes in a cube (`cubincub_n02`) | 2 | cube centre lemma (d = 3) + grid | `cubincub_n02` |
| 3 cubes in a cube (`cubincub_n03`) | 2 | cube centre lemma (d = 3) + grid | `cubincub_n03` |
| 4 cubes in a cube (`cubincub_n04`) | 2 | cube centre lemma (d = 3) + grid | `cubincub_n04` |
| 5 cubes in a cube (`cubincub_n05`) | 2 | cube centre lemma (d = 3) + grid | `cubincub_n05` |
| 6 cubes in a cube (`cubincub_n06`) | 2 | cube centre lemma (d = 3) + grid | `cubincub_n06` |
| 7 cubes in a cube (`cubincub_n07`) | 2 | cube centre lemma (d = 3) + grid | `cubincub_n07` |
| 2 tesseracts in a tesseract (`c8inc8_n02`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n02` |
| 3 tesseracts in a tesseract (`c8inc8_n03`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n03` |
| 4 tesseracts in a tesseract (`c8inc8_n04`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n04` |
| 5 tesseracts in a tesseract (`c8inc8_n05`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n05` |
| 6 tesseracts in a tesseract (`c8inc8_n06`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n06` |
| 7 tesseracts in a tesseract (`c8inc8_n07`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n07` |
| 8 tesseracts in a tesseract (`c8inc8_n08`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n08` |
| 9 tesseracts in a tesseract (`c8inc8_n09`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n09` |
| 10 tesseracts in a tesseract (`c8inc8_n10`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n10` |
| 11 tesseracts in a tesseract (`c8inc8_n11`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n11` |
| 12 tesseracts in a tesseract (`c8inc8_n12`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n12` |
| 13 tesseracts in a tesseract (`c8inc8_n13`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n13` |
| 14 tesseracts in a tesseract (`c8inc8_n14`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n14` |
| 15 tesseracts in a tesseract (`c8inc8_n15`) | 2 | cube centre lemma (d = 4) + grid | `c8inc8_n15` |
| 2 5-cubes in a 5-cube (`hc5inhc5_n02`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n02` |
| 3 5-cubes in a 5-cube (`hc5inhc5_n03`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n03` |
| 4 5-cubes in a 5-cube (`hc5inhc5_n04`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n04` |
| 5 5-cubes in a 5-cube (`hc5inhc5_n05`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n05` |
| 6 5-cubes in a 5-cube (`hc5inhc5_n06`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n06` |
| 7 5-cubes in a 5-cube (`hc5inhc5_n07`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n07` |
| 8 5-cubes in a 5-cube (`hc5inhc5_n08`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n08` |
| 9 5-cubes in a 5-cube (`hc5inhc5_n09`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n09` |
| 10 5-cubes in a 5-cube (`hc5inhc5_n10`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n10` |
| 11 5-cubes in a 5-cube (`hc5inhc5_n11`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n11` |
| 12 5-cubes in a 5-cube (`hc5inhc5_n12`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n12` |
| 13 5-cubes in a 5-cube (`hc5inhc5_n13`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n13` |
| 14 5-cubes in a 5-cube (`hc5inhc5_n14`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n14` |
| 15 5-cubes in a 5-cube (`hc5inhc5_n15`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n15` |
| 16 5-cubes in a 5-cube (`hc5inhc5_n16`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n16` |
| 17 5-cubes in a 5-cube (`hc5inhc5_n17`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n17` |
| 18 5-cubes in a 5-cube (`hc5inhc5_n18`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n18` |
| 19 5-cubes in a 5-cube (`hc5inhc5_n19`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n19` |
| 20 5-cubes in a 5-cube (`hc5inhc5_n20`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n20` |
| 21 5-cubes in a 5-cube (`hc5inhc5_n21`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n21` |
| 22 5-cubes in a 5-cube (`hc5inhc5_n22`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n22` |
| 23 5-cubes in a 5-cube (`hc5inhc5_n23`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n23` |
| 24 5-cubes in a 5-cube (`hc5inhc5_n24`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n24` |
| 25 5-cubes in a 5-cube (`hc5inhc5_n25`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n25` |
| 26 5-cubes in a 5-cube (`hc5inhc5_n26`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n26` |
| 27 5-cubes in a 5-cube (`hc5inhc5_n27`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n27` |
| 28 5-cubes in a 5-cube (`hc5inhc5_n28`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n28` |
| 29 5-cubes in a 5-cube (`hc5inhc5_n29`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n29` |
| 30 5-cubes in a 5-cube (`hc5inhc5_n30`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n30` |
| 31 5-cubes in a 5-cube (`hc5inhc5_n31`) | 2 | cube centre lemma (d = 5) + grid | `hc5inhc5_n31` |

The five records with k^d cubes are instances of one theorem, `cubes_in_cube_optimal`: in every dimension d ≥ 1, the smallest cube
holding k^d unit cubes has side exactly k. The proof works for any rigid motions, reflections included, and only
requires disjoint interiors, so touching is allowed. Its lower bound is the general volume theorem
`card_mul_volume_le`, for congruent convex bodies in any finite-dimensional Euclidean space; its upper bound is
the grid. The prism results are instances of `prisms_in_prism_optimal`. The scale-k prism is tiled by k³ unit
prisms: k layers of k² triangles, upward ones placed as translates and downward ones as point reflections.
Distinct tiles have disjoint interiors because an interior point determines its tile. Every theorem depends only
on Lean's standard axioms (`Axioms.lean`, checked in CI).

**Cubes in a cube, n = 2–7 (`CubeCentre.lean`).** Side 2 is optimal for every n from 2 to 8. The upper bound is
the 2×2×2 grid with cubes removed. The lower bound is the **cube centre lemma in dimension 3** (`centre3`): a unit
cube placed by any rigid motion inside a cube of side s < 2 contains the centre (s/2, s/2, s/2) in its interior.
So any two such cubes share an interior point, and no two fit (the common-point lemma).

The lemma reduces to a matrix inequality, `core`. For an orthogonal matrix with columns a, b, c:

  2 (|a₀| + |a₁| + |a₂| − 1) ≤ Σᵢ |aᵢ| (|bᵢ| + |cᵢ|).

The proof has two steps.

1. **A zero entry.** If one entry of b or c is zero, the inequality is an identity. The difference of the two
   sides is 2(1 − P)(1 − Q) + 2P(1 − S)(1 − T), where P, Q, S, T ∈ [0, 1] are absolute values of remaining
   entries. This is `reduced`, and `zero_case` covers all six positions by symmetry.
2. **The general case.** Rotate (b, c) in its own plane by a unit vector (p, q). The right side is continuous on
   the unit circle, so it has a minimiser.
   - If the minimiser has a zero entry, step 1 applies.
   - If not, no entry changes sign for small t. The rotated neighbours (p ∓ tq, q ± tp)/√(1 + t²) then have
     values that average to the minimum divided by √(1 + t²). One of them is below the minimum, which is
     impossible.

The Lean proof uses no computer search. Hiroaki Hosono had proved the same inequality ("Lemma F") with
computer assistance; see section 2.

The geometric step (`centre3`) takes an image vertex in each coordinate direction. This shows the image centre
is within (s − wᵢ)/2 of s/2 in coordinate i, where wᵢ is the cube's width along that axis. Pulled back through
the isometry and combined with `core`, the container's centre lies strictly inside the unit cube.

**Tesseracts in a tesseract, n = 2–15 (`Tesseracts.lean`).** Side 2 is optimal for every n from 2 to 16, by the
same plateau argument with the **cube centre lemma in dimension 4** (`centre4`). The result s₄(2) = 2 is
Hiroaki Hosono's; his proof is computer-assisted away from the axes. The Lean proof here has no computer search.
The lemma follows from Lemma F in dimension 4 (`LemmaF4.lemmaF4`), whose two regions are proved as follows. Fix
a column j and write xᵢ = |Rᵢⱼ| and S = Σᵢ xᵢ.

1. **Near an axis (some xᵢ² ≥ 2/3): Hosono's argument, ported unchanged.** A polar-decomposition step reduces
   F_j ≤ 1 to Lemma F in dimension 3. It is his Lean file (`NearAxis.lean`, MIT, credited), with our
   `CubeCentre.core` discharging its 3D hypothesis (`lemmaF3`).
2. **Elsewhere (every xᵢ² ≤ 2/3): new, elementary.**
   - **Zero-sum bound.** For each other column k, the vector zᵢ = RᵢⱼRᵢₖ has zero sum, so ‖z‖₁ ≥ √2‖z‖₂.
   - **Cauchy–Schwarz.** It gives ‖z‖₂ ≥ Σᵢ xᵢRᵢₖ² (`pair_bound`).
   - **Summing over k ≠ j** with the row norms gives F_j ≤ 2S − 1 − √2 Σᵢ xᵢ(1 − xᵢ²).
   - **The remaining inequality** is Σᵢ φ(xᵢ) ≥ −2, with φ(t) = √2(t − t³) − 2t, Σxᵢ² = 1 and xᵢ² ≤ 2/3. Each
     coordinate is small (xᵢ² ≤ 2/5), middle (2/5 to 3/5) or big (≥ 3/5). On each range φ lies above an
     explicit line in t², a one-variable cubic inequality with an exact certificate (`phi_small`, `phi_large`,
     `phi_large2`). At most two coordinates exceed 2/5, and `linarith` closes all 81 combinations
     (`far_poly`). Lean uses 140/99 ≤ √2. The inequality's true minimum is ≈ 0.009 above −2, at
     p = xᵢ² = (2/3, 1/9, 1/9, 1/9); the certificates leave about 0.0008 of slack each.

The final step, from Lemma F to the centre lemma, is proved once for every dimension
(`CentreGeneral.centre_of_lemmaF`).

Hosono's spectral bound replaces √2 Σᵢ xᵢ(1 − xᵢ²) by √2 Tr √(diag(p) − ppᵀ). That needs matrix square roots, and
it is what he extends to 5D. The elementary bound is weaker: in 5D it holds only while every pᵢ ≤ 1/2.

**5-cubes in a 5-cube, n = 2–31 (`Penteracts.lean`, 7 Nov 2026).** Side 2 is optimal for every n from 2 to 32.
The cube centre lemma in dimension 5 (`centre5`) follows from Lemma F in dimension 5 (`LemmaF5.lemmaF5`). Hosono
proved s₅(2) = 2 first, with a spectral certificate of 21,502 simplices. The Lean proof splits a column by its
entry c of largest square (any entry in the band works):

1. **Near an axis (c² ≥ 3/4): Hosono's polar step** with m = 4, which needs Lemma F in 4D (now proven).
2. **The band (9/20 ≤ c² ≤ 3/4): new.** Write R = [c r; x M] and ρ = ‖x‖₂. Each other column k gives a zero-sum
   vector ζ = (c rₖ, xᵢMᵢₖ), so ‖ζ‖₁ ≥ √2‖ζ‖₂ ≥ √2⟨|ζ|, |w|⟩ for every weight with ‖w‖₂ ≤ 1. The far region uses the
   column itself as weight. Here the column is first turned in the plane of e₁ and x, so that x points in a fixed
   direction at angle ψ ≈ 56° from e₁ (cos ψ = 14/25, sin ψ = 207/250):
   w = (sin ψ · rₖ/ρ, Mᵢₖ + (c − cos ψ) xᵢ rₖ/ρ²). Then ‖w‖₂² = 1 − (1 − cos²ψ − sin²ψ) rₖ²/ρ² ≤ 1. Summing over k
   with the orthonormal rows reduces F ≤ 1 to two facts. The first is λT + m₃/ρ² ≤ ρ U(λ), where T = Σ|xᵢ|,
   m₃ = Σ|xᵢ|³, λ = (2 − √2)/(√2 (1 − c cos ψ)) ∈ [0.66, 0.81], and U(λ) bounds Σ(sᵢ³ + λsᵢ) on the unit sphere in
   R⁴. U is checked at λ = 33/50, 147/200 and 161/200 and interpolated linearly in λ, which is valid because the
   sum is linear in λ. The second is a one-variable inequality in c (`band_final`; smallest slack about 0.002, at
   c² = 3/4).
3. **Far from the axes (every c² ≤ 9/20): the 4D argument with five rows**, with the sphere bound
   Σ(sᵢ³ + (29/70) sᵢ) ≤ 99/70 under sᵢ² ≤ 9/20 (true maximum about 1.4061).

The four sphere bounds are in `LemmaF5Sphere.lean`. A tournament reduces each to its largest coordinate. Each
coordinate range is cut into intervals, and on each interval s³ + λs ≤ α + βs² holds by an exact factorization:
a tangent (s − t)²(u − s) or a chord (s − a)(b − s)(s − u). For every choice of intervals, `linarith` closes the
resulting linear bound in the sᵢ² (1,174 cases in all). The partitions were found by a small search over exact
linear programs (`scripts/optimality/lemma_f5/`). Lean checks every case, and no other computer search is used.

### New optimality results (not previously proven by anyone, as far as we found)

| Record | Optimal side | Lean theorem |
|---|---|---|
| 2 octahedra in a cube (`octincub_n02`) | √2 | `octincub_n02` (`OctInCube.lean`) |
| 2 tetrahedra in a cube (`tetincub_n02`) | 2√2/3 | `tetincub_n02` (`TetInCube.lean`) |
| 2 tetrahedra in an octahedron (`tetinoct_n02`) | 2/√3 | `tetinoct_n02` (`TetInOct.lean`) |
| 2 tetrahedra in a dodecahedron (`tetindod_n02`) | 2√2/(3φ) = √2(√5 − 1)/3 | `tetindod_n02` (`TetInDod.lean`) |
| 2 tetrahedra in an icosahedron (`tetinico_n02`) | 2√((5 − √5)/15) | `tetinico_n02` (`TetInIco.lean`) |
| 2 16-cells in a tesseract (`c16inc8_n02`) | 3√2/4 | `Polytopes4.c16inc8_n02` |
| 2 24-cells in a tesseract (`c24inc8_n02`) | 3√2/2 | `Polytopes4.c24inc8_n02` |
| 2 24-cells in a 16-cell (`c24inc16_n02`) | 3 | `Polytopes4.c24inc16_n02` |
| 2 120-cells in a tesseract (`c120inc8_n02`) | (21 + 9√5)/4 | `Cells120.c120inc8_n02` |
| 2 120-cells in a 16-cell (`c120inc16_n02`) | 3√2(7 + 3√5)/4 | `Cells120.c120inc16_n02` |
| 2 600-cells in a tesseract (`c600inc8_n02`) | (6√2 + 3√10)/4 | `Cells600.c600inc8_n02` |
| 2 600-cells in a 16-cell (`c600inc16_n02`) | (6 + 3√5)/2 | `Cells600.c600inc16_n02` |
| 2 5-simplices in a 5-cube (`sx5inhc5_n02`) | 2√3/5 | `sx5inhc5_n02` (`Simplex5.lean`) |
| 2 5-cells in a 24-cell (`c5inc24_n02`) | √10/4 | `c5inc24_n02` (`C5inC24.lean`) |

**2 octahedra in a cube, side √2.** For n = 2 and a centrally symmetric container, s(2) is the smallest scale at
which one piece fits beside the centre; the piece and its point reflection then form the packing. The lower bound
is the **octahedron centre lemma** (`centre_oct`): a regular octahedron of edge 1 inside a cube of edge s < √2
contains the centre.
- **Reduction.** It comes down to **Lemma O**: for an orthogonal 3×3 matrix with rows ρᵢ, signs σ ∈ {±1}³ and
  mᵢ ≥ ‖ρᵢ‖∞, Σᵢ |⟨ρᵢ, σ⟩| (1 − mᵢ) ≤ 1.
- **Per row.** With r = |⟨ρ, σ⟩|, a unit row gives 1 ≤ 6m² − 4mr + r² (substitute dₖ = m ∓ ρₖσₖ ≥ 0).
- **Summing.** Then r(1 − m) lies below the tangent line 1/4 + r²/12, which is exact at r = 1, while r² ≤ 2.09.
  It lies below ten other exact lines for larger r² (`OctBands.lean`). Σrᵢ² = 3 lets at most one row be large.
- **Equality.** It holds for the reflection H = I − (2/3)𝟙𝟙ᵀ. The packing places H(octahedron) + (√2/6)(1, 1, 1)
  and its point reflection in the two opposite corners of the cube, separated by the hexagonal plane x + y + z = 0.

**Two elementary lower bounds for n = 2**, each proven once in Lean for any dimension:
- **Facet width** (`FacetWidth.centre_of_facet_width`). If a polytope piece misses the container's centre, one of
  its facet planes separates them. The opposite vertex is then at least the piece's width in that direction away
  from the centre, so s(2) ≥ min_f w_f / R_C, with R_C the container's circumradius. For 2 tetrahedra in a cube
  this is height/(√3/2) = 2√2/3. The packing translates the tetrahedron by (√2/12)(1, 1, 1), putting its apex at
  a corner and its base in the plane x + y + z = 0, and adds its point reflection. The same bound is attained
  for 2 tetrahedra in an octahedron (2/√3) and in a dodecahedron (√2(√5 − 1)/3). In the dodecahedron, the 8
  vertices (±φ/2)(±1, ±1, ±1) form an inscribed cube, and at the optimal scale this cube is exactly the cube of
  the tetrahedron-in-cube packing, so that packing fits unchanged. Each tetrahedron vertex is a corner of that
  cube or the combination ½A + ¼B + ¼C of three corners, which puts it in the convex hull of the dodecahedron's
  vertices.
  In the icosahedron (2√((5 − √5)/15) ≈ 0.8585) the apex is a vertex and the base lies in the plane through the
  centre perpendicular to it, with one base edge parallel to an axis. With ι = 1/√(3(φ + 2)), the rotation has
  entries in ℚ(√2, φ, ι). Each base vertex is an explicit combination, with weights in [0, 1], of three
  icosahedron vertices and the centre.
  For 2 5-simplices in a 5-cube (2√3/5), the apex is the corner (√3/5)𝟙 and the base lies in Σxᵢ = 0. Its five
  vertices are the rows of the order-5 Paley matrix, M_ij = χ(j − i) with χ the quadratic character mod 5,
  divided by √10. The rows have entries 0, ±1, sum zero and pairwise inner product −1, so they form a regular
  simplex of edge 1 with every coordinate at most 1/√10 < √3/5.
  For 2 5-cells in a 24-cell (√10/4), the apex is the vertex (√5/4)(1, 1, 0, 0) and the base tetrahedron lies in
  y₀ + y₁ = 0. Three of its vertices sit at 15°, 135° and 255° in the (y₂, y₃)-plane; the 15° rotation from the
  axes is what makes them fit, with largest coordinate (3√2 + √6)/12 ≈ 0.5577 ≤ √5/4 ≈ 0.5590.
- **Two balls** (`BallBound`). Each piece contains its inscribed ball (radius k), and two disjoint balls of
  radius k need s ≥ 2k(1 + 1/√d) in a hypercube, and s ≥ k(1 + √d)/ρ in the cross-polytope {‖x‖₁ ≤ ρ}. The
  16-cell, 24-cell, 120-cell and 600-cell attain this bound in the tesseract, and the 24-cell, 120-cell and
  600-cell in the 16-cell. All seven cases are proven. The 24-cell and 120-cell need only a translation, the
  16-cell the reflection I − ½𝟙𝟙ᵀ, and the 600-cell the rotation M = (1/√2)[[1, 1, 0, 0], [1, −1, 0, 0],
  [0, 0, 1, 1], [0, 0, 1, −1]]; the point reflection gives the second piece.
- **120-cells and 600-cells in Lean.** Each is written as the polar of the other. The 120-cell of edge 1 is
  {⟨n, y⟩ ≤ (7 + 3√5)/4} over the 120 vertices n of the unit 600-cell. The 600-cell of edge 1 is
  {⟨v, y⟩ ≤ 2 + √5} over the 600 vertices v of the standard 120-cell of circumradius 2√2
  (`scripts/optimality/check_polar_hreps.py` checks both descriptions numerically). The proofs use only that
  the normals have equal length, for the inscribed ball, and nine of the facets, for the construction. For the
  600-cell these are the facets with normals (0, 0, ±2, ±2) and their permutations, which M turns into ±eᵢ
  and (±½)⁴.

These lower bounds are elementary. What is new is that the records attain them exactly.

### Prisms in a cube: thirteen more new results (6 Nov 2026)

| Records | Optimal side | Argument | Lean theorems |
|---|---|---|---|
| 2 and 3 triangular prisms of height 3/2 (`pr3l15incub_n02`, `_n03`) | 3/2 | one prism already needs 3/2 (axis widths) | `PrismCube.pr3l15incub_n02`, `_n03` (`TriPrismCube.lean`) |
| 2 to 6 triangular prisms of height 2 (`pr3l2incub_n02` … `_n06`) | 2 | box centre lemma | `PrismCube.pr3l2incub_n02` … `_n06` (`TriPrismCube.lean`) |
| 2 and 3 dodecagonal prisms of height 1 (`pr12incub_n02`, `_n03`) | 2 + √3 | box centre lemma | `PrismCube.pr12incub_n02`, `_n03` (`PrismCube.lean`) |
| 2 dodecagonal prisms of height 3/2 (`pr12l15incub_n02`) | 2 + √3 | one prism already needs 2 + √3 (axis widths) | `PrismCube.pr12l15incub_n02` |
| 2 dodecagonal prisms of height 2 (`pr12l2incub_n02`) | 4 | box centre lemma | `PrismCube.pr12l2incub_n02` |
| 2 octagonal prisms of height 1 (`pr8incub_n02`) | 1 + √2 | one prism already needs 1 + √2 (axis widths) | `PrismCube.pr8incub_n02` (`PolyPrism.lean`) |
| 2 hexagonal prisms of height 1 (`pr6incub_n02`) | 2 | box centre lemma for any polygon (`pcentre`) | `PrismCube.pr6incub_n02` (`PolyPrism.lean`) |

All bases have unit edges; "height" is the length of the lateral edges. A cube container makes two arguments
exact, because a piece can be translated independently along each axis.

- **Axis widths** (`PrismCube.width_le`). A piece inside a cube of side s has width at most s along each axis.
  For a prism with axis a, the width along eᵢ is at least L|aᵢ| plus the base's width in the projected direction.
  For the triangle, six differences of its vertices lie at 60° steps, so that width is at least (√3/2)√(1 − aᵢ²)
  (`six_dirs`). The dodecagon contains the disc of radius r = (2 + √3)/2, so for it the width is 2r√(1 − aᵢ²).
  Some axis has aᵢ² ≥ 1/3, which gives s ≥ 3/2 for the triangular prism of height 3/2. Some axis also has
  aᵢ² ≤ 1/3, which gives s ≥ 2 + √3 for the dodecagonal prism of height 3/2. For the octagonal prism of
  height 1 (`PolyPrism.lean`, any polygon with an inscribed circle) the same step needs |aᵢ| ≤ 4ρ/(4ρ² + 1),
  and for ρ = (1 + √2)/2 that is exactly 1/√2.
- **Box centre lemma** (`PrismCube.centre_of_box`). The admissible translations of a placed piece form a box. For
  each facet (normal β, offset h) and any points vᵢ of the piece, the cube's centre satisfies
  ⟨β, y⟩ ≤ (s/2) Σᵢ |bᵢ| + Σᵢ bᵢ (L vᵢ)ᵢ in piece coordinates, with b = Lβ. For the best vᵢ this is sharp. If the
  bound is below h for every facet, the centre is inside every piece, and two pieces cannot fit. The vᵢ used are
  vertices or points on the inscribed cylinder.
  - *Dodecagonal prism, height 1, s < 2 + √3.* Widths force |aᵢ| > 1/2 for every coordinate; the threshold
    4r/(4r² + 1) is exactly 1/2. The caps then reduce to r Σ|aᵢ|(1 − √(1 − aᵢ²)) < 1, and the twelve sides to
    ‖b‖₁ ≤ √3 < 2.
  - *Any polygon with inradius ρ, height L, s < 2L* (`pcentre`): the box lemma holds when L√3 ≤ 2ρ (sides,
    via |bᵢ| ≤ √(1 − aᵢ²) and ‖b‖₁ ≤ √3) and L ≤ (7/5)ρ (caps). The hexagonal prism of height 1 meets the first
    condition with equality: √3 = 2ρ.
  - *Dodecagonal prism, height 2, s < 4.* No width step is needed. The sides use |bᵢ| ≤ √(1 − aᵢ²), the caps use
    √(1 − aᵢ²) ≥ (7/10)(|aⱼ| + |aₖ|).
  - *Triangular prism, height 2, s < 2.* Widths force |aᵢ| < 13/19. The caps hold because ‖a‖₁ ≤ √3 < 2. Each side
    reduces to Σᵢ |bᵢ|(1 − |aᵢ|) ≤ √3/2 for unit b ⊥ a (`key3`). Adding a multiple of Σ aᵢbᵢ = 0 and applying
    Cauchy–Schwarz gives the square of the left side at most 4 − 2Σ|aᵢ| − P². Here P = Σ ±(|aᵢ| − aᵢ²) has
    mixed signs, so P² ≥ 1/64. Also Σ|aᵢ| ≥ 115/71, which follows from 1/4 ≤ |aᵢ| ≤ 13/19.
- **Constructions.**
  - The dodecagonal prisms are stacked along an axis.
  - Six triangular prisms of height 2 fit in the cube of side exactly 2. In each half of the cube, three prisms
    form a strip of alternating triangles: along y in the half x ≤ 0, along z in the half x ≥ 0. The previous
    record for n = 6 was 2.0000000034.
  - Three triangular prisms of height 3/2 fit at exactly 3/2: their bases form a pinwheel in the square of side
    3/2, and each base touches the other two. The bases have vertices (0, a), (0, a + 1), (√3/2, √3/2);
    (a, 0), (a + 1, 0), (√3/2, √3/2); and (3/2, 1/2), (3/2, 3/2), (3/2 − √3/2, 1), with a = (√3 − 1)/2.
- **Numerical survey** (`scripts/optimality/one_piece.py`, `width_bound.py`, `scan_lower_bounds.py`). The
  scripts compare the one-piece scale s₁ and the centre-avoiding scale with every record. The centre argument
  is numerically exact for further cube families: 4, 5 and 12-gonal antiprisms (n = 2; for the 12-gonal one,
  n = 2–4), and dodecagonal prisms of height 3 (n = 2). For 6- and 8-gonal antiprisms and the pentagonal prism of
  height 3, s₁ itself equals s(2). These are the next candidates; they need sector bounds for the 12-, 16- and
  10-gon.

## 2. Proven elsewhere, not in Lean (43 records)

### Hiroaki Hosono: computer-assisted proofs (27 records)

Hiroaki Hosono (wand125) has computer-assisted proofs of the following results. Each was checked by two
independent checkers, and none has been peer reviewed. They are in
[wand125/square-packing](https://github.com/wand125/square-packing) (MIT; read at commit `ea1c454`,
31 Oct 2026). The catalogue records equal these values.

| Result | Records | Method |
|---|---|---|
| s₆(2) = 2 (d = 4 and d = 5 are now in Lean, section 1) | `hc6inhc6_n02`–`n24` (23 records, side 2) | the cube centre lemma in dimension 6 (see below), then the plateau argument |
| s₃(9) = s₃(10) = 2 + 1/√2 | `cubincub_n09`, `cubincub_n10` | an 8-point lemma by interval branch and bound ([`problems/cubes-in-cube`](https://github.com/wand125/square-packing/tree/main/problems/cubes-in-cube)) |
| s₃(25) = s₃(26) = 3 | `cubincub_n25`, `cubincub_n26` | a closed counting measure by interval branch and bound ([`closed-measure`](https://github.com/wand125/square-packing/tree/main/problems/cubes-in-cube/closed-measure)) |

**The cube centre lemma.** A unit d-cube inside a cube of side less than 2 contains that cube's centre in its
interior. For a cube placed by an orthogonal matrix R, it follows from "Lemma F": Σᵢ |Rᵢⱼ| (2 − Σₖ |Rᵢₖ|) ≤ 1 for
every column j. With the common-point lemma and the 2×2×…×2 grid, it gives side 2 for every 2 ≤ n ≤ 2^d. Lean
proves that implication (`cube_plateau_of_centre_lemma`). Status by dimension:

- **d = 2.** The inequality is (u − 1)² ≥ 0 with u = |cos θ| + |sin θ|.
- **d = 3.** Proven in Lean here (`CubeCentre.core`, section 1). Hosono proved it earlier with computer
  assistance: a hand proof near the axes plus interval checks elsewhere, and later a 5-simplex spectral
  certificate. The Lean proof here uses no computer search.
- **d = 4.** Proven in Lean here (section 1). Hosono proved it earlier with computer assistance.
- **d = 5.** Proven in Lean here (section 1), with a new bound for the band 9/20 ≤ c² ≤ 3/4. Hosono proved it
  earlier with computer assistance.
- **d = 6.** Hosono, [`problems/cubes-n-dim`](https://github.com/wand125/square-packing/tree/main/problems/cubes-n-dim).
  - **Near an axis:** the same polar-decomposition step, which is formalized for any dimension, with
    Lemma F one dimension down as its hypothesis.
  - **Elsewhere:** a spectral bound with exact rational certificates: 21,502 simplices in 5D and about
    2.8 million in 6D.
- **All d.** Open.

**Numerical check here.** The maximum of the left side of Lemma F over all rotations is exactly 1, attained at
axis-aligned placements, in every dimension d = 2–6 (`scripts/optimality/center_lemma.py`, `center_nd.py`).

### Hirotaka Nakano: optimality certificates for 16 Platonic records (#131, 13 Nov 2026)

Hirotaka Nakano (konoha-ily2) published certificates for the minimal container edge of the records below, in
[konoha-ily2/packing-optimality-certificates](https://github.com/konoha-ily2/packing-optimality-certificates)
(v0.2.0, read at commit `0755979`, [doi:10.5281/zenodo.24191316](https://doi.org/10.5281/zenodo.24191316)),
and submitted them in [#131](https://github.com/alejandrozu/platonic-packing/issues/131).

- **Upper bound:** an exact substitution of the optimal configuration.
- **Lower bound for n = 2:** a symmetry reduction, then a tree of rotation boxes, each closed by a rational
  certificate, and an exact local lemma at the optimum. A separate replay checker re-checks every box, and
  Lean 4 (no Mathlib) re-checks the arithmetic.
- **Lower bound for n = 3, 4:** monotonicity in n.
- **Lower bound for n = 5:** inscribed balls and a pigeonhole argument.

By the repository's own account, the arguments, code and reviews were written by Claude (Anthropic) and
re-derived by a second Claude model, with no human review. The reductions are prose arguments, and Lean
checks only the arithmetic. On 14 November, at Alejandro Zarzuelo's request, the certificates were re-run here in an
isolated sandbox: a separate user, no network and no access to credentials
([run log](optimality_evidence/131_replay_2026-11-14.log)). They passed; see "What was checked here" below. What
remains unchecked by anyone is the meaning of the reductions, which no human has reviewed.

| Records | Optimal edge | Lower bound | Status here |
|---|---|---|---|
| `cubinoct_n02` | 1 + √2 | box certificates | computer-assisted, re-run here |
| `icoincub_n02` | 1 + 2√5/3 | box certificates | computer-assisted, re-run here |
| `dodinico_n02` | 2 + 2√5/5 | box certificates | computer-assisted, re-run here |
| `icoinoct_n02` | √(9/2 + 2√5) | box certificates | computer-assisted, re-run here |
| `icoindod_n02` | √5 − 1 | box certificates | computer-assisted, re-run here |
| `octindod_n02` | (2√5 + √10 − √2 − 4)/3 | box certificates | computer-assisted, re-run here |
| `cubinico_n02` | (49√5 − 53)/38 | box certificates | computer-assisted, re-run here |
| `cubintet_n02` | 2 + √6/2 + 2√3/3 | box certificates (tetrahedron reduction) | computer-assisted, re-run here |
| `icointet_n02`–`n04` | 2√2 (1 + 2/√5) | box certificates for n = 2, then monotonicity | computer-assisted, re-run here |
| `octintet_n02`–`n04` | 3 | box certificates for n = 2, then monotonicity | computer-assisted, re-run here |
| `icointet_n05` | (5/3)√(3√5 + 7) | inscribed balls + pigeonhole | **proven; argument checked here** |
| `octintet_n05` | 10/3 | inscribed balls + pigeonhole | **proven; argument checked here** |

**What was checked here.**

- **Upper bounds.** Each of the 16 records holds a packing that this catalogue's exact certifier certifies at
  the claimed edge plus the clearance (relative gap at most 5 × 10⁻⁸). Each record's closed form equals the
  claimed edge exactly (sympy).
- **n = 5.** The lower bound L ≥ 20r/√6 (r the inradius of the piece) was re-derived by hand:
  1. Inscribed balls of radius r are disjoint, so their centres are at least 2r apart.
  2. The centres lie in the tetrahedron of edge L − 2√6 r.
  3. Split that tetrahedron into its four nearest-vertex cells. Each cell has squared diameter 3/8 of the
     squared edge; this was recomputed exactly with fractions.
  4. Five centres in four cells put two of them in one cell, which gives the bound.

  Both inradii (r² = 1/6 for the octahedron, (7 + 3√5)/24 for the icosahedron) were recomputed, and
  20r/√6 equals 10/3 and (5/3)√(3√5 + 7). With the certified packings this settles `octintet_n05` and
  `icointet_n05`. Neither is in Lean yet.
- **n = 3, 4.** Removing pieces keeps a packing feasible, so these rest entirely on the n = 2 certificates.
- **The certificates, re-run (14 Nov, commit `0755979`, sandboxed).**
  - `certificates/SHA256SUMS`: every file matches.
  - `tests/replay_all.py`: every stored n = 2 certificate was replayed from its multipliers alone, with 0 failed
    boxes and every coverage tree closed: about 137,000 accepted boxes over the nine cases that print a count,
    from 426 for icoinoct to 85,522 for cubintet. The octintet replay prints only "all 3 passed". The local
    stages and the n = 3–5 substitutions passed too.
  - Lean 4 `build.py all` and `build.py plateau`: all modules built with no `sorry`. The n = 2 modules use
    `native_decide`, which trusts the Lean compiler; the plateau uses `decide +kernel`.
  - Injected errors: `build.py inject` rejected 63/63 corrupted certificates and built the 3 that are meant to
    build; `build.py inject plateau` rejected 24/24.
  - Not run: the randomized Python tests (`run_python_tests.py`, 1–25 minutes per case).

## 3. n = 2: numerical evidence for 20 Platonic records

Five of these records are now proven in Lean (section 1): `octincub_n02`, `tetincub_n02`, `tetinoct_n02`,
`tetindod_n02` and `tetinico_n02`. The table keeps them so the numerical method can be compared with the proofs.
Eight more now have external computer-assisted certificates (section 2, #131): `cubinoct_n02`, `icoincub_n02`,
`dodinico_n02`, `icoinoct_n02`, `icoindod_n02`, `octindod_n02`, `cubinico_n02` and `cubintet_n02`. Every one
of them agrees with the numerical value below.

For n = 2 a stronger fact holds. Let s_c be the scale below which every placement of a single piece contains
the container's centre in its interior. The common-point lemma gives s(2) ≥ s_c. When the container is
centrally symmetric (cube, octahedron, dodecahedron, icosahedron), equality holds: the best single placement that
avoids the centre, together with its reflection through the centre, is a 2-packing. So **s(2) is a one-piece
problem**, the best fit of one piece beside the centre.

A global search over rotations, with exact linear programming over translations (`scripts/optimality/center_all.py`), finds
s_c equal to the record value to about 7 significant digits in all 20 cases below. That includes 2 cubes in a
tetrahedron, whose container is not centrally symmetric. So each of these n = 2 records is optimal to within
about 10⁻⁷, as far as the search can tell. This is evidence, not proof: the search over rotations could miss
the worst placement.

| Record | s | Closed form | Found by |
|---|---|---|---|
| 2 octahedra in an octahedron (`octinoct_n02`) | 1.9331196 | — | Alejandro Zarzuelo |
| 2 icosahedra in an icosahedron (`icoinico_n02`) | 1.9630860 | — | Alejandro Zarzuelo |
| 2 dodecahedra in a dodecahedron (`dodindod_n02`) | 1.9875981 | — | Alejandro Zarzuelo |
| 2 cubes in an octahedron (`cubinoct_n02`) | 2.4142136 | 1 + √2 | Alejandro Zarzuelo |
| 2 octahedra in a cube (`octincub_n02`) | 1.4142136 | √2 | Alejandro Zarzuelo |
| 2 dodecahedra in an icosahedron (`dodinico_n02`) | 2.8944272 | (10 + 2√5)/5 | Alejandro Zarzuelo |
| 2 icosahedra in a dodecahedron (`icoindod_n02`) | 1.2360680 | -1 + √5 | Alejandro Zarzuelo |
| 2 tetrahedra in a cube (`tetincub_n02`) | 0.9428091 | — | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 tetrahedra in an octahedron (`tetinoct_n02`) | 1.1547006 | — | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 tetrahedra in a dodecahedron (`tetindod_n02`) | 0.5826881 | — | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 tetrahedra in an icosahedron (`tetinico_n02`) | 0.8585154 | — | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 cubes in a tetrahedron (`cubintet_n02`) | 4.3794455 | 2 + √(72√2 + 102)/6 | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 cubes in a dodecahedron (`cubindod_n02`) | 0.9155439 | — | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 cubes in an icosahedron (`cubinico_n02`) | 1.4886140 | -53/38 + 49√5/38 | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 octahedra in a dodecahedron (`octindod_n02`) | 0.7400667 | -4/3 + (2√(3 - √5) + 2√5)/3 | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 octahedra in an icosahedron (`octinico_n02`) | 1.0803631 | √(28 - 12√5) | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 dodecahedra in a cube (`dodincub_n02`) | 3.8368484 | 16/267 + (334√2 + √(63020√2 + 198270))/267 | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 dodecahedra in an octahedron (`dodinoct_n02`) | 4.7268394 | √(64527√5 + 146083)/114 | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 icosahedra in a cube (`icoincub_n02`) | 2.4907120 | 1 + 2√5/3 | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |
| 2 icosahedra in an octahedron (`icoinoct_n02`) | 2.9953525 | √(2√5 + 9/2) | Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik |

The centre argument fails for tetrahedron containers with tetrahedra, octahedra, dodecahedra or icosahedra as
pieces: a single piece can avoid the centroid at the record scale. Nakano's certificates (section 2, #131) use a
different reduction for the tetrahedron. They cover the plateaus of octahedra in a tetrahedron at s = 3 and of
icosahedra in a tetrahedron at s = 5.3582 for n = 2–4, and their end at n = 5. Tetrahedra and dodecahedra in a
tetrahedron (n = 2) remain open.

## 4. Next targets

- s₆(2) = 2 in Lean (23 records). Lemma F in 5D is now proven, but the formalized polar step uses
  ‖row‖₁ ≤ 2, which holds only up to four coordinates. The 6D near region therefore needs that step adapted,
  and the band and far region need their own sphere bounds.
- n = 3 for the Platonic solids. Every n = 3 Platonic record is open except cubes in a cube. The two tools used so
  far stop at n = 2: a common point shared by all pieces, and a one-piece bound. For n = 3 a pigeonhole on two
  points, or a structure lemma, is needed. One candidate is tetrahedra in a cube at side 1. Below side 1, a
  tetrahedron either contains the ball of radius 0.05 about the centre, or has a face plane within 0.05 of the
  centre with the opposite vertex towards a corner (the facet-width argument). Two steps are missing: that a
  tetrahedron of the second kind meets any tetrahedron containing the ball, and that two of the second kind
  point to opposite corners. Then three cannot fit. This is a plan, not yet a proof.
- n = 2: external computer-assisted certificates now cover ten pairs (section 2, #131). The next step is a
  Lean proof of one of them: Lean already re-checks their arithmetic, and what is missing is the reduction,
  which is now a prose argument. Another next step is `octintet_n05` / `icointet_n05` in Lean, a short
  argument with inscribed balls.
- Plateaus starting above n = 2, which need new ideas:
  - octahedra in an octahedron, n = 3–6 (s = 2)
  - tetrahedra in a tetrahedron, n = 3–4 (2)
  - dodecahedra in a dodecahedron, n = 3–4 (2) and n = 5–6 (√5)
  - icosahedra in an octahedron, n = 4–6
  - dodecahedra in a cube, n = 3–4 (2 + √5)
  - octahedra in a cube, n = 7–8 (19√2/15)
  - cubes in a dodecahedron, n = 6–8 (√5 − 1)
