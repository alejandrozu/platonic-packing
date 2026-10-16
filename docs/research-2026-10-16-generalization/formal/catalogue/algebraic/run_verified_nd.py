#!/usr/bin/env python3
"""Source-bound ND quadratic-inverse builds using the recursive closure runner."""
from __future__ import annotations
from fractions import Fraction as Q
import json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_verified as base
import generate_nd_pilots as generator
from nd_geometry import parse_mq,mu_parameters,render_template,render_root_data

FORMAL=base.FORMAL
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def qarray(x):
    if isinstance(x,list):return [qarray(v)for v in x]
    return Q(x)

def source_binding(row):
    if row['source_freeze']!=base.FREEZE:raise ValueError('Unexpected ND source freeze')
    native=base.path('catalogue/algebraic/inputs/'+row['source_path'])
    files=[base.digest_file(base.rel(native),row['source_sha256']),
        base.digest_file(row['proposal_path'],row['proposal_sha256']),
        base.digest_file(row['generated_module'],row['generated_source_sha256']),
        base.digest_file(row['geometry_source_path'],row['geometry_source_sha256']),
        base.digest_file(row['geometry_intervals_path'],row['geometry_intervals_sha256'])]
    proposal=read(base.path(row['proposal_path']));raw=read(native);geometry=read(base.path(row['geometry_intervals_path']));sourceGeometry=read(base.path(row['geometry_source_path']))
    for key in ['record_id','problem','source_path','source_sha256','source_freeze','dimension','n','piece','container']:
        if proposal[key]!=row[key]:raise ValueError('ND proposal/source registry mismatch '+key)
    if raw['dim']!=row['dimension']or raw['n']!=row['n']or raw['piece']!=row['piece']or raw['container']!=row['container']or len(raw['pieces'])!=row['n']:
        raise ValueError('ND source category/count mismatch')
    if Q(proposal['s_full'])!=Q(raw['s_full'])or Q(proposal['scale'])!=Q(raw['s_full']):raise ValueError('Native ND scale not exact binary64 value')
    if proposal['native_mu']!=raw['mu']:raise ValueError('Native ND mu string not preserved')
    if list(map(Q,proposal['container_center']))!=list(map(Q,raw.get('container_center',[0]*row['dimension']))):raise ValueError('Native ND container centre changed')
    sys.path.insert(0,str(HERE.parent))
    from export_nd import cayley
    if not all(len(proposal[k])==raw['n']for k in ['centres','raw_skews','diagonal_signs','cayley_inverses','rotations']):raise ValueError('ND source pose count mismatch')
    for i,pose in enumerate(raw['pieces']):
        expected=cayley(pose,row['dimension'])
        actual=[qarray(proposal[k][i])for k in ['centres','raw_skews','diagonal_signs','cayley_inverses','rotations']]
        if list(expected)!=actual:raise ValueError('ND raw Cayley placement differs from exact source')
    expectedPairs=[(i,j)for i in range(raw['n'])for j in range(i+1,raw['n'])]
    if [(z['i'],z['j'])for z in proposal['planes']]!=expectedPairs or proposal['pair_count']!=len(expectedPairs):raise ValueError('ND all-pair coverage mismatch')
    if proposal['geometry_sha256']!=row['geometry_source_sha256']or geometry['geometry_sha256']!=row['geometry_source_sha256']:raise ValueError('ND geometry source hash mismatch')
    rootSource=FORMAL/'PackingCertificates/Algebraic/Generated/ND/RootData.lean'
    if rootSource.read_bytes()!=render_root_data(geometry['roots']):raise ValueError('ND RootData source differs from exact geometry-root transcription')
    files.append(dict(path=base.rel(rootSource),sha256=base.core.digest(rootSource)))
    for name,pid in [('piece_'+raw['piece'],raw['piece']),('container_'+row['problem'],raw['container'])]:
        t=geometry['templates'][name];s=sourceGeometry[pid];r=t['radicand']
        if t['dimension']!=s['dim']or t['vertex_count']!=len(s['V']):raise ValueError('ND canonical shape count mismatch')
        expected=[]
        for v in s['V']:
            coords=[]
            for text in v:
                c=parse_mq(text)
                if set(c)-{1,r}:raise ValueError('ND primitive root mismatch')
                coords.append([c.get(1,Q(0)),c.get(r,Q(0))])
            expected.append(coords)
        if qarray(t['coefficients'])!=expected:raise ValueError('ND exact canonical coordinate coefficient mismatch')
        root=geometry['roots'][str(r)]
        if list(map(Q,root['polynomial']))!=[-r,0,1]:raise ValueError('ND primitive root polynomial mismatch')
        if name.startswith('piece_')and t['D']is not None:raise ValueError('ND raw piece template was rescaled')
        canonical=FORMAL/'PackingCertificates/Algebraic/Generated/ND'/(name+'.lean')
        if canonical.read_bytes()!=render_template(name,t):raise ValueError('ND canonical Lean source differs from exact geometry transcription '+name)
        files.append(dict(path=base.rel(canonical),sha256=base.core.digest(canonical)))
    pieceCount=geometry['templates']['piece_'+raw['piece']]['vertex_count']
    for key in ['placed_vertex_intervals','normalized_vertex_intervals','containment']:
        if len(proposal[key])!=raw['n']or any(len(values)!=pieceCount for values in proposal[key]):raise ValueError('ND proposal omits an exact placed piece vertex '+key)
    if proposal['vertex_count']!=raw['n']*pieceCount:raise ValueError('ND proposal total exact vertex count mismatch')
    a,b,e=mu_parameters(raw['mu']);spec=proposal['mu_spec'];container=geometry['templates']['container_'+row['problem']]
    if Q(spec['a'])!=a or Q(spec['b'])!=b or spec['times_sqrt_two']!=e or spec['radicand']!=container['radicand']:
        raise ValueError('ND literal native mu expression transcription mismatch')
    if b and spec['radicand']!=5:raise ValueError('ND nonconstant mu primitive mismatch')
    if list(map(Q,container['D']))!=[Q(spec['d0']),Q(spec['d1'])]:raise ValueError('ND normalization polynomial not bound to native mu proof')
    r=Q(spec['radicand']);f=2 if e else 1;m0=f*(a*a+r*b*b);m1=f*2*a*b
    if m0*Q(spec['d0'])+r*m1*Q(spec['d1'])!=1 or m0*Q(spec['d1'])+m1*Q(spec['d0'])!=0:raise ValueError('ND inverse-square normalization identity fails')
    exporter=HERE/'export_nd_pilots.py'
    if proposal['proposal_exporter_sha256']!=base.core.digest(exporter):raise ValueError('ND proposal exporter source changed')
    exact=generator.generate(base.path(row['proposal_path']),write=False)
    if exact!=row:raise ValueError('ND deterministic generated source/registry differs')
    for helper in [Path(__file__),exporter,HERE/'nd_geometry.py',HERE/'generate_nd_pilots.py',HERE/'generate_3d.py',HERE/'geometry_intervals.py',HERE.parent/'export_nd.py',HERE.parent/'export_cubes.py']:
        files.append(dict(path=base.rel(helper),sha256=base.core.digest(helper)))
    return files

