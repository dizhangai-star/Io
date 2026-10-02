"""Io from above (05): the far ground as an exact sphere cap, its km-scale colour, hot spots, a ballistic plume
umbrella, and the eclipse egress seen point by point.

Conventions as io_world: 1 BU = 1 m, X = west, Y = south, Z = up, the site (the astronaut's feet) at the origin on a
sphere of radius R centred at (0, 0, −R). Ground positions are given as arc coordinates (x, y): arc distance
s = hypot(x, y) along the surface in the azimuth atan2(x, y). Everything here is at true size and distance (the
camera climbs 100 km: parallax is real), except Jupiter, its ring and the Sun disc, which the shot keeps at true angle.

Egress: the Sun leaves Jupiter's west limb at a slightly different moment at every point, because Jupiter (421,000 km
off) shifts by parallax; the Sun is at infinity. A point Δ from the site sees the Sun's centre deg(Δ·n/d) further
from the limb (physics.sun_offset_dir), so the shadow's 750 km penumbra sweeps the ground west → east. A Sun lamp can't
vary per point, so the far ground and the plume get a lamp of their own at full strength, and their shaders take the
uncovered fraction of the Sun's disc at each shading point (`egress`), keyed per frame through one Value node.
"""
import math
import os

import bpy
import numpy as np
from mathutils import Matrix, Vector
import physics as P
from . import nodes, io_world as W

R = W.R_IO_M


def to_world(x, y, h=0.0):
    """Arc coordinates (m) + height above the sphere → local XYZ (arrays or floats)."""
    s = np.hypot(x, y)
    a = np.arctan2(x, y)
    th = s / R
    rr = R + h
    return rr * np.sin(th) * np.sin(a), rr * np.sin(th) * np.cos(a), rr * np.cos(th) - R


def normal_at(x, y):
    X, Y, Z = to_world(x, y)
    return Vector((X, Y, Z + R)).normalized()


def cap(sc, name, r0, r1, height, mat=None, nseg=720, step=0.01):
    """Polar grid on the exact sphere from arc distance r0 to r1 (m), full circle, height(x, y) (arc coords, m) along
    the radius. (io_world.terrain's parabolic drop is 2.7 km low at 600 km: the horizon from 100 km must be exact.)"""
    rr = np.geomspace(r0, r1, int(math.log(r1 / r0) / step))
    a = np.linspace(0, 2 * math.pi, nseg + 1)[:-1]
    RR, AA = np.meshgrid(rr, a, indexing='ij')
    x, y = RR * np.sin(AA), RR * np.cos(AA)
    X, Y, Z = to_world(x, y, height(x, y))
    nr, na = RR.shape
    verts = np.stack([X, Y, Z], -1).reshape(-1, 3)
    i = np.arange(nr - 1)[:, None] * na
    j = np.arange(na)[None, :]
    jn = (j + 1) % na
    faces = np.stack([i + j, i + jn, i + na + jn, i + na + j], -1).reshape(-1, 4)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts))
    me.vertices.foreach_set('co', verts.ravel().astype(np.float32))
    me.loops.add(faces.size)
    me.loops.foreach_set('vertex_index', faces.ravel().astype(np.int32))
    me.polygons.add(len(faces))
    me.polygons.foreach_set('loop_start', np.arange(0, faces.size, 4, dtype=np.int32))
    me.update()
    me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    print(f'NOTE globe {name}: {len(verts):,} verts, {r0 / 1000:.1f}–{r1 / 1000:.0f} km')
    return ob


def massifs(x, y, blocks, seed=40):
    """Tilted crustal blocks (Io's mountains): (az°, km out, km high, km long, km wide, strike°, tilt) → height (m)."""
    z = np.zeros_like(x)
    for k, (az, d, hgt, ln, wd, strike, tilt) in enumerate(blocks):
        cx, cy = 1000 * d * math.sin(math.radians(az)), 1000 * d * math.cos(math.radians(az))
        sa, ca = math.sin(math.radians(strike)), math.cos(math.radians(strike))
        u, v = ((x - cx) * sa + (y - cy) * ca) / (500 * ln), ((x - cx) * ca - (y - cy) * sa) / (500 * wd)
        edge = 1 + 0.35 * (W.fbm(x / 6000, y / 6000, 4, seed + k) - 0.5)
        r = np.hypot(u, v) / edge
        body = 0.8 * W.smooth(1.0, 0.7, r) + 0.2 * W.smooth(1.45, 0.9, r)            # scarps over debris aprons
        top = 0.75 + 0.25 * tilt * u + 0.25 * (W.fbm(x / 4000, y / 4000, 5, seed + 10 + k) - 0.5)
        z = z + 1000 * hgt * body * top * (0.85 + 0.3 * W.fbm(x / 1500, y / 1500, 4, seed + 20 + k))
    return z


