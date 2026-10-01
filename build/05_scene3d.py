# ====================================================================== GEOMETRY_ENGINE/scene3d
#   perspective scene : tunnel of instanced polygon rings, icosahedra, tori, Copy-SOP Flower of Life and the three
#   2D geometry layers on parallax planes at different Z depths.  Camera is driven by the body (parallax + dolly).
ge = op(ROOT + '/GEOMETRY_ENGINE')
old = ge.op('scene3d')
if old is not None:
    old.destroy()
s3 = ge.create(T('baseCOMP'), 'scene3d')
s3.nodeX, s3.nodeY = 0, -400
_pos[s3.path] = 0
UCH = ROOT + '/GEOMETRY_ENGINE/OUT_UNIFORM_CHOP'
D = 2.5                                  # camera distance to the z = 0 reference plane
ASPECT = 16.0 / 9.0
FOVH = 2.0 * __import__('math').degrees(__import__('math').atan(ASPECT / D))

# ---------------------------------------------------------------- camera
target = mk(s3, 'nullCOMP', 'look_target')
cam = mk(s3, 'cameraCOMP', 'cam3d')
P(cam, fov=FOVH, near=0.05, far=60)
X(cam, tx="op('%s')['r'][20] * 0.9" % UCH,
  ty="op('%s')['g'][20] * 0.5" % UCH,
  tz="%s - op('%s')['b'][20] * 1.4" % (D, UCH))
P(cam, lookat=target.path)

# ---------------------------------------------------------------- materials
def wire_mat(name, width=1.6):
    m = mk(s3, 'wireframeMAT', name)
    P(m, colorr=1.0, colorg=1.0, colorb=1.0, alpha=1.0, linewidth=width, blending=True, srcblend='one',
      destblend='one', depthwriting=False, wireframemode='topology')
    return m


def tex_mat(name, top_path):
    m = mk(s3, 'constantMAT', name)
    P(m, colormap=top_path, blending=True, srcblend='one', destblend='one', depthwriting=False, depthtest=False,
      colorr=1.0, colorg=1.0, colorb=1.0)
    return m


mat_wire = wire_mat('mat_wire', 1.6)
mat_wire_thin = wire_mat('mat_wire_thin', 1.1)
mat_flower = wire_mat('mat_flower', 1.3)
for i, (ch, off) in enumerate((('colorr', 0.0), ('colorg', 0.33), ('colorb', 0.67))):
    X(mat_flower, **{ch: "0.55 * (0.5 + 0.5 * math.cos(6.2831853 * (op('%s')['a'][15] + 0.02 + %s)))" % (UCH, off)})

# ---------------------------------------------------------------- geometry COMP helper
def geo_comp(name, sop_type, sop_pars, mat, inst_chop=None, extra=None, x=None, y=None):
    g = mk(s3, 'geometryCOMP', name)
    for ch in list(g.children):
        ch.destroy()
    sp = g.create(T(sop_type), 'shape')
    P(sp, **sop_pars)
    sp.display = True
    sp.render = True
    P(g, material=mat.path)
    if inst_chop is not None:
        P(g, instancing=True, instanceop=inst_chop.path, instancetx='tx', instancety='ty', instancetz='tz',
          instancerx='rx', instancery='ry', instancerz='rz', instancesx='sx', instancesy='sy', instancesz='sz')
        try:
            P(g, instancecolormode=True)
        except Exception:
            pass
        P(g, instancer='cr', instanceg='cg', instanceb='cb')
    return g, sp


def inst_chop(name, group):
    s = mk(s3, 'scriptCHOP', name)
    s.par.callbacks.eval().text = read('scripts/instances_cb.py').replace('__GROUP__', group)
    P(s, timeslice=False)
    return s


geos = []
# tunnel rings : triangle / hexagon / octagon families interleaved
for k, divs in enumerate((6, 3, 8)):
    ic = inst_chop('inst_ring%d' % k, 'ring%d' % k)
    g, sp = geo_comp('geo_ring%d' % k, 'circleSOP', dict(type='polygon', divs=divs, radx=1.0, rady=1.0, orient='xy')
                     if False else dict(divs=divs, radx=1.0, rady=1.0), mat_wire, ic)
    try:
        sp.par.type = 'polygon'
    except Exception as e:
        WARN.append('circle type: %s' % e)
    geos.append(g)

# icosahedra (Script SOP) and tori
ico_sop_holder = mk(s3, 'geometryCOMP', 'geo_ico')
for ch in list(ico_sop_holder.children):
    ch.destroy()
