"""03 · eternity (Sprint 3).  20 mm, locked off on a tripod: 39 h of Io in 12 s, and Jupiter does not move.

The landing site of 01 (lib/landing.py) from 22 m further back: the frost plain, the boot-print trail running out
toward Jupiter, the lander right of the disc (its shadow is the clock hand), the massif on the horizon right.
Time (user 2026-10-03: 40 h without an eclipse, eased rate): physics.SHOT['03'] / lapse03: 39 h centred on midnight,
0.6 h/s at the ends, ≈ 4 h/s between. It opens with the Sun just clear of Jupiter's right limb (2 % crescent, the
last eclipse just over), the Sun slides out right and sets (3.1 s), night: Jupiter waxes to full (5.8 s, the Great
Red Spot on the central meridian then) lighting the plain alone, the stars wheel about the pole behind us; sunrise
on the left (8.5 s), long shadows sweep, and it ends with the Sun nearing the left limb, a thin crescent again (04
picks up there). Jupiter turns 3× (12.95 h seen from Io). Sun, phase, stars, Jupiter's spin: all from physics.

Stars turn as a world rotation about Io's pole and smear over the shutter (`taps` lookups: trails); Jupiter's spin and
everything else blur by Cycles motion blur (shutter 0.5). Exposure fixed for Jupiter (its lit face is equally bright
at every phase); `--lift EV` opens it up while the Sun is down (holy-grail ramp, +1.5 by default).

    node render.mjs 03-eternity --animatic --engine eevee     (light is the beat: EEVEE, not Workbench)
    node preview.mjs 03-eternity 0.5 5.8 11.5 --pct 50
Options: --exposure EV  --lift EV  --glare STRENGTH (0 = off)  --pitch DEG  --stars GAIN  --taps N  --grs-mid DEG  --eye M
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import bpy
from mathutils import Matrix, Quaternion, Vector
import physics
from lib import nodes, rig, shot, io_world, jupiter, sky, prints, lander, landing
for m in (physics, nodes, rig, shot, io_world, jupiter, sky, prints, lander, landing):
    importlib.reload(m)
W = io_world
P = physics
L = landing

A = shot.args()
FPS = 24
LENS = 20.0
EYE = float(A.opt('eye', 1.5))                                   # tripod
O = (-3.5, -22.0)                                                # the camera in the site frame: 22 m behind 01's spot
PITCH = float(A.opt('pitch', 6.5))                               # frame −14.2°…+27.2°: Jupiter 5.6°…23.9°, horizon at 35 %
HALF = 56.0                                                      # terrain sector ± (hfov ± 42°, + room for side light)
EV = float(A.opt('exposure', -4.5))
LIFT = float(A.opt('lift', 1.5))                               # night: +1.5 EV (Jupiter stays readable; +2 washed it out)
C = P.SHOT['03']
SHUTTER = 0.5
assert abs(A.frames / FPS - C['dur']) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, physics.SHOT 03 says {C["dur"]} s'

sc = rig.new_scene('S03_Eternity')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = SHUTTER

# ---------------------------------------------------------------- ground, trail, massif, lander (lib/landing.py)
height = L.shifted(L.height, O)
mat = W.surface('IoSurface', frost=1.0, prints=True, clod=0.06)
near = W.terrain(sc, 'GroundNear', W.rings(3.0, 130.0, 0.003), 0.0, HALF, 1201, height, mat)
far = W.terrain(sc, 'GroundFar', W.rings(130.0, 9000.0, 0.004), 0.0, HALF, 401, height, mat)
for ob in (near, far):
    L.mark_prints(ob, O)
W.terrain(sc, 'Massifs', W.rings(60000.0, 200000.0, 0.004), 0.0, HALF, 1201, L.shifted(L.mountains, O),
          W.surface('IoMassif', scale=30.0, frost=0.3))
W.io_body(sc)
L.build_lander(sc, height, O)
cam_loc = Vector((0.0, 0.0, W.ground_z(height, 0, 0) + EYE))

# ---------------------------------------------------------------- sky: Sun (lamp + disc), turning stars, Jupiter
h0 = P.lapse03(0.0)
sun = sky.sun(sc, P.lapse03_elong(h0))
sun.rotation_mode = 'QUATERNION'
disc = sky.sun_disc(sc, P.lapse03_elong(h0))
u_j, _, _, _, pole = P.jupiter_local()
world, turn, smear = sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('stars', 20.0)), axis=pole,
                               taps=int(A.opt('taps', 12)))
GRS_MID = float(A.opt('grs-mid', 0.0))                           # the GRS's longitude from the central meridian at midnight
grs0 = GRS_MID - 360.0 * (C['hours'] / 2) / P.P_ROT_J_IO
jup, _ = jupiter.build(sc, cam_loc, grs=grs0)
sun_j, _ = jupiter.io_shadow(sc, sun, jup, (0.0, 0.0, W.ground_z(height, 0, 0)))
if float(A.opt('glare', 1.0)) > 0:
    sky.glare(sc, strength=float(A.opt('glare', 1.0)))
J_LOC, J_ROT, J_SCL = jup.matrix_world.decompose()
jup.rotation_mode = 'QUATERNION'

cam = rig.camera(sc, cam_loc, cam_loc + Vector((0, 1, 0)), lens=LENS, fstop=8.0, focus=cam_loc + Vector((0, 25.0, 0)))
cam.data.clip_start, cam.data.clip_end = 0.05, 2.0e6
cam.rotation_euler = (math.radians(90.0 + PITCH), 0.0, 0.0)

# ---------------------------------------------------------------- the clock: one key per frame, straight between
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


q_prev = None
log = []
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    h = P.lapse03(t)
    rate = (P.lapse03(t + 0.005) - P.lapse03(t - 0.005)) / 0.01            # h per clip second
    e = P.lapse03_elong(h)
    u = Vector(P.sun_local(e))
    q = (-u).to_track_quat('-Z', 'Y')
    if q_prev is not None and q.dot(q_prev) < 0:
        q.negate()
    q_prev = q
    for s_ in (sun, sun_j):
        s_.rotation_quaternion = q
        s_.keyframe_insert('rotation_quaternion', frame=f)
    disc.location = cam_loc + u * disc['dist']
    disc.keyframe_insert('location', frame=f)
    turn.outputs[0].default_value = math.radians(P.STAR_RATE * h)
    turn.outputs[0].keyframe_insert('default_value', frame=f)
    smear.outputs[0].default_value = math.radians(P.STAR_RATE * rate * SHUTTER / FPS)
    smear.outputs[0].keyframe_insert('default_value', frame=f)
    spin = Quaternion((0.0, 0.0, 1.0), math.radians(360.0 * h / P.P_ROT_J_IO))
    jup.location, jup.rotation_quaternion, jup.scale = J_LOC, J_ROT @ spin, J_SCL
    jup.keyframe_insert('location', frame=f)
    jup.keyframe_insert('rotation_quaternion', frame=f)
    el = P.alt_az(u)[0]
    sc.view_settings.exposure = EV + LIFT * smoothstep(3.0, -5.0, el)
    sc.view_settings.keyframe_insert('exposure', frame=f)
    if f % 24 == 1 or f == sc.frame_end:
        log.append(f'{t:4.1f}s +{h:4.1f}h e{e:+6.1f} el{el:+5.1f} {100 * P.lit_fraction(e):3.0f}%')

lx, ly = L.LANDER[0] - O[0], L.LANDER[1] - O[1]
print(f'NOTE 03: lander az {math.degrees(math.atan2(lx, ly)):.1f}° at {math.hypot(lx, ly):.1f} m; ' + ' | '.join(log))

shot.run(sc, A)
