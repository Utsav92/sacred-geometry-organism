# ====================================================================== CAMERA_INPUT + COMPUTER_VISION
# ---------------------------------------------------------------- CAMERA_INPUT
c = container('CAMERA_INPUT')
cam = mk(c, 'videodeviceinTOP', 'cam')
X(cam, active="1 - %s.eval()" % C('Demomode'))
cam_fit = mk(c, 'fitTOP', 'cam_fit')
P(cam_fit, outputresolution='custom', resolutionw=1280, resolutionh=720, fit='fill')
wire(cam, cam_fit)
cam_flip = mk(c, 'flipTOP', 'cam_flip')
X(cam_flip, flipx="%s.eval()" % C('Mirror'))
wire(cam_fit, cam_flip)
demo_view_sel = sel(c, 'demo_view', ROOT + '/COMPUTER_VISION/demo_view')
cam_sw = mk(c, 'switchTOP', 'cam_switch')
X(cam_sw, index="%s.eval()" % C('Demomode'))
wire(cam_flip, cam_sw, 0)
wire(demo_view_sel, cam_sw, 1)
null(c, 'OUT_CAMERA', cam_sw)

# ---------------------------------------------------------------- COMPUTER_VISION
c = container('COMPUTER_VISION')
uni = sel_uni(c)
demo_body = glsl(c, 'demo_body', 'demo_body', res=(640, 360), fmt='rgba8fixed', uni=uni, defines={'VIEW': 0})
demo_view = glsl(c, 'demo_view', 'demo_body', res=(1280, 720), fmt='rgba8fixed', uni=uni, defines={'VIEW': 1})

cv_in = sel(c, 'cv_in', ROOT + '/CAMERA_INPUT/OUT_CAMERA')
cv_frame = mk(c, 'fitTOP', 'cv_frame')
P(cv_frame, outputresolution='custom', resolutionw=640, resolutionh=360, fit='fill', format='rgba8fixed')
wire(cv_in, cv_frame)

mask_script = script_top(c, 'mask_script', 'mask_top_cb.py')
sil_sw = mk(c, 'switchTOP', 'sil_source')
X(sil_sw, index="%s.eval()" % C('Demomode'))
wire(mask_script, sil_sw, 0)
wire(demo_body, sil_sw, 1)

# camera -> segmentation -> threshold -> blur -> edge -> silhouette mask
thr = mk(c, 'thresholdTOP', 'sil_threshold')
P(thr, comparator='less')            # TD: white where the pixel is above the threshold
X(thr, threshold="%s.eval()" % C('Silthreshold'), soften="%s.eval() * 0.5" % C('Silsoft'))
wire(sil_sw, thr)
blur = mk(c, 'blurTOP', 'sil_blur')
X(blur, size="%s.eval()" % C('Silblur'))
wire(thr, blur)
lvl = mk(c, 'levelTOP', 'sil_level')
P(lvl, inlow=0.3, inhigh=0.7)
wire(blur, lvl)
sil_mask = null(c, 'SIL_MASK', lvl)

# afterimage : the last silhouette persists (feedback loop) and erodes while the EXIT dissolve runs
hold_fb = mk(c, 'feedbackTOP', 'hold_fb')
hold_init = mk(c, 'constantTOP', 'hold_init')
P(hold_init, colorr=0, colorg=0, colorb=0, alpha=1, outputresolution='custom', resolutionw=640, resolutionh=360,
  format='rgba16float')
wire(hold_init, hold_fb)
hold_step = glsl(c, 'hold_step', 'sil_hold', inputs=[hold_fb, sil_mask], res=(640, 360), fmt='rgba16float', uni=uni)
P(hold_fb, top=hold_step.path)
sil_held = null(c, 'SIL_HELD', hold_step)

# luminous contour + halo come from the HELD silhouette, so the geometric afterimage persists after exit
edge = mk(c, 'edgeTOP', 'sil_edge')
P(edge, strength=2.0)
wire(sil_held, edge)
eb = mk(c, 'blurTOP', 'sil_edge_blur')
P(eb, size=1.5)
wire(edge, eb)
el = mk(c, 'levelTOP', 'sil_edge_level')
P(el, brightness1=2.2, contrast=1.3)
wire(eb, el)
null(c, 'SIL_CONTOUR', el)

halo = mk(c, 'blurTOP', 'sil_halo_blur')
P(halo, size=70)
wire(sil_held, halo)
hl_ = mk(c, 'levelTOP', 'sil_halo_level')
P(hl_, brightness1=1.8)
wire(halo, hl_)
null(c, 'SIL_HALO', hl_)

skel = glsl(c, 'skeleton', 'skeleton', res=(1280, 720), fmt='rgba8fixed', uni=uni)
null(c, 'SKELETON_OVERLAY', skel)

dbg = glsl(c, 'cv_debug', 'cv_debug', inputs=[cv_frame, sil_mask, op(c.path + '/SIL_CONTOUR'), skel],
           res=(1280, 720), fmt='rgba8fixed', uni=uni)
null(c, 'CV_DEBUG', dbg)

tick = mk(c, 'executeDAT', 'tick')
tick.text = read('scripts/tick_exec.py')
P(tick, framestart=True, active=True)
log('camera_cv built')
