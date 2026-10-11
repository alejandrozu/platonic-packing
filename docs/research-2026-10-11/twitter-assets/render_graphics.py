"""Render original scientific social graphics from the frozen pose archive.

Usage: python render_graphics.py --repo PATH --analysis PATH --out PATH
Optional: --dependencies PATH for a local Matplotlib/NumPy installation.
No fitted placement or generated-image approximation is used.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import os
import sys

BASE=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--repo',type=Path,default=BASE/'work/repository')
parser.add_argument('--analysis',type=Path,default=BASE/'outputs/analysis')
parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
parser.add_argument('--dependencies',type=Path,default=BASE/'work/analysis-dependencies')
args=parser.parse_args()
if args.dependencies.exists():sys.path.insert(0,str(args.dependencies))
scratch=BASE/'work/twitter-graphics'
scratch.mkdir(parents=True,exist_ok=True)
os.environ['MPLCONFIGDIR']=str(scratch/'mplconfig')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.mplot3d.art3d import Line3DCollection,Poly3DCollection

FREEZE='e15b496ae7306287e0e70bb5b14be79f5dfdde84'
BG='#f6f5f1';INK='#17293a';SUB='#566675';LINE='#d5dce0'
TEAL='#188a8b';GOLD='#e19a31';PURPLE='#6b5dc0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,
                     'text.color':INK,'axes.labelcolor':INK,'xtick.color':SUB,'ytick.color':SUB,
                     'svg.fonttype':'none','axes.unicode_minus':False})
solids=json.loads((args.repo/'src/solids.json').read_text(encoding='utf-8'))
metrics={r['record_id']:r for r in csv.DictReader((args.analysis/'record-metrics.csv').open(encoding='utf-8'))}
detail=json.loads((args.analysis/'geometry-details.json').read_text(encoding='utf-8'))
source_paths={args.repo/'src/solids.json',args.analysis/'record-metrics.csv',args.analysis/'geometry-details.json'}
frozen_hashes={row['path']:row['sha256'] for row in csv.DictReader((args.analysis/'source-manifest.csv').open(encoding='utf-8'))}
assert hashlib.sha256((args.repo/'src/solids.json').read_bytes()).hexdigest()==frozen_hashes['src/solids.json']
containment_checks={}

def record(problem,n):
    path=args.repo/'records'/problem/f'{problem}_n{n:02d}.json'
    source_paths.add(path)
    r=json.loads(path.read_text(encoding='utf-8'))
    assert len(r['pieces'])==r['n']==n
    expected=frozen_hashes[path.relative_to(args.repo).as_posix()]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
    # Validate exactly the vertices used in the floating-point drawing, rather
    # than relying on the apparent projected extent of container wire edges.
    B=np.asarray(solids[r['piece']]['V']);A=solids[r['container']]
    normals=np.asarray(A['normals']);offset=float(A['inradius'])*r['s_full']
    largest=-math.inf
    for p in r['pieces']:
        vertices=B@qrot(p[3:]).T+np.asarray(p[:3])
        largest=max(largest,float((vertices@normals.T-offset).max()))
    tolerance=1e-10*max(1,r['s_full'])
    assert largest<=tolerance,(problem,n,largest,tolerance)
    containment_checks[f'{problem}_n{n:02d}']={'rendered_vertices':r['n']*len(B),
        'max_signed_halfspace_excess':largest,'minimum_wall_margin':-largest,
        'floating_tolerance':tolerance,'inside':True,'source_hash_matches_frozen_manifest':True}
    return r

def qrot(q):
    q=np.asarray(q,dtype=float);q=q/np.linalg.norm(q);w,x,y,z=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
                     [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
                     [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])

def face_color(poly,color,alpha):
    normal=np.cross(poly[1]-poly[0],poly[2]-poly[0]);normal/=np.linalg.norm(normal)
    light=np.array([-.4,-.6,1.]);light/=np.linalg.norm(light)
    intensity=.66+.30*max(0,float(normal@light))
    return (*np.asarray(to_rgb(color))*intensity,alpha)

def clean_3d(ax,extent,elev=19,azim=-53):
    ax.set_axis_off();ax.set_proj_type('ortho');ax.view_init(elev=elev,azim=azim)
    ax.set_xlim(-extent,extent);ax.set_ylim(-extent,extent);ax.set_zlim(-extent,extent)
    ax.set_box_aspect((1,1,1),zoom=1.15)
    ax.set_facecolor(BG)

def pose_faces(r,colors,alphas=None):
    b=solids[r['piece']];V=np.asarray(b['V']);faces=[];shade=[]
    if isinstance(colors,str):colors=[colors]*r['n']
    alphas=[.96]*r['n'] if alphas is None else alphas
    for i,p in enumerate(r['pieces']):
        world=V@qrot(p[3:]).T+np.asarray(p[:3])
        for face in b['faces']:
            poly=world[face];faces.append(poly);shade.append(face_color(poly,colors[i],alphas[i]))
    return faces,shade

def packing(ax,r,color,alphas=None,wire=True,elev=19,azim=-53):
    A=solids[r['container']];W=np.asarray(A['V'])*r['s_full']
    extent=np.max(np.abs(W))*1.025
    clean_3d(ax,extent,elev,azim)
    faces,shade=pose_faces(r,color,alphas)
    if wire:
        ax.add_collection3d(Line3DCollection([W[e] for e in A['edges']],colors='#8796a0',linewidths=1.1,alpha=.52))
    ax.add_collection3d(Poly3DCollection(faces,facecolors=shade,edgecolors=(.10,.18,.23,.38),linewidths=.40,zsort='average'))
    return extent

def base_figure(width=16,height=14):
    fig=plt.figure(figsize=(width,height),facecolor=BG)
    return fig

def title(fig,headline,sub,fontsize=31,y=.951):
    fig.text(.047,y,headline,fontsize=fontsize,fontweight='bold',ha='left',va='top')
    fig.text(.048,y-.045,sub,fontsize=17,color=SUB,ha='left',va='top')

def footer(fig,credit=None,y=.027):
    fig.text(.047,y,'Frozen certified study archive e15b496 · feasible bounds, not a current-best leaderboard or proved optima.',
             fontsize=10.5,color=SUB,ha='left',va='bottom')
    if credit:fig.text(.047,y+.021,credit,fontsize=10.5,color=SUB,ha='left',va='bottom')

def save(fig,stem):
    args.out.mkdir(parents=True,exist_ok=True)
    png=args.out/(stem+'.png');svg=args.out/(stem+'.svg')
    # Headline, explanatory and footer text must stay within the full canvas.
    fig.canvas.draw();renderer=fig.canvas.get_renderer();width,height=fig.canvas.get_width_height()
    for label in fig.texts:
        bbox=label.get_window_extent(renderer)
        assert bbox.x0>=0 and bbox.y0>=0 and bbox.x1<=width and bbox.y1<=height,(stem,label.get_text(),bbox)
    fig.savefig(png,dpi=150,facecolor=BG,pil_kwargs={'optimize':True},metadata={'Description':f'Actual frozen polyhedral packing data at {FREEZE}.'})
    fig.savefig(svg,facecolor=BG,metadata={'Description':f'Geometry/metrics from frozen pose archive {FREEZE}; construction upper bounds, not optimum claims.'})
    plt.close(fig)
    from PIL import Image
    with Image.open(png) as im:size=list(im.size)
    assert size[0]>=1600 and png.stat().st_size<5_000_000
    return {'png':png.name,'svg':svg.name,'pixel_size':size,'png_bytes':png.stat().st_size,
            'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest()}

def hero():
    fig=base_figure(15,14)
    title(fig,'Polyhedra in polyhedra packing','351 certified constructions · 9 families · n = 2–40',fontsize=31)
    fig.text(.95,.874,'piece → container',ha='right',fontsize=13,color=SUB)
    examples=[('cubincub',12,'Cube → Cube','#3b76b0'),
              ('tetintet',12,'Tetra → Tetra','#228f8a'),
              ('octinoct',12,'Octa → Octa','#cf9440'),
              ('dodindod',33,'Dodeca → Dodeca','#7665b4'),
              ('icoinico',12,'Icosa → Icosa','#418dab'),
              ('cubinoct',12,'Cube → Octa','#b97163'),
              ('octincub',12,'Octa → Cube','#a65f97'),
              ('dodinico',12,'Dodeca → Icosa','#567aa2'),
              ('icoindod',12,'Icosa → Dodeca','#70974b')]
    for index,(problem,n,label,color) in enumerate(examples):
        row,col=divmod(index,3);x=.045+col*.31;y=.624-row*.262
        # Panel text has a fixed place; geometry cannot overlap another label.
        fig.text(x+.15,y+.200,label,ha='center',fontsize=21,fontweight='bold')
        fig.text(x+.15,y+.173,f'n = {n}',ha='center',fontsize=16,color=SUB)
        ax=fig.add_axes([x,y-.035,.30,.190],projection='3d')
        packing(ax,record(problem,n),color)
    footer(fig,'Alejandro Zarzuelo Urdiales · Cube/Cube n=12: Yohei Nakajima construction, certified reproduction.')
    output=save(fig,'01-nine-families')
    output['record_ids']=[f'{p}_n{n:02d}' for p,n,_,_ in examples]
    output['alt_text']='Nine rendered configurations from certified stored poses, arranged in a three-by-three grid. Unit pieces are solid colored polyhedra; enclosing containers are muted wireframes. The labeled piece-to-container pairs are cubes/cube n=12, tetrahedra/tetrahedron n=12, octahedra/octahedron n=12, dodecahedra/dodecahedron n=33, icosahedra/icosahedron n=12, cubes/octahedron n=12, octahedra/cube n=12, dodecahedra/icosahedron n=12 and icosahedra/dodecahedron n=12. Headline: Polyhedra in polyhedra packing. The archive contains 351 certified constructions across nine ordered families, all counts 2–40. This is the frozen certified study archive, not a current-best leaderboard. A better externally reported octahedra-in-cube n=12 bound lacks retrieved poses. The cube n=12 specimen reproduces Yohei Nakajima’s construction.'
    return output

def shell():
    fig=base_figure(15,10)
    title(fig,'33 dodecahedra: hidden order','A central piece + an icosahedral inner shell + a dodecahedral outer shell',fontsize=30,y=.947)
    r=record('dodindod',33);centers=np.asarray(r['pieces'])[:,:3];radii=np.linalg.norm(centers,axis=1)
    assert all(len(detail['dodindod_n33']['contacts'][t]['edges'])==102 for t in ['1e-05','0.0001','0.001'])
    assert all(len(detail['dodindod_n33']['grains'][t])==33 for t in ['0.1','1.0','5.0'])
    central=np.flatnonzero(radii<1e-8);inner=np.flatnonzero((radii>=1e-8)&(radii<3));outer=np.flatnonzero(radii>=3)
    assert (len(central),len(inner),len(outer))==(1,12,20)
    colors=[PURPLE if i in central else GOLD if i in inner else TEAL for i in range(33)]
    alphas=[1 if i in central else .98 if i in inner else .40 for i in range(33)]
    fig.text(.26,.836,'Actual certified poses',ha='center',fontsize=20,fontweight='bold')
    fig.text(.26,.804,'Outer pieces translucent to reveal the interior',ha='center',fontsize=12,color=SUB)
    ax=fig.add_axes([.037,.272,.45,.52],projection='3d');packing(ax,r,colors,alphas,elev=20,azim=-50)
    fig.text(.745,.836,'Actual centers, schematic shell guides',ha='center',fontsize=19,fontweight='bold')
    fig.text(.745,.804,'Guide edges are not the contact graph',ha='center',fontsize=12,color=SUB)
    ax=fig.add_axes([.518,.272,.445,.52],projection='3d');clean_3d(ax,4.0,elev=20,azim=-50)
    for indices,color,ms in [(outer,TEAL,100),(inner,GOLD,120),(central,PURPLE,180)]:
        pair_dist=np.linalg.norm(centers[indices,None,:]-centers[None,indices,:],axis=2)
        if len(indices)>1:
            minimum=pair_dist[pair_dist>1e-7].min();edges=[]
            for j in range(len(indices)):
                for k in range(j+1,len(indices)):
                    if abs(pair_dist[j,k]-minimum)<1e-7:edges.append(centers[[indices[j],indices[k]]])
            ax.add_collection3d(Line3DCollection(edges,colors=color,linewidths=1.2,alpha=.60,linestyles='dashed'))
        ax.scatter(*centers[indices].T,color=color,s=ms,edgecolors=BG,linewidths=.8,depthshade=False)
    # A separate literal count legend avoids an interpretation as orientation colors.
    for x,label,color in [(.23,'1 central',PURPLE),(.47,'12 inner',GOLD),(.71,'20 outer',TEAL)]:
        fig.text(x,.242,'●',fontsize=21,color=color,ha='left',va='center')
        fig.text(x+.024,.242,label,fontsize=17,fontweight='bold',ha='left',va='center')
    fig.text(.5,.201,'Colors indicate shell classes, not orientation domains.',ha='center',fontsize=12.5,color=SUB)
    fig.text(.5,.151,'Counts 29–33 share the same certified edge: 3.747091',ha='center',fontsize=21,fontweight='bold')
    fig.text(.5,.113,'Smaller witnesses omit only outer pieces · 102 near contacts at n=33 · no aligned contact within 5°',
             ha='center',fontsize=13.1,color=SUB)
    footer(fig,'Alejandro Zarzuelo Urdiales · geometry and shell structure measured from dodindod_n33.')
    output=save(fig,'02-dodecahedral-shell')
    output['record_ids']=[f'dodindod_n{n:02d}' for n in range(29,34)]
    output['alt_text']='Two views of the same certified 33-dodecahedron witness: left shows actual solid poses with translucent teal outer pieces, gold inner pieces, and a purple central piece; right shows the actual centers with explicitly schematic dashed shell guides that do not represent contacts. There is one central piece, 12 inner centers forming a dual icosahedral shell and 20 outer centers forming a dodecahedral shell. Counts 29–33 share certified container edge 3.7470909531576 by omitting outer pieces. The 33-piece near-contact graph has 102 edges and none connects similarly oriented pieces within 5 degrees. Colors denote shell class, not orientation. Feasible construction bounds, not a claim of global optimality.'
    output['shell_counts']={'central':1,'inner':12,'outer':20}
    output['guide_edges_are_contacts']=False
    return output

def bar_axes(fig,rect):
    ax=fig.add_axes(rect,facecolor=BG)
    ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color(LINE)
    ax.tick_params(length=0,pad=10);ax.set_axisbelow(True)
    ax.grid(axis='y',color=LINE,linewidth=.6,alpha=.7)
    return ax

def jumps():
    fig=base_figure(15,10)
    title(fig,'Same scale. Very different marginal costs.','Observed patterns in certified constructions — not a curve of proved optima',fontsize=29,y=.947)
    fig.text(.047,.802,'Dodecahedra in a dodecahedron',fontsize=21,fontweight='bold')
    fig.text(.047,.759,'n = 29–33: a five-count plateau',fontsize=17,color=TEAL)
    fig.text(.55,.802,'Octahedra in an octahedron',fontsize=21,fontweight='bold')
    fig.text(.55,.759,'n = 6 → 7: a sharp expansion step',fontsize=17,color=GOLD)
    d=[metrics[f'dodindod_n{n:02d}'] for n in range(29,34)]
    assert len({x['s_full'] for x in d})==1
    fig.text(.264,.682,'3.747091',ha='center',fontsize=39,fontweight='bold',color=TEAL)
    fig.text(.264,.638,'same certified container edge at every count',ha='center',fontsize=12.6,color=SUB)
    ax=bar_axes(fig,[.100,.290,.367,.280]);xx=np.arange(5);yy=np.array([float(x['density'])*100 for x in d])
    ax.bar(xx,yy,color=TEAL,width=.60,zorder=3)
    ax.set_ylim(0,73);ax.set_yticks([0,20,40,60]);ax.set_yticklabels(['0%','20%','40%','60%'],fontsize=12)
    ax.set_xticks(xx);ax.set_xticklabels([f'n={n}' for n in range(29,34)],fontsize=15)
    ax.set_ylabel('Occupied volume',fontsize=13,labelpad=12)
    for x,y in zip(xx,yy):ax.text(x,y+2.2,f'{y:.1f}%',ha='center',fontsize=14,fontweight='bold')
    six=metrics['octinoct_n06'];seven=metrics['octinoct_n07'];edge=np.array([float(six['s_full']),float(seven['s_full'])])
    rel=edge[1]/edge[0]-1;vol=(edge[1]/edge[0])**3-1
    fig.text(.764,.682,f'+{100*rel:.1f}% edge',ha='center',fontsize=34,fontweight='bold',color=GOLD)
    fig.text(.764,.638,f'+{100*vol:.1f}% container volume',ha='center',fontsize=18,color=SUB)
    ax=bar_axes(fig,[.583,.290,.359,.280]);ax.bar([0,1],edge,color=['#89a9af',GOLD],width=.55,zorder=3)
    ax.set_ylim(0,3.1);ax.set_yticks([0,1,2,3]);ax.set_yticklabels(['0','1','2','3'],fontsize=12)
    ax.set_xticks([0,1]);ax.set_xticklabels(['n=6','n=7'],fontsize=16)
    ax.set_ylabel('Container edge / piece edge',fontsize=13,labelpad=12)
    for x,y in enumerate(edge):ax.text(x,y+.10,f'{y:.6f}',ha='center',fontsize=17,fontweight='bold')
    fig.text(.27,.200,'More pieces; unchanged scale',ha='center',fontsize=20,fontweight='bold',color=TEAL)
    fig.text(.76,.200,'Occupied volume: 75.0% → 44.8%',ha='center',fontsize=20,fontweight='bold',color=GOLD)
    fig.text(.50,.145,'Plateaus and jumps expose construction families, shell capacities and opportunities for new searches.',
             ha='center',fontsize=14,color=SUB)
    footer(fig,'Alejandro Zarzuelo Urdiales · scales rounded for display; exact feasibility concerns the stored values.',y=.065)
    output=save(fig,'03-plateau-and-jump')
    output['record_ids']=[f'dodindod_n{n:02d}' for n in range(29,34)]+['octinoct_n06','octinoct_n07']
    output['numeric_values']={'dodeca_plateau_certified_scale':float(d[0]['s_full']),
                              'dodeca_density_by_n':{int(float(x['n'])):float(x['density']) for x in d},
                              'octa_certified_scales':edge.tolist(),'octa_edge_increase_pct':100*rel,
                              'octa_volume_increase_pct':100*vol,
                              'octa_density':[float(six['density']),float(seven['density'])]}
    output['alt_text']='A comparison of two actual archived patterns. Left: dodecahedra in a dodecahedron at counts 29–33 all have certified edge 3.7470909531576, while occupied volume rises through 55.1%, 57.0%, 58.9%, 60.8%, 62.7%. Right: six octahedra in an octahedron have certified edge 2.0000003674235; seven have 2.5000004286608. The edge rises 25.0% and container volume 95.3%, while occupied volume falls from 75.0% to 44.8%. Values are feasible construction upper bounds and their structural measurements, not proved global optima.'
    return output

assets=[hero(),shell(),jumps()]
def source_label(path):
    path=path.resolve()
    if path.is_relative_to(args.repo.resolve()):return 'archive/'+path.relative_to(args.repo.resolve()).as_posix()
    return 'analysis/'+path.relative_to(args.analysis.resolve()).as_posix()

manifest={'source_commit':FREEZE,'author':'Alejandro Zarzuelo Urdiales','generation_method':'Matplotlib vector/3D geometry rendered from full stored poses and canonical vertex/face coordinates; plots from full-precision record metrics.',
          'numeric_rotation_note':'Stored scalar-first quaternions normalized for floating-point visualization; source exact certificates concern original stored records.',
          'matplotlib_version':matplotlib.__version__,'numpy_version':np.__version__,
          'rendered_images_are_new':True,'model_generated_images':False,'assets':assets,
          'leaderboard_status':'Frozen certified study archive, not current-best leaderboard; octincub n12 has a superior external reported value without retrieved poses. The archive specimen is shown unchanged.',
          'rendered_vertex_containment_checks':containment_checks,
          'rendered_vertex_total':sum(c['rendered_vertices'] for c in containment_checks.values()),
          'floating_containment_scope':'Every rendered piece vertex is inside the rendered container halfspaces; source exact certificates apply separately to archived data.',
          'source_sha256':{source_label(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_paths)}}
(args.out/'figure-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
alt=['# Suggested images and alt text','',
     'These new scientific graphics use the frozen certified pose files and full-precision metrics. They do not claim global optimality. PNGs are sized for social sharing; SVGs preserve editable vector output.','']
for i,a in enumerate(assets,1):alt.extend([f'## {i}. {a["png"]}','',a['alt_text'],''])
(args.out/'alt-text.md').write_text('\n'.join(alt),encoding='utf-8')
print(json.dumps([{k:v for k,v in a.items() if k in ['png','svg','pixel_size','png_bytes']} for a in assets],indent=2))
