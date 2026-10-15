import json, sys, collections, math, glob
import numpy as np
rs=[]
for f in sys.argv[1:]:
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        if 'error' in r or 's' not in r: continue
        rs.append(r)
print('attempts', len(rs))
M=collections.defaultdict(list)
for r in rs: M[r['method']].append(r)
print(f"{'method':11s} {'att':>5s} {'beat':>5s} {'rate':>6s} {'s/att':>6s} {'beats/CPUh':>10s} {'gain/CPUh':>10s} {'med gap':>8s} {'p10 gap':>8s} {'mean gain|beat':>14s}")
for m,v in sorted(M.items()):
    a=len(v); b=sum(r['beat'] for r in v); t=sum(r['secs'] for r in v)
    gaps=np.array([r['s']/r['rec']-1 for r in v]); gain=sum(max(0,math.log(r['rec']/r['s'])) for r in v)
    print(f"{m:11s} {a:5d} {b:5d} {b/a:6.1%} {t/a:6.1f} {b/(t/3600):10.2f} {gain/(t/3600):10.2e} {np.median(gaps):8.4f} {np.quantile(gaps,0.1):8.4f} {(gain/b if b else 0):14.2e}")
# per case best per method (relative to record)
cases=sorted({(r['p'],r['n']) for r in rs})
print('\nper case: best s/rec-1 by method (beats marked *)')
meths=sorted(M)
print(f"{'case':16s} "+' '.join(f'{m:>11s}' for m in meths))
wins=collections.Counter()
for c in cases:
    row=[]; bestm=None; bests=1e9
    for m in meths:
        v=[r for r in M[m] if (r['p'],r['n'])==c]
        if not v: row.append(f"{'-':>11s}"); continue
        x=min(r['s']/r['rec']-1 for r in v); row.append(f"{x:+.4f}({len(v):2d})".rjust(11))
        if x<bests: bests=x; bestm=m
    if bests< -1e-9: wins[bestm]+=1
    print(f"{c[0]+':'+str(c[1]):16s} "+' '.join(row))
print('cases where method found the overall best (and beat the record):', dict(wins))
sy=[r for r in rs if r['method'].startswith('symfresh')]
if sy:
    g=collections.defaultdict(lambda:[0,0,[]])
    for r in sy:
        key=(f"k{r.get('k')}", 'proper' if r.get('det')==1 else 'improper', f"fix{r.get('dfix')}")
        g[key][0]+=1; g[key][1]+=r['beat']; g[key][2].append(r['s']/r['rec']-1)
    print('\nsymfresh by group element type: attempts, beats, median gap')
    for k,(a,b,x) in sorted(g.items()): print(k, a, b, round(float(np.median(x)),4))
