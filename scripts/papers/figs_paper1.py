"""Figures for Paper I (cube centre lemmas): docs/papers/I-cube-centre/fig_*.pdf"""
import os, json, itertools
from fractions import Fraction as Fr
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.optimize import minimize_scalar
from scipy.stats import special_ortho_group

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'docs', 'papers', 'I-cube-centre')
plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'cm', 'font.size': 9, 'axes.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02})
BLUE, ORANGE, GREEN, RED, GREY = '#2b5797', '#d9822b', '#3a8f5c', '#b22222', '#777777'


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.pdf')); plt.close(fig)


# ---------------------------------------------------------------- unit cube geometry
CV = np.array(list(itertools.product([0, 1], repeat=3)), float)
EDGES = [(i, j) for i in range(8) for j in range(i + 1, 8) if np.abs(CV[i] - CV[j]).sum() == 1]
FACES = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]


def draw_box(ax, V, color, alpha=0.12, lw=0.7, ec=None):
    ax.add_collection3d(Poly3DCollection([[V[k] for k in f] for f in FACES], facecolor=color, alpha=alpha, edgecolor='none'))
    ax.add_collection3d(Line3DCollection([[V[i], V[j]] for i, j in EDGES], colors=ec or color, linewidths=lw))


def fig_grid_tilt():
    fig = plt.figure(figsize=(6.3, 2.9))
    ax = fig.add_subplot(1, 2, 1, projection='3d')
    for v in itertools.product([0, 1], repeat=3):
        draw_box(ax, CV + np.array(v), BLUE, alpha=0.10, lw=0.6)
    draw_box(ax, 2 * CV, GREY, alpha=0.0, lw=1.0)
    ax.set_title(r'$2^3$ unit cubes, side $2$', fontsize=9)
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    # a tilted unit cube, translated to the corner of its translation box
    a, b = np.radians(22), np.radians(14)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    R = Rx @ Rz
    W = CV @ R.T
    w = W.max(0) - W.min(0); s = w.max() + 0.12
    W = W - W.min(0)                           # lower corner of the translation box
    draw_box(ax2, s * CV, GREY, alpha=0.0, lw=1.0)
    draw_box(ax2, W, ORANGE, alpha=0.18, lw=0.8)
    ax2.scatter([s / 2], [s / 2], [s / 2], color=RED, s=14, depthshade=False, zorder=5)
    ax2.set_title(r'a tilted unit cube, side $s=%.2f<2$' % s, fontsize=9)
    for A, L in ((ax, 2), (ax2, s)):
        A.set_xlim(0, L); A.set_ylim(0, L); A.set_zlim(0, L); A.set_box_aspect((1, 1, 1))
        A.set_axis_off(); A.view_init(elev=18, azim=-58)
    save(fig, 'fig_grid_tilt')
    return R, s


def fig_square():
    th = np.radians(25); s = 1.72
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    U = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float) - 0.5
    P = U @ R.T
    w = P.max(0) - P.min(0)
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    ax.add_patch(plt.Rectangle((0, 0), s, s, fill=False, ec=GREY, lw=1.0))
    lo = w / 2; hi = s - w / 2
    ax.add_patch(plt.Rectangle(lo, *(hi - lo), fc=GREEN, alpha=0.25, ec=GREEN, lw=0.6))
    for cpos, ls in ((lo, '-'), (hi, '--')):
        Q = P + cpos
        ax.add_patch(plt.Polygon(Q, closed=True, fill=False, ec=ORANGE, lw=0.9, ls=ls))
    ax.plot([s / 2], [s / 2], 'o', color=RED, ms=3.5)
    ax.annotate('container centre', (s / 2, s / 2), (s + 0.12, s / 2 + 0.55), fontsize=7.5, color=RED,
                arrowprops=dict(arrowstyle='-', color=RED, lw=0.5), annotation_clip=False)
    ax.annotate('translations of\nthe square\'s centre', (hi[0] - 0.02, lo[1] + 0.03), (s + 0.12, 0.25), fontsize=7.5,
                color=GREEN, arrowprops=dict(arrowstyle='-', color=GREEN, lw=0.5), annotation_clip=False)
    ax.annotate('', (0, -0.07), (w[0], -0.07), arrowprops=dict(arrowstyle='<->', lw=0.6))
    ax.text(w[0] / 2, -0.17, r'$w_1=|\cos\theta|+|\sin\theta|$', ha='center', fontsize=8)
    ax.set_xlim(-0.05, s + 0.05); ax.set_ylim(-0.25, s + 0.05); ax.set_aspect('equal'); ax.set_axis_off()
    save(fig, 'fig_square')


