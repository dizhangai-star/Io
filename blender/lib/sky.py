"""Io's sky: the Sun lamp (true size, true irradiance, place from its elongation), a black world with stars, exposure.

No air: the world is black apart from stars; no sky light, no haze, shadows razor-sharp (the Sun is 0.10° wide).
Ground light besides the Sun comes from the scene itself (Jupiter's lit disc, lava): Cycles traces it, no fill lamps.
Units: the Sun lamp's strength is its irradiance, E_SUN = 50.3 W/m², so a surface of albedo a facing it has
radiance a·E/π ≈ 10 for frost. Shots set the film exposure (EV) to suit: ≈ −4.5 for sunlit ground and Jupiter,
≈ +2 for the eclipse (Jupiter-shine alone is 6 stops below sunlight).
"""
import math

import bpy
from mathutils import Vector
import physics as P
from . import nodes


def sun(sc, elong, strength=None):
    """Sun lamp at signed elongation `elong` (deg, physics.sun_local). Returns the object."""
    L = bpy.data.lights.new('Sun', 'SUN')
    L.energy = P.E_SUN if strength is None else strength
    L.angle = math.radians(2 * P.R_SUN_DEG)
    L.color = (1.0, 1.0, 1.0)                     # white: the grade's warmth comes later, not from the lamp
    ob = bpy.data.objects.new('Sun', L)
    sc.collection.objects.link(ob)
    ob.rotation_euler = (-Vector(P.sun_local(elong))).to_track_quat('-Z', 'Y').to_euler()
    return ob


def stars(sc, px_rad, gain=1.0, density=0.35, cell=0.012, seed=0.0, axis=None, taps=1):
    """Black world + procedural stars: one per Voronoi cell (cell ≈ `cell` rad) kept with probability `density`,
    a round spot `px_rad` radians in radius (≈ 1 px at the shot's lens and resolution), brightness heavy-tailed
    (rand⁸: a few bright, many faint), colour 3500–11000 K. `gain` = the brightest star's radiance.
    `axis` (local unit vector: Io's pole, physics.jupiter_local()[4]) makes the sky turnable: returns (world, turn,
    smear), two Value nodes a shot keys: turn = the stars' rotation about the pole so far (rad, + = the way they move,
    east → west), smear = their rotation during the shutter (rad), spread over `taps` lookups (star trails; the
    trail's light is shared out, as on film). Without `axis`: returns the world (the static sky of 01/02/04)."""
    w = bpy.data.worlds.new(sc.name + '_Sky')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    g = nodes.Graph.__new__(nodes.Graph)
    g.nt = nt
    out = g.add('ShaderNodeOutputWorld')
    tc = g.add('ShaderNodeTexCoord')
    turn = smear = None
    if axis is None:
        dirs = [g.o(tc, 'Generated')]
    else:
        turn, smear = g.add('ShaderNodeValue'), g.add('ShaderNodeValue')
        turn.name, smear.name = 'StarTurn', 'StarSmear'
        turn.outputs[0].default_value = smear.outputs[0].default_value = 0.0
        dirs = []
        for k in range(taps):
            f = k / (taps - 1) - 0.5 if taps > 1 else 0.0
            ang = g.math('ADD', g.o(turn, 0), g.math('MULTIPLY', g.o(smear, 0), f))
            rot = g.add('ShaderNodeVectorRotate', rotation_type='AXIS_ANGLE')
            g.set(rot, 'Vector', g.o(tc, 'Generated'))
            g.set(rot, 'Axis', tuple(axis))
            g.set(rot, 'Angle', ang)        # view direction → the inertial sky: undo the turn (stars drift + about the pole)
            dirs.append(g.o(rot, 0))
    total = None
    for vec in dirs:
        nrm = g.add('ShaderNodeVectorMath', operation='NORMALIZE')
        g.set(nrm, 0, vec)
        sc_ = g.add('ShaderNodeVectorMath', operation='SCALE', Scale=1.0 / cell)
        g.set(sc_, 0, g.o(nrm, 0))
        v = g.add('ShaderNodeTexVoronoi', feature='F1', Randomness=1.0, W=seed)
        v.voronoi_dimensions = '3D'
        g.set(v, 'Vector', g.o(sc_, 0))
        dist = g.math('MULTIPLY', g.o(v, 'Distance'), cell)                 # radians from the cell's star
        spot = g.math('POWER', g.maprange(dist, px_rad * 1.6, 0.0), 2.0)
        r, gg, b = g.xyz(g.o(v, 'Color'))
        keep = g.math('GREATER_THAN', r, 1.0 - density)
        bright = g.math('POWER', gg, 8.0)
        k = g.math('MULTIPLY', g.math('MULTIPLY', spot, keep), g.math('MULTIPLY', bright, gain))
        if total is None:
            total, temp = k, b                                              # colour: the first lookup's star
        else:
            total = g.math('ADD', total, k)
    if len(dirs) > 1:
        total = g.math('DIVIDE', total, float(len(dirs)))
    bb = g.add('ShaderNodeBlackbody')
    g.set(bb, 'Temperature', g.maprange(temp, 0.0, 1.0, 3500.0, 11000.0))
    bg = g.add('ShaderNodeBackground')
    g.set(bg, 'Color', g.o(bb, 0))
    g.set(bg, 'Strength', total)
    g.link(bg, 0, out, 'Surface')
    return w if axis is None else (w, turn, smear)


