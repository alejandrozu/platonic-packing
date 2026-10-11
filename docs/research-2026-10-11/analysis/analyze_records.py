#!/usr/bin/env python3
"""Reproduce Paper 2 from frozen record JSON. Requires NumPy; plots require Matplotlib.

Usage: python analyze_records.py --repo /path/to/platonic-packing --out /path/to/analysis
All output is empirical. Exact feasibility is delegated to certify_exact.py.
"""
from pathlib import Path
import argparse, csv, hashlib, json, math, platform, subprocess, sys
from itertools import combinations
import numpy as np

ORDER = ['tetintet','octinoct','icoinico','dodindod','cubincub','cubinoct','octincub','dodinico','icoindod']
ANG_TOLS = [0.1, 1.0, 5.0]
CONTACT_TOLS = [1e-5,1e-4,1e-3]
EXPECTED_GROUPS = {'tetrahedron':12,'cube':24,'octahedron':24,'dodecahedron':60,'icosahedron':60}

def write_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def plateau_runs(rows,col,tol):
    """Maximal sequential runs whose WHOLE min/max range is within tolerance."""
    start=0;lo=hi=rows[0][col];runs=[]
    for idx in range(1,len(rows)+1):
        value=rows[idx][col] if idx<len(rows) else None
        end=idx==len(rows) or max(hi,value)-min(lo,value)>tol
        if end:
            if idx-start>1:runs.append((start,idx,lo,hi))
            if idx<len(rows):start=idx;lo=hi=value
        else:lo=min(lo,value);hi=max(hi,value)
    return runs

def qrot(q):
    q=np.array(q,dtype=float);q=q/np.linalg.norm(q);w,x,y,z=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
                     [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
                     [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])

def frame(a,b):
    x=a/np.linalg.norm(a); y=b-np.dot(b,x)*x;y/=np.linalg.norm(y)
    return np.column_stack([x,y,np.cross(x,y)])

def symmetry_group(V, expected):
    # Every proper symmetry is determined by the image of two non-collinear vertices.
    a=V[0];b=next(v for v in V[1:] if np.linalg.norm(np.cross(a,v))>1e-8)
    ref=frame(a,b);dot0=np.dot(a,b);Gs=[]
    for c in V:
        for d in V:
            if abs(np.dot(c,d)-dot0)>1e-8 or np.linalg.norm(np.cross(c,d))<1e-8:continue
            G=frame(c,d)@ref.T; W=V@G.T
            if np.max(np.min(np.linalg.norm(W[:,None,:]-V[None,:,:],axis=2),axis=1))<1e-8:
                if all(np.linalg.norm(G-H)>1e-7 for H in Gs):Gs.append(G)
    assert len(Gs)==expected,(len(Gs),expected)
    for G in Gs:
        assert np.max(np.abs(G.T@G-np.eye(3)))<1e-12 and np.linalg.det(G)>1-1e-12
    return np.array(Gs)

def angle_matrix(R,G):
    n=len(R);out=np.zeros((n,n))
    for i,j in combinations(range(n),2):
        D=R[i].T@R[j]
        trace=np.einsum('ij,gji->g',D,G).max()
        out[i,j]=out[j,i]=np.degrees(np.arccos(np.clip((trace-1)/2,-1,1)))
    return out

def components(n,edges):
    parents=list(range(n))
    def root(a):
        while parents[a]!=a:parents[a]=parents[parents[a]];a=parents[a]
        return a
    for a,b in edges:
        a=root(a);b=root(b)
        if a!=b:parents[b]=a
    groups={}
    for i in range(n):groups.setdefault(root(i),[]).append(i)
    return sorted(groups.values(),key=lambda a:(-len(a),a[0]))

def uniq_dirs(dirs):
    ans=[]
    for v in dirs:
        v=v/np.linalg.norm(v)
        if all(abs(np.dot(v,w))<1-1e-9 for w in ans):ans.append(v)
    return np.array(ans)

def sat_gap(A,B,FA,FB,EA,EB):
    cross=np.cross(EA[:,None,:],EB[None,:,:]).reshape(-1,3)
    cross=cross[np.linalg.norm(cross,axis=1)>1e-9]
    cross=cross/np.linalg.norm(cross,axis=1)[:,None]
    axes=np.concatenate([FA,FB,cross],axis=0)
    pa=A@axes.T;pb=B@axes.T
    return np.max(np.maximum(pb.min(axis=0)-pa.max(axis=0),pa.min(axis=0)-pb.max(axis=0)))

