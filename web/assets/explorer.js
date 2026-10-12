// Record explorer for polyhedrainpolyhedra.wiki: families, atlas of problems, 3D viewer (three.js r128), table, charts.
// Data: window.PP_DATA (inlined copy) or data/records.json next to the page (see scripts/site.py).
(async () => {
  const $ = id => document.getElementById(id);
  const ROOT = document.documentElement.dataset.root || './';
  let D = window.PP_DATA;
  if (!D) {
    try { D = await (await fetch(ROOT + 'data/records.json')).json() }
    catch (e) { $('ptitle').textContent = 'The record data did not load. Reload the page, or browse the records on GitHub.'; return }
  }
  const NAMES = { tetrahedron: ['tetrahedron', 'tetrahedra'], cube: ['cube', 'cubes'], octahedron: ['octahedron', 'octahedra'],
                  dodecahedron: ['dodecahedron', 'dodecahedra'], icosahedron: ['icosahedron', 'icosahedra'] };
  const SRC = { F: 'E. Friedman 1998', W: 'R. Walsh 2026', L: 'H. Lin 2026', N: 'Y. Nakajima 2026', T: 'trivial grid' };
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const store = { get(k) { try { return localStorage.getItem(k) } catch (e) { return null } }, set(k, v) { try { localStorage.setItem(k, v) } catch (e) {} } };
  const hashId = location.hash.slice(1);
  let prob = D.problems.find(p => p.id === hashId.split('_')[0]) || D.problems.find(p => p.id === store.get('ppr-prob')) || D.problems[0];
  let row = null, sel = null, isolate = false;
  let colMode = store.get('ppr-col') || 'orient', axis = 2;
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
  function chip(r) {
    if (r.cmp == null) return '';
    if (r.cmp === 'better') return `<span class="chip better" title="More than 1e-5 below the published value">better by ${(-pct(r)).toFixed(2)}%</span>`;
    if (r.cmp === 'equal') return '<span class="chip">equal</span>';
    return `<span class="chip behind">+${pct(r)}%</span>`;
  }

  // ---------- geometry helpers
  function qn(p) { const q = [p[3], p[4], p[5], p[6]], m = Math.hypot(...q); return q.map(v => v / m) }
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
  const GROUPS = [['platonic', 'Platonic', [['platonic', '']]], ['archcat', 'Archimedean and Catalan', [['archimedean', 'Archimedean solids'], ['catalan', 'Catalan solids']]],
                  ['prisms', 'Prisms and antiprisms', [['prisms', '']]]];
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
    grp[2].forEach(([fam, head]) => {
      const ps = D.problems.filter(p => p.family === fam); if (!ps.length) return;
      if (head) { const h = document.createElement('h2'); h.textContent = head; atlas.appendChild(h) }
      const box = document.createElement('div'); box.className = 'tiles'; box.setAttribute('role', 'tablist'); box.setAttribute('aria-label', head || grp[1]);
      ps.forEach(p => {
        const b = document.createElement('button'); b.className = 'tile'; b.type = 'button'; b.setAttribute('role', 'tab'); b.id = 'tab-' + p.id;
        const cv = document.createElement('canvas'); cv.setAttribute('aria-hidden', 'true');
        const best = p.rows.length ? p.rows[p.rows.length - 1] : null;
        b.innerHTML = `<span><span class="t">${ptitle(p)}</span><span class="m" style="display:block">${p.rows.length} of ${D.nmax - D.nmin + 1} values` +
          (p.hasref ? ', published values' : '') + `</span></span>`;
        b.prepend(cv); thumb(cv, p);
        b.onclick = () => { selectProb(p); $('viewer').scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' }) };
        box.appendChild(b);
      });
      atlas.appendChild(box);
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
      $('lit').innerHTML = `<span><b>Published values</b> (Erich Friedman's Packing Center) for n = ${refs[0].n}–${refs[refs.length - 1].n}:</span>` +
        `<span class="chip better">better at ${rng(g('better'))}</span><span class="chip">equal at ${rng(g('equal'))}</span><span class="chip behind">behind at ${rng(g('behind'))}</span>`;
    } else $('lit').innerHTML = `<span>No published values were found for this problem. <a href="${ROOT}contribute/">Submit a better packing</a>.</span>`;
    $('thead').innerHTML = '<tr><th>n</th><th>s</th><th>Closed form?</th>' + (p.hasref ? '<th title="Best previously published value">Previous</th><th>Compared</th>' : '') +
      '<th>Density</th><th title="(n · volume of a piece / volume of the unit container)^(1/3)">Volume bound</th><th>Proof</th></tr>';
    const tb = $('rows'); tb.innerHTML = '';
    const ncol = p.hasref ? 7 : 5;
    for (let n = D.nmin; n <= D.nmax; n++) {
      const r = p.rows.find(r => r.n === n);
      const tr = document.createElement('tr');
      if (!r) { tr.innerHTML = `<td class="n">${n}</td><td class="pending" colspan="${ncol}">no packing yet</td>`; tr.style.cursor = 'default'; tb.appendChild(tr); continue }
      tr.tabIndex = 0; tr.dataset.n = n;
      tr.innerHTML = `<td class="n">${n}</td><td class="s">${r.s}</td><td class="cf">${r.cf ? fmtCF(r.cf) : ''}</td>` +
        (p.hasref ? `<td class="mut" title="${r.refsrc || ''}">${r.ref != null ? r.ref.toFixed(5) + ' ' + r.refcode : ''}</td><td>${chip(r)}</td>` : '') +
        `<td class="mut">${r.den.toFixed(3)}</td><td class="mut">${r.vlb.toFixed(3)}</td>` +
        `<td>${r.ok ? '<span class="tick" title="Exact certificate: CERTIFIED">✓ certified</span>' : r.ver ? '<span class="tick" title="Floating-point check passed; exact certificate pending">✓ float-checked</span>' : '<span class="cross">pending</span>'}</td>`;
      const open = () => { selectRow(r, true); $('viewer').scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' }) };
      tr.onclick = open; tr.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open() } };
      tb.appendChild(tr);
    }
    const want = wantN || +((hashId.split('_n')[1]) || 0);
    selectRow(p.rows.find(r => r.n === want) || p.rows.find(r => r.n === 12) || p.rows[p.rows.length - 1], true);
  }

  function niceStep(range, k) { const raw = range / k, p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p; return (f < 1.5 ? 1 : f < 3.5 ? 2 : f < 7.5 ? 5 : 10) * p }
  function txt(x, y, s, o) { o = o || {}; return `<text x="${x}" y="${y}" font-size="${o.fs || 12}" text-anchor="${o.a || 'start'}" fill="${o.c || css('--muted')}" font-family="${o.f || 'IBM Plex Sans, sans-serif'}"${o.rot ? ` transform="rotate(${o.rot} ${x} ${y})"` : ''}>${s}</text>` }
  function drawChart() { drawS(); drawInc() }
  function dims(box) { const W = Math.max(300, Math.round($(box).clientWidth || 800)); return [W, Math.round(W / 2)] }
  function drawS() {
    const svg = $('chart'), [W, H] = dims('box1'), L = 62, R = 18, T = 16, B = 62;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    $('c1title').textContent = `s(n) for ${pl(prob.piece)} in ${article(dn(prob.container))}`;
    const rows = prob.rows; if (!rows.length) { svg.innerHTML = ''; return }
    const mut = css('--muted'), rule = css('--rule'), acc = css('--accent'), ex = css('--exact'), sheet = css('--sheet');
    const ys = rows.flatMap(r => [r.sf, r.vlb].concat(r.ref != null ? [r.ref] : []));
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
    g += `<polyline points="${rows.map(r => `${X(r.n)},${Y(r.sf)}`).join(' ')}" fill="none" stroke="${acc}" stroke-width="2.2"/>`;
    rows.filter(r => r.ref != null).forEach(r => { const x = X(r.n), y = Y(r.ref);
      g += `<path d="M${x} ${y - 6}L${x + 6} ${y}L${x} ${y + 6}L${x - 6} ${y}Z" fill="none" stroke="${ex}" stroke-width="1.6"><title>n = ${r.n}: published ${r.ref.toFixed(5)} (${SRC[r.refcode]})</title></path>` });
    rows.forEach(r => { const on = row && row.n === r.n;
      g += `<circle cx="${X(r.n)}" cy="${Y(r.sf)}" r="${on ? 6.5 : 4}" fill="${on ? acc : sheet}" stroke="${acc}" stroke-width="2" data-n="${r.n}" style="cursor:pointer"><title>n = ${r.n}: s = ${r.s}</title></circle>` });
    const ly = H - 10; let lx = L;
    g += `<line x1="${lx}" x2="${lx + 22}" y1="${ly - 4}" y2="${ly - 4}" stroke="${acc}" stroke-width="2.2"/>` + txt(lx + 28, ly, 's(n), best found');
    lx += 150; g += `<line x1="${lx}" x2="${lx + 22}" y1="${ly - 4}" y2="${ly - 4}" stroke="${mut}" stroke-width="1.4" stroke-dasharray="5 5"/>` + txt(lx + 28, ly, 'volume bound');
    if (prob.hasref) { lx += 130; g += `<path d="M${lx + 11} ${ly - 10}L${lx + 17} ${ly - 4}L${lx + 11} ${ly + 2}L${lx + 5} ${ly - 4}Z" fill="none" stroke="${ex}" stroke-width="1.6"/>` + txt(lx + 28, ly, 'published (Friedman\'s Packing Center)') }
    svg.innerHTML = g;
    svg.querySelectorAll('circle').forEach(c => c.onclick = () => selectRow(prob.rows.find(r => r.n === +c.dataset.n)));
  }
  function drawInc() {
    const svg = $('chart2'), [W, H] = dims('box2'), L = 62, R = 74, T = 16, B = 62;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const by = {}; prob.rows.forEach(r => by[r.n] = r);
    const inc = [];
    for (let n = D.nmin + 1; n <= D.nmax; n++) if (by[n] && by[n - 1]) {
      const s1 = by[n].st ?? by[n].sf, s0 = by[n - 1].st ?? by[n - 1].sf, d = s1 - s0;
      inc.push({ n, pct: 100 * (s1 / s0 - 1), abs: d, zero: Math.abs(d) < 1e-9 * s1 });
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
    if (!r) return; row = r; sel = null; isolate = false;
    document.querySelectorAll('#rows tr').forEach(t => t.setAttribute('aria-selected', +t.dataset.n === r.n));
    $('cap').innerHTML = `${r.n} ${pl(prob.piece)}, s = ${r.s}` + (r.cf ? ` <span class="cf">≈ ${fmtCF(r.cf)}</span>` : '');
    const oc = orient(r), id = `${prob.id}_n${pad(r.n)}`;
    const facts = [['Record', id], ['s_full', String(r.sf)], ['Touching limit', r.st != null ? String(r.st) : '—']];
    if (r.ref != null) facts.push(['Published', `${r.ref} (${r.refsrc})`]);
    facts.push(['Orientations', `${oc.sizes.length} (${oc.sizes.join(' + ')} pieces)`]);
    facts.push(['Origin', r.who && /published packing/.test(r.who) ? r.who : r.derived ? `record = ${r.derived}` : `found by ${r.who || 'the search'}` + (r.move ? ` (move: ${r.move})` : '')]);
    if (r.issue) facts.push(['Submitted in', `<a href="${r.issue}" target="_blank" rel="noopener">${r.issue.replace(/^https:\/\/github.com\//, '')}</a>`]);
    if (r.cert.length) facts.push(['Certificate', r.cert.join(' ')]);
    $('facts').innerHTML = facts.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
    const url = `${D.repo}/blob/main/${r.file}`;
    $('links').innerHTML = `<a href="${url}" target="_blank" rel="noopener">Record file (JSON)</a>` +
      (r.ok ? `<a href="${url.replace('.json', '.certify.txt')}" target="_blank" rel="noopener">Exact certificate</a>` : '') +
      `<a href="${url.replace('.json', '.verify.txt')}" target="_blank" rel="noopener">Float check</a>` +
      `<button class="small" type="button" id="copy">Copy coordinates</button><span id="copied"></span>`;
    $('copy').onclick = copyCoords;
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
  new ResizeObserver(() => drawChart()).observe($('box1'));
  function copyCoords() {
    const t = JSON.stringify({ record_id: `${prob.id}_n${pad(row.n)}`, piece: prob.piece, container: prob.container, n: row.n, s_full: row.sf,
      format: '[x, y, z, qw, qx, qy, qz] per piece (rounded to 7 decimals; full precision in the record file); container = s_full x canonical container centred at the origin',
      pieces: row.p });
    const done = ok => { $('copied').textContent = ok ? 'Copied' : 'Copy from the record file instead' };
    try { navigator.clipboard.writeText(t).then(() => done(true), () => done(false)) } catch (e) { done(false) }
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
  } else { stage.innerHTML = '<p class="meta" style="padding:18px">The 3D view needs WebGL and the three.js script, which did not load. The table, charts and record links still work.</p>' }

  function solidGeom(name) {
    const S = D.solids[name], pos = [];
    S.F.forEach(f => { for (let i = 1; i + 1 < f.length; i++) [f[0], f[i], f[i + 1]].forEach(k => pos.push(...S.V[k])) });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
    const ep = []; S.E.forEach(([a, b]) => ep.push(...S.V[a], ...S.V[b]));
    const eg = new THREE.BufferGeometry(); eg.setAttribute('position', new THREE.Float32BufferAttribute(ep, 3));
    return { g, eg };
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
    legend();
    if (!hasGL || !row) return;
    while (world.children.length) world.remove(world.children[0]);
    pieceObjs = [];
    const C = D.solids[prob.container], piece = solidGeom(prob.piece);
    const cp = []; C.E.forEach(([a, b]) => cp.push(...C.V[a].map(x => x * row.sf), ...C.V[b].map(x => x * row.sf)));
    const cg = new THREE.BufferGeometry(); cg.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3));
    contLines = new THREE.LineSegments(cg, new THREE.LineBasicMaterial({ color: new THREE.Color(css('--ink')), transparent: true, opacity: 0.85 }));
    world.add(contLines);
    contFaces = new THREE.Mesh(solidGeom(prob.container).g, new THREE.MeshBasicMaterial({ color: new THREE.Color(css('--accent')), transparent: true, opacity: 0.07, side: THREE.DoubleSide, depthWrite: false }));
    contFaces.scale.setScalar(row.sf); world.add(contFaces);
    row.p.forEach((p, i) => {
      const grp = new THREE.Group();
      const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(pieceColour(i)), flatShading: true, roughness: 0.55, metalness: 0.05,
        polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1, transparent: true, opacity: 1 });
      const mesh = new THREE.Mesh(piece.g, mat); mesh.userData.i = i;
      const edges = new THREE.LineSegments(piece.eg, new THREE.LineBasicMaterial({ color: 0x10181b, transparent: true, opacity: 0.55 }));
      grp.add(mesh); grp.add(edges);
      grp.quaternion.copy(new THREE.Quaternion(p[4], p[5], p[6], p[3]).normalize()); grp.userData = { c: new THREE.Vector3(p[0], p[1], p[2]), mesh, edges, i };
      world.add(grp); pieceObjs.push(grp);
    });
    R0 = Math.max(...C.V.map(v => Math.hypot(...v))) * row.sf;
    applyVisibility(); applySpread(); fit(); paint();
  }
  function applyVisibility() {
    if (!row) return;
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
      m.opacity = vis ? (dim ? 0.3 : 1) : 0.07; m.depthWrite = vis && !dim; g.userData.edges.visible = vis;
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
  $('ghost').onchange = () => applyVisibility();
  $('faces').onchange = () => applyVisibility();

  if (hasGL) {
    RESET();
    const ptrs = new Map(); let downAt = null, moved = 0, pinch0 = null;
    stage.addEventListener('pointerdown', e => {
      if (e.target.closest('.views')) return;
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
    stage.addEventListener('wheel', e => { e.preventDefault(); zoom = Math.min(6, Math.max(0.5, zoom * Math.exp(-e.deltaY * 0.0015))); fit(); paint() }, { passive: false });
    const ray = new THREE.Raycaster();
    function pickAt(x, y) {
      const r = cv.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1), camera);
      const hits = ray.intersectObjects(pieceObjs.filter(g => g.visible && g.userData.mesh.material.opacity > 0.5).map(g => g.userData.mesh));
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
      if (spin.checked && ptrs.size === 0) { world.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), dt * 0.00025)); paint() }
      requestAnimationFrame(loop) })(last);
    new ResizeObserver(() => { fit(); paint() }).observe(stage);
  }
  const repaintAll = () => { build(); drawChart(); atlas.querySelectorAll('.tile').forEach(t => { const p = D.problems.find(q => 'tab-' + q.id === t.id); if (p) thumb(t.querySelector('canvas'), p) }) };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', repaintAll);
  new MutationObserver(repaintAll).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  selectProb(prob);
})();
