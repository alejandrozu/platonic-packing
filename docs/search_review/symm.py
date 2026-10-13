import json, glob, itertools, collections, sys
import numpy as np
S=json.load(open('src/solids.json'))
def V(name): return np.array(S[name]['V'],float)
def qR(q):
    w,x,y,z=np.array(q)/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
GC={}
def group(name):
    if name in GC: return GC[name]
    X=V(name); X=X-X.mean(0)
    nr=np.linalg.norm(X,axis=1)
    # choose basis triple: vertices a,b,c linearly independent
    idx=[0]
    for i in range(1,len(X)):
        M=X[idx+[i]]
        if np.linalg.matrix_rank(M,1e-6)==len(idx)+1: idx.append(i)
        if len(idx)==3: break
    A=X[idx].T; Ainv=np.linalg.inv(A)
    D=np.linalg.norm(X[:,None]-X[None],axis=2)
    gs=[]
    for a in range(len(X)):
        if abs(nr[a]-nr[idx[0]])>1e-6: continue
        for b in range(len(X)):
            if abs(nr[b]-nr[idx[1]])>1e-6 or abs(D[a,b]-D[idx[0],idx[1]])>1e-6: continue
            for c in range(len(X)):
                if abs(nr[c]-nr[idx[2]])>1e-6 or abs(D[a,c]-D[idx[0],idx[2]])>1e-6 or abs(D[b,c]-D[idx[1],idx[2]])>1e-6: continue
                M=X[[a,b,c]].T@Ainv
                if np.abs(M@M.T-np.eye(3)).max()>1e-6: continue
                Y=X@M.T
                if np.min(np.linalg.norm(Y[:,None]-X[None],axis=2),axis=1).max()<1e-6: gs.append(M)
    GC[name]=gs; return gs
def sym_order(rec, tol):
    pc=V(rec['piece']); pc=pc-0  # canonical piece centred at origin? assume yes
    cen=np.array(rec.get('container_center') or [0,0,0],float)
    pcs=[]
    for p in rec['pieces']:
        c=np.array(p[:3])-cen; R=qR(p[3:])
        pcs.append((c, pc@R.T + c))
    C=np.array([c for c,_ in pcs])
    ok=[]
    for g in group(rec['container']):
        good=True
        for c,Xv in pcs:
            gc=g@c; j=np.argmin(np.linalg.norm(C-gc,axis=1))
            if np.linalg.norm(C[j]-gc)>tol: good=False; break
            Y=Xv@g.T; Z=pcs[j][1]
            if np.min(np.linalg.norm(Y[:,None]-Z[None],axis=2),axis=1).max()>tol: good=False; break
        if good: ok.append(g)
    return ok
out=collections.Counter(); byfam=collections.defaultdict(collections.Counter); rows=[]
for f in sorted(glob.glob('records/*/*_n[0-9][0-9].json')):
    r=json.load(open(f))
    if 'pieces' not in r or not isinstance(r['pieces'],list): continue
    for tol in (1e-3,):
        g=sym_order(r,tol)
        k=len(g)
        rows.append((r['record_id'],r.get('family'),r['n'],k,len(group(r['container']))))
        out[k]+=1; byfam[r.get('family')][k]+=1
print('symmetry order of records (tol 1e-3, includes identity):', sorted(out.items()))
for fm,c in byfam.items(): 
    tot=sum(c.values()); print(fm, tot, 'nontrivial', sum(v for k,v in c.items() if k>1), f"{sum(v for k,v in c.items() if k>1)/tot:.0%}", sorted(c.items()))
nb=collections.defaultdict(lambda:[0,0])
for rid,fm,n,k,G in rows:
    b='02-08' if n<=8 else '09-16' if n<=16 else '17-28' if n<=28 else '29-40'
    nb[b][0]+=1; nb[b][1]+=k>1
print({b:(a,f'{x/a:.0%}') for b,(a,x) in sorted(nb.items())})
json.dump(rows,open(sys.argv[1],'w'))
