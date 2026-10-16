"""Emit actual ND source-bound kernel instances; generation is not proof."""
from pathlib import Path
import argparse,hashlib,json
from geometry_intervals import rat,interval
from generate_3d import nested,filehash
from nd_geometry import parse_mq

HERE=Path(__file__).resolve().parent;FORMAL=HERE.parents[1]
G=json.loads((HERE/'geometry-intervals-nd.json').read_text(encoding='utf8'));T=G['templates']

def pair(x):return '⟨'+rat(x[0])+', '+rat(x[1])+'⟩'
def generate(path,write=True):
    path=Path(path).resolve();c=json.loads(path.read_text(encoding='utf8'));ident=c['record_id'];problem=c['problem']
    d,n=c['dimension'],c['n'];p='piece_'+c['piece'];v='container_'+problem;pt=T[p];ct=T[v];k=pt['vertex_count'];l=ct['vertex_count']
    bases=c['container_bases'];b=len(bases);mapping={z['id']:i for i,z in enumerate(bases)};r=ct['radicand'];spec=c['mu_spec']
    out=FORMAL/'PackingCertificates/Algebraic/Generated/ND/Records'/f'{ident}.lean';out.parent.mkdir(exist_ok=True)
    imports=['PackingCertificates.Algebraic.PackingND','PackingCertificates.Algebraic.RootSqrt',f'PackingCertificates.Algebraic.Generated.ND.{p}',f'PackingCertificates.Algebraic.Generated.ND.{v}']
    rows=['import '+x for x in imports]+['','set_option maxRecDepth 1000000','set_option maxHeartbeats 0','',
        f'namespace PackingCertificates.Algebraic.Generated.ND.Records.{ident}','','open PackingCertificates.Algebraic.PackingND','',
        'def nativeScale : QuadraticScale.Spec where',f'  rootSpec := nd_root{r}',f'  radicand := {rat(r)}',
        '  a := '+rat(spec['a']),'  b := '+rat(spec['b']),
        '  timesSqrtTwo := '+str(spec['times_sqrt_two']).lower(),'  d0 := '+rat(spec['d0']),'  d1 := '+rat(spec['d1']),
        '  sqrtTwoInterval := '+interval(spec['sqrt_two_interval']),'',
        'theorem native_scale_checked : nativeScale.check = true := by decide +kernel','',
        f'theorem native_mu_binding : {v}.normalization nd_root{r}_checked = nativeScale.mu nd_root{r}_checked :=',
        f'  (nativeScale.check_sound nd_root{r}_checked native_scale_checked).2','']
    literal=[]
    for radical,coefficient in sorted(parse_mq(c['native_mu']).items()):
        term='(('+rat(coefficient)+') : ℝ)'
        if radical!=1:term+=' * Real.sqrt '+str(radical)
        literal.append(term)
    rows+=[f'theorem native_mu_literal : nativeScale.mu nd_root{r}_checked = '+(' + '.join(literal)or'0')+' := by',
        '  have h10 : Real.sqrt (10 : ℝ) = Real.sqrt 2 * Real.sqrt 5 := by',
        '    rw [show (10 : ℝ) = 2*5 by norm_num,Real.sqrt_mul (by norm_num : (0 : ℝ) ≤ 2)]',
        f'  rw [nativeScale.mu_eq_sqrt_expression nd_root{r}_checked native_scale_checked]',
        '  norm_num [nativeScale,h10] <;> ring','',
        f'def certificate : Certificate {d} {n} {k} {l} {b} where',f'  piece := {p}',f'  container := {v}',
        f'  pieceRoot := nd_root{pt["radicand"]}_checked',f'  containerRoot := nd_root{r}_checked','  containerDegree := 2',
        '  scale := '+rat(c['scale']),'  containerCenter := '+nested(c['container_center'],1,rat),
        '  cayley := !['+', '.join('{ skew := '+nested(s,2,rat)+', signs := '+nested(ds,1,rat)+', inverse := '+nested(ai,2,rat)+', rotation := '+nested(R,2,rat)+' }'for s,ds,ai,R in zip(c['raw_skews'],c['diagonal_signs'],c['cayley_inverses'],c['rotations']))+']',
        '  rotation := '+nested(c['rotations'],3,rat),'  center := '+nested(c['centres'],2,rat),
        '  placedIntervals := '+nested(c['placed_vertex_intervals'],3,interval),'  normalizedIntervals := '+nested(c['normalized_vertex_intervals'],3,interval),
        '  basisIndices := '+nested([z['indices']for z in bases],2,str),'  radicand := '+rat(r),'  rootPolynomial := rfl',
        '  containerRaw := '+nested(ct['coefficients'],2,pair),'  rawCoefficients := by decide +kernel',
        '  basisInverses := '+nested([z['inverse_coefficients']for z in bases],3,pair),
        '  basisInverseIntervals := '+nested([z['inverse_intervals']for z in bases],3,interval),
        '  vertexBasis := '+nested([[mapping[z['basis']]for z in row]for row in c['containment']],2,str),
        '  epsilon := '+nested([[z['epsilon']for z in row]for row in c['containment']],2,rat)]
    planes=[[dict(normal=['0']*d,lower='0',upper='1')for _ in range(n)]for _ in range(n)]
    for z in c['planes']:planes[z['i']][z['j']]=z
    def pl(z):return '⟨'+nested(z['normal'],1,rat)+', '+rat(z['lower'])+', '+rat(z['upper'])+'⟩'
    rows+=['  separation := '+nested(planes,2,pl),'',
        'theorem source_checked : certificate.sourceCheck = true := by decide +kernel',
        'theorem templates_checked : certificate.templateCheck = true := by',
        f'  change ({p}.normalizationCheck && ({p}.verticesCheck && ({v}.normalizationCheck && ({v}.verticesCheck && {v}.centroidCheck 2)))) = true',
        '  simp only ['+', '.join([p+'_normalization_checked',p+'_vertices_checked',v+'_normalization_checked',v+'_vertices_checked',v+'_centroid_checked'])+'] <;> rfl',
        'theorem placements_checked : certificate.placementCheck = true := by decide +kernel',
        'theorem bases_checked : certificate.basisCheck = true := by decide +kernel',
        'theorem containment_checked : certificate.containmentCheck = true := by decide +kernel',
        'theorem pairs_checked : certificate.pairsCheck = true := by decide +kernel','',
        'theorem checked : certificate.check = true := by',
        '  simp only [Certificate.check,source_checked,templates_checked,placements_checked,bases_checked,containment_checked,pairs_checked] <;> rfl','',
        'theorem valid : certificate.Valid := certificate.check_sound checked','',
        '#print axioms valid','#print axioms native_mu_binding','#print axioms native_mu_literal',
        f'end PackingCertificates.Algebraic.Generated.ND.Records.{ident}','']
    rendered='\n'.join(rows).replace('\n','\r\n').encode('utf8')
    if write:out.write_bytes(rendered)
    elif not out.is_file()or out.read_bytes()!=rendered:raise ValueError('ND generated source not exact proposal transcription '+ident)
    return dict(record_id=ident,problem=problem,dimension=d,piece=c['piece'],container=c['container'],n=n,
        source_path=c['source_path'],source_sha256=c['source_sha256'],source_freeze=c['source_freeze'],
        proposal_path=path.relative_to(FORMAL).as_posix(),proposal_sha256=filehash(path),generated_module=out.relative_to(FORMAL).as_posix(),generated_source_sha256=filehash(out),
        expected_declaration=f'PackingCertificates.Algebraic.Generated.ND.Records.{ident}.valid',
        expected_mu_declarations=[f'PackingCertificates.Algebraic.Generated.ND.Records.{ident}.native_mu_binding',f'PackingCertificates.Algebraic.Generated.ND.Records.{ident}.native_mu_literal'],
        geometry_source_path='catalogue/algebraic/inputs/src/polytopes_nd.json',geometry_source_sha256=c['geometry_sha256'],
        geometry_intervals_path='catalogue/algebraic/geometry-intervals-nd.json',geometry_intervals_sha256=filehash(HERE/'geometry-intervals-nd.json'),
        canonical_template_modules=[f'PackingCertificates/Algebraic/Generated/ND/{p}.lean',f'PackingCertificates/Algebraic/Generated/ND/{v}.lean'],status='GENERATED_NOT_LEAN_VERIFIED')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only',nargs='*');a=ap.parse_args();records=[]
    for p in sorted((HERE/'witnesses_nd_pilots').glob('*.json')):
        if a.only and p.stem not in a.only:continue
        records.append(generate(p))
    canonical=[dict(module=p.relative_to(FORMAL).as_posix(),sha256=filehash(p))for p in sorted((FORMAL/'PackingCertificates/Algebraic/Generated/ND').glob('*.lean'))]
    registry=dict(schema='nd-quadratic-packing-registry-v1',status='GENERATION_NOT_FORMAL_VERIFICATION',canonical_data_modules=canonical,records=records)
    (HERE/'generated-nd-pilots-registry.json').write_bytes((json.dumps(registry,indent=2)+'\n').replace('\n','\r\n').encode('utf8'))
    print(json.dumps(dict(generated=len(records),status='NOT_LEAN_VERIFIED')))

if __name__=='__main__':main()
