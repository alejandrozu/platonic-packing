#!/usr/bin/env python3
"""Bounded streaming-reader regressions; optional real 34-record replay."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import zipfile

import evidence_store as store
import ingest_ci as checked


def archive(path, objects, inventory_objects=None):
    payload = dict(objects)
    rows = payload if inventory_objects is None else inventory_objects
    inventory = dict(files=[dict(path=n, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        for n, data in rows.items()])
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, 'w') as z:
        for name, data in payload.items():
            z.writestr('formal/' + name, data)
        z.writestr('formal/catalogue/evidence-inventory.json', json.dumps(inventory))
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('evidence.zip', inner.getvalue())


def negative_tests():
    results = []
    with tempfile.TemporaryDirectory(prefix='lean-zip-reader-') as temporary:
        here = Path(temporary)
        good = {'A.olean': b'checked object bytes', 'A.lean': b'theorem a : True := by trivial\n'}
        archive(here/'good.zip', good)
        root = here/'formal'
        with store.EvidenceStore(here/'good.zip', root) as evidence:
            evidence.validate()
            assert not (root/'A.olean').exists()
            with evidence.activate() as view:
                assert (view/'A.olean').is_file()
                assert (view/'A.olean').read_bytes() == good['A.olean']
                with checked.digest_memoization([]) as memo:
                    assert memo.digest(view/'A.olean') == hashlib.sha256(good['A.olean']).hexdigest()
                assert memo.report()['fresh_final_hashes'] == 1
            assert evidence.descriptor()['raw_archive_fresh_final_hash_passed']
        results.append('valid object read without extraction and fresh-final-hash passed')
        # A real object from a previous extraction cannot conceal a missing
        # immutable member in the currently selected archive.
        (root/'B.olean').write_bytes(b'old unrelated object')
        with store.EvidenceStore(here/'good.zip', root) as evidence:
            evidence.validate()
            with evidence.activate() as view:
                assert not (view/'B.olean').is_file()
                try: (view/'B.olean').read_bytes()
                except FileNotFoundError: pass
                else: raise AssertionError('Physical stale object concealed missing member')
        results.append('missing virtual object rejected despite physical stale object')
        archive(here/'altered.zip', dict(good, **{'A.olean': b'altered object bytes'}), good)
        try:
            with store.EvidenceStore(here/'altered.zip', root) as evidence: evidence.validate(False)
        except ValueError as exc: assert 'SHA256' in str(exc)
        else: raise AssertionError('Altered object accepted')
        results.append('altered member rejected against original inventory SHA256')
        archive(here/'missing.zip', {'A.lean': good['A.lean']}, good)
        try: store.EvidenceStore(here/'missing.zip', root)
        except ValueError as exc: assert 'missing/unlisted' in str(exc)
        else: raise AssertionError('Missing inventoried object accepted')
        results.append('missing inventoried member rejected before replay')
        # Resolution must stay lexical for virtual objects, even when the
        # physical filesystem attempts to send the same path elsewhere.
        from unittest.mock import patch
        with store.EvidenceStore(here/'good.zip', root) as evidence:
            evidence.validate(False)
            with evidence.activate() as view:
                with patch.object(type(Path()), 'resolve', side_effect=AssertionError('physical resolution reached')):
                    assert str((view/'A.olean').resolve()) == str(evidence.root/'A.olean')
                    assert not (view/'B.olean').is_file()
        results.append('virtual object resolution never follows physical aliases')
        outside = here/'outside'
        outside.mkdir()
        (outside/'marker').write_bytes(b'outside must stay unchanged')
        alias = here/'alias'
        try:
            alias.symlink_to(outside, target_is_directory=True)
        except OSError:
            # Simulate the platform lstat boundary only when this account is
            # forbidden to create links; the lexical test above still runs.
            import stat
            from types import SimpleNamespace
            original = type(Path()).lstat
            def alias_stat(path):
                return SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0) if path == alias else original(path)
            with patch.object(type(Path()), 'lstat', alias_stat):
                try: store.EvidenceStore(here/'good.zip', alias/'formal')
                except ValueError as exc: assert 'reparse' in str(exc)
                else: raise AssertionError('Existing alias ancestor accepted')
            results.append('reparse ancestor rejected via platform-lstat boundary regression (link creation unavailable)')
        else:
            try: store.EvidenceStore(here/'good.zip', alias/'formal')
            except ValueError as exc: assert 'reparse' in str(exc)
            else: raise AssertionError('Existing symlink ancestor accepted')
            assert not (outside/'formal').exists()
            results.append('actual existing symlink ancestor rejected without outside writes')
        for label, names in [('traversal', ['formal/../outside.olean']),
                             ('case collision', ['formal/A.olean', 'formal/a.olean'])]:
            inner = io.BytesIO()
            with zipfile.ZipFile(inner, 'w') as z:
                for name in names: z.writestr(name, b'object')
                z.writestr('formal/catalogue/evidence-inventory.json', '{"files":[]}')
            candidate = here/(label.replace(' ', '-')+'.zip')
            with zipfile.ZipFile(candidate, 'w') as z: z.writestr('evidence.zip', inner.getvalue())
            try: store.EvidenceStore(candidate, root)
            except ValueError: pass
            else: raise AssertionError(label + ' ZIP accepted')
            results.append(label + ' ZIP rejected')
        # Keep size and modification time unchanged: the final raw SHA pass
        # must still reject bytes altered after the immutable buffer was read.
        mutation = here/'mutation.zip'
        mutation.write_bytes((here/'good.zip').read_bytes())
        with zipfile.ZipFile(mutation, 'a') as z: z.comment = b'a'
        with store.EvidenceStore(mutation, root) as evidence:
            evidence.validate(False)
            before = mutation.stat()
            data = mutation.read_bytes()
            mutation.write_bytes(data[:-1]+b'b')
            os.utime(mutation, ns=(before.st_atime_ns, before.st_mtime_ns))
            try:
                with evidence.activate(): pass
            except ValueError: pass
            else: raise AssertionError('Raw archive mutation after buffering accepted')
        results.append('equal-size raw archive mutation rejected before final acceptance')
        # A bounded guard may accept successive small files that fit while a
        # conservative reservation of their entire uncompressed sum does not.
        floor = 1024
        archive(here/'budget.zip', {f'p{i}.lean': b'x'*1_500_000 for i in range(3)})
        with patch.object(store.shutil, 'disk_usage', return_value=type('Space', (), {'free': 2_000_000})()):
            with store.EvidenceStore(here/'budget.zip', here/'conservative') as evidence:
                try: evidence.validate(min_free_bytes=floor)
                except ValueError: pass
                else: raise AssertionError('Conservative sum reservation ignored')
            with store.EvidenceStore(here/'budget.zip', here/'bounded') as evidence:
                evidence.validate(min_free_bytes=floor, bounded_writes=True)
                assert evidence.write_guard['minimum_free_bytes'] == floor
        results.append('bounded writes retain the same floor while reserving each next file')
        with patch.object(store.shutil, 'disk_usage', side_effect=[
                type('Space', (), {'free': 2_000_000})(),
                type('Space', (), {'free': 2_000_000})(),
                type('Space', (), {'free': 2_000_000})(),
                type('Space', (), {'free': floor-1})()]):
            with store.EvidenceStore(here/'budget.zip', here/'external-writer') as evidence:
                try: evidence.validate(min_free_bytes=floor, bounded_writes=True)
                except ValueError as exc: assert 'floor crossed' in str(exc)
                else: raise AssertionError('External writer crossing free-space floor accepted')
        results.append('post-write free-space loss fails closed before acceptance')
        with store.EvidenceStore(here/'good.zip', root) as evidence:
            try:
                with evidence.activate(): pass
            except ValueError as exc: assert 'complete inventory' in str(exc)
            else: raise AssertionError('Unvalidated object store activated')
            evidence.validate(False)
            with evidence.activate(): pass
            descriptor = evidence.descriptor()
        provenance = dict(validation_formal_root=str(root), storage_mode='zip-streamed-objects',
            object_store=descriptor, github_archive_sha256=descriptor['raw_archive_sha256'],
            evidence_zip_sha256=descriptor['nested_sha256'], evidence_inventory_sha256=descriptor['inventory_sha256'])
        for field in ['github_archive_sha256', 'evidence_zip_sha256', 'evidence_inventory_sha256']:
            corrupted = dict(provenance, **{field: '0'*64})
            try:
                with store.reopen(corrupted): pass
            except ValueError as exc: assert 'enclosing provenance' in str(exc)
            else: raise AssertionError('Mismatched enclosing object-store hash accepted')
        corrupted = dict(provenance, object_store=dict(descriptor, raw_archive_fresh_final_hash_passed=False))
        try:
            with store.reopen(corrupted): pass
        except ValueError as exc: assert 'required hash' in str(exc)
        else: raise AssertionError('Incomplete original raw-final-hash attestation accepted')
        results.append('unvalidated activation and four enclosing-provenance corruptions rejected')
        prior_floor,prior_mode=checked._MIN_FREE_BYTES,checked._BOUNDED_WRITES
        try:
            checked._MIN_FREE_BYTES=1024
            checked._BOUNDED_WRITES=False
            with patch.object(checked.shutil, 'disk_usage', return_value=type('Space', (), {'free': 2_000_000})()):
                try:checked.metadata_bytes(here/'conservative-metadata.json',b'x'*3_000_000)
                except ValueError:pass
                else:raise AssertionError('Conservative metadata reservation ignored')
                checked._BOUNDED_WRITES=True
                checked.metadata_bytes(here/'bounded-metadata.json',b'x'*3_000_000)
                assert (here/'bounded-metadata.json').stat().st_size==3_000_000
        finally:
            checked._MIN_FREE_BYTES,checked._BOUNDED_WRITES=prior_floor,prior_mode
        results.append('large generated metadata uses bounded writes without lowering the free-space floor')
    return results


def cross_mode(base, provenance):
    p = checked.read(provenance)
    root = Path(p['validation_formal_root'])
    original = checked.read(Path(p['validation_path']))
    archive_path = provenance.parent/'github-artifact.zip'
    with store.EvidenceStore(archive_path, root, p['github_archive_sha256']) as evidence:
        evidence.validate(extract=False)
        with evidence.activate() as view:
            checked.supplement_missing_probes(base, view)
            checked.verify_core(base, view)
            summary = checked.load_validator(base, view)
            with checked.digest_memoization([(summary, 'sha'), (summary.extension_audit.core, 'digest')]) as audit:
                result = checked._replay_using(summary, base, view,
                    [view/r['path'] for r in original['receipt_inputs']])
        # Ignore only filesystem/ZIP timestamps, which rank equivalent valid
        # receipts; all proof identities and hash-pinned obligations must agree.
        def identities(data):
            return {r['record_id']: {k: v for k, v in r['evidence'].items() if k not in {'artifact_mtime_utc'}}
                for r in data['verified_records']}
        assert identities(result) == identities(original), 'Cross-mode evidence mismatch'
        assert result['ignored_rows'] == original['ignored_rows']
        return dict(verified=len(result['verified_records']), ignored=len(result['ignored_rows']),
            proof_hash_and_closure_equivalence=True, digest_audit=audit.report(), object_store=evidence.descriptor())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-formal', type=Path)
    p.add_argument('--cross-mode-provenance', type=Path)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = dict(negative_tests=negative_tests())
    if args.cross_mode_provenance:
        result['cross_mode'] = cross_mode(args.base_formal.resolve(), args.cross_mode_provenance.resolve())
    if args.output: checked.write(args.output, result)
    print(json.dumps(result))


if __name__ == '__main__': main()
