#!/usr/bin/env python3
"""Normalize independently published coordinates and certify imported copies.

This never edits the search archive or the project's existing records. Imported
records live in records/external/. Authorship and the exact upstream file are
retained; adding our usual 1e-7 clearance is not a new geometric improvement.
"""
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import urlopen

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from claim import make_claim_fast
from exact import Problem, SOL

SOURCES = ROOT / 'docs' / 'literature' / 'external'
GAP = 1e-7
DATE = '2026-10-13'


def save_source(name, url):
    SOURCES.mkdir(parents=True, exist_ok=True)
    path = SOURCES / name
    if not path.exists():
        path.write_bytes(urlopen(url, timeout=45).read())
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def write_claim(pid, tag, piece, centers, quaternions, published, source, note):
    pb = Problem(piece, 'cube')
    n = len(centers)
    rid = f'{pid}_n{n:02d}_{tag}'
    meta = {
        'record_id': rid,
        'title': f'{n} unit {"cubes" if piece == "cube" else "octahedra"} in a cube',
        'found_by': source['author'],
        'credit': f"Published construction by {source['author']}; imported and checked without transferring discovery credit.",
        'method': source['method'],
        'date': DATE,
        'source': {**source, 'kind': 'external', 'published_s_full': published,
                   'normalization': note, 'imported_on': DATE},
        'search': {'move': 'published construction'},
        'volume_lower_bound': (n * SOL[piece]['volume'] / SOL['cube']['volume']) ** (1 / 3),
        'closed_form_conjecture': None,
    }
    claim = make_claim_fast({'piece': piece, 'container': 'cube', 'C': np.asarray(centers) * pb.edge,
                             'Q': quaternions}, GAP=GAP, WALL=GAP, meta=meta)
    # The upstream value is reported separately, not recast as a newly improved
    # touching limit just because recentering or rounding changes its last digits.
    claim['s_tight'] = None
    claim['density'] = n * SOL[piece]['volume'] / (SOL['cube']['volume'] * claim['s_full'] ** 3)
    folder = ROOT / 'records' / 'external' / pid
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (rid + '.json')
    path.write_text(json.dumps(claim, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    for script, suffix in [('verify.py', '.verify.txt'), ('certify_exact.py', '.certify.txt')]:
        check = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / script), str(path)],
                               capture_output=True, text=True, encoding='utf-8')
        path.with_suffix(suffix).write_text(check.stdout + check.stderr, encoding='utf-8')
        if check.returncode:
            raise RuntimeError(f'{rid}: {script} failed\n{check.stdout}\n{check.stderr}')
    print(f'{rid}: published {published:.15f}, clearance copy {claim["s_full"]:.15f}: CERTIFIED', flush=True)
    return {'problem': pid, 'n': n, 'file': path.relative_to(ROOT).as_posix(),
            'published_value': published, 'author': source['author'], 'url': source['url'],
            'value_precision': 'full coordinates', 'kind': 'coordinates'}


