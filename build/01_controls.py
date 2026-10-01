# ====================================================================== CONTROL_DASHBOARD
c = container('CONTROL_DASHBOARD')
c.destroyCustomPars()

GEO_NAMES = ['all', 'flower', 'metatron', 'yantra', 'fib', 'vesica', 'hex', 'mandala', 'fractal']
GEO_LABELS = ['All (state driven)', 'Flower of Life', "Metatron's Cube", 'Sri Yantra', 'Fibonacci', 'Vesica Piscis',
              'Hexagonal Lattice', 'Radial Mandala', 'Recursive Fractal']
PAGES = [
    ('System', [
        ('toggle', 'Demomode', 'Demo performer (no camera needed)', 1),
        ('toggle', 'Mirror', 'Mirror camera', 1),
        ('toggle', 'Demofreeze', 'Demo: manual clock', 0),
        ('float', 'Democlock', 'Demo: clock / offset (s)', 0.0, -3600.0, 3600.0),
        ('menu', 'Quality', 'Quality mode', 'standard', ['performance', 'standard', 'high'],
         ['Performance (960x540)', 'Standard (1280x720)', 'High quality (1920x1080)']),
        ('menu', 'Statelock', 'State override', 'auto', ['auto', 'idle', 'awaken', 'interaction', 'transcend',
                                                      'stillness', 'exit'],
         ['Auto (state machine)', 'IDLE', 'AWAKEN', 'INTERACTION', 'TRANSCENDENCE', 'STILLNESS', 'EXIT']),
        ('toggle', 'Cvdebug', 'CV debug view', 0),
        ('toggle', 'Skeleton', 'Skeleton overlay', 0),
        ('toggle', 'Silpreview', 'Silhouette preview', 0),
        ('toggle', 'Calibration', 'Projection calibration pattern', 0),
        ('float', 'Motionsens', 'Motion sensitivity', 1.0, 0.1, 5.0),
        ('pulse', 'Resetfeedback', 'Reset feedback'),
        ('pulse', 'Recalibrate', 'Recalibrate tracking'),
        ('pulse', 'Openprojector', 'Open projector window'),
        ('pulse', 'Opendashboard', 'Open dashboard window'),
        ('pulse', 'Openkantan', 'Open Kantan Mapper editor')]),
    ('CV', [
        ('menu', 'Cvbackend', 'Tracking backend', 'auto', ['auto', 'mediapipe', 'opencv'],
         ['Auto', 'MediaPipe (pose + hands)', 'OpenCV silhouette only']),
        ('float', 'Smoothing', 'Tracking smoothing', 0.5, 0.0, 1.0),
        ('float', 'Detectconf', 'Detection confidence', 0.5, 0.1, 0.95),
        ('float', 'Silthreshold', 'Silhouette threshold', 0.45, 0.0, 1.0),
        ('float', 'Silblur', 'Silhouette blur (px)', 3.0, 0.0, 24.0),
        ('float', 'Silsoft', 'Silhouette softness', 0.18, 0.01, 0.6),
        ('int', 'Cvrate', 'Analysis rate (fps)', 30, 5, 60)]),
    ('Geometry', [
        ('menu', 'Geotype', 'Geometry type', 'all', GEO_NAMES, GEO_LABELS),
        ('int', 'Symmetry', 'Symmetry count', 12, 3, 48),
        ('float', 'Complexity', 'Complexity', 0.55, 0.0, 1.0),
        ('float', 'Rotation', 'Rotation speed', 0.35, 0.0, 3.0),
        ('float', 'Scale', 'Scale', 1.0, 0.3, 2.5),
        ('int', 'Recursion', 'Recursion depth', 5, 2, 10),
        ('menu', 'Mattemode', 'Silhouette mode', 'auto', ['auto', 'body', 'aura'],
         ['Auto (state driven)', 'BODY (geometry inside silhouette)', 'AURA (geometry radiates outward)'])]),
    ('Psychedelic', [
        ('float', 'Feedbackamt', 'Feedback amount', 0.90, 0.0, 0.985),
        ('float', 'Feedbackrot', 'Feedback rotation (deg/frame)', 0.35, -4.0, 4.0),
        ('float', 'Feedbackzoom', 'Feedback zoom', 1.004, 0.98, 1.02),
        ('float', 'Displacement', 'Displacement', 0.35, 0.0, 2.0),
        ('float', 'Chroma', 'Chromatic separation', 0.6, 0.0, 3.0),
        ('float', 'Glow', 'Glow', 0.8, 0.0, 3.0),
        ('float', 'Noiseint', 'Noise intensity', 0.45, 0.0, 2.0),
        ('float', 'Huespeed', 'Hue drift speed', 0.04, 0.0, 0.5),
        ('float', 'Kaleido', 'Kaleidoscope amount', 0.35, 0.0, 1.0)]),
    ('Particles', [
        ('int', 'Particlecount', 'Particle count', 40000, 1000, 65536),
        ('float', 'Particlevel', 'Velocity', 1.0, 0.0, 4.0),
        ('float', 'Turbulence', 'Turbulence', 0.6, 0.0, 3.0),
        ('float', 'Attraction', 'Attraction strength', 1.0, 0.0, 4.0),
        ('float', 'Particledecay', 'Particle lifetime / decay (s)', 4.0, 0.5, 12.0),
        ('float', 'Particlesize', 'Particle size', 1.0, 0.2, 4.0)]),
    ('Depth', [
        ('float', 'Tunnelspeed', 'Tunnel speed', 0.25, 0.0, 3.0),
        ('float', 'Tunneldepth', 'Tunnel dolly (forward = deeper)', 1.0, 0.0, 3.0),
        ('float', 'Parallax', 'Parallax strength', 0.35, 0.0, 1.5),
        ('float', 'Fog', 'Depth fog', 0.55, 0.0, 2.0)]),
    ('Projection', [
        ('float', 'Brightness', 'Brightness', 1.0, 0.0, 2.0),
        ('float', 'Gamma', 'Gamma', 1.0, 0.3, 3.0),
        ('float', 'Blacklevel', 'Black level', 0.0, 0.0, 0.5),
        ('int', 'Outputw', 'Output width', 1920, 320, 7680),
        ('int', 'Outputh', 'Output height', 1080, 180, 4320),
        ('menu', 'Mappingmode', 'Mapping mode', 'cornerpin', ['cornerpin', 'surfaces', 'kantan'],
         ['Corner pin (rectangular wall)', 'Multi-surface (architectural)', 'Kantan Mapper']),
        ('int', 'Monitor', 'Projector monitor index', 1, 0, 8)]),
]

