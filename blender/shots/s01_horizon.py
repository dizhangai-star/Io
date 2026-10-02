"""01 · horizon (Sprint 3).  24 mm, eye 1.6 m, one slow tilt from the ground up to Jupiter.

Day: the Sun 5° up in the east, out of frame left (elongation 70°, physics.SHOT['01']), Jupiter 33 % lit. The shot
opens on boot prints in frost and a lander footpad (right), grazing light carving them; the camera tilts up along
the trail (out toward Jupiter and back) to a bare horizon and a black sky with stars, and Jupiter's lower limb enters
the frame top and keeps coming until the camera stops with the horizon low and the planet over the upper half.

Tilt: −30° (frame −47°…−13°: ground 1.5–7 m out) → +14° (frame −3°…+31°; Jupiter 5.6°…23.9°; user 2026-10-03), trapezoid speed
with smooth ramps, hold 0–0.8 s and 7.4–9 s (caption IO 5.5–8.6). Jupiter's limb enters the frame top at pitch
≈ −12°. Lander = lib/lander.py: only one footpad, its leg and the ladder foot are in frame; the body is right of it.

    node render.mjs 01-horizon --animatic        (→ out/01-horizon-animatic.mp4)
    node preview.mjs 01-horizon 0.5 4.5 8.5 --pct 50
Options: --elong DEG  --exposure EV  --pitch0 DEG  --pitch1 DEG  --t0 S  --t1 S  --stars GAIN  --frost 0..1
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
from lib import nodes, rig, shot, io_world, jupiter, sky, prints, lander, landing
for m in (physics, nodes, rig, shot, io_world, jupiter, sky, prints, lander, landing):
    importlib.reload(m)
W = io_world
P = physics

A = shot.args()
FPS = 24
LENS = 24.0
EYE = 1.6
ELONG = float(A.opt('elong', P.SHOT['01']['elong']))
PITCH0, PITCH1 = float(A.opt('pitch0', -30.0)), float(A.opt('pitch1', 14.0))
T0, T1 = float(A.opt('t0', 0.8)), float(A.opt('t1', 7.4))       # tilt start / end (s)
HALF = 52.0                                                      # terrain sector ± (deg): the −30° frame's corners are at ±47°

sc = rig.new_scene('S01_Horizon')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
sky.exposure(sc, float(A.opt('exposure', -3.0)))

# ---------------------------------------------------------------- the landing site (lib/landing.py: lander right, the trail)
L = landing
PR = L.PR
height = L.height
mat = W.surface('IoSurface', frost=float(A.opt('frost', 1.0)), prints=True, clod=float(A.opt('clod', 0.06)))
near = W.terrain(sc, 'GroundNear', W.rings(0.5, 24.0, 0.0025), 0.0, HALF, 1201, height, mat)
far = W.terrain(sc, 'GroundFar', W.rings(24.0, 9000.0, 0.004), 0.0, HALF, 401, height, mat)
for ob in (near, far):
    L.mark_prints(ob)
W.terrain(sc, 'Massifs', W.rings(60000.0, 200000.0, 0.004), 0.0, HALF, 1201, L.mountains,
          W.surface('IoMassif', scale=30.0, frost=0.3))
W.io_body(sc)

z0 = W.ground_z(height, 0, 0)
cam_loc = Vector((0.0, 0.0, z0 + EYE))

L.build_lander(sc, height)                                      # the pad sunk 4 cm

# ---------------------------------------------------------------- sky, Sun, Jupiter
sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('stars', 6.0)))
jupiter.build(sc, cam_loc, grs=float(A.opt('grs', -40.0)))


# ---------------------------------------------------------------- camera: one tilt
def ease(x, a=0.25, b=0.45):
    """0..1 → 0..1: speed ramps up (smoothstep) over the first `a`, cruises, ramps down over the last `b`."""
    v = 1.0 / (1.0 - a / 2 - b / 2)
    S = lambda t: t ** 3 - t ** 4 / 2                            # ∫ smoothstep, S(1) = ½
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x < a:
        return v * a * S(x / a)
    if x > 1 - b:
        return 1.0 - v * b * S((1 - x) / b)
    return v * (a / 2 + x - a)


cam = rig.camera(sc, cam_loc, cam_loc + Vector((0, 1, 0)), lens=LENS, fstop=8.0, focus=cam_loc + Vector((0, 2.6, 0)))
cam.data.clip_start, cam.data.clip_end = 0.05, 2.0e6
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'     # a key per frame, straight between
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    p = PITCH0 + (PITCH1 - PITCH0) * ease((t - T0) / (T1 - T0))
    cam.rotation_euler = (math.radians(90.0 + p), 0.0, 0.0)
    cam.keyframe_insert('rotation_euler', index=0, frame=f)

VFOV = 2 * math.degrees(math.atan(18.0 * shot.RES[1] / shot.RES[0] / LENS))
u, _, r_eq, r_pol, _ = P.jupiter_local()
j_el = P.alt_az(u)[0]
p_enter = j_el - r_pol - VFOV / 2
x = next(f for f in range(1, sc.frame_end + 1)
         if PITCH0 + (PITCH1 - PITCH0) * ease(((f - 1) / FPS - T0) / (T1 - T0)) >= p_enter)
print(f'NOTE 01: vfov {VFOV:.1f}°, tilt {PITCH0}° → {PITCH1}° over {T0}–{T1} s; Jupiter {j_el - r_pol:.1f}°…'
      f'{j_el + r_pol:.1f}°, its limb enters at pitch {p_enter:.1f}° = {(x - 1) / FPS:.2f} s; '
      f'{len(PR)} prints, Sun elongation {ELONG}°')

shot.run(sc, A)
