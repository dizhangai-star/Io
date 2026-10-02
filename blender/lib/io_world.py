"""Io's ground: a camera-centred polar terrain patch on the curved surface, the Io surface material, lava, proxies.

Conventions (tools/physics.py): 1 BU = 1 m, X = west (right, facing Jupiter), Y = south (toward Jupiter), Z = up;
the ground under the camera's foot is z = 0. Io's curvature is real: a point r metres away sits r²/2R lower
(R = 1821.6 km; 2 m at the 2.7 km horizon, 0.6 m at the 1.5 km ridge of 02).

The patch is one polar grid around the camera (rings dense where the shot needs silhouette detail, a `band`),
cut to the shot's azimuth sector, heights from numpy fbm plus a shot's own height function. Fine detail is in the
material (bump), not the mesh.
"""
import math
import os

import bpy
import numpy as np
import physics as P
from . import nodes

R_IO_M = P.R_IO * 1000.0


# ---------------------------------------------------------------- numpy value-noise fbm (deterministic)
def _hash(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h & 0xFFFF) / 65535.0


def vnoise(x, y, seed=0):
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - ix, y - iy
    ux, uy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _hash(ix, iy, seed), _hash(ix + 1, iy, seed)
    c, d = _hash(ix, iy + 1, seed), _hash(ix + 1, iy + 1, seed)
    return (a + (b - a) * ux) * (1 - uy) + (c + (d - c) * ux) * uy


def fbm(x, y, oct=5, seed=0, gain=0.5):
    """0..1, mean ~0.5."""
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(oct):
        s = s + amp * vnoise(x, y, seed + o * 17)
        tot += amp
        x, y, amp = x * 2.03 + 3.1, y * 2.03 - 1.7, amp * gain
    return s / tot


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- terrain
def rings(r0, r1, step_frac=0.004, bands=()):
    """Ring radii: geometric (spacing = step_frac × r) from r0 to r1, plus dense bands (a, b, spacing m)."""
    r = list(np.geomspace(r0, r1, int(math.log(r1 / r0) / step_frac)))
    for a, b, s in bands:
        r += list(np.arange(a, b, s))
    return np.unique(np.array(r))


def terrain(sc, name, rr, az_c, az_half, nseg, height, mat=None):
    """Polar grid: radii rr (m) × nseg azimuths in az_c ± az_half (deg, 0 = south, + = west), z = height(X, Y)
    minus the curvature drop. Returns the object."""
    a = np.radians(az_c + np.linspace(-az_half, az_half, nseg))
    RR, AA = np.meshgrid(rr, a, indexing='ij')
    X, Y = RR * np.sin(AA), RR * np.cos(AA)
    Z = height(X, Y) - RR ** 2 / (2 * R_IO_M)
    nr, na = RR.shape
    verts = np.stack([X, Y, Z], -1).reshape(-1, 3)
    ii = np.arange(nr - 1)[:, None] * na + np.arange(na - 1)[None, :]
    faces = np.stack([ii, ii + 1, ii + na + 1, ii + na], -1).reshape(-1, 4)
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
    print(f'NOTE terrain {name}: {len(verts):,} verts')
    return ob


def io_body(sc, below=25.0, r1=100_000.0):
    """Io itself as a shadow-only occluder: a full 360° curved skirt (z = −r²/2R − `below`) out to r1, so a Sun below
    the horizon, or behind the camera outside the terrain's sector, is blocked by the moon, not by nothing.
    r1 stays ~100 km: the scaled-down Jupiter (1000 km out) must not fall in its shadow."""
    rr = np.geomspace(20.0, r1, 160)
    a = np.linspace(0, 2 * math.pi, 129)[:-1]
    RR, AA = np.meshgrid(rr, a, indexing='ij')
    X, Y = RR * np.sin(AA), RR * np.cos(AA)
    Z = -RR ** 2 / (2 * R_IO_M) - below
    verts = np.concatenate([[[0.0, 0.0, -below]], np.stack([X, Y, Z], -1).reshape(-1, 3)])
    na = len(a)
    faces = [(0, 1 + (j + 1) % na, 1 + j) for j in range(na)]
    for i in range(len(rr) - 1):
        for j in range(na):
            k0, k1 = 1 + i * na + j, 1 + i * na + (j + 1) % na
            faces.append((k0, k1, k1 + na, k0 + na))
    me = bpy.data.meshes.new('IoBody')
    me.from_pydata(verts.tolist(), [], faces)
    ob = bpy.data.objects.new('IoBody', me)
    sc.collection.objects.link(ob)
    for k in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'):
        setattr(ob, k, False)
    return ob


