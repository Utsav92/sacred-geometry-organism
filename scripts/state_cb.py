# Script CHOP  STATE_MACHINE/state  -  IDLE / AWAKEN / INTERACTION / TRANSCENDENCE / STILLNESS / EXIT
# Every state is a continuous WEIGHT (never a hard switch); transitions glide through one-pole smoothing.
import math
ROOT = '__ROOT__'
NAMES = ['idle', 'awaken', 'interaction', 'transcend', 'stillness', 'exit']
S = dict(state=0, t_state=0.0, prev=None, w=[1, 0, 0, 0, 0, 0], t_present=0.0, t_absent=9.0, t_still=0.0,
         t_active=0.0, t_above=0.0, t_calm=0.0, order=0.9, sing=0.0, crown=0.0, burst=0.0, burst_cool=0.0,
         pres_s=0.0, dissolve=0.0, burst_n=0.0, afterimg=0.0)


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.isTimeSlice = False
    scriptOp.clear()
    scriptOp.numSamples = 1
    D = op(ROOT + '/TRACKING_DATA/OUT_TRACKING')
    ctl = op(ROOT + '/CONTROL_DASHBOARD')

    def g(n, d=0.0):
        c = D[n] if D is not None else None
        return float(c[0]) if c is not None else d

    now = absTime.seconds
    dt = 1 / 60.0 if S['prev'] is None else max(1e-3, min(0.2, now - S['prev']))
    S['prev'] = now
    present = g('present') > 0.5
    energy = g('motion_energy')
    vel = g('body_velocity')
    above = g('hands_above_head')
    touch = g('hands_touch')

    # ------------------------------------------------------------ timers
    S['t_present'] = S['t_present'] + dt if present else 0.0
    S['t_absent'] = 0.0 if present else S['t_absent'] + dt
    S['t_still'] = S['t_still'] + dt if (present and energy < 0.14) else 0.0
    S['t_active'] = S['t_active'] + dt if energy > 0.9 else 0.0
    S['t_calm'] = S['t_calm'] + dt if energy < 0.45 else 0.0
    S['t_above'] = S['t_above'] + dt if above > 0.7 else 0.0
    S['t_state'] += dt
    s = S['state']
    new = s
    if s in (1, 2, 3, 4) and S['t_absent'] > 1.2:
        new = 5
    elif s == 0:
        if S['t_present'] > 0.4:
            new = 1
    elif s == 1:
        if S['t_state'] > 3.0:
            new = 2
    elif s == 2:
        if S['t_above'] > 1.0 or S['t_active'] > 2.5:
            new = 3
        elif S['t_still'] > 2.5:
            new = 4
    elif s == 3:
        if S['t_state'] > 7.0 and S['t_above'] < 0.1 and S['t_calm'] > 2.0:
            new = 2
        elif S['t_state'] > 4.0 and S['t_still'] > 3.0:
            new = 4
    elif s == 4:
        if energy > 0.5 or touch > 0.5 or above > 0.7:
            new = 2
    elif s == 5:
        if S['t_present'] > 0.6:
            new = 1
        elif S['t_state'] > 7.0:
            new = 0
    lock = ctl.par.Statelock.eval()          # menu : auto idle awaken interaction transcend stillness exit
    if lock != 'auto':
        new = NAMES.index(lock) if lock in NAMES else new
    if new != s:
        S['state'], S['t_state'] = new, 0.0

    # ------------------------------------------------------------ continuous weights
    tgt = [0.0] * 6
    tgt[S['state']] = 1.0
    for i in range(6):
        tau = 1.1 if tgt[i] > S['w'][i] else 1.8
        S['w'][i] += (tgt[i] - S['w'][i]) * (1 - math.exp(-dt / tau))
    tot = sum(S['w']) or 1.0
    w = [x / tot for x in S['w']]

    # ------------------------------------------------------------ order (stillness -> perfect symmetry)
    ord_t = 0.92 * w[0] + 0.30 * w[1] + 0.22 * w[2] + 0.0 * w[3] + 1.0 * w[4] + 0.5 * w[5]
    if S['state'] == 4:
        tau = 5.0
    elif S['state'] == 0:
        tau = 2.5
    else:
        tau = 0.8 if ord_t < S['order'] else 3.0
    S['order'] += (ord_t - S['order']) * (1 - math.exp(-dt / tau))

    # ------------------------------------------------------------ gesture envelopes
    def env(key, target, up, down):
        S[key] += (target - S[key]) * (1 - math.exp(-dt / (up if target > S[key] else down)))
        return S[key]
    sing = env('sing', touch, 0.45, 1.1)
    crown = env('crown', 1.0 if (above > 0.7 and present) else 0.0, 0.7, 1.6)
    S['pres_s'] += ((1.0 if present else 0.0) - S['pres_s']) * (1 - math.exp(-dt / 0.35))

    # burst : rapid movement -> explosion envelope (with refractory period)
    S['burst_cool'] = max(0.0, S['burst_cool'] - dt)
    fire = 0.0
    if vel > 0.95 and S['burst_cool'] <= 0.0 and present:
        S['burst'] = 1.0
        S['burst_cool'] = 0.45
        S['burst_n'] += 1.0
        fire = 1.0
    S['burst'] = max(0.0, S['burst'] - dt / 1.4)

    # exit dissolve + afterimage
    if S['state'] == 5:
        S['dissolve'] = min(1.0, S['t_state'] / 6.5)
    else:
        S['dissolve'] += (0.0 - S['dissolve']) * (1 - math.exp(-dt / 0.5))
    afterimage = w[5]

    out = dict(idle=w[0], awaken=w[1], interaction=w[2], transcend=w[3], stillness=w[4], exit=w[5],
               state_id=float(S['state']), order=S['order'], singularity=sing, crown=crown, burst=S['burst'],
               burst_fire=fire, burst_count=S['burst_n'], present_s=S['pres_s'], dissolve=S['dissolve'],
               afterimage=afterimage, t_state=S['t_state'], t_still=S['t_still'])
    for k, v in out.items():
        scriptOp.appendChan(k)[0] = float(v)
