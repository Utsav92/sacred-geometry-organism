# Module DAT : text for the operator HUD (shown with CV debug view)
ROOT = '__ROOT__'
NAMES = ['IDLE', 'AWAKEN', 'INTERACTION', 'TRANSCENDENCE', 'STILLNESS', 'EXIT']


def hud():
    T = op(ROOT + '/TRACKING_DATA/OUT_TRACKING')
    S = op(ROOT + '/TRACKING_DATA/OUT_STATE')
    P = op(ROOT + '/FINAL_OUTPUT/OUT_PERF')
    if T is None or S is None:
        return ''
    try:
        import sgo_cv
        w = sgo_cv.RT.worker
        backend = w.backend if w is not None else 'demo performer'
        err = (' | ' + w.err) if (w is not None and w.err) else ''
    except Exception:
        backend, err = '?', ''
    st = NAMES[int(S['state_id'][0]) % 6]
    lines = [
        'STATE  %s   (t=%.1fs)' % (st, S['t_state'][0]),
        'present %d   energy %.2f   velocity %.2f' % (T['present'][0], T['motion_energy'][0], T['body_velocity'][0]),
        'hand distance %.2f   order %.2f   crown %.2f   singularity %.2f' % (
            T['hand_distance'][0], S['order'][0], S['crown'][0], S['singularity'][0]),
        'tracking: %s   cv fps %.0f%s' % (backend, T['cv_fps'][0], err),
    ]
    return '\n'.join(lines)
