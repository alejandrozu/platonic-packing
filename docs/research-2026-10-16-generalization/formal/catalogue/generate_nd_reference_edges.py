"""Source-bound small Lean reference-edge/normalization leaf (not regularity)."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MODULE = 'PackingCertificates/Algebraic/NDReferenceEdges.lean'
spec = importlib.util.spec_from_file_location('edge_audit', HERE/'catalogue/nd-edge-scale-audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

PRELUDE = r'''import PackingCertificates.Algebraic.QuadraticInverse

/-! Exact reference endpoint literals and native edge-ratio factors.
This leaf does not establish adjacency, regularity, or equality with a full vertex array.
The accompanying generator binds these selected literals to frozen native JSON hashes.
-/
set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace PackingCertificates.Algebraic.NDReferenceEdges
open scoped BigOperators Matrix
open QuadraticInverse

def difference (x y : PairQ) : PairQ := (x.1-y.1,x.2-y.2)
def scalePair (q : ℚ) (x : PairQ) : PairQ := (q*x.1,q*x.2)
def distancePair {d : ℕ} (r : ℚ) (u v : Fin d → PairQ) : PairQ :=
  ∑ a, product r (difference (u a) (v a)) (difference (u a) (v a))

theorem embed_difference (α : ℝ) (x y : PairQ) :
    embed α (difference x y) = embed α x - embed α y := by
  simp only [embed,difference,Rat.cast_sub]; ring

theorem embed_scale (α : ℝ) (q : ℚ) (x : PairQ) :
    embed α (scalePair q x) = (q : ℝ)*embed α x := by
  simp only [embed,scalePair,Rat.cast_mul]; ring

theorem distancePair_sound {d : ℕ} (r : ℚ) (α : ℝ) (hα : α^2 = (r : ℝ))
    (u v : Fin d → PairQ) (e : PairQ) (h : distancePair r u v = e) :
    (∑ a, (embed α (u a)-embed α (v a))^2) = embed α e := by
  rw [← h,distancePair,show embed α = embedAdd α from rfl,map_sum]
  apply Finset.sum_congr rfl
  intro a _
  change _ = embed α (product r _ _)
  rw [embed_product r α hα,embed_difference,pow_two]
  rfl

noncomputable def nativeMu (m : PairQ) (timesTwo : Bool) : ℝ :=
  embed (Real.sqrt 5) m * (if timesTwo then Real.sqrt 2 else 1)

theorem native_ratio_sound (m ce pe : PairQ) (timesTwo : Bool)
    (h : scalePair (if timesTwo then 2 else 1)
      (product 5 (product 5 m m) ce) = pe) :
    (nativeMu m timesTwo)^2 * embed (Real.sqrt 5) ce = embed (Real.sqrt 5) pe := by
  have hs5 : (Real.sqrt 5)^2 = ((5 : ℚ) : ℝ) := by norm_num
  have he := congrArg (embed (Real.sqrt 5)) h
  rw [embed_scale,embed_product 5 _ hs5,embed_product 5 _ hs5] at he
  cases timesTwo
  · simpa [nativeMu,pow_two,mul_assoc] using he
  · have hs2 : (Real.sqrt 2)^2 = (2 : ℝ) := by norm_num
    simp only [ite_true,Rat.cast_ofNat] at he
    simp only [nativeMu,ite_true,mul_pow,hs2]
    nlinarith [he]

'''


def q(x):
    x = audit.Fraction(x)
    return f'({x.numerator} : ℚ)' if x.denominator == 1 else f'({x.numerator}/{x.denominator} : ℚ)'


def pair(x, r):
    if set(x) - {1,r}:
        raise ValueError('Unexpected primitive field')
    return f'({q(x.get(1,0))},{q(x.get(r,0))})'


def generate():
    receipt = audit.run(HERE)
    g = json.loads((HERE/audit.GEOMETRY).read_text(encoding='utf8'))
    lines = [PRELUDE]
    names = []
    for s in receipt['shapes']:
        name = s['shape']; row = g[name]
        i,j = row['edges'][0]
        vals = [audit.parse(x) for v in [row['V'][i],row['V'][j]] for x in v]
        roots = set().union(*(set(x)-{1} for x in vals))
        r = next(iter(roots)) if roots else 5
        if len(roots)>1: raise ValueError('Multiple primitive roots in selected endpoint')
        for n,v in [('u',row['V'][i]),('v',row['V'][j])]:
            lines.append(f'def {name}_{n} : Fin {row["dim"]} → PairQ := ![' + ','.join(pair(audit.parse(x),r) for x in v)+']\n')
        lines.append(f'def {name}_edge : PairQ := {pair(audit.parse(row["edge2"]),r)}\n')
        lines.append(f'theorem {name}_edge_exact : distancePair {r} {name}_u {name}_v = {name}_edge := by decide +kernel\n')
        lines.append(f'theorem {name}_reference_distance : (∑ a, (embed (Real.sqrt {r}) ({name}_u a)-embed (Real.sqrt {r}) ({name}_v a))^2) = embed (Real.sqrt {r}) {name}_edge :=\n  distancePair_sound {r} _ (by norm_num) _ _ _ {name}_edge_exact\n')
        names += [name+'_edge_exact',name+'_reference_distance']
    for row in receipt['records']:
        ident = row['record_id']; mu = audit.parse(row['native_mu'])
        t = set(mu)<={2,10}
        m = {1:mu.get(2,0),5:mu.get(10,0)} if t else mu
        m = audit.clean(m)
        tt = 'true' if t else 'false'
        ce = pair(audit.parse(g[row['container']]['edge2']),5)
        pe = pair(audit.parse(g[row['piece']]['edge2']),5)
        lines.append(f'def {ident}_m : PairQ := {pair(m,5)}\n')
        lines.append(f'theorem {ident}_coefficient_identity : scalePair (if {tt} then 2 else 1) (product 5 (product 5 {ident}_m {ident}_m) {ce}) = {pe} := by decide +kernel\n')
        lines.append(f'theorem {ident}_edge_ratio : (nativeMu {ident}_m {tt})^2 * embed (Real.sqrt 5) {ce} = embed (Real.sqrt 5) {pe} := native_ratio_sound _ _ _ _ {ident}_coefficient_identity\n')
        lines.append(f'theorem {ident}_mu_positive : 0 < nativeMu {ident}_m {tt} := by\n  have hs : (Real.sqrt 5)^2 = (5 : ℝ) := by norm_num\n  have hp := Real.sqrt_nonneg (5 : ℝ)\n  have hm : 0 < embed (Real.sqrt 5) {ident}_m := by\n    norm_num [{ident}_m,embed] <;> nlinarith\n')
        lines.append('  exact mul_pos hm (Real.sqrt_pos.2 (by norm_num))\n' if t else '  simpa [nativeMu] using hm\n')
        names += [ident+'_coefficient_identity',ident+'_edge_ratio',ident+'_mu_positive']
    lines += ['end PackingCertificates.Algebraic.NDReferenceEdges\n']
    lines += ['#print axioms PackingCertificates.Algebraic.NDReferenceEdges.'+n+'\n' for n in names]
    text='\n'.join(lines).encode()
    binding = dict(schema='nd-selected-reference-edge-lean-binding-v1',
        status='source_bound_not_compilation_receipt', source_freeze=receipt['source_freeze'],
        registry_path=audit.REGISTRY,registry_sha256=audit.REGISTRY_SHA256,
        geometry_path=audit.GEOMETRY,geometry_sha256=audit.GEOMETRY_SHA256,
        generated_path=MODULE,generated_sha256=hashlib.sha256(text).hexdigest(),
        generator_path='catalogue/generate_nd_reference_edges.py',
        generator_sha256=audit.digest(Path(__file__)),
        endpoint_count=24,selected_edges=12,native_ratio_records=45,
        scope='Selected exact endpoint literals and positive native mu squared edge-ratios only; no adjacency, classification, regularity or whole-array identity claim',
        shapes=receipt['shapes'],records=receipt['records'],audited_declarations=names)
    return text,binding


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    text,binding=generate();out=HERE/MODULE
    if a.check:
        if out.read_bytes()!=text: raise ValueError('Generated Lean differs from frozen source-bound rendering')
    else:
        out.write_bytes(text)
    (HERE/'catalogue/nd-reference-edge-lean-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:binding[k] for k in ['status','generated_path','generated_sha256','selected_edges','native_ratio_records']}))

if __name__=='__main__': main()
