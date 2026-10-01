# Script CHOP  TRACKING_DATA/tracking_raw  -  raw (unsmoothed) tracking channels in TouchDesigner uv coordinates
# (x 0..1 left->right of the mirrored picture, y 0..1 bottom->top).  Smoothing happens downstream in CHOPs.
import sys
ROOT = '__ROOT__'
SCRIPTS = r'__DIR__\scripts'
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import sgo_cv
import math

NEUTRAL = dict(
    conf=0.0, have_hands=0.0, open_l=0.5, open_r=0.5, pinch_l=0.0, pinch_r=0.0,
    head_x=0.5, head_y=0.70, hand_left_x=0.36, hand_left_y=0.48, hand_right_x=0.64, hand_right_y=0.48,
    body_center_x=0.5, body_center_y=0.50, shoulder_y=0.62, shoulder_w=0.15,
    bbox_minx=0.4, bbox_maxx=0.6, bbox_miny=0.1, bbox_maxy=0.9, depth=0.5)
JN = ['head', 'lsh', 'rsh', 'lel', 'rel', 'lwr', 'rwr', 'lhip', 'rhip', 'lkn', 'rkn', 'lan', 'ran']
_N = {'head': (0.5, 0.70), 'lsh': (0.43, 0.62), 'rsh': (0.57, 0.62), 'lel': (0.40, 0.52), 'rel': (0.60, 0.52),
      'lwr': (0.36, 0.48), 'rwr': (0.64, 0.48), 'lhip': (0.46, 0.40), 'rhip': (0.54, 0.40), 'lkn': (0.46, 0.24),
      'rkn': (0.54, 0.24), 'lan': (0.46, 0.08), 'ran': (0.54, 0.08)}
for k, (x, y) in _N.items():
    NEUTRAL['j_%s_x' % k], NEUTRAL['j_%s_y' % k] = x, y


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.isTimeSlice = False
    scriptOp.clear()
    scriptOp.numSamples = 1
    ctl = op(ROOT + '/CONTROL_DASHBOARD')
    RT = sgo_cv.RT
    t = absTime.seconds
    if bool(ctl.par.Demofreeze.eval()):
        t = float(ctl.par.Democlock.eval())              # frozen on a chosen moment of the choreography
    else:
        t = t + float(ctl.par.Democlock.eval())          # running, shifted by an offset (rehearsal)
    demo = bool(ctl.par.Demomode.eval())
    if demo:
        ch = sgo_cv.demo_channels(RT.tracker, t)
        if ch is not None:
            ch['depth'] = 0.5 + 0.28 * math.sin(t * 0.21)
        present = ch is not None
    else:
        snap = RT.worker.snapshot() if RT.worker is not None else None
        ch, present = RT.tracker.update(snap, t)
    out = dict(NEUTRAL)
    if ch:
        out.update(ch)
    out['present'] = 1.0 if present else 0.0
    out['cv_fps'] = float(RT.worker.snapshot().get('fps', 0.0)) if (RT.worker is not None and not demo) else 60.0
    for k, v in out.items():
        scriptOp.appendChan(k)[0] = float(v)
