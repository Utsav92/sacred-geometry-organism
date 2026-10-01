# Script SOP : 19 hexagonal-lattice points (Flower of Life centres, unit spacing).  Template for the Copy SOP.
import math


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.clear()
    for i in range(-2, 3):
        for j in range(-2, 3):
            if max(abs(i), abs(j), abs(i + j)) <= 2:
                p = scriptOp.appendPoint()
                p.x = i + j * 0.5
                p.y = j * math.sqrt(3.0) / 2.0
                p.z = 0.0
