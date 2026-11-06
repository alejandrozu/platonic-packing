"""Verify all high-count exact constructions with Python's standard library.

Optional --derive re-derives the contact polynomial systems using SymPy.
The default replay requires only the Python standard library.
Files are copied into a temporary directory so the evidence is not modified.
"""
from pathlib import Path
import argparse,gzip,json,hashlib,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--derive',action='store_true')
args=parser.parse_args()
with tempfile.TemporaryDirectory(prefix='ap4-high-')as temp:
 root=Path(temp)/'proofs';shutil.copytree(HERE,root,ignore=shutil.ignore_patterns('__pycache__'))
 def run(*parts):
  print('$',*parts,flush=True)
  subprocess.run([sys.executable,*map(str,parts)],cwd=root,check=True)
 run(root/'n17/verify_native.py',root/'n17/n17_exact.json')
 run(root/'check_deletion_plateau.py')
 for n in [18,19]:
  folder=root/f'n{n}'
  certificate=json.loads((folder/'interval_root_certificate.json').read_text())
  expected={name:certificate['source_sha256'][name] for name in ['polynomial_rows.json','structural_reduction.json']}
  if args.derive:
   run(folder/'reduce.py')
  else:
   for name in expected:
    (folder/name).write_bytes(gzip.decompress((folder/(name+'.gz')).read_bytes()))
  assert all(hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest for name,digest in expected.items())
  run(folder/'interval_root.py','--replay')
  run(folder/'check_root_packing.py')
 run(root/'n20/verify_endpoint.py',root/'n20/endpoint.json')
print('PASS: all exact constructions and translation certificates verified.')
