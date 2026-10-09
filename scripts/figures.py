#!/usr/bin/env python3
"""Render claim files as PNGs. usage: python3 scripts/figures.py [claims/<case>/nXX.json ...]
(no arguments: every claim, plus one overview sheet per piece/container case in figures/)."""
import json, os, sys, glob, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
PAL = ['#4C78A8', '#F58518', '#54A24B', '#E45756', '#72B7B2', '#EECA3B', '#B279A2', '#FF9DA6', '#9D755D', '#BAB0AC',
       '#2F6690', '#D1495B', '#66A182', '#EDAE49', '#00798C', '#8F2D56', '#3A6EA5', '#C44536', '#6A994E', '#BC6C25']


def R(q):
    q = np.array(q) / np.linalg.norm(q); w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)], [2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)], [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)]])


def draw(ax, c, title=True, elev=22, azim=-58):
    P, C = SOL[c['piece']], SOL[c['container']]
    s = c['s_full']; cc = np.array(c.get('container_center', [0, 0, 0]))
    CV = np.array(C['V']) * s + cc
    light = np.array([0.4, -0.5, 0.75]); light /= np.linalg.norm(light)
    polys, cols = [], []   # one collection, so faces are depth-sorted together
    for k, p in enumerate(c['pieces']):
        Rm = R(p[3:]); X = np.array(p[:3]) + np.array(P['V']) @ Rm.T
        base = np.array(matplotlib.colors.to_rgb(PAL[k % len(PAL)]))
        for f, nrm in zip(P['faces'], P['normals']):
            polys.append(X[f]); sh = 0.55 + 0.45 * max(0.0, float((Rm @ np.array(nrm)) @ light))
            cols.append((*np.clip(base * sh, 0, 1), 0.92))
    ax.add_collection3d(Poly3DCollection(polys, facecolors=cols, edgecolors=(0.1, 0.1, 0.1, 0.6), linewidths=0.4))
    ax.add_collection3d(Line3DCollection([CV[list(e)] for e in C['edges']], colors=(0.15, 0.15, 0.15, 0.9), linewidths=1.1))
    m = np.abs(CV - cc).max() * 1.02
    for setlim, k in ((ax.set_xlim, 0), (ax.set_ylim, 1), (ax.set_zlim, 2)): setlim(cc[k] - m, cc[k] + m)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    if title: ax.set_title(f"n = {c['n']}   s = {c['s']:.5f}+", fontsize=10)


def one(path, out=None):
    c = json.load(open(path))
    fig = plt.figure(figsize=(4, 4), dpi=150); ax = fig.add_subplot(111, projection='3d')
    draw(ax, c)
    out = out or path.replace('.json', '.png')
    fig.savefig(out, bbox_inches='tight', pad_inches=0.05); plt.close(fig)
    return out


def sheet(case_dir, out):
    files = sorted(glob.glob(os.path.join(case_dir, 'n*.json')), key=lambda f: int(os.path.basename(f)[1:3]))
    files = [f for f in files if not f.endswith(('.verify.json', '.certify.json'))]
    if not files: return
    cols = 4; rows = math.ceil(len(files) / cols)
    fig = plt.figure(figsize=(3.2 * cols, 3.3 * rows), dpi=110)
    for i, f in enumerate(files):
        ax = fig.add_subplot(rows, cols, i + 1, projection='3d'); draw(ax, json.load(open(f)))
    c = json.load(open(files[0]))
    fig.suptitle(f"unit {c['piece']}s in the smallest {c['container']} found (s = container edge / piece edge)", fontsize=12)
    fig.tight_layout(); fig.savefig(out, bbox_inches='tight'); plt.close(fig)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for p in sys.argv[1:]: print(one(p))
    else:
        os.makedirs(os.path.join(ROOT, 'figures'), exist_ok=True)
        for d in sorted(glob.glob(os.path.join(ROOT, 'claims', '*'))):
            for p in glob.glob(os.path.join(d, 'n*.json')): one(p)
            sheet(d, os.path.join(ROOT, 'figures', os.path.basename(d) + '.png'))
            print('sheet', os.path.basename(d))
