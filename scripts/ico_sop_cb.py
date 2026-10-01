# Script SOP : unit icosahedron (12 points, 20 triangles).  Built once; wireframe-rendered + instanced.
import math


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.clear()
    t = (1.0 + math.sqrt(5.0)) / 2.0
    raw = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
           (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    n = math.sqrt(1 + t * t)
    pts = []
    for x, y, z in raw:
        p = scriptOp.appendPoint()
        p.x, p.y, p.z = x / n, y / n, z / n
        pts.append(p)
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2),
             (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11),
             (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for a, b, c in faces:
        poly = scriptOp.appendPoly(3, closed=True, addPoints=False)
        poly[0].point, poly[1].point, poly[2].point = pts[a], pts[b], pts[c]
