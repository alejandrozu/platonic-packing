// Convex-polytope geometry for the soft-to-rigid packer: signed distance between two rounded polytopes' cores
// (exact penetration depth by the separating-axis theorem when they overlap, exact Euclidean distance by
// feature enumeration when they are apart) with analytic gradients w.r.t. both centres and both world-frame
// rotation vectors.
//
// Conventions. A piece is (c, R, k): its core is c + k R P, where P is the solid (scaled so its inradius is 1/2)
// and k = 1 - 2r is the core scale of the rounded shape kP (+) B(r). R is row-major 3x3, world = R * local.
'use strict';
const SOLIDS = require('./solids.json');

// ---------------------------------------------------------------- shapes
// scale: multiply unit-edge coordinates by this (default: make inradius 1/2)
function prepShape(name, scale) {
  const S = SOLIDS[name];
  if (!S) throw new Error('unknown solid ' + name);
  if (scale === undefined) scale = 0.5 / S.inradius;
  const V = S.V.map(v => v.map(x => x * scale));
  const nv = V.length;
  const N = S.normals;
  const beta = S.faces.map((f, i) => N[i][0] * V[f[0]][0] + N[i][1] * V[f[0]][1] + N[i][2] * V[f[0]][2]);
  const uniq = (list) => {
    const out = [];
    for (const u of list) if (!out.some(w => Math.abs(u[0] * w[0] + u[1] * w[1] + u[2] * w[2]) > 1 - 1e-9)) out.push(u);
    return out;
  };
  const faxes = uniq(N);
  const edirs = uniq(S.edges.map(([i, j]) => {
    const d = [V[j][0] - V[i][0], V[j][1] - V[i][1], V[j][2] - V[i][2]], l = Math.hypot(...d);
    return d.map(x => x / l);
  }));
  // per face: edges as (p, m) with m the inward in-plane unit normal  (CCW loop seen from outside: m = n x (q - p))
  const fedges = S.faces.map((f, fi) => f.map((a, t) => {
    const b = f[(t + 1) % f.length], n = N[fi], p = V[a], q = V[b];
    const e = [q[0] - p[0], q[1] - p[1], q[2] - p[2]];
    const m = [n[1] * e[2] - n[2] * e[1], n[2] * e[0] - n[0] * e[2], n[0] * e[1] - n[1] * e[0]], l = Math.hypot(...m);
    return { p, m: m.map(x => x / l) };
  }));
  const circ = Math.max(...V.map(v => Math.hypot(...v)));
  return {
    name, scale, V, nv, faces: S.faces, N, beta, faxes, edirs, fedges, edges: S.edges, circ,
    inradius: S.inradius * scale, edge: scale, volume: S.volume * scale ** 3,
  };
}

// ---------------------------------------------------------------- rotations
function quatToR(q) {
  const [w, x, y, z] = q;
  return [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y),
    2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x),
    2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)];
}
// q <- exp(omega) q  (world-frame rotation vector)
function rotq(q, wx, wy, wz) {
  const th = Math.hypot(wx, wy, wz);
  if (th < 1e-16) return q;
  const h = th / 2, sh = Math.sin(h) / th;
  const dw = Math.cos(h), dx = wx * sh, dy = wy * sh, dz = wz * sh;
  const [w, x, y, z] = q;
  const r = [dw * w - dx * x - dy * y - dz * z, dw * x + dx * w + dy * z - dz * y, dw * y - dx * z + dy * w + dz * x, dw * z + dx * y - dy * x + dz * w];
  const m = Math.hypot(r[0], r[1], r[2], r[3]);
  return [r[0] / m, r[1] / m, r[2] / m, r[3] / m];
}

