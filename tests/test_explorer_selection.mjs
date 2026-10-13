import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { packingConstructionChoices } = require('../web/assets/explorer.js');

const pose = [0, 0, 0, 1, 0, 0, 0];
const coordinate = (id, sf, who, n = 2) => ({ id, n, sf, who, p: Array.from({ length: n }, () => [...pose]), ok: true });
const local = coordinate('local', 3.1, 'Local constructor');
const external = { ...coordinate('imported', 3.0, 'Original constructor'), external: true };
const reference = { id: 'catalogue', n: 2, sf: 2.9, who: 'Published constructor', source_only: true,
  p: [], ok: false, alternatives: [local, external] };
const before = JSON.stringify(reference);

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

if (process.argv[2]) {
  const data = JSON.parse(readFileSync(process.argv[2], 'utf8'));
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
