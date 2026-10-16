#!/usr/bin/env python3
"""Exact transcription into bounded kernel-proof modules for the 85 3D pilots.

The unfragmented registry and source binding remain authoritative inputs.  No
coordinate, inverse, interval, scale, basis index or separation plane changes.
All arithmetic is still checked by `decide +kernel`; fragmentation only bounds
per-file reduction caches.  The certificate is noncomputable to avoid generating
unused native executable code for multi-megabyte exact rational constants.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parents[1]
REGISTRY = HERE / 'generated3d-registry.json'
HELPER = 'PackingCertificates.Algebraic.Fragment3D'


def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).resolve().relative_to(FORMAL).as_posix()
def module(p): return rel(p)[:-5].replace('/', '.')
def bytes_of(lines): return ('\n'.join(lines)+'\n').replace('\n','\r\n').encode('utf8')


def split_ranges(size, width):
    return [(lo, min(width, size-lo)) for lo in range(0,size,width)]


def range_assembly(variable, ranges, names, indent='  '):
    """Balanced comparisons; no expansion into hundreds of `fin_cases` goals."""
    if not ranges:
        return [indent+'exact Fin.elim0 '+variable]
    if len(ranges) == 1:
        return [indent+f'exact rangeCheck_sound {names[0]} {variable} (by omega) (by omega)']
    mid=len(ranges)//2; boundary=ranges[mid][0]
    rows=[indent+f'by_cases h{boundary} : {variable}.val < {boundary}']
    rows+= [indent+'· '+range_assembly(variable,ranges[:mid],names[:mid],indent+'  ')[0].lstrip()]
    rows+=range_assembly(variable,ranges[:mid],names[:mid],indent+'  ')[1:]
    rows+= [indent+'· '+range_assembly(variable,ranges[mid:],names[mid:],indent+'  ')[0].lstrip()]
    rows+=range_assembly(variable,ranges[mid:],names[mid:],indent+'  ')[1:]
    return rows


def generate(original, basis_width=1, vertex_width=8, write=True):
    if basis_width < 1 or vertex_width < 1:
        raise ValueError('Proof widths must be positive')
    source=FORMAL/original['generated_module']
    if sha(source)!=original['generated_source_sha256']:
        raise ValueError('Unfragmented authoritative source changed')
    proposal=read(FORMAL/original['proposal_path'])
    n,d=original['n'],original['dimension']
    k=len(proposal['placed_vertex_intervals'][0]); b=len(proposal['container_bases'])
    ident=original['record_id']; variant=f'FB{basis_width}V{vertex_width}_{ident}'
    out=FORMAL/'PackingCertificates/Algebraic/Generated/Records/Chunked'/variant
    ns='PackingCertificates.Algebraic.Generated.Records.Chunked.'+variant
    oldns='PackingCertificates.Algebraic.Generated.Records.'+ident
    files=[]

    def emit(name, imports, body, audits, role, **coverage):
        p=out/(name+'.lean')
        text=['import '+x for x in imports]+['','set_option maxRecDepth 1000000',
            'set_option maxHeartbeats 0','',f'namespace {ns}',
            'open PackingCertificates.Rational (allFin allFin_eq_true)',
            'open PackingCertificates.Algebraic.Packing',
            'open PackingCertificates.Algebraic.Fragment3D','']+body+['']
        text += ['#print axioms '+x for x in audits]+[f'end {ns}']
        raw=bytes_of(text)
        if write:
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        elif not p.is_file() or p.read_bytes()!=raw:
            raise ValueError('Fragment differs from deterministic transcription '+rel(p))
        item=dict(path=rel(p),module=module(p),sha256=hashlib.sha256(raw).hexdigest(),
            role=role,expected_audits=[ns+'.'+x for x in audits],**coverage)
        files.append(item)
        return item['module']

    original_text=source.read_text(encoding='utf8')
    prefix=original_text.split('theorem source_checked :',1)[0]
    if prefix==original_text: raise ValueError('Unrecognized original proof boundary')
    prefix=prefix.replace(oldns,ns).replace('set_option maxRecDepth 0','set_option maxRecDepth 1000000')
    prefix=prefix.replace('def certificate :','noncomputable def certificate :')
    # Prefix carries the original scale/root-literal proofs and all raw fields.
    data=out/'Data.lean';raw=(prefix+'\nend '+ns+'\n').replace('\n','\r\n').encode('utf8')
    if write:out.mkdir(parents=True,exist_ok=True);data.write_bytes(raw)
    elif not data.is_file()or data.read_bytes()!=raw:raise ValueError('Changed exact raw Data fragment '+rel(data))
    files.append(dict(path=rel(data),module=module(data),sha256=hashlib.sha256(raw).hexdigest(),role='data',expected_audits=[]))
    data_module=module(data)
    imports=[data_module,HELPER]

    # A source block is independent of expensive interval/basis arithmetic.
    template_original=original_text.split('theorem templates_checked :',1)[1].split('theorem placements_checked :',1)[0]
    body=['theorem source_checked : certificate.sourceCheck = true := by decide +kernel','',
        'theorem templates_checked :'+template_original.rstrip(),'']
    emit('Sources',imports,body,['source_checked','templates_checked'],'sources',piece_indices=list(range(n)))

    br=split_ranges(b,basis_width);bnames=[];bmodules=[]
    for q,(lo,length) in enumerate(br):
        name=f'bases_range_{q}';bnames.append(name)
        bmodules.append(emit(f'Basis{q:04d}',imports,[
            f'theorem {name} : rangeCheck {lo} {length} (by decide) (basisItemCheck certificate) = true := by decide +kernel'],
            [name],'basis',basis_indices=list(range(lo,lo+length))))
    body=['theorem bases_checked : certificate.basisCheck = true := by',
        '  apply basisCheck_of_items','  intro z']+range_assembly('z',br,bnames)
    bases_module=emit('Bases',imports+bmodules,body,['bases_checked'],'basis_assembly')

    vr=split_ranges(k,vertex_width);piece_modules=[]
    for i in range(n):
        vnames=[];vmodules=[]
        for q,(lo,length) in enumerate(vr):
            name=f'vertices_{i}_range_{q}';vnames.append(name)
            vmodules.append(emit(f'Vertices{i:03d}_{q:04d}',imports,[
                f'theorem {name} : rangeCheck {lo} {length} (by decide)',
                f'    (fun p => certificate.placedCheck {i} p && certificate.vertexContainmentCheck {i} p) = true := by decide +kernel'],
                [name],'vertices',vertex_indices=[[i,p]for p in range(lo,lo+length)]))
        body=[f'theorem vertices_piece_{i} (p : Fin {k}) :',
            f'    (certificate.placedCheck {i} p && certificate.vertexContainmentCheck {i} p) = true := by']+range_assembly('p',vr,vnames)
        piece_modules.append(emit(f'Vertices{i:03d}',imports+vmodules,body,[f'vertices_piece_{i}'],'vertices_assembly'))

    pair_modules=[]
    for i in range(n):
        for j in range(i+1,n):
            names=[];modules=[]
            for q,(lo,length) in enumerate(vr):
                name=f'pair_{i}_{j}_range_{q}';names.append(name)
                modules.append(emit(f'Pair{i:03d}_{j:03d}_{q:04d}',imports,[
                    f'theorem {name} : rangeCheck {lo} {length} (by decide)',
                    f'    (fun p => pairLeftCheck certificate {i} {j} p && pairRightCheck certificate {i} {j} p) = true := by decide +kernel'],
                    [name],'pair_vertices',pair_vertex_indices=[[i,j,p]for p in range(lo,lo+length)]))
            body=[f'theorem pair_vertices_{i}_{j} (p : Fin {k}) :',
                f'    (pairLeftCheck certificate {i} {j} p && pairRightCheck certificate {i} {j} p) = true := by']+range_assembly('p',vr,names)+['',
                f'theorem pair_{i}_{j} : certificate.pairCheck {i} {j} = true := by',
                '  apply pairCheck_of_vertices','  · decide +kernel',
                f'  · intro p; exact (Bool.and_eq_true_iff.mp (pair_vertices_{i}_{j} p)).1',
                f'  · intro p; exact (Bool.and_eq_true_iff.mp (pair_vertices_{i}_{j} p)).2']
            pair_modules.append(emit(f'Pair{i:03d}_{j:03d}',imports+modules,body,[f'pair_{i}_{j}'],'pair_assembly'))

    body=[]
    for name,fn,part in [('placements_checked','placementCheck_of_vertices',1),('containment_checked','containmentCheck_of_vertices',2)]:
        prop='placementCheck'if part==1 else'containmentCheck'
        body+=['',f'theorem {name} : certificate.{prop} = true := by',f'  apply {fn}',
            '  intro i p; fin_cases i']
        body += [f'  · exact (Bool.and_eq_true_iff.mp (vertices_piece_{i} p)).{part}'for i in range(n)]
    body+=['','theorem pairs_checked : certificate.pairsCheck = true := by',
        '  apply pairsCheck_of_pairs','  intro i j hij; fin_cases i <;> fin_cases j <;> try (norm_num at hij)']
    # Concrete Fin comparisons are discharged before selecting the opaque proof.
    body += ['  all_goals first']
    body += [f'    | exact pair_{i}_{j}'for i in range(n)for j in range(i+1,n)]
    body+=['','theorem checked : certificate.check = true := by',
        '  simp only [Certificate.check,source_checked,templates_checked,placements_checked,bases_checked,containment_checked,pairs_checked] <;> rfl','',
        'theorem valid : certificate.Valid := certificate.check_sound checked',
        'theorem proper_orientation (i) : Matrix.det (fun a z => (certificate.rotation i a z : ℝ)) = 1 := certificate.proper_rotation checked i','']
    aggregate=emit('Aggregate',imports+[files[1]['module'],bases_module]+piece_modules+pair_modules,
        body,['valid','proper_orientation'],'aggregate')
    result=dict(original)
    result.update(generated_module=files[-1]['path'],generated_source_sha256=files[-1]['sha256'],
        expected_declaration=ns+'.valid',
        original_registry_row=original,fragmentation=dict(schema='3d-proof-fragments-v1',basis_width=basis_width,
            vertex_width=vertex_width,namespace=ns,basis_count=b,vertex_count=k,piece_count=n,files=files),
        fragment_generator_path=rel(Path(__file__)),fragment_generator_sha256=sha(Path(__file__)),
        status='FRAGMENTED_NOT_LEAN_VERIFIED')
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only',nargs='*');ap.add_argument('--basis-width',type=int,default=1)
    ap.add_argument('--vertex-width',type=int,default=8)
    ap.add_argument('--registry',type=Path,default=REGISTRY)
    ap.add_argument('--output',type=Path,default=HERE/'generated-fragmented-3d-pilots-registry.json')
    args=ap.parse_args();registry=read(args.registry)
    records=[r for r in registry['records']if not args.only or r['record_id']in args.only]
    if args.only and set(args.only)-{r['record_id']for r in records}:ap.error('Unknown record ID')
    rendered=[generate(r,args.basis_width,args.vertex_width)for r in records]
    out=dict(schema='3d-fragmented-packing-registry-v1',status='NOT_LEAN_VERIFIED',
        original_registry_path=rel(args.registry),original_registry_sha256=sha(args.registry),
        canonical_data_modules=registry['canonical_data_modules'],records=rendered)
    args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(records=len(rendered),modules=sum(len(r['fragmentation']['files'])for r in rendered),output=rel(args.output))))


if __name__=='__main__':main()
