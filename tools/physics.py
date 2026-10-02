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
P_ORB_IO = 42.4593        # h, Io sidereal orbit = its rotation (the stars' period in its sky)
P_SYN = 42.4767           # h, Io synodic period (Sun to Sun): 1 / (1/P_ORB_IO − 1/Jupiter's 11.862 yr)
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


# ---------------------------------------------------------------- the site and its sky (user 2026-10-02)
# The site is SITE_THETA from the sub-Jupiter point toward Io's north pole (latitude 75° N on the sub-Jupiter
# meridian): Jupiter due south, its axis upright in the frame (bands horizontal); the Sun runs low round the sky along
# the celestial equator, at most 15° up, and is up only while Jupiter is less than half lit.
# Io frame: Xi → Jupiter, Zi → Io's north pole, Yi = Zi × Xi = east (Io turns prograde, so the sky turns east → west).
# Local frame (Blender): X = west (right, facing Jupiter), Y = south (toward Jupiter), Z = up. 1 BU = 1 m.
# The Sun's place is its signed elongation from Jupiter E (deg): E > 0 east of Jupiter (morning, before the eclipse),
# 0 = behind Jupiter, E < 0 west (after); E falls 8.48°/h. Jupiter's 3° obliquity (seasonal tilt of the Sun's path) is
# ignored: the Sun passes behind Jupiter's equator.
SITE_THETA = 75.0
R_SUN_DEG = deg(math.atan(R_SUN / (AU_J * AU)))              # Sun's angular radius


def _io_to_local(v):
    """Io-frame vector → local (west, south, up)."""
    t = math.radians(SITE_THETA)
    up = (math.cos(t), 0.0, math.sin(t))
    south = (math.sin(t), 0.0, -math.cos(t))
    west = (0.0, -1.0, 0.0)
    return tuple(sum(a * b for a, b in zip(v, axis)) for axis in (west, south, up))


def jupiter_local():
    """Jupiter as seen from the site: (unit direction, distance km, angular radius eq deg, polar deg, axis unit)."""
    t = math.radians(SITE_THETA)
    v = (A_IO - R_IO * math.cos(t), 0.0, -R_IO * math.sin(t))
    d = math.sqrt(sum(c * c for c in v))
    u = _io_to_local(tuple(c / d for c in v))
    return u, d, deg(math.asin(R_J / d)), deg(math.asin(R_J_POL / d)), _io_to_local((0.0, 0.0, 1.0))


def sun_local(elong):
    """Unit vector toward the Sun at signed elongation elong (deg)."""
    h = math.radians(elong)
    return _io_to_local((math.cos(h), math.sin(h), 0.0))


def alt_az(u):
    """(elevation, azimuth) deg of a local unit vector; azimuth 0 = Jupiter (south), + = toward west (right)."""
    return deg(math.asin(u[2])), deg(math.atan2(u[0], u[1]))


def lit_fraction(elong):
    """Fraction of Jupiter's disc lit; phase angle = 180° − |elongation|."""
    return (1 - math.cos(math.radians(abs(elong)))) / 2


def jupiter_shine(elong):
    """Irradiance (W/m²) from Jupiter on a surface facing it, for a Lambert sphere at phase angle 180° − |E|."""
    a = math.radians(180 - abs(elong))
    phi = (math.sin(a) + (math.pi - a) * math.cos(a)) / math.pi
    _, d, *_ = jupiter_local()
    return P_GEOM_J * S_EARTH / AU_J ** 2 * (R_J / d) ** 2 * phi


def contact_elong():
    """Elongation (deg) at which the Sun's limb touches Jupiter's equatorial limb (first / last contact)."""
    return jupiter_local()[2] + R_SUN_DEG


E_SUN = S_EARTH / AU_J ** 2                                   # W/m², sunlight at Io

P_ROT_J_IO = 1 / (1 / P_ROT_J - 1 / P_ORB_IO)               # h, Jupiter's rotation seen from Io (Io follows it round)
SUN_RATE = 360 / P_SYN                                       # deg/h, the Sun across Io's sky (elongation falls)
STAR_RATE = 360 / P_ORB_IO                                   # deg/h, the stars about Io's pole


# Per-shot picks (directing), everything else derived. 01: day, the Sun 5° up in the east (out of frame left), Jupiter
# 33 % lit (lit limb on the left, its lower limb lit as it enters), grazing light that carves the boot prints. 02 (user 2026-10-02: night): the Sun 13° below the horizon,
# Jupiter 93 % lit, the ridge and the figures in silhouette against it; 04 still: the Sun 2.5° inside the limb (eclipse peak in the beat sheet).
SHOT = {
    '01': dict(elong=70.0),
    '03': dict(hours=39.0, dur=12.0, rate0=0.6, ramp_in=2.0, ramp_out=3.0),
    '02': dict(elong=150.0),
    '04': dict(elong=contact_elong() - 2.5),
}


def _S(x):
    return x ** 3 - x ** 4 / 2                               # ∫ smoothstep from 0 to x; S(1) = ½


