"""Clean the downloaded EMU astronaut into a plain deform rig the film can append and retarget.

Source: Blend Swap #12622 "Astronaut - EMU suit - Rigged", jgilhutton (Juan Ignacio), CC-BY 4.0
(`_assets/models/astronaut-emu-12622/Astronauta.blend`, Blender 2.6x). Output: `emu_clean.blend` beside it, every
object in collection "Astronaut", armature "EMU" (feet on z = 0, facing −Y, 1.89 m tall). The original stays untouched;
re-run this whenever the cleanup changes:

    Blender -b --factory-startup -P tools/prep_astronaut.py

What it does:
- drops the file's camera, sun, backdrop sphere/circle and the 0-face rig widget meshes;
- no emblems (user 2026-10-03): the shoulder patches are dropped, the UN flag on the PLSS is cloned over with fabric
  in the suit texture, the chest's Expedition 44 patch is removed;
- applies the suit's multires at level 3 (the sculpt) and pulls in one stray sculpt spike (two vertices dragged up to 1.7 m
  out from the waist) by relaxing them onto their neighbours;
- flattens the rig: the deform bones (spine, chest, arms, legs) lose their Copy Rotation links to the IK/FK helper
  chains, the helpers and pole bones are deleted (that also removes the file's 6 dependency cycles), the shoulder
  flags weighted to `upper_arm.IK.*` move to `upper_arm.*`, the notepad on `forearm.IK.L` moves to `forearm.L`.
  Every bone inherits its parent's rotation (the thighs didn't).
  Finger chains keep their own Copy Rotation (02/03 follow 01), so a hand curls from one bone per finger.
  The file's helmet pose stays (Parasol −59°, Visera frontal −88.5°, lateral −60.8°: the gold sun visor down); the
  helmet is empty, so with the visor up the clear bubble shows its white lining.
The helmet bone `Casco` is a child of `chest`, as on a real EMU: the head turns inside a helmet fixed to the hard
upper torso, so "looking up" is a lean of the whole upper body.
"""
import os

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.normpath(os.path.join(HERE, '../../../_assets/models/astronaut-emu-12622'))
SRC = os.path.join(SRC_DIR, 'Astronauta.blend')
OUT = os.path.join(SRC_DIR, 'emu_clean.blend')

DROP = {'Camera', 'Sun', 'Sphere', 'Circle',
        'Plane.004', 'Plane.006'}                  # shoulder patches: UN flag, "Vitruvian astronaut" (user: plain suit)
UNLINK = ['upper_arm', 'forearm', 'hand', 'thigh', 'shin', 'foot']   # deform bones driven by IK/FK helpers
HELPER = ('.IK.', '.FK.', 'Polo.')


def relax_spikes(ob, lim=0.2, passes=4):
    """Move vertices with an edge longer than `lim` m onto the mean of their short-edge neighbours.

    The applied sculpt has a 3 mm median edge and none over 0.2 m except the two stray vertices (0.7 and 1.8 m edges).
    """
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    moved = 0
    for _ in range(passes):
        bad = {v for e in bm.edges if e.calc_length() > lim for v in e.verts}
        if not bad:
            break
        for v in bad:
            nb = [e.other_vert(v) for e in v.link_edges]
            good = [u.co for u in nb if u not in bad] or [u.co for u in nb]
            v.co = sum(good, Vector()) / len(good)
            moved += 1
    bm.to_mesh(ob.data)
    bm.free()
    print(f'  {ob.name}: relaxed {moved} vertex moves (edges > {lim} m)')


