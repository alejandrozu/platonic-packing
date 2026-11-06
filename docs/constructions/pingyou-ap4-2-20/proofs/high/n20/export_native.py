"""Export the exact N20 construction as a positive-clearance native record.

Usage: python3 export_native.py output.json
Requires mpmath. Verification of endpoint.json needs only the standard library.
"""
from pathlib import Path
from fractions import Fraction
import json,sys
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
import mpmath as mp
mp.mp.dps=110
HERE=Path(__file__).resolve().parent
d=json.loads((HERE/'endpoint.json').read_text())
alpha=mp.root(2,4)
def scalar(v):
 q=Fraction(v);return mp.mpf(q.numerator)/q.denominator
def field(v):return sum(scalar(c)*alpha**i for i,c in enumerate(v))
def decimal_up(v,places=45):
 den=10**places;num=int(mp.ceil(v*den))
 return f'{num//den}.{num%den:0{places}d}'
rho=1+mp.mpf('1e-12')
S=field(d['scale_coefficients'])
record={'piece':'antiprism4','container':'antiprism4','n':20,
 's_full':decimal_up(S*rho),
 'pieces':[[mp.nstr(rho*field(v),48)for v in center]+q for center,q in zip(d['physical_centers'],d['quaternions_wxyz'])],
 'found_by':'PingYou Ltd (PY)','credit':'PingYou Ltd (PY)',
 'method':'Exact rational-quaternion construction and fixed-frame translation endpoint; positive-clearance native export.',
 'publication_permission':'Permission granted by the contributor to publish this construction, coordinates and certificate.'}
Path(sys.argv[1]).write_text(json.dumps(record,indent=2)+'\n')
print('Native s_full:',record['s_full'])
print('Exact endpoint:',mp.nstr(S,75))
print('Scale overhead:',mp.nstr(S*(rho-1),30))
