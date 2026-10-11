"""Export selected packing meshes for local review; no upload is performed.

STL coordinates are floating-point visualization geometry. Exact validity comes
from the source JSON and its certificate, never from this export.
"""
import argparse, json, math, pathlib

p=argparse.ArgumentParser(); p.add_argument('--repo',type=pathlib.Path,required=True); p.add_argument('--out',type=pathlib.Path,required=True); a=p.parse_args()
sol=json.loads((a.repo/'src/solids.json').read_text(encoding='utf-8'))
ids=['octinoct_n06','octinoct_n07','dodindod_n33','dodindod_n34','cubincub_n27','dodinico_n13','dodinico_n14']
a.out.mkdir(parents=True,exist_ok=True)

def rotate(q,v):
    w,x,y,z=q; n=w*w+x*x+y*y+z*z
    R=[[w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]]
    return [sum(t*b for t,b in zip(row,v))/n for row in R]

for rid in ids:
    fam=rid.split('_')[0]; rec=json.loads((a.repo/'records'/fam/(rid+'.json')).read_text(encoding='utf-8')); shape=sol[rec['piece']]; out=[]
    for i,piece in enumerate(rec['pieces']):
        out.append(f'solid {rid}_piece_{i+1}')
        V=[[piece[k]+rotate(piece[3:],v)[k] for k in range(3)] for v in shape['V']]
        for face in shape['faces']:
            for j in range(1,len(face)-1):
                tri=[V[face[0]],V[face[j]],V[face[j+1]]]
                u=[tri[1][k]-tri[0][k] for k in range(3)]; v=[tri[2][k]-tri[0][k] for k in range(3)]
                normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]; norm=math.sqrt(sum(x*x for x in normal)); normal=[x/norm for x in normal]
                out.append(' facet normal '+' '.join(f'{x:.12g}' for x in normal)); out.append('  outer loop')
                for xyz in tri: out.append('   vertex '+' '.join(f'{x:.12g}' for x in xyz))
                out.extend(['  endloop',' endfacet'])
        out.append(f'endsolid {rid}_piece_{i+1}')
    (a.out/(rid+'.stl')).write_text('\n'.join(out)+'\n',encoding='ascii')
print(f'Exported {len(ids)} local packing models')
