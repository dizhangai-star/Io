"""The astronaut: NASA EMU suit, rigged (Blend Swap #12622, jgilhutton, CC-BY 4.0), cleaned by tools/prep_astronaut.py.

Conventions: 1 BU = 1 m, boot soles on the root's z = 0, 1.89 m tall, faces −Y at heading 0 (heading 180 faces +Y,
south, toward Jupiter). `load` appends collection "Astronaut" from the shared asset library and parents its armature
"EMU" to an empty `<name>Root` at `loc`; shots move/turn the root, motion goes on the armature (retarget.py).
Bones (deform): Bone (root) > hips > thigh/shin/foot.L/R; Bone > spine > chest > shoulder/upper_arm/forearm/hand.L/R
(+ fingers, 02/03 copy 01), chest > Casco (helmet, fixed to the hard upper torso as on a real EMU: looking up is a
lean of the upper body) and Bone.001 (chest display module + its knobs).
Missing library file → the code-built proxy (io_world.astronaut_proxy), so every shot still builds.
"""
import math
import os

import bpy
from . import io_world

SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../../_assets/models/astronaut-emu-12622/emu_clean.blend'))
HEIGHT = 1.89


def load(sc, loc, heading=0.0, name='Astronaut'):
    """Append the suit at `loc` (boot soles), turned `heading` degrees about Z. Returns the armature (or the proxy)."""
    if not os.path.exists(SRC):
        print(f'NOTE astronaut: {SRC} missing, using the proxy (run tools/prep_astronaut.py)')
        return io_world.astronaut_proxy(sc, loc, height=HEIGHT, heading=heading)
    with bpy.data.libraries.load(SRC, link=False) as (src, dst):
        dst.collections = ['Astronaut']
    col = dst.collections[0]
    col.name = name
    sc.collection.children.link(col)
    arm = next(o for o in col.objects if o.type == 'ARMATURE')
    root = bpy.data.objects.new(f'{name}Root', None)
    col.objects.link(root)
    root.location = loc
    root.rotation_euler = (0.0, 0.0, math.radians(heading))
    arm.parent = root
    return arm
