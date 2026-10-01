# ====================================================================== PROJECTION_MAPPING
#   OUT_FEEDBACK -> [surface 1..3: crop -> corner pin (keystone) -> edge blend -> projection mask] -> sum
#                -> (optional Kantan Mapper) -> brightness / gamma / black level -> OUT_PROJECTION
#   Each surface is an independent COMP so architectural surfaces can later be mapped one by one.
import os
c = container('PROJECTION_MAPPING')
uni = sel_uni(c)
src = sel(c, 'source', ROOT + '/FEEDBACK_SYSTEM/OUT_FEEDBACK')
OW, OH = C('Outputw') + '.eval()', C('Outputh') + '.eval()'

SURF_PARS = [
    ('toggle', 'Enable', 'Surface enabled', 1),
    ('float', 'Cropl', 'Crop left', 0.0, 0.0, 1.0), ('float', 'Cropr', 'Crop right', 0.0, 0.0, 1.0),
    ('float', 'Cropb', 'Crop bottom', 0.0, 0.0, 1.0), ('float', 'Cropt', 'Crop top', 0.0, 0.0, 1.0),
    ('float', 'Tlx', 'Top-left X', 0.0, -0.5, 1.5), ('float', 'Tly', 'Top-left Y', 1.0, -0.5, 1.5),
    ('float', 'Trx', 'Top-right X', 1.0, -0.5, 1.5), ('float', 'Try', 'Top-right Y', 1.0, -0.5, 1.5),
    ('float', 'Blx', 'Bottom-left X', 0.0, -0.5, 1.5), ('float', 'Bly', 'Bottom-left Y', 0.0, -0.5, 1.5),
    ('float', 'Brx', 'Bottom-right X', 1.0, -0.5, 1.5), ('float', 'Bry', 'Bottom-right Y', 0.0, -0.5, 1.5),
    ('float', 'Blendl', 'Edge blend left', 0.0, 0.0, 0.5), ('float', 'Blendr', 'Edge blend right', 0.0, 0.0, 0.5),
    ('float', 'Blendt', 'Edge blend top', 0.0, 0.0, 0.5), ('float', 'Blendb', 'Edge blend bottom', 0.0, 0.0, 0.5),
    ('float', 'Blendgamma', 'Blend curve gamma', 1.8, 0.5, 4.0),
    ('float', 'Opacity', 'Surface brightness', 1.0, 0.0, 2.0),
    ('float', 'Maskinset', 'Projection mask inset', 0.0, 0.0, 0.45),
    ('float', 'Maskfeather', 'Projection mask feather', 0.01, 0.0005, 0.3),
]