# ---------------------------------------------------------------- materials
class _Edit(nodes.Graph):
    """A Graph on an existing material (no clearing)."""
    def __init__(self, mat):
        self.nt = mat.node_tree
        self.out = next(n for n in self.nt.nodes if n.type == 'OUTPUT_MATERIAL')


FAR_MAP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures/src/io_far_1km.png')
FAR_KM = 2048.0                                   # its width (km), centred on the site, X west → right, south up
FAR_MEAN = (0.3546, 0.2349, 0.1111)               # its mean linear colour (python3 tools/maps.py far)


def far_layer(mat, vent=None, ring=None, quiet=15000.0, weight=0.9):
    """km-scale Io on top of io_world.surface, and a plume's deposits: a pale SO2 ring of radius `ring` m round
    `vent` (x, y) with a dark flow field at the vent. Inserted before the Principled Base Color, so near and far ground
    share it. Regional colour: FAR_MAP (tools/maps.py far: a well-imaged northern region of the USGS mosaic standing in
    for the smeared polar site, user 2026-10-03) as map / its mean, `weight` 0..1, so the site's polar mean stays;
    missing file → noise: regional tone (80 / 25 km) and dark paterae (Voronoi, ~35 km apart, none within `quiet` m)."""
    g = _Edit(mat)
    b = next(n for n in g.nt.nodes if n.type == 'BSDF_PRINCIPLED')
    src = b.inputs['Base Color'].links[0].from_socket
    tc = g.add('ShaderNodeTexCoord')
    pos = g.o(tc, 'Object')

    def noise(size, detail=4, rough=0.55, dist=0.2):
        n = g.add('ShaderNodeTexNoise', Scale=1.0 / size, Detail=detail, Roughness=rough, Distortion=dist)
        g.set(n, 'Vector', pos)
        return g.o(n, 'Fac')

    reg, sub = noise(80000.0, 3, 0.5, 0.4), noise(25000.0, 5, 0.6, 0.3)
    if os.path.exists(FAR_MAP):
        img = bpy.data.images.load(FAR_MAP, check_existing=True)
        mp = g.add('ShaderNodeMapping')
        g.set(mp, 'Vector', pos)
        mp.inputs['Location'].default_value = (0.5, 0.5, 0.0)
        mp.inputs['Scale'].default_value = (1 / (FAR_KM * 1000), 1 / (FAR_KM * 1000), 1.0)
        tex = g.add('ShaderNodeTexImage', extension='EXTEND', interpolation='Cubic')
        tex.image = img
        g.set(tex, 'Vector', g.o(mp, 0))
        rel = g.mix(1.0, g.o(tex, 'Color'), tuple(1 / c for c in FAR_MEAN), blend='MULTIPLY', clamp=False)
        tone = g.mix(weight, (1.0, 1.0, 1.0), rel, clamp=False)
        col = g.mix(1.0, src, tone, blend='MULTIPLY', clamp=False)
        return _deposits(g, b, col, pos, sub, vent, ring)
    print(f'NOTE globe: {FAR_MAP} missing (python3 tools/maps.py far): noise stands in')
    tone = g.ramp(g.math('ADD', g.math('MULTIPLY', reg, 0.6), g.math('MULTIPLY', sub, 0.4)),
                  [(0.28, (0.45, 0.36, 0.28)), (0.42, (0.85, 0.72, 0.58)), (0.52, (1.05, 1.00, 0.90)),
                   (0.62, (1.45, 1.35, 0.85)), (0.72, (1.20, 0.70, 0.45)), (0.82, (1.55, 1.50, 1.30))])
    col = g.mix(1.0, src, tone, blend='MULTIPLY', clamp=False)
    vo = g.add('ShaderNodeTexVoronoi', feature='F1', distance='EUCLIDEAN')
    wob = g.add('ShaderNodeVectorMath', operation='ADD')
    g.set(wob, 0, pos)
    nv = g.add('ShaderNodeTexNoise', Scale=1 / 9000.0, Detail=3)
    g.set(nv, 'Vector', pos)
    sv = g.add('ShaderNodeVectorMath', operation='SCALE')
    g.set(sv, 0, g.o(nv, 'Color'))
    sv.inputs['Scale'].default_value = 6000.0
    g.set(wob, 1, g.o(sv, 0))
    g.set(vo, 'Vector', g.o(wob, 0))
    vo.inputs['Scale'].default_value = 1 / 35000.0
    vo.inputs['Randomness'].default_value = 0.9
    size = g.maprange(g.o(vo, 'Color'), 0.0, 1.0, 0.04, 0.16)                    # each patera its own radius
    pat = g.math('LESS_THAN', g.o(vo, 'Distance'), size)
    dist0 = g.add('ShaderNodeVectorMath', operation='LENGTH')
    g.set(dist0, 0, pos)
    pat = g.math('MULTIPLY', pat, g.maprange(g.o(dist0, 'Value'), quiet, 2 * quiet))
    col = g.mix(pat, col, W.PAL['lava'])
    return _deposits(g, b, col, pos, sub, vent, ring)


