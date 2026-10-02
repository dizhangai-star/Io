"""04 · eclipse.  28 mm, locked, the whole disc in frame, from a 40 m rise above a plain with a lava lake.

Beat sheet (20 s, user 2026-10-03; TREATMENT §6, physics.SHOT['04'], `python3 tools/physics.py` row "Shot 04"):
0–4 s the Sun slides in: 2° off Jupiter's east (left) limb, glare, visibly slowing; hairline limb arc, plain backlit,
no stars (day exposure) → 4.0 it touches the limb, the arc lights → 4–9 s swallowed: a bead on the limb shrinking ever
slower, the ground dims through the penumbra → 9.0 gone: near black, a thread of dark red arc and a few lava points →
9–10.5 black, wait → 10.5–14.5 the eyes adjust (exposure EV_DAY → EV_NIGHT): stars flood the frame except a 19.6°
hole, the black disc shows by its missing stars, the ring steadies, lake and vents glow → 14.5 heartbeat (sound) →
hold to 20 s. Time is eased (physics.lapse04): 619× at 0 s (Sun and stars drift 1.5°/s) → 33× at contact → 1.4× at
second contact → real time from 10.9 s, so nothing in the frame moves after the eclipse.

Light: the Sun lamp on the ground is keyed by the uncovered fraction of its disc (physics.sun_visible: exact, the Sun is
0.1° wide and the whole site is in or out together); Jupiter has its own Sun (jupiter.own_sun) and casts no shadow, so
Cycles and EEVEE agree. Ring (jupiter._ring controls, keyed on the Sun's distance from the limb): a faint haze ring
that comes up from 4° out (the hairline limb at 0 s: the Lambert crescent alone, 1 % lit, doesn't read at day
exposure), and a bright Sun-side arc from 3° out that flares while the Sun slides in and keeps `tail` of it.

Lens: 35 mm (the treatment) leaves no ground: the disc spans 5.6°–23.9° up and the frame is 24.3° tall. 28 mm
(30.1° tall) from a 40 m rise puts the lake ~1 km out at the bottom of the frame.

    node render.mjs 04-eclipse --animatic --engine eevee      (→ out/04-eclipse-animatic.mp4)
    node preview.mjs 04-eclipse 0 4 6.5 9.5 16 --pct 50        (→ frames/04-eclipse-strip.png)
Options: --day EV  --night EV (exposure before / after the eyes adjust)  --arc A  --haze H  --focus K  --tail F
         --glow LAVA  --stars GAIN  --density D  --glare STRENGTH  --taps N  --lens MM  --pitch DEG
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
from mathutils import Quaternion, Vector
import physics
from lib import nodes, rig, shot, io_world, jupiter, sky
for m in (physics, nodes, rig, shot, io_world, jupiter, sky):
    importlib.reload(m)
W = io_world
P = physics

A = shot.args()
FPS = 24
C = P.SHOT['04']
LENS = float(A.opt('lens', 28.0))
EYE = 1.7
SHUTTER = 0.5
EV_DAY = float(A.opt('day', -4.5))
EV_NIGHT = float(A.opt('night', 0.0))
ADAPT = (10.5, 14.5)                   # the eyes adjust (s): exposure EV_DAY → EV_NIGHT
u, _, r_eq, r_pol, pole = P.jupiter_local()
J_EL = P.alt_az(u)[0]
VFOV = 2 * math.degrees(math.atan(18.0 * shot.RES[1] / shot.RES[0] / LENS))
PITCH = float(A.opt('pitch', J_EL + r_pol + 0.7 - VFOV / 2))      # disc top 0.7° under the frame top
assert abs(A.frames / FPS - C['dur']) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, physics.SHOT 04 says {C["dur"]} s'

sc = rig.new_scene('S04_Eclipse')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = SHUTTER

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

# ---------------------------------------------------------------- sky: Sun (lamp + disc), turning stars, Jupiter + ring
e0 = P.lapse04_elong(0.0)
sun = sky.sun(sc, e0)
sun.rotation_mode = 'QUATERNION'
disc = sky.sun_disc(sc, e0)
world, turn, smear = sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('stars', 8.0)),   # dense: the black disc
                               density=float(A.opt('density', 0.8)), axis=pole,       # reads as a starless hole
                               taps=int(A.opt('taps', 3)))
jup, shell = jupiter.build(sc, cam_loc, grs=-40.0, ring=1.0, sun_elong=e0)
sun_j = jupiter.own_sun(sc, sun, jup)
sky.glare(sc, strength=float(A.opt('glare', 1.0)))
expo = None
if A.engine == 'eevee' and not A.opt('freeze'):   # EEVEE drops the sub-pixel Sun disc at any negative view exposure (EV 0: there, −2: gone):
    g = sc.compositing_node_group                 # key the exposure in the compositor, after the glare, view at 0
    expo = g.nodes.new('CompositorNodeExposure')
    out = next(n for n in g.nodes if n.type == 'GROUP_OUTPUT')
    src = out.inputs[0].links[0].from_socket
    g.links.new(src, expo.inputs['Image'])
    g.links.new(expo.outputs['Image'], out.inputs[0])
J_LOC, J_ROT, J_SCL = jup.matrix_world.decompose()
jup.rotation_mode = 'QUATERNION'
ring = shell.active_material.node_tree.nodes
ARC, HAZE, FOCUS, TAIL = (float(A.opt(k, d)) for k, d in (('arc', 400.0), ('haze', 4.0), ('focus', 12.0), ('tail', 0.06)))
ring['RingFocus'].outputs[0].default_value = FOCUS

# ---------------------------------------------------------------- camera
d = Vector((0.0, math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))))
cam = rig.camera(sc, cam_loc, cam_loc + d * 1000, lens=LENS, fstop=5.6, focus=cam_loc + d * 1000)
cam.data.clip_start, cam.data.clip_end = 0.5, 2.0e6


# ---------------------------------------------------------------- the clock: one key per frame, straight between
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


q_prev = None
log = []
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    tau = P.lapse04(t)                                                  # real s since first contact
    rate = P.rate04(t)
    e = P.lapse04_elong(t)
    sep, vis = P.sun_limb_sep(e), P.sun_visible(e)
    uu = Vector(P.sun_local(e))
    q = (-uu).to_track_quat('-Z', 'Y')
    if q_prev is not None and q.dot(q_prev) < 0:
        q.negate()
    q_prev = q
    for s_ in (sun, sun_j):
        s_.rotation_quaternion = q
        s_.keyframe_insert('rotation_quaternion', frame=f)
    sun.data.energy = P.E_SUN * vis
    sun.data.keyframe_insert('energy', frame=f)
    disc.location = cam_loc + uu * disc['dist']
    disc.keyframe_insert('location', frame=f)
    turn.outputs[0].default_value = math.radians(P.STAR_RATE * tau / 3600)
    turn.outputs[0].keyframe_insert('default_value', frame=f)
    smear.outputs[0].default_value = math.radians(P.STAR_RATE * rate / 3600 * SHUTTER / FPS)
    smear.outputs[0].keyframe_insert('default_value', frame=f)
    spin = Quaternion((0.0, 0.0, 1.0), math.radians(360.0 * tau / 3600 / P.P_ROT_J_IO))
    jup.location, jup.rotation_quaternion, jup.scale = J_LOC, J_ROT @ spin, J_SCL
    jup.keyframe_insert('location', frame=f)
    jup.keyframe_insert('rotation_quaternion', frame=f)
    ring['RingHaze'].outputs[0].default_value = HAZE * smoothstep(4.0, 0.0, sep)
    ring['RingArc'].outputs[0].default_value = ARC * smoothstep(3.0, 0.0, sep) * (TAIL + (1 - TAIL) * vis)
    ring['RingDir'].inputs[0].default_value, ring['RingDir'].inputs[1].default_value, \
        ring['RingDir'].inputs[2].default_value = jupiter.ring_dir(shell, e)
    for k in ('RingHaze', 'RingArc'):
        ring[k].outputs[0].keyframe_insert('default_value', frame=f)
    for i in range(3):
        ring['RingDir'].inputs[i].keyframe_insert('default_value', frame=f)
    ev = EV_DAY + (EV_NIGHT - EV_DAY) * smoothstep(*ADAPT, t)
    if expo is None:
        sc.view_settings.exposure = ev
        sc.view_settings.keyframe_insert('exposure', frame=f)
    else:
        expo.inputs['Exposure'].default_value = ev
        expo.inputs['Exposure'].keyframe_insert('default_value', frame=f)
    if f % 24 == 1 or f == sc.frame_end:
        log.append(f'{t:4.1f}s {tau:+7.1f}s {rate:5.0f}x e{e:6.3f} sep{sep:+.3f} sun{100 * vis:3.0f}%')

print(f'NOTE 04: lens {LENS} mm, vfov {VFOV:.1f}°, pitch {PITCH:.2f}°; ' + ' | '.join(log))

shot.run(sc, A)
