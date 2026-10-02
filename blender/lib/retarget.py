"""Mixamo clip → the EMU rig (astronaut.py), baked to an Action by script so every shot rebuilds from files.

Method: world-space rotation transfer with rest alignment. For each mapped bone pointing within 60° of its Mixamo
twin, its rest orientation is first turned (shortest arc) so its direction matches the Mixamo T-pose bone; each frame the Mixamo bone's rotation away from its
rest is applied to that aligned rest. Bones are then solved down the hierarchy into local pose keys (heads stay where
the parent puts them). Hip translation goes on the root bone `Bone` (the EMU's spine hangs off the root, not the
hips), scaled by the hip-height ratio. Unmapped bones keep their pose (helmet visors, palms; fingers 02/03 follow 01).

Timing: the clip's 30 fps is resampled to the scene's fps; `loop=True` wraps it (Mixamo idles loop).
Direction layer: `extra = {bone: f(frame) -> Quaternion}` (armature space) turns that bone and everything below it,
on top of the clip, e.g. the 02 look-up: `{'chest': lambda f: Quaternion((1, 0, 0), -lean(f))}`.

Mixamo download (user): FBX Binary, Without Skin, 30 fps, no keyframe reduction → ../../_assets/mocap/.
"""
import math
import os

import bpy
from mathutils import Matrix, Quaternion, Vector

MOCAP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../_assets/mocap'))

MIXAMO_EMU = {
    'Hips': 'hips', 'Spine': 'spine', 'Spine2': 'chest',
    'LeftShoulder': 'shoulder.L', 'LeftArm': 'upper_arm.L', 'LeftForeArm': 'forearm.L', 'LeftHand': 'hand.L',
    'RightShoulder': 'shoulder.R', 'RightArm': 'upper_arm.R', 'RightForeArm': 'forearm.R', 'RightHand': 'hand.R',
    'LeftUpLeg': 'thigh.L', 'LeftLeg': 'shin.L', 'LeftFoot': 'foot.L',
    'RightUpLeg': 'thigh.R', 'RightLeg': 'shin.R', 'RightFoot': 'foot.R',
    'LeftHandThumb1': 'thumb.01.L', 'LeftHandThumb2': 'thumb.02.L', 'LeftHandIndex1': 'f_index.01.L',
    'LeftHandMiddle1': 'f_middle.01.L', 'LeftHandRing1': 'f_ring.01.L', 'LeftHandPinky1': 'f_pinky.01.L',
    'RightHandThumb1': 'thumb.01.R', 'RightHandThumb2': 'thumb.02.R', 'RightHandIndex1': 'f_index.01.R',
    'RightHandMiddle1': 'f_middle.01.R', 'RightHandRing1': 'f_ring.01.R', 'RightHandPinky1': 'f_pinky.01.R',
}
ROOT = 'Bone'


