"""Bounded regression checks for archive safety and the exact publication gate."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.dont_write_bytecode=True

sys.path.insert(0,str(Path(__file__).resolve().parent/'formal'))
import evidence_bundle as evidence
import validate_package as package_validator

_raw_spec=importlib.util.spec_from_file_location('_test_raw_metadata',
    Path(__file__).resolve().parent/'ci-evidence/verify_raw_github_metadata.py')
raw_metadata=importlib.util.module_from_spec(_raw_spec);_raw_spec.loader.exec_module(raw_metadata)


class ArchiveSafety(unittest.TestCase):
    def bundle(self,root,items,corrupt=False):
        archive=root/'proof-sources-and-logs.zip';rows=[]
        with zipfile.ZipFile(archive,'w')as output:
            for name,data in items:
                output.writestr(name,data)
                rows.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        if corrupt and rows:rows[0]['sha256']='0'*64
        (root/'proof-sources-and-logs-manifest.json').write_text(json.dumps(dict(
            schema='lean-catalogue-source-log-bundle-v1',archive=archive.name,
            archive_sha256=evidence.sha(archive),files=rows)),encoding='utf8')

    def portable_bundle(self,root,streamed=False):
        """Small structural evidence fixture; no kernel proof is claimed here."""
        digest=lambda data:hashlib.sha256(data).hexdigest()
        encoded=lambda value:json.dumps(value).encode('utf8')
        ident='run-1-artifact-2';prefix='environments/'+ident+'/formal/'
        source=b'theorem valid : True := by trivial\n'
        log=b"'Packing.valid' does not depend on any axioms\n"
        stage=dict(path='A.lean',source_sha256=digest(source),log='A.log',log_sha256=digest(log),
            olean_path='A.olean',olean_sha256=digest(b'objects live in raw archives'),
            passed=True,exit_code=0,audited_theorems={'Packing.valid':[]},imported_dependencies=[])
        receipt=encoded(dict(stages=[stage]));plan=b'{}'
        compact=dict(module='Packing',generated_source_path='A.lean',generated_source_sha256=digest(source),
            olean_path=stage['olean_path'],olean_sha256=stage['olean_sha256'],log_path='A.log',log_sha256=digest(log),
            receipt_path='receipt.json',receipt_sha256=digest(receipt),plan_manifest_path='plan.json',
            plan_manifest_sha256=digest(plan),audited_theorems=stage['audited_theorems'],axioms=[])
        full=dict(record_id='r',dimension=3,n=2,evidence=dict(compact,steps=[stage]))
        independent=encoded(dict(frozen_catalogue_commit=evidence.FREEZE,verified_records=[full],
            receipt_inputs=[dict(path='receipt.json',sha256=digest(receipt))]))
        self.bundle(root,[(prefix+'A.lean',source),(prefix+'A.log',log),
            (prefix+'core-verification.json',encoded(dict(status='passed',results=[stage]))),
            (prefix+'receipt.json',receipt),(prefix+'plan.json',plan),
            ('environments/'+ident+'/independent-validation.json',independent)])
        archive='ci-evidence/run-1/artifacts/2/github-artifact.zip';raw_sha=digest(b'raw artifact')
        raw=dict(schema='preserved-lean-artifact-index-v1',artifacts=[dict(run_id=1,artifact_id=2,
            head_sha='a'*40,path=archive,sha256=raw_sha)])
        (root/'raw-artifacts.json').write_text(json.dumps(raw),encoding='utf8')
        environment=dict(environment_id=ident,formal_prefix=prefix.rstrip('/'),run_id=1,artifact_id=2,
            run_head_sha='a'*40,github_archive_path=archive,github_archive_sha256=raw_sha,
            evidence_zip_path='ci-evidence/run-1/artifacts/2/evidence.zip',evidence_zip_sha256=digest(b'nested ZIP'))
        if streamed:
            environment.update(storage_mode='zip-streamed-objects',evidence_zip_path=None,object_store=dict(
                schema='zip-streamed-proof-objects-v1',raw_artifact_index_key=ident,raw_archive_sha256=raw_sha,
                nested_member='evidence.zip',nested_sha256=environment['evidence_zip_sha256'],
                inventory_member='formal/catalogue/evidence-inventory.json',inventory_sha256=digest(b'inventory'),
                objects_not_extracted=True,all_inventory_members_hashed=True,
                raw_archive_fresh_final_hash_passed=True,primary_object_count=1))
        compact.update(environment_id=ident,complete_validation_member='environments/'+ident+'/independent-validation.json')
        report=dict(schema='portable-source-bound-lean-catalogue-v1',cohort_id='test-fixture',
            frozen_catalogue_commit=evidence.FREEZE,verified_records=[dict(record_id='r',dimension=3,n=2,evidence=compact)],
            verified_totals=dict(records=1,pieces=2,unordered_pairs=1),environments=[environment],
            proof_source_bundle='proof-sources-and-logs.zip',proof_source_manifest='proof-sources-and-logs-manifest.json',
            proof_source_bundle_sha256=evidence.sha(root/'proof-sources-and-logs.zip'),
            proof_source_manifest_sha256=evidence.sha(root/'proof-sources-and-logs-manifest.json'),
            raw_artifact_index='raw-artifacts.json',raw_artifact_index_sha256=evidence.sha(root/'raw-artifacts.json'))
        (root/'verified-catalogue.json').write_text(json.dumps(report),encoding='utf8')
        return report

    def test_roundtrip_preserves_separate_formal_roots(self):
        with tempfile.TemporaryDirectory()as td:
            root=Path(td);self.bundle(root,[('environments/a/formal/A.lean',b'first'),('environments/b/formal/A.lean',b'second')])
            with evidence.SourceBundle(root)as archive:
                archive.extract(root/'out','a')
                self.assertEqual((root/'out/environments/a/formal/A.lean').read_bytes(),b'first')
                self.assertFalse((root/'out/environments/b').exists())
                archive.extract(root/'out')
                self.assertEqual((root/'out/environments/b/formal/A.lean').read_bytes(),b'second')
                (root/'out/environments/a/formal/A.lean').write_bytes(b'changed')
                with self.assertRaises(ValueError):archive.extract(root/'out')

    def test_rejects_traversal_compiled_objects_and_collisions(self):
        for names in [('../escape',),('/absolute',),('a\\b',),('C:/evil',),('a/./b',),
                      ('a/../b',),('a/.lake/file',),('a/A.olean',),('a/CON.txt',),('a/b.',),
                      ('a/A.lean','a/a.lean'),('a/A.lean','a/A.lean')]:
            with self.subTest(names=names),tempfile.TemporaryDirectory()as td:
                root=Path(td);self.bundle(root,[(n,b'x')for n in names])
                with self.assertRaises(ValueError):evidence.SourceBundle(root)

    def test_rejects_corrupt_manifest_hash(self):
        with tempfile.TemporaryDirectory()as td:
            root=Path(td);self.bundle(root,[('a.lean',b'actual')],corrupt=True)
            with self.assertRaises(ValueError):evidence.SourceBundle(root)

    def test_embedded_witness_manifest_is_explicit_and_consistent(self):
        with tempfile.TemporaryDirectory()as td:
            root=Path(td);self.bundle(root,[('witnesses/a.json',b'{}')])
            mp=root/'proof-sources-and-logs-manifest.json';manifest=json.loads(mp.read_text());manifest['freeze_git_sha']=evidence.FREEZE
            archive=root/'proof-sources-and-logs.zip'
            with zipfile.ZipFile(archive,'a')as output:
                output.writestr('witness-manifest.json',json.dumps(dict(files=manifest['files'],freeze_git_sha=evidence.FREEZE)))
            manifest['archive_sha256']=evidence.sha(archive);mp.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):evidence.SourceBundle(root)
            with evidence.SourceBundle(root,internal_manifest='witness-manifest.json')as bundle:
                self.assertEqual(len(bundle.files),1)
            with zipfile.ZipFile(archive,'w')as output:
                output.writestr('witnesses/a.json',b'{}');output.writestr('witness-manifest.json',json.dumps(dict(files=[],freeze_git_sha=evidence.FREEZE)))
            manifest['archive_sha256']=evidence.sha(archive);mp.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):evidence.SourceBundle(root,internal_manifest='witness-manifest.json')

    def test_rejects_zip_symlink(self):
        with tempfile.TemporaryDirectory()as td:
            root=Path(td);self.bundle(root,[('a.lean',b'target')]);archive=root/'proof-sources-and-logs.zip'
            info=zipfile.ZipInfo('a.lean');info.create_system=3;info.external_attr=(stat.S_IFLNK|0o777)<<16
            with zipfile.ZipFile(archive,'w')as output:output.writestr(info,b'target')
            manifest=root/'proof-sources-and-logs-manifest.json';x=json.loads(manifest.read_text());x['archive_sha256']=evidence.sha(archive)
            manifest.write_text(json.dumps(x))
            with self.assertRaises(ValueError):evidence.SourceBundle(root)

    def test_exact_402_gate(self):
        manifest=dict(files=[dict(path='witnesses/r'+str(i)+'.json')for i in range(402)])
        report=dict(verified_records=[dict(record_id='r'+str(i))for i in range(402)],
                    verified_totals=dict(records=402,pieces=10796,unordered_pairs=235462),
                    missing_record_ids=[],complete_402=True)
        self.assertEqual(len(evidence.require_rational_402(report,manifest)),402)
        report['verified_records'][-1]['record_id']='r0'
        with self.assertRaises(ValueError):evidence.require_rational_402(report,manifest)
        report['verified_records']=report['verified_records'][:57];report['verified_totals']['records']=57
        with self.assertRaises(ValueError):evidence.require_rational_402(report,manifest)

    def test_exact_disjoint_140_family_union(self):
        rational=[dict(dimension=3,piece='r'+str(i),container='c')for i in range(10)]
        additional=[dict(dimension=4,piece='a'+str(i),container='c')for i in range(130)]
        self.assertEqual(evidence.require_family_union(rational,additional),140)
        additional[-1]=dict(rational[0])
        with self.assertRaises(ValueError):evidence.require_family_union(rational,additional)
        with self.assertRaises(ValueError):evidence.require_family_union(rational,additional[:-1])

    def test_portable_legacy_and_streamed_environments(self):
        for streamed in (False,True):
            with self.subTest(streamed=streamed),tempfile.TemporaryDirectory()as td:
                root=Path(td);self.portable_bundle(root,streamed)
                _,result=evidence.verify_portable_cohort(root,expected_count=1)
                self.assertEqual(result['records'],1)

    def test_portable_rejects_corrupted_streaming_metadata(self):
        cases=('missing-initial-check','missing-final-check','integer-final-check','not-virtual',
            'wrong-index-key','wrong-object-raw-sha','wrong-environment-raw-sha','wrong-nested-sha',
            'wrong-commit','wrong-locator','missing-index-row','duplicate-index-row','changed-index-sha')
        for case in cases:
            with self.subTest(case=case),tempfile.TemporaryDirectory()as td:
                root=Path(td);report=self.portable_bundle(root,True)
                environment=report['environments'][0];store=environment['object_store']
                raw=json.loads((root/'raw-artifacts.json').read_text())
                if case=='missing-initial-check':store.pop('all_inventory_members_hashed')
                elif case=='missing-final-check':store.pop('raw_archive_fresh_final_hash_passed')
                elif case=='integer-final-check':store['raw_archive_fresh_final_hash_passed']=1
                elif case=='not-virtual':store['objects_not_extracted']=False
                elif case=='wrong-index-key':store['raw_artifact_index_key']='run-1-artifact-999'
                elif case=='wrong-object-raw-sha':store['raw_archive_sha256']='0'*64
                elif case=='wrong-environment-raw-sha':environment['github_archive_sha256']='0'*64
                elif case=='wrong-nested-sha':store['nested_sha256']='0'*64
                elif case=='wrong-commit':environment['run_head_sha']='b'*40
                elif case=='wrong-locator':environment['github_archive_path']='different.zip'
                elif case=='missing-index-row':raw['artifacts']=[]
                elif case=='duplicate-index-row':raw['artifacts'].append(dict(raw['artifacts'][0]))
                elif case=='changed-index-sha':raw['artifacts'][0]['sha256']='0'*64
                (root/'raw-artifacts.json').write_text(json.dumps(raw),encoding='utf8')
                # Keep the index file hash valid: these cases test semantic
                # provenance linkage, rather than merely a corrupt file digest.
                report['raw_artifact_index_sha256']=evidence.sha(root/'raw-artifacts.json')
                (root/'verified-catalogue.json').write_text(json.dumps(report),encoding='utf8')
                with self.assertRaises(ValueError):evidence.verify_portable_cohort(root,expected_count=1)

    def test_portable_rejects_compact_object_identity_mismatch(self):
        for key,value in [('olean_path','Other.olean'),('olean_sha256','0'*64),('olean_path',None)]:
            with self.subTest(key=key,value=value),tempfile.TemporaryDirectory()as td:
                root=Path(td);report=self.portable_bundle(root)
                if value is None:report['verified_records'][0]['evidence'].pop(key)
                else:report['verified_records'][0]['evidence'][key]=value
                (root/'verified-catalogue.json').write_text(json.dumps(report),encoding='utf8')
                with self.assertRaises(ValueError):evidence.verify_portable_cohort(root,expected_count=1)

    def test_approved_environment_helper_versions_are_archive_bound(self):
        with tempfile.TemporaryDirectory()as td:
            root=Path(td);prefix='environments/run-1-artifact-2/formal'
            helper='catalogue/algebraic/helper.py';data=b'# retained source, never executed\n'
            helper_sha=hashlib.sha256(data).hexdigest()
            manifest=json.dumps(dict(schema='algebraic-pilot-assets-v1',frozen_commit=evidence.FREEZE,
                record_count=85,files=[dict(path=helper,sha256=helper_sha,bytes=len(data))])).encode('utf8')
            member=prefix+'/catalogue/algebraic/ci-pilot-assets.json';digest=hashlib.sha256(manifest).hexdigest()
            self.bundle(root,[(member,manifest),(prefix+'/'+helper,data)])
            valid=dict(approved_publication_manifest_member=member,approved_publication_manifest_sha256=digest,
                approved_helper_versions=[dict(path=helper,sha256=helper_sha)])
            validation=dict(publication_manifest_sha256=digest,expected_record_count=85,cohort_id='algebraic-3d85')
            with evidence.SourceBundle(root)as bundle:
                evidence.check_approved_publication_version(valid,prefix,bundle,validation)
                evidence.check_approved_publication_version({},prefix,bundle,{})
                for case in ('missing-field','other-environment','wrong-manifest-hash','missing-helper','changed-helper','wrong-replay-hash'):
                    with self.subTest(case=case):
                        row=copy.deepcopy(valid);replay=dict(validation)
                        if case=='missing-field':row.pop('approved_helper_versions')
                        elif case=='other-environment':row['approved_publication_manifest_member']=member.replace('run-1-artifact-2','other')
                        elif case=='wrong-manifest-hash':row['approved_publication_manifest_sha256']='0'*64
                        elif case=='missing-helper':row['approved_helper_versions']=[]
                        elif case=='changed-helper':row['approved_helper_versions'][0]['sha256']='0'*64
                        elif case=='wrong-replay-hash':replay['publication_manifest_sha256']='0'*64
                        with self.assertRaises(ValueError):evidence.check_approved_publication_version(row,prefix,bundle,replay)

    def test_real_reference_edge_receipt_and_compressed_native_inputs(self):
        formal=Path(__file__).resolve().parent/'formal'
        with evidence.SourceBundle(formal/'catalogue/algebraic',
                manifest_filename='pilot-inputs-and-proposals-manifest.json',expected_schema='bounded-algebraic-pilot-inputs-v1')as inputs:
            result=package_validator.validate_reference_edges(formal,evidence,inputs)
        self.assertEqual((result['lean_stages'],result['lean_audited_declarations']),(1,159))
        self.assertEqual((result['selected_reference_edges'],result['native_positive_edge_ratios'],result['python_listed_edges_checked']),(12,45,2490))
        self.assertIs(result['python_audit_is_lean_proof'],False)

    def test_reference_edge_report_rejects_false_claims_or_source_hashes(self):
        formal=Path(__file__).resolve().parent/'formal';original=package_validator.read
        for case in ('python-labelled-lean','missing-ratio','changed-generator'):
            with self.subTest(case=case):
                def altered(path):
                    value=original(path)
                    if case=='python-labelled-lean'and Path(path).name=='nd-edge-scale-audit.json':value['lean_verification']=True
                    if case=='missing-ratio'and Path(path).name=='nd-reference-edge-lean-binding.json':value['native_ratio_records']=44
                    if case=='changed-generator'and Path(path).name=='nd-reference-edge-lean-binding.json':value['generator_sha256']='0'*64
                    return value
                with patch.object(package_validator,'read',side_effect=altered):
                    with self.assertRaises(ValueError):package_validator.validate_reference_edges(formal,evidence)

    def final_metadata_fixture(self,rational_only=False):
        # Structural-only rows exercise metadata sealing, not certificate proofs.
        names=['published-402']if rational_only else list(evidence.COHORTS)
        current={};portable=[];entries={}
        for name in names:
            cohort,count=evidence.COHORTS[name];ident=name+'-environment';prefix='environments/'+ident+'/formal'
            records=[];module_rows=[]
            for i in range(count):
                rid=name+'-'+str(i);source_hash=hashlib.sha256(rid.encode()).hexdigest()
                proof=dict(environment_id=ident,module='Numeric.N'+str(i),generated_source_path='Numeric/N'+str(i)+'.lean',
                    generated_source_sha256=source_hash,complete_validation_member='environments/'+ident+'/independent-validation.json')
                records.append(dict(record_id=rid,n=2,dimension=4 if name=='published-45'else 3,
                    piece=('r'+str(i%10))if name=='published-402'else name+'-'+str(i),container='c',evidence=proof))
                module_rows.append(dict(record_id=rid,module=proof['module'],path=proof['generated_source_path'],source_sha256=source_hash))
            report=dict(verified_records=records,verified_totals=dict(records=count,pieces=2*count,unordered_pairs=count),
                environments=[dict(environment_id=ident,formal_prefix=prefix)])
            checked=dict(cohort_id=cohort,records=count,environments=1,summary_sha256=hashlib.sha256(name.encode()).hexdigest())
            current[name]=(report,checked);portable.append(dict(directory='ci-evidence/'+name,**checked))
            entries[name]=dict(cohort='ci-evidence/'+name,summary_sha256=checked['summary_sha256'],
                environments=[dict(environment_id=ident,formal_prefix=prefix,records=module_rows)])
        rational,checked=current['published-402'];extra=0 if rational_only else 130
        metadata=dict(schema='portable-paper-verification-v2',portable_cohorts=portable,
            catalogue_receipt='ci-evidence/published-402/verified-catalogue.json',catalogue_receipt_sha256=checked['summary_sha256'],
            verified_totals=rational['verified_totals'],archive_records_formally_imported=402,
            additional_algebraic_records=extra,additional_algebraic_families=extra,verified_problem_families=10+extra)
        modules=dict(entries['published-402'],schema='environment-scoped-lean-module-manifest-v1',
            additional_cohorts=[entries[n]for n in names if n!='published-402'])
        return metadata,modules,current

    def test_final_metadata_accepts_full_and_explicit_rational_only(self):
        for rational_only in (False,True):
            with self.subTest(rational_only=rational_only):
                evidence.check_final_cohort_metadata(*self.final_metadata_fixture(rational_only))

    def test_final_metadata_rejects_stale_additional_sha_counts_and_proof_pointers(self):
        for case in ('portable-extra-sha','portable-extra-count','module-extra-sha','module-proof-path',
                     'missing-extra-cohort','wrong-rational-count','wrong-rational-sha','missing-extra-record'):
            with self.subTest(case=case):
                metadata,modules,current=self.final_metadata_fixture()
                if case=='portable-extra-sha':metadata['portable_cohorts'][1]['summary_sha256']='0'*64
                elif case=='portable-extra-count':metadata['portable_cohorts'][2]['records']=44
                elif case=='module-extra-sha':modules['additional_cohorts'][0]['summary_sha256']='0'*64
                elif case=='module-proof-path':modules['additional_cohorts'][1]['environments'][0]['records'][0]['path']='Stale.lean'
                elif case=='missing-extra-cohort':modules['additional_cohorts'].pop()
                elif case=='wrong-rational-count':metadata['archive_records_formally_imported']=401
                elif case=='wrong-rational-sha':metadata['catalogue_receipt_sha256']='0'*64
                elif case=='missing-extra-record':modules['additional_cohorts'][0]['environments'][0]['records'].pop()
                with self.assertRaises(ValueError):evidence.check_final_cohort_metadata(metadata,modules,current)


class RawGitHubMetadata(unittest.TestCase):
    """Synthetic API/schema fixtures; these never assert a kernel proof."""
    def fixture(self,paper,remote=False):
        ci=paper/'ci-evidence';ci.mkdir();dirs={};rows={};answers={}
        save=lambda path,value:path.write_text(json.dumps(value),encoding='utf8')
        root=Path(__file__).resolve().parent
        operators={'aggregate_publication.py','ingest_ci.py','ingest_core.py','ingest_algebraic.py',
            'validate_algebraic.py','evidence_store.py','compact_cohort.py','publish_402.py','publish_algebraic.py',
            'verify_raw_github_metadata.py'}
        for name in operators:(ci/name).write_bytes((root/'ci-evidence'/name).read_bytes())
        repository='alejandrozu/platonic-packing';repository_info=dict(id=42,full_name=repository)
        for i in range(1,34):
            data=('synthetic archive '+str(i)).encode();run=100+i//12;aid=1000+i
            row=dict(run_id=run,artifact_id=aid,head_sha='a'*40,bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),path=f'ci-evidence/raw/{aid}.zip',
                artifact_name='synthetic-'+str(aid),proposed_release_asset_name=f'run-{run}-{aid}.zip',
                permanent_download_url=f'https://github.com/{repository}/releases/download/test/{aid}.zip')
            row['github_published_digest']='sha256:'+row['sha256'];rows[i]=row
            answers[f'repos/{repository}/actions/runs/{run}']=dict(id=run,head_sha='a'*40,
                repository=repository_info,head_repository=repository_info,status='completed',conclusion='success')
            answers[f'repos/{repository}/actions/artifacts/{aid}']=dict(id=aid,name=row['artifact_name'],
                size_in_bytes=len(data),digest=row['github_published_digest'],expired=False,
                workflow_run=dict(id=run,head_sha='a'*40,head_repository_id=42))
            if i==1:
                path=paper/row['path'];path.parent.mkdir();path.write_bytes(data)
        for name,count,selected in [('published-402',402,list(range(1,13))+[33]),
                                     ('published-85',85,list(range(13,21))+[33]),
                                     ('published-45',45,list(range(21,34)))]:
            directory=ci/name;directory.mkdir();dirs[name]=directory
            save(directory/'raw-artifacts.json',dict(schema='preserved-lean-artifact-index-v1',
                artifacts=[rows[i]for i in selected]))
            (directory/'proof-sources-and-logs.zip').write_bytes(b'structural fixture, not a proof ZIP')
            (directory/'proof-sources-and-logs-manifest.json').write_bytes(b'{}')
            report=dict(schema='portable-source-bound-lean-catalogue-v1',frozen_catalogue_commit=evidence.FREEZE,
                cohort_id=raw_metadata.COHORTS[name],verified_records=[dict(record_id=str(i))for i in range(count)],
                raw_artifact_index='raw-artifacts.json',raw_artifact_index_sha256=evidence.sha(directory/'raw-artifacts.json'),
                proof_source_bundle='proof-sources-and-logs.zip',proof_source_manifest='proof-sources-and-logs-manifest.json')
            if remote:report['publication_storage_mode']='remote-strict-aggregation'
            save(directory/'verified-catalogue.json',report)
        if remote:
            (paper/'formal').mkdir()
            (paper/'formal/evidence_bundle.py').write_bytes((root/'formal/evidence_bundle.py').read_bytes())
            cohorts=[]
            for name,directory in dirs.items():
                report=read_json(directory/'verified-catalogue.json')
                row=dict(relative_directory=name,cohort_id=report['cohort_id'],record_count=len(report['verified_records']))
                for key,filename in [('report','verified-catalogue.json'),('source_bundle',report['proof_source_bundle']),
                                     ('source_manifest',report['proof_source_manifest']),('raw_index',report['raw_artifact_index'])]:
                    row[key]=name+'/'+filename;row[key+'_sha256']=evidence.sha(directory/filename)
                cohorts.append(row)
            save(ci/'operator-source-hashes.json',dict(schema='reviewed-lean-aggregation-operator-sources-v1',
                sources={name:evidence.sha(ci/name)for name in operators if name!='verify_raw_github_metadata.py'},
                portable_validator=dict(path='formal/evidence_bundle.py',sha256=evidence.sha(paper/'formal/evidence_bundle.py'))))
            save(ci/'raw-preservation-index.json',dict(schema='remote-original-lean-artifact-preservation-v1',
                path_base='paper',artifacts=list(rows.values()),original_zip_count=33,
                byte_total=sum(row['bytes']for row in rows.values()),release_uploaded=False))
            save(ci/'remote-aggregation-provenance.json',dict(schema='remote-strict-lean-aggregation-v1',
                storage_mode='remote-strict-aggregation',repository=repository,frozen_catalogue_commit=evidence.FREEZE,
                aggregation_run_id=999,aggregation_commit='b'*40,approved_base_commit='c'*40,
                approved_manifest_hashes={'catalogue/synthetic.json':'d'*64},portable_cohorts=cohorts,
                operator_source_hashes='operator-source-hashes.json',operator_source_hashes_sha256=evidence.sha(ci/'operator-source-hashes.json'),
                raw_preservation_index='raw-preservation-index.json',raw_preservation_index_sha256=evidence.sha(ci/'raw-preservation-index.json'),
                complete_records=532,strict_replay_complete=True,kernel_reexecuted=False))
            answers[f'repos/{repository}/actions/runs/999']=dict(id=999,head_sha='b'*40,
                repository=repository_info,head_repository=repository_info,status='completed',conclusion='success')
        def api(endpoint):return copy.deepcopy(answers[endpoint])
        return dirs,answers,api

    def generate(self,paper,dirs,api):
        return raw_metadata.verify(paper,dirs,'alejandrozu/platonic-packing',api,
            verifier_path=paper/'ci-evidence/verify_raw_github_metadata.py')

    def test_deduplicates_all33_and_distinguishes_absent_local_bytes(self):
        with tempfile.TemporaryDirectory()as folder:
            paper=Path(folder);dirs,_,api=self.fixture(paper)
            receipt=self.generate(paper,dirs,api)
            result=raw_metadata.validate_receipt(paper,dirs,receipt)
            self.assertEqual(result,dict(raw_artifacts=33,locally_hashed_artifacts=1,metadata_only_artifacts=32))
            self.assertEqual(len(receipt['artifacts']),33)
            missing=[r for r in receipt['artifacts']if r['expected']['artifact_id']==1002][0]['local_archives'][0]
            self.assertEqual(missing['status'],'absent_not_hashed_locally');self.assertIsNone(missing['sha256'])

    def test_fails_closed_on_missing_digest_foreign_run_size_and_commit(self):
        for case in ('missing-digest','wrong-run','wrong-size','wrong-head','foreign-repository','wrong-name'):
            with self.subTest(case=case),tempfile.TemporaryDirectory()as folder:
                paper=Path(folder);dirs,answers,api=self.fixture(paper)
                artifact=answers['repos/alejandrozu/platonic-packing/actions/artifacts/1001']
                if case=='missing-digest':artifact['digest']=None
                elif case=='wrong-run':artifact['workflow_run']['id']=999
                elif case=='wrong-size':artifact['size_in_bytes']+=1
                elif case=='wrong-head':artifact['workflow_run']['head_sha']='f'*40
                elif case=='wrong-name':artifact['name']='other'
                else:answers['repos/alejandrozu/platonic-packing/actions/runs/100']['repository']['full_name']='other/repo'
                with self.assertRaises(ValueError):self.generate(paper,dirs,api)

    def test_saved_receipt_rejects_stale_index_or_false_local_hash(self):
        for case in ('false-local-hash','stale-index','wrong-artifact','missing-artifact'):
            with self.subTest(case=case),tempfile.TemporaryDirectory()as folder:
                paper=Path(folder);dirs,_,api=self.fixture(paper);receipt=self.generate(paper,dirs,api)
                if case=='false-local-hash':receipt['artifacts'][1]['local_archives'][0]['sha256']='0'*64
                elif case=='wrong-artifact':receipt['artifacts'][0]['github_artifact']['digest']='sha256:'+'0'*64
                elif case=='missing-artifact':receipt['artifacts'].pop()
                else:receipt['source_indices'][0]['index_sha256']='0'*64
                with self.assertRaises(ValueError):raw_metadata.validate_receipt(paper,dirs,receipt)

    def test_remote_gate_accepts_complete_metadata_without_raw_archive_downloads(self):
        with tempfile.TemporaryDirectory()as folder:
            paper=Path(folder);dirs,_,api=self.fixture(paper,remote=True);receipt=self.generate(paper,dirs,api)
            (paper/'ci-evidence/raw-github-metadata-verification.json').write_text(json.dumps(receipt),encoding='utf8')
            result=package_validator.validate_remote_publication(paper,evidence,
                {name:(directory,read_json(directory/'verified-catalogue.json'))for name,directory in dirs.items()})
            self.assertEqual((result['raw_artifacts'],result['metadata_only_artifacts']),(33,32))
            self.assertFalse(result['kernel_reexecuted']);self.assertEqual(len(result['required_files']),4)

    def test_remote_gate_rejects_omitted_receipt_changed_sources_and_false_kernel_claim(self):
        for case in ('missing-receipt','changed-operator','false-kernel','wrong-report','wrong-remote-run'):
            with self.subTest(case=case),tempfile.TemporaryDirectory()as folder:
                paper=Path(folder);dirs,_,api=self.fixture(paper,remote=True);receipt=self.generate(paper,dirs,api)
                ci=paper/'ci-evidence';(ci/'raw-github-metadata-verification.json').write_text(json.dumps(receipt),encoding='utf8')
                if case=='missing-receipt':(ci/'raw-github-metadata-verification.json').unlink()
                elif case=='changed-operator':(ci/'ingest_ci.py').write_text('changed',encoding='utf8')
                else:
                    path=ci/'remote-aggregation-provenance.json';value=read_json(path)
                    if case=='false-kernel':value['kernel_reexecuted']=True
                    elif case=='wrong-report':value['portable_cohorts'][0]['report_sha256']='0'*64
                    else:value['aggregation_run_id']=998
                    path.write_text(json.dumps(value),encoding='utf8')
                with self.assertRaises(ValueError):package_validator.validate_remote_publication(paper,evidence,
                    {name:(directory,read_json(directory/'verified-catalogue.json'))for name,directory in dirs.items()})

    def test_remote_gate_rejects_stale_portable_validator_source_hash(self):
        with tempfile.TemporaryDirectory()as folder:
            paper=Path(folder);dirs,_,api=self.fixture(paper,remote=True);receipt=self.generate(paper,dirs,api)
            ci=paper/'ci-evidence';(ci/'raw-github-metadata-verification.json').write_text(json.dumps(receipt),encoding='utf8')
            operators_path=ci/'operator-source-hashes.json';operators=read_json(operators_path)
            operators['portable_validator']['sha256']='0'*64
            operators_path.write_text(json.dumps(operators),encoding='utf8')
            provenance_path=ci/'remote-aggregation-provenance.json';provenance=read_json(provenance_path)
            provenance['operator_source_hashes_sha256']=evidence.sha(operators_path)
            provenance_path.write_text(json.dumps(provenance),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Evidence file SHA-256 mismatch .*evidence_bundle.py'):
                package_validator.validate_remote_publication(paper,evidence,
                    {name:(directory,read_json(directory/'verified-catalogue.json'))for name,directory in dirs.items()})


class AnalyticReceiptIntegrity(unittest.TestCase):
    def fixture(self,root,audit_names=None):
        """Structural test data only; these fixtures are not kernel proof claims."""
        audit_names=package_validator.ANALYTIC_AUDITS if audit_names is None else audit_names
        modules=['PackingCertificates/Extensions/'+name+'.lean'for name in audit_names]
        core=root/'PackingCertificates/Core.lean';core.parent.mkdir(parents=True)
        core.write_text('-- structural fixture dependency\n',encoding='utf8')
        for name in ('verify_core.py','verify_extensions.py'):
            (root/name).write_text('# structural fixture\n',encoding='utf8')
        rows=[]
        for path in modules:
            source=root/path;source.parent.mkdir(parents=True,exist_ok=True)
            names=['PackingCertificates.Extensions.'+source.stem+'.'+name
                for name in audit_names[source.stem]]
            source.write_text('import PackingCertificates.Core\n'+''.join('#print axioms '+name+'\n'for name in names),encoding='utf8')
            log=root/(source.stem+'.log')
            log.write_text(''.join("'"+name+"' does not depend on any axioms\n"for name in names),encoding='utf8')
            rows.append(dict(path=path,passed=True,exit_code=0,source_unchanged_during_build=True,
                source_sha256=evidence.sha(source),log=log.name,log_sha256=evidence.sha(log),
                olean_path=path[:-5]+'.olean',olean_sha256='1'*64,
                errors=[],unexpected_axioms=[],missing_audit_theorems=[],
                changed_imported_dependencies=[],changed_imported_dependencies_at_receipt=[],
                audited_theorems={name:[]for name in names},imported_dependencies=[dict(path='PackingCertificates/Core.lean',
                    source_sha256=evidence.sha(core),olean_path='PackingCertificates/Core.olean',olean_sha256='2'*64)]))
        return dict(schema='packing-extension-verification-v2',passed=True,requested_modules=modules,
            changed_core_dependencies=[],core_dependencies=[],results=rows,
            verifier=dict(path='verify_extensions.py',sha256=evidence.sha(root/'verify_extensions.py')),
            core_verifier_sha256=evidence.sha(root/'verify_core.py'),preflight=dict(
                expected_lean_version='4.31.0',expected_mathlib_revision='fabf563a7c95a166b8d7b6efca11c8b4dc9d911f',
                actual_mathlib_revision='fabf563a7c95a166b8d7b6efca11c8b4dc9d911f'))

    def test_complete_analytic_receipt_roundtrip(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);receipt=self.fixture(root)
            result=package_validator.validate_clearance_support(root,evidence,receipt)
            self.assertEqual(result['catalogue_records_added'],0)
            self.assertEqual(len(result['audited_theorems']),2)

    def test_rejects_failed_partial_or_changed_analytic_evidence(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);receipt=self.fixture(root)
            bads=[]
            bad=copy.deepcopy(receipt);bad['results'].pop();bads.append(bad)
            bad=copy.deepcopy(receipt);bad['changed_core_dependencies']=['Core'];bads.append(bad)
            bad=copy.deepcopy(receipt);bad['preflight']['actual_mathlib_revision']='0'*40;bads.append(bad)
            bad=copy.deepcopy(receipt);bad['results'][0]['exit_code']=1;bads.append(bad)
            bad=copy.deepcopy(receipt);bad['results'][0]['errors']=['compiler_timeout'];bads.append(bad)
            bad=copy.deepcopy(receipt);bad['results'][0]['source_sha256']='0'*64;bads.append(bad)
            bad=copy.deepcopy(receipt);bad['results'][0]['changed_imported_dependencies']=['Core'];bads.append(bad)
            for bad in bads:
                with self.assertRaises(ValueError):package_validator.validate_clearance_support(root,evidence,bad)

    def test_rejects_missing_semantic_audits_or_import_closure(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);receipt=self.fixture(root)
            bad=copy.deepcopy(receipt);bad['results'][0]['imported_dependencies']=[]
            with self.assertRaisesRegex(ValueError,'exact local import closure'):
                package_validator.validate_clearance_support(root,evidence,bad)
            bad=copy.deepcopy(receipt);bad['results'][0]['audited_theorems']={}
            with self.assertRaisesRegex(ValueError,'semantic audits'):
                package_validator.validate_clearance_support(root,evidence,bad)

    def test_rejects_missing_object_identities_and_intended_semantics(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);receipt=self.fixture(root)
            for stage in (True,False):
                bad=copy.deepcopy(receipt)
                row=bad['results'][0]if stage else bad['results'][0]['imported_dependencies'][0]
                row.pop('olean_sha256')
                with self.assertRaisesRegex(ValueError,'proof object identity'):
                    package_validator.validate_clearance_support(root,evidence,bad)
            bad=copy.deepcopy(receipt);row=bad['results'][1]
            name='PackingCertificates.Extensions.SupportIdentity.support_ballBlend'
            source=root/row['path'];log=root/row['log']
            source.write_text(source.read_text().replace('#print axioms '+name+'\n',''),encoding='utf8')
            log.write_text(log.read_text().replace("'"+name+"' does not depend on any axioms\n",''),encoding='utf8')
            row['source_sha256']=evidence.sha(source);row['log_sha256']=evidence.sha(log)
            row['audited_theorems'].pop(name)
            with self.assertRaisesRegex(ValueError,'semantic declaration audit'):
                package_validator.validate_clearance_support(root,evidence,bad)

    def test_materials_receipt_preserves_physical_scope_and_catalogue_counts(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);receipt=self.fixture(root,package_validator.MATERIALS_AUDITS)
            result=package_validator.validate_materials(root,evidence,receipt)
            self.assertEqual(sum(map(len,result['audited_theorems'].values())),37)
            self.assertEqual(result['catalogue_records_added'],0)
            self.assertTrue(result['measurable_certified_region'])
            self.assertTrue(result['periodic_whole_body_packing'])
            self.assertFalse(result['full_rotational_partition_function_proved'])
            self.assertFalse(result['per_record_free_volumes_computed'])

    def test_materials_receipt_rejects_partial_failed_or_reordered_builds(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);receipt=self.fixture(root,package_validator.MATERIALS_AUDITS)
            bads=[]
            bad=copy.deepcopy(receipt);bad['results'].pop();bads.append(bad)
            bad=copy.deepcopy(receipt);bad['passed']=False;bads.append(bad)
            bad=copy.deepcopy(receipt);bad['results'][1]['exit_code']=1;bads.append(bad)
            bad=copy.deepcopy(receipt);bad['changed_core_dependencies']=['Core'];bads.append(bad)
            bad=copy.deepcopy(receipt);bad['requested_modules'].reverse();bad['results'].reverse();bads.append(bad)
            for bad in bads:
                with self.assertRaises(ValueError):package_validator.validate_materials(root,evidence,bad)

    def test_materials_receipt_requires_semantic_volume_and_periodic_theorems(self):
        cases={0:'exists_positive_measurable_feasible_region',1:'vertex_certificate_periodic_packing'}
        for index,short in cases.items():
            with self.subTest(theorem=short),tempfile.TemporaryDirectory()as folder:
                root=Path(folder);receipt=self.fixture(root,package_validator.MATERIALS_AUDITS)
                row=receipt['results'][index];source=root/row['path'];log=root/row['log']
                name='PackingCertificates.Extensions.'+source.stem+'.'+short
                source.write_text(source.read_text().replace('#print axioms '+name+'\n',''),encoding='utf8')
                log.write_text(log.read_text().replace("'"+name+"' does not depend on any axioms\n",''),encoding='utf8')
                row['source_sha256']=evidence.sha(source);row['log_sha256']=evidence.sha(log)
                row['audited_theorems'].pop(name)
                with self.assertRaisesRegex(ValueError,'semantic declaration audit'):
                    package_validator.validate_materials(root,evidence,receipt)

    def test_materials_receipt_rejects_missing_imports_objects_and_custom_axioms(self):
        for case in ('imports','stage-object','import-object','custom-axiom'):
            with self.subTest(case=case),tempfile.TemporaryDirectory()as folder:
                root=Path(folder);receipt=self.fixture(root,package_validator.MATERIALS_AUDITS)
                row=receipt['results'][0]
                if case=='imports':row['imported_dependencies']=[]
                elif case=='stage-object':row['olean_sha256']=None
                elif case=='import-object':row['imported_dependencies'][0]['olean_sha256']=None
                else:
                    row['unexpected_axioms']=['Materials.unprovedPhysics']
                with self.assertRaises(ValueError):package_validator.validate_materials(root,evidence,receipt)


def read_json(path):return json.loads(Path(path).read_text(encoding='utf8'))


if __name__=='__main__':unittest.main()
