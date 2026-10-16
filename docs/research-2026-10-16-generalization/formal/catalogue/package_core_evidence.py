#!/usr/bin/env python3
"""Archive every successful core stage, including root-level probe objects."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

FORMAL = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def checked_path(name):
    p = (FORMAL / name).resolve()
    if not p.is_relative_to(FORMAL.resolve()) or not p.is_file():
        raise ValueError('Missing or unsafe evidence path: ' + str(name))
    return p

def main():
    core = json.loads((FORMAL/'core-verification.json').read_text(encoding='utf8'))
    if core['status'] != 'passed':
        raise ValueError('Core verification did not pass')
    paths = {checked_path(n) for n in ['core-verification.json', 'verify_core.py',
        'lean-toolchain', 'lakefile.toml', 'lake-manifest.json',
        'catalogue/package_core_evidence.py']}
    for row in core['results']:
        for key, hash_key in [('path','source_sha256'), ('olean_path','olean_sha256'),
                              ('log','log_sha256')]:
            p = checked_path(row[key])
            if sha(p) != row[hash_key]:
                raise ValueError('Core receipt byte mismatch: ' + row[key])
            paths.add(p)
    out = FORMAL/'catalogue/ci-core'
    out.mkdir(parents=True,exist_ok=True)
    inventory = dict(schema='complete-core-evidence-v1',
        github_run_id=os.environ.get('GITHUB_RUN_ID'),
        github_commit=os.environ.get('GITHUB_SHA'),
        core_stages=len(core['results']), core_receipt_sha256=sha(FORMAL/'core-verification.json'),
        files=[dict(path=p.relative_to(FORMAL).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
            for p in sorted(paths,key=lambda p:p.relative_to(FORMAL).as_posix())])
    manifest=out/'evidence-inventory.json'
    manifest.write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf8')
    with zipfile.ZipFile(out/'evidence.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in paths | {manifest}:
            z.write(p, 'formal/'+p.relative_to(FORMAL).as_posix())
    print(json.dumps(dict(core_stages=len(core['results']), files=len(paths),
        archive=str(out/'evidence.zip'), archive_sha256=sha(out/'evidence.zip'))))

if __name__ == '__main__':
    main()
