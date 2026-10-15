// Soft->rigid packer for unit copies of any Platonic solid in a container that is a scaled copy of any Platonic
// solid (default: the same solid). Generalizes Yohei Nakajima's sim3.js (rounded cubes) to convex polytopes.
//
// Shape at softness r (internal units: the piece's inradius is 1/2):   S_r = (1 - 2r) P  (+)  B(r).
//   r = 1/2 -> the inscribed ball;   r = 0 -> the solid P;   S_r is contained in P for every r (README, Lemma 1).
// Energy: sum_pairs (2r - sd_core)_+^2 + sum_walls (violation)_+^2 + mu * L, where L/2 is the container's inradius.
// Orientation = quaternion, analytic gradients (src/geom.js), heavy-ball descent with velocity cap and annealed noise.
'use strict';
const G = require('./geom.js');
const GEO = G;

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
  const rhoC = Math.min(...C.beta);                 // container inradius (smallest face distance)
  const rcap = P.cores ? P.cores[P.cores.length - 1].r1 : 0.5;
  return { P, C, off: C.beta.map(b => b / rhoC), rhoC, rcap, sOfL: L => L / (2 * rhoC), LofS: s => 2 * rhoC * s };
}

// Soft shape at softness r: (core shape, core scale k, rounding radius rr) with S_r = k * core (+) B(rr).
// Tangential solids (an insphere touching every face: Platonic, Catalan): Nakajima's (1 - 2r) P (+) B(r).
// Others: the r-rounding (P (-) B(r)) (+) B(r), whose core is a polytope precomputed by polyhedra.py; it is capped at
// rcap < 1/2 where the core would become flat (a polygon or a segment).
function softShape(pb, r) {
  const P = pb.P;
  if (P.tangential || r <= 0) return { S: P, k: P.tangential ? 1 - 2 * r : 1, rr: r };
  const rr = Math.min(r, pb.rcap);
  return { S: G.coreShape(P, rr), k: 1, rr };
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

function dyn(st, r0, mu, noise, moveL) {
  const { pb, n } = st;
  const sh = softShape(pb, r0), P = sh.S, k = sh.k, r = sh.rr;
  const beta = 0.85, cap = 0.03, lr = 0.04;
  const poses = st.C.map((c, i) => G.pose(P, c, st.Q[i], k));
  const GC = st.C.map(() => [0, 0, 0]), GW = st.C.map(() => [0, 0, 0]);
  const lim = (2 * (k * P.circ + r) + 1e-3) ** 2, GR = G.GR;
  if (!st.hints) st.hints = new Map();
  const H = st.hints;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
    const a = st.C[i], b = st.C[j];
    if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2 > lim) continue;
    const key = i * n + j;
    const sd = G.sdCores(poses[i], poses[j], 2 * r, true, H.get(key));
    if (G.sdCores.lastAxis) H.set(key, G.sdCores.lastAxis); else H.delete(key);
    const o = 2 * r - sd; if (o <= 0) continue;
    if (st.ov) st.ov.set(key, o);
    const c = -2 * o * (st.wp ? (st.wp.get(key) || 1) : 1);
    for (let t = 0; t < 3; t++) { GC[i][t] += c * GR[t]; GW[i][t] += c * GR[3 + t]; GC[j][t] += c * GR[6 + t]; GW[j][t] += c * GR[9 + t]; }
  }
  let gL = mu;
  if (st.ov) { st.ov.clear(); st.wq = new Float64Array(n); }
  const Cn = pb.C.N, nv = P.nv;
  for (let i = 0; i < n; i++) {
    const X = poses[i].X, c = st.C[i];
    for (let f = 0; f < Cn.length; f++) {
      const N = Cn[f];
      let m = -Infinity, im = 0;
      for (let v = 0; v < nv; v++) { const p = X[3 * v] * N[0] + X[3 * v + 1] * N[1] + X[3 * v + 2] * N[2]; if (p > m) { m = p; im = v; } }
      const q = m + r - (st.L / 2) * pb.off[f];
      if (q <= 0) continue;
      if (st.wq && q > st.wq[i]) st.wq[i] = q;
      const lev = [X[3 * im] - c[0], X[3 * im + 1] - c[1], X[3 * im + 2] - c[2]], tq = G.cross(lev, N);
      for (let t = 0; t < 3; t++) { GC[i][t] += 2 * q * N[t]; GW[i][t] += 2 * q * tq[t]; }
      if (moveL) gL -= 2 * q * pb.off[f];
    }
  }
  const ball = pb.P.tangential && r0 >= 0.4999;
  for (let i = 0; i < n; i++) {
    const V = st.V[i], W = st.W[i];
    for (let t = 0; t < 3; t++) { V[t] = beta * V[t] - lr * GC[i][t]; W[t] = ball ? 0 : beta * W[t] - lr * GW[i][t]; }
    const vm = Math.hypot(...V); if (vm > cap) for (let t = 0; t < 3; t++) V[t] *= cap / vm;
    const wm = Math.hypot(...W); if (wm > cap) for (let t = 0; t < 3; t++) W[t] *= cap / wm;
    const nz = st.mask ? noise * st.mask[i] : noise;           // optional per-piece noise (focused hops)
    for (let t = 0; t < 3; t++) st.C[i][t] += V[t] + (nz > 0 ? nz * gauss(st.rng) : 0);
    let wx = W[0], wy = W[1], wz = W[2];
    if (nz > 0 && !ball) { wx += 1.5 * nz * gauss(st.rng); wy += 1.5 * nz * gauss(st.rng); wz += 1.5 * nz * gauss(st.rng); }
    st.Q[i] = G.rotq(st.Q[i], wx, wy, wz);
  }
  if (moveL) {
    st.vL = beta * st.vL - 0.02 * gL;
    if (Math.abs(st.vL) > cap) st.vL = Math.sign(st.vL) * cap;
    st.L += st.vL;
  }
  st.r = r0; st.step++;
}

