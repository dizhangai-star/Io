"""The landing site shared by 01 (horizon) and 03 (eternity): the lander, its boot-print trail, the frost plain's
relief and the massif on the horizon.

Site frame: origin = where 01's camera stands, +Y = south (toward Jupiter), +X = west, metres. A shot standing
elsewhere passes its own origin's site coordinates `o = (ox, oy)` and gets functions of its own (X, Y); the curvature
drop stays the terrain's job (io_world.terrain / ground_z, centred on the shot's camera).
"""
import math

import numpy as np
from . import io_world as W, prints, lander

PAD = (1.03, 2.82)                                               # the footpad 01 frames (az 20°, 3.0 m)
LANDER = (4.62, 1.06)                                            # body centre: az 77°, 4.7 m from 01's camera
LEG = 1                                                          # that pad's leg (it carries the ladder)
L_HEAD = math.degrees(math.atan2(PAD[1] - LANDER[1], PAD[0] - LANDER[0])) - (45 + 90 * LEG)
OUT = [(0.45, 3.3), (0.5, 8.0), (-1.2, 20.0), (-3.4, 40.0), (-4.2, 75.0)]      # down the ladder, out toward Jupiter
BACK = [(-0.35, 0.75), (-0.45, 7.0), (-2.3, 19.0), (-4.5, 39.0), (-5.4, 75.0)]  # and back to where 01's camera stands
PR = (prints.trail(OUT, stride=1.3, seed=1, depth=0.008)
      + prints.trail(BACK, stride=1.25, seed=2, back=True, start=0.4, depth=0.008))
_rng = np.random.default_rng(3)
for _ in range(9):                                               # milling about at the foot of the ladder
    a, r = _rng.uniform(0, 2 * math.pi), _rng.uniform(0.25, 0.8)
    PR.append((PAD[0] + 0.15 + r * math.cos(a), PAD[1] - 0.85 + r * math.sin(a), _rng.uniform(-180, 180),
               0.007 * _rng.uniform(0.7, 1.1), 1))
# a massif on the far horizon (right; 01's left one removed, user 2026-10-03), at true distance (Io's curvature hides
# its lower 4–5 km). Io's mountains are tilted crustal blocks: long, flat-topped, steep scarps.
# (az°, km away, km high, km long, km wide, strike°, tilt)
MASSIFS = [(31.0, 115.0, 7.0, 45.0, 20.0, 110.0, -0.6)]


def base(X, Y):
    """Frost-plain relief: km swells down to 1 m bumps."""
    return (9.0 * (W.fbm(X / 900, Y / 900, 4, 20) - 0.5) + 1.5 * (W.fbm(X / 150, Y / 150, 4, 21) - 0.5) + 0.25 * (W.fbm(X / 12, Y / 12, 4, 22) - 0.5)
            + 0.03 * (W.fbm(X / 0.8, Y / 0.8, 3, 23) - 0.5))


def height(X, Y):
    """Ground height in the site frame: relief + the prints + the footpad's push-up rim of fines."""
    d = np.hypot(X - PAD[0], Y - PAD[1]) - 0.47
    return base(X, Y) + prints.stamp(X, Y, PR)[0] + 0.015 * np.exp(-(d / 0.06) ** 2)


def mountains(X, Y):
    z = np.zeros_like(X)
    for az, d, hgt, ln, wd, strike, tilt in MASSIFS:
        cx, cy = 1000 * d * math.sin(math.radians(az)), 1000 * d * math.cos(math.radians(az))
        sa, ca = math.sin(math.radians(strike)), math.cos(math.radians(strike))
        u, v = ((X - cx) * sa + (Y - cy) * ca) / (500 * ln), ((X - cx) * ca - (Y - cy) * sa) / (500 * wd)
        edge = 1 + 0.25 * (W.fbm(X / 4000, Y / 4000, 4, 31) - 0.5)          # ragged outline
        body = W.smooth(1.0, 0.82, np.hypot(u, v) / edge)                    # plateau with steep scarps
        top = 0.75 + 0.25 * tilt * u + 0.15 * (W.fbm(X / 3000, Y / 3000, 5, 32) - 0.5)
        z += 1000 * hgt * body * top
    return z


def shifted(f, o):
    """f in the site frame → the same function of a shot's own (X, Y), whose origin sits at site point o."""
    if not o or o == (0.0, 0.0):
        return f
    return lambda X, Y: f(X + o[0], Y + o[1])


def mark_prints(ob, o=(0.0, 0.0)):
    """Trodden soil → the 'prints' point attribute the ground material reads (half-darkened frost)."""
    me = ob.data
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    at = me.attributes.new('prints', 'FLOAT', 'POINT')
    at.data.foreach_set('value', prints.stamp(co[:, 0] + o[0], co[:, 1] + o[1], PR)[1].astype(np.float32))


def build_lander(sc, hfn, o=(0.0, 0.0)):
    """The lander, its pads on the ground of `hfn` (the shot's own height function), the pad 4 cm sunk."""
    c = (LANDER[0] - o[0], LANDER[1] - o[1])
    return lander.build(sc, c, L_HEAD, W.ground_z(hfn, PAD[0] - o[0], PAD[1] - o[1]) - 0.04, ladder_leg=LEG)
