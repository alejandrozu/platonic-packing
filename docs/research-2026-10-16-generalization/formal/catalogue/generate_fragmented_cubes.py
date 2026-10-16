#!/usr/bin/env python3
"""Emit bounded kernel computations for the exact cube catalogue.

Raw data declarations and source hashes come unchanged from generate_lean.py.
Every source-orientation condition, Gram test, wall row and pair row receives
its own proof. Final assembly references those proofs and never reruns a
monolithic record decision procedure. This generator is not a Lean receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import generate_lean as ordinary

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent


def assemble_all(name, count, predicate, proof_prefix):
    cases = '\n'.join(f'  · exact {proof_prefix}_{i}' for i in range(count))
    return f'''theorem {name} : allFin {count} ({predicate}) = true := by
  apply allFin_eq_true.mpr
  intro i
  fin_cases i
{cases}
'''


def source_predicate(i):
    return (f'decide (0 < Cube.quaternionNormSq (record.quaternion {i})) && '
        f'decide (record.rotation {i} = Cube.quaternionMatrix (record.quaternion {i})) && '
        f'decide (Cube.determinant3 (record.rotation {i}) = 1)')


def gram_predicate(i):
    return (f'allFin 3 (fun a => allFin 3 (fun b => decide '
        f'(qdot (record.toPlacement.rotation {i} a) '
        f'(record.toPlacement.rotation {i} b) = if a = b then 1 else 0)))')


def generate(c):
    original_name, ordinary_text = ordinary.generate(c)
    name = 'F' + original_name
    text = ordinary_text.replace('import PackingCertificates.Catalogue',
        'import Mathlib.Tactic.FinCases\nimport PackingCertificates.CubeFast', 1)
    text = text.replace(f'namespace PackingCertificates.Catalogue.{original_name}',
        f'namespace PackingCertificates.Catalogue.{name}', 1)
    text = text.replace('open PackingCertificates.Rational',
        'open PackingCertificates.Rational\nopen PackingCertificates.CubeFast', 1)
    prefix = text.split('theorem checked :', 1)[0]
    n = c['n']
    fragments = []
    for i in range(n):
        index = f'({i} : Fin {n})'
        fragments.append(f'''theorem source_piece_{i} :
    ({source_predicate(index)}) = true := by decide +kernel

theorem gram_piece_{i} :
    {gram_predicate(index)} = true := by decide +kernel

theorem wall_row_{i} : wallRowCheck record {index} = true := by decide +kernel

theorem pair_row_{i} : pairRowCheck record {index} = true := by decide +kernel
''')
    source_all = assemble_all('source_pieces_checked', n,
        'fun i => '+source_predicate('i'), 'source_piece')
    gram_all = assemble_all('gram_pieces_checked', n,
        'fun i => '+gram_predicate('i'), 'gram_piece')
    walls_all = assemble_all('walls_checked', n,
        'fun i => wallRowCheck record i', 'wall_row')
    pairs_all = assemble_all('pairs_checked', n,
        'fun i => pairRowCheck record i', 'pair_row')
    suffix = f'''
theorem scale_checked : decide (0 < record.scale) = true := by decide +kernel

theorem source_checked : record.sourceCheck = true := by
  simp only [CubeRecord.sourceCheck, Bool.and_eq_true]
  exact ⟨scale_checked, source_pieces_checked⟩

theorem gram_checked : orthogonalCheck record.toPlacement = true := gram_pieces_checked

theorem fast_checked : fastCheck record = true :=
  fastCheck_of_rows record source_checked gram_checked
    (allFin_eq_true.mp walls_checked) (allFin_eq_true.mp pairs_checked)

/-- Assembled from independently kernel-checked row proofs, without evaluating
all vertex tests or all pair rows again in one large computation. -/
theorem checked : record.check = true := fastCheck_implies_check record fast_checked

/-- Actual source-bound proper rigid unit cubes in the actual side-s_full
container, with complete containment and pairwise separation. -/
theorem packing : record.Valid := fastCheck_sound record fast_checked

#print axioms source_checked
#print axioms fast_checked
#print axioms checked
#print axioms packing
end PackingCertificates.Catalogue.{name}
'''
    result = prefix + '\n'.join(fragments) + '\n' + source_all + '\n' + gram_all + '\n' + walls_all + '\n' + pairs_all + suffix
    # Verify data declarations are copied byte-for-byte except namespace/imports.
    ordinary_data = ordinary_text.split('def rawQuaternions :', 1)[1].split('theorem checked :', 1)[0]
    generated_data = result.split('def rawQuaternions :', 1)[1].split('theorem source_piece_0 :', 1)[0]
    assert ordinary_data.rstrip() == generated_data.rstrip(), 'Raw data changed'
    return name, result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-n', type=int, default=100)
    ap.add_argument('--only', nargs='*')
    args = ap.parse_args()
    dest = FORMAL / 'PackingCertificates' / 'Catalogue'
    dest.mkdir(parents=True, exist_ok=True)
    generated = []
    for path in sorted((HERE / 'witnesses').glob('*.json')):
        c = json.loads(path.read_text(encoding='utf-8'))
        if c['n'] > args.max_n or (args.only and c['record_id'] not in args.only):
            continue
        name, text = generate(c)
        out = dest / (name + '.lean')
        out.write_text(text, encoding='utf-8', newline='\n')
        generated.append(dict(id='fragmented_' + c['record_id'], record_id=c['record_id'],
            n=c['n'], dimension=c['dimension'], module='PackingCertificates.Catalogue.' + name,
            path=str(out.relative_to(FORMAL)).replace('\\','/'), fragmentation='piece',
            checking_strategy='cube support functions; separate source, Gram, wall and pair rows',
            original_json_sha256=c['source_sha256'],
            generated_source_sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
    manifest = HERE / 'generated-fragmented-cube-modules.json'
    manifest.write_text(json.dumps(generated,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(generated=len(generated),manifest=manifest.name,
        source_bytes=sum((FORMAL/r['path']).stat().st_size for r in generated))))


if __name__ == '__main__':
    main()
