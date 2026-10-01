# exec inside TouchDesigner : hot-reload every script / shader from disk into the live network (no rebuild).
#     exec(open(r'C:\Users\Utsav\SacredGeometryOrganism\tools\sync.py').read())
import os
DIR = r'C:\Users\Utsav\SacredGeometryOrganism'
ROOT = '/project1'


def rd(rel):
    return open(os.path.join(DIR, rel), encoding='utf-8').read().replace('__ROOT__', ROOT).replace('__DIR__', DIR)


SCRIPTS = {
    'TRACKING_DATA/tracking_raw_callbacks': 'scripts/tracking_raw_cb.py',
    'TRACKING_DATA/derived_callbacks': 'scripts/derived_cb.py',
    'TRACKING_DATA/state_callbacks': 'scripts/state_cb.py',
    'GEOMETRY_ENGINE/uniform_pack_callbacks': 'scripts/pack_cb.py',
    'COMPUTER_VISION/mask_script_callbacks': 'scripts/mask_top_cb.py',
    'FINAL_OUTPUT/hud_mod': 'scripts/hud_mod.py',
    'COMPUTER_VISION/tick': 'scripts/tick_exec.py',
}
n = 0
for path, f in SCRIPTS.items():
    o = op(ROOT + '/' + path)
    if o is not None:
        o.text = rd(f)
        n += 1
# instance scripts
for g in ('ring0', 'ring1', 'ring2', 'ico', 'torus'):
    o = op(ROOT + '/GEOMETRY_ENGINE/scene3d/inst_%s_callbacks' % g)
    if o is not None:
        o.text = rd('scripts/instances_cb.py').replace('__GROUP__', g)
        n += 1
# shaders : re-assemble header + common + body exactly like the builder does
common = rd('shaders/common.glsl')
SH = {}
for o in op(ROOT).findChildren(maxDepth=6):
    if o.OPType == 'textDAT' and o.name.endswith('_pixel'):
        SH[o.path] = o
for path, d in SH.items():
    old = d.text
    head = ''.join(l + '\n' for l in old.splitlines() if l.startswith('#define '))
    # which shader file ? stored as a comment-free lookup by node name
    name = d.name[:-len('_pixel')]
    FILE = {'geo_near': 'geo', 'geo_mid': 'geo', 'geo_far': 'geo', 'demo_body': 'demo_body', 'demo_view': 'demo_body',
            'skeleton': 'skeleton', 'cv_debug': 'cv_debug', 'hold_step': 'sil_hold', 'sim_step': 'sim',
            'scene_composite': 'scene_comp', 'kaleidoscope': 'kaleido', 'chromatic': 'chroma',
            'feedback_out': 'tonemap', 'final_grade': 'final_grade',
            'debug_overlay': 'debug_overlay'}.get(name)
    if name == 'edge_blend':                    # per-surface pass : own uniforms, no shared header
        d.text = rd('shaders/surface_pass.glsl')
        n += 1
    elif name == 'calibration':
        d.text = rd('shaders/calibration.glsl')
        n += 1
    elif FILE:
        d.text = head + common + '\n' + rd('shaders/%s.glsl' % FILE)
        n += 1
for nm, f in (('PARTICLE_ENGINE/particle_vertex', 'shaders/particle_vertex.glsl'),
              ('PARTICLE_ENGINE/particle_pixel', 'shaders/particle_pixel.glsl')):
    o = op(ROOT + '/' + nm)
    if o is not None:
        o.text = rd(f)
        n += 1
print('synced', n, 'DATs')
