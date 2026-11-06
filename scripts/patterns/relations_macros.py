#!/usr/bin/env python3
"""Macros for the relations, contacts and transfer sections of the patterns paper (relations_macros.tex)."""
import json, os, collections
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)
rel = json.load(open(P('docs', 'patterns', 'relations.json')))
con = json.load(open(P('docs', 'patterns', 'contacts3d.json')))
tr = json.load(open(P('docs', 'patterns', 'transfer.json')))
opt = json.load(open(P('docs', 'optimality.json')))['records']
m = {}
m['nCon'] = len(con)
m['nConRattler'] = sum(c['rattlers'] > 0 for c in con)
m['pctConRattler'] = round(100 * m['nConRattler'] / len(con))
m['nConIso'] = sum(c['excess'] >= 0 for c in con)
m['meanCoord'] = f"{np.mean([2 * c['pair_contacts'] / c['n'] for c in con]):.1f}"
m['meanWall'] = f"{np.mean([c['wall_contacts'] / c['n'] for c in con]):.1f}"
m['medExcess'] = int(np.median([c['excess'] for c in con]))
pr = rel['pairs']
def L(k): return f"{pr[k]['lift']:.2f}"
def Pc(k): return f"{100 * pr[k]['p_b_given_a']:.0f}"
m['liftWinPla'] = L('window->plateau'); m['pWinPla'] = Pc('window->plateau')
m['liftFroPla'] = L('frozen->plateau'); m['pFroPla'] = Pc('frozen->plateau')
m['liftIsoPla'] = L('isostatic->plateau'); m['pIsoPla'] = Pc('isostatic->plateau')
m['liftRatPla'] = L('rattler->plateau'); m['pRatPla'] = Pc('rattler->plateau')
m['liftRatWin'] = L('rattler->window'); m['nRatWin'] = pr['rattler->window']['n_ab']
m['liftRatIns'] = L('rattler->insertion')
m['liftWinOne'] = L('window->one_orient'); m['pWinOne'] = Pc('window->one_orient')
m['liftSymWin'] = L('symmetric->window')
m['liftWinRat'] = L('window->rational')
m['liftCompRat'] = L('composite->rational')
m['liftClosedPla'] = L('closed->plateau'); m['pClosedPla'] = Pc('closed->plateau')
m['liftInsWin'] = L('insertion->window')
m['liftOptClosed'] = L('optimal->closed')
m['liftSymRat'] = f"{pr['symmetric->rattler']['lift']:.2f}"
m['nTrMatch'] = len(tr['matches']); m['nTrBeat'] = len(tr['beats'])
h = tr['ratio_hist']; m['nTrOne'] = h[0]; m['nTrFive'] = h[0] + h[1]; m['nTrAll'] = sum(h)
m['nProven'] = sum(e['status'] == 'proven' for e in opt)
m['nNovel'] = sum(bool(e.get('novel')) for e in opt)
m['nPrism'] = sum(e['record_id'].startswith('pr') and 'incub' in e['record_id'] and e.get('novel') for e in opt)
with open(P('docs', 'patterns-paper', 'relations_macros.tex'), 'w') as f:
    for k, v in m.items(): f.write(f'\\newcommand{{\\{k}}}{{{v}}}\n')
print(m)
