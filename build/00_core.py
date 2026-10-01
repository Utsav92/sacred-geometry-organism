# shared helpers for every build section  (exec'd into one namespace by run.py)
import os
import sys
import td

DIR = r'C:\Users\Utsav\SacredGeometryOrganism'
ROOT = '/project1'
CTRL = ROOT + '/CONTROL_DASHBOARD'
WARN = []
_pos = {}
for _p in (os.path.join(DIR, 'scripts'),):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def read(rel):
    with open(os.path.join(DIR, rel), 'r', encoding='utf-8') as f:
        return f.read().replace('__ROOT__', ROOT).replace('__DIR__', DIR)


def T(name):
    return getattr(td, name)


def P(o, **kw):
    """set constant parameter values; unknown names are logged, never fatal"""
    for k, v in kw.items():
        try:
            getattr(o.par, k).val = v
        except Exception as e:
            WARN.append('%s.%s = %r  ->  %s' % (o.path, k, v, e))


def X(o, **kw):
    """set parameter expressions"""
    for k, v in kw.items():
        try:
            getattr(o.par, k).expr = v
        except Exception as e:
            WARN.append('%s.%s expr %r  ->  %s' % (o.path, k, v, e))


def mk(parent, typ, name, x=None, y=None):
    o = parent.create(T(typ), name)
    i = _pos.get(parent.path, 0)
    _pos[parent.path] = i + 1
    o.nodeX = x if x is not None else (i % 6) * 220
    o.nodeY = y if y is not None else -(i // 6) * 140
    return o


def wire(src, dst, idx=0):
    try:
        dst.inputConnectors[idx].connect(src)
    except Exception as e:
        WARN.append('wire %s -> %s[%d]: %s' % (src.path, dst.path, idx, e))


def chain(*ops_):
    for a, b in zip(ops_[:-1], ops_[1:]):
        wire(a, b)
    return ops_[-1]


def null(parent, name, src=None, kind='TOP'):
    n = mk(parent, 'null' + kind, name)
    if src is not None:
        wire(src, n)
    return n


def sel(parent, name, path, kind='TOP'):
    s = mk(parent, 'select' + kind, name)
    if kind == 'TOP':
        P(s, top=path)
    elif kind == 'CHOP':
        P(s, chops=path)
    return s


def C(n):
    return "op('%s').par.%s" % (CTRL, n)


def container(name):
    root = op(ROOT)
    if root is None:
        root = op('/').create(T('baseCOMP'), 'project1')
    old = root.op(name)
    if old is not None:
        old.destroy()
    c = root.create(T('baseCOMP'), name)
    _pos[c.path] = 0
    idx = ['CONTROL_DASHBOARD', 'CAMERA_INPUT', 'COMPUTER_VISION', 'TRACKING_DATA', 'GEOMETRY_ENGINE',
           'PARTICLE_ENGINE', 'PSYCHEDELIC_EFFECTS', 'FEEDBACK_SYSTEM', 'PROJECTION_MAPPING', 'FINAL_OUTPUT']
    i = idx.index(name) if name in idx else len(idx)
    c.nodeX, c.nodeY = (i % 5) * 300, -(i // 5) * 200
    return c


def text_dat(parent, name, text):
    d = mk(parent, 'textDAT', name)
    d.text = text
    return d


def common_glsl():
    return read('shaders/common.glsl')


def glsl(parent, name, shader, inputs=(), res=None, fmt='rgba16float', defines=None, uni=None, common=True,
         filt='linear'):
    """GLSL TOP from shaders/<shader>.  `uni` = TOP (the uniform texture); it is appended as the last input and
    UNI_IDX is defined accordingly.  `res` = (w, h) constants or (expr_w, expr_h) strings."""
    g = mk(parent, 'glslmultiTOP', name)
    ins = list(inputs)
    head = ''
    if uni is not None:
        ins.append(uni)
        head += '#define UNI_IDX %d\n' % (len(ins) - 1)
    for k, v in (defines or {}).items():
        head += '#define %s %s\n' % (k, v)
    src = head + (common_glsl() + '\n' if common else '') + read('shaders/' + shader + '.glsl')
    d = g.par.pixeldat.eval()                     # TD's own docked pixel DAT
    d.text = src
    for i, s in enumerate(ins):
        wire(s, g, i)
    if res:
        P(g, outputresolution='custom')
        for k, v in zip(('resolutionw', 'resolutionh'), res):
            if isinstance(v, str):
                X(g, **{k: v})
            else:
                P(g, **{k: v})
    if fmt:
        P(g, format=fmt)
    P(g, inputfiltertype=filt)
    return g


def script_chop(parent, name, cb_file):
    s = mk(parent, 'scriptCHOP', name)
    s.par.callbacks.eval().text = read('scripts/' + cb_file)
    P(s, timeslice=False)
    return s


def script_top(parent, name, cb_file):
    s = mk(parent, 'scriptTOP', name)
    s.par.callbacks.eval().text = read('scripts/' + cb_file)
    return s


def uniforms_top():
    return op(ROOT + '/GEOMETRY_ENGINE/OUT_UNIFORMS')


def sel_uni(parent, name='uni'):
    s = mk(parent, 'selectTOP', name)
    P(s, top=ROOT + '/GEOMETRY_ENGINE/OUT_UNIFORMS')
    return s


def ensure_playing():
    op('/').time.play = True
    op('/').time.rate = 60


def log(msg):
    WARN.append(msg)

ensure_playing()
