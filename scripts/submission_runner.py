"""Certify every discovered witness and write only immutable reviewed improvements."""
from collections import Counter
from fractions import Fraction
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time

from submission_batch import discover, BatchError

MAX_SECONDS = 70 * 60
WORKERS = 4


def escaped(value):
    return str(value).replace('|', '&#124;').replace('\n', ' ')[:240]


def guard_paths(api, candidates):
    paths = {'docs/external_records.json', 'docs/community_records.json', 'src/solids.json',
             'src/solids_exact.json', 'certify_general.py', 'verify_general.py', 'algebraic.py'}
    root = Path(api.ROOT).resolve()
    registries = []
    for name in ('docs/external_records.json', 'docs/community_records.json'):
        if (root / name).exists(): registries.extend(api.load_json(root / name).get('entries', []))
    for row in candidates:
        if not row.get('pid'): continue
        pid, n = row['pid'], row['rec']['n']
        paths.add(f'records/{pid}/{pid}_n{n:02d}.json')
        for entry in registries:
            if entry.get('kind') == 'coordinates' and entry.get('problem') == pid and entry.get('n') == n:
                path = (root / entry['file']).resolve()
                if path.is_relative_to(root / 'records'):
                    relative = path.relative_to(root).as_posix()
                    paths.update((relative, str(Path(relative).with_suffix('.certify.txt')).replace('\\', '/')))
    return sorted(paths)


def check_one(api, row, directory, deadline):
    if time.monotonic() >= deadline:
        row['status'] = 'deferred'; row['message'] = 'Batch time budget reached; this witness was not certified.'
        return row
    filename = directory / f'candidate-{row["index"]:04d}.json'
    api.save_json(filename, row['rec'])
    remaining = max(1, int(deadline - time.monotonic()))
    row['vcode'], row['vout'] = api.run([sys.executable, 'verify_general.py', str(filename)], min(900, remaining))
    remaining = max(1, int(deadline - time.monotonic()))
    row['ccode'], row['cout'] = api.run([sys.executable, 'certify_general.py', str(filename)], min(3000, remaining))
    api.save_text(filename.with_suffix('.verify.txt'), row['vout'] + '\n')
    api.save_text(filename.with_suffix('.certify.txt'), row['cout'] + '\n')
    row['certified'] = row['ccode'] == 0 and 'NOT CERTIFIED' not in row['cout'] and 'CERTIFIED' in row['cout']
    row['status'] = 'certified' if row['certified'] else 'deferred' if row['ccode'] == 99 else 'not-certified'
    return row


def metadata_text(obj, key, default='', limit=2000):
    value = obj.get(key)
    return value.strip()[:limit] if isinstance(value, str) and value.strip() else default


def geometry_signature(record):
    """Exact native poses relative to the container; excludes scale and order.

    Scalar multiples/sign changes of quaternions give the same rational
    rotation. No approximate angle tolerance or rounded position comparison
    can silently turn changed geometry into an inherited construction.
    """
    centre = tuple(Fraction(value) for value in record.get('container_center', [0, 0, 0]))
    poses = []
    for piece in record['pieces']:
        w, x, y, z = (Fraction(value) for value in piece[3:])
        norm = w*w + x*x + y*y + z*z
        if not norm: raise ValueError('Zero quaternion in predecessor.')
        rotation = (w*w + x*x - y*y - z*z, 2*(x*y-w*z), 2*(x*z+w*y),
                    2*(x*y+w*z), w*w-x*x+y*y-z*z, 2*(y*z-w*x),
                    2*(x*z-w*y), 2*(y*z+w*x), w*w-x*x-y*y+z*z)
        position = tuple(Fraction(piece[k]) - centre[k] for k in range(3))
        poses.append(position + tuple(value/norm for value in rotation))
    return Counter(poses)


