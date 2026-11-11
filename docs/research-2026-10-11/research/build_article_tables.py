"""Insert source-linked n=2..12 tables into the article and MediaWiki text."""
import argparse,json,re
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);a=p.parse_args()
data=json.loads((a.packet/'research/current-records.json').read_text(encoding='utf-8'))
cases={(x['problem'],x['n']):x for x in data['cases']}
same=[('tetintet','Tetrahedra in tetrahedron'),('cubincub','Cubes in cube'),('octinoct','Octahedra in octahedron'),('dodindod','Dodecahedra in dodecahedron'),('icoinico','Icosahedra in icosahedron')]
dual=[('cubinoct','Cubes in octahedron'),('octincub','Octahedra in cube'),('dodinico','Dodecahedra in icosahedron'),('icoindod','Icosahedra in dodecahedron')]
assert len(cases)==99
assert set(cases)=={(fam,n)for fam,_ in same+dual for n in range(2,13)}

def credit(c):
    if c['problem']=='cubincub':
        return 'G' if c['n']<=8 else 'F/Z' if c['n']<=10 else 'L→Z' if c['n']==11 else 'N/Z'
    if c['problem']=='octincub':return 'W/Z' if c['n']<=10 else 'W' if c['n']==11 else 'L'
    return 'Z'

def cell(c,wiki=False):
    link=c.get('paperURL') or c['sourceURL'];value=c['displayValue'];code=credit(c)
    view='https://alejandrozu.github.io/platonic-packing/#'+c['recordID']
    if wiki:
        s=f'[{link} {value}] <sup>{code}</sup><br /><small>'
        links=[f'[{view} 3D]',f'[{c["configURL"]} construction]'] if c.get('configURL') else [f'[{c["reportedSourceImageURL"]} diagram]',f'[{c["sourceURL"]} catalogue]']
        return s+' · '.join(links)+'</small>'
    s=f'[{value}]({link}) <sup>{code}</sup><br>'
    links=[f'[3D]({view})',f'[construction]({c["configURL"]})'] if c.get('configURL') else [f'[diagram]({c["reportedSourceImageURL"]})',f'[catalogue]({c["sourceURL"]})']
    return s+' · '.join(links)

def table(families,wiki=False):
    if wiki:
        out=['{| class="wikitable"','! n !! '+' !! '.join(label for _,label in families)]
        for n in range(2,13):out.extend(['|-',f'! {n}','| '+' || '.join(cell(cases[(fam,n)],True)for fam,_ in families)])
        out.append('|}');return '\n'.join(out)
    out=['| n | '+' | '.join(label for _,label in families)+' |','|---:|'+'---|'*len(families)]
    for n in range(2,13):out.append('| '+str(n)+' | '+' | '.join(cell(cases[(fam,n)])for fam,_ in families)+' |')
    return '\n'.join(out)

for name,wiki in [('wikipedia-polyhedral-fits.md',False),('wikipedia-polyhedral-fits.wiki',True)]:
    path=a.packet/name;text=path.read_text(encoding='utf-8')
    if 'SAME_SOLID_RESULTS_HERE' in text and 'DUAL_SOLID_RESULTS_HERE' in text:
        text=text.replace('SAME_SOLID_RESULTS_HERE',table(same,wiki)).replace('DUAL_SOLID_RESULTS_HERE',table(dual,wiki))
    else:
        pattern=r'^\{\| class="wikitable".*?^\|\}' if wiki else r'^\| n \|[^\n]*\n(?:\|[^\n]*\n)+'
        matches=list(re.finditer(pattern,text,re.M|re.S if wiki else re.M))
        if len(matches)!=2:raise RuntimeError(f'{name}: expected exactly two result tables')
        for match,families in reversed(list(zip(matches,[same,dual]))):
            text=text[:match.start()]+table(families,wiki)+'\n'+text[match.end():]
    path.write_text(text,encoding='utf-8')
print('Inserted 99 source-linked cells in each article format: two tables, n=2..12.')
