"""Jupiter at its true angular size and place in Io's sky, lit by the Sun lamp (its phase is never set by hand).

Scaled toward the camera: the real Jupiter is 421,232 km away; here it sits DIST metres out along the true direction
with the radius that gives the true angular radius (physics.jupiter_local), so its angle, phase, the Jupiter-shine it
throws on the ground (Cycles traces it: Jupiter is a lit diffuse sphere 19.5° across) and its eclipse shadow are all
exact. DIST (1000 km) is far beyond any terrain the shots build (≤ 60 km), so its shadow covers the whole patch.

Map: Björn Jónsson's Cassini + Juno-poles map, 14400×7200 (NASA/JPL-Caltech/SSI/SwRI/MSSS/Björn Jónsson, via The
Planetary Society); falls back to Cassini PIA07782 (3601×1801, public domain) if missing. Both in the shared library
(REFERENCES.md); their mean luminance and Great Red Spot position come from `python3 tools/maps.py jupiter`.
Albedo: map × gain so the disc's mean Lambert albedo is 1.5 × geometric albedo 0.538 (Lambert sphere: p = 2/3 A).
Orientation: object +X toward the observer, +Z = Jupiter's north (= Io's north: upright in the frame at our site).
`grs` = the Great Red Spot's longitude from the central meridian, deg, + = right (west in our sky).

Eclipse ring: a camera-only shell 0.6 % above the cloud tops whose emission peaks where the line of sight grazes it
(sunlight refracted and scattered through Jupiter's upper atmosphere), red-orange, brightest toward the Sun's position
behind the disc: emission = core/halo profile × (RingArc · toward^RingFocus + RingHaze). Those Value nodes and the
Combine XYZ 'RingDir' (the Sun's direction, object space; `ring_dir`) are keyable by a shot (04 keys them on the
Sun's distance from the limb).
"""
import math
import os

import bpy
from mathutils import Matrix, Vector
import physics as P
from . import nodes

DIST = 1.0e6                     # m
_LIB = os.path.expanduser('~/dev/workspace/claude/videos/_assets/textures/jupiter/')
MAPS = [  # (file, mean linear luminance, GRS u from the left), measured by tools/maps.py jupiter
    ('jupiter_map_css_plus_juno_bj.png', 0.4078, 0.8500),
    ('PIA07782.png', 0.3293, 0.3685),
]


def _map():
    for f, lum, grs_u in MAPS:
        if os.path.exists(_LIB + f) and lum is not None:
            return _LIB + f, lum, grs_u
    raise FileNotFoundError(_LIB)


def build(sc, cam_loc, grs=-40.0, ring=0.0, sun_elong=None, ring_width=0.006):
    u, d, r_eq, r_pol, axis = P.jupiter_local()
    u, axis = Vector(u), Vector(axis)
    R = DIST * math.sin(math.radians(r_eq))
    flat = P.R_J_POL / P.R_J
    centre = Vector(cam_loc) + u * DIST
    x = -u
    z = (axis - axis.dot(x) * x).normalized()
    y = z.cross(x)
    rot = Matrix((x, y, z)).transposed().to_4x4()

    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1.0)
    ob = bpy.context.object
    ob.name = 'Jupiter'
    ob.matrix_world = Matrix.Translation(centre) @ rot @ Matrix.Diagonal((R, R, R * flat, 1.0))
    bpy.ops.object.shade_smooth()

    m = bpy.data.materials.new('Jupiter')
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    ox, oy, oz = g.xyz(g.o(tc, 'Object'))
    lon = g.add('ShaderNodeMath', operation='ARCTAN2')
    g.set(lon, 0, oy)
    g.set(lon, 1, ox)
    path, lum, grs_u = _map()
    uu = g.math('ADD', g.math('DIVIDE', g.o(lon, 0), 2 * math.pi), grs_u - grs / 360.0)
    vv = g.math('ADD', g.math('DIVIDE', g.math('ARCSINE', g.math('MINIMUM', g.math('MAXIMUM', oz, -1.0), 1.0)),
                                  math.pi), 0.5)
    img = bpy.data.images.load(path, check_existing=True)
    tex = g.add('ShaderNodeTexImage', interpolation='Cubic', extension='REPEAT')
    tex.image = img
    g.set(tex, 'Vector', g.combine(uu, vv))
    gain = 1.5 * P.P_GEOM_J / lum
    col = g.mix(1.0, g.o(tex, 'Color'), (gain, gain, gain), blend='MULTIPLY', clamp=False)
    b = g.add('ShaderNodeBsdfDiffuse')
    g.set(b, 'Color', col)
    g.output(g.o(b, 0))
    ob.data.materials.append(m)
    print(f'NOTE jupiter: radius {R / 1000:.0f} km at {DIST / 1000:.0f} km (true {r_eq:.2f}°), albedo gain {gain:.2f}, map {os.path.basename(path)}')

    shell = None
    if ring > 0:
        shell = _ring(sc, ob, centre, rot, R, flat, ring, ring_width, sun_elong)
    return ob, shell


