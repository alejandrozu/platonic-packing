#!/usr/bin/env python3
"""Emit fragmented cube proofs with independently checked axis-support caches.

The original exact placements, planes and source declarations are unchanged.
Python proposes cache values and signed-axis tags; Lean verifies every cache
entry and verifies each tagged plane normal before using the shortcut.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

import generate_fragmented_cubes as fragmented
import generate_lean as ordinary

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent


def axis_tag(normal):
    normal=tuple(Q(x) for x in normal)
    for k in range(3):
        for sign in (1,-1):
            axis=tuple(Q(sign if a==k else 0) for a in range(3))
            if normal==axis:
                return k,sign<0
    return None


def direction_text(tag):
    if tag is None:
        return 'none'
    k,negative=tag
    return f'some ({k}, {str(negative).lower()})'


def generate(c):
    fragmented_name,text=fragmented.generate(c)
    name='A'+fragmented_name[1:]
    text=text.replace('import PackingCertificates.CubeFast','import PackingCertificates.AxisFast',1)
    text=text.replace('PackingCertificates.Catalogue.'+fragmented_name,
        'PackingCertificates.Catalogue.'+name)
    prefix,body=text.split('theorem source_piece_0 :',1)
    body='theorem source_piece_0 :'+body.split('theorem fast_checked :',1)[0]
    body=body.replace('pairRowCheck record','AxisFast.pairRowCheck record cache directions')
    n=c['n']
    lower=[];upper=[]
    for center,rotation in zip(c['centres'],c['rotations']):
        radii=[sum((abs(Q(x)) for x in row),Q(0))/2 for row in rotation]
        lower.append([Q(center[k])-radii[k] for k in range(3)])
        upper.append([Q(center[k])+radii[k] for k in range(3)])
    tags={(p['i'],p['j']):axis_tag(p['normal']) for p in c['planes']}
    assert len(tags)==n*(n-1)//2
    direction_rows=[ordinary.arr([direction_text(tags[i,j]) for j in range(i+1,n)]) for i in range(n)]
    caches=f'''def rawAxisLower : Array (QPoint 3) := {ordinary.arr([ordinary.vec(row) for row in lower])}

def rawAxisUpper : Array (QPoint 3) := {ordinary.arr([ordinary.vec(row) for row in upper])}

def rawDirections : Array (Array (Option AxisFast.SignedAxis)) := {ordinary.arr(direction_rows)}

def cache : AxisFast.Cache {n} where
  lower i := rawAxisLower.getD i.val 0
  upper i := rawAxisUpper.getD i.val 0

def directions : AxisFast.Directions {n} := fun i j =>
  (rawDirections.getD i.val #[]).getD (j.val-i.val-1) none

theorem cache_input_sizes : rawAxisLower.size = {n} ∧ rawAxisUpper.size = {n} ∧
    rawDirections.size = {n} := by decide +kernel

'''
    cache_pieces='\n'.join(f'''theorem cache_row_{i} :
    AxisFast.cacheRowCheck record cache ({i} : Fin {n}) = true := by decide +kernel
''' for i in range(n))
    cache_all=fragmented.assemble_all('cache_checked',n,
        'fun i => AxisFast.cacheRowCheck record cache i','cache_row')
    suffix=f'''
theorem axis_checked : AxisFast.check record cache directions = true :=
  AxisFast.check_of_rows record cache directions source_checked gram_checked
    (allFin_eq_true.mp cache_checked)
    (allFin_eq_true.mp walls_checked) (allFin_eq_true.mp pairs_checked)

theorem fast_checked : CubeFast.fastCheck record = true :=
  AxisFast.check_implies_fastCheck record cache directions axis_checked

theorem checked : record.check = true := CubeFast.fastCheck_implies_check record fast_checked

/-- Same source-bound packing theorem, using independently checked exact
axis supports and the generic fallback for every non-axis plane. -/
theorem packing : record.Valid := AxisFast.check_sound record cache directions axis_checked

#print axioms source_checked
#print axioms axis_checked
#print axioms checked
#print axioms packing
end PackingCertificates.Catalogue.{name}
'''
    result=prefix+caches+body+cache_pieces+'\n'+cache_all+suffix
    _,original=ordinary.generate(c)
    original_data=original.split('def rawQuaternions :',1)[1].split('theorem checked :',1)[0]
    generated_data=prefix.split('def rawQuaternions :',1)[1]
    assert original_data.rstrip()==generated_data.rstrip(),'Original source data changed'
    return name,result,sum(tag is not None for tag in tags.values())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--only',nargs='*')
    args=ap.parse_args()
    dest=FORMAL/'PackingCertificates'/'Catalogue'
    dest.mkdir(parents=True,exist_ok=True)
    generated=[]
    for path in sorted((HERE/'witnesses').glob('*.json')):
        c=json.loads(path.read_text(encoding='utf-8'))
        if c['n']>args.max_n or (args.only and c['record_id'] not in args.only):
            continue
        name,text,axis_pairs=generate(c)
        out=dest/(name+'.lean')
        out.write_text(text,encoding='utf-8',newline='\n')
        generated.append(dict(id='axis_'+c['record_id'],record_id=c['record_id'],n=c['n'],
            dimension=3,module='PackingCertificates.Catalogue.'+name,
            path=str(out.relative_to(FORMAL)).replace('\\','/'),fragmentation='piece',
            checking_strategy='certified cached axis bounds plus exact support fallback',
            cached_axis_pairs=axis_pairs,generic_pairs=len(c['planes'])-axis_pairs,
            original_json_sha256=c['source_sha256'],
            generated_source_sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
    manifest=HERE/'generated-axis-cube-modules.json'
    manifest.write_text(json.dumps(generated,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(generated=len(generated),manifest=manifest.name,
        cached_axis_pairs=sum(r['cached_axis_pairs'] for r in generated),
        generic_pairs=sum(r['generic_pairs'] for r in generated),
        source_bytes=sum((FORMAL/r['path']).stat().st_size for r in generated))))


if __name__=='__main__':
    main()
