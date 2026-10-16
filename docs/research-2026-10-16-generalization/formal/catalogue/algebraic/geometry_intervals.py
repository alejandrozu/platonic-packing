"""Export exact algebraic template expressions and checked rational enclosures.

No geometry is rounded or changed: the semantic vertex is the source Horner
polynomial at the source's unique isolated real root, with its source D scale.
Only enclosing interval endpoints are rounded outward.  This Python preparation
is not a Lean verification receipt.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
from math import isqrt

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parents[1]
SOURCE=HERE/'inputs/src/solids_exact.json'

def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[1],-a[0]
def mul(a,b):
    v=[x*y for x in a for y in b]
    return min(v),max(v)
def inverse(a):
    if not a[0]>0:raise ValueError('positive reciprocal interval required')
    return 1/a[1],1/a[0]
def evaluate(p,a):
    v=(Q(0),Q(0))
    for c in reversed(p):v=add((Q(c),Q(c)),mul(a,v))
    return v
def slope(p,a):
    return (Q(0),Q(0)) if not p else add(evaluate(p[1:],a),mul(a,slope(p[1:],a)))
def outward(a,bits):
    scale=1<<bits
    return Q(a[0]*scale//1,scale),Q(-((-a[1]*scale)//1),scale)
def square_root(a,bits):
    if a[0]<0:raise ValueError('negative square root interval')
    scale=1<<bits
    lo=isqrt((a[0].numerator*scale*scale)//a[0].denominator)
    hi=isqrt((a[1].numerator*scale*scale)//a[1].denominator)+1
    candidate=(Q(lo,scale),Q(hi,scale))
    assert 0<=candidate[0] and candidate[0]**2<=a[0] and a[1]<=candidate[1]**2
    return candidate
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v)for v in x]
    return x
def rat(x):
    x=Q(x)
    return f'({x.numerator} : ℚ)' if x.denominator==1 else f'(({x.numerator} : ℚ) / {x.denominator})'
def interval(a):return '⟨'+rat(a[0])+', '+rat(a[1])+'⟩'
def polynomial(p):return '['+', '.join(rat(x)for x in p)+']'
def vector(xs,render):return '!['+', '.join(render(x)for x in xs)+']'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--bits',type=int,default=170)
    parser.add_argument('--lean',action='store_true',help='also emit canonical RootData and TemplateData source, without claiming compilation')
    args=parser.parse_args()
    raw=SOURCE.read_bytes();solids=json.loads(raw);roots={};templates={}
    for name,s in solids.items():
        p=list(map(Q,s['minpoly']));a=tuple(map(Q,s['interval']))
        key=(tuple(p),a)
        if key not in roots:
            left=evaluate(p,(a[0],a[0]))[0];right=evaluate(p,(a[1],a[1]))[0];sl=slope(p,a)
            assert a[0]<a[1] and left*right<0 and (sl[0]>0 or sl[1]<0),name
            roots[key]=dict(id=f'root{len(roots)}',polynomial=p,interval=a,endpoint_values=[left,right],slope_interval=sl)
        root=roots[key]
        D=None if s['D'] is None else list(map(Q,s['D']))
        sqrtI=(Q(1),Q(1)) if D is None else square_root(evaluate(D,a),args.bits)
        norm=(Q(1),Q(1)) if D is None else inverse(sqrtI)
        coeff=[[[Q(c)for c in coordinate]for coordinate in v]for v in s['V']]
        vertices=[[outward(mul(norm,evaluate(c,a)),args.bits)for c in v]for v in coeff]
        assert all(all(sum((v[a][j]for v in coeff),Q(0))==0 for j in range(len(p)-1))for a in range(3)),name
        templates[name]=dict(root_id=root['id'],dimension=3,vertex_count=len(coeff),coefficients=coeff,
            normalizer_polynomial=D,normalizer_sqrt_interval=sqrtI,normalizer_interval=norm,
            vertex_intervals=vertices,centroid_zero_coefficientwise=True,faces=s['faces'])
    report=dict(schema='algebraic-template-intervals-v1',status='EXPORTED_NOT_LEAN_VERIFIED',
        geometry_path='src/solids_exact.json',geometry_sha256=hashlib.sha256(raw).hexdigest(),
        semantic_vertices='exact source polynomials at unique source-interval roots, optionally divided by sqrt(D)',
        interval_rounding_bits=args.bits,roots=list(roots.values()),templates=templates)
    out=HERE/'geometry-intervals.json'
    out.write_bytes((json.dumps(encode(report),indent=2)+'\n').replace('\n','\r\n').encode('utf8'))
    if args.lean:
        lean=FORMAL/'PackingCertificates/Algebraic/Generated'
        lean.mkdir(exist_ok=True)
        lines=['import PackingCertificates.Algebraic.Template','', 'set_option maxRecDepth 0','set_option maxHeartbeats 0','',
            'namespace PackingCertificates.Algebraic.Generated','']
        for r in roots.values():
            n=r['id']
            lines.extend([f'def {n} : RootSpec := ⟨{polynomial(r["polynomial"])}, {interval(r["interval"])}⟩',
                f'theorem {n}_checked : {n}.check = true := by decide +kernel',''])
        lines.extend(['end PackingCertificates.Algebraic.Generated',''])
        (lean/'RootData.lean').write_bytes('\n'.join(lines).replace('\n','\r\n').encode('utf8'))
        for name,t in templates.items():
            D=t['normalizer_polynomial']
            rows=['import PackingCertificates.Algebraic.Generated.RootData','', 'set_option maxRecDepth 0','set_option maxHeartbeats 0','',
                'namespace PackingCertificates.Algebraic.Generated','',
                f'def {name} : TemplateData 3 {t["vertex_count"]} where',
                f'  rootSpec := {t["root_id"]}',
                '  coefficients := '+vector(t['coefficients'],lambda v:vector(v,polynomial)),
                '  normalizerPolynomial := '+('none'if D is None else '(some '+polynomial(D)+')'),
                '  normalizerSqrtInterval := '+interval(t['normalizer_sqrt_interval']),
                '  vertexIntervals := '+vector(t['vertex_intervals'],lambda v:vector(v,interval)),
                '',f'theorem {name}_normalization_checked : {name}.normalizationCheck = true := by decide +kernel',
                f'theorem {name}_vertices_checked : {name}.verticesCheck = true := by decide +kernel',
                f'theorem {name}_centroid_checked : {name}.centroidCheck {len(t["coefficients"][0][0])} = true := by decide +kernel',
                f'theorem {name}_centered : (∑ j, {name}.vertex {t["root_id"]}_checked j) = 0 :=',
                f'  {name}.centroid_sound {len(t["coefficients"][0][0])} {t["root_id"]}_checked {name}_centroid_checked',
                '',f'theorem {name}_vertices_enclosed (j : Fin {t["vertex_count"]}) (a : Fin 3) :',
                f'    ({name}.vertexIntervals j a).Contains ({name}.vertex {t["root_id"]}_checked j a) :=',
                f'  {name}.vertices_sound {t["root_id"]}_checked {name}_normalization_checked {name}_vertices_checked j a',
                '', 'end PackingCertificates.Algebraic.Generated','']
            (lean/(name+'.lean')).write_bytes('\n'.join(rows).replace('\n','\r\n').encode('utf8'))
    print(json.dumps(dict(templates=len(templates),root_specs=len(roots),vertices=sum(t['vertex_count']for t in templates.values()),
        generated_lean=args.lean,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),status=report['status'])))

if __name__=='__main__':main()
