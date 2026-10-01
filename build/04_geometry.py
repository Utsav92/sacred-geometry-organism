# ====================================================================== GEOMETRY_ENGINE  (2D procedural systems)
c = container('GEOMETRY_ENGINE')
RES = (C('Renderw') + '.eval()', C('Renderh') + '.eval()')

pack = script_chop(c, 'uniform_pack', 'pack_cb.py')
null(c, 'OUT_UNIFORM_CHOP', pack, 'CHOP')
ct = mk(c, 'choptoTOP', 'uniform_tex')
P(ct, chop=pack.path, dataformat='rgba', layout='rowscropped', format='rgba32float', inputfiltertype='nearest',
  outputresolution='useinput')
X(ct, chop="'%s'" % pack.path) if False else None
uni_out = null(c, 'OUT_UNIFORMS', ct)
uni_local = uni_out

# three depth groups : 0 body-attached   1 head-centred radial   2 far field
gA = glsl(c, 'geo_near', 'geo', res=RES, uni=uni_local, defines={'GROUP': 0})
gB = glsl(c, 'geo_mid', 'geo', res=RES, uni=uni_local, defines={'GROUP': 1})
HALF = (C('Renderw') + '.eval() / 2', C('Renderh') + '.eval() / 2')      # soft background layer : half-res is plenty
gC = glsl(c, 'geo_far', 'geo', res=HALF, uni=uni_local, defines={'GROUP': 2})
null(c, 'OUT_GEO_NEAR', gA)
null(c, 'OUT_GEO_MID', gB)
null(c, 'OUT_GEO_FAR', gC)
log('geometry built')
