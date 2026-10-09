// Soft->rigid packer for unit copies of any Platonic solid in a container that is a scaled copy of any Platonic
// solid (default: the same solid). Generalizes Yohei Nakajima's sim3.js (rounded cubes) to convex polytopes.
//
// Shape at softness r (internal units: the piece's inradius is 1/2):   S_r = (1 - 2r) P  (+)  B(r).
//   r = 1/2 -> the inscribed ball;   r = 0 -> the solid P;   S_r is contained in P for every r (README, Lemma 1).
// Energy: sum_pairs (2r - sd_core)_+^2 + sum_walls (violation)_+^2 + mu * L, where L/2 is the container's inradius.
// Orientation = quaternion, analytic gradients (src/geom.js), heavy-ball descent with velocity cap and annealed noise.
'use strict';
const G = require('./geom.js');

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function gauss(rng) { let u = 0; while (u === 0) u = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rng()); }

// Problem: piece solid P (inradius 1/2) and container solid C at the same edge length; container of "size" L is
// { x : N_f . x <= (L/2) off_f } (centred at the origin), and its edge ratio is s = L / (2 rho_C).
function makeProblem(piece, container) {
  const P = G.prepShape(piece);
  const C = G.prepShape(container || piece, P.edge);
  const rhoC = C.inradius;
  return { P, C, off: C.beta.map(b => b / rhoC), rhoC, sOfL: L => L / (2 * rhoC), LofS: s => 2 * rhoC * s };
}

function makeState(pb, n, seed, L0) {
  const rng = mulberry32(seed * 7919 + 13);
  const st = { pb, n, rng, L: L0, vL: 0, r: 0.5, step: 0, phase: 'init', frames: [], log: [], C: [], Q: [], V: [], W: [] };
  const Rc = (L0 / 2) * Math.max(...pb.C.V.map(v => Math.hypot(...v))) / pb.rhoC;
  for (let i = 0; i < n; i++) {
    let p;
    for (let tries = 0; ; tries++) {   // uniform in the container shrunk by 0.7
      p = [(2 * rng() - 1) * Rc, (2 * rng() - 1) * Rc, (2 * rng() - 1) * Rc];
      if (pb.C.N.every((N, f) => G.dot(N, p) <= (L0 / 2) * pb.off[f] - 0.7)) break;
      if (tries > 100000) throw new Error('cannot place initial centre');
    }
    st.C.push(p);
    const q = [gauss(rng), gauss(rng), gauss(rng), gauss(rng)], m = Math.hypot(...q); st.Q.push(q.map(v => v / m));
    st.V.push([0, 0, 0]); st.W.push([0, 0, 0]);
  }
  return st;
}

