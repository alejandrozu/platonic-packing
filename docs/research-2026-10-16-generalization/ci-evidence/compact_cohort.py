#!/usr/bin/env python3
"""Compact top-level cohort pointers; full pinned per-artifact proof rows stay."""
from pathlib import Path

EVIDENCE_FIELDS={'module','generated_source_path','generated_source_sha256','olean_path','olean_sha256',
    'log_path','log_sha256','receipt_path','receipt_sha256','plan_manifest_path','plan_manifest_sha256',
    'audited_theorems','axioms','source_path','source_sha256','proof_step_count'}
PROVENANCE_FIELDS={'run_id','run_head_sha','artifact_id','shard_index','validation_path',
    'validation_sha256','storage_mode'}
HEAVY_FIELDS={'fragmentation','imported_dependencies','steps','dependencies','extension_dependencies'}


def compact_rows(rows):
    result=[]
    for row in rows:
        value={k:v for k,v in row.items()if k not in HEAVY_FIELDS}
        provenance=row['artifact_provenance']
        evidence=row.get('evidence',{})
        value['evidence']={k:v for k,v in evidence.items()if k in EVIDENCE_FIELDS}
        value['evidence']['proof_step_count']=evidence.get('proof_step_count',len(evidence.get('steps',[])))
        value['artifact_provenance']={k:v for k,v in provenance.items()if k in PROVENANCE_FIELDS}
        value['full_evidence_ref']=dict(path=provenance['validation_path'],sha256=provenance['validation_sha256'],
            record_id=row['record_id'],run_id=provenance['run_id'],artifact_id=provenance['artifact_id'])
        result.append(value)
    return result


def identities(rows):
    return {r['record_id']:dict(source_sha=r.get('source_json_sha256',r.get('source_sha256')),
        evidence={k:v for k,v in r.get('evidence',{}).items()if k in EVIDENCE_FIELDS-{'proof_step_count'}},
        artifact_id=r['artifact_provenance']['artifact_id'],run_id=r['artifact_provenance']['run_id'],
        validation_sha256=r['artifact_provenance']['validation_sha256'])for r in rows}


def main():
    import argparse
    import hashlib
    import json
    import shutil
    import ingest_ci as checked
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cohort',type=Path,required=True)
    p.add_argument('--regression-report',type=Path)
    args=p.parse_args();path=args.cohort.resolve();data=path.read_bytes();before=checked.read(path)
    compact=compact_rows(before['verified_records'])
    if identities(compact)!=identities(before['verified_records']):raise ValueError('Compaction changed a record ID/proof hash')
    by_artifact={p['artifact_id']:p for p in before['validated_shards']};matched=0
    for artifact,provenance in by_artifact.items():
        independent=Path(provenance['validation_path'])
        if checked.sha(independent)!=provenance['validation_sha256']:raise ValueError('Full independent proof report changed')
        full=checked.read(independent);full_ids={r['record_id']:r for r in full['verified_records']}
        selected=[r for r in compact if r['artifact_provenance']['artifact_id']==artifact]
        if {r['record_id']for r in selected}!=set(full_ids):raise ValueError('Compaction dropped/added an independently verified record')
        for row in selected:
            expected=full_ids[row['record_id']].get('evidence',{})
            if any(expected.get(k)!=v for k,v in row['evidence'].items()if k!='proof_step_count'):
                raise ValueError('Compact pointer differs from its full source/object/log/receipt hashes')
            matched+=1
    if matched!=len(compact):raise ValueError('An accepted record lacks a pinned per-artifact report')
    old_sha=hashlib.sha256(data).hexdigest()
    history=path.parent/'report-history'/(path.stem+'-'+old_sha+'.json')
    checked._MIN_FREE_BYTES=512*1024**2;checked._BOUNDED_WRITES=True
    if shutil.disk_usage(path.parent).free<checked._MIN_FREE_BYTES+1024**2:
        raise ValueError('Compaction metadata requires the unchanged 512 MiB reserve')
    checked.link(path,history) # Preserve the original inode; never rewrite it.
    output=dict(before,verified_records=compact,record_evidence_storage='pinned-per-artifact-independent-validation-v1',
        compaction=dict(helper=Path(__file__).name,helper_sha256=checked.sha(Path(__file__)),
            original_top_sha256=old_sha,original_top_history=history.relative_to(path.parent).as_posix(),
            record_ids_and_proof_hashes_preserved=True,full_per_artifact_reports_unchanged=True))
    checked.write(path,output)
    report=dict(records=matched,ids_and_source_object_log_receipt_plan_hashes_match=True,
        full_reports_freshly_sha256_checked=len(by_artifact),before_bytes=len(data),after_bytes=path.stat().st_size,
        original_top_sha256=old_sha,compacted_top_sha256=checked.sha(path),original_history=str(history))
    if args.regression_report:checked.write(args.regression_report.resolve(),report)
    print(json.dumps(report))


if __name__=='__main__':main()
