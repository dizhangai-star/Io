"""Io · 永恒: every number the shots rely on, from constants. `python3 tools/physics.py` → the table for TREATMENT.md.

Conventions: km, s, degrees unless named. Io is tidally locked: Jupiter hangs at a fixed point in its sky; the Sun goes
round once per synodic day (42.46 h). Jupiter's phase seen from Io = the Sun's angle from Jupiter in Io's sky.
"""
import json
import math
import sys

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
    # 04 (beat sheet): the Sun `pre`° off the limb at 0 s, touches it at `contact` s, gone at `gone` s; time slows
    # from 03's end rate (0.6 h/s) to real time (log-rate eased, fit04), so the eclipse itself plays in real time.
    '04': dict(dur=20.0, pre=2.0, contact=4.0, gone=9.0),     # 20 s version (user 2026-10-03; was 14 / 3 / 5)
    # 05 (user 2026-10-03: rise as high as looks best → 100 km; the plume lights with the diamond). The cut from 04
    # skips ~2 h 17 min of the eclipse: 05 opens `contact` s before third contact in real time; from contact the rate
    # eases (smoothstep over `ramp` s) up to the rate that brings the whole Sun out by `full` s. Camera: holds `hold`
    # s, then rises log-eased (smoothstep in log altitude) from alt[0] m to alt[1] km by `rise` s, the lens zooming
    # lens[0] → lens[1] mm with the disc's top kept 0.7° under the frame top
    # (04's lens and margin at 0 s, so the ring sits on 04's last frame for the 04 → 05 dissolve, Sprint 4.01). Plume (Prometheus-type umbrella): apex
    # `h` km, ejecta up to `cone`° off vertical, vent `d` km from the site at azimuth `az`°: a little east, so the
    # sweeping light reaches it ≈ 2 s after the diamond (west of the site it lit before third contact).
    '05': dict(dur=10.0, contact=5.0, full=8.0, ramp=2.0, hold=1.0, rise=9.0, alt=(0.8, 100.0), lens=(28.0, 17.0),
               plume=dict(h=100.0, cone=24.0, d=450.0, az=-6.0)),
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


def sun_limb_sep(elong):
    """Angular distance (deg) of the Sun's centre outside Jupiter's limb (< 0: behind it), along the line from
    Jupiter's centre, using the oblate disc's radius at the Sun's position angle."""
    u, _, r_eq, r_pol, ax = jupiter_local()
    s = sun_local(elong)
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    z = tuple(a - dot(ax, u) * b for a, b in zip(ax, u))                       # north on the disc
    y = (u[1] * z[2] - u[2] * z[1], u[2] * z[0] - u[0] * z[2], u[0] * z[1] - u[1] * z[0])
    phi = math.atan2(dot(s, z), dot(s, y))
    r = r_eq * r_pol / math.hypot(r_pol * math.cos(phi), r_eq * math.sin(phi))
    return deg(math.acos(max(-1.0, min(1.0, dot(s, u))))) - r


def sun_visible(elong):
    """Fraction of the Sun's disc not hidden by Jupiter (the limb is straight across a 0.1° Sun)."""
    x = max(-1.0, min(1.0, sun_limb_sep(elong) / R_SUN_DEG))
    return 1 - (math.acos(x) - x * math.sqrt(1 - x * x)) / math.pi


def _elong_at_sep(sep):
    lo, hi = 0.0, 40.0
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if sun_limb_sep(m) < sep else (lo, m)
    return lo


def _rate04(s, t0, t1):
    """04: time rate (real s per clip s): log-rate eased (smoothstep) from 03's end rate at clip second t0 to 1 at t1."""
    x = min(max((s - t0) / (t1 - t0), 0.0), 1.0)
    return math.exp(math.log(SHOT['03']['rate0'] * 3600) * (1 - x * x * (3 - 2 * x)))


def _int04(a, b, t0, t1, n=400):
    h = (b - a) / n
    return h / 3 * sum((1 if i in (0, n) else 4 if i % 2 else 2) * _rate04(a + i * h, t0, t1) for i in range(n + 1))


_FIT04 = {}


def fit04():
    """04: (t0, t1) of the ease so that the Sun is `pre` deg (limb to limb) off Jupiter's limb at 0 s, touches it at
    `contact` s and is gone at `gone` s; cached. Returns (t0, t1, e_start, e_first, e_second)."""
    if not _FIT04:
        c = SHOT['04']
        e1, e2 = _elong_at_sep(R_SUN_DEG), _elong_at_sep(-R_SUN_DEG)
        e0 = _elong_at_sep(c['pre'] + R_SUN_DEG)
        pre, cover = (e0 - e1) / SUN_RATE * 3600, (e1 - e2) / SUN_RATE * 3600

        def t1_for(t0):                                    # the ease end that puts first contact at `contact`
            lo, hi = c['contact'], 40.0
            for _ in range(40):
                m = (lo + hi) / 2
                lo, hi = (lo, m) if _int04(0.0, c['contact'], t0, m) > pre else (m, hi)
            return (lo + hi) / 2
        lo, hi = -8.0, c['contact'] - 0.5                  # then the ease start that puts second contact at `gone`
        for _ in range(40):
            m = (lo + hi) / 2
            t1 = t1_for(m)
            lo, hi = (lo, m) if _int04(c["contact"], c["gone"], m, t1) < cover else (m, hi)
        t0 = (lo + hi) / 2
        _FIT04.update(t0=t0, t1=t1_for(t0), e0=e0, e1=e1, e2=e2)
    f = _FIT04
    return f['t0'], f['t1'], f['e0'], f['e1'], f['e2']


