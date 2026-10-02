"""05 · forever.  Rise from the astronaut to 100 km over the curve of Io; the Sun's diamond on Jupiter's west limb.

Beat sheet (10 s, user 2026-10-03; physics.SHOT['05'], `python3 tools/physics.py` rows "Shot 05"):
The cut from 04 skips 137 min of the eclipse (the Sun now behind the west limb, the ring's bright arc on the right).
0–1 s low (0.8 m) behind the astronaut, 5 m off (user 2026-10-03: cut at the knees, the helmet against the stars),
at the end of the boot-print trail: the black disc ringed red, the
stars, the suit's two helmet lamps the only light on the plain (Breathing Idle) → 1–9 s the camera climbs, smoothstep
in log altitude, 0.8 m → 100 km (5 m at 3 s, 283 m at 5 s, 16 km at 7 s), pulling back due north, the lens 29 → 17 mm,
the disc's top held 1° under the frame top: the astronaut, the lander, the plain fall away; hot spots glow on the
dark ground → 5.0 s third contact: a bead of Sun on Jupiter's west limb (the diamond), glare; time eases from real time
to 21× so the whole Sun is out at 8.0 s; the light comes up across the curve west → east (the shadow's 750 km
penumbra sweeping at 17 km/s × rate: globe.egress), the plume umbrella under the diamond lights up, backlit; exposure
adapts EV_NIGHT → EV_DAY; the horizon bulges (dip 18.6°) → 9–10 s hold (fade to black at compile; caption 5.0–9.4).

Light (globe.py): the near ground (6 km), the astronaut and the lander have a Sun keyed by the site's uncovered
fraction (as 04); the far ground and the plume a full Sun with the fraction computed per shading point (parallax);
Jupiter its own Sun (jupiter.own_sun). Jupiter, its ring and the Sun disc follow the camera (true angle; the camera's
100 km is nothing at 421,000 km); the ground, hot spots and plume are at true size and distance.

    node render.mjs 05-forever --animatic --engine eevee      (→ out/05-forever-animatic.mp4)
    node preview.mjs 05-forever 0.5 5.5 9.5 --pct 50           (→ frames/05-forever-strip.png)
Options: --day EV  --night EV  --arc A  --haze H  --tail F  --glow LAVA  --stars GAIN  --density D  --glare S
         --plume DENSITY  --lamps W  --proxy 1
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
from mathutils import Matrix, Quaternion, Vector
import physics
from lib import nodes, rig, shot, io_world, jupiter, sky, prints, lander, landing, astronaut, retarget, globe
for m in (physics, nodes, rig, shot, io_world, jupiter, sky, prints, lander, landing, astronaut, retarget, globe):
    importlib.reload(m)
W, P, L, G = io_world, physics, landing, globe

A = shot.args()
FPS = 24
C = P.SHOT['05']
SHUTTER = 0.5
EV_DAY = float(A.opt('day', -4.5))
EV_NIGHT = float(A.opt('night', 0.0))
ADAPT = (C['contact'] + 0.3, C['full'] + 0.5)          # the eyes adjust back to daylight (s)
u, D_J, r_eq, r_pol, pole = P.jupiter_local()
J_EL = P.alt_az(u)[0]
TOP = J_EL + r_pol + 0.7                               # frame top: the disc's top + 0.7° (as 04: ring match)
ASPECT = shot.RES[1] / shot.RES[0]
assert abs(A.frames / FPS - C['dur']) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, physics.SHOT 05 says {C["dur"]} s'

sc = rig.new_scene('S05_Forever')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = SHUTTER

# ---------------------------------------------------------------- the site: the end of 01's out-trail (lib/landing.py)
O = (L.OUT[-1][0] - 0.4, L.OUT[-1][1] + 1.5)           # the astronaut's feet, in the landing-site frame
height = L.shifted(L.height, O)
AZ0, D0, EYE0 = 14.0, 5.0, C['alt'][0]                 # astronaut at az +14°, 5 m from the camera at the start
CAM_X = -D0 * math.sin(math.radians(AZ0))              # the pull-back runs due north from there

mat = W.surface('IoSurface', frost=1.0, clod=0.06, prints=True)
p = C['plume']
VENT = (1000 * p['d'] * math.sin(math.radians(p['az'])), 1000 * p['d'] * math.cos(math.radians(p['az'])))
_, RING, _ = P.umbrella(p['h'], p['cone'])
G.far_layer(mat, vent=VENT, ring=RING * 1000)
far_mat = mat.copy()
far_mat.name = 'IoFar'
e_c = P.egress05()[0]
N_SKY = P.sun_offset_dir(e_c)
eg_ground = G.egress(far_mat, N_SKY, D_J * 1000)

rr = W.rings(0.5, 6000.0, 0.01)
near = W.terrain(sc, 'Ground', rr, 0.0, 180.0, 720, height, mat)
L.mark_prints(near, O)
# far: Io's own relief (the landing site's swells) + the 01/03 massif (same place and size, softer scarps:
# landing.mountains' cliffs read as a black slab from above, backlit) + blocks on the far horizon
BLOCKS = [L.MASSIFS[0], (-34.0, 260.0, 6.0, 70.0, 30.0, 70.0, 0.5), (47.0, 520.0, 9.0, 110.0, 45.0, 150.0, -0.7),
          (-12.0, 700.0, 5.0, 90.0, 35.0, 20.0, 0.3)]


def far_height(x, y):
    return L.base(x + O[0], y + O[1]) + G.massifs(x, y, BLOCKS) - 1.0


glob = G.cap(sc, 'Globe', 4000.0, 1.5e6, far_height, far_mat)
z0 = W.ground_z(height, 0.0, 0.0)

rng = np.random.default_rng(5)
spots = [(VENT[0], VENT[1], 6000.0)]
for _ in range(14):                                     # hot paterae, 15–650 km out across the view
    a, r = math.radians(rng.uniform(-70, 70)), 1000 * rng.uniform(15, 650)
    spots.append((r * math.sin(a), r * math.cos(a), 1000 * rng.uniform(0.6, 4.0) * (r / 2e5) ** 0.5))
G.hotspots(sc, 'HotSpots', spots, glow=float(A.opt('glow', 3.0)))
# hot cracks near the site (as 04's plain): the only things that show the climb before the Sun returns (user
# 2026-10-03: something to measure the rise by). All round the site (the pull-back runs north over it), 15 m–5 km,
# in bands whose crack size grows with distance, so each band reads at the altitude that passes it.
for k, (r0, r1, n, size) in enumerate([(15, 60, 10, 0.5), (60, 250, 18, 1.5), (250, 1200, 26, 5.0), (1200, 5000, 30, 18.0)]):
    vents = []
    for _ in range(n):
        a, r = rng.uniform(-math.pi, math.pi), math.exp(rng.uniform(math.log(r0), math.log(r1)))
        x, y = r * math.sin(a), r * math.cos(a)
        vents.append((x, y, W.ground_z(height, x, y)))
    W.vent_glow(sc, f'Vents{k}', vents, size=size, glow=6.0)
pl, eg_plume = G.plume(sc, 'Plume', VENT[0], VENT[1], 1000 * p['h'], 1000 * RING, N_SKY, D_J * 1000,
                       density=float(A.opt('plume', 2e-6)))

# ---------------------------------------------------------------- the lander, the astronaut (helmet lamps on)
before = set(sc.objects)
L.build_lander(sc, height, O)
# the lander's floodlight, on through the eclipse, aimed at the astronaut 75 m out: from behind, the helmet lamps'
# pool is hidden by the body and nothing else lights the suit (it was a starless hole); the lit oval with the trail
# in it is also the first thing to shrink as the camera climbs
lc = Vector((L.LANDER[0] - O[0], L.LANDER[1] - O[1], 0.0))
lc.z = W.ground_z(height, lc.x, lc.y) + 4.5
aim = Vector((0.0, 0.0, W.ground_z(height, 0.0, 0.0) + 1.0))
fd = bpy.data.lights.new('Flood', 'SPOT')
fd.energy, fd.spot_size, fd.spot_blend = float(A.opt('flood', 20000.0)), math.radians(16), 0.7
fd.shadow_soft_size, fd.color = 0.15, (1.0, 0.96, 0.9)
if A.opt('draft') and A.engine == 'eevee':
    fd.use_shadow = False
flood = bpy.data.objects.new('Flood', fd)
sc.collection.objects.link(flood)
flood.location = lc + (aim - lc).normalized() * 1.5               # just clear of the cabin, toward the astronaut
flood.rotation_euler = (aim - lc).to_track_quat('-Z', 'Y').to_euler()
near_objs = [near] + [o for o in sc.objects if o not in before]
if A.opt('proxy', '0') == '1':
    arm = W.astronaut_proxy(sc, (0.0, 0.0, z0), heading=180.0)
    near_objs.append(arm)
else:
    before = set(sc.objects)
    arm = astronaut.load(sc, (0.0, 0.0, z0), heading=180.0)          # facing south, toward Jupiter
    near_objs += [o for o in sc.objects if o not in before]
    if arm.type == 'ARMATURE':
        retarget.retarget(sc, arm, 'Breathing Idle.fbx')
        bpy.context.view_layer.update()
        LAMP_W = float(A.opt('lamps', 150.0))
        for sx in (-1, 1):                                               # EVVA helmet lights ('Lamparas'), ±0.19 m
            ld = bpy.data.lights.new(f'HelmetLamp{sx:+d}', 'SPOT')
            ld.energy, ld.spot_size, ld.spot_blend = LAMP_W, math.radians(50), 0.6
            ld.shadow_soft_size, ld.color = 0.02, (1.0, 0.95, 0.88)
            if A.opt('draft') and A.engine == 'eevee':                  # EEVEE redraws a spot's shadow maps of the
                ld.use_shadow = False                                    # 1.1 M-vertex ground every frame: 3.5 s/frame
            lo = bpy.data.objects.new(ld.name, ld)
            sc.collection.objects.link(lo)
            lo.matrix_world = (arm.matrix_world @ Matrix.Translation((0.193 * sx, -0.07, 1.874))
                               @ Matrix.Rotation(math.radians(-70), 4, 'X'))      # forward (−Y), 20° down
            pb = arm.pose.bones['Casco']
            lo.parent, lo.parent_type, lo.parent_bone = arm, 'BONE', 'Casco'
            lo.matrix_parent_inverse = (arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))).inverted()

# ---------------------------------------------------------------- sky: two Suns + Jupiter's, the disc, stars, Jupiter
e0 = P.lapse05_elong(0.0)
sun_near = sky.sun(sc, e0)                    # keyed by the site's uncovered fraction
sun_far = sky.sun(sc, e0)                     # full; the far shaders take the fraction per point
for s_ in (sun_near, sun_far):
    s_.rotation_mode = 'QUATERNION'
sun_far.name = 'SunFar'
disc = sky.sun_disc(sc, e0, dist=0.9e6)
# the Sun for the camera as a bead in front of the limb (0.9e6 < Jupiter's 1e6): at true size (0.1°, ~1 px) a few-%
# sliver covers a few % of one pixel, and adaptive sampling stops on a black pixel before a sample hits it, so the
# diamond (the beat) went missing or would flicker. The bead is ≥ 1.5 px across, its strength = the uncovered
# fraction (physics.sun_visible) × the disc's radiance × (true / drawn radius)², so its flux stays exact.
D_EM = next(n for n in disc.active_material.node_tree.nodes if n.type == 'EMISSION').inputs['Strength']
D_S0 = D_EM.default_value
R_TRUE = math.radians(P.R_SUN_DEG)
# star lattice: its cube diagonal toward the view (south), the nearest axes at 54.7° (straight up, and lower left /
# right under the ground): no lattice rings in frame (sky.stars `orient`)
_q = Vector((1, 1, 1)).normalized().rotation_difference(Vector((0, 1, 0)))
_ups = [(_q @ a) for a in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))]
_up = max(_ups, key=lambda v: v.z)
_q = Quaternion((0, 1, 0), -math.atan2(_up.x, _up.z)) @ _q             # roll about south: that axis straight up
_ax, _an = _q.inverted().to_axis_angle()
world, turn, smear = sky.stars(sc, sky.px_angle(C['lens'][0], A.pct), gain=float(A.opt('stars', 8.0)),
                               density=float(A.opt('density', 0.8)), axis=pole, taps=1, camera_only=True,
                               orient=(tuple(_ax), _an))
G0 = math.degrees(math.atan2(EYE0, D0 * math.cos(math.radians(AZ0))))     # the site's depression: 3.8° → 18°
G1 = 18.0


def cam_at(t):
    """Camera at clip second t: (location, lens mm, pitch°, altitude m, pull-back m)."""
    h, x = P.rise05(t)
    gam = G0 + (G1 - G0) * x
    back = h / math.tan(math.radians(gam))
    gz = float(height(np.array([CAM_X]), np.array([-back]))[0]) if back < 5000 else 0.0
    loc = Vector([float(v) for v in G.to_world(CAM_X, -back, gz + h)])
    lens = P.lens05(x)
    vfov = 2 * math.degrees(math.atan(18.0 * ASPECT / lens))
    return loc, lens, TOP - vfov / 2, h, back


cam0 = cam_at(0.0)[0]
jup, shell = jupiter.build(sc, cam0, grs=-40.0, ring=1.0, sun_elong=e0)
sun_j = jupiter.own_sun(sc, sun_near, jup)
sky.glare(sc, strength=float(A.opt('glare', 1.0)))


def receivers(name, objs):
    c = bpy.data.collections.new(name)
    for o in objs:
        c.objects.link(o)
    for i in range(len(c.collection_objects)):
        c.collection_objects[i].light_linking.link_state = 'INCLUDE'
    return c


# the ground is real size, Jupiter scaled to 1000 km: seen from there the sunlit far ground would fill its sky (a false
# Io-shine on the eclipsed disc). The ground and the plume bounce no light (their own look is direct light anyway).
for o in (near, glob, pl):
    o.visible_diffuse = o.visible_glossy = False
sun_near.light_linking.receiver_collection = receivers('NearSun', [o for o in near_objs if o.type in ('MESH', 'CURVE')])
sun_far.light_linking.receiver_collection = receivers('FarSun', [glob, pl])
expo = None
if A.engine == 'eevee':                       # as 04: EEVEE drops the sub-pixel Sun disc at negative view exposure
    g = sc.compositing_node_group
    expo = g.nodes.new('CompositorNodeExposure')
    out = next(n for n in g.nodes if n.type == 'GROUP_OUTPUT')
    src = out.inputs[0].links[0].from_socket
    g.links.new(src, expo.inputs['Image'])
    g.links.new(expo.outputs['Image'], out.inputs[0])
    sc.eevee.volumetric_start, sc.eevee.volumetric_end = 2.0e5, 1.2e6        # froxels only where the plume is
    sc.eevee.volumetric_tile_size = A.opt('vtile', '2')               # (8 / 32 measured: no faster, 2026-10-03)
    sc.eevee.volumetric_samples = int(A.opt('vsamples', 128))
FAR = [(o, o.location.copy()) for o in (jup, shell)]
jup.rotation_mode = 'QUATERNION'
J_ROT = jup.rotation_quaternion.copy()
ring = shell.active_material.node_tree.nodes
ARC, HAZE, FOCUS, TAIL = (float(A.opt(k, d)) for k, d in (('arc', 400.0), ('haze', 4.0), ('focus', 12.0), ('tail', 0.06)))
ring['RingFocus'].outputs[0].default_value = FOCUS

# ---------------------------------------------------------------- camera
cam = rig.camera(sc, cam0, cam0 + Vector((0, 1000, 0)), lens=C['lens'][0], fstop=8.0, focus=cam0 + Vector((0, 1000, 0)))
cam.data.clip_start, cam.data.clip_end = 0.3, 4.0e6
cam.data.dof.use_dof = False
cam.rotation_mode = 'QUATERNION'


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
q_prev = None
log = []
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    # camera: altitude, pull-back, lens, pitch (the disc's top 1° under the frame top)
    cl, lens, pitch, h, back = cam_at(t)
    cam.location = cl
    cam.rotation_quaternion = Quaternion((1, 0, 0), math.radians(90 + pitch))
    cam.data.lens = lens
    cam.keyframe_insert('location', frame=f)
    cam.keyframe_insert('rotation_quaternion', frame=f)
    cam.data.keyframe_insert('lens', frame=f)
    for o, base in FAR:
        o.location = base + (cl - cam0)
        o.keyframe_insert('location', frame=f)
    # the clock: Sun, light, ring, stars, Jupiter's spin
    tau = P.lapse05(t)
    e = P.lapse05_elong(t)
    sep, vis = P.sun_limb_sep(e), P.sun_visible(e)
    uu = Vector(P.sun_local(e))
    q = (-uu).to_track_quat('-Z', 'Y')
    if q_prev is not None and q.dot(q_prev) < 0:
        q.negate()
    q_prev = q
    for s_ in (sun_near, sun_far, sun_j):
        s_.rotation_quaternion = q
        s_.keyframe_insert('rotation_quaternion', frame=f)
    sun_near.data.energy = P.E_SUN * vis
    sun_near.data.keyframe_insert('energy', frame=f)
    disc.location = cl + uu * disc['dist']
    disc.keyframe_insert('location', frame=f)
    k = max(1.0, 1.5 * sky.px_angle(lens, A.pct) / R_TRUE)              # drawn radius / true radius
    disc.scale = (k, k, k)
    disc.keyframe_insert('scale', frame=f)
    D_EM.default_value = D_S0 * vis / (k * k)
    D_EM.keyframe_insert('default_value', frame=f)
    for S in (eg_ground, eg_plume):
        S.outputs[0].default_value = sep / P.R_SUN_DEG
        S.outputs[0].keyframe_insert('default_value', frame=f)
    turn.outputs[0].default_value = math.radians(P.STAR_RATE * tau / 3600)
    turn.outputs[0].keyframe_insert('default_value', frame=f)
    smear.outputs[0].default_value = math.radians(P.STAR_RATE * P.rate05(t) / 3600 * SHUTTER / FPS)
    smear.outputs[0].keyframe_insert('default_value', frame=f)
    jup.rotation_quaternion = J_ROT @ Quaternion((0.0, 0.0, 1.0), math.radians(360.0 * tau / 3600 / P.P_ROT_J_IO))
    jup.keyframe_insert('rotation_quaternion', frame=f)
    ring['RingHaze'].outputs[0].default_value = HAZE * smoothstep(4.0, 0.0, sep)
    ring['RingArc'].outputs[0].default_value = ARC * smoothstep(3.0, 0.0, sep) * (TAIL + (1 - TAIL) * vis)
    for i, v in enumerate(jupiter.ring_dir(shell, e)):
        ring['RingDir'].inputs[i].default_value = v
        ring['RingDir'].inputs[i].keyframe_insert('default_value', frame=f)
    for k in ('RingHaze', 'RingArc'):
        ring[k].outputs[0].keyframe_insert('default_value', frame=f)
    ev = EV_NIGHT + (EV_DAY - EV_NIGHT) * smoothstep(*ADAPT, t)
    if expo is None:
        sc.view_settings.exposure = ev
        sc.view_settings.keyframe_insert('exposure', frame=f)
    else:
        expo.inputs['Exposure'].default_value = ev
        expo.inputs['Exposure'].keyframe_insert('default_value', frame=f)
    if f % 24 == 1 or f == sc.frame_end:
        log.append(f'{t:4.1f}s alt {h:9.1f}m back {back / 1000:7.2f}km {lens:4.1f}mm pitch {pitch:5.2f} '
                   f'{tau:+6.1f}s e{e:6.3f} sun{100 * vis:3.0f}%')

print('NOTE 05: ' + ' | '.join(log))
for nm in filter(None, str(A.opt('hide', '')).split('+')):  # diagnosis: --hide SunFar+Plume
    sc.objects[nm].hide_render = True

shot.run(sc, A)
