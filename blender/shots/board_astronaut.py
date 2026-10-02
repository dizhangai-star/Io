"""Look board for the astronaut (Sprint 2): the EMU suit on Io ground in the film's real light, four headings.

Frames 1–4 turn the suit 0 / 90 / 180 / 270° (0 faces the camera). Camera 50 mm, 8 m from the suit (arms lowered 65° from the T-pose), eye 1.5 m,
`--facing north` (default: the Sun, always in the southern half of the sky when up, behind the camera) or `south`
(toward Jupiter, 14.8° up above the frame: the suit against the light); the Sun at `--elong` (default 40: 11.4° up),
Jupiter's lit disc adds its own fill. Not a clip; run directly:

    Blender -b --factory-startup -P blender/shots/board_astronaut.py -- --stills 1,2,3,4 --pct 50 --samples 64 \
        --stills-dir frames/astronaut --id emu
Options: --elong DEG  --facing north|south  --exposure EV  --dist M  --lens MM  --aimz M  --arms DEG
         --clip FILE (mocap library) --lean DEG --turn DEG --frames N: motion test (stills at chosen frames)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import bpy
from mathutils import Matrix, Quaternion, Vector
import physics
from lib import nodes, rig, shot, io_world, jupiter, sky, astronaut, retarget
for m in (physics, nodes, rig, shot, io_world, jupiter, sky, astronaut, retarget):
    importlib.reload(m)
P = physics

A = shot.args()
LENS = float(A.opt('lens', 50.0))
DIST = float(A.opt('dist', 8.0))
CLIP = A.opt('clip')                          # e.g. "Breathing Idle.fbx": motion test instead of the turntable
LEAN = float(A.opt('lean', 20.0))             # with --clip: upper-body lean back (the 02 look-up), frames 120 → 168
ARMS = 0.0 if CLIP else float(A.opt('arms', 65.0))            # lower the T-pose arms by this many degrees (tests the shoulder weights)
ELONG = float(A.opt('elong', 40.0))           # Sun 11.4° up, 41° west of Jupiter (0 = behind Jupiter: eclipse)
NORTH = A.opt('facing', 'north') == 'north'   # north: the Sun behind the camera (suit lit); south: toward Jupiter

sc = rig.new_scene('Board_Astronaut')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames if CLIP else 4
sky.exposure(sc, float(A.opt('exposure', -4.8)))

SGN = -1.0 if NORTH else 1.0                  # +Y is south
ground = io_world.terrain(sc, 'Ground', io_world.rings(0.5, 400.0, 0.02), 180.0 if NORTH else 0.0, 60.0, 240,
                          lambda X, Y: 0.15 * (io_world.fbm(X / 6, Y / 6, 4, 3) - 0.5), io_world.surface('IoSurface'))
io_world.io_body(sc)

arm = astronaut.load(sc, (0.0, SGN * DIST, 0.0), heading=180.0 if NORTH else 0.0)
root = arm.parent or arm
if arm.type == 'ARMATURE' and ARMS:
    bpy.context.view_layer.update()
    for side, sgn in (('L', 1.0), ('R', -1.0)):
        pb = arm.pose.bones[f'upper_arm.{side}']
        h = pb.head.copy()
        R = Matrix.Translation(h) @ Matrix.Rotation(math.radians(sgn * ARMS), 4, 'Y') @ Matrix.Translation(-h)
        pb.matrix = R @ pb.matrix
if CLIP:
    root.rotation_euler.z += math.radians(float(A.opt('turn', 30.0)))      # three-quarter view: the lean reads
    def lean(f):
        u = min(max((f - 120) / 48.0, 0.0), 1.0)
        return Quaternion((1, 0, 0), -math.radians(LEAN) * u * u * (3 - 2 * u))
    retarget.retarget(sc, arm, CLIP, extra={'chest': lean})
else:
    h0 = math.degrees(root.rotation_euler.z)
    for f, h in zip(range(1, 5), (0, 90, 180, 270)):
        root.rotation_euler.z = math.radians(h0 + h)
        root.keyframe_insert('rotation_euler', index=2, frame=f)   # stills land on the keys: interpolation moot

cam_loc = Vector((0.0, 0.0, 1.5))
sun = sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=20.0)
jupiter.build(sc, cam_loc, grs=-40.0)
aim = Vector((0.0, SGN * DIST, float(A.opt('aimz', 0.95))))
cam = rig.camera(sc, cam_loc, aim, lens=LENS, fstop=8.0, focus=aim)
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6
el, az = P.alt_az(P.sun_local(ELONG))
print(f'NOTE board: Sun elongation {ELONG:.0f}° → el {el:.1f}° az {az:+.1f}°, Jupiter {100 * P.lit_fraction(ELONG):.0f} % lit')

shot.run(sc, A, tag='emu')