def _ring(sc, jup, centre, rot, R, flat, strength, width, sun_elong):
    s = 1.0 + width
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1.0)
    ob = bpy.context.object
    ob.name = 'JupiterRing'
    ob.matrix_world = Matrix.Translation(centre) @ rot @ Matrix.Diagonal((R * s, R * s, R * s * flat, 1.0))
    bpy.ops.object.shade_smooth()
    for k in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        setattr(ob, k, False)
    # direction (object space, in the disc plane) toward where the Sun sits behind the disc
    sdir = Vector((0.0, -1.0, 0.0))
    if sun_elong is not None:
        su = Vector(P.sun_local(sun_elong))
        so = (rot.to_3x3().transposed() @ su)
        sdir = Vector((0.0, so.y, so.z)).normalized() if so.yz.length > 1e-6 else sdir
    m = bpy.data.materials.new('JupiterRing')
    m.surface_render_method = 'BLENDED'          # EEVEE: dithered drops a fully transparent pixel with its emission
    g = nodes.Graph(m)
    geo = g.add('ShaderNodeNewGeometry')
    dot = g.add('ShaderNodeVectorMath', operation='DOT_PRODUCT')
    g.set(dot, 0, g.o(geo, 'Normal'))
    g.set(dot, 1, g.o(geo, 'Incoming'))
    c = g.math('ABSOLUTE', g.o(dot, 'Value'))
    c0 = math.sqrt(2 * width)                      # |cos| at the line of sight that grazes the cloud tops
    core = g.math('POWER', g.maprange(c, c0 * 1.05, 0.0), 3.0)          # bright thin ring
    halo = g.math('MULTIPLY', g.maprange(c, c0 * 2.2, 0.0), 0.18)        # faint scattered halo
    tc = g.add('ShaderNodeTexCoord')
    on = g.add('ShaderNodeVectorMath', operation='NORMALIZE')
    g.set(on, 0, g.o(tc, 'Object'))
    rdir = g.add('ShaderNodeCombineXYZ')                 # keyable: the Sun's direction behind the disc (object space)
    rdir.name = 'RingDir'
    for i, v in enumerate(sdir):
        rdir.inputs[i].default_value = v
    sd = g.add('ShaderNodeVectorMath', operation='DOT_PRODUCT')
    g.set(sd, 0, g.o(on, 0))
    g.link(rdir, 0, sd, 1)
    ctl = {}
    for k, v in (('RingArc', 8.0 * strength), ('RingHaze', 0.6 * strength), ('RingFocus', 6.0)):
        n = g.add('ShaderNodeValue')
        n.name = k
        n.outputs[0].default_value = v
        ctl[k] = n
    toward = g.math('POWER', g.maprange(g.o(sd, 'Value'), -0.3, 1.0), g.o(ctl['RingFocus'], 0))
    amp = g.math('ADD', g.math('MULTIPLY', toward, g.o(ctl['RingArc'], 0)), g.o(ctl['RingHaze'], 0))
    k = g.math('MULTIPLY', g.math('ADD', core, halo), amp)
    col = g.mix(g.math('POWER', core, 0.5), (1.0, 0.30, 0.10), (1.0, 0.55, 0.28))   # orange core, redder halo
    em = g.add('ShaderNodeEmission')
    g.set(em, 'Color', col)
    g.set(em, 'Strength', k)
    tr = g.add('ShaderNodeBsdfTransparent')
    add = g.add('ShaderNodeAddShader')
    g.link(tr, 0, add, 0)
    g.link(em, 0, add, 1)
    g.output(g.o(add, 0))
    ob.data.materials.append(m)
    return ob


