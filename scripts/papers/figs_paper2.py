"""Figures for Paper II (width, facet and ball bounds): docs/papers/II-width-ball/fig_*.pdf

Every configuration is the explicit construction of the corresponding Lean file.
"""
import os, itertools
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial import ConvexHull

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'docs', 'papers', 'II-width-ball')
plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'cm', 'font.size': 9, 'axes.linewidth': 0.6,
                     'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02})
BLUE, ORANGE, GREEN, RED, GREY, PURPLE = '#2b5797', '#d9822b', '#3a8f5c', '#b22222', '#777777', '#7b4f9d'
PHI = (1 + 5 ** 0.5) / 2
s2, s3 = 2 ** 0.5, 3 ** 0.5


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.pdf')); plt.close(fig)


def hull_faces(V):
    """Faces of a convex polytope as vertex cycles (coplanar triangles merged)."""
    H = ConvexHull(V)
    groups = {}
    for simplex, eq in zip(H.simplices, H.equations):
        key = tuple(np.round(eq, 6))
        groups.setdefault(key, set()).update(simplex)
    faces = []
    for key, idx in groups.items():
        n = np.array(key[:3]); P = V[list(idx)]; c = P.mean(0)
        u = P[0] - c; u /= np.linalg.norm(u); w = np.cross(n, u)
        ang = np.arctan2((P - c) @ w, (P - c) @ u)
        faces.append(P[np.argsort(ang)])
    return faces


def draw_poly(ax, V, color, alpha=0.25, lw=0.6, edges_only=False, ec=None):
    F = hull_faces(np.asarray(V, float))
    if not edges_only:
        ax.add_collection3d(Poly3DCollection(F, facecolor=color, alpha=alpha, edgecolor='none'))
    segs = []
    for f in F:
        for i in range(len(f)): segs.append([f[i], f[(i + 1) % len(f)]])
    ax.add_collection3d(Line3DCollection(segs, colors=ec or color, linewidths=lw))


def setup3d(ax, L, elev=20, azim=-60):
    ax.set_xlim(-L, L); ax.set_ylim(-L, L); ax.set_zlim(-L, L); ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off(); ax.view_init(elev=elev, azim=azim)


SIG = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
TET = (s2 / 4) * SIG                                    # regular tetrahedron of edge 1, centred


def cube_vertices(s):
    return np.array(list(itertools.product([-s / 2, s / 2], repeat=3)))


def octa_vertices(R):
    return np.array([R * e for e in np.vstack([np.eye(3), -np.eye(3)])])


def dod_vertices():
    # standard edge-1 dodecahedron: (±φ/2)(±1,±1,±1), cyclic perms of (0, ±1/2, ±φ²/2)
    V = [np.array(v) * PHI / 2 for v in itertools.product([-1, 1], repeat=3)]
    for a, b in itertools.product([-1, 1], repeat=2):
        base = np.array([0, a / 2, b * PHI ** 2 / 2])
        for p in range(3): V.append(np.roll(base, p))
    return np.array(V)


def ico_vertices():
    V = []
    for a, b in itertools.product([-1, 1], repeat=2):
        base = np.array([0, a / 2, b * PHI / 2])
        for p in range(3): V.append(np.roll(base, p))
    return np.array(V)


def householder_e3():
    u = np.array([1, 1, 1]) / s3 - np.array([0, 0, 1.0]); u /= np.linalg.norm(u)
    return np.eye(3) - 2 * np.outer(u, u)


