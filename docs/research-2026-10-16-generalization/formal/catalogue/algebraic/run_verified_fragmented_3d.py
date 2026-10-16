#!/usr/bin/env python3
"""Build exact 3D proof fragments using full source/import/object/log receipts."""
from __future__ import annotations
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_verified as base
native_source_binding = base.source_binding
import generate_fragmented_3d_pilots as generator


def source_binding(row):
    original=row['original_registry_row']
    files=native_source_binding(original)
    spec=row['fragmentation']
    exact=generator.generate(original,spec['basis_width'],spec['vertex_width'],write=False)
    if exact!=row:
        raise ValueError('Fragment registry differs from exact original-data/proof transcription')
    if row['record_id']!=original['record_id']:
        raise ValueError('Fragment record identity changed')
    for entry in spec['files']:
        files.append(base.digest_file(entry['path'],entry['sha256']))
    # Complete, disjoint basis/vertex/pair coverage is checked independently of
    # generator metadata, as well as being required by the final Lean theorem.
    b,k,n=spec['basis_count'],spec['vertex_count'],spec['piece_count']
    bases=[z for f in spec['files']for z in f.get('basis_indices',[])]
    vertices=[tuple(z)for f in spec['files']for z in f.get('vertex_indices',[])]
    pairs=[tuple(z)for f in spec['files']for z in f.get('pair_vertex_indices',[])]
    if sorted(bases)!=list(range(b)):
        raise ValueError('Missing/duplicate exact inverse basis check')
    if sorted(vertices)!=[(i,p)for i in range(n)for p in range(k)]:
        raise ValueError('Missing/duplicate placed or containment vertex check')
    if sorted(pairs)!=[(i,j,p)for i in range(n)for j in range(i+1,n)for p in range(k)]:
        raise ValueError('Missing/duplicate pair separating vertex check')
    for helper in [Path(__file__),HERE/'generate_fragmented_3d_pilots.py',HERE/'run_verified.py']:
        files.append(dict(path=base.rel(helper),sha256=base.core.digest(helper)))
    return files


def option(flag,default):
    return Path(sys.argv[sys.argv.index(flag)+1])if flag in sys.argv else default


def main():
    if '--registry'not in sys.argv:
        sys.argv+=['--registry',str(HERE/'generated-fragmented-3d-pilots-registry.json')]
    if '--receipt'not in sys.argv:
        sys.argv+=['--receipt',str(HERE/'fragmented-3d-pilots-verification.json')]
    base.source_binding=source_binding
    base.main()
    if '--plan-only'in sys.argv:return
    receipt_path=option('--receipt',HERE/'fragmented-3d-pilots-verification.json')
    receipt=base.read(receipt_path);stages={s['path']:s for s in receipt['stages']}
    problems=[]
    for record in receipt['verified_records']:
        for entry in record['fragmentation']['files']:
            stage=stages.get(entry['path'])
            if not stage or any(a not in stage['audited_theorems']for a in entry['expected_audits']):
                problems.append(dict(record_id=record['record_id'],path=entry['path']))
    receipt.update(fragment_builder_path=base.rel(Path(__file__)),
        fragment_builder_sha256=base.core.digest(Path(__file__)),
        fragment_semantic_audits_passed=not problems)
    if problems:
        receipt['status']='partial_or_failed';receipt['fragment_audit_failures']=problems
    base.save(receipt_path,receipt)
    if problems:raise SystemExit(1)


if __name__=='__main__':main()
