// Record explorer for polyhedrainpolyhedra.wiki: families, atlas of problems, 3D viewer (three.js r128), table, charts.
// Data: window.PP_DATA (inlined copy) or data/records.json next to the page (see scripts/site.py).
// A published bound without poses is a reference, never geometry. Resolve it
// to the smallest available coordinate construction at that construction's s.
function packingConstructionChoices(primary, requested = primary) {
  const hasGeometry = c => c && c.n === primary.n && !c.source_only && Array.isArray(c.p) && c.p.length === c.n;
  const choices = [primary, ...(primary.alternatives || [])].filter(hasGeometry).sort((a, b) => a.sf - b.sf);
  return { choices, row: choices.includes(requested) ? requested : choices[0] || null,
    reference: primary.source_only ? primary : null };
}
function packingInitialSelection(problem, hash, requestedN) {
  const prefix = problem.id + '_n';
  const match = typeof hash === 'string' && hash.startsWith(prefix) ? /^(\d+)(?:_|$)/.exec(hash.slice(prefix.length)) : null;
  const n = requestedN || (match ? Number(match[1]) : 0);
  const primary = problem.rows.find(r => r.n === n) || problem.rows.find(r => r.n === 12) || problem.rows[problem.rows.length - 1];
  if (!primary || requestedN || !match || hash === prefix + String(n).padStart(2, '0')) return primary;
  return [primary, ...(primary.alternatives || [])].find(r => r.id === hash) || primary;
}
function packingPublicURL(value) {
  if (typeof value !== 'string' || /[\u0000-\u0020\u007f]/.test(value)) return null;
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) && url.hostname && !url.username && !url.password ? url.href : null;
  } catch (e) { return null }
}
function packingUnitQuaternion(q) {
  const scale = Math.max(...q.map(Math.abs));
  if (q.length !== 4 || !q.every(Number.isFinite) || !scale) return [1, 0, 0, 0];
  const scaled = q.map(x => x / scale), length = Math.hypot(...scaled);
  return scaled.map(x => x / length);
}
function packingReferenceTolerance(row) {
  const value = Number(row.ref_quantum);
  return Number.isFinite(value) && value >= 0 ? Math.max(1e-5, value) : 1e-5;
}
function packingDerivationText(value) {
  if (typeof value === 'string') return value;
  if (!value || typeof value !== 'object' || Array.isArray(value)) return '';
  return Object.entries(value).map(([key, item]) => `${key.replace(/_/g, ' ')}: ${typeof item === 'object' ? JSON.stringify(item) : item}`).join('; ');
}
function packingRecordRawURL(repo, file, version) {
  const publicRepo = packingPublicURL(repo);
  if (!publicRepo || typeof file !== 'string') return null;
  const url = new URL(publicRepo), parts = file.split('/');
  if (url.origin !== 'https://github.com' || !/^\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/.test(url.pathname) ||
      url.search || url.hash || parts[0] !== 'records' || !file.endsWith('.json') ||
      parts.some(part => !/^[A-Za-z0-9_.-]+$/.test(part) || part === '.' || part === '..')) return null;
  const raw = new URL(`https://raw.githubusercontent.com${url.pathname.replace(/\/$/, '')}/main/${parts.map(encodeURIComponent).join('/')}`);
  if (version) raw.searchParams.set('v', String(version));
  return raw.href;
}
async function packingFullPrecisionRecord(repo, row, problem, version, fetchRecord = fetch) {
  const url = packingRecordRawURL(repo, row.file, version);
  if (!url) throw new Error('No trusted record file is available.');
  const response = await fetchRecord(url, { cache: 'no-cache' });
  if (!response.ok) throw new Error('The full-precision record could not be fetched.');
  const text = await response.text(), record = JSON.parse(text);
  if (!record || record.piece !== problem.piece || record.container !== problem.container || record.n !== row.n ||
      Number(record.s_full) !== row.sf || !Array.isArray(record.pieces) || record.pieces.length !== row.n) {
    throw new Error('The record changed. Reload the site before copying it.');
  }
  // Preserve every source field and the exact decimal text of the witness.
  return text;
}
if (typeof module !== 'undefined' && module.exports) module.exports = { packingConstructionChoices, packingInitialSelection, packingPublicURL,
  packingUnitQuaternion, packingReferenceTolerance, packingDerivationText, packingRecordRawURL, packingFullPrecisionRecord };
