"""Independent exact-field check of native rational AP4 witnesses; standard library.

All arithmetic lies in Q(alpha), alpha the positive fourth root of 2.
Face normals and edge-cross-edge axes are derived exactly from complete bodies.
The JSON stores rational centers/quaternions. A quaternion need not be unit:
its exact norm denominator makes the resulting frame a proper rotation.
"""
from pathlib import Path
import json,itertools,sys
from exact_field import K,P,U,B,edges,add,sub,dot,cross,mv,mm,transpose,maxk,h

def frame(q):
    w,x,y,z=map(K,q);n=w*w+x*x+y*y+z*z
    return [[a/n for a in row] for row in [
      [w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)],
      [2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],
      [2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]]]

def verify(path):
    data=json.loads(path.read_text());n=data['n']
    if 'pieces' in data:
        S=K(data['s_full']);scale_label=data['s_full']
        assert data['piece']==data['container']=='antiprism4'
        assert len(data['pieces'])==n
        bodies=[(list(map(K,row[:3])),frame(row[3:]))for row in data['pieces']]
    elif 'frames_wxyz_integer' in data:
        S=K(data['scale']);scale_label=str(float(S))
        bodies=[([K(c[0]),K(c[1]),K(c[2])*h],frame(q))
                for c,q in zip(data['centers_normalized'],data['frames_wxyz_integer'])]
    elif 'normalized_centers' in data:
        S=K(data['scale']);scale_label=str(float(S))
        bodies=[([K(c[0]),K(c[1]),K(c[2])*h],frame([0,1,0,0]if t else[1,0,0,0]))
                for c,t in zip(data['normalized_centers'],data['types'])]
    elif 'physical_centers' in data:
        S=K(data['scale_coefficients']);scale_label=str(float(S))
        bodies=[(list(map(K,c)),[[K(x)for x in row]for row in m])
                for c,m in zip(data['physical_centers'],data['frames'])]
    else:raise ValueError('Unsupported exact witness format')
    assert len(bodies)==n
    vertices=[];normals=[];directions=[]
    for c,M in bodies:
        assert all((v-int(i==j)).sign()==0 for i,r in enumerate(mm(M,transpose(M)))for j,v in enumerate(r))
        assert (dot(M[0],cross(M[1],M[2]))-1).sign()==0
        vs=[add(c,mv(M,p))for p in P];vertices.append(vs)
        normals.append([mv(M,u)for u in U])
        directions.append([sub(vs[j],vs[i])for i,j in edges])
    margins=[];separators=[]
    for i,vs in enumerate(vertices):
        for v in vs:
            for u,b in zip(U,B):
                g=S*b-dot(u,v);assert g.sign()>=0,(i,'host');margins.append(float(g))
    for i,j in itertools.combinations(range(n),2):
        candidates=normals[i]+normals[j]+[cross(e,f)for e in directions[i]for f in directions[j]]
        for u in candidates:
            if dot(u,u).sign()==0:continue
            a=[dot(u,v)for v in vertices[i]];b=[dot(u,v)for v in vertices[j]]
            g=-maxk([-v for v in b])-maxk(a)
            if g.sign()<0:
                g=-maxk([-v for v in a])-maxk(b);u=[-v for v in u]
            if g.sign()>=0:
                separators.append({'pair':[i,j],'normal':[v.out()for v in u],'gap':g.out()});break
        else:raise ValueError(f'No full-body separator for {i},{j}')
    receipt={'status':'PASS_EXACT_FIELD','n':n,'scale_coefficients':S.out(),'proper_rotations':n,
       'host_vertex_inequalities':len(margins),'minimum_host_slack':min(margins),
       'complete_body_pairs':len(separators),'separators':separators}
    path.with_name(path.stem+'_exact_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'PASS: N={n}, S={scale_label}; {len(margins)} host checks, {len(separators)} pair checks.')
    return receipt

if __name__=='__main__':
    verify(Path(sys.argv[1])if len(sys.argv)>1 else Path(__file__).with_name('n5_native.json'))
