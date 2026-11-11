"""Create slow scientific rotation GIFs from unrounded stored poses.

This is a standalone renderer. It does not import or execute the social-figure
script. No optimization, image generation, or pose perturbation occurs.
"""
from pathlib import Path
import os,sys,csv,json,hashlib,argparse,math,time
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/"work/analysis-dependencies"))
os.environ["MPLCONFIGDIR"]=str(BASE/"work/wiki-animation/mplconfig")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Line3DCollection,Poly3DCollection
from mpl_toolkits.mplot3d import proj3d
from PIL import Image,PngImagePlugin

FREEZE="e15b496ae7306287e0e70bb5b14be79f5dfdde84"
AUTHOR="Alejandro Zarzuelo Urdiales"
OUT=BASE/"outputs/wikipedia-assets"
REPO=BASE/"work/repository"
BG="#fafafa"
NFRAMES=48
SIZE=512
DURATION=500
LIGHT=np.asarray([-.4,-.6,1.]);LIGHT/=np.linalg.norm(LIGHT)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def qrot(q):
    """Homogeneous Hamilton rotation, using every stored binary float."""
    w,x,y,z=map(float,q)
    q2=w*w+x*x+y*y+z*z
    if q2<=0:raise ValueError("Zero quaternion")
    return np.array([
        [w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)],
        [2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],
        [2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]
    ])/q2

def build(record_id):
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={r["path"]:r for r in csv.DictReader((BASE/"outputs/analysis/source-manifest.csv").open(encoding="utf-8-sig"))}
    solids_path=REPO/"src/solids.json"
    assert sha(solids_path)==manifest["src/solids.json"]["sha256"]
    problem=record_id.split("_n")[0]
    record_path=REPO/"records"/problem/(record_id+".json")
    source_relative=record_path.relative_to(REPO).as_posix()
    assert sha(record_path)==manifest[source_relative]["sha256"]
    r=json.loads(record_path.read_text(encoding="utf-8-sig"))
    solids=json.loads(solids_path.read_text(encoding="utf-8-sig"))
    B=solids[r["piece"]];C=solids[r["container"]]
    V=np.asarray(B["V"],dtype=float)
    container_center=np.asarray(r.get("container_center",[0.,0.,0.]),dtype=float)
    W=np.asarray(C["V"],dtype=float)*r["s_full"]+container_center
    normals=np.asarray(C["normals"],dtype=float)
    bound=float(C["inradius"])*r["s_full"]
    assert len(r["pieces"])==r["n"]
    centers=np.asarray(r["pieces"],dtype=float)[:,:3]
    max_excess=-math.inf;orth_error=0.;all_faces=[];face_colors=[];all_vertices=[]
    shell_indices=None
    if record_id=="dodindod_n33":
        rad=np.linalg.norm(centers,axis=1)
        central=np.flatnonzero(rad<1e-8).tolist()
        inner=np.flatnonzero((rad>=1e-8)&(rad<3)).tolist()
        outer=np.flatnonzero(rad>=3).tolist()
        assert [len(central),len(inner),len(outer)]==[1,12,20]
        shell_indices={"central":central,"inner":inner,"outer":outer}
        colors=["#525c6d" if i in central else "#ae8951" if i in inner else "#6e8e9c" for i in range(33)]
        alphas=[1.0 if i in central else .84 if i in inner else .42 for i in range(33)]
    else:
        colors=["#6a859e"]*r["n"]
        alphas=[.98]*r["n"]
    for i,pose in enumerate(r["pieces"]):
        R=qrot(pose[3:])
        orth_error=max(orth_error,float(np.max(np.abs(R.T@R-np.eye(3)))))
        world=V@R.T+np.asarray(pose[:3],dtype=float)
        all_vertices.extend(world.tolist())
        max_excess=max(max_excess,float(((world-container_center)@normals.T-bound).max()))
        for face in B["faces"]:
            poly=world[face]
            normal=np.cross(poly[1]-poly[0],poly[2]-poly[0]);normal/=np.linalg.norm(normal)
            intensity=.68+.27*max(0.,float(normal@LIGHT))
            all_faces.append(poly)
            face_colors.append((*np.asarray(to_rgb(colors[i]))*intensity,alphas[i]))
    tolerance=1e-10*max(1.,float(r["s_full"]))
    assert max_excess<=tolerance,(record_id,max_excess,tolerance)
    assert orth_error<1e-12
    extent=np.max(np.abs(W-container_center))*1.055
    fig=plt.figure(figsize=(SIZE/100,SIZE/100),dpi=100,facecolor=BG)
    ax=fig.add_axes([0,0,1,1],projection="3d")
    ax.set_axis_off();ax.set_proj_type("ortho")
    ax.set_xlim(-extent,extent);ax.set_ylim(-extent,extent);ax.set_zlim(-extent,extent)
    ax.set_box_aspect((1,1,1),zoom=1.18);ax.set_facecolor(BG)
    ax.add_collection3d(Line3DCollection([W[e] for e in C["edges"]],colors="#78848d",linewidths=.8,alpha=.54))
    ax.add_collection3d(Poly3DCollection(all_faces,facecolors=face_colors,
        edgecolors=(.19,.23,.26,.24 if r["n"]==33 else .42),
        linewidths=.36 if r["n"]==33 else .50,zsort="average"))
    ax.view_init(elev=19 if r["n"]==12 else 20,azim=-53)
    ax._verification_world_vertices=np.vstack([np.asarray(all_vertices),W])
    return r,fig,ax,{"source_path":source_relative,"source_sha256":sha(record_path),
        "solids_path":"src/solids.json","solids_sha256":sha(solids_path),
        "rendered_vertex_count":len(V)*r["n"],"maximum_signed_container_halfspace_excess":max_excess,
        "minimum_rendered_wall_margin":-max_excess,"containment_tolerance":tolerance,
        "rendered_vertices_inside":True,"maximum_rotation_orthogonality_error":orth_error,
        "full_stored_pose_precision_used":True,"shell_indices":shell_indices,
        "piece_colors":colors,"piece_opacities":alphas}

