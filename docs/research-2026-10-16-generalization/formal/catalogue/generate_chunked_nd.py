#!/usr/bin/env python3
"""Split exact ND certificates into separately compiled piece-proof modules.

All Cayley source data, canonical-template references, barycentric weights,
indices and separating planes are inherited unchanged from the established
fragment generator. Only module/declaration boundaries and size-proof syntax
change; aggregate soundness still checks every source, vertex and pair.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import generate_fragmented_nd as fragmented
import generate_nd_lean as ordinary

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(c,per_vertex=False,per_pair=False):
    old_name,text=fragmented.generate(c,per_vertex,per_pair)
    plain_name,ordinary_text=ordinary.generate(c)
    name='C'+plain_name
    namespace='PackingCertificates.Catalogue.'+name
    text=text.replace('PackingCertificates.Catalogue.'+old_name,namespace)
    prefix,remaining=text.split('theorem source_piece_0 :',1)
    pieces='theorem source_piece_0 :'+remaining.split('theorem source_checked :',1)[0]
    suffix='theorem source_checked :'+remaining.split('theorem source_checked :',1)[1]
    # Inspect only finite array spines; avoid numerical source/vertex obligations
    # in the common data module.
    prefix=re.sub(r'(theorem template_sizes\s*:.*?:=) by decide \+kernel',
        r'\1 by exact ⟨rfl, rfl⟩',prefix,count=1,flags=re.S)
    prefix=re.sub(r'(theorem input_sizes\s*:.*?:=) by decide \+kernel',
        r'\1 by exact ⟨rfl, rfl, rfl, rfl, rfl⟩',prefix,count=1,flags=re.S)
    data=prefix+f'''#print axioms edge_normalization
#print axioms template_sizes
#print axioms input_sizes
end {namespace}
'''
    original_data=ordinary_text.split('def rawSources :',1)[1].split('theorem edge_normalization :',1)[0]
    generated_data=data.split('def rawSources :',1)[1].split('theorem edge_normalization :',1)[0]
    assert original_data.rstrip()==generated_data.rstrip(),'ND raw source data changed'
    files=[('Data',data,'data',None)]
    starts=list(re.finditer(r'^theorem source_piece_(\d+)\s*:',pieces,re.M))
    if [int(m.group(1)) for m in starts]!=list(range(c['n'])):
        raise ValueError('Unexpected fragmented piece ordering')
    blocks=[]
    for i,start in enumerate(starts):
        stop=starts[i+1].start() if i+1<len(starts) else len(pieces)
        piece=pieces[start.start():stop]
        block=f'Block{i:03d}'
        blocks.append(block)
        audits='\n'.join(f'#print axioms {p}_{i}' for p in
            ('source_piece','gram_piece','pair_row','vertices_piece'))
        body=f'''import {namespace}.Data

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {namespace}
open PackingCertificates.Rational

{piece}
{audits}
end {namespace}
'''
        files.append((block,body,'proof_block',[i]))
    imports='\n'.join('import '+namespace+'.'+block for block in blocks)
    aggregate=f'''{imports}

-- Original source: {c['source_path']}
-- Original JSON SHA256: {c['source_sha256']}
-- Canonical geometry SHA256: {c['geometry_sha256']}
-- Record identifier: {c['record_id']}
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {namespace}
open PackingCertificates.Rational

{suffix}'''
    files.append(('',aggregate,'aggregate',None))
    return name,files


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--only',nargs='*',default=['hc6inhc6_n03','hc6inhc6_n04'])
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--per-vertex',action='store_true')
    ap.add_argument('--per-pair',action='store_true')
    args=ap.parse_args()
    generated=[]
    for path in sorted((HERE/'witnesses_nd').glob('*.json')):
        c=json.loads(path.read_text(encoding='utf8'))
        if c['n']>args.max_n or (args.only and c['record_id'] not in args.only):
            continue
        name,files=generate(c,args.per_vertex,args.per_pair)
        module='PackingCertificates.Catalogue.'+name
        directory=FORMAL/'PackingCertificates'/'Catalogue'/name
        directory.mkdir(parents=True,exist_ok=True)
        steps=[]
        for short,text,kind,indices in files:
            out=directory/(short+'.lean') if short else directory.with_suffix('.lean')
            out.write_text(text,encoding='utf8',newline='\n')
            expected=([module+'.'+p for p in ('edge_normalization','template_sizes','input_sizes')]
                if kind=='data' else
                [module+'.'+p+'_'+str(i) for i in indices for p in
                    ('source_piece','gram_piece','pair_row','vertices_piece')]
                if kind=='proof_block' else
                [module+'.'+p for p in ('source_valid','packing','proper_orientation')])
            steps.append(dict(id='chunked_'+c['record_id']+('_'+short.lower() if short else ''),
                record_id=c['record_id'],n=c['n'],dimension=c['dimension'],
                module=module+('.'+short if short else ''),
                path=str(out.relative_to(FORMAL)).replace('\\','/'),kind=kind,
                piece_indices=indices,generated_source_sha256=digest(out),expected_audits=expected))
        generated.append(dict(id='chunked_'+c['record_id'],record_id=c['record_id'],n=c['n'],
            dimension=c['dimension'],module=module,path=steps[-1]['path'],block_size=1,
            original_json_sha256=c['source_sha256'],original_source_path=c['source_path'],
            original_geometry_sha256=c['geometry_sha256'],original_geometry_path='src/polytopes_nd.json',
            original_witness_sha256=digest(path),steps=steps,
            per_vertex=args.per_vertex,per_pair=args.per_pair,
            dependencies=[{key:s[key] for key in ('module','path','generated_source_sha256')} for s in steps[:-1]]))
    manifest=HERE/'generated-chunked-nd-modules.json'
    manifest.write_text(json.dumps(generated,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(generated_records=len(generated),steps=sum(len(r['steps']) for r in generated),
        manifest=manifest.name,source_bytes=sum((FORMAL/s['path']).stat().st_size for r in generated for s in r['steps']))))


if __name__=='__main__':
    main()

