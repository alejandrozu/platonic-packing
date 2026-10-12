"""Render verified table specimens with symmetry-reduced orientation colors.

Only files inside this script's output directory are written. Source records,
analysis data, existing renderers, article files, and mention files are read-only.
Matplotlib/NumPy/Pillow are taken from the existing workspace dependencies.
"""
from pathlib import Path
import os,sys,csv,json,hashlib,math,itertools,argparse
BASE=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(BASE/"work/analysis-dependencies"))
os.environ["MPLCONFIGDIR"]=str(BASE/"work/wiki-animation/mplconfig")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection,Poly3DCollection
from mpl_toolkits.mplot3d import proj3d
from matplotlib.colors import to_rgb
from PIL import Image

OUT=Path(__file__).resolve().parent
FREEZE="e15b496ae7306287e0e70bb5b14be79f5dfdde84"
PALETTE=['#4c6fd6','#d9822b','#3f9a6a','#c8524a','#7a5fc4','#2a9fb0','#c9a227','#b5577f','#6d8a2f','#8a6a4b',
         '#5a86c2','#d36b3b','#4aa087','#a8484a','#8c76d1','#3b8fa0','#b8962e','#9c5c8f','#7f9a3a','#a37b5a']
GROUP_ORDERS={"tetrahedron":12,"cube":24,"octahedron":24,"dodecahedron":60,"icosahedron":60}
ALPHA=.42
LIGHT=np.asarray([-.4,-.6,1.]);LIGHT/=np.linalg.norm(LIGHT)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def qrot(q):
    w,x,y,z=map(float,q);norm=w*w+x*x+y*y+z*z
    assert norm>0
    return np.array([[w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)],
                     [2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],
                     [2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]])/norm
def frame(a,b):
    x=a/np.linalg.norm(a);y=b-np.dot(b,x)*x;y/=np.linalg.norm(y)
    return np.column_stack([x,y,np.cross(x,y)])
def symmetry_group(vertices,expected):
    a=vertices[0];b=next(v for v in vertices[1:] if np.linalg.norm(np.cross(a,v))>1e-8)
    ref=frame(a,b);dot0=np.dot(a,b);group=[]
    for c in vertices:
        for d in vertices:
            if abs(np.dot(c,d)-dot0)>1e-8 or np.linalg.norm(np.cross(c,d))<1e-8:continue
            G=frame(c,d)@ref.T;rotated=vertices@G.T
            err=np.max(np.min(np.linalg.norm(rotated[:,None,:]-vertices[None,:,:],axis=2),axis=1))
            if err<1e-8 and all(np.linalg.norm(G-H)>1e-7 for H in group):group.append(G)
    assert len(group)==expected
    for G in group:
        assert np.max(np.abs(G.T@G-np.eye(3)))<1e-12 and np.linalg.det(G)>1-1e-12
    return np.asarray(group)