def lapse04(s):
    """04: clip second → real seconds since first contact (< 0 before it)."""
    t0, t1, *_ = fit04()
    c = SHOT['04']
    return _int04(c['contact'], s, t0, t1, n=max(40, int(abs(s - c['contact']) * 60)))


def rate04(s):
    """04: time rate at clip second s (real s per clip s)."""
    t0, t1, *_ = fit04()
    return _rate04(s, t0, t1)


def lapse04_elong(s):
    """04: the Sun's elongation (deg) at clip second s (it falls: the Sun slides into Jupiter's east limb)."""
    return fit04()[3] - lapse04(s) / 3600 * SUN_RATE


def egress05():
    """05: (e3, e4, T, r1): elongation (deg, < 0, west) at third contact (the Sun's leading limb leaves Jupiter's
    west limb) and at fourth (the whole disc out), the real seconds between, and the eased peak rate."""
    c = SHOT['05']
    e3, e4 = -_elong_at_sep(-R_SUN_DEG), -_elong_at_sep(R_SUN_DEG)
    T = (e3 - e4) / SUN_RATE * 3600
    # τ(full) = (full − contact) + (r1 − 1)·(full − contact − ramp/2) = T
    r1 = 1 + (T - (c['full'] - c['contact'])) / (c['full'] - c['contact'] - c['ramp'] / 2)
    return e3, e4, T, r1


def rate05(s):
    c = SHOT['05']
    r1 = egress05()[3]
    x = min(max((s - c['contact']) / c['ramp'], 0.0), 1.0)
    return 1 + (r1 - 1) * x * x * (3 - 2 * x)


def lapse05(s):
    """05: clip second → real seconds since third contact (real time before it, eased up after)."""
    c = SHOT['05']
    r1 = egress05()[3]
    x = s - c['contact']
    if x <= 0:
        return x
    G = c['ramp'] * _S(x / c['ramp']) if x < c['ramp'] else c['ramp'] / 2 + x - c['ramp']
    return x + (r1 - 1) * G


def lapse05_elong(s):
    """05: the Sun's elongation (deg) at clip second s (falling: the Sun leaves Jupiter's west limb)."""
    return egress05()[0] - lapse05(s) / 3600 * SUN_RATE


def sun_offset_dir(elong):
    """Unit vector (local) across the sky from Jupiter's centre toward the Sun (perpendicular to Jupiter's direction).
    A point displaced Δ (km) from the site sees Jupiter shifted −Δ/d by parallax, so the Sun's limb distance there is
    sun_limb_sep + deg(Δ·n / d): the eclipse shadow's edge sweeps across the ground (05)."""
    u, s = jupiter_local()[0], sun_local(elong)
    k = sum(a * b for a, b in zip(s, u))
    n = tuple(a - k * b for a, b in zip(s, u))
    m = math.sqrt(sum(a * a for a in n))
    return tuple(a / m for a in n)


def rise05(s):
    """05: camera altitude (m) above the ground at clip second s (smoothstep in log altitude)."""
    c = SHOT['05']
    x = min(max((s - c['hold']) / (c['rise'] - c['hold']), 0.0), 1.0)
    x = x * x * (3 - 2 * x)
    a0, a1 = math.log(c['alt'][0]), math.log(c['alt'][1] * 1000)
    return math.exp(a0 + (a1 - a0) * x), x


def lens05(x):
    """05: focal length (mm) at rise progress x (0..1, log-interpolated like the altitude)."""
    l0, l1 = SHOT['05']['lens']
    return math.exp(math.log(l0) + (math.log(l1) - math.log(l0)) * x)


def dip(alt_km):
    """Horizon dip (deg) and distance (km) seen from alt_km above a smooth Io."""
    return deg(math.acos(R_IO / (R_IO + alt_km))), math.sqrt(2 * R_IO * alt_km + alt_km ** 2)


def umbrella(h_max, cone):
    """A ballistic plume (1/r gravity, no air): launch speed for apex h_max (km) straight up, and the surface range
    (km) of a particle launched at `cone` deg off vertical with that speed: the radius of the deposit ring, where the
    umbrella's outer curtain lands. Returns (v km/s, ring radius km, its flight s)."""
    v = plume(h_max)[0]
    a = math.radians(cone)
    x, y, vx, vy, t, dt = 0.0, R_IO, v * math.sin(a), v * math.cos(a), 0.0, 0.25
    while True:
        r = math.hypot(x, y)
        g = GM_IO / r ** 3
        vx, vy = vx - g * x * dt, vy - g * y * dt
        x, y, t = x + vx * dt, y + vy * dt, t + dt
        if math.hypot(x, y) <= R_IO:
            return v, R_IO * math.atan2(x, y), t


