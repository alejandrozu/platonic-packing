#!/usr/bin/env python3
"""Split actual cube certificates into separately compiled arithmetic blocks.

The data module contains unchanged exact source values and small shape/length
checks. Each block covers a disjoint range of piece indices. The aggregate
imports opaque checked proofs and performs no new numerical decision run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import generate_axis_cubes as axis
import generate_fragmented_cubes as fragments
import generate_lean as ordinary

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def piece_fragments(n,indices):
    result=[]
    for i in indices:
        index=f'({i} : Fin {n})'
        result.append(f'''theorem source_piece_{i} :
    ({fragments.source_predicate(index)}) = true := by decide +kernel

theorem gram_piece_{i} :
    {fragments.gram_predicate(index)} = true := by decide +kernel

theorem cache_row_{i} :
    AxisFast.cacheRowCheck record cache {index} = true := by decide +kernel

theorem wall_row_{i} : CubeFast.wallRowCheck record {index} = true := by decide +kernel

theorem pair_row_{i} :
    AxisFast.pairRowCheck record cache directions {index} = true := by decide +kernel
''')
    return '\n'.join(result)


def generate(c,block_size=5):
    if block_size<1:
        raise ValueError('block_size must be positive')
    axis_name,axis_text,axis_pairs=axis.generate(c)
    ordinary_name,_=ordinary.generate(c)
    name='C'+ordinary_name
    namespace='PackingCertificates.Catalogue.'+name
    n=c['n']
    data=axis_text.split('theorem source_piece_0 :',1)[0]
    data=data.replace('PackingCertificates.Catalogue.'+axis_name,namespace)
    # Size proofs inspect only the array spines, not source arithmetic.
    data=re.sub(r'(theorem input_sizes\s*:.*?:=) by decide \+kernel',
        r'\1 by exact ⟨rfl, rfl, rfl, rfl⟩',data,count=1,flags=re.S)
    data=re.sub(r'(theorem cache_input_sizes\s*:.*?:=) by decide \+kernel',
        r'\1 by exact ⟨rfl, rfl, rfl⟩',data,count=1,flags=re.S)
    data+=f'''#print axioms input_sizes
#print axioms cache_input_sizes
end {namespace}
'''
    files=[('Data',data,'data',None)]
    blocks=[]
    for start in range(0,n,block_size):
        block_index=start//block_size
        block=f'Block{block_index:03d}'
        indices=list(range(start,min(n,start+block_size)))
        blocks.append(block)
        declarations=piece_fragments(n,indices)
        audits='\n'.join(f'#print axioms {prefix}_{i}' for i in indices
            for prefix in ('source_piece','gram_piece','cache_row','wall_row','pair_row'))
        text=f'''import {namespace}.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {namespace}
open PackingCertificates.Rational
open PackingCertificates.CubeFast

{declarations}
{audits}
end {namespace}
'''
        files.append((block,text,'proof_block',indices))
    all_sources=fragments.assemble_all('source_pieces_checked',n,
        'fun i => '+fragments.source_predicate('i'),'source_piece')
    all_grams=fragments.assemble_all('gram_pieces_checked',n,
        'fun i => '+fragments.gram_predicate('i'),'gram_piece')
    all_cache=fragments.assemble_all('cache_checked',n,
        'fun i => AxisFast.cacheRowCheck record cache i','cache_row')
    all_walls=fragments.assemble_all('walls_checked',n,
        'fun i => CubeFast.wallRowCheck record i','wall_row')
    all_pairs=fragments.assemble_all('pairs_checked',n,
        'fun i => AxisFast.pairRowCheck record cache directions i','pair_row')
    imports='\n'.join('import '+namespace+'.'+block for block in blocks)
    aggregate=f'''{imports}

-- Original source: {c['source_path']}
-- Original JSON SHA256: {c['source_sha256']}
-- Record identifier: {c['record_id']}
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {namespace}
open PackingCertificates.Rational
open PackingCertificates.CubeFast

{all_sources}
{all_grams}
{all_cache}
{all_walls}
{all_pairs}
theorem scale_checked : decide (0 < record.scale) = true := by decide +kernel

theorem source_checked : record.sourceCheck = true := by
  simp only [CubeRecord.sourceCheck, Bool.and_eq_true]
  exact ⟨scale_checked, source_pieces_checked⟩

theorem gram_checked : orthogonalCheck record.toPlacement = true := gram_pieces_checked

theorem axis_checked : AxisFast.check record cache directions = true :=
  AxisFast.check_of_rows record cache directions source_checked gram_checked
    (allFin_eq_true.mp cache_checked)
    (allFin_eq_true.mp walls_checked) (allFin_eq_true.mp pairs_checked)

theorem checked : record.check = true :=
  CubeFast.fastCheck_implies_check record
    (AxisFast.check_implies_fastCheck record cache directions axis_checked)

/-- Complete actual catalogue packing, assembled from separately compiled
kernel-checked arithmetic blocks. No numerical test is silently omitted. -/
theorem packing : record.Valid := AxisFast.check_sound record cache directions axis_checked

#print axioms source_checked
#print axioms axis_checked
#print axioms checked
#print axioms packing
end {namespace}
'''
    files.append(('',aggregate,'aggregate',None))
    return name,files,axis_pairs


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--only',nargs='*',default=['cubincub_n100'])
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--block-size',type=int,default=5)
    args=ap.parse_args()
    generated=[]
    for path in sorted((HERE/'witnesses').glob('*.json')):
        c=json.loads(path.read_text(encoding='utf8'))
        if c['n']>args.max_n or (args.only and c['record_id'] not in args.only):
            continue
        name,files,axis_pairs=generate(c,args.block_size)
        module='PackingCertificates.Catalogue.'+name
        directory=FORMAL/'PackingCertificates'/'Catalogue'/name
        directory.mkdir(parents=True,exist_ok=True)
        steps=[]
        for short,text,kind,indices in files:
            out=directory/(short+'.lean') if short else directory.with_suffix('.lean')
            out.write_text(text,encoding='utf8',newline='\n')
            steps.append(dict(id='chunked_'+c['record_id']+('_'+short.lower() if short else ''),
                record_id=c['record_id'],n=c['n'],dimension=3,
                module=module+('.'+short if short else ''),
                path=str(out.relative_to(FORMAL)).replace('\\','/'),kind=kind,
                piece_indices=indices,generated_source_sha256=sha(out),
                expected_audits=([module+'.input_sizes',module+'.cache_input_sizes'] if kind=='data' else
                    [module+'.'+prefix+'_'+str(i) for i in indices for prefix in
                        ('source_piece','gram_piece','cache_row','wall_row','pair_row')]
                    if kind=='proof_block' else
                    [module+'.'+proof for proof in ('source_checked','axis_checked','checked','packing')])) )
        generated.append(dict(id='chunked_'+c['record_id'],record_id=c['record_id'],n=c['n'],
            dimension=3,module=module,path=steps[-1]['path'],
            original_json_sha256=c['source_sha256'],original_source_path=c['source_path'],block_size=args.block_size,
            cached_axis_pairs=axis_pairs,generic_pairs=len(c['planes'])-axis_pairs,
            original_witness_sha256=sha(path),steps=steps,
            dependencies=[{key:s[key] for key in ('module','path','generated_source_sha256')} for s in steps[:-1]]))
    manifest=HERE/'generated-chunked-cube-modules.json'
    manifest.write_text(json.dumps(generated,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(generated_records=len(generated),
        steps=sum(len(r['steps']) for r in generated),manifest=manifest.name,
        source_bytes=sum((FORMAL/s['path']).stat().st_size for r in generated for s in r['steps']))))


if __name__=='__main__':
    main()


