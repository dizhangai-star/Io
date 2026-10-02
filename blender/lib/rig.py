"""Scene, render settings, camera and the lighting looks."""
import bpy
from mathutils import Vector


def new_scene(name):
    """A fresh scene (the user's other scenes are left alone) made active in the current window."""
    if bpy.app.background:                       # headless: reuse the factory scene
        sc = bpy.context.scene
        for ob in list(sc.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        sc.name = name
        return sc
    old = bpy.data.scenes.get(name)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.scenes.remove(old)
    sc = bpy.data.scenes.new(name)
    bpy.context.window.scene = sc
    return sc


def enable_gpu():
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type != 'CPU'
    return [d.name for d in prefs.devices if d.use]


def render_settings(sc, samples=128, res=(1920, 1080), pct=100, fps=24):
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'GPU'
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 16
    sc.cycles.transmission_bounces = 16
    sc.cycles.glossy_bounces = 8
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.caustics_refractive = True
    sc.cycles.caustics_reflective = True
    sc.cycles.blur_glossy = 0.5
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = pct
    sc.render.fps = fps
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '8'
    vs = sc.view_settings
    vs.view_transform = 'AgX'
    for look in ('AgX - Medium High Contrast', 'Medium High Contrast'):
        try:
            vs.look = look
            break
        except TypeError:
            pass


def camera(sc, loc, target, lens=100.0, fstop=5.6, focus=None, name='Cam'):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.sensor_width = 36.0
    cam.clip_start = 0.001
    cam.clip_end = 10.0
    cam.dof.use_dof = True
    cam.dof.aperture_fstop = fstop
    ob = bpy.data.objects.new(name, cam)
    sc.collection.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.dof.focus_distance = (Vector(focus) - Vector(loc)).length if focus else d.length
    sc.camera = ob
    return ob


def _area(sc, name, loc, target, size, power, color, shape='RECTANGLE', size_y=None):
    L = bpy.data.lights.new(name, 'AREA')
    L.shape = shape
    L.size = size
    L.size_y = size_y or size
    L.energy = power
    L.color = color
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def _world(sc, top, bottom, strength=1.0):
    """Gradient backdrop seen by the camera, plus faint ambient."""
    w = bpy.data.worlds.new(sc.name + '_World')
    sc.world = w
    if not w.node_tree:
        w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = strength
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = -0.4
    mr.inputs['From Max'].default_value = 0.6
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*bottom, 1)
    ramp.color_ramp.elements[1].color = (*top, 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    return w


# Each look: lights placed around a subject at the origin, eye looking toward the camera side.
# Positions are in metres; the eye is 24 mm across.
def look(sc, name, subject=(0, 0, 0)):
    s = Vector(subject)
    if name == 'clinical':     # cool teal key softbox, warm rim, dark navy backdrop
        _world(sc, (0.010, 0.022, 0.035), (0.001, 0.002, 0.004))
        _area(sc, 'Key', s + Vector((-0.18, -0.30, 0.22)), s, 0.22, 9.0, (0.78, 0.92, 1.0), size_y=0.14)
        _area(sc, 'Fill', s + Vector((0.30, -0.25, -0.08)), s, 0.35, 1.2, (0.55, 0.75, 1.0))
        _area(sc, 'Rim', s + Vector((0.20, 0.25, 0.12)), s, 0.10, 6.0, (1.0, 0.72, 0.45))
    elif name == 'dramatic':   # single hard warm side key, black backdrop, thin cool kicker
        _world(sc, (0.002, 0.002, 0.002), (0.0, 0.0, 0.0))
        key = _area(sc, 'Key', s + Vector((-0.35, -0.12, 0.10)), s, 0.05, 6.0, (1.0, 0.80, 0.60), shape='DISK')
        kick = _area(sc, 'Kicker', s + Vector((0.22, 0.20, 0.05)), s, 0.06, 2.5, (0.60, 0.80, 1.0))
        # soft catchlights instead of the lights' crisp mirror dots (peaks kept low: a clipped falloff reads as a hard
        # disc); a firm-edged card far right mirrors in the sclera
        # beside the limbus (in the macro focus plane), where the ripple breaks it into wet glints and shows the wet film
        soft_reflector(sc, 'KeyGlint', 0.05, light=key, k=60.0)
        soft_reflector(sc, 'KickerGlint', 0.06, light=kick, k=40.0)
        soft_reflector(sc, 'Sheen', 0.05, 8.0, s + Vector((0.26, -0.10, 0.0)), s, core=0.6)
    elif name == 'textbook':   # high key: big soft lights, pale grey backdrop
        _world(sc, (0.55, 0.58, 0.62), (0.30, 0.32, 0.35), strength=0.9)
        _area(sc, 'Key', s + Vector((-0.20, -0.30, 0.25)), s, 0.45, 10.0, (1.0, 0.98, 0.95))
        _area(sc, 'Fill', s + Vector((0.30, -0.28, 0.0)), s, 0.50, 4.0, (0.95, 0.97, 1.0))
    else:
        raise ValueError(name)


def soft_reflector(sc, name, radius, strength=0.0, loc=(0, 0, 0), target=(0, 0, 0), light=None, k=None, core=0.0):
    """A round emitter seen only in reflections (glossy rays), with a smooth radial falloff: a soft catchlight.
    Hard area lights mirror as crisp dots on the cornea. With `light`, the disk is parented to that light, the
    light is hidden from reflections, and the disk's strength follows it: strength = light.energy × k (a driver,
    so dimming or animating the light's energy carries over). `core` (0..1): the fraction of the radius that is
    flat-bright (0 = all falloff; ~0.8 = a firm-edged card whose edge the tear-film ripple breaks). Returns the
    Emission node."""
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=radius)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    if light:
        ob.parent = light
        light.visible_glossy = False
    else:
        ob.location = loc
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    ob.visible_camera = ob.visible_diffuse = ob.visible_shadow = ob.visible_transmission = False
    ob.visible_volume_scatter = False
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ln = nt.nodes.new('ShaderNodeVectorMath')
    ln.operation = 'LENGTH'
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = radius, radius * core
    sq = nt.nodes.new('ShaderNodeMath')
    sq.operation = 'POWER'
    sq.inputs[1].default_value = 2.0
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tc.outputs['Object'], ln.inputs[0])
    nt.links.new(ln.outputs['Value'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], sq.inputs[0])
    nt.links.new(sq.outputs['Value'], em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    me.materials.append(m)
    if light:
        fc = em.inputs['Strength'].driver_add('default_value')
        fc.driver.type = 'SCRIPTED'
        v = fc.driver.variables.new()
        v.name = 'e'
        v.targets[0].id_type = 'LIGHT'
        v.targets[0].id = light.data
        v.targets[0].data_path = 'energy'
        fc.driver.expression = f'e*{k}'          # simple expression: evaluated without Python auto-exec
    return em