function snap(st) {
  const f = { ph: st.phase, r: +st.r.toFixed(4), L: +st.L.toFixed(5), s: st.step, p: [] };
  for (let i = 0; i < st.n; i++) f.p.push(...st.C[i].map(v => +v.toFixed(4)), ...st.Q[i].map(v => +v.toFixed(5)));
  st.frames.push(f);
}

// Smallest container (any translation) holding all given world vertices: min z s.t. N_f.(x + t) <= z off_f.
// LP in (t, z); its optimum is a vertex = 4 active constraints, so enumerate 4-subsets of faces.
// Dual of  min z s.t. N_f.t - off_f z <= -S_f :  max sum_f S_f lam_f  s.t. sum_f lam_f N_f = 0, sum_f lam_f off_f = 1,
// lam >= 0 (4 equality rows). Two-phase tableau simplex with Bland's rule; the optimal multipliers y of the 4 rows give
// the primal solution t = -y[0..2]. Only used to choose t: the reported size is recomputed exactly at that t.
function lpTranslation(N, off, S) {
  const F = N.length, m = 4, nc = F + m, eps = 1e-12;
  const T = [0, 1, 2, 3].map(i => { const row = new Float64Array(nc + 1); for (let f = 0; f < F; f++) row[f] = i < 3 ? N[f][i] : off[f]; row[F + i] = 1; row[nc] = i === 3 ? 1 : 0; return row; });
  const basis = [F, F + 1, F + 2, F + 3];
  const run = (cost, allowArt) => {
    const rc = new Float64Array(nc);
    for (let j = 0; j < nc; j++) { let v = cost[j]; for (let i = 0; i < m; i++) v -= cost[basis[i]] * T[i][j]; rc[j] = v; }
    for (let it = 0; it < 500; it++) {
      let e = -1; for (let j = 0; j < nc; j++) if (rc[j] > eps && (allowArt || j < F)) { e = j; break; }
      if (e < 0) return rc;
      let r = -1, best = Infinity;
      for (let i = 0; i < m; i++) if (T[i][e] > eps) { const q = T[i][nc] / T[i][e]; if (q < best - 1e-15 || (Math.abs(q - best) <= 1e-15 && basis[i] < basis[r])) { best = q; r = i; } }
      if (r < 0) return rc;                                   // unbounded (cannot happen: the feasible set is bounded)
      const pv = T[r][e]; for (let j = 0; j <= nc; j++) T[r][j] /= pv;
      for (let i = 0; i < m; i++) if (i !== r && T[i][e] !== 0) { const f = T[i][e]; for (let j = 0; j <= nc; j++) T[i][j] -= f * T[r][j]; }
      const f = rc[e]; for (let j = 0; j < nc; j++) rc[j] -= f * T[r][j];
      basis[r] = e;
    }
    return rc;
  };
  const c1 = new Float64Array(nc); for (let j = F; j < nc; j++) c1[j] = -1;
  run(c1, true);
  const c2 = new Float64Array(nc); for (let f = 0; f < F; f++) c2[f] = S[f];
  const rc = run(c2, false);
  return [rc[F], rc[F + 1], rc[F + 2]];                     // t = -y = reduced costs of the artificial columns
}