def lapse03(s):
    """03 time-lapse: clip second → hours since +0 h. The rate is `rate0` h/s at both ends, ramps up (smoothstep)
    over `ramp_in` s, cruises, ramps down over the last `ramp_out` s; the cruise rate makes the total `hours`."""
    c = SHOT['03']
    D, a, b, r0 = c['dur'], c['ramp_in'], c['ramp_out'], c['rate0']
    r1 = r0 + (c['hours'] - r0 * D) / (D - (a + b) / 2)
    s = min(max(s, 0.0), D)
    if s < a:
        G = a * _S(s / a)
    elif s > D - b:
        G = D - (a + b) / 2 - b * _S((D - s) / b)
    else:
        G = a / 2 + s - a
    return r0 * s + (r1 - r0) * G


def lapse03_elong(h):
    """03: the Sun's signed elongation (deg, east +) h hours in. Centred on midnight (180°, full Jupiter): it starts
    west of Jupiter (just past the last eclipse) and ends east of it (before the next one, shot 04)."""
    e = 180 + SHOT['03']['hours'] / 2 * SUN_RATE - h * SUN_RATE
    return (e + 180) % 360 - 180


def lapse03_second(h):
    """Inverse of lapse03 (bisection)."""
    lo, hi = 0.0, SHOT['03']['dur']
    for _ in range(50):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if lapse03(m) < h else (lo, m)
    return lo


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
    rows.append(('Jupiter rotation seen from Io', f'{P_ROT_J_IO:.2f} h (Io moves with it: {P_ROT_J} h inertial); '
                 f'GRS crosses the disc in ≈ {P_ROT_J_IO / 2:.1f} h; stars {STAR_RATE:.2f}°/h'))
    rows.append(('Jupiter rotation', f'{P_ROT_J} h inertial; GRS {GRS_W:,} km = {deg(GRS_W / d_sub):.1f}° across'))
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
    u, d, rj, rjp, ax = jupiter_local()
    el, az = alt_az(u)
    rows.append((f'Site: {SITE_THETA:.0f}° toward the north pole', f'Jupiter centre el {el:.2f}° az {az:.1f}°, '
                 f'radius {rj:.2f}° eq / {rjp:.2f}° pol, distance {d:,.0f} km, axis upright in frame (bands horizontal)'))
    rows.append(('Jupiter-shine on flat ground, full Jupiter', f'{jupiter_shine(180) * u[2]:.3f} W/m² '
                 f'(Jupiter {el:.1f}° up; {jupiter_shine(180):.2f} W/m² facing it)'))
    rows.append(('First/last contact (Sun limb on Jupiter limb)', f'elongation ±{contact_elong():.2f}°, '
                 f'{contact_elong() / (360 / P_SYN) * 60:.0f} min before/after mid-eclipse'))
    for E in (150, 120, 90, 75, 60, 30, contact_elong(), 0):
        se, sa = alt_az(sun_local(E))
        rows.append((f'Sun at elongation {E:.1f}° (east)', f'el {se:+.1f}° az {sa:+.1f}°; Jupiter {100 * lit_fraction(E):.0f} % lit; '
                     f'sun on flat ground {max(0, E_SUN * math.sin(math.radians(se))):.2f} W/m², '
                     f'Jupiter-shine facing it {jupiter_shine(E):.3f} W/m²'))
    c = SHOT['03']
    h_set = (lapse03_elong(0) + 90) / SUN_RATE
    h_rise = (lapse03_elong(0) + 360 - 90) / SUN_RATE
    lim = contact_elong() - R_SUN_DEG
    r_peak = max(lapse03(s + 0.01) - lapse03(s) for s in [i / 10 for i in range(120)]) * 100
    rows.append(('Shot 03 time-lapse', f'{c["hours"]:.0f} h in {c["dur"]:.0f} s, {c["rate0"]} h/s at the ends, peak {r_peak:.2f} h/s; '
                 f'Sun from elongation {lapse03_elong(0):+.2f}° to {lapse03_elong(c["hours"]):+.2f}° '
                 f'({abs(lapse03_elong(0)) - lim - R_SUN_DEG:.1f}° clear of the limb), Jupiter {100 * lit_fraction(lapse03_elong(0)):.0f} % lit at both ends; '
                 f'sunset +{h_set:.1f} h at {lapse03_second(h_set):.2f} s, midnight (100 %) at {lapse03_second(c["hours"] / 2):.2f} s, '
                 f'sunrise +{h_rise:.1f} h at {lapse03_second(h_rise):.2f} s; Jupiter turns {c["hours"] / P_ROT_J_IO:.2f}×'))
    for k, s in SHOT.items():
        if 'elong' not in s:
            continue
        se, sa = alt_az(sun_local(s['elong']))
        rows.append((f'Shot {k}', f'elongation {s["elong"]:.2f}°: Sun el {se:.2f}° az {sa:+.1f}°, '
                     f'Jupiter {100 * lit_fraction(s["elong"]):.0f} % lit'))
    w = max(len(a) for a, _ in rows)
    for a, b in rows:
        print(f'| {a:<{w}} | {b} |')
