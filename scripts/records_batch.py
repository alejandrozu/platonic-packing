#!/usr/bin/env python3
"""Build and certify the Platonic records of some problems in parallel (15 Oct 2026; used by the records_platonic
workflow on GitHub Actions for the first batch of n = 41-100, about 1,500 records; the main machine's publisher
then only rebuilds records whose packing has changed since).

    python3 scripts/records_batch.py PID[,PID...] [PROCS]

Runs publish.build_problem (records/<pid>/<pid>_nNN.json, .verify.txt, .certify.txt) for each problem in its own
process. Prints one summary line per problem."""
import os, sys
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'src'))


def one(p):
    import publish
    lines = []
    rows, k = publish.build_problem(p, lambda m: lines.append(m))
    bad = sum('FAILED' in l for l in lines)
    return f'{p}: {len(rows)} records, {k} built, {bad} failed'


if __name__ == '__main__':
    ps = [p for p in sys.argv[1].split(',') if p]
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    with Pool(procs) as pool:
        for line in pool.imap_unordered(one, ps): print(line, flush=True)
