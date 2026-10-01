# exec inside TouchDesigner:  reports compile logs of every GLSL TOP / MAT under /project1 into tools/glsl_report.txt
import td
out = []
root = op('/project1')
tmp = root.create(td.baseCOMP, '_glsl_report_tmp')
n_bad = 0
for o in [x for x in root.findChildren(maxDepth=6) if x.OPType in ('glslTOP', 'glslmultiTOP', 'glslMAT')]:
    if '_glsl_report_tmp' in o.path:
        continue
    d = tmp.create(td.infoDAT, 'i')
    d.par.op = o.path
    try:
        d.cook(force=True)
        txt = d.text
    except Exception as e:
        txt = 'ERR %s' % e
    errs = o.errors() + '\n' + o.warnings()
    bad = ('error' in txt.lower() and 'compile' in txt.lower()) or 'compile errors' in errs
    flag = 'BAD ' if bad else 'ok  '
    if bad:
        n_bad += 1
        out.append('%s%s\n%s\n%s\n' % (flag, o.path, errs.strip(), txt))
    else:
        out.append('%s%s' % (flag, o.path))
    d.destroy()
tmp.destroy()
open(r'C:\Users\Utsav\SacredGeometryOrganism\tools\glsl_report.txt', 'w', encoding='utf-8').write(
    '%d bad\n' % n_bad + '\n'.join(out))
