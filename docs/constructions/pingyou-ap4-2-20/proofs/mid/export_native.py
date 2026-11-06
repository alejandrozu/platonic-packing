"""Export exact square-antiprism endpoints as strict-clearance native records."""
from pathlib import Path
from decimal import Decimal as D, localcontext, ROUND_CEILING
from fractions import Fraction
import json

HERE = Path(__file__).resolve().parent

def qdec(x):
    f = Fraction(x)
    return D(f.numerator) / D(f.denominator)

def quaternion(m):
    tr = m[0][0] + m[1][1] + m[2][2]
    if tr > 0:
        s = 2 * (tr + 1).sqrt()
        return [s / 4, (m[2][1]-m[1][2])/s,
                (m[0][2]-m[2][0])/s, (m[1][0]-m[0][1])/s]
    i = max(range(3), key=lambda k: m[k][k])
    j, k = (i+1)%3, (i+2)%3
    s = 2 * (1+m[i][i]-m[j][j]-m[k][k]).sqrt()
    q = [D(0)]*4
    q[0], q[i+1] = (m[k][j]-m[j][k])/s, s/4
    q[j+1], q[k+1] = (m[j][i]+m[i][j])/s, (m[k][i]+m[i][k])/s
    return q

def export(source, target):
    d = json.loads(Path(source).read_text())
    with localcontext() as ctx:
        ctx.prec = 140
        alpha = D(2).sqrt().sqrt()
        def value(c):
            return sum(qdec(x)*alpha**i for i,x in enumerate(c))
        dilation = 1+D('1e-12')
        scale = value(d['scale_coefficients'])
        poses = []
        for c,m in zip(d['physical_centers'], d['frames']):
            q = quaternion([[value(x)for x in row]for row in m])
            pose = [value(x)*dilation for x in c]+q
            poses.append([format(x.quantize(D('1e-48')),'f')for x in pose])
        result = {'piece':'antiprism4','container':'antiprism4','n':d['n'],
                  's_full':format((scale*dilation).quantize(D('1e-48'),rounding=ROUND_CEILING),'f'),
                  'pieces':poses,
                  'exact_endpoint':{'field':'Q(alpha), alpha^4=2, alpha>0',
                                    'scale_coefficients':d['scale_coefficients']},
                  'native_export':{'center_dilation':'1.000000000001','coordinate_decimal_places':48}}
    Path(target).parent.mkdir(parents=True,exist_ok=True)
    Path(target).write_text(json.dumps(result,indent=2)+'\n')

if __name__ == '__main__':
    import sys
    export(sys.argv[1],sys.argv[2])
