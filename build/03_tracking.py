# ====================================================================== TRACKING_DATA  (+ state machine)
c = container('TRACKING_DATA')
raw = script_chop(c, 'tracking_raw', 'tracking_raw_cb.py')
null(c, 'RAW_TRACKING', raw, 'CHOP')

# smoothing so the graphics react organically:  Filter -> Lag -> Math
flt = mk(c, 'filterCHOP', 'sm_filter')
P(flt, type='gauss')
X(flt, width="0.01 + 0.22 * %s.eval()" % C('Smoothing'))
wire(raw, flt)
lag = mk(c, 'lagCHOP', 'sm_lag')
X(lag, lag1="0.02 + 0.45 * %s.eval()" % C('Smoothing'), lag2="0.03 + 0.70 * %s.eval()" % C('Smoothing'))
wire(flt, lag)
mth = mk(c, 'mathCHOP', 'sm_math')
P(mth, gain=1.0)
wire(lag, mth)
sm = null(c, 'SMOOTHED', mth, 'CHOP')

# velocity (units / second) is measured on the LIGHTLY filtered signal so quick gestures are not low-passed away,
# while the visuals follow the heavier Lag-smoothed positions
vel = mk(c, 'slopeCHOP', 'vel_slope')
wire(flt, vel)
P(vel, renamefrom='*', renameto='*_v')
velnull = null(c, 'VELOCITY', vel, 'CHOP')

# gesture / motion features
der = script_chop(c, 'derived', 'derived_cb.py')
wire(sm, der, 0)
wire(velnull, der, 1)

# Speed CHOP integrates body-velocity into a rotation phase (rotation rate follows how fast the body moves)
rs = mk(c, 'selectCHOP', 'rot_rate_sel')
P(rs, chops=der.path, channames='rot_rate')
wire(der, rs)
spd = mk(c, 'speedCHOP', 'rot_speed')
P(spd, renamefrom='rot_rate', renameto='vel_phase', limittype='loop', min=0.0, max=1000.0)
wire(rs, spd)

mg = mk(c, 'mergeCHOP', 'merge_tracking')
wire(der, mg, 0)
wire(spd, mg, 1)
null(c, 'OUT_TRACKING', mg, 'CHOP')

# ---------------------------------------------------------------- state machine
st = script_chop(c, 'state', 'state_cb.py')
null(c, 'OUT_STATE', st, 'CHOP')
log('tracking built')
