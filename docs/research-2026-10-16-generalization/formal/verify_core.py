#!/usr/bin/env python3
"""Sequential, pinned-toolchain reproduction of the formal core and regressions.

Use --mathlib-project to reuse an already-built compatible Lake dependency
tree. No package is downloaded. This script does not build catalogue instances
and does not alter the historical verification.json receipt.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
LEAN_VERSION = '4.31.0'
MATHLIB_REVISION = 'fabf563a7c95a166b8d7b6efca11c8b4dc9d911f'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
LIBRARIES = ['Core', 'Rational', 'Cube', 'Catalogue', 'Barycentric', 'Cayley',
    'TemplateData', 'BoxGeometry', 'CubeFast', 'AxisFast', 'Example']
REGRESSIONS = ['RationalRegression.lean', 'BarycentricRegression.lean',
    'CubeAuditProbe.lean', 'CayleyAuditProbe.lean', 'AxisFastRegression.lean']
EXPECTED_NEGATIVES = {
    'RationalRegression.lean': {'overlap', 'nonorthogonal', 'missingPlane', 'protrudes'},
    'BarycentricRegression.lean': {'negativeWeight', 'wrongMass', 'wrongVertex', 'zeroScale', 'protrudes'},
    'CayleyAuditProbe.lean': {'wrongInverse', 'oddSign', 'changedRotation'},
    'AxisFastRegression.lean': {'wrongCache', 'falseAxisLabel', 'falseAxisSign'},
}
CENTRAL_AUDITS = {
    'PackingCertificates.finite_certificate_sound',
    'PackingCertificates.Rational.check_sound',
    'PackingCertificates.Rational.checkPlaced_sound',
    'PackingCertificates.Rational.checkPlaced_preserves_squared_distance',
    'PackingCertificates.Cube.vertexBody_eq_unitBox',
    'PackingCertificates.Cube.image_vertexBody',
    'PackingCertificates.Catalogue.CubeRecord.check_sound',
    'PackingCertificates.Barycentric.vertexCheck_sound',
    'PackingCertificates.Barycentric.check_sound',
    'PackingCertificates.Cayley.check_sound',
    'PackingCertificates.Cayley.determinant_real',
    'PackingCertificates.BoxGeometry.corner_hull_eq_unitBox',
    'PackingCertificates.BoxGeometry.template_hull_eq_box',
    'PackingCertificates.BoxGeometry.c8_body',
    'PackingCertificates.BoxGeometry.hc5_body',
    'PackingCertificates.BoxGeometry.hc6_body',
    'PackingCertificates.CubeFast.support_bounds',
    'PackingCertificates.CubeFast.fastCheck_sound',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    try:
        return str(path.resolve().relative_to(HERE)).replace('\\', '/')
    except ValueError:
        return str(path.resolve())


def run_capture(command, timeout, env=None, cwd=HERE):
    try:
        completed = subprocess.run(list(map(str, command)), cwd=cwd, env=env,
            capture_output=True, text=True, encoding='utf8', errors='replace', timeout=timeout)
        return completed.returncode, completed.stdout+completed.stderr
    except subprocess.TimeoutExpired as error:
        def decoded(value):
            return value.decode('utf8', errors='replace') if isinstance(value, bytes) else value or ''
        return None, 'TIMEOUT\n'+decoded(error.stdout)+decoded(error.stderr)


def axiom_audit(log):
    found = {name: sorted(x.strip() for x in axioms.split(',') if x.strip())
        for name, axioms in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", log, re.S)}
    found.update({name: [] for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", log)})
    return found


def negative_assertions(text):
    pattern = r'\b(?:example|theorem\s+\w+)\s*:\s*(checkPlaced|check|cacheRowCheck)\s+([\w\s.]+?)\s*=\s*false\s*:=\s*by\s+decide\s+\+kernel'
    labels = set().union(*EXPECTED_NEGATIVES.values())
    return [{'checker': checker, 'arguments': args.split(),
        'case': next((arg for arg in args.split() if arg in labels), args.split()[0]),
        'expected': False, 'method': 'by decide +kernel'}
        for checker, args in re.findall(pattern, text)]


def default_lean():
    directory = Path.home()/'.elan/toolchains'/('leanprover--lean4---v'+LEAN_VERSION)/'bin'
    executable = directory/('lean.exe' if os.name == 'nt' else 'lean')
    return executable if executable.is_file() else Path(shutil.which('lean') or executable)


def preflight(args):
    toolchain = (HERE/'lean-toolchain').read_text(encoding='utf8').strip()
    if toolchain != 'leanprover/lean4:v'+LEAN_VERSION:
        raise ValueError('lean-toolchain does not match the expected pinned version')
    command = [str(args.lean), '--version']
    code, version = run_capture(command, 30)
    match = re.search(r'Lean \(version ([^, )]+)', version)
    if code != 0 or not match or match.group(1) != LEAN_VERSION:
        raise ValueError('Expected Lean '+LEAN_VERSION+'; received '+version.strip())
    project = args.mathlib_project.resolve()
    packages = project/'.lake/packages'
    mathlib = packages/'mathlib'
    if not mathlib.is_dir():
        raise ValueError('No mathlib source tree under '+str(packages))
    git = shutil.which('git')
    if not git:
        raise ValueError('git is required to check the pinned mathlib source revision')
    git_command = [git, '-C', str(mathlib), 'rev-parse', 'HEAD']
    git_code, revision = run_capture(git_command, 30)
    if git_code != 0 or revision.strip() != MATHLIB_REVISION:
        raise ValueError('Expected mathlib '+MATHLIB_REVISION+'; received '+revision.strip())
    dependency_paths = [HERE]
    project_build = project/'.lake/build/lib/lean'
    if project_build.is_dir():
        dependency_paths.append(project_build)
    dependency_paths.extend(p/'.lake/build/lib/lean' for p in sorted(packages.iterdir())
        if (p/'.lake/build/lib/lean').is_dir())
    if not (mathlib/'.lake/build/lib/lean/Mathlib/Data/Real/Basic.olean').is_file():
        raise ValueError('mathlib compiled dependencies are missing; obtain the pinned cache first')
    env = os.environ.copy()
    env['LEAN_PATH'] = os.pathsep.join(map(str, dependency_paths))
    return env, dict(lean_command=command, lean_version_output=version.strip(),
        expected_lean_version=LEAN_VERSION, mathlib_command=git_command,
        expected_mathlib_revision=MATHLIB_REVISION, actual_mathlib_revision=revision.strip(),
        mathlib_project=str(project), dependency_paths=list(map(str, dependency_paths)))


def stages():
    result = []
    for name in LIBRARIES:
        source = HERE/'PackingCertificates'/(name+'.lean')
        if name == 'AxisFast' and not source.is_file():
            continue
        result.append(source)
    result.extend(HERE/name for name in ['PackingCertificates.lean', 'Audit.lean', *REGRESSIONS])
    return result


def build_one(source, args, env, central_audits):
    started = time.monotonic()
    text = source.read_text(encoding='utf8')
    source_hash = digest(source)
    target = source.with_suffix('.olean')
    command = [str(args.lean), '-j', '1', '-M', str(args.memory_mb),
        '-o', str(target), str(source)]
    code, log = run_capture(command, args.timeout, env)
    logpath = HERE/'core-build-logs'/(relative(source).replace('/', '_')+'.log')
    logpath.parent.mkdir(exist_ok=True)
    logpath.write_text(log, encoding='utf8')
    audited = axiom_audit(log)
    used = set().union(*(set(v) for v in audited.values())) if audited else set()
    expected = set(re.findall(r'^\s*#print\s+axioms\s+([\w.]+)', text, re.M))
    if source.name == 'Audit.lean':
        expected |= central_audits
    missing_audits = sorted(name for name in expected if name not in audited and
        not any(full.endswith('.'+name) for full in audited))
    negatives = negative_assertions(text)
    missing_negatives = sorted(EXPECTED_NEGATIVES.get(source.name, set())-
        {item['case'] for item in negatives})
    changed = digest(source) != source_hash
    errors = []
    if code != 0:
        errors.append('compiler_timeout' if code is None else 'compiler_nonzero_exit')
    if not target.is_file():
        errors.append('olean_not_created')
    if changed:
        errors.append('source_changed_during_build')
    if used-ALLOWED_AXIOMS or 'sorryAx' in log:
        errors.append('unexpected_or_admitted_axiom')
    if missing_audits:
        errors.append('required_axiom_audit_missing')
    if missing_negatives:
        errors.append('required_negative_regression_missing')
    passed = not errors
    for item in negatives:
        item['kernel_checked'] = passed
    return dict(path=relative(source), passed=passed, exit_code=code,
        elapsed_seconds=round(time.monotonic()-started, 3), command=command,
        source_sha256=source_hash, source_unchanged_during_build=not changed,
        olean_path=relative(target), olean_sha256=digest(target) if passed else None,
        log=relative(logpath), log_sha256=digest(logpath),
        axioms=sorted(used), unexpected_axioms=sorted(used-ALLOWED_AXIOMS),
        audited_theorems=audited, missing_audit_theorems=missing_audits,
        negative_checks=negatives, missing_negative_cases=missing_negatives, errors=errors)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lean', type=Path, default=default_lean())
    ap.add_argument('--mathlib-project', type=Path, default=HERE)
    ap.add_argument('--timeout', type=int, default=600)
    ap.add_argument('--memory-mb', type=int, default=4096)
    ap.add_argument('--receipt', type=Path, default=HERE/'core-verification.json')
    args = ap.parse_args()
    args.lean = args.lean.resolve()
    receipt = dict(started_at_utc=datetime.now(timezone.utc).isoformat(),
        status='running', sequential=True, expected_lean_version=LEAN_VERSION,
        expected_mathlib_revision=MATHLIB_REVISION, allowed_axioms=sorted(ALLOWED_AXIOMS),
        builder_sha256=digest(Path(__file__)), results=[], not_run=[],
        catalogue_records_built=False,
        scope='Core geometry, source interpretation, soundness, axiom audits and positive/negative regressions')
    def save():
        args.receipt.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
    try:
        env, info = preflight(args)
        receipt['preflight'] = dict(passed=True, **info)
        save()
        central = set(CENTRAL_AUDITS)
        if (HERE/'PackingCertificates/AxisFast.lean').is_file():
            central.add('PackingCertificates.AxisFast.check_sound')
        files = stages()
        for index, source in enumerate(files):
            if not source.is_file():
                raise FileNotFoundError('Required source missing: '+str(source))
            result = build_one(source, args, env, central)
            receipt['results'].append(result)
            save()
            print(json.dumps({k: result[k] for k in ('path', 'passed', 'exit_code', 'elapsed_seconds')}), flush=True)
            if not result['passed']:
                receipt['not_run'] = [relative(p) for p in files[index+1:]]
                break
        receipt['status'] = 'passed' if len(receipt['results']) == len(files) and all(r['passed'] for r in receipt['results']) else 'failed'
    except (OSError, ValueError, KeyError) as error:
        receipt['status'] = 'failed'
        receipt['error'] = str(error)
        receipt.setdefault('preflight', dict(passed=False))
    receipt['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    receipt['negative_checks_passed'] = sum(item['kernel_checked'] for r in receipt['results'] for item in r['negative_checks'])
    receipt['audited_theorem_count'] = len({name for r in receipt['results'] for name in r['audited_theorems']})
    save()
    print(json.dumps({'status': receipt['status'], 'stages_completed': len(receipt['results']),
        'negative_checks_passed': receipt['negative_checks_passed'],
        'audited_theorem_count': receipt['audited_theorem_count'], 'receipt': str(args.receipt)}))
    return 0 if receipt['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
