"""Boot prints stamped into the ground height field (shot 01: a trail out from the lander toward Jupiter and back).

Conventions as io_world: 1 BU = 1 m, X = west (right, facing Jupiter), Y = south, Z = up. A print is (x, y, heading,
depth, side): heading in degrees (0 = toe toward +Y, + = toward +X), depth of the sole (m), side −1 left / +1 right.
EMU boot sole ≈ 32 × 13 cm, flat with cross-bar lugs every 22 mm; prints in fine frost-covered regolith are 2–3 cm
deep (0.8 cm in shot 01's thin frost; user 2026-10-03: shallower) with a soft raised rim (displaced fines), deeper at the toe (push-off). At 0.18 g a loping step is ~1.3 m.

    P = prints.trail([(0.7, 1.8), (−3, 30), (−6, 60)], stride=1.3)    # alternating L/R along a polyline
    dz, mask = prints.stamp(X, Y, P)                                   # height offset (m), 0..1 disturbed-soil mask
"""
import math

import numpy as np

L = 0.16                     # half length (m)
LUG = 0.022                  # tread period (m)


def _half_width(u):
    """Sole half width (m) along u (−L heel … +L toe): heel 5 cm, ball 6.5 cm."""
    t = np.clip((u + 0.04) / 0.12, 0.0, 1.0)
    return 0.050 + 0.015 * t * t * (3 - 2 * t)


def trail(path, stride=1.3, gauge=0.13, start=0.0, end=None, seed=0, depth=0.018, back=False):
    """Alternating prints along a polyline `path` [(x, y), …] every `stride` m from arc length `start` to `end`.
    `gauge` = lateral distance between left and right feet. `back` reverses the walking direction (toes point
    toward the polyline's start). Small random yaw / spacing / depth so it doesn't read as a stamp."""
    rng = np.random.default_rng(seed)
    p = np.asarray(path, float)
    seg = np.diff(p, axis=0)
    sl = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0.0], np.cumsum(sl)])
    end = cum[-1] if end is None else min(end, cum[-1])
    out, s, k = [], start, 0
    while s <= end:
        i = min(np.searchsorted(cum, s, side='right') - 1, len(sl) - 1)
        f = (s - cum[i]) / sl[i]
        x, y = p[i] + f * seg[i]
        dx, dy = seg[i] / sl[i]
        if back:
            dx, dy = -dx, -dy
        side = -1 if k % 2 == 0 else 1
        ox, oy = dy * side * gauge / 2, -dx * side * gauge / 2          # right of the walking direction = (dy, −dx)
        h = math.degrees(math.atan2(dx, dy)) + side * 6.0 + rng.normal(0, 4.0)   # toes turned out a little
        out.append((x + ox, y + oy, h, depth * rng.uniform(0.8, 1.2), side))
        s += stride * rng.uniform(0.92, 1.08)
        k += 1
    return out


def stamp(X, Y, prints, tread_fade=(3.0, 6.0)):
    """Height offset (m) and disturbed-soil mask (0..1) of `prints` at points X, Y (any shape). The lug tread fades
    out between `tread_fade` metres from the origin (beyond, the mesh can't resolve it and it would alias)."""
    X, Y = np.asarray(X, float), np.asarray(Y, float)
    dz, mask = np.zeros_like(X), np.zeros_like(X)
    r = np.hypot(X, Y)
    a, b = tread_fade
    tread_w = np.clip((b - r) / (b - a), 0.0, 1.0)
    for (px, py, h, depth, side) in prints:
        near = (np.abs(X - px) < 0.3) & (np.abs(Y - py) < 0.3)
        if not near.any():
            continue
        x, y = X[near] - px, Y[near] - py
        hr = math.radians(h)
        fx, fy = math.sin(hr), math.cos(hr)                              # toe direction
        u = x * fx + y * fy
        v = x * fy - y * fx
        w = _half_width(u)
        q = ((np.abs(u) / L) ** 4 + (np.abs(v) / w) ** 4) ** 0.25        # boxy superellipse: < 1 inside the sole
        d = (q - 1.0) * w                                                # ≈ distance outside the edge (m)
        floor = 1.0 - np.clip((d + 0.02) / 0.03, 0.0, 1.0)              # 1 on the sole, soft wall 3 cm (fines slump)
        floor = floor * floor * (3 - 2 * floor)
        push = depth * (1.0 + 0.35 * np.clip((u - 0.02) / 0.12, 0.0, 1.0))
        rim = 0.25 * depth * np.exp(-((d - 0.016) / 0.012) ** 2) * (d > 0)
        lug = 0.5 + 0.5 * np.cos(2 * math.pi * (u + 0.35 * np.abs(v)) / LUG)   # chevron bars across the sole
        lug = lug * (np.abs(u + 0.05) > 0.012)                           # a plain band at the waist
        z = -push * floor + rim + 0.002 * lug * floor * tread_w[near]
        dz[near] += z
        mask[near] = np.maximum(mask[near], np.maximum(floor, 0.5 * rim / (0.25 * depth)))
    return dz, mask