def ring_dir(shell, sun_elong):
    """Object-space direction (in the disc plane) toward where the Sun sits behind the disc, for 'RingDir'."""
    rot = shell.matrix_world.to_3x3().normalized()
    so = rot.transposed() @ Vector(P.sun_local(sun_elong))
    return Vector((0.0, so.y, so.z)).normalized() if so.yz.length > 1e-6 else Vector((0.0, -1.0, 0.0))


def own_sun(sc, sun, jup):
    """Jupiter lit by its own copy of `sun` (light linking); `sun` lights everything else and Jupiter casts no
    shadow. For a shot that keys the Sun's strength on the ground (04: the eclipse, by the uncovered fraction of its
    disc) while Jupiter's sunlit side stays sunlit. Returns Jupiter's sun."""
    def coll(name, state):
        c = bpy.data.collections.new(name)
        c.objects.link(jup)
        c.collection_objects[0].light_linking.link_state = state
        return c
    jup.visible_shadow = False
    sun.light_linking.receiver_collection = coll('NotJupiter', 'EXCLUDE')
    sj = bpy.data.objects.new('SunJupiter', sun.data.copy())
    sc.collection.objects.link(sj)
    sj.rotation_mode = sun.rotation_mode
    sj.rotation_euler, sj.rotation_quaternion = sun.rotation_euler, sun.rotation_quaternion
    sj.light_linking.receiver_collection = coll('OnlyJupiter', 'INCLUDE')
    return sj


def io_shadow(sc, sun, jup, ground, sink=30.0):
    """Jupiter gets its own Sun, shadowed by Io alone (light linking), so Io's shadow transit is exact and the
    real-size terrain near the camera never shadows the scaled-down Jupiter (it did, as a huge saucer, at full phase).

    Io at Jupiter's scale: everything far is scaled toward the camera by k = DIST / true distance, so Io is a sphere
    of R_IO·k (4.3 km) whose top is the ground under the camera (sunk `sink` m so it never shadows the real ground),
    and its shadow on Jupiter falls where the Sun–Io line meets it, at the true angular size (≈ 0.4° umbra; the
    lamp's 0.1° Sun gives the scaled penumbra). It shows near full Jupiter (elongation 180 ± 10°) for ≈ 2.3 h.
    The main `sun` then lights everything but Jupiter. Returns (jupiter's sun, the Io sphere)."""
    k = DIST / (P.jupiter_local()[1] * 1000.0)
    r = P.R_IO * 1000.0 * k
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=r,
                                         location=Vector(ground) - Vector((0.0, 0.0, r + sink)))
    io = bpy.context.object
    io.name = 'IoScaled'
    for kk in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'):
        setattr(io, kk, False)

    def coll(name, ob, state):
        c = bpy.data.collections.new(name)
        c.objects.link(ob)
        c.collection_objects[0].light_linking.link_state = state
        return c

    sun.light_linking.receiver_collection = coll('NotJupiter', jup, 'EXCLUDE')
    sj = bpy.data.objects.new('SunJupiter', sun.data)
    sc.collection.objects.link(sj)
    sj.rotation_mode = sun.rotation_mode
    sj.rotation_euler, sj.rotation_quaternion = sun.rotation_euler, sun.rotation_quaternion
    sj.light_linking.receiver_collection = coll('OnlyJupiter', jup, 'INCLUDE')
    sj.light_linking.blocker_collection = coll('IoShadow', io, 'INCLUDE')
    print(f'NOTE jupiter: Io at scale k {k:.5f}, radius {r / 1000:.2f} km; own Sun for Jupiter (light linking)')
    return sj, io
