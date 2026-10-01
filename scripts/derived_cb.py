# Script CHOP  TRACKING_DATA/derived  -  gesture + motion features computed from the SMOOTHED tracking channels
# input 0 : smoothed positions (Filter -> Lag -> Math)      input 1 : Speed CHOP (channels suffixed _v, units per second)
import math
ROOT = '__ROOT__'
_S = {'energy': 0.0, 'vel': 0.0, 'prev_t': None, 'burst_hand': (0.5, 0.5), 'still': 0.0}


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a if b != a else 1e-6)))
    return t * t * (3 - 2 * t)


def onCook(scriptOp):
    scriptOp.isTimeSlice = False
    scriptOp.clear()
    scriptOp.numSamples = 1
    P = scriptOp.inputs[0]
    V = scriptOp.inputs[1] if len(scriptOp.inputs) > 1 else None
    ctl = op(ROOT + '/CONTROL_DASHBOARD')
    sens = float(ctl.par.Motionsens.eval())
    asp = 16.0 / 9.0
    now = absTime.seconds
    dt = 1 / 60.0 if _S['prev_t'] is None else max(1e-3, min(0.2, now - _S['prev_t']))
    _S['prev_t'] = now

    def g(n, d=0.0):
        c = P[n] if P is not None else None
        return float(c[0]) if c is not None else d

    def v(n):
        c = V[n + '_v'] if V is not None else None
        return float(c[0]) if c is not None else 0.0

    lx, ly, rx, ry = g('hand_left_x'), g('hand_left_y'), g('hand_right_x'), g('hand_right_y')
    hx, hy = g('head_x'), g('head_y')
    present = g('present')
    hand_distance = math.hypot((lx - rx) * asp, ly - ry)
    above = min(sstep(0.03, 0.14, ly - hy), sstep(0.03, 0.14, ry - hy))
    sh = g('shoulder_y', 0.6)
    raised = 0.5 * (sstep(0.0, 0.25, ly - sh) + sstep(0.0, 0.25, ry - sh))
    touch = sstep(0.17, 0.045, hand_distance) * (1 - above) * (1 if present > 0.5 else 0)

    def spd(a, b):
        return math.hypot(v(a) * asp, v(b))

    sl = spd('hand_left_x', 'hand_left_y')
    sr = spd('hand_right_x', 'hand_right_y')
    sh_ = spd('head_x', 'head_y')
    st = spd('body_center_x', 'body_center_y')
    vel = (0.6 * 0.5 * (sl + sr) + 0.8 * (sh_ + st)) / 1.6 * sens
    vel = min(vel, 4.0)
    _S['vel'] += (vel - _S['vel']) * (1 - math.exp(-dt / 0.08))
    # motion energy : fast attack, slow release
    e = _S['energy']
    k = 0.10 if _S['vel'] > e else 0.9
    e += (_S['vel'] - e) * (1 - math.exp(-dt / k))
    _S['energy'] = e
    if sl >= sr:
        _S['burst_hand'] = (lx, ly)
    else:
        _S['burst_hand'] = (rx, ry)
    out = {
        'hand_distance': hand_distance, 'body_velocity': _S['vel'], 'motion_energy': e,
        'hands_above_head': above, 'raised_arms': raised, 'hands_touch': touch,
        'hand_speed_l': sl, 'hand_speed_r': sr, 'head_speed': sh_, 'torso_speed': st,
        'burst_x': _S['burst_hand'][0], 'burst_y': _S['burst_hand'][1],
        'hand_mid_x': 0.5 * (lx + rx), 'hand_mid_y': 0.5 * (ly + ry),
        'rot_rate': 0.9 * _S['vel'],
    }
    # forward everything from the smoothed bank too so one CHOP carries it all
    if P is not None:
        for c in P.chans():
            out.setdefault(c.name, float(c[0]))
    if V is not None:
        for c in V.chans():
            out.setdefault(c.name, float(c[0]))
    for kx, vx in out.items():
        scriptOp.appendChan(kx)[0] = float(vx)
