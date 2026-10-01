"""
Section runner.  From TouchDesigner's Textport (Alt+T):

    import builtins; builtins.SGO_SECTIONS = None      # None = everything
    exec(open(r'C:\\Users\\Utsav\\SacredGeometryOrganism\\build\\run.py').read())

or build selected sections only, e.g.  builtins.SGO_SECTIONS = ['controls', 'camera_cv'].
Warnings (parameters that did not exist on this TD build etc.) are collected in WARN and written to build/last_build.log
"""
import builtins
import os
import time

BUILD_DIR = r'C:\Users\Utsav\SacredGeometryOrganism\build'
ORDER = ['controls', 'camera_cv', 'tracking', 'geometry', 'scene3d', 'particles', 'psychedelic', 'feedback',
         'projection', 'output']
want = getattr(builtins, 'SGO_SECTIONS', None) or ORDER
G = dict(globals())            # keeps TD's op / absTime / project / app visible to the sections
G['__name__'] = 'sgo_build'
exec(open(os.path.join(BUILD_DIR, '00_core.py'), encoding='utf-8').read(), G)
t0 = time.time()
for name in ORDER:
    if name in want:
        f = os.path.join(BUILD_DIR, '%02d_%s.py' % (ORDER.index(name) + 1, name))
        G['WARN'].append('---- section %s' % name)
        try:
            exec(open(f, encoding='utf-8').read(), G)
        except Exception as e:                       # keep going so later sections still get built
            import traceback
            G['WARN'].append('SECTION %s FAILED:\n%s' % (name, traceback.format_exc()))
open(os.path.join(BUILD_DIR, 'last_build.log'), 'w', encoding='utf-8').write(
    'built %s in %.1fs\n' % (want, time.time() - t0) + '\n'.join(G['WARN']))
