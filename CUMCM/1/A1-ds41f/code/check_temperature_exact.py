import numpy as np, json
A1=np.load(r"E:\HUST\国赛\A1-codex\data\full_precision.npz")
print("keys", list(A1.keys()))
T=A1["T_C"]; C=A1["C_kgkg"]
print("shapes", T.shape, C.shape)
# heat equation = exactly solvable modal ODE; compare A1 T with series-integrated modal?
import sys; sys.path.insert(0,"code")
from scipy.special import j0,j1
from scipy.optimize import brentq
R,RHO,CP,K,H=0.02,820.,2600.,.36,25.
env=np.loadtxt(r"E:\HUST\国赛\A1-codex\data\ambient.csv",delimiter=",",skiprows=1)
def modes(biot,n=300):
    f=lambda z:z*j1(z)-biot*j0(z)
    scan=np.linspace(1e-9,(n+1)*np.pi,12*n+40); vals=f(scan)
    return np.array([brentq(f,x,y,xtol=1e-15) for x,y,fx,fy in zip(scan[:-1],scan[1:],vals[:-1],vals[1:]) if fx*fy<0][:n])
z=modes(H*R/K,300); Am=2*j1(z)/(z*(j0(z)**2+j1(z)**2))
rate=K/(RHO*CP*R**2)*z**2
basis=Am[:,None]*j0(z[:,None]*np.linspace(0,1,21)[None,:])
st=np.zeros(len(z)); hist=[np.full(21,28.)]
for k in range(1,1801):
    i=min(int((k-1)//60),len(env)-2); slope=(env[i+1,1]-env[i,1])/60.
    Ta0=env[i,1]+slope*((k-1)-env[i,0]); Ta1=Ta0+slope
    st=st*np.exp(-rate)+slope*(-np.expm1(-rate))/rate
    hist.append(Ta1-st@basis)
EX=np.array(hist)
d=np.abs(T-EX)
print("A1 T vs exact modal: max abs =",d.max(),"at t=",d.max(axis=1).argmax(),"r idx",d.max(axis=0).argmax())
for t in [100,300,600,900,1200,1500,1800]:
    print(f"  t={t:5d} A1={T[t,[0,5,10,15,20]]} exact={EX[t,[0,5,10,15,20]]} maxd={d[t].max():.3e}")
