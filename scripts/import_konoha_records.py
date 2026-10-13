#!/usr/bin/env python3
"""Import issue #1's exact cube poses without changing their geometric values.

Usage: python scripts/import_konoha_records.py ARCHIVE_DIRECTORY
ARCHIVE_DIRECTORY contains the extracted konoha28/ and konoha34_36/ folders.
Contributor executable code is not loaded; only certificate JSON is used.
"""
import contextlib, hashlib, io, json, math, pathlib, sys
from fractions import Fraction as Q
if not __debug__:
    raise SystemExit('Exact canonical-solid checks require assertions; do not use Python -O.')

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import certify_general as U
import verify_general as V

SOURCES={
    28:('konoha28','https://github.com/user-attachments/files/33297232/n28_submission.zip',
        'f58937c6e9cdd9e4b0f5d18a4086d5a607d3adce33f5c471cecca82784ba485d',
        'https://github.com/alejandrozu/platonic-packing/issues/1#issuecomment-6105978918'),
    34:('konoha34_36','https://github.com/user-attachments/files/33296986/n34_36_submission.zip',
        '51a4a58441e44fb93d088008744e6070e8da31d5f042cf5b249801f2ef7dbe82',
        'https://github.com/alejandrozu/platonic-packing/issues/1'),
}

def main():
    archives=pathlib.Path(sys.argv[1]).resolve(); solids=json.loads((ROOT/'src/solids.json').read_text(encoding='utf-8'))
    entries=[]
    for n in (28,34,35,36):
        folder,archive,archive_sha,url=SOURCES[28 if n==28 else 34]
        source=archives/folder/f'n{n}_certificate.json';raw=source.read_bytes();d=json.loads(raw);size=Q(d['S'])
        assert d['n']==n
        pieces=[]
        for cube in d['cubes']:
            center=[Q(c)-size/2 for c in cube['c']]
            floats=list(map(float,center));assert all(Q(x)==c for x,c in zip(floats,center)), 'not exactly binary64'
            pieces.append([*floats,*map(int,cube['q'])])
        sf=float(size);assert Q(sf)==size
        rid=f'cubincub_n{n:02d}_konoha';floor=math.floor(sf*1e5)/1e5
        out={'problem':'min/cube_in_cube','record_id':rid,'piece':'cube','container':'cube','n':n,
             's_full':sf,'s_tight':None,'s':floor,'s_plus':f'{floor:.5f}+','pieces':pieces,'family':'platonic',
             'title':f'{n} cubes in a cube','found_by':'konoha-ily2',
             'credit':'Construction and original rational certificate by konoha-ily2; exact source poses and scale retained.',
             'method':'Sphere-to-cube continuation with L-BFGS; explicit separating-plane tightening; basin hopping for n=28.',
             'date':'2026-10-11','source':{'kind':'external','author':'konoha-ily2','url':url,'archive':archive,
                  'archive_sha256':archive_sha,'original_certificate_sha256':hashlib.sha256(raw).hexdigest(),
                  'source_file':f'docs/literature/external/konoha_n{n}_certificate.json','sha256':hashlib.sha256(raw).hexdigest(),
                  'published_s_full':sf,'normalization':'Exact common translation from [0,S]^3 to an origin-centred container; no inflation or rotation rounding.'},
             'measure':'edge length of the container divided by the edge length of the pieces',
             'format':'[x, y, z, qw, qx, qy, qz]; centres and scalar-first integer quaternions preserve all source rationals exactly',
             'density':n/sf**3,'volume_lower_bound':n**(1/3),'closed_form_conjecture':None,
             'certificate':'exact feasibility certificate replayed with certify_general.py, unchanged canonical geometry'}
        target=ROOT/'records/external/cubincub'/f'{rid}.json';target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(out,indent=1)+'\n',encoding='utf-8')
        for fn,suffix in ((U.main,'.certify.txt'),(V.main,'.verify.txt')):
            buf=io.StringIO()
            with contextlib.redirect_stdout(buf):code=fn(str(target))
            target.with_suffix(suffix).write_text(buf.getvalue(),encoding='utf-8');assert code==0,buf.getvalue()
        source_out=ROOT/'docs/literature/external'/f'konoha_n{n}_certificate.json';source_out.parent.mkdir(parents=True,exist_ok=True)
        source_out.write_bytes(raw)
        entries.append({'problem':'cubincub','n':n,'file':target.relative_to(ROOT).as_posix(),'published_value':sf,
                        'author':'konoha-ily2','url':url,'value_precision':'full exact rational coordinates','kind':'coordinates'})
        print(rid,sf,'CERTIFIED',flush=True)
    receipt=ROOT/'docs/community/2026-10-13/konoha-source-entries.json';receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps(entries,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
