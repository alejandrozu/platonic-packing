import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import crypto from 'node:crypto';

const packet=path.resolve(process.argv[2]||path.join(path.dirname(fileURLToPath(import.meta.url)),'..'));
const repo=path.resolve(process.argv[3]);
const markedPath=process.argv[4];
const {marked}=await import(pathToFileURL(markedPath).href);
const freeze='e15b496ae7306287e0e70bb5b14be79f5dfdde84';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const sources=fs.readFileSync(path.join(packet,'analysis/source-manifest.csv'),'utf8').trim().split(/\r?\n/).slice(1);
const sourceHashes=Object.fromEntries(sources.map(l=>{const cells=l.split(',');return [cells[0],cells[1]];}));
const methodsDOI='https://doi.org/10.5281/zenodo.23306098',patternsDOI='https://doi.org/10.5281/zenodo.23306126';
const comparison=JSON.parse(fs.readFileSync(path.join(packet,'research/current-records.json'),'utf8'));
for(const c of comparison.cases){
  if(c.paperURL?.includes('/docs/research-2026-10-11/paper-1-methods.pdf'))c.paperURL=methodsDOI;
  if(c.analysisPaperURL?.includes('/docs/research-2026-10-11/paper-2-patterns.pdf'))c.analysisPaperURL=patternsDOI;
}
comparison.presentationUpdatedDate='2026-10-12';
comparison.comparisonRecheckedDate='2026-10-12';
comparison.comparisonRecheck='Live Friedman cube and octahedron catalogues retained the existing n=2..12 comparison entries. No exhaustive global-best claim is made.';
fs.writeFileSync(path.join(packet,'research/current-records.json'),JSON.stringify(comparison,null,2)+'\n');
const shapesBytes=fs.readFileSync(path.join(repo,'src/solids.json'));
if(sha(shapesBytes)!==sourceHashes['src/solids.json'])throw Error('Geometry input hash mismatch');
const solidsRaw=JSON.parse(shapesBytes),solids=Object.fromEntries(Object.entries(solidsRaw).map(([name,s])=>[name,{V:s.V,F:s.faces,E:s.edges}]));
const records={},audits=[];
const thumbnailFolder=path.join(packet,'wikipedia-assets/table-thumbnails');
const thumbnailManifest=JSON.parse(fs.readFileSync(path.join(thumbnailFolder,'manifest.json'),'utf8'));
const diagramFolder=path.join(packet,'wikipedia-assets/source-diagrams');
const diagramManifest=JSON.parse(fs.readFileSync(path.join(diagramFolder,'manifest.json'),'utf8'));
function matrix(q){let [w,x,y,z]=q;const norm=Math.hypot(w,x,y,z);w/=norm;x/=norm;y/=norm;z/=norm;return [[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]];}
function mv(m,v){return m.map(row=>row.reduce((s,x,i)=>s+x*v[i],0));}
for(const id of [...comparison.cases.map(c=>c.recordID),'dodindod_n33']){
  const compared=comparison.cases.find(c=>c.recordID===id);
  if(compared&&!compared.configURL){records[id]={id,n:compared.n,piece:compared.piece,container:compared.container,pieces:[],scale:null,url:null};continue;}
  const family=id.split('_n')[0],rel='records/'+family+'/'+id+'.json',bytes=fs.readFileSync(path.join(repo,rel));
  if(sha(bytes)!==sourceHashes[rel])throw Error('Frozen pose hash mismatch: '+id);
  const r=JSON.parse(bytes);if(r.pieces.length!==r.n)throw Error('Population mismatch');
  const b=solidsRaw[r.piece],a=solidsRaw[r.container];let maxGap=-Infinity;
  for(const p of r.pieces){const m=matrix(p.slice(3));for(const v of b.V){const world=mv(m,v).map((x,i)=>x+p[i]);for(const normal of a.normals){const gap=normal.reduce((s,x,i)=>s+x*world[i],0)-a.inradius*r.s_full;maxGap=Math.max(maxGap,gap);}}}
  if(maxGap>1e-10*Math.max(1,r.s_full))throw Error('Rendered vertices exceed container: '+id);
  const item={id,n:r.n,piece:r.piece,container:r.container,scale:r.s_full,pieces:r.pieces,url:'https://github.com/alejandrozu/platonic-packing/blob/'+freeze+'/'+rel};
  const thumb=id==='dodindod_n33'?thumbnailManifest.hero:thumbnailManifest.assets[id];
  if(!thumb||!thumb.orientation_labels||thumb.orientation_labels.length!==r.n)throw Error('Missing orientation colour labels for '+id);
  if(sha(fs.readFileSync(path.join(thumbnailFolder,thumb.png)))!==thumb.sha256)throw Error('Thumbnail hash mismatch: '+id);
  item.orientationLabels=thumb.orientation_labels;
  if(id==='dodindod_n33'){
    const levels=[...new Set(r.pieces.map(p=>Number(Math.hypot(...p.slice(0,3)).toFixed(8))))].sort((a,b)=>a-b);
    if(levels.length!==3)throw Error('Unexpected shell radius classes');
    const low=(levels[0]+levels[1])/2,high=(levels[1]+levels[2])/2;
    item.shells=r.pieces.map(p=>{const radius=Math.hypot(...p.slice(0,3));return radius<low?'center':radius<high?'inner':'outer';});
    const counts=['center','inner','outer'].map(s=>item.shells.filter(v=>v===s).length);
    if(JSON.stringify(counts)!=='[1,12,20]')throw Error('Shell population mismatch');
  }
  records[id]=item;audits.push({id,input_sha256:sha(bytes),pieces:r.n,rendered_vertices:r.n*b.V.length,maximum_containment_gap:maxGap});
}
const data={sourceCommit:freeze,solids,records,palette:thumbnailManifest.palette,faceAlpha:thumbnailManifest.alpha,comparisons:Object.fromEntries(comparison.cases.map(c=>[c.recordID,c])),sourceAnimations:Object.fromEntries(diagramManifest.assets.map(a=>[a.record_id,'wikipedia-assets/source-diagrams/'+a.slow_gif]))};
const md=fs.readFileSync(path.join(packet,'wikipedia-polyhedral-fits.md'),'utf8');
const math=[];
const protectedMd=md.replace(/\$\$[\s\S]*?\$\$|\$(?:\\.|[^$\n])+\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]/g,s=>'POLYMATHTOKEN'+(math.push(s)-1)+'END');
let body=marked.parse(protectedMd).replace(/POLYMATHTOKEN(\d+)END/g,(_,i)=>math[Number(i)].replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'));
body=body.replace(/^<h1>.*?<\/h1>\s*/,'');
const slug=s=>s.replace(/<[^>]+>/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const toc=[];
body=body.replace(/<h2>(.*?)<\/h2>/g,(_,title)=>{const id='wp-'+slug(title);toc.push({id,title:title.replace(/<[^>]+>/g,'')});return '<h2 id="'+id+'">'+title+'</h2>';});
const same=[['tetintet','Tetrahedra in tetrahedron'],['cubincub','Cubes in cube'],['octinoct','Octahedra in octahedron'],['dodindod','Dodecahedra in dodecahedron'],['icoinico','Icosahedra in icosahedron']];
const dual=[['cubinoct','Cubes in octahedron'],['octincub','Octahedra in cube'],['dodinico','Dodecahedra in icosahedron'],['icoindod','Icosahedra in dodecahedron']];
const escape=s=>String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const imageSource=(id,inline=false)=>{
  const asset=id==='dodindod_n33'?thumbnailManifest.hero:thumbnailManifest.assets[id];
  let rel;
  if(asset.external_source_only){const d=diagramManifest.assets.find(a=>a.record_id===id);rel='wikipedia-assets/source-diagrams/'+(inline?d.webp:d.png);}
  else rel='wikipedia-assets/table-thumbnails/'+(inline?asset.png.replace('.png','-inline.webp'):asset.png);
  return inline?'data:image/webp;base64,'+fs.readFileSync(path.join(packet,rel)).toString('base64'):rel;
};
function credit(c){if(c.problem==='cubincub')return c.n<=8?['G','Cubic grid']:c.n<=10?['F/Z','Friedman / Zarzuelo']:c.n===11?['L→Z','Lin → Zarzuelo']:['N/Z','Nakajima / Zarzuelo'];if(c.problem==='octincub')return c.n<=10?['W/Z','Walsh / Zarzuelo']:c.n===11?['W','Walsh']:['L','Lin'];return ['Z','Zarzuelo Urdiales'];}
function table(families,inline=false){let text='<div class="wp-table-scroll"><table><thead><tr><th scope="col">n</th>'+families.map(f=>'<th scope="col">'+f[1]+'</th>').join('')+'</tr></thead><tbody>';
 for(let n=2;n<=12;n++){text+='<tr><th scope="row">'+n+'</th>';for(const [fam]of families){const c=data.comparisons[fam+'_n'+String(n).padStart(2,'0')],id=c.recordID,source=c.paperURL||c.sourceURL;
  const image='<img src="'+imageSource(id,inline)+'" width="240" height="240" loading="lazy" alt="'+escape(n+' '+c.piece+' pieces in a '+c.container)+'">';
  const preview=inline&&!c.configURL?'<a class="wp-image-button" href="'+c.reportedSourceImageURL+'" target="_blank" rel="noopener">'+image+'</a>':'<button class="wp-image-button" data-record="'+id+'" aria-label="'+escape('Inspect '+n+' '+c.piece+' pieces in a '+c.container)+'">'+image+'</button>';
  text+='<td>'+preview+'<div class="wp-result"><a href="'+source+'" target="_blank" rel="noopener">'+escape(c.displayValue)+'</a></div><div class="wp-cell-links">'+(c.configURL?'<a href="'+c.configURL+'" target="_blank" rel="noopener">Construction</a>':'<a href="'+c.sourceURL+'" target="_blank" rel="noopener">Catalogue</a>')+'</div></td>';
 }text+='</tr>';}return text+'</tbody></table></div>';}
let tableIndex=0;
const fullBody=body.replace(/<table>[\s\S]*?<\/table>/g,()=>table(tableIndex++===0?same:dual,false));
if(tableIndex!==2)throw Error('Expected exactly two result tables');
tableIndex=0;
const inlineTableBody=body.replace(/<table>[\s\S]*?<\/table>/g,()=>table(tableIndex++===0?same:dual,true));
body=fullBody;
const sections=inlineTableBody.split(/(?=<h2 id="wp-)/);
const inlineBody=sections.map((section,i)=>{
  if(i===0||section.includes('wp-same-solid-and-dual-solid-results'))return section;
  const h=section.match(/^<h2 id="([^"]+)">(.*?)<\/h2>/);
  if(!h)return section;
  return '<details id="'+h[1]+'"><summary>'+h[2]+'</summary>'+section.slice(h[0].length)+'</details>';
}).join('\n');
const template=fs.readFileSync(path.join(packet,'research/wikipedia-gallery-template.html'),'utf8');
const make=(content,inline=false)=>template.replace('__TOC__',toc.map(t=>'<a href="#'+t.id+'">'+t.title+'</a>').join('')).replace('__ARTICLE_BODY__',content).replace('__HERO_IMAGE__','<img src="'+imageSource('dodindod_n33',inline)+'" width="420" height="420" alt="Thirty-three dodecahedra in a dodecahedron">').replace('__CONSTRUCTION_DATA__',JSON.stringify(data).replace(/</g,'\\u003c'));
const mathScripts='<script>window.MathJax={tex:{inlineMath:[["$","$"]],displayMath:[["$$","$$"]]}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>';
const inline=make(inlineBody,true)+mathScripts;
if(Buffer.byteLength(inline)>=1000000)throw Error('Inline preview exceeds one megabyte');
fs.writeFileSync(path.join(packet,'wikipedia-inline-preview.html'),inline);
const full='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Draft: Polyhedra in polyhedra packing</title><style>body{margin:0}#poly-wiki-preview{max-width:1240px;margin:auto}</style></head><body>'+make(body)+mathScripts+'</body></html>';
fs.writeFileSync(path.join(packet,'wikipedia-article-preview.html'),full);
fs.writeFileSync(path.join(packet,'polyhedra-in-polyhedra-packing.html'),full);
const oldRenderer=path.join(packet,'research/render_article.cjs');
let old=fs.readFileSync(oldRenderer,'utf8');
old=old.replace('Repository article and construction explorer · Alejandro Zarzuelo Urdiales · Source data frozen 11 October 2026. No Wikipedia or external repository submission has been made.',
                'Local draft article and construction explorer · Alejandro Zarzuelo Urdiales · Source data frozen 11 October 2026 · Papers and dataset published on Zenodo; this article has not been submitted to Wikipedia.');
fs.writeFileSync(oldRenderer,old);
const audit={date:'2026-10-12',edition:'Static infobox and image tables',status:'PASS',source_commit:freeze,source_article_sha256:sha(fs.readFileSync(path.join(packet,'wikipedia-polyhedral-fits.md'))),construction_count:audits.length,total_pieces:audits.reduce((s,a)=>s+a.pieces,0),total_rendered_vertices:audits.reduce((s,a)=>s+a.rendered_vertices,0),full_precision_poses:true,all_input_hashes_match:true,all_rendered_vertices_contained:true,external_source_only_records:['octincub_n11','octincub_n12'],source_only_records_use_original_diagrams_and_animation_not_other_poses:true,static_hero:true,static_table_images:99,result_tables:2,result_cells:99,images_with_orientation_colours:97,container_faces_rendered:false,piece_alpha:thumbnailManifest.alpha,inline_bytes:Buffer.byteLength(inline),preview:'../wikipedia-article-preview.html',inline_preview:'../wikipedia-inline-preview.html',constructions:audits};
fs.writeFileSync(path.join(packet,'research/wikipedia-preview-audit.json'),JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify({status:'PASS',records:audits.length,pieces:audit.total_pieces,vertices:audit.total_rendered_vertices,inlineBytes:audit.inline_bytes,articleSha256:audit.source_article_sha256}));
