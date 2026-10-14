import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { packingConstructionChoices, packingInitialSelection, packingPublicURL, packingUnitQuaternion, packingReferenceTolerance,
  packingDerivationText, packingRecordRawURL, packingFullPrecisionRecord } = require('../web/assets/explorer.js');

const pose = [0, 0, 0, 1, 0, 0, 0];
const coordinate = (id, sf, who, n = 2) => ({ id, n, sf, who, p: Array.from({ length: n }, () => [...pose]), ok: true });
const local = coordinate('local', 3.1, 'Local constructor');
const external = { ...coordinate('imported', 3.0, 'Original constructor'), external: true };
const reference = { id: 'catalogue', n: 2, sf: 2.9, who: 'Published constructor', source_only: true,
  p: [], ok: false, alternatives: [local, external] };
const before = JSON.stringify(reference);

// Named construction hashes retain their piece count and chosen alternative on reload.
const archived = { ...coordinate('tetinico_n05_archive', 1.5, 'Archive author', 5) };
const named = { ...coordinate('tetinico_n05_kamp', 1.4, 'Prior author', 5), alternatives: [archived] };
const defaultTwelve = coordinate('tetinico_n12_kamp', 2, 'Prior author', 12);
const hashProblem = { id: 'tetinico', rows: [named, defaultTwelve] };
assert.equal(packingInitialSelection(hashProblem, 'tetinico_n05_kamp'), named);
assert.equal(packingInitialSelection(hashProblem, 'tetinico_n05_archive'), archived);
assert.equal(packingInitialSelection(hashProblem, 'tetinico_n05'), named);
assert.equal(packingInitialSelection(hashProblem, 'cubincub_n33'), defaultTwelve);
assert.equal(packingInitialSelection(hashProblem, 'tetinico_n05_archive', 5), named);

// A better bound never borrows a larger construction's geometry or certificate.
const resolved = packingConstructionChoices(reference);
assert.equal(resolved.row, external);
assert.equal(resolved.row.sf, 3.0);
assert.equal(resolved.row.who, 'Original constructor');
assert.equal(resolved.reference, reference);
assert.equal(resolved.reference.sf, 2.9);
assert.equal(resolved.reference.ok, false);
assert.deepEqual(resolved.choices, [external, local]);
assert.equal(JSON.stringify(reference), before);

// Explicitly choosing an alternative preserves its own coordinates and credit.
assert.equal(packingConstructionChoices(reference, local).row, local);
const independentBest = { ...external, alternatives: [local] };
assert.equal(packingConstructionChoices(independentBest).row, independentBest);
assert.equal(packingConstructionChoices(independentBest).reference, null);

// Missing/mismatched poses cannot silently create a 3D depiction of the bound.
assert.equal(packingConstructionChoices({ ...reference, alternatives: [] }).row, null);
assert.equal(packingConstructionChoices({ ...reference, alternatives: [coordinate('wrong-n', 1, 'Other', 3)] }).row, null);
assert.equal(packingConstructionChoices({ ...reference, alternatives: [{ ...local, p: [] }] }).row, null);

// Public provenance is clickable only for credential-free HTTP(S) URLs.
assert.equal(packingPublicURL('https://example.org/paper?a=1&b=2'), 'https://example.org/paper?a=1&b=2');
assert.equal(packingPublicURL('http://example.org/paper'), 'http://example.org/paper');
for (const value of ['javascript:alert(1)', 'data:text/html,unsafe', '//example.org/paper',
  'https://user:password@example.org/paper', 'https://example.org/\nunsafe', { url: 'https://example.org' }]) {
  assert.equal(packingPublicURL(value), null);
}
assert.equal(packingReferenceTolerance({ ref_quantum: 0.001 }), 0.001);
assert.equal(packingReferenceTolerance({ ref_quantum: 1e-12 }), 1e-5);
assert.equal(packingReferenceTolerance({ ref_quantum: 'invalid' }), 1e-5);
assert.equal(packingDerivationText('Delete one piece from the original construction.'), 'Delete one piece from the original construction.');
assert.equal(packingDerivationText({ kind: 'subset', original_n: 33, removed: [0, 1] }), 'kind: subset; original n: 33; removed: [0,1]');

