# ====================================================================== PSYCHEDELIC_EFFECTS
c = container('PSYCHEDELIC_EFFECTS')
UCH = ROOT + '/GEOMETRY_ENGINE/OUT_UNIFORM_CHOP'
RES = (C('Renderw') + '.eval()', C('Renderh') + '.eval()')
uni = sel_uni(c)

s_scene = sel(c, 'in_scene3d', ROOT + '/GEOMETRY_ENGINE/OUT_SCENE3D')
s_part = sel(c, 'in_particles', ROOT + '/PARTICLE_ENGINE/OUT_PARTICLES')
s_held = sel(c, 'in_silhouette', ROOT + '/COMPUTER_VISION/SIL_HELD')
s_cont = sel(c, 'in_contour', ROOT + '/COMPUTER_VISION/SIL_CONTOUR')
s_halo = sel(c, 'in_halo', ROOT + '/COMPUTER_VISION/SIL_HALO')

comp = glsl(c, 'scene_composite', 'scene_comp', inputs=[s_scene, s_part, s_held, s_cont, s_halo], res=RES, uni=uni)
clean = null(c, 'CLEAN_SCENE', comp)

# ---- kaleidoscope-style recursive symmetry (head = centre of radial symmetry)
kal = glsl(c, 'kaleidoscope', 'kaleido', inputs=[clean], res=RES, uni=uni)

# ---- organic displacement field
noise = mk(c, 'noiseTOP', 'psy_noise')
try:
    WARN.append('noise type menu: %r' % (noise.par.type.menuNames,))
    P(noise, type='simplex3d' if 'simplex3d' in noise.par.type.menuNames else noise.par.type.menuNames[0])
except Exception as e:
    WARN.append('noise type: %s' % e)
P(noise, period=1.1, harmon=2, outputresolution='custom', resolutionw=480, resolutionh=270, format='rgba16float', mono=True)
X(noise, tz="absTime.seconds * 0.06",
  amp="0.4 + 0.6 * op('%s')['b'][15]" % UCH)
disp = mk(c, 'displaceTOP', 'psy_displace')
wire(kal, disp, 0)
wire(noise, disp, 1)
X(disp, displaceweightx="op('%s')['a'][14] * 0.0042" % UCH, displaceweighty="op('%s')['a'][14] * 0.0042" % UCH)

# ---- chromatic separation + diffraction ghosts
chroma = glsl(c, 'chromatic', 'chroma', inputs=[disp], res=RES, uni=uni)

# ---- iridescent gradient mapping : luminance -> spectral ramp (Lookup TOP), added back as thin-film colour
tbl = mk(c, 'tableDAT', 'iridescent_stops')
tbl.text = ('pos\tr\tg\tb\ta\n0\t0.02\t0.0\t0.10\t1\n0.15\t0.10\t0.05\t0.55\t1\n0.30\t0.0\t0.55\t0.95\t1\n'
            '0.45\t0.05\t0.95\t0.55\t1\n0.60\t0.90\t0.95\t0.20\t1\n0.75\t1.0\t0.45\t0.15\t1\n'
            '0.88\t0.95\t0.15\t0.65\t1\n1\t1.0\t0.85\t1.0\t1\n')
ramp = mk(c, 'rampTOP', 'iridescent_ramp')
P(ramp, type='horizontal', dat=tbl.path, outputresolution='custom', resolutionw=256, resolutionh=1,
  format='rgba16float')
luma = mk(c, 'monochromeTOP', 'luma')
wire(chroma, luma)
lev_l = mk(c, 'levelTOP', 'luma_boost')
P(lev_l, brightness1=1.0, clamp=True) if False else P(lev_l, brightness1=0.9)
wire(luma, lev_l)
look = mk(c, 'lookupTOP', 'iridescence_lookup')
wire(lev_l, look, 0)
wire(ramp, look, 1)
irid_lvl = mk(c, 'levelTOP', 'iridescence_amount')
X(irid_lvl, brightness1="0.10 + 0.16 * op('%s')['g'][15] / 2.0" % UCH)
wire(look, irid_lvl)
irid_mask = mk(c, 'multiplyTOP', 'iridescence_masked')       # colour only where there is light
wire(irid_lvl, irid_mask, 0)
wire(lev_l, irid_mask, 1)
irid_add = mk(c, 'compositeTOP', 'iridescence_add')
P(irid_add, operand='add')
wire(chroma, irid_add, 0)
wire(irid_mask, irid_add, 1)

PERF = "0 if %s.eval() == 'performance' else 1" % C('Quality')
irid_sw = mk(c, 'switchTOP', 'iridescence_bypass')      # performance mode skips the 6-pass iridescence branch
X(irid_sw, index=PERF)
wire(chroma, irid_sw, 0)
wire(irid_add, irid_sw, 1)

# ---- hue drift / saturation / levels
hsv = mk(c, 'hsvadjustTOP', 'hue_drift')
X(hsv, hueoffset="op('%s')['a'][15] * 0.15" % UCH)
P(hsv, saturationmult=1.18)
wire(irid_sw, hsv)
lvl = mk(c, 'levelTOP', 'tone')
P(lvl, contrast=1.08)
wire(hsv, lvl)

# ---- glow
bloom = mk(c, 'bloomTOP', 'glow')
X(bloom, bloomintensity="op('%s')['g'][15] * 0.45" % UCH)
P(bloom, bloomthreshold=0.5)
wire(lvl, bloom)

# ---- edge enhancement keeps the sacred geometry readable under the processing
edge = mk(c, 'edgeTOP', 'structure_edge')
P(edge, strength=1.4)
wire(bloom, edge)
edge_l = mk(c, 'levelTOP', 'structure_edge_amount')
P(edge_l, brightness1=0.07)
wire(edge, edge_l)
fin = mk(c, 'compositeTOP', 'structure_add')
P(fin, operand='add')
wire(bloom, fin, 0)
wire(edge_l, fin, 1)
fx_sw = mk(c, 'switchTOP', 'glow_edge_bypass')          # performance mode skips bloom + edge enhancement
X(fx_sw, index=PERF)
wire(lvl, fx_sw, 0)
wire(fin, fx_sw, 1)
null(c, 'OUT_PSY', fx_sw)
log('psychedelic built')