# ---------------------------------------------------------------- Lemma F samples
def F1(R):
    u = np.abs(R[:, 0]); return (u * (2 - np.abs(R).sum(1))).sum()


def sample_F(d, N, rng):
    out = []
    G = special_ortho_group(d, seed=rng)
    for k in range(N):
        mode = k % 3
        if mode == 0:
            R = G.rvs()
        else:
            # near a signed permutation, or a 2x2 rotation block: where F is largest
            P = np.eye(d)[rng.permutation(d)] * rng.choice([-1, 1], d)
            if mode == 1:
                th = rng.uniform(0, np.pi / 2); i, j = rng.choice(d, 2, replace=False)
                B = np.eye(d); B[i, i] = B[j, j] = np.cos(th); B[i, j] = -np.sin(th); B[j, i] = np.sin(th)
                P = B @ P
            A = rng.normal(size=(d, d)) * rng.choice([0.02, 0.08, 0.25]); A = A - A.T
            from scipy.linalg import expm
            R = expm(A) @ P
        c2 = (R[:, 0] ** 2).max()
        out.append((c2, F1(R)))
    return np.array(out)


def fig_lemmaF():
    rng = np.random.default_rng(3)
    fig, axs = plt.subplots(1, 3, figsize=(6.4, 2.3), sharey=True)
    regions = {3: [], 4: [(2 / 3, 1, 'near', BLUE), (1 / 4, 2 / 3, 'far', GREEN)],
               5: [(3 / 4, 1, 'near', BLUE), (9 / 20, 3 / 4, 'band', ORANGE), (1 / 5, 9 / 20, 'far', GREEN)]}
    for ax, d in zip(axs, (3, 4, 5)):
        S = sample_F(d, 6000, rng)
        for lo, hi, lab, col in regions[d]:
            ax.axvspan(lo, hi, color=col, alpha=0.10, lw=0)
            ax.text((lo + hi) / 2, -0.28, lab, ha='center', fontsize=7, color=col)
        ax.scatter(S[:, 0], S[:, 1], s=1.2, color='#333333', alpha=0.35, lw=0, rasterized=True)
        c = np.linspace(1 / 2, 1, 200); cc = np.sqrt(c)
        ax.plot(c, 1 - (cc + np.sqrt(1 - c) - 1) ** 2, color=RED, lw=0.9)
        ax.axhline(1, color=GREY, lw=0.6, ls='--')
        ax.set_xlim(1 / d, 1); ax.set_ylim(-0.35, 1.05)
        ax.set_title(f'$d={d}$', fontsize=9); ax.set_xlabel(r'largest $R_{ij}^2$ in column $j$')
    axs[0].set_ylabel(r'$F_j(R)$')
    axs[0].text(0.36, 0.05, r'red: $2\times2$ rotation block,' '\n' r'$F=1-(|c|+\sqrt{1-c^2}-1)^2$', fontsize=7, color=RED)
    save(fig, 'fig_lemmaF')


# ---------------------------------------------------------------- 4D far region
def fig_phi4():
    r = 140 / 99
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.3))
    t = np.linspace(0, np.sqrt(2 / 3), 400)
    axs[0].plot(t ** 2, r * (t - t ** 3) - 2 * t, color='k', lw=1.0)
    axs[0].set_xlabel(r'$t^2$'); axs[0].set_title(r'$\varphi(t)=\frac{140}{99}(t-t^3)-2t$', fontsize=8.5)
    ax = axs[1]
    for lo, hi, a, b, col, lab in ((0, 2 / 5, -0.06592, -1.65782, BLUE, r'small: $t^2\leq 2/5$'),
                                   (2 / 5, 3 / 5, 0.03645, -1.91374, ORANGE, r'middle: $2/5\leq t^2\leq 3/5$'),
                                   (2 / 5, 2 / 3, -0.14366, -1.65782, GREEN, r'big: $t^2\geq 2/5$')):
        tt = np.sqrt(np.linspace(lo, hi, 300)); ph = r * (tt - tt ** 3) - 2 * tt
        ax.plot(tt ** 2, ph - (a + b * tt ** 2), color=col, lw=1.0, label=lab)
    ax.axhline(0, color=GREY, lw=0.5)
    ax.set_xlabel(r'$t^2$'); ax.set_title(r'$\varphi(t)-(\alpha+\beta t^2)\geq 0$ for the three lines', fontsize=8.5)
    ax.legend(fontsize=6.5, frameon=False)
    save(fig, 'fig_phi4')