// Rotation equivalence must survive very large and subnormal finite quaternions.
const normal = packingUnitQuaternion([1, -2, 3, -4]);
for (const q of [[1e307, -2e307, 3e307, -4e307], [1e-320, -2e-320, 3e-320, -4e-320]]) {
  const unit = packingUnitQuaternion(q);
  assert(unit.every(Number.isFinite));
  assert(Math.abs(Math.hypot(...unit) - 1) < 1e-15);
  assert(unit.every((value, index) => Math.abs(value - normal[index]) < 1e-15));
}

// The clipboard source retains the exact decimal text and every provenance field,
// instead of reserializing the rounded seven-decimal viewer poses.
const repo = 'https://github.com/alejandrozu/platonic-packing';
const file = 'records/community/cubincub/cubincub_n02_submission_8_abcdef.json';
const rawText = '{"piece":"cube","container":"cube","n":2,"s_full":3,"pieces":[[0.123456789012345678901234,0,0,1,0,0,0],[1,0,0,1,0,0,0]],"found_by":"Original constructor","certificate_refined_by":"Independent refiner","source":{"url":"https://example.org/source"},"contribution":{"archive_sha256":"bound-to-source"}}\n';
const rawRow = { ...external, file }, problem = { piece: 'cube', container: 'cube' };
let requested;
const text = await packingFullPrecisionRecord(repo, rawRow, problem, 'dataset/123', async (url, options) => {
  requested = { url, options }; return { ok: true, text: async () => rawText };
});
assert.equal(text, rawText);
assert.equal(requested.options.cache, 'no-cache');
assert.equal(new URL(requested.url).hostname, 'raw.githubusercontent.com');
assert.equal(new URL(requested.url).searchParams.get('v'), 'dataset/123');
assert.equal(packingRecordRawURL(repo, 'records/../unsafe.json', '1'), null);
assert.equal(packingRecordRawURL('https://example.org/repo', file, '1'), null);
await assert.rejects(packingFullPrecisionRecord(repo, rawRow, problem, '1', async () => ({ ok: false })), /could not be fetched/);
await assert.rejects(packingFullPrecisionRecord(repo, { ...rawRow, sf: 2.99 }, problem, '1',
  async () => ({ ok: true, text: async () => rawText })), /record changed/);

if (process.argv[2]) {
  const data = JSON.parse(readFileSync(process.argv[2], 'utf8'));
  if (data.lazy) {     // 14 Oct: coordinates live in data/pieces/<problem>.json (loaded by the explorer per problem)
    const dir = process.argv[2].replace(/records\.json$/, 'pieces/');
    for (const problem of data.problems) {
      const m = JSON.parse(readFileSync(dir + problem.id + '.json', 'utf8'));
      for (const r of problem.rows) {
        r.p = m[r.id] || r.p || [];
        for (const a of r.alternatives || []) a.p = m[r.id + '|' + a.id] || a.p || [];
      }
    }
  }
  let checked = 0;
  for (const problem of data.problems) for (const primary of problem.rows) {
    const selection = packingConstructionChoices(primary);
    assert(selection.row, `${problem.id} n=${primary.n}: missing coordinate construction`);
    assert.equal(selection.row.p.length, primary.n);
    assert.equal(selection.row.sf, Math.min(...selection.choices.map(c => c.sf)));
    if (primary.source_only) {
      assert.equal(selection.reference, primary);
      assert(selection.row.sf > primary.sf, `${problem.id} n=${primary.n}: bound borrowed a pose`);
      assert.equal(primary.ok, false);
      assert.equal(primary.p.length, 0);
    }
    checked++;
  }
  console.log(`Built-site selection checked for ${checked} cases.`);
}
console.log('Explorer selection: actual scales, attribution, alternatives and missing-pose cases passed.');