def unchanged_geometry(record, predecessor):
    if not predecessor or (record.get('piece'), record.get('container'), record.get('n')) != (
            predecessor.get('piece'), predecessor.get('container'), predecessor.get('n')):
        return False
    try:
        return geometry_signature(record) == geometry_signature(predecessor)
    except (TypeError, ValueError, KeyError, ZeroDivisionError):
        return False


def trusted_geometry_predecessor(api, row):
    """Find a checked matching origin even if another geometry is the best case."""
    if unchanged_geometry(row['rec'], row.get('current')):
        return row['current'], row.get('current_file')
    root = Path(api.ROOT).resolve()
    pid, n = row['pid'], row['rec']['n']
    paths = [f'records/{pid}/{pid}_n{n:02d}.json']
    for name in ('docs/external_records.json', 'docs/community_records.json'):
        registry = root / name
        if registry.exists():
            paths.extend(entry['file'] for entry in api.load_json(registry).get('entries', [])
                         if entry.get('kind') == 'coordinates' and entry.get('problem') == pid and entry.get('n') == n)
    for relative in dict.fromkeys(paths):
        path = (root / relative).resolve()
        if not path.is_relative_to(root / 'records') or not path.exists(): continue
        certificate = path.with_suffix('.certify.txt')
        if not certificate.exists(): continue
        proof = certificate.read_text(encoding='utf-8')
        if 'CERTIFIED' not in proof or 'NOT CERTIFIED' in proof: continue
        candidate = api.load_json(path)
        if unchanged_geometry(row['rec'], candidate): return candidate, path.relative_to(root).as_posix()
    return None, None


