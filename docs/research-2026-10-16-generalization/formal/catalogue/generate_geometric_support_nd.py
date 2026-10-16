#!/usr/bin/env python3
"""Generate exact support/hull certificates without barycentric arrays.

Supported containers are the canonical hypercubes and cross polytopes with a
proved NDModels container constructor. Placements, scales and planes come
verbatim from the frozen proposed witness. Generating source is not proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import generate_nd_lean as ordinary
import generate_fragmented_nd as fragments
from generate_lean import module_name, rat, vec

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent
SUPPORTED = {'c8', 'hc5', 'hc6', 'c16', 'op5', 'op6'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_representatives(c):
    representatives, seen = [], {}
    for i, data in enumerate(zip(c['raw_skews'], c['diagonal_signs'], c['cayley_inverses'], c['rotations'])):
        key = json.dumps(data, separators=(',', ':'))
        representatives.append(seen.setdefault(key, i))
    return representatives


def generate(c, use_box_support=False, derive_gram=False, reuse_sources=False, block_size=1):
    if c['container'] not in SUPPORTED:
        raise ValueError('Container needs original barycentric fallback: ' + c['container'])
    d, n = c['dimension'], c['n']
    k, l = len(c['template_vertices']), len(c['container_vertices'])
    if use_box_support and c['container'] not in {'c8', 'hc5', 'hc6'}:
        raise ValueError('Coordinate-wall shortcut requires a box container')
    if block_size < 1:
        raise ValueError('block_size must be positive')
    name = ('W' if use_box_support else 'G') + ('D' if derive_gram else '') + ('U' if reuse_sources else '') + f'B{block_size}' + module_name(c['record_id'])
    ns = 'PackingCertificates.Catalogue.' + name
    _, original = ordinary.generate(c)
    raw = 'def rawSources :' + original.split('def rawSources :', 1)[1].split('def vertexIndices :', 1)[0]
    data = ('import PackingCertificates.Extensions.BoxSupport\n' if use_box_support else '') + (
        'import PackingCertificates.Extensions.CayleyGeometry\n' if derive_gram else '') + f'''import Mathlib.Tactic.FinCases
import PackingCertificates.Extensions.NDModels
import PackingCertificates.Cayley

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {ns}
open PackingCertificates.Rational
open PackingCertificates.Extensions
open scoped BigOperators

{raw}
def source (i : Fin {n}) : Cayley.Certificate {d} :=
  rawSources.getD i.val {{skew := 0, signs := 0, inverse := 0, rotation := 0}}

def record : NDSupport.Certificate {d} {n} {k} {l} where
  piece := NDModels.{c['piece']}Piece
  outer := NDModels.{c['container']}Outer
  rotation := fun i => (source i).rotation
  center := fun i => rawCenters.getD i.val 0
  separation := fun i j => (allPlanes.getD i.val #[]).getD (j.val-i.val-1) ⟨0,0,0⟩
  scale := {rat(c['scale'])}
  containerCenter := {vec(c['container_center'])}

def storedScale : ℚ := {rat(c['s_full'])}
def edgeRatio : ℚ := {rat(c['edge_ratio'])}

theorem edge_normalization : edgeRatio = 1 ∧ record.scale = storedScale * edgeRatio := by decide +kernel

theorem template_sizes : TemplateData.{c['piece']}.size = {k} ∧
    TemplateData.{c['container']}.size = {l} := by exact ⟨rfl, rfl⟩

theorem input_sizes : rawSources.size = {n} ∧ rawCenters.size = {n} ∧ allPlanes.size = {n} :=
  by exact ⟨rfl, rfl, rfl⟩

#print axioms edge_normalization
#print axioms template_sizes
#print axioms input_sizes
end {ns}
'''
    files = [dict(short='Data', text=data, kind='data', piece_indices=None)]
    representatives = source_representatives(c)
    for i in range(n):
        source_proof = 'by decide +kernel'
        source_extra = ''
        imports = ''
        if reuse_sources and representatives[i] < i:
            source_extra = f'''theorem source_equal_{i} : source ({i} : Fin {n}) = source ({representatives[i]} : Fin {n}) := rfl
#print axioms source_equal_{i}
'''
            source_proof = f'''by
  rw [source_equal_{i}]
  exact source_piece_{representatives[i]}'''
            if representatives[i] // block_size != i // block_size:
                imports = f'import {ns}.Block{representatives[i] // block_size:03d}\n'
        gram_proof = 'by decide +kernel'
        if derive_gram:
            gram_proof = f'''by
  apply allFin_eq_true.mpr
  intro a
  apply allFin_eq_true.mpr
  intro b
  exact decide_eq_true (CayleyGeometry.check_row_gram (source ({i} : Fin {n})) source_piece_{i} a b)'''
        vertices = f'''theorem vertices_piece_{i} :
    allFin {k} (fun p => NDSupport.vertexCheck record ({i} : Fin {n}) p) = true := by decide +kernel
'''
        if use_box_support:
            vertices = f'''theorem walls_piece_{i} : BoxSupport.wallRowCheck record ({i} : Fin {n}) = true := by decide +kernel

theorem vertices_piece_{i} :
    allFin {k} (fun p => NDSupport.vertexCheck record ({i} : Fin {n}) p) = true :=
  BoxSupport.wallRowCheck_implies_vertices record rfl ({i} : Fin {n}) walls_piece_{i}

#print axioms walls_piece_{i}
'''
        body = imports + f'''import {ns}.Data
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {ns}
open PackingCertificates.Rational
open PackingCertificates.Extensions

{source_extra}
theorem source_piece_{i} : Cayley.check (source ({i} : Fin {n})) = true := {source_proof}

theorem gram_piece_{i} :
    allFin {d} (fun a => allFin {d} (fun b => decide
      (qdot (record.rotation ({i} : Fin {n}) a) (record.rotation ({i} : Fin {n}) b) =
        if a = b then 1 else 0))) = true := {gram_proof}

theorem pair_row_{i} : NDSupport.pairRowCheck record ({i} : Fin {n}) = true := by decide +kernel

{vertices}

#print axioms source_piece_{i}
#print axioms gram_piece_{i}
#print axioms pair_row_{i}
#print axioms vertices_piece_{i}
end {ns}
'''
        files.append(dict(short=f'Block{i:03d}', text=body, kind='proof_block', piece_indices=[i]))
    if block_size > 1:
        merged = [files[0]]
        for start in range(0, n, block_size):
            group = files[start+1:min(n,start+block_size)+1]
            imports = sorted({line for item in group for line in item['text'].splitlines() if line.startswith('import ')})
            bodies = [item['text'].split(f'namespace {ns}\n', 1)[1].rsplit(f'end {ns}', 1)[0] for item in group]
            text = '\n'.join(imports) + f'\nset_option maxRecDepth 1000000\nset_option maxHeartbeats 0\nnamespace {ns}\n' + '\n'.join(bodies) + f'\nend {ns}\n'
            merged.append(dict(short=f'Block{start//block_size:03d}', text=text, kind='proof_block',
                               piece_indices=list(range(start,min(n,start+block_size)))))
        files = merged
    source_all = fragments.assemble_all('source_checked', n, 'fun i => Cayley.check (source i)', 'source_piece')
    gram_all = fragments.assemble_all('gram_checked_all', n,
        f'fun i => allFin {d} (fun a => allFin {d} (fun b => decide '
        '(qdot (record.rotation i a) (record.rotation i b) = if a = b then 1 else 0)))', 'gram_piece')
    pair_all = fragments.assemble_all('pairs_checked', n,
        'fun i => NDSupport.pairRowCheck record i', 'pair_row')
    vertex_all = fragments.assemble_all('vertices_checked', n,
        f'fun i => allFin {k} (fun p => NDSupport.vertexCheck record i p)', 'vertices_piece')
    aggregate = '\n'.join(f'import {ns}.Block{i:03d}' for i in range((n+block_size-1)//block_size)) + f'''

-- Original source: {c['source_path']}
-- Original JSON SHA256: {c['source_sha256']}
-- Canonical geometry SHA256: {c['geometry_sha256']}
-- Record identifier: {c['record_id']}
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {ns}
open PackingCertificates.Rational
open PackingCertificates.Extensions

{source_all}
{gram_all}
{pair_all}
{vertex_all}
theorem source_valid : ∀ i, Cayley.Valid (source i) := by
  intro i
  exact Cayley.check_sound _ (allFin_eq_true.mp source_checked i)

theorem gram_checked : orthogonalCheck record.placement = true := gram_checked_all

theorem placed_checked : NDSupport.checkPlacedFast record = true := by
  simp only [NDSupport.checkPlacedFast, Bool.and_eq_true]
  exact ⟨gram_checked, pairs_checked⟩

theorem scale_checked : decide (0 < record.scale) = true := by decide +kernel

theorem checked : NDSupport.check record = true := by
  simp only [NDSupport.check, Bool.and_eq_true]
  exact ⟨⟨placed_checked, scale_checked⟩, vertices_checked⟩

theorem packing : NDSupport.Valid record := NDSupport.check_sound record checked

theorem proper_orientation : ∀ i : Fin {n}, Matrix.det (fun a b => (record.rotation i a b : ℝ)) = 1 := by
  intro i
  exact Cayley.determinant_real (source i) (allFin_eq_true.mp source_checked i)

#print axioms source_valid
#print axioms packing
#print axioms proper_orientation
end {ns}
'''
    files.append(dict(short='', text=aggregate, kind='aggregate', piece_indices=None))
    return name, files


def main():
    import re
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only', nargs='+', required=True)
    ap.add_argument('--box-support', action='store_true', help='Check only coordinate support walls for box containers')
    ap.add_argument('--manifest', default='generated-geometric-support-nd-modules.json')
    ap.add_argument('--derive-gram', action='store_true', help='Derive orthogonality from the exact Cayley source check')
    ap.add_argument('--reuse-sources', action='store_true', help='Reuse definitionally identical complete raw Cayley source proofs')
    ap.add_argument('--block-size', type=int, default=1)
    args = ap.parse_args()
    plans = []
    for path in sorted((HERE / 'witnesses_nd').glob('*.json')):
        c = json.loads(path.read_text(encoding='utf8'))
        if c['record_id'] not in args.only:
            continue
        name, files = generate(c, args.box_support, args.derive_gram, args.reuse_sources, args.block_size)
        ns = 'PackingCertificates.Catalogue.' + name
        directory = FORMAL / 'PackingCertificates' / 'Catalogue' / name
        directory.mkdir(parents=True, exist_ok=True)
        steps = []
        for entry in files:
            short = entry['short']
            out = directory / (short + '.lean') if short else directory.with_suffix('.lean')
            out.write_text(entry['text'], encoding='utf8', newline='\n')
            audits = re.findall(r'^#print axioms ([A-Za-z0-9_.]+)', entry['text'], re.M)
            steps.append(dict(id='geometric_support_' + name + ('_' + short.lower() if short else ''),
                record_id=c['record_id'], n=c['n'], dimension=c['dimension'], module=ns + ('.' + short if short else ''),
                path=str(out.relative_to(FORMAL)).replace('\\', '/'), kind=entry['kind'], piece_indices=entry['piece_indices'],
                generated_source_sha256=sha(out), expected_audits=[a if '.' in a else ns + '.' + a for a in audits]))
        names = ['NDGeometry', 'NDSupport', 'NDModels'] + (['BoxSupport'] if args.box_support else [])
        if args.derive_gram:
            names.append('CayleyGeometry')
        ext = [FORMAL / 'PackingCertificates/Extensions' / (x + '.lean') for x in names]
        plans.append(dict(id='geometric_support_' + name, record_id=c['record_id'], n=c['n'], dimension=c['dimension'],
            module=ns, path=steps[-1]['path'], original_source_path=c['source_path'], original_json_sha256=c['source_sha256'],
            original_witness_sha256=sha(path), original_geometry_path='src/polytopes_nd.json', original_geometry_sha256=c['geometry_sha256'],
            steps=steps, dependencies=[{k:s[k] for k in ('module','path','generated_source_sha256')} for s in steps[:-1]],
            source_representatives=source_representatives(c) if args.reuse_sources else list(range(c['n'])),
            block_size=args.block_size,
            extension_dependencies=[dict(path=str(p.relative_to(FORMAL)).replace('\\','/'), source_sha256=sha(p),
                olean_sha256=sha(p.with_suffix('.olean')) if p.with_suffix('.olean').is_file() else None) for p in ext],
            proof_status='Unverified generated source; requires successful builds and extension-dependency audit'))
    if len(plans) != len(set(args.only)):
        raise ValueError('Some requested identifiers were not found')
    out = HERE / args.manifest
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plans, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(generated=len(plans), steps=sum(len(r['steps']) for r in plans), manifest=out.name)))


if __name__ == '__main__':
    main()
