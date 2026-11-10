"""Tables, numbers and figures for Paper IV (docs/papers/IV-all-dimensions/).

Reads the evidence of scripts/optimality/lemmaF_all_d/evidence/ (global, free, far, rc, rcS, frames .jsonl;
closed_forms.json; nearid.json) and writes numbers.tex, tab_*.tex and fig_*.pdf, so every number in the paper has
one source.  Usage: python3 scripts/papers/figs_paper4.py <evidence commit> [evidence dir]
"""
import os, sys, json, math, itertools
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'docs', 'papers', 'IV-all-dimensions')
EV = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'scripts', 'optimality', 'lemmaF_all_d', 'evidence')
COMMIT = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'cm', 'font.size': 9, 'axes.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02})
# Paper I palette (series consistency); categorical order fixed
BLUE, ORANGE, GREEN, RED, GREY, PURPLE = '#2b5797', '#d9822b', '#3a8f5c', '#b22222', '#777777', '#7a4f9a'


def load(name):
    p = os.path.join(EV, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def best_by(rows, key):
    out = {}
    for r in rows:
        if 'maxF' not in r:
            continue
        k = key(r)
        if k not in out or r['maxF'] > out[k]['maxF']:
            out[k] = dict(r)
        out[k]['starts_total'] = out[k].get('starts_total', 0)
    tot = defaultdict(int)
    for r in rows:
        tot[key(r)] += r['starts']
    for k in out:
        out[k]['starts_total'] = tot[k]
    return out


def fmt(x, n=6):
    return f'{x:.{n}f}'


glob_ = best_by(load('global.jsonl'), lambda r: r['d'])
free = best_by(load('free.jsonl'), lambda r: r['d'])
far = best_by(load('far.jsonl'), lambda r: (r['d'], round(r['tau'], 9)))
rc = best_by(load('rc.jsonl'), lambda r: r['d'])
rcS = best_by(load('rcS.jsonl'), lambda r: (r['d'], round(r['tau'], 9)))
frames = load('frames.jsonl')
cf = json.load(open(os.path.join(EV, 'closed_forms.json')))
nearid = json.load(open(os.path.join(EV, 'nearid.json'))) if os.path.exists(os.path.join(EV, 'nearid.json')) else {}

macros = {k: '?' for k in ('maxdim', 'farHosonoFour', 'profilegap', 'farlowmax', 'rcmax', 'rcdmax', 'frameslast',
                             'framestarts', 'framesgap', 'framesmingap', 'framesaligned', 'framescount', 'nearidmin',
                             'evidencecommit')}
dims = sorted(glob_)
macros['maxdim'] = str(max(dims)) if dims else '?'

# ---------------------------------------------------------------- global / free table
lines = [r'\begin{tabular}{r r l r l}', r'\toprule',
         r'$d$ & starts & largest $F_j$, rows $\le2$ & starts & largest $F_j$, all of $O(d)$ \\', r'\midrule']
for d in sorted(set(glob_) | set(free)):
    g = glob_.get(d); f = free.get(d)
    gs = (str(g['starts_total']), fmt(g['maxF'], 10)) if g else ('--', '--')
    fs = (str(f['starts_total']), fmt(f['maxF'], 10)) if f else ('--', '--')
    lines.append(f'{d} & {gs[0]} & {gs[1]} & {fs[0]} & {fs[1]} \\\\')
lines += [r'\bottomrule', r'\end{tabular}']
open(os.path.join(OUT, 'tab_global.tex'), 'w').write('\n'.join(lines) + '\n')
assert all(r.get('count_F_gt_1', 0) == 0 for r in load('global.jsonl') + load('free.jsonl'))
assert all(r['argmax_maxcol'] > 1 - 1e-6 for r in list(glob_.values()) + list(free.values())), 'global maximiser not axis-aligned'

# ---------------------------------------------------------------- far region
def plane(t):
    c = math.sqrt(t)
    return 1 - (c + math.sqrt(1 - t) - 1) ** 2 if t >= 0.5 else 1 - (math.sqrt(2) - 1) ** 2


fdims = sorted({d for d, _ in far})
lines = [r'\begin{tabular}{r r l l l}', r'\toprule',
         r'$d$ & $\tau_d$ & $\Phi_d(\tau_d)$ & $\Phi_d(1/2)$ & smallest $\tau$ tested: $\Phi_d(\tau)$ \\', r'\midrule']
gaps = []; lowmax = 0
for d in fdims:
    taus = sorted(t for dd, t in far if dd == d)
    tH = round(1 - 1 / (d - 1), 9)
    vH = far.get((d, tH)); vh = far.get((d, 0.5))
    tmin = taus[0]; vmin = far[(d, tmin)]
    lines.append(f"{d} & {tH:.4f} & {fmt(vH['maxF']) if vH else '--'} & {fmt(vh['maxF']) if vh else '--'} & "
                 f"$\\tau={tmin:g}$: {fmt(vmin['maxF'])} \\\\")
    for t in taus:
        if t >= 0.5:
            gaps.append(far[(d, t)]['maxF'] - plane(t))
        else:
            lowmax = max(lowmax, far[(d, t)]['maxF'])
lines += [r'\bottomrule', r'\end{tabular}']
open(os.path.join(OUT, 'tab_far.tex'), 'w').write('\n'.join(lines) + '\n')
if (4, round(2 / 3, 9)) in far:
    macros['farHosonoFour'] = fmt(far[(4, round(2 / 3, 9))]['maxF'])
macros['profilegap'] = f'{max(abs(g) for g in gaps):.1e}'.replace('e-0', r'\cdot10^{-').replace('e-', r'\cdot10^{-') + '}' if gaps else '?'
macros['profilegapmax'] = f'{max(gaps):.2e}' if gaps else '?'
macros['farlowmax'] = fmt(lowmax, 4)

# ---------------------------------------------------------------- remaining case
sig = sorted({t for _, t in rcS})
lines = [r'\begin{tabular}{r r l l l' + ' l' * len(sig) + '}', r'\toprule',
         r'$d$ & starts & largest $F_j$ in $\mathrm{RC}(d)$ & $\norm x_1$ & $\min_i(w_i-x_i)$' +
         ''.join(f' & $\\norm x_1\\ge{t:g}$' for t in sig) + r' \\', r'\midrule']
for d in sorted(rc):
    r = rc[d]
    extra = ''.join(f" & {fmt(rcS[(d, t)]['maxF'], 4) if (d, t) in rcS else '--'}" for t in sig)
    lines.append(f"{d} & {r['starts_total']} & {fmt(r['maxF'])} & {r['argmax_S']:.5f} & {r['argmax_minrest']:.4f}{extra} \\\\")
lines += [r'\bottomrule', r'\end{tabular}']
open(os.path.join(OUT, 'tab_rc.tex'), 'w').write('\n'.join(lines) + '\n')
macros['rcmax'] = fmt(max(r['maxF'] for r in rc.values()), 4) if rc else '?'
macros['rcdmax'] = str(max(rc)) if rc else '?'

# ---------------------------------------------------------------- frames
byd = defaultdict(list)
for r in frames:
    byd[r['d']].append(r)
lines = [r'\begin{tabular}{r r r l l l r}', r'\toprule',
         r'$d$ & $v$ tested & starts & $\min(\text{found}-H)$ & $\max(\text{found}-H)$ & $\min(H-2(\norm v_1-1))$ & aligned \\',
         r'\midrule']
allgap = []; aligned = 0; count = 0
for d in sorted(byd):
    rs = byd[d]
    g = [r['gap'] for r in rs]; allgap += g
    room = min(r['helmert'] - r['lemmaF_bound'] for r in rs)
    al = sum(1 for r in rs if r['aligned_rows_at_min'] >= 1); aligned += al; count += len(rs)
    lines.append(f"{d} & {len(rs)} & {rs[0]['starts']} & {min(g):.1e} & {max(g):.1e} & {room:.4f} & {al}/{len(rs)} \\\\")
lines += [r'\bottomrule', r'\end{tabular}']
open(os.path.join(OUT, 'tab_frames.tex'), 'w').write('\n'.join(lines) + '\n')
macros['frameslast'] = str(max(byd)) if byd else '?'
macros['framestarts'] = '/'.join(sorted({str(r['starts']) for r in frames}, key=int, reverse=True)) if frames else '?'
macros['framesgap'] = f'{max(abs(x) for x in allgap):.0e}' if allgap else '?'
macros['framesmingap'] = f'{min(allgap):.1e}' if allgap else '?'
macros['framesaligned'] = str(aligned)
macros['framescount'] = str(count)

# ---------------------------------------------------------------- regular simplices
lines = [r'\begin{tabular}{r l l l}', r'\toprule', r'$n$ & $\sigma_n$ (\cref{conj:regular}) & Lemma~F bound & volume bound \\', r'\midrule']
for n in range(1, 13):
    e = cf['regular_simplex'][str(n)]
    lines.append(f"{n} & {e['conjecture_H']:.6f} & {e['lemmaF_bound']:.6f} & {e['volume_bound']:.6f} \\\\")
lines += [r'\bottomrule', r'\end{tabular}']
open(os.path.join(OUT, 'tab_regular.tex'), 'w').write('\n'.join(lines) + '\n')
macros['nearidmin'] = fmt(min(nearid.values()), 5) if nearid else '?'
macros['evidencecommit'] = COMMIT[:10]

def tex_number(s):
    return s
with open(os.path.join(OUT, 'numbers.tex'), 'w') as f:
    f.write('% generated by scripts/papers/figs_paper4.py\n')
    for k, v in sorted(macros.items()):
        if k.startswith('profilegap') and k != 'profilegap':
            continue
        f.write(f'\\newcommand{{\\{k}}}{{{v}}}\n')
print(json.dumps(macros, indent=1))
print('profile gaps (found - plane) for tau >= 1/2: min %.2e max %.2e' % (min(gaps), max(gaps)) if gaps else '')


# ---------------------------------------------------------------- figure: far-region profile
def fig_profile():
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    tt = np.linspace(0.5, 1, 200)
    ax.plot(tt, [plane(t) for t in tt], color=GREY, lw=1.2, ls='--', zorder=1)
    ax.text(0.985, plane(0.985) - 0.035, 'plane rotation', color=GREY, ha='right', fontsize=8)
    show = [d for d in (4, 6, 8, 12, 16) if any(dd == d for dd, _ in far)]
    cols = [BLUE, ORANGE, GREEN, PURPLE, RED]
    for d, col in zip(show, cols):
        ts = sorted(t for dd, t in far if dd == d)
        ax.plot(ts, [far[(d, t)]['maxF'] for t in ts], color=col, lw=2, marker='o', ms=4.5,
                mec='white', mew=1.0, label=f'$d={d}$', zorder=3)
    ax.axhline(1, color='black', lw=0.6, alpha=0.5)
    ax.set_xlabel(r'$\tau$ (bound on every squared entry of column $j$)')
    ax.set_ylabel(r'largest $F_j$ found')
    ax.set_xlim(0, 1); ax.set_ylim(0.3, 1.03)
    ax.grid(axis='y', color='#dddddd', lw=0.5)
    ax.legend(frameon=False, loc='lower right', fontsize=8)
    fig.savefig(os.path.join(OUT, 'fig_profile.pdf')); plt.close(fig)


# ---------------------------------------------------------------- figure: cubes in simplices
def fig_simplex():
    fig = plt.figure(figsize=(6.4, 3.0))
    # left: an acute triangle with vertices t_i e_i, drawn in its plane, with the Helmert square
    ax = fig.add_subplot(1, 2, 1)
    t = np.array([1.0, 1.25, 1.6])
    V3 = np.diag(t)
    o = V3.mean(0); n = 1 / t; n /= np.linalg.norm(n)
    e1 = V3[1] - V3[0]; e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
    P = lambda X: np.array([(X - o) @ e1, (X - o) @ e2])
    T = np.array([P(V) for V in V3])
    # largest square standing on the side opposite the farthest vertex (vertex 2 = largest t)
    A, B, C = T[0], T[1], T[2]
    u = (B - A) / np.linalg.norm(B - A); w = np.array([-u[1], u[0]])
    if (C - A) @ w < 0: w = -w
    h = (C - A) @ w; base = np.linalg.norm(B - A)
    s = base * h / (base + h)                 # square on a side of a triangle: side = base*h/(base+h)
    # place it: bottom edge on AB, top corners on AC and BC
    lam = s / h
    L = A + lam * (C - A); Rr = B + lam * (C - B)
    sq = np.array([L - s * w, L - s * w + s * u, L + s * u, L])
    tri = plt.Polygon(T, fill=False, ec='black', lw=1.0); ax.add_patch(tri)
    ax.add_patch(plt.Polygon(sq, fc=ORANGE, alpha=0.25, ec=ORANGE, lw=1.2))
    for k, lab in enumerate([r'$t_1e_1$', r'$t_2e_2$', r'$t_3e_3$']):
        dvec = T[k] - T.mean(0); dvec /= np.linalg.norm(dvec)
        ax.text(*(T[k] + 0.13 * dvec), lab, ha='center', va='center', fontsize=8)
    ax.text(*(sq.mean(0)), 'Helmert\nsquare', ha='center', va='center', fontsize=7, color='#8a4a10')
    lo, hi = T.min(0) - 0.25, T.max(0) + 0.25
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1])
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(r'$d=3$: a square in an acute triangle', fontsize=9)
    # right: regular tetrahedron with the face-on-face cube
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    e = 1 / 0.29590654
    Vt = np.array([[0, 0, 0], [e, 0, 0], [e / 2, e * math.sqrt(3) / 2, 0], [e / 2, e * math.sqrt(3) / 6, e * math.sqrt(2 / 3)]])
    faces = [[0, 1, 2], [0, 1, 3], [1, 2, 3], [0, 2, 3]]
    ax2.add_collection3d(Line3DCollection([[Vt[i], Vt[j]] for i, j in itertools.combinations(range(4), 2)], colors='black', linewidths=0.7))
    ax2.add_collection3d(Poly3DCollection([[Vt[k] for k in f] for f in faces], facecolor=GREY, alpha=0.05, edgecolor='none'))
    # cube: bottom face on the base, top face = largest square in the cross-section at height 1 (side on a side)
    hgt = 1.0
    tri_top = Vt[:3] + (Vt[3] - Vt[:3]) * (hgt / (e * math.sqrt(2 / 3)))
    A, B, C = tri_top[0][:2], tri_top[1][:2], tri_top[2][:2]
    u = (B - A) / np.linalg.norm(B - A); w = np.array([-u[1], u[0]])
    if (C - A) @ w < 0: w = -w
    hh = (C - A) @ w; base = np.linalg.norm(B - A); s2 = base * hh / (base + hh)
    lam = s2 / hh; L = A + lam * (C - A)
    q = [L - s2 * w, L - s2 * w + s2 * u, L + s2 * u, L]
    CV = np.array([[*q[k], z] for z in (0, 1) for k in range(4)])
    CF = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    ax2.add_collection3d(Poly3DCollection([[CV[k] for k in f] for f in CF], facecolor=ORANGE, alpha=0.22, edgecolor=ORANGE, linewidths=0.8))
    ax2.set_xlim(0, e); ax2.set_ylim(0, e * math.sqrt(3) / 2); ax2.set_zlim(0, e * math.sqrt(2 / 3))
    ax2.set_box_aspect((1, math.sqrt(3) / 2, math.sqrt(2 / 3)), zoom=1.25)
    ax2.set_axis_off(); ax2.view_init(elev=16, azim=-75)
    ax2.set_title(r'$d=4$: Croft\textquoteright s cube'.replace(r'\textquoteright ', "'"), fontsize=9)
    fig.savefig(os.path.join(OUT, 'fig_simplex.pdf')); plt.close(fig)
    return s, s2


