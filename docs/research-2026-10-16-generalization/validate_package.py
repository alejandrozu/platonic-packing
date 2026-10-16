"""Validate the published source closure without mixing build environments."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
from math import gcd, isqrt
from pathlib import Path
import re
import sys
import zipfile

sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
DEFAULT=HERE if (HERE/'package-files.json').is_file() else HERE.parents[1]/'work/packing-external-records/docs/research-2026-10-16-generalization'
CI_TOOLS={'ingest_ci.py','ingest_core.py','ingest_algebraic.py','validate_algebraic.py',
          'publish_402.py','publish_algebraic.py','archive_release.py','README.md',
          'evidence_store.py','test_evidence_store.py','compact_cohort.py',
          'stream_old_checkpoints.py','audit_object_cache.py',
          'aggregate_publication.py','verify_raw_github_metadata.py',
          'release_from_preservation.py'}
CI_METADATA={'remote-aggregation-provenance.json','raw-preservation-index.json',
             'operator-source-hashes.json','raw-github-metadata-verification.json'}


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))


def validate_remote_publication(paper,evidence,cohorts):
    """Check remote replay provenance locally, without opening raw archives.

    The only imported helper is our named plaintext publication operator. Python
    retained in proof artifacts is never imported or executed here.
    """
    paper=Path(paper).resolve();ci=paper/'ci-evidence'
    present={name for name in CI_METADATA if (ci/name).is_file()}
    remote=any(report.get('publication_storage_mode')=='remote-strict-aggregation'
               for _,report in cohorts.values())
    if not remote and not present:return dict(mode='local',required_files=[])
    if present!=CI_METADATA:raise ValueError('Remote publication needs provenance and the local GitHub API verification receipt')
    if set(cohorts)!={'published-402','published-85','published-45'}:
        raise ValueError('The remote final aggregation provenance must cover all three publication cohorts')
    provenance=read(evidence.checked_file(ci,'remote-aggregation-provenance.json'))
    if (provenance.get('schema')!='remote-strict-lean-aggregation-v1'or
            provenance.get('storage_mode')!='remote-strict-aggregation'or
            provenance.get('repository')!='alejandrozu/platonic-packing'or
            provenance.get('frozen_catalogue_commit')!=evidence.FREEZE or
            provenance.get('strict_replay_complete')is not True or
            provenance.get('kernel_reexecuted')is not False or provenance.get('complete_records')!=532):
        raise ValueError('Remote aggregation does not retain the approved strict replay boundary')
    if type(provenance.get('aggregation_run_id'))is not int or provenance['aggregation_run_id']<=0:
        raise ValueError('Invalid remote aggregation run identity')
    for key in ('aggregation_commit','approved_base_commit'):
        if not re.fullmatch(r'[0-9a-f]{40}',str(provenance.get(key,''))):raise ValueError('Invalid remote aggregation commit')
    if not provenance.get('approved_manifest_hashes'):raise ValueError('Missing approved remote proof asset hashes')
    for name,digest in provenance['approved_manifest_hashes'].items():
        evidence.safe_name(name);evidence.sha_value(digest)
    rows={}
    for row in provenance['portable_cohorts']:
        name=row['relative_directory']
        if name in rows or name not in cohorts:raise ValueError('Changed/duplicate remote portable cohort')
        rows[name]=row;folder,report=cohorts[name]
        if report.get('publication_storage_mode')!='remote-strict-aggregation':
            raise ValueError('Remote portable cohort lacks its explicit publication marker')
        if row.get('cohort_id')!=report['cohort_id']or row.get('record_count')!=len(report['verified_records']):
            raise ValueError('Remote portable cohort identity/count mismatch')
        files=[('report','verified-catalogue.json'),('source_bundle',report['proof_source_bundle']),
               ('source_manifest',report['proof_source_manifest']),('raw_index',report['raw_artifact_index'])]
        for key,filename in files:
            if row[key]!=name+'/'+filename:raise ValueError('Remote portable cohort locator mismatch')
            evidence.checked_file(folder,filename,row[key+'_sha256'])
    if set(rows)!=set(cohorts):raise ValueError('Incomplete remote portable cohort provenance')
    for name,hkey in [('operator_source_hashes','operator_source_hashes_sha256'),
                      ('raw_preservation_index','raw_preservation_index_sha256')]:
        expected='operator-source-hashes.json'if name=='operator_source_hashes'else'raw-preservation-index.json'
        if provenance.get(name)!=expected:raise ValueError('Unexpected remote aggregation metadata locator')
        evidence.checked_file(ci,expected,provenance[hkey])
    operators=read(ci/'operator-source-hashes.json')
    expected_operators={'aggregate_publication.py','ingest_ci.py','ingest_core.py','ingest_algebraic.py',
        'validate_algebraic.py','evidence_store.py','compact_cohort.py','publish_402.py','publish_algebraic.py'}
    if (operators.get('schema')!='reviewed-lean-aggregation-operator-sources-v1'or
            set(operators.get('sources',{}))!=expected_operators):
        raise ValueError('Missing reviewed remote aggregation operator implementation hashes')
    portable_validator=operators.get('portable_validator')or{}
    if portable_validator.get('path')!='formal/evidence_bundle.py':
        raise ValueError('Remote aggregation lacks its exact portable validator source identity')
    evidence.checked_file(paper,portable_validator['path'],portable_validator.get('sha256',''))
    for name,digest in operators['sources'].items():
        if name not in CI_TOOLS or not name.endswith('.py'):raise ValueError('Unpackaged remote aggregation operator')
        evidence.checked_file(ci,name,digest)
    preserve=read(ci/'raw-preservation-index.json');raw={}
    keys=('run_id','artifact_id','head_sha','path','bytes','sha256','github_published_digest',
          'proposed_release_asset_name','permanent_download_url')
    for folder,report in cohorts.values():
        for row in read(folder/report['raw_artifact_index'])['artifacts']:
            key=(row['run_id'],row['artifact_id']);value={k:row[k]for k in keys}
            if key in raw and raw[key]!=value:raise ValueError('Conflicting remote original-archive identities')
            raw[key]=value
    if (preserve.get('schema')!='remote-original-lean-artifact-preservation-v1'or
            preserve.get('path_base')!='paper'or preserve.get('release_uploaded')is not False or
            preserve.get('original_zip_count')!=len(raw)or len(raw)!=33 or
            preserve.get('byte_total')!=sum(row['bytes']for row in raw.values())):
        raise ValueError('Remote original-archive preservation metadata is incomplete')
    listed={}
    for row in preserve['artifacts']:
        key=(row['run_id'],row['artifact_id'])
        if key in listed:raise ValueError('Duplicate remote preserved archive')
        listed[key]={k:row[k]for k in keys}
    if listed!=raw:raise ValueError('Remote preserved archive list differs from public raw indices')
    helper=evidence.checked_file(ci,'verify_raw_github_metadata.py')
    spec=importlib.util.spec_from_file_location('_publication_raw_api_'+evidence.sha(helper),helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    receipt_path=evidence.checked_file(ci,'raw-github-metadata-verification.json');receipt=read(receipt_path)
    result=module.validate_receipt(paper,{name:folder for name,(folder,_)in cohorts.items()},receipt)
    record=receipt.get('remote_aggregation')or{};actual=record.get('github_run')or{}
    if (record.get('provenance_path')!='ci-evidence/remote-aggregation-provenance.json'or
            record.get('provenance_sha256')!=evidence.sha(ci/'remote-aggregation-provenance.json')or
            actual.get('id')!=provenance['aggregation_run_id']or actual.get('head_sha')!=provenance['aggregation_commit']or
            actual.get('status')!='completed'or actual.get('conclusion')!='success'or
            (actual.get('repository')or{}).get('full_name','').casefold()!=provenance['repository'].casefold()or
            (actual.get('head_repository')or{}).get('full_name','').casefold()!=provenance['repository'].casefold()):
        raise ValueError('Local API receipt does not authenticate the matching remote aggregation run')
    return dict(mode='remote-strict-aggregation',aggregation_run_id=provenance['aggregation_run_id'],
        aggregation_commit=provenance['aggregation_commit'],kernel_reexecuted=False,
        **result,required_files=['ci-evidence/'+name for name in sorted(CI_METADATA)])


def validate_reference_edges(formal,evidence,inputs=None):
    """Read-only source/receipt audit; never execute a packaged generator."""
    formal=Path(formal)
    receipt_name='catalogue/nd-reference-edge-lean-verification.json'
    binding=read(evidence.checked_file(formal,'catalogue/nd-reference-edge-lean-binding.json'))
    audit=read(evidence.checked_file(formal,'catalogue/nd-edge-scale-audit.json'))
    receipt=read(evidence.checked_file(formal,receipt_name))
    module='PackingCertificates/Algebraic/NDReferenceEdges.lean'
    registry='catalogue/algebraic/generated-nd-pilots-registry.json'
    geometry='catalogue/algebraic/inputs/src/polytopes_nd.json'
    if (binding.get('schema')!='nd-selected-reference-edge-lean-binding-v1' or
            binding.get('status')!='source_bound_not_compilation_receipt' or
            binding.get('source_freeze')!=evidence.FREEZE or
            (binding.get('endpoint_count'),binding.get('selected_edges'),binding.get('native_ratio_records'))!=(24,12,45)):
        raise ValueError('Unexpected source-bound ND reference-edge coverage/status')
    if (audit.get('schema')!='nd-reference-edge-python-audit-v1' or
            audit.get('status')!='passed_python_exact_audit' or audit.get('lean_verification')is not False or
            audit.get('source_freeze')!=evidence.FREEZE or
            (audit.get('shape_count'),audit.get('listed_edges_checked'),audit.get('records_checked'))!=(12,2490,45)):
        raise ValueError('Python ND edge audit must remain a separate exact audit, not a Lean proof')
    paths={'registry_path':registry,'geometry_path':geometry,'generated_path':module,
        'generator_path':'catalogue/generate_nd_reference_edges.py'}
    for key,value in paths.items():
        if binding.get(key)!=value:raise ValueError('Unexpected ND reference-edge source path '+key)
    for key in ('registry_path','registry_sha256','geometry_path','geometry_sha256','shapes','records'):
        if audit.get(key)!=binding.get(key):raise ValueError('ND edge Python/Lean source-binding mismatch '+key)
    if audit.get('auditor_path')!='catalogue/nd-edge-scale-audit.py':
        raise ValueError('Unexpected ND edge auditor source')
    evidence.checked_file(formal,binding['generator_path'],binding['generator_sha256'])
    evidence.checked_file(formal,audit['auditor_path'],audit['auditor_sha256'])
    leaf=evidence.checked_file(formal,module,binding['generated_sha256'])
    def input_json(name,expected):
        if inputs is None:return read(evidence.checked_file(formal,name,expected))
        value=inputs.json(name,expected)
        if (formal/name).exists():evidence.checked_file(formal,name,expected)
        return value
    reg=input_json(registry,binding['registry_sha256'])
    shapes=input_json(geometry,binding['geometry_sha256'])
    def parse(text):
        text=str(text).replace(' ','');terms=re.findall(r'[+-]?[^+-]+',text)
        if not terms or ''.join(terms)!=text:raise ValueError('Unsupported exact reference radical')
        result={}
        for term in terms:
            if 'sqrt'in term:
                coefficient,radical=term.split('sqrt');coefficient=coefficient.rstrip('*');r=int(radical)
                c=Fraction(1)if coefficient in ('','+')else Fraction(-1)if coefficient=='-'else Fraction(coefficient)
                if r<1 or any(r%(p*p)==0 for p in range(2,isqrt(r)+1)):
                    raise ValueError('Reference radical must be positive and square-free')
            else:c,r=Fraction(term),1
            result[r]=result.get(r,Fraction(0))+c
        return {r:c for r,c in result.items()if c}
    def add(x,y):
        result=dict(x)
        for r,c in y.items():result[r]=result.get(r,Fraction(0))+c
        return {r:c for r,c in result.items()if c}
    def multiply(x,y):
        result={}
        for r,c in x.items():
            for s,d in y.items():
                common=gcd(r,s);z=r*s//(common*common)
                result[z]=result.get(z,Fraction(0))+c*d*common
        return {r:c for r,c in result.items()if c}
    def encode(x):return {str(r):str(c)for r,c in sorted(x.items())}
    def positive(mu):
        if set(mu)<={1,5}:a,b=mu.get(1,Fraction(0)),mu.get(5,Fraction(0))
        elif set(mu)<={2,10}:a,b=mu.get(2,Fraction(0)),mu.get(10,Fraction(0))
        else:raise ValueError('Unexpected exact native mu field')
        if a>=0 and b>=0:return a>0 or b>0
        if a<=0 and b<=0:return False
        return a*a>5*b*b if a>=0 else 5*b*b>a*a
    records=reg['records'];ids=[r['record_id']for r in records]
    if len(ids)!=45 or len(set(ids))!=45:raise ValueError('Reference leaf must bind the exact45 distinct ND pilots')
    expected_records=[];used=set()
    for row in records:
        if (row['source_freeze']!=evidence.FREEZE or row['geometry_source_path']!=geometry or
                row['geometry_source_sha256']!=binding['geometry_sha256']):
            raise ValueError('ND reference record changed frozen geometry/source identity')
        native='catalogue/algebraic/inputs/'+row['source_path']
        raw=input_json(native,row['source_sha256'])
        if any(raw[k]!=row[k]for k in ('piece','container','n'))or raw['dim']!=row['dimension']:
            raise ValueError('ND reference native record identity mismatch')
        mu=parse(raw['mu']);square=multiply(mu,mu)
        pe=parse(shapes[row['piece']]['edge2']);ce=parse(shapes[row['container']]['edge2'])
        if not positive(mu)or multiply(square,ce)!=pe:raise ValueError('ND exact positive native edge ratio failed')
        expected_records.append(dict(record_id=row['record_id'],source_path=native,source_sha256=row['source_sha256'],
            piece=row['piece'],container=row['container'],dimension=row['dimension'],native_mu=raw['mu'],
            native_mu_positive=True,mu_squared=encode(square),piece_edge_squared=encode(pe),
            container_edge_squared=encode(ce),edge_ratio_identity=True))
        used.update((row['piece'],row['container']))
    if binding['records']!=expected_records:raise ValueError('Reference-edge binding does not match all45 exact native inputs')
    expected_shapes=[];total=0
    for name in sorted(used):
        shape=shapes[name];vertices=[[parse(x)for x in v]for v in shape['V']];edges=shape['edges']
        if not vertices or any(len(v)!=shape['dim']for v in vertices):raise ValueError('ND reference coordinate dimension mismatch')
        if not edges or len({tuple(sorted(e))for e in edges})!=len(edges):raise ValueError('Empty/duplicate reference edge list')
        expected=parse(shape['edge2'])
        for edge in edges:
            if len(edge)!=2 or any(type(i)is not int or not 0<=i<len(vertices)for i in edge)or edge[0]==edge[1]:
                raise ValueError('Malformed native reference edge')
            distance={}
            for a,b in zip(vertices[edge[0]],vertices[edge[1]]):
                delta=add(a,{r:-c for r,c in b.items()});distance=add(distance,multiply(delta,delta))
            if distance!=expected:raise ValueError('Exact Python reference edge identity failed '+name)
        total+=len(edges)
        semantic=json.dumps(shape,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
        expected_shapes.append(dict(shape=name,dimension=shape['dim'],vertex_count=len(vertices),
            listed_edges_checked=len(edges),edge_squared=encode(expected),geometry_entry_sha256=hashlib.sha256(semantic).hexdigest(),
            reference_edge=edges[0],all_listed_edge_identities=True))
    if len(used)!=12 or total!=2490 or binding['shapes']!=expected_shapes:
        raise ValueError('Reference shape binding/2490-edge Python coverage mismatch')
    # Bind the small Lean leaf's selected literals directly to frozen JSON;
    # no generated/packaged Python is executed by this independent check.
    leaf_text=leaf.read_text(encoding='utf8')
    def rational(x):
        x=Fraction(x)
        return f'({x.numerator} : ℚ)'if x.denominator==1 else f'({x.numerator}/{x.denominator} : ℚ)'
    def pair(x,r):
        if set(x)-{1,r}:raise ValueError('Selected endpoint uses a different primitive field')
        return '('+rational(x.get(1,0))+','+rational(x.get(r,0))+')'
    def literal(text):
        if text not in leaf_text:raise ValueError('Lean reference literal/statement differs from frozen source')
    for item in expected_shapes:
        name=item['shape'];shape=shapes[name];i,j=shape['edges'][0]
        roots=set().union(*(set(parse(x))-{1}for v in [shape['V'][i],shape['V'][j]]for x in v))
        if len(roots)>1:raise ValueError('Selected reference endpoints have multiple primitive roots')
        r=next(iter(roots))if roots else 5
        for suffix,vertex in [('u',shape['V'][i]),('v',shape['V'][j])]:
            literal(f'def {name}_{suffix} : Fin {shape["dim"]} → PairQ := !['+','.join(pair(parse(x),r)for x in vertex)+']\n')
        literal(f'def {name}_edge : PairQ := '+pair(parse(shape['edge2']),r)+'\n')
        literal(f'theorem {name}_edge_exact : distancePair {r} {name}_u {name}_v = {name}_edge :=')
    for item in expected_records:
        ident=item['record_id'];mu=parse(item['native_mu']);times_two=set(mu)<={2,10}
        m={r:c for r,c in {1:mu.get(2,0),5:mu.get(10,0)}.items()if c}if times_two else mu
        factor='true'if times_two else'false'
        ce=pair(parse(shapes[item['container']]['edge2']),5);pe=pair(parse(shapes[item['piece']]['edge2']),5)
        literal(f'def {ident}_m : PairQ := '+pair(m,5)+'\n')
        literal(f'theorem {ident}_edge_ratio : (nativeMu {ident}_m {factor})^2 * embed (Real.sqrt 5) {ce} = embed (Real.sqrt 5) {pe} :=')
    if (receipt.get('schema')!='packing-extension-verification-v2' or receipt.get('passed')is not True or
            receipt.get('requested_modules')!=[module]or len(receipt.get('results',[]))!=1 or receipt.get('changed_core_dependencies')):
        raise ValueError('Reference-edge Lean receipt did not completely pass')
    preflight=receipt['preflight']
    if (preflight.get('expected_lean_version')!='4.31.0' or
            preflight.get('expected_mathlib_revision')!='fabf563a7c95a166b8d7b6efca11c8b4dc9d911f' or
            preflight.get('actual_mathlib_revision')!=preflight.get('expected_mathlib_revision')):
        raise ValueError('Reference-edge Lean receipt uses different pinned dependencies')
    if receipt['verifier'].get('path')!='verify_extensions.py':raise ValueError('Unexpected reference-edge verifier source')
    evidence.checked_file(formal,receipt['verifier']['path'],receipt['verifier']['sha256'])
    evidence.checked_file(formal,'verify_core.py',receipt['core_verifier_sha256'])
    stage=receipt['results'][0]
    if (stage.get('path')!=module or stage.get('olean_path')!=module[:-5]+'.olean' or
            stage.get('source_sha256')!=binding['generated_sha256'] or
            stage.get('passed')is not True or stage.get('exit_code')!=0 or stage.get('source_unchanged_during_build')is not True or
            any(stage.get(k)for k in ('errors','unexpected_axioms','missing_audit_theorems','changed_imported_dependencies','changed_imported_dependencies_at_receipt'))):
        raise ValueError('Reference-edge Lean stage failed a source/build invariant')
    log=evidence.checked_file(formal,stage['log'],stage['log_sha256'])
    parsed=evidence.axiom_audit(log.read_text(encoding='utf8'))
    namespace='PackingCertificates.Algebraic.NDReferenceEdges.'
    names=[namespace+n for n in binding['audited_declarations']]
    directives=re.findall(r'^\s*#print\s+axioms\s+([\w.]+)',leaf_text,re.M)
    if (len(names)!=159 or len(set(names))!=159 or directives!=names or set(parsed)!=set(names) or
            stage['audited_theorems']!=parsed or set(stage.get('axioms',[]))!={a for v in parsed.values()for a in v}):
        raise ValueError('Reference-edge159 Lean audits do not match the actual leaf/log/binding')
    evidence.sha_value(stage['olean_sha256'])
    dependencies=stage['imported_dependencies'];depmap={d['path']:d for d in dependencies}
    if len(depmap)!=len(dependencies):raise ValueError('Duplicate reference-edge transitive source dependency')
    required={module,stage['log'],receipt_name,'catalogue/nd-reference-edge-lean-binding.json','catalogue/nd-edge-scale-audit.json',
        binding['generator_path'],audit['auditor_path'],'verify_extensions.py','verify_core.py'}
    reached=set()
    def visit(path):
        source=evidence.checked_file(formal,path)
        for line in re.findall(r'^\s*import\s+([^\n]+)',source.read_text(encoding='utf8'),re.M):
            for item in line.split('--',1)[0].split():
                if item=='PackingCertificates'or item.startswith('PackingCertificates.'):
                    target=item.replace('.','/')+'.lean'
                    if target not in reached:reached.add(target);visit(target)
    visit(module)
    if reached!=set(depmap):raise ValueError('Reference-edge receipt lacks the exact transitive generic source closure')
    for dep in [*dependencies,*receipt.get('core_dependencies',[])]:
        evidence.checked_file(formal,dep['path'],dep['source_sha256']);required.add(dep['path'])
        evidence.sha_value(dep['olean_sha256'])
    return dict(receipt=receipt_name,lean_stages=1,lean_audited_declarations=159,selected_reference_edges=12,
        native_positive_edge_ratios=45,python_listed_edges_checked=2490,python_audit_is_lean_proof=False,
        transitive_generic_sources=len(reached),required_files=sorted(required))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=DEFAULT)
    parser.add_argument('--rational-only',action='store_true',help='Explicitly validate a rational-only publication')
    args=parser.parse_args();package=args.package.resolve();formal=package/'formal'
    sys.path.insert(0,str(formal))
    import evidence_bundle as evidence
    allowlist=read(package/'package-files.json')
    if allowlist.get('schema')!='polyhedral-paper-publication-allowlist-v2':
        raise ValueError('Unsupported publication allowlist schema')
    expected={}
    for row in allowlist['files']:
        name=evidence.safe_name(row['path'])
        if name.casefold()in {p.casefold()for p in expected}:raise ValueError('Duplicate publication allowlist member')
        source=evidence.checked_file(package,name,row['sha256'])
        if source.stat().st_size!=row['bytes']:raise ValueError('Publication file byte count mismatch '+name)
        expected[name]=row
    actual={p.relative_to(package).as_posix()for p in package.rglob('*')if p.is_file()}
    extras=actual-set(expected)-{'package-files.json','package-validation.json','reproduction-report.json'}
    if extras:raise ValueError('Unlisted publication files: '+', '.join(sorted(extras)[:10]))
    ci_tools=package/'ci-evidence'
    ci_files={p.name for p in ci_tools.iterdir()if p.is_file()}
    if not CI_TOOLS<=ci_files or ci_files-(CI_TOOLS|CI_METADATA)or any(p.is_dir()for p in ci_tools.iterdir()):
        raise ValueError('Root CI evidence tree must contain only the approved plaintext tooling')
    if any(p.suffix in evidence.COMPILED_SUFFIXES or '.lake'in p.parts or '__pycache__'in p.parts
           for p in formal.rglob('*')if p.is_file()):
        raise ValueError('Compiled objects/caches must not enter the Git publication tree')
    library_folders={formal/'PackingCertificates',formal/'PackingCertificates/Algebraic',formal/'PackingCertificates/Extensions'}
    if any(p.parent not in library_folders for p in(formal/'PackingCertificates').rglob('*.lean')):
        raise ValueError('Generated/trial numerical Lean sources must remain in their environment-scoped archives')
    for name in ('GenericDimension','Complexity','NDIdentity'):
        if not (formal/'PackingCertificates/Extensions'/(name+'.lean')).is_file():
            raise ValueError('Required generic method theorem source missing '+name)
    method_proofs=[];checked_sources=set()
    for name,stages,audits in [('core-verification.json',None,None),
                              ('extension-verification-v2.json',10,61),
                              ('extension-identity-verification.json',1,10),
                              ('catalogue/nd-reference-edge-lean-verification.json',1,159)]:
        receipt=read(formal/name)
        if name=='core-verification.json':
            if receipt.get('status')!='passed':raise ValueError('Plaintext generic core receipt did not pass')
        elif receipt.get('passed')is not True:raise ValueError('Generic method receipt did not pass '+name)
        if receipt.get('verifier'):
            evidence.checked_file(formal,receipt['verifier']['path'],receipt['verifier']['sha256'])
        count=0
        for row in receipt['results']:
            if row.get('passed')is not True or row.get('exit_code')!=0:raise ValueError('Unsuccessful generic method stage')
            evidence.checked_file(formal,row['path'],row['source_sha256'])
            log=evidence.checked_file(formal,row['log'],row['log_sha256'])
            parsed=evidence.axiom_audit(log.read_text(encoding='utf8'))
            if parsed!=row['audited_theorems']:raise ValueError('Generic method audit differs from actual log')
            checked_sources.add(row['path']);count+=len(parsed)
            for dep in row.get('imported_dependencies',[]):
                evidence.checked_file(formal,dep['path'],dep['source_sha256']);checked_sources.add(dep['path'])
        if stages is not None and (len(receipt['results'])!=stages or count!=audits):
            raise ValueError('Generic method proof coverage differs from the required receipt '+name)
        method_proofs.append(dict(receipt=name,stages=len(receipt['results']),audited_declarations=count))
    inputs=read(formal/'catalogue/inputs/source-manifest.json')
    for row in [*inputs['records'],*inputs['geometry']]:
        evidence.checked_file(formal/'catalogue/inputs',row.get('file',row.get('path')),row['sha256'])
    witness=read(formal/'catalogue/rational-witnesses-manifest.json')
    with evidence.SourceBundle(formal/'catalogue',manifest_filename='rational-witnesses-manifest.json',
            archive_filename='rational-witnesses.zip',expected_schema=None,internal_manifest='witness-manifest.json')as bundle:
        witness_count=len(bundle.files)
    targets={Path(r['path']).stem for r in witness['files']}
    report,checked=evidence.verify_portable_cohort(formal/'ci-evidence/published-402',expected_count=402,
        expected_ids=targets,require_complete=True)
    evidence.require_rational_402(report,witness)
    evidence.checked_file(package,'ci-evidence/publish_402.py',report['exporter_sha256'])
    cohorts=[checked];additional=[];current_cohorts={'published-402':(report,checked)}
    remote_cohorts={'published-402':(formal/'ci-evidence/published-402',report)}
    for name in (()if args.rational_only else ('published-85','published-45')):
        folder=formal/'ci-evidence'/name
        target_ids=evidence.pilot_target_ids(formal,name)
        summary,validation=evidence.verify_portable_cohort(folder,expected_count=evidence.COHORTS[name][1],
            expected_ids=target_ids,require_complete=True)
        evidence.checked_file(package,'ci-evidence/publish_algebraic.py',summary['exporter_sha256'])
        if summary.get('validator_sha256'):
            evidence.checked_file(package,'ci-evidence/validate_algebraic.py',summary['validator_sha256'])
        additional.extend(summary['verified_records']);cohorts.append(validation)
        current_cohorts[name]=(summary,validation)
        remote_cohorts[name]=(folder,summary)
    remote=validate_remote_publication(package,evidence,remote_cohorts)
    pilot_manifest=formal/'catalogue/algebraic/pilot-inputs-and-proposals-manifest.json'
    reference_edges=None
    if pilot_manifest.exists():
        with evidence.SourceBundle(pilot_manifest.parent,manifest_filename=pilot_manifest.name,
                expected_schema='bounded-algebraic-pilot-inputs-v1')as bundle:
            if any(p.startswith(('catalogue/algebraic/witnesses3d/','catalogue/algebraic/witnesses_nd_pilots/'))for p in bundle.files):
                proposals=sum(p.startswith(('catalogue/algebraic/witnesses3d/','catalogue/algebraic/witnesses_nd_pilots/'))for p in bundle.files)
                if proposals!=130:raise ValueError('Shared pilot input archive must include exactly85+45 bounded proposals')
            if any(p.startswith('catalogue/algebraic/inputs/records/')for p in bundle.files):
                natives=sum(p.startswith('catalogue/algebraic/inputs/records/')for p in bundle.files)
                if natives!=130:raise ValueError('Shared pilot input archive must include exactly130 selected native inputs')
            reference_edges=validate_reference_edges(formal,evidence,bundle)
    else:
        reference_edges=validate_reference_edges(formal,evidence)
    with zipfile.ZipFile(package/'arxiv-source.zip')as archive:
        if sorted(archive.namelist())!=['figures/generalization-examples.pdf','manuscript.tex']:
            raise ValueError('Unexpected arXiv source archive contents')
        for name in archive.namelist():
            if archive.read(name)!=(package/name).read_bytes():raise ValueError('arXiv archive does not match final source')
    text=(package/'manuscript.tex').read_text(encoding='utf8')
    if 'FINAL_'in text:raise ValueError('Unresolved manuscript placeholder')
    rows=report['verified_records'];dimensions={d:sum(r['dimension']==d for r in rows)for d in (3,4,5,6)}
    macros=dict(leanRecords=402,leanCubeRecords=dimensions[3],leanNDRecords=sum(dimensions[d]for d in(4,5,6)),
        leanFourDRecords=dimensions[4],leanFiveDRecords=dimensions[5],leanSixDRecords=dimensions[6],
        leanPieces=10796,leanPairs=235462)
    additional_ids=[r['record_id']for r in additional]
    if len(additional_ids)!=len(set(additional_ids))or set(additional_ids)&targets:
        raise ValueError('Additional algebraic records overlap/duplicate another cohort')
    families={(r['dimension'],r['piece'],r['container'])for r in additional}
    if not args.rational_only:evidence.require_family_union(rows,additional)
    macros.update(leanAlgebraicRecords=len(additional),leanAlgebraicFamilies=len(families))
    for name,value in macros.items():
        match=re.search(r'\\newcommand\{\\'+name+r'\}\{([\d,]+)\}',text)
        if not match or int(match.group(1).replace(',',''))!=value:raise ValueError('Manuscript count differs from strict evidence '+name)
    metadata=read(formal/'verification.json')
    if metadata.get('schema')!='portable-paper-verification-v2'or metadata['catalogue_receipt_sha256']!=checked['summary_sha256']:
        raise ValueError('Final verification metadata does not bind the portable catalogue summary')
    modules=read(formal/'catalogue/verified-module-manifest.json')
    if modules.get('schema')!='environment-scoped-lean-module-manifest-v1':
        raise ValueError('Reproduction metadata must preserve environment-scoped module roots')
    evidence.check_final_cohort_metadata(metadata,modules,current_cohorts)
    compatibility=read(formal/'catalogue/verified-catalogue.json')
    if (compatibility.get('schema')!='portable-catalogue-compatibility-summary-v1'or
            compatibility.get('complete_402')is not True or
            set(compatibility.get('verified_record_ids',[]))!=targets or
            compatibility['source_report_sha256']!=checked['summary_sha256']or
            compatibility['verified_totals']!=report['verified_totals']or
            compatibility['additional_algebraic_records']!=len(additional)):
        raise ValueError('Compatibility summary differs from its authoritative portable proof cohorts')
    result=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),status='passed',
        distinct_verified_rational_records=402,additional_verified_algebraic_records=len(additional),
        additional_verified_algebraic_families=len(families),method_proofs=method_proofs,cohorts=cohorts,
        remote_publication={k:v for k,v in remote.items()if k!='required_files'},
        nd_reference_edge_evidence={k:v for k,v in reference_edges.items()if k!='required_files'},
        checked_plaintext_generic_sources=len(checked_sources),native_rational_records=len(inputs['records']),
        compressed_rational_witnesses=witness_count,
        checks=['All publication allowlist byte hashes match',
                'Each proof environment retains its own source/log/receipt/plan closure',
                'Every archived byte hash and semantic axiom audit matches',
                'Generic all-dimension method proofs have separate actual receipts',
                'Selected ND reference-edge Lean leaf and separate 2490-edge Python audit match frozen native inputs',
                'All frozen native inputs and bounded proposed witness archives match',
                'Exact402 record identities and fixed totals match the frozen target cohort',
                'Manuscript macros and portable verification metadata match strict evidence',
                'No compiled objects, caches or flat generated numerical source copies are included'],
        optimality_proved=False,submission_status='GitHub manuscript; no arXiv submission')
    data=json.dumps(result,indent=2)+'\n'
    (package/'package-validation.json').write_text(data,encoding='utf8',newline='\n')
    if HERE!=package:(HERE/'package-validation.json').write_text(data,encoding='utf8',newline='\n')
    print(data)


if __name__=='__main__':main()

