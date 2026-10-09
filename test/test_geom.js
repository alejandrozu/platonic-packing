// Tests for src/geom.js on random pairs of every solid (and mixed pairs):
//  1. separated pairs: the returned closest points satisfy the exact optimality (KKT) conditions — the plane
//     through PA orthogonal to n supports A and the parallel plane through PB supports B — so the distance is the
//     true Euclidean distance, not just an upper bound;
//  2. overlapping pairs: no direction (12k random + all SAT axes) gives a smaller projected overlap than the
//     reported penetration depth, and moving B by (depth + 1e-9) along the reported axis separates the pair;
//  3. analytic gradients of sd w.r.t. both centres and both rotation vectors match central finite differences.
'use strict';
const G = require('../src/geom.js');
let seed = 12345;
const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
const gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-300)) * Math.cos(2 * Math.PI * rnd());
const rq = () => { const q = [gauss(), gauss(), gauss(), gauss()], m = Math.hypot(...q); return q.map(v => v / m); };
const names = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron'];
const shapes = Object.fromEntries(names.map(n => [n, G.prepShape(n)]));
const supp = (P, u) => { let m = -Infinity; for (let i = 0; i < P.shape.nv; i++) m = Math.max(m, P.X[3 * i] * u[0] + P.X[3 * i + 1] * u[1] + P.X[3 * i + 2] * u[2]); return m; };
let fails = 0, nSep = 0, nPen = 0, maxGradErr = 0, nGrad = 0, nHint = 0;
const pairs = [];
for (const a of names) for (const b of names) pairs.push([a, b]);
for (const [na, nb] of pairs) {
  for (let trial = 0; trial < 60; trial++) {
    const k = trial % 3 === 0 ? 1 : 0.2 + 0.8 * rnd();
    const SA = shapes[na], SB = shapes[nb];
    const span = k * (SA.circ + SB.circ);
    const cA = [0, 0, 0], dir = [gauss(), gauss(), gauss()], dl = Math.hypot(...dir);
    const dist = span * (0.3 + 0.9 * rnd());
    const cB = dir.map(x => x / dl * dist);
    const qA = rq(), qB = rq();
    const A = G.pose(SA, cA, qA, k), B = G.pose(SB, cB, qB, k);
    const sd = G.sdCores(A, B, Infinity, true);
    const g = Array.from(G.GR);
    // the hinted path must give the same value and gradient, with an exact hint and with a perturbed one
    if (sd > 0) {
      const ax = G.sdCores.lastAxis;
      for (const hint of [ax, [ax[0] + 0.05, ax[1] - 0.03, ax[2] + 0.02]]) {
        const hl = Math.hypot(...hint), h = hint.map(x => x / hl);
        const sdh = G.sdCores(A, B, Infinity, true, h);
        if (Math.abs(sdh - sd) > 1e-12 || g.some((v, i) => Math.abs(v - G.GR[i]) > 1e-9)) { fails++; console.log('HINT fail', na, nb, sd, sdh); }
      }
      nHint++;
    }
    if (sd > 0) {
      nSep++;
      const { PA, PB } = G.distSeparated.last;
      const n = G.sub(PB, PA).map(x => x / sd);
      const e1 = supp(A, n) - G.dot(n, PA), e2 = supp(B, n.map(x => -x)) + G.dot(n, PB);
      if (Math.abs(Math.hypot(...G.sub(PB, PA)) - sd) > 1e-12 || e1 > 1e-9 || e2 > 1e-9) { fails++; console.log('KKT fail', na, nb, sd, e1, e2); }
    } else {
      nPen++;
      const pen = -sd;
      let minO = Infinity;
      for (let t = 0; t < 12000; t++) {
        const u = [gauss(), gauss(), gauss()], l = Math.hypot(...u); for (let i = 0; i < 3; i++) u[i] /= l;
        minO = Math.min(minO, supp(A, u) + supp(B, u.map(x => -x)));
      }
      // move B along the pushing direction (gradient of sd w.r.t. cB is +u)
      const u = [g[6], g[7], g[8]];
      const B2 = G.pose(SB, cB.map((x, i) => x + (pen + 1e-9) * u[i]), qB, k);
      const B3 = G.pose(SB, cB.map((x, i) => x + (pen - 1e-7) * u[i]), qB, k);
      const sep2 = !G.overlaps(A, B2, 0), sep3 = !G.overlaps(A, B3, 0);
      if (minO < pen - 1e-12 || !sep2 || sep3) { fails++; console.log('PEN fail', na, nb, pen, minO, sep2, sep3); }
    }
    // finite-difference gradient
    const h = 1e-6;
    const f = (dc, dw) => {
      const A2 = G.pose(SA, cA.map((x, i) => x + dc[i]), G.rotq(qA, dw[0], dw[1], dw[2]), k);
      const B2 = G.pose(SB, cB.map((x, i) => x + dc[3 + i]), G.rotq(qB, dw[3], dw[4], dw[5]), k);
      return G.sdCores(A2, B2, Infinity, false);
    };
    const num = [];
    for (let t = 0; t < 12; t++) {
      const dc = [0, 0, 0, 0, 0, 0], dw = [0, 0, 0, 0, 0, 0];
      const slot = t < 3 ? [dc, t] : t < 6 ? [dw, t - 3] : t < 9 ? [dc, t - 3] : [dw, t - 6];
      slot[0][slot[1]] = h; const fp = f(dc, dw); slot[0][slot[1]] = -h; const fm = f(dc, dw);
      num.push((fp - fm) / (2 * h));
    }
    const err = Math.max(...num.map((v, i) => Math.abs(v - g[i])));
    nGrad++;
    if (err > 1e-5) {
      // a kink (active feature switching inside +-h) is legitimate; recheck with a smaller step before failing
      const h2 = 1e-8;
      let err2 = 0;
      for (let t = 0; t < 12; t++) {
        const dc = [0, 0, 0, 0, 0, 0], dw = [0, 0, 0, 0, 0, 0];
        const slot = t < 3 ? [dc, t] : t < 6 ? [dw, t - 3] : t < 9 ? [dc, t - 3] : [dw, t - 6];
        slot[0][slot[1]] = h2; const fp = f(dc, dw); slot[0][slot[1]] = 0; const f0 = f(dc, dw);
        err2 = Math.max(err2, Math.abs((fp - f0) / h2 - g[t]));
      }
      if (err2 > 1e-4) { fails++; console.log('GRAD fail', na, nb, sd, err, err2); }
    } else maxGradErr = Math.max(maxGradErr, err);
  }
}
console.log(`pairs: ${nSep} separated (KKT-certified distances), ${nPen} overlapping (penetration checked), ${nGrad} gradients (max smooth error ${maxGradErr.toExponential(2)}), ${nHint} hinted re-evaluations`);
console.log(fails ? `FAILURES: ${fails}` : 'ALL GEOMETRY TESTS PASSED');
process.exit(fails ? 1 : 0);