def lapse03_second(h):
    """Inverse of lapse03 (bisection)."""
    lo, hi = 0.0, SHOT['03']['dur']
    for _ in range(50):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if lapse03(m) < h else (lo, m)
    return lo


def card():
    """The numbers on the 06 title card (tools/card.mjs reads `python3 tools/physics.py --card`)."""
    dj = 2 * deg(math.asin(R_J / (A_IO - R_IO)))
    return {'jupiter_deg': round(dj, 1), 'moons': round(dj / 0.52), 'moves_deg_h': 0,
            'eclipse_every_h': round(P_SYN, 2), 'eclipse_h': round(2 * R_J / V_IO / 3600, 2)}


if __name__ == '__main__' and '--card' in sys.argv:
    print(json.dumps(card()))
elif __name__ == '__main__':
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
    c = SHOT['04']
    t0, t1, e0, e1, e2 = fit04()
    rt = lambda s: _rate04(s, t0, t1)
    rows.append(('Shot 04 eclipse ingress', f'{c["dur"]:.0f} s; rate eased (log) from {SHOT["03"]["rate0"] * 3600:.0f}× at '
                 f'{t0:+.2f} s to 1× at {t1:.2f} s: {rt(0):.0f}× at 0 s, {rt(c["contact"]):.0f}× at first contact '
                 f'{c["contact"]:.1f} s, {rt(c["gone"]):.1f}× at second contact {c["gone"]:.1f} s; elongation '
                 f'{e0:.2f}° → {e1:.2f}° → {e2:.2f}° → {lapse04_elong(c["dur"]):.2f}° at the end '
                 f'({lapse04(0) / 60:+.1f} → {lapse04(c["dur"]):+.1f} s real from contact; stars and Sun '
                 f'{rt(0) * SUN_RATE / 3600:.2f}°/s at 0 s); Sun {100 * sun_visible(e0):.0f} % → '
                 f'{100 * sun_visible(lapse04_elong((c["contact"] + c["gone"]) / 2)):.0f} % at '
                 f'{(c["contact"] + c["gone"]) / 2:.1f} s → {100 * sun_visible(e2):.0f} %'))
    c = SHOT['05']
    e3, e4, T, r1 = egress05()
    _, dj_km, *_ = jupiter_local()
    n = sun_offset_dir(e3)
    se, sa = alt_az(sun_local(e3))
    rows.append(('Shot 05 eclipse egress', f'{c["dur"]:.0f} s; the cut from 04 skips '
                 f'{((e2 - e3) / SUN_RATE * 3600 - (lapse04(SHOT["04"]["dur"]) - lapse04(SHOT["04"]["gone"])) - c["contact"]) / 60:.0f} min; third contact '
                 f'(elongation {e3:.2f}°, Sun el {se:.1f}° az {sa:+.1f}°, west limb) at {c["contact"]:.1f} s in real '
                 f'time, then eased to {r1:.1f}× over {c["ramp"]:.0f} s: whole Sun out ({e4:.2f}°, {T:.0f} s real) at '
                 f'{c["full"]:.1f} s; Sun {100 * sun_visible(lapse05_elong(6.0)):.0f} % at 6 s, '
                 f'{100 * sun_visible(lapse05_elong(7.0)):.0f} % at 7 s; the shadow edge sweeps the ground toward '
                 f'({n[0]:+.2f}, {n[1]:+.2f}, {n[2]:+.2f}) at {V_IO:.1f} km/s × rate ({V_IO * r1:.0f} km/s at the peak); '
                 f'penumbra {2 * R_SUN_DEG * math.pi / 180 * dj_km:.0f} km wide'))
    for s in (0.0, c['hold'], 3.0, c['contact'], 7.0, c['rise']):
        a, x = rise05(s)
        dp, dh = dip(a / 1000)
        rows.append((f'Shot 05 camera at {s:.1f} s', f'{a:,.1f} m up, {lens05(x):.1f} mm; horizon dip {dp:.2f}°, '
                     f'{dh:,.1f} km away'))
    p = c['plume']
    v, ring, tf = umbrella(p['h'], p['cone'])
    rows.append(('Shot 05 plume', f'apex {p["h"]:.0f} km (vent {v * 1000:.0f} m/s), ejecta ≤ {p["cone"]:.0f}° off '
                 f'vertical → deposit ring radius {ring:.0f} km (flight {tf / 60:.1f} min); vent {p["d"]:.0f} km out at '
                 f'az {p["az"]:+.0f}°: {hidden(p["d"]):.0f} km hidden from the ground'))
    for k, s in SHOT.items():
        if 'elong' not in s:
            continue
        se, sa = alt_az(sun_local(s['elong']))
        rows.append((f'Shot {k}', f'elongation {s["elong"]:.2f}°: Sun el {se:.2f}° az {sa:+.1f}°, '
                     f'Jupiter {100 * lit_fraction(s["elong"]):.0f} % lit'))
    w = max(len(a) for a, _ in rows)
    for a, b in rows:
        print(f'| {a:<{w}} | {b} |')