function tightContainer(pb, Xs) {
  const N = pb.C.N, F = N.length, off = pb.off;
  const S = N.map(u => { let m = -Infinity; for (const X of Xs) for (let v = 0; v < X.length; v += 3) m = Math.max(m, X[v] * u[0] + X[v + 1] * u[1] + X[v + 2] * u[2]); return m; });
  if (F > 14) {
    const zAt = t => { let z = -Infinity; for (let f = 0; f < F; f++) z = Math.max(z, (S[f] + G.dot(N[f], t)) / off[f]); return z; };
    const t = lpTranslation(N, off, S), tn = t.map(x => -x);
    const z1 = zAt(t), z2 = zAt(tn), z0 = zAt([0, 0, 0]);
    const tb = z1 <= z2 && z1 <= z0 ? t : (z2 <= z0 ? tn : [0, 0, 0]);
    return { L: 2 * Math.min(z0, z1, z2), t: tb };
  }
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
  // initial container: balls (diameter 1) at packing fraction ~0.07, centres at least 0.7 inside every wall; for a
  // non-tangential piece the starting shape is its rcap-rounding, so the piece's own volume is used instead
  const volAtL = L => pb.C.volume * Math.pow(pb.sOfL(L), 3);
  const vp = pb.P.tangential ? Math.PI / 6 : pb.P.volume;
  let L = 2; while (n * vp / volAtL(L) > 0.07) L *= 1.02;
  return Math.max(L, 2 * (0.7 + 0.35));
}