if (typeof document !== 'undefined') (async () => {
  const $ = id => document.getElementById(id);
  const ROOT = document.documentElement.dataset.root || './';
  const DATA_VERSION = document.documentElement.dataset.recordsVersion;
  const DATA_URL = ROOT + 'data/records.json' + (DATA_VERSION ? '?v=' + encodeURIComponent(DATA_VERSION) : '');
  let D = window.PP_DATA;
  if (!D) {
    try { D = await (await fetch(DATA_URL, { cache: 'no-cache' })).json() }
    catch (e) { $('ptitle').textContent = 'The record data did not load. Reload the page, or browse the records on GitHub.'; return }
  }
  const NAMES = { tetrahedron: ['tetrahedron', 'tetrahedra'], cube: ['cube', 'cubes'], octahedron: ['octahedron', 'octahedra'],
                  dodecahedron: ['dodecahedron', 'dodecahedra'], icosahedron: ['icosahedron', 'icosahedra'] };
  const SRC = { F: 'E. Friedman catalogue', W: 'R. Walsh', L: 'H. Lin', N: 'Y. Nakajima', T: 'trivial grid' };
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  function sourceLink(value, label) {
    const url = packingPublicURL(value);
    return url ? `<a href="${escapeHTML(url)}" target="_blank" rel="noopener">${escapeHTML(label)}</a>` : escapeHTML(label);
  }
  function submissionIssue(value) {
    try {
      const url = new URL(value);
      if (url.origin !== 'https://github.com' || url.username || url.password ||
          !/^\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/issues\/[1-9]\d*\/?$/.test(url.pathname)) return null;
      return url;
    } catch (e) { return null }
  }
  const store = { get(k) { try { return localStorage.getItem(k) } catch (e) { return null } }, set(k, v) { try { localStorage.setItem(k, v) } catch (e) {} } };
  const hashId = location.hash.slice(1);
  let prob = D.problems.find(p => p.id === hashId.split('_')[0]) || D.problems.find(p => p.id === store.get('ppr-prob')) || D.problems[0];
  let row = null, sel = null, isolate = false;
  let colMode = store.get('ppr-col') || 'orient', axis = 2;
  let edgeMode = store.get('ppr-edge-mode') === 'contrast' ? 'contrast' : 'piece';
  const storedWidth = Number(store.get('ppr-edge-width'));
  let edgeWidth = storedWidth >= 0.5 && storedWidth <= 6 ? storedWidth : 1.5;
  const PAL = ['#4c6fd6', '#d9822b', '#3f9a6a', '#c8524a', '#7a5fc4', '#2a9fb0', '#c9a227', '#b5577f', '#6d8a2f', '#8a6a4b',
               '#5a86c2', '#d36b3b', '#4aa087', '#a8484a', '#8c76d1', '#3b8fa0', '#b8962e', '#9c5c8f', '#7f9a3a', '#a37b5a'];
  const POLY = { 3: 'triangular', 4: 'square', 5: 'pentagonal', 6: 'hexagonal', 8: 'octagonal', 12: 'dodecagonal' };
  const dn = s => { const m = /^(anti)?prism(\d+)$/.exec(s); return m ? `${POLY[m[2]]} ${m[1] ? 'antiprism' : 'prism'}` : s.replace(/_/g, ' ') };
  const pl = s => { if (NAMES[s]) return NAMES[s][1]; const w = dn(s); return w.endsWith('hedron') ? w.slice(0, -6) + 'hedra' : w + 's' };
  const cap = s => s[0].toUpperCase() + s.slice(1);
  const article = s => (/^[aeiou]/.test(s) ? 'an ' : 'a ') + s;
  const fmtCF = s => s.replace(/√(\d+)/g, '√<span style="text-decoration:overline">$1</span>');
  const pct = r => (100 * (r.sf / r.ref - 1)).toFixed(2);
  const pad = n => String(n).padStart(2, '0');
  const chartScale = r => r.st ?? r.published_sf ?? r.sf;
  function chip(r) {
    if (r.cmp == null) return '';
    const tolerance = packingReferenceTolerance(r), title = `Compared at the published precision; tolerance ${tolerance}.`;
    if (r.cmp === 'better') return `<span class="chip better" title="${title}">better by ${(-pct(r)).toFixed(2)}%</span>`;
    if (r.cmp === 'equal') return `<span class="chip" title="${title}">equal</span>`;
    return `<span class="chip behind" title="${title}">+${pct(r)}%</span>`;
  }

  // ---------- geometry helpers
  function qn(p) { return packingUnitQuaternion(p.slice(3, 7)) }
  function qrot(q, v) {
    const [w, x, y, z] = q, tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
    return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)];
  }
  function circ(name) { return Math.max(...D.solids[name].V.map(v => Math.hypot(...v))) }
  function orient(r) {           // orientation classes: pieces that are exact translates of each other
    if (r._oc) return r._oc;
    const V = D.solids[prob.piece].V, reps = [], cls = [];
    r.p.forEach(p => {
      const q = qn(p), W = V.map(v => qrot(q, v));
      let k = reps.findIndex(R => W.every(a => R.some(b => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) < 3e-3)));
      if (k < 0) { reps.push(W); k = reps.length - 1 }
      cls.push(k);
    });
    const size = reps.map((_, k) => cls.filter(c => c === k).length);
    const rank = size.map((_, k) => k).sort((a, b) => size[b] - size[a] || a - b);
    const rk = []; rank.forEach((k, i) => rk[k] = i);
    return r._oc = { cls: cls.map(k => rk[k]), sizes: rank.map(k => size[k]) };
  }
  function neighbours(r, i) {
    const c = r.p[i];
    return r.p.map((p, j) => [j, Math.hypot(p[0] - c[0], p[1] - c[1], p[2] - c[2])]).filter(x => x[0] !== i).sort((a, b) => a[1] - b[1]);
  }

  // ---------- families and the atlas of problems (each tile is a drawing of a real packing from the archive)
  // 14 Oct (Alejandro): each family tab is split into side-by-side columns so a packing is easy to find
  const DUAL = { cube: 'octahedron', octahedron: 'cube', dodecahedron: 'icosahedron', icosahedron: 'dodecahedron', tetrahedron: 'tetrahedron' };
  const isPrism = p => /^prism\d+$/.test(p.piece), isElong = p => /^prism\d+_l/.test(p.piece), isAnti = p => /^antiprism/.test(p.piece);
  const GROUPS = [['platonic', 'Platonic', [['Self packings', p => p.family === 'platonic' && p.piece === p.container],
                                           ['Dual packings', p => p.family === 'platonic' && p.piece !== p.container && DUAL[p.piece] === p.container],
                                           ['Heterogeneous packings', p => p.family === 'platonic' && p.piece !== p.container && DUAL[p.piece] !== p.container, 2]]],
                  ['archcat', 'Archimedean and Catalan', [['Archimedean solids', p => p.family === 'archimedean', 2], ['Catalan solids', p => p.family === 'catalan', 2]]],
                  ['prisms', 'Prisms and antiprisms', [['Prisms', p => p.family === 'prisms' && isPrism(p)], ['Antiprisms', p => p.family === 'prisms' && isAnti(p)],
                                                       ['Elongated prisms', p => p.family === 'prisms' && isElong(p)]]]];
  const ptitle = p => p.title || `${cap(pl(p.piece))} in ${article(dn(p.container))}`;
  const ROT = (() => { const a = -0.5, b = 0.62, ca = Math.cos(a), sa = Math.sin(a), cb = Math.cos(b), sb = Math.sin(b);
    return v => { const x1 = cb * v[0] + sb * v[2], z1 = -sb * v[0] + cb * v[2]; return [x1, ca * v[1] - sa * z1] } })();
  function thumb(cv, p) {
    const dpr = Math.min(2, window.devicePixelRatio || 1), W = 64; cv.width = W * dpr; cv.height = W * dpr;
    const g = cv.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, W);
    const r = p.rows.find(x => x.n === 6) || p.rows.find(x => x.n === 5) || p.rows[0]; if (!r) return;
    const C = D.solids[p.container], P = D.solids[p.piece], R = Math.max(...C.V.map(v => Math.hypot(...v))) * r.sf, k = (W / 2 - 3) / R;
    const tp = v => { const [x, y] = ROT(v); return [W / 2 + k * x, W / 2 - k * y] };
    g.lineWidth = 0.8; g.strokeStyle = css('--accent'); g.globalAlpha = 0.8; g.beginPath();
    r.p.forEach(pc => { const q = qn(pc), V = P.V.map(v => { const w = qrot(q, v); return tp([w[0] + pc[0], w[1] + pc[1], w[2] + pc[2]]) });
      P.E.forEach(([a, b]) => { g.moveTo(...V[a]); g.lineTo(...V[b]) }) });
    g.stroke(); g.globalAlpha = 1; g.strokeStyle = css('--ink'); g.lineWidth = 1.1; g.beginPath();
    C.E.forEach(([a, b]) => { g.moveTo(...tp(C.V[a].map(x => x * r.sf))); g.lineTo(...tp(C.V[b].map(x => x * r.sf))) }); g.stroke();
  }
  const fams = $('fams'), atlas = $('atlas');
  function showGroup(g, pick) {
    fams.querySelectorAll('.fam').forEach(t => t.setAttribute('aria-selected', t.dataset.g === g));
    atlas.innerHTML = '';
    const grp = GROUPS.find(x => x[0] === g);
    // a column may be several tiles wide (Platonic 1 | 1 | 2, so the columns are about equally long; Archimedean 2 | Catalan 2)
    const cols = grp[2].map(([head, f, w]) => [head, D.problems.filter(f), w || 1]).filter(c => c[1].length);
    atlas.className = 'atlas cols'; atlas.style.setProperty('--cols', cols.map(c => `minmax(0, ${c[2]}fr)`).join(' '));
    cols.forEach(([head, ps, w]) => {
      const col = document.createElement('section'); col.className = 'col'; col.style.setProperty('--w', w);
      const h = document.createElement('h2'); h.innerHTML = `${head} <span class="k">${ps.length}</span>`; col.appendChild(h);
      const box = document.createElement('div'); box.className = 'tiles'; box.setAttribute('role', 'tablist'); box.setAttribute('aria-label', head);
      ps.forEach(p => {
        const b = document.createElement('button'); b.className = 'tile'; b.type = 'button'; b.setAttribute('role', 'tab'); b.id = 'tab-' + p.id;
        const cv = document.createElement('canvas'); cv.setAttribute('aria-hidden', 'true');
        b.innerHTML = `<span><span class="t">${ptitle(p)}</span><span class="m" style="display:block">${p.rows.length} of ${D.nmax - D.nmin + 1} values` +
          (p.hasref ? ', published values' : '') + `</span></span>`;
        b.prepend(cv); thumb(cv, p);
        b.onclick = () => { selectProb(p); $('viewer').scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' }) };
        box.appendChild(b);
      });
      col.appendChild(box); atlas.appendChild(col);
    });
    if (pick) { const p = D.problems.find(p => p.group === g); if (p) selectProb(p) }
    else markTile();
  }
  const reduceMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  GROUPS.forEach(([g, label]) => {
    const ps = D.problems.filter(p => p.group === g); if (!ps.length) return;
    const b = document.createElement('button');
    b.className = 'fam'; b.type = 'button'; b.setAttribute('role', 'tab'); b.dataset.g = g;
    b.innerHTML = `${label} <span class="k">${ps.length} problems</span>`;
    b.onclick = () => showGroup(g, true);
    fams.appendChild(b);
  });
  function markTile() { atlas.querySelectorAll('.tile').forEach(t => t.setAttribute('aria-selected', t.id === 'tab-' + prob.id)) }
  showGroup(prob.group, false);

  // ---------- table + charts
  function selectProb(p, wantN) {
    prob = p; store.set('ppr-prob', p.id);
    const cur = (fams.querySelector('.fam[aria-selected="true"]') || {}).dataset;
    if (!cur || cur.g !== p.group) showGroup(p.group, false);
    markTile();
    $('ptitle').textContent = ptitle(p);
    $('psub').textContent = `${p.rows.length} of ${D.nmax - D.nmin + 1} values of n (${D.nmin}–${D.nmax}) recorded. ` +
      (p.unit === 'size' ? 's = container size ÷ piece size (the same canonical solid at both sizes).' : 's = container edge ÷ piece edge.') + (p.note ? ' ' + p.note : '');
    const refs = p.rows.filter(r => r.cmp);
    if (p.hasref && refs.length) {
      const g = k => refs.filter(r => r.cmp === k).map(r => r.n);
      const rng = a => a.length ? a.join(', ') : 'none';
      $('lit').innerHTML = `<span><b>Published comparisons</b> (Packing Center and linked coordinate sources) for n = ${refs[0].n}–${refs[refs.length - 1].n}:</span>` +
        `<span class="chip better">better at ${rng(g('better'))}</span><span class="chip">equal at ${rng(g('equal'))}</span><span class="chip behind">behind at ${rng(g('behind'))}</span>`;
    } else $('lit').innerHTML = `<span>No reference values registered yet for this problem. <a href="${ROOT}contribute/">Submit a better packing</a>.</span>`;
    $('thead').innerHTML = '<tr><th>n</th><th>s</th><th>Closed form?</th>' + (p.hasref ? '<th title="Published comparison value; its source is linked in the viewer">Reference</th><th>Compared</th>' : '') +
      '<th>Density</th><th title="(n · volume of a piece / volume of the unit container)^(1/3)">Volume bound</th><th>Proof</th></tr>';
    const tb = $('rows'); tb.innerHTML = '';
    const ncol = p.hasref ? 7 : 5;
    for (let n = D.nmin; n <= D.nmax; n++) {
      const r = p.rows.find(r => r.n === n);
      const tr = document.createElement('tr');
      if (!r) { tr.innerHTML = `<td class="n">${n}</td><td class="pending" colspan="${ncol}">no packing yet</td>`; tr.style.cursor = 'default'; tb.appendChild(tr); continue }
      tr.tabIndex = 0; tr.dataset.n = n;
      tr.innerHTML = `<td class="n">${n}</td><td class="s">${r.s}</td><td class="cf">${r.cf ? fmtCF(r.cf) : ''}</td>` +
        (p.hasref ? `<td class="mut" title="${escapeHTML(r.refsrc || '')}">${r.ref != null ? r.ref.toFixed(5) + (r.refcode && !r.external ? ' ' + r.refcode : '') : ''}</td><td>${chip(r)}</td>` : '') +
        `<td class="mut">${r.den.toFixed(3)}</td><td class="mut">${r.vlb.toFixed(3)}</td>` +
        `<td>${r.ok ? '<span class="tick" title="Exact certificate: CERTIFIED">✓ certified</span>' : r.source_only ? `<span class="mut" title="Source linked; no coordinates or local certificate">${r.author_report ? 'author report' : 'published source'}</span>` : r.ver ? '<span class="tick" title="Floating-point check passed; exact certificate pending">✓ float-checked</span>' : '<span class="cross">pending</span>'}</td>`;
      const open = () => { selectRow(r, true); $('viewer').scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' }) };
      tr.onclick = open; tr.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open() } };
      tb.appendChild(tr);
    }
    if ($('table-scroll-region')) $('table-scroll-region').scrollTop = 0;
    syncTableScroll();
    selectRow(packingInitialSelection(p, hashId, wantN), true);
  }

  function niceStep(range, k) { const raw = range / k, p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p; return (f < 1.5 ? 1 : f < 3.5 ? 2 : f < 7.5 ? 5 : 10) * p }
  function txt(x, y, s, o) { o = o || {}; return `<text x="${x}" y="${y}" font-size="${o.fs || 12}" text-anchor="${o.a || 'start'}" fill="${o.c || css('--muted')}" font-family="${o.f || 'IBM Plex Sans, sans-serif'}"${o.rot ? ` transform="rotate(${o.rot} ${x} ${y})"` : ''}>${s}</text>` }
  function drawChart() { drawS(); drawInc() }
  function dims(box) {
    const el = $(box), W = Math.max(300, Math.round(el.clientWidth || 800));
    return [W, Math.max(240, Math.round(el.clientHeight || W / 2))];
  }
  function drawS() {
    const svg = $('chart'), [W, H] = dims('box1'), L = 62, R = 18, T = 16, B = 62;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    $('c1title').textContent = `s(n) for ${pl(prob.piece)} in ${article(dn(prob.container))}`;
    const rows = prob.rows; if (!rows.length) { svg.innerHTML = ''; return }
    const mut = css('--muted'), rule = css('--rule'), acc = css('--accent'), ex = css('--exact'), sheet = css('--sheet');
    const ys = rows.flatMap(r => [chartScale(r), r.vlb].concat(r.ref != null ? [r.ref] : []));
    const st = niceStep(Math.max(...ys) - Math.min(...ys), 6);
    const y0 = Math.floor(Math.min(...ys) / st) * st, y1 = Math.ceil(Math.max(...ys) / st) * st;
    const X = n => L + (n - D.nmin) / (D.nmax - D.nmin) * (W - L - R), Y = v => T + (1 - (v - y0) / (y1 - y0)) * (H - T - B);
    let g = '';
    for (let v = y0; v <= y1 + st / 2; v += st) g += `<line x1="${L}" x2="${W - R}" y1="${Y(v)}" y2="${Y(v)}" stroke="${rule}" stroke-width="1"/>` + txt(L - 8, Y(v) + 4, v.toFixed(st < 0.1 ? 2 : 1), { a: 'end' });
    const every = W < 700 ? 5 : W < 1000 ? 2 : 1;
    for (let n = D.nmin; n <= D.nmax; n++) {
      g += `<line x1="${X(n)}" x2="${X(n)}" y1="${H - B}" y2="${H - B + 4}" stroke="${mut}" stroke-width="1"/>`;
      if (n % every === 0 || n === D.nmin) g += txt(X(n), H - B + 18, n, { a: 'middle' });
    }
    g += txt((L + W - R) / 2, H - B + 38, 'n (number of pieces)', { a: 'middle' });
    g += txt(16, (T + H - B) / 2, prob.unit === 'size' ? 's = container size ÷ piece size' : 's = container edge ÷ piece edge', { a: 'middle', rot: -90 });
    g += `<polyline points="${rows.map(r => `${X(r.n)},${Y(r.vlb)}`).join(' ')}" fill="none" stroke="${mut}" stroke-width="1.4" stroke-dasharray="5 5"/>`;
    g += `<polyline points="${rows.map(r => `${X(r.n)},${Y(chartScale(r))}`).join(' ')}" fill="none" stroke="${acc}" stroke-width="2.2"/>`;
    rows.filter(r => r.ref != null).forEach(r => { const x = X(r.n), y = Y(r.ref);
      g += `<path d="M${x} ${y - 6}L${x + 6} ${y}L${x} ${y + 6}L${x - 6} ${y}Z" fill="none" stroke="${ex}" stroke-width="1.6"><title>n = ${r.n}: published ${r.ref.toFixed(5)} (${escapeHTML(r.refsrc || SRC[r.refcode] || '')})</title></path>` });
    rows.forEach(r => { const on = row && row.n === r.n;
      g += `<circle cx="${X(r.n)}" cy="${Y(chartScale(r))}" r="${on ? 6.5 : 4}" fill="${on ? acc : sheet}" stroke="${acc}" stroke-width="2" data-n="${r.n}" style="cursor:pointer"><title>n = ${r.n}: s = ${r.s}${r.source_only ? ' (catalogue display)' : ''}</title></circle>` });
    const ly = H - 10; let lx = L;
    g += `<line x1="${lx}" x2="${lx + 22}" y1="${ly - 4}" y2="${ly - 4}" stroke="${acc}" stroke-width="2.2"/>` + txt(lx + 28, ly, 's(n), best found');
    lx += 150; g += `<line x1="${lx}" x2="${lx + 22}" y1="${ly - 4}" y2="${ly - 4}" stroke="${mut}" stroke-width="1.4" stroke-dasharray="5 5"/>` + txt(lx + 28, ly, 'volume bound');
    if (prob.hasref) { lx += 130; g += `<path d="M${lx + 11} ${ly - 10}L${lx + 17} ${ly - 4}L${lx + 11} ${ly + 2}L${lx + 5} ${ly - 4}Z" fill="none" stroke="${ex}" stroke-width="1.6"/>` + txt(lx + 28, ly, 'published reference') }
    svg.innerHTML = g;
    svg.querySelectorAll('circle').forEach(c => c.onclick = () => selectRow(prob.rows.find(r => r.n === +c.dataset.n)));
  }
  function drawInc() {
    const svg = $('chart2'), [W, H] = dims('box2'), L = 62, R = 74, T = 16, B = 62;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const by = {}; prob.rows.forEach(r => by[r.n] = r);
    const inc = [];
    for (let n = D.nmin + 1; n <= D.nmax; n++) if (by[n] && by[n - 1]) {
      const s1 = chartScale(by[n]), s0 = chartScale(by[n - 1]), d = s1 - s0;
      const tolerance = by[n].source_only || by[n - 1].source_only ? 1e-5 : 1e-9 * s1;
      inc.push({ n, pct: 100 * (s1 / s0 - 1), abs: d, zero: Math.abs(d) < tolerance });
    }
    if (!inc.length) { svg.innerHTML = ''; return }
    const mut = css('--muted'), rule = css('--rule'), acc = css('--accent'), ex = css('--exact'), zc = css('--zero');
    const pmax = Math.max(1e-6, ...inc.map(d => d.pct)), amax = Math.max(1e-6, ...inc.map(d => d.abs));
    const ps = niceStep(pmax, 5), as = niceStep(amax, 5);
    const P1 = Math.ceil(pmax / ps) * ps, A1 = Math.ceil(amax / as) * as;
    const n0 = D.nmin + 1, slot = (W - L - R) / (D.nmax - n0 + 1);
    const X = n => L + (n - n0 + 0.5) * slot, YP = v => T + (1 - v / P1) * (H - T - B), YA = v => T + (1 - v / A1) * (H - T - B);
    let g = '';
    inc.filter(d => d.zero).forEach(d => g += `<rect x="${X(d.n) - slot / 2}" y="${T}" width="${slot}" height="${H - T - B}" fill="${zc}" fill-opacity="0.16"><title>n = ${d.n}: no increase over n = ${d.n - 1}</title></rect>`);
    for (let v = 0; v <= P1 + ps / 2; v += ps) g += `<line x1="${L}" x2="${W - R}" y1="${YP(v)}" y2="${YP(v)}" stroke="${rule}" stroke-width="1"/>` + txt(L - 8, YP(v) + 4, (ps < 1 ? v.toFixed(1) : v.toFixed(0)) + '%', { a: 'end' });
    for (let v = 0; v <= A1 + as / 2; v += as) g += `<line x1="${W - R}" x2="${W - R + 4}" y1="${YA(v)}" y2="${YA(v)}" stroke="${ex}" stroke-width="1"/>` + txt(W - R + 8, YA(v) + 4, v.toFixed(as < 0.01 ? 3 : as < 0.1 ? 2 : 1), { c: ex });
    const every = W < 700 ? 5 : W < 1000 ? 2 : 1;
    for (let n = n0; n <= D.nmax; n++) if (n % every === 0 || n === n0) g += txt(X(n), H - B + 18, n, { a: 'middle' });
    g += txt((L + W - R) / 2, H - B + 38, 'n', { a: 'middle' });
    g += txt(16, (T + H - B) / 2, 'Increase over n − 1 (%)', { a: 'middle', rot: -90 });
    g += txt(W - 14, (T + H - B) / 2, 'Increase over n − 1 (absolute)', { a: 'middle', rot: 90, c: ex });
    const bw = Math.max(2, slot * 0.62);
    inc.forEach(d => { const on = row && row.n === d.n, y = YP(Math.max(0, d.pct));
      g += `<rect x="${X(d.n) - bw / 2}" y="${y}" width="${bw}" height="${Math.max(0, YP(0) - y)}" fill="${acc}" fill-opacity="${on ? 1 : 0.62}" data-n="${d.n}" style="cursor:pointer"><title>n = ${d.n}: +${d.pct.toFixed(3)}% (+${d.abs.toFixed(5)})</title></rect>` });
    g += `<line x1="${L}" x2="${W - R}" y1="${YP(0)}" y2="${YP(0)}" stroke="${mut}" stroke-width="1"/>`;
    g += `<polyline points="${inc.map(d => `${X(d.n)},${YA(Math.max(0, d.abs))}`).join(' ')}" fill="none" stroke="${ex}" stroke-width="2"/>`;
    inc.forEach(d => g += `<circle cx="${X(d.n)}" cy="${YA(Math.max(0, d.abs))}" r="3" fill="${ex}"/>`);
    const ly = H - 10; let lx = L;
    g += `<rect x="${lx}" y="${ly - 10}" width="14" height="12" fill="${acc}" fill-opacity="0.62"/>` + txt(lx + 20, ly, '% increase');
    lx += 110; g += `<line x1="${lx}" x2="${lx + 22}" y1="${ly - 4}" y2="${ly - 4}" stroke="${ex}" stroke-width="2"/>` + txt(lx + 28, ly, 'absolute increase');
    lx += 150; g += `<rect x="${lx}" y="${ly - 10}" width="14" height="12" fill="${zc}" fill-opacity="0.25"/>` + txt(lx + 20, ly, `no increase (${inc.filter(d => d.zero).length} of ${inc.length})`);
    svg.innerHTML = g;
    svg.querySelectorAll('rect[data-n]').forEach(c => c.onclick = () => selectRow(prob.rows.find(r => r.n === +c.dataset.n)));
  }

  function selectRow(r) {
    if (!r) return;
    const primary = prob.rows.find(c => c.n === r.n) || r;
    const selection = packingConstructionChoices(primary, r), choices = selection.choices;
    const reference = selection.reference;
    r = selection.row || primary; row = r; sel = null; isolate = false;
    document.querySelectorAll('#rows tr').forEach(t => t.setAttribute('aria-selected', +t.dataset.n === r.n));
    $('cap').innerHTML = `${r.n} ${pl(prob.piece)}, s = ${r.s}` + (r.cf ? ` <span class="cf">≈ ${fmtCF(r.cf)}</span>` : '');
    const id = `${prob.id}_n${pad(r.n)}`;
    const facts = [['Record', escapeHTML(r.id || id)], [r.source_only ? 'Published scale' : 's_full', String(r.sf)]];
    if (!r.source_only) facts.push(['Touching limit', r.st != null ? String(r.st) : '—']);
    if (r.published_sf != null && !r.source_only) facts.push(['Original published scale', String(r.published_sf)]);
    if (r.published_expression) facts.push(['Published expression', escapeHTML(r.published_expression)]);
    if (reference) {
      facts.push([reference.author_report ? 'Reported best' : 'Published best',
        sourceLink(reference.source_url, `${reference.s} · ${reference.source_author || reference.who}`)]);
      facts.push(['Shown in 3D', selection.row ?
        `Coordinate construction at s = ${escapeHTML(r.s)}. The better ${reference.author_report ? 'reported' : 'published'} result has no available coordinates; this view shows a different construction.` :
        'No coordinates are available for this result.']);
    } else if (r.ref != null) facts.push(['Published reference', escapeHTML(`${r.ref} (${r.refsrc})`)]);
    if (!r.source_only) {
      const k = orient(r).sizes.length, sizes = orient(r).sizes;
      facts.push(['Orientations', k === 1 ? 'all pieces are translates of one another' : k === r.n ? `${k}, every piece oriented differently` :
        k <= 8 ? `${k} (${sizes.join(' + ')} pieces)` : `${k} (largest groups: ${sizes.slice(0, 5).join(', ')} pieces)`]);
    }
    facts.push(['Origin', escapeHTML(r.external ? `${r.source_derivation ? 'Source construction credit: ' : 'Published construction by '}${r.source_author || r.who}` : r.who && /published packing/.test(r.who) ? r.who : r.derived ? `record = ${r.derived}` : `found by ${r.who || 'the search'}` + (r.move ? ` (move: ${r.move})` : ''))]);
    const derivation = packingDerivationText(r.source_derivation);
    if (derivation) facts.push(['Derivation', escapeHTML(derivation)]);
    if (r.refined_by) facts.push(['Certificate refinement', escapeHTML(`${r.refined_by}; inherited piece positions and orientations, smaller certified container padding.`)]);
    if (r.source_only) facts.push(['Status', r.author_report ? 'Author-reported result; coordinates and the claimed certificate are unavailable for local verification.' : 'Published source; coordinates and a local certificate are unavailable. The displayed scale retains the catalogue precision.']);
    else if (r.external) facts.push(['Import', r.source_derivation ?
      'Derived coordinates independently certified at the displayed scale; the linked source documents the original construction or bound.' :
      'Coordinates normalized to the common canonical solids and independently certified at the displayed scale.']);
    const issue = r.issue ? submissionIssue(r.issue) : null;
    if (issue) facts.push(['Submitted in', `<a href="${escapeHTML(issue.href)}" target="_blank" rel="noopener">${escapeHTML(issue.pathname.slice(1))}</a>`]);
    if (r.cert.length) facts.push(['Certificate', r.cert.join(' ')]);
    $('facts').innerHTML = facts.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
    const url = `${D.repo}/blob/main/${r.file}`;
    $('links').innerHTML = (r.file ? `<a href="${url}" target="_blank" rel="noopener">Record file (JSON)</a>` +
      (r.ok ? `<a href="${url.replace('.json', '.certify.txt')}" target="_blank" rel="noopener">Exact certificate</a>` : '') +
      `<a href="${url.replace('.json', '.verify.txt')}" target="_blank" rel="noopener">Float check</a>` +
      `<button class="small" type="button" id="copy">Copy coordinates</button><span id="copied"></span>` : '') +
      (packingPublicURL(r.source_url) ? sourceLink(r.source_url, 'Original published construction') : '') +
      (packingPublicURL(r.refurl) && r.refurl !== r.source_url ? sourceLink(r.refurl, 'Published reference') : '') +
      (reference && packingPublicURL(reference.source_url) && reference.source_url !== r.source_url && reference.source_url !== r.refurl ?
        sourceLink(reference.source_url, `${reference.author_report ? 'Reported' : 'Published'} best source`) : '');
    if ($('copy')) $('copy').onclick = copyCoords;
    if (choices.length > 1) {
      $('links').insertAdjacentHTML('beforeend', '<div class="construction-choice"><label for="construction-variant">Construction</label><select id="construction-variant">' +
        choices.map((c, i) => `<option value="${i}"${c.id === r.id ? ' selected' : ''}>${i === 0 ? 'Best with coordinates' : 'Alternative'}: ${escapeHTML(c.who || 'project search')} · ${c.s}${c.ok ? ' (certified)' : c.ver ? ' (float-checked)' : ' (pending)'}</option>`).join('') + '</select></div>');
      $('construction-variant').onchange = e => selectRow(choices[Number(e.target.value)]);
    }
    $('prevn').disabled = !prob.rows.find(x => x.n === r.n - 1); $('nextn').disabled = !prob.rows.find(x => x.n === r.n + 1);
    $('nnow').textContent = `n = ${r.n}`;
    try { history.replaceState(null, '', '#' + id) } catch (e) {}
    $('pick').hidden = true;
    drawChart(); build();
  }
  $('prevn').onclick = () => selectRow(prob.rows.find(x => x.n === row.n - 1));
  $('nextn').onclick = () => selectRow(prob.rows.find(x => x.n === row.n + 1));
  document.addEventListener('keydown', e => {
    if (e.target.closest && e.target.closest('input, textarea, select')) return;
    if (e.key === 'ArrowLeft' && !$('prevn').disabled) { e.preventDefault(); $('prevn').click() }
    if (e.key === 'ArrowRight' && !$('nextn').disabled) { e.preventDefault(); $('nextn').click() }
  });
  const chartResize = new ResizeObserver(() => drawChart());
  ['box1', 'box2'].forEach(id => chartResize.observe($(id)));
  function syncTableScroll() {
    const region = $('table-scroll-region'), range = $('table-scroll');
    if (!region || !range) return;
    const max = Math.max(0, region.scrollHeight - region.clientHeight);
    range.disabled = max === 0;
    range.value = max ? String(100 * region.scrollTop / max) : '0';
    range.setAttribute('aria-valuetext', max ? `${Math.round(Number(range.value))}% through the record table` : 'All records are visible');
  }
  if ($('table-scroll-region') && $('table-scroll')) {
    const region = $('table-scroll-region'), range = $('table-scroll');
    range.addEventListener('input', () => {
      region.scrollTop = Number(range.value) / 100 * Math.max(0, region.scrollHeight - region.clientHeight);
      syncTableScroll();
    });
    region.addEventListener('scroll', syncTableScroll, { passive: true });
    const tableResize = new ResizeObserver(syncTableScroll);
    tableResize.observe(region);
    tableResize.observe($('rows'));
  }
  async function copyCoords() {
    const selected = row, problem = prob, button = $('copy'), status = $('copied');
    if (!selected || !selected.file) return;
    if (button) button.disabled = true;
    if (status) status.textContent = 'Loading full-precision JSON…';
    try {
      const text = await packingFullPrecisionRecord(D.repo, selected, problem, DATA_VERSION);
      await navigator.clipboard.writeText(text);
      if (status) status.textContent = 'Copied full-precision JSON';
    } catch (e) {
      if (status) status.textContent = 'Could not copy full-precision JSON. Use Record file (JSON).';
    } finally { if (button) button.disabled = false }
  }

  // ---------- 3D
  const stage = $('stage'), cv = $('cv');
  let renderer, scene, camera, world, contLines, contFaces, pieceObjs = [], R0 = 3, zoom = 1;
  const hasGL = typeof THREE !== 'undefined' && (() => { try { return !!document.createElement('canvas').getContext('webgl') } catch (e) { return false } })();
  if (hasGL) {
    renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(32, 1, 0.01, 1000);
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const l1 = new THREE.DirectionalLight(0xffffff, 0.75); l1.position.set(3, 5, 6); scene.add(l1);
    const l2 = new THREE.DirectionalLight(0xffffff, 0.3); l2.position.set(-4, -2, -3); scene.add(l2);
    world = new THREE.Group(); scene.add(world);
  } else { cv.hidden = true; stage.insertAdjacentHTML('beforeend', '<p class="meta" id="webgl-note" style="padding:18px">The 3D view needs WebGL and the three.js script, which did not load. The table, charts and record links still work.</p>') }

  function solidGeom(name) {
    const S = D.solids[name], pos = [];
    S.F.forEach(f => { for (let i = 1; i + 1 < f.length; i++) [f[0], f[i], f[i + 1]].forEach(k => pos.push(...S.V[k])) });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
    const eg = edgeGeom(S);
    return { g, eg };
  }
  // WebGL ignores LineBasicMaterial.linewidth on most platforms. Each edge is
  // therefore two camera-facing triangles, expanded in clip space by CSS pixels.
  // The geometry remains attached to its piece, so rotation/spread/slicing and
  // opacity behave exactly like the surface without rebuilding on width changes.
  function edgeGeom(S) {
    const pos = [], starts = [], ends = [];
    const corners = [[0, -1], [1, -1], [1, 1], [0, -1], [1, 1], [0, 1]];
    S.E.forEach(([a, b]) => corners.forEach(([along, side]) => {
      pos.push(along, side, 0); starts.push(...S.V[a]); ends.push(...S.V[b]);
    }));
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('edgeStart', new THREE.Float32BufferAttribute(starts, 3));
    g.setAttribute('edgeEnd', new THREE.Float32BufferAttribute(ends, 3));
    return g;
  }
  function edgeMaterial(colour) {
    return new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
      uniforms: { lineColour: { value: new THREE.Color(colour) }, lineOpacity: { value: 1 },
        lineWidth: { value: edgeWidth }, viewport: { value: new THREE.Vector2(1, 1) } },
      vertexShader: `
        attribute vec3 edgeStart;
        attribute vec3 edgeEnd;
        uniform vec2 viewport;
        uniform float lineWidth;
        void main() {
          vec4 a = projectionMatrix * modelViewMatrix * vec4(edgeStart, 1.0);
          vec4 b = projectionMatrix * modelViewMatrix * vec4(edgeEnd, 1.0);
          // Trim against the near plane before dividing by w when zooming in.
          float da = a.z + a.w, db = b.z + b.w;
          if (da < 0.0 && db < 0.0) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); return; }
          if (da < 0.0) a = mix(a, b, da / (da - db));
          else if (db < 0.0) b = mix(b, a, db / (db - da));
          vec2 screenDelta = (b.xy / b.w - a.xy / a.w) * viewport;
          vec2 tangent = screenDelta / max(length(screenDelta), 0.0001);
          vec2 normal = vec2(-tangent.y, tangent.x);
          vec4 point = mix(a, b, position.x);
          vec2 offset = (normal * position.y + tangent * (position.x * 2.0 - 1.0)) * lineWidth / viewport;
          point.xy += offset * point.w;
          gl_Position = point;
        }`,
      fragmentShader: `
        uniform vec3 lineColour;
        uniform float lineOpacity;
        void main() { gl_FragColor = vec4(lineColour, lineOpacity); }`
    });
  }
  function darkTheme() {
    const theme = document.documentElement.dataset.theme;
    if (theme === 'dark' || theme === 'light') return theme === 'dark';
    return matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function edgeColour(i) { return edgeMode === 'contrast' ? (darkTheme() ? '#ffffff' : '#000000') : pieceColour(i) }
  function updateEdges() {
    pieceObjs.forEach(g => {
      const u = g.userData.edges.material.uniforms;
      u.lineColour.value.set(edgeColour(g.userData.i));
      u.lineWidth.value = edgeWidth;
      u.viewport.value.set(stage.clientWidth || 400, stage.clientHeight || stage.clientWidth || 400);
    });
  }
  function updateEdgeControls() {
    const button = $('edge-mode'), range = $('edge-width'), output = $('edge-width-value');
    if (button) {
      button.setAttribute('aria-pressed', String(edgeMode === 'contrast'));
      button.textContent = edgeMode === 'contrast' ? `Edges: ${darkTheme() ? 'white' : 'black'}` : 'Edges: piece colour';
      button.title = edgeMode === 'contrast' ? 'Switch edges to the colour of each piece' : `Switch edges to ${darkTheme() ? 'white' : 'black'}`;
    }
    if (range) range.value = String(edgeWidth);
    if (output) output.value = `${edgeWidth.toFixed(1)} px`;
  }
  function pieceColour(i) {
    if (colMode === 'index') return PAL[i % PAL.length];
    if (colMode === 'orient') return PAL[orient(row).cls[i] % PAL.length];
    const zs = row.p.map(p => p[axis]), lo = Math.min(...zs), hi = Math.max(...zs), t = hi > lo ? (row.p[i][axis] - lo) / (hi - lo) : 0.5;
    const a = new THREE.Color('#3557b8'), b = new THREE.Color('#3f9a6a'), c = new THREE.Color('#d9822b');
    return '#' + (t < 0.5 ? a.lerp(b, t * 2) : b.clone().lerp(c, (t - 0.5) * 2)).getHexString();
  }
  function legend() {
    const el = $('legend'); if (!row) { el.innerHTML = ''; return }
    if (colMode === 'orient') { const oc = orient(row);
      el.innerHTML = oc.sizes.slice(0, 8).map((s, k) => `<span><i style="background:${PAL[k % PAL.length]}"></i>${s}</span>`).join('') + (oc.sizes.length > 8 ? `<span>+${oc.sizes.length - 8} more</span>` : '');
    } else if (colMode === 'height') el.innerHTML = `<span><i style="background:#3557b8"></i>low ${'xyz'[axis]}</span><span><i style="background:#d9822b"></i>high ${'xyz'[axis]}</span>`;
    else el.innerHTML = '';
  }
  function build() {
    const sourceOnly = !!(row && row.source_only);
    cv.hidden = sourceOnly || !hasGL;
    stage.querySelector('.views').hidden = sourceOnly || !hasGL;
    stage.querySelector('.hint').hidden = sourceOnly || !hasGL;
    $('viewer').querySelector('.tools').hidden = sourceOnly;
    if ($('webgl-note')) $('webgl-note').hidden = sourceOnly;
    $('geometry-note').hidden = !sourceOnly;
    if (!sourceOnly) legend();
    if (!hasGL || !row) return;
    const oldGeometry = new Set(), oldMaterials = new Set();
    world.traverse(obj => {
      if (obj.geometry) oldGeometry.add(obj.geometry);
      if (obj.material) (Array.isArray(obj.material) ? obj.material : [obj.material]).forEach(m => oldMaterials.add(m));
    });
    while (world.children.length) world.remove(world.children[0]);
    oldGeometry.forEach(g => g.dispose()); oldMaterials.forEach(m => m.dispose());
    pieceObjs = [];
    contLines = null; contFaces = null;
    if (sourceOnly) return;
    const C = D.solids[prob.container], piece = solidGeom(prob.piece);
    const cp = []; C.E.forEach(([a, b]) => cp.push(...C.V[a].map(x => x * row.sf), ...C.V[b].map(x => x * row.sf)));
    const cg = new THREE.BufferGeometry(); cg.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3));
    contLines = new THREE.LineSegments(cg, new THREE.LineBasicMaterial({ color: new THREE.Color(css('--ink')), transparent: true, opacity: 0.85 }));
    world.add(contLines);
    const containerGeometry = solidGeom(prob.container);
    containerGeometry.eg.dispose();
    contFaces = new THREE.Mesh(containerGeometry.g, new THREE.MeshBasicMaterial({ color: new THREE.Color(css('--accent')), transparent: true, opacity: 0.07, side: THREE.DoubleSide, depthWrite: false }));
    contFaces.scale.setScalar(row.sf); world.add(contFaces);
    row.p.forEach((p, i) => {
      const grp = new THREE.Group();
      const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(pieceColour(i)), flatShading: true, roughness: 0.55, metalness: 0.05,
        polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1, transparent: true, opacity: 1 });
      const mesh = new THREE.Mesh(piece.g, mat); mesh.userData.i = i;
      const edges = new THREE.Mesh(piece.eg, edgeMaterial(edgeColour(i)));
      edges.frustumCulled = false;
      grp.add(mesh); grp.add(edges);
      const [qw, qx, qy, qz] = qn(p);
      grp.quaternion.set(qx, qy, qz, qw); grp.userData = { c: new THREE.Vector3(p[0], p[1], p[2]), mesh, edges, i };
      world.add(grp); pieceObjs.push(grp);
    });
    R0 = Math.max(...C.V.map(v => Math.hypot(...v))) * row.sf;
    applyVisibility(); applySpread(); fit(); paint();
  }
  function applyVisibility() {
    if (!row || row.source_only) return;
    const t = +$('cut').value, zs = row.p.map(p => p[axis]), lo = Math.min(...zs), hi = Math.max(...zs), lev = lo + t * (hi - lo) + 1e-9;
    const ghost = $('ghost').checked;
    let keep = null;
    if (sel != null && isolate) { const rc = 2 * circ(prob.piece) + 1e-6; keep = new Set([sel, ...neighbours(row, sel).filter(x => x[1] < rc).map(x => x[0])]) }
    let shown = 0;
    pieceObjs.forEach(g => {
      const i = g.userData.i, vis = row.p[i][axis] <= lev && (!keep || keep.has(i));
      if (vis) shown++;
      const m = g.userData.mesh.material;
      g.visible = vis || ghost;
      const dim = vis && sel != null && !isolate && i !== sel;
      const op = +$('opac').value;
      m.opacity = vis ? (dim ? 0.3 * op : op) : 0.07; m.depthWrite = vis && !dim && op > 0.99; g.userData.edges.visible = vis;
      g.userData.edges.material.uniforms.lineOpacity.value = dim ? 0.35 * op : 0.6 + 0.4 * op;
      m.emissive.set(i === sel ? css('--accent') : '#000000'); m.emissiveIntensity = i === sel ? 0.45 : 0;
      m.needsUpdate = true;
    });
    if (contFaces) contFaces.visible = $('faces').checked;
    $('cutinfo').textContent = `${shown} of ${row.p.length} shown`;
    paint();
  }
  function applySpread() { const k = +$('explode').value; pieceObjs.forEach(g => g.position.copy(g.userData.c).multiplyScalar(k)) }
  function fit() {
    if (!hasGL) return;
    const w = stage.clientWidth || 400, hgt = stage.clientHeight || w; renderer.setSize(w, hgt, false); camera.aspect = w / hgt; camera.updateProjectionMatrix();
    updateEdges();
    const k = +$('explode').value;
    const half = Math.min(16, THREE.MathUtils.radToDeg(Math.atan(Math.tan(THREE.MathUtils.degToRad(16)) * camera.aspect)));
    camera.position.set(0, 0, (R0 * Math.max(1, 0.55 + 0.45 * k)) / Math.sin(THREE.MathUtils.degToRad(half)) * 1.04 / zoom); camera.lookAt(0, 0, 0);
  }
  function paint() { if (!hasGL) return; scene.background = new THREE.Color(css('--sheet')); if (contLines) contLines.material.color.set(css('--ink')); renderer.render(scene, camera) }
  const RESET = () => { if (!hasGL) return; world.quaternion.setFromEuler(new THREE.Euler(-0.5, 0.6, 0.05)); paint() };
  function setView(v) {
    if (!hasGL) return;
    if (v === 'r') { zoom = 1; $('explode').value = 1; applySpread(); fit(); RESET(); return }
    const from = { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1], d: [1, 1, 1] }[v];
    world.quaternion.setFromUnitVectors(new THREE.Vector3(...from).normalize(), new THREE.Vector3(0, 0, 1));
    $('spin').checked = false; paint();
  }
  document.querySelectorAll('.views button').forEach(b => b.onclick = () => setView(b.dataset.view));

  function showPick() {
    const el = $('pick');
    if (sel == null) { el.hidden = true; return }
    const p = row.p[sel], nb = neighbours(row, sel).slice(0, 4), oc = orient(row);
    el.hidden = false;
    el.innerHTML = `<div><b>Piece ${sel + 1}</b> of ${row.p.length}, orientation class ${oc.cls[sel] < 26 ? String.fromCharCode(65 + oc.cls[sel]) : oc.cls[sel] + 1} (${oc.sizes[oc.cls[sel]]} piece${oc.sizes[oc.cls[sel]] > 1 ? 's' : ''})</div>` +
      `<div class="meta">centre (${p.slice(0, 3).map(v => v.toFixed(4)).join(', ')})   q = (${qn(p).map(v => v.toFixed(4)).join(', ')})</div>` +
      `<div class="meta">nearest centres: ${nb.map(([j, d]) => `#${j + 1} at ${d.toFixed(4)}`).join(', ')}</div>` +
      `<div class="trow"><label class="inl" for="iso"><input type="checkbox" id="iso" ${isolate ? 'checked' : ''}> isolate this piece and its possible contacts</label>` +
      `<button class="small" type="button" id="unpick">Clear</button></div>`;
    $('iso').onchange = e => { isolate = e.target.checked; applyVisibility() };
    $('unpick').onclick = () => { sel = null; isolate = false; showPick(); applyVisibility() };
  }
  function pressSeg(id, attr, val) { document.querySelectorAll(`#${id} button`).forEach(b => b.setAttribute('aria-pressed', b.dataset[attr] === String(val))) }
  pressSeg('colmode', 'm', colMode);
  document.querySelectorAll('#colmode button').forEach(b => b.onclick = () => { colMode = b.dataset.m; store.set('ppr-col', colMode); pressSeg('colmode', 'm', colMode); build() });
  document.querySelectorAll('#axis button').forEach(b => b.onclick = () => { axis = +b.dataset.a; pressSeg('axis', 'a', axis); if (colMode === 'height') build(); else applyVisibility() });
  $('cut').oninput = () => applyVisibility();
  { const o = parseFloat(store.get('ppr-opac')); if (o >= 0.1 && o <= 1) $('opac').value = o }
  $('opac').oninput = () => { store.set('ppr-opac', $('opac').value); applyVisibility() };
  $('ghost').onchange = () => applyVisibility();
  $('faces').onchange = () => applyVisibility();
  updateEdgeControls();
  if ($('edge-mode')) $('edge-mode').onclick = () => {
    edgeMode = edgeMode === 'piece' ? 'contrast' : 'piece';
    store.set('ppr-edge-mode', edgeMode); updateEdgeControls(); updateEdges(); paint();
  };
  if ($('edge-width')) $('edge-width').oninput = e => {
    edgeWidth = Math.min(6, Math.max(0.5, Number(e.target.value)));
    store.set('ppr-edge-width', String(edgeWidth)); updateEdgeControls(); updateEdges(); paint();
  };

  if (hasGL) {
    RESET();
    const ptrs = new Map(); let downAt = null, moved = 0, pinch0 = null;
    stage.addEventListener('pointerdown', e => {
      if (row && row.source_only || e.target.closest('.views')) return;
      ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); stage.setPointerCapture(e.pointerId);
      if (ptrs.size === 1) { downAt = { x: e.clientX, y: e.clientY }; moved = 0 }
      if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch0 = { d: Math.hypot(a.x - b.x, a.y - b.y), z: zoom } }
    });
    stage.addEventListener('pointermove', e => {
      const prev = ptrs.get(e.pointerId); if (!prev) return;
      const dx = e.clientX - prev.x, dy = e.clientY - prev.y; ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); moved += Math.abs(dx) + Math.abs(dy);
      if (ptrs.size === 2 && pinch0) { const [a, b] = [...ptrs.values()]; zoom = Math.min(6, Math.max(0.5, pinch0.z * Math.hypot(a.x - b.x, a.y - b.y) / pinch0.d)); fit(); paint(); return }
      if (ptrs.size === 1) { world.quaternion.premultiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(dy * 0.01, dx * 0.01, 0))); paint() }
    });
    const end = e => {
      const was = ptrs.has(e.pointerId); ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch0 = null;
      if (was && e.type === 'pointerup' && ptrs.size === 0 && moved < 6 && downAt) pickAt(e.clientX, e.clientY);
    };
    stage.addEventListener('pointerup', end); stage.addEventListener('pointercancel', end);
    stage.addEventListener('wheel', e => { if (row && row.source_only) return; e.preventDefault(); zoom = Math.min(6, Math.max(0.5, zoom * Math.exp(-e.deltaY * 0.0015))); fit(); paint() }, { passive: false });
    const ray = new THREE.Raycaster();
    function pickAt(x, y) {
      const r = cv.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1), camera);
      const hits = ray.intersectObjects(pieceObjs.filter(g => g.visible && g.userData.edges.visible).map(g => g.userData.mesh));
      const i = hits.length ? hits[0].object.userData.i : null;
      sel = (i === sel) ? null : i; if (sel == null) isolate = false;
      showPick(); applyVisibility();
    }
    $('explode').oninput = () => { applySpread(); fit(); paint() };
    const spin = $('spin');
    spin.checked = !reduceMotion() && store.get('ppr-spin') === '1';
    spin.onchange = () => store.set('ppr-spin', spin.checked ? '1' : '0');
    let last = performance.now();
    (function loop(t) { const dt = Math.min(50, t - last); last = t;
      if (spin.checked && ptrs.size === 0 && !(row && row.source_only)) { world.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), dt * 0.00025)); paint() }
      requestAnimationFrame(loop) })(last);
    new ResizeObserver(() => { fit(); paint() }).observe(stage);
  }
  const repaintAll = () => {
    updateEdgeControls(); updateEdges();
    if (contFaces) contFaces.material.color.set(css('--accent'));
    applyVisibility(); paint(); drawChart();
    atlas.querySelectorAll('.tile').forEach(t => { const p = D.problems.find(q => 'tab-' + q.id === t.id); if (p) thumb(t.querySelector('canvas'), p) });
  };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', repaintAll);
  document.addEventListener('ppr-themechange', repaintAll);
  new MutationObserver(repaintAll).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  addEventListener('hashchange', () => {
    const match = /^([a-z0-9]+)_n(\d+)$/.exec(location.hash.slice(1));
    if (!match) return;
    const p = D.problems.find(p => p.id === match[1]);
    if (!p) return;
    if (p !== prob) selectProb(p, Number(match[2]));
    else selectRow(p.rows.find(r => r.n === Number(match[2])));
  });
  selectProb(prob);
})();