def main():
    imports = []
    existing = [('cubincub', 'cube', 11, 'hyra'), ('cubincub', 'cube', 12, 'hyra'),
                ('octincub', 'octahedron', 21, 'hyra'), ('octincub', 'octahedron', 24, 'hyra'),
                ('cubincub', 'cube', 12, 'nakajima')]
    for pid, piece, n, tag in existing:
        if tag == 'hyra':
            revision = '09b2d2e3c362c67a78f544c836bd8e4b54a05527'
            repository = 'https://github.com/Tencent-Hunyuan/Hyra-results'
            filename = f'AI4Science/packing_records/records/{pid}_n{n}.json'
            url = f'https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/{revision}/{filename}'
            author, method = 'Haowei Lin (Tencent Hunyuan)', 'Published packing from Tencent Hunyuan Hyra-results'
        else:
            revision = 'efe7a920142350a4f0678633490c3e3dbed71fa0'
            repository = 'https://github.com/yoheinakajima/soft-to-rigid-packing'
            filename = 'claims/cubincub_n12/cubincub_n12.json'
            url = f'https://raw.githubusercontent.com/yoheinakajima/soft-to-rigid-packing/{revision}/{filename}'
            author, method = 'Yohei Nakajima', 'Soft-to-rigid cube packing with subsequent tightening'
        path, sha = save_source(f'{tag}-{pid}-n{n:02d}.json', url)
        rec = json.loads(path.read_text(encoding='utf-8'))
        poses = np.asarray(rec['pieces'], dtype=float)
        center = np.asarray(rec.get('container_center', [rec['s_full'] / 2] * 3))
        source = {'author': author, 'repository': repository, 'revision': revision,
                  'url': f'{repository}/blob/{revision}/{filename}', 'source_file': path.relative_to(ROOT).as_posix(),
                  'sha256': sha, 'method': method}
        imports.append(write_claim(pid, tag, piece, poses[:, :3] - center, poses[:, 3:], rec['s_full'], source,
                                   'Published unit-edge poses; translate to the origin, normalize rotations, '
                                   'and refit with 1e-7 pair and wall clearance.'))

    revision = '9535d65d84cc33f20f4e26329f8da12bdcef216e'
    raw_url = f'https://raw.githubusercontent.com/ry-xu/square_packing/{revision}/cube_packing_records.json'
    path, sha = save_source('ry-xu-cube-packing-records.json', raw_url)
    source = {'author': 'Ryan Xu', 'handle': '@small_LM', 'repository': 'https://github.com/ry-xu/square_packing',
              'revision': revision, 'url': f'https://github.com/ry-xu/square_packing/blob/{revision}/cube_packing_records.json',
              'source_file': path.relative_to(ROOT).as_posix(), 'sha256': sha,
              'method': 'LLM-driven evolutionary program search, as described in the upstream repository'}
    for rec in json.loads(path.read_text(encoding='utf-8'))['records']:
        s = float(rec['side'])
        poses = np.asarray([[float(p[k]) for k in ('x', 'y', 'z', 'qw', 'qx', 'qy', 'qz')] for p in rec['cubes']])
        imports.append(write_claim('cubincub', 'ryxu', 'cube', poses[:, :3] - s / 2, poses[:, 3:], s, source,
                                   'Unit-edge cubes in [0,s]^3; translate centers by -s/2, normalize quaternions, '
                                   'then uniformly spread centers and refit the container for 1e-7 clearance.'))

    revision = '27f71632d8655ae4b6a049410a401976748b94e3'
    filename = 'platonic/l3/m2/n17/platonic_n17_m2_l3.html'
    raw_url = f'https://raw.githubusercontent.com/DominikKamp/Packing/{revision}/{filename}'
    path, sha = save_source('kamp-octahedra-in-cube-n17.html', raw_url)
    text_path, _ = save_source('kamp-octahedra-in-cube-n17.txt', raw_url.replace('.html', '.txt'))
    raw = path.read_text(encoding='utf-8')
    match = re.search(r'Plotly.newPlot\(\s*"[^"]+",\s*', raw)
    traces = json.JSONDecoder().raw_decode(raw[match.end():])[0]
    meshes = [t for t in traces if t.get('type') == 'mesh3d']
    assert len(meshes) == 17
    centers, quaternions = [], []
    max_error = 0.0
    def decode(value):
        return np.frombuffer(base64.b64decode(value['bdata']), dtype=value['dtype']) if isinstance(value, dict) else np.asarray(value)
    for mesh in meshes:
        V = np.column_stack([decode(mesh[k]) for k in 'xyz'])
        center = V.mean(axis=0)
        axes = (V[[0, 2, 4]] - center).T
        # Source octahedra have unit circumradius. Opposite pairs are ordered
        # (0,1),(2,3),(4,5); fitting the three orthogonal directions removes only
        # last-bit conversion noise, verified against all six published vertices.
        u, _, vt = np.linalg.svd(axes)
        rot = u @ vt
        if np.linalg.det(rot) < 0:
            rot[:, 2] *= -1
        canonical = np.concatenate([np.eye(3), -np.eye(3)]) @ rot.T + center
        error = max(min(np.linalg.norm(v - w) for w in V) for v in canonical)
        max_error = max(max_error, float(error))
        assert error < 1e-12, error
        quat = Rotation.from_matrix(rot).as_quat()
        centers.append(center / math.sqrt(2))
        quaternions.append([quat[3], *quat[:3]])
    published = float(text_path.read_text().splitlines()[1]) * math.sqrt(2 / 3)
    source = {'author': 'T. Berthold, D. Kamp, G. Mexi, S. Pokutta and I. Polik',
              'repository': 'https://github.com/DominikKamp/Packing', 'revision': revision,
              'url': f'https://github.com/DominikKamp/Packing/blob/{revision}/{filename}',
              'source_file': path.relative_to(ROOT).as_posix(), 'sha256': sha,
              'paper': 'Out-of-the-Box Global Optimization for Packing Problems: New Models and Improved Solutions (2026)',
              'method': 'Global optimization models from the 2026 Berthold, Kamp, Mexi, Pokutta and Polik paper',
              'vertex_conversion_max_error': max_error}
    imports.append(write_claim('octincub', 'kamp', 'octahedron', centers, quaternions, published, source,
                               'Published mesh vertices have unit circumradius; divide centers by sqrt(2) to obtain '
                               'unit edges. Fit canonical octahedron rotations to all six vertices (maximum discrepancy '
                               f'{max_error:.3g} source units), then add 1e-7 clearance.'))
    catalogue = json.loads((ROOT / 'docs' / 'references.json').read_text(encoding='utf-8'))
    entries = []
    for pid in ('cubincub', 'octincub'):
        for nn, (value, author) in catalogue[pid].items():
            n = int(nn)
            expression = None
            if pid == 'cubincub' and n in (9, 10):
                value, expression = 2 + 1 / math.sqrt(2), '2 + 1/√2'
            elif pid == 'cubincub' and n == 14:
                value, expression = 2 + 7 * math.sqrt(2) / 10, '2 + 7√2/10'
            elif pid == 'cubincub' and 28 <= n <= 33:
                value, expression = 3 + 1 / math.sqrt(2), '3 + 1/√2'
            elif pid == 'octincub' and n == 2:
                value, expression = math.sqrt(2), '√2'
            if pid == 'cubincub':
                image = 'cube10.gif' if n in (9, 10) else 'cube33.gif' if 28 <= n <= 33 else f'cube{n}.gif' if n in (11,12,13,14) else None
            else:
                image = f'{8 if n in (7,8) else 27 if n in (26,27) else n}.gif' if n <= 30 else None
            url = f'https://erich-friedman.github.io/packing/{pid}/'
            name = ('Yohei Nakajima' if author.startswith('Y. Nakajima') else 'Erich Friedman' if 'Friedman, 1998' in author else
                    'Ríain Walsh' if 'Walsh' in author else 'Haowei Lin' if 'Lin' in author else 'Trivial grid')
            if name == 'Yohei Nakajima':
                url = 'https://github.com/yoheinakajima/soft-to-rigid-packing'
            entries.append({'problem': pid, 'n': n, 'published_value': value, 'published_expression': expression,
                            'author': name, 'original_reference': author,
                            'url': url, 'image_url': f'https://erich-friedman.github.io/packing/{pid}/' + image if image else None,
                            'display_quantum': .001 if pid == 'cubincub' and n == 13 else 1e-5,
                            'value_precision': 'published expression' if expression else 'catalogue display; not a full-precision certificate', 'kind': 'catalogue'})
    entries.append({'problem': 'cubincub', 'n': 28, 'published_value': 3.66600,
                    'author': '紺葉 (@konoha_ily2)',
                    'url': 'https://x.com/konoha_ily2/status/2109306733999120589', 'image_url': None,
                    'value_precision': 'author-reported value; coordinates and the claimed certificate were not available for local verification',
                    'kind': 'author_report'})
    registry_path = ROOT / 'docs' / 'external_records.json'
    previous = json.loads(registry_path.read_text(encoding='utf-8')).get('entries', []) if registry_path.exists() else []
    def entry_key(e):
        return ('file', e['file']) if e.get('file') else (e['problem'], e['n'], e['kind'], e['url'], e['author'])
    merged = {entry_key(e): e for e in previous}
    merged.update({entry_key(e): e for e in imports + entries})
    registry = {'checked_on': DATE,
                'scope': 'Registered independent coordinate sources and published comparison bounds; not a claim of global completeness or optimality.',
                'entries': list(merged.values())}
    (ROOT / 'docs' / 'external_records.json').write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
