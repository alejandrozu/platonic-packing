import argparse, pathlib, re
p=argparse.ArgumentParser(); p.add_argument('--repo',type=pathlib.Path,required=True); p.add_argument('--out',type=pathlib.Path,required=True); a=p.parse_args()
repo=a.repo.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
sha='e15b496ae7306287e0e70bb5b14be79f5dfdde84'
text=(repo/'site/index.html').read_text(encoding='utf-8')
text=text.replace('/blob/main/',f'/blob/{sha}/')
notice='''<aside style="padding:14px 20px;background:#fff4d8;color:#342d1f;border-bottom:1px solid #d9c48e;font:14px/1.6 sans-serif">
<strong>Paper review snapshot · 11 October 2026.</strong> 351 feasible constructions from source commit
<code>e15b496ae7306287e0e70bb5b14be79f5dfdde84</code>.
Numerical equality, conjectured formulas, orientation colors and historical comparisons are exploratory;
exact certificates apply to the original full-precision JSON configurations at the links.
Rendering coordinates are rounded. This copy loads Three.js and fonts from external CDNs; it publishes nothing.
</aside>'''
text=re.sub(r'(<body[^>]*>)',r'\1'+notice,text,count=1)
(out/'packing-explorer.html').write_text(text,encoding='utf-8')
(out/'LICENSE-viewer.txt').write_text((repo/'LICENSE').read_text(encoding='utf-8'),encoding='utf-8')
print('Prepared frozen, self-contained-data explorer; immutable source links and license included.')
