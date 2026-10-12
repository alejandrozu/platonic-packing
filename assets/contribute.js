// Contribute page: floating-point checker for pasted packings (any piece/container pair of the solid library),
// 3D preview, and pre-filled GitHub issues for packing submissions, category proposals and other constructions.
// The proof-grade check runs on GitHub (scripts/check_submission.py -> certify_general.py) after submission.
(async () => {
  const $ = id => document.getElementById(id);
  const ROOT = document.documentElement.dataset.root || './';
  const REPO = document.documentElement.dataset.repo;
  const RAW = REPO.replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/main/';
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  let D;
  try { D = await (await fetch(ROOT + 'data/records.json')).json() }
  catch (e) { $('result').innerHTML = '<p class="mut">The solid library did not load. Reload the page to use the checker.</p>'; return }

  const POLY = { 3: 'triangular', 4: 'square', 5: 'pentagonal', 6: 'hexagonal', 8: 'octagonal', 12: 'dodecagonal' };
  const dn = s => { const m = /^(anti)?prism(\d+)$/.exec(s); return m ? `${POLY[m[2]]} ${m[1] ? 'antiprism' : 'prism'}` : s.replace(/_/g, ' ') };
  const names = Object.keys(D.solids).sort((a, b) => dn(a).localeCompare(dn(b)));
  $('names').innerHTML = names.map(n => `<code>${n}</code>`).join(', ');

  // ---------- selects
  const FAMS = [['platonic', 'Platonic'], ['archimedean', 'Archimedean'], ['catalan', 'Catalan'], ['prisms', 'Prisms and antiprisms']];
  const ps = $('prob');
  FAMS.forEach(([f, label]) => {
    const g = document.createElement('optgroup'); g.label = label;
    D.problems.filter(p => p.family === f).forEach(p => { const o = document.createElement('option'); o.value = p.id; o.textContent = p.title; g.appendChild(o) });
    ps.appendChild(g);
  });
  const other = document.createElement('option'); other.value = '_pair'; other.textContent = 'Another pair of solids'; ps.appendChild(other);
  ['piece', 'container'].forEach(id => names.forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = dn(n); $(id).appendChild(o) }));
  $('container').value = 'cube';
  const hashP = D.problems.find(p => p.id === location.hash.slice(1).split('_')[0]);
  if (hashP) ps.value = hashP.id;
  ps.onchange = () => { $('pair').hidden = ps.value !== '_pair'; invalidate() };
  const current = () => ps.value === '_pair' ? { piece: $('piece').value, container: $('container').value } : D.problems.find(p => p.id === ps.value);
  ['piece', 'container'].forEach(id => $(id).onchange = invalidate);

  // ---------- geometry
  const solidCache = {};
  function prep(name) {
    if (solidCache[name]) return solidCache[name];
    const S = D.solids[name], V = S.V, N = [], B = [];
    S.F.forEach(f => {
      let nx = 0, ny = 0, nz = 0, cx = 0, cy = 0, cz = 0;
      f.forEach((a, i) => { const p = V[a], q = V[f[(i + 1) % f.length]];
        nx += (p[1] - q[1]) * (p[2] + q[2]); ny += (p[2] - q[2]) * (p[0] + q[0]); nz += (p[0] - q[0]) * (p[1] + q[1]); cx += p[0]; cy += p[1]; cz += p[2] });
      let l = Math.hypot(nx, ny, nz); nx /= l; ny /= l; nz /= l;
      if (nx * cx + ny * cy + nz * cz < 0) { nx = -nx; ny = -ny; nz = -nz }
      N.push([nx, ny, nz]); B.push(nx * V[f[0]][0] + ny * V[f[0]][1] + nz * V[f[0]][2]);
    });
    const dirs = [];
    S.E.forEach(([a, b]) => { const d = [V[b][0] - V[a][0], V[b][1] - V[a][1], V[b][2] - V[a][2]], l = Math.hypot(...d); d[0] /= l; d[1] /= l; d[2] /= l;
      if (!dirs.some(e => Math.hypot(e[1] * d[2] - e[2] * d[1], e[2] * d[0] - e[0] * d[2], e[0] * d[1] - e[1] * d[0]) < 1e-9)) dirs.push(d) });
    // unique face normals (parallel ones give the same axis)
    const fn = []; N.forEach(n => { if (!fn.some(m => Math.abs(m[0] * n[0] + m[1] * n[1] + m[2] * n[2]) > 1 - 1e-12)) fn.push(n) });
    return solidCache[name] = { V, N, B, dirs, fn, R: Math.max(...V.map(v => Math.hypot(...v))) };
  }
  function qR(q) {
    const l = Math.hypot(q[0], q[1], q[2], q[3]); if (!(l > 0)) return null;
    const [w, x, y, z] = q.map(v => v / l);
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]];
  }
  const mv = (R, v) => [R[0][0] * v[0] + R[0][1] * v[1] + R[0][2] * v[2], R[1][0] * v[0] + R[1][1] * v[1] + R[1][2] * v[2], R[2][0] * v[0] + R[2][1] * v[1] + R[2][2] * v[2]];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  function proj(X, u) { let lo = Infinity, hi = -Infinity; for (let k = 0; k < X.length; k += 3) { const t = X[k] * u[0] + X[k + 1] * u[1] + X[k + 2] * u[2]; if (t < lo) lo = t; if (t > hi) hi = t } return [lo, hi] }
  function gapAlong(Xi, Xj, u) {
    const l = Math.hypot(u[0], u[1], u[2]); if (l < 1e-12) return -Infinity;
    const a = proj(Xi, u), b = proj(Xj, u); return Math.max(b[0] - a[1], a[0] - b[1]) / l;
  }

  // ---------- parsing
  function parse() {
    const txt = $('json').value.trim(); if (!txt) throw new Error('Paste a packing first.');
    let obj; try { obj = JSON.parse(txt) } catch (e) { throw new Error('This is not valid JSON: ' + e.message) }
    if (Array.isArray(obj)) obj = { pieces: obj };
    if (!obj || !Array.isArray(obj.pieces)) throw new Error('The JSON needs a "pieces" list: one [x, y, z, qw, qx, qy, qz] per piece.');
    const cur = current();
    const piece = obj.piece || cur.piece, container = obj.container || cur.container;
    if (!D.solids[piece]) throw new Error(`Unknown piece solid "${piece}". Use one of the names listed under “Format of a packing”.`);
    if (!D.solids[container]) throw new Error(`Unknown container solid "${container}".`);
    if (obj.piece && obj.container && ps.value !== '_pair') {
      const p = D.problems.find(p => p.piece === obj.piece && p.container === obj.container);
      if (p && p.id !== ps.value) { ps.value = p.id; $('pair').hidden = true }
      else if (!p) { ps.value = '_pair'; $('pair').hidden = false; $('piece').value = piece; $('container').value = container }
    }
    const sTxt = $('sval').value.trim();
    const s = sTxt ? Number(sTxt) : Number(obj.s_full ?? obj.s);
    if (!(s > 0) || !isFinite(s)) throw new Error('No container scale: give "s_full" in the JSON or fill in s.');
    const pcs = obj.pieces;
    if (!pcs.length) throw new Error('The packing has no pieces.');
    if (pcs.length > 400) throw new Error('The checker takes at most 400 pieces.');
    pcs.forEach((p, i) => { if (!Array.isArray(p) || p.length !== 7 || !p.every(x => typeof x === 'number' && isFinite(x))) throw new Error(`Piece ${i + 1} is not a list of 7 numbers [x, y, z, qw, qx, qy, qz].`) });
    if (obj.n != null && obj.n !== pcs.length) throw new Error(`"n" is ${obj.n} but there are ${pcs.length} pieces.`);
    const cc = Array.isArray(obj.container_center) ? obj.container_center.map(Number) : [0, 0, 0];
    return { piece, container, s, cc, pcs, n: pcs.length };
  }

  // ---------- the check (floating point, separating axis test)
  async function check(pk) {
    const P = prep(pk.piece), C = prep(pk.container), n = pk.n;
    const Rs = pk.pcs.map(p => qR(p.slice(3)));
    const bad = Rs.findIndex(R => !R); if (bad >= 0) throw new Error(`Piece ${bad + 1} has a zero quaternion.`);
    const X = pk.pcs.map((p, i) => { const a = new Float64Array(P.V.length * 3); P.V.forEach((v, k) => { const w = mv(Rs[i], v); a[3 * k] = w[0] + p[0]; a[3 * k + 1] = w[1] + p[1]; a[3 * k + 2] = w[2] + p[2] }); return a });
    let sNeed = -Infinity, wall = Infinity, outside = new Set();
    X.forEach((A, i) => { for (let k = 0; k < A.length; k += 3) C.N.forEach((u, f) => {
      const t = u[0] * (A[k] - pk.cc[0]) + u[1] * (A[k + 1] - pk.cc[1]) + u[2] * (A[k + 2] - pk.cc[2]);
      sNeed = Math.max(sNeed, t / C.B[f]); const sl = pk.s * C.B[f] - t; wall = Math.min(wall, sl); if (sl <= 0) outside.add(i) }) });
    const lim = 2 * P.R * (1 + 1e-9), pairs = [];
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) { const c = pk.pcs[i], d = pk.pcs[j]; if (Math.hypot(c[0] - d[0], c[1] - d[1], c[2] - d[2]) < lim) pairs.push([i, j]) }
    const rotN = Rs.map(R => P.fn.map(u => mv(R, u))), rotE = Rs.map(R => P.dirs.map(u => mv(R, u)));
    let minGap = Infinity; const over = [];
    for (let k = 0; k < pairs.length; k++) {
      const [i, j] = pairs[k]; let best = -Infinity;
      for (const u of rotN[i]) best = Math.max(best, gapAlong(X[i], X[j], u));
      for (const u of rotN[j]) best = Math.max(best, gapAlong(X[i], X[j], u));
      if (!(best > 0)) for (const a of rotE[i]) { for (const b of rotE[j]) { best = Math.max(best, gapAlong(X[i], X[j], cross(a, b))); if (best > 0) break } if (best > 0) break }
      if (best > 0) minGap = Math.min(minGap, best); else over.push([i, j, -best]);
      if (k % 25 === 24) { $('busy').textContent = `Checking pairs: ${k + 1} of ${pairs.length}`; await new Promise(r => setTimeout(r)) }
    }
    return { X, sNeed, wall, outside, pairs: pairs.length, far: n * (n - 1) / 2 - pairs.length, minGap, over };
  }

  // ---------- preview (three.js)
  const pv = $('prev'), pcv = $('pcv');
  const hasGL = typeof THREE !== 'undefined' && (() => { try { return !!document.createElement('canvas').getContext('webgl') } catch (e) { return false } })();
  let R3, scene, cam, world, pR = 3;
  if (hasGL) {
    R3 = new THREE.WebGLRenderer({ canvas: pcv, antialias: true }); R3.setPixelRatio(Math.min(2, devicePixelRatio || 1));
    scene = new THREE.Scene(); cam = new THREE.PerspectiveCamera(32, 4 / 3, 0.01, 1000);
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const l1 = new THREE.DirectionalLight(0xffffff, 0.75); l1.position.set(3, 5, 6); scene.add(l1);
    world = new THREE.Group(); scene.add(world); world.quaternion.setFromEuler(new THREE.Euler(-0.5, 0.6, 0.05));
    let drag = null;
    pv.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY }; pv.setPointerCapture(e.pointerId) });
    pv.addEventListener('pointermove', e => { if (!drag) return; const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag = { x: e.clientX, y: e.clientY };
      world.quaternion.premultiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(dy * 0.01, dx * 0.01, 0))); paint() });
    ['pointerup', 'pointercancel'].forEach(t => pv.addEventListener(t, () => drag = null));
    new ResizeObserver(() => { fit(); paint() }).observe(pv);
  } else pv.innerHTML = '<p class="busy" style="padding:14px">The preview needs WebGL; the check itself still works.</p>';
  function fit() { if (!hasGL) return; const w = pv.clientWidth || 400, h = pv.clientHeight || 300; R3.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
    cam.position.set(0, 0, pR / Math.sin(THREE.MathUtils.degToRad(Math.min(16, THREE.MathUtils.radToDeg(Math.atan(Math.tan(THREE.MathUtils.degToRad(16)) * cam.aspect))))) * 1.05); cam.lookAt(0, 0, 0) }
  function paint() { if (!hasGL) return; scene.background = new THREE.Color(css('--paper')); R3.render(scene, cam) }
  function show(pk, res) {
    if (!hasGL) return;
    while (world.children.length) world.remove(world.children[0]);
    const C = D.solids[pk.container], P = D.solids[pk.piece];
    const cp = []; C.E.forEach(([a, b]) => cp.push(...C.V[a].map((x, k) => x * pk.s + pk.cc[k]), ...C.V[b].map((x, k) => x * pk.s + pk.cc[k])));
    const cg = new THREE.BufferGeometry(); cg.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3));
    world.add(new THREE.LineSegments(cg, new THREE.LineBasicMaterial({ color: new THREE.Color(css('--ink')) })));
    const pos = []; P.F.forEach(f => { for (let i = 1; i + 1 < f.length; i++) [f[0], f[i], f[i + 1]].forEach(k => pos.push(...P.V[k])) });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
    const ep = []; P.E.forEach(([a, b]) => ep.push(...P.V[a], ...P.V[b])); const eg = new THREE.BufferGeometry(); eg.setAttribute('position', new THREE.Float32BufferAttribute(ep, 3));
    const badSet = new Set(res ? [...res.over.flatMap(o => [o[0], o[1]]), ...res.outside] : []);
    pk.pcs.forEach((p, i) => {
      const grp = new THREE.Group();
      grp.add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: new THREE.Color(badSet.has(i) ? '#c8524a' : '#4c6fd6'), flatShading: true, roughness: 0.6, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 })));
      grp.add(new THREE.LineSegments(eg, new THREE.LineBasicMaterial({ color: 0x10181b, transparent: true, opacity: 0.5 })));
      grp.quaternion.copy(new THREE.Quaternion(p[4], p[5], p[6], p[3]).normalize()); grp.position.set(p[0], p[1], p[2]);
      world.add(grp);
    });
    pR = Math.max(...C.V.map(v => Math.hypot(...v))) * pk.s + Math.hypot(...pk.cc);
    fit(); paint();
  }

  // ---------- run the check
  let last = null;
  function invalidate() { last = null; $('send').disabled = true; $('sendnote').textContent = '' }
  $('json').addEventListener('input', invalidate); $('sval').addEventListener('input', invalidate);
  const fmt = (x, d = 10) => Number.isFinite(x) ? x.toPrecision(d) : '—';
  $('check').onclick = async () => {
    invalidate(); const out = $('result');
    let pk; try { pk = parse() } catch (e) { out.innerHTML = `<p class="verdict bad">Cannot check this yet</p><p>${esc(e.message)}</p>`; return }
    $('check').disabled = true; $('busy').textContent = 'Checking…'; show(pk, null);
    let res; try { res = await check(pk) } catch (e) { out.innerHTML = `<p class="verdict bad">Cannot check this yet</p><p>${esc(e.message)}</p>`; $('check').disabled = false; $('busy').textContent = ''; return }
    $('check').disabled = false; $('busy').textContent = '';
    show(pk, res);
    const ok = res.wall > 0 && !res.over.length;
    const prob = D.problems.find(p => p.piece === pk.piece && p.container === pk.container);
    const rec = prob && prob.rows.find(r => r.n === pk.n);
    let cmp = '';
    if (!ok) cmp = prob && rec ? `The current record is s = ${rec.sf}.` : '';
    else if (prob && rec) {
      const d = pk.s - rec.sf;
      cmp = d < -1e-12 ? `<b>Smaller than the current record</b> (s = ${rec.sf}) by ${fmt(-d, 6)}. Submit it.` :
            `The current record is s = ${rec.sf}${d > 0 ? `, ${fmt(d, 6)} smaller than this one` : ', the same size'}.`;
    } else if (prob) cmp = `There is no record for n = ${pk.n} yet, so a valid packing fills an empty case.`;
    else cmp = `${cap(dn(pk.piece))} in ${dn(pk.container)} is not a tracked problem yet. You can still submit it, or <a href="#category">propose the category</a>.`;
    const thin = ok && Math.min(res.wall, res.minGap) < 1e-12;
    out.innerHTML = `<p class="verdict ${ok ? 'ok' : 'bad'}">${ok ? (thin ? 'Valid, with almost no clearance' : 'Valid in floating point') : 'Not valid'}</p>` +
      `<dl><dt>Pieces</dt><dd>${pk.n} ${esc(dn(pk.piece))} in ${esc(dn(pk.container))}</dd><dt>s</dt><dd>${pk.s}</dd>` +
      `<dt>Smallest s for these positions</dt><dd>${fmt(res.sNeed, 14)}</dd><dt>Wall clearance</dt><dd>${fmt(res.wall, 4)}</dd>` +
      `<dt>Closest pair</dt><dd>${res.pairs ? (res.over.length ? `${res.over.length} overlapping pair${res.over.length > 1 ? 's' : ''}` : `separated by ≥ ${fmt(res.minGap, 4)}`) : 'no pieces close enough to touch'}</dd>` +
      `<dt>Pairs checked</dt><dd>${res.pairs} near, ${res.far} farther apart than two circumradii</dd></dl>` +
      (res.outside.size ? `<p>${res.outside.size} piece${res.outside.size > 1 ? 's reach' : ' reaches'} outside the container. Use s ≥ ${fmt(res.sNeed, 14)}, plus a little clearance.</p>` : '') +
      (res.over.length ? `<ul>${res.over.slice(0, 6).map(([i, j, d]) => `<li>pieces ${i + 1} and ${j + 1} overlap by ${fmt(d, 4)}</li>`).join('')}${res.over.length > 6 ? `<li>and ${res.over.length - 6} more</li>` : ''}</ul>` : '') +
      (thin ? '<p>The exact certifier needs strictly positive clearance; spread the pieces by about 10<sup>−7</sup> and round s up before submitting.</p>' : '') +
      `<p>${cmp}</p>`;
    if (ok) { last = pk; $('send').disabled = false }
  };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const cap = s => s[0].toUpperCase() + s.slice(1);

  // ---------- example: the current record, at full precision from GitHub
  $('loadrec').onclick = async () => {
    const p = current(); if (!p || !p.id) { $('busy').textContent = 'Pick a tracked problem to load its record.'; return }
    const r = p.rows.find(r => r.n === 12) || p.rows[p.rows.length - 1]; if (!r) return;
    $('busy').textContent = 'Loading the record…';
    try {
      const rec = await (await fetch(RAW + r.file)).json();
      $('json').value = JSON.stringify({ piece: rec.piece, container: rec.container, n: rec.n, s_full: rec.s_full, ...(rec.container_center ? { container_center: rec.container_center } : {}), pieces: rec.pieces }, null, 1);
      $('busy').textContent = `Loaded ${p.id}_n${String(r.n).padStart(2, '0')}. Check it, or change it and check again.`;
    } catch (e) {
      $('json').value = JSON.stringify({ piece: p.piece, container: p.container, n: r.n, s_full: r.sf, pieces: r.p }, null, 1);
      $('busy').textContent = 'GitHub did not answer, so this copy is rounded to 7 decimals and may show tiny overlaps.';
    }
    $('sval').value = ''; invalidate();
  };

  // ---------- GitHub issues
  function openIssue(template, title, fields, big) {
    const u = new URL(REPO + '/issues/new'); u.searchParams.set('template', template); u.searchParams.set('title', title);
    Object.entries(fields).forEach(([k, v]) => { if (v) u.searchParams.set(k, v) });
    let note = '';
    if (big && u.href.length + encodeURIComponent(big[1]).length < 7800) u.searchParams.set(big[0], big[1]);
    else if (big) { try { navigator.clipboard.writeText(big[1]) } catch (e) {} note = 'The packing is too long for a link, so it was copied to your clipboard: paste it into the Packing box of the issue.' }
    window.open(u.href, '_blank', 'noopener');
    return note;
  }
  $('send').onclick = () => {
    if (!last) return;
    const pk = last, prob = D.problems.find(p => p.piece === pk.piece && p.container === pk.container);
    const rec = { piece: pk.piece, container: pk.container, n: pk.n, s_full: pk.s, ...(pk.cc.some(x => x) ? { container_center: pk.cc } : {}), pieces: pk.pcs };
    const json = JSON.stringify(rec);
    const pid = prob ? prob.id : `${pk.piece} in ${pk.container}`;
    $('sendnote').textContent = openIssue('submit-packing.yml', `[packing] ${pid} n=${pk.n}: s = ${pk.s}`,
      { problem: pid, n: String(pk.n), s: String(pk.s), credit: $('credit').value.trim(), method: $('how').value.trim() }, ['packing', json]) || 'Opened GitHub in a new tab.';
  };
  $('c_send').onclick = () => {
    const v = id => $(id).value.trim();
    openIssue('new-category.yml', `[category] ${v('c_pieces') || 'pieces'} in ${v('c_container') || 'a container'}`,
      { pieces: v('c_pieces'), container: v('c_container'), measure: v('c_measure'), motivation: v('c_motivation'), details: v('c_details') });
  };
  $('o_send').onclick = () => {
    const v = id => $(id).value.trim();
    openIssue('other-construction.yml', `[construction] ${v('o_title') || 'a new construction'}`,
      { summary: v('o_title'), description: v('o_description'), data: v('o_data'), links: v('o_links') });
  };
})();
