"""Verify the square-antiprism constructions and their native records."""
from pathlib import Path
import argparse, json, shutil, subprocess, sys, tempfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--native-only',action='store_true')
args=parser.parse_args()

def run(*parts,cwd=None):
    subprocess.run([sys.executable,*map(str,parts)],cwd=cwd,check=True)

if not args.native_only:
    with tempfile.TemporaryDirectory(prefix='ap4-proof-')as name:
        p=Path(name)/'proofs'
        shutil.copytree(HERE/'proofs',p,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        low=p/'low'
        for n in [2,3]:run(low/f'n{n:02}'/'verify.py')
        for n in [4,7]:run(low/'verify_endpoint.py',low/f'n{n:02}'/'endpoint.json')
        for n in [5,6]:
            run(low/f'n{n:02}'/'verify.py')
            run(low/f'n{n:02}'/'verify_decoder.py')
        run(p/'mid/verify_endpoint.py',*[p/f'mid/n{n:02}.json'for n in range(8,15)])
        run(p/'high/verify.py')

cases=json.loads((HERE/'bounds.json').read_text())['cases']
assert [c['n']for c in cases]==list(range(2,21))
for case in cases:
    record=REPO/case['record']
    run(REPO/'certify_general.py',record)
    run(REPO/'verify_general.py',record)
print('PASS: 19 square-antiprism native records'+(''if args.native_only else ' and all exact endpoint proofs')+'.')