def ground_z(height, x, y):
    """Terrain height at one point (with curvature), for placing things on it."""
    X, Y = np.array([float(x)]), np.array([float(y)])
    return float(height(X, Y)[0] - (x * x + y * y) / (2 * R_IO_M))


# ---------------------------------------------------------------- Io surface
# Palette (linear). The site is in Io's reddish-brown polar region: POLAR = the six colour clusters of the USGS
# colour mosaic within ±200 km of the site (`python3 tools/maps.py io`), dark → light. Scattered over it (user
# 2026-10-02, "compromise"): pale SO2 frost fields and yellow sulfur deposits, red short-chain sulfur near vents,
# dark silicate lava.
POLAR = [(0.217, 0.140, 0.059), (0.259, 0.166, 0.069), (0.301, 0.192, 0.075), (0.340, 0.221, 0.095),
         (0.399, 0.248, 0.087), (0.479, 0.287, 0.087)]
PAL = dict(
    frost=(0.70, 0.66, 0.50),
    sulfur=(0.60, 0.47, 0.15),
    ochre=(0.42, 0.20, 0.06),
    red=(0.30, 0.06, 0.025),
    lava=(0.028, 0.023, 0.019),
)
# Galileo SSI's sharpest Io frame (PIA02507, 5–6 m/px, public domain): its grey pattern shapes the colour patches at
# 10 m – 1 km (used as a mask only: it has the Sun's shading baked in). Missing file → a noise stands in.
GALILEO = os.path.expanduser('~/dev/workspace/claude/videos/_assets/textures/io/galileo/PIA02507.png')
GALILEO_M_PX = 5.5


