// JSON-lines compute server for the search engine (scripts/engine.py): one request per stdin line, one reply per
// stdout line. Ops: fresh (a full soft-to-rigid run, sim.run), hop (sim.hop: relax / add / remove + re-sharpen), ping.
'use strict';
const S = require('./sim.js');
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin, terminal: false });
rl.on('line', line => {
  let msg = null, out;
  try {
    msg = JSON.parse(line);
    const t0 = Date.now();
    if (msg.op === 'fresh') {
      const r = S.run(Object.assign({}, msg, { recEvery: 1e9 }));
      out = { n: msg.n, s: r.s, L: r.L, C: r.final.C, Q: r.final.Q, edge: r.edge };
    } else if (msg.op === 'hop') out = S.hop(msg);
    else if (msg.op === 'ping') out = { ok: true };
    else throw new Error('unknown op ' + msg.op);
    out.ms = Date.now() - t0; out.id = msg.id;
  } catch (e) { out = { error: String((e && e.stack) || e), id: msg && msg.id }; }
  process.stdout.write(JSON.stringify(out) + '\n');
});
