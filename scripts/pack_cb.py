# Script CHOP  GEOMETRY_ENGINE/uniform_pack  -  packs tracking + state + dashboard values into 48 vec4 "slots"
# (channels r g b a, 48 samples).  CHOP-to-TOP turns that into a 48x1 float texture that every shader reads.
# Slot layout is documented in shaders/common.glsl  (keep the two in sync).
import math
ROOT = '__ROOT__'
NSLOTS = 48
LAYERS = ['flower', 'metatron', 'yantra', 'fib', 'vesica', 'hex', 'mandala', 'fractal']
#              flower metatron yantra fib  vesica hex  mandala fractal
STATE_TABLE = [[0.90, 0.00, 0.00, 0.35, 0.00, 0.50, 0.90, 0.00],      # idle         slow rotating structure
               [0.80, 0.25, 0.25, 0.30, 0.30, 0.60, 0.70, 0.00],      # awaken
               [0.80, 0.90, 0.90, 0.50, 0.90, 0.60, 0.60, 0.35],      # interaction
               [1.00, 1.00, 1.00, 0.90, 0.90, 0.85, 1.00, 1.00],      # transcendence
               [1.00, 0.60, 0.70, 0.80, 0.50, 0.50, 1.00, 0.20],      # stillness
               [0.40, 0.00, 0.00, 0.20, 0.00, 0.40, 0.50, 0.00]]      # exit
GEO_SOLO = {'all': None, 'flower': 0, 'metatron': 1, 'yantra': 2, 'fib': 3, 'vesica': 4, 'hex': 5, 'mandala': 6,
            'fractal': 7}
