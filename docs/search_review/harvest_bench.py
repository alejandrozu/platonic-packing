import json, glob, os, sys, shutil
sys.path.insert(0,'scripts'); import engine
files=sys.argv[2:]; out=sys.argv[1]
best={}
for f in files:
    for l in open(f):
        r=json.loads(l)
        if not r.get('beat') or 'C' not in r: continue
        k=(r['p'],r['n'])
        if k not in best or r['s']<best[k]['s']: best[k]=r
shutil.rmtree(out, ignore_errors=True)
for (p,n),r in best.items():
    os.makedirs(os.path.join(out,p),exist_ok=True)
    src={'move':'bench-'+r['method'], **{k:r[k] for k in ('k','det','dfix','a','b','delta','from','minDiff') if k in r}}
    json.dump({'best':{'s':r['s'],'C':r['C'],'Q':r['Q'],'src':src}}, open(os.path.join(out,p,f'n{n:02d}.json'),'w'))
print(len(best),'cases with a bench improvement')
engine.harvest(out,'bench')
