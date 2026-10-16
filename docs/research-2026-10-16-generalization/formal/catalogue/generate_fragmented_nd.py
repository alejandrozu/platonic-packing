#!/usr/bin/env python3
"""Emit bounded kernel computations for exact ND catalogue certificates.

Data definitions come verbatim from the ordinary generator. Numerical checks
are split across independent declarations; final soundness is assembled from
their checked proofs, without rerunning the monolithic decision procedure.
"""
import argparse
import json
from pathlib import Path

import generate_nd_lean as ordinary

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent


def assemble_all(name, count, predicate, prefix):
    cases = '\n'.join(f'  · exact {prefix}_{i}' for i in range(count))
    return f'''theorem {name} : allFin {count} ({predicate}) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
{cases}
'''


def generate(c, per_vertex=False, per_pair=False):
    original_name, text = ordinary.generate(c)
    name = 'F' + original_name
    text = text.replace(f'namespace PackingCertificates.Catalogue.{original_name}',
        f'namespace PackingCertificates.Catalogue.{name}')
    text = text.replace('import PackingCertificates.Barycentric',
        'import Mathlib.Tactic.FinCases\nimport PackingCertificates.Barycentric', 1)
    prefix = text.split('theorem source_checked :', 1)[0]
    d, n, k = c['dimension'], c['n'], len(c['template_vertices'])
    pieces = []
    for i in range(n):
        pieces.append(f'''theorem source_piece_{i} : Cayley.check (source ({i} : Fin {n})) = true := by decide +kernel

theorem gram_piece_{i} :
    allFin {d} (fun a => allFin {d} (fun b =>
      decide (qdot (record.placement.rotation ({i} : Fin {n}) a)
        (record.placement.rotation ({i} : Fin {n}) b) = if a = b then 1 else 0))) = true := by decide +kernel

''')
        pair_predicate = f'''fun j => if ({i} : Fin {n}) < j then
      planeCheck (record.placement.toCertificate.vertices ({i} : Fin {n}))
        (record.placement.toCertificate.vertices j)
        (record.placement.separation ({i} : Fin {n}) j) else true'''
        if per_pair:
            for j in range(i+1, n):
                pieces.append(f'''theorem pair_{i}_{j} :
    ({pair_predicate}) ({j} : Fin {n}) = true := by decide +kernel
''')
            pair_cases = '\n'.join(f'  · exact pair_{i}_{j}' if i < j else '  · decide +kernel' for j in range(n))
            pieces.append(f'''theorem pair_row_{i} :
    allFin {n} ({pair_predicate}) = true := by
  apply allFin_eq_true.mpr
  intro j
  fin_cases j
{pair_cases}
''')
        else:
            pieces.append(f'''theorem pair_row_{i} :
    allFin {n} ({pair_predicate}) = true := by decide +kernel
''')
        if per_vertex:
            for p in range(k):
                pieces.append(f'''theorem vertex_{i}_{p} :
    record.vertexCheck ({i} : Fin {n}) ({p} : Fin {k}) = true := by decide +kernel
''')
            cases = '\n'.join(f'  · exact vertex_{i}_{p}' for p in range(k))
            pieces.append(f'''theorem vertices_piece_{i} :
    allFin {k} (fun p => record.vertexCheck ({i} : Fin {n}) p) = true := by
  apply allFin_eq_true.mpr
  intro p
  fin_cases p
{cases}
''')
        else:
            pieces.append(f'''theorem vertices_piece_{i} :
    allFin {k} (fun p => record.vertexCheck ({i} : Fin {n}) p) = true := by decide +kernel
''')
    source_all = assemble_all('source_checked', n, 'fun i => Cayley.check (source i)', 'source_piece')
    gram_all = assemble_all('gram_checked_all', n,
        f'fun i => allFin {d} (fun a => allFin {d} (fun b => decide '
        '(qdot (record.placement.rotation i a) (record.placement.rotation i b) = if a = b then 1 else 0)))',
        'gram_piece')
    pair_all = assemble_all('pair_checked', n,
        f'fun i => allFin {n} (fun j => if i < j then '
        'planeCheck (record.placement.toCertificate.vertices i) '
        '(record.placement.toCertificate.vertices j) (record.placement.separation i j) else true)',
        'pair_row')
    vertex_all = assemble_all('vertices_checked', n,
        f'fun i => allFin {k} (fun p => record.vertexCheck i p)', 'vertices_piece')
    suffix = f'''
theorem source_valid : ∀ i, Cayley.Valid (source i) := by
  intro i
  exact Cayley.check_sound _ (allFin_eq_true.mp source_checked i)

theorem gram_checked : orthogonalCheck record.placement = true := gram_checked_all

theorem walls_checked :
    allFin {n} (fun i => allFin {k} (fun p => allFin 0 (fun f =>
      decide (qdot (record.placement.toCertificate.walls f).normal
        (record.placement.toCertificate.vertices i p) ≤
          (record.placement.toCertificate.walls f).offset)))) = true := by
  apply allFin_eq_true.mpr
  intro i
  apply allFin_eq_true.mpr
  intro p
  apply allFin_eq_true.mpr
  intro f
  exact Fin.elim0 f

theorem rational_checked : Rational.check record.placement.toCertificate = true := by
  simp only [Rational.check, Bool.and_eq_true]
  exact ⟨walls_checked, pair_checked⟩

theorem placed_checked : checkPlaced record.placement = true := by
  simp only [checkPlaced, Bool.and_eq_true]
  exact ⟨gram_checked, rational_checked⟩

theorem scale_checked : decide (0 < record.scale) = true := by decide +kernel

theorem checked : Barycentric.check record = true := by
  simp only [Barycentric.check, Bool.and_eq_true]
  exact ⟨⟨placed_checked, scale_checked⟩, vertices_checked⟩

/-- Complete convex-polytope packing, assembled from kernel-checked fragments. -/
theorem packing : Barycentric.Valid record := Barycentric.check_sound record checked

theorem proper_orientation : ∀ i : Fin {n},
    Matrix.det (fun a b => (record.placement.rotation i a b : ℝ)) = 1 := by
  intro i
  exact Cayley.determinant_real (source i) (allFin_eq_true.mp source_checked i)

#print axioms source_valid
#print axioms packing
#print axioms proper_orientation
end PackingCertificates.Catalogue.{name}
'''
    return name, prefix + '\n'.join(pieces) + '\n' + source_all + '\n' + gram_all + '\n' + pair_all + '\n' + vertex_all + suffix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-n', type=int, default=100)
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--per-vertex', action='store_true')
    ap.add_argument('--per-pair', action='store_true')
    args = ap.parse_args()
    dest = FORMAL / 'PackingCertificates/Catalogue'
    dest.mkdir(parents=True, exist_ok=True)
    generated = []
    for path in sorted((HERE / 'witnesses_nd').glob('*.json')):
        c = json.loads(path.read_text())
        if c['n'] > args.max_n or (args.only and c['record_id'] not in args.only):
            continue
        name, text = generate(c, args.per_vertex, args.per_pair)
        out = dest / (name + '.lean')
        out.write_text(text, encoding='utf8', newline='\n')
        generated.append({'id': 'fragmented_' + c['record_id'], 'record_id': c['record_id'],
            'n': c['n'], 'dimension': c['dimension'], 'module': 'PackingCertificates.Catalogue.' + name,
            'path': str(out.relative_to(FORMAL)).replace('\\', '/'),
            'fragmentation': 'vertex' if args.per_vertex else 'piece',
            'pair_fragmentation': 'pair' if args.per_pair else 'row'})
    manifest = HERE / 'generated-fragmented-nd-modules.json'
    manifest.write_text(json.dumps(generated, indent=2)+'\n')
    print(json.dumps({'generated': len(generated), 'manifest': manifest.name,
        'source_bytes': sum((FORMAL / r['path']).stat().st_size for r in generated)}))


if __name__ == '__main__':
    main()
