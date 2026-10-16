"""Exact ND root/coordinate/edge-ratio-normalization certificate preparation."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,itertools,json,re
from geometry_intervals import evaluate,mul,inverse,outward,square_root,rat,interval,polynomial,vector,encode

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parents[1]
SOURCE=HERE/'inputs/src/polytopes_nd.json'
BITS=170

def parse_mq(s):
    result={}
    for term in re.findall(r'[+-]?[^+-]+',str(s).replace(' ','')):
        if 'sqrt'in term:
            a,b=term.split('sqrt');a=a.rstrip('*')
            coefficient=Q(1)if a in ('','+')else Q(-1)if a=='-'else Q(a)
            radicand=int(b)
        else:coefficient=Q(term);radicand=1
        result[radicand]=result.get(radicand,Q(0))+coefficient
    return {r:c for r,c in result.items()if c}

def qmul(x,y,r):return x[0]*y[0]+r*x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def qadd(x,y):return x[0]+y[0],x[1]+y[1]
def qneg(x):return -x[0],-x[1]
def qinv(x,r):
    den=x[0]*x[0]-r*x[1]*x[1]
    if not den:raise ValueError('singular quadratic-field pivot')
    return x[0]/den,-x[1]/den

def inverse_matrix(A,r):
    k=len(A);a=[[tuple(c)for c in row]+[(Q(int(i==j)),Q(0))for j in range(k)]for i,row in enumerate(A)]
    for j in range(k):
        pivot=next((i for i in range(j,k)if a[i][j]!=(0,0)),None)
        if pivot is None:raise ValueError('singular quadratic-field matrix')
        a[j],a[pivot]=a[pivot],a[j];rec=qinv(a[j][j],r);a[j]=[qmul(x,rec,r)for x in a[j]]
        for i in range(k):
            if i==j:continue
            multiplier=a[i][j]
            a[i]=[qadd(x,qneg(qmul(multiplier,y,r)))for x,y in zip(a[i],a[j])]
    B=[row[k:]for row in a]
    for i,j in itertools.product(range(k),repeat=2):
        v=(Q(0),Q(0))
        for z in range(k):v=qadd(v,qmul(A[i][z],B[z][j],r))
        if v!=(int(i==j),0):raise ValueError('quadratic matrix inverse failed exact replay')
    return B

def shape_radicand(shape):
    rs={r for v in shape['V']for c in v for r in parse_mq(c)if r!=1}
    if len(rs)>1:raise ValueError('canonical ND geometry needs multiple primitive roots')
    return next(iter(rs),2)

def pairs(shape,r):
    out=[]
    for v in shape['V']:
        row=[]
        for c in v:
            q=parse_mq(c)
            if set(q)-{1,r}:raise ValueError('coordinate primitive root mismatch')
            row.append((q.get(1,Q(0)),q.get(r,Q(0))))
        out.append(row)
    return out

def mu_parameters(text):
    q=parse_mq(text)
    if set(q)<={1,5}:return q.get(1,Q(0)),q.get(5,Q(0)),False
    if set(q)<={2,10}:return q.get(2,Q(0)),q.get(10,Q(0)),True
    raise ValueError('unsupported native edge-ratio expression '+str(text))

def render_template(name,t):
    rows=['import PackingCertificates.Algebraic.Generated.ND.RootData','',
        'set_option maxRecDepth 1000000','set_option maxHeartbeats 0','',
        'namespace PackingCertificates.Algebraic.Generated.ND','',
        f'def {name} : TemplateData {t["dimension"]} {t["vertex_count"]} where',
        f'  rootSpec := nd_root{t["radicand"]}',
        '  coefficients := '+vector(t['coefficients'],lambda v:vector(v,polynomial)),
        '  normalizerPolynomial := '+('none'if t['D']is None else 'some '+polynomial(t['D'])),
        '  normalizerSqrtInterval := '+interval(t['normalizer_sqrt_interval']),
        '  vertexIntervals := '+vector(t['vertex_intervals'],lambda v:vector(v,interval)),
        '',f'theorem {name}_normalization_checked : {name}.normalizationCheck = true := by decide +kernel',
        f'theorem {name}_vertices_checked : {name}.verticesCheck = true := by decide +kernel',
        f'theorem {name}_centroid_checked : {name}.centroidCheck 2 = true := by decide +kernel','',
        'end PackingCertificates.Algebraic.Generated.ND','']
    return '\n'.join(rows).replace('\n','\r\n').encode('utf8')

def emit_template(name,t,lean):
    (lean/(name+'.lean')).write_bytes(render_template(name,t))

def render_root_data(roots):
    """Pure canonical rendering, also checked against every published source."""
    roots={int(r):data for r,data in roots.items()}
    rows=['import PackingCertificates.Algebraic.RootSqrt','','set_option maxRecDepth 1000000','set_option maxHeartbeats 0','','namespace PackingCertificates.Algebraic.Generated.ND','']
    for r,data in roots.items():rows +=[f'def nd_root{r} : RootSpec := ⟨{polynomial(data["polynomial"])}, {interval(data["interval"])}⟩',f'theorem nd_root{r}_checked : nd_root{r}.check = true := by decide +kernel','']
    for r in roots:
        rows +=[f'def nd_root{r}_literal : QuadraticScale.Spec :=',
            f'  ⟨nd_root{r}, {rat(r)}, 1, 0, false, 1, 0, {interval(roots[2]["interval"])}⟩',
            f'theorem nd_root{r}_literal_checked : nd_root{r}_literal.check = true := by decide +kernel',
            f'theorem nd_root{r}_is_sqrt : nd_root{r}.root nd_root{r}_checked = Real.sqrt ({r} : ℝ) := by',
            f'  simpa [nd_root{r}_literal] using nd_root{r}_literal.root_eq_sqrt nd_root{r}_checked nd_root{r}_literal_checked','']
    rows+=['end PackingCertificates.Algebraic.Generated.ND','']
    return '\n'.join(rows).replace('\n','\r\n').encode('utf8')

def main():
    raw=SOURCE.read_bytes();solids=json.loads(raw);roots={r:dict(polynomial=[Q(-r),Q(0),Q(1)],interval=square_root((Q(r),Q(r)),BITS))for r in [2,5,6,7]}
    minimum={}
    for row in json.loads((HERE/'remaining-targets.json').read_text(encoding='utf8'))['records']:
        if row['dimension']<=3:continue
        if row['problem']not in minimum or row['n']<minimum[row['problem']]['n']:minimum[row['problem']]=row
    templates={};scales={}
    def build(name,pid,r,D):
        rawpair=pairs(solids[pid],r);a=roots[r]['interval']
        sqrtI=(Q(1),Q(1))if D is None else square_root(evaluate(D,a),BITS)
        norm=(Q(1),Q(1))if D is None else inverse(sqrtI)
        VI=[[outward(mul(norm,evaluate(c,a)),BITS)for c in v]for v in rawpair]
        assert all(sum((v[k][j]for v in rawpair),Q(0))==0 for k in range(solids[pid]['dim'])for j in range(2))
        templates[name]=dict(source_shape=pid,radicand=r,dimension=solids[pid]['dim'],vertex_count=len(rawpair),
            coefficients=rawpair,D=D,normalizer_sqrt_interval=sqrtI,normalizer_interval=norm,vertex_intervals=VI)
    for pid,s in solids.items():build('piece_'+pid,pid,shape_radicand(s),None)
    for problem,row in minimum.items():
        rec=json.loads((HERE/'inputs'/row['file']).read_bytes());a,b,e=mu_parameters(rec['mu']);r=shape_radicand(solids[row['container']])
        if b and r!=5:
            if any(c[1]for v in pairs(solids[row['container']],r)for c in v):raise ValueError('incompatible geometry/ratio root')
            r=5
        factor=2 if e else 1;m0=factor*(a*a+r*b*b);m1=factor*2*a*b;den=m0*m0-r*m1*m1
        D=[m0/den,-m1/den]
        assert m0*D[0]+r*m1*D[1]==1 and m0*D[1]+m1*D[0]==0
        build('container_'+problem,row['container'],r,D)
        scales[problem]=dict(source_mu=rec['mu'],radicand=r,a=a,b=b,times_sqrt_two=e,d0=D[0],d1=D[1],sqrt_two_interval=roots[2]['interval'])
    output=dict(schema='nd-quadratic-geometry-v1',status='PREPARATION_NOT_FORMAL_VERIFICATION',
        geometry_path='src/polytopes_nd.json',geometry_sha256=hashlib.sha256(raw).hexdigest(),roots=roots,templates=templates,scales=scales,pilot_records=list(minimum.values()))
    (HERE/'geometry-intervals-nd.json').write_bytes((json.dumps(encode(output),indent=2)+'\n').replace('\n','\r\n').encode('utf8'))
    lean=FORMAL/'PackingCertificates/Algebraic/Generated/ND';lean.mkdir(exist_ok=True)
    (lean/'RootData.lean').write_bytes(render_root_data(roots))
    for name,t in templates.items():emit_template(name,t,lean)
    print(json.dumps(dict(templates=len(templates),roots=len(roots),pilot_families=len(minimum),status=output['status'])))

if __name__=='__main__':main()