M = dict(prev=None, rot=0.0, lw=[0.0] * 8, hue=0.0, aura=0.0, cam=[0.0, 0.0, 0.0], depth_s=0.5, tun=0.0, warp=0.0,
         sym=12.0)


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.isTimeSlice = False
    scriptOp.clear()
    for n in 'rgba':
        scriptOp.appendChan(n)
    scriptOp.numSamples = NSLOTS
    T = op(ROOT + '/TRACKING_DATA/OUT_TRACKING')
    S = op(ROOT + '/TRACKING_DATA/OUT_STATE')
    C = op(ROOT + '/CONTROL_DASHBOARD')
    asp = 16.0 / 9.0

    def t(n, d=0.0):
        c = T[n] if T is not None else None
        return float(c[0]) if c is not None else d

    def s(n, d=0.0):
        c = S[n] if S is not None else None
        return float(c[0]) if c is not None else d

    def c(n):
        return C.par[n].eval()

    vel_phase = t('vel_phase')
    if not math.isfinite(vel_phase):                         # self-heal the Speed CHOP integrator
        vel_phase = 0.0
        try:
            op(ROOT + '/TRACKING_DATA/rot_speed').par.resetpulse.pulse()
        except Exception:
            pass

    now = absTime.seconds
    dt = 1 / 60.0 if M['prev'] is None else max(1e-3, min(0.2, now - M['prev']))
    M['prev'] = now
    k1 = lambda tau: 1 - math.exp(-dt / tau)
    slots = [[0.0, 0.0, 0.0, 0.0] for _ in range(NSLOTS)]

    st = [s('idle'), s('awaken'), s('interaction'), s('transcend'), s('stillness'), s('exit')]
    order = s('order')
    energy = t('motion_energy')
    vel = t('body_velocity')
    hand_d = t('hand_distance')
    stillness = max(0.0, min(1.0, st[4] + 0.5 * order * (1 - energy)))

    # ---- tracking slots
    slots[0] = [t('hand_left_x', .36), t('hand_left_y', .48), t('hand_left_x_v'), t('hand_left_y_v')]
    slots[1] = [t('hand_right_x', .64), t('hand_right_y', .48), t('hand_right_x_v'), t('hand_right_y_v')]
    slots[2] = [t('head_x', .5), t('head_y', .7), t('head_x_v'), t('head_y_v')]
    slots[3] = [t('body_center_x', .5), t('body_center_y', .5), t('body_center_x_v'), t('body_center_y_v')]
    slots[4] = [t('bbox_minx', .4), t('bbox_miny', .1), t('bbox_maxx', .6), t('bbox_maxy', .9)]
    slots[5] = [hand_d, vel, energy, stillness]
    slots[6] = [t('depth', .5), s('present_s'), t('raised_arms'), t('hands_above_head')]
    slots[7] = [s('singularity'), s('crown'), s('burst'), now]
    slots[8] = st[:4]
    slots[9] = [st[4], st[5], order, s('afterimage')]

    # ---- geometry parameters (dashboard x state x body)
    raised = t('raised_arms')
    cplx = float(c('Complexity')) + 0.30 * raised + 0.20 * min(energy, 1.5) / 1.5 + 0.35 * st[3] - 0.10 * st[5]
    cplx = max(0.05, min(1.0, cplx))
    sym_t = float(c('Symmetry'))
    if order > 0.6:                                      # settle on an even, highly symmetric count
        sym_t = round(sym_t / 2.0) * 2.0
    M['sym'] += (sym_t - M['sym']) * k1(1.5)
    M['rot'] += dt * (float(c('Rotation')) * 0.6 * (1.0 - 0.8 * order) + 0.2 * st[3] + 0.03)
    M['hue'] += dt * float(c('Huespeed')) * (1.0 + 0.5 * energy)
    expand = 0.25 + hand_d * 1.15
    expand = expand * (1 - 0.25 * s('singularity'))
    rec = float(c('Recursion')) + 3.0 * min(energy, 1.5) / 1.5 + 2.0 * st[3]
    aura_mode = c('Mattemode')                           # body / aura / auto
    aura_t = {'body': 0.0, 'aura': 1.0}.get(aura_mode, min(1.0, 0.25 + 0.55 * st[1] + 0.45 * st[3] + 0.4 * st[5]))
    M['aura'] += (aura_t - M['aura']) * k1(1.0)
    awaken_grow = 0.35 + 0.65 * (1 - st[1] * 0.6)
    scale = float(c('Scale')) * (awaken_grow if st[1] > 0.01 else 1.0)
    slots[10] = [M['sym'], cplx, M['rot'] + vel_phase, scale]

    # layer weights
    solo = GEO_SOLO.get(c('Geotype'), None)
    target = [sum(st[i] * STATE_TABLE[i][j] for i in range(6)) for j in range(8)]
    if solo is not None:
        target = [1.0 if j == solo else 0.0 for j in range(8)]
    for j in range(8):
        M['lw'][j] += (target[j] - M['lw'][j]) * k1(1.2)
    lw = M['lw']
    slots[11] = [lw[0], lw[1], lw[2], lw[3]]
    slots[12] = [lw[4], lw[5], lw[6], lw[7]]
    quality = c('Quality')                               # performance / standard / high
    hq = {'performance': 0.0, 'standard': 0.0, 'high': 1.0}.get(quality, 0.0)
    slots[13] = [rec, M['aura'], 1.0 if quality == 'performance' else 0.0, expand]

    # ---- psychedelic
    fb = float(c('Feedbackamt')) + 0.05 * st[3] - 0.03 * order
    slots[14] = [min(0.985, fb), float(c('Feedbackrot')), float(c('Feedbackzoom')),
                 float(c('Displacement')) * (1 + 0.8 * min(energy, 1.5)) * (1 - 0.6 * order)]
    slots[15] = [float(c('Chroma')) * (1 + 0.5 * st[3]), float(c('Glow')) * (1 + 0.4 * st[3]),
                 float(c('Noiseint')) * (1 - 0.7 * order), M['hue']]

    # ---- particles
    slots[16] = [float(c('Particlecount')) / 65536.0 * {'performance': 0.35, 'standard': 0.85, 'high': 1.0}[quality], float(c('Particlevel')), float(c('Turbulence')) * (0.4 + min(energy, 1.5)),
                 float(c('Attraction'))]
    slots[17] = [float(c('Particledecay')), float(c('Particlesize')), order, s('burst')]

    # ---- projection / flags
    slots[18] = [float(c('Brightness')), float(c('Gamma')), float(c('Blacklevel')), float(c('Calibration'))]
    slots[19] = [float(c('Cvdebug')), float(c('Skeleton')), float(c('Silpreview')), 1.0 if quality == 'high' else 0.0]

    # ---- camera / depth illusion
    M['depth_s'] += (t('depth', .5) - M['depth_s']) * k1(0.6)
    dolly_t = (M['depth_s'] - 0.5) * 2.0 * float(c('Tunneldepth'))
    cx = (t('body_center_x', .5) - 0.5) * 2.0 * float(c('Parallax'))
    cy = (t('body_center_y', .5) - 0.5) * 2.0 * float(c('Parallax'))
    M['cam'][0] += (cx - M['cam'][0]) * k1(0.5)
    M['cam'][1] += (cy - M['cam'][1]) * k1(0.5)
    M['cam'][2] += (dolly_t - M['cam'][2]) * k1(0.7)
    M['tun'] += dt * (float(c('Tunnelspeed')) + 1.2 * vel + 0.6 * st[3] - 0.4 * order * 0.0)
    slots[20] = [M['cam'][0], M['cam'][1], M['cam'][2], M['tun']]
    slots[23] = [min(1.0, float(c('Kaleido')) * (0.35 + 0.65 * order) + 0.55 * st[3]), float(c('Fog')), 0.0, 0.0]
    slots[21] = [t('open_l', .5), t('open_r', .5), max(t('pinch_l'), t('pinch_r')), s('dissolve')]
    slots[40] = [min(max(dt, 1 / 120.0), 1 / 12.0), 1.0 / dt, 0.0, 0.0]
    slots[22] = [t('burst_x', .5), t('burst_y', .5), s('burst_fire'), s('burst_count')]

    # ---- joints for skeleton overlay / demo silhouette
    names = ['head', 'lsh', 'rsh', 'lel', 'rel', 'lwr', 'rwr', 'lhip', 'rhip', 'lkn', 'rkn', 'lan', 'ran']
    for i, n in enumerate(names):
        slots[24 + i] = [t('j_%s_x' % n, .5), t('j_%s_y' % n, .5), s('present_s'), 0.0]

    for i in range(NSLOTS):
        for ch, v in zip('rgba', slots[i]):
            scriptOp[ch][i] = v if math.isfinite(v) else 0.0
