#!/usr/bin/env python3
"""Restore the compressed derived rational witnesses and check every byte hash.

These are untrusted proposed certificates, not proof receipts. The Lean kernel
must check any regenerated instance before it is called formally verified.
"""
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent


def main():
    with zipfile.ZipFile(HERE / 'rational-witnesses.zip') as archive:
        manifest = json.loads(archive.read('witness-manifest.json'))
        for row in manifest['files']:
            path = (HERE / row['path']).resolve()
            if not path.is_relative_to(HERE) or path.parts[len(HERE.parts)] not in ('witnesses', 'witnesses_nd'):
                raise ValueError('Unexpected archive path')
            data = archive.read(row['path'])
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('Witness archive hash mismatch: ' + row['path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({'restored_proposed_witnesses': len(manifest['files']),
                      'formal_verification': 'Requires successful Lean builds; unpacking is not verification'}))


if __name__ == '__main__':
    main()