def _deposits(g, b, col, pos, sub, vent, ring):
    if vent is not None:
        dv = g.add('ShaderNodeVectorMath', operation='DISTANCE')
        g.set(dv, 0, pos)
        g.set(dv, 1, (vent[0], vent[1], 0.0))
        d = g.o(dv, 'Value')
        rag = g.math('MULTIPLY', g.math('SUBTRACT', sub, 0.5), 0.35 * ring)
        dd = g.math('ADD', d, rag)
        band = g.math('MULTIPLY', g.maprange(dd, 0.70 * ring, 0.92 * ring), g.maprange(dd, 1.12 * ring, 0.98 * ring))
        col = g.mix(g.math('MULTIPLY', band, 0.85), col, W.PAL['frost'])
        col = g.mix(g.maprange(dd, 0.22 * ring, 0.10 * ring), col, W.PAL['lava'])
    g.nt.links.new(col, b.inputs['Base Color'])
    return g.nt.id_data


def _egress_factor(g, n, d_m):
    """Shader socket: uncovered fraction of the Sun at the shading point, and the Value node keyed with the site's
    sun_limb_sep / R_SUN. x = S + (P·n)·k, f = 1 − (acos x − x√(1 − x²)) / π."""
    geo = g.add('ShaderNodeNewGeometry')
    dt = g.add('ShaderNodeVectorMath', operation='DOT_PRODUCT')
    g.set(dt, 0, g.o(geo, 'Position'))
    g.set(dt, 1, tuple(n))
    S = g.add('ShaderNodeValue')
    S.name = S.label = 'Egress'
    k = math.degrees(1.0 / d_m) / P.R_SUN_DEG
    x = g.math('ADD', g.o(S, 0), g.math('MULTIPLY', g.o(dt, 'Value'), k))
    x = g.math('MINIMUM', g.math('MAXIMUM', x, -1.0), 1.0)
    root = g.math('SQRT', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', x, x)))
    seg = g.math('SUBTRACT', g.math('ARCCOSINE', x), g.math('MULTIPLY', x, root))
    return g.math('SUBTRACT', 1.0, g.math('DIVIDE', seg, math.pi)), S


def egress(mat, n, d_m):
    """Scale everything the surface reflects by the Sun's uncovered fraction at the point (mix to black). Returns the
    'Egress' Value node."""
    g = _Edit(mat)
    out = g.out.inputs['Surface'].links[0].from_socket
    f, S = _egress_factor(g, n, d_m)
    blk = g.add('ShaderNodeEmission', Strength=0.0)
    mx = g.add('ShaderNodeMixShader')
    g.set(mx, 'Fac', f)
    g.nt.links.new(g.o(blk, 0), mx.inputs[1])
    g.nt.links.new(out, mx.inputs[2])
    g.nt.links.new(g.o(mx, 0), g.out.inputs['Surface'])
    return S


# ---------------------------------------------------------------- hot spots and the plume
def hotspots(sc, name, spots, temp=1250.0, glow=2.0, lift=40.0):
    """Glowing lava (visible in the eclipse): ragged discs tangent to the sphere. spots: (x, y, radius m) arc coords."""
    import bmesh
    bm = bmesh.new()
    rng = np.random.default_rng(11)
    for x, y, r in spots:
        X, Y, Z = (float(v) for v in to_world(x, y, lift))
        nrm = normal_at(x, y)
        rot = nrm.to_track_quat('Z', 'Y').to_matrix()
        geom = bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=1.0)
        sx = 0.5 + rng.random()
        for v in geom['verts']:
            k = r * (0.75 + 0.5 * rng.random())
            v.co = Vector((X, Y, Z)) + rot @ Vector((v.co.x * k * sx, v.co.y * k / sx, 0.0))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    bb = g.add('ShaderNodeBlackbody', Temperature=temp)
    nz = g.add('ShaderNodeTexNoise', Scale=1 / 900.0, Detail=4)
    tc = g.add('ShaderNodeTexCoord')
    g.set(nz, 'Vector', g.o(tc, 'Object'))
    em = g.add('ShaderNodeEmission')
    g.set(em, 'Color', g.o(bb, 0))
    g.set(em, 'Strength', g.maprange(g.o(nz, 'Fac'), 0.35, 0.65, 0.1 * glow, glow))
    g.output(g.o(em, 0))
    me.materials.append(m)
    return ob


