#!/usr/bin/env python3
"""Summarize current, hash-matched Lean evidence from explicit receipt files.

This program never invokes Lean and never turns exported/generated records
into verified records. Failed and stale evidence is retained separately.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent
INPUTS = HERE / 'inputs'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    try:
        return str(path.resolve().relative_to(FORMAL)).replace('\\', '/')
    except ValueError:
        return str(path.resolve())


def labels(value):
    if value is None or value == '':
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return [str(value)]


def inventory():
    ci = json.loads((HERE/'inventory/catalogue-inventory.json').read_text(encoding='utf8'))
    ni = json.loads((HERE/'inventory/rational-nd-inventory.json').read_text(encoding='utf8'))
    if ci['freeze_git_sha'] != FREEZE or ni['freeze_git_sha'] != FREEZE:
        raise ValueError('Unexpected catalogue freeze')
    rows = []
    for dimension_kind, source_rows in [('cube', ci['cube_native_records']), ('nd', ni['records'])]:
        for source in source_rows:
            path = INPUTS/source['file']
            raw = json.loads(path.read_bytes())
            if sha(path) != source['sha256']:
                raise ValueError('Frozen input hash mismatch: '+source['file'])
            rid = path.stem
            folder = 'witnesses' if dimension_kind == 'cube' else 'witnesses_nd'
            witness_path = HERE/folder/(rid+'.json')
            w = json.loads(witness_path.read_text(encoding='utf8'))
            source_path = source['file'].replace('\\', '/')
            if w['source_path'] != source_path or w['source_sha256'] != source['sha256']:
                raise ValueError('Exported witness provenance mismatch: '+rid)
            n, d = raw['n'], 3 if dimension_kind == 'cube' else raw['dim']
            if w['n'] != n or w['dimension'] != d or len(raw['pieces']) != n:
                raise ValueError('Input dimension/piece count mismatch: '+rid)
            problem = 'cubincub' if dimension_kind == 'cube' else source['problem']
            authors = labels(raw.get('found_by', raw.get('author', raw.get('authors')))) or ['Unspecified']
            author_labels = ['Alejandro Zarzuelo' if a.startswith('Alejandro Zarzuelo (') else a
                for a in authors]
            refiners = labels(raw.get('certificate_refined_by'))
            k = len(w['template_vertices'])
            l = 8 if dimension_kind == 'cube' else len(w['container_vertices'])
            rows.append(dict(record_id=rid, catalogue_key=f'{problem}_n{n:02}',
                problem_family=problem, family_group=raw.get('family', 'platonic' if d == 3 else f'{d}d'),
                dimension=d, n=n, piece=raw['piece'], container=raw['container'],
                construction_authors=author_labels, construction_authors_verbatim=authors,
                source_credit=raw.get('credit'), certificate_refiners=refiners,
                source_path=source_path, source_json_sha256=source['sha256'],
                witness_path=rel(witness_path), witness_sha256=sha(witness_path),
                geometry_path=w.get('geometry_path'), geometry_sha256=w.get('geometry_sha256'),
                template_vertices=k, container_vertices=l,
                piece_vertices=n*k, unordered_pairs=n*(n-1)//2,
                vertex_wall_tests=n*k*6 if d == 3 else 0,
                vertex_membership_tests=n*k if d > 3 else 0))
    if len(rows) != 402 or len({r['record_id'] for r in rows}) != 402:
        raise ValueError('Expected exactly 402 distinct eligible records')
    return rows


def artifact_path(value):
    path = (FORMAL/value).resolve()
    path.relative_to(FORMAL)
    return path


def identify(row, text, by_id, by_path):
    candidates = []
    if row.get('record_id'):
        candidates.append(row['record_id'])
    candidate = row.get('id', '')
    candidates.append(candidate)
    while '_' in candidate:
        candidate = candidate.split('_', 1)[1]
        candidates.append(candidate)
    selected = next((by_id[r] for r in candidates if r in by_id), None)
    match = re.search(r'^-- (?:Original source|Exact source):\s*(.*?)\s*$', text, re.M)
    if not match:
        raise ValueError('Missing original-source comment')
    comment_path = match.group(1).replace('\\', '/')
    if comment_path not in by_path:
        raise ValueError('Source comment is outside the 402-record scope')
    from_path = by_path[comment_path]
    if selected and selected['record_id'] != from_path['record_id']:
        raise ValueError('Receipt ID and source comment identify different records')
    selected = from_path
    match = re.search(r'^-- (?:Original JSON SHA256|JSON SHA256):\s*([0-9a-f]{64})\s*$', text, re.M)
    if not match or match.group(1) != selected['source_json_sha256']:
        raise ValueError('Original JSON hash comment mismatch')
    if row.get('original_json_sha256', selected['source_json_sha256']) != selected['source_json_sha256']:
        raise ValueError('Receipt original JSON hash mismatch')
    if row.get('n') != selected['n'] or row.get('dimension', selected['dimension']) != selected['dimension']:
        raise ValueError('Receipt dimension/piece count mismatch')
    return selected


def parse_axioms(log):
    audited = {name: sorted(v.strip() for v in values.split(',') if v.strip())
        for name, values in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", log, re.S)}
    audited.update({name: [] for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", log)})
    return audited


def verify_core_maps(receipt, required=False):
    source_map = receipt.get('core_source_hashes')
    object_map = receipt.get('core_olean_hashes')
    if source_map is None and object_map is None:
        if required:
            raise ValueError('chunk_receipt_missing_core_dependency_hashes')
        return {'status': 'not_recorded_in_original_receipt',
            'limitation': 'Generated source, object and log hashes match; this older receipt did not record core dependency hashes.'}
    if required and (not source_map or not object_map):
        raise ValueError('incomplete_core_dependency_hash_maps')
    for mapping in (source_map, object_map):
        for path, expected in (mapping or {}).items():
            current = artifact_path(path)
            if not current.is_file() or sha(current) != expected:
                raise ValueError('recorded_core_dependency_changed: '+path)
    status = 'recorded_hashes_match_current_files'
    limitation = None
    if source_map and not object_map:
        status = 'recorded_source_hashes_match_objects_not_recorded'
        limitation = 'Every recorded core source hash matches; this ordinary receipt did not record core object hashes.'
    elif object_map and not source_map:
        status = 'recorded_object_hashes_match_sources_not_recorded'
        limitation = 'Every recorded core object hash matches; this ordinary receipt did not record core source hashes.'
    return {'status': status, 'source_hashes': source_map,
        'olean_hashes': object_map, 'limitation': limitation}


def inspect_chunks(row, receipt, selected):
    if not row.get('complete') or not row.get('steps'):
        raise ValueError('chunk_record_not_complete')
    manifest = (HERE/receipt['manifest']).resolve()
    manifest.relative_to(HERE)
    if not manifest.is_file() or sha(manifest) != receipt.get('manifest_sha256'):
        raise ValueError('chunk_plan_manifest_missing_or_changed')
    plans = json.loads(manifest.read_text(encoding='utf8'))
    matches = [p for p in plans if p.get('id') == row['id'] and
        p.get('record_id', p.get('id')) == selected['record_id']]
    if len(matches) != 1:
        raise ValueError('chunk_record_has_no_unique_matching_plan')
    plan = matches[0]
    ordinary = row.get('portable_original_kind') == 'ordinary'
    if ordinary:
        # A portable single-step manifest may not carry its normalized step.
        if len(row['steps']) != 1 or row['steps'][0].get('kind') != 'ordinary':
            raise ValueError('invalid_portable_ordinary_step')
        expected_steps = [dict(plan, **{k: row['steps'][0][k]
            for k in ('id', 'kind', 'expected_audits', 'generated_source_sha256')})]
    else:
        expected_steps = plan.get('steps', [])
        if not expected_steps or expected_steps[0].get('kind') != 'data' or expected_steps[-1].get('kind') != 'aggregate':
            raise ValueError('chunk_plan_missing_data_or_aggregate')
        if any(s.get('kind') != 'proof_block' for s in expected_steps[1:-1]):
            raise ValueError('unexpected_chunk_plan_stage')
        indices = [i for s in expected_steps if s['kind'] == 'proof_block' for i in s['piece_indices']]
        if indices != list(range(selected['n'])):
            raise ValueError('chunk_piece_indices_do_not_cover_every_piece_exactly_once')
        if plan.get('fine_vertex_coverage'):
            if plan.get('fine_vertex_coverage') is not True or row.get('fine_vertex_coverage') is not True:
                raise ValueError('fine_vertex_coverage_flag_mismatch')
            vertex_count = plan.get('vertex_count')
            if vertex_count != selected['template_vertices'] or row.get('vertex_count') != vertex_count:
                raise ValueError('fine_vertex_count_does_not_match_canonical_template')
            vertex_pairs = [tuple(pair) for s in expected_steps
                for pair in s.get('vertex_indices', [])]
            required_pairs = {(i, p) for i in range(selected['n']) for p in range(vertex_count)}
            if len(vertex_pairs) != len(required_pairs) or set(vertex_pairs) != required_pairs:
                raise ValueError('fine_vertex_indices_do_not_cover_every_piece_vertex_exactly_once')
        for field, actual in [('original_source_path', selected['source_path']),
                ('original_json_sha256', selected['source_json_sha256']),
                ('original_witness_sha256', selected['witness_sha256'])]:
            if plan.get(field) != actual or row.get(field) != actual:
                raise ValueError('chunk_frozen_provenance_mismatch: '+field)
        if selected['dimension'] > 3:
            geometry = INPUTS/selected['geometry_path']
            if not geometry.is_file() or sha(geometry) != selected['geometry_sha256']:
                raise ValueError('canonical_geometry_hash_mismatch')
            for field, actual in [('original_geometry_path', selected['geometry_path']),
                    ('original_geometry_sha256', selected['geometry_sha256'])]:
                if plan.get(field) != actual or row.get(field) != actual:
                    raise ValueError('chunk_geometry_provenance_mismatch: '+field)
    if len(row['steps']) != len(expected_steps):
        raise ValueError('not_every_planned_chunk_step_was_built')
    if row['path'] != expected_steps[-1]['path'] or row['module'] != expected_steps[-1]['module']:
        raise ValueError('chunk_aggregate_does_not_match_plan')
    prior, source_hashes, dependencies, steps, all_axioms = {}, {}, [], [], set()
    for expected, built in zip(expected_steps, row['steps']):
        for key in ('id', 'path', 'module', 'kind'):
            if built.get(key) != expected.get(key):
                raise ValueError('chunk_step_does_not_match_plan: '+key)
        if built.get('piece_indices') != expected.get('piece_indices'):
            raise ValueError('chunk_step_piece_indices_differ_from_plan')
        if built.get('vertex_indices') != expected.get('vertex_indices'):
            raise ValueError('chunk_step_vertex_indices_differ_from_plan')
        if not built.get('passed') or built.get('exit_code') != 0:
            raise ValueError('unpassed_chunk_step')
        if built.get('all_sources_stable') is not True or built.get('source_unchanged_during_build') is False:
            raise ValueError('chunk_sources_were_not_stable_during_build')
        source = artifact_path(built['path'])
        obj = source.with_suffix('.olean')
        logpath = artifact_path(built['log'])
        if not source.is_file() or sha(source) != built.get('source_sha256') or sha(source) != expected.get('generated_source_sha256'):
            raise ValueError('chunk_dependency_source_hash_mismatch: '+built['path'])
        if not obj.is_file() or sha(obj) != built.get('olean_sha256'):
            raise ValueError('chunk_dependency_olean_hash_mismatch: '+built['path'])
        if not logpath.is_file() or sha(logpath) != built.get('log_sha256'):
            raise ValueError('chunk_dependency_log_hash_mismatch: '+built['path'])
        if built.get('dependency_olean_hashes') != prior:
            raise ValueError('chunk_dependency_chain_mismatch: '+built['path'])
        log = logpath.read_text(encoding='utf8')
        audited = parse_axioms(log)
        audits = expected.get('expected_audits', [])
        if not audits or not all(a in audited for a in audits) or built.get('all_expected_audits_seen') is not True:
            raise ValueError('chunk_required_axiom_audit_missing: '+built['path'])
        used = {a for values in audited.values() for a in values}
        if used-ALLOWED or 'sorryAx' in log or built.get('unexpected_axioms') or set(built.get('axioms', [])) != used:
            raise ValueError('chunk_unexpected_or_unmatched_axioms: '+built['path'])
        imports = re.findall(r'^import\s+(PackingCertificates\.Catalogue\.[\w.]+)', source.read_text(encoding='utf8'), re.M)
        if any(name not in prior for name in imports):
            raise ValueError('chunk_imports_an_unverified_record_dependency: '+built['path'])
        source_hashes[built['path']] = sha(source)
        prior[built['module']] = sha(obj)
        all_axioms |= used
        evidence = dict(built, source_sha256=sha(source), olean_path=rel(obj),
            olean_sha256=sha(obj), log_sha256=sha(logpath), audited_theorems=audited)
        steps.append(evidence)
        if built['kind'] not in ('aggregate', 'ordinary'):
            dependencies.append(evidence)
    if row.get('source_hashes_before') != source_hashes or row.get('source_hashes_after') != source_hashes:
        raise ValueError('chunk_whole_plan_source_stability_mismatch')
    if row.get('dependency_olean_hashes') != prior or set(row.get('axioms', [])) != all_axioms:
        raise ValueError('chunk_final_dependency_or_axiom_summary_mismatch')
    if not ordinary:
        if row.get('dependency_source_hashes') != {d['path']: d['source_sha256'] for d in dependencies}:
            raise ValueError('chunk_dependency_source_summary_mismatch')
        if row.get('dependency_object_hashes') != {d['olean_path']: d['olean_sha256'] for d in dependencies}:
            raise ValueError('chunk_dependency_object_summary_mismatch')
    return dict(dependencies=dependencies, steps=steps, plan=plan,
        plan_manifest_path=rel(manifest), plan_manifest_sha256=sha(manifest),
        core_dependencies=verify_core_maps(receipt, required=True),
        all_step_axioms=sorted(all_axioms))


def inspect(row, receipt_path, receipt, by_id, by_path):
    result = {'receipt': rel(receipt_path), 'receipt_id': row.get('id'),
        'module': row.get('module'), 'record_id': row.get('record_id'), 'reasons': []}
    if not row.get('passed') or row.get('exit_code') != 0:
        result['reasons'].append('receipt_reports_failed_or_incomplete_build')
        result['exit_code'] = row.get('exit_code')
        return None, result
    try:
        source = artifact_path(row['path'])
        target = source.with_suffix('.olean')
        logpath = artifact_path(row['log'])
        if not source.is_file() or sha(source) != row.get('source_sha256'):
            raise ValueError('generated_source_missing_or_changed_since_receipt')
        if row.get('source_unchanged_during_build') is False:
            raise ValueError('source_changed_during_build')
        if not target.is_file() or sha(target) != row.get('olean_sha256'):
            raise ValueError('olean_missing_or_hash_mismatch')
        if not logpath.is_file() or sha(logpath) != row.get('log_sha256'):
            raise ValueError('build_log_missing_or_hash_mismatch')
        text, log = source.read_text(encoding='utf8'), logpath.read_text(encoding='utf8')
        selected = identify(row, text, by_id, by_path)
        result['record_id'] = selected['record_id']
        audited = parse_axioms(log)
        module = row['module']
        required = [module+'.packing']
        if selected['dimension'] > 3:
            required += [module+'.source_valid', module+'.proper_orientation']
        if not all(name in audited for name in required):
            raise ValueError('required_semantic_theorem_axiom_audit_missing')
        used = set().union(*(set(values) for values in audited.values())) if audited else set()
        if used-ALLOWED or 'sorryAx' in log or row.get('unexpected_axioms'):
            raise ValueError('unexpected_or_admitted_axiom')
        summary_axioms = set(row.get('axioms', []))
        if not row.get('audit_output_seen') or (used != summary_axioms if not row.get('steps') else not used <= summary_axioms):
            raise ValueError('receipt_axiom_summary_does_not_match_log')
        evidence = dict(module=module, generated_source_path=rel(source),
            generated_source_sha256=sha(source), olean_path=rel(target),
            olean_sha256=sha(target), log_path=rel(logpath), log_sha256=sha(logpath),
            receipt_path=rel(receipt_path), receipt_sha256=sha(receipt_path),
            receipt_checked_at_utc=receipt.get('checked_at_utc'),
            artifact_mtime_utc=datetime.fromtimestamp(target.stat().st_mtime, timezone.utc).isoformat(),
            elapsed_seconds=row.get('elapsed_seconds'), axioms=sorted(used),
            audited_theorems=audited, checking_strategy=row.get('checking_strategy'),
            fragmentation=row.get('fragmentation'), pair_fragmentation=row.get('pair_fragmentation'))
        if row.get('steps'):
            evidence.update(inspect_chunks(row, receipt, selected))
        else:
            evidence['core_dependencies'] = verify_core_maps(receipt)
        return (selected, evidence, (target.stat().st_mtime_ns,
            receipt.get('checked_at_utc') or '', receipt_path.stat().st_mtime_ns)), None
    except (KeyError, ValueError, OSError) as error:
        result['reasons'].append(str(error))
        return None, result


def totals(rows):
    return {'records': len(rows), 'pieces': sum(r['n'] for r in rows),
        'piece_vertices': sum(r['piece_vertices'] for r in rows),
        'container_vertices': sum(r['container_vertices'] for r in rows),
        'unordered_pairs': sum(r['unordered_pairs'] for r in rows),
        'vertex_wall_tests': sum(r['vertex_wall_tests'] for r in rows),
        'vertex_membership_tests': sum(r['vertex_membership_tests'] for r in rows)}


def grouped(rows, key):
    groups = {}
    for row in rows:
        values = row[key] if isinstance(row[key], list) else [row[key]]
        for value in values:
            groups.setdefault(str(value), []).append(row)
    return {name: dict(totals(items), n_values=sorted({r['n'] for r in items}))
        for name, items in sorted(groups.items())}


def coverage(summary):
    vt, et = summary['verified_totals'], summary['eligible_totals']
    lines = ['# Lean-verified catalogue coverage', '',
        f"Generated: {summary['generated_at_utc']}", '',
        f"Frozen catalogue commit: `{FREEZE}`.", '',
        f"**{vt['records']} of {et['records']} eligible records** have current, hash-matched, "
        'successful Lean evidence in the explicitly supplied receipts. This count excludes '
        'stale artifacts, failed builds, and uncompiled exports.', '',
        f"The verified instances contain **{vt['pieces']} pieces**, "
        f"**{vt['piece_vertices']} piece vertices**, and **{vt['unordered_pairs']} unordered pairs**.", '',
        '| Dimension | Verified records | Eligible records |', '|---|---:|---:|']
    for d, entry in summary['eligible_by_dimension'].items():
        lines.append(f"| {d} | {summary['verified_by_dimension'].get(d, {}).get('records', 0)} | {entry['records']} |")
    lines += ['', '| Family | Verified | Eligible | Verified n |', '|---|---:|---:|---|']
    for name, entry in summary['eligible_by_family'].items():
        v = summary['verified_by_family'].get(name, {})
        ns = ', '.join(map(str, v.get('n_values', []))) or '-'
        lines.append(f"| {name} | {v.get('records', 0)} | {entry['records']} | {ns} |")
    lines += ['', 'Construction author labels below follow the frozen record metadata; '
        'parenthetical notes attached to Alejandro Zarzuelo are retained verbatim in the JSON '
        'and grouped under the same person here. Certificate refinement is counted separately '
        'and is not relabelled as a new construction.', '',
        '| Construction author | Verified records |', '|---|---:|']
    for name, entry in summary['verified_by_construction_author'].items():
        lines.append(f"| {name} | {entry['records']} |")
    if summary['verified_by_certificate_refiner']:
        lines += ['', '| Certificate refiner | Verified records refined |', '|---|---:|']
        for name, entry in summary['verified_by_certificate_refiner'].items():
            lines.append(f"| {name} | {entry['records']} |")
    lines += ['', f"Ignored evidence rows: **{len(summary['ignored_rows'])}**. "
        f"Superseded duplicate successful modules: **{len(summary['superseded_verified_modules'])}**.", '',
        'The JSON manifest lists every eligible record, the selected evidence for each verified '
        'record, all ignored rows and their reasons, and all superseded valid modules.', '',
        'These are feasibility proofs for explicit canonical coordinate models and frozen '
        'placements. They do not prove global optimality, verify a parser or optimizer, '
        'classify every named regular polytope, or certify the entire live catalogue.', '']
    older = sum(r['evidence'].get('core_dependencies', {}).get('status') ==
        'not_recorded_in_original_receipt' for r in summary['verified_records'])
    if older:
        lines += [f'{older} selected records retain earlier receipts without recorded core '
            'dependency hashes. Their generated source, object and log hashes match; '
            'the missing older dependency attestation is retained as an explicit limitation.', '']
    partial = sum(r['evidence'].get('core_dependencies', {}).get('status') in
        ('recorded_source_hashes_match_objects_not_recorded',
         'recorded_object_hashes_match_sources_not_recorded') for r in summary['verified_records'])
    if partial:
        lines += [f'{partial} selected ordinary receipts record only one core hash map. '
            'Every recorded hash matches; the absent source or object attestation is '
            'identified in each evidence entry. Chunked receipts require both maps.', '']
    return '\n'.join(lines)


def resolve_receipt(value):
    path = Path(value)
    if path.is_file():
        return path.resolve()
    path = HERE/value
    if path.is_file():
        return path.resolve()
    raise FileNotFoundError('Receipt not found: '+value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts', nargs='+', required=True)
    ap.add_argument('--output', type=Path, default=HERE/'verified-catalogue.json')
    ap.add_argument('--coverage', type=Path, default=HERE/'coverage.md')
    args = ap.parse_args()
    eligible = inventory()
    by_id = {r['record_id']: r for r in eligible}
    by_path = {r['source_path']: r for r in eligible}
    selected, ignored, superseded, receipts = {}, [], [], []
    for value in args.receipts:
        path = resolve_receipt(value)
        receipt = json.loads(path.read_text(encoding='utf8'))
        receipts.append({'path': rel(path), 'sha256': sha(path),
            'checked_at_utc': receipt.get('checked_at_utc'), 'compiler': receipt.get('compiler')})
        for row in receipt.get('results', []):
            valid, failure = inspect(row, path, receipt, by_id, by_path)
            if failure:
                ignored.append(failure)
                continue
            record, evidence, rank = valid
            key = record['record_id']
            if key in selected:
                previous = selected[key]
                if rank > previous[2]:
                    superseded.append(dict(record_id=key, evidence=previous[1]))
                    selected[key] = valid
                else:
                    superseded.append(dict(record_id=key, evidence=evidence))
            else:
                selected[key] = valid
    verified = [dict(r, evidence=selected[r['record_id']][1])
        for r in eligible if r['record_id'] in selected]
    scope = [dict(r, verified=r['record_id'] in selected) for r in eligible]
    summary = dict(generated_at_utc=datetime.now(timezone.utc).isoformat(),
        freeze_git_sha=FREEZE, allowed_axioms=sorted(ALLOWED), receipt_inputs=receipts,
        eligible_totals=totals(eligible), verified_totals=totals(verified),
        eligible_by_dimension=grouped(eligible, 'dimension'),
        verified_by_dimension=grouped(verified, 'dimension'),
        eligible_by_family=grouped(eligible, 'problem_family'),
        verified_by_family=grouped(verified, 'problem_family'),
        verified_by_family_group=grouped(verified, 'family_group'),
        verified_by_construction_author=grouped(verified, 'construction_authors'),
        verified_by_certificate_refiner=grouped(verified, 'certificate_refiners'),
        verified_records=verified, eligible_records=scope, ignored_rows=ignored,
        superseded_verified_modules=superseded,
        trust_boundary='Successful kernel builds of explicit coordinate models; '
            'JSON parsing, source transcription and regular-polytope classification beyond the proved box models remain outside the kernel.')
    args.output.write_text(json.dumps(summary, indent=2)+'\n', encoding='utf8')
    args.coverage.write_text(coverage(summary), encoding='utf8')
    print(json.dumps({'verified_records': len(verified), 'eligible_records': len(eligible),
        'ignored_rows': len(ignored), 'superseded_modules': len(superseded),
        'output': str(args.output), 'coverage': str(args.coverage)}))


if __name__ == '__main__':
    main()