def sun_disc(sc, elong, dist=1.5e6):
    """The Sun's disc for the camera only (a Sun lamp is invisible to camera rays): an emitter of true angular size
    and true radiance (E / solid angle) beyond Jupiter, so Jupiter hides it. Returns the object; shots move it with
    `place_sun`."""
    import bmesh
    r = dist * math.tan(math.radians(P.R_SUN_DEG))
    me = bpy.data.meshes.new('SunDisc')
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new('SunDisc', me)
    sc.collection.objects.link(ob)
    for k in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        setattr(ob, k, False)
    m = bpy.data.materials.new('SunDisc')
    g = nodes.Graph(m)
    em = g.add('ShaderNodeEmission')
    g.set(em, 'Color', (1.0, 1.0, 1.0))
    g.set(em, 'Strength', P.E_SUN / (math.pi * math.sin(math.radians(P.R_SUN_DEG)) ** 2))
    g.output(g.o(em, 0))
    me.materials.append(m)
    ob['dist'] = dist
    place_sun(None, ob, elong)
    return ob


def place_sun(lamp, disc, elong, origin=(0.0, 0.0, 0.0)):
    """Point the Sun lamp and move its disc to elongation `elong` (either may be None)."""
    u = Vector(P.sun_local(elong))
    if lamp is not None:
        lamp.rotation_euler = (-u).to_track_quat('-Z', 'Y').to_euler()
    if disc is not None:
        disc.location = Vector(origin) + u * disc['dist']


def glare(sc, threshold=500.0, maximum=3000.0, size=7, strength=1.0, kind='Fog Glow'):
    """Lens glow around the Sun's disc (compositor; only light above `threshold`, i.e. the Sun's ~2e7, glows;
    `maximum` clamps it so the glow stays a camera's, not a white-out)."""
    g = bpy.data.node_groups.new(sc.name + '_Comp', 'CompositorNodeTree')
    g.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = g.nodes.new('CompositorNodeRLayers')
    rl.scene = sc
    gl = g.nodes.new('CompositorNodeGlare')
    for k, v in (('Type', kind), ('Threshold', threshold), ('Clamp', True), ('Maximum', maximum), ('Size', size),
                 ('Strength', strength), ('Quality', 'High')):
        gl.inputs[k].default_value = v
    out = g.nodes.new('NodeGroupOutput')
    g.links.new(rl.outputs['Image'], gl.inputs['Image'])
    g.links.new(gl.outputs['Image'], out.inputs[0])
    sc.compositing_node_group = g
    sc.render.use_compositing = True
    return gl


def exposure(sc, ev):
    sc.view_settings.exposure = ev


def px_angle(lens, pct=100, width=1920):
    """Angle (rad) of one pixel at the centre of the frame for a 36 mm-wide sensor."""
    return 36.0 / lens / (width * pct / 100.0)
