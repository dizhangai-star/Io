"""Io · 永恒: every number the shots rely on, from constants. `python3 tools/physics.py` → the table for TREATMENT.md.

Conventions: km, s, degrees unless named. Io is tidally locked: Jupiter hangs at a fixed point in its sky; the Sun goes
round once per synodic day (42.46 h). Jupiter's phase seen from Io = the Sun's angle from Jupiter in Io's sky.
"""
import math

GM_IO = 5959.9            # km³/s²
R_IO = 1821.6             # km (mean)
A_IO = 421_700            # km, orbit semi-major axis
R_J = 71_492              # km, equatorial
R_J_POL = 66_854          # km, polar
P_ROT_J = 9.925           # h, Jupiter System III rotation
P_SYN = 42.456            # h, Io synodic period (Sun to Sun)
V_IO = 17.334             # km/s, orbital speed
AU_J = 5.203              # Jupiter's distance from the Sun (AU)
S_EARTH = 1361.0          # W/m², solar constant at 1 AU
P_GEOM_J = 0.538          # Jupiter geometric albedo (visual)
GRS_W = 16_000            # km, Great Red Spot long axis (2020s)
R_SUN = 696_000           # km
AU = 149_597_870          # km


def deg(x):
    return math.degrees(x)


def jupiter_elev(theta):
    """Elevation (deg) of Jupiter's centre for an observer theta deg from the sub-Jupiter point (Io centre to
    Jupiter centre = A_IO)."""
    t = math.radians(theta)
    # observer at R_IO·(sin t, cos t) in the plane, Jupiter at (0, A_IO); local up = (sin t, cos t)
    ox, oy = R_IO * math.sin(t), R_IO * math.cos(t)
    dx, dy = -ox, A_IO - oy
    d = math.hypot(dx, dy)
    return deg(math.asin((dx * math.sin(t) + dy * math.cos(t)) / d)), d


def g_at(h):
    return GM_IO / (R_IO + h) ** 2 * 1000          # m/s²


def plume(h_max):
    """Vertical launch speed for apex h_max (km), exact in 1/r gravity, and the flight time (s), integrated."""
    v = math.sqrt(2 * GM_IO * (1 / R_IO - 1 / (R_IO + h_max)))        # km/s
    r, vr, t, dt = R_IO, v, 0.0, 0.5
    while True:
        vr -= GM_IO / r ** 2 * dt
        r += vr * dt
        t += dt
        if r <= R_IO:
            return v, t


def hidden(d_arc):
    """Height (km) hidden below the horizon at arc distance d_arc (km), eye at the ground."""
    return R_IO * (1 / math.cos(d_arc / R_IO) - 1)


def elev_of_top(h, d_arc, eye=0.002):
    """Elevation (deg) of a point h km above the surface at arc distance d_arc, seen from eye km up."""
    a = d_arc / R_IO
    ox, oy = 0.0, R_IO + eye
    px, py = (R_IO + h) * math.sin(a), (R_IO + h) * math.cos(a)
    return deg(math.atan2(py - oy, px - ox))


def px_across(ang_deg, lens_mm, width_px=1920, sensor=36.0):
    return width_px * math.tan(math.radians(ang_deg / 2)) / (sensor / 2 / lens_mm)


if __name__ == '__main__':
    rows = []
    d_sub = A_IO - R_IO
    dj = 2 * deg(math.asin(R_J / d_sub))
    rows.append(('Jupiter angular diameter (sub-Jupiter point)', f'{dj:.2f}° equatorial, '
                 f'{2 * deg(math.asin(R_J_POL / d_sub)):.2f}° polar; {dj / 0.52:.0f}× the Moon from Earth'))
    for th in (60, 70, 75, 80):
        e, d = jupiter_elev(th)
        rows.append((f'Jupiter centre elevation, {th}° from sub-Jupiter point', f'{e:.1f}° (lower limb {e - dj / 2:.1f}°)'))
    e_sun = S_EARTH / AU_J ** 2
    rows.append(('Sun', f'{2 * deg(math.atan(R_SUN / (AU_J * AU))):.3f}° wide; {e_sun:.1f} W/m² = 1/{AU_J ** 2:.1f} of Earth'))
    e_js = P_GEOM_J * e_sun * (R_J / d_sub) ** 2
    rows.append(('Full-Jupiter shine on the ground (Jupiter overhead-ish)', f'{e_js:.2f} W/m² = {100 * e_js / e_sun:.2f} % '
                 f'of Io sunlight ({math.log2(e_sun / e_js):.1f} stops down); ≈ {e_js / (S_EARTH * 2.0e-6):.0f}× full moonlight on Earth'))
    rows.append(('Eclipse', f'every {P_SYN:.2f} h; shadow {2 * R_J:,} km wide / {V_IO} km/s = {2 * R_J / V_IO / 3600:.2f} h'))
    rows.append(('Sun motion in Io sky', f'{360 / P_SYN:.2f}°/h (stars likewise); Jupiter: 0°/h'))
    rows.append(('Jupiter rotation', f'{P_ROT_J} h; GRS {GRS_W:,} km = {deg(GRS_W / d_sub):.1f}° across, crosses the disc '
                 f'in ≈ {P_ROT_J / 2:.1f} h'))
    rows.append(('Surface gravity', f'{g_at(0):.3f} m/s² = {g_at(0) / 9.81:.3f} g'))
    for h in (300, 400):
        v, t = plume(h)
        rows.append((f'Plume {h} km', f'vent speed {v * 1000:.0f} m/s, flight {t / 60:.1f} min (ballistic, no air)'))
    rows.append(('Horizon distance, eye 2 m', f'{math.sqrt(2 * R_IO * 0.002) * 1000:,.0f} m'))
    for d, h in ((300, 300), (500, 300), (800, 400), (200, 17), (100, 17)):
        rows.append((f'{h} km high at {d} km', f'{hidden(d):.1f} km hidden; top at {elev_of_top(h, d):.1f}° elevation'))
    for lens in (24, 35, 50, 85, 135):
        hfov = 2 * deg(math.atan(18 / lens))
        rows.append((f'{lens} mm (hfov {hfov:.1f}°)', f'Jupiter ≈ {px_across(dj, lens):.0f} px across of 1920'))
    w = max(len(a) for a, _ in rows)
    for a, b in rows:
        print(f'| {a:<{w}} | {b} |')
