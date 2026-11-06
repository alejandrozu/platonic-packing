"""Replay the N20 exact primal/dual certificate with the standard library."""
from pathlib import Path
import shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='ap4-n20-') as temp:
 folder=Path(temp)
 for name in ['endpoint.json','verify_endpoint.py','check_field.py']:
  shutil.copy2(HERE/name,folder/name)
 subprocess.run([sys.executable,str(folder/'verify_endpoint.py'),str(folder/'endpoint.json')],cwd=folder,check=True)