// ---------------------------------------------------------------- symmetric search (experimental)
// st.sym = { orbits: [{ m: [piece indices], G: [3x3 row-major], D: [det G], M: [3x3 piece-frame matrix] }], fixed: [{ i, P }] }
// Piece m[j] is the image of the representative under G[j]: c = G c0, R = G R0 M[j] (M[j] a reflection symmetry of the
// piece when det G[j] = -1, else the identity). fixed: pieces whose centre is projected onto the fixed subspace (P).
const mv = (G, v) => [G[0] * v[0] + G[1] * v[1] + G[2] * v[2], G[3] * v[0] + G[4] * v[1] + G[5] * v[2], G[6] * v[0] + G[7] * v[1] + G[8] * v[2]];
const mtv = (G, v) => [G[0] * v[0] + G[3] * v[1] + G[6] * v[2], G[1] * v[0] + G[4] * v[1] + G[7] * v[2], G[2] * v[0] + G[5] * v[1] + G[8] * v[2]];
function mm(A, B) { const C = new Array(9); for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) C[3 * i + j] = A[3 * i] * B[j] + A[3 * i + 1] * B[3 + j] + A[3 * i + 2] * B[6 + j]; return C; }
const mT = A => [A[0], A[3], A[6], A[1], A[4], A[7], A[2], A[5], A[8]];
function RtoQ(R) {
  const t = R[0] + R[4] + R[8]; let w, x, y, z;
  if (t > 0) { const S = Math.sqrt(t + 1) * 2; w = 0.25 * S; x = (R[7] - R[5]) / S; y = (R[2] - R[6]) / S; z = (R[3] - R[1]) / S; }
  else if (R[0] > R[4] && R[0] > R[8]) { const S = Math.sqrt(1 + R[0] - R[4] - R[8]) * 2; w = (R[7] - R[5]) / S; x = 0.25 * S; y = (R[1] + R[3]) / S; z = (R[2] + R[6]) / S; }
  else if (R[4] > R[8]) { const S = Math.sqrt(1 + R[4] - R[0] - R[8]) * 2; w = (R[2] - R[6]) / S; x = (R[1] + R[3]) / S; y = 0.25 * S; z = (R[5] + R[7]) / S; }
  else { const S = Math.sqrt(1 + R[8] - R[0] - R[4]) * 2; w = (R[3] - R[1]) / S; x = (R[2] + R[6]) / S; y = (R[5] + R[7]) / S; z = 0.25 * S; }
  const m = Math.hypot(w, x, y, z); return [w / m, x / m, y / m, z / m];
}
function symmetrize(st) {
  const S = st.sym; if (!S) return;
  for (const o of S.orbits) {
    const k = o.m.length, c0 = [0, 0, 0], v0 = [0, 0, 0], w0 = [0, 0, 0], q0 = [0, 0, 0, 0];
    let qref = null;
    for (let j = 0; j < k; j++) {
      const i = o.m[j], G = o.G[j];
      const a = mtv(G, st.C[i]), b = mtv(G, st.V[i]), c = mtv(G, st.W[i]);
      for (let t = 0; t < 3; t++) { c0[t] += a[t] / k; v0[t] += b[t] / k; w0[t] += o.D[j] * c[t] / k; }
      const E = mm(mm(mT(G), GEO.quatToR(st.Q[i])), mT(o.M[j]));
      const q = RtoQ(E);
      if (!qref) qref = q;
      const sg = (q[0] * qref[0] + q[1] * qref[1] + q[2] * qref[2] + q[3] * qref[3]) < 0 ? -1 : 1;
      for (let t = 0; t < 4; t++) q0[t] += sg * q[t];
    }
    const qm = Math.hypot(...q0); for (let t = 0; t < 4; t++) q0[t] /= qm;
    const R0 = GEO.quatToR(q0);
    for (let j = 0; j < k; j++) {
      const i = o.m[j], Gj = o.G[j];
      st.C[i] = mv(Gj, c0); st.V[i] = mv(Gj, v0); const w = mv(Gj, w0); st.W[i] = w.map(x => o.D[j] * x);
      st.Q[i] = RtoQ(mm(mm(Gj, R0), o.M[j]));
    }
  }
  for (const f of S.fixed) { st.C[f.i] = mv(f.P, st.C[f.i]); st.V[f.i] = mv(f.P, st.V[f.i]); }
}

function run(cfg) {
  const c = Object.assign({ seed: 1, n: 8, piece: 'tetrahedron', container: null, mode: 'improved', L0: 0, compact: 5000, morph: 45000, settle: 3000, mu: 0.02, recEvery: 1e9 }, cfg);
  const pb = makeProblem(c.piece, c.container || c.piece);
  if (!c.L0) c.L0 = defaultL0(pb, c.n);
  if (c.anneal === undefined) c.anneal = c.mode === 'improved';
  const rigid = c.mode === 'rigid';
  const st = makeState(pb, c.n, c.seed, c.L0);
  if (c.sym) { st.sym = c.sym; symmetrize(st); }
  const r0 = c.r0 === undefined ? 0.5 : c.r0;
  const rec = () => { if (st.step % c.recEvery === 0) snap(st); };
  snap(st);
  st.phase = rigid ? 'compress (rigid)' : 'compress balls';
  for (let k = 0; k < c.compact; k++) { const u = k / c.compact; dyn(st, rigid ? 0 : r0, c.mu * 3, (c.anneal ? 0.015 : 0.008) * (1 - u), true); if (st.sym) symmetrize(st); rec(); }
  st.log.push({ phase: st.phase, L: st.L });
  st.phase = rigid ? 'hold (rigid)' : 'morph ball->solid';
  for (let k = 0; k < c.morph; k++) { const u = k / c.morph; dyn(st, rigid ? 0 : r0 * (1 - u), c.mu, c.anneal ? 0.004 * (1 - u) : 0, true); if (st.sym) symmetrize(st); rec(); }
  st.log.push({ phase: st.phase, L: st.L });
  st.phase = 'rigid settle';
  for (let k = 0; k < c.settle; k++) { dyn(st, 0, c.mu * Math.pow(1e-4, k / c.settle), 0, true); if (st.sym) symmetrize(st); rec(); }
  st.log.push({ phase: st.phase, L: st.L });
  st.phase = 'final'; snap(st);
  const leg = legalize(pb, st.C, st.Q);
  st.frames.push({ ph: 'certified', r: 0, L: +leg.L.toFixed(6), s: st.step, p: leg.C.flatMap((p, i) => [...p.map(v => +v.toFixed(5)), ...leg.Q[i].map(v => +v.toFixed(6))]) });
  return { cfg: c, s: leg.s, L: leg.L, Lsoft: st.L, scale: leg.k, frames: st.frames, log: st.log, final: leg, edge: pb.P.edge };
}

