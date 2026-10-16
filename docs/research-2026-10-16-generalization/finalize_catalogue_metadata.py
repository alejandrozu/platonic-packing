"""Finalize count macros only after portable, environment-scoped proof gates."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True

HERE = Path(__file__).resolve().parent
FORMAL = HERE/'formal'
sys.path.insert(0,str(FORMAL))
import evidence_bundle as evidence


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def cohort(name):
    return next((p for p in (FORMAL/'ci-evidence'/name,HERE/'ci-evidence'/name)
                 if (p/'verified-catalogue.json').is_file()),FORMAL/'ci-evidence'/name)


def group_totals(rows,key):
    groups={}
    for row in rows:groups.setdefault(str(row[key]),[]).append(row)
    result={}
    for name,items in sorted(groups.items()):
        totals=dict(records=len(items),pieces=sum(r['n']for r in items),
            unordered_pairs=sum(r.get('unordered_pairs',r['n']*(r['n']-1)//2)for r in items))
        for field in ('piece_vertices','container_vertices','vertex_wall_tests','vertex_membership_tests'):
            if all(field in r for r in items):totals[field]=sum(r[field]for r in items)
        totals['n_values']=sorted({r['n']for r in items});result[name]=totals
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rational-only',action='store_true',
                   help='Explicitly finalize only402 records; set additional algebraic count macros to zero')
    p.add_argument('--check-only',action='store_true')
    args=p.parse_args()
    witness=read(FORMAL/'catalogue/rational-witnesses-manifest.json')
    targets={Path(r['path']).stem for r in witness['files']}
    report,checked=evidence.verify_portable_cohort(cohort('published-402'),expected_count=402,
        expected_ids=targets,require_complete=True)
    evidence.require_rational_402(report,witness)
    rows=report['verified_records']
    by_dim=group_totals(rows,'dimension')
    values=dict(leanRecords=402,leanCubeRecords=by_dim['3']['records'],
        leanNDRecords=sum(by_dim[str(d)]['records']for d in (4,5,6)),
        leanFourDRecords=by_dim['4']['records'],leanFiveDRecords=by_dim['5']['records'],
        leanSixDRecords=by_dim['6']['records'],leanPieces=10796,leanPairs=235462)
    algebraic=[];cohorts=[dict(directory='ci-evidence/published-402',**checked)]
    portable_reports=[('published-402',report,checked)]
    if not args.rational_only:
        for name,count in [('published-85',85),('published-45',45)]:
            expected_ids=evidence.pilot_target_ids(FORMAL,name)
            extra,validation=evidence.verify_portable_cohort(cohort(name),expected_count=count,
                expected_ids=expected_ids,require_complete=True)
            algebraic.extend(extra['verified_records']);cohorts.append(dict(directory='ci-evidence/'+name,**validation))
            portable_reports.append((name,extra,validation))
        ids=[r['record_id']for r in algebraic]
        families={(r['dimension'],r['piece'],r['container'])for r in algebraic}
        if len(ids)!=len(set(ids)) or len(ids)!=130 or len(families)!=130 or set(ids)&targets:
            raise ValueError('Additional pilot cohort must comprise130 distinct additional records/families')
        evidence.require_family_union(rows,algebraic)
        values.update(leanAlgebraicRecords=130,leanAlgebraicFamilies=130)
    else:values.update(leanAlgebraicRecords=0,leanAlgebraicFamilies=0)
    text=(HERE/'manuscript.tex').read_text(encoding='utf8')
    for name,value in values.items():
        pattern=r'\\newcommand\{\\'+name+r'\}\{[^}]*\}'
        text,n=re.subn(pattern,lambda _: '\\newcommand{\\'+name+'}{'+format(value,',')+'}',text)
        if n!=1:raise ValueError('Missing/duplicate count macro '+name)
    if 'FINAL_'in text:raise ValueError('Unresolved manuscript placeholder')
    result=dict(status='passed',values=values,cohorts=cohorts)
    if args.check_only:print(json.dumps(result,indent=2));return
    environment_manifest=dict(schema='environment-scoped-lean-module-manifest-v1',
        cohort='ci-evidence/published-402',summary_sha256=checked['summary_sha256'],
        environments=[dict(environment_id=e['environment_id'],formal_prefix=e['formal_prefix'],
            records=[dict(record_id=r['record_id'],module=r['evidence']['module'],
                path=r['evidence']['generated_source_path'],
                source_sha256=r['evidence']['generated_source_sha256'],
                complete_validation_member=r['evidence']['complete_validation_member'])
                for r in rows if r['evidence']['environment_id']==e['environment_id']])
            for e in report['environments']],
        additional_cohorts=[dict(cohort='ci-evidence/'+name,summary_sha256=validation['summary_sha256'],
            environments=[dict(environment_id=env['environment_id'],formal_prefix=env['formal_prefix'],
                records=[dict(record_id=r['record_id'],module=r['evidence']['module'],
                    path=r['evidence']['generated_source_path'],source_sha256=r['evidence']['generated_source_sha256'])
                    for r in extra['verified_records']if r['evidence']['environment_id']==env['environment_id']])
                for env in extra['environments']])for name,extra,validation in portable_reports[1:]],
        reproduction='Extract and rebuild each named environment separately; never flatten source/object namespaces.')
    summary=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),schema='portable-paper-verification-v2',
        catalogue_receipt='ci-evidence/published-402/verified-catalogue.json',
        catalogue_receipt_sha256=checked['summary_sha256'],verified_totals=report['verified_totals'],
        verified_by_dimension=by_dim,archive_records_formally_imported=402,rational_export_targets=402,
        additional_algebraic_records=len(algebraic),additional_algebraic_families=values['leanAlgebraicFamilies'],
        verified_problem_families=10+values['leanAlgebraicFamilies'],
        portable_cohorts=cohorts,axioms_allowed=sorted(evidence.ALLOWED_AXIOMS),additional_axioms_found=[],
        semantics='Real convex hulls under source-linked exact proper rigid placements; complete containment and every unordered pair strictly separated.',
        trust_boundary=report['trust_boundary'],optimality_proved=False,entire_live_catalogue_proved=False)
    core=read(FORMAL/'core-verification.json')
    summary.update(core_status=core['status'],core_receipt='core-verification.json',
        core_audited_theorems=core['audited_theorem_count'],negative_kernel_checks=core['negative_checks_passed'],
        compiler=core['preflight']['lean_version_output'],mathlib_commit=core['expected_mathlib_revision'],
        generic_method_receipts=[dict(path=name,sha256=evidence.sha(FORMAL/name),
            stages=len(read(FORMAL/name)['results']),
            audited_declarations=sum(len(r['audited_theorems'])for r in read(FORMAL/name)['results']))
            for name in ('extension-verification-v2.json','extension-identity-verification.json',
                         'extension-clearance-support-verification.json',
                         'extension-materials-verification.json',
                         'catalogue/nd-reference-edge-lean-verification.json')])
    compatibility=dict(schema='portable-catalogue-compatibility-summary-v1',complete_402=True,
        source_report='ci-evidence/published-402/verified-catalogue.json',source_report_sha256=checked['summary_sha256'],
        freeze_git_sha=evidence.FREEZE,verified_record_ids=sorted(targets),
        verified_totals=report['verified_totals'],verified_by_dimension=by_dim,
        verified_by_family=group_totals(rows,'problem_family'),
        additional_algebraic_records=len(algebraic),additional_algebraic_families=values['leanAlgebraicFamilies'],
        verified_problem_families=10+values['leanAlgebraicFamilies'],
        additional_algebraic_by_dimension=group_totals(algebraic,'dimension')if algebraic else {},
        portable_cohorts=cohorts,
        evidence_layout='Every proof path is relative to its own archived environment formal root; source_report is authoritative.')
    # All gates and metadata construction finish before any final output changes.
    # No prose or README editing is performed by this finalizer.
    (HERE/'manuscript.tex').write_text(text,encoding='utf8',newline='\n')
    save(FORMAL/'catalogue/verified-module-manifest.json',environment_manifest)
    save(FORMAL/'verification.json',summary)
    save(FORMAL/'catalogue/verified-catalogue.json',compatibility)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

