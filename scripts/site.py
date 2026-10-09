#!/usr/bin/env python3
"""Build site/index.html: record tables, s(n) chart and an interactive 3D viewer, with every record embedded.
usage: python3 scripts/site.py"""
import json, os, glob, csv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
AB = {'tet': 'tetrahedron', 'cub': 'cube', 'oct': 'octahedron', 'dod': 'dodecahedron', 'ico': 'icosahedron'}
ORDER = ['tetintet', 'octinoct', 'icoinico', 'dodindod']


def load():
    probs = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'records', '*', '*_n[0-9][0-9].json'))):
        r = json.load(open(f)); pid = r['record_id'].split('_')[0]
        cert = open(f.replace('.json', '.certify.txt')).read() if os.path.exists(f.replace('.json', '.certify.txt')) else ''
        p = probs.setdefault(pid, {'id': pid, 'piece': r['piece'], 'container': r['container'], 'rows': []})
        p['rows'].append({'n': r['n'], 's': r['s_plus'], 'sf': r['s_full'], 'st': r.get('s_tight'), 'cf': r.get('closed_form_conjecture'),
                          'den': round(r['density'], 4), 'vlb': round(r['volume_lower_bound'], 5),
                          'ok': 'CERTIFIED' in cert and 'NOT CERTIFIED' not in cert,
                          'cert': [l for l in cert.splitlines() if l.startswith('(')],
                          'p': [[round(x, 7) for x in q] for q in r['pieces']]})
    for p in probs.values(): p['rows'].sort(key=lambda r: r['n'])
    ids = [i for i in ORDER if i in probs] + sorted(i for i in probs if i not in ORDER)
    solids = {k: {'V': v['V'], 'F': v['faces'], 'E': v['edges'], 'vol': v['volume']} for k, v in SOL.items()}
    return {'problems': [probs[i] for i in ids], 'solids': solids}


