# Square antiprisms in a square antiprism

Constructions and exact certificates by **PingYou Ltd (PY)**. Each piece has unit edge length; the container has edge length `S`. Boundary touching is permitted in the exact constructions.

All nineteen native coordinate records improve the catalogue’s certified scales. N = 11–20 improve its nominal bounds; N = 2–10 provide exact endpoint certificates at the existing displayed scales. Original construction attribution is preserved for certificate refinements.

| N | Online nominal S (rounded) | Online certified S | Our exact S ≤ |
|---:|---:|---:|---:|
| 2 | 1.664197290498 | 1.664197408753304 | 1.66419729049787581634 |
| 3 | 1.972649083082 | 1.9726494315757 | 1.97264908308208920905 |
| 4 | 2 | 2.0000001110000003 | 2.00000000000000000000 |
| 5 | 2.178581501511 | 2.1785818692596 | 2.17858150151050014252 |
| 6 | 2.245921799598 | 2.2459221621635 | 2.24592179959800605909 |
| 7 | 2.362975809545 | 2.362976179963 | 2.36297580954527605118 |
| 8 | 2.38494257434 | 2.3849429627158 | 2.38494257433693010309 |
| 9 | 2.489041676411 | 2.4890420412952 | 2.48904167641086825826 |
| 10 | 2.59007618947 | 2.5900766031074 | 2.59007618947117053068 |
| 11 | 2.743255403185 | 2.7432558483366 | 2.65264643496540881859 |
| 12 | 2.807779603729 | 2.807780046219 | 2.76499377740834363123 |
| 13 | 2.907150482438 | 2.9071509307251 | 2.84221912570791973312 |
| 14 | 2.970066702945 | 2.9700671873264 | 2.94585849856083744061 |
| 15 | 3.011775526561 | 3.0117760051631 | 3.00000000000000000000 |
| 16 | 3.060556764522 | 3.0605572388858 | 3.00000000000000000000 |
| 17 | 3.091031384381 | 3.0910318676381 | 3.00000000000000000000 |
| 18 | 3.141705571523 | 3.1417060596309 | 3.04212021468433419560 |
| 19 | 3.17380865053 | 3.1738091514068 | 3.13108766535194265875 |
| 20 | 3.294160346392 | 3.2941608665307 | 3.21934697592104598071 |

Online nominal values are rounded approximations; online certified scales include their export clearance. Our exact upper decimals are rounded outward. The strictly positive-clearance native scales are listed separately in `bounds.csv`. The defining exact data are in `proofs/`; `bounds.json` retains the enclosing intervals. In particular, N = 2 has `S = √(26√2 − 34)`, N = 4 has `S = 2`, N = 9 has `S = (31 + 8√2)/17`, N = 15–17 have `S = 3`, and N = 20 has an exact fixed-frame contact endpoint over `Q(2^(1/4))`.

## Native records

The repository certifier requires strictly positive separation. The native records therefore dilate centres and container by `1 + 10⁻¹²`, then round only the exported coordinates and container scale outward. This export adjustment is separate from the exact construction bound. `bounds.csv` includes both scales.

Original catalogue files remain unchanged. Each new record identifies its construction author, comparison source, and exact proof. N = 15 and 16 are deletions of the supplied N = 17 construction.

## Verification

```sh
python -m pip install -r docs/constructions/pingyou-ap4-2-20/requirements.txt
python docs/constructions/pingyou-ap4-2-20/verify.py
```

The replay checks exact rotations, all host inequalities, and every body pair. The finite linear-programming certificates also verify a matching nonnegative dual for their stated fixed-frame and separating-direction classes. The N = 3, 5, 6, 18 and 19 proofs certify algebraic contact roots. The N = 18 and 19 polynomial systems are stored as compressed exact JSON; `python proofs/high/verify.py --derive` additionally regenerates them symbolically.

These are feasible upper bounds. Fixed-frame duals do not establish unrestricted optimality.

The contribution is available under the repository’s MIT license. Original construction credit for certificate refinements is retained in the native records.
