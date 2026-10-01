# ====================================================================== FEEDBACK_SYSTEM
#   Feedback -> Transform (rotate + scale 1.001-1.01 about the head) -> Level (decay) -> HSV drift -> Displace
#   -> Composite (+ current psychedelic frame) -> Feedback          luminous geometric trails that slowly decay
c = container('FEEDBACK_SYSTEM')
UCH = ROOT + '/GEOMETRY_ENGINE/OUT_UNIFORM_CHOP'
RES = (C('Renderw') + '.eval()', C('Renderh') + '.eval()')
uni = sel_uni(c)
psy = sel(c, 'in_psy', ROOT + '/PSYCHEDELIC_EFFECTS/OUT_PSY')

init = mk(c, 'constantTOP', 'fb_init')
P(init, colorr=0, colorg=0, colorb=0, alpha=1, outputresolution='custom', format='rgba16float')
X(init, resolutionw=C('Renderw'), resolutionh=C('Renderh'))
fb = mk(c, 'feedbackTOP', 'fb_loop')
wire(init, fb)

xf = mk(c, 'transformTOP', 'fb_transform')
wire(fb, xf)
P(xf, punit='fraction')
X(xf, rotate="op('%s')['g'][14] * op('%s')['r'][40] * 60" % (UCH, UCH),
  sx="op('%s')['b'][14] ** (op('%s')['r'][40] * 60)" % (UCH, UCH), sy="op('%s')['b'][14] ** (op('%s')['r'][40] * 60)" % (UCH, UCH),
  px="op('%s')['r'][2]" % UCH, py="op('%s')['g'][2]" % UCH)
P(xf, extend='zero')

dec = mk(c, 'levelTOP', 'fb_decay')
X(dec, brightness1="op('%s')['r'][14] ** (op('%s')['r'][40] * 60)" % (UCH, UCH))
wire(xf, dec)
hue = mk(c, 'hsvadjustTOP', 'fb_hue')
P(hue, hueoffset=0.004, saturationmult=1.02)
wire(dec, hue)
dnoise = mk(c, 'noiseTOP', 'fb_noise')
P(dnoise, period=1.0, harmon=2, outputresolution='custom', resolutionw=480, resolutionh=270, format='rgba16float', mono=True)
X(dnoise, tz="absTime.seconds * 0.11 + 7")
disp = mk(c, 'displaceTOP', 'fb_displace')
wire(hue, disp, 0)
wire(dnoise, disp, 1)
X(disp, displaceweightx="op('%s')['a'][14] * 0.0009" % UCH, displaceweighty="op('%s')['a'][14] * 0.0009" % UCH)
acc = mk(c, 'compositeTOP', 'fb_accumulate')
P(acc, operand='maximum')           # lighten: trails persist and fade without runaway brightness
wire(psy, acc, 0)
wire(disp, acc, 1)
P(fb, top=acc.path)
fbn = null(c, 'FB_ACCUM', acc)

tone = glsl(c, 'feedback_out', 'tonemap', inputs=[psy, fbn], res=RES, uni=uni)
null(c, 'OUT_FEEDBACK', tone)
log('feedback built')
