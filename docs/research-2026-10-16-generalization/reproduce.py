"""Audit the frozen paper supplement; Python standard library only.

This rechecks exact Python certificates. It does not run Lean or claim that the
archive has been formally imported. Run the separately pinned formal project
to repeat kernel verification.
"""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import math
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((DATA / 'source-manifest.json').read_text(encoding='utf-8'))
    checked = []
    for item in manifest['sources']:
        path = DATA / item['file']
        if path.is_file():
            assert sha(path.read_bytes()) == item['sha256'], item['file']
            checked.append(item['file'])
        elif item['file'] == 'records.json':
            raw = gzip.decompress((DATA / 'records.json.gz').read_bytes())
            assert sha(raw) == item['sha256']
            checked.append('records.json (decompressed)')
        elif item.get('packaged'):
            raise FileNotFoundError('Missing packaged upstream source: '+item['file'])

    catalogue = json.loads(gzip.decompress((DATA / 'records.json.gz').read_bytes()))
    rows = [r for p in catalogue['problems'] for r in p['rows']]
    counts = dict(problems=len(catalogue['problems']), slots=len(rows),
                  populated=sum(r.get('sf') is not None for r in rows),
                  coordinates=sum(bool(r.get('file')) for r in rows),
                  certified=sum(bool(r.get('ok')) for r in rows),
                  source_only=sum(r.get('sf') is not None and not r.get('file') for r in rows))
    assert counts == json.loads((DATA / 'catalogue-counts.json').read_text())['totals']

    attempts = []
    for shard in sorted((DATA / 'sources/docs/search_review/bench').glob('bench_d[0-5].jsonl')):
        for line in shard.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if 'error' not in row and 's' in row:
                attempts.append(row)
    assert len(attempts) == 1824
    assert len({(r['p'], r['n']) for r in attempts}) == 40
    aggregates = {}
    for method in ['fresh', 'hop', 'symfresh']:
        rr = [r for r in attempts if r['method'] == method]
        elapsed = sum(r['secs'] for r in rr)
        aggregates[method] = dict(attempts=len(rr), wins=sum(bool(r['beat']) for r in rr),
            elapsed_seconds=elapsed,
            positive_log_gain_per_worker_hour=sum(max(0, math.log(r['rec']/r['s'])) for r in rr)/(elapsed/3600))
    assert [aggregates[m]['wins'] for m in ['fresh', 'hop', 'symfresh']] == [71, 200, 86]
    cases = {(r['p'], r['n']) for r in attempts}
    best_methods = collections.Counter()
    for case in cases:
        best = min((r for r in attempts if (r['p'], r['n']) == case), key=lambda r:r['s'])
        if 1-best['s']/best['rec'] > .001:
            best_methods[best['method']] += 1
    assert best_methods == {'symfresh': 21, 'fresh': 5, 'hop': 5}

    rechecks = []
    for example in json.loads((DATA / 'illustrative-cases.json').read_text()):
        checker = DATA / 'sources' / ('certify_nd.py' if example['dimension'] > 3 else 'certify_general.py')
        witness = DATA / 'sources' / example['file']
        result = subprocess.run([sys.executable, str(checker), str(witness)],
                                capture_output=True, text=True, check=True)
        assert 'CERTIFIED:' in result.stdout, example['id']
        rechecks.append(dict(case=example['id'], exit_code=result.returncode, output=result.stdout))
    report = dict(source_files_hash_checked=len(checked), counts=counts,
        round_d=aggregates, round_d_best_methods=dict(best_methods), exact_rechecks=rechecks,
        lean='Run formal/ separately; no archive-wide Lean claim.')
    (ROOT / 'reproduction-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(dict(source_files_hash_checked=len(checked), counts=counts,
                         round_d=aggregates, exact_rechecks=len(rechecks)), indent=2))


if __name__ == '__main__':
    main()