# ---------------------------------------------------------------- 5D sphere bounds
CERT = json.load(open(os.path.join(ROOT, 'scripts', 'optimality', 'lemma_f5', 'certificates.json')))


def Psi(lam, n=4, cap=None):
    best = -9
    for k in range(1, n + 1):
        for j in range(0, n + 1 - k):
            def f(s):
                a = np.sqrt(s / k); b = np.sqrt((1 - s) / j) if j else 0
                if cap and (a * a > cap + 1e-12 or b * b > cap + 1e-12): return 9
                return -(k * a ** 3 + j * b ** 3 + lam * (k * a + j * b))
            if j == 0:
                best = max(best, -f(1.0)); continue
            for lo, hi in ((0, 0.5), (0.5, 1)):
                r = minimize_scalar(f, bounds=(lo, hi), method='bounded', options={'xatol': 1e-12})
                best = max(best, -r.fun)
    return best


def fig_sphere():
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.4))
    c = CERT['sphA']; lam = float(Fr(c['lam']))
    cols = [BLUE, ORANGE, GREEN, RED, GREY]
    for ax, part, title in ((axs[0], 'small', r'other coordinates $s_i$ ($s_i^2\leq 1/2$)'), (axs[1], 'big', r'largest coordinate $s_0$ ($s_0^2\geq 1/4$)')):
        for k, (a, b, L) in enumerate(c[part]):
            a, b = float(Fr(a)), float(Fr(b)); al, be = float(Fr(L['al'])), float(Fr(L['be']))
            ss = np.linspace(a, b, 200)
            ax.plot(ss ** 2, 1e3 * (al + be * ss ** 2 - ss ** 3 - lam * ss), color=cols[k % 5], lw=1.0)
            ax.axvline(b * b, color=GREY, lw=0.4, ls=':')
            if L['kind'] == 'tan':
                t0 = float(Fr(L['t0'])); ax.plot([t0 ** 2], [0], 'o', color=cols[k % 5], ms=2.5)
        ax.axhline(0, color=GREY, lw=0.5)
        ax.set_title(title, fontsize=8.5); ax.set_xlabel(r'$s^2$')
    axs[0].set_ylabel(r'$10^3\,(\alpha+\beta s^2-s^3-\lambda s)$')
    save(fig, 'fig_sphere')


def fig_margin():
    r = 140 / 99; cp, sp = 14 / 25, 207 / 250
    nodes = [(float(Fr(CERT[k]['lam'])), float(Fr(CERT[k]['U']))) for k in ('sphA', 'sphB', 'sphC')]
    lam_grid = np.linspace(0.62, 0.84, 60)
    psi = np.array([Psi(l) for l in lam_grid])
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.4))
    ax = axs[0]
    ax.plot(lam_grid, psi, color='k', lw=1.0, label=r'$\Psi(\lambda)$')
    ax.plot([n[0] for n in nodes], [n[1] for n in nodes], 'o-', color=ORANGE, ms=3, lw=0.9, label=r'certified $U$, interpolated')
    cs = np.sqrt(np.array([9 / 20, 3 / 4]))
    lam_rng = (2 - r) / (r * (1 - cs * cp))
    ax.axvspan(*lam_rng, color=GREY, alpha=0.12, lw=0)
    ax.set_xlabel(r'$\lambda$'); ax.legend(fontsize=7, frameon=False)
    ax.set_title(r'sphere maximum $\Psi(\lambda)$ and the three nodes', fontsize=8.5)
    ax = axs[1]
    c2 = np.linspace(9 / 20, 3 / 4, 200); c = np.sqrt(c2); rho = np.sqrt(1 - c2)
    lam = (2 - r) / (r * (1 - c * cp))
    U = np.interp(lam, [n[0] for n in nodes], [n[1] for n in nodes])
    exact = np.array([Psi(l) for l in lam])
    for vals, col, lab in ((exact, 'k', r'with $\Psi(\lambda)$'), (U, ORANGE, r'with certified $U(\lambda)$')):
        m = r * sp * c * rho + 2 - 2 * c - r * (1 - c * cp) * rho * vals
        ax.plot(c2, m, color=col, lw=1.0, label=lab)
    ax.axhline(0, color=GREY, lw=0.6)
    ax.set_xlabel(r'$c^2$'); ax.set_title('slack of the band inequality', fontsize=8.5); ax.legend(fontsize=7, frameon=False)
    save(fig, 'fig_margin')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_grid_tilt(); fig_square(); fig_lemmaF(); fig_phi4(); fig_sphere(); fig_margin()
    print('figures written to', OUT)
