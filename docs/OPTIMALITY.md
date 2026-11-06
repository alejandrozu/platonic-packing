# Which records are optimal?

_6 November 2026._ A record gives an upper bound: its packing fits in a container of scale s. It is **optimal**
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
it is what extends to 5D. The elementary bound here is weaker and fails in 5D, where its minimum on the far
region is about −0.10.

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

### Prisms in a cube: twelve more new results (6 Nov 2026)

| Records | Optimal side | Argument | Lean theorems |
|---|---|---|---|
| 2 and 3 triangular prisms of height 3/2 (`pr3l15incub_n02`, `_n03`) | 3/2 | one prism already needs 3/2 (axis widths) | `PrismCube.pr3l15incub_n02`, `_n03` (`TriPrismCube.lean`) |
| 2 to 6 triangular prisms of height 2 (`pr3l2incub_n02` … `_n06`) | 2 | box centre lemma | `PrismCube.pr3l2incub_n02` … `_n06` (`TriPrismCube.lean`) |
| 2 and 3 dodecagonal prisms of height 1 (`pr12incub_n02`, `_n03`) | 2 + √3 | box centre lemma | `PrismCube.pr12incub_n02`, `_n03` (`PrismCube.lean`) |
| 2 dodecagonal prisms of height 3/2 (`pr12l15incub_n02`) | 2 + √3 | one prism already needs 2 + √3 (axis widths) | `PrismCube.pr12l15incub_n02` |
| 2 dodecagonal prisms of height 2 (`pr12l2incub_n02`) | 4 | box centre lemma | `PrismCube.pr12l2incub_n02` |
| 2 octagonal prisms of height 1 (`pr8incub_n02`) | 1 + √2 | one prism already needs 1 + √2 (axis widths) | `PrismCube.pr8incub_n02` (`PolyPrism.lean`) |

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

## 2. Proven with computer assistance elsewhere, not in Lean (57 records)

Hiroaki Hosono (wand125) has computer-assisted proofs of the following results. Each was checked by two
independent checkers, and none has been peer reviewed. They are in
[wand125/square-packing](https://github.com/wand125/square-packing) (MIT; read at commit `ea1c454`,
31 Oct 2026). The catalogue records equal these values.

| Result | Records | Method |
|---|---|---|
| s_d(2) = 2 for d = 5, 6 (d = 4 is now in Lean, section 1) | `hc5inhc5_n02`–`n31`, `hc6inhc6_n02`–`n24` (53 records, side 2) | the cube centre lemma in dimension d (see below), then the plateau argument |
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
- **d = 5, 6.** Hosono, [`problems/cubes-n-dim`](https://github.com/wand125/square-packing/tree/main/problems/cubes-n-dim).
  - **Near an axis:** the same polar-decomposition step, which is formalized for any dimension, with
    Lemma F one dimension down as its hypothesis.
  - **Elsewhere:** a spectral bound with exact rational certificates: 21,502 simplices in 5D and about
    2.8 million in 6D.
- **All d.** Open.

**Numerical check here.** The maximum of the left side of Lemma F over all rotations is exactly 1, attained at
axis-aligned placements, in every dimension d = 2–6 (`scripts/optimality/center_lemma.py`, `center_nd.py`).

## 3. n = 2: numerical evidence for 20 Platonic records

Five of these records are now proven in Lean (section 1): `octincub_n02`, `tetincub_n02`, `tetinoct_n02`,
`tetindod_n02` and `tetinico_n02`. The table keeps them so the numerical method can be compared with the proofs.

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
pieces: a single piece can avoid the centroid at the record scale. The plateaus there, for example octahedra in
a tetrahedron at s = 3 for n = 2–4 and icosahedra in a tetrahedron at s = 5.3582 for n = 2–4, need a different
argument.

## 4. Next targets

- s₅(2) = 2 in Lean (30 records). The near-axis step is already in Lean and needs Lemma F in 4D, which is now
  proven. The far region needs more than the elementary bound: Hosono's spectral bound with its certificate, or
  a new idea.
- n = 2: certify s_c rigorously for one pair, for example 2 octahedra in a cube at √2. That needs a rigorous
  global bound over all rotations.
- Plateaus starting above n = 2, which need new ideas:
  - octahedra in an octahedron, n = 3–6 (s = 2)
  - tetrahedra in a tetrahedron, n = 3–4 (2)
  - dodecahedra in a dodecahedron, n = 3–4 (2) and n = 5–6 (√5)
  - icosahedra in an octahedron, n = 4–6
  - dodecahedra in a cube, n = 3–4 (2 + √5)
  - octahedra in a cube, n = 7–8 (19√2/15)
  - cubes in a dodecahedron, n = 6–8 (√5 − 1)
