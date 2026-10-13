// Offline DOM harness runs the production checker and opens only captured URLs: no issues or network requests.
// Run: node tests/test_submission_forms.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const record = JSON.parse(fs.readFileSync(path.join(root, 'records/cubincub/cubincub_n02.json'), 'utf8'));
const solids = JSON.parse(fs.readFileSync(path.join(root, 'src/solids.json'), 'utf8'));
const D = { solids: Object.fromEntries(Object.entries(solids).map(([k, s]) => [k, { V: s.V, F: s.faces, E: s.edges }])), problems: [
  { id: 'cubincub', title: 'Cubes in a cube', piece: 'cube', container: 'cube', family: 'platonic', rows: [{ n: 2, sf: record.s_full, p: record.pieces, file: 'records/cubincub/cubincub_n02.json' }] }
] };
class Element {
  constructor() { this.value = ''; this.children = []; this.listeners = {}; this.hidden = false; this.disabled = false; this.innerHTML = ''; this.textContent = '' }
  appendChild(element) { this.children.push(element); return element }
  replaceChildren(...elements) { this.children = elements }
  addEventListener(name, listener) { this.listeners[name] = listener }
  focus() { this.focused = true }
  select() { this.selected = true }
  getContext() { return null }
}
const elements = new Map();
const el = name => { if (!elements.has(name)) elements.set(name, new Element()); return elements.get(name) };
el('prob').value = 'cubincub';
const opened = [];
const window = { open: (url, ...args) => { opened.push(new URL(url)); return {} }, addEventListener() {} };
const context = { document: { documentElement: { dataset: { root: './', repo: 'https://github.com/alejandrozu/platonic-packing' } }, getElementById: el, createElement: () => new Element(), addEventListener() {} },
  window, URL, Blob, location: { hash: '' }, navigator: { clipboard: { writeText: async () => { throw new Error('Denied') } } },
  getComputedStyle: () => ({ getPropertyValue: () => '#ffffff' }), setTimeout, console,
  fetch: async () => ({ ok: true, json: async () => D }),
};
await vm.runInNewContext(fs.readFileSync(path.join(root, 'web/assets/contribute.js'), 'utf8'), context);

// A real record passes the production SAT checker; required credit prevents an incomplete packing form.
el('json').value = JSON.stringify(record);
await el('check').onclick();
assert.equal(el('send').disabled, false);
assert.match(el('result').innerHTML, /Valid in floating point/);
el('send').onclick();
assert.equal(opened.length, 0);
assert.match(el('sendnote').textContent, /credit/);
el('credit').value = 'Example contributor'; el('how').value = 'Lattice';
el('send').onclick();
let url = opened.at(-1);
assert.equal(url.searchParams.get('template'), 'submit-packing.yml');
assert.equal(url.searchParams.get('problem'), 'cubincub');
assert.equal(url.searchParams.get('n'), '2');
assert.equal(url.searchParams.get('s'), String(record.s_full));
assert.equal(url.searchParams.get('credit'), 'Example contributor');
assert.equal(JSON.parse(url.searchParams.get('packing')).pieces.length, 2);

// Required category fields and every supported proposal field map to the real issue-form IDs.
el('c_send').onclick(); assert.equal(opened.length, 1);
Object.entries({ c_pieces: 'New convex solid', c_container: 'cube', c_measure: 'volume scale', c_motivation: 'A new family', c_details: 'Vertices and source references' }).forEach(([id, value]) => el(id).value = value);
el('c_send').onclick(); url = opened.at(-1);
assert.equal(url.searchParams.get('template'), 'new-category.yml');
for (const [key, value] of Object.entries({ pieces: 'New convex solid', container: 'cube', measure: 'volume scale', motivation: 'A new family', details: 'Vertices and source references' })) assert.equal(url.searchParams.get(key), value);

