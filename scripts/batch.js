// usage: node scripts/batch.js <piece> <container|same> <n> <seedFrom> <seedTo> [budget=1] [mode=improved|rigid]
// Appends one JSON line per run to runs/<piece>_in_<container>/n<n>_<mode>_x<budget>.jsonl
// Each line: piece, container, n, seed, mode, B, s (certified edge ratio after legalization), ms, edge (internal
// piece edge), C (centres, internal units, container centred at the origin), Q (scalar-first quaternions).
'use strict';
const S = require('../src/sim.js');
const fs = require('fs'), path = require('path');
const [piece, cont0, n, s0, s1] = [process.argv[2], process.argv[3], +process.argv[4], +process.argv[5], +process.argv[6]];
const B = +(process.argv[7] || 1), mode = process.argv[8] || 'improved';
const container = cont0 === 'same' ? piece : cont0;
const steps = { compact: 5000 * B, morph: 45000 * B, settle: 3000 * B };
const dir = path.join(__dirname, '..', 'runs', `${piece}_in_${container}`);
fs.mkdirSync(dir, { recursive: true });
const F = path.join(dir, `n${n}_${mode}_x${B}.jsonl`);
const have = new Set(fs.existsSync(F) ? fs.readFileSync(F, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).seed) : []);
for (let seed = s0; seed <= s1; seed++) {
  if (have.has(seed)) continue;   // idempotent: queues can be restarted
  const t0 = Date.now();
  const r = S.run(Object.assign({ piece, container, n, seed, mode, anneal: true }, steps));
  fs.appendFileSync(F, JSON.stringify({ piece, container, n, seed, mode, B, s: r.s, ms: Date.now() - t0, edge: r.edge, C: r.final.C, Q: r.final.Q }) + '\n');
}
