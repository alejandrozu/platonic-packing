#!/usr/bin/env python3
"""Immutable ZIP-backed proof objects for read-only evidence replay.

Sources, logs and receipts remain ordinary files. Objects are read directly
from the preserved GitHub artifact; no marker files or physical-object fallback
are used. This adapter never executes artifact-supplied Python or Lean.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
from types import SimpleNamespace
import zipfile

_ACTIVE = []
_Path = type(Path())
METADATA_RESERVE = 64 * 1024


def physical_sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def file_identity(path):
    value = Path(path).stat()
    if not stat.S_ISREG(value.st_mode):
        raise ValueError('Archive is not a regular file: ' + str(path))
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def reject_reparse_ancestors(path):
    """Reject existing filesystem aliases before any evidence write."""
    candidate = Path(os.path.abspath(path))
    for item in [candidate, *candidate.parents]:
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Existing symlink/junction/reparse evidence path forbidden: ' + str(item))


def safe_name(value):
    if '\\' in value or '\x00' in value:
        raise ValueError('Unsafe evidence path: ' + repr(value))
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(x in {'.', '..'} or ':' in x for x in path.parts):
        raise ValueError('Unsafe evidence path: ' + repr(value))
    return path.as_posix()


def entries(archive, maximum):
    result, folded, total = {}, set(), 0
    for info in archive.infolist():
        name = safe_name(info.filename.rstrip('/'))
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError('Evidence symlink forbidden: ' + name)
        if info.is_dir():
            continue
        if name in result or name.casefold() in folded:
            raise ValueError('Duplicate/case-colliding evidence member: ' + name)
        result[name] = info
        folded.add(name.casefold())
        total += info.file_size
    if total > maximum:
        raise ValueError('Evidence exceeds uncompressed-byte limit')
    return result


def active_store(path):
    candidate = Path(os.path.abspath(path))
    for store in reversed(_ACTIVE):
        try:
            relative = candidate.relative_to(store.root).as_posix()
        except ValueError:
            continue
        if candidate.suffix == '.olean':
            return store, relative
    return None, None


class EvidencePath(_Path):
    """A Path binding scoped to approved validators; no global Path patch."""
    def is_file(self):
        store, relative = active_store(self)
        return relative in store.objects if store else super().is_file()

    def resolve(self, strict=False):
        # An object is an inventory entry, never a physical symlink target.
        # Resolving through the ordinary filesystem first would let a stale
        # alias escape the active ZIP namespace before the digest check.
        store, relative = active_store(self)
        if store:
            if strict and relative not in store.objects:
                raise FileNotFoundError('Object is absent from selected ZIP inventory: ' + relative)
            return EvidencePath(store.root / relative)
        return super().resolve(strict=strict)

    def exists(self, *, follow_symlinks=True):
        store, relative = active_store(self)
        return relative in store.objects if store else super().exists(follow_symlinks=follow_symlinks)

    def stat(self, *, follow_symlinks=True):
        store, relative = active_store(self)
        if not store:
            return super().stat(follow_symlinks=follow_symlinks)
        return store.object_stat(relative)

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        store, relative = active_store(self)
        if not store:
            return super().open(mode, buffering, encoding, errors, newline)
        if mode != 'rb':
            raise ValueError('ZIP-backed proof objects permit only binary reads')
        return store.object_open(relative)


class EvidenceStore:
    def __init__(self, archive, root, expected_sha256=None, maximum=10_000_000_000):
        self.archive = Path(archive).resolve()
        reject_reparse_ancestors(root)
        self.root = Path(root).resolve()
        self.maximum = maximum
        self.identity = file_identity(self.archive)
        self.raw_sha256 = physical_sha(self.archive)
        if expected_sha256 is not None and self.raw_sha256 != expected_sha256:
            raise ValueError('Preserved raw archive SHA256 changed')
        with zipfile.ZipFile(self.archive) as outer:
            outer_entries = entries(outer, maximum)
            names = [n for n in outer_entries if n == 'evidence.zip' or n.endswith('/evidence.zip')]
            if len(names) != 1:
                raise ValueError('Expected exactly one nested evidence.zip')
            self.nested_member = names[0]
            self.nested_bytes = outer.read(names[0])
        self.nested_sha256 = hashlib.sha256(self.nested_bytes).hexdigest()
        self.buffer = io.BytesIO(self.nested_bytes)
        self.zip = zipfile.ZipFile(self.buffer)
        self.entries = entries(self.zip, maximum)
        names = [n for n in self.entries if n.endswith('/evidence-inventory.json')]
        if len(names) != 1 or not names[0].startswith('formal/'):
            raise ValueError('Expected exactly one formal evidence inventory')
        self.inventory_member = names[0]
        self.inventory_bytes = self.zip.read(names[0])
        self.inventory = json.loads(self.inventory_bytes.decode('utf8'))
        self.inventory_relative = names[0][len('formal/'):]
        self.rows = {}
        folded = set()
        for row in self.inventory['files']:
            name = safe_name(row['path'])
            if name in self.rows or name.casefold() in folded:
                raise ValueError('Duplicate/case-colliding inventory path')
            if not re.fullmatch('[0-9a-f]{64}', row['sha256']) or type(row['bytes']) is not int or row['bytes'] < 0:
                raise ValueError('Invalid evidence inventory size/digest')
            self.rows[name] = row
            folded.add(name.casefold())
        if set(self.entries) != {'formal/' + n for n in self.rows} | {self.inventory_member}:
            raise ValueError('Evidence contains missing/unlisted members')
        self.objects = {n: (self, n) for n in self.rows if n.endswith('.olean')}
        self.donors = {}
        self.initial_checked = False
        self.final_checked = False

    def _assert_archive_identity(self):
        if file_identity(self.archive) != self.identity:
            raise ValueError('Preserved artifact identity changed during replay')

    def _read_digest(self, relative, target=None, min_free_bytes=0):
        self._assert_archive_identity()
        row = self.rows[relative]
        entry = self.entries['formal/' + relative]
        if entry.file_size != row['bytes']:
            raise ValueError('Evidence member size mismatch: ' + relative)
        result = hashlib.sha256()
        with self.zip.open(entry) as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                result.update(block)
                if target is not None:
                    if shutil.disk_usage(self.root).free < len(block) + min_free_bytes + METADATA_RESERVE:
                        raise ValueError('Nonobject write would cross the required free-space floor')
                    target.write(block)
                    target.flush()
                    if shutil.disk_usage(self.root).free < min_free_bytes:
                        raise ValueError('Free-space floor crossed during nonobject write; acceptance stopped')
        if result.hexdigest() != row['sha256']:
            raise ValueError('Evidence member SHA256 mismatch: ' + relative)
        return result.hexdigest()

    def validate(self, extract=True, min_free_bytes=0, bounded_writes=False):
        """Hash every listed payload, extracting only nonobjects, once."""
        if extract:
            ancestor = self.root
            while not ancestor.exists():
                ancestor = ancestor.parent
            missing = [row['bytes'] for n, row in self.rows.items()
                if not n.endswith('.olean') and not (self.root / n).exists()]
            pending = max(missing, default=0) if bounded_writes else sum(missing)
            if shutil.disk_usage(ancestor).free < pending + min_free_bytes:
                raise ValueError('Insufficient space for nonobject evidence plus headroom')
            self.write_guard = dict(mode='per-file-and-per-1MiB-write' if bounded_writes else 'all-missing-uncompressed-bytes',
                minimum_free_bytes=min_free_bytes, metadata_reserve_bytes=METADATA_RESERVE,
                before_each_write_checked=True, after_each_write_checked=True,
                initial_reservation_bytes=pending)
        for name, row in self.rows.items():
            target = self.root / name
            reject_reparse_ancestors(target)
            if not target.resolve().is_relative_to(self.root):
                raise ValueError('Evidence target resolves outside the selected root')
            if name.endswith('.olean') or not extract:
                self._read_digest(name)
                continue
            if target.exists():
                if not target.is_file() or physical_sha(target) != row['sha256']:
                    raise ValueError('Conflicting existing immutable evidence: ' + name)
                self._read_digest(name)
            else:
                if shutil.disk_usage(self.root if self.root.exists() else ancestor).free < row['bytes'] + min_free_bytes + METADATA_RESERVE:
                    raise ValueError('Next nonobject file would cross the required free-space floor')
                target.parent.mkdir(parents=True, exist_ok=True)
                reject_reparse_ancestors(target)
                with target.open('xb') as output:
                    self._read_digest(name, output, min_free_bytes)
                if physical_sha(target) != row['sha256']:
                    raise ValueError('Extracted evidence SHA256 mismatch: ' + name)
        if extract:
            target = self.root / self.inventory_relative
            reject_reparse_ancestors(target)
            if target.exists():
                if target.read_bytes() != self.inventory_bytes:
                    raise ValueError('Changed existing evidence inventory')
            else:
                if shutil.disk_usage(self.root).free < len(self.inventory_bytes) + min_free_bytes + METADATA_RESERVE:
                    raise ValueError('Inventory write would cross the required free-space floor')
                target.parent.mkdir(parents=True, exist_ok=True)
                reject_reparse_ancestors(target)
                target.write_bytes(self.inventory_bytes)
                if shutil.disk_usage(self.root).free < min_free_bytes:
                    raise ValueError('Free-space floor crossed during inventory write; acceptance stopped')
        self.initial_checked = True
        return self.inventory, self.inventory_relative

    def add_supplement_object(self, archive, expected_archive_sha256, relative, expected_object_sha256):
        """Caller must independently approve exact older/donor receipt equality."""
        if relative not in {'CubeAuditProbe.olean', 'CayleyAuditProbe.olean'}:
            raise ValueError('Only omitted audit-probe objects may be supplemented')
        if relative in self.rows:
            if self.rows[relative]['sha256'] != expected_object_sha256:
                raise ValueError('Supplement conflicts with original inventory')
            return
        key = str(Path(archive).resolve())
        if key not in self.donors:
            donor = EvidenceStore(archive, self.root, expected_archive_sha256, self.maximum)
            donor.validate(extract=False)
            self.donors[key] = donor
        donor = self.donors[key]
        if relative not in donor.rows or donor.rows[relative]['sha256'] != expected_object_sha256:
            raise ValueError('Supplement object is missing or has a different SHA256')
        self.objects[relative] = (donor, relative)

    def object_open(self, relative):
        if relative not in self.objects:
            raise FileNotFoundError('No object in immutable evidence inventory: ' + relative)
        owner, name = self.objects[relative]
        owner._assert_archive_identity()
        return owner.zip.open(owner.entries['formal/' + name])

    def object_stat(self, relative):
        if relative not in self.objects:
            raise FileNotFoundError('No object in immutable evidence inventory: ' + relative)
        owner, name = self.objects[relative]
        owner._assert_archive_identity()
        info = owner.entries['formal/' + name]
        timestamp = datetime(*info.date_time, tzinfo=timezone.utc).timestamp()
        ident = owner.identity
        return SimpleNamespace(st_mode=stat.S_IFREG | 0o444, st_size=info.file_size,
            st_mtime=timestamp, st_mtime_ns=int(timestamp * 1e9), st_ctime_ns=ident[4],
            st_dev=ident[0], st_ino=int(hashlib.sha256((owner.raw_sha256 + name).encode()).hexdigest()[:15], 16))

    def verify_final(self):
        self._assert_archive_identity()
        if physical_sha(self.archive) != self.raw_sha256:
            raise ValueError('Raw artifact bytes changed before final acceptance')
        self._assert_archive_identity()
        for donor in self.donors.values():
            donor.verify_final()
        self.final_checked = True

    def descriptor(self):
        return dict(schema='zip-streamed-proof-objects-v1', raw_archive=str(self.archive),
            raw_archive_sha256=self.raw_sha256, nested_member=self.nested_member,
            nested_sha256=self.nested_sha256, inventory_member=self.inventory_member,
            inventory_sha256=hashlib.sha256(self.inventory_bytes).hexdigest(),
            objects_not_extracted=True, primary_object_count=sum(n.endswith('.olean') for n in self.rows),
            object_mtime_basis='ZIP member metadata, used only for evidence ranking',
            all_inventory_members_hashed=self.initial_checked,
            raw_archive_fresh_final_hash_passed=self.final_checked,
            nonobject_write_guard=getattr(self, 'write_guard', None),
            supplements=[d.descriptor() for d in self.donors.values()])

    @contextmanager
    def activate(self):
        if not self.initial_checked:
            raise ValueError('Object store must validate its complete inventory before replay')
        _ACTIVE.append(self)
        try:
            yield EvidencePath(self.root)
            self.verify_final()
        finally:
            if _ACTIVE.pop() is not self:
                raise RuntimeError('Evidence store context nesting changed')

    def close(self):
        for donor in self.donors.values():
            donor.close()
        self.zip.close()
        self.buffer.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


@contextmanager
def reopen(provenance):
    """Reopen an accepted streamed environment for a fresh independent replay."""
    root = Path(provenance['validation_formal_root']).resolve()
    if provenance.get('storage_mode') != 'zip-streamed-objects':
        yield root
        return
    descriptor = provenance['object_store']
    for stored, enclosing in [('raw_archive_sha256', 'github_archive_sha256'),
                              ('nested_sha256', 'evidence_zip_sha256'),
                              ('inventory_sha256', 'evidence_inventory_sha256')]:
        if descriptor[stored] != provenance[enclosing]:
            raise ValueError('Streamed object store disagrees with enclosing provenance: ' + stored)
    if any(descriptor.get(key) is not True for key in ['objects_not_extracted',
            'all_inventory_members_hashed', 'raw_archive_fresh_final_hash_passed']):
        raise ValueError('Accepted object-store provenance omits required hash/immutability flags')
    with EvidenceStore(descriptor['raw_archive'], root, descriptor['raw_archive_sha256']) as store:
        actual = store.descriptor()
        for key in ['nested_member', 'nested_sha256', 'inventory_member', 'inventory_sha256', 'primary_object_count']:
            if actual[key] != descriptor[key]:
                raise ValueError('ZIP-backed object descriptor changed: ' + key)
        store.validate(extract=False)
        supplement = provenance.get('exact_sha_core_supplement')
        if supplement:
            donor_path = Path(supplement['source_provenance_path'])
            if physical_sha(donor_path) != supplement['source_provenance_sha256']:
                raise ValueError('Core-supplement provenance changed')
            donor = json.loads(donor_path.read_text(encoding='utf8'))
            for row in supplement['files']:
                if row['path'].endswith('.olean'):
                    store.add_supplement_object(donor['github_archive'], donor['github_archive_sha256'], row['path'], row['sha256'])
        with store.activate() as view:
            yield view


def public_descriptor(provenance):
    """Portable metadata; the raw-artifact index supplies its relative locator."""
    if provenance.get('storage_mode') != 'zip-streamed-objects':
        return None
    descriptor = provenance['object_store']
    result = {key: descriptor[key] for key in ['schema', 'raw_archive_sha256', 'nested_member',
        'nested_sha256', 'inventory_member', 'inventory_sha256', 'objects_not_extracted',
        'primary_object_count', 'object_mtime_basis', 'all_inventory_members_hashed',
        'raw_archive_fresh_final_hash_passed']}
    result['raw_artifact_index_key'] = f'run-{provenance["run_id"]}-artifact-{provenance["artifact_id"]}'
    result['nonobject_write_guard'] = descriptor.get('nonobject_write_guard')
    return result
