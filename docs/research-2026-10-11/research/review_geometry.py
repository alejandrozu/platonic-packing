from pathlib import Path
import argparse,importlib.util,json,shutil,subprocess,sys
import numpy as np

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--analysis',type=Path,default=ROOT.parent/'analysis/analyze_records.py')
p.add_argument('--out',type=Path,required=True)
p.add_argument('--node',default=shutil.which('node'))
args=p.parse_args();REPO=args.repo.resolve();NODE=args.node
if not NODE:raise RuntimeError('Node.js must be available on PATH, or provided with --node')
spec=importlib.util.spec_from_file_location('analysis',args.analysis)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
solid=json.loads((REPO/'src/solids.json').read_text())
rng=np.random.default_rng(20261011)
rows=[];ori=[]
for name,d in solid.items():
    V=np.array(d['V']);N=np.array(d['normals'])
    group=a.symmetry_group(V,a.EXPECTED_GROUPS[name])
    closure=max(float(np.min(np.linalg.norm(group-(g@h),axis=(1,2))))for g in group for h in group)
    for _ in range(500):
        qa=rng.normal(size=4);qa/=np.linalg.norm(qa)
        qb=rng.normal(size=4);qb/=np.linalg.norm(qb)
        direction=rng.normal(size=3);direction/=np.linalg.norm(direction)
        cb=direction*rng.uniform(1.3,3.0)*d['circumradius']
        rows.append(dict(piece=name,ca=[0,0,0],cb=cb.tolist(),qa=qa.tolist(),qb=qb.tolist(),kind='random'))
    maxinv=0
    for _ in range(20):
        qa=rng.normal(size=4);qb=rng.normal(size=4);qc=rng.normal(size=4)
        Ri,Rj,Q=a.qrot(qa),a.qrot(qb),a.qrot(qc)
        base=a.angle_matrix(np.array([Ri,Rj]),group)[0,1]
        gi,gj=group[rng.integers(len(group))],group[rng.integers(len(group))]
        alt=a.angle_matrix(np.array([Q@Ri@gi,Q@Rj@gj]),group)[0,1]
        maxinv=max(maxinv,abs(base-alt))
    ori.append(dict(piece=name,group_order=len(group),max_closure_frobenius_error=closure,max_disorientation_invariance_error_deg=maxinv))
    assert closure<1e-10 and maxinv<1e-8

# Add actual certified near pairs, including small projection gaps with larger real distance.
for path in sorted((REPO/'records').glob('*/*_n40.json')):
    d=json.loads(path.read_text());s=solid[d['piece']];V=np.array(s['V']);N=np.array(s['normals'])
    FA=a.uniq_dirs(N);ED=a.uniq_dirs([V[j]-V[i]for i,j in s['edges']]);poses=np.array(d['pieces'])
    R=np.array([a.qrot(p[3:])for p in poses]);W=np.array([V@r.T+c for r,c in zip(R,poses[:,:3])])
    from itertools import combinations
    for i,j in combinations(range(d['n']),2):
        if np.linalg.norm(poses[i,:3]-poses[j,:3])>2*s['circumradius']+.001:continue
        gap=a.sat_gap(W[i],W[j],FA@R[i].T,FA@R[j].T,ED@R[i].T,ED@R[j].T)
        if gap>.001:continue
        rows.append(dict(piece=d['piece'],ca=poses[i,:3].tolist(),cb=poses[j,:3].tolist(),qa=poses[i,3:].tolist(),qb=poses[j,3:].tolist(),kind='record_near',record=d['record_id'],i=i,j=j))

run=subprocess.run([str(NODE),str(ROOT/'review_geometry.js'),str(REPO)],input=json.dumps(rows),capture_output=True,text=True,check=True)
results=[json.loads(l)for l in run.stdout.splitlines()]
assert len(results)==len(rows)
summary={};worst=[]
for row,result in zip(rows,results):
    if result['sd']<=0:continue
    d=solid[row['piece']];V=np.array(d['V']);N=np.array(d['normals']);Ra=a.qrot(row['qa']);Rb=a.qrot(row['qb'])
    va=V@Ra.T+row['ca'];vb=V@Rb.T+row['cb']
    dist=a.poly_distance(va,vb,d['faces'],d['edges'],N@Ra.T,N@Rb.T)
    err=abs(dist-result['sd']);key=row['piece']+'/'+row['kind']
    st=summary.setdefault(key,dict(count=0,max_absolute_error=0,threshold_classification_differences=0))
    st['count']+=1;st['max_absolute_error']=max(st['max_absolute_error'],err)
    st['threshold_classification_differences']+=sum((dist<=e)!=(result['sd']<=e)for e in a.CONTACT_TOLS)
    if err>1e-8:worst.append(dict(**row,analysis_distance=dist,kernel_distance=result['sd'],error=err))
out=dict(random_seed=20261011,total_requests=len(rows),orientation_checks=ori,distance_checks=summary,discrepancies_over_1e_8=worst)
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
assert not worst
assert all(st['threshold_classification_differences']==0 for st in summary.values())
