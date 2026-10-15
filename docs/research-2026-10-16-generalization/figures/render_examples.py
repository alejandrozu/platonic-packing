"""Reproduce the three-panel figure from frozen full-precision coordinate witnesses.

Run with the project Python and Matplotlib available (work/analysis-dependencies).
Colors label pieces, not symmetry-aware orientation classes. No coordinates are
spread, jittered, retightened or otherwise altered for display.
"""
import sys, pathlib, json, hashlib
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
DEPS=ROOT/'work'/'analysis-dependencies'
if DEPS.is_dir():sys.path.insert(0,str(DEPS))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from matplotlib.colors import to_rgb
OUT=pathlib.Path(__file__).resolve().parent
DATA=OUT.parent/'data'/'sources'
FLOAT=json.loads((DATA/'src/solids.json').read_text())
HP=json.loads((DATA/'src/solids_hp.json').read_text())
CASES=[('pr5inpr5','pr5inpr5_n12','(a) Pentagonal prisms',24,38),
       ('tocintoc','tocintoc_n08','(b) Truncated octahedra',22,35),
       ('phcinphc','phcinphc_n04','(c) Pentagonal hexecontahedra',19,35)]
PALETTE=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9',
         '#882255','#44AA99','#AA4499','#661100','#332288','#999933']

def vertices(name):
    # HP vertices use the canonical native witness units, not simulator inradius units.
    return np.array(HP.get(name,FLOAT[name])['V'],dtype=float)

def rotation(q):
    # Scalar-first q=(w,x,y,z), identical H(q)/||q||^2 convention to certify_general.py.
    q=np.array(q,dtype=float);q=q/np.max(np.abs(q));w,x,y,z=q;n=q@q
    return np.array([[w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)],
                     [2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],
                     [2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]])/n

def main():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,
                         'svg.fonttype':'none','axes.titlesize':9.5,'figure.facecolor':'white'})
    fig=plt.figure(figsize=(7.25,2.76),layout=None)
    fig.subplots_adjust(left=0.005,right=0.995,bottom=0.085,top=0.89,wspace=-0.10)
    validation=[]
    for ix,(pid,rid,title,elev,azim) in enumerate(CASES):
        path=DATA/'records'/pid/(rid+'.json');raw=path.read_bytes();rec=json.loads(raw)
        P=FLOAT[rec['piece']];C=FLOAT[rec['container']]
        V=vertices(rec['piece']);W=vertices(rec['container']);faces=P['faces']
        center=np.array(rec.get('container_center',[0,0,0]),dtype=float)
        scale=float(rec['s_full']);WC=scale*W
        cp=np.asarray(C['normals'],dtype=float);beta=np.asarray(C['offsets'],dtype=float)
        allvertices=[];deterror=0;orthoerror=0;edgeerror=0;slack=float('inf')
        ax=fig.add_subplot(1,3,ix+1,projection='3d');ax.set_proj_type('ortho')
        for i,pose in enumerate(rec['pieces']):
            rot=rotation(pose[3:]);X=V@rot.T+np.asarray(pose[:3],dtype=float)-center
            allvertices.append(X);color=PALETTE[i%len(PALETTE)]
            deterror=max(deterror,abs(np.linalg.det(rot)-1));orthoerror=max(orthoerror,np.max(abs(rot@rot.T-np.eye(3))))
            slack=min(slack,float(np.min(scale*beta[None,:]-X@cp.T)))
            for a,b in P['edges']:
                edgeerror=max(edgeerror,abs(np.linalg.norm(X[a]-X[b])-np.linalg.norm(V[a]-V[b])))
            fc=Poly3DCollection([X[f]for f in faces],facecolors=[(*to_rgb(color),0.16)],
                                edgecolors='none',zsort='average')
            ax.add_collection3d(fc)
            ec=Line3DCollection([X[[a,b]]for a,b in P['edges']],colors=[(*to_rgb(color),0.78)],linewidths=0.37)
            ax.add_collection3d(ec)
        wire=Line3DCollection([WC[[a,b]]for a,b in C['edges']],colors=[(0.15,0.17,0.20,0.80)],linewidths=0.58)
        ax.add_collection3d(wire)
        extent=(WC.max(0)-WC.min(0));mid=(WC.max(0)+WC.min(0))/2
        radius=extent.max()*0.535
        ax.set_xlim(mid[0]-radius,mid[0]+radius);ax.set_ylim(mid[1]-radius,mid[1]+radius);ax.set_zlim(mid[2]-radius,mid[2]+radius)
        ax.set_box_aspect((1,1,1),zoom=1.18);ax.view_init(elev=elev,azim=azim);ax.set_axis_off()
        ax.set_title(title,pad=1)
        ax.text2D(.5,-.012,f'$n={rec["n"]}$,  $s\\approx {scale:.6f}$',transform=ax.transAxes,ha='center',va='top',fontsize=9)
        assert len(rec['pieces'])==rec['n'];assert slack>-1e-10;assert deterror<1e-12;assert edgeerror<1e-12
        validation.append({'case':rid,'native_file':str(path.relative_to(OUT.parent)),
                           'native_sha256':hashlib.sha256(raw).hexdigest(),'n':rec['n'],'s_full':rec['s_full'],
                           'container_center_removed_from_all_vertices':center.tolist(),
                           'canonical_geometry':'src/solids_hp.json native vertices, src/solids.json faces/edges/normals',
                           'quaternion':'scalar-first H(q)/norm(q)^2; stable rescaling only',
                           'maximum_rotation_determinant_error':deterror,'maximum_rotation_orthogonality_error':orthoerror,
                           'maximum_rigid_edge_length_error':edgeerror,'minimum_display_containment_slack':slack,
                           'colors':'piece index, not orientation class',
                           'source_certificate':str(path.relative_to(OUT.parent)).removesuffix('.json')+'.certify.txt'})
    fig.savefig(OUT/'generalization-examples.pdf',bbox_inches=None)
    fig.savefig(OUT/'generalization-examples.png',dpi=300,bbox_inches=None)
    plt.close(fig)
    (OUT/'figure-validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    print(json.dumps(validation,indent=2))
if __name__=='__main__':main()
