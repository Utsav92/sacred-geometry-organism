# exec inside TouchDesigner : ranks nodes by GPU / CPU cook time (ms) -> tools/profile.txt
rows = []
for o in op('/project1').findChildren(maxDepth=8):
    try:
        g = o.gpuCookTime
        c = o.cpuCookTime
    except Exception:
        continue
    if o.OPType.endswith(('TOP', 'MAT', 'COMP', 'CHOP', 'SOP', 'DAT')):
        rows.append((g, c, o.path, o.OPType))
rows.sort(reverse=True)
out = ['GPU ms   CPU ms   node']
for g, c, p, t in rows[:25]:
    out.append('%7.2f  %7.2f  %s [%s]' % (g, c, p, t))
rows.sort(key=lambda r: -r[1])
out.append('---- by CPU')
for g, c, p, t in rows[:12]:
    out.append('%7.2f  %7.2f  %s [%s]' % (g, c, p, t))
out.append('total GPU %.1f ms  total CPU %.1f ms' % (sum(r[0] for r in rows), sum(r[1] for r in rows)))
open(r'C:\Users\Utsav\SacredGeometryOrganism\tools\profile.txt', 'w', encoding='utf-8').write('\n'.join(out))