el('o_send').onclick(); assert.equal(opened.length, 2);
Object.entries({ o_title: 'Symmetric packing', o_description: 'A construction and proof', o_data: '{"vertices": []}', o_links: 'https://example.invalid/paper' }).forEach(([id, value]) => el(id).value = value);
el('o_send').onclick(); url = opened.at(-1);
assert.equal(url.searchParams.get('template'), 'other-construction.yml');
for (const [key, value] of Object.entries({ summary: 'Symmetric packing', description: 'A construction and proof', data: '{"vertices": []}', links: 'https://example.invalid/paper' })) assert.equal(url.searchParams.get(key), value);

// Oversized coordinates in either non-packing form stay in a persistent, copyable handoff.
const huge = 'Vertices \u03b1: '.repeat(2000).trim();
el('c_details').value = huge; el('c_send').onclick();
assert.ok(opened.at(-1).href.length <= 7800);
assert.equal(opened.at(-1).searchParams.has('details'), false);
assert.equal(el('issue_handoff').hidden, false);
let label = el('issue_handoff').children.find(e => e.className === 'field');
assert.equal(label.children[1].value, huge);
let copy = el('issue_handoff').children.find(e => e.textContent.startsWith('Copy '));
await copy.onclick();
assert.equal(label.children[1].selected, true);
assert.match(copy.textContent, /Ctrl\+C/);
el('o_data').value = huge; el('o_send').onclick();
assert.ok(opened.at(-1).href.length <= 7800);
assert.equal(opened.at(-1).searchParams.has('data'), false);
assert.equal(el('issue_handoff').children.find(e => e.className === 'field').children[1].value, huge);

// A large valid cubic packing cannot be silently truncated by a URL or clipboard failure.
const grid = [];
for (let x = -2; x <= 2; x++) for (let y = -2; y <= 2; y++) for (let z = -2; z <= 2; z++) grid.push([x * 1.10000000000001, y * 1.10000000000001, z * 1.10000000000001, 1, 0, 0, 0]);
const largePacking = { piece: 'cube', container: 'cube', n: grid.length, s_full: 6.1, pieces: grid };
el('json').value = JSON.stringify(largePacking); await el('check').onclick();
assert.equal(el('send').disabled, false);
el('send').onclick();
assert.ok(opened.at(-1).href.length <= 7800);
assert.equal(opened.at(-1).searchParams.has('packing'), false);
label = el('issue_handoff').children.find(e => e.className === 'field');
assert.equal(JSON.parse(label.children[1].value).pieces.length, 125);

// Changing an input while the asynchronous pair loop yields invalidates the entire result.
const pendingCheck = el('check').onclick();
el('json').value = '{}'; el('json').listeners.input();
await pendingCheck;
assert.equal(el('send').disabled, true);
assert.match(el('result').innerHTML, /changed during the check/);

// Frontend/backend agree on limits and numeric types; an invalid center can never report valid containment.
for (const change of [{ container_center: [0, 0] }, { container_center: [false, 0, 0] }, { container_center: null }, { s_full: true }, { pieces: Array.from({ length: 201 }, () => record.pieces[0]) }]) {
  el('json').value = JSON.stringify({ ...record, ...change });
  await el('check').onclick();
  assert.equal(el('send').disabled, true);
  assert.match(el('result').innerHTML, /Cannot check this yet/);
}
const overlap = { ...record, pieces: [record.pieces[0], record.pieces[0]] };
el('json').value = JSON.stringify(overlap); await el('check').onclick();
assert.equal(el('send').disabled, true);
assert.match(el('result').innerHTML, /Not valid/);

// Every query key in the captured form links corresponds to a checked-in issue form ID.
for (const url of opened) {
  const yaml = fs.readFileSync(path.join(root, '.github/ISSUE_TEMPLATE', url.searchParams.get('template')), 'utf8');
  const ids = [...yaml.matchAll(/^\s+id: (\w+)$/gm)].map(match => match[1]);
  for (const key of url.searchParams.keys()) if (!['template', 'title'].includes(key)) assert.ok(ids.includes(key), `${key} is missing from the template`);
}
console.log('PASS: packing SAT and rejection, required fields, all 3 issue forms, oversized proposals/constructions, clipboard fallback, and template mappings.');