for page_name, items in PAGES:
    page = c.appendCustomPage(page_name)
    for it in items:
        kind, name, label, default = it[0], it[1], it[2], (it[3] if len(it) > 3 else None)
        try:
            if kind == 'pulse':
                page.appendPulse(name, label=label)
                continue
            if kind == 'float':
                p = page.appendFloat(name, label=label)[0]
            elif kind == 'int':
                p = page.appendInt(name, label=label)[0]
            elif kind == 'toggle':
                p = page.appendToggle(name, label=label)[0]
            elif kind == 'menu':
                p = page.appendMenu(name, label=label)[0]
                p.menuNames = it[4]
                p.menuLabels = it[5]
            p.default = default
            p.val = default
            if kind in ('float', 'int'):
                p.min, p.max = it[4], it[5]
                p.normMin, p.normMax = it[4], it[5]
                p.clampMin = p.clampMax = True
        except Exception as e:
            WARN.append('custom par %s: %s' % (name, e))

# render resolution follows the quality mode
page = c.appendCustomPage('Derived')
for nm, lab in (('Renderw', 'Render width'), ('Renderh', 'Render height')):
    p = page.appendInt(nm, label=lab)[0]
    p.readOnly = True
X(c, Renderw="{'performance': 960, 'standard': 1280, 'high': 1920}[me.par.Quality.eval()]",
  Renderh="{'performance': 540, 'standard': 720, 'high': 1080}[me.par.Quality.eval()]")

# ---- pulse / change callbacks
cb = '''
ROOT = '%s'
def onPulse(par):
    n = par.name
    if n == 'Resetfeedback':
        for p in (ROOT + '/FEEDBACK_SYSTEM/fb_loop', ROOT + '/COMPUTER_VISION/hold_fb', ROOT + '/PARTICLE_ENGINE/sim_fb'):
            o = op(p)
            if o is not None:
                try: o.par.resetpulse.pulse()
                except Exception: pass
    elif n == 'Recalibrate':
        import sgo_cv
        sgo_cv.RT.recalibrate()
    elif n == 'Openprojector':
        w = op(ROOT + '/FINAL_OUTPUT/projector_window')
        if w is not None:
            w.par.winopen.pulse()
    elif n == 'Openkantan':
        k = op(ROOT + '/PROJECTION_MAPPING/kantan_mapper/kantanMapper')
        if k is not None:
            k.par.Open.pulse()
    elif n == 'Opendashboard':
        w = op(ROOT + '/CONTROL_DASHBOARD/dashboard_window')
        if w is not None:
            w.par.winopen.pulse()
    return

def onValueChange(par, prev):
    return
''' % ROOT
pe = mk(c, 'parameterexecuteDAT', 'par_exec')
pe.text = cb
P(pe, op=c.path, pars='Resetfeedback Recalibrate Openprojector Opendashboard Openkantan', valuechange=False, onpulse=True)

# ---- on-screen parameter panel + window
ui = mk(c, 'parameterCOMP', 'dashboard_ui')
P(ui, op=c.path, builtin=False, custom=True)
P(ui, w=620, h=1000)
win = mk(c, 'windowCOMP', 'dashboard_window')
P(win, winop=ui.path, title='SACRED GEOMETRY ORGANISM - controls', winw=640, winh=900, borders=True)
log('controls built: %d custom pars' % len([p for p in c.customPars]))

# ---- autostart : make sure the timeline runs when the saved project is opened
su = mk(c, 'executeDAT', 'startup')
su.text = """def onStart():
    op('/').time.play = True
    return

def onCreate():
    op('/').time.play = True
    return
"""
P(su, start=True, create=True, active=True)
