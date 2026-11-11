import argparse, json, pathlib, re
p=argparse.ArgumentParser(); p.add_argument('--repo',type=pathlib.Path,required=True); p.add_argument('--out',type=pathlib.Path,required=True); a=p.parse_args()
repo=a.repo.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
sha='e15b496ae7306287e0e70bb5b14be79f5dfdde84'
text=(repo/'site/index.html').read_text(encoding='utf-8')
text=text.replace('/blob/main/',f'/blob/{sha}/')
match=re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)',text,re.S)
data=json.loads(match.group(2))
for problem in data['problems']:
    for row in problem['rows']:
        original=json.loads((repo/row['file']).read_text(encoding='utf-8'))
        row['p']=original['pieces']
text=text[:match.start(2)]+json.dumps(data,separators=(',',':'))+text[match.end(2):]
text=text.replace("spin.checked = !reduce && store.get('ppr-spin') === '1';","spin.checked = !reduce && store.get('ppr-spin') !== '0';")
text=re.sub(r'so the search follows one monotone path from\s+sphere packing to polytope packing\.',
            'so the intermediate shapes are nested. Numerical search still requires rearrangement and can become trapped.',text)
embed_style='''
.embedded-view body{margin:0}
.embedded-view .wrap{max-width:none;margin:0;padding:0}
.embedded-view header,.embedded-view nav,.embedded-view aside,.embedded-view .charts,.embedded-view .notes,.embedded-view footer,.embedded-view .grid>.panel:not(.viewer){display:none!important}
.embedded-view .grid{display:block}
.embedded-view .viewer{position:static;top:auto;width:100%;border:0;border-radius:0}
.embedded-view .stage{height:400px;min-height:260px}
.embedded-view .meta{display:none}
.embedded-view .caption{grid-template-columns:1fr;padding:14px 18px}
'''
text=text.replace('</style>',embed_style+'</style>',1)
text=text.replace('</head>',"<script>if(new URLSearchParams(location.search).get('embed')==='1')document.documentElement.classList.add('embedded-view');</script></head>",1)
notice='''<aside style="padding:14px 20px;background:#fff4d8;color:#342d1f;border-bottom:1px solid #d9c48e;font:14px/1.6 sans-serif">
<strong>Polyhedra in polyhedra packing · 11 October 2026.</strong> 351 feasible constructions from source commit
<code>e15b496ae7306287e0e70bb5b14be79f5dfdde84</code>.
Numerical equality, conjectured formulas, orientation colors and historical comparisons are exploratory;
exact certificates apply to the original full-precision JSON configurations at the links.
The viewer uses the full-precision poses of the stored records. This copy loads Three.js and fonts from external CDNs.
</aside>'''
text=re.sub(r'(<body[^>]*>)',r'\1'+notice,text,count=1)
(out/'packing-explorer.html').write_text(text,encoding='utf-8')
(out/'LICENSE-viewer.txt').write_text((repo/'LICENSE').read_text(encoding='utf-8'),encoding='utf-8')
print('Prepared frozen, self-contained-data explorer; immutable source links and license included.')