def make_surface(idx, defaults):
    s = mk(c, 'baseCOMP', 'surface_%d' % idx)
    s.nodeX, s.nodeY = 220 * idx, -300
    _pos[s.path] = 0
    page = s.appendCustomPage('Surface')
    for it in SURF_PARS:
        kind, name, label, default = it[0], it[1], it[2], it[3]
        default = defaults.get(name, default)
        p = (page.appendToggle(name, label=label) if kind == 'toggle' else page.appendFloat(name, label=label))[0]
        p.default = default
        p.val = default
        if kind == 'float':
            p.min, p.max = it[4], it[5]
            p.normMin, p.normMax = it[4], it[5]
    sin = mk(s, 'selectTOP', 'in')
    P(sin, top=src.path)
    crop = mk(s, 'cropTOP', 'crop')
    P(crop, cropleftunit='fraction', croprightunit='fraction', cropbottomunit='fraction', croptopunit='fraction')
    X(crop, cropleft="parent().par.Cropl", cropright="1 - parent().par.Cropr", cropbottom="parent().par.Cropb",
      croptop="1 - parent().par.Cropt")          # Crop TOP takes region positions, not margins
    wire(sin, crop)
    fit = mk(s, 'fitTOP', 'fit')
    P(fit, outputresolution='custom', fit='fill', format='rgba16float')
    X(fit, resolutionw=OW, resolutionh=OH)
    wire(crop, fit)
    cp = mk(s, 'cornerpinTOP', 'cornerpin')
    for corner in ('topleft', 'topright', 'botleft', 'botright'):
        P(cp, **{'pin%sunit' % corner: 'fraction'})
    X(cp, pintopleftx="parent().par.Tlx", pintoplefty="parent().par.Tly",
      pintoprightx="parent().par.Trx", pintoprighty="parent().par.Try",
      pinbotleftx="parent().par.Blx", pinbotlefty="parent().par.Bly",
      pinbotrightx="parent().par.Brx", pinbotrighty="parent().par.Bry")
    P(cp, outputresolution='custom', format='rgba16float')
    X(cp, resolutionw=OW, resolutionh=OH)
    wire(fit, cp)
    sp = glsl(s, 'edge_blend', 'surface_pass', inputs=[cp], res=(OW, OH), fmt='rgba16float', common=False)
    # surface-local uniforms
    P(sp, vec0name='uBlend', vec1name='uMask')
    X(sp, vec0valuex="parent().par.Blendl", vec0valuey="parent().par.Blendr", vec0valuez="parent().par.Blendt",
      vec0valuew="parent().par.Blendb", vec1valuex="parent().par.Blendgamma",
      vec1valuey="parent().par.Opacity * parent().par.Enable * %s" % ACTIVE_EXPR.format(idx=idx),
      vec1valuez="parent().par.Maskinset", vec1valuew="parent().par.Maskfeather")
    blk = mk(s, 'constantTOP', 'black')
    P(blk, colorr=0, colorg=0, colorb=0, alpha=1, outputresolution='custom', format='rgba16float')
    X(blk, resolutionw=OW, resolutionh=OH)
    o = mk(s, 'switchTOP', 'OUT')            # a disabled surface costs nothing : its branch is never cooked
    X(o, index="1 if (parent().par.Enable and %s) else 0" % ACTIVE_EXPR.format(idx=idx))
    wire(blk, o, 0)
    wire(sp, o, 1)
    return s


ACTIVE_EXPR = "(1 if (%s.eval() == 'surfaces' or {idx} == 1) else 0)" % C('Mappingmode')
s1 = make_surface(1, {})
s2 = make_surface(2, {'Enable': 0, 'Cropl': 0.0, 'Cropr': 0.5})
s3 = make_surface(3, {'Enable': 0, 'Cropl': 0.5, 'Cropr': 0.0})
for s in (s1, s2, s3):
    try:
        s.par.Enable.val = 1 if s is s1 else 0
    except Exception:
        pass

# the surface TOPs live in separate COMPs -> pull them in with Select TOPs, then sum them
sels = []
for s in (s1, s2, s3):
    sels.append(sel(c, 'out_' + s.name, s.path + '/OUT'))
sm = mk(c, 'compositeTOP', 'surfaces_sum')
P(sm, operand='add')
for i, t_ in enumerate(sels):
    wire(t_, sm, i)

# ---- Kantan Mapper (palette component) as the "free-form" mapping alternative
kantan_src = None
tox = (app.paletteFolder + '/Mapping/kantanMapper.tox') if True else ''
cands = [tox, app.paletteFolder + '/Mapping/kantanMapper/kantanMapper.tox']
kp = None
for cand in cands:
    if os.path.exists(cand):
        kp = cand
        break
if kp is None:
    import glob
    g = glob.glob(app.paletteFolder + '/**/kantanMapper.tox', recursive=True)
    kp = g[0] if g else None
kantan_top = None
if kp:
    try:
        k = c.loadTox(kp)
        k.name = 'kantan_mapper'
        k.nodeX, k.nodeY = 900, -300
        kantan_top = sel(c, 'kantan_out', k.path + '/kantanMapper/out1')
        WARN.append('kantan loaded from %s' % kp)
    except Exception as e:
        WARN.append('kantan load failed: %s' % e)
else:
    WARN.append('kantanMapper.tox not found in palette')

sw = mk(c, 'switchTOP', 'mapping_switch')
X(sw, index="1 if %s.eval() == 'kantan' else 0" % C('Mappingmode'))
wire(sm, sw, 0)
if kantan_top is not None:
    wire(kantan_top, sw, 1)
else:
    wire(sm, sw, 1)

grade = glsl(c, 'final_grade', 'final_grade', inputs=[sw], res=(OW, OH), fmt='rgba16float', uni=uni)
null(c, 'OUT_PROJECTION', grade)
log('projection built')
