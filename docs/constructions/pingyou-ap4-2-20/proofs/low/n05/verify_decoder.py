"""Check that the compact wall-elimination/2x2 decoder is valid on the root box.
Runs the full independent interval lift as a prerequisite.
"""
import verify as q
from pathlib import Path
import json
A=q.A;dot=q.dot;cross=q.cross
H=A(q.ak(q.H));P=[[v[0],v[1],v[2]/H]for v in q.PP]
faces=[[1,3,4],[1,4,5],[0,3,6],[3,4,6],[1,2,5],[0,2,7],[0,6,7],[2,5,7],[0,1,2,3],[4,5,6,7]]
sgns=[1,-1,-1,1,1,-1,1,1,1,1]
# Determine orientation exactly from physical normals; normalized map is invertible.
U=[]
for f in faces:
 n=cross([P[f[1]][k]-P[f[0]][k]for k in range(3)],[P[f[2]][k]-P[f[0]][k]for k in range(3)])
 if dot(n,P[f[0]]).v.upper()<0:n=[-x for x in n]
 assert dot(n,P[f[0]]).v.lower()>0
 U.append(n)
B=[dot(U[i],P[f[0]])for i,f in enumerate(faces)]
_,X,_,_,PV,_,_,_=q.evaluate(q.box)
V=[[[v[0],v[1],v[2]/H]for v in vs]for vs in PV]
N=[]
for vs in V:
 ns=[]
 for f,u in zip(faces,U):
  n=cross([vs[f[1]][k]-vs[f[0]][k]for k in range(3)],[vs[f[2]][k]-vs[f[0]][k]for k in range(3)])
  raw=cross([P[f[1]][k]-P[f[0]][k]for k in range(3)],[P[f[2]][k]-P[f[0]][k]for k in range(3)])
  if dot(raw,u).v.upper()<0:n=[-x for x in n]
  ns.append(n)
 N.append(ns)
E=[[[vs[b][k]-vs[a][k]for k in range(3)]for a,b in q.ED]for vs in V]
wall=[[(7,5),(9,7)],[(4,1),(5,0),(8,0)],[(0,1),(3,3)],[(0,1),(8,1)],[(2,4),(3,5),(6,6)]]
free={0:0,2:2,3:1};cf=[]
for i,fs in enumerate(wall):
 M=[U[f]for f,j in fs];b0=[-dot(U[f],V[i][j])for f,j in fs];bs=[B[f]for f,j in fs];bv=[A()for f,j in fs]
 if i in free:
  M=M+[[A(int(k==free[i]))for k in range(3)]];b0=b0+[A()];bs=bs+[A()];bv=bv+[A(1)]
 cf.append((q.invsolve(M,b0),q.invsolve(M,bs),q.invsolve(M,bv)))
rows=[];rhs=[]
for tag,feats in zip(q.D['active_tags'][13:],q.D['support_vertices'][13:]):
 _,i,j,ix,sense=tag
 if ix<10:n=N[i][ix]
 elif ix<20:n=N[j][ix-10]
 else:ea,eb=divmod(ix-20,len(q.ED));n=cross(E[i][ea],E[j][eb])
 n=[sense*v for v in n];cs=[]
 for own in [0,2,3]:cs.append(dot(n,[cf[j][2][k]*(j==own)-cf[i][2][k]*(i==own)for k in range(3)]))
 cs.append(dot(n,[cf[j][1][k]-cf[i][1][k]for k in range(3)]))
 rows.append(cs);rhs.append(-dot(n,[cf[j][0][k]-cf[i][0][k]+V[j][feats[1]][k]-V[i][feats[0]][k]for k in range(3)]))
det=rows[4][2]*rows[6][3]-rows[4][3]*rows[6][2]
for z in [det,rows[3][0],rows[5][1]]:assert not z.v.contains(0)
S=(rows[4][2]*rhs[6]-rows[6][2]*rhs[4])/det
v3=(rhs[4]*rows[6][3]-rhs[6]*rows[4][3])/det
v0=(rhs[3]-rows[3][3]*S)/rows[3][0]
v2=(rhs[5]-rows[5][3]*S)/rows[5][1]
y=[v0,v2,v3,S]
for i in range(7):assert (dot(rows[i],y)-rhs[i]).v.contains(0)
assert (S-X[15]).v.contains(0)
assert (S-X[15]).v.abs_upper()<q.ball(q.Q(1,10**58))
out={'status':'PASS_COMPACT_DECODER_ON_VALIDATED_ROOT_BOX','scale_2x2_denominator':str(det.v),'free_v0_denominator':str(rows[3][0].v),'free_v2_denominator':str(rows[5][1].v),'compact_scale_ball':str(S.v),'root_box_and_full_lift_receipt':'verify.py','equivalence':'All walls solved by constant nonsingular blocks; pair rows4,6 solve(v3,S); rows3,5 solve(v0,v2); remaining rows0,1,2 define the same full-contact root.'}
print(json.dumps(out,indent=2))
