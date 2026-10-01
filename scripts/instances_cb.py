# Script CHOP : per-instance transforms for one 3D wireframe family.  Builder replaces __GROUP__ with
#   ring0 ring1 ring2  (infinite tunnel of polygons; 3 side-counts interleaved)   ico   torus
# Channels : tx ty tz  rx ry rz  sx sy sz  cr cg cb       (degrees / world units)
import math
ROOT = '__ROOT__'
GROUP = '__GROUP__'
ASP = 16.0 / 9.0


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def pal(t):
    return [0.5 + 0.5 * math.cos(6.2831853 * (t + o)) for o in (0.0, 0.33, 0.67)]


def onCook(scriptOp):
    scriptOp.isTimeSlice = False
    scriptOp.clear()
    for n in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'cr', 'cg', 'cb'):
        scriptOp.appendChan(n)
    U = op(ROOT + '/GEOMETRY_ENGINE/OUT_UNIFORM_CHOP')
    C = op(ROOT + '/CONTROL_DASHBOARD')
    if U is None:
        scriptOp.numSamples = 1
        return

    def s(slot, ch='r'):
        return float(U[ch][slot])
    T = s(7, 'a')
    tun = s(20, 'a')
    cam_x, cam_y = s(20, 'r'), s(20, 'g')
    rot = s(10, 'b')
    energy = s(5, 'b')
    order = s(9, 'b')
    trans = s(8, 'a')
    hue = s(15, 'a')
    fog = float(C.par.Fog.eval())
    hl = (s(0, 'r'), s(0, 'g'))
    hr = (s(1, 'r'), s(1, 'g'))
    torso = (s(3, 'r'), s(3, 'g'))
    head = (s(2, 'r'), s(2, 'g'))
    complexity = s(10, 'g')

    def w(u, v):
        return ((u - 0.5) * 2.0 * ASP, (v - 0.5) * 2.0)

    rows = []
    if GROUP.startswith('ring'):
        k0 = int(GROUP[4])
        N, SP = 9, 0.62                # 9 rings per family, 3 families interleaved -> 27 rings, spacing 0.62/3
        L = N * SP
        for i in range(N):
            kk = i * 3 + k0
            zz = -(L - ((i * SP + tun * SP * 0.33 + k0 * SP / 3.0) % L)) - 0.4
            depth = -zz / L
            # the whole tunnel leans toward the body and is bent by the hands / energy
            bx, by = w(*torso)
            hx = (w(*hl)[0] + w(*hr)[0]) * 0.5
            hy = (w(*hl)[1] + w(*hr)[1]) * 0.5
            bend = (1.0 - order * 0.85)
            tx = (bx * 0.55 + hx * 0.35) * depth * 1.0 + 0.18 * energy * bend * math.sin(zz * 1.3 + T * 1.7)
            ty = (by * 0.55 + hy * 0.35) * depth * 1.0 + 0.18 * energy * bend * math.cos(zz * 1.1 + T * 1.3)
            rad = 1.85 + 0.12 * math.sin(kk * 0.7 + T * 0.5) * bend
            rz = math.degrees(rot * 0.35) * (1 if kk % 2 == 0 else -1) + kk * 12.0
            fade = math.exp(-fog * 2.2 * depth) * min(1.0, (depth) * 6.0) * min(1.0, (1.0 - depth) * 3.0 + 0.2)
            br = (0.22 + 0.35 * trans + 0.1 * complexity) * fade
            c = pal(hue + 0.55 + kk * 0.035)
            rows.append((tx, ty, zz, 0, 0, rz, rad, rad, rad, c[0] * br, c[1] * br, c[2] * br))
    elif GROUP == 'ico':
        n = 6
        for i in range(n):
            ph = (i / n + tun * 0.02) % 1.0
            zz = -0.9 - ph * 7.0
            depth = ph
            ang = i * 2.399 + T * 0.05
            r = 1.1 + 0.9 * depth
            tx = math.cos(ang) * r + w(*torso)[0] * 0.2 * depth
            ty = math.sin(ang) * r * 0.7 + w(*torso)[1] * 0.2 * depth
            fade = math.exp(-fog * 1.6 * depth) * min(1.0, depth * 5.0) * min(1.0, (1 - depth) * 4.0)
            sc = 0.32 + 0.25 * depth
            c = pal(hue + 0.12 + i * 0.09)
            br = (0.45 + 0.4 * trans) * fade
            rows.append((tx, ty, zz, T * 11.0 + i * 40.0 + rot * 20.0, T * 17.0 + i * 20.0, i * 30.0, sc, sc, sc,
                         c[0] * br, c[1] * br, c[2] * br))
    elif GROUP == 'torus':
        n = 4
        for i in range(n):
            ph = (i / n + tun * 0.012) % 1.0
            zz = -1.4 - ph * 6.5
            depth = ph
            tx = math.sin(i * 1.7 + T * 0.07) * (0.9 + depth) + w(*head)[0] * 0.2 * depth
            ty = math.cos(i * 2.3 + T * 0.05) * (0.5 + 0.5 * depth) + w(*head)[1] * 0.2 * depth
            fade = math.exp(-fog * 1.6 * depth) * min(1.0, depth * 5.0) * min(1.0, (1 - depth) * 4.0)
            sc = 0.55 + 0.35 * depth + 0.15 * energy
            c = pal(hue + 0.32 + i * 0.11)
            br = (0.4 + 0.4 * trans) * fade
            rows.append((tx, ty, zz, 60.0 + T * 8.0 * (1 + i), T * 13.0 + i * 70.0, T * 5.0, sc, sc, sc,
                         c[0] * br, c[1] * br, c[2] * br))
    scriptOp.numSamples = max(1, len(rows))
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            scriptOp[j][i] = v
