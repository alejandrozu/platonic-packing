#!/usr/bin/env python3
"""Build extension modules sequentially without changing the frozen core.

Example:
  python verify_extensions.py --mathlib-project /path/to/built/project

Uses verify_core's pinned Lean/mathlib preflight and strict axiom audit. The
normal catalogue runner intentionally snapshots only direct core modules;
these extension modules live in subdirectories to avoid mutating that boundary.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import verify_core as core

DEFAULT_MODULES = [
    'PackingCertificates/Extensions/GenericDimension.lean',
    'PackingCertificates/Extensions/Complexity.lean',
]


def local_import_closure(source, formal_root=None):
    """Find every transitive local Lean import, not only direct core files.

    Lean's static import header uses dotted module names. Mathlib/Lean/Std
    dependencies are supplied by the separately pinned toolchain preflight;
    missing project imports are an error rather than silently omitted.
    """
    formal_root = Path(formal_root or core.HERE).resolve()
    def relative(path):
        return str(path.resolve().relative_to(formal_root)).replace('\\', '/')
    found = {}
    visiting = set()
    def visit(path):
        text = path.read_text(encoding='utf8')
        for header in re.findall(r'^\s*(?:public\s+)?import\s+([^\n]+)', text, re.M):
            for module in header.split('--', 1)[0].split():
                if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*', module):
                    raise ValueError('Unrecognized static import token in '+relative(path)+': '+module)
                dependency = formal_root.joinpath(*module.split('.')).with_suffix('.lean')
                if not dependency.is_file():
                    if module.split('.')[0] in {'Mathlib', 'Lean', 'Std', 'Init', 'Batteries', 'Aesop', 'Qq', 'ProofWidgets', 'Plausible', 'ImportGraph'}:
                        continue
                    raise ValueError('Missing local import '+module+' from '+relative(path))
                dependency = dependency.resolve()
                if dependency in visiting:
                    raise ValueError('Cyclic local imports at '+relative(dependency))
                if dependency not in found:
                    found[dependency] = None
                    visiting.add(dependency)
                    visit(dependency)
                    visiting.remove(dependency)
    visiting.add(source.resolve())
    visit(source.resolve())
    return sorted(found, key=relative)


def dependency_snapshot(source, formal_root=None):
    formal_root = Path(formal_root or core.HERE).resolve()
    def relative(path):
        return str(path.resolve().relative_to(formal_root)).replace('\\', '/')
    rows = []
    for path in local_import_closure(source, formal_root):
        target = path.with_suffix('.olean')
        if not target.is_file():
            raise ValueError('Imported local object is missing: '+relative(target))
        rows.append(dict(path=relative(path), source_sha256=core.digest(path),
            olean_path=relative(target), olean_sha256=core.digest(target)))
    return rows


def changed_dependencies(rows, formal_root=None):
    formal_root = Path(formal_root or core.HERE).resolve()
    changed = []
    for item in rows:
        source, target = formal_root/item['path'], formal_root/item['olean_path']
        if not source.is_file() or not target.is_file() or core.digest(source) != item['source_sha256'] or core.digest(target) != item['olean_sha256']:
            changed.append(item['path'])
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mathlib-project', type=Path, required=True)
    parser.add_argument('--lean', type=Path, default=core.default_lean())
    parser.add_argument('--memory-mb', type=int, default=3072)
    parser.add_argument('--timeout', type=float, default=900)
    parser.add_argument('--modules', nargs='+', default=DEFAULT_MODULES)
    parser.add_argument('--output', type=Path, default=core.HERE/'extension-verification.json')
    args = parser.parse_args()
    if args.memory_mb <= 0 or args.timeout <= 0:
        parser.error('memory-mb and timeout must be positive')
    sources = []
    for module in args.modules:
        source = (core.HERE/module).resolve()
        relative = source.relative_to(core.HERE)
        if len(relative.parts) < 3 or relative.parts[0] != 'PackingCertificates':
            parser.error('Only extension sources in PackingCertificates subdirectories are accepted')
        if source.suffix != '.lean' or not source.is_file():
            parser.error('Missing Lean source: '+str(source))
        sources.append(source)
    env, preflight = core.preflight(args)
    # The new geometric module imports Core. Record the existing source and
    # object boundary instead of silently rebuilding it while catalogue proofs
    # may be running. The pinned mathlib tree is checked by preflight.
    dependencies = []
    for source in sorted((core.HERE/'PackingCertificates').glob('*.lean')):
        target = source.with_suffix('.olean')
        dependencies.append(dict(path=core.relative(source), source_sha256=core.digest(source),
            olean=core.relative(target), olean_sha256=core.digest(target) if target.is_file() else None))
    rows = []
    for source in sources:
        imported = dependency_snapshot(source)
        row = core.build_one(source, args, env, set())
        row['imported_dependencies'] = imported
        row['changed_imported_dependencies'] = changed_dependencies(imported)
        if row['changed_imported_dependencies']:
            row['errors'].append('transitive_import_dependency_changed_during_build')
            row['passed'] = False
        rows.append(row)
        print(json.dumps(dict(path=core.relative(source), passed=row['passed'],
            elapsed_seconds=row.get('elapsed_seconds'), errors=row.get('errors')), ensure_ascii=False), flush=True)
        if not row['passed']:
            break
    changed = [item['path'] for item in dependencies
        if core.digest(core.HERE/item['path']) != item['source_sha256'] or
        (item['olean_sha256'] is not None and
         core.digest(core.HERE/item['olean']) != item['olean_sha256'])]
    for row in rows:
        row['changed_imported_dependencies_at_receipt'] = changed_dependencies(row['imported_dependencies'])
        if row['changed_imported_dependencies_at_receipt']:
            row['errors'].append('transitive_import_dependency_changed_before_receipt')
            row['passed'] = False
    receipt = dict(schema='packing-extension-verification-v2',
        created_utc=datetime.now(timezone.utc).isoformat(),
        verifier=dict(path='verify_extensions.py', sha256=core.digest(Path(__file__))),
        core_verifier_sha256=core.digest(core.HERE/'verify_core.py'),
        preflight=preflight, memory_mb=args.memory_mb,
        requested_modules=args.modules, core_dependencies=dependencies,
        changed_core_dependencies=changed, results=rows,
        passed=len(rows) == len(sources) and all(row['passed'] for row in rows) and not changed)
    args.output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False)+'\n', encoding='utf8')
    if not receipt['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
