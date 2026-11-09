"""Render a journal cover from a frozen native packing witness.

Run: uv run --no-project --with fonttools --with pillow -- python render_cover.py
The SVG outlines its typography and contains no external font/image resources.
No record coordinates, orientations or scale values are changed.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import math
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import fontTools

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parents[2] / 'work/packing-external-records'
COMMIT = 'e3d934be831e9878655d2999fbd6e8fe20d7ffeb'
RECORD = 'records/icoinico/icoinico_n16.json'
WIDTH, HEIGHT, PIXEL_SCALE = 1200, 1600, 3
CREAM, NAVY, TEAL, GOLD = '#f4f0e6', '#152c3c', '#286665', '#b58a43'
PALETTE = ['#286665', '#aa733f', '#637983', '#6b8060', '#6f6077', '#9d5961',
           '#6b8b88', '#907b48', '#315a74', '#a9716d', '#657344', '#6c5b92',
           '#a5895f', '#4b7c6c', '#50768f', '#896b5a']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git_bytes(repo, path, commit):
    return subprocess.check_output(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
                                    '-C', str(repo), 'show', f'{commit}:{path}'])

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def rotation(q):
    m = max(abs(x) for x in q)
    w, x, y, z = [x/m for x in q]
    n = w*w+x*x+y*y+z*z
    return [[v/n for v in row] for row in
            [[w*w+x*x-y*y-z*z, 2*(x*y-w*z), 2*(x*z+w*y)],
             [2*(x*y+w*z), w*w-x*x+y*y-z*z, 2*(y*z-w*x)],
             [2*(x*z-w*y), 2*(y*z+w*x), w*w-x*x-y*y+z*z]]]

def rgb(hexcode, alpha=1):
    return tuple(int(hexcode[i:i+2], 16) for i in (1, 3, 5)) + (round(alpha*255),)

class Canvas:
    def __init__(self):
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                    f'width="8in" height="10.6666667in" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
                    'aria-labelledby="cover-title cover-desc">',
                    '<title id="cover-title">Polyhedra in Polyhedra Journal, Q4 2026</title>',
                    '<desc id="cover-desc">Inaugural issue in progress. Sixteen semi-transparent '
                    'icosahedra in a wireframe icosahedron, drawn from the native icoinico_n16 packing witness.</desc>']
        self.image = Image.new('RGB', (WIDTH*PIXEL_SCALE, HEIGHT*PIXEL_SCALE), CREAM)
        self.draw = ImageDraw.Draw(self.image, 'RGBA')
        self.font_cache = {}
        self.fonts = {}
        self.rect(0, 0, WIDTH, HEIGHT, CREAM)

    def rect(self, x, y, width, height, color, opacity=1):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                        f'fill="{color}" fill-opacity="{opacity}"/>')
        self.draw.rectangle([x*PIXEL_SCALE, y*PIXEL_SCALE, (x+width)*PIXEL_SCALE,
                             (y+height)*PIXEL_SCALE], fill=rgb(color, opacity))

    def line(self, points, color, width, opacity=1):
        coords = ' '.join(f'{x:.4f},{y:.4f}' for x, y in points)
        self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" '
                        f'stroke-width="{width}" stroke-opacity="{opacity}" stroke-linecap="round" '
                        'stroke-linejoin="round"/>')
        self.draw.line([(x*PIXEL_SCALE, y*PIXEL_SCALE) for x, y in points],
                       fill=rgb(color, opacity), width=max(1, round(width*PIXEL_SCALE)), joint='curve')

    def polygon(self, points, color, opacity):
        coords = ' '.join(f'{x:.4f},{y:.4f}' for x, y in points)
        self.svg.append(f'<polygon points="{coords}" fill="{color}" fill-opacity="{opacity}"/>')
        self.draw.polygon([(x*PIXEL_SCALE, y*PIXEL_SCALE) for x, y in points], fill=rgb(color, opacity))

    def text(self, value, x, y, size, color=NAVY, font='serif', tracking=0, align='left'):
        path = Path('C:/Windows/Fonts') / {'serif':'georgia.ttf', 'italic':'georgiai.ttf',
                                         'sans':'segoeui.ttf', 'sans-bold':'seguisb.ttf'}[font]
        if font not in self.fonts:
            face = TTFont(path)
            self.fonts[font] = (face, face.getGlyphSet(), face.getBestCmap(), face['head'].unitsPerEm)
        face, glyphs, cmap, upm = self.fonts[font]
        scale = size/upm
        names = [cmap.get(ord(char), '.notdef') for char in value]
        advances = [face['hmtx'][name][0]*scale + tracking for name in names]
        length = sum(advances)-tracking
        if align == 'right': x -= length
        if align == 'center': x -= length/2
        key = (str(path), size)
        if key not in self.font_cache:
            self.font_cache[key] = ImageFont.truetype(str(path), round(size*PIXEL_SCALE))
        pfont = self.font_cache[key]
        self.svg.append(f'<g aria-label="{html.escape(value, quote=True)}" fill="{color}">')
        for char, name, advance in zip(value, names, advances):
            pen = SVGPathPen(glyphs)
            glyphs[name].draw(pen)
            d = pen.getCommands()
            if d:
                self.svg.append(f'<path transform="translate({x:.4f},{y:.4f}) scale({scale:.8f},'
                                f'{-scale:.8f})" d="{d}"/>')
            self.draw.text((x*PIXEL_SCALE, y*PIXEL_SCALE), char, font=pfont,
                           fill=rgb(color), anchor='ls')
            x += advance
        self.svg.append('</g>')
        return length

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--commit', default=COMMIT)
    args = parser.parse_args()
    record_raw = git_bytes(args.repo, RECORD, args.commit)
    solids_raw = git_bytes(args.repo, 'src/solids.json', args.commit)
    rec = json.loads(record_raw)
    solid = json.loads(solids_raw)['icosahedron']
    V = solid['V']
    assert rec['piece'] == rec['container'] == 'icosahedron'
    assert rec['n'] == len(rec['pieces']) == 16
    whole = []
    max_edge_error = 0
    min_wall_slack = float('inf')
    for pose in rec['pieces']:
        R = rotation(pose[3:])
        X = [[dot(row, v)+c for row, c in zip(R, pose[:3])] for v in V]
        for a, b in solid['edges']:
            edge = math.sqrt(sum((X[a][q]-X[b][q])**2 for q in range(3)))
            max_edge_error = max(max_edge_error, abs(edge-1))
        for v in X:
            for normal in solid['normals']:
                min_wall_slack = min(min_wall_slack, rec['s_full']*solid['inradius']-dot(v, normal))
        whole.append(X)
    assert max_edge_error < 1e-12
    assert min_wall_slack > -1e-12

    # One common rigid camera, then one common display scale, for all geometry.
    elev, azim = map(math.radians, (22, 37))
    eye = [math.cos(elev)*math.cos(azim), math.cos(elev)*math.sin(azim), math.sin(elev)]
    right = [-math.sin(azim), math.cos(azim), 0]
    up = [-math.sin(elev)*math.cos(azim), -math.sin(elev)*math.sin(azim), math.cos(elev)]
    WC = [[x*rec['s_full'] for x in v] for v in V]
    projected = [(dot(v, right), -dot(v, up)) for v in WC]
    extent_x = max(p[0] for p in projected)-min(p[0] for p in projected)
    extent_y = max(p[1] for p in projected)-min(p[1] for p in projected)
    scale = min(990/extent_x, 775/extent_y)
    center = ((max(p[0] for p in projected)+min(p[0] for p in projected))/2,
              (max(p[1] for p in projected)+min(p[1] for p in projected))/2)
    def project(v):
        return (600+(dot(v, right)-center[0])*scale, 835+(-dot(v, up)-center[1])*scale)

    c = Canvas()
    c.rect(0, 0, 16, HEIGHT, TEAL)
    c.text('JOURNAL', 84, 97, 24, TEAL, 'sans-bold', tracking=6)
    c.text('VOLUME 1  /  ISSUE 1', 1116, 97, 18, NAVY, 'sans', tracking=2.3, align='right')
    c.line([(84, 120), (1116, 120)], GOLD, 1.25)
    c.text('Polyhedra', 78, 244, 112)
    c.text('in Polyhedra', 80, 360, 103)
    c.text('GEOMETRY  /  COMPUTATION  /  CERTIFIED CONSTRUCTIONS', 85, 410, 15.5,
           TEAL, 'sans', tracking=1.4)

    # Light depth-sorted faces show the actual arrangement through every layer.
    faces = []
    for i, X in enumerate(whole):
        for f in solid['faces']:
            depth = sum(dot(X[j], eye) for j in f)/len(f)
            faces.append((depth, i, [project(X[j]) for j in f]))
    for _, i, points in sorted(faces):
        c.polygon(points, PALETTE[i], 0.033)
    ordered = sorted(enumerate(whole), key=lambda pair: sum(dot(v, eye) for v in pair[1])/len(V))
    for i, X in ordered:
        for a, b in solid['edges']:
            c.line([project(X[a]), project(X[b])], PALETTE[i], 1.26, 0.69)
    for a, b in solid['edges']:
        c.line([project(WC[a]), project(WC[b])], NAVY, 1.95, 0.84)

    c.text('SIXTEEN ICOSAHEDRA IN AN ICOSAHEDRON', 84, 1272, 15.3,
           TEAL, 'sans-bold', tracking=1.2)
    c.text('Native construction: icoinico_n16', 84, 1301, 16, NAVY, 'sans')
    c.text('s = 3.121305388046', 1116, 1301, 16, NAVY, 'sans', align='right')
    c.line([(84, 1331), (1116, 1331)], GOLD, 1.25)

    c.text('Inaugural issue', 80, 1401, 45)
    c.text('in progress', 82, 1451, 41, TEAL, 'italic')
    c.text('Q4', 1114, 1410, 70, NAVY, 'serif', align='right')
    c.text('2026', 1116, 1455, 36, TEAL, 'sans', tracking=4, align='right')
    c.line([(84, 1490), (1116, 1490)], GOLD, 1.25)
    c.text('OPEN ACCESS', 84, 1535, 19, TEAL, 'sans-bold', tracking=3)
    c.text('polyhedrainpolyhedra.wiki', 1116, 1535, 19, NAVY, 'sans', align='right')
    c.svg.append('</svg>')
    svg = '\n'.join(c.svg).encode('utf8')
    (HERE/'q4-2026-cover.svg').write_bytes(svg)
    c.image.save(HERE/'q4-2026-cover.png', dpi=(450, 450), optimize=True)
    preview = c.image.copy()
    preview.thumbnail((900, 1200), Image.Resampling.LANCZOS)
    preview.save(HERE/'q4-2026-cover-preview.png', optimize=True)
    (HERE/'icoinico_n16.json').write_bytes(record_raw)
    (HERE/'icosahedron-geometry.json').write_text(json.dumps(solid, indent=2)+'\n')
    provenance = dict(schema='journal-cover-native-witness-v1', commit=args.commit,
        source_record=RECORD, source_record_sha256=sha(record_raw), geometry_source='src/solids.json',
        source_record_url=f'https://github.com/alejandrozu/platonic-packing/blob/{args.commit}/{RECORD}',
        interactive_record_url='https://polyhedrainpolyhedra.wiki/#icoinico_n16',
        complete_geometry_source_sha256=sha(solids_raw), n=16, s_full=rec['s_full'],
        original_found_by=rec.get('found_by'), camera=dict(type='orthographic', elevation_degrees=22,
            azimuth_degrees=37, pixel_scale_per_native_unit=scale, art_center=[600,835]),
        display_geometry_changes='None; scalar-first quaternion H(q)/norm(q)^2 and one common projection.',
        palette='Piece-index identities, not claimed symmetry-aware orientation classes.',
        maximum_unit_edge_error=max_edge_error, minimum_float_wall_slack=min_wall_slack,
        verification_boundary='Display sanity checks only. Existing catalogue certificate supplies exact feasibility.',
        svg=dict(width_inches=8, height_inches=10.6666667, viewbox=[0,0,WIDTH,HEIGHT],
                 typography='Georgia and Segoe UI glyph outlines; no external fonts or images'),
        png=dict(width=WIDTH*PIXEL_SCALE,height=HEIGHT*PIXEL_SCALE),
        versions=dict(python=sys.version, pillow=Image.__version__, fonttools=fontTools.__version__),
        files={name:sha((HERE/name).read_bytes()) for name in
               ['q4-2026-cover.svg','q4-2026-cover.png','q4-2026-cover-preview.png','render_cover.py',
                'icoinico_n16.json','icosahedron-geometry.json']})
    (HERE/'cover-provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(provenance, indent=2))

if __name__ == '__main__':
    main()
