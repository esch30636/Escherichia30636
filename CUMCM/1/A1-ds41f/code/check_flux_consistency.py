"""Moisture boundary-closure / discrete-flux consistency on A1-codex's own 800-cell
field, in consistent SI units.

  c*    : dimensionless concentration used inside A1's solver (c = C, dimensionless)
  flux scale: the solver's flux carries an implicit factor D0/R once multiplied by
              the dimensionless group; the physical surface flux is thus
                  J = rho_d0 * (D0/R) * [dimensionless flux]
              with rho_d0 the reference dry density.
"""
import numpy as np
from scipy.optimize import brentq

R, D0, DECAY, HM = 0.02, 7e-9, 0.89, 8e-7
RHO, C0 = 820.0, 2.55
rho_d0 = RHO / (1 + C0)
A1 = np.load(r"E:\HUST\国赛\A1-codex\data\full_precision.npz")
ENV = np.loadtxt(r"E:\HUST\国赛\A1-codex\data\ambient.csv", delimiter=",", skiprows=1)
Cc = A1["Ccells_1800"]
Ctab = A1["C_kgkg"]
n = len(Cc)
scale = D0 / R ** 2                       # A1's diffusivity scaling
beta = HM / R                             # A1's mass-transfer scaling

faces = 1.0 - (1.0 - np.linspace(0.0, 1.0, n + 1)) ** 2
centers = 0.5 * (faces[1:] + faces[:-1])
g = faces[1:-1] / (centers[1:] - centers[:-1])
half = 1.0 - centers[-1]


def U(a, b):
    """int_b^a D dC in A1's dimensionless units."""
    m, d = 0.5 * (a + b), 0.5 * (a - b)
    z = 0.7745966692414834 * d
    return d * scale * (5 / 9 * np.exp(-DECAY / (m - z)) + 8 / 9 * np.exp(-DECAY / (m + z))
                        + 8 / 9 * np.exp(-DECAY / m))


q_face = float(g[-1] * U(Cc[-2], Cc[-1]))            # interior face -> last cell
Ca = float(np.interp(1800.0, ENV[:, 0], ENV[:, 2]))
f = lambda cs: U(Cc[-1], cs) / (2 * half) - beta * (cs - Ca)
cs = brentq(f, min(Cc[-1], Ca), max(Cc[-1], Ca), xtol=1e-16)
q_robin = float(beta * (cs - Ca))                    # last cell -> surface

J_face = rho_d0 * (D0 / R) * q_face
J_robin = rho_d0 * (D0 / R) * q_robin
mean_reported = 2.293558
J_avg = rho_d0 * R * (C0 - mean_reported) / 1800.0   # dM/dt / (2 pi R L)

ln = np.log(1.0 / np.sqrt(centers[-1]))
dN = D0 * np.exp(-DECAY / Cc[-1])
cs_log = (dN * Cc[-1] / ln + HM * Ca) / (dN / ln + HM)

print(f"rho_d0 = {rho_d0:.4f} kg/m3")
print(f"interior face flux   q = {q_face:.6e}  ->  J = {J_face:.4e} kg/(m2 s)")
print(f"surface Robin flux   q = {q_robin:.6e}  ->  J = {J_robin:.4e} kg/(m2 s)")
print(f"mean flux (mass balance, A1 reported mean) J_avg = {J_avg:.4e} kg/(m2 s)")
print(f"J_avg / J_robin = {J_avg / J_robin:.4f}   (must be > 1: drying slows down)")
print(f"implied surface C = {cs:.7f}   A1 table value = {Ctab[1800, 20]:.7f}")
print(f"quasi-steady log-layer C = {cs_log:.7f}   relative error = {abs(cs - cs_log)/cs:.3e}")
print(f"surface / interior flux ratio = {q_robin / q_face:.6f}")
