"""New figures for Paper III (patterns, dimensions 4-6): docs/papers/III-patterns/fig_nd_*.pdf

Reads docs/patterns/stats_nd.json and features_nd.json (written by scripts/patterns/features_nd.py, stats_nd.py).
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'docs', 'papers', 'III-patterns')
DATA = os.path.join(ROOT, 'docs', 'patterns')
plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'cm', 'font.size': 9, 'axes.linewidth': 0.6,
                     'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02})
BLUE, ORANGE, GREY, RED = '#2b5797', '#d9822b', '#777777', '#b22222'
NAMES = {'c5': '5-cell', 'c8': 'tesseract', 'c16': '16-cell', 'c24': '24-cell', 'c120': '120-cell', 'c600': '600-cell',
         'sx5': '5-simplex', 'hc5': '5-cube', 'op5': '5-orthoplex', 'sx6': '6-simplex', 'hc6': '6-cube', 'op6': '6-orthoplex'}
ORDER = ['c5', 'c8', 'c16', 'c24', 'c600', 'c120', 'sx5', 'hc5', 'op5', 'sx6', 'hc6', 'op6']


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.pdf')); plt.close(fig)


def fig_nd_containers():
    """Share of records with nontrivial symmetry and with one orientation class, by container."""
    st = json.load(open(os.path.join(DATA, 'stats_nd.json')))
    bc = st['by_container']; ref = st['reference_3d']
    ys = np.arange(len(ORDER))[::-1].astype(float)
    for k in range(len(ORDER)):            # gaps between the dimension groups
        if k >= 6: ys[k] -= 0.6
        if k >= 9: ys[k] -= 0.6
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    h = 0.36
    sym = [100 * bc[c]['symmetric'] for c in ORDER]; one = [100 * bc[c]['single_orientation'] for c in ORDER]
    ax.barh(ys + h / 2, sym, height=h, color=BLUE, label='nontrivial symmetry')
    ax.barh(ys - h / 2, one, height=h, color=ORANGE, label='one orientation class')
    ax.axvline(100 * ref['symmetric'], color=BLUE, lw=0.7, ls='--')
    ax.axvline(100 * ref['single_orientation'], color=ORANGE, lw=0.7, ls=':')
    ax.text(100 * ref['symmetric'] - 0.4, ys[0] + 0.75, '3D: %.1f%%' % (100 * ref['symmetric']), color=BLUE, fontsize=7,
            ha='right')
    ax.text(100 * ref['single_orientation'] + 0.4, ys[0] + 0.75, '3D: %.1f%%' % (100 * ref['single_orientation']),
            color=ORANGE, fontsize=7)
    ax.set_yticks(ys); ax.set_yticklabels(['%s (%d)' % (NAMES[c], bc[c]['records']) for c in ORDER], fontsize=8)
    for grp, lab in ((range(0, 6), '4D'), (range(6, 9), '5D'), (range(9, 12), '6D')):
        ax.text(-13.5, np.mean([ys[k] for k in grp]), lab, fontsize=8.5, fontweight='bold', ha='right', va='center',
                clip_on=False)
    ax.set_xlabel('share of records (%)'); ax.set_xlim(0, 40); ax.set_ylim(ys[-1] - 0.7, ys[0] + 1.3)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, fontsize=7.5, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2)
    save(fig, 'fig_nd_containers')


def fig_nd_angles():
    """Relative rotations between orientation classes in 4D: the two rotation angles of each class pair."""
    f = json.load(open(os.path.join(DATA, 'features_nd.json')))
    A, rat = [], []
    for x in f:
        if x['dim'] != 4 or not x['rel']: continue
        for r in x['rel']:
            a = sorted(r['angles'], reverse=True)
            A.append(a); rat.append(bool(r['rational']))
    A = np.array(A); rat = np.array(rat)
    fig, ax = plt.subplots(figsize=(3.6, 3.3))
    ax.scatter(A[~rat, 0], A[~rat, 1], s=3, color=GREY, alpha=0.35, lw=0, label='other (%d)' % (~rat).sum())
    ax.scatter(A[rat, 0], A[rat, 1], s=10, color=BLUE, alpha=0.8, lw=0, label='rational (%d)' % rat.sum())
    ax.plot([0, 180], [0, 180], color='k', lw=0.4, ls=':')
    for (a, b), lab, dx, dy in (((60, 60), r'$(60^\circ,60^\circ)$', 3, 3), ((45, 45), r'$(45^\circ,45^\circ)$', -3, 3),
                                ((108, 36), r'$(108^\circ,36^\circ)$', 3, 3)):
        ax.annotate(lab, (a, b), (a + dx, b + dy), fontsize=7, color=BLUE, ha='right' if dx < 0 else 'left')
    for a, yy in ((45, -9), (72, -9), (90, -9)):
        ax.annotate(r'$%d^\circ$' % a, (a, 0), (a, yy), fontsize=7, color=BLUE, ha='center', va='top',
                    arrowprops=dict(arrowstyle='-', lw=0.4, color=BLUE))
    ax.set_xlabel(r'larger angle $\theta_1$ (deg)', labelpad=2); ax.set_ylabel(r'smaller angle $\theta_2$ (deg)')
    ax.set_xlim(0, 125); ax.set_ylim(-16, 75); ax.set_aspect('equal')
    ax.axhline(0, color='k', lw=0.4)
    ax.spines['bottom'].set_visible(False); ax.set_yticks([0, 20, 40, 60])
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, fontsize=7, loc='upper left', markerscale=1.5)
    save(fig, 'fig_nd_angles')
    return len(A), int(rat.sum())


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_nd_containers(); print(fig_nd_angles())