def poly_distance(A,B,faces,edges,NA,NB):
    """Euclidean distance: vertex-face projections and all segment-segment distances.
    For disjoint convex polytopes, a closest pair has one of these feature types.
    Segment interior critical points plus four endpoint projections cover degeneracies.
    """
    best=float('inf')
    for X,Y,N in [(A,B,NB),(B,A,NA)]:
        for idx,n in zip(faces,N):
            poly=Y[idx];sd=(X-poly[0])@n;proj=X-sd[:,None]*n
            side=np.cross(poly[np.roll(np.arange(len(poly)),-1)]-poly,proj[:,None,:]-poly[None,:,:])@n
            inside=(side.min(axis=1)>=-1e-10)|(side.max(axis=1)<=1e-10)
            if inside.any():best=min(best,float(np.abs(sd[inside]).min()))
    aa=A[np.array(edges)[:,0]];ab=A[np.array(edges)[:,1]]
    ba=B[np.array(edges)[:,0]];bb=B[np.array(edges)[:,1]]
    U=ab-aa;V=bb-ba
    def endpoint_to_segments(P,C,D):
        v=D-C;z=P[:,None,:]-C[None,:,:]
        t=np.einsum('ijk,jk->ij',z,v)/(v*v).sum(axis=1)[None,:]
        diff=z-np.clip(t,0,1)[:,:,None]*v[None,:,:]
        return np.einsum('ijk,ijk->ij',diff,diff).min()
    b2=min(endpoint_to_segments(aa,ba,bb),endpoint_to_segments(ab,ba,bb),
           endpoint_to_segments(ba,aa,ab),endpoint_to_segments(bb,aa,ab))
    w=aa[:,None,:]-ba[None,:,:];a=(U*U).sum(axis=1)[:,None];c=(V*V).sum(axis=1)[None,:]
    b=U@V.T;d=np.einsum('ijk,ik->ij',w,U);e=np.einsum('ijk,jk->ij',w,V)
    den=a*c-b*b;safe=np.where(den>1e-14,den,1)
    s=(b*e-c*d)/safe;t=(a*e-b*d)/safe
    interior=(den>1e-14)&(s>=0)&(s<=1)&(t>=0)&(t<=1)
    if interior.any():
        diff=w+s[:,:,None]*U[:,None,:]-t[:,:,None]*V[None,:,:]
        b2=min(b2,np.einsum('ijk,ijk->ij',diff,diff)[interior].min())
    return min(best,math.sqrt(max(float(b2),0)))