// ---------------------------------------------------------------- basin hopping
// Relative-arrangement change between two states of the SAME pieces (identities tracked): RMS change of the centre
// distances of all pairs that were neighbours (distance < 2 x circumradius) in either state, in units of the piece edge.
function arrangementChange(pb, C0, C1, scale1, focus) {
  const n = C0.length, R2 = (2 * pb.P.circ) ** 2;
  let sum = 0, cnt = 0;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
    if (focus && !focus[i] && !focus[j]) continue;          // focused hop: only pairs touching the shaken cluster
    const d0 = (C0[i][0] - C0[j][0]) ** 2 + (C0[i][1] - C0[j][1]) ** 2 + (C0[i][2] - C0[j][2]) ** 2;
    const d1 = ((C1[i][0] - C1[j][0]) ** 2 + (C1[i][1] - C1[j][1]) ** 2 + (C1[i][2] - C1[j][2]) ** 2) * scale1 * scale1;
    if (d0 > R2 && d1 > R2) continue;
    sum += (Math.sqrt(d1) - Math.sqrt(d0)) ** 2; cnt++;
  }
  return cnt ? Math.sqrt(sum / cnt) / pb.P.edge : 0;
}

// Best hole: among random points of the container (kept 0.5 inside every wall), the one farthest from all centres.
function bestHole(pb, C, L, rng, tries) {
  const Rc = (L / 2) * Math.max(...pb.C.V.map(v => Math.hypot(...v))) / pb.rhoC;
  let best = null, bd = -1;
  for (let t = 0; t < tries; t++) {
    const p = [(2 * rng() - 1) * Rc, (2 * rng() - 1) * Rc, (2 * rng() - 1) * Rc];
    if (!pb.C.N.every((N, f) => G.dot(N, p) <= (L / 2) * pb.off[f] - 0.5)) continue;
    let m = Infinity;
    for (const c of C) m = Math.min(m, (c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2 + (c[2] - p[2]) ** 2);
    if (m > bd) { bd = m; best = p; }
  }
  return best || [0, 0, 0];
}

// One hop from a rigid packing (C, Q, L), in internal units with the container centred at the origin:
//  1. remove the pieces listed in `remove`, scale everything by (1 + expand) (and by ((n+add)/n)^(1/3) when adding),
//     put `add` new pieces into the largest holes;
//  2. soften the pieces to S_rh (they shrink inside their rigid shapes, Lemma 1) and shake them at fixed container
//     size with noise until the relative arrangement has changed by at least minDiff piece edges (escalating the
//     noise and the softness each block), or maxEsc blocks;
//  3. re-sharpen under pressure (r: rh -> 0 over `morph` steps), settle rigid pieces, legalize.
function hop(c) {
  c = Object.assign({ expand: 0.03, rh: 0.12, noise: 0.004, shake: 400, morph: 6000, settle: 1500, mu: 0.02, minDiff: 0.15,
    maxEsc: 8, add: 0, remove: [], seed: 1, focus: 0 }, c);
  const pb = makeProblem(c.piece, c.container);
  const rng = mulberry32((c.seed * 7919 + 17) | 0);
  const keep = c.C.map((_, i) => i).filter(i => !c.remove.includes(i));
  let C = keep.map(i => c.C[i].slice()), Q = keep.map(i => c.Q[i].slice());
  const n0 = C.length, add = c.add | 0;
  const f = (1 + c.expand) * (add ? Math.cbrt((n0 + add) / n0) : 1);
  C = C.map(p => p.map(x => x * f));
  let L = c.L * f;
  const ref = C.map(p => p.slice());           // arrangement before shaking (already scaled)
  for (let a = 0; a < add; a++) {
    C.push(bestHole(pb, C, L, rng, 4000));
    const q = [gauss(rng), gauss(rng), gauss(rng), gauss(rng)], m = Math.hypot(...q); Q.push(q.map(v => v / m));
  }
  const n = C.length;
  const st = { pb, n, rng, L, vL: 0, r: c.rh, step: 0, phase: 'hop', frames: [], log: [], C, Q,
    V: C.map(() => [0, 0, 0]), W: C.map(() => [0, 0, 0]), hints: new Map() };
  // focus: shake only a cluster (a random piece and its focus-1 nearest neighbours); the rest gets 15% of the noise
  let focusSet = null;
  if (c.focus && c.focus < ref.length) {
    const i0 = Math.floor(rng() * ref.length);
    const order = ref.map((p, i) => [(p[0] - ref[i0][0]) ** 2 + (p[1] - ref[i0][1]) ** 2 + (p[2] - ref[i0][2]) ** 2, i]).sort((a, b) => a[0] - b[0]);
    focusSet = new Array(n).fill(false);
    for (let t = 0; t < c.focus; t++) focusSet[order[t][1]] = true;
    for (let i = ref.length; i < n; i++) focusSet[i] = true;
    st.mask = focusSet.map(f => (f ? 1 : 0.15));
  }
  let noise = c.noise, rh = c.rh, esc = 0, diff = 0;
  const structural = add > 0 || c.remove.length > 0;
  for (;;) {
    for (let k = 0; k < c.shake; k++) dyn(st, rh, 0, noise, false);
    diff = arrangementChange(pb, ref, st.C.slice(0, ref.length), 1, focusSet);
    if (structural || diff >= c.minDiff || esc >= c.maxEsc) break;
    esc++; noise *= 1.5; rh = Math.min(0.4, rh * 1.3);
  }
  const noise0 = noise * 0.25;
  for (let k = 0; k < c.morph; k++) { const u = k / c.morph; dyn(st, rh * (1 - u), c.mu, noise0 * (1 - u), true); }
  for (let k = 0; k < c.settle; k++) dyn(st, 0, c.mu * Math.pow(1e-4, k / c.settle), 0, true);
  const leg = legalize(pb, st.C, st.Q);
  st.mask = null;
  return { n, s: leg.s, L: leg.L, C: leg.C, Q: leg.Q, diff, esc, rh, noise, steps: st.step, edge: pb.P.edge };
}


// ---------------------------------------------------------------- fixed-size separation below the record (experimental)
// sparrow / HAMSP style: shrink the container by delta, then remove all overlap at FIXED size by weighted overlap
// descent (guided-local-search pair weights grow while a pair keeps colliding) and occasional relocation of the worst
// piece to the best of many sampled poses. Success = no overlap at the smaller size.
function squeeze(c) {
  c = Object.assign({ delta: 0.003, r: 0, rounds: 60, steps: 120, relocEvery: 5, samples: 300, seed: 1 }, c);
  const pb = makeProblem(c.piece, c.container);
  const rng = mulberry32((c.seed * 7919 + 29) | 0);
  const f = 1 - c.delta;
  const st = { pb, n: c.C.length, rng, L: c.L * f, vL: 0, r: c.r, step: 0, phase: 'squeeze', frames: [], log: [],
    C: c.C.map(p => p.map(x => x * f)), Q: c.Q.map(q => q.slice()), V: c.C.map(() => [0, 0, 0]), W: c.C.map(() => [0, 0, 0]),
    hints: new Map(), wp: new Map(), ov: new Map() };
  const n = st.n, P = pb.P, Rc = (st.L / 2) * Math.max(...pb.C.V.map(v => Math.hypot(...v))) / pb.rhoC;
  let ok = false, round = 0, best = Infinity, bestC = null, bestQ = null;
  for (; round < c.rounds; round++) {
    for (let k = 0; k < c.steps; k++) dyn(st, c.r, 0, 0, false);
    let omax = 0, tot = 0;
    for (const o of st.ov.values()) { omax = Math.max(omax, o); tot += o; }
    let qmax = 0; for (let i = 0; i < n; i++) { qmax = Math.max(qmax, st.wq[i]); tot += st.wq[i]; }
    if (tot < best) { best = tot; bestC = st.C.map(p => p.slice()); bestQ = st.Q.map(q => q.slice()); }
    if (omax < 1e-9 && qmax < 1e-9) { ok = true; break; }
    for (const [key, w] of st.wp) if (!st.ov.has(key)) { const w2 = Math.max(1, 0.95 * w); if (w2 === 1) st.wp.delete(key); else st.wp.set(key, w2); }
    for (const [key, o] of st.ov) st.wp.set(key, (st.wp.get(key) || 1) * (1.2 + 0.8 * o / Math.max(omax, 1e-12)));
    if (round % c.relocEvery === c.relocEvery - 1) {
      const score = new Float64Array(n);
      for (const [key, o] of st.ov) { const i = Math.floor(key / n), j = key % n, w = st.wp.get(key) || 1; score[i] += w * o; score[j] += w * o; }
      for (let i = 0; i < n; i++) score[i] += 10 * st.wq[i];
      let i0 = 0; for (let i = 1; i < n; i++) if (score[i] > score[i0]) i0 = i;
      const others = [];
      for (let j = 0; j < n; j++) if (j !== i0) others.push([j, G.pose(P, st.C[j], st.Q[j], 1)]);
      const energy = (cc, qq) => {
        const A = G.pose(P, cc, qq, 1); let e = 0;
        for (let f2 = 0; f2 < pb.C.N.length; f2++) {
          const N = pb.C.N[f2]; let m = -Infinity;
          for (let v = 0; v < P.nv; v++) m = Math.max(m, A.X[3 * v] * N[0] + A.X[3 * v + 1] * N[1] + A.X[3 * v + 2] * N[2]);
          const q = m - (st.L / 2) * pb.off[f2]; if (q > 0) e += 10 * q * q;
        }
        const lim = (2 * P.circ) ** 2;
        for (const [j, B] of others) {
          const d2 = (cc[0] - st.C[j][0]) ** 2 + (cc[1] - st.C[j][1]) ** 2 + (cc[2] - st.C[j][2]) ** 2;
          if (d2 > lim) continue;
          const sd = G.sdCores(A, B, 0, false);
          if (sd < 0) { const key = i0 < j ? i0 * n + j : j * n + i0; e += (st.wp.get(key) || 1) * sd * sd; }
        }
        return e;
      };
      let bc = st.C[i0], bq = st.Q[i0], be = energy(bc, bq);
      for (let t = 0; t < c.samples; t++) {
        let cc, qq;
        if (t % 2 === 0) {
          for (let tries = 0; tries < 1000; tries++) {
            cc = [(2 * rng() - 1) * Rc, (2 * rng() - 1) * Rc, (2 * rng() - 1) * Rc];
            if (pb.C.N.every((N, f2) => G.dot(N, cc) <= (st.L / 2) * pb.off[f2] - 0.5)) break;
          }
          const q = [gauss(rng), gauss(rng), gauss(rng), gauss(rng)], m = Math.hypot(...q); qq = q.map(v => v / m);
        } else {
          cc = st.C[i0].map(x => x + 0.15 * gauss(rng));
          qq = G.rotq(st.Q[i0], 0.2 * gauss(rng), 0.2 * gauss(rng), 0.2 * gauss(rng));
        }
        const e = energy(cc, qq);
        if (e < be) { be = e; bc = cc; bq = qq; }
      }
      st.C[i0] = bc.slice(); st.Q[i0] = bq.slice(); st.V[i0] = [0, 0, 0]; st.W[i0] = [0, 0, 0]; st.hints.clear();
    }
  }
  const leg = ok ? legalize(pb, st.C, st.Q) : legalize(pb, bestC, bestQ);
  return { n, s: leg.s, L: leg.L, C: leg.C, Q: leg.Q, ok, rounds: round, edge: pb.P.edge };
}

module.exports = { run, hop, squeeze, makeProblem, softShape, legalize, tightContainer, lpTranslation, defaultL0, dyn, makeState, arrangementChange };
