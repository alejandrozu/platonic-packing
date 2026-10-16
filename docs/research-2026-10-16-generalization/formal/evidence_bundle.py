#!/usr/bin/env python3
"""Validate or unpack portable Lean source/log evidence without proof objects.

Unpacking preserves each build environment's own formal root. It never merges
different environments, invokes a shell/compiler, or overwrites differing bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile

FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'
ALLOWED_AXIOMS = {'Classical.choice', 'Quot.sound', 'propext'}
COMPILED_SUFFIXES = {'.olean', '.ilean', '.trace', '.o', '.obj', '.pyc'}
COHORTS = {'published-402': ('rational-402', 402),
           'published-85': ('algebraic-3d85', 85),
           'published-45': ('algebraic-nd45', 45)}
MAX_BYTES = 8 * 1024**3


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def sha_value(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('Expected a lowercase SHA-256 value')
    return value


def safe_name(value, *, allow_compiled=False):
    if not isinstance(value, str) or not value or '\\' in value or '\x00' in value:
        raise ValueError('Unsafe evidence path '+repr(value))
    parts = value.split('/')
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *('COM'+str(i) for i in range(1, 10)),
                *('LPT'+str(i) for i in range(1, 10))}
    if (PurePosixPath(value).is_absolute() or any(
            not p or p in {'.', '..'} or ':' in p or p.endswith((' ', '.')) or
            p.split('.')[0].upper() in reserved for p in parts)):
        raise ValueError('Unsafe evidence path '+repr(value))
    if any(p in {'.git', '.lake', '__pycache__'} for p in parts):
        raise ValueError('Cache/repository metadata in evidence path '+value)
    if not allow_compiled and PurePosixPath(value).suffix.lower() in COMPILED_SUFFIXES:
        raise ValueError('Compiled/cache object in source evidence '+value)
    return value


def raw_artifact_rows(value):
    """Index exact immutable archive identities, without opening object ZIPs."""
    if value is None:
        return {}
    if value.get('schema') != 'preserved-lean-artifact-index-v1':
        raise ValueError('Unsupported raw artifact provenance index')
    rows = {}
    for row in value['artifacts']:
        key = f'run-{row["run_id"]}-artifact-{row["artifact_id"]}'
        if key in rows:
            raise ValueError('Duplicate raw artifact provenance identity '+key)
        sha_value(row['sha256'])
        rows[key] = row
    return rows


def check_environment_storage(row, raw_artifacts):
    """A streamed object view must identify its hash-checked preserved archive."""
    mode = row.get('storage_mode', 'extracted')
    if mode == 'extracted':
        if row.get('object_store') is not None:
            raise ValueError('Extracted environment unexpectedly declares streamed objects')
        return
    if mode != 'zip-streamed-objects':
        raise ValueError('Unsupported evidence environment storage mode')
    descriptor = row.get('object_store')
    if not isinstance(descriptor, dict) or descriptor.get('schema') != 'zip-streamed-proof-objects-v1':
        raise ValueError('Streamed environment lacks an approved object-store descriptor')
    for flag in ('objects_not_extracted', 'all_inventory_members_hashed',
                 'raw_archive_fresh_final_hash_passed'):
        if descriptor.get(flag) is not True:
            raise ValueError('Streamed object store lacks a completed invariant '+flag)
    if row.get('evidence_zip_path') is not None:
        raise ValueError('Streamed environment must retain its nested ZIP virtually')
    key = f'run-{row["run_id"]}-artifact-{row["artifact_id"]}'
    if descriptor.get('raw_artifact_index_key') != key or key not in raw_artifacts:
        raise ValueError('Streamed object store references an absent/different raw artifact')
    artifact = raw_artifacts[key]
    digest = sha_value(descriptor['raw_archive_sha256'])
    if digest != sha_value(row['github_archive_sha256']) or digest != artifact['sha256']:
        raise ValueError('Streamed object store/raw-index archive SHA256 mismatch')
    if artifact.get('head_sha') != row.get('run_head_sha'):
        raise ValueError('Streamed object store/raw-index commit mismatch')
    if artifact.get('path') != row.get('github_archive_path'):
        raise ValueError('Streamed object store/raw-index archive locator mismatch')
    if sha_value(descriptor['nested_sha256']) != sha_value(row['evidence_zip_sha256']):
        raise ValueError('Streamed object store nested archive SHA256 mismatch')
    safe_name(descriptor['nested_member'])
    inventory = safe_name(descriptor['inventory_member'])
    if not inventory.startswith('formal/') or not inventory.endswith('/evidence-inventory.json'):
        raise ValueError('Streamed object inventory lies outside its formal evidence namespace')
    sha_value(descriptor['inventory_sha256'])
    count = descriptor.get('primary_object_count')
    if type(count) is not int or count < 0:
        raise ValueError('Streamed object count must be a nonnegative integer')


def check_compact_evidence(compact, full):
    for key in ('olean_path', 'olean_sha256'):
        if key not in compact or key not in full or compact[key] != full[key]:
            raise ValueError('Compact/complete evidence mismatch '+key)
    object_path = safe_name(compact['olean_path'], allow_compiled=True)
    if PurePosixPath(object_path).suffix != '.olean':
        raise ValueError('Recorded proof object must be a logical .olean path')
    sha_value(compact['olean_sha256'])
    for key in ('module', 'generated_source_path', 'generated_source_sha256', 'log_path', 'log_sha256',
                'receipt_path', 'receipt_sha256', 'plan_manifest_path', 'plan_manifest_sha256', 'audited_theorems'):
        if key in compact and compact[key] != full.get(key):
            raise ValueError('Compact/complete evidence mismatch '+key)


def check_approved_publication_version(row, prefix, bundle, validation):
    fields=('approved_publication_manifest_member','approved_publication_manifest_sha256','approved_helper_versions')
    if not any(key in row for key in fields):return
    if any(key not in row for key in fields):raise ValueError('Incomplete approved publication-version metadata')
    member=safe_name(row[fields[0]])
    candidates={prefix+'/catalogue/algebraic/ci-pilot-assets.json':('algebraic-pilot-assets-v1',85,'algebraic-3d85'),
        prefix+'/catalogue/algebraic/ci-nd45-assets.json':('nd45-publication-assets-v1',45,'algebraic-nd45')}
    if member not in candidates:raise ValueError('Approved publication manifest belongs to another namespace')
    expected=row[fields[1]];manifest=bundle.json(member,expected)
    schema,count,cohort=candidates[member]
    if (manifest.get('schema')!=schema or manifest.get('record_count')!=count or
            manifest.get('frozen_commit')!=FREEZE or validation.get('publication_manifest_sha256')!=expected or
            validation.get('expected_record_count')!=count or validation.get('cohort_id')!=cohort):
        raise ValueError('Approved publication manifest identity/hash differs from independent replay')
    helpers={}
    for asset in manifest['files']:
        name=safe_name(asset['path'])
        if name.endswith('.py'):
            if name in helpers:raise ValueError('Duplicate approved publication helper')
            helpers[name]=sha_value(asset['sha256'])
    declared={}
    for helper in row[fields[2]]:
        name=safe_name(helper['path'])
        if name in declared:raise ValueError('Duplicate declared approved helper version')
        declared[name]=sha_value(helper['sha256'])
        bundle.member(prefix+'/'+name,declared[name])
    if declared!=helpers:raise ValueError('Approved helper versions differ from the environment publication manifest')


def check_final_cohort_metadata(metadata, modules, current):
    """Reject finalized proof pointers made stale by any cohort re-publication."""
    names=set(current)
    if names not in ({'published-402'},set(COHORTS)):
        raise ValueError('Final metadata requires either the rational-only or all three cohorts')
    if metadata.get('schema')!='portable-paper-verification-v2':
        raise ValueError('Unsupported final verification metadata')
    if modules.get('schema')!='environment-scoped-lean-module-manifest-v1':
        raise ValueError('Unsupported finalized environment module manifest')
    actual={}
    for row in metadata.get('portable_cohorts',[]):
        directory=row.get('directory')
        if directory in actual:raise ValueError('Duplicate finalized portable cohort')
        actual[directory]=row
    if set(actual)!={'ci-evidence/'+name for name in names}:
        raise ValueError('Final metadata portable cohort scope differs from the current publication')
    for name,(report,validation)in current.items():
        expected_count=COHORTS[name][1]
        if (validation.get('records')!=expected_count or report['verified_totals']['records']!=expected_count or
                len(report['verified_records'])!=expected_count):
            raise ValueError('Incomplete cohort cannot be sealed into final metadata '+name)
        row=actual['ci-evidence/'+name]
        for key,value in validation.items():
            if row.get(key)!=value:raise ValueError('Stale finalized cohort SHA/count metadata '+name+' '+key)
    rational,checked=current['published-402']
    additional=[r for name,(report,_)in current.items()if name!='published-402'for r in report['verified_records']]
    def family(row):return(row['dimension'],row['piece'],row['container'])
    counts=dict(archive_records_formally_imported=402,additional_algebraic_records=len(additional),
        additional_algebraic_families=len({family(r)for r in additional}),
        verified_problem_families=len({family(r)for r in [*rational['verified_records'],*additional]}))
    if any(metadata.get(key)!=value for key,value in counts.items()):
        raise ValueError('Finalized rational/additional family counts differ from current cohorts')
    if (metadata.get('catalogue_receipt')!='ci-evidence/published-402/verified-catalogue.json' or
            metadata.get('catalogue_receipt_sha256')!=checked['summary_sha256'] or
            metadata.get('verified_totals')!=rational['verified_totals']):
        raise ValueError('Finalized rational catalogue pointer/totals changed')
    def environments(entry,report):
        expected={e['environment_id']:e for e in report['environments']};seen=set();seen_records=set()
        for env in entry.get('environments',[]):
            ident=env['environment_id']
            if ident in seen or ident not in expected or env['formal_prefix']!=expected[ident]['formal_prefix']:
                raise ValueError('Finalized module manifest references an absent/duplicate environment')
            seen.add(ident)
            records={r['record_id']:r for r in report['verified_records']if r['evidence']['environment_id']==ident}
            found=set()
            for row in env['records']:
                rid=row['record_id']
                if rid in found or rid not in records:raise ValueError('Finalized module manifest changed record scope')
                found.add(rid);seen_records.add(rid);e=records[rid]['evidence']
                for key,other in (('module','module'),('path','generated_source_path'),('source_sha256','generated_source_sha256')):
                    if row[key]!=e[other]:raise ValueError('Stale finalized numerical proof pointer '+rid+' '+key)
                if 'complete_validation_member'in row and row['complete_validation_member']!=e['complete_validation_member']:
                    raise ValueError('Stale finalized independent validation pointer '+rid)
            if found!=set(records):raise ValueError('Finalized module manifest omits a current proof record')
        if seen!=set(expected)or seen_records!={r['record_id']for r in report['verified_records']}:
            raise ValueError('Finalized module manifest omits an environment/record')
    if modules.get('cohort')!='ci-evidence/published-402'or modules.get('summary_sha256')!=checked['summary_sha256']:
        raise ValueError('Finalized rational module manifest SHA changed')
    environments(modules,rational)
    extras={}
    for row in modules.get('additional_cohorts',[]):
        name=row.get('cohort')
        if name in extras:raise ValueError('Duplicate finalized additional module cohort')
        extras[name]=row
    if set(extras)!={'ci-evidence/'+name for name in names-{'published-402'}}:
        raise ValueError('Finalized additional module cohort scope changed')
    for name in names-{'published-402'}:
        report,validation=current[name];row=extras['ci-evidence/'+name]
        if row.get('summary_sha256')!=validation['summary_sha256']:
            raise ValueError('Stale finalized additional module cohort SHA '+name)
        environments(row,report)


def under(root, value):
    root = Path(root).resolve()
    result = root.joinpath(*safe_name(value).split('/'))
    if not result.resolve().is_relative_to(root):
        raise ValueError('Evidence path escapes destination '+value)
    return result


def checked_file(root, value, expected=None):
    path = under(root, value)
    if not path.is_file() or path.is_symlink():
        raise ValueError('Missing regular evidence file '+str(path))
    if expected is not None and sha(path) != sha_value(expected):
        raise ValueError('Evidence file SHA-256 mismatch '+str(path))
    return path


class SourceBundle:
    """Strict manifest-backed ZIP view. All bytes are checked before extraction."""
    def __init__(self, directory, max_bytes=MAX_BYTES,
                 manifest_filename='proof-sources-and-logs-manifest.json',
                 archive_filename=None, expected_schema='lean-catalogue-source-log-bundle-v1',
                 internal_manifest=None):
        self.directory = Path(directory).resolve()
        self.manifest_path = checked_file(self.directory, manifest_filename)
        self.manifest = read(self.manifest_path)
        if expected_schema is not None and self.manifest.get('schema') != expected_schema:
            raise ValueError('Unsupported source/log manifest schema')
        self.archive_path = checked_file(self.directory, archive_filename or self.manifest['archive'],
                                         self.manifest['archive_sha256'])
        self.files = {}
        folded = set()
        total = 0
        for row in self.manifest['files']:
            name = safe_name(row['path'])
            if name.casefold() in folded:
                raise ValueError('Duplicate/case-colliding source/log member '+name)
            folded.add(name.casefold())
            if type(row['bytes']) is not int or row['bytes'] < 0:
                raise ValueError('Invalid evidence byte count '+name)
            sha_value(row['sha256'])
            total += row['bytes']
            self.files[name] = row
        if total > max_bytes:
            raise ValueError('Evidence exceeds the configured uncompressed byte limit')
        self.archive = zipfile.ZipFile(self.archive_path)
        try:
            actual = {}
            for info in self.archive.infolist():
                name = safe_name(info.filename)
                if info.is_dir() or name in actual or info.flag_bits & 1:
                    raise ValueError('Duplicate/directory/encrypted source/log member '+name)
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                    raise ValueError('Non-regular source/log member '+name)
                actual[name] = info
            metadata = set()
            if internal_manifest is not None:
                internal_manifest = safe_name(internal_manifest)
                if internal_manifest in self.files or internal_manifest not in actual or actual[internal_manifest].file_size > 16*1024**2:
                    raise ValueError('Missing/oversized/conflicting embedded witness manifest')
                embedded = json.loads(self.archive.read(internal_manifest).decode('utf8'))
                if embedded.get('files') != self.manifest['files'] or embedded.get('freeze_git_sha') != self.manifest.get('freeze_git_sha'):
                    raise ValueError('Embedded and external frozen witness manifests differ')
                metadata.add(internal_manifest)
            if set(actual) != set(self.files) | metadata:
                raise ValueError('Archive and exact source/log manifest member sets differ')
            for name, row in self.files.items():
                if actual[name].file_size != row['bytes']:
                    raise ValueError('Archive byte count mismatch '+name)
                h = hashlib.sha256()
                with self.archive.open(actual[name]) as stream:
                    for block in iter(lambda: stream.read(1024*1024), b''):
                        h.update(block)
                if h.hexdigest() != row['sha256']:
                    raise ValueError('Archived evidence SHA-256 mismatch '+name)
        except BaseException:
            self.archive.close()
            raise

    def close(self):
        self.archive.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def member(self, value, expected=None):
        name = safe_name(value)
        if name not in self.files:
            raise ValueError('Missing archived evidence '+name)
        if expected is not None and self.files[name]['sha256'] != sha_value(expected):
            raise ValueError('Archived reference SHA-256 mismatch '+name)
        return name

    def text(self, value, expected=None):
        return self.archive.read(self.member(value, expected)).decode('utf8')

    def json(self, value, expected=None):
        return json.loads(self.text(value, expected))

    def extract(self, destination, environment=None):
        destination = Path(destination).resolve()
        if environment is not None:
            safe_name(environment)
            if '/' in environment:
                raise ValueError('Expected a single environment identifier')
        prefix = None if environment is None else 'environments/'+environment+'/'
        selected = [name for name in self.files if prefix is None or name.startswith(prefix)]
        if environment is not None and not selected:
            raise ValueError('Unknown archived environment '+environment)
        # Preflight every target before writing any member. Reject junctions and
        # symlinks even when their resolved destination happens to be in bounds.
        for name in selected:
            target = under(destination, name)
            current = target
            while current != destination.parent:
                if current.is_symlink() or (getattr(current, 'is_junction', lambda: False)()):
                    raise ValueError('Link/junction in extraction destination '+str(current))
                if current == destination:
                    break
                current = current.parent
            if target.exists() and (not target.is_file() or sha(target) != self.files[name]['sha256']):
                raise ValueError('Refusing to overwrite differing evidence '+str(target))
        for name in selected:
            target = under(destination, name)
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(prefix='.evidence-', dir=target.parent, delete=False) as output:
                temporary = Path(output.name)
                try:
                    with self.archive.open(name) as source:
                        for block in iter(lambda: source.read(1024*1024), b''):
                            output.write(block)
                    output.flush()
                    os.fsync(output.fileno())
                except BaseException:
                    output.close()
                    temporary.unlink(missing_ok=True)
                    raise
            try:
                if sha(temporary) != self.files[name]['sha256']:
                    raise ValueError('Extracted evidence SHA-256 mismatch '+name)
                if target.exists():
                    if not target.is_file() or sha(target) != self.files[name]['sha256']:
                        raise ValueError('Extraction target changed concurrently '+str(target))
                else:
                    os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        return selected


def axiom_audit(text):
    found = {name: sorted(a.strip() for a in axioms.split(',') if a.strip())
             for name, axioms in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", text, re.S)}
    found.update({name: [] for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", text)})
    if {a for values in found.values() for a in values} - ALLOWED_AXIOMS:
        raise ValueError('Nonstandard axiom in archived build log')
    return found


def check_stage(bundle, prefix, row):
    if row.get('passed') is not True or row.get('exit_code') != 0:
        raise ValueError('Unsuccessful archived proof stage '+str(row.get('path')))
    bundle.member(prefix+'/'+safe_name(row['path']), row['source_sha256'])
    log = bundle.text(prefix+'/'+safe_name(row['log']), row['log_sha256'])
    parsed = axiom_audit(log)
    if row.get('audited_theorems') != parsed:
        raise ValueError('Archived stage/log axiom audits differ '+row['path'])
    if row.get('unexpected_axioms') or row.get('errors') or row.get('changed_imported_dependencies'):
        raise ValueError('Archived proof stage reports a failed invariant')
    for dep in row.get('imported_dependencies', []):
        bundle.member(prefix+'/'+safe_name(dep['path']), dep['source_sha256'])
    return parsed


def verify_portable_cohort(directory, expected_count=None, expected_ids=None, require_complete=False):
    directory = Path(directory).resolve()
    report = read(checked_file(directory, 'verified-catalogue.json'))
    if report.get('schema') != 'portable-source-bound-lean-catalogue-v1' or report.get('frozen_catalogue_commit') != FREEZE:
        raise ValueError('Unsupported portable cohort schema or frozen catalogue')
    if directory.name in COHORTS:
        cohort_id, count = COHORTS[directory.name]
        if report.get('cohort_id') != cohort_id or report.get('expected_record_count') != count:
            raise ValueError('Portable cohort identity/count mismatch')
        expected_count = count if expected_count is None else expected_count
    ids = [r['record_id'] for r in report['verified_records']]
    if len(ids) != len(set(ids)) or report['verified_totals']['records'] != len(ids):
        raise ValueError('Duplicate or inconsistent verified record counts')
    for key, value in [('pieces', sum(r['n'] for r in report['verified_records'])),
                       ('unordered_pairs', sum(r['n']*(r['n']-1)//2 for r in report['verified_records']))]:
        if key in report['verified_totals'] and report['verified_totals'][key] != value:
            raise ValueError('Portable cohort total does not match its actual records: '+key)
    if expected_count is not None and len(ids) > expected_count:
        raise ValueError('Portable cohort contains too many records')
    if expected_ids is not None and set(ids) - set(expected_ids):
        raise ValueError('Portable cohort contains a non-target frozen record')
    if require_complete and (len(ids) != expected_count or (expected_ids is not None and set(ids) != set(expected_ids)) or report.get('missing_record_ids')):
        raise ValueError('Complete exact frozen target cohort is a publication gate')
    raw_name = report.get('raw_artifact_index', 'raw-artifacts.json')
    raw_index = under(directory, raw_name)
    if require_complete and directory.name in COHORTS and not raw_index.is_file():
        raise ValueError('Completed publication cohort lacks its preserved raw artifact index')
    if raw_index.exists() or report.get('raw_artifact_index_sha256'):
        raw_index = checked_file(directory, raw_name, report.get('raw_artifact_index_sha256'))
        raw_digest = report.get('raw_artifact_index_sha256') or sha(raw_index)
        raw_artifacts = raw_artifact_rows(read(raw_index))
    else:
        raw_digest = None
        raw_artifacts = {}
    with SourceBundle(directory) as bundle:
        if (report['proof_source_bundle'] != bundle.archive_path.name or
                report['proof_source_manifest'] != bundle.manifest_path.name or
                report['proof_source_bundle_sha256'] != sha(bundle.archive_path) or
                report['proof_source_manifest_sha256'] != sha(bundle.manifest_path)):
            raise ValueError('Portable summary does not bind the exact archive/manifest')
        for source in report.get('source_cohorts', []):
            if source.get('archive_member'):
                bundle.member(source['archive_member'], source['sha256'])
        environments = {}
        independent = {}
        checked_stages = set()
        checked_sources = set()
        for row in report['environments']:
            ident = safe_name(row['environment_id'])
            prefix = 'environments/'+ident+'/formal'
            if '/' in ident or ident in environments or row['formal_prefix'] != prefix:
                raise ValueError('Duplicate/unsafe environment formal root')
            check_environment_storage(row, raw_artifacts)
            environments[ident] = prefix
            core = bundle.json(prefix+'/core-verification.json')
            if core.get('status') != 'passed':
                raise ValueError('Environment lacks a successful independent core receipt')
            for stage in core['results']:
                check_stage(bundle, prefix, stage)
                checked_stages.add((ident, stage['path']))
                checked_sources.add((ident, stage['path']))
            independent[ident] = bundle.json('environments/'+ident+'/independent-validation.json')
            validation = independent[ident]
            if validation.get('freeze_git_sha', validation.get('frozen_catalogue_commit')) != FREEZE:
                raise ValueError('Independent validation freeze mismatch')
            check_approved_publication_version(row,prefix,bundle,validation)
            for receipt in validation.get('receipt_inputs', []):
                bundle.member(prefix+'/'+safe_name(receipt['path']), receipt['sha256'])
        for record in report['verified_records']:
            e = record['evidence'];ident = e['environment_id']
            if ident not in environments:
                raise ValueError('Record references an absent environment')
            prefix = environments[ident]
            member = 'environments/'+ident+'/independent-validation.json'
            if e['complete_validation_member'] != member:
                raise ValueError('Record references a different validation environment')
            fulls = [r for r in independent[ident]['verified_records'] if r['record_id'] == record['record_id']]
            if len(fulls) != 1:
                raise ValueError('Record missing/duplicated in its complete independent validation')
            full = fulls[0]
            for key in ('record_id', 'n', 'dimension', 'source_path', 'source_sha256',
                        'source_json_sha256', 'problem_family', 'catalogue_key'):
                if key in record and full.get(key) != record[key]:
                    raise ValueError('Compact/complete record identity mismatch '+key)
            fe = full['evidence']
            core_pins = fe.get('core_dependencies', {})
            if report.get('cohort_id') == 'rational-402':
                if (core_pins.get('status') != 'recorded_hashes_match_current_files' or
                        not core_pins.get('source_hashes') or not core_pins.get('olean_hashes')):
                    raise ValueError('Portable rational proof lacks full recorded core source/object pins')
            for source, expected_hash in (core_pins.get('source_hashes') or {}).items():
                bundle.member(prefix+'/'+safe_name(source), expected_hash)
            for expected_hash in (core_pins.get('olean_hashes') or {}).values():
                sha_value(expected_hash)
            check_compact_evidence(e, fe)
            for key, hkey in (('generated_source_path','generated_source_sha256'),('log_path','log_sha256'),
                              ('receipt_path','receipt_sha256'),('plan_manifest_path','plan_manifest_sha256')):
                if fe.get(key):
                    bundle.member(prefix+'/'+safe_name(fe[key]), fe[hkey])
            parsed = axiom_audit(bundle.text(prefix+'/'+fe['log_path']))
            if any(parsed.get(name) != values for name, values in fe['audited_theorems'].items()):
                raise ValueError('Final semantic declaration missing from its actual log')
            if not fe['audited_theorems']:
                raise ValueError('No audited semantic declaration in verified record')
            checked_sources.add((ident, fe['generated_source_path']))
            for key in ('dependencies', 'steps', 'extension_dependencies'):
                for stage in fe.get(key, []):
                    if 'source_sha256' in stage and 'log_sha256' in stage:
                        check_stage(bundle, prefix, stage)
                        checked_stages.add((ident, stage['path']))
                    else:
                        if stage.get('path'):
                            bundle.member(prefix+'/'+safe_name(stage['path']), stage.get('source_sha256', stage.get('generated_source_sha256')))
                        if stage.get('log'):
                            bundle.member(prefix+'/'+safe_name(stage['log']), stage.get('log_sha256'))
                    if stage.get('path'):
                        checked_sources.add((ident, stage['path']))
            receipt = bundle.json(prefix+'/'+fe['receipt_path'], fe['receipt_sha256'])
            # Algebraic receipts explicitly enumerate every recursively imported
            # source/object pair; only source bytes belong in this archive.
            for stage in receipt.get('stages', []):
                check_stage(bundle, prefix, stage)
                checked_stages.add((ident, stage['path']))
                checked_sources.add((ident, stage['path']))
        if raw_digest is not None:
            checked_file(directory, raw_name, raw_digest)
        result = dict(cohort_id=report.get('cohort_id'), records=len(ids), environments=len(environments),
                      archive_members=len(bundle.files), checked_sources=len(checked_sources),
                      checked_stages=len(checked_stages), archive_sha256=sha(bundle.archive_path),
                      manifest_sha256=sha(bundle.manifest_path), summary_sha256=sha(directory/'verified-catalogue.json'))
    return report, result


def require_rational_402(report, witness_manifest):
    expected = {Path(r['path']).stem for r in witness_manifest['files']}
    ids = [r['record_id'] for r in report['verified_records']]
    if (len(expected) != 402 or len(ids) != len(set(ids)) or len(ids) != 402 or set(ids) != expected or
            report['verified_totals']['records'] != 402 or report['verified_totals']['pieces'] != 10796 or
            report['verified_totals']['unordered_pairs'] != 235462 or report.get('missing_record_ids') or
            report.get('complete_402') is not True):
        raise ValueError('The exact complete 402-record rational cohort and fixed totals are required')
    return expected


def pilot_target_ids(formal, cohort_name):
    filename = {'published-85':'generated3d-registry.json',
                'published-45':'generated-nd-pilots-registry.json'}[cohort_name]
    directory = Path(formal)/'catalogue/algebraic'
    if (directory/filename).is_file():
        registry = read(directory/filename)
    else:
        with SourceBundle(directory, manifest_filename='pilot-inputs-and-proposals-manifest.json',
                          expected_schema='bounded-algebraic-pilot-inputs-v1') as bundle:
            registry = bundle.json('catalogue/algebraic/'+filename)
    ids = [r['record_id'] for r in registry['records']]
    expected = COHORTS[cohort_name][1]
    if len(ids) != len(set(ids)) or len(ids) != expected:
        raise ValueError('Pilot registry does not contain the exact expected target count')
    return set(ids)


def require_family_union(rational_rows, additional_rows):
    rational = {(r['dimension'],r['piece'],r['container']) for r in rational_rows}
    additional = {(r['dimension'],r['piece'],r['container']) for r in additional_rows}
    if len(rational) != 10 or len(additional) != 130 or rational & additional or len(rational | additional) != 140:
        raise ValueError('Strict rational/additional cohorts must cover140 distinct disjoint problem families')
    return 140


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--cohort', type=Path)
    choice.add_argument('--input-manifest', type=Path, help='Verify/unpack a manifest-backed shared input ZIP')
    parser.add_argument('--input-archive', help='Archive filename, required when absent from the input manifest')
    parser.add_argument('--embedded-manifest', help='Named embedded witness manifest, checked against its external counterpart')
    parser.add_argument('--extract', type=Path, help='Extract under this root, preserving environments/<id>/formal')
    parser.add_argument('--environment', help='Extract only this environment identifier')
    args = parser.parse_args()
    if args.input_manifest:
        if args.environment:parser.error('--environment applies only to a proof cohort')
        with SourceBundle(args.input_manifest.parent, manifest_filename=args.input_manifest.name,
                          archive_filename=args.input_archive, expected_schema=None,
                          internal_manifest=args.embedded_manifest) as bundle:
            result = dict(status='passed', archive_members=len(bundle.files), archive_sha256=sha(bundle.archive_path))
            if args.extract:result['extracted_files'] = len(bundle.extract(args.extract))
        print(json.dumps(result, indent=2));return
    report, result = verify_portable_cohort(args.cohort)
    if args.extract:
        with SourceBundle(args.cohort) as bundle:
            files = bundle.extract(args.extract, args.environment)
        result['extracted_files'] = len(files)
        result['formal_roots'] = [str(args.extract.resolve()/r['formal_prefix']) for r in report['environments']
                                  if args.environment is None or r['environment_id'] == args.environment]
    elif args.environment:
        parser.error('--environment requires --extract')
    print(json.dumps(dict(status='passed', **result), indent=2))


if __name__ == '__main__':
    main()
