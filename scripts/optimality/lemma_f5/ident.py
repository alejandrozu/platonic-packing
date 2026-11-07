import sympy as sp
c,rho=sp.symbols('c rho')
r=sp.symbols('r0:4'); x=sp.symbols('x0:4'); M=[[sp.Symbol(f'M{i}{k}') for k in range(4)] for i in range(4)]
cp=sp.Rational(14,25); spsi=sp.Rational(207,250)
# norm identity for column k=0
k=0
w=[spsi*rho*r[k]]+[rho**2*M[i][k]+(c-cp)*x[i]*r[k] for i in range(4)]
LHS=sum(t**2 for t in w); RHS=rho**4-sp.Rational(51,62500)*rho**2*r[k]**2
K=r[k]**2+sum(M[i][k]**2 for i in range(4))-1
P=c*r[k]+sum(x[i]*M[i][k] for i in range(4))
C1=c**2+sum(t**2 for t in x)-1
H=rho**2-(1-c**2)
comb=rho**4*K+2*rho**2*(c-cp)*r[k]*P+(c-cp)**2*r[k]**2*C1-r[k]**2*(rho**2+(c-cp)**2)*H
print('norm identity residual:',sp.expand(LHS-RHS-comb))
print('kappa-1 =',cp**2+spsi**2-1)
# sum identity
ax=sp.symbols('a0:4')  # stands for |x_i|
ylow=sum(c*spsi*rho*r[k]**2+sum(ax[i]*M[i][k]*(rho**2*M[i][k]+(c-cp)*x[i]*r[k]) for i in range(4)) for k in range(4))
target=c*spsi*rho*(1-c**2)+rho**2*sum(ax[i]*(1-x[i]**2) for i in range(4))-c*(c-cp)*sum(ax[i]*x[i]**2 for i in range(4))
R1=c**2+sum(t**2 for t in r)-1
W=[x[i]**2+sum(M[i][k]**2 for k in range(4))-1 for i in range(4)]
Q=[c*x[i]+sum(r[k]*M[i][k] for k in range(4)) for i in range(4)]
comb2=c*spsi*rho*R1+sum(rho**2*ax[i]*W[i] for i in range(4))+sum((c-cp)*ax[i]*x[i]*Q[i] for i in range(4))
print('sum identity residual:',sp.expand(ylow-target-comb2))
