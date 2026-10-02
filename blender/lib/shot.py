"""Shared entry for shot scripts: argument parsing and the two ways a shot is rendered.

    from lib import shot
    A = shot.args()                         # A.opt('look', 'dramatic'), A.frames, A.samples, A.pct, A.engine
    ... build the scene sc ...
    shot.run(sc, A)                         # --out DIR → animation · --stills 1,30,60 → preview PNGs · neither → nothing
                                            # --freeze F (with --out): frames F… from one EXR + keyed exposure (freeze)

--engine cycles (default) | eevee | workbench: run() switches the engine just before rendering, keeping the camera,
lens, DOF and frame range. workbench = the animatic draft (seconds per frame): flat material colours + cavity + shadow,
volume-only objects (Haze) hidden.

Called by ../../render.mjs (animation) and ../../preview.mjs (stills); both pass --frames from the clip's duration.
"""
import os
import sys
import time

import bpy
from . import rig

RES = (1920, 804)                           # 2.39:1 picture only (−25 % render time); render.mjs pads to 1920×1080


class Args:
    def __init__(self, argv):
        self.argv = argv

    def opt(self, k, d=None):
        return self.argv[self.argv.index('--' + k) + 1] if '--' + k in self.argv else d

    @property
    def frames(self):
        return int(self.opt('frames', 144))

    @property
    def samples(self):
        return int(self.opt('samples', 64))

    @property
    def pct(self):
        return int(self.opt('pct', 100))

    @property
    def engine(self):
        return self.opt('engine', 'cycles')


def args():
    return Args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


ENGINES = {'cycles': 'CYCLES', 'eevee': 'BLENDER_EEVEE', 'workbench': 'BLENDER_WORKBENCH'}


def _base_color(m):
    """(r, g, b, a) for Workbench: the first Principled BSDF's unlinked Base Color (linked → its image's mean or grey);
    alpha from Alpha × (1 − Transmission) so glass stays see-through."""
    if not (m.use_nodes and m.node_tree):
        return tuple(m.diffuse_color)
    b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if b is None:
        return None
    i = b.inputs['Base Color']
    c = (0.6, 0.6, 0.6)
    if not i.is_linked:
        c = tuple(i.default_value)[:3]
    else:
        src = i.links[0].from_node
        img = getattr(src, 'image', None)
        if img is not None and img.size[0]:
            px = img.pixels[:]
            n = len(px) // 4
            step = max(1, n // 4096)
            c = tuple(sum(px[4 * k + j] for k in range(0, n, step)) / len(range(0, n, step)) for j in range(3))
    a = b.inputs['Alpha'].default_value * (1 - b.inputs['Transmission Weight'].default_value)
    return (*c, max(a, 0.15))


def engine(sc, A):
    """Switch sc to A.engine (render settings for Cycles are already set by rig.render_settings)."""
    e = A.engine
    sc.render.engine = ENGINES[e]
    if e != 'workbench':
        return
    sc.view_settings.exposure = 0.0           # studio light: the Cycles exposure (set for true irradiance) would blacken it
    sh = sc.display.shading
    sh.light, sh.color_type = 'STUDIO', 'TEXTURE'     # image-textured parts show their image, the rest diffuse_color
    sh.show_cavity, sh.cavity_type = True, 'BOTH'
    sh.show_shadows = True
    sc.display.render_aa = '8'
    for m in bpy.data.materials:
        c = _base_color(m)
        if c is not None:
            m.diffuse_color = c
    for ob in sc.objects:                     # volume-only meshes (the haze box) would render as a solid block
        ms = [s.material for s in ob.material_slots if s.material and s.material.node_tree]
        if ms and all(not any(n.type == 'BSDF_PRINCIPLED' for n in mm.node_tree.nodes) and
                      any(n.type.startswith('PRINCIPLED_VOLUME') or n.type == 'VOLUME_SCATTER' for n in mm.node_tree.nodes)
                      for mm in ms):
            ob.hide_render = True
        elif not ob.visible_camera:           # shadow-only rigs (fan) stay out of the frame
            ob.hide_render = True


def run(sc, A, tag=None):
    tag = tag or sc.name
    engine(sc, A)
    gpus = rig.enable_gpu() if A.engine == 'cycles' else A.engine
    out, stills = A.opt('out'), A.opt('stills')
    if stills:
        d = os.path.abspath(A.opt('stills-dir', 'frames'))
        os.makedirs(d, exist_ok=True)
        t = time.time()
        for f in (int(x) for x in stills.split(',')):
            sc.frame_set(f)
            sc.render.filepath = os.path.join(d, f'{A.opt("id", tag)}-f{f:04d}.png')
            bpy.ops.render.render(write_still=True, scene=sc.name)
        print(f'SHOT {tag}: stills {stills} in {time.time() - t:.1f}s')
    if out:
        os.makedirs(out, exist_ok=True)
        sc.render.filepath = os.path.join(os.path.abspath(out), '')
        end, F = sc.frame_end, int(A.opt('freeze', 0))
        if F:
            sc.frame_end = F - 1
        t = time.time()
        bpy.ops.render.render(animation=True, scene=sc.name)
        dt = time.time() - t
        n = sc.frame_end - sc.frame_start + 1
        print(f'SHOT {tag}: {n} frames in {dt:.0f}s = {dt / n:.1f}s/frame on {gpus}')
        if F:
            sc.frame_end = end
            freeze(sc, F, out)


def freeze(sc, F, out):
    """Frames F…frame_end from one render: frame F is rendered once into a linear EXR (after the compositor, so the
    glare is in it), then an empty post scene shows that EXR through the same view transform and look with each
    frame's own exposure (the shot's keyed `view_settings.exposure`) → out/NNNN.png. For a still tail where nothing
    moves but the exposure (04: the eyes adjust after the eclipse); grain is added at compile."""
    t = time.time()
    ev = []
    for f in range(F, sc.frame_end + 1):
        sc.frame_set(f)
        ev.append(sc.view_settings.exposure)
    sc.frame_set(F)
    im = sc.render.image_settings
    fmt, depth = im.file_format, im.color_depth
    im.file_format, im.color_depth = 'OPEN_EXR', '32'
    exr = os.path.join(os.path.abspath(out), f'freeze-{F:04d}.exr')
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True, scene=sc.name)
    im.file_format, im.color_depth = fmt, depth

    post = bpy.data.scenes.new(sc.name + '_Freeze')
    post.render.engine = 'BLENDER_WORKBENCH'
    r = post.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = sc.render.resolution_x, sc.render.resolution_y, \
        sc.render.resolution_percentage
    r.image_settings.file_format, r.image_settings.color_depth = fmt, depth
    post.display_settings.display_device = sc.display_settings.display_device
    vs = post.view_settings
    vs.view_transform, vs.look, vs.gamma = sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.gamma
    g = bpy.data.node_groups.new(post.name + '_Comp', 'CompositorNodeTree')
    g.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    node = g.nodes.new('CompositorNodeImage')
    node.image = bpy.data.images.load(exr)
    o = g.nodes.new('NodeGroupOutput')
    g.links.new(node.outputs['Image'], o.inputs[0])
    post.compositing_node_group = g
    r.use_compositing = True
    for f, e in zip(range(F, sc.frame_end + 1), ev):
        vs.exposure = e
        r.filepath = os.path.join(os.path.abspath(out), f'{f:04d}.png')
        bpy.ops.render.render(write_still=True, scene=post.name)
    print(f'SHOT {sc.name}: frozen {F}–{sc.frame_end} from one frame in {time.time() - t:.0f}s')