function dyn(st, r, mu, noise, moveL) {
  const { pb, n } = st, P = pb.P;
  const beta = 0.85, cap = 0.03, lr = 0.04, k = 1 - 2 * r;
  const poses = st.C.map((c, i) => G.pose(P, c, st.Q[i], k));
  const GC = st.C.map(() => [0, 0, 0]), GW = st.C.map(() => [0, 0, 0]);
  const lim = (2 * (k * P.circ + r) + 1e-3) ** 2, GR = G.GR;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
    const a = st.C[i], b = st.C[j];
    if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2 > lim) continue;
    const sd = G.sdCores(poses[i], poses[j], 2 * r, true);
    const o = 2 * r - sd; if (o <= 0) continue;
    const c = -2 * o;
    for (let t = 0; t < 3; t++) { GC[i][t] += c * GR[t]; GW[i][t] += c * GR[3 + t]; GC[j][t] += c * GR[6 + t]; GW[j][t] += c * GR[9 + t]; }
  }
  let gL = mu;
  const Cn = pb.C.N, nv = P.nv;
  for (let i = 0; i < n; i++) {
    const X = poses[i].X, c = st.C[i];
    for (let f = 0; f < Cn.length; f++) {
      const N = Cn[f];
      let m = -Infinity, im = 0;
      for (let v = 0; v < nv; v++) { const p = X[3 * v] * N[0] + X[3 * v + 1] * N[1] + X[3 * v + 2] * N[2]; if (p > m) { m = p; im = v; } }
      const q = m + r - (st.L / 2) * pb.off[f];
      if (q <= 0) continue;
      const lev = [X[3 * im] - c[0], X[3 * im + 1] - c[1], X[3 * im + 2] - c[2]], tq = G.cross(lev, N);
      for (let t = 0; t < 3; t++) { GC[i][t] += 2 * q * N[t]; GW[i][t] += 2 * q * tq[t]; }
      if (moveL) gL -= 2 * q * pb.off[f];
    }
  }
  const ball = r >= 0.4999;
  for (let i = 0; i < n; i++) {
    const V = st.V[i], W = st.W[i];
    for (let t = 0; t < 3; t++) { V[t] = beta * V[t] - lr * GC[i][t]; W[t] = ball ? 0 : beta * W[t] - lr * GW[i][t]; }
    const vm = Math.hypot(...V); if (vm > cap) for (let t = 0; t < 3; t++) V[t] *= cap / vm;
    const wm = Math.hypot(...W); if (wm > cap) for (let t = 0; t < 3; t++) W[t] *= cap / wm;
    for (let t = 0; t < 3; t++) st.C[i][t] += V[t] + (noise > 0 ? noise * gauss(st.rng) : 0);
    let wx = W[0], wy = W[1], wz = W[2];
    if (noise > 0 && !ball) { wx += 1.5 * noise * gauss(st.rng); wy += 1.5 * noise * gauss(st.rng); wz += 1.5 * noise * gauss(st.rng); }
    st.Q[i] = G.rotq(st.Q[i], wx, wy, wz);
  }
  if (moveL) {
    st.vL = beta * st.vL - 0.02 * gL;
    if (Math.abs(st.vL) > cap) st.vL = Math.sign(st.vL) * cap;
    st.L += st.vL;
  }
  st.r = r; st.step++;
}

function snap(st) {
  const f = { ph: st.phase, r: +st.r.toFixed(4), L: +st.L.toFixed(5), s: st.step, p: [] };
  for (let i = 0; i < st.n; i++) f.p.push(...st.C[i].map(v => +v.toFixed(4)), ...st.Q[i].map(v => +v.toFixed(5)));
  st.frames.push(f);
}

// Smallest container (any translation) holding all given world vertices: min z s.t. N_f.(x + t) <= z off_f.
// LP in (t, z); its optimum is a vertex = 4 active constraints, so enumerate 4-subsets of faces.
function tightContainer(pb, Xs) {
  const N = pb.C.N, F = N.length, off = pb.off;
  const S = N.map(u => { let m = -Infinity; for (const X of Xs) for (let v = 0; v < X.length; v += 3) m = Math.max(m, X[v] * u[0] + X[v + 1] * u[1] + X[v + 2] * u[2]); return m; });
  let best = null;
  const solve4 = (M, b) => {   // Gaussian elimination with partial pivoting
    const A = M.map((row, i) => [...row, b[i]]);
    for (let c = 0; c < 4; c++) {
      let p = c; for (let r = c + 1; r < 4; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      if (Math.abs(A[p][c]) < 1e-12) return null;
      [A[c], A[p]] = [A[p], A[c]];
      for (let r = 0; r < 4; r++) if (r !== c) { const f = A[r][c] / A[c][c]; for (let k = c; k < 5; k++) A[r][k] -= f * A[c][k]; }
    }
    return A.map((row, i) => row[4] / row[i]);
  };
  for (let a = 0; a < F; a++) for (let b = a + 1; b < F; b++) for (let c = b + 1; c < F; c++) for (let d = c + 1; d < F; d++) {
    const idx = [a, b, c, d];
    const sol = solve4(idx.map(f => [N[f][0], N[f][1], N[f][2], -off[f]]), idx.map(f => -S[f]));
    if (!sol) continue;
    const [t0, t1, t2, z] = sol;
    let ok = true;
    for (let f = 0; f < F; f++) if (S[f] + N[f][0] * t0 + N[f][1] * t1 + N[f][2] * t2 > z * off[f] + 1e-9 * (1 + Math.abs(z))) { ok = false; break; }
    if (ok && (best === null || z < best.z)) best = { z, t: [t0, t1, t2] };
  }
  // exact feasibility of the reported L: recompute z as the max ratio at the chosen translation
  const t = best.t;
  let z = -Infinity; for (let f = 0; f < F; f++) z = Math.max(z, (S[f] + G.dot(N[f], t)) / off[f]);
  return { L: 2 * z, t };
}

// Legalization: scale centres apart about their mean until no pair of rigid pieces overlaps (SAT, tol 1e-12),
// then measure the tight container.
function legalize(pb, C, Q) {
  const n = C.length, P = pb.P;
  const cen = [0, 1, 2].map(t => C.reduce((a, c) => a + c[t], 0) / n);
  const pos = s => C.map(c => [cen[0] + s * (c[0] - cen[0]), cen[1] + s * (c[1] - cen[1]), cen[2] + s * (c[2] - cen[2])]);
  const lim = (2 * P.circ) ** 2;
  const ok = s => {
    const Pp = pos(s), ps = Pp.map((c, i) => G.pose(P, c, Q[i], 1));
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      const a = Pp[i], b = Pp[j];
      if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2 > lim) continue;
      if (G.overlaps(ps[i], ps[j], 1e-12)) return false;
    }
    return true;
  };
  let lo = 1, hi = 1;
  if (!ok(1)) { hi = 1.0001; while (!ok(hi)) hi = 1 + (hi - 1) * 2; for (let it = 0; it < 60; it++) { const m = (lo + hi) / 2; if (ok(m)) hi = m; else lo = m; } }
  const Pp = pos(hi);
  const tc = tightContainer(pb, Pp.map((c, i) => G.pose(P, c, Q[i], 1).X));
  return { L: tc.L, s: pb.sOfL(tc.L), k: hi, C: Pp.map(p => [p[0] + tc.t[0], p[1] + tc.t[1], p[2] + tc.t[2]]), Q: Q.map(q => q.slice()) };
}

