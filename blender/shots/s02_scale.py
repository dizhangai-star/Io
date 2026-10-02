"""02 · scale (Sprint 1 look spike: static).  135 mm, locked, 1 km from a ridge (user 2026-10-02).

A ridge ~150 m high crosses the frame 1 km out; its crest (≈ 8° up) hides Jupiter's lower limb, so the planet
stands behind it as a wall wider than the frame. An astronaut (proxy) and the lander (proxy) on the crest, against the
disc. Night (user 2026-10-02): the Sun 13° below the horizon (elongation 150°, physics.SHOT['02']), Jupiter 93 % lit,
ridge and figures in silhouette; --elong 80 gives the day variant (Sun 2.6° up, Jupiter 41 % lit).

    node preview.mjs 02-scale 0 --pct 50          (→ frames/02-scale-strip.png)
Options: --elong DEG  --exposure EV  --az DEG (frame centre azimuth)  --pitch DEG  --grs DEG  --stars GAIN  --proxy 0
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
from mathutils import Vector
import physics
from lib import nodes, rig, shot, io_world, jupiter, sky
for m in (physics, nodes, rig, shot, io_world, jupiter, sky):
    importlib.reload(m)
W = io_world
P = physics

A = shot.args()
LENS = 135.0
EYE = 1.7
AZ = float(A.opt('az', -1.5))                 # frame centre: 1.5° left of Jupiter's centre, toward the lit limb
PITCH = float(A.opt('pitch', 10.6))
D = 1000.0                                    # ridge distance (m)
ELONG = float(A.opt('elong', P.SHOT['02']['elong']))      # --elong 80: the day variant

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


if A.opt('proxy', '1') == '1':
    ax = D * math.tan(math.radians(-3.0))
    ay, az_ = crest(ax)
    W.astronaut_proxy(sc, (ax, ay + 1.0, az_), heading=200)
    lx = D * math.tan(math.radians(-1.8))
    ly, lz = crest(lx)
    W.lander_proxy(sc, (lx, ly + 5.0, W.ground_z(height, lx, ly + 5.0)), heading=20)
    print(f'NOTE crest: astronaut ({ax:.0f}, {ay:.0f}) at {az_ - cam_loc.z:.0f} m above the eye, '
          f'{math.degrees(math.atan2(az_ - cam_loc.z, math.hypot(ax, ay))):.2f}° up')

# ---------------------------------------------------------------- sky, Sun, Jupiter
sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('stars', 20.0)))
jupiter.build(sc, cam_loc, grs=float(A.opt('grs', -40.0)))

# ---------------------------------------------------------------- camera
d = Vector((math.sin(math.radians(AZ)) * math.cos(math.radians(PITCH)),
            math.cos(math.radians(AZ)) * math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))))
cam = rig.camera(sc, cam_loc, cam_loc + d * D, lens=LENS, fstop=8.0, focus=cam_loc + d * D)
cam.data.clip_start, cam.data.clip_end = 0.5, 2.0e6

shot.run(sc, A)
