#!/usr/bin/env python3
"""Exercise full assembled/chunked Data on the exact native c5 packing.

This isolated regression forces the actual five-vertex witness through the
same lazy/grouped rational storage used for larger ND records. It does not
alter the frozen witness, geometry, source scale or production shard plan.
"""
from pathlib import Path
import hashlib
import json
import nd_array_data
import nd_split_data
import run_verified_nd as native

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parents[1]
NAMESPACE = 'PackingCertificates.Algebraic.Trials.NDArrayDataRegression'
OUT = FORMAL / 'PackingCertificates/Algebraic/Trials/NDArrayDataRegression'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    registry = json.loads((HERE/'generated-nd-pilots-registry.json').read_text(encoding='utf8'))
    row = next(r for r in registry['records'] if r['record_id'] == 'c5inc5_n02')
    inputs = native.source_binding(row)
    original = (FORMAL/row['generated_module']).read_text(encoding='utf8')
    prefix = original.split('theorem source_checked :', 1)[0]
    prefix = prefix.replace('PackingCertificates.Algebraic.Generated.ND.Records.c5inc5_n02', NAMESPACE)
    prefix = prefix.replace('def certificate :', 'noncomputable def certificate :')
    proposal = json.loads((FORMAL/row['proposal_path']).read_text(encoding='utf8'))
    prefix, audits = nd_array_data.rewrite(prefix, proposal, [], 8,
        fast_rationals=True, lazy_chunks=True)
    prefix, auxiliary = nd_split_data.split(prefix, NAMESPACE, OUT, FORMAL)
    prefix = prefix.replace('namespace '+NAMESPACE, 'namespace '+NAMESPACE+'\nopen PackingCertificates.Algebraic.Generated.ND', 1)
    prefix += '\ntheorem regression_checked : certificate.check = true := by decide +kernel\n'
    prefix += '\ntheorem regression_valid : certificate.Valid := certificate.check_sound regression_checked\n'
    names = ['native_scale_checked', 'native_mu_binding', 'native_mu_literal',
        *audits, 'regression_checked', 'regression_valid']
    prefix += '\n' + '\n'.join('#print axioms '+name for name in names)
    prefix += '\nend '+NAMESPACE+'\n'
    path = OUT/'Data.lean'
    path.write_bytes(prefix.replace('\n', '\r\n').encode('utf8'))
    inputs += [dict(path=p.relative_to(FORMAL).as_posix(), sha256=digest(p))
        for p in [Path(__file__), HERE/'nd_array_data.py', HERE/'nd_split_data.py']]
    modules = [item['path'] for item in auxiliary] + [path.relative_to(FORMAL).as_posix()]
    report = dict(schema='assembled-nd-array-regression-plan-v1',
        status='native_source_bound_not_yet_lean_verified', record_id=row['record_id'],
        numeric_witness_unchanged=True, canonical_geometry_unchanged=True,
        native_source_binding=inputs, modules=modules,
        module_sha256={name:digest(FORMAL/name) for name in modules},
        expected_final_audits=[NAMESPACE+'.'+name for name in names])
    (HERE/'nd-array-data-regression-plan.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(modules=len(modules), record_id=row['record_id'],
        source_bound=True, final_module=modules[-1])))


if __name__ == '__main__':
    main()
