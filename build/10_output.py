# ====================================================================== FINAL_OUTPUT
c = container('FINAL_OUTPUT')
uni = sel_uni(c)
OW, OH = C('Outputw') + '.eval()', C('Outputh') + '.eval()'
proj = sel(c, 'in_projection', ROOT + '/PROJECTION_MAPPING/OUT_PROJECTION')
art = mk(c, 'fitTOP', 'output_resolution')
P(art, outputresolution='custom', fit='fill', format='rgba8fixed')
X(art, resolutionw=OW, resolutionh=OH)
wire(proj, art)

cvdbg = sel(c, 'in_cv_debug', ROOT + '/COMPUTER_VISION/CV_DEBUG')
skel = sel(c, 'in_skeleton', ROOT + '/COMPUTER_VISION/SKELETON_OVERLAY')
sil = sel(c, 'in_silhouette', ROOT + '/COMPUTER_VISION/SIL_MASK')

hud = mk(c, 'textTOP', 'hud_text')
P(hud, outputresolution='custom', resolutionw=1280, resolutionh=720, fontsizex=15, alignx='left', aligny='top',
  fontcolorr=0.85, fontcolorg=1.0, fontcolorb=1.0, bgalpha=0, format='rgba8fixed')
hud_mod = text_dat(c, 'hud_mod', read('scripts/hud_mod.py'))
X(hud, text="op('%s').module.hud()" % hud_mod.path)
hud_pad = mk(c, 'fitTOP', 'hud_fit')
P(hud_pad, outputresolution='custom', fit='fill', format='rgba8fixed')
X(hud_pad, resolutionw=OW, resolutionh=OH)
wire(hud, hud_pad)

# nothing below cooks unless its toggle is on (Switch TOPs only cook the selected input)
black = mk(c, 'constantTOP', 'black')
P(black, colorr=0, colorg=0, colorb=0, alpha=0, outputresolution='custom', resolutionw=16, resolutionh=9,
  format='rgba8fixed')


def gate(name, flag, src_top):
    g = mk(c, 'switchTOP', name)
    X(g, index="%s.eval()" % C(flag))
    wire(black, g, 0)
    wire(src_top, g, 1)
    return g


g_dbg = gate('gate_cv_debug', 'Cvdebug', cvdbg)
g_skel = gate('gate_skeleton', 'Skeleton', skel)
g_sil = gate('gate_silhouette', 'Silpreview', sil)
g_hud = gate('gate_hud', 'Cvdebug', hud_pad)
ov = glsl(c, 'debug_overlay', 'debug_overlay', inputs=[art, g_dbg, g_skel, g_sil, g_hud], res=(OW, OH),
          fmt='rgba8fixed', uni=uni)
ov_sw = mk(c, 'switchTOP', 'overlay_bypass')
X(ov_sw, index="1 if (%s.eval() or %s.eval() or %s.eval()) else 0" % (C('Cvdebug'), C('Skeleton'), C('Silpreview')))
wire(art, ov_sw, 0)
wire(ov, ov_sw, 1)
cal = glsl(c, 'calibration', 'calibration', res=(OW, OH), fmt='rgba8fixed', common=False)
sw = mk(c, 'switchTOP', 'calibration_switch')
X(sw, index=C('Calibration'))
wire(ov_sw, sw, 0)
wire(cal, sw, 1)
final = null(c, 'OUT_FINAL', sw)

# ---- projector window (borderless, on the selected monitor)
view = mk(c, 'containerCOMP', 'projector_view')
P(view, top=final.path, w=1920, h=1080, align='verttb') if False else P(view, top=final.path, w=1920, h=1080)
win = mk(c, 'windowCOMP', 'projector_window')
P(win, winop=view.path, borders=False, alwaysontop=False, cursorvisible=False, title='SACRED GEOMETRY - projector')
X(win, winw=OW, winh=OH)
try:
    WARN.append('window display menu: %r' % (win.par.display.menuNames if win.par.display.isMenu else win.par.display.eval()))
except Exception as e:
    WARN.append('window display: %s' % e)

# ---- performance-monitor friendly boundaries : one cheap Null per expensive stage, plus a live Perform CHOP
perf = mk(c, 'performCHOP', 'perf')
nul = null(c, 'OUT_PERF', perf, 'CHOP')
log('output built')