def surface(name='IoSurface', scale=1.0, dark=0.0, red=0.0, frost=0.0, prints=False, clod=0.25):
    """Io ground. Base colour: the site's polar browns, laid out by a km-scale noise mixed with the Galileo pattern;
    over it frost fields (~10 %; `frost` 0..1 widens them), sulfur deposits (~6 %), `red` (0..1) red sulfur, `dark`
    (0..1) dark lava flows. `prints`: the mesh's 'prints' point attribute (lib/prints.py) marks trodden soil: frost
    broken, the brown underneath compacted (darker, a little smoother).
    Bump: 20 m undulation, 1 m clods (`clod` m; less for a close-up, where the mesh carries the relief), 5 cm grain.
    `scale` stretches every size."""
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    pos = g.o(tc, 'Object')

    def noise(size, detail=4, rough=0.55, dist=0.0, w=None):
        n = g.add('ShaderNodeTexNoise', Scale=1.0 / (size * scale), Detail=detail, Roughness=rough, Distortion=dist)
        g.set(n, 'Vector', pos)
        return g.o(n, 'Fac')

    big, mid, small = noise(900, 3, 0.5, 0.3), noise(110, 5, 0.6), noise(9, 6, 0.6)
    if os.path.exists(GALILEO):
        img = bpy.data.images.load(GALILEO, check_existing=True)
        img.colorspace_settings.name = 'Non-Color'
        w, h = img.size
        mp = g.add('ShaderNodeMapping')
        g.set(mp, 'Vector', pos)
        mp.inputs['Rotation'].default_value = (0.0, 0.0, math.radians(23.0))
        mp.inputs['Scale'].default_value = (1 / (w * GALILEO_M_PX * scale), 1 / (h * GALILEO_M_PX * scale), 1.0)
        tex = g.add('ShaderNodeTexImage', extension='MIRROR', interpolation='Cubic')
        tex.image = img
        g.set(tex, 'Vector', g.o(mp, 0))
        gal = g.maprange(g.o(tex, 'Color'), 0.25, 0.80)
    else:
        gal = noise(60, 6, 0.65)
    field = g.math('ADD', g.math('MULTIPLY', big, 0.55), g.math('MULTIPLY', gal, 0.45))
    n = len(POLAR)
    col = g.ramp(field, [(0.30 + 0.40 * k / (n - 1), c) for k, c in enumerate(POLAR)])
    pat = g.math('ADD', g.math('MULTIPLY', mid, 0.5), g.math('MULTIPLY', gal, 0.5))
    col = g.mix(g.maprange(pat, 0.66 - 0.25 * frost, 0.72 - 0.25 * frost), col, PAL['frost'])  # frost fields
    col = g.mix(g.maprange(noise(320, 4, 0.6), 0.68, 0.73), col, PAL['sulfur'])             # sulfur deposits
    col = g.mix(g.math('MULTIPLY', g.maprange(big, 0.36, 0.30 - 0.1 * red), g.maprange(mid, 0.45, 0.35)),
                col, PAL['red'])                                                              # red sulfur
    lava_f = g.math('MULTIPLY', g.maprange(big, 0.70 - 0.2 * dark, 0.76 - 0.2 * dark),
                    g.maprange(small, 0.40, 0.48))
    col = g.mix(lava_f, col, PAL['lava'])                                                     # dark flow fields
    # scarps and steep faces: layered flows (strata, lenses ~7 m thick) and downslope streaks (talus, frost runs)
    geo = g.add('ShaderNodeNewGeometry')
    _, _, nz = g.xyz(g.o(geo, 'Normal'))
    steep = g.maprange(nz, 0.95, 0.80)
    lay = g.add('ShaderNodeMapping')                 # layers: noise squashed 12:1 vertically → irregular lenses
    g.set(lay, 'Vector', pos)
    lay.inputs['Scale'].default_value = (1 / (90.0 * scale), 1 / (90.0 * scale), 1 / (7.0 * scale))
    wave = g.add('ShaderNodeTexNoise', Scale=1.0, Detail=3, Roughness=0.5, Distortion=0.4)
    g.set(wave, 'Vector', g.o(lay, 0))
    strata = g.ramp(g.o(wave, 'Fac'), [(0.10, PAL['frost']), (0.35, POLAR[4]), (0.60, POLAR[1]),
                                       (0.80, PAL['ochre']), (0.95, PAL['frost'])])
    col = g.mix(g.math('MULTIPLY', steep, g.maprange(mid, 0.3, 0.7, 0.15, 0.55)), col, strata)
    mp = g.add('ShaderNodeMapping')
    g.set(mp, 'Vector', pos)
    mp.inputs['Scale'].default_value = (1 / (4.0 * scale), 1 / (4.0 * scale), 1 / (60.0 * scale))
    st = g.add('ShaderNodeTexNoise', Scale=1.0, Detail=4, Roughness=0.6)
    g.set(st, 'Vector', g.o(mp, 0))
    col = g.mix(g.math('MULTIPLY', steep, g.maprange(g.o(st, 'Fac'), 0.5, 0.7)), col, PAL['frost'])
    col = g.mix(g.maprange(small, 0.35, 0.75, 0.0, 0.25), col, (0.25, 0.20, 0.10), blend='MULTIPLY')  # grit
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.92)
    b.inputs['Specular IOR Level'].default_value = 0.25
    if prints:
        at = g.add('ShaderNodeAttribute', attribute_name='prints')
        pm = g.o(at, 'Fac')
        col = g.mix(g.math('MULTIPLY', pm, 0.5), col, tuple(0.9 * c for c in POLAR[2]))
        g.set(b, 'Roughness', g.maprange(pm, 0.0, 1.0, 0.92, 0.8))
    g.set(b, 'Base Color', col)
    clods, grain = noise(1.0, 6, 0.6), noise(0.05, 4, 0.5)
    h = g.math('ADD', g.math('MULTIPLY', noise(20, 3), 1.5), g.math('MULTIPLY', clods, clod))
    h = g.math('ADD', h, g.math('MULTIPLY', grain, 0.012))
    bp = g.add('ShaderNodeBump', Strength=1.0, Distance=1.0)
    g.set(bp, 'Height', h)
    g.set(b, 'Normal', g.o(bp, 'Normal'))
    g.output(g.o(b, 'BSDF'))
    return m


