"""Split exact large ND data into bounded, independently elaborated constants.

Each literal chunk is preserved verbatim. Imported groups only change storage;
source binding re-renders every byte and all numeric certificate checks remain.
"""
from __future__ import annotations
import re
import hashlib


def entries(array):
    if not array.startswith('#[')or not array.endswith(']'):raise ValueError('Expected exact array literal')
    text=array[2:-1]; result=[];start=0;depth=0
    for i,c in enumerate(text):
        if c in '[(⟨':depth+=1
        elif c in '])⟩':depth-=1
        elif c==','and depth==0:result.append(text[start:i].strip());start=i+1
    if depth:raise ValueError('Unbalanced exact array literal')
    if text.strip():result.append(text[start:].strip())
    return result


def split(prefix,ns,out,formal,write=True,group_width=4):
    if group_width<1:raise ValueError('Positive data group width required')
    lines=prefix.splitlines(); modules=[];files=[]
    first=next(i for i,z in enumerate(lines)if z.startswith('noncomputable def array_'))
    header=[z for z in lines[:first]if z.startswith(('import ','set_option ','namespace ','open '))]
    replaced=[]
    for line in lines:
        m=re.fullmatch(r'noncomputable def (array_\w+) : (.+) := (.+)',line)
        if not m:replaced.append(line);continue
        name,typ,literal=m.groups(); chunks=entries(literal);lookups=[]
        default='(fun _ => #[])'if typ.startswith('Array (Unit →')else'#[]'
        for q,lo in enumerate(range(0,len(chunks),group_width)):
            group=chunks[lo:lo+group_width];decl=f'{name}_group_{q:03d}'
            p=out/(f'Input_{name[6:]}_{q:03d}.lean')
            value='#['+', '.join(group)+']'
            content='\n'.join(header+['',f'noncomputable def {decl} : {typ} := {value}','',f'#print axioms {decl}',f'end {ns}',''])
            raw=content.replace('\n','\r\n').encode('utf8')
            if write:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            elif not p.is_file()or p.read_bytes()!=raw:raise ValueError('Changed exact ND input module '+str(p))
            rel=p.relative_to(formal).as_posix();mod=rel[:-5].replace('/','.')
            modules.append(mod);files.append(dict(path=rel,module=mod,sha256=hashlib.sha256(raw).hexdigest(),role='auxiliary_data',
                data_field=name,data_chunk_indices=list(range(lo,lo+len(group))),expected_audits=[ns+'.'+decl]))
            lookups.extend(f'({decl}.getD {j} {default})'for j in range(len(group)))
        replaced.append(f'noncomputable def {name} : {typ} := #['+', '.join(lookups)+']')
    if not files:raise ValueError('No exact array declarations to split')
    return '\n'.join(['import '+m for m in modules]+replaced)+'\n',files
