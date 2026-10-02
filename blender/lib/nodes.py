"""Tiny shader-node builder: keeps material code readable.

    g = Graph(mat)                       # clears the tree, adds Material Output as g.out
    n = g.add('ShaderNodeTexNoise', Scale=40, Detail=6, noise_type='FBM')
    g.link(n, 'Fac', bsdf, 'Roughness')  # sockets by name, or by identifier (Mix node: 'A_Color')
    g.mix(fac, a, b)                      # RGBA mix; fac/a/b are sockets or constants
"""
import bpy


def _sock(coll, key):
    if isinstance(key, int):
        return coll[key]
    for s in coll:
        if s.identifier == key:
            return s
    for s in coll:
        if s.name == key and s.enabled:
            return s
    raise KeyError(key)


class Graph:
    def __init__(self, mat):
        if not mat.node_tree:
            mat.use_nodes = True
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.out = self.add('ShaderNodeOutputMaterial')

    def add(self, kind, **kw):
        n = self.nt.nodes.new(kind)
        for k, v in kw.items():
            if hasattr(n, k) and k not in {s.name for s in n.inputs}:
                setattr(n, k, v)
            else:
                self.set(n, k, v)
        return n

    def set(self, node, key, value):
        s = _sock(node.inputs, key)
        if isinstance(value, bpy.types.NodeSocket):
            self.nt.links.new(value, s)
        else:
            if isinstance(value, tuple) and len(value) == 3 and s.type == 'RGBA':
                value = (*value, 1.0)
            s.default_value = value
        return s

    def link(self, a, a_out, b, b_in):
        self.nt.links.new(_sock(a.outputs, a_out), _sock(b.inputs, b_in))

    def o(self, node, key=0):
        """Output socket of a node."""
        return _sock(node.outputs, key)

    # --- helpers returning output sockets ---
    def mix(self, fac, a, b, blend='MIX', clamp=True):
        n = self.add('ShaderNodeMix', data_type='RGBA', blend_type=blend, clamp_result=clamp)
        self.set(n, 'Factor_Float', fac)
        self.set(n, 'A_Color', a)
        self.set(n, 'B_Color', b)
        return self.o(n, 'Result_Color')

    def math(self, op, a, b=0.0, clamp=False):
        n = self.add('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.set(n, 0, a)
        self.set(n, 1, b)
        return self.o(n, 0)

    def ramp(self, fac, stops, interp='LINEAR'):
        """stops: [(pos, (r,g,b,a) | float), ...] → Color output."""
        n = self.add('ShaderNodeValToRGB')
        cr = n.color_ramp
        cr.interpolation = interp
        while len(cr.elements) > len(stops):
            cr.elements.remove(cr.elements[-1])
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for el, (pos, col) in zip(cr.elements, stops):
            el.position = pos
            el.color = (col, col, col, 1.0) if isinstance(col, (int, float)) else (*col[:3], 1.0)
        self.set(n, 'Fac', fac)
        return self.o(n, 'Color')

    def maprange(self, v, a0, a1, b0=0.0, b1=1.0, interp='LINEAR', clamp=True):
        n = self.add('ShaderNodeMapRange', interpolation_type=interp, clamp=clamp)
        self.set(n, 'Value', v)
        self.set(n, 'From Min', a0); self.set(n, 'From Max', a1)
        self.set(n, 'To Min', b0); self.set(n, 'To Max', b1)
        return self.o(n, 'Result')

    def xyz(self, v):
        n = self.add('ShaderNodeSeparateXYZ')
        self.set(n, 0, v)
        return self.o(n, 'X'), self.o(n, 'Y'), self.o(n, 'Z')

    def combine(self, x, y, z=0.0):
        n = self.add('ShaderNodeCombineXYZ')
        self.set(n, 'X', x); self.set(n, 'Y', y); self.set(n, 'Z', z)
        return self.o(n, 0)

    def output(self, shader, volume=None):
        self.nt.links.new(shader, _sock(self.out.inputs, 'Surface'))
        if volume is not None:
            self.nt.links.new(volume, _sock(self.out.inputs, 'Volume'))
