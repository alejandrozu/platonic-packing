#!/usr/bin/env python3
"""Ingest GitHub Lean evidence into isolated Linux-object validation roots.

No Lean process is launched. No object or source in --base-formal is changed.
Only the trusted local summarize_verified.py is executed; artifact Python is
retained as evidence and never imported. A full claim requires all 402 exact
IDs, independently validated, with no cross-shard duplicates.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import zipfile
import evidence_store
from compact_cohort import compact_rows

FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'
LEAN = '4.31.0'
MATHLIB = 'fabf563a7c95a166b8d7b6efca11c8b4dc9d911f'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
ARTIFACT_PATTERN = r'lean-(catalogue|support225)-shard-(\d+)'
_MIN_FREE_BYTES = 0
_BOUNDED_WRITES = False


def sha(path):
    h = hashlib.sha256()
    with evidence_store.EvidencePath(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


class ReplayDigests:
    """Memoize immutable audit bytes, then rehash every unique file afresh.

    A hit still checks device, inode, byte size and both nanosecond timestamps.
    This is local to one read-only replay, never a persisted digest cache.
    """
    def __init__(self):
        self.entries = {}
        self.hits = 0
        self.finalized = False

    @staticmethod
    def identity(path):
        value = path.stat()
        if not stat.S_ISREG(value.st_mode):
            raise ValueError('Digest target is not a regular file: ' + str(path))
        return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)

    def digest(self, value):
        if self.finalized:
            raise ValueError('Digest replay cache used after final verification')
        path = evidence_store.EvidencePath(value).resolve(); before = self.identity(path)
        if path in self.entries:
            identity, result = self.entries[path]
            if identity != before:
                raise ValueError('File identity changed during digest replay: ' + str(path))
            self.hits += 1
            return result
        result = sha(path)
        if self.identity(path) != before:
            raise ValueError('File changed while computing its digest: ' + str(path))
        self.entries[path] = (before, result)
        return result

    def verify(self):
        for path, (identity, expected) in self.entries.items():
            if self.identity(path) != identity:
                raise ValueError('File identity changed before final digest pass: ' + str(path))
            actual = sha(path)  # Deliberately bypass the memoized digest.
            if actual != expected or self.identity(path) != identity:
                raise ValueError('File bytes changed before final digest pass: ' + str(path))
        self.finalized = True

    def report(self):
        return dict(unique_files=len(self.entries), memoized_references=self.hits,
            fresh_final_hashes=len(self.entries) if self.finalized else 0,
            identity_checked_on_every_reference=True, final_pass_completed=self.finalized)


@contextmanager
def digest_memoization(targets):
    """Patch approved digest readers for one replay; restore them on failure."""
    audit = ReplayDigests(); originals = []; seen = set()
    for module, field in targets:
        key = (id(module), field)
        if key in seen:
            continue
        seen.add(key); originals.append((module, field, getattr(module, field)))
        setattr(module, field, audit.digest)
    try:
        yield audit
        audit.verify()
    finally:
        for module, field, original in reversed(originals):
            setattr(module, field, original)


def metadata_bytes(path, data, exclusive=False):
    evidence_store.reject_reparse_ancestors(path)
    ancestor=path.parent
    while not ancestor.exists():ancestor=ancestor.parent
    reserve=(min(len(data),1024**2)if _BOUNDED_WRITES else len(data))+evidence_store.METADATA_RESERVE
    if shutil.disk_usage(ancestor).free<_MIN_FREE_BYTES+reserve:
        raise ValueError('Metadata write would cross the required free-space floor')
    path.parent.mkdir(parents=True,exist_ok=True)
    evidence_store.reject_reparse_ancestors(path)
    with path.open('xb'if exclusive else'wb')as stream:
        for offset in range(0,len(data),1024**2):
            block=data[offset:offset+1024**2]
            if shutil.disk_usage(path.parent).free<_MIN_FREE_BYTES+len(block)+evidence_store.METADATA_RESERVE:
                raise ValueError('Metadata block would cross the required free-space floor')
            stream.write(block);stream.flush()
            if shutil.disk_usage(path.parent).free<_MIN_FREE_BYTES:
                raise ValueError('Free-space floor crossed during metadata write; acceptance stopped')


def write(path, value):
    payload=json.dumps(value,indent=2)+'\n'
    encoded=payload.replace('\n','\r\n').encode('utf8')if os.name=='nt'else payload.encode('utf8')
    previous=path.read_bytes()if path.name.startswith('cohort-validation')and path.is_file()else None
    if previous is not None:
        history=path.parent/'report-history'/(path.stem+'-'+hashlib.sha256(previous).hexdigest()+'.json')
        if not history.exists():metadata_bytes(history,previous,exclusive=True)
        elif history.read_bytes()!=previous:raise ValueError('Preserved report history changed')
    temporary=path.with_suffix(path.suffix+'.tmp')
    metadata_bytes(temporary,encoded)
    temporary.replace(path)


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def safe_name(value):
    if '\\' in value or '\x00' in value:
        raise ValueError('Unsafe ZIP/manifest path '+repr(value))
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(p in {'.', '..'} or ':' in p for p in path.parts):
        raise ValueError('Unsafe ZIP/manifest path '+repr(value))
    return path.as_posix()


def under(root, value):
    return root.joinpath(*PurePosixPath(safe_name(value)).parts)


def link(source, target):
    """Never write through an existing hardlink into the frozen base."""
    if target.exists():
        if not target.is_file() or sha(source) != sha(target):
            raise ValueError('Conflicting immutable validation file '+str(target))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def base_inputs(base, root):
    for relative in ['catalogue/inputs', 'catalogue/inventory', 'catalogue/witnesses', 'catalogue/witnesses_nd']:
        source = base/relative
        if not source.is_dir():
            raise ValueError('Missing complete frozen base directory '+str(source))
        for path in source.rglob('*'):
            if path.is_file():
                link(path, root/path.relative_to(base))
    manifest = base/'catalogue/rational-witnesses-manifest.json'
    link(manifest, root/manifest.relative_to(base))


def load_validator(base, root):
    source = base/'catalogue/summarize_verified.py'
    spec = importlib.util.spec_from_file_location('trusted_summary_'+str(id(root)), source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = evidence_store.EvidencePath(root)
    module.extension_audit.Path = evidence_store.EvidencePath
    module.FORMAL = root
    module.HERE = root/'catalogue'
    module.INPUTS = module.HERE/'inputs'
    return module


def _replay_using(summary, base, root, receipts):
    eligible = summary.inventory()
    by_id = {r['record_id']: r for r in eligible}
    by_path = {r['source_path']: r for r in eligible}
    selected, ignored, inputs, duplicates = {}, [], [], []
    for path in receipts:
        receipt = read(path)
        inputs.append(dict(path=path.relative_to(root).as_posix(), sha256=sha(path)))
        # CI receipts must attest both source and object dependencies, even for
        # ordinary one-module records; the historical local exception is not used.
        summary.verify_core_maps(receipt, required=True)
        for row in receipt.get('results', []):
            valid, failure = summary.inspect(row, path, receipt, by_id, by_path)
            if failure:
                ignored.append(failure)
            else:
                record, evidence, rank = valid
                rid = record['record_id']
                if rid in selected:
                    duplicates.append(rid)
                    if rank <= selected[rid][2]:
                        continue
                selected[rid] = valid
    verified = [dict(r, evidence=selected[r['record_id']][1]) for r in eligible if r['record_id'] in selected]
    result = dict(freeze_git_sha=FREEZE, verified_records=verified,
        eligible_records=eligible, verified_totals=summary.totals(verified),
        eligible_totals=summary.totals(eligible), ignored_rows=ignored,
        superseded_record_ids=duplicates, receipt_inputs=inputs,
        validator_source_sha256=sha(base/'catalogue/summarize_verified.py'))
    return result


def replay(base, root, receipts, output):
    summary = load_validator(base, root)
    targets = [(summary, 'sha'), (summary.extension_audit.core, 'digest')]
    with digest_memoization(targets) as audit:
        result = _replay_using(summary, base, root, receipts)
    # No acceptance output is written until the fresh final pass has succeeded.
    result['digest_audit'] = audit.report()
    write(output, result)
    return result


def zip_entries(z, maximum):
    entries, folded, total = {}, set(), 0
    for info in z.infolist():
        name = safe_name(info.filename.rstrip('/'))
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError('ZIP symlink is forbidden: '+name)
        if info.is_dir():
            continue
        if name in entries or name.casefold() in folded:
            raise ValueError('Duplicate/case-colliding ZIP entry '+name)
        entries[name] = info
        folded.add(name.casefold())
        total += info.file_size
    if total > maximum:
        raise ValueError('ZIP exceeds configured uncompressed-byte limit')
    return entries


def extract_evidence(archive, root, maximum):
    with zipfile.ZipFile(archive) as z:
        entries = zip_entries(z, maximum)
        inventories = [n for n in entries if n.endswith('/evidence-inventory.json')]
        if len(inventories) != 1:
            raise ValueError('Expected exactly one nested evidence inventory')
        inventory_name = inventories[0]
        inventory_data = z.read(inventory_name)
        inventory = json.loads(inventory_data.decode('utf8'))
        expected, folded = {}, set()
        for row in inventory['files']:
            relative = safe_name(row['path'])
            name = 'formal/'+relative
            if name in expected or name.casefold() in folded:
                raise ValueError('Duplicate evidence-inventory path '+relative)
            if not re.fullmatch('[0-9a-f]{64}', row['sha256']) or not isinstance(row['bytes'], int) or row['bytes'] < 0:
                raise ValueError('Invalid inventory digest/size')
            expected[name] = row
            folded.add(name.casefold())
        if set(entries) != set(expected)|{inventory_name}:
            raise ValueError('Nested ZIP contains missing or unlisted files')
        for name, row in expected.items():
            if not name.startswith('formal/') or entries[name].file_size != row['bytes']:
                raise ValueError('Evidence size/prefix mismatch '+name)
            target = under(root, row['path'])
            # Existing paths are frozen-base hardlinks or previous identical
            # extraction files. Never open them for writing.
            existing = target.is_file()
            if target.exists() and not existing:
                raise ValueError('Non-file target collision '+str(target))
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            output = None if existing else target.open('xb')
            try:
                with z.open(entries[name]) as stream:
                    for block in iter(lambda: stream.read(1024*1024), b''):
                        digest.update(block)
                        if output is not None:
                            output.write(block)
            finally:
                if output is not None:
                    output.close()
            if digest.hexdigest() != row['sha256'] or sha(target) != row['sha256']:
                raise ValueError('Evidence SHA256 mismatch '+name)
        inventory_relative = inventory_name.removeprefix('formal/')
        if inventory_relative == inventory_name:
            raise ValueError('Inventory lies outside formal/')
        target = under(root, inventory_relative)
        if target.exists():
            if target.read_bytes() != inventory_data:
                raise ValueError('Changed inventory at existing validation root')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(inventory_data)
    return inventory, inventory_relative


def verify_core(base, root):
    receipt = read(root/'core-verification.json')
    if receipt.get('status') != 'passed' or receipt.get('not_run') or receipt.get('expected_lean_version') != LEAN or receipt.get('expected_mathlib_revision') != MATHLIB:
        raise ValueError('Core build incomplete or wrong pinned dependencies')
    if receipt.get('builder_sha256') != sha(root/'verify_core.py'):
        raise ValueError('Core builder digest mismatch')
    audited, negatives, checked = {}, set(), []
    for row in receipt['results']:
        if not row.get('passed') or row.get('exit_code') != 0 or row.get('errors') or row.get('unexpected_axioms'):
            raise ValueError('Core row is not a successful build')
        for field, digest in [('path','source_sha256'), ('olean_path','olean_sha256'), ('log','log_sha256')]:
            path = under(root, row[field])
            if not path.is_file() or sha(path) != row[digest]:
                raise ValueError('Core artifact hash mismatch '+row[field])
        source = under(root, row['path'])
        approved = under(base, row['path'])
        if not approved.is_file() or sha(source) != sha(approved):
            raise ValueError('CI core source differs from approved frozen base '+row['path'])
        log = under(root, row['log']).read_text(encoding='utf8')
        parsed = load_validator(base, root).parse_axioms(log)
        used = {a for values in parsed.values() for a in values}
        if used-ALLOWED or 'sorryAx' in log or used != set(row.get('axioms', [])) or parsed != row.get('audited_theorems', {}):
            raise ValueError('Core axiom audit mismatch '+row['path'])
        expected = re.findall(r'^\s*#print\s+axioms\s+([\w.]+)', source.read_text(encoding='utf8'), re.M)
        if any(not any(full == name or full.endswith('.'+name) for full in parsed) for name in expected):
            raise ValueError('Core source audit directive was not printed')
        audited.update(parsed)
        for negative in row.get('negative_checks', []):
            if negative.get('expected') is not False or negative.get('kernel_checked') is not True:
                raise ValueError('Negative regression was not kernel checked')
            negatives.add((row['path'], negative['checker'], tuple(negative['arguments']), negative['case']))
        checked.append(row['path'])
    if len(checked) < 18 or len(negatives) < 16 or len(audited) < 51:
        raise ValueError('Expected full core and negative-regression coverage')
    return dict(receipt_sha256=sha(root/'core-verification.json'),
        stages=len(checked), negative_assertions=len(negatives), audited_declarations=len(audited))


def supplement_missing_probes(base,root,provenance_path=None):
    """Repair only four omitted audit files, using exact older receipt SHAs."""
    saved=root.parent/'core-supplement-provenance.json'
    probe_paths=['CubeAuditProbe.lean','CubeAuditProbe.olean','CayleyAuditProbe.lean','CayleyAuditProbe.olean']
    if not saved.is_file()and all((root/name).is_file()for name in probe_paths):
        return None
    if provenance_path is None and saved.is_file():
        provenance_path=Path(read(saved)['source_provenance_path'])
    if provenance_path is None:return None
    provenance_path=Path(provenance_path).resolve();provenance=read(provenance_path)
    if provenance.get('schema')!='verified-linux-core-supplement-v1':
        raise ValueError('Unrecognized complete-core supplement provenance')
    for path_key,hash_key in [('github_archive','github_archive_sha256'),('evidence_zip','evidence_zip_sha256'),('inventory_path','inventory_sha256')]:
        if sha(Path(provenance[path_key]))!=provenance[hash_key]:raise ValueError('Supplement archive/inventory changed')
    supplement=Path(provenance['formal_root']).resolve()
    supplied=read(supplement/'core-verification.json')
    if 'linux'not in supplied['preflight']['lean_version_output'].lower()or sha(supplement/'core-verification.json')!=provenance['core_receipt_sha256']:
        raise ValueError('Supplement is not the recorded Linux core')
    verify_core(base,supplement)
    older=read(root/'core-verification.json');rows={r['path']:r for r in older['results']}
    supplied_rows={r['path']:r for r in supplied['results']};repairs=[]
    for name in ['CubeAuditProbe.lean','CayleyAuditProbe.lean']:
        row,donor=rows[name],supplied_rows[name]
        for field,hash_key in [('path','source_sha256'),('olean_path','olean_sha256')]:
            if row[field]!=donor[field]or row[hash_key]!=donor[hash_key]:
                raise ValueError('New Linux probe does not exactly match the older build receipt: '+row[field])
            source,target=under(supplement,donor[field]),under(root,row[field])
            if sha(source)!=row[hash_key]:raise ValueError('Supplied Linux probe bytes changed')
            existed=target.is_file()
            streamed,_=evidence_store.active_store(target)
            if streamed and target.suffix=='.olean':
                streamed.add_supplement_object(provenance['github_archive'],provenance['github_archive_sha256'],row[field],row[hash_key])
            else:
                link(source,target)
            repairs.append(dict(path=row[field],sha256=row[hash_key],was_missing=not existed,
                donor_path=str(source),older_recorded_sha256=row[hash_key]))
    result=dict(schema='exact-sha-core-probe-repair-v1',source_provenance_path=str(provenance_path),
        source_provenance_sha256=sha(provenance_path),source_run_id=provenance['run_id'],source_head_sha=provenance['head_sha'],
        source_artifact_id=provenance['artifact_id'],files=repairs,
        raw_original_archive_changed=False,boundary='Only omitted non-imported audit-probe source/object files; exact older receipt SHA equality required.')
    # Keep the original missing-file history on repeated independent replays.
    if saved.is_file():
        prior=read(saved)
        if prior['source_provenance_sha256']!=result['source_provenance_sha256']or[(x['path'],x['sha256'])for x in prior['files']]!=[(x['path'],x['sha256'])for x in repairs]:
            raise ValueError('A different supplement was already recorded for this isolated root')
        return prior
    write(saved,result);return result


def expected_shards(eligible, count, base=None, support_block_size=None):
    shards = [dict(index=i, cost=0, records=[]) for i in range(count)]
    records = []
    for r in eligible:
        n,d,k = r['n'],r['dimension'],r['template_vertices']
        cost=n*n*d*d*max(k,8)+n*k*d*(d+2)*8
        if support_block_size is not None:
            folder='witnesses'if d==3 else'witnesses_nd'
            witness=read(base/'catalogue'/folder/(r['record_id']+'.json'))
            if d==3 or witness['container']=='c24':
                ordinary=d==3 and n<=12 or d>3 and n<=4 and not(d==6 and k==64 and n>=3)
                modules=1 if ordinary else 2+(n+4)//5 if d==3 else n+2 if k<24 else 2+n*(2+(k+7)//8)
                cost+=modules*30000
            else:
                signatures={json.dumps(x,separators=(',',':'))for x in zip(witness['raw_skews'],witness['diagonal_signs'],witness['cayley_inverses'],witness['rotations'])}
                modules=(n+support_block_size-1)//support_block_size+2
                cost=modules*30000+n*n*d*d*10+len(signatures)*d*d*d*100
        records.append(dict(record_id=r['record_id'], cost=cost))
    for r in sorted(records, key=lambda r:(-r['cost'],r['record_id'])):
        target = min(shards, key=lambda s:(s['cost'],s['index']))
        target['cost'] += r['cost']; target['records'].append(r['record_id'])
    return [set(s['records']) for s in shards]


def verify_extensions(base,root,status):
    info=status['generic_extension_receipt']
    source=under(root,info['path']);receipt=read(source)
    if sha(source)!=info['sha256']or status['generic_extension_receipt_path']!=info['path']or status['generic_extension_receipt_sha256']!=info['sha256']:
        raise ValueError('Generic extension receipt provenance changed')
    if receipt.get('schema')!='packing-extension-verification-v2'or receipt.get('passed')is not True or receipt.get('changed_core_dependencies'):
        raise ValueError('Generic extension receipt is incomplete or unstable')
    if receipt['verifier']['sha256']!=sha(base/'verify_extensions.py')or receipt['core_verifier_sha256']!=sha(base/'verify_core.py'):
        raise ValueError('Generic extension builder differs from approved implementation')
    summary=load_validator(base,root)
    audited={}
    required={'NDGeometry','NDSupport','NDModels','BoxSupport','CayleyGeometry','NDSupportRegression'}
    names=set()
    for row in receipt['results']:
        if not row.get('passed')or row.get('exit_code')!=0 or row.get('errors')or row.get('changed_imported_dependencies')or row.get('changed_imported_dependencies_at_receipt'):
            raise ValueError('Unsuccessful or unstable generic extension stage')
        names.add(Path(row['path']).stem)
        for field,digest in [('path','source_sha256'),('olean_path','olean_sha256'),('log','log_sha256')]:
            if sha(under(root,row[field]))!=row[digest]:raise ValueError('Generic extension source/object/log mismatch')
        if sha(under(root,row['path']))!=sha(under(base,row['path'])):
            raise ValueError('Generic extension source differs from approved local source')
        log=under(root,row['log']).read_text(encoding='utf8');parsed=summary.parse_axioms(log)
        if parsed!=row['audited_theorems']or {a for v in parsed.values()for a in v}-ALLOWED or 'sorryAx'in log:
            raise ValueError('Generic extension axiom audit mismatch')
        directives=re.findall(r'^\s*#print\s+axioms\s+([\w.]+)',under(root,row['path']).read_text(encoding='utf8'),re.M)
        if any(not any(full==name or full.endswith('.'+name)for full in parsed)for name in directives):
            raise ValueError('Generic extension audit directive omitted')
        actual=summary.extension_audit.dependency_snapshot(under(root,row['path']),root)
        if row['imported_dependencies']!=actual:raise ValueError('Generic transitive import closure changed')
        audited.update(parsed)
    if not required<=names:raise ValueError('Required support geometry/regression modules not built')
    for dep in receipt['core_dependencies']:
        if sha(under(root,dep['path']))!=dep['source_sha256']or sha(under(root,dep['path']))!=sha(under(base,dep['path'])):
            raise ValueError('Generic receipt direct-core source boundary changed')
        if dep.get('olean_sha256')is not None and sha(under(root,dep['olean']))!=dep['olean_sha256']:
            raise ValueError('Generic receipt direct-core object changed')
    return dict(path=info['path'],sha256=sha(source),stages=len(receipt['results']),audited_declarations=len(audited))


def validate_shard(base, root, artifact, run, inventory_relative, supplement=None):
    summary = load_validator(base, root)
    eligible = summary.inventory()
    match=re.fullmatch(ARTIFACT_PATTERN,artifact['name']);kind,shard=match.group(1),int(match.group(2))
    directory = root/'catalogue'/('ci-support'if kind=='support225'else'ci')/f'shard-{shard:02}'
    status = read(directory/'status.json')
    plan = read(directory/'shard-plan.json')
    count = status['shard_count']
    support=kind=='support225'
    if support and(status.get('schema_version')!=2 or status.get('cohort')!='support-first-all402'or status.get('total_cohort_records')!=402 or plan.get('schema_version')!=2):
        raise ValueError('Unexpected support cohort/schema/scope')
    block=status.get('block_size')if support else None
    if support and block not in {1,4,8}:raise ValueError('Unexpected support proof block size')
    expected = expected_shards(eligible,count,base,block)
    if status.get('shard_index') != shard or status.get('frozen_commit') != FREEZE or count != (12 if support else 24) or plan.get('frozen_commit') != FREEZE or plan.get('total_records') != 402:
        raise ValueError('Unexpected shard identity/freeze/size')
    actual_plan = [set(r['record_id'] for r in s['records']) for s in plan['shards']]
    if actual_plan != expected or len({r['record_id'] for r in status['records']}) != len(status['records']):
        raise ValueError('Shard plan differs from frozen deterministic partition')
    if status.get('total_selected') != len(expected[shard]) or any(r['record_id'] not in expected[shard] for r in status['records']):
        raise ValueError('Shard status includes out-of-partition records')
    receipts = []
    approved_passed = set()
    for record in status['records']:
        for attempt in record.get('attempts', []):
            path = under(root/'catalogue', attempt['receipt'])
            if path.is_file():
                if attempt.get('receipt_sha256') and sha(path) != attempt['receipt_sha256']:
                    raise ValueError('Status/receipt digest mismatch')
                receipts.append(path)
        if record.get('passed') and record.get('complete'):
            approved_passed.add(record['record_id'])
            path = under(root/'catalogue', record['accepted_receipt'])
            if not path.is_file():
                raise ValueError('Accepted receipt is missing')
    core = verify_core(base, root)
    generic=None
    if support:
        if str(status.get('github_run_id'))!=str(run['id'])or status.get('github_commit')!=run['head_sha']:
            raise ValueError('Worker status belongs to a different GitHub run/commit')
        worker=under(root,status['worker_path'])
        if sha(worker)!=status['worker_sha256']or sha(worker)!=sha(under(base,status['worker_path'])):
            raise ValueError('Worker source differs from approved source/provenance')
        if status.get('worker_source_unchanged')is False or status.get('generic_extension_receipt_unchanged')is False:
            raise ValueError('Worker or generic receipt changed during build')
        generic=verify_extensions(base,root,status)
    output = root.parent/'independent-validation.json'
    result = replay(base, root, receipts, output)
    verified = {r['record_id'] for r in result['verified_records']}
    if verified != approved_passed or not verified <= expected[shard]:
        raise ValueError('Independent verified IDs disagree with completed passed status')
    maps = []
    for path in receipts:
        r = read(path)
        maps.append((r.get('core_source_hashes'), r.get('core_olean_hashes')))
    if not maps or any(m != maps[0] for m in maps):
        raise ValueError('Shard receipts do not share one recorded core environment')
    extensions={}
    for record in result['verified_records']:
        for dependency in record['evidence'].get('extension_dependencies',[]):
            if dependency['path']in extensions and extensions[dependency['path']]!=dependency:
                raise ValueError('One shard reports conflicting extension dependency objects')
            extensions[dependency['path']]=dependency
    provenance = dict(run_id=run['id'], run_head_sha=run['head_sha'], artifact_id=artifact['id'],
        artifact_name=artifact['name'], artifact_created_at=artifact['created_at'], shard_index=shard,
        shard_complete=status.get('complete'), assigned_records=len(expected[shard]),
        verified_records=len(verified), unverified_records=sorted(expected[shard]-verified),
        validation_path=str(output), validation_sha256=sha(output), core_validation=core,
        validation_formal_root=str(root),
        evidence_inventory_path=inventory_relative, core_source_hashes=maps[0][0], core_olean_hashes=maps[0][1],
        extension_dependencies=[extensions[k]for k in sorted(extensions)],generic_extension_validation=generic,
        cohort=status.get('cohort','original-402'),shard_count=count,exact_sha_core_supplement=supplement)
    write(root.parent/'validation-provenance.json', provenance)
    return provenance, result, receipts


def gh_json(endpoint):
    p = subprocess.run(['gh','api',endpoint], check=True, capture_output=True, text=True, encoding='utf8')
    return json.loads(p.stdout)


def fetch(args, store):
    run = gh_json(f'repos/{args.repo}/actions/runs/{args.run_id}')
    if run['head_sha'] != args.commit:
        raise ValueError('GitHub run is for a different commit')
    pages, page = [], 1
    while True:
        response = gh_json(f'repos/{args.repo}/actions/runs/{args.run_id}/artifacts?per_page=100&page={page}')
        pages.extend(response['artifacts'])
        if len(response['artifacts']) < 100: break
        page += 1
    write(store/'run.json', run)
    write(store/'artifacts.json', pages)
    requested=set(args.download_artifact_ids or [])
    available={a['id']for a in pages if re.fullmatch(ARTIFACT_PATTERN,a['name'])}
    if requested-available:
        raise ValueError('Requested artifact IDs are absent from the approved run: '+str(sorted(requested-available)))
    for artifact in pages:
        if not re.fullmatch(ARTIFACT_PATTERN,artifact['name']):
            continue
        if artifact.get('workflow_run',{}).get('id') != args.run_id or artifact.get('workflow_run',{}).get('head_sha') != args.commit:
            raise ValueError('Artifact workflow provenance mismatch')
        directory = store/'artifacts'/str(artifact['id'])
        directory.mkdir(parents=True,exist_ok=True)
        write(directory/'github-artifact.json', artifact)
        archive = directory/'github-artifact.zip'
        if not archive.is_file():
            if requested and artifact['id']not in requested:
                continue
            if artifact['expired']: raise ValueError('Cannot download expired artifact')
            if shutil.disk_usage(store).free<artifact['size_in_bytes']+args.min_free_mb*1024**2:
                raise ValueError('Insufficient free space for raw artifact while retaining configured headroom')
            temporary = archive.with_suffix('.download')
            with temporary.open('wb') as stream:
                subprocess.run(['gh','api',f'repos/{args.repo}/actions/artifacts/{artifact["id"]}/zip'],stdout=stream,check=True)
            temporary.replace(archive)
        published_digest = artifact.get('digest')
        if published_digest and published_digest.startswith('sha256:') and sha(archive) != published_digest.split(':',1)[1]:
            raise ValueError('GitHub-published artifact SHA256 does not match the downloaded archive')
        write(directory/'download.json',dict(run_id=args.run_id,head_sha=args.commit,artifact_id=artifact['id'],
            sha256=sha(archive),bytes=archive.stat().st_size,downloaded_at_utc=datetime.now(timezone.utc).isoformat()))
    return run, pages


def main():
    global _MIN_FREE_BYTES,_BOUNDED_WRITES
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='alejandrozu/platonic-packing')
    p.add_argument('--run-id',type=int,required=True)
    p.add_argument('--commit',required=True)
    p.add_argument('--base-formal',type=Path,required=True)
    p.add_argument('--store',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--fetch',action='store_true',help='One metadata/download pass; never polls')
    p.add_argument('--stream-objects',action='store_true',help='Hash proof objects directly from immutable raw ZIPs; extract only sources/logs/receipts')
    p.add_argument('--bounded-nonobject-writes',action='store_true',help='Keep the same free-space floor, reserving each next file and checking every <=1MiB write')
    p.add_argument('--download-artifact-ids',nargs='+',type=int,
        help='Fetch only these new artifacts; already downloaded artifacts are still revalidated')
    p.add_argument('--min-free-mb',type=int,default=512,help='Required free-space headroom before new downloads')
    p.add_argument('--core-supplement',type=Path,help='Verified Linux core supplement provenance; only four exact-SHA omitted probe files may be restored')
    p.add_argument('--require-all-402',action='store_true')
    p.add_argument('--max-uncompressed-bytes',type=int,default=10_000_000_000)
    args=p.parse_args()
    if args.min_free_mb<0:p.error('min-free-mb must be nonnegative')
    _MIN_FREE_BYTES=args.min_free_mb*1024**2
    _BOUNDED_WRITES=args.bounded_nonobject_writes
    operator_reader=Path(evidence_store.__file__).resolve()
    operator_reader_sha256=sha(operator_reader)
    base=args.base_formal.resolve(); store=args.store.resolve()/f'run-{args.run_id}'
    store.mkdir(parents=True,exist_ok=True)
    if args.fetch:
        run,artifacts=fetch(args,store)
    else:
        run,artifacts=read(store/'run.json'),read(store/'artifacts.json')
    if run['id'] != args.run_id or run['head_sha'] != args.commit:
        raise ValueError('Stored run provenance mismatch')
    validated=[]; failures=[]; unfetched=[]
    for artifact in artifacts:
        if not re.fullmatch(ARTIFACT_PATTERN,artifact['name']): continue
        directory=store/'artifacts'/str(artifact['id'])
        if not(directory/'github-artifact.zip').is_file():
            unfetched.append(artifact['id']);continue
        try:
            if artifact.get('workflow_run',{}).get('id')!=args.run_id or artifact.get('workflow_run',{}).get('head_sha')!=args.commit:
                raise ValueError('Stored artifact belongs to a different workflow run or commit')
            outer=directory/'github-artifact.zip'; download=read(directory/'download.json')
            if sha(outer)!=download['sha256'] or download['artifact_id']!=artifact['id'] or download['run_id']!=args.run_id or download['head_sha']!=args.commit:
                raise ValueError('Downloaded artifact digest/provenance mismatch')
            published_digest=artifact.get('digest')
            if published_digest and published_digest.startswith('sha256:') and sha(outer)!=published_digest.split(':',1)[1]:
                raise ValueError('Stored archive differs from GitHub-published artifact SHA256')
            root=(Path.home()/'Documents/Codex/lean-ci'/str(artifact['id'])/'formal')if os.name=='nt'else directory/'validation/formal'
            root=root.resolve()
            if args.stream_objects:
                with evidence_store.EvidenceStore(outer,root,download['sha256'],args.max_uncompressed_bytes)as objects:
                    inventory,relative=objects.validate(min_free_bytes=args.min_free_mb*1024**2,
                        bounded_writes=args.bounded_nonobject_writes)
                    base_inputs(base,root)
                    with objects.activate()as view:
                        supplement=supplement_missing_probes(base,view,args.core_supplement)
                        provenance,result,receipts=validate_shard(base,view,artifact,run,relative,supplement)
                    provenance.update(github_archive_sha256=sha(outer),evidence_zip_sha256=objects.nested_sha256,
                        evidence_inventory_sha256=sha(root/relative),storage_mode='zip-streamed-objects',object_store=objects.descriptor())
                write(directory/'validation-provenance.json',provenance)
                validated.append((provenance,result,root,receipts))
            else:
                nested=directory/'evidence.zip'
                with zipfile.ZipFile(outer) as z:
                    entries=zip_entries(z,args.max_uncompressed_bytes)
                    nested_names=[name for name in entries if name.endswith('/evidence.zip')or name=='evidence.zip']
                    if len(nested_names)!=1:
                        raise ValueError('Expected one evidence.zip in GitHub artifact')
                    data=z.read(nested_names[0])
                    if nested.exists() and nested.read_bytes()!=data:
                        raise ValueError('Nested evidence changed in existing artifact directory')
                    if not nested.exists(): nested.write_bytes(data)
                # Old evidence archives may include deeply named generated proof
                # sources. Keep raw artifacts/provenance in their original folder,
                # but use a short persistent Windows overlay to avoid MAX_PATH.
                root=(Path.home()/'Documents/Codex/lean-ci'/str(artifact['id'])/'formal')if os.name=='nt'else directory/'validation/formal'
                root=root.resolve()
                with zipfile.ZipFile(nested)as z:
                    pending=sum(info.file_size for name,info in zip_entries(z,args.max_uncompressed_bytes).items()
                        if not under(root,name.removeprefix('formal/')).exists())
                if shutil.disk_usage(root.parent if root.parent.exists()else store).free<pending+args.min_free_mb*1024**2:
                    raise ValueError('Insufficient free space for conservative extraction size plus configured headroom')
                base_inputs(base,root)
                inventory,relative=extract_evidence(nested,root,args.max_uncompressed_bytes)
                supplement=supplement_missing_probes(base,root,args.core_supplement)
                provenance,result,receipts=validate_shard(base,root,artifact,run,relative,supplement)
                provenance.update(github_archive_sha256=sha(outer),evidence_zip_sha256=sha(nested),
                    evidence_inventory_sha256=sha(root/relative))
                write(directory/'validation-provenance.json',provenance)
                validated.append((provenance,result,root,receipts))
        except Exception as exc:
            failures.append(dict(artifact_id=artifact['id'],error=repr(exc)))
    # Keep the most complete independently checked artifact per shard. Earlier
    # artifacts remain preserved and explicitly superseded, never silently mixed.
    chosen={}; superseded=[]
    for item in validated:
        provenance=item[0]; index=provenance['shard_index']
        rank=(provenance['verified_records'],provenance['artifact_created_at'],provenance['artifact_id'])
        if index not in chosen or rank>chosen[index][0]:
            if index in chosen: superseded.append(chosen[index][1][0])
            chosen[index]=(rank,item)
        else: superseded.append(provenance)
    accepted=[value[1] for _,value in sorted(chosen.items())]
    all_records=[]; core_environments=[]
    for provenance,result,root,receipts in accepted:
        environment=dict(sources=provenance['core_source_hashes'],objects=provenance['core_olean_hashes'])
        core_environments.append(environment)
        for record in result['verified_records']:
            all_records.append(dict(record,artifact_provenance=provenance))
    counts=Counter(r['record_id'] for r in all_records)
    if any(v!=1 for v in counts.values()): raise ValueError('Cross-shard duplicate verified record IDs')
    validator=load_validator(base,base)
    eligible=validator.inventory(); expected={r['record_id'] for r in eligible}
    if not set(counts)<=expected: raise ValueError('Verified record outside frozen402 scope')
    core_identical=bool(core_environments) and all(e==core_environments[0] for e in core_environments)
    common=core_identical
    shared_extensions={}
    for provenance,_,_,_ in accepted:
        for dependency in provenance.get('extension_dependencies',[]):
            previous=shared_extensions.get(dependency['path'])
            if previous is not None and previous!=dependency:common=False
            shared_extensions[dependency['path']]=dependency
    combined_path=None
    combined_performed=common and not any(p[0].get('storage_mode')=='zip-streamed-objects'for p in accepted)
    if combined_performed:
        root=store/'combined/formal'; base_inputs(base,root); receipts=[]
        # Retain one complete core receipt/log cohort. Other shard core
        # receipts remain intact in their raw artifacts and isolated roots;
        # their timestamps must not overwrite this selected cohort.
        first_core_root=accepted[0][2]
        first_core=read(first_core_root/'core-verification.json')
        core_files={'core-verification.json','verify_core.py','lean-toolchain',
            'lakefile.toml','lake-manifest.json','PackingCertificates.lean','PackingCertificates.olean'}
        for row in first_core['results']:
            core_files.update(row[k]for k in ('path','olean_path','log'))
        for relative in sorted(core_files):
            source=first_core_root/relative
            if source.is_file():link(source,root/relative)
        for provenance,result,source_root,source_receipts in accepted:
            extension_paths={p for d in provenance.get('extension_dependencies',[])for p in (d['path'],d['olean_path'])}
            for path in source_root.rglob('*'):
                if not path.is_file(): continue
                relative=path.relative_to(source_root).as_posix()
                if relative.startswith(('PackingCertificates/Catalogue/','catalogue/ci/','catalogue/ci-support/','catalogue/build-logs/')) or relative in provenance['core_source_hashes'] or relative in provenance['core_olean_hashes'] or relative in extension_paths:
                    link(path,root/relative)
            receipts.extend(root/path.relative_to(source_root) for path in source_receipts)
        combined_path=store/'combined/strict-replay.json'
        combined=replay(base,root,receipts,combined_path)
        if {r['record_id'] for r in combined['verified_records']}!=set(counts):
            raise ValueError('Common-root strict replay disagrees with independent shard validations')
        byid={r['record_id']:r for r in all_records}
        all_records=[dict(r,artifact_provenance=byid[r['record_id']]['artifact_provenance']) for r in combined['verified_records']]
    if sha(operator_reader)!=operator_reader_sha256:
        raise ValueError('Operator ZIP reader changed during evidence replay')
    result=dict(schema='github-lean-cohort-ingestion-v1',generated_at_utc=datetime.now(timezone.utc).isoformat(),
        run_id=args.run_id,run_head_sha=args.commit,frozen_catalogue_commit=FREEZE,
        ingestor_sha256=sha(Path(__file__)),trusted_validator_sha256=sha(base/'catalogue/summarize_verified.py'),
        operator_reader_sha256=operator_reader_sha256,
        artifact_validation_failures=failures,not_downloaded_artifact_ids=unfetched,
        validated_shards=[r[0] for r in accepted],superseded_artifacts=superseded,
        core_objects_identical_across_selected_shards=core_identical,
        shared_local_import_objects_compatible=common,combined_replay_omitted_for_streamed_objects=common and not combined_performed,combined_strict_replay=str(combined_path) if combined_path else None,
        verified_records=compact_rows(all_records),record_evidence_storage='pinned-per-artifact-independent-validation-v1',
        verified_totals=validator.totals(all_records),eligible_totals=validator.totals(eligible),
        missing_record_ids=sorted(expected-set(counts)),duplicate_record_ids=[],complete_402=(set(counts)==expected),
        trust_boundary='Source-bound kernel build receipts and matching Linux objects/logs, independently replayed. '
            'No compiler is rerun here; parsing, source transcription and unproved regular-template classification remain outside the kernel.')
    write(store/'cohort-validation.json',result)
    write(store/'cohort-reproduction.json',dict(schema='github-lean-cohort-reproduction-v1',
        run_id=args.run_id,run_head_sha=args.commit,frozen_catalogue_commit=FREEZE,
        shared_immutable_base=str(base),shared_base_directories=['catalogue/inputs','catalogue/inventory','catalogue/witnesses','catalogue/witnesses_nd'],
        combined_formal_root=str(store/'combined/formal')if combined_performed else None,
        selected_core_receipt_cohort_artifact=accepted[0][0]['artifact_id']if combined_performed else None,
        selected_shards=[dict(artifact_id=p['artifact_id'],shard_index=p['shard_index'],
            isolated_formal_root=p['validation_formal_root'],
            raw_artifact_zip=str(store/'artifacts'/str(p['artifact_id'])/'github-artifact.zip'),
            raw_artifact_sha256=p['github_archive_sha256'],
            evidence_zip=str(store/'artifacts'/str(p['artifact_id'])/'evidence.zip'),
            evidence_zip_sha256=p['evidence_zip_sha256'])for p,_,_,_ in accepted],
        reproduction='Restore one shared frozen input/witness/inventory tree; overlay each shard in an isolated root, '
            'or use the combined root only when all shared dependency objects agree. Never overlay Linux objects onto the Windows working tree.'))
    print(json.dumps(dict(verified=len(all_records),eligible=402,validated_shards=len(accepted),
        artifacts_failed_validation=len(failures),complete_402=result['complete_402'],output=str(store/'cohort-validation.json'))))
    if failures or args.require_all_402 and not result['complete_402']: raise SystemExit(1)


if __name__=='__main__':
    main()
