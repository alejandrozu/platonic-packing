"""Compile one extension with the pinned local dependencies and save evidence."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf8')

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'catalogue'))
import run_lean
ap=argparse.ArgumentParser()
ap.add_argument('path')
ap.add_argument('--mathlib-project',type=Path,default=Path('C:/Users/Propietario/Documents/Codex/rh-paper-work'))
ap.add_argument('--timeout',type=int,default=600)
args=ap.parse_args()
deps=[p/'.lake/build/lib/lean' for p in (args.mathlib_project/'.lake/packages').iterdir()
      if (p/'.lake/build/lib/lean').is_dir()]
env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[HERE,HERE/'.lake/build/lib/lean',*deps]))
lean=Path.home()/'.elan/toolchains/leanprover--lean4---v4.31.0/bin/lean.exe'
row=dict(id='extension_'+Path(args.path).stem,path=args.path)
r=run_lean.run_one(row,lean,env,args.timeout,3072)
receipt=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
    compiler=subprocess.check_output([str(lean),'--version'],text=True).strip(),
    core_source_hashes={str(p.relative_to(HERE)).replace('\\','/'):run_lean.digest(p)
        for p in (HERE/'PackingCertificates').glob('*.lean')},results=[r],passed=r['passed'])
(HERE/(row['id']+'-verification.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:r[k] for k in ('passed','exit_code','elapsed_seconds','log','axioms')}))
if not r['passed']:
    print((HERE/r['log']).read_text(encoding='utf8'))
raise SystemExit(int(not r['passed']))
