#!/usr/bin/env python3
"""Read-only mapping of reconstructible Linux .olean cache copies.

This program has no deletion operation. It checks exact raw/member/source
hashes and hardlink groups, then writes a reviewable dry-run report.
"""
import argparse
from collections import defaultdict
import ctypes
import hashlib
import json
import os
from pathlib import Path

import evidence_store as objects
import ingest_ci as checked


def allocated_bytes(path):
    if os.name!='nt':return path.stat().st_blocks*512
    function=ctypes.WinDLL('kernel32',use_last_error=True).GetCompressedFileSizeW
    function.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)]
    function.restype=ctypes.c_ulong
    high=ctypes.c_ulong();ctypes.set_last_error(0)
    name=str(path.resolve())
    if not name.startswith('\\\\?\\'):name='\\\\?\\'+name
    low=function(name,ctypes.byref(high))
    if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
    return (high.value<<32)|low


def allowed_objects(root,result,provenance):
    allowed=set()
    def add(row):
        if row.get('olean_path')and row.get('olean_sha256'):
            allowed.add((row['olean_path'],row['olean_sha256']))
    core=checked.read(root/'core-verification.json')
    for row in core['results']:add(row)
    generic=provenance.get('generic_extension_validation')
    if generic:
        for row in checked.read(root/generic['path'])['results']:
            add(row)
            for dependency in row.get('imported_dependencies',[]):add(dependency)
    for row in result['verified_records']:
        e=row['evidence'];add(e)
        for key in ['steps','dependencies','extension_dependencies']:
            for dependency in e.get(key,[]):
                add(dependency)
                for item in dependency.get('imported_dependencies',[]):add(item)
                for item in dependency.get('local_import_dependencies_before',[]):add(item)
        for path,digest in provenance['core_olean_hashes'].items():allowed.add((path,digest))
    return allowed


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cohorts',type=Path,nargs='+',required=True)
    p.add_argument('--candidate-root',type=Path,action='append',required=True)
    p.add_argument('--output',type=Path)
    p.add_argument('--compact-plan',type=Path,help='Write only a deduplicated review plan, limited to 1 MiB')
    p.add_argument('--small-plan-reserve-mb',type=int,default=512,
        help='Free-space reserve for the <=1 MiB diagnostic plan only; does not alter ingestion guards')
    args=p.parse_args();stores=[];origins=defaultdict(list);excluded=[]
    try:
        for cohort_path in args.cohorts:
            cohort_path=cohort_path.resolve();cohort=checked.read(cohort_path)
            for provenance in cohort['validated_shards']:
                if provenance.get('storage_mode')!='zip-streamed-objects':
                    raise ValueError('Every accepted checkpoint must first pass streamed replay')
                descriptor=provenance['object_store']
                if not descriptor['all_inventory_members_hashed']or not descriptor['raw_archive_fresh_final_hash_passed']:
                    raise ValueError('Incomplete recorded streamed hash audit')
                root=Path(provenance['validation_formal_root']).resolve()
                result_path=Path(provenance['validation_path'])
                if checked.sha(result_path)!=provenance['validation_sha256']:raise ValueError('Independent replay changed')
                result=checked.read(result_path);allowed=allowed_objects(root,result,provenance)
                primary=objects.EvidenceStore(descriptor['raw_archive'],root,provenance['github_archive_sha256'])
                stores.append(primary)
                if primary.nested_sha256!=provenance['evidence_zip_sha256']:
                    raise ValueError('Raw nested evidence differs from accepted provenance')
                donor=None
                supplement=provenance.get('exact_sha_core_supplement')
                if supplement:
                    path=Path(supplement['source_provenance_path'])
                    if checked.sha(path)!=supplement['source_provenance_sha256']:raise ValueError('Supplement provenance changed')
                    supplied=checked.read(path)
                    donor=objects.EvidenceStore(supplied['github_archive'],Path(supplied['formal_root']),supplied['github_archive_sha256'])
                    stores.append(donor)
                for relative,digest in sorted(allowed):
                    owner=primary if relative in primary.rows else donor
                    if owner is None or relative not in owner.rows or owner.rows[relative]['sha256']!=digest:
                        raise ValueError('Accepted object has no exact raw inventory member: '+relative)
                    source=relative[:-6]+'.lean'
                    if source not in owner.rows:raise ValueError('Raw object has no source member: '+relative)
                    origins[relative].append(dict(owner=owner,relative=relative,sha256=digest,
                        source_path=source,source_sha256=owner.rows[source]['sha256'],
                        run_id=provenance['run_id'],artifact_id=provenance['artifact_id']))
        roots=[]
        for value in args.candidate_root:
            value=value.absolute();objects.reject_reparse_ancestors(value)
            value=value.resolve()
            if not value.is_relative_to(Path.home()/'Documents/Codex'):
                raise ValueError('Candidate root is outside the explicit workspace')
            if value.exists():roots.append(value)
        # A root may overlap another root; each physical pathname appears once.
        candidates={}
        for root in roots:
            for path in root.rglob('*.olean'):
                objects.reject_reparse_ancestors(path)
                resolved=path.resolve()
                if not resolved.is_relative_to(root):raise ValueError('Cache path escapes explicit root')
                if path.is_file():candidates[resolved]=(root,path.relative_to(root).as_posix())
        hashes={};rows=[];raw_checked=set()
        for path,(root,relative)in sorted(candidates.items(),key=lambda item:str(item[0])):
            objects.reject_reparse_ancestors(path)
            st=path.stat();identity=(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
            key=identity[:2]
            if key not in hashes:hashes[key]=(identity,checked.sha(path),path)
            if hashes[key][0]!=identity:raise ValueError('Hardlinked object changed during cache audit')
            digest=hashes[key][1];match=None
            for origin in origins.get(relative,[]):
                if digest!=origin['sha256']:continue
                source=root/origin['source_path']
                objects.reject_reparse_ancestors(source)
                if source.is_file()and checked.sha(source)==origin['source_sha256']:
                    match=origin;break
            if match is None:
                excluded.append(dict(path=str(path),reason='not_an_exact_accepted_raw_object_and_source_pair'))
                continue
            owner=match['owner'];member=(str(owner.archive),relative)
            if member not in raw_checked:
                owner._read_digest(relative);raw_checked.add(member)
            rows.append(dict(path=str(path),candidate_root=str(root),relative_path=relative,
                sha256=digest,bytes=st.st_size,device=st.st_dev,file_id=st.st_ino,link_count=st.st_nlink,
                reported_compressed_bytes=allocated_bytes(path),raw_archive=str(owner.archive),
                raw_archive_sha256=owner.raw_sha256,nested_member=owner.nested_member,
                raw_member='formal/'+relative,source_path=str(root/match['source_path']),
                source_sha256=match['source_sha256'],accepted_run_id=match['run_id'],
                accepted_artifact_id=match['artifact_id']))
        groups=defaultdict(list)
        for row in rows:groups[(row['device'],row['file_id'])].append(row)
        recoverable=0;group_rows=[]
        for key,files in sorted(groups.items()):
            links={x['link_count']for x in files};sizes={x['reported_compressed_bytes']for x in files}
            if len(links)!=1 or len(sizes)!=1:raise ValueError('Hardlink metadata changed during dry run')
            complete=next(iter(links))==len(files)
            value=next(iter(sizes))if complete else 0
            recoverable+=value
            group_rows.append(dict(device=key[0],file_id=key[1],candidate_links=len(files),
                recorded_total_links=next(iter(links)),all_links_in_this_dry_run=complete,
                estimated_recoverable_bytes=value,paths=[x['path']for x in files]))
        # Freshly hash every unique physical candidate object before accepting
        # the dry-run mapping; a later cleanup must perform its own checks too.
        for identity,digest,path in hashes.values():
            st=path.stat()
            if (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)!=identity or checked.sha(path)!=digest:
                raise ValueError('Physical object changed before final dry-run hash pass')
        for owner in stores:owner.verify_final()
        result=dict(schema='read-only-raw-backed-object-cache-audit-v1',objects_deleted=False,
            roots=[str(r)for r in roots],eligible_cache_paths=rows,excluded_paths=excluded,
            hardlink_groups=group_rows,unique_eligible_file_ids=len(groups),
            eligible_path_count=len(rows),estimated_recoverable_bytes=recoverable,
            physical_candidates_freshly_hashed=len(hashes),raw_object_members_freshly_hashed=len(raw_checked),
            audit_script_sha256=checked.sha(Path(__file__)),
            boundary='Dry run only. Reported compressed sizes are filesystem estimates; actual freed space can differ. '
                'Only all-link groups are counted recoverable. Every raw archive, source, log, receipt, '
                'donor supplement and local Windows proof-library object remains untouched. '
                'Any later bounded removal must recheck exact resolved paths, identities and hashes.')
        checked._MIN_FREE_BYTES=512*1024**2;checked._BOUNDED_WRITES=True
        if args.output:checked.write(args.output.resolve(),result)
        plan_bytes=None
        if args.compact_plan:
            root_names=[str(r)for r in roots];raw=[];raw_indices={};files=[];file_indices={}
            for row in rows:
                key=(row['raw_archive'],row['raw_archive_sha256'],row['nested_member'])
                if key not in raw_indices:
                    raw_indices[key]=len(raw);raw.append(dict(path=key[0],sha256=key[1],nested_member=key[2]))
                file_indices[row['path']]=len(files)
                files.append(dict(root=root_names.index(row['candidate_root']),path=row['relative_path'],
                    sha256=row['sha256'],source_sha256=row['source_sha256'],bytes=row['bytes'],raw=raw_indices[key]))
            compact_groups=[dict(device=g['device'],file_id=g['file_id'],total_links=g['recorded_total_links'],
                all_links_in_plan=g['all_links_in_this_dry_run'],recoverable_bytes=g['estimated_recoverable_bytes'],
                files=[file_indices[path]for path in g['paths']])for g in group_rows]
            plan=dict(schema='compact-raw-backed-object-cache-dry-run-v1',objects_deleted=False,
                roots=root_names,raw_archives=raw,files=files,groups=compact_groups,
                estimated_recoverable_bytes=recoverable,excluded_count=len(excluded),
                physical_candidates_freshly_hashed=len(hashes),raw_members_freshly_hashed=len(raw_checked),
                audit_script_sha256=result['audit_script_sha256'],
                boundary=result['boundary'],source_member_rule='For each path X.olean, preserve X.lean; source SHA is recorded. Raw member is formal/X.olean.')
            payload=(json.dumps(plan,separators=(',',':'))+'\n').encode('utf8')
            if len(payload)>1024**2:raise ValueError('Diagnostic plan exceeds its explicit 1 MiB cap')
            if args.small_plan_reserve_mb<128:raise ValueError('Small diagnostic reserve must be at least 128 MiB')
            checked._MIN_FREE_BYTES=args.small_plan_reserve_mb*1024**2
            checked.metadata_bytes(args.compact_plan.resolve(),payload)
            plan_bytes=len(payload)
        print(__import__('json').dumps(dict(eligible_paths=len(rows),unique_files=len(groups),
            recoverable_mb=round(recoverable/1024**2,2),excluded=len(excluded),deleted=False,
            compact_plan_bytes=plan_bytes,per_root=[dict(root=str(root),paths=sum(r['candidate_root']==str(root)for r in rows))for root in roots])))
    finally:
        for owner in stores:owner.close()


if __name__=='__main__':main()
