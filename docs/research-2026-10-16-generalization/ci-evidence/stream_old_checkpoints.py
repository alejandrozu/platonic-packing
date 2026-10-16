#!/usr/bin/env python3
"""Replay already extracted checkpoints through ZIP objects; never delete files."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json

import evidence_store
import ingest_ci as checked


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-formal',type=Path,required=True)
    p.add_argument('--cohort',type=Path,required=True)
    p.add_argument('--core-supplement',type=Path)
    args=p.parse_args();base=args.base_formal.resolve();path=args.cohort.resolve()
    checked._MIN_FREE_BYTES=512*1024**2;checked._BOUNDED_WRITES=True
    cohort=checked.read(path);run=checked.read(path.parent/'run.json')
    if run['id']!=cohort['run_id']or run['head_sha']!=cohort['run_head_sha']:
        raise ValueError('Stored cohort/run provenance mismatch')
    artifacts={a['id']:a for a in checked.read(path.parent/'artifacts.json')}
    fresh=[];rows=[];reader_sha=checked.sha(Path(evidence_store.__file__))
    for old in cohort['validated_shards']:
        archive=path.parent/'artifacts'/str(old['artifact_id'])/'github-artifact.zip'
        root=Path(old['validation_formal_root']).resolve();artifact=artifacts[old['artifact_id']]
        if old['run_id']!=run['id']or old['run_head_sha']!=run['head_sha']:
            raise ValueError('Checkpoint belongs to another run/commit')
        published=artifact.get('digest')
        if published and published.startswith('sha256:')and published[7:]!=old['github_archive_sha256']:
            raise ValueError('Checkpoint raw digest disagrees with GitHub metadata')
        with evidence_store.EvidenceStore(archive,root,old['github_archive_sha256'])as objects:
            objects.validate(extract=False)
            with objects.activate()as view:
                supplement=checked.supplement_missing_probes(base,view,args.core_supplement)
                provenance,result,_=checked.validate_shard(base,view,artifact,run,objects.inventory_relative,supplement)
            provenance.update(github_archive_sha256=objects.raw_sha256,evidence_zip_sha256=objects.nested_sha256,
                evidence_inventory_sha256=checked.sha(root/objects.inventory_relative),
                storage_mode='zip-streamed-objects',object_store=objects.descriptor())
        if {r['record_id']for r in result['verified_records']}!={r['record_id']for r in cohort['verified_records']
                if r['artifact_provenance']['artifact_id']==old['artifact_id']}:
            raise ValueError('Streaming replay changed accepted checkpoint scope')
        checked.write(path.parent/'artifacts'/str(old['artifact_id'])/'validation-provenance.json',provenance)
        checked.write(root.parent/'validation-provenance.json',provenance)
        fresh.append(provenance)
        rows.extend(dict(r,artifact_provenance=provenance)for r in result['verified_records'])
        print(json.dumps(dict(artifact=old['artifact_id'],verified=len(result['verified_records']),streamed=True)),flush=True)
    if checked.sha(Path(evidence_store.__file__))!=reader_sha:
        raise ValueError('Operator reader changed during conversion')
    if len({r['record_id']for r in rows})!=len(rows):raise ValueError('Duplicate checkpoint record')
    summary=checked.load_validator(base,base)
    compact=checked.compact_rows(rows)
    from compact_cohort import identities
    if identities(compact)!=identities(rows):raise ValueError('Compaction changed checkpoint proof identities')
    history=path.parent/'report-history'/(path.stem+'-'+checked.sha(path)+'.json')
    checked.link(path,history)
    cohort.update(validated_shards=fresh,verified_records=compact,verified_totals=summary.totals(rows),
        record_evidence_storage='pinned-per-artifact-independent-validation-v1',
        prior_combined_strict_replay=cohort.get('prior_combined_strict_replay')or cohort.get('combined_strict_replay'),
        combined_strict_replay=None,combined_replay_omitted_for_streamed_objects=True,
        operator_reader_sha256=reader_sha,stream_conversion=dict(path=Path(__file__).name,
            sha256=checked.sha(Path(__file__)),checked_at_utc=datetime.now(timezone.utc).isoformat(),
            raw_archives_changed=False,objects_deleted=False))
    checked.write(path,cohort)
    print(json.dumps(dict(verified=len(rows),cohort=str(path),objects_deleted=False)))


if __name__=='__main__':main()