def orientation_groups(rotations,symmetries):
    parents=list(range(len(rotations)))
    def root(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    for i,j in itertools.combinations(range(len(rotations)),2):
        relative=rotations[i].T@rotations[j]
        trace=float(np.einsum("ij,gji->g",relative,symmetries).max())
        angle=math.degrees(math.acos(float(np.clip((trace-1)/2,-1,1))))
        if angle<=1.0:
            a,b=root(i),root(j)
            if a!=b:parents[b]=a
    classes={}
    for i in range(len(rotations)):classes.setdefault(root(i),[]).append(i)
    return sorted(classes.values(),key=lambda g:(-len(g),g[0]))
def projected_pixels(ax,vertices):
    p=proj3d.proj_transform(vertices[:,0],vertices[:,1],vertices[:,2],ax.get_proj())
    return ax.transData.transform(np.column_stack(p[:2]))

def render(record_id,repo,analysis,source_hashes,solids,groups,details,size,filename):
    problem=record_id.split("_n")[0]
    path=repo/"records"/problem/(record_id+".json")
    relative=path.relative_to(repo).as_posix()
    digest=sha(path)
    assert digest==source_hashes[relative]["sha256"]
    r=json.loads(path.read_text(encoding="utf-8-sig"))
    assert len(r["pieces"])==r["n"]
    B=solids[r["piece"]];C=solids[r["container"]]
    V=np.asarray(B["V"],dtype=float)
    R=np.asarray([qrot(p[3:]) for p in r["pieces"]])
    calculated=orientation_groups(R,groups[r["piece"]])
    established=details[record_id]["orientation_components"]["1.0"]
    assert calculated==established,(record_id,calculated,established)
    assert len(calculated)<=len(PALETTE)
    labels=[None]*r["n"]
    for label,component in enumerate(calculated):
        for i in component:labels[i]=label
    center=np.asarray(r.get("container_center",[0.,0.,0.]),dtype=float)
    W=np.asarray(C["V"],dtype=float)*r["s_full"]+center
    normals=np.asarray(C["normals"],dtype=float)
    bound=float(C["inradius"])*r["s_full"]
    faces=[];facecolors=[];edgecolors=[];world_vertices=[];excess=-math.inf
    for i,p in enumerate(r["pieces"]):
        world=V@R[i].T+np.asarray(p[:3])
        world_vertices.extend(world.tolist())
        excess=max(excess,float(((world-center)@normals.T-bound).max()))
        color=np.asarray(to_rgb(PALETTE[labels[i]]))
        for face in B["faces"]:
            polygon=world[face]
            normal=np.cross(polygon[1]-polygon[0],polygon[2]-polygon[0]);normal/=np.linalg.norm(normal)
            intensity=.77+.21*max(0.,float(normal@LIGHT))
            faces.append(polygon)
            facecolors.append((*color*intensity,ALPHA))
            edgecolors.append((*color*.63,.49))
    tolerance=1e-10*max(1.,r["s_full"])
    assert excess<=tolerance,(record_id,excess)
    all_vertices=np.vstack([np.asarray(world_vertices),W])
    extent=np.max(np.abs(W-center))*1.055
    fig=plt.figure(figsize=(size/100,size/100),dpi=100,facecolor="white")
    ax=fig.add_axes([0,0,1,1],projection="3d")
    ax.set_axis_off();ax.set_proj_type("ortho");ax.set_facecolor("white")
    ax.set_xlim(-extent,extent);ax.set_ylim(-extent,extent);ax.set_zlim(-extent,extent)
    ax.view_init(elev=19,azim=-53)
    zoom=1.18;ax.set_box_aspect((1,1,1),zoom=zoom)
    ax.add_collection3d(Poly3DCollection(faces,facecolors=facecolors,edgecolors=edgecolors,
                                        linewidths=.46 if size>300 else .35,zsort="average"))
    # Container faces are never drawn: the container is a line-only wireframe.
    ax.add_collection3d(Line3DCollection([W[e] for e in C["edges"]],colors="#62717c",
                                        linewidths=.95 if size>300 else .75,alpha=.70))
    fig.canvas.draw()
    xy=projected_pixels(ax,all_vertices)
    span=float(max(np.ptp(xy[:,0]),np.ptp(xy[:,1])))
    zoom*=.88*size/span
    ax.set_box_aspect((1,1,1),zoom=zoom);fig.canvas.draw()
    xy=projected_pixels(ax,all_vertices)
    margin=float(min(xy.min(),size-xy.max()))
    if margin<4:
        zoom*=.95;ax.set_box_aspect((1,1,1),zoom=zoom);fig.canvas.draw()
        xy=projected_pixels(ax,all_vertices);margin=float(min(xy.min(),size-xy.max()))
    assert margin>=4,(record_id,margin)
    output=OUT/filename
    fig.savefig(output,dpi=100,facecolor="white",metadata={
        "Author":"Alejandro Zarzuelo Urdiales","Copyright":"CC BY 4.0",
        "Description":f"Full stored {record_id} poses; source {FREEZE}; feasible certified construction."},
        pil_kwargs={"optimize":True})
    plt.close(fig)
    with Image.open(output) as im:
        assert im.size==(size,size)
        pixels=np.asarray(im.convert("RGB"))
        nonwhite=np.any(pixels<245,axis=2)
        coverage=float(nonwhite.mean())
        assert coverage>.12,(record_id,coverage)
    plural={"cube":"cubes","tetrahedron":"tetrahedra","octahedron":"octahedra","dodecahedron":"dodecahedra","icosahedron":"icosahedra"}[r["piece"]]
    return {"recordID":record_id,"filename":filename,"dimensions":[size,size],"bytes":output.stat().st_size,"sha256":sha(output),
            "source_path":relative,"source_sha256":digest,"source_hash_matches":True,"piece":r["piece"],"container":r["container"],"n":r["n"],
            "stored_scale":r["s_full"],"orientation_threshold_degrees":1.0,"proper_symmetry_group_order":len(groups[r["piece"]]),
            "orientation_components":calculated,"piece_orientation_labels":labels,"component_colors":PALETTE[:len(calculated)],
            "orientation_labels_match_analysis":True,"piece_opacity":ALPHA,"container_faces_rendered":False,"container_wireframe_only":True,
            "rendered_vertices":len(world_vertices),"maximum_signed_halfspace_excess":excess,"minimum_wall_margin":-excess,
            "containment_tolerance":tolerance,"rendered_vertices_inside":True,"minimum_canvas_margin_pixels":margin,
            "nonwhite_pixel_fraction":coverage,"camera":{"elevation":19,"azimuth":-53,"orthographic":True,"box_zoom":zoom},
            "alt_text":f"{r['n']} {plural} packed inside a wireframe {r['container']}.","external_source_only":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=BASE/"work/repository")
    p.add_argument("--analysis",type=Path,default=BASE/"outputs/analysis")
    p.add_argument("--registry",type=Path,default=BASE/"outputs/research/current-records.json")
    args=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    source_hashes={r["path"]:r for r in csv.DictReader((args.analysis/"source-manifest.csv").open(encoding="utf-8-sig"))}
    solid_path=args.repo/"src/solids.json"
    assert sha(solid_path)==source_hashes["src/solids.json"]["sha256"]
    solids=json.loads(solid_path.read_text(encoding="utf-8-sig"))
    details=json.loads((args.analysis/"geometry-details.json").read_text(encoding="utf-8"))
    groups={name:symmetry_group(np.asarray(d["V"]),GROUP_ORDERS[name]) for name,d in solids.items()}
    cases=json.loads(args.registry.read_text(encoding="utf-8"))["cases"]
    assets=[];external=[]
    for case in cases:
        if case["configURL"] is None:
            assert case["recordID"] in ["octincub_n11","octincub_n12"]
            external.append({"recordID":case["recordID"],"filename":None,"external_source_only":True,
                             "reported_value":case["displayValue"],"attribution":case["attribution"],
                             "original_diagram_url":case["reportedSourceImageURL"],"sourceURL":case["sourceURL"],
                             "reason":"No coordinates for the superior external configuration were retrieved. The inferior local placement was not rendered for this table cell."})
            continue
        result=render(case["recordID"],args.repo,args.analysis,source_hashes,solids,groups,details,240,case["recordID"]+".png")
        result["constructionURL"]=case["configURL"];result["attribution"]=case["attribution"]
        assets.append(result)
        if len(assets)%20==0:print(f"Rendered {len(assets)}/97 coordinate-backed table thumbnails",flush=True)
    assert len(assets)==97 and len(external)==2
    hero=render("dodindod_n33",args.repo,args.analysis,source_hashes,solids,groups,details,420,"hero-dodindod-n33.png")
    output={"author":"Alejandro Zarzuelo Urdiales","license":"CC BY 4.0","licenseURL":"https://creativecommons.org/licenses/by/4.0/",
            "source_commit":FREEZE,"source_solids_sha256":sha(solid_path),"source_analysis_detail_sha256":sha(args.analysis/"geometry-details.json"),
            "selection_registry_sha256":sha(args.registry),"generation_method":"Scientific Matplotlib rendering from full stored poses, proper-symmetry disorientation, and verified canonical vertices/faces.",
            "model_generated_images":False,"rendered_table_thumbnails":97,"external_source_only_cells":2,"total_table_cells":99,
            "orientation_definition":"Connected components at pairwise symmetry-reduced disorientation <=1 degree, over each particle's proper rotational symmetry group; labels sorted by decreasing component size then first piece index.",
            "palette_source":"Exact 20-color palette from the existing frozen packing viewer.",
            "palette":PALETTE,"encoding_notes_are_manifest_only":True,
            "matplotlib_version":matplotlib.__version__,"numpy_version":np.__version__,
            "assets":assets,"external_cases":external,"infobox_hero":hero,
            "audit":{"all_source_hashes_match":True,"all_orientation_partitions_match_analysis":True,
                     "all_rendered_vertices_contained":True,"all_containers_wireframe_only":True,
                     "all_pieces_opacity":ALPHA,"all_images_have_no_overlaid_labels_or_captions":True,
                     "all_images_uncropped_and_nonblank":True,"rendered_png_count":98},
            "source_and_credit_boundary":"Cube n12 reproduces Yohei Nakajima's touching family with Zarzuelo's smaller clearance. Imported benchmark origins stay credited through the cell attribution and source URLs; orientation colors do not denote shell classes.",
            "commons_upload_status":"LOCAL ONLY; not uploaded to Commons; no Wikimedia file name invented."}
    (OUT/"thumbnail-manifest.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    def keyed_asset(item):
        return {**item,"png":item["filename"],
                "orientation_labels":item.get("piece_orientation_labels"),
                "piece_index_groups":item.get("orientation_components"),
                "alpha":item.get("piece_opacity")}
    integration={**output,
                 "assets":{item["recordID"]:keyed_asset(item) for item in assets+external},
                 "hero":keyed_asset(hero),"alpha":ALPHA,
                 "piece_indices":"Zero-based, in the exact order of the source record's pieces array."}
    (OUT/"manifest.json").write_text(json.dumps(integration,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"rendered_table_thumbnails":len(assets),"external_cells":len(external),"hero":hero["filename"],
                      "minimum_canvas_margin":min(x["minimum_canvas_margin_pixels"] for x in assets+[hero]),
                      "minimum_nonwhite_fraction":min(x["nonwhite_pixel_fraction"] for x in assets+[hero])}),flush=True)

if __name__=="__main__":main()
