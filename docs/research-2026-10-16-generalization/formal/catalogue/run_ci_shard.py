#!/usr/bin/env python3
"""Fresh, source-bound Linux kernel builds of deterministic catalogue shards.

Generation is untrusted. A record is accepted only by run_chunked.py's full
source/object/log/dependency checks and prescribed axiom audits. Failed attempts
remain in the evidence archive even when a finer attempt subsequently succeeds.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile

import generate_lean
import generate_nd_lean
import generate_chunked_cubes
import generate_chunked_nd
import generate_fine_chunked_nd
import run_chunked

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent
FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'


class IntegrityError(RuntimeError):
    """A frozen-input mismatch invalidates the global evidence environment."""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')
    temporary.replace(path)


def load_catalogue():
    if len(list((HERE / 'witnesses').glob('*.json'))) != 99 or len(list((HERE / 'witnesses_nd').glob('*.json'))) != 303:
        import unpack_witnesses
        unpack_witnesses.main()
    witness_manifest = json.loads((HERE / 'rational-witnesses-manifest.json').read_text(encoding='utf8'))
    if witness_manifest.get('freeze_git_sha') != FREEZE:
        raise IntegrityError('Witness bundle has an unexpected frozen commit')
    expected = {r['path']: r for r in witness_manifest['files']}
    records = []
    for folder in ('witnesses', 'witnesses_nd'):
        for path in sorted((HERE / folder).glob('*.json')):
            relative = str(path.relative_to(HERE)).replace('\\', '/')
            published = expected.get(relative)
            if published is None or sha(path) != published['sha256'] or path.stat().st_size != published['bytes']:
                raise IntegrityError('Witness differs from published bundle manifest: ' + relative)
            c = json.loads(path.read_text(encoding='utf8'))
            d, n, k = c['dimension'], c['n'], len(c['template_vertices'])
            # Fixed integer workload proxy; scheduling changes no proof data.
            cost = n * n * d * d * max(k, 8) + n * k * d * (d + 2) * 8
            records.append(dict(record_id=c['record_id'], n=n, dimension=d,
                                family=c['record_id'].split('_n')[0], cost=cost,
                                witness_path=relative,
                                witness_sha256=sha(path)))
    if len(records) != 402 or len({r['record_id'] for r in records}) != 402:
        raise ValueError('Expected exactly 402 distinct frozen rational witnesses')
    return sorted(records, key=lambda r: r['record_id'])


def shard_plan(records, count):
    shards = [dict(shard_index=i, estimated_cost=0, records=[]) for i in range(count)]
    for row in sorted(records, key=lambda r: (-r['cost'], r['record_id'])):
        target = min(shards, key=lambda s: (s['estimated_cost'], s['shard_index']))
        target['records'].append(row)
        target['estimated_cost'] += row['cost']
    for shard in shards:
        shard['records'].sort(key=lambda r: (r['cost'], r['record_id']))
    assert sorted(r['record_id'] for s in shards for r in s['records']) == sorted(r['record_id'] for r in records)
    return dict(schema_version=1, frozen_commit=FREEZE, shard_count=count,
                total_records=402, scheduling='deterministic greedy descending integer cost; lowest index breaks ties', shards=shards)


def ensure_input(relative, expected):
    path = (HERE / 'inputs' / relative).resolve()
    if not path.is_relative_to((HERE / 'inputs').resolve()):
        raise ValueError('Input path escapes frozen input directory')
    if not path.is_file():
        url = f'https://raw.githubusercontent.com/alejandrozu/platonic-packing/{FREEZE}/{relative}'
        data = urllib.request.urlopen(url, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != expected:
            raise IntegrityError('Fetched frozen input hash mismatch: ' + relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if sha(path) != expected:
        raise IntegrityError('Frozen input hash mismatch: ' + relative)


def metadata(c, witness):
    row = dict(record_id=c['record_id'], n=c['n'], dimension=c['dimension'],
               original_json_sha256=c['source_sha256'], original_source_path=c['source_path'],
               original_witness_sha256=sha(witness))
    if c['dimension'] > 3:
        row.update(original_geometry_path='src/polytopes_nd.json', original_geometry_sha256=c['geometry_sha256'])
    return row


def emit(c, witness, strategy, vertex_block_size=8, cube_block_size=5):
    """Create a disjoint CI namespace; never overwrite the original 57 builds."""
    if strategy == 'ordinary':
        old_name, text = (generate_lean.generate(c) if c['dimension'] == 3 else generate_nd_lean.generate(c))
        entries = [dict(short='', text=text, kind='ordinary', piece_indices=None)]
        extra = {}
    elif strategy == 'cube_chunks':
        old_name, files, axes = generate_chunked_cubes.generate(c, cube_block_size)
        entries = [dict(short=short, text=text, kind=kind, piece_indices=indices)
                   for short, text, kind, indices in files]
        extra = dict(block_size=cube_block_size, cached_axis_pairs=axes, generic_pairs=len(c['planes']) - axes)
    elif strategy == 'nd_chunks':
        old_name, files = generate_chunked_nd.generate(c, per_vertex=True, per_pair=False)
        entries = [dict(short=short, text=text, kind=kind, piece_indices=indices)
                   for short, text, kind, indices in files]
        extra = dict(block_size=1)
    elif strategy == 'nd_fine':
        old_name, entries = generate_fine_chunked_nd.generate(c, vertex_block_size)
        extra = dict(block_size=1, fine_vertex_coverage=True, vertex_count=len(c['template_vertices']),
                     vertex_block_size=vertex_block_size)
    else:
        raise ValueError(strategy)
    suffix = {'ordinary': 'M', 'cube_chunks': 'C', 'nd_chunks': 'N', 'nd_fine': 'V'}[strategy]
    name = 'CI' + suffix + old_name
    old_ns, ns = 'PackingCertificates.Catalogue.' + old_name, 'PackingCertificates.Catalogue.' + name
    directory = FORMAL / 'PackingCertificates' / 'Catalogue' / name
    directory.mkdir(parents=True, exist_ok=True)
    steps = []
    for entry in entries:
        short = entry['short']
        path = directory / (short + '.lean') if short else directory.with_suffix('.lean')
        text = entry['text'].replace(old_ns, ns)
        path.write_text(text, encoding='utf8', newline='\n')
        audits = re.findall(r'^\s*#print axioms\s+([A-Za-z0-9_.]+)', text, re.M)
        audits = [a if '.' in a else ns + '.' + a for a in audits]
        step = dict(id='ci_' + strategy + '_' + c['record_id'] + ('_' + short.lower() if short else ''),
                    record_id=c['record_id'], n=c['n'], dimension=c['dimension'],
                    module=ns + ('.' + short if short else ''), path=str(path.relative_to(FORMAL)).replace('\\', '/'),
                    kind=entry['kind'], piece_indices=entry.get('piece_indices'),
                    generated_source_sha256=sha(path), expected_audits=audits)
        for key in ('vertex_indices', 'fragment_role'):
            if key in entry:
                step[key] = entry[key]
        steps.append(step)
    row = dict(metadata(c, witness), id='ci_' + strategy + '_' + c['record_id'],
               module=ns, path=steps[-1]['path'], **extra)
    if strategy == 'ordinary':
        row.update(generated_source_sha256=steps[0]['generated_source_sha256'],
                   expected_audits=steps[0]['expected_audits'], dependencies=[])
    else:
        row.update(steps=steps, dependencies=[{k: s[k] for k in ('module', 'path', 'generated_source_sha256')} for s in steps[:-1]])
    run_chunked.validate_plan(run_chunked.normalize_row(row))
    return row


def strategies(c):
    if c['dimension'] == 3:
        return ['ordinary', 'cube_chunks'] if c['n'] <= 12 else ['cube_chunks']
    k = len(c['template_vertices'])
    if c['n'] <= 4 and not (c['dimension'] == 6 and k == 64 and c['n'] >= 3):
        return ['ordinary', 'nd_chunks', 'nd_fine']
    return ['nd_fine'] if k >= 24 else ['nd_chunks', 'nd_fine']


def evidence_files(status, outdir):
    paths = set()
    def add_receipt_artifacts(receipt_path):
        """Archive actual receipt paths, including root-level audit probes."""
        if not receipt_path.is_file():
            return
        paths.add(receipt_path)
        receipt = json.loads(receipt_path.read_text(encoding='utf8'))
        def add(value, required=False):
            if not value:
                return
            target = (FORMAL/value).resolve()
            if not target.is_relative_to(FORMAL.resolve()):
                raise ValueError('Receipt artifact escapes formal project: '+str(value))
            if required and not target.is_file():
                raise ValueError('Successful receipt artifact missing before packaging: '+str(value))
            if target.is_file():
                paths.add(target)
        for row in receipt.get('results', []):
            successful = row.get('passed') is True
            for key in ('path', 'olean_path', 'log'):
                add(row.get(key), successful)
            for dependency in row.get('imported_dependencies', []):
                add(dependency['path'], successful)
                add(dependency.get('olean_path') or dependency.get('olean'), successful)
        for dependency in receipt.get('core_dependencies', []):
            add(dependency['path'], True)
            add(dependency.get('olean_path') or dependency.get('olean'), dependency.get('olean_sha256') is not None)
    add_receipt_artifacts(FORMAL/'core-verification.json')
    for root in (FORMAL / 'PackingCertificates',):
        # Direct proof core plus extensions, excluding unrelated catalogue instances.
        for path in root.rglob('*'):
            if path.is_file() and path.suffix in ('.lean', '.olean') and 'Catalogue' not in path.relative_to(root).parts:
                paths.add(path)
    for path in (FORMAL / 'PackingCertificates.lean', FORMAL / 'PackingCertificates.olean', FORMAL / 'lean-toolchain'):
        if path.is_file():
            paths.add(path)
    for pattern in ('*.py', '*.toml', '*manifest*.json', '*verification.json', '*Regression.lean', '*Regression.olean', 'Audit.lean', 'Audit.olean'):
        paths.update(FORMAL.glob(pattern))
    if (FORMAL / 'core-build-logs').is_dir():
        paths.update(p for p in (FORMAL / 'core-build-logs').rglob('*') if p.is_file())
    for record in status['records']:
        witness = HERE / record['witness_path']
        paths.add(witness)
        c = json.loads(witness.read_text(encoding='utf8'))
        paths.add(HERE / 'inputs' / c['source_path'])
        if c['dimension'] > 3:
            paths.add(HERE / 'inputs' / 'src/polytopes_nd.json')
        for attempt in record.get('attempts', []):
            manifest = HERE / attempt['manifest']
            receipt = HERE / attempt['receipt']
            if manifest.is_file():
                paths.add(manifest)
                for row in json.loads(manifest.read_text(encoding='utf8')):
                    for step in run_chunked.normalize_row(row)['steps']:
                        source = FORMAL / step['path']
                        paths.add(source)
                        if source.with_suffix('.olean').is_file():
                            paths.add(source.with_suffix('.olean'))
            if receipt.is_file():
                paths.add(receipt)
                data = json.loads(receipt.read_text(encoding='utf8'))
                for result in data.get('results', []):
                    for step in result.get('steps', []):
                        if step.get('log'):
                            paths.add(FORMAL / step['log'])
            driver_log = HERE / attempt['driver_log']
            if driver_log.is_file():
                paths.add(driver_log)
    paths.update(p for p in outdir.iterdir() if p.is_file() and p.suffix in ('.json', '.log') and p.name != 'evidence-inventory.json')
    paths.update(p for p in HERE.glob('*.py'))
    paths.add(HERE / 'rational-witnesses-manifest.json')
    generic=status.get('generic_extension_receipt',{})
    if generic.get('path'):
        receipt=(FORMAL/generic['path']).resolve()
        if not receipt.is_relative_to(FORMAL.resolve()):
            raise ValueError('Generic receipt path escapes formal project')
        add_receipt_artifacts(receipt)
    return sorted((p for p in paths if p.is_file()), key=lambda p: str(p.relative_to(FORMAL)))


def package(status, outdir):
    archive = outdir / 'evidence.zip'
    files = evidence_files(status, outdir)
    inventory = [{'path': str(p.relative_to(FORMAL)).replace('\\', '/'), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files]
    write_json(outdir / 'evidence-inventory.json', dict(schema_version=1, files=inventory))
    temporary = archive.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for p in files:
            z.write(p, 'formal/' + str(p.relative_to(FORMAL)).replace('\\', '/'))
        z.write(outdir / 'evidence-inventory.json', 'formal/' + str((outdir / 'evidence-inventory.json').relative_to(FORMAL)).replace('\\', '/'))
    temporary.replace(archive)


def build_record(rec, args, outdir, status, status_path, deadline, strategy_picker=None, emitter=None):
    witness = HERE / rec['witness_path']
    if sha(witness) != rec['witness_sha256']:
        raise IntegrityError('Witness changed after plan: ' + rec['record_id'])
    c = json.loads(witness.read_text(encoding='utf8'))
    ensure_input(c['source_path'], c['source_sha256'])
    if c['dimension'] > 3:
        ensure_input('src/polytopes_nd.json', c['geometry_sha256'])
    for strategy in (strategy_picker or strategies)(c):
        if deadline - time.monotonic() < 600:
            rec['failure'] = 'Insufficient remaining job budget for another attempt; no formal success claimed'
            break
        row = (emitter or emit)(c, witness, strategy)
        stem = rec['record_id'] + '-' + strategy
        manifest, receipt, driver_log = (outdir / (stem + ending) for ending in ('-plan.json', '-receipt.json', '-driver.log'))
        write_json(manifest, [row])
        relative = lambda p: str(p.relative_to(HERE)).replace('\\', '/')
        attempt = dict(strategy=strategy, manifest=relative(manifest), receipt=relative(receipt),
                       driver_log=relative(driver_log), passed=False, complete=False)
        rec['attempts'].append(attempt)
        write_json(status_path, status)
        command = [sys.executable, '-u', str(HERE / 'run_chunked.py'), '--lean', str(args.lean),
                   '--mathlib-project', str(args.mathlib_project), '--manifest', relative(manifest),
                   '--receipt', relative(receipt), '--memory-mb', str(args.memory_mb), '--timeout', str(args.timeout)]
        if args.resume:
            command.append('--resume')
        print(json.dumps(dict(record_id=rec['record_id'], strategy=strategy, planned_modules=len(run_chunked.normalize_row(row)['steps']))), flush=True)
        with driver_log.open('w', encoding='utf8') as log:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, encoding='utf8', errors='replace', bufsize=1,
                                       start_new_session=(os.name != 'nt'))
            timed_out = []
            def stop_at_deadline():
                if process.poll() is not None:
                    return
                timed_out.append(True)
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
                else:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            timer = threading.Timer(max(1, deadline - time.monotonic() - 180), stop_at_deadline)
            timer.daemon = True
            timer.start()
            try:
                for line in process.stdout:
                    print(line, end='', flush=True)
                    log.write(line)
                    log.flush()
                exit_code = process.wait()
            finally:
                timer.cancel()
        attempt.update(complete=True, exit_code=exit_code, global_budget_timeout=bool(timed_out))
        if receipt.is_file():
            built = json.loads(receipt.read_text(encoding='utf8'))
            results = built.get('results', [])
            attempt['passed'] = bool(exit_code == 0 and len(results) == 1 and results[0].get('complete') and results[0].get('passed'))
            attempt['receipt_sha256'], attempt['manifest_sha256'] = sha(receipt), sha(manifest)
        rec['passed'] = attempt['passed']
        write_json(status_path, status)
        if rec['passed']:
            rec['accepted_receipt'], rec['accepted_manifest'] = attempt['receipt'], attempt['manifest']
            break
    rec['complete'] = True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--shard-index', type=int, default=0)
    ap.add_argument('--shard-count', type=int, default=24)
    ap.add_argument('--mathlib-project', type=Path, default=FORMAL)
    ap.add_argument('--lean', type=Path, default=Path(shutil.which('lean') or str(Path.home() / '.elan/toolchains/leanprover--lean4---v4.31.0/bin/lean.exe')))
    ap.add_argument('--timeout', type=int, default=900, help='Timeout per compiler module, seconds')
    ap.add_argument('--memory-mb', type=int, default=8192)
    ap.add_argument('--only', nargs='*', help='Explicit record IDs; bypass shard selection for pilots')
    ap.add_argument('--plan-only', action='store_true')
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--job-budget-seconds', type=int, default=19800)
    args = ap.parse_args()
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        ap.error('Require 0 <= shard-index < shard-count')
    records = load_catalogue()
    plan = shard_plan(records, args.shard_count)
    outdir = HERE / 'ci' / f'shard-{args.shard_index:02d}'
    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / 'shard-plan.json', plan)
    selected = plan['shards'][args.shard_index]['records']
    if args.only:
        unknown = set(args.only) - {r['record_id'] for r in records}
        if unknown:
            ap.error('Unknown record IDs: ' + ', '.join(sorted(unknown)))
        selected = [r for r in records if r['record_id'] in args.only]
    if args.plan_only:
        print(json.dumps(dict(plan=str((outdir / 'shard-plan.json').relative_to(FORMAL)), selected=len(selected),
                              records=[r['record_id'] for r in selected], shard_count=args.shard_count, total_records=402)), flush=True)
        return 0
    status_path = outdir / 'status.json'
    status = dict(schema_version=1, started_at_utc=datetime.now(timezone.utc).isoformat(),
                  shard_index=args.shard_index, shard_count=args.shard_count,
                  frozen_commit=FREEZE, memory_mb=args.memory_mb, timeout_per_module=args.timeout,
                  total_selected=len(selected), records=[], complete=False,
                  proof_rule='Only a fully passed strict run_chunked receipt accepts a record; failed attempts are retained.')
    started = time.monotonic()
    deadline = started + args.job_budget_seconds
    error = None
    try:
        for selected_row in selected:
            rec = dict(selected_row, attempts=[], passed=False, complete=False)
            status['records'].append(rec)
            write_json(status_path, status)
            if deadline - time.monotonic() < 600:
                rec['failure'] = 'job budget reached before record; no formal success claimed'
                write_json(status_path, status)
                continue
            try:
                build_record(rec, args, outdir, status, status_path, deadline)
            except IntegrityError:
                raise
            except Exception as exc:
                rec['driver_error'], rec['complete'] = repr(exc), True
                print(json.dumps(dict(record_id=rec['record_id'], driver_error=repr(exc))), flush=True)
            status['passed_records'] = sum(r['passed'] for r in status['records'])
            status['unverified_records'] = len(selected) - status['passed_records']
            status['elapsed_seconds'] = round(time.monotonic() - started, 3)
            write_json(status_path, status)
            package(status, outdir)
    except Exception as exc:
        error = repr(exc)
        status['driver_error'] = error
        raise
    finally:
        status['complete'] = error is None and len(status['records']) == len(selected) and all(r['complete'] for r in status['records'])
        status['passed_records'] = sum(r['passed'] for r in status['records'])
        status['unverified_records'] = len(selected) - status['passed_records']
        status['elapsed_seconds'] = round(time.monotonic() - started, 3)
        status['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        write_json(status_path, status)
        package(status, outdir)
        print(json.dumps(dict(status=str(status_path.relative_to(FORMAL)), passed_records=status['passed_records'],
                              unverified_records=status['unverified_records'], evidence=str((outdir / 'evidence.zip').relative_to(FORMAL)))), flush=True)
    return int(status['unverified_records'] > 0 or not status['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