def plain_emblems():
    """No emblems (user 2026-10-03): the UN flag in the suit texture is covered with a clone of the fabric beside it
    (colour and normal map; a flat fill reads as a blank label), the chest patch (ISS Expedition 44) is removed (the module under it is
    textured). The shoulder patches are dropped with DROP."""
    import numpy as np
    im = bpy.data.images['Traje.jpg.001']
    w, h = im.size
    px = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    blue = (px[..., 2] > px[..., 0] + 0.25) & (px[..., 2] > 0.4)
    ys, xs = np.nonzero(blue)
    y0, y1, x0, x1 = ys.min() - 6, ys.max() + 7, xs.min() - 6, xs.max() + 7
    hh, ww = y1 - y0, x1 - x0
    for dy, dx in ((0, ww + 8), (0, -ww - 8), (hh + 8, 0), (-hh - 8, 0)):        # clone real fabric from beside it
        src = px[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
        if src.shape[:2] == (hh, ww) and src[..., :3].min() > 0.25:            # all inside the same white island
            break
    else:
        raise RuntimeError('no clean fabric next to the flag')
    px[y0:y1, x0:x1] = src
    im.pixels.foreach_set(px.ravel())
    im.pack()
    nm = bpy.data.images['Normal para traje.jpg.002']                          # flat where the flag was: clone it too
    k = nm.size[0] / w
    n = np.empty(nm.size[0] * nm.size[1] * 4, np.float32)
    nm.pixels.foreach_get(n)
    n = n.reshape(nm.size[1], nm.size[0], 4)
    a, b, c, d, oy, ox = (round(v * k) for v in (y0, y1, x0, x1, dy, dx))
    n[a:b, c:d] = n[a + oy:b + oy, c + ox:d + ox].copy()
    nm.pixels.foreach_set(n.ravel())
    nm.pack()
    print(f'  suit texture + normal map: flag {ww}×{hh} px at ({x0}, {y0}) replaced by fabric from offset ({dx}, {dy})')
    bpy.data.objects.remove(bpy.data.objects['Insignia modulo de comando'])


def main():
    bpy.ops.wm.open_mainfile(filepath=SRC)
    for ob in list(bpy.data.objects):
        if ob.name in DROP or (ob.type == 'MESH' and len(ob.data.polygons) == 0):
            bpy.data.objects.remove(ob)

    suit = bpy.data.objects['Traje (Suit)']
    vl = bpy.context.view_layer
    with bpy.context.temp_override(object=suit, active_object=suit, selected_objects=[suit]):
        mr = next(m for m in suit.modifiers if m.type == 'MULTIRES')
        mr.levels = mr.sculpt_levels = mr.render_levels = 3
        bpy.ops.object.modifier_apply(modifier=mr.name)
    relax_spikes(suit)
    plain_emblems()

    arm = bpy.data.objects['metarig']
    arm.name = arm.data.name = 'EMU'
    for pb in arm.pose.bones:
        base = pb.name.rsplit('.', 1)[0]
        if base in UNLINK or pb.name == 'hips':
            for c in list(pb.constraints):
                pb.constraints.remove(c)
    for ob in bpy.data.objects:
        for side in 'LR':
            g = ob.vertex_groups.get(f'upper_arm.IK.{side}')
            if g:
                g.name = f'upper_arm.{side}'
    pad = bpy.data.objects['Notepad']
    mw = pad.matrix_world.copy()
    pad.parent_bone = 'forearm.L'
    vl.update()
    pad.matrix_world = mw

    vl.objects.active = arm
    for o in vl.objects:
        o.select_set(o == arm)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    for b in list(eb):
        if any(h in b.name for h in HELPER):
            eb.remove(b)
    for b in eb:                                   # thighs didn't follow the hips (retarget assumes they do)
        b.use_inherit_rotation = True
    bpy.ops.object.mode_set(mode='OBJECT')          # pose kept: only the helmet bones are posed (sun visor down)

    col = bpy.data.collections.new('Astronaut')
    bpy.context.scene.collection.children.link(col)
    for ob in list(bpy.data.objects):
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        col.objects.link(ob)

    vl.update()
    dg = bpy.context.evaluated_depsgraph_get()
    pts = [suit.evaluated_get(dg).matrix_world @ Vector(c) for c in suit.evaluated_get(dg).bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    arm.location.z -= lo[2]                       # boot soles on z = 0 (they sit 59 mm below the file's origin)
    print('  suit bbox', [round(v, 3) for v in lo], [round(v, 3) for v in hi], f'lifted {-lo[2]:.3f} m')
    print('  bones', len(arm.data.bones), [b.name for b in arm.data.bones if not b.name.startswith(('f_', 'thumb', 'palm'))])
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    print('wrote', OUT)


main()
