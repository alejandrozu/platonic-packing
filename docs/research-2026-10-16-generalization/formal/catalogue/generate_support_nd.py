#!/usr/bin/env python3
"""Generate a disjoint ND support-checking variant; generation proves nothing.

The original raw Cayley data, centers, rotations, separating planes, template
references and barycentric witnesses are unchanged. Only the arithmetic proving
each pair is replaced with the proved support adapter. Extension dependencies
must be pinned and verified by any runner accepting these new modules.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

import generate_fine_chunked_nd as fine
import generate_chunked_nd as chunks
import generate_fragmented_nd as fragments
import generate_nd_lean as ordinary

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_source(c):
    piece, d, k = c['piece'], c['dimension'], len(c['template_vertices'])
    if piece in ('c8', 'hc5', 'hc6'):
        return f'''theorem template_support_bound :
    ∀ p : Fin {k}, ∀ a : Fin {d}, |record.placement.template p a| ≤ (1/2 : ℚ) := by decide +kernel

def supportModel : NDSupport.TemplateModel {d} {k} :=
  NDSupport.boxModel record.placement.template template_support_bound
'''
    if piece in ('c16', 'op5', 'op6'):
        return f'''theorem template_support_bound :
    ∀ p : Fin {k}, (∑ a, |record.placement.template p a|) ≤ (1 : ℚ) := by decide +kernel

def supportModel : NDSupport.TemplateModel {d} {k} :=
  NDSupport.crossModel (by decide) record.placement.template template_support_bound
'''
    return f'''def supportModel : NDSupport.TemplateModel {d} {k} :=
  NDSupport.finiteModel record.placement.template (by decide)
'''


def generate(c, vertex_block_size=8, use_fine=True):
    if use_fine:
        old_name, entries = fine.generate(c, vertex_block_size)
    else:
        old_name, files = chunks.generate(c, per_vertex=True)
        entries = [dict(short=short, text=text, kind=kind, piece_indices=indices)
                   for short, text, kind, indices in files]
    ordinary_name, _ = ordinary.generate(c)
    name = ('SF' + str(vertex_block_size) if use_fine else 'SC1') + ordinary_name
    old_ns, ns = 'PackingCertificates.Catalogue.' + old_name, 'PackingCertificates.Catalogue.' + name
    n = c['n']
    result = []
    for original in entries:
        entry = dict(original)
        text = entry['text'].replace(old_ns, ns)
        if entry['kind'] == 'data':
            text = 'import PackingCertificates.Extensions.NDBarySupport\n' + text
            text = text.replace('open PackingCertificates.Rational',
                'open PackingCertificates.Rational\nopen PackingCertificates.Extensions\nopen scoped BigOperators', 1)
            position = text.index('#print axioms')
            text = text[:position] + model_source(c) + '\n#print axioms supportModel\n' + text[position:]
        else:
            for i in entry.get('piece_indices') or []:
                pattern = rf'^theorem pair_row_{i}\s*:.*?(?=^theorem\s|^#print|^end\s)'
                replacement = f'''theorem pair_row_{i} :
    PackingCertificates.Extensions.NDBarySupport.pairRowCheck record supportModel ({i} : Fin {n}) = true := by decide +kernel

'''
                text, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.M | re.S)
                if count != 1:
                    raise ValueError('Missing pair row in generated source: ' + c['record_id'])
            if entry['kind'] == 'aggregate':
                pattern = r'^theorem pair_checked\s*:(.*?)\s*:= by.*?(?=^theorem\s)'
                match = re.search(pattern, text, re.M | re.S)
                if not match:
                    raise ValueError('Missing aggregate pair proof: ' + c['record_id'])
                fast_assembly = fragments.assemble_all('support_pairs_checked', n,
                    'fun i => PackingCertificates.Extensions.NDBarySupport.pairRowCheck record supportModel i', 'pair_row')
                proof = f'''{fast_assembly}
theorem pair_checked :{match.group(1)} := by
  apply allFin_eq_true.mpr
  intro i
  apply allFin_eq_true.mpr
  intro j
  by_cases hij : i < j
  · simp only [hij, if_true]
    apply PackingCertificates.Extensions.NDBarySupport.planeCheck_implies_vertex_check
      record supportModel rfl i j
    have hr := allFin_eq_true.mp support_pairs_checked i
    have hp := allFin_eq_true.mp hr j
    simpa only [hij, if_true] using hp
  · simp [hij]

'''
                text = text[:match.start()] + proof + text[match.end():]
        entry['text'] = text
        audits = re.findall(r'^\s*#print axioms\s+([A-Za-z0-9_.]+)', text, re.M)
        entry['audits'] = [a if '.' in a else ns + '.' + a for a in audits]
        result.append(entry)
    return name, result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only', nargs='+', required=True)
    ap.add_argument('--vertex-block-size', type=int, default=8)
    ap.add_argument('--coarse', action='store_true')
    ap.add_argument('--manifest', default='generated-support-nd-modules.json')
    args = ap.parse_args()
    plans = []
    for path in sorted((HERE / 'witnesses_nd').glob('*.json')):
        c = json.loads(path.read_text(encoding='utf8'))
        if c['record_id'] not in args.only:
            continue
        name, entries = generate(c, args.vertex_block_size, not args.coarse)
        ns = 'PackingCertificates.Catalogue.' + name
        directory = FORMAL / 'PackingCertificates' / 'Catalogue' / name
        directory.mkdir(parents=True, exist_ok=True)
        steps = []
        for entry in entries:
            short = entry['short']
            out = directory / (short + '.lean') if short else directory.with_suffix('.lean')
            out.write_text(entry['text'], encoding='utf8', newline='\n')
            step = dict(id='support_' + name + ('_' + short.lower() if short else ''),
                        record_id=c['record_id'], n=c['n'], dimension=c['dimension'],
                        path=str(out.relative_to(FORMAL)).replace('\\', '/'),
                        module=ns + ('.' + short if short else ''), kind=entry['kind'],
                        piece_indices=entry.get('piece_indices'), expected_audits=entry['audits'],
                        generated_source_sha256=sha(out))
            for key in ('vertex_indices', 'fragment_role'):
                if key in entry:
                    step[key] = entry[key]
            steps.append(step)
        extensions = [FORMAL / 'PackingCertificates/Extensions' / (name + '.lean')
                      for name in ('NDSupport', 'NDBarySupport')]
        row = dict(id='support_' + name, record_id=c['record_id'], n=c['n'], dimension=c['dimension'],
                   module=ns, path=steps[-1]['path'], original_source_path=c['source_path'],
                   original_json_sha256=c['source_sha256'], original_witness_sha256=sha(path),
                   original_geometry_path='src/polytopes_nd.json', original_geometry_sha256=c['geometry_sha256'],
                   steps=steps, dependencies=[{k: s[k] for k in ('module', 'path', 'generated_source_sha256')} for s in steps[:-1]],
                   extension_dependencies=[dict(path=str(p.relative_to(FORMAL)).replace('\\', '/'), source_sha256=sha(p),
                       olean_sha256=sha(p.with_suffix('.olean')) if p.with_suffix('.olean').is_file() else None) for p in extensions],
                   proof_status='Unverified generated source; requires successful builds and extension-dependency audit')
        if not args.coarse:
            row.update(fine_vertex_coverage=True, vertex_count=len(c['template_vertices']), vertex_block_size=args.vertex_block_size)
        plans.append(row)
    if len(plans) != len(set(args.only)):
        raise ValueError('Some requested ND identifiers were not found')
    out = HERE / args.manifest
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plans, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(generated=len(plans), steps=sum(len(r['steps']) for r in plans), manifest=out.name,
                          proof_status='Unverified generated source')))


if __name__ == '__main__':
    main()