def write_record(api, row, fields, issue):
    rec, pid, obj = row['rec'], row['pid'], row['object']
    n, s = rec['n'], rec['s_full']
    rid = f'{pid}_n{n:02d}'
    submit_credit = fields['credit'].strip().splitlines()[0][:120]
    metadata = row.get('metadata') or {}
    original = obj.get('source_credit', metadata.get('original_credit', {}))
    if not isinstance(original, dict): original = {}
    original_author = metadata_text(original, 'found_by', metadata_text(original, 'construction_and_original_certificate'), 120)
    credit = metadata_text(obj, 'found_by', original_author or submit_credit, 120)
    method = metadata_text(obj, 'method', metadata_text(original, 'method', fields.get('method', '').strip()[:2000] or 'submitted packing'))
    native_credit = metadata_text(obj, 'credit', metadata_text(original, 'credit', f'{credit}, submitted in {issue["html_url"]}'))
    current = row.get('current')
    predecessor, predecessor_file = trusted_geometry_predecessor(api, row)
    padding = predecessor is not None
    if padding:
        credit = metadata_text(predecessor, 'found_by', 'Construction author not recorded', 120)
        native_credit = metadata_text(predecessor, 'credit', credit)
        method = metadata_text(predecessor, 'method', 'Inherited construction; certificate scale refined')
    today = datetime.date.today().isoformat()
    vc, vp = api.SOL[rec['container']]['volume'], api.SOL[rec['piece']]['volume']
    container = api.disp(rec['container'])
    title = f'{n} {api.plural(rec["piece"]) if n > 1 else api.disp(rec["piece"])} in {"an" if container[0] in "aeiou" else "a"} {container}'
    wall = re.search(r'min wall gap ([0-9.eE+-]+)', row['vout'])
    pair = re.search(r'min pair separation ([0-9.eE+-]+)', row['vout'])
    out = {'problem': f'min/{rec["piece"]}_in_{rec["container"]}', **rec,
           's': math.floor(s * 1e5) / 1e5, 's_plus': f'{math.floor(s * 1e5) / 1e5:.5f}+',
           'measure': ('edge length of the container divided by the edge length of the pieces'
                       if api.SOL[rec['piece']].get('unit', 'edge') == 'edge'
                       else 'linear size of the container divided by the linear size of the pieces (same canonical solid)'),
           'clearance': {'min_pair_gap': float(pair.group(1)) if pair else None,
                         'min_wall_gap': float(wall.group(1)) if wall else None},
           'format': '[x, y, z, qw, qx, qy, qz] per canonical piece; scalar-first quaternion; container = s_full times canonical container',
           'method': method, 'date': today, 'record_id': rid, 'title': title, 'family': api.FAM[pid],
           'source': obj.get('source') if isinstance(obj.get('source'), dict) else original.get('source') if isinstance(original.get('source'), dict)
                     else {'issue': original['issue']} if isinstance(original.get('issue'), str)
                     else {'issue': issue['html_url'], 'submitted_by': issue['user']['login']},
           's_tight': None, 'closed_form_conjecture': None,
           'volume_lower_bound': (n * vp / vc) ** (1 / 3), 'density': n * vp / vc / s / s / s,
           'found_by': credit, 'credit': native_credit,
           'certificate': 'exact certificate: certify_general.py (src/solids_exact.json)'}
    refinement = obj.get('source_refinement')
    if padding: out['source'] = predecessor.get('source') if isinstance(predecessor.get('source'), dict) else {}
    same_nominal = 'certificate-only' in str(metadata.get('classification', ''))
    contribution = {'issue': issue['html_url'], 'submitted_by': issue['user']['login'], 'credit': submit_credit,
                    'kind': 'wall_padding' if padding else 'same_nominal' if same_nominal else 'construction', 'replayed_on': today,
                    'witness_sha256': row.get('witness_sha256', row['digest']),
                    'method': fields.get('method', '').strip()[:2000]}
    for key in ('archive', 'archive_sha256'):
        if row.get(key): contribution[key] = row[key]
    out['contribution'] = contribution
    if original: out['source_credit'] = original
    if padding:
        # This role is distinct from original geometric authorship. A form may
        # explicitly separate the two roles; otherwise retain its credit as given.
        refiner = metadata_text(obj, 'certificate_refined_by', submit_credit, 120)
        role = re.search(r'(?:^|;)\s*([^;]+?)\s*\(certificate refinement(?: only)?\)', submit_credit, re.I)
        if role: refiner = role.group(1).strip()
        out['certificate_refined_by'], out['certificate_refined_on'] = refiner, today
        old_scale, new_scale = Fraction(predecessor['s_full']), Fraction(s)
        out['certificate_refinement'] = {'kind': 'wall-padding certificate refinement',
                                         'new_nominal_construction': False, 'geometry_matched_exactly': True,
                                         'previous_scale_exact': str(old_scale), 'scale_exact': str(new_scale),
                                         'decrease_exact': str(old_scale-new_scale)}
        out['source_refinement'] = {'type': 'certified wall-padding reduction only', 'pieces_unchanged': True,
                                    'source_record': predecessor_file, 'source_credit_preserved': True}
    if row.get('current'):
        out['previous_record'] = {k: row['current'].get(k) for k in ('s_full', 'found_by', 'date')}
        # A submitted feasibility certificate does not prove its proposed
        # touching limit or optimality claim. Retain existing annotations only
        # when the trusted predecessor has exactly the same native poses.
        if padding:
            out['s_tight'] = predecessor.get('s_tight')
            out['closed_form_conjecture'] = predecessor.get('closed_form_conjecture')
    # Content-addressing also keeps a second accepted edit of the same issue immutable.
    relative = f'records/community/{pid}/{rid}_submission_{issue["number"]}_{row["digest"][:12]}.json'
    filename = Path(api.ROOT) / relative
    out['case_id'], out['record_id'] = rid, filename.stem
    row['accepted_credit'] = credit
    filename.parent.mkdir(parents=True, exist_ok=True)
    if filename.exists():
        raise api.Bad('This immutable submitted witness already exists; review the registry before accepting it again.')
    api.save_json(filename, out, indent=1)
    api.save_text(filename.with_suffix('.certify.txt'), row['cout'] + '\n')
    api.save_text(filename.with_suffix('.verify.txt'), row['vout'] + '\n')
    registry_path = Path(api.ROOT) / 'docs/community_records.json'
    registry = api.load_json(registry_path) if registry_path.exists() else {'schema_version': 1, 'entries': []}
    registry['entries'].append({'problem': pid, 'n': n, 'kind': 'coordinates', 'file': relative,
                                'author': credit, 'url': issue['html_url']})
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    api.save_json(registry_path, registry, indent=2)
    log = Path(api.ROOT) / 'records/CONTRIBUTIONS.md'
    if not log.exists():
        api.save_text(log, '# Contributed records\n\nExactly certified, maintainer-accepted coordinate records.\n\n| date | record | s | previous | credit | issue |\n|---|---|---|---|---|---|\n')
    previous = repr(row['current']['s_full']) if row.get('current') else 'none'
    with log.open('a', encoding='utf-8') as stream:
        stream.write(f'| {today} | [{rid}]({Path(relative).relative_to("records").as_posix()}) | {s!r} | {previous} | '
                     f'{escaped(credit)} | [#{issue["number"]}]({issue["html_url"]}) |\n')
    return relative