def option(flag,default):
    if flag in sys.argv:return Path(sys.argv[sys.argv.index(flag)+1])
    return default

def main():
    if '--registry'not in sys.argv:sys.argv +=['--registry',str(HERE/'generated-nd-pilots-registry.json')]
    if '--receipt'not in sys.argv:sys.argv +=['--receipt',str(HERE/'nd-pilots-verification.json')]
    base.source_binding=source_binding
    base.main()
    if '--plan-only'in sys.argv:return
    receiptPath=option('--receipt',HERE/'nd-pilots-verification.json');receipt=read(receiptPath)
    stages={x['path']:x for x in receipt['stages']};problems=[]
    for record in receipt['verified_records']:
        audited=stages[record['proof_stage']]['audited_theorems']
        if any(name not in audited for name in record['expected_mu_declarations']):problems.append(record['record_id'])
    if problems:
        receipt['status']='partial_or_failed';receipt['missing_native_mu_semantic_audits']=problems;base.save(receiptPath,receipt)
        raise SystemExit('Native mu proof declarations missing from source-bound audits')
    receipt['native_mu_semantic_audits_passed']=True
    receipt['nd_builder_sha256']=base.core.digest(Path(__file__))
    base.save(receiptPath,receipt)

if __name__=='__main__':main()
