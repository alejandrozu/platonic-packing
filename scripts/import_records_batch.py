#!/usr/bin/env python3
"""Copy Platonic records built by the records_platonic workflow into records/ (15 Oct 2026).

    python3 scripts/import_records_batch.py ARTIFACT_DIR [ARTIFACT_DIR ...]

A record is copied only when it was built from the archive's current packing (its 'source' hash matches what
scripts/publish.py computes now) and the local record is missing or stale; its .verify.txt / .certify.txt / .png come
with it. Records of packings that changed since are left to the main machine's publisher."""
import glob, hashlib, json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'src'))
from engine import _read, _path


def current_hash(p, n):
    c = _read(_path('best', p, n)); b = c and c.get('best')
    if not b: return None
    return hashlib.sha1(json.dumps([round(b['s'], 13), b['C'], b['Q']]).encode()).hexdigest()[:16]


def main(dirs):
    took = skipped = 0
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, '*', '*_n[0-9][0-9]*.json'))):
            p = os.path.basename(os.path.dirname(f)); name = os.path.basename(f)
            try: n = int(name.rsplit('_n', 1)[1].split('.')[0]); rec = json.load(open(f))
            except (ValueError, IndexError, json.JSONDecodeError): skipped += 1; continue
            if not isinstance(rec, dict) or rec.get('record_id') != f'{p}_n{n:02d}': skipped += 1; continue
            h = current_hash(p, n)
            if not h or (rec.get('source') or {}).get('hash') != h: skipped += 1; continue
            dst = os.path.join(ROOT, 'records', p, name)
            old = _read(dst) if os.path.exists(dst) else None
            if old and (old.get('source') or {}).get('hash') == h and os.path.exists(dst.replace('.json', '.certify.txt')): continue
            cert = f.replace('.json', '.certify.txt')
            if not os.path.exists(cert) or 'NOT CERTIFIED' in open(cert).read() or 'CERTIFIED' not in open(cert).read(): skipped += 1; continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            for ext in ('.json', '.verify.txt', '.certify.txt', '.png'):
                src = f.replace('.json', ext)
                if os.path.exists(src): shutil.copyfile(src, dst.replace('.json', ext))
            took += 1
    print(f'{took} records imported, {skipped} skipped (packing changed since, or not certified)')


if __name__ == '__main__':
    main(sys.argv[1:])
