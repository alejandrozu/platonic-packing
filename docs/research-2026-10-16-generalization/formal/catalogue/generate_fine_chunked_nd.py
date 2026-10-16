#!/usr/bin/env python3
"""Emit bounded ND proof files with eight atomic vertex checks per process.

This creates a fresh VR namespace and never overwrites the active CR cohort.
Shared data, source checks, Gram tests, pair tests, and every vertex obligation
are inherited unchanged from generate_chunked_nd.py. Numerical containment
checks are split across small files; per-piece and final assembly use opaque
checked proofs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import generate_chunked_nd as chunked
import generate_nd_lean as ordinary

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def header(imports,namespace):
    return '\n'.join('import '+m for m in imports)+f'''

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace {namespace}
open PackingCertificates.Rational

'''


def generate(c,vertex_block_size=8):
    if vertex_block_size<1:
        raise ValueError('vertex_block_size must be positive')
    old_name,old_files=chunked.generate(c,per_vertex=True,per_pair=False)
    ordinary_name,_=ordinary.generate(c)
    name='V'+ordinary_name
    old_ns='PackingCertificates.Catalogue.'+old_name
    namespace='PackingCertificates.Catalogue.'+name
    old={short:text.replace(old_ns,namespace) for short,text,_,_ in old_files}
    n,k=c['n'],len(c['template_vertices'])
    files=[dict(short='Data',text=old['Data'],kind='data',piece_indices=None,
        vertex_indices=[],fragment_role='data',
        audits=[namespace+'.'+p for p in ('edge_normalization','template_sizes','input_sizes')])]
    aggregate_imports=[]
    for i in range(n):
        source_block=old[f'Block{i:03d}']
        first=source_block.index(f'theorem source_piece_{i} :')
        first_vertex=source_block.index(f'theorem vertex_{i}_0 :')
        first_assembly=source_block.index(f'theorem vertices_piece_{i} :')
        source_body=source_block[first:first_vertex]
        vertex_body=source_block[first_vertex:first_assembly]
        assembly_body=source_block[first_assembly:].split('#print axioms',1)[0]
        source_name=f'Source{i:03d}'
        source_audits=[namespace+'.'+p+'_'+str(i) for p in ('source_piece','gram_piece','pair_row')]
        source_text=header([namespace+'.Data'],namespace)+source_body+'\n'+'\n'.join(
            '#print axioms '+a for a in source_audits)+f'\nend {namespace}\n'
        files.append(dict(short=source_name,text=source_text,kind='proof_block',
            piece_indices=[i],vertex_indices=[],fragment_role='source',audits=source_audits))
        aggregate_imports.append(namespace+'.'+source_name)
        matches=list(re.finditer(r'^theorem vertex_(\d+)_(\d+)\s*:.*?(?=^theorem\s|\Z)',vertex_body,re.M|re.S))
        if [(int(m.group(1)),int(m.group(2))) for m in matches]!=[(i,p) for p in range(k)]:
            raise ValueError('Unexpected atomic vertex sequence: '+c['record_id'])
        vertex_imports=[]
        for start in range(0,k,vertex_block_size):
            stop=min(k,start+vertex_block_size)
            block_index=start//vertex_block_size
            vertex_name=f'Vertex{i:03d}_{block_index:03d}'
            vertex_imports.append(namespace+'.'+vertex_name)
            body='\n'.join(m.group(0) for m in matches[start:stop])
            audits=[namespace+f'.vertex_{i}_{p}' for p in range(start,stop)]
            text=header([namespace+'.Data'],namespace)+body+'\n'+'\n'.join(
                '#print axioms '+a for a in audits)+f'\nend {namespace}\n'
            files.append(dict(short=vertex_name,text=text,kind='proof_block',piece_indices=[],
                vertex_indices=[[i,p] for p in range(start,stop)],fragment_role='vertices',audits=audits))
        assembly_name=f'Assemble{i:03d}'
        assembly_audits=[namespace+f'.vertices_piece_{i}']
        assembly_text=header(vertex_imports,namespace)+assembly_body+'\n'+(
            '#print axioms '+assembly_audits[0])+f'\nend {namespace}\n'
        files.append(dict(short=assembly_name,text=assembly_text,kind='proof_block',piece_indices=[],
            vertex_indices=[],fragment_role='vertex_assembly',audits=assembly_audits))
        aggregate_imports.append(namespace+'.'+assembly_name)
    aggregate_tail=old[''].split('-- Original source:',1)[1]
    aggregate='\n'.join('import '+m for m in aggregate_imports)+'\n\n-- Original source:'+aggregate_tail
    files.append(dict(short='',text=aggregate,kind='aggregate',piece_indices=None,vertex_indices=[],
        fragment_role='aggregate',audits=[namespace+'.'+p for p in ('source_valid','packing','proper_orientation')]))
    return name,files


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--only',nargs='*',default=['hc6inhc6_n04'])
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--vertex-block-size',type=int,default=8)
    args=ap.parse_args()
    generated=[]
    for path in sorted((HERE/'witnesses_nd').glob('*.json')):
        c=json.loads(path.read_text(encoding='utf8'))
        if c['n']>args.max_n or (args.only and c['record_id'] not in args.only):
            continue
        name,files=generate(c,args.vertex_block_size)
        module='PackingCertificates.Catalogue.'+name
        directory=FORMAL/'PackingCertificates'/'Catalogue'/name
        directory.mkdir(parents=True,exist_ok=True)
        steps=[]
        for entry in files:
            short=entry['short']
            out=directory/(short+'.lean') if short else directory.with_suffix('.lean')
            out.write_text(entry['text'],encoding='utf8',newline='\n')
            steps.append(dict(id='chunked_fine_'+c['record_id']+('_'+short.lower() if short else ''),
                record_id=c['record_id'],n=c['n'],dimension=c['dimension'],
                module=module+('.'+short if short else ''),
                path=str(out.relative_to(FORMAL)).replace('\\','/'),kind=entry['kind'],
                piece_indices=entry['piece_indices'],vertex_indices=entry['vertex_indices'],
                fragment_role=entry['fragment_role'],generated_source_sha256=digest(out),
                expected_audits=entry['audits']))
        generated.append(dict(id='chunked_fine_'+c['record_id'],record_id=c['record_id'],n=c['n'],
            dimension=c['dimension'],module=module,path=steps[-1]['path'],block_size=1,
            fine_vertex_coverage=True,vertex_count=len(c['template_vertices']),
            vertex_block_size=args.vertex_block_size,
            original_json_sha256=c['source_sha256'],original_source_path=c['source_path'],
            original_geometry_sha256=c['geometry_sha256'],original_geometry_path='src/polytopes_nd.json',
            original_witness_sha256=digest(path),steps=steps,
            dependencies=[{key:s[key] for key in ('module','path','generated_source_sha256')} for s in steps[:-1]]))
    manifest=HERE/'generated-chunked-fine-nd-modules.json'
    manifest.write_text(json.dumps(generated,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(generated_records=len(generated),steps=sum(len(r['steps']) for r in generated),
        vertex_checks=sum(len(s['vertex_indices']) for r in generated for s in r['steps']),
        manifest=manifest.name,source_bytes=sum((FORMAL/s['path']).stat().st_size for r in generated for s in r['steps']))))


if __name__=='__main__':
    main()