// world data for one piece: centre, rotation, core scale, world vertices, world face axes, world edge dirs
function pose(shape, c, q, k) {
  const R = quatToR(q);
  const X = new Float64Array(3 * shape.nv);
  for (let i = 0; i < shape.nv; i++) {
    const v = shape.V[i];
    X[3 * i] = c[0] + k * (R[0] * v[0] + R[1] * v[1] + R[2] * v[2]);
    X[3 * i + 1] = c[1] + k * (R[3] * v[0] + R[4] * v[1] + R[5] * v[2]);
    X[3 * i + 2] = c[2] + k * (R[6] * v[0] + R[7] * v[1] + R[8] * v[2]);
  }
  const rot = u => [R[0] * u[0] + R[1] * u[1] + R[2] * u[2], R[3] * u[0] + R[4] * u[1] + R[5] * u[2], R[6] * u[0] + R[7] * u[1] + R[8] * u[2]];
  return { shape, c, R, k, X, FA: shape.faxes.map(rot), ED: shape.edirs.map(rot) };
}

// ---------------------------------------------------------------- small vector helpers
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const vx = (X, i) => [X[3 * i], X[3 * i + 1], X[3 * i + 2]];

// projection of a vertex array on u: sets PR = [min, max, argmin, argmax]
const PR = [0, 0, 0, 0];
function proj(X, n, u0, u1, u2) {
  let mn = Infinity, mx = -Infinity, imn = 0, imx = 0;
  for (let i = 0, j = 0; i < n; i++, j += 3) {
    const p = X[j] * u0 + X[j + 1] * u1 + X[j + 2] * u2;
    if (p < mn) { mn = p; imn = i; }
    if (p > mx) { mx = p; imx = i; }
  }
  PR[0] = mn; PR[1] = mx; PR[2] = imn; PR[3] = imx;
}

// closest points between segments p1q1, p2q2 (Ericson, Real-Time Collision Detection 5.1.9)
function segClosest(p1, q1, p2, q2) {
  const d1 = sub(q1, p1), d2 = sub(q2, p2), r = sub(p1, p2);
  const a = dot(d1, d1), e = dot(d2, d2), f = dot(d2, r);
  const c = dot(d1, r), b = dot(d1, d2), den = a * e - b * b;
  let s = den > 1e-14 * a * e ? Math.min(1, Math.max(0, (b * f - c * e) / den)) : 0;
  let t = (b * s + f) / e;
  if (t < 0) { t = 0; s = Math.min(1, Math.max(0, -c / a)); }
  else if (t > 1) { t = 1; s = Math.min(1, Math.max(0, (b - c) / a)); }
  return [[p1[0] + d1[0] * s, p1[1] + d1[1] * s, p1[2] + d1[2] * s], [p2[0] + d2[0] * t, p2[1] + d2[1] * t, p2[2] + d2[2] * t]];
}

// allocation-free version of segClosest on flat vertex arrays: segment X1[a]-X1[b] vs X2[c]-X2[e];
// writes the two closest points into out[0..5] and returns their squared distance
const SEG = new Float64Array(6);
function segDist2(X1, a, b, X2, c, e, out) {
  const p1x = X1[a], p1y = X1[a + 1], p1z = X1[a + 2], p2x = X2[c], p2y = X2[c + 1], p2z = X2[c + 2];
  const d1x = X1[b] - p1x, d1y = X1[b + 1] - p1y, d1z = X1[b + 2] - p1z;
  const d2x = X2[e] - p2x, d2y = X2[e + 1] - p2y, d2z = X2[e + 2] - p2z;
  const rx = p1x - p2x, ry = p1y - p2y, rz = p1z - p2z;
  const A = d1x * d1x + d1y * d1y + d1z * d1z, E = d2x * d2x + d2y * d2y + d2z * d2z, F = d2x * rx + d2y * ry + d2z * rz;
  const C = d1x * rx + d1y * ry + d1z * rz, Bq = d1x * d2x + d1y * d2y + d1z * d2z, den = A * E - Bq * Bq;
  let s = den > 1e-14 * A * E ? Math.min(1, Math.max(0, (Bq * F - C * E) / den)) : 0;
  let t = (Bq * s + F) / E;
  if (t < 0) { t = 0; s = Math.min(1, Math.max(0, -C / A)); }
  else if (t > 1) { t = 1; s = Math.min(1, Math.max(0, (Bq - C) / A)); }
  out[0] = p1x + d1x * s; out[1] = p1y + d1y * s; out[2] = p1z + d1z * s;
  out[3] = p2x + d2x * t; out[4] = p2y + d2y * t; out[5] = p2z + d2z * t;
  const qx = out[0] - out[3], qy = out[1] - out[4], qz = out[2] - out[5];
  return qx * qx + qy * qy + qz * qz;
}

