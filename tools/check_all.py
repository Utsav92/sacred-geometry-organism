# exec inside TouchDesigner : audits the whole /project1 network -> tools/check_all.txt
import numpy as np
out = []
root = op('/project1')
n_nodes = n_bad = 0
skip = ('kantan_mapper',)
for o in root.findChildren(maxDepth=8):
    if any(('/' + s + '/') in o.path + '/' for s in skip):
        continue
    n_nodes += 1
    e = (o.errors() or '').strip()
    w = (o.warnings() or '').strip()
    if e or w:
        n_bad += 1
        out.append('%s [%s]  E: %s | W: %s' % (o.path, o.OPType, e[:160], w[:160]))
out.insert(0, '%d nodes, %d with errors/warnings' % (n_nodes, n_bad))
out.append('---- key outputs (size / max / mean / nan)')
for p in ('GEOMETRY_ENGINE/OUT_GEO_NEAR', 'GEOMETRY_ENGINE/OUT_GEO_MID', 'GEOMETRY_ENGINE/OUT_GEO_FAR',
          'GEOMETRY_ENGINE/OUT_SCENE3D', 'PARTICLE_ENGINE/OUT_PARTICLES', 'COMPUTER_VISION/SIL_MASK',
          'COMPUTER_VISION/SIL_HELD', 'PSYCHEDELIC_EFFECTS/CLEAN_SCENE', 'PSYCHEDELIC_EFFECTS/OUT_PSY',
          'FEEDBACK_SYSTEM/OUT_FEEDBACK', 'PROJECTION_MAPPING/OUT_PROJECTION', 'FINAL_OUTPUT/OUT_FINAL'):
    o = op('/project1/' + p)
    if o is None:
        out.append('%-40s MISSING' % p)
        continue
    try:
        o.cook(force=True)
        a = o.numpyArray()
        out.append('%-40s %4dx%-4d max=%8.3f mean=%7.4f nan=%d' % (p, o.width, o.height, np.nanmax(a), np.nanmean(a),
                                                                    int(np.isnan(a).sum())))
    except Exception as ex:
        out.append('%-40s ERR %s' % (p, ex))
open(r'C:\Users\Utsav\SacredGeometryOrganism\tools\check_all.txt', 'w', encoding='utf-8').write('\n'.join(out))