function defaultL0(pb, n) {
  // initial container: balls (diameter 1) at packing fraction ~0.07, centres at least 0.7 inside every wall
  const volAtL = L => pb.C.volume * Math.pow(pb.sOfL(L), 3);
  let L = 2; while (n * Math.PI / 6 / volAtL(L) > 0.07) L *= 1.02;
  return Math.max(L, 2 * (0.7 + 0.35));
}

function run(cfg) {
  const c = Object.assign({ seed: 1, n: 8, piece: 'tetrahedron', container: null, mode: 'improved', L0: 0, compact: 5000, morph: 45000, settle: 3000, mu: 0.02, recEvery: 1e9 }, cfg);
  const pb = makeProblem(c.piece, c.container || c.piece);
  if (!c.L0) c.L0 = defaultL0(pb, c.n);
  if (c.anneal === undefined) c.anneal = c.mode === 'improved';
  const rigid = c.mode === 'rigid';
  const st = makeState(pb, c.n, c.seed, c.L0);
  const rec = () => { if (st.step % c.recEvery === 0) snap(st); };
  snap(st);
  st.phase = rigid ? 'compress (rigid)' : 'compress balls';
  for (let k = 0; k < c.compact; k++) { const u = k / c.compact; dyn(st, rigid ? 0 : 0.5, c.mu * 3, (c.anneal ? 0.015 : 0.008) * (1 - u), true); rec(); }
  st.log.push({ phase: st.phase, L: st.L });
  st.phase = rigid ? 'hold (rigid)' : 'morph ball->solid';
  for (let k = 0; k < c.morph; k++) { const u = k / c.morph; dyn(st, rigid ? 0 : 0.5 * (1 - u), c.mu, c.anneal ? 0.004 * (1 - u) : 0, true); rec(); }
  st.log.push({ phase: st.phase, L: st.L });
  st.phase = 'rigid settle';
  for (let k = 0; k < c.settle; k++) { dyn(st, 0, c.mu * Math.pow(1e-4, k / c.settle), 0, true); rec(); }
  st.log.push({ phase: st.phase, L: st.L });
  st.phase = 'final'; snap(st);
  const leg = legalize(pb, st.C, st.Q);
  st.frames.push({ ph: 'certified', r: 0, L: +leg.L.toFixed(6), s: st.step, p: leg.C.flatMap((p, i) => [...p.map(v => +v.toFixed(5)), ...leg.Q[i].map(v => +v.toFixed(6))]) });
  return { cfg: c, s: leg.s, L: leg.L, Lsoft: st.L, scale: leg.k, frames: st.frames, log: st.log, final: leg, edge: pb.P.edge };
}

module.exports = { run, makeProblem, legalize, tightContainer, defaultL0, dyn, makeState };
