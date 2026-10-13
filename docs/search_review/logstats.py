import json, collections, math, sys, glob, os
sys.path.insert(0,'scripts')
from engine import FAM
P2 = 1791817980  # 12 Oct 16:53 Paris approx
rows=[]
for l in open('state/attempts.jsonl'):
    try: r=json.loads(l)
    except: continue
    rows.append(r)
loc=[r for r in rows if r['move']!='harvest']
def fam(p): return FAM.get(p,'?')
def table(key, rs, title):
    c=collections.defaultdict(lambda:[0,0,0.0,0.0])
    for r in rs:
        k=key(r)
        if k is None: continue
        x=c[k]; x[0]+=1; x[1]+=bool(r['improved']); x[2]+=r.get('secs') or 0
        if r['improved'] and r.get('best_before'): x[3]+= (r['best_before']-r['s'])/r['best_before']
    print(f'\n== {title}')
    print(f"{'key':28s} {'att':>7s} {'impr':>6s} {'rate':>7s} {'s/att':>6s} {'impr/CPUh':>9s} {'meangain':>9s}")
    for k in sorted(c, key=lambda k: str(k)):
        a,i,s,g=c[k]
        print(f"{str(k):28s} {a:7d} {i:6d} {i/a:7.2%} {s/a:6.1f} {i/(s/3600) if s else 0:9.1f} {g/i if i else 0:9.2e}")
for ph,rs in (('phase1',[r for r in loc if r['t']<P2]),('phase2',[r for r in loc if r['t']>=P2])):
    table(lambda r:r['move'], rs, f'move {ph}')
p2=[r for r in loc if r['t']>=P2]
table(lambda r:(fam(r['p']),r['move']), p2, 'phase2 family x move')
def nb(n): return '02-08' if n<=8 else '09-16' if n<=16 else '17-28' if n<=28 else '29-40'
table(lambda r:(nb(r['n']),r['move']), loc, 'n bucket x move (all)')
hops=[r for r in loc if r['move']=='hop']
table(lambda r:r.get('var','base'), hops, 'hop variant')
table(lambda r:r.get('from'), hops, 'hop from')
table(lambda r:'focus0' if not r.get('focus') else 'focus>0', hops, 'hop focus')
def bins(v, edges):
    for e in edges:
        if v is not None and v<e: return f'<{e}'
    return f'>={edges[-1]}'
table(lambda r:bins(r.get('minDiff'),[0.03,0.06,0.12,0.25,0.6]), hops, 'hop minDiff')
table(lambda r:bins(r.get('expand'),[0.01,0.02,0.03,0.05,0.1,0.15]), hops, 'hop expand')
# saturation: k-th local attempt on a case
seen=collections.Counter(); since=collections.Counter()
kk=collections.defaultdict(lambda:[0,0]); ss=collections.defaultdict(lambda:[0,0])
for r in loc:
    key=(r['p'],r['n'])
    if r['best_before'] is None: continue
    k=seen[key]; seen[key]+=1
    b=bins(k,[5,10,20,40,80,160])
    kk[b][0]+=1; kk[b][1]+=r['improved']
    s=since[key]; bs=bins(s,[2,5,10,20,40,80])
    ss[bs][0]+=1; ss[bs][1]+=r['improved']
    since[key]= 0 if r['improved'] else s+1
print('\n== improvement rate vs k-th local attempt on the case'); [print(f'{b:8s} {a:7d} {i/a:7.2%}') for b,(a,i) in sorted(kk.items(), key=lambda x: float(x[0].strip('<>=')))]
print('\n== improvement rate vs attempts since last improvement'); [print(f'{b:8s} {a:7d} {i/a:7.2%}') for b,(a,i) in sorted(ss.items(), key=lambda x: float(x[0].strip('<>=')))]
# raw vs final
tight=[r for r in loc if r['s'] is not None and r['move'] in ('hop','reinsert','fresh','ascend') and r['best_before']]
gated=[r for r in loc if r['s'] is None]
print(f'\n== gated (raw too far, no tightening): {len(gated)} of {len(loc)} ({len(gated)/len(loc):.1%}); mean secs gated {sum(r["secs"] for r in gated)/max(1,len(gated)):.1f}')
tot=sum(r['secs'] for r in loc); raw=sum(r.get('raw_secs') or 0 for r in loc)
print(f'time: total {tot/3600:.0f} CPU-h, soft phase {raw/tot:.0%}, tightening {1-raw/tot:.0%}')
# raw-gap vs success
gb=collections.defaultdict(lambda:[0,0])
for r in tight:
    g=r['raw']/r['best_before']-1
    b=bins(g,[-0.001,0,0.002,0.005,0.01,0.02,0.04])
    gb[b][0]+=1; gb[b][1]+=r['improved']
print('\n== P(improve) vs raw gap to best (tightened attempts)')
for b,(a,i) in sorted(gb.items(), key=lambda x: float(x[0].strip('<>='))): print(f'{b:8s} {a:7d} {i/a:7.2%}')
tg=[r['raw']/r['s']-1 for r in tight]
tg.sort(); print('tightening gain raw/s-1 quantiles', [round(tg[int(q*(len(tg)-1))],4) for q in (0.1,0.25,0.5,0.75,0.9)])
# cascade: ascend success when n-1 improved recently (within last 30 local attempts on problem p)
last_imp={}  # (p,n)-> index of last improvement
casc=collections.defaultdict(lambda:[0,0])
for i,r in enumerate(loc):
    if r['move']=='ascend' and r['best_before']:
        j=last_imp.get((r['p'],r['n']-1)); jr=last_imp.get((r['p'],r['n']))
        fresh_lower = j is not None and (jr is None or j>jr)
        casc['lower improved since this case last improved' if fresh_lower else 'no'][0]+=1
        casc['lower improved since this case last improved' if fresh_lower else 'no'][1]+=r['improved']
    if r['move']=='descend' and r['best_before']:
        j=last_imp.get((r['p'],r['n']+1)); jr=last_imp.get((r['p'],r['n']))
        fu = j is not None and (jr is None or j>jr)
        casc['DESC upper improved since' if fu else 'DESC no'][0]+=1
        casc['DESC upper improved since' if fu else 'DESC no'][1]+=r['improved']
    if r['improved']: last_imp[(r['p'],r['n'])]=i
print('\n== cascade effect')
for k,(a,i) in casc.items(): print(f'{k:50s} {a:6d} {i/a:7.2%}')
# record origins
org=collections.Counter(); orgf=collections.Counter()
for f in glob.glob('state/best/*/n*.json'):
    c=json.load(open(f)); b=c.get('best')
    if not b: continue
    src=b.get('src',{}); m=src.get('move'); h=src.get('host','cloud')
    org[m]+=1; orgf[(FAM.get(c['problem']),m)]+=1
print('\n== final record origin move', org.most_common())
print(sorted(orgf.items()))