def fig_tets():
    fig = plt.figure(figsize=(6.4, 6.0))
    # cube
    s = 2 * s2 / 3
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    A = TET + s2 / 12
    draw_poly(ax, cube_vertices(s), GREY, edges_only=True, lw=0.8)
    draw_poly(ax, A, BLUE); draw_poly(ax, -A, ORANGE)
    setup3d(ax, s / 2 * 1.05); ax.set_title(r'cube, side $2\sqrt{2}/3\approx0.943$', fontsize=8.5)
    # octahedron: Householder H(1,1,1)/sqrt3 = e3, lift by sqrt6/12 e3
    so = 2 / s3; H = householder_e3()
    B = TET @ H.T + np.array([0, 0, 6 ** 0.5 / 12])
    ax = fig.add_subplot(2, 2, 2, projection='3d')
    draw_poly(ax, octa_vertices(so * s2 / 2), GREY, edges_only=True, lw=0.8)
    draw_poly(ax, B, BLUE); draw_poly(ax, -B, ORANGE)
    setup3d(ax, so * s2 / 2 * 0.85, elev=12); ax.set_title(r'octahedron, edge $2/\sqrt{3}\approx1.155$', fontsize=8.5)
    # dodecahedron: the cube packing inside the inscribed cube
    sd = 2 * s2 / (3 * PHI)
    ax = fig.add_subplot(2, 2, 3, projection='3d')
    draw_poly(ax, sd * dod_vertices(), GREY, edges_only=True, lw=0.7)
    draw_poly(ax, cube_vertices(2 * s2 / 3), GREEN, edges_only=True, lw=0.5)
    draw_poly(ax, A, BLUE); draw_poly(ax, -A, ORANGE)
    setup3d(ax, sd * np.linalg.norm(dod_vertices()[0]) * 0.8); ax.set_title(r'dodecahedron, edge $\sqrt{2}(\sqrt{5}-1)/3\approx0.583$', fontsize=8.5)
    # icosahedron
    si = 2 * ((5 - 5 ** 0.5) / 15) ** 0.5
    io = 1 / (3 * (PHI + 2)) ** 0.5
    C = np.array([[0, s2 * io, s2 * PHI * io], [0, PHI * io, -io], [0.5, -PHI * io / 2, io / 2], [-0.5, -PHI * io / 2, io / 2]])
    ax = fig.add_subplot(2, 2, 4, projection='3d')
    draw_poly(ax, si * ico_vertices(), GREY, edges_only=True, lw=0.7)
    draw_poly(ax, C, BLUE); draw_poly(ax, -C, ORANGE)
    setup3d(ax, si * np.linalg.norm(ico_vertices()[0]) * 0.8, elev=10, azim=-75)
    ax.set_title(r'icosahedron, edge $2\sqrt{(5-\sqrt{5})/15}\approx0.859$', fontsize=8.5)
    for P, nm in ((A, 'cube'), (B, 'oct'), (C, 'ico')):
        d = np.linalg.norm(P[:, None] - P[None], axis=2); assert abs(d[d > 0].min() - 1) < 1e-9 and abs(d.max() - 1) < 1e-9, nm
    save(fig, 'fig_tets')


