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


def stars(sc, px_rad, gain=1.0, density=0.35, cell=0.012, seed=0.0):
    """Black world + procedural stars: one per Voronoi cell (cell ≈ `cell` rad) kept with probability `density`,
    a round spot `px_rad` radians in radius (≈ 1 px at the shot's lens and resolution), brightness heavy-tailed
    (rand⁸: a few bright, many faint), colour 3500–11000 K. `gain` = the brightest star's radiance."""
    w = bpy.data.worlds.new(sc.name + '_Sky')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    g = nodes.Graph.__new__(nodes.Graph)
    g.nt = nt
    out = g.add('ShaderNodeOutputWorld')
    tc = g.add('ShaderNodeTexCoord')
    nrm = g.add('ShaderNodeVectorMath', operation='NORMALIZE')
    g.set(nrm, 0, g.o(tc, 'Generated'))
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
    bb = g.add('ShaderNodeBlackbody')
    g.set(bb, 'Temperature', g.maprange(b, 0.0, 1.0, 3500.0, 11000.0))
    bg = g.add('ShaderNodeBackground')
    g.set(bg, 'Color', g.o(bb, 0))
    g.set(bg, 'Strength', k)
    g.link(bg, 0, out, 'Surface')
    return w


def exposure(sc, ev):
    sc.view_settings.exposure = ev


def px_angle(lens, pct=100, width=1920):
    """Angle (rad) of one pixel at the centre of the frame for a 36 mm-wide sensor."""
    return 36.0 / lens / (width * pct / 100.0)
