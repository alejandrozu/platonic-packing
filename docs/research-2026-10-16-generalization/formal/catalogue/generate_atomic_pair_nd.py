#!/usr/bin/env python3
"""Alternative exact ND route with independently decided unordered pairs.

The ordinary fine route decides each entire pair row. This route retains the
same data and eight-vertex fragments, but decides each pair separately before
assembling its row from opaque lemmas. It does not alter the active CI emitter.
Generation is not a successful proof and performs no compiler invocation.
"""
import re
import generate_chunked_nd as chunked
import generate_nd_lean as ordinary
from generate_fine_chunked_nd import header

def _atomic_generate(c,vertex_block_size=8):
    if vertex_block_size<1:
        raise ValueError('vertex_block_size must be positive')
    old_name,old_files=chunked.generate(c,per_vertex=True,per_pair=True)
    ordinary_name,_=ordinary.generate(c)
    name='P'+ordinary_name
    old_ns='PackingCertificates.Catalogue.'+old_name
    namespace='PackingCertificates.Catalogue.'+name
    old={short:text.replace(old_ns,namespace) for short,text,_,_ in old_files}
    n,k=c['n'],len(c['template_vertices'])
    files=[dict(short='Data',text=old['Data'],kind='data',piece_indices=None,
        vertex_indices=[],fragment_role='data',
        audits=[namespace+'.'+p for p in ('edge_normalization','template_sizes','input_sizes')])]
    aggregate_imports=[]
    for i in range(n):
        source_block=old[f'Block{i:03d}']
        first=source_block.index(f'theorem source_piece_{i} :')
        first_vertex=source_block.index(f'theorem vertex_{i}_0 :')
        first_assembly=source_block.index(f'theorem vertices_piece_{i} :')
        source_body=source_block[first:first_vertex]
        pair_matches=re.findall(r'^theorem pair_(\d+)_(\d+)\s*:',source_body,re.M)
        if [(int(a),int(b))for a,b in pair_matches]!=[(i,j)for j in range(i+1,n)]:
            raise ValueError('Atomic pair sequence does not cover the source row: '+c['record_id'])
        vertex_body=source_block[first_vertex:first_assembly]
        assembly_body=source_block[first_assembly:].split('#print axioms',1)[0]
        source_name=f'Source{i:03d}'
        source_audits=[namespace+'.'+p+'_'+str(i) for p in ('source_piece','gram_piece','pair_row')]
        source_text=header([namespace+'.Data'],namespace)+source_body+'\n'+'\n'.join(
            '#print axioms '+a for a in source_audits)+f'\nend {namespace}\n'
        files.append(dict(short=source_name,text=source_text,kind='proof_block',
            piece_indices=[i],vertex_indices=[],fragment_role='source',audits=source_audits))
        aggregate_imports.append(namespace+'.'+source_name)
        matches=list(re.finditer(r'^theorem vertex_(\d+)_(\d+)\s*:.*?(?=^theorem\s|\Z)',vertex_body,re.M|re.S))
        if [(int(m.group(1)),int(m.group(2))) for m in matches]!=[(i,p) for p in range(k)]:
            raise ValueError('Unexpected atomic vertex sequence: '+c['record_id'])
        vertex_imports=[]
        for start in range(0,k,vertex_block_size):
            stop=min(k,start+vertex_block_size)
            block_index=start//vertex_block_size
            vertex_name=f'Vertex{i:03d}_{block_index:03d}'
            vertex_imports.append(namespace+'.'+vertex_name)
            body='\n'.join(m.group(0) for m in matches[start:stop])
            audits=[namespace+f'.vertex_{i}_{p}' for p in range(start,stop)]
            text=header([namespace+'.Data'],namespace)+body+'\n'+'\n'.join(
                '#print axioms '+a for a in audits)+f'\nend {namespace}\n'
            files.append(dict(short=vertex_name,text=text,kind='proof_block',piece_indices=[],
                vertex_indices=[[i,p] for p in range(start,stop)],fragment_role='vertices',audits=audits))
        assembly_name=f'Assemble{i:03d}'
        assembly_audits=[namespace+f'.vertices_piece_{i}']
        assembly_text=header(vertex_imports,namespace)+assembly_body+'\n'+(
            '#print axioms '+assembly_audits[0])+f'\nend {namespace}\n'
        files.append(dict(short=assembly_name,text=assembly_text,kind='proof_block',piece_indices=[],
            vertex_indices=[],fragment_role='vertex_assembly',audits=assembly_audits))
        aggregate_imports.append(namespace+'.'+assembly_name)
    aggregate_tail=old[''].split('-- Original source:',1)[1]
    aggregate='\n'.join('import '+m for m in aggregate_imports)+'\n\n-- Original source:'+aggregate_tail
    files.append(dict(short='',text=aggregate,kind='aggregate',piece_indices=None,vertex_indices=[],
        fragment_role='aggregate',audits=[namespace+'.'+p for p in ('source_valid','packing','proper_orientation')]))
    return name,files


def generate(c, vertex_block_size=8, pair_block_size=4):
    """Bound both vertex and pair decisions in separate compiler processes.

    A source/Gram/row module imports its small pair modules and assembles the
    exact original allFin pair row from their opaque atomic proofs. No accepted
    predicate, coordinate, scale or plane changes.
    """
    if pair_block_size < 1:
        raise ValueError('pair_block_size must be positive')
    name, entries = _atomic_generate(c, vertex_block_size)
    namespace = 'PackingCertificates.Catalogue.' + name
    result = []
    for entry in entries:
        if entry['fragment_role'] != 'source':
            result.append(entry)
            continue
        i = entry['piece_indices'][0]
        matches = list(re.finditer(r'^theorem pair_(\d+)_(\d+)\s*:.*?(?=^theorem\s|\Z)',
            entry['text'].split('#print axioms', 1)[0], re.M | re.S))
        if [(int(m[1]), int(m[2])) for m in matches] != [(i,j) for j in range(i+1,c['n'])]:
            raise ValueError('Missing or unordered pair obligation')
        imported = []
        for first in range(0, len(matches), pair_block_size):
            group = matches[first:first+pair_block_size]
            short = f'Pairs{i:03d}_{first//pair_block_size:03d}'
            imported.append(namespace + '.' + short)
            audits = [namespace + f'.pair_{m[1]}_{m[2]}' for m in group]
            body = header([namespace + '.Data'], namespace) + '\n'.join(m.group(0) for m in group)
            body += '\n' + '\n'.join('#print axioms ' + a for a in audits) + f'\nend {namespace}\n'
            result.append(dict(short=short, text=body, kind='proof_block', piece_indices=[],
                vertex_indices=[], pair_indices=[[int(m[1]),int(m[2])] for m in group],
                fragment_role='pairs', audits=audits))
        source = entry['text']
        for m in matches:
            source = source.replace(m.group(0), '', 1)
        source = '\n'.join('import ' + n for n in imported) + '\n' + source
        result.append(dict(entry, text=source, pair_indices=[]))
    expected = {(i,j) for i in range(c['n']) for j in range(i+1,c['n'])}
    actual = [tuple(pair) for item in result for pair in item.get('pair_indices', [])]
    if len(actual) != len(expected) or set(actual) != expected:
        raise ValueError('Per-process pair fragments do not cover every unordered pair exactly once')
    return name, result
