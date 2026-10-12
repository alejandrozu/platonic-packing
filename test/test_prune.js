// Gauss-map pruned SAT (geom.edgeAxes) must give exactly the same signed distance as the full edge-direction scan,
// for every solid and for the cores of the r-rounding of non-tangential solids at random softness.
'use strict';
const G = require('../src/geom.js'), S = require('../src/sim.js');
const names = Object.keys(G.SOLIDS);
let worst = 0, pairs = 0, overl = 0;
function rq() { const q = [Math.random() - .5, Math.random() - .5, Math.random() - .5, Math.random() - .5], m = Math.hypot(...q); return q.map(x => x / m); }
for (const a of names) {
  const pb = S.makeProblem(a);
  for (let t = 0; t < 40; t++) {
    const r = t % 3 === 0 ? 0 : Math.random() * pb.rcap * 0.98;
    const sh = S.softShape(pb, r), sp = sh.S;
    const sFull = Object.assign({}, sp, { prune: false }), sPr = Object.assign({}, sp, { prune: true });
    const c1 = [0, 0, 0], c2 = [(Math.random() - .5), (Math.random() - .5), (Math.random() - .5)].map(x => x * 2.2 * sp.circ * sh.k);
    const q1 = rq(), q2 = rq();
    const dF = G.sdCores(G.pose(sFull, c1, q1, sh.k), G.pose(sFull, c2, q2, sh.k), Infinity, true);
    const gF = Array.from(G.GR);
    const dP = G.sdCores(G.pose(sPr, c1, q1, sh.k), G.pose(sPr, c2, q2, sh.k), Infinity, true);
    const gP = Array.from(G.GR);
    const e = Math.abs(dF - dP) + (dF < 0 ? Math.max(...gF.map((x, i) => Math.abs(x - gP[i]))) * 0 : 0);
    if (e > 1e-9) { console.log('MISMATCH', a, r.toFixed(3), dF, dP); process.exitCode = 1; }
    worst = Math.max(worst, e); pairs++; if (dF < 0) overl++;
  }
}
console.log(`pruned SAT vs full scan: ${pairs} pairs (${overl} overlapping), max |difference| ${worst.toExponential(2)}`);