def render(record_id,poster_only=False):
    r,fig,ax,validation=build(record_id)
    stem={"cubincub_n12":"cube-in-cube-n12","dodindod_n33":"dodecahedron-in-dodecahedron-n33"}[record_id]
    poster=OUT/(stem+"-poster.png")
    metadata=PngImagePlugin.PngInfo()
    metadata.add_text("Author",AUTHOR)
    metadata.add_text("Copyright",f"CC BY 4.0; source geometry/coordinates at {FREEZE}; original cube method and n12 family by Yohei Nakajima.")
    metadata.add_text("Description",f"Rendered from the full stored poses of {record_id}; stored scale {r['s_full']}; feasible construction, no global-optimality claim.")
    fig.canvas.draw()
    projection=ax._verification_world_vertices
    projected=proj3d.proj_transform(projection[:,0],projection[:,1],projection[:,2],ax.get_proj())
    xy=ax.transData.transform(np.column_stack(projected[:2]))
    min_canvas_margin=float(min(xy.min(),SIZE-xy.max()))
    assert min_canvas_margin>=2,(record_id,0,min_canvas_margin)
    first=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert("RGB")
    first.save(poster,pnginfo=metadata,optimize=True)
    if poster_only:
        plt.close(fig)
        print(json.dumps({"poster":str(poster),"validation":validation},ensure_ascii=False))
        return
    frames=[first]
    for i in range(1,NFRAMES):
        ax.view_init(elev=19 if r["n"]==12 else 20,azim=-53+360*i/NFRAMES)
        fig.canvas.draw()
        projected=proj3d.proj_transform(projection[:,0],projection[:,1],projection[:,2],ax.get_proj())
        xy=ax.transData.transform(np.column_stack(projected[:2]))
        margin=float(min(xy.min(),SIZE-xy.max()))
        min_canvas_margin=min(min_canvas_margin,margin)
        assert margin>=2,(record_id,i,margin)
        frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert("RGB"))
        if i%12==0:print(f"{record_id}: rendered {i+1}/{NFRAMES}",flush=True)
    plt.close(fig)
    # A shared, explicitly constructed color palette avoids palette changes
    # between frames; it does not alter the plotted geometry or camera path.
    palette_source=Image.new("RGB",(SIZE*8,SIZE))
    for i,j in enumerate(range(0,NFRAMES,6)):palette_source.paste(frames[j],(SIZE*i,0))
    pal=palette_source.quantize(colors=192,method=Image.Quantize.MEDIANCUT)
    indexed=[im.quantize(palette=pal,dither=Image.Dither.FLOYDSTEINBERG) for im in frames]
    gif=OUT/(stem+"-rotation.gif")
    comment=(f"CC BY 4.0; {AUTHOR}; real full-precision {record_id} poses, source {FREEZE}; "
             "original soft-to-rigid cube method and n12 family by Yohei Nakajima; no global-optimality claim.").encode("ascii")
    indexed[0].save(gif,save_all=True,append_images=indexed[1:],duration=DURATION,loop=0,
                    disposal=2,optimize=False,comment=comment)
    with Image.open(gif) as image:
        actual_frames=image.n_frames;actual_size=list(image.size);durations=[]
        for i in range(image.n_frames):
            image.seek(i);durations.append(image.info.get("duration"))
        loop=image.info.get("loop")
    assert actual_frames==NFRAMES and actual_size==[SIZE,SIZE]
    assert durations==[DURATION]*NFRAMES and loop==0
    pixel_count=SIZE*SIZE*NFRAMES
    assert pixel_count<100_000_000
    upstream="Yohei Nakajima: original soft-to-rigid cube method; n12 cube family. Alejandro Zarzuelo Urdiales: generalized search and certified smaller-clearance reproduction." if r["n"]==12 else "Alejandro Zarzuelo Urdiales: generalized search, exact certified configuration, and structural analysis; method/software lineage after Yohei Nakajima."
    alt="Slowly rotating rendering of twelve unit-edge cubes in a wireframe cube. The actual stored translations and rotations are shown, including tilted cubes. This reproduces Yohei Nakajima's touching family with Alejandro Zarzuelo Urdiales's smaller positive-clearance convention." if r["n"]==12 else "Slowly rotating rendering of thirty-three dodecahedra in a wireframe dodecahedron. Gray marks the central particle, ochre the twelve inner-shell pieces, and translucent blue-gray the twenty outer-shell pieces. These are shell colors, not orientation classes; the solid poses are the certified stored configuration."
    info={"record_id":record_id,"source_commit":FREEZE,"author":AUTHOR,"license":"CC BY 4.0",
          "licenseURL":"https://creativecommons.org/licenses/by/4.0/","source_repository":"https://github.com/alejandrozu/platonic-packing",
          "source_record_url":f"https://github.com/alejandrozu/platonic-packing/blob/{FREEZE}/{validation['source_path']}",
          "upstream_credit":upstream,"stored_container_scale":r["s_full"],"numerical_touching_estimate":r.get("s_tight"),
          "claim_scope":"Feasible certified stored construction; no assertion of global optimality.",
          "geometry_validation":validation,"minimum_projected_vertex_canvas_margin_pixels":min_canvas_margin,
          "generation_method":"Scientific Matplotlib polygon renderer, using unrounded stored poses and canonical vertex/face data; homogeneous scalar-first quaternion rotation.",
          "model_generated_image":False,"matplotlib_version":matplotlib.__version__,"numpy_version":np.__version__,
          "animation":{"filename":gif.name,"sha256":sha(gif),"bytes":gif.stat().st_size,"dimensions":actual_size,
                       "frames":actual_frames,"frame_duration_ms":DURATION,"loop_duration_ms":sum(durations),"loop":0,
                       "yaw_degrees_per_frame":360/NFRAMES,"total_decoded_frame_pixels":pixel_count,
                       "under_100_million_frame_pixels":True},
          "poster":{"filename":poster.name,"sha256":sha(poster),"bytes":poster.stat().st_size,"dimensions":[SIZE,SIZE]},
          "alt_text":alt,"commons_upload_status":"LOCAL ONLY; not uploaded to Commons; no Wikimedia filename reserved or invented.",
          "renderer_source":"work/wiki-animation/render_rotating_packings.py"}
    (OUT/(stem+"-manifest.json")).write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"record":record_id,"gif":str(gif),"poster":str(poster),"frames":actual_frames,
                      "loop_ms":sum(durations),"gif_bytes":gif.stat().st_size,"wall_margin":validation["minimum_rendered_wall_margin"]},ensure_ascii=False),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("record_id",choices=["cubincub_n12","dodindod_n33"]);p.add_argument("--poster-only",action="store_true")
    a=p.parse_args();render(a.record_id,a.poster_only)
