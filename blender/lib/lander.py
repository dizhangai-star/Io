"""The lander: a code-built, generic crewed lander (ours, not a real spacecraft design).

Conventions: 1 BU = 1 m; `build(sc, centre, heading, z)` puts an empty "LanderRoot" at (centre, z) = the ground plane
under the pads; leg k (0..3) points at 45 + 90 k + heading degrees (math angle from +X toward +Y). Sizes at the
scale of a two-crew lander: footpads 0.92 m across on a 4.0 m radius (8 m pad to pad), octagonal descent stage 3.2 m
across, 1.2–2.5 m up, wrapped in gold multilayer foil; a white ascent cabin on top (to 3.9 m); engine bell under.
Each leg: a telescoping primary strut (pad → outrigger at the deck edge), two secondary struts (lower primary → body
bottom corners), a dish footpad on a ball joint. Leg 1 carries the ladder. The pad nearest the camera is what shot 01
shows, so the detail is there; the rest only has to hold a silhouette (02, 1 km).
"""
import math

import bpy
from mathutils import Matrix, Vector
from . import nodes

R_PAD, R_BODY, Z_BOT, Z_DECK, Z_TOP = 4.0, 1.6, 1.2, 2.5, 3.9


def _principled(name, color, rough, metal=0.0, bump=None):
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=rough, Metallic=metal)
    g.set(b, 'Base Color', color)
    if bump:                                                     # (scale, strength): crinkled foil / brushed metal
        tc = g.add('ShaderNodeTexCoord')
        n = g.add('ShaderNodeTexNoise', Scale=bump[0], Detail=8, Roughness=0.7, Distortion=1.2)
        g.set(n, 'Vector', g.o(tc, 'Object'))
        bp = g.add('ShaderNodeBump', Strength=bump[1], Distance=0.01)
        g.set(bp, 'Height', g.o(n, 'Fac'))
        g.set(b, 'Normal', g.o(bp, 'Normal'))
        g.set(b, 'Roughness', g.maprange(g.o(n, 'Fac'), 0.3, 0.7, rough * 0.6, rough * 1.4))
    g.output(g.o(b, 'BSDF'))
    return m


def _dusty(name, color, rough, metal, dust, h):
    """Metal that is dust-coated up to h metres (object space, soft edge): the pads stand in the regolith."""
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    _, _, z = g.xyz(g.o(tc, 'Object'))
    n = g.add('ShaderNodeTexNoise', Scale=9.0, Detail=5, Roughness=0.6)
    g.set(n, 'Vector', g.o(tc, 'Object'))
    f = g.maprange(g.math('ADD', z, g.math('MULTIPLY', g.o(n, 'Fac'), 0.12)), h + 0.06, h - 0.04)
    b = g.add('ShaderNodeBsdfPrincipled')
    g.set(b, 'Base Color', g.mix(f, color, dust))
    g.set(b, 'Metallic', g.maprange(f, 0, 1, metal, 0.0))
    g.set(b, 'Roughness', g.maprange(f, 0, 1, rough, 0.95))
    g.output(g.o(b, 'BSDF'))
    return m


def _mats(dust):
    return dict(
        foil=_principled('LanderFoil', (0.95, 0.66, 0.30), 0.22, 1.0, bump=(14.0, 0.5)),
        foil_dark=_principled('LanderFoilDark', (0.55, 0.52, 0.48), 0.30, 1.0, bump=(10.0, 0.4)),
        alu=_principled('LanderAlu', (0.80, 0.80, 0.82), 0.32, 1.0),
        white=_principled('LanderWhite', (0.78, 0.78, 0.75), 0.55),
        black=_principled('LanderBlack', (0.025, 0.025, 0.025), 0.6),
        pad=_dusty('LanderPad', (0.80, 0.80, 0.82), 0.3, 1.0, dust, 0.10),
    )


def _link(sc, ob, root, mat):
    """Move a new part under the root, its transform baked into the mesh: object space = the lander's frame (z = 0
    on the ground plane), which the dust and foil textures use."""
    for c in ob.users_collection:
        c.objects.unlink(ob)
    sc.collection.objects.link(ob)
    ob.data.transform(ob.matrix_basis)
    ob.matrix_basis = Matrix.Identity(4)
    ob.parent = root
    ob.data.materials.append(mat)
    return ob


def _strut(sc, root, a, b, r, mat, verts=16):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=(b - a).length, location=(a + b) / 2)
    ob = bpy.context.object
    ob.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    bpy.ops.object.shade_smooth()
    return _link(sc, ob, root, mat)


