"""Exact chunked-Array representation of large finite ND witness functions.

Only storage/indexing changes. Every rational literal and original finite index
is rendered from the same frozen proposal; no geometric value is recomputed.
Array chunk sizes are independently checked by the Lean kernel.
"""
from __future__ import annotations
import re
from fractions import Fraction
from geometry_intervals import rat,interval


def arr(values,depth,render):
    return '#['+', '.join(render(v)if depth==1 else arr(v,depth-1,render)for v in values)+']'


def fast_rat(value):
    q=Fraction(value)
    integer='(Int.ofNat '+str(q.numerator)+')'if q.numerator>=0 else'(Int.negSucc '+str(-q.numerator-1)+')'
    return '(mkRat '+integer+' '+str(q.denominator)+')'


def fast_interval(value):return '⟨'+fast_rat(value[0])+', '+fast_rat(value[1])+'⟩'


def rewrite(prefix,c,canonical_plans,basis_width=8,point_width=32,fast_rationals=True,lazy_chunks=False):
    d,n=c['dimension'],c['n'];k=len(c['placed_vertex_intervals'][0]);l=None
    bases=c['container_bases'];b=len(bases)
    # Containment basis labels are arbitrary proposal ids, not assumed indices.
    mapping={z['id']:i for i,z in enumerate(bases)}
    declarations=[];checks=[];shape_proofs=[];audit_names=[]
    render_rat=fast_rat if fast_rationals else rat
    render_interval=fast_interval if fast_rationals else interval

    def field(name,values,item_depth,item_type,render,width,args,flat_index,default):
        total=len(values);chunks=[values[q:q+width]for q in range(0,total,width)]
        data='array_'+name
        typ=item_type
        for _ in range(item_depth+2):typ='Array ('+typ+')'
        if lazy_chunks:
            chunk_type=item_type
            for _ in range(item_depth+1):chunk_type='Array ('+chunk_type+')'
            typ='Array (Unit → '+chunk_type+')'
            value='#['+', '.join('(fun _ => '+arr(chunk,item_depth+1,render)+')'for chunk in chunks)+']'
            getter=f'(({data}.getD (({flat_index})/{width}) (fun _ => #[])) ())'
            size_getter=f'(({data}.getD q.val (fun _ => #[])) ())'
        else:
            value=arr(chunks,item_depth+2,render)
            getter=f'({data}.getD (({flat_index})/{width}) #[])'
            size_getter=f'({data}.getD q.val #[])'
        declarations.append(f'noncomputable def {data} : {typ} := '+value)
        decoder=f'({getter}.getD (({flat_index})%{width}) '+default+')'
        # Additional coordinate indices select only within one small item.
        for binder,fallback in args[1]:decoder='('+decoder+').getD '+binder+'.val '+fallback
        replacement='  '+name+' := fun '+args[0]+' => '+decoder
        pattern=r'^  '+re.escape(name)+r' := .*?$'
        nonlocal prefix
        prefix,count=re.subn(pattern,lambda _:replacement,prefix,count=1,flags=re.M)
        if count!=1:raise ValueError('Missing original large certificate field '+name)
        checks.append(f'{data}.size = {len(chunks)}')
        shape_proofs.append('by rfl')
        # Bound each source chunk's item count without reducing its numbers.
        checks.append(f'allFin {len(chunks)} (fun q => decide ({size_getter}.size = min {width} ({total}-q.val*{width}))) = true')
        shape_proofs.append('by apply allFin_eq_true.mpr; intro q; fin_cases q <;> rfl')

    flattened=lambda rows:[v for row in rows for v in row]
    field('placedIntervals',flattened(c['placed_vertex_intervals']),1,'Interval',render_interval,point_width,
        ('i p a',[('a','(Interval.point 0)')]),f'i.val*{k}+p.val','#[]')
    field('normalizedIntervals',flattened(c['normalized_vertex_intervals']),1,'Interval',render_interval,point_width,
        ('i p a',[('a','(Interval.point 0)')]),f'i.val*{k}+p.val','#[]')
    # Basis-index element type is inferred explicitly from the canonical count.
    geometry_count=None
    for plan in canonical_plans:
        if plan['name']=='container_'+c['problem']:geometry_count=plan['vertex_count']
    if geometry_count is None:
        from generate_nd_pilots import T
        geometry_count=T['container_'+c['problem']]['vertex_count']
    field('basisIndices',[z['indices']for z in bases],1,f'Fin {geometry_count}',str,basis_width,
        ('z a',[('a','0')]),'z.val','#[]')
    def pair(v):return '⟨'+render_rat(v[0])+', '+render_rat(v[1])+'⟩'
    field('basisInverses',[z['inverse_coefficients']for z in bases],2,'ℚ × ℚ',pair,basis_width,
        ('z i j',[('i','#[]'),('j','(0,0)')]),'z.val','#[]')
    field('basisInverseIntervals',[z['inverse_intervals']for z in bases],2,'Interval',render_interval,basis_width,
        ('z i j',[('i','#[]'),('j','(Interval.point 0)')]),'z.val','#[]')
    field('vertexBasis',flattened([[mapping[z['basis']]for z in row]for row in c['containment']]),0,f'Fin {b}',str,point_width,
        ('i p',[]),f'i.val*{k}+p.val','0')
    field('epsilon',flattened([[z['epsilon']for z in row]for row in c['containment']]),0,'ℚ',render_rat,point_width,
        ('i p',[]),f'i.val*{k}+p.val','0')
    # The large canonical polynomial is *defined* from these same exact pairs;
    # this pointwise identity needs no enormous finite decision procedure.
    for plan in canonical_plans:
        if plan['name']=='container_'+c['problem']:
            qualified=plan['namespace']+'.'+plan['name']+'_rawCoordinates'
            prefix,count=re.subn(r'^  containerRaw := .*?$',lambda _:'  containerRaw := '+qualified,prefix,count=1,flags=re.M)
            if count!=1:raise ValueError('Missing canonical raw-coordinate field')
            prefix=prefix.replace('  rawCoefficients := by decide +kernel','  rawCoefficients := by intro j a; rfl')
    marker='noncomputable def certificate :'
    if marker not in prefix:raise ValueError('Missing exact noncomputable certificate boundary')
    prefix=prefix.replace(marker,'\n\n'.join(declarations)+'\n\n'+marker,1)
    # All dimensions/index coverage remain typed by the original Certificate.
    predicate=' ∧\n    '.join(checks)
    proof=shape_proofs[-1]
    for term in reversed(shape_proofs[:-1]):proof='And.intro ('+term+') ('+proof+')'
    prefix+='\ntheorem chunk_input_sizes : '+predicate+' := '+proof+'\n'
    return prefix,['chunk_input_sizes']