def fig_facet_width():
    """2D analogue: a triangle that misses the centre of a square container."""
    fig, ax = plt.subplots(figsize=(3.3, 3.1))
    s = 1.9; R = s / 2 * s2
    ax.add_patch(plt.Rectangle((-s / 2, -s / 2), s, s, fill=False, ec=GREY, lw=1.0))
    ax.add_patch(plt.Circle((0, 0), R, fill=False, ec=GREY, lw=0.6, ls=':'))
    th = np.radians(40); h = 3 ** 0.5 / 2
    n = np.array([np.cos(th), np.sin(th)]); t = np.array([-n[1], n[0]])
    base_c = 0.18 * n - 0.2 * t
    P = np.array([base_c - 0.5 * t, base_c + 0.5 * t, base_c + h * n])
    assert np.abs(P).max() <= s / 2
    ax.add_patch(plt.Polygon(P, closed=True, fc=BLUE, alpha=0.25, ec=BLUE, lw=0.9))
    L = np.array([base_c - 1.0 * t, base_c + 1.0 * t]); ax.plot(L[:, 0], L[:, 1], color=BLUE, lw=0.6, ls='--')
    ax.plot(0, 0, 'o', color=RED, ms=3.5)
    ax.annotate('', P[2], base_c, arrowprops=dict(arrowstyle='<->', color=ORANGE, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text(*(base_c + 0.5 * h * n - 0.06 * t), '$w$', color=ORANGE, fontsize=9, ha='left', va='top')
    ax.plot([0, P[2][0]], [0, P[2][1]], color=RED, lw=0.6, ls=':')
    dn = np.array([-P[2][1], P[2][0]]) / np.linalg.norm(P[2]); ax.text(*(0.5 * P[2] + 0.05 * dn), r'$\geq w$', color=RED, fontsize=8, ha='right', va='bottom')
    e = R * np.array([np.cos(-2.3), np.sin(-2.3)])
    ax.annotate('', e, (0, 0), arrowprops=dict(arrowstyle='->', color=GREY, lw=0.6, shrinkA=0, shrinkB=0))
    ax.text(*(0.5 * e + np.array([0.05, -0.12])), '$sR_C$', color=GREY, fontsize=8)
    ax.text(0.62, -0.62, 'facet line', color=BLUE, fontsize=7.5)
    ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4); ax.set_aspect('equal'); ax.set_axis_off()
    save(fig, 'fig_facet_width')


def fig_two_ball():
    fig, axs = plt.subplots(1, 2, figsize=(5.6, 2.6))
    k = 1.0
    # square: two balls of radius k, s = 2k(1 + 1/sqrt2)
    s = 2 * k * (1 + 1 / s2)
    ax = axs[0]
    ax.add_patch(plt.Rectangle((-s / 2, -s / 2), s, s, fill=False, ec=GREY, lw=1.0))
    c = (s / 2 - k) * np.array([1, 1])
    for sg, col in ((1, BLUE), (-1, ORANGE)):
        ax.add_patch(plt.Circle(sg * c, k, fc=col, alpha=0.25, ec=col))
    ax.plot(0, 0, 'o', color=RED, ms=3)
    ax.set_title(r'hypercube: $s\geq 2k(1+1/\sqrt{d})$', fontsize=8.5)
    ax = axs[1]
    rho = k * (1 + s2)                                  # cross-polytope {|x|_1 <= rho}, d = 2
    D = np.array([[rho, 0], [0, rho], [-rho, 0], [0, -rho]])
    ax.add_patch(plt.Polygon(D, closed=True, fill=False, ec=GREY, lw=1.0))
    c = np.array([rho - k * s2, 0])
    for sg, col in ((1, BLUE), (-1, ORANGE)):
        ax.add_patch(plt.Circle(sg * c, k, fc=col, alpha=0.25, ec=col))
    ax.plot(0, 0, 'o', color=RED, ms=3)
    ax.set_title(r'cross-polytope: $s\geq k(1+\sqrt{d})/\rho$', fontsize=8.5)
    for ax in axs:
        ax.set_aspect('equal'); ax.set_axis_off(); ax.set_xlim(-2.6, 2.6); ax.set_ylim(-2.6, 2.6)
    save(fig, 'fig_two_ball')


def fig_octa():
    s = s2; rho = s2 / 2
    H = np.eye(3) - 2 / 3 * np.ones((3, 3))
    O = octa_vertices(rho) @ H.T + rho / 3
    fig = plt.figure(figsize=(3.2, 3.0))
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    draw_poly(ax, cube_vertices(s), GREY, edges_only=True, lw=0.8)
    draw_poly(ax, O, BLUE); draw_poly(ax, -O, ORANGE)
    # hexagonal separating plane x + y + z = 0
    hexv = np.array([[s / 2, -s / 2, 0], [s / 2, 0, -s / 2], [0, s / 2, -s / 2], [-s / 2, s / 2, 0], [-s / 2, 0, s / 2], [0, -s / 2, s / 2]])
    ax.add_collection3d(Poly3DCollection([hexv], facecolor=GREEN, alpha=0.12, edgecolor=GREEN, lw=0.5))
    setup3d(ax, s / 2 * 1.02, elev=22, azim=-50)
    assert np.abs(O).max() <= s / 2 + 1e-12
    save(fig, 'fig_octa')


# ---------------------------------------------------------------- prisms
def tri_prism(L):
    T = np.array([[0, 0], [0, 1], [s3 / 2, 0.5]])
    return np.array([[x, y, z] for x, y in T for z in (-L / 2, L / 2)])


def fig_six_prisms():
    P = tri_prism(2)
    maps = [lambda y: (-y[0], y[2], y[1] - 1), lambda y: (y[0] - s3 / 2, y[2], y[1] - 0.5), lambda y: (-y[0], y[2], y[1]),
            lambda y: (y[0], y[1] - 1, y[2]), lambda y: (s3 / 2 - y[0], y[1] - 0.5, y[2]), lambda y: (y[0], y[1], y[2])]
    cols = [BLUE, '#6f9bd6', '#1d3f73', ORANGE, '#f0b878', '#a35c14']
    W = [np.array([f(y) for y in P]) for f in maps]
    for w in W: assert np.abs(w).max() <= 1 + 1e-12
    fig = plt.figure(figsize=(6.4, 2.9))
    ax = fig.add_subplot(1, 3, (1, 2), projection='3d')
    gap = 0.45                                          # exploded view: the two halves pulled apart along x
    C = cube_vertices(2)
    draw_poly(ax, C[C[:, 0] < 0] .tolist() + (C[C[:, 0] < 0] * [0, 1, 1]).tolist() - np.array([gap, 0, 0]), GREY, edges_only=True, lw=0.6)
    draw_poly(ax, C[C[:, 0] > 0] .tolist() + (C[C[:, 0] > 0] * [0, 1, 1]).tolist() + np.array([gap, 0, 0]), GREY, edges_only=True, lw=0.6)
    for k, (w, c) in enumerate(zip(W, cols)):
        draw_poly(ax, w + np.array([-gap if k < 3 else gap, 0, 0]), c, alpha=0.35, lw=0.5)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_zlim(-1.5, 1.5); ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off(); ax.view_init(elev=22, azim=-62)
    ax.text2D(0.02, 0.95, '(a)', transform=ax.transAxes, fontsize=9)
    ax = fig.add_subplot(1, 3, 3)
    tri = [np.array([[0, -1], [0, 0], [-s3 / 2, -0.5]]), np.array([[-s3 / 2, -0.5], [-s3 / 2, 0.5], [0, 0]]),
           np.array([[0, 0], [0, 1], [-s3 / 2, 0.5]])]
    ax.add_patch(plt.Rectangle((-1, -1), 1, 2, fill=False, ec=GREY, lw=0.9))
    for t, c in zip(tri, cols[:3]):
        ax.add_patch(plt.Polygon(t, closed=True, fc=c, alpha=0.35, ec=c, lw=0.9))
    ax.text(-0.5, -1.17, '1', ha='center', fontsize=8); ax.text(0.07, 0, '2', va='center', fontsize=8)
    ax.text(-1.05, 1.08, '(b)', fontsize=9)
    ax.set_aspect('equal'); ax.set_axis_off(); ax.set_xlim(-1.15, 0.25); ax.set_ylim(-1.25, 1.25)
    save(fig, 'fig_six_prisms')


def fig_pinwheel():
    a = (s3 - 1) / 2
    T = [np.array([[0, a], [0, a + 1], [s3 / 2, s3 / 2]]), np.array([[a, 0], [a + 1, 0], [s3 / 2, s3 / 2]]),
         np.array([[1.5, 0.5], [1.5, 1.5], [1.5 - s3 / 2, 1]])]
    for t in T:
        d = np.linalg.norm(t[:, None] - t[None], axis=2); assert abs(d[d > 0].min() - 1) < 1e-12 and abs(d.max() - 1) < 1e-12
        assert t.min() >= -1e-12 and t.max() <= 1.5 + 1e-12
    fig, ax = plt.subplots(figsize=(2.8, 2.8))
    ax.add_patch(plt.Rectangle((0, 0), 1.5, 1.5, fill=False, ec=GREY, lw=1.0))
    for t, c in zip(T, (BLUE, ORANGE, GREEN)):
        ax.add_patch(plt.Polygon(t, closed=True, fc=c, alpha=0.3, ec=c, lw=0.9))
    ax.text(0.75, -0.12, r'$3/2$', ha='center', fontsize=8)
    ax.set_aspect('equal'); ax.set_axis_off(); ax.set_xlim(-0.05, 1.55); ax.set_ylim(-0.2, 1.55)
    save(fig, 'fig_pinwheel')


def ngon_prism(m, L, z0=0.0):
    R = 0.5 / np.sin(np.pi / m)
    pts = [(R * np.cos(2 * np.pi * k / m + np.pi / m), R * np.sin(2 * np.pi * k / m + np.pi / m)) for k in range(m)]
    return np.array([[x, y, z] for x, y in pts for z in (z0 - L / 2, z0 + L / 2)])


def fig_stacks():
    fig = plt.figure(figsize=(6.4, 1.9))
    cases = [(12, 1, 2 + s3, 3), (12, 1.5, 2 + s3, 2), (12, 2, 4, 2), (8, 1, 1 + s2, 2), (6, 1, 2, 2)]
    for k, (m, L, s, n) in enumerate(cases):
        ax = fig.add_subplot(1, 5, k + 1, projection='3d')
        draw_poly(ax, cube_vertices(s), GREY, edges_only=True, lw=0.6)
        z = -s / 2 + L / 2
        for i in range(n):
            P = ngon_prism(m, L, z + i * L)
            assert np.abs(P).max() <= s / 2 + 1e-12
            draw_poly(ax, P, [BLUE, ORANGE, GREEN][i], alpha=0.25, lw=0.35)
        setup3d(ax, s / 2 * 1.0, elev=16, azim=-55)
        ax.text2D(0.5, 0.0, '(%s)' % 'abcde'[k], transform=ax.transAxes, ha='center', fontsize=8)
    fig.subplots_adjust(wspace=0.0)
    save(fig, 'fig_stacks')


def fig_tiling():
    fig, ax = plt.subplots(figsize=(2.9, 2.5))
    k = 3
    sh = np.array([[1, 0.5], [0, s3 / 2]])          # shear: right triangle -> equilateral
    for a in range(k):
        for b in range(k - a):
            up = np.array([[a, b], [a + 1, b], [a, b + 1]]) @ sh.T
            ax.add_patch(plt.Polygon(up, closed=True, fc=BLUE, alpha=0.3, ec='k', lw=0.6))
            if a + b < k - 1:
                dn = np.array([[a + 1, b + 1], [a + 1, b], [a, b + 1]]) @ sh.T
                ax.add_patch(plt.Polygon(dn, closed=True, fc=ORANGE, alpha=0.3, ec='k', lw=0.6))
    ax.set_aspect('equal'); ax.set_axis_off(); ax.set_xlim(-0.1, 3.1); ax.set_ylim(-0.1, 2.7)
    save(fig, 'fig_tiling')


def fig_lemmaO():
    """r(1 - m*(r)) against r^2, the tangent line and the band lines of OctBands.lean."""
    import re
    from fractions import Fraction as Fr
    src = open(os.path.join(ROOT, 'lean-optimality', 'PackingOptimality', 'OctBands.lean')).read()
    pat = r'h1 : \(([-\d/ ]+) : ℝ\) ≤ r \^ 2\) \(h2 : r \^ 2 ≤ \(([-\d/ ]+) : ℝ\)\) : r \* \(1 - m\) ≤ \(([-\d/ ]+) : ℝ\) \+ \(([-\d/ ]+) : ℝ\)'
    lines = [tuple(float(Fr(x.replace(' ', ''))) for x in g) for g in re.findall(pat, src)]
    assert len(lines) == 11, len(lines)
    q = np.linspace(0, 3, 1201); r = np.sqrt(q)
    m = (2 * r + np.sqrt(np.maximum(6 - 2 * q, 0))) / 6
    f = r * (1 - m)
    fig, axs = plt.subplots(1, 2, figsize=(6.2, 2.4))
    ax = axs[0]
    ax.plot(q, f, color='k', lw=1.0, label=r'$r(1-m_*(r))$')
    for i, (lo, hi, al, be) in enumerate(lines):
        x = np.linspace(lo, hi, 50)
        ax.plot(x, al + be * x, color=BLUE if i == 0 else ORANGE, lw=0.9)
    ax.plot([1], [1 / 3], 'o', color=RED, ms=3)
    ax.annotate('equality at $r=1$', (1, 1 / 3), (1.25, 0.2), fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.5))
    ax.axvline(2.09, color=GREY, lw=0.5, ls=':')
    ax.set_xlabel('$r^2$'); ax.set_xlim(0, 3); ax.set_ylim(0, 0.62)
    ax.spines[['top', 'right']].set_visible(False)
    ax = axs[1]
    for i, (lo, hi, al, be) in enumerate(lines):
        x = np.linspace(lo, hi, 400); rr = np.sqrt(x); mm = (2 * rr + np.sqrt(np.maximum(6 - 2 * x, 0))) / 6
        ax.plot(x, al + be * x - rr * (1 - mm), color=BLUE if i == 0 else ORANGE, lw=0.9)
    ax.axhline(0, color='k', lw=0.5); ax.axvline(2.09, color=GREY, lw=0.5, ls=':')
    ax.set_xlabel('$r^2$'); ax.set_ylabel('line $-$ curve'); ax.set_xlim(0, 3); ax.set_ylim(-0.005, 0.12)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    save(fig, 'fig_lemmaO')