def import_fbx(path):
    """Import a Mixamo FBX (skeleton only); returns its armature object."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False, ignore_leaf_bones=True)
    new = [o for o in bpy.data.objects if o not in before]
    src = next(o for o in new if o.type == 'ARMATURE')
    for o in new:
        if o is not src:
            bpy.data.objects.remove(o)
    return src


def _short(name):
    return name.split(':', 1)[-1]


def _order(arm):
    out = []

    def walk(b):
        out.append(b.name)
        for c in b.children:
            walk(c)
    for b in arm.data.bones:
        if b.parent is None:
            walk(b)
    return out


def retarget(sc, arm, fbx, name=None, start=1, end=None, loop=True, offset=0.0, extra=None, src_fps=30.0):
    """Bake the clip in `fbx` (path, or a file name in the mocap library) onto `arm` for scene frames start..end.

    `offset` (s) starts the clip that far in. Returns the Action (assigned to arm)."""
    path = fbx if os.path.isabs(fbx) else os.path.join(MOCAP, fbx)
    src = import_fbx(path)
    if src.name not in sc.objects:
        sc.collection.objects.link(src)
    s_act = src.animation_data.action
    f0, f1 = (int(round(v)) for v in s_act.frame_range)
    length = (f1 - f0) / src_fps
    end = end or sc.frame_end
    extra = extra or {}

    smap = {}
    for b in src.data.bones:
        t = MIXAMO_EMU.get(_short(b.name))
        if t and t in arm.data.bones:
            smap[t] = b.name
    missing = sorted(set(MIXAMO_EMU.values()) - set(smap))
    if missing:
        print(f'NOTE retarget: no source for {missing}')

    # rest alignment, per target bone. Frames: the source's world (Mixamo stands at the origin facing −Y once the FBX
    # import has turned it Z-up) ≡ the EMU's armature space (also facing −Y): motion stays relative to the character
    # whatever the shot does with its root
    vl = bpy.context.view_layer
    sw = src.matrix_world.copy()
    s_rest, t_aligned = {}, {}
    for t, s in smap.items():
        sb, tb = src.data.bones[s], arm.data.bones[t]
        sm, tm = sw @ sb.matrix_local, tb.matrix_local
        s_rest[t] = sm.to_3x3().normalized().to_quaternion()
        sdir = (sm.to_3x3() @ Vector((0, 1, 0))).normalized()
        tdir = (tm.to_3x3() @ Vector((0, 1, 0))).normalized()
        tq = tm.to_3x3().normalized().to_quaternion()
        # align only bones that point roughly the same way (T-pose vs the EMU's A-pose arms); a bone defined the other
        # way round (Mixamo Hips points up, the EMU hips down) takes the plain delta: shortest arc of opposites is
        # undefined and flips the legs
        t_aligned[t] = (tdir.rotation_difference(sdir) @ tq) if tdir.angle(sdir) < math.radians(60) else tq
    hips_s = src.data.bones[smap['hips']]
    s_hip0 = (sw @ hips_s.matrix_local).translation
    hip_scale = arm.data.bones['hips'].head_local.z / max(s_hip0.z, 1e-6)

    order = _order(arm)
    rest = {n: arm.data.bones[n].matrix_local.copy() for n in order}
    basis0 = {n: arm.pose.bones[n].matrix_basis.copy() for n in order}
    below = {}                                  # bone → the `extra` bones at or above it
    for n in order:
        p = arm.data.bones[n].parent
        below[n] = (below[p.name] if p else []) + ([n] if n in extra else [])

    act = bpy.data.actions.new(name or f'EMU_{os.path.splitext(os.path.basename(path))[0]}')
    arm.animation_data_create()
    arm.animation_data.action = act
    for n in order:
        arm.pose.bones[n].rotation_mode = 'QUATERNION'
    prev = {}
    fps = sc.render.fps / sc.render.fps_base
    for f in range(start, end + 1):
        t = offset + (f - start) / fps
        t = t % length if loop else min(t, length)
        sf = f0 + t * src_fps
        sc.frame_set(int(math.floor(sf)), subframe=sf - math.floor(sf))
        vl.update()
        want = {}
        for tn, sn in smap.items():
            sq = (sw @ src.pose.bones[sn].matrix).to_3x3().normalized().to_quaternion()
            want[tn] = (sq @ s_rest[tn].inverted()) @ t_aligned[tn]
        ex = {n: fn(f) for n, fn in extra.items()}
        hip = (sw @ src.pose.bones[smap['hips']].matrix).translation
        d_arm = (hip - s_hip0) * hip_scale
        pose = {}
        for n in order:
            pb, b = arm.pose.bones[n], arm.data.bones[n]
            par = pose[b.parent.name] @ (rest[b.parent.name].inverted() @ rest[n]) if b.parent else rest[n]
            if n in want:
                rot = want[n]
                for e in below[n]:
                    rot = ex[e] @ rot
                M = Matrix.Translation(par.translation) @ rot.to_matrix().to_4x4()
                basis = par.inverted() @ M
            elif n == ROOT:
                basis = par.inverted() @ (Matrix.Translation(d_arm) @ par)
            else:                                # unmapped (helmet, palms…): rides on its parent
                basis = basis0[n]
            pose[n] = par @ basis
            q = basis.to_quaternion()
            if n in prev and q.dot(prev[n]) < 0:
                q.negate()
            prev[n] = q
            pb.rotation_quaternion = q
            pb.keyframe_insert('rotation_quaternion', frame=f, group=n)
            if n == ROOT:
                pb.location = basis.translation
                pb.keyframe_insert('location', frame=f, group=n)
    bpy.data.objects.remove(src)
    sc.frame_set(start)
    print(f'NOTE retarget: {os.path.basename(path)} ({length:.2f} s @ {src_fps:g} fps) → {act.name}, '
          f'frames {start}-{end}, {len(smap)} bones, hip scale {hip_scale:.3f}')
    return act