ico = ico_sop_holder.create(T('scriptSOP'), 'ico')
ico.par.callbacks.eval().text = read('scripts/ico_sop_cb.py')
ico.display = True
ico.render = True
ic = inst_chop('inst_ico', 'ico')
P(ico_sop_holder, material=mat_wire_thin.path, instancing=True, instanceop=ic.path, instancetx='tx', instancety='ty',
  instancetz='tz', instancerx='rx', instancery='ry', instancerz='rz', instancesx='sx', instancesy='sy',
  instancesz='sz', instancer='cr', instanceg='cg', instanceb='cb')
geos.append(ico_sop_holder)

ic = inst_chop('inst_torus', 'torus')
g, sp = geo_comp('geo_torus', 'torusSOP', dict(rows=14, cols=28), mat_wire_thin, ic)
P(sp, radx=1.0, rady=0.38)
geos.append(g)

# Flower of Life in 3D : Circle SOP copied onto a hex lattice (Copy SOP), then Transform SOP
fol = mk(s3, 'geometryCOMP', 'geo_flower3d')
for ch in list(fol.children):
    ch.destroy()
cir = fol.create(T('circleSOP'), 'circle')
P(cir, divs=48, radx=0.5, rady=0.5)
try:
    cir.par.type = 'polygon'
except Exception:
    pass
pts = fol.create(T('scriptSOP'), 'lattice')
pts.par.callbacks.eval().text = read('scripts/hexpts_sop_cb.py')
cp = fol.create(T('copySOP'), 'copy')
wire(cir, cp, 0)
wire(pts, cp, 1)
xf = fol.create(T('transformSOP'), 'xform')
wire(cp, xf)
X(xf, ry="absTime.seconds * 14", rx="20 * math.sin(absTime.seconds * 0.2)") if False else None
xf.display = True
xf.render = True
P(fol, material=mat_flower.path)
X(fol, tx="(op('%s')['r'][3] - 0.5) * 2 * %s" % (UCH, ASPECT), ty="(op('%s')['g'][3] - 0.5) * 2" % UCH,
  ry="absTime.seconds * 12", rz="absTime.seconds * 3", sx="0.16 + 0.12 * op('%s')['g'][10]" % UCH)
X(fol, sy=fol.par.sx.expr, sz=fol.par.sx.expr)
geos.append(fol)

# ---------------------------------------------------------------- parallax planes (the 2D layers at depth)
def plane(name, top_path, z):
    sc = (D - z) / D
    m = tex_mat('mat_' + name, top_path)
    g = mk(s3, 'geometryCOMP', name)
    for ch in list(g.children):
        ch.destroy()
    r = g.create(T('rectangleSOP'), 'quad')
    P(r, sizex=2.0 * ASPECT * sc, sizey=2.0 * sc)
    r.display = True
    r.render = True
    P(g, material=m.path, tz=z)
    return g


geos.append(plane('plane_near', ROOT + '/GEOMETRY_ENGINE/OUT_GEO_NEAR', 0.0))
geos.append(plane('plane_mid', ROOT + '/GEOMETRY_ENGINE/OUT_GEO_MID', -1.4))
geos.append(plane('plane_far', ROOT + '/GEOMETRY_ENGINE/OUT_GEO_FAR', -3.6))

# ---------------------------------------------------------------- render
rnd = mk(s3, 'renderTOP', 'render3d')
P(rnd, camera=cam.path, geometry=' '.join(g.path for g in geos), bgcolorr=0, bgcolorg=0, bgcolorb=0, bgcolora=0,
  outputresolution='custom', format='rgba16float', antialias='aa2' if False else None) if False else None
P(rnd, camera=cam.path, geometry=' '.join(g.path for g in geos), bgcolorr=0, bgcolorg=0, bgcolorb=0, bgcolora=0,
  outputresolution='custom', format='rgba16float')
X(rnd, resolutionw=C('Renderw'), resolutionh=C('Renderh'))
X(rnd, antialias="{'performance': 'aa1', 'standard': 'aa2', 'high': 'aa4'}[%s.eval()]" % C('Quality'))
scene_out = mk(s3, 'nullTOP', 'scene_out')
wire(rnd, scene_out)
old_out = ge.op('OUT_SCENE3D')
if old_out is not None:
    old_out.destroy()
so = mk(ge, 'selectTOP', 'OUT_SCENE3D')
P(so, top=scene_out.path)
log('scene3d built; geometry comps: %d' % len(geos))