def fig_axis_width():
    """Width of a tilted prism along a coordinate axis: L|a_i| + 2 rho sqrt(1 - a_i^2)."""
    fig, ax = plt.subplots(figsize=(3.2, 2.4))
    L, rho, th = 2.0, 0.6, np.radians(35)              # th: angle between the prism axis and e_i
    u = np.array([np.cos(th), np.sin(th)]); v = np.array([-u[1], u[0]])
    P = np.array([-L / 2 * u - rho * v, L / 2 * u - rho * v, L / 2 * u + rho * v, -L / 2 * u + rho * v])
    ax.add_patch(plt.Polygon(P, closed=True, fc=BLUE, alpha=0.25, ec=BLUE, lw=0.9))
    ax.plot(*np.array([-L / 2 * u, L / 2 * u]).T, color=BLUE, lw=0.6, ls='--')
    lo, hi = P[:, 0].min(), P[:, 0].max(); y0 = P[:, 1].min() - 0.25
    for x in (lo, hi): ax.plot([x, x], [y0, P[:, 1].max()], color=GREY, lw=0.5, ls=':')
    ax.annotate('', (hi, y0), (lo, y0), arrowprops=dict(arrowstyle='<->', color=ORANGE, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text((lo + hi) / 2, y0 - 0.17, r'$L\,|a_i|+2\rho\sqrt{1-a_i^2}$', ha='center', color=ORANGE, fontsize=8)
    ax.annotate('', (hi + 0.45, y0 + 0.3), (hi + 0.1, y0 + 0.3), arrowprops=dict(arrowstyle='->', lw=0.6))
    ax.text(hi + 0.48, y0 + 0.27, '$e_i$', fontsize=8)
    ax.text(*(0.35 * u + 0.07 * v), 'axis $a$', color=BLUE, fontsize=7.5, rotation=np.degrees(th))
    ax.set_aspect('equal'); ax.set_axis_off(); ax.set_xlim(lo - 0.15, 1.85); ax.set_ylim(y0 - 0.35, P[:, 1].max() + 0.05)
    save(fig, 'fig_axis_width')


def fig_box():
    """The box of admissible translations, and the preimages of the centre inside the piece (unit square, d = 2)."""
    s, th = 1.75, np.radians(25)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    K = np.array([[-.5, -.5], [.5, -.5], [.5, .5], [-.5, .5]])
    a = s / 2 - np.abs(R).sum(1) / 2                    # |p_i| <= a_i
    fig, axs = plt.subplots(1, 2, figsize=(5.6, 2.7))
    ax = axs[0]
    ax.add_patch(plt.Rectangle((-s / 2, -s / 2), s, s, fill=False, ec=GREY, lw=1.0))
    for p, al in ((np.array([a[0], a[1]]), 0.3), (np.array([-a[0], -a[1]]), 0.12)):
        ax.add_patch(plt.Polygon(K @ R.T + p, closed=True, fc=BLUE, alpha=al, ec=BLUE, lw=0.8))
    ax.add_patch(plt.Rectangle((-a[0], -a[1]), 2 * a[0], 2 * a[1], fc=GREEN, alpha=0.35, ec=GREEN, lw=0.8))
    ax.plot(0, 0, 'o', color=RED, ms=3)
    ax.set_title(r'positions $p$ of the piece', fontsize=8.5)
    ax = axs[1]
    ax.add_patch(plt.Polygon(K, closed=True, fc=BLUE, alpha=0.18, ec=BLUE, lw=0.9))
    B = np.array([[-a[0], -a[1]], [a[0], -a[1]], [a[0], a[1]], [-a[0], a[1]]])
    Y = -(B @ R)                                        # y = -R^T p
    ax.add_patch(plt.Polygon(Y, closed=True, fc=GREEN, alpha=0.35, ec=GREEN, lw=0.8))
    ax.plot(0, 0, '+', color='k', ms=5, mew=0.6)
    ax.set_title(r'preimages $-A^{-1}p$ of the centre', fontsize=8.5)
    for ax in axs:
        ax.set_aspect('equal'); ax.set_axis_off(); ax.set_xlim(-0.95, 0.95); ax.set_ylim(-0.95, 1.0)
    save(fig, 'fig_box')


def fig_widths():
    """The six vertex differences of the unit triangle, at 60-degree steps."""
    fig, ax = plt.subplots(figsize=(2.6, 2.6))
    T = np.array([[0, 0], [0, 1], [s3 / 2, 0.5]])
    for i, j in itertools.permutations(range(3), 2):
        d = T[i] - T[j]
        ax.annotate('', d, (0, 0), arrowprops=dict(arrowstyle='->', color=BLUE, lw=0.8))
    u = np.array([np.cos(0.35), np.sin(0.35)])
    ax.plot([-1.2 * u[0], 1.2 * u[0]], [-1.2 * u[1], 1.2 * u[1]], color=ORANGE, lw=0.7, ls='--')
    ax.text(1.0 * u[0] + 0.02, 1.0 * u[1] + 0.12, r'$u$', color=ORANGE)
    ax.set_aspect('equal'); ax.set_axis_off(); ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25)
    save(fig, 'fig_widths')


def fig_c5():
    """Base of the 5-cell in the 24-cell: the three vertices off the (1,-1,0,0) direction, in the (y2, y3)-plane."""
    b = 5 ** 0.5 / 4; rad = 3 ** 0.5 / 3; l1 = 5 ** 0.5 / 2 - 3 ** 0.5 / 6
    fig, ax = plt.subplots(figsize=(2.9, 2.9))
    ax.add_patch(plt.Rectangle((-b, -b), 2 * b, 2 * b, fill=False, ec=GREY, lw=0.9))
    ax.add_patch(plt.Circle((0, 0), rad, fill=False, ec=BLUE, lw=0.5, ls=':'))
    for deg, mk in ((0, 'o'), (15, 'o')):
        P = np.array([[rad * np.cos(np.radians(deg + 120 * k)), rad * np.sin(np.radians(deg + 120 * k))] for k in range(3)])
        if deg == 15:
            assert np.abs(P).max() <= b and np.abs(P).sum(1).max() <= l1
            ax.add_patch(plt.Polygon(P, closed=True, fill=False, ec=BLUE, lw=0.8))
            ax.plot(P[:, 0], P[:, 1], 'o', color=BLUE, ms=3.5)
        else:
            ax.plot(P[:, 0], P[:, 1], 'o', mfc='none', mec=RED, ms=4, mew=0.7)
    ax.annotate(r'$0^\circ$: outside', (rad, 0), (0.2, -0.33), fontsize=7, color=RED, arrowprops=dict(arrowstyle='->', lw=0.5, color=RED))
    ax.text(rad * np.cos(np.radians(15)) - 0.03, rad * np.sin(np.radians(15)) + 0.05, r'$15^\circ$', fontsize=7, color=BLUE, ha='right')
    ax.text(-b, b + 0.03, r'$|y_i|\leq\sqrt{5}/4$', fontsize=7, color=GREY)
    ax.set_xlabel('$y_2$', fontsize=8); ax.set_ylabel('$y_3$', fontsize=8)
    ax.set_aspect('equal'); ax.set_xlim(-0.65, 0.65); ax.set_ylim(-0.65, 0.68)
    ax.set_xticks([]); ax.set_yticks([]); ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    save(fig, 'fig_c5')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_tets(); fig_facet_width(); fig_lemmaO(); fig_axis_width(); fig_box(); fig_two_ball(); fig_octa(); fig_six_prisms(); fig_pinwheel(); fig_stacks(); fig_tiling(); fig_widths(); fig_c5()
    print('figures written to', OUT)
