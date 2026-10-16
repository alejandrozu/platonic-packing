"""Inventory every remaining frozen algebraic-coordinate packing target.

Exact rational arithmetic checks candidate root-isolation and interval data;
these results are preparation, not Lean verification receipts.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
PAPER=HERE.parents[2]
FREEZE='1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'
DATA=PAPER/'data'

def add(a,b):return (a[0]+b[0],a[1]+b[1])
def mul(a,b):
    p=[x*y for x in a for y in b]
    return min(p),max(p)
def evaluate(cs,x):
    v=(Q(0),Q(0))
    for c in reversed(cs):v=add((Q(c),Q(c)),mul(x,v))
    return v
def slope(cs,x):
    if not cs:return Q(0),Q(0)
    return add(evaluate(cs[1:],x),mul(x,slope(cs[1:],x)))
def exact(cs,x):return evaluate(cs,(x,x))[0]
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v)for v in x]
    return x

index=json.loads((DATA/'records.json').read_text(encoding='utf8'))
solid_path=DATA/'sources/src/solids_exact.json'
solids=json.loads(solid_path.read_text(encoding='utf8'))
nd_path=DATA/'sources/src/polytopes_nd.json'
nd=json.loads(nd_path.read_text(encoding='utf8'))
old=json.loads((HERE.parent/'inventory/rational-nd-inventory.json').read_text(encoding='utf8'))
old_ids={(r['problem'],r['n'])for r in old['records']}
templates={}
for name,s in solids.items():
    interval=tuple(map(Q,s['interval']));p=list(map(Q,s['minpoly']));ds=slope(p,interval)
    sums=[sum((Q(v[a][j])for v in s['V']),Q(0))for a in range(3)for j in range(len(p)-1)]
    templates[name]=dict(degree=len(p)-1,vertices=len(s['V']),faces=len(s['faces']),
        has_inverse_sqrt_scale=s['D']is not None,minpoly=p,root_interval=interval,
        endpoint_values=[exact(p,x)for x in interval],slope_interval=ds,
        proposed_root_check=interval[0] < interval[1] and exact(p,interval[0])*exact(p,interval[1]) < 0 and (ds[0] > 0 or ds[1] < 0),
        centroid_zero_coefficientwise=all(x == 0 for x in sums),
        scale_square_interval=evaluate(s['D'],interval)if s['D']else[Q(1),Q(1)])
rows=[]
for problem in index['problems']:
    d=problem.get('dim',3)
    for row in problem['rows']:
        if not row.get('file') or (d == 3 and problem['id'] == 'cubincub') or (problem['id'],row['n']) in old_ids:continue
        rows.append(dict(problem=problem['id'],family=problem['family'],dimension=d,
            piece=problem['piece'],container=problem['container'],n=row['n'],file=row['file'],
            immutable_url='https://raw.githubusercontent.com/alejandrozu/platonic-packing/'+FREEZE+'/'+row['file'],
            index_source_credit={k:row.get(k)for k in ['who','refined_by','source_author','source_url','issue']}))
nd_templates={name:dict(dimension=s['dim'],vertices=len(s['V']),facets=len(s['facets']),edge2=s['edge2'],
    literal_radicands=sorted({int(r)for v in s['V']for c in v for r in re.findall(r'sqrt(\d+)',c)}))for name,s in nd.items()}
report=dict(freeze_git_sha=FREEZE,formal_verification='Preparation only; no Lean build implied',
    remaining_targets=len(rows),by_dimension=dict(Counter(r['dimension']for r in rows)),
    three_d_by_family=dict(Counter(r['family']for r in rows if r['dimension']==3)),
    three_d_templates=templates,three_d_degree_counts=dict(Counter(x['degree']for x in templates.values())),
    nd_templates=nd_templates,geometry_sources=[dict(path='src/solids_exact.json',sha256=hashlib.sha256(solid_path.read_bytes()).hexdigest()),dict(path='src/polytopes_nd.json',sha256=hashlib.sha256(nd_path.read_bytes()).hexdigest())],records=rows)
(HERE/'remaining-targets.json').write_text(json.dumps(encode(report),indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items()if k not in ['three_d_templates','nd_templates','records']},indent=2))
print('root_check_failures',[n for n,s in templates.items()if not s['proposed_root_check']])
print('nonzero_centroid_coefficients',[n for n,s in templates.items()if not s['centroid_zero_coefficientwise']])