// ---------------------------------------------------------------- signed distance between cores
// Returns sd (< 0: penetration depth by SAT; > 0: Euclidean distance) and fills GR with
// d sd / d [cA(3), wA(3), cB(3), wB(3)]. If some axis already separates by >= cutoff, returns that lower bound
// (> 0, no gradient). STAT records which branch ran.
const GR = new Float64Array(12);
const STAT = { sat: 0, dist: 0, far: 0, feat: 0 };

function sdCores(A, B, cutoff, needGrad) {
  if (cutoff === undefined) cutoff = Infinity;
  if (needGrad === undefined) needGrad = true;
  const SA = A.shape, SB = B.shape, k = A.k;
  if (k <= 1e-12) { // cores are points
    const D = sub(A.c, B.c), d = Math.hypot(...D) || 1e-300;
    GR.fill(0); for (let t = 0; t < 3; t++) { GR[t] = D[t] / d; GR[6 + t] = -D[t] / d; }
    return d;
  }
  let minO = Infinity, best = null, sepGap = -Infinity, sepU = null;
  // test one axis; returns true if it separates
  const test = (u, kind, ia, ib, w, l) => {
    proj(A.X, SA.nv, u[0], u[1], u[2]); const aMin = PR[0], aMax = PR[1], aiMin = PR[2], aiMax = PR[3];
    proj(B.X, SB.nv, u[0], u[1], u[2]); const bMin = PR[0], bMax = PR[1], biMin = PR[2], biMax = PR[3];
    const o1 = aMax - bMin, o2 = bMax - aMin;   // o1: A below B along u ; o2: A above B
    if (o1 <= 0 || o2 <= 0) {
      const gap = o1 <= 0 ? -o1 : -o2;
      if (gap > sepGap) { sepGap = gap; sepU = o1 <= 0 ? u : [-u[0], -u[1], -u[2]]; }
      return true;
    }
    const o = Math.min(o1, o2);
    if (o < minO) {
      minO = o;
      best = o1 <= o2 ? { u, sg: 1, ia: aiMax, ib: biMin, kind, i: ia, j: ib, w, l }
        : { u: [-u[0], -u[1], -u[2]], sg: -1, ia: aiMin, ib: biMax, kind, i: ia, j: ib, w, l };
    }
    return false;
  };
  let sep = false;
  for (let i = 0; i < A.FA.length; i++) if (test(A.FA[i], 'A', i)) sep = true;
  for (let i = 0; i < B.FA.length; i++) if (test(B.FA[i], 'B', i)) sep = true;
  if (!sep) {
    for (let i = 0; i < A.ED.length && !sep; i++) for (let j = 0; j < B.ED.length; j++) {
      const w = cross(A.ED[i], B.ED[j]), l = Math.hypot(w[0], w[1], w[2]);
      if (l < 1e-9) continue;
      if (test([w[0] / l, w[1] / l, w[2] / l], 'X', i, j, w, l)) { sep = true; break; }
    }
  }
  if (sep) {
    if (sepGap >= cutoff) { STAT.far++; return sepGap; }
    STAT.dist++;
    return distSeparated(A, B, sepU, sepGap, needGrad);
  }
  STAT.sat++;
  if (!needGrad) return -minO;
  // penetration o = h_A(u) + h_B(-u) along the oriented best axis u; sd = -o
  const u = best.u, pa = vx(A.X, best.ia), pb = vx(B.X, best.ib);
  const g = sub(pa, pb);
  let dA = cross(sub(pa, A.c), u), dB = cross(sub(pb, B.c), u); dB = [-dB[0], -dB[1], -dB[2]];
  if (best.kind === 'A') { const t = cross(u, g); dA = [dA[0] + t[0], dA[1] + t[1], dA[2] + t[2]]; }
  else if (best.kind === 'B') { const t = cross(u, g); dB = [dB[0] + t[0], dB[1] + t[1], dB[2] + t[2]]; }
  else {
    const a = A.ED[best.i], b = B.ED[best.j], ug = dot(u, g);
    const h = [best.sg * (g[0] - u[0] * ug) / best.l, best.sg * (g[1] - u[1] * ug) / best.l, best.sg * (g[2] - u[2] * ug) / best.l];
    const tA = cross(a, cross(b, h)), tB = cross(b, cross(h, a));
    dA = [dA[0] + tA[0], dA[1] + tA[1], dA[2] + tA[2]]; dB = [dB[0] + tB[0], dB[1] + tB[1], dB[2] + tB[2]];
  }
  for (let t = 0; t < 3; t++) { GR[t] = -u[t]; GR[3 + t] = -dA[t]; GR[6 + t] = u[t]; GR[9 + t] = -dB[t]; }
  return -minO;
}

