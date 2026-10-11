#!/usr/bin/env python3
"""Move packings between the main archive and extra workers on another machine (Alejandro's laptop).

  python3 scripts/remote.py export STATE REF      print (base64 gzip JSON) every case of STATE/best whose packing is
                                                  smaller than the same case in REF (a state/best tree, e.g. the
                                                  laptop's synced clone of the repo)
  python3 scripts/remote.py import BLOBFILE HOST  decode such a blob and merge it with `engine.py harvest` (every
                                                  packing is re-legalized before it can enter the archive)

The extra workers run `engine.py work` with PP_STATE pointing at their own archive; their results reach the main
archive only through export -> import -> harvest, so the two archives never write to each other's files."""
import base64, gzip, json, os, sys, tempfile, glob


def export(state, ref):
    out = {}
    for f in glob.glob(os.path.join(state, 'best', '*', 'n[0-9][0-9].json')):
        p, nn = f.split(os.sep)[-2], os.path.basename(f)
        try:
            b = json.load(open(f)).get('best')
            r = json.load(open(os.path.join(ref, p, nn))).get('best') if os.path.exists(os.path.join(ref, p, nn)) else None
        except (json.JSONDecodeError, OSError):
            continue
        if b and (r is None or b['s'] < r['s'] - 1e-12):
            out.setdefault(p, {})[nn] = {'best': {k: b[k] for k in ('s', 'C', 'Q', 'src') if k in b}}
    blob = base64.b64encode(gzip.compress(json.dumps(out, separators=(',', ':')).encode())).decode()
    print(f'EXPORT {sum(len(v) for v in out.values())} {blob}')


def do_import(blobfile, host):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import engine
    txt = open(blobfile).read().strip()
    if txt.startswith('EXPORT'): txt = txt.split(None, 2)[2] if len(txt.split(None, 2)) > 2 else ''
    data = json.loads(gzip.decompress(base64.b64decode(txt))) if txt else {}
    with tempfile.TemporaryDirectory() as d:
        for p, cases in data.items():
            os.makedirs(os.path.join(d, p), exist_ok=True)
            for nn, c in cases.items(): json.dump(c, open(os.path.join(d, p, nn), 'w'))
        return engine.harvest(d, host)


if __name__ == '__main__':
    if sys.argv[1] == 'export': export(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'import': do_import(sys.argv[2], sys.argv[3])
