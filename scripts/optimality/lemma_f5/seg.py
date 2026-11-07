import sympy as sp
c=sp.symbols('c')
F=sp.Rational
r=F(140,99); cp=F(14,25); spsi=F(207,250)
D=r*(1-cp*c)
lam={'A':F(33,50),'B':F(147,200),'C':F(161,200)}
U={'A':F(187333,100000),'B':F(199925,100000),'C':F(212352,100000)}
def seg(a,b):
    d=lam[b]-lam[a]
    al=(D*lam[b]-F(58,99))/d; be=(F(58,99)-D*lam[a])/d
    G=sp.expand(al*U[a]+be*U[b]-r*spsi*c)
    P=sp.expand(4*(1-c)-(1+c)*G**2)
    return sp.expand(al),sp.expand(be),G,P
cmid=F(11225,14406)
for (a,b),(lo,hi) in [(('A','B'),(F(67,100),cmid)),(('B','C'),(cmid,F(8661,10000)))]:
    al,be,G,P=seg(a,b)
    import numpy as np
    f=sp.lambdify(c,P); xs=np.linspace(float(lo),float(hi),2001); v=f(xs)
    print(a,b,'G =',G,'\n  P =',P,'\n  min P',v.min(),'at',xs[v.argmin()],' P(lo)',f(float(lo)),'P(hi)',f(float(hi)))
    print('  alpha',al,' beta',be)
