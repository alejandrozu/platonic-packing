"""Before/after figure for a symmetrized record (scripts/symmetrize.py): the container as a wireframe, pieces that the
container maps onto themselves in colour (darker = larger stabilizer), the others in grey.

Usage: python3 scripts/symmetry_figure.py ORIGINAL.json SYMMETRIZED.json OUT.png"""
import json, sys, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symmetrize as sy


def draw(ax, fn, title):
    r, C, Rs = sy.load(fn)
    geo = sy.Geo(r['piece'], r['container']); s = float(r['s_full'])
    sol_p, sol_c = sy.SOL[r['piece']], sy.SOL[r['container']]
    CV = np.array(sol_c['V'], float) * s
    for a, b in sol_c['edges']:
        ax.plot(*zip(CV[a], CV[b]), color='#222222', lw=0.8)
    st = [geo.stabilizer(C[i], Rs[i]) for i in range(len(C))]
    top = max(st + [2])
    cmap = plt.get_cmap('viridis_r')
    view = np.array([1.0, -1.3, 0.8]); view /= np.linalg.norm(view)
    order = np.argsort(C @ view)                        # far pieces first
    for i in order:
        X = C[i] + np.array(sol_p['V'], float) @ Rs[i].T
        faces = [X[F] for F in sol_p['faces']]
        col = cmap(0.25 + 0.75 * np.log(st[i]) / np.log(top)) if st[i] > 1 else (0.78, 0.78, 0.78, 1)
        pc = Poly3DCollection(faces, facecolor=col, edgecolor=(0.15, 0.15, 0.15, 0.6), lw=0.3, alpha=0.92)
        ax.add_collection3d(pc)
    m = CV.max() * 1.02
    ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m, m); ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=-52); ax.set_axis_off()
    k = sum(x > 1 for x in st)
    ax.set_title(f'{title}\n{k} of {len(C)} pieces on a symmetric placement · s = {s:.7f}', fontsize=9)


if __name__ == '__main__':
    a, b, out = sys.argv[1:4]
    fig = plt.figure(figsize=(10, 5.2), dpi=150)
    draw(fig.add_subplot(1, 2, 1, projection='3d'), a, 'record')
    draw(fig.add_subplot(1, 2, 2, projection='3d'), b, 'symmetrized (same container)')
    plt.tight_layout(); plt.savefig(out); print(out)
