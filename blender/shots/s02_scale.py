"""02 · scale (Sprint 3).  135 mm, locked, 1 km from a ridge (user 2026-10-02).

A ridge ~150 m high crosses the frame 1 km out; its crest (≈ 8° up) hides Jupiter's lower limb, so the planet
stands behind it as a wall wider than the frame. The astronaut (EMU, Breathing Idle) and the lander on the crest,
against the disc. Night (user 2026-10-02): the Sun 13° below the horizon (elongation 150°, physics.SHOT['02']),
Jupiter 93 % lit, ridge and figures in silhouette; --elong 80 gives the day variant (Sun 2.6° up, Jupiter 41 % lit).
No plume (user 2026-10-03: a plume whose top is in this 6.4°-tall frame is wider than the frame; it moves to 05).

Action (one): at 1 km the astronaut is ≈ 14 px tall, so a lean alone moves the helmet ~1.5 px. The look-up is a lean
back of the upper body (15°) plus the near (right) arm raised to point up at Jupiter (115° from hanging): idle
0–2.5 s, raise 2.5–4.5 s (caption 4.0–9.5), hold, lower 8.0–9.8 s, the lean held to the end.

    node render.mjs 02-scale --animatic --pct 100     (→ out/02-scale-animatic.mp4; figures ≈ 14 px, review crop below)
    node preview.mjs 02-scale 1 5 9 --pct 50
Options: --elong DEG  --exposure EV  --az DEG (frame centre azimuth)  --pitch DEG  --grs DEG  --stars GAIN
         --lean DEG  --point DEG  --heading DEG  --proxy 1 (box figures)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Quaternion, Vector
import physics
from lib import nodes, rig, shot, io_world, jupiter, sky, astronaut, retarget, lander
for m in (physics, nodes, rig, shot, io_world, jupiter, sky, astronaut, retarget, lander):
    importlib.reload(m)
W = io_world
P = physics

A = shot.args()
FPS = 24
LENS = 135.0
EYE = 1.7
AZ = float(A.opt('az', -1.5))                 # frame centre: 1.5° left of Jupiter's centre, toward the lit limb
PITCH = float(A.opt('pitch', 10.6))
D = 1000.0                                    # ridge distance (m)
ELONG = float(A.opt('elong', P.SHOT['02']['elong']))      # --elong 80: the day variant
LEAN = float(A.opt('lean', 15.0))             # upper-body lean back (deg)
POINT = float(A.opt('point', 115.0))          # right arm raised forward, from hanging (deg)
HEADING = float(A.opt('heading', 125.0))      # facing right and away (toward Jupiter's centre), near arm = right
T_UP, T_HOLD, T_DOWN = (2.5, 4.5), 8.0, 9.8   # raise, start lowering, down (s)

sc = rig.new_scene('S02_Scale')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
sky.exposure(sc, float(A.opt('exposure', -4.8)))


# ---------------------------------------------------------------- ground: plain + the ridge
def height(X, Y):
    plain = 3.0 * (W.fbm(X / 250, Y / 250, 4, 3) - 0.5) + 0.6 * (W.fbm(X / 30, Y / 30, 4, 4) - 0.5)
    yc = D - 0.5 * X + 110 * (W.fbm(X / 350, 3.3 + 0 * X, 4, 5) - 0.5)          # crest line: nearer on the right, so the face looks NE, toward the Sun
    hc = 150 + 27 * (W.fbm(X / 250, 7.7 + 0 * X, 3, 6) - 0.5)                       # crest height
    t = Y - yc
    s = np.clip(1 + t / 190.0, 0, 1)                                                # front face (toward us)
    front = hc * s ** 1.8
    back = hc * (1 - 0.7 * W.smooth(30, 400, t))                                    # plateau, then a long fall
    ridge = np.where(t < 0, front, back)
    spur = (W.fbm(X / 50, Y / 50, 5, 8) - 0.5) * 47 * s * (1 - s) * 4             # spurs and gullies on the face
    return plain + ridge + np.where(t < 0, spur, 0)


rr = W.rings(3.0, 9000.0, 0.004, bands=[(700, 1450, 0.5)])
half = math.degrees(math.atan(18 / LENS)) + 2.0
ground = W.terrain(sc, 'Ground', rr, AZ, half, 720, height, W.surface('IoSurface'))
W.io_body(sc)

z0 = W.ground_z(height, 0, 0)
cam_loc = Vector((0.0, 0.0, z0 + EYE))


def crest(x):
    ys = np.arange(D - 330.0, D + 400.0, 0.25)
    hs = height(np.full_like(ys, x), ys) - (x * x + ys * ys) / (2 * W.R_IO_M)
    k = int(np.argmax(hs >= hs.max() - 0.3))       # the front edge, not anywhere on the plateau behind it
    return float(ys[k]), float(hs[k])


# ---------------------------------------------------------------- the figures on the crest
ax = D * math.tan(math.radians(-3.0))
ay, _ = crest(ax)
a_loc = (ax, ay + 1.0, W.ground_z(height, ax, ay + 1.0))
lx = D * math.tan(math.radians(-1.8))
ly, _ = crest(lx)
l_ctr = (lx, ly + 6.0)                             # 6 m behind the edge: the pads (4 m out) stay on the plateau
l_z = min(W.ground_z(height, *lander.pad_xy(l_ctr, 20.0, k)) for k in range(4)) - 0.05

if A.opt('proxy', '0') == '1':
    W.astronaut_proxy(sc, a_loc, heading=HEADING)
    W.lander_proxy(sc, (*l_ctr, W.ground_z(height, *l_ctr)), heading=20)
    arm = None
else:
    arm = astronaut.load(sc, a_loc, heading=HEADING)
    lander.build(sc, l_ctr, 20.0, l_z)


def ramp(t, a, b):
    u = min(max((t - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


def up(f):
    """0 → 1 → 0: raise, hold, lower."""
    t = (f - 1) / FPS
    return ramp(t, *T_UP) * (1 - ramp(t, T_HOLD, T_DOWN))


if arm is not None and arm.type == 'ARMATURE':
    lean = lambda f: Quaternion((1, 0, 0), -math.radians(LEAN) * ramp((f - 1) / FPS, *T_UP))       # held after
    point = lambda f: Quaternion((1, 0, 0), -math.radians(POINT) * up(f))                           # forward, up
    retarget.retarget(sc, arm, 'Breathing Idle.fbx', extra={'chest': lean, 'upper_arm.R': point})

# ---------------------------------------------------------------- sky, Sun, Jupiter
sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('stars', 20.0)))
jupiter.build(sc, cam_loc, grs=float(A.opt('grs', -40.0)))

# ---------------------------------------------------------------- camera (locked)
d = Vector((math.sin(math.radians(AZ)) * math.cos(math.radians(PITCH)),
            math.cos(math.radians(AZ)) * math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))))
cam = rig.camera(sc, cam_loc, cam_loc + d * D, lens=LENS, fstop=8.0, focus=cam_loc + d * D)
cam.data.clip_start, cam.data.clip_end = 0.5, 2.0e6

bpy.context.view_layer.update()
pxm = shot.RES[0] / (2 * D * math.tan(math.atan(18 / LENS)))
for nm, p in (('astronaut', Vector(a_loc) + Vector((0, 0, 0.95))), ('lander', Vector((*l_ctr, l_z + 2.0)))):
    v = world_to_camera_view(sc, cam, p)
    print(f'NOTE 02 {nm}: frame px ({v.x * shot.RES[0]:.0f}, {(1 - v.y) * shot.RES[1]:.0f}) of {shot.RES}; '
          f'{math.degrees(math.atan2(p.z - cam_loc.z, p.xy.length)):.2f}° up; {pxm:.1f} px/m at 1 km')

shot.run(sc, A)