def lava_lake(sc, name, centre, radius, z, temp=1350.0, glow=1.0, crust=0.85, seed=0.0):
    """Loki-type lava lake: a flat disc at height z, dark cooled crust broken into plates; the cracks between plates
    and a band at the shore glow at blackbody `temp` K. `glow` = emission strength (W/m²-ish radiance scale), keyed
    by the shot against its exposure. Lights the ground near it (emission is a light source in Cycles)."""
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=radius)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.location = (centre[0], centre[1], z)
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    pos = g.o(tc, 'Object')
    vor = g.add('ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE', Scale=1 / 18.0, W=seed)
    vor.voronoi_dimensions = '3D'
    g.set(vor, 'Vector', pos)
    nz = g.add('ShaderNodeTexNoise', Scale=1 / 40.0, Detail=4)
    g.set(nz, 'Vector', pos)
    crack = g.maprange(g.o(vor, 'Distance'), 0.02 + 0.06 * (1 - crust), 0.0)     # 1 on the plate edges
    crack = g.math('MULTIPLY', crack, g.maprange(g.o(nz, 'Fac'), 0.35, 0.6))
    ln = g.add('ShaderNodeVectorMath', operation='LENGTH')
    g.set(ln, 0, pos)
    shore = g.math('POWER', g.maprange(g.o(ln, 'Value'), radius * 0.93, radius), 2.0)
    hot = g.math('MAXIMUM', crack, shore)
    bb = g.add('ShaderNodeBlackbody', Temperature=temp)
    em = g.add('ShaderNodeEmission')
    g.set(em, 'Color', g.o(bb, 0))
    g.set(em, 'Strength', g.math('MULTIPLY', g.math('POWER', hot, 3.0), glow))
    d = g.add('ShaderNodeBsdfDiffuse', Color=(0.02, 0.018, 0.016, 1))
    add = g.add('ShaderNodeAddShader')
    g.link(d, 0, add, 0)
    g.link(em, 0, add, 1)
    g.output(g.o(add, 0))
    me.materials.append(m)
    return ob


def vent_glow(sc, name, pts, size=0.6, temp=1100.0, glow=1.0):
    """Small hot cracks / vents: flattened emissive discs at given (x, y, z)."""
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rng = np.random.default_rng(7)
    for (x, y, z) in pts:
        r = size * (0.4 + rng.random())
        geom = bmesh.ops.create_circle(bm, cap_ends=True, segments=12, radius=r)
        sx = 0.4 + 1.6 * rng.random()
        for v in geom['verts']:
            v.co.x, v.co.y, v.co.z = x + v.co.x * sx, y + v.co.y / sx, z + 0.02
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    bb = g.add('ShaderNodeBlackbody', Temperature=temp)
    em = g.add('ShaderNodeEmission', Strength=glow)
    g.set(em, 'Color', g.o(bb, 0))
    g.output(g.o(em, 0))
    me.materials.append(m)
    return ob


# ---------------------------------------------------------------- proxies (Sprint 2 replaces them)
def _mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=rough, Metallic=metal)
    g.set(b, 'Base Color', color)
    g.output(g.o(b, 'BSDF'))
    return m


def astronaut_proxy(sc, loc, height=1.85, heading=0.0):
    """Suit stand-in: a white capsule (body) + sphere (helmet) + pack box, 1.85 m tall."""
    suit = _mat('SuitProxy', (0.80, 0.79, 0.76), 0.7)
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=height * 0.62, location=(0, 0, height * 0.42))
    parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(0, 0, height * 0.85))
    parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.26, height * 0.55))
    parts.append(bpy.context.object)
    parts[-1].scale = (0.45, 0.22, 0.6)
    for p in parts:
        p.data.materials.append(suit)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = 'Astronaut'
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(heading))
    return ob


def lander_proxy(sc, loc, heading=0.0):
    """Lander stand-in: octagonal body 2.8 m across on four splayed legs with pads, gold-foil skirt; ~4 m tall."""
    body = _mat('LanderBody', (0.62, 0.62, 0.60), 0.35, 0.6)
    foil = _mat('LanderFoil', (0.80, 0.55, 0.18), 0.28, 1.0)
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.4, depth=1.6, location=(0, 0, 2.0))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(body)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.5, depth=0.7, location=(0, 0, 0.95))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(foil)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.5, radius2=0.25, depth=0.7, location=(0, 0, 3.1))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(body)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        top, foot = (1.2 * math.cos(a), 1.2 * math.sin(a), 1.4), (2.3 * math.cos(a), 2.3 * math.sin(a), 0.1)
        mid = tuple((p + q) / 2 for p, q in zip(top, foot))
        d = math.dist(top, foot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=d, location=mid)
        leg = bpy.context.object
        v = np.subtract(top, foot)
        leg.rotation_euler = (0, math.atan2(math.hypot(v[0], v[1]), v[2]), math.atan2(v[1], v[0]))
        leg.data.materials.append(body)
        parts.append(leg)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.08, location=foot)
        parts.append(bpy.context.object)
        parts[-1].data.materials.append(body)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = 'Lander'
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(heading))
    return ob
