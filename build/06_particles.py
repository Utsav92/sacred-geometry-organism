# ====================================================================== PARTICLE_ENGINE
c = container('PARTICLE_ENGINE')
uni = sel_uni(c)
SIM = 256

held = sel(c, 'held_mask', ROOT + '/COMPUTER_VISION/SIL_HELD')
init = mk(c, 'constantTOP', 'sim_init')
P(init, colorr=0, colorg=0, colorb=0, alpha=0, outputresolution='custom', resolutionw=SIM, resolutionh=SIM,
  format='rgba32float')
fb = mk(c, 'feedbackTOP', 'sim_fb')
wire(init, fb)
step = glsl(c, 'sim_step', 'sim', inputs=[fb, held], res=(SIM, SIM), fmt='rgba32float', uni=uni,
            defines={'FIXED_ASPECT': '1.7777778'}, filt='nearest')
P(fb, top=step.path)
null(c, 'OUT_SIM', step)

# GPU point cloud : Grid SOP in "points" mode (65,536 points) rendered by a GLSL MAT that reads the sim texture
geo = mk(c, 'geometryCOMP', 'geo_particles')
for ch in list(geo.children):
    ch.destroy()
grid = geo.create(T('gridSOP'), 'points')
P(grid, rows=SIM, cols=SIM, sizex=2.0, sizey=2.0)
conv = geo.create(T('convertSOP'), 'to_particles')          # mesh -> particle-system primitive (one point sprite each)
P(conv, fromtype='mesh', totype='part')
wire(grid, conv)
conv.display = True
conv.render = True

mat = mk(c, 'glslMAT', 'mat_particles')
vd = text_dat(c, 'particle_vertex', read('shaders/particle_vertex.glsl'))
pd = text_dat(c, 'particle_pixel', read('shaders/particle_pixel.glsl'))
P(mat, vdat=vd.path, pdat=pd.path)
P(mat, sampler0name='uSim', sampler0top=step.path, sampler1name='uUni', sampler1top=uni.path)
try:
    mat.seq.sampler.numBlocks = 2
    P(mat, sampler0name='uSim', sampler0top=step.path, sampler1name='uUni', sampler1top=uni.path)
except Exception as e:
    WARN.append('sampler seq: %s' % e)
P(mat, vec0name='uRes')
X(mat, vec0valuex=C('Renderw'), vec0valuey=C('Renderh'))
P(mat, blending=True, srcblend='one', destblend='one', depthtest=False, depthwriting=False)
P(geo, material=mat.path)

rp = mk(c, 'renderTOP', 'render_particles')
P(rp, camera=ROOT + '/GEOMETRY_ENGINE/scene3d/cam3d', geometry=geo.path, bgcolorr=0, bgcolorg=0, bgcolorb=0,
  bgcolora=0, outputresolution='custom', format='rgba16float')
X(rp, resolutionw=C('Renderw'), resolutionh=C('Renderh'),
  antialias="{'performance': 'aa1', 'standard': 'aa1', 'high': 'aa2'}[%s.eval()]" % C('Quality'))
null(c, 'OUT_PARTICLES', rp)
log('particles built')
