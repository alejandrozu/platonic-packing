#!/usr/bin/env python3
"""Emit actual high-dimensional packing proofs; success requires Lean builds."""
import argparse
import json
from pathlib import Path
from generate_lean import rat,vec,matrix,arr,plane,module_name

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent


def generate_templates():
    geom=json.loads((HERE/'inputs/src/polytopes_nd.json').read_text())
    names=('c8','c16','c24','hc5','op5','hc6','op6')
    parts=['import PackingCertificates.Rational\nnamespace PackingCertificates.TemplateData\nopen PackingCertificates.Rational\n']
    for name in names:
        p=geom[name]
        parts.append(f'def {name} : Array (QPoint {p["dim"]}) := {arr([vec(v) for v in p["V"]])}\n')
    parts.append('end PackingCertificates.TemplateData\n')
    (FORMAL/'PackingCertificates/TemplateData.lean').write_text('\n'.join(parts),encoding='utf8',newline='\n')


def generate(c):
    d,n=c['dimension'],c['n'];k,l=len(c['template_vertices']),len(c['container_vertices']);t=c['barycentric_width']
    name=module_name(c['record_id'])
    sources=[]
    for S,D,A,R in zip(c['raw_skews'],c['diagonal_signs'],c['cayley_inverses'],c['rotations']):
        sources.append('{ skew := '+matrix(S)+', signs := '+vec(D)+', inverse := '+matrix(A)+', rotation := '+matrix(R)+' }')
    index={(p['i'],p['j']):p for p in c['planes']}
    assert len(index)==n*(n-1)//2
    planes=arr([arr([plane(index[i,j]) for j in range(i+1,n)]) for i in range(n)])
    inds=arr([arr(['!['+', '.join(str(int(z)) for z in v)+']' for v in row]) for row in c['indices']])
    weights=arr([arr([vec(v) for v in row]) for row in c['weights']])
    text=f'''import PackingCertificates.Barycentric
import PackingCertificates.Cayley
import PackingCertificates.TemplateData

-- Exact source: {c['source_path']}
-- JSON SHA256: {c['source_sha256']}
-- Canonical geometry SHA256: {c['geometry_sha256']}
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.{name}
open PackingCertificates.Rational

def rawSources : Array (Cayley.Certificate {d}) := {arr(sources)}
def rawCenters : Array (QPoint {d}) := {arr([vec(v) for v in c['centres']])}
def allPlanes : Array (Array (QPlane {d})) := {planes}
def vertexIndices : Array (Array (Fin {t} → Fin {l})) := {inds}
def vertexWeights : Array (Array (Fin {t} → ℚ)) := {weights}

def source (i : Fin {n}) : Cayley.Certificate {d} :=
  rawSources.getD i.val {{skew := 0, signs := 0, inverse := 0, rotation := 0}}

def record : Barycentric.Certificate {d} {n} {k} {l} {t} where
  placement := {{
    template := fun p => TemplateData.{c['piece']}.getD p.val 0
    rotation := fun i => (source i).rotation
    center := fun i => rawCenters.getD i.val 0
    walls := Fin.elim0
    separation := fun i j => (allPlanes.getD i.val #[]).getD (j.val-i.val-1) ⟨0,0,0⟩ }}
  containerVertices := fun p => TemplateData.{c['container']}.getD p.val 0
  scale := {rat(c['scale'])}
  containerCenter := {vec(c['container_center'])}
  indices := fun i p => (vertexIndices.getD i.val #[]).getD p.val 0
  weights := fun i p => (vertexWeights.getD i.val #[]).getD p.val 0

def storedScale : ℚ := {rat(c['s_full'])}
def edgeRatio : ℚ := {rat(c['edge_ratio'])}

theorem edge_normalization : edgeRatio = 1 ∧ record.scale = storedScale * edgeRatio := by decide +kernel

theorem template_sizes : TemplateData.{c['piece']}.size = {k} ∧
    TemplateData.{c['container']}.size = {l} := by decide +kernel

theorem input_sizes : rawSources.size = {n} ∧ rawCenters.size = {n} ∧
    allPlanes.size = {n} ∧ vertexIndices.size = {n} ∧ vertexWeights.size = {n} := by decide +kernel

theorem source_checked : allFin {n} (fun i => Cayley.check (source i)) = true := by decide +kernel

theorem source_valid : ∀ i, Cayley.Valid (source i) := by
  intro i
  exact Cayley.check_sound _ (allFin_eq_true.mp source_checked i)

theorem checked : Barycentric.check record = true := by decide +kernel

/-- Complete convex-polytope packing at the exact stored scale. -/
theorem packing : Barycentric.Valid record := Barycentric.check_sound record checked

theorem proper_orientation : ∀ i : Fin {n},
    Matrix.det (fun a b => (record.placement.rotation i a b : ℝ)) = 1 := by
  intro i
  exact Cayley.determinant_real (source i) (allFin_eq_true.mp source_checked i)

#print axioms source_valid
#print axioms packing
#print axioms proper_orientation
end PackingCertificates.Catalogue.{name}
'''
    return name,text


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-n',type=int,default=100)
    args=ap.parse_args();generate_templates()
    dest=FORMAL/'PackingCertificates/Catalogue';dest.mkdir(parents=True,exist_ok=True)
    generated=[]
    for path in sorted((HERE/'witnesses_nd').glob('*.json')):
        c=json.loads(path.read_text())
        if c['n']>args.max_n:
            continue
        name,text=generate(c);out=dest/(name+'.lean')
        out.write_text(text,encoding='utf8',newline='\n')
        generated.append({'id':c['record_id'],'n':c['n'],'dimension':c['dimension'],'module':'PackingCertificates.Catalogue.'+name,'path':str(out.relative_to(FORMAL)).replace('\\','/')})
    (HERE/'generated-nd-modules.json').write_text(json.dumps(generated,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'generated':len(generated),'source_bytes':sum((FORMAL/r['path']).stat().st_size for r in generated)}))


if __name__=='__main__':
    main()
