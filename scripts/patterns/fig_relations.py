#!/usr/bin/env python3
"""Figure: relations between the pattern classes (docs/patterns-paper/fig_relations.pdf).

(a) Formal implications proved in Lean, with the theorem on each arrow.
(b) Empirical associations over the 3D records: log2 of the lift P(B | A) / P(B), a symmetric measure
    (diverging scale, white = independent); cells with fewer than 20 joint records are left blank.
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = json.load(open(os.path.join(ROOT, 'docs', 'patterns', 'relations.json')))
INK, MUTED = '#1f2328', '#57606a'
plt.rcParams.update({'font.size': 8, 'font.family': 'DejaVu Sans'})
fig = plt.figure(figsize=(11.5, 5.6))
axA = fig.add_axes([0.0, 0.02, 0.47, 0.93]); axB = fig.add_axes([0.56, 0.17, 0.36, 0.74])
axC = fig.add_axes([0.935, 0.17, 0.012, 0.74])

# (a) formal implications
axA.axis('off'); axA.set_xlim(-0.2, 10.6); axA.set_ylim(0.6, 9.6)
box = dict(boxstyle='round,pad=0.35', fc='white', ec=INK, lw=1.1)
nodes = {
    'del': (1.3, 8.6, 'P1 deletion'), 'win': (4.2, 8.6, 'P5 Voronoi /\nlattice window'),
    'comp': (6.9, 8.6, 'P4 composition'), 'lem': (9.4, 8.6, 'centre, width,\nbox, volume\nlemmas'),
    'sep': (1.3, 5.4, 'separator\ncertificate'), 'pla': (4.2, 5.4, 'P1 plateau'),
    'tr': (6.9, 5.4, 'P11 transfer\nby inclusion'), 'ext': (9.4, 5.4, 'P9 extremal\nlower bound'),
    'arr': (1.3, 2.0, 'P2 arrows\n(F step sound)'), 'opt': (6.9, 2.0, 'P9 optimal\nplateau')}
for k, (x, y, t) in nodes.items():
    axA.text(x, y, t, ha='center', va='center', bbox=box, fontsize=8, color=INK)
def arrow(a, b, label, lx, ly, rad=0.0, ha='left'):
    (x1, y1, _), (x2, y2, _) = nodes[a], nodes[b]
    axA.annotate('', xy=(x2, y2), xytext=(x1, y1),
                 arrowprops=dict(arrowstyle='-|>', lw=1.4, color=INK, shrinkA=24, shrinkB=24,
                                 connectionstyle=f'arc3,rad={rad}'))
    if label:
        axA.text(lx, ly, label, ha=ha, va='center', fontsize=6.6, color=MUTED, family='DejaVu Sans Mono')
arrow('win', 'pla', 'lattice_windows', 4.32, 7.0)
arrow('del', 'pla', 'restrict', 2.55, 7.35)
arrow('comp', 'tr', 'transfer_piece,\ntransfer_container', 7.02, 7.0)
arrow('lem', 'ext', 'centre_of_box,\nwidth_le, ...', 9.52, 7.0)
arrow('sep', 'arr', 'of_separators', 1.42, 3.7)
arrow('del', 'arr', 'restrict', 0.05, 5.3, rad=0.35, ha='center')
arrow('pla', 'opt', '', 0, 0)
arrow('ext', 'opt', 'optimal_plateau_of_common_point,\noptimal_plateau_of_one_piece', 6.9, 1.0, ha='center')
axA.set_title('(a) formal implications (Lean)', loc='left', fontsize=9, color=INK)

# (b) lift matrix
order = ['plateau', 'frozen', 'deletion', 'insertion', 'rattler', 'isostatic', 'window', 'one_orient', 'layered',
         'symmetric', 'composite', 'closed', 'rational', 'optimal']
name = {'plateau': 'plateau', 'frozen': 'frozen subset', 'deletion': 'built by deletion', 'insertion': 'built by insertion',
        'rattler': 'has a rattler', 'isostatic': 'over-constrained', 'window': 'lattice window', 'one_orient': 'one orientation',
        'layered': '2-3 layers', 'symmetric': 'symmetric', 'composite': 'composite', 'closed': 'closed form',
        'rational': 'rational scale', 'optimal': 'proven optimal'}
n = len(order); M = np.full((n, n), np.nan)
for i, a in enumerate(order):
    for j, b in enumerate(order):
        v = R['pairs'].get(f'{a}->{b}')
        if {a, b} == {'deletion', 'insertion'}: continue      # exclusive by definition (last lineage move)
        if v and v['n_ab'] >= 20: M[i, j] = np.log2(max(v['lift'], 1 / 16))
        elif v and v['n_ab'] == 0 and v['n_a'] * v['p_b'] >= 20: M[i, j] = -4
cmap = matplotlib.colormaps['RdBu'].copy(); cmap.set_bad('#f3f4f6')
im = axB.imshow(np.ma.masked_invalid(M), cmap=cmap, vmin=-4, vmax=4)
axB.set_xticks(range(n)); axB.set_xticklabels([name[k] for k in order], rotation=55, ha='right', fontsize=7)
axB.set_yticks(range(n)); axB.set_yticklabels([name[k] for k in order], fontsize=7)
for i in range(n):
    for j in range(n):
        if not np.isnan(M[i, j]) and abs(M[i, j]) >= 1.5:
            v = R['pairs'][f'{order[i]}->{order[j]}']['lift']
            axB.text(j, i, f'{v:.1f}' if v >= 1 else f'{v:.2f}', ha='center', va='center', fontsize=5.6,
                     color='white' if abs(M[i, j]) > 2.6 else INK)
axB.set_title('(b) association: lift = P(B | A) / P(B)', loc='left', fontsize=9, color=INK)
cb = fig.colorbar(im, cax=axC, ticks=[-4, -2, 0, 2, 4]); cb.ax.set_yticklabels(['1/16', '1/4', '1', '4', '16'], fontsize=7)
cb.outline.set_visible(False)
out = os.path.join(ROOT, 'docs', 'patterns-paper', 'fig_relations')
fig.savefig(out + '.pdf', bbox_inches='tight'); fig.savefig(out + '.png', dpi=200, bbox_inches='tight')
print('wrote', out)