def main(api):
    mode, event_path, outdir = sys.argv[1:4]
    if mode not in ('check', 'accept'): raise SystemExit('Mode must be check or accept.')
    directory = Path(outdir); directory.mkdir(parents=True, exist_ok=True)
    event = api.load_json(event_path); issue = event['issue']; fields = api.sections(issue.get('body') or '')
    result = {'labels_add': [], 'labels_remove': [], 'accepted': False, 'record': None, 'records': [], 'complete': False,
              'guard_paths': [], 'entries': [], 'attachments': [], 'summary': {}}
    try:
        if mode == 'accept': api.authorize_accept(event, fields)
        rows, attachments, ignored = discover(issue.get('body') or '', fields)
    except (api.Bad, BatchError) as exc:
        result['labels_add'], result['labels_remove'] = ['needs-fix'], ['certified', 'not-certified', 'new-record']
        result['summary'] = {'discovered': 0, 'processed': 0, 'rejected': 1, 'accepted': 0}
        api.save_text(directory / 'comment.md', f'### Could not check this submission\n\n{exc}\n\nNo record was written.\n')
        api.save_json(directory / 'result.json', result, indent=2); return
    result['attachments'] = attachments
    seen, active = {}, []
    single = len(rows) == 1
    for index, row in enumerate(rows, 1):
        row['index'] = index
        if row.get('error'):
            row['status'], row['message'] = 'rejected', row['error']; continue
        try:
            defaults = fields if single and not row.get('archive') else {'problem': fields.get('problem', '') if not row.get('archive') else ''}
            row['rec'], row['pid'] = api.parse_object(row['object'], defaults)
            row['digest'] = hashlib.sha256(json.dumps(row['rec'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            if row['digest'] in seen:
                prior = rows[seen[row['digest']] - 1]
                def provenance_score(candidate):
                    obj = candidate['object']; metadata = candidate.get('metadata', {})
                    return (int(bool(candidate.get('archive'))) + int(bool(obj.get('found_by'))) + int(bool(obj.get('credit')))
                            + 3 * int(bool(obj.get('source_refinement') or obj.get('source_credit') or metadata.get('original_credit'))))
                if provenance_score(row) > provenance_score(prior):
                    # An inline specimen often omits the archive's original-author
                    # and refinement roles. Certify the richer identical witness.
                    prior['status'], prior['message'] = 'duplicate', f'Identical witness with fuller provenance is candidate {index}.'
                    active.remove(prior); active.append(row); seen[row['digest']] = index
                else:
                    row['status'], row['message'] = 'duplicate', f'Identical witness to candidate {seen[row["digest"]]}.'
            else:
                seen[row['digest']] = index; active.append(row)
        except (api.Bad, TypeError, ValueError) as exc:
            row['status'], row['message'] = 'rejected', str(exc)
    result['guard_paths'] = guard_paths(api, active)
    deadline = time.monotonic() + MAX_SECONDS
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(check_one, api, row, directory, deadline) for row in active]
        for future in as_completed(futures):
            future.result()
    winners = {}
    for row in active:
        if not row.get('certified'): continue
        if not row['pid']:
            row['status'], row['message'] = 'untracked', 'Certified 3D pair; propose a polyhedron-in-polyhedron category for review.'
            continue
        key = (row['pid'], row['rec']['n'])
        if key not in winners or row['rec']['s_full'] < winners[key]['rec']['s_full']: winners[key] = row
    for row in active:
        if not row.get('certified') or not row['pid']: continue
        key = (row['pid'], row['rec']['n'])
        if winners[key] is not row:
            row['status'], row['message'] = 'superseded-in-batch', f'A smaller certified witness is candidate {winners[key]["index"]}.'
            continue
        current, filename, reference = api.comparison_records(*key)
        row['current'], row['current_file'], row['reference'] = current, filename, reference
        s = row['rec']['s_full']
        row['beats'] = current is None or s < current['s_full'] - 1e-12
        row['status'] = 'improvement' if row['beats'] else 'not-better'
        if not row['beats']: row['message'] = 'Certified, but equal or larger than the current certified coordinate record.'
        if mode == 'accept' and row['beats']:
            row['accepted_file'] = write_record(api, row, fields, issue)
            row['status'] = 'accepted'; result['records'].append(row['accepted_file'])
    result['accepted'] = bool(result['records']); result['record'] = result['records'][0] if result['records'] else None
    counts = Counter(row['status'] for row in rows)
    summary = {'discovered': len(rows), 'processed': len(rows) - counts['deferred'],
               'certified': sum(bool(row.get('certified')) for row in rows),
               'improvements': counts['improvement'] + counts['accepted'], 'accepted': counts['accepted'],
               'skipped': counts['duplicate'] + counts['superseded-in-batch'] + counts['not-better'],
               'rejected': counts['rejected'] + counts['not-certified'], 'untracked': counts['untracked'],
               'deferred': counts['deferred'], 'ignored_auxiliary_members': ignored, 'statuses': dict(counts)}
    result['summary'] = summary
    result['complete'] = not (summary['rejected'] or summary['untracked'] or summary['deferred'])
    labels = []
    if summary['certified']: labels.append('certified')
    if counts['not-certified']: labels.append('not-certified')
    if summary['improvements']: labels.append('new-record')
    if counts['rejected'] or counts['deferred']: labels.append('needs-fix')
    result['labels_add'] = labels
    result['labels_remove'] = [label for label in ('certified', 'not-certified', 'new-record', 'needs-fix') if label not in labels]
    lines = ['### Packing submission results', '',
             f'**{summary["discovered"]} candidates found; {summary["processed"]} processed; '
             f'{summary["certified"]} exactly certified; {summary["improvements"]} certified coordinate improvements; '
             f'{summary["accepted"]} accepted; {summary["skipped"]} skipped; {summary["rejected"]} rejected; '
             f'{summary["untracked"]} untracked 3D pairs; {summary["deferred"]} deferred.**', '',
             'Every discovered witness has a separate result in the `submission-results` workflow artifact '
             '(`result.json`, `results.csv`, and the trusted checker logs). Auxiliary source/history files and submitted '
             'scripts are ignored; submitted code and certificates are never executed or trusted.', '',
             '| Candidate | Case | s_full | Result | Detail |', '|---|---|---:|---|---|']
    public_entries = []
    for row in rows:
        entry = {key: row[key] for key in ('index', 'source', 'status', 'message', 'accepted_file', 'archive_sha256', 'witness_sha256') if key in row}
        if row.get('rec'):
            entry.update({'problem': row.get('pid'), 'piece': row['rec']['piece'], 'container': row['rec']['container'],
                          'n': row['rec']['n'], 's_full': row['rec']['s_full'], 'certified': bool(row.get('certified'))})
        public_entries.append(entry)
        if row['index'] <= 80:
            case = f'{row["pid"] or row["rec"]["piece"] + " in " + row["rec"]["container"]}_n{row["rec"]["n"]:02d}' if row.get('rec') else 'unreadable / unsupported'
            lines.append(f'| {row["index"]} | {escaped(case)} | {row["rec"]["s_full"] if row.get("rec") else "—"} | {row["status"]} | {escaped(row.get("message", ""))} |')
    if len(rows) > 80: lines += ['', f'The remaining {len(rows) - 80} per-candidate outcomes are in the workflow artifact.']
    # Keep small submissions convenient without exceeding GitHub's comment-size limit for large batches.
    for row in active[:6]:
        rec = row['rec']; current = row.get('current'); reference = row.get('reference')
        lines += ['', f'#### Candidate {row["index"]}: {row["status"]}', '', f'Submitted s: `{rec["s_full"]!r}`.']
        if current:
            delta = rec['s_full'] - current['s_full']
            lines += [f'Current certified coordinate record: `{current["s_full"]!r}`, found by {escaped(current.get("found_by", "?"))} '
                      f'([record]({api.REPO}/blob/main/{row["current_file"]})). Difference: {delta:+.3e} '
                      f'({"equal" if delta == 0 else "smaller, better" if delta < 0 else "larger"}).']
        if reference:
            lines += [f'Published reference: `{reference["published_value"]!r}`, {escaped(reference["author"])} ([source]({reference["url"]})).']
            if reference['published_value'] < rec['s_full'] - max(1e-5, reference.get('display_quantum', 1e-5)):
                lines += ['This comparison does not certify that source; this submission is not an improvement over its reported scale. Acceptance compares certified coordinates.']
        if row.get('message'): lines += [escaped(row['message'])]
        if row.get('vout'):
            lines += ['<details><summary>Float check</summary>', '', '```', row['vout'][-1500:], '```', '</details>']
        if row.get('cout'):
            lines += ['<details><summary>Exact certificate</summary>', '', '```', row['cout'][-2000:], '```', '</details>']
        if row.get('accepted_file'):
            lines += [f'**Accepted and recorded** as [this immutable coordinate record]({api.REPO}/blob/main/{row["accepted_file"]}), '
                      f'credited to {escaped(row["accepted_credit"])}. '
                      f'It appears on [the site]({api.SITE}#{row["pid"]}_n{rec["n"]:02d}) after the rebuild.']
    if summary['untracked']: lines += ['', f'[Propose the category]({api.REPO}/issues/new?template=new-category.yml) for untracked 3D convex polyhedra. 2D packings are outside this archive.']
    if not result['accepted'] and mode == 'accept': lines += ['', '**Not recorded:** only exactly certified improvements to tracked polyhedron-in-polyhedron cases can be accepted.']
    if mode == 'check' and summary['improvements']: lines += ['', 'A maintainer can accept all eligible improvements with the `accepted` label; each candidate is checked again against the then-current archive.']
    if not result['complete']: lines += ['', 'This batch remains open: rejected, unsupported, untracked or deferred candidates require review. Positive clearance is required; no touching or overlapping packing is accepted.']
    result['entries'] = public_entries
    api.save_json(directory / 'result.json', result, indent=2)
    with (directory / 'results.csv').open('w', newline='', encoding='utf-8') as stream:
        keys = ['index', 'problem', 'piece', 'container', 'n', 's_full', 'status', 'certified', 'message', 'source', 'accepted_file']
        writer = csv.DictWriter(stream, fieldnames=keys, extrasaction='ignore'); writer.writeheader(); writer.writerows(public_entries)
    api.save_text(directory / 'comment.md', '\n'.join(lines) + '\n')
