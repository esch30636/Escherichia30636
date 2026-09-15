"""Minimal helper used only by the audit scripts in this folder.

Contains the reviewed model's geometry and the Appendix-3 property law, so that
audit_*.py can re-evaluate quantities without importing the reviewed package.
"""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"
R = 0.02
LV0, LV_SLOPE = 2.501e6, 2.361e3
P_ATM = 101325.0
MW, MDA = 0.018015, 0.028964
RHO_D = (650.0 + 128.0 * 2.55) / (1.0 + 2.55)


def properties(t, c, q1=False, df=1.0):
    """Appendix-3 properties; returns (rho*cp, k, D, d(rho*cp)/dC)."""
    if q1:
        return 820. * 2600., .36, df * 7e-9 * np.exp(-.89 / c), 0.
    rho = 650. + 128. * c
    cp = 1450. + 2736. * c / (1. + c)
    cap = rho * cp
    capprime = 128. * cp + rho * 2736. / (1. + c) ** 2
    return cap, .21 + .38 * c / (1. + c), df * .0024 * np.exp(-.45 / c - 3850. / (t + 273.15)), capprime


def p_sat(t_c):
    """ASHRAE saturation vapour pressure over water, Pa (t in Celsius)."""
    tt = np.asarray(t_c, dtype=float) + 273.15
    return np.exp(-5.8002206e3 / tt + 1.3914993 - 4.8640239e-2 * tt
                  + 4.1764768e-5 * tt ** 2 - 1.4452093e-8 * tt ** 3
                  + 6.5459673 * np.log(tt))


def y_sat(t_c):
    ps = p_sat(t_c)
    return 0.621945 * ps / (P_ATM - ps)


def mesh(n):
    """The reviewed quadratic-graded mesh."""
    faces = R * (1 - (1 - np.linspace(0, 1, n + 1)) ** 2)
    x = (faces[1:] + faces[:-1]) / 2
    v = (faces[1:] ** 2 - faces[:-1] ** 2) / 2
    g = faces[1:-1] / np.diff(x)
    return x, v, g, R - x[-1]


def load_delivered():
    return np.load(A2 / "data/full_precision.npz")


def load_ambient():
    return np.loadtxt(A2 / "data/ambient.csv", delimiter=",", skiprows=1)