def self_tests():
    # Distances distinguish real contacts from merely small SAT lower bounds.
    V=np.array([[x,y,z] for x in [-.5,.5] for y in [-.5,.5] for z in [-.5,.5]])
    faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
    N=np.array([[-1,0,0],[1,0,0],[0,-1,0],[0,1,0],[0,0,-1],[0,0,1]])
    edges=[(i,j) for i,j in combinations(range(8),2) if np.linalg.norm(V[i]-V[j])==1]
    for shift,expect in [([1.001,0,0],.001),([1.1,1.2,0],math.sqrt(.05)),([1.1,1.2,1.3],math.sqrt(.14))]:
        assert abs(poly_distance(V,V+shift,faces,edges,N,N)-expect)<1e-10
    assert plateau_runs([{'x':0},{'x':.75},{'x':-.75}],'x',1)==[(0,2,0,.75)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();repo=args.repo.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    self_tests()
    sd=json.loads((repo/'src/solids.json').read_text(encoding='utf-8'))
    geo={}
    for name,d in sd.items():
        V=np.array(d['V']);normals=np.array(d['normals']);edges=d['edges']
        geo[name]=(V,normals,edges,uniq_dirs(normals),uniq_dirs([V[j]-V[i] for i,j in edges]),symmetry_group(V,EXPECTED_GROUPS[name]))
    sourcefiles=sorted((repo/'records').glob('*/*_n[0-9][0-9].json'))
    manifest=[];records=[];pairs=[];details={}
    for k,path in enumerate(sourcefiles):
        raw=path.read_bytes();d=json.loads(raw);pid=d['record_id'].split('_')[0];n=d['n']
        manifest.append({'path':path.relative_to(repo).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
        assert n==len(d['pieces'])
        P=d['piece'];C=d['container'];vp=sd[P]['volume'];vc=sd[C]['volume'];s=d['s_full'];st=d['s_tight']
        L=(n*vp/vc)**(1/3);density=n*vp/(vc*s**3)
        assert abs(density-d['density'])<1e-12
        V,N,E,FA,ED,G=geo[P];poses=np.array(d['pieces']);R=np.array([qrot(p[3:]) for p in poses]);centres=poses[:,:3]
        W=np.array([V@r.T+c for r,c in zip(R,centres)]);FN=np.array([N@r.T for r in R]);F=np.array([FA@r.T for r in R]);D=np.array([ED@r.T for r in R])
        angles=angle_matrix(R,G);maxcontact=max(CONTACT_TOLS);ce={x:[] for x in CONTACT_TOLS};mind=float('inf')
        for i,j in combinations(range(n),2):
            cd=float(np.linalg.norm(centres[i]-centres[j]));dist=None;sat=None
            if cd<=2*sd[P]['circumradius']+maxcontact:
                sat=float(sat_gap(W[i],W[j],F[i],F[j],D[i],D[j]))
                if sat<=maxcontact:
                    dist=float(poly_distance(W[i],W[j],sd[P]['faces'],E,FN[i],FN[j]));mind=min(mind,dist)
                    for eps in CONTACT_TOLS:
                        if dist<=eps:ce[eps].append((i,j))
            pairs.append({'record_id':d['record_id'],'i':i,'j':j,'misorientation_deg':float(angles[i,j]),'centre_distance':cd,'sat_lower_bound':sat,'euclidean_distance_if_near':dist})
        cn=np.array(sd[C]['normals']);rho=sd[C]['inradius'];wall=s*rho-np.einsum('ivk,fk->ivf',W,cn)
        row={'record_id':d['record_id'],'problem':pid,'piece':P,'container':C,'n':n,'s_full':s,'s_full_hex':float(s).hex(),'s_tight':st,
             'volume_bound':L,'normalized_scale':s/L,'density':density,'linear_volume_bound_gap_pct':100*(s/L-1),
             'closed_form_conjecture':d.get('closed_form_conjecture') or '', 'search_move':(d.get('search')or{}).get('move',''),
             'derived_from':d.get('derived_from',''),'certificate_text_present':path.with_suffix('.certify.txt').exists(),
             'pair_angle_median_deg':float(np.median(angles[np.triu_indices(n,1)])),
             'pair_angle_mean_deg':float(np.mean(angles[np.triu_indices(n,1)])), 'minimum_near_pair_distance':mind,
             'pair_angle_max_deg':float(angles.max()),
             'minimum_wall_gap':float(wall.min())}
        det={'orientation_components':{},'contacts':{},'grains':{}}
        for tol in ANG_TOLS:
            cl=components(n,[(i,j)for i,j in combinations(range(n),2)if angles[i,j]<=tol]);key=str(tol)
            sizes=[len(g)for g in cl];entropy=-sum((a/n)*math.log(a/n)for a in sizes)/math.log(n)
            row[f'orientation_components_{tol}deg']=len(cl);row[f'orientation_largest_fraction_{tol}deg']=max(sizes)/n
            row[f'orientation_entropy_{tol}deg']=entropy
            row[f'orientation_max_component_diameter_{tol}deg']=max(float(angles[np.ix_(g,g)].max())for g in cl)
            det['orientation_components'][key]=cl
            grain=components(n,[(i,j)for i,j in ce[1e-4]if angles[i,j]<=tol])
            row[f'grains_{tol}deg']=len(grain);row[f'grain_largest_fraction_{tol}deg']=len(grain[0])/n
            det['grains'][key]=grain
        for eps in CONTACT_TOLS:
            edges=ce[eps];cl=components(n,edges);deg=[0]*n
            for i,j in edges:deg[i]+=1;deg[j]+=1
            row[f'contact_edges_{eps}']=len(edges);row[f'contact_components_{eps}']=len(cl);row[f'contact_mean_degree_{eps}']=2*len(edges)/n
            row[f'contact_isolated_pieces_{eps}']=deg.count(0);row[f'wall_near_pieces_{eps}']=int((wall.min(axis=(1,2))<=eps).sum())
            det['contacts'][str(eps)]={'edges':edges,'degrees':deg,'components':cl}
        details[d['record_id']]=det;records.append(row)
        if (k+1)%25==0:print(f'Analyzed {k+1}/{len(sourcefiles)}',flush=True)
    recordfiles={m['path']:m['sha256'] for m in manifest}
    manifest.append({'path':'src/solids.json','sha256':hashlib.sha256((repo/'src/solids.json').read_bytes()).hexdigest(),'bytes':(repo/'src/solids.json').stat().st_size})
    # Certified deletion envelope: any n pieces can be retained from a certified m>=n packing.
    families=[];plateaus=[];largejumps=[]
    for pid in ORDER:
        rr=sorted([r for r in records if r['problem']==pid],key=lambda r:r['n']);assert [r['n']for r in rr]==list(range(2,41))
        best=float('inf');witness=None
        for r in reversed(rr):
            if r['s_full']<best:best=r['s_full'];witness=r['record_id']
            r['envelope_s_full']=best;r['envelope_witness']=witness
        for idx,r in enumerate(rr):
            prev=rr[idx-1]if idx else None
            r['delta_s_full']=r['s_full']-prev['s_full']if prev else None
            r['delta_s_tight']=r['s_tight']-prev['s_tight']if prev else None
            r['relative_edge_increment_pct']=100*(r['s_full']/prev['s_full']-1)if prev else None
            r['relative_volume_increment_pct']=100*((r['s_full']/prev['s_full'])**3-1)if prev else None
            r['density_change']=r['density']-prev['density']if prev else None
            r['count_scaled_edge_increment']=(r['n']-1)*(r['s_full']/prev['s_full']-1)if prev else None
        for kind,col,tol in [('identical_certified_value','s_full',0),('identical_certified_envelope','envelope_s_full',0),('numerical_touching_plateau','s_tight',1e-8)]:
            for start,idx,lo,hi in plateau_runs(rr,col,tol):
                plateaus.append({'problem':pid,'kind':kind,'n_start':rr[start]['n'],'n_end':rr[idx-1]['n'],'length':idx-start,'min_value':lo,'max_value':hi,'tolerance':tol})
        rrj=sorted(rr[1:],key=lambda r:r['relative_edge_increment_pct'],reverse=True)
        for r in rrj[:3]:largejumps.append({k:r[k]for k in ['problem','n','delta_s_full','relative_edge_increment_pct','relative_volume_increment_pct','density_change','count_scaled_edge_increment']})
        med=lambda key:float(np.median([r[key]for r in rr]))
        families.append({'problem':pid,'piece':rr[0]['piece'],'container':rr[0]['container'],'records':len(rr),'s_at_2':rr[0]['s_full'],'s_at_40':rr[-1]['s_full'],
                         'density_at_2':rr[0]['density'],'density_at_40':rr[-1]['density'],'density_max':max(r['density']for r in rr),'density_max_n':max(rr,key=lambda r:r['density'])['n'],
                         'median_density':med('density'),'median_normalized_scale':med('normalized_scale'),'median_orientation_components_1deg':med('orientation_components_1.0deg'),
                         'single_orientation_component_records_1deg':sum(r['orientation_components_1.0deg']==1 for r in rr),
                         'all_pairwise_aligned_records_1deg':sum(r['pair_angle_max_deg']<=1 for r in rr),
                         'all_distinct_records_1deg':sum(r['orientation_components_1.0deg']==r['n']for r in rr),
                         'median_grains_1deg':med('grains_1.0deg'),'median_contact_degree':med('contact_mean_degree_0.0001'),
                         'raw_monotonicity_violations':sum(rr[i]['s_full']<rr[i-1]['s_full']for i in range(1,len(rr))),
                         'envelope_improvements':sum(r['envelope_s_full']<r['s_full']for r in rr),'closed_form_labels':sum(bool(r['closed_form_conjecture'])for r in rr)})
    records.sort(key=lambda r:(ORDER.index(r['problem']),r['n']))
    write_csv(out/'record-metrics.csv',records);write_csv(out/'pair-metrics.csv',pairs);write_csv(out/'family-summary.csv',families)
    write_csv(out/'plateaus.csv',plateaus);write_csv(out/'largest-jumps.csv',largejumps);write_csv(out/'source-manifest.csv',manifest)
    (out/'geometry-details.json').write_text(json.dumps(details,separators=(',',':')),encoding='utf-8')
    correlations=[]
    # Within-family rank correlations: descriptive, not independence tests.
    def rank(x):
        x=np.asarray(x);order=np.argsort(x);out=np.zeros(len(x));i=0
        while i<len(x):
            j=i+1
            while j<len(x)and x[order[j]]==x[order[i]]:j+=1
            out[order[i:j]]=(i+j-1)/2;i=j
        return out
    for pid in ORDER:
        rr=[r for r in records if r['problem']==pid]
        for a,b in [('density','orientation_largest_fraction_1.0deg'),('density','grain_largest_fraction_1.0deg'),('density','contact_mean_degree_0.0001'),('relative_edge_increment_pct','orientation_entropy_1.0deg')]:
            rr2=[r for r in rr if r[a]is not None and r[b]is not None];x=rank([r[a]for r in rr2]);y=rank([r[b]for r in rr2])
            rho=float(np.corrcoef(x,y)[0,1])if x.std()>0 and y.std()>0 else None
            correlations.append({'problem':pid,'x':a,'y':b,'spearman_rho':rho,'records':len(rr2)})
    write_csv(out/'descriptive-correlations.csv',correlations)
    try:
        sha=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
    except Exception:sha='unknown'
    metadata={'source_commit':sha,'source_record_count':len(records),'piece_count':sum(r['n']for r in records),'pair_count':len(pairs),
              'analysis_version':'1.0','numpy_version':np.__version__,'python_version':platform.python_version(),
              'proper_symmetry_group_orders':EXPECTED_GROUPS,'orientation_tolerances_deg':ANG_TOLS,'euclidean_contact_tolerances_piece_edges':CONTACT_TOLS,
              'numerical_plateau_tolerance':1e-8,'source_manifest_combined_sha256':hashlib.sha256(json.dumps(recordfiles,sort_keys=True).encode()).hexdigest(),
              'certificate_status':'source text presence only; independent exact rerun is reported separately'}
    (out/'analysis-metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    plot(records,families,out)
    print(json.dumps(metadata,indent=2));print(json.dumps(families,indent=2))

def plot(records,families,out):
    try:import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    except ImportError:print('Matplotlib unavailable; data complete, plots skipped',flush=True);return
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
    colors=plt.get_cmap('tab10').colors
    fig,axes=plt.subplots(3,3,figsize=(11,8),sharex=True)
    for ax,pid,c in zip(axes.flat,ORDER,colors):
        rr=[r for r in records if r['problem']==pid];n=[r['n']for r in rr]
        ax.plot(n,[r['s_full']for r in rr],color=c,lw=1.8,label='certified upper bound')
        ax.plot(n,[r['volume_bound']for r in rr],color='.35',ls='--',lw=1,label='volume lower bound')
        ax.set_title(pid);ax.set_ylabel('container / piece edge');ax.grid(alpha=.15)
    for ax in axes[-1]:ax.set_xlabel('piece count n')
    axes[0,0].legend(fontsize=7);fig.tight_layout()
    for ext in ['png','svg','pdf']:fig.savefig(out/f'figure-1-scale-curves.{ext}',dpi=220)
    plt.close(fig)
    fig,axes=plt.subplots(3,3,figsize=(11,8),sharex=True)
    for ax,pid,c in zip(axes.flat,ORDER,colors):
        rr=[r for r in records if r['problem']==pid and r['n']>2]
        ax.bar([r['n']for r in rr],[r['relative_edge_increment_pct']for r in rr],color=c,width=.8)
        ax.set_title(pid);ax.set_ylabel('edge increment (%)');ax.grid(axis='y',alpha=.15)
    for ax in axes[-1]:ax.set_xlabel('new piece count n')
    fig.tight_layout()
    for ext in ['png','svg','pdf']:fig.savefig(out/f'figure-2-increments.{ext}',dpi=220)
    plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(10,7))
    for pid,c in zip(ORDER,colors):
        rr=[r for r in records if r['problem']==pid];n=[r['n']for r in rr]
        axes[0,0].plot(n,[r['density']for r in rr],color=c,label=pid,lw=1.2)
        axes[0,1].plot(n,[r['orientation_largest_fraction_1.0deg']for r in rr],color=c,lw=1.2)
        axes[1,0].plot(n,[r['grain_largest_fraction_1.0deg']for r in rr],color=c,lw=1.2)
        axes[1,1].plot(n,[r['contact_mean_degree_0.0001']for r in rr],color=c,lw=1.2)
    for ax,title in zip(axes.flat,['occupied volume fraction','largest orientation component (1 degree)','largest operational grain (1 degree)','mean contact degree (distance <= 1e-4)']):
        ax.set_title(title);ax.set_xlabel('piece count n');ax.grid(alpha=.15)
    axes[0,0].legend(ncol=3,fontsize=6.8);fig.tight_layout()
    for ext in ['png','svg','pdf']:fig.savefig(out/f'figure-3-structure.{ext}',dpi=220)
    plt.close(fig)

if __name__=='__main__':main()