def fig_dims():
    rc4 = best_by(load('rc4.jsonl'), lambda r: r['d'])
    series = []
    if far:
        ds = sorted({d for d, _ in far if (d, round(1 - 1 / (d - 1), 9)) in far})
        series.append((r"Hosono's far region $\tau_d=1-1/(d-1)$", ds, [far[(d, round(1 - 1 / (d - 1), 9))]['maxF'] for d in ds], GREY))
        ds = sorted({d for d, t in far if t == 0.5})
        series.append((r'far region $\tau=1/2$', ds, [far[(d, 0.5)]['maxF'] for d in ds], BLUE))
    if rc:
        ds = sorted(rc); series.append((r'remaining case $\mathrm{RC}(d)$', ds, [rc[d]['maxF'] for d in ds], ORANGE))
    if rc4:
        ds = sorted(rc4); series.append((r'$\mathrm{RC4}(d)$', ds, [rc4[d]['maxF'] for d in ds], GREEN))
    fig, ax = plt.subplots(figsize=(5.6, 3.1))
    for lab, ds, ys, col in series:
        ax.plot(ds, ys, color=col, lw=2, marker='o', ms=4.5, mec='white', mew=1.0, label=lab)
    ax.axhline(1, color='black', lw=0.6, alpha=0.5)
    ax.set_xlabel('dimension $d$'); ax.set_ylabel(r'largest $F_j$ found')
    ax.set_ylim(0.55, 1.02); ax.grid(axis='y', color='#dddddd', lw=0.5)
    ax.legend(frameon=False, loc='lower right', fontsize=8)
    fig.savefig(os.path.join(OUT, 'fig_dims.pdf')); plt.close(fig)


fig_profile()
fig_dims()
print('square side %.4f, cube top square side %.6f (should be 1)' % fig_simplex())