TEMPLATE = r'''<title>Platonic Packing Records</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=STIX+Two+Text:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: drafting-sheet record book: problem tabs, a record table beside a sticky 3D specimen viewer, chart below. */
:root {
  --paper: #eef1f0; --sheet: #f8faf9; --ink: #172024; --muted: #59666b; --rule: #d3dad9;
  --accent: #2c49a8; --exact: #9a4f17; --ok: #2f6b45; --warn: #a33b2b;
  --f-display: "STIX Two Text", "STIX Two Math", Georgia, serif;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #0f1416; --sheet: #151c1f; --ink: #e1e7e8; --muted: #94a3a7; --rule: #27323a;
  --accent: #91a8ff; --exact: #e3a466; --ok: #7cc79a; --warn: #f08b7a; color-scheme: dark } }
:root[data-theme="dark"] {
  --paper: #0f1416; --sheet: #151c1f; --ink: #e1e7e8; --muted: #94a3a7; --rule: #27323a;
  --accent: #91a8ff; --exact: #e3a466; --ok: #7cc79a; --warn: #f08b7a; color-scheme: dark }
* { box-sizing: border-box }
body { background: var(--paper); color: var(--ink); font: 15px/1.55 var(--f-body); }
.wrap { max-width: 1180px; margin: 0 auto; padding-inline: max(16px, 3vw); padding-block: 28px 56px; display: grid; gap: 28px }
header { display: grid; gap: 10px; max-width: 70ch }
h1 { font: 600 clamp(28px, 4.2vw, 44px)/1.08 var(--f-display); margin: 0; text-wrap: balance; letter-spacing: -0.01em }
h1 em { font-style: italic; font-weight: 400; color: var(--accent) }
.lede { margin: 0; color: var(--muted) }
.lede b { color: var(--ink); font-weight: 500 }
.tabs { display: flex; flex-wrap: wrap; gap: 8px }
.tab { font: 500 13px/1 var(--f-body); padding: 9px 12px; border-radius: 999px; border: 1px solid var(--rule); background: var(--sheet); color: var(--ink); cursor: pointer; display: inline-flex; gap: 8px; align-items: center }
.tab .id { font-family: var(--f-mono); color: var(--muted); font-size: 12px }
.tab[aria-selected="true"] { border-color: var(--accent); color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent) }
.tab:focus-visible, button:focus-visible, tr:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }
.grid { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: 24px; align-items: start }
@media (max-width: 860px) { .grid { grid-template-columns: minmax(0, 1fr) } .viewer { position: static !important } }
.panel { background: var(--sheet); border: 1px solid var(--rule); border-radius: 10px; min-width: 0 }
.panel h2 { font: 600 19px/1.2 var(--f-display); margin: 0; text-wrap: balance }
.phead { padding: 16px 18px 10px; display: grid; gap: 4px; border-bottom: 1px solid var(--rule) }
.phead p { margin: 0; color: var(--muted); font-size: 13px }
.tablewrap { overflow-x: auto }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; font-size: 14px }
th { text-align: left; font: 500 11px/1 var(--f-body); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); padding: 10px 12px; border-bottom: 1px solid var(--rule); white-space: nowrap }
td { padding: 7px 12px; border-bottom: 1px solid var(--rule); white-space: nowrap }
tbody tr { cursor: pointer }
tbody tr:hover td { background: color-mix(in srgb, var(--accent) 6%, transparent) }
tbody tr[aria-selected="true"] td { background: color-mix(in srgb, var(--accent) 12%, transparent) }
td.n { font-family: var(--f-mono); color: var(--muted) }
td.s { font-family: var(--f-mono); font-weight: 500 }
td.cf { font-family: var(--f-display); font-size: 16px; color: var(--exact) }
td.den, td.vlb { font-family: var(--f-mono); color: var(--muted); font-size: 13px }
.tick { color: var(--ok); font-weight: 600 } .cross { color: var(--warn); font-weight: 600 }
td.pending { color: var(--muted); font-style: italic }
.viewer { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 12px) }
.stage { position: relative; aspect-ratio: 1 / 1; max-width: 100%; touch-action: none; cursor: grab; border-bottom: 1px solid var(--rule) }
.stage:active { cursor: grabbing }
.stage canvas { width: 100%; height: 100%; display: block; border-radius: 10px 10px 0 0 }
.caption { padding: 14px 18px 16px; display: grid; gap: 8px }
.caption .big { font: 600 22px/1.15 var(--f-display) }
.caption .big .cf { color: var(--exact); font-weight: 400; font-style: italic }
.meta { font: 12px/1.5 var(--f-mono); color: var(--muted); margin: 0; overflow-wrap: anywhere }
.controls { display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: center; font-size: 13px; color: var(--muted) }
.controls label { display: inline-flex; gap: 8px; align-items: center }
input[type=range] { accent-color: var(--accent); width: 130px }
button.small { font: 500 12px/1 var(--f-body); padding: 7px 10px; border-radius: 6px; border: 1px solid var(--rule); background: transparent; color: var(--ink); cursor: pointer }
.hint { position: absolute; left: 12px; bottom: 10px; font: 11px/1 var(--f-body); color: var(--muted); letter-spacing: .04em; pointer-events: none }
.chart { padding: 6px 12px 12px }
.chart svg { width: 100%; height: auto; display: block }
.notes { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px }
.note { display: grid; gap: 6px; min-width: 0 }
.note h3 { font: 600 16px/1.25 var(--f-display); margin: 0 }
.note p { margin: 0; color: var(--muted); font-size: 14px; max-width: 62ch }
.note code { font: 12.5px var(--f-mono); color: var(--ink) }
footer { color: var(--muted); font-size: 13px; max-width: 80ch }
footer a { color: var(--accent) }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto } }
</style>

<div class="wrap">
  <header>
    <h1>How small can the container be? <em>Platonic solids in Platonic solids</em></h1>
    <p class="lede">Each row is the smallest container found for <b>n unit-edge copies</b> of a solid, reported as
      <b>s = container edge ÷ piece edge</b>. Pieces start as their inscribed spheres and are sharpened into the solid
      under pressure (Yohei Nakajima's soft-to-rigid method), then tightened, and every packing is proven valid in exact
      arithmetic over ℚ(√2, √5).</p>
  </header>

  <nav class="tabs" id="tabs" role="tablist" aria-label="Packing problem"></nav>

  <div class="grid">
    <section class="panel" aria-labelledby="ptitle">
      <div class="phead"><h2 id="ptitle"></h2><p id="psub"></p></div>
      <div class="tablewrap"><table>
        <thead><tr><th>n</th><th>s</th><th>closed form?</th><th>density</th><th>volume bound</th><th>exact check</th></tr></thead>
        <tbody id="rows"></tbody>
      </table></div>
      <div class="chart"><svg id="chart" viewBox="0 0 560 230" role="img" aria-label="s against n"></svg></div>
    </section>

    <section class="panel viewer" aria-label="3D view of the selected packing">
      <div class="stage" id="stage"><canvas id="cv"></canvas><span class="hint">drag to turn</span></div>
      <div class="caption">
        <div class="big" id="cap"></div>
        <div class="controls">
          <label for="explode">spread <input type="range" id="explode" min="1" max="1.8" step="0.01" value="1"></label>
          <label for="spin"><input type="checkbox" id="spin"> turn slowly</label>
          <button class="small" id="reset" type="button">reset view</button>
        </div>
        <p class="meta" id="meta"></p>
      </div>
    </section>
  </div>

  <section class="notes" aria-label="Method">
    <div class="note"><h3>Inscribed sphere first</h3><p>Every piece starts as the ball inscribed in it. The intermediate shape is
      (1 − r/ρ)·P ⊕ B(r): it always fits inside the final solid and only grows as r falls, so the search follows one monotone path from
      sphere packing to polytope packing.</p></div>
    <div class="note"><h3>Sharpened under pressure</h3><p>Inward pressure on the container, exact penetration depths (separating axes) and exact
      distances (feature pairs) with analytic gradients; then SLSQP with a separating plane per pair squeezes out the last contacts.</p></div>
    <div class="note"><h3>Proven, not just plotted</h3><p><code>certify_exact.py</code> rebuilds each unit-edge solid with coordinates in ℚ(√2, √5),
      checks every vertex is strictly inside the container and exhibits a separating plane for every pair, with no rounding.
      A row is an upper bound with a proof; optimality is not claimed.</p></div>
    <div class="note"><h3>Reading the table</h3><p><b>s</b> is the certified size truncated to five decimals, with 10⁻⁷ clearance on every
      contact. <b>Closed form?</b> is the touching-contact limit matched to 11 digits by a small quadratic irrationality: a conjecture.
      <b>Volume bound</b> is (n·vol piece / vol container)^⅓.</p></div>
  </section>

  <footer>Method and original cube code: Yohei Nakajima, <i>Twelve unit cubes in a cube of side 2.9315: soft-to-rigid packing</i> (2026).
    Record ids follow Erich Friedman's Packing Center naming: tet, cub, oct, dod, ico, so <code>dodindod_n07</code> is seven dodecahedra in a dodecahedron.
    <span id="stamp"></span></footer>
</div>

<script id="data" type="application/json">__DATA__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(() => {
  const D = JSON.parse(document.getElementById('data').textContent);
  const NAMES = { tetrahedron: ['tetrahedron', 'tetrahedra'], cube: ['cube', 'cubes'], octahedron: ['octahedron', 'octahedra'],
                  dodecahedron: ['dodecahedron', 'dodecahedra'], icosahedron: ['icosahedron', 'icosahedra'] };
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const store = { get(k) { try { return localStorage.getItem(k) } catch (e) { return null } }, set(k, v) { try { localStorage.setItem(k, v) } catch (e) {} } };
  let prob = D.problems.find(p => p.id === (location.hash.slice(1).split('_')[0])) || D.problems.find(p => p.id === store.get('ppr-prob')) || D.problems[0];
  let row = null;

  // ---------- tabs
  const tabs = document.getElementById('tabs');
  D.problems.forEach(p => {
    const b = document.createElement('button');
    b.className = 'tab'; b.type = 'button'; b.setAttribute('role', 'tab'); b.id = 'tab-' + p.id;
    b.innerHTML = `${cap(NAMES[p.piece][1])} in ${article(p.container)} <span class="id">${p.id}</span>`;
    b.onclick = () => selectProb(p);
    tabs.appendChild(b);
  });
  function cap(s) { return s[0].toUpperCase() + s.slice(1) }
  function article(s) { return (/^[aeiou]/.test(s) ? 'an ' : 'a ') + s }

  // ---------- table + chart
  function selectProb(p) {
    prob = p; store.set('ppr-prob', p.id);
    document.querySelectorAll('.tab').forEach(t => t.setAttribute('aria-selected', t.id === 'tab-' + p.id));
    document.getElementById('ptitle').textContent = `${cap(NAMES[p.piece][1])} in ${article(p.container)}`;
    const done = p.rows.length;
    document.getElementById('psub').textContent = `${done} of 19 values of n (2–20) recorded · s = container edge ÷ piece edge`;
    const tb = document.getElementById('rows'); tb.innerHTML = '';
    for (let n = 2; n <= 20; n++) {
      const r = p.rows.find(r => r.n === n);
      const tr = document.createElement('tr');
      if (!r) { tr.innerHTML = `<td class="n">${n}</td><td class="pending" colspan="5">searching</td>`; tr.style.cursor = 'default'; tb.appendChild(tr); continue; }
      tr.tabIndex = 0; tr.dataset.n = n;
      tr.innerHTML = `<td class="n">${n}</td><td class="s">${r.s}</td><td class="cf">${r.cf ? fmtCF(r.cf) : ''}</td>` +
        `<td class="den">${r.den.toFixed(3)}</td><td class="vlb">${r.vlb.toFixed(3)}</td>` +
        `<td>${r.ok ? '<span class="tick" title="certify_exact.py: CERTIFIED">✓ certified</span>' : '<span class="cross">not certified</span>'}</td>`;
      tr.onclick = () => selectRow(r); tr.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectRow(r) } };
      tb.appendChild(tr);
    }
    drawChart();
    const want = +((location.hash.split('_n')[1]) || 0);
    selectRow(p.rows.find(r => r.n === want) || p.rows.find(r => r.n === 7) || p.rows[p.rows.length - 1]);
  }
  function fmtCF(s) { return s.replace(/√(\d+)/g, '√<span style="text-decoration:overline">$1</span>') }

  function drawChart() {
    const svg = document.getElementById('chart'), W = 560, H = 230, L = 46, R = 14, T = 14, B = 34;
    const rows = prob.rows; if (!rows.length) { svg.innerHTML = ''; return }
    const ys = rows.flatMap(r => [parseFloat(r.s), r.vlb]);
    let y0 = Math.floor(Math.min(...ys) * 4) / 4, y1 = Math.ceil(Math.max(...ys) * 4) / 4;
    const X = n => L + (n - 2) / 18 * (W - L - R), Y = v => T + (1 - (v - y0) / (y1 - y0)) * (H - T - B);
    const ink = 'var(--ink)', mut = 'var(--muted)', rule = 'var(--rule)', acc = 'var(--accent)';
    let g = '';
    for (let v = y0; v <= y1 + 1e-9; v += 0.25) g += `<line x1="${L}" x2="${W - R}" y1="${Y(v)}" y2="${Y(v)}" stroke="${rule}" stroke-width="1"/>` +
      `<text x="${L - 8}" y="${Y(v) + 4}" text-anchor="end" font-size="11" font-family="IBM Plex Mono, monospace" fill="${mut}">${v.toFixed(2)}</text>`;
    for (let n = 2; n <= 20; n += 2) g += `<text x="${X(n)}" y="${H - B + 18}" text-anchor="middle" font-size="11" font-family="IBM Plex Mono, monospace" fill="${mut}">${n}</text>`;
    g += `<text x="${W - R}" y="${H - 4}" text-anchor="end" font-size="11" fill="${mut}" font-family="IBM Plex Sans, sans-serif">n</text>`;
    const vl = rows.map(r => `${X(r.n)},${Y(r.vlb)}`).join(' ');
    g += `<polyline points="${vl}" fill="none" stroke="${mut}" stroke-width="1.4" stroke-dasharray="4 4"/>`;
    const last = rows[rows.length - 1];
    g += `<text x="${X(last.n) - 4}" y="${Y(last.vlb) + 16}" text-anchor="end" font-size="11" fill="${mut}" font-family="IBM Plex Sans, sans-serif">volume bound</text>`;
    const sl = rows.map(r => `${X(r.n)},${Y(parseFloat(r.s))}`).join(' ');
    g += `<polyline points="${sl}" fill="none" stroke="${acc}" stroke-width="2"/>`;
    rows.forEach(r => g += `<circle cx="${X(r.n)}" cy="${Y(parseFloat(r.s))}" r="${row && row.n === r.n ? 5.5 : 3.6}" fill="${row && row.n === r.n ? acc : 'var(--sheet)'}" stroke="${acc}" stroke-width="2" data-n="${r.n}" style="cursor:pointer"><title>n = ${r.n}: s = ${r.s}</title></circle>`);
    svg.innerHTML = g;
    svg.querySelectorAll('circle').forEach(c => c.onclick = () => selectRow(prob.rows.find(r => r.n === +c.dataset.n)));
  }

  function selectRow(r) {
    if (!r) return; row = r;
    document.querySelectorAll('#rows tr').forEach(t => t.setAttribute('aria-selected', +t.dataset.n === r.n));
    const pl = NAMES[prob.piece][r.n === 1 ? 0 : 1];
    document.getElementById('cap').innerHTML = `${r.n} ${pl} · s = ${r.s}` + (r.cf ? ` <span class="cf">≈ ${fmtCF(r.cf)}</span>` : '');
    document.getElementById('meta').textContent = `${prob.id}_n${String(r.n).padStart(2, '0')}  s_full = ${r.sf}  touching limit ${r.st}\n` + r.cert.join('  ');
    try { history.replaceState(null, '', '#' + prob.id + '_n' + String(r.n).padStart(2, '0')) } catch (e) {}
    drawChart(); build();
  }

  // ---------- 3D
  const stage = document.getElementById('stage'), cv = document.getElementById('cv');
  const PAL = ['#4c6fd6', '#d9822b', '#3f9a6a', '#c8524a', '#7a5fc4', '#2a9fb0', '#c9a227', '#b5577f', '#6d8a2f', '#8a6a4b',
               '#5a86c2', '#d36b3b', '#4aa087', '#a8484a', '#8c76d1', '#3b8fa0', '#b8962e', '#9c5c8f', '#7f9a3a', '#a37b5a'];
  let renderer, scene, camera, world, piecesGroup, contLines, pieceObjs = [], R0 = 3;
  const hasGL = typeof THREE !== 'undefined';
  if (hasGL) {
    renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(32, 1, 0.01, 1000);
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const l1 = new THREE.DirectionalLight(0xffffff, 0.75); l1.position.set(3, 5, 6); scene.add(l1);
    const l2 = new THREE.DirectionalLight(0xffffff, 0.3); l2.position.set(-4, -2, -3); scene.add(l2);
    world = new THREE.Group(); scene.add(world);
  } else { stage.innerHTML = '<p class="meta" style="padding:18px">The 3D view needs WebGL and the three.js script, which did not load.</p>' }

  function quatOf(p) { const q = new THREE.Quaternion(p[4], p[5], p[6], p[3]); return q.normalize() }
  function solidGeom(name) {
    const S = D.solids[name], pos = [];
    S.F.forEach(f => { for (let i = 1; i + 1 < f.length; i++) [f[0], f[i], f[i + 1]].forEach(k => pos.push(...S.V[k])) });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
    const ep = []; S.E.forEach(([a, b]) => ep.push(...S.V[a], ...S.V[b]));
    const eg = new THREE.BufferGeometry(); eg.setAttribute('position', new THREE.Float32BufferAttribute(ep, 3));
    return { g, eg };
  }
  function build() {
    if (!hasGL || !row) return;
    while (world.children.length) world.remove(world.children[0]);
    pieceObjs = [];
    const C = D.solids[prob.container], piece = solidGeom(prob.piece);
    const ink = new THREE.Color(css('--ink'));
    const cp = []; C.E.forEach(([a, b]) => cp.push(...C.V[a].map(x => x * row.sf), ...C.V[b].map(x => x * row.sf)));
    const cg = new THREE.BufferGeometry(); cg.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3));
    contLines = new THREE.LineSegments(cg, new THREE.LineBasicMaterial({ color: ink, transparent: true, opacity: 0.85 }));
    world.add(contLines);
    row.p.forEach((p, i) => {
      const grp = new THREE.Group();
      const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(PAL[i % PAL.length]), flatShading: true, roughness: 0.55, metalness: 0.05,
        polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
      grp.add(new THREE.Mesh(piece.g, mat));
      grp.add(new THREE.LineSegments(piece.eg, new THREE.LineBasicMaterial({ color: 0x10181b, transparent: true, opacity: 0.55 })));
      grp.quaternion.copy(quatOf(p)); grp.userData.c = new THREE.Vector3(p[0], p[1], p[2]);
      world.add(grp); pieceObjs.push(grp);
    });
    R0 = Math.max(...C.V.map(v => Math.hypot(...v))) * row.sf;
    applySpread(); fit(); paint();
  }
  function applySpread() { const k = +document.getElementById('explode').value; pieceObjs.forEach(g => g.position.copy(g.userData.c).multiplyScalar(k)) }
  function fit() {
    const w = stage.clientWidth || 400; renderer.setSize(w, w, false); camera.aspect = 1; camera.updateProjectionMatrix();
    const k = +document.getElementById('explode').value;
    camera.position.set(0, 0, (R0 * Math.max(1, 0.55 + 0.45 * k)) / Math.sin(THREE.MathUtils.degToRad(16)) * 1.04); camera.lookAt(0, 0, 0);
  }
  function paint() { if (!hasGL) return; scene.background = new THREE.Color(css('--sheet')); if (contLines) contLines.material.color.set(css('--ink')); renderer.render(scene, camera) }
  const RESET = () => { if (!hasGL) return; world.quaternion.setFromEuler(new THREE.Euler(-0.5, 0.6, 0.05)); paint() };
  if (hasGL) {
    RESET();
    let drag = null;
    stage.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY }; stage.setPointerCapture(e.pointerId) });
    stage.addEventListener('pointermove', e => {
      if (!drag) return;
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag = { x: e.clientX, y: e.clientY };
      const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(dy * 0.01, dx * 0.01, 0));
      world.quaternion.premultiply(q); paint();
    });
    const end = () => drag = null; stage.addEventListener('pointerup', end); stage.addEventListener('pointercancel', end);
    document.getElementById('explode').oninput = () => { applySpread(); fit(); paint() };
    document.getElementById('reset').onclick = () => { document.getElementById('explode').value = 1; applySpread(); fit(); RESET() };
    const spin = document.getElementById('spin');
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    spin.checked = !reduce && store.get('ppr-spin') !== '0';
    spin.onchange = () => store.set('ppr-spin', spin.checked ? '1' : '0');
    let last = performance.now();
    (function loop(t) { const dt = Math.min(50, t - last); last = t;
      if (spin.checked && !drag) { world.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), dt * 0.00025)); paint() }
      requestAnimationFrame(loop) })(last);
    new ResizeObserver(() => { fit(); paint() }).observe(stage);
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { build() });
    new MutationObserver(() => build()).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }
  document.getElementById('stamp').textContent = 'Built ' + D.built + '.';
  selectProb(prob);
})();
</script>
'''

if __name__ == '__main__':
    import datetime
    data = load(); data['built'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    os.makedirs(os.path.join(ROOT, 'site'), exist_ok=True)
    html = TEMPLATE.replace('__DATA__', json.dumps(data, separators=(',', ':')).replace('</', '<\\/'))
    out = os.path.join(ROOT, 'site', 'index.html'); open(out, 'w').write(html)
    print(out, len(html) // 1024, 'KB', sum(len(p['rows']) for p in data['problems']), 'records')
