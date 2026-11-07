"""LaTeX macros and the dimension table for the 4D-6D section of the patterns paper (from stats_nd.json)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s = json.load(open(os.path.join(ROOT, 'docs', 'patterns', 'stats_nd.json')))
pct = lambda x: f'{100 * x:.1f}'
L = [f'\\newcommand{{\\ndRecords}}{{{s["records"]:,}}}'.replace(',', '{,}'), f'\\newcommand{{\\ndFamilies}}{{{s["families"]}}}']
names = {'4': 'Four', '5': 'Five', '6': 'Six'}
for d, v in s['by_dim'].items():
    N = names[d]
    L += [f'\\newcommand{{\\nd{N}Rec}}{{{v["records"]:,}}}'.replace(',', '{,}'),
          f'\\newcommand{{\\nd{N}One}}{{{pct(v["single_orientation"])}}}',
          f'\\newcommand{{\\nd{N}Sym}}{{{pct(v["symmetric"])}}}',
          f'\\newcommand{{\\nd{N}Pla}}{{{pct(v["on_plateau"])}}}',
          f'\\newcommand{{\\nd{N}Rat}}{{{pct(v["relative_rational"])}}}',
          f'\\newcommand{{\\nd{N}Lat}}{{{v["lattice_windows"]}}}']
    I = s['inheritance'][d]
    L.append(f'\\newcommand{{\\nd{N}Frz}}{{{pct(I["consecutive_frozen"] / I["consecutive"])}}}')
r3 = s['reference_3d']
L += [f'\\newcommand{{\\ndThreeOne}}{{{pct(r3["single_orientation"])}}}', f'\\newcommand{{\\ndThreeSym}}{{{pct(r3["symmetric"])}}}',
      f'\\newcommand{{\\ndThreeFrz}}{{{pct(r3["consecutive_frozen"])}}}']
for k, nm in (('symmetric|single_orientation', 'SymOne'), ('lattice|symmetric', 'LatSym'), ('plateau|lattice', 'PlaLat'),
              ('plateau|symmetric', 'PlaSym'), ('closed_form|symmetric', 'CfSym')):
    L.append(f'\\newcommand{{\\ndLift{nm}}}{{{s["lifts"][k]:.1f}}}')
c = s['by_container']
for k, nm in (('c5', 'Cfive'), ('sx5', 'Sxfive'), ('sx6', 'Sxsix'), ('c8', 'Ceight'), ('hc5', 'Hcfive'), ('hc6', 'Hcsix')):
    L.append(f'\\newcommand{{\\ndSym{nm}}}{{{pct(c[k]["symmetric"])}}}')
ang = dict((tuple(a), n) for a, n in s['by_dim']['4']['common_rational_angles'])
L += [f'\\newcommand{{\\ndIsoSixty}}{{{ang.get((60.0, 60.0), 0)}}}', f'\\newcommand{{\\ndSimpleFortyfive}}{{{ang.get((45.0, 0.0), 0)}}}',
      f'\\newcommand{{\\ndSimpleSeventytwo}}{{{ang.get((72.0, 0.0), 0)}}}', f'\\newcommand{{\\ndIsoFortyfive}}{{{ang.get((45.0, 45.0), 0)}}}',
      f'\\newcommand{{\\ndSimpleNinety}}{{{ang.get((90.0, 0.0), 0)}}}']
open(os.path.join(ROOT, 'docs', 'patterns-paper', 'nd_macros.tex'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
