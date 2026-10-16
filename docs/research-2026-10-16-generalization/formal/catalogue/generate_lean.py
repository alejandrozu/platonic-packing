#!/usr/bin/env python3
"""Generate kernel-checkable modules; never writes a success assertion/receipt."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent


def rat(x):
    q=Fraction(x)
    if q.denominator==1:
        return f'({q.numerator} : ℚ)'
    return f'({q.numerator}/{q.denominator} : ℚ)'


def vec(xs):
    return '!['+', '.join(rat(x) for x in xs)+']'


def matrix(xs):
    return '!['+', '.join(vec(x) for x in xs)+']'


def arr(xs):
    return '#['+',\n  '.join(xs)+']'


def plane(p):
    return '⟨'+vec(p['normal'])+', '+rat(p['lower'])+', '+rat(p['upper'])+'⟩'


def module_name(record_id):
    return 'R'+re.sub('[^A-Za-z0-9]','_',record_id)


def generate(c):
    n=c['n']; name=module_name(c['record_id'])
    rows=[]
    index={(p['i'],p['j']):p for p in c['planes']}
    assert len(index)==n*(n-1)//2
    for i in range(n):
        rows.append(arr([plane(index[i,j]) for j in range(i+1,n)]))
    text=f'''import PackingCertificates.Catalogue

-- Generated from the immutable catalogue; numbers are exact rationals.
-- Original JSON SHA256: {c['source_sha256']}
-- Original source: {c['source_path']}
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Catalogue.{name}
open PackingCertificates.Rational

def rawQuaternions : Array (Fin 4 → ℚ) := {arr([vec(q) for q in c['quaternions']])}
def rawCenters : Array (QPoint 3) := {arr([vec(q) for q in c['centres']])}
def exactRotations : Array (Fin 3 → QPoint 3) := {arr([matrix(q) for q in c['rotations']])}
def allPlanes : Array (Array (QPlane 3)) := {arr(rows)}

def record : CubeRecord {n} where
  scale := {rat(c['scale'])}
  containerCenter := {vec(c['container_center'])}
  quaternion i := rawQuaternions.getD i.val 0
  center i := rawCenters.getD i.val 0
  rotation i := exactRotations.getD i.val 0
  separation i j := (allPlanes.getD i.val #[]).getD (j.val-i.val-1) ⟨0,0,0⟩

theorem input_sizes : rawQuaternions.size = {n} ∧ rawCenters.size = {n} ∧
    exactRotations.size = {n} ∧ allPlanes.size = {n} := by decide +kernel

theorem checked : record.check = true := by decide +kernel

/-- Actual catalogue placements are proper rigid copies of the side-one cube,
contained in the side-s_full cube and pairwise disjoint. No optimality claim. -/
theorem packing : record.Valid := CubeRecord.check_sound record checked

#print axioms checked
#print axioms packing
end PackingCertificates.Catalogue.{name}
'''
    return name,text


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-n',type=int,default=100)
    args=ap.parse_args()
    dest=FORMAL/'PackingCertificates'/'Catalogue';dest.mkdir(parents=True,exist_ok=True)
    generated=[]
    for p in sorted((HERE/'witnesses').glob('*.json')):
        c=json.loads(p.read_text())
        if c['n']>args.max_n:
            continue
        name,text=generate(c)
        out=dest/(name+'.lean');out.write_text(text,encoding='utf8',newline='\n')
        generated.append({'id':c['record_id'],'n':c['n'],'module':'PackingCertificates.Catalogue.'+name,'path':str(out.relative_to(FORMAL)).replace('\\','/')})
    (HERE/'generated-modules.json').write_text(json.dumps(generated,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'generated':len(generated),'source_bytes':sum((FORMAL/r['path']).stat().st_size for r in generated)}))


if __name__=='__main__':
    main()
