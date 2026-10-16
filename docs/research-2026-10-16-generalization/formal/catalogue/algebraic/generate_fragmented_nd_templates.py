#!/usr/bin/env python3
"""Optional bounded proofs for large exact ND canonical vertex templates.

This isolated alternative retains the exact original TemplateData fields.  Its
noncomputable data constant avoids native code generation; all coordinate
enclosures are still reduced and checked by Lean's kernel in finite blocks.
No published canonical source is modified.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from fractions import Fraction
from pathlib import Path
from generate_fragmented_nd_pilots import range_assembly,split_ranges,bytes_of
from geometry_intervals import rat,interval

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parents[1]
NS='PackingCertificates.Algebraic.Generated.ND.Records.FastCanonical'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(FORMAL).as_posix()
def mod(p):return rel(p)[:-5].replace('/','.')


def generate(name,width=32,write=True):
    source=FORMAL/'PackingCertificates/Algebraic/Generated/ND'/(name+'.lean')
    text=source.read_text(encoding='utf8')
    shape=re.search(r'def '+re.escape(name)+r' : TemplateData (\d+) (\d+) where',text)
    if not shape:raise ValueError('Unrecognized canonical TemplateData declaration')
    d,k=map(int,shape.groups())
    if width<1:raise ValueError('Coordinate proof width must be positive')
    # Bounded path depth also keeps captured log paths portable on Windows.
    out=FORMAL/'PackingCertificates/Algebraic/CN'/(f'V{width}_{name}')
    files=[]
    geometry=json.loads((HERE/'geometry-intervals-nd.json').read_text(encoding='utf8'))
    template=geometry['templates'][name]
    coeff=template['coefficients']
    if any(len(v)!=d or any(len(a)!=2 for a in v)for v in coeff):
        raise ValueError('Expected exact quadratic coordinates in every dimension')
    def key(v):return tuple(tuple(Fraction(x)for x in a)for a in v)
    lookup={key(v):i for i,v in enumerate(coeff)}
    opposite=[]
    for v in coeff:
        negative=tuple(tuple(-Fraction(x)for x in a)for a in v)
        if negative not in lookup:raise ValueError('Canonical antipodal vertex absent')
        opposite.append(lookup[negative])
    if any(opposite[opposite[i]]!=i for i in range(k)):
        raise ValueError('Proposed canonical antipodal map is not involutive')

    def emit(stem,imports,body,audits,role,**coverage):
        p=out/(stem+'.lean')
        rows=['import '+x for x in imports]+['','set_option maxRecDepth 1000000','set_option maxHeartbeats 0',
            '',f'namespace {NS}','open PackingCertificates.Rational',
            'open PackingCertificates.Algebraic.FragmentND',
            'open PackingCertificates.Algebraic.TemplateFragments','']+body+['']
        rows+=['#print axioms '+a for a in audits]+[f'end {NS}']
        raw=bytes_of(rows)
        if write:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        elif not p.is_file()or p.read_bytes()!=raw:raise ValueError('Changed canonical proof fragment '+rel(p))
        files.append(dict(path=rel(p),module=mod(p),sha256=hashlib.sha256(raw).hexdigest(),role=role,
            expected_audits=[NS+'.'+a for a in audits],**coverage))
        return mod(p)

    def arr(values,render):return '#['+', '.join(render(v)for v in values)+']'
    def pair(x):return '⟨'+rat(x[0])+', '+rat(x[1])+'⟩'
    original_fields={line.strip().split(' := ',1)[0]:line.strip().split(' := ',1)[1]
        for line in text.splitlines()if line.startswith('  ')and' := 'in line}
    rawname=name+'_raw';intname=name+'_intervals';oppname=name+'_opposite_array'
    data_width=32
    def chunks(values):return [values[q:q+data_width]for q in range(0,len(values),data_width)]
    count=len(chunks(coeff))
    rawrow=f'(({rawname}.getD (j.val/{data_width}) #[]).getD (j.val%{data_width}) #[])'
    introw=f'(({intname}.getD (j.val/{data_width}) #[]).getD (j.val%{data_width}) #[])'
    opprow=f'({oppname}.getD (j.val/{data_width}) #[])'
    body=[f'noncomputable def {rawname} : Array (Array (Array (ℚ × ℚ))) := '+arr(chunks(coeff),lambda ch:arr(ch,lambda v:arr(v,pair))),
        f'noncomputable def {intname} : Array (Array (Array Interval)) := '+arr(chunks(template['vertex_intervals']),lambda ch:arr(ch,lambda v:arr(v,interval))),
        f'noncomputable def {oppname} : Array (Array (Fin {k})) := '+arr(chunks(opposite),lambda ch:arr(ch,str)),'',
        f'noncomputable def {name}_rawCoordinates (j : Fin {k}) (a : Fin {d}) : ℚ × ℚ :=',
        f'  {rawrow}.getD a.val (0,0)','',
        f'noncomputable def {name} : TemplateData {d} {k} where',
        '  rootSpec := '+original_fields['rootSpec'],
        f'  coefficients := fun j a => [({name}_rawCoordinates j a).1,({name}_rawCoordinates j a).2]',
        '  normalizerPolynomial := '+original_fields['normalizerPolynomial'],
        '  normalizerSqrtInterval := '+original_fields['normalizerSqrtInterval'],
        f'  vertexIntervals := fun j a => {introw}.getD a.val (Interval.point 0)','',
        f'theorem {name}_input_sizes : {rawname}.size = {count} ∧ {intname}.size = {count} ∧ {oppname}.size = {count} :=',
        '  ⟨rfl,rfl,rfl⟩','',
        f'noncomputable def {name}_shapeCheck (j : Fin {k}) : Bool := decide',
        f'    ({rawrow}.size = {d} ∧ {introw}.size = {d} ∧ j.val%{data_width} < {opprow}.size)','',
        f'theorem {name}_normalization_checked : {name}.normalizationCheck = true := by decide +kernel','',
        f'noncomputable def {name}_opposite (j : Fin {k}) : Fin {k} := {opprow}.getD (j.val%{data_width}) 0']
    data=emit('Data',['PackingCertificates.Algebraic.Generated.ND.RootData',
        'PackingCertificates.Algebraic.TemplateFragments'],body,
        [name+'_normalization_checked',name+'_input_sizes'],'canonical_data')
    ranges=split_ranges(k,width);blocks=[];names=[]
    for q,(lo,length)in enumerate(ranges):
        label=f'{name}_vertices_range_{q}';names.append(label)
        blocks.append(emit(f'Vertices{q:04d}',[data],[
            f'theorem {label} : rangeCheck {lo} {length} (by decide)',
            f'    (fun j => allFin {d} ({name}.coordinateCheck j) &&',
            f'      (antipodalItemCheck {name} {name}_opposite 2 j && {name}_shapeCheck j)) = true := by decide +kernel'],
            [label],'canonical_vertices',canonical_vertex_indices=list(range(lo,lo+length))))
    body=[f'theorem {name}_point_checked (j : Fin {k}) :',
        f'    (allFin {d} ({name}.coordinateCheck j) && (antipodalItemCheck {name} {name}_opposite 2 j && {name}_shapeCheck j)) = true := by']+range_assembly('j',ranges,names)+['',
        f'theorem {name}_vertices_checked : {name}.verticesCheck = true := by',
        f'  change allFin {k} (fun j => allFin {d} ({name}.coordinateCheck j)) = true',
        '  apply allFin_eq_true.mpr','  intro j',
        f'  exact (Bool.and_eq_true_iff.mp ({name}_point_checked j)).1','',
        f'theorem {name}_centroid_checked : {name}.centroidCheck 2 = true :=',
        f'  centroidCheck_of_antipodal {name} {name}_opposite 2 (fun j =>',
        f'    (Bool.and_eq_true_iff.mp ((Bool.and_eq_true_iff.mp ({name}_point_checked j)).2)).1)','',
        f'theorem {name}_row_sizes : allFin {k} {name}_shapeCheck = true :=',
        f'  allFin_eq_true.mpr (fun j => (Bool.and_eq_true_iff.mp ((Bool.and_eq_true_iff.mp ({name}_point_checked j)).2)).2)']
    final=emit('Export',[data]+blocks,body,[name+'_normalization_checked',name+'_vertices_checked',name+'_centroid_checked',name+'_row_sizes'],'canonical_assembly')
    return dict(name=name,dimension=d,vertex_count=k,width=width,
        original_path=rel(source),original_sha256=sha(source),module=final,
        namespace=NS,files=files,status='GENERATED_NOT_LEAN_VERIFIED')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only',nargs='+',required=True);ap.add_argument('--width',type=int,default=32)
    ap.add_argument('--output',type=Path,default=HERE/'fragmented-nd-templates-plan.json')
    args=ap.parse_args();plans=[generate(name,args.width)for name in args.only]
    args.output.write_text(json.dumps(dict(schema='nd-canonical-fragments-v1',templates=plans),indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(templates=len(plans),modules=sum(len(p['files'])for p in plans))))


if __name__=='__main__':main()
