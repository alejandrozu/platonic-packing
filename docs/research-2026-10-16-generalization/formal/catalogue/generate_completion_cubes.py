#!/usr/bin/env python3
"""Generate a disjoint completion cohort without touching the verified baseline."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import generate_chunked_cubes as cubes

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline',default='verified-module-manifest.json')
    ap.add_argument('--only',nargs='*')
    ap.add_argument('--block-size',type=int,default=5)
    args=ap.parse_args()
    baseline=HERE/args.baseline
    verified=json.loads(baseline.read_text())
    done={r['record_id'] for r in verified}
    generated=[]
    for path in sorted((HERE/'witnesses').glob('*.json')):
        c=json.loads(path.read_text())
        if c['record_id'] in done or (args.only and c['record_id'] not in args.only):continue
        oldname,files,axis_pairs=cubes.generate(c,args.block_size)
        name='E'+oldname[1:]
        oldns='PackingCertificates.Catalogue.'+oldname
        module='PackingCertificates.Catalogue.'+name
        directory=FORMAL/'PackingCertificates'/'Catalogue'/name
        directory.mkdir(parents=True,exist_ok=True)
        steps=[]
        for short,text,kind,indices in files:
            text=text.replace(oldns,module)
            out=directory/(short+'.lean') if short else directory.with_suffix('.lean')
            out.write_text(text,encoding='utf8',newline='\n')
            expected=([module+'.input_sizes',module+'.cache_input_sizes'] if kind=='data' else
                [module+'.'+prefix+'_'+str(i) for i in indices for prefix in
                    ('source_piece','gram_piece','cache_row','wall_row','pair_row')]
                if kind=='proof_block' else
                [module+'.'+proof for proof in ('source_checked','axis_checked','checked','packing')])
            steps.append(dict(id='completion_'+c['record_id']+('_'+short.lower() if short else ''),
                record_id=c['record_id'],n=c['n'],dimension=3,module=module+('.'+short if short else ''),
                path=str(out.relative_to(FORMAL)).replace('\\','/'),kind=kind,piece_indices=indices,
                generated_source_sha256=digest(out),expected_audits=expected))
        generated.append(dict(id='completion_'+c['record_id'],record_id=c['record_id'],n=c['n'],
            dimension=3,module=module,path=steps[-1]['path'],completion_group='cubes',
            original_json_sha256=c['source_sha256'],original_source_path=c['source_path'],
            original_witness_sha256=digest(path),block_size=args.block_size,
            baseline_manifest=args.baseline,baseline_manifest_sha256=digest(baseline),
            cached_axis_pairs=axis_pairs,generic_pairs=len(c['planes'])-axis_pairs,
            steps=steps,dependencies=[{key:s[key] for key in ('module','path','generated_source_sha256')} for s in steps[:-1]]))
    generated.sort(key=lambda r:r['n'])
    out=HERE/'generated-completion-cube-modules.json'
    out.write_text(json.dumps(generated,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(baseline_records=len(done),generated_records=len(generated),
        total_steps=sum(len(r['steps']) for r in generated),manifest=out.name,
        source_bytes=sum((FORMAL/s['path']).stat().st_size for r in generated for s in r['steps']))))

if __name__=='__main__':main()
