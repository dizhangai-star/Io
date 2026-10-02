"""04 · eclipse (Sprint 1 look spike: the peak, static).  28 mm, locked, the whole disc in frame.

The Sun is 2.5° inside Jupiter's limb (physics.SHOT['04']): Jupiter a black disc ringed in red-orange (brightest on
the side where the Sun went in), the ground in Jupiter's shadow, lit only by lava: a lava lake on the plain below
and hot cracks on the slope in front. Exposure is the "eyes adjusted" state (beat 9.0 s).

Lens: 35 mm (the treatment) leaves no ground: the disc spans 5.6°–23.9° up and the frame is 24.3° tall. 28 mm
(30.1° tall) from a 40 m rise puts the lake ~1 km out at the bottom of the frame.

    node preview.mjs 04-eclipse 0 --pct 50        (→ frames/04-eclipse-strip.png)
Options: --exposure EV  --lens MM  --pitch DEG  --ring STRENGTH  --glow LAVA  --stars GAIN
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
LENS = float(A.opt('lens', 28.0))
EYE = 1.7
ELONG = float(A.opt('elong', P.SHOT['04']['elong']))
u, _, r_eq, r_pol, _ = P.jupiter_local()
J_EL = P.alt_az(u)[0]
VFOV = 2 * math.degrees(math.atan(18.0 * shot.RES[1] / shot.RES[0] / LENS))
PITCH = float(A.opt('pitch', J_EL + r_pol + 0.7 - VFOV / 2))      # disc top 0.7° under the frame top

sc = rig.new_scene('S04_Eclipse')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
sky.exposure(sc, float(A.opt('exposure', 0.0)))

LAKE = (-140.0, 950.0, 210.0)          # x, y, radius (m)
LAKE_Z = -5.0


# ---------------------------------------------------------------- ground: a low rise under the camera, the plain, a lake
def height(X, Y):
    r = np.hypot(X, Y)
    plain = 2.5 * (W.fbm(X / 220, Y / 220, 4, 11) - 0.5) + 0.5 * (W.fbm(X / 25, Y / 25, 4, 12) - 0.5)
    rise = 40.0 * np.exp(-(r / 260.0) ** 2) * (0.85 + 0.3 * W.fbm(X / 90, Y / 90, 3, 13))
    dl = np.hypot(X - LAKE[0], Y - LAKE[1])
    shore = W.smooth(LAKE[2] * 1.02, LAKE[2] * 1.25, dl)                  # 0 in the lake, 1 beyond the levee
    levee = 3.0 * np.exp(-((dl - LAKE[2] * 1.12) / 18.0) ** 2)
    return (plain + rise) * shore + LAKE_Z * (1 - shore) + levee


rr = W.rings(2.0, 12000.0, 0.004, bands=[(700, 1250, 1.0)])
half = math.degrees(math.atan(18 / LENS)) + 3.0
W.terrain(sc, 'Ground', rr, 0.0, half, 900, height, W.surface('IoSurface', dark=0.6, red=0.6))
W.io_body(sc)
z0 = W.ground_z(height, 0, 0)
cam_loc = Vector((0.0, 0.0, z0 + EYE))

glow = float(A.opt('glow', 2.0))
dl = math.hypot(LAKE[0], LAKE[1])
W.lava_lake(sc, 'LavaLake', LAKE[:2], LAKE[2], LAKE_Z + 0.05 - dl * dl / (2 * W.R_IO_M), glow=glow)
rng = np.random.default_rng(4)
vents = []
for _ in range(22):                                                    # hot cracks on the plain, 0.4-1.6 km out
    a, r = math.radians(rng.uniform(-28, 28)), rng.uniform(420, 1600)
    x, y = r * math.sin(a), r * math.cos(a)
    vents.append((x, y, W.ground_z(height, x, y)))
W.vent_glow(sc, 'Vents', vents, size=1.5, temp=1100.0, glow=glow * 3.0)

# ---------------------------------------------------------------- sky, Sun (behind Jupiter), Jupiter + ring
sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('stars', 3.0)), density=0.3)
jupiter.build(sc, cam_loc, grs=-40.0, ring=float(A.opt('ring', 3.0)), sun_elong=ELONG)

# ---------------------------------------------------------------- camera
d = Vector((0.0, math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))))
cam = rig.camera(sc, cam_loc, cam_loc + d * 1000, lens=LENS, fstop=5.6, focus=cam_loc + d * 1000)
cam.data.clip_start, cam.data.clip_end = 0.5, 2.0e6
print(f'NOTE 04: lens {LENS} mm, vfov {VFOV:.1f}°, pitch {PITCH:.2f}°, Sun elongation {ELONG:.2f}° '
      f'({r_eq - ELONG:.2f}° inside the limb)')

shot.run(sc, A)