def _prism(sc, root, n, r, z0, z1, mat, r1=None, rot=0.0, name='Part'):
    bpy.ops.mesh.primitive_cone_add(vertices=n, radius1=r, radius2=r if r1 is None else r1, depth=z1 - z0,
                                    location=(0, 0, (z0 + z1) / 2), rotation=(0, 0, rot))
    ob = bpy.context.object
    ob.name = name
    return _link(sc, ob, root, mat)


def _uv(sc, root, loc, r, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=r, location=loc)
    ob = bpy.context.object
    ob.scale = scale
    bpy.ops.object.shade_smooth()
    return _link(sc, ob, root, mat)


def build(sc, centre, heading=0.0, z=0.0, dust=(0.30, 0.22, 0.12), ladder_leg=1):
    """Lander at ground point (centre, z), legs turned by `heading` degrees. Returns the root empty."""
    M = _mats(dust)
    root = bpy.data.objects.new('LanderRoot', None)
    sc.collection.objects.link(root)
    root.location = (centre[0], centre[1], z)
    root.rotation_euler = (0, 0, math.radians(heading))
    oct_rot = math.radians(22.5)                                  # flat faces toward the legs
    _prism(sc, root, 8, R_BODY / math.cos(math.radians(22.5)), Z_BOT, Z_DECK, M['foil'], rot=oct_rot, name='Stage')
    _prism(sc, root, 8, 1.15, Z_BOT - 0.08, Z_BOT, M['foil_dark'], rot=oct_rot, name='Heatshield')
    _prism(sc, root, 32, 0.55, 0.75, Z_BOT - 0.08, M['black'], r1=0.32, name='Bell')
    _prism(sc, root, 8, 1.05, Z_DECK, Z_DECK + 0.25, M['alu'], rot=oct_rot, name='Deck')
    _prism(sc, root, 24, 0.95, Z_DECK + 0.25, Z_TOP - 0.35, M['white'], name='Cabin')
    _prism(sc, root, 24, 0.95, Z_TOP - 0.35, Z_TOP, M['white'], r1=0.55, name='CabinTop')
    _prism(sc, root, 6, 0.05, Z_TOP, Z_TOP + 0.6, M['alu'], name='Antenna')
    for k in range(4):
        a = math.radians(45 + 90 * k)
        c, s = math.cos(a), math.sin(a)
        tx, ty = -s, c                                           # tangent
        P = lambda r, zz, t=0.0: (r * c + t * tx, r * s + t * ty, zz)
        pad, top = P(R_PAD, 0.30), P(R_BODY + 0.05, Z_DECK - 0.2)
        # footpad: shallow dish, rim, ball joint
        bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=0.40, radius2=0.46, depth=0.16, location=P(R_PAD, 0.08))
        ob = bpy.context.object
        bpy.ops.object.shade_smooth()
        _link(sc, ob, root, M['pad'])
        _strut(sc, root, P(R_PAD, 0.155), P(R_PAD, 0.175), 0.47, M['pad'], verts=40)
        _uv(sc, root, P(R_PAD, 0.30), 0.09, M['alu'])
        # primary strut: thick outer cylinder up top, thinner piston below
        mid = tuple(p + 0.42 * (q - p) for p, q in zip(pad, top))
        _strut(sc, root, pad, mid, 0.055, M['alu'])
        _strut(sc, root, mid, top, 0.085, M['foil'])
        _strut(sc, root, top, P(R_BODY - 0.1, Z_DECK - 0.2), 0.10, M['alu'])
        # secondary struts: from the lower primary to the body's bottom corners either side
        q = tuple(p + 0.28 * (t - p) for p, t in zip(pad, top))
        for sgn in (-1, 1):
            _strut(sc, root, q, P(R_BODY, Z_BOT + 0.05, sgn * 0.75), 0.035, M['alu'])
        if k == ladder_leg:                                       # ladder: two rails beside the primary, rungs every 0.3 m
            lo, hi = Vector(P(R_PAD - 0.35, 0.45)), Vector(P(R_BODY + 0.15, Z_DECK - 0.05))
            side = Vector((tx, ty, 0)) * 0.24
            for sg in (-1, 1):
                _strut(sc, root, lo + sg * side, hi + sg * side, 0.018, M['alu'], verts=8)
            n = int((hi - lo).length / 0.3)
            for j in range(1, n + 1):
                p = lo + (hi - lo) * (j / (n + 1))
                _strut(sc, root, p - side, p + side, 0.014, M['alu'], verts=8)
    return root


def pad_xy(centre, heading, k):
    """World (x, y) of footpad k's centre."""
    a = math.radians(45 + 90 * k + heading)
    return centre[0] + R_PAD * math.cos(a), centre[1] + R_PAD * math.sin(a)