// Exact distance between disjoint cores. u: unit axis with max_A u.x + gap <= min_B u.x (gap > 0).
// The closest pair lies in the slabs  u.x >= h_A - delta (on A)  and  u.x <= m_B + delta (on B),  delta = D - gap,
// where D is any upper bound on the distance; every candidate feature pair touching the slabs is enumerated:
// vertex-of-A / face-of-B (projection inside the face), face-of-A / vertex-of-B, edge-of-A / edge-of-B (segments).
function distSeparated(A, B, u, gap, needGrad) {
  const SA = A.shape, SB = B.shape, k = A.k;
  const pa_ = new Float64Array(SA.nv), pb_ = new Float64Array(SB.nv);
  let hA = -Infinity, mB = Infinity, ia = 0, ib = 0;
  for (let i = 0; i < SA.nv; i++) { const p = A.X[3 * i] * u[0] + A.X[3 * i + 1] * u[1] + A.X[3 * i + 2] * u[2]; pa_[i] = p; if (p > hA) { hA = p; ia = i; } }
  for (let i = 0; i < SB.nv; i++) { const p = B.X[3 * i] * u[0] + B.X[3 * i + 1] * u[1] + B.X[3 * i + 2] * u[2]; pb_[i] = p; if (p < mB) { mB = p; ib = i; } }
  let PA = vx(A.X, ia), PB = vx(B.X, ib);
  let d2 = (PA[0] - PB[0]) ** 2 + (PA[1] - PB[1]) ** 2 + (PA[2] - PB[2]) ** 2;
  const delta = Math.sqrt(d2) - (mB - hA) + 1e-12 * (1 + Math.sqrt(d2));
  const thA = hA - delta, thB = mB + delta;
  const consider = (p, q) => { const dd = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2; if (dd < d2) { d2 = dd; PA = p; PB = q; } };
  // vertex of X (world point x) against faces of polytope Y lying in Y's slab; returns closest point on Y or null
  const vertFace = (x, Y, faceOK) => {
    const SY = Y.shape, R = Y.R, kk = Y.k;
    const dx = x[0] - Y.c[0], dy = x[1] - Y.c[1], dz = x[2] - Y.c[2];
    const y = [(R[0] * dx + R[3] * dy + R[6] * dz) / kk, (R[1] * dx + R[4] * dy + R[7] * dz) / kk, (R[2] * dx + R[5] * dy + R[8] * dz) / kk];
    let bestq = null, bestt = Infinity;
    for (let f = 0; f < SY.faces.length; f++) {
      if (!faceOK[f]) continue;
      const n = SY.N[f], t = dot(n, y) - SY.beta[f];
      if (t <= 0 || t >= bestt) continue;
      let inside = true;
      for (const e of SY.fedges[f]) if ((y[0] - e.p[0]) * e.m[0] + (y[1] - e.p[1]) * e.m[1] + (y[2] - e.p[2]) * e.m[2] < 0) { inside = false; break; }
      if (!inside) continue;
      bestt = t; const nw = [R[0] * n[0] + R[1] * n[1] + R[2] * n[2], R[3] * n[0] + R[4] * n[1] + R[5] * n[2], R[6] * n[0] + R[7] * n[1] + R[8] * n[2]];
      bestq = [x[0] - kk * t * nw[0], x[1] - kk * t * nw[1], x[2] - kk * t * nw[2]];
    }
    return bestq;
  };
  const fA = SA.faces.map(f => f.some(i => pa_[i] >= thA)), fB = SB.faces.map(f => f.some(i => pb_[i] <= thB));
  for (let i = 0; i < SA.nv; i++) if (pa_[i] >= thA) { const x = vx(A.X, i), q = vertFace(x, B, fB); if (q) consider(x, q); }
  for (let i = 0; i < SB.nv; i++) if (pb_[i] <= thB) { const x = vx(B.X, i), q = vertFace(x, A, fA); if (q) consider(q, x); }
  // the vertex-face candidates gave a better upper bound D; the slab argument holds for any D >= d, so re-slab
  const delta2 = Math.sqrt(d2) - (mB - hA) + 1e-12 * (1 + Math.sqrt(d2));
  const thA2 = hA - delta2, thB2 = mB + delta2;
  const eA = SA.edges.filter(([i, j]) => pa_[i] >= thA2 || pa_[j] >= thA2), eB = SB.edges.filter(([i, j]) => pb_[i] <= thB2 || pb_[j] <= thB2);
  const XA = A.X, XB = B.X, halfSum = 0.5 * k * (SA.edge + SB.edge) * (1 + 1e-12);
  for (const [i1, j1] of eA) {
    const a = 3 * i1, b = 3 * j1;
    const mx1 = 0.5 * (XA[a] + XA[b]), my1 = 0.5 * (XA[a + 1] + XA[b + 1]), mz1 = 0.5 * (XA[a + 2] + XA[b + 2]);
    for (const [i2, j2] of eB) {
      const c = 3 * i2, e = 3 * j2;
      // segment distance >= |m1 - m2| - (l1 + l2)/2 : skip pairs that cannot be strictly closer than the best so far
      const ex = mx1 - 0.5 * (XB[c] + XB[e]), ey = my1 - 0.5 * (XB[c + 1] + XB[e + 1]), ez = mz1 - 0.5 * (XB[c + 2] + XB[e + 2]);
      const lb = Math.sqrt(d2) + halfSum;
      if (ex * ex + ey * ey + ez * ez >= lb * lb) continue;
      STAT.feat++;
      const dd = segDist2(XA, a, b, XB, c, e, SEG);
      if (dd < d2) { d2 = dd; PA = [SEG[0], SEG[1], SEG[2]]; PB = [SEG[3], SEG[4], SEG[5]]; }
    }
  }
  const d = Math.sqrt(d2) || 1e-300;
  if (needGrad) {
    const n = [(PA[0] - PB[0]) / d, (PA[1] - PB[1]) / d, (PA[2] - PB[2]) / d];
    const tA = cross(sub(PA, A.c), n), tB = cross(sub(PB, B.c), n);
    for (let t = 0; t < 3; t++) { GR[t] = n[t]; GR[3 + t] = tA[t]; GR[6 + t] = -n[t]; GR[9 + t] = -tB[t]; }
  }
  distSeparated.last = { PA, PB };
  return d;
}

// boolean SAT overlap test on full pieces (true if interiors overlap by more than tol along every axis)
function overlaps(A, B, tol) {
  const SA = A.shape, SB = B.shape;
  const chk = u => {
    proj(A.X, SA.nv, u[0], u[1], u[2]); const aMin = PR[0], aMax = PR[1];
    proj(B.X, SB.nv, u[0], u[1], u[2]);
    return Math.min(aMax - PR[0], PR[1] - aMin) > tol;
  };
  for (const u of A.FA) if (!chk(u)) return false;
  for (const u of B.FA) if (!chk(u)) return false;
  for (const a of A.ED) for (const b of B.ED) {
    const w = cross(a, b), l = Math.hypot(...w);
    if (l < 1e-9) continue;
    if (!chk([w[0] / l, w[1] / l, w[2] / l])) return false;
  }
  return true;
}

module.exports = { SOLIDS, prepShape, quatToR, rotq, pose, sdCores, distSeparated, overlaps, GR, STAT, segClosest, dot, cross, sub };