def plume(sc, name, x, y, h_m, ring_m, n, d_m, density=6e-6, anis=0.7):
    """Umbrella plume at arc point (x, y): apex h_m, deposit ring radius ring_m (physics.umbrella). A box volume
    (−1.2…1.2 × ring, 0…1.25 × apex, along the local vertical); density = a shell on the canopy z = 1 − ρ² (normalised:
    apex 1, ring ρ = 1, the envelope of the ballistic paths) with radial filaments, a faint fill under it and a thin
    column; forward-scattering grains, scatter colour × egress. Returns (object, 'Egress' node)."""
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 2.4, v.co.y * 2.4, (v.co.z + 0.5) * 1.25))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    X, Y, Z = (float(v) for v in to_world(x, y))
    rot = normal_at(x, y).to_track_quat('Z', 'Y').to_matrix().to_4x4()
    ob.matrix_world = Matrix.Translation((X, Y, Z)) @ rot @ Matrix.Diagonal((ring_m, ring_m, h_m, 1.0))
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    p = g.o(tc, 'Object')
    px, py, pz = g.xyz(p)
    rho = g.math('SQRT', g.math('ADD', g.math('MULTIPLY', px, px), g.math('MULTIPLY', py, py)))
    env = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', rho, rho))
    dz = g.math('DIVIDE', g.math('SUBTRACT', pz, env), 0.07)
    shell = g.math('EXPONENT', g.math('MULTIPLY', g.math('MULTIPLY', dz, dz), -1.0))
    shell = g.math('MULTIPLY', shell, g.maprange(pz, 0.0, 0.12))
    fill = g.math('MULTIPLY', g.maprange(pz, g.o(env.node, 0), g.math('SUBTRACT', env, 0.15), 0.0, 0.12), 1.0)
    col_ = g.math('MULTIPLY', g.math('EXPONENT', g.math('MULTIPLY', g.math('MULTIPLY', rho, rho), -1 / 0.0016)),
                  g.maprange(pz, 1.0, 0.85, 0.0, 0.35))
    ang = g.add('ShaderNodeMath', operation='ARCTAN2')
    g.set(ang, 0, py)
    g.set(ang, 1, px)
    fil = g.add('ShaderNodeTexNoise', Detail=5, Roughness=0.6, Distortion=0.5)
    g.set(fil, 'Vector', g.combine(g.math('MULTIPLY', g.o(ang, 0), 6.0), g.math('MULTIPLY', rho, 1.5),
                                   g.math('MULTIPLY', pz, 1.5)))
    fil.inputs['Scale'].default_value = 1.0
    streak = g.maprange(g.o(fil, 'Fac'), 0.3, 0.7, 0.25, 1.4)
    dens = g.math('MULTIPLY', g.math('ADD', g.math('ADD', shell, fill), col_), streak)
    dens = g.math('MULTIPLY', dens, g.maprange(rho, 1.15, 0.95))
    f, S = _egress_factor(g, n, d_m)
    sc_ = g.add('ShaderNodeVolumeScatter', Anisotropy=anis)
    g.set(sc_, 'Color', g.combine(g.math('MULTIPLY', f, 0.80), g.math('MULTIPLY', f, 0.90), f))   # fine grains: bluish
    g.set(sc_, 'Density', g.math('MULTIPLY', dens, density))
    g.nt.links.new(g.o(sc_, 0), g.out.inputs['Volume'])
    me.materials.append(m)
    return ob, S
