# Script TOP  COMPUTER_VISION/mask_script : pushes the CV worker's person mask (MediaPipe segmentation or OpenCV
# background subtraction) into a TOP.  640x360, row 0 = bottom (TouchDesigner convention).
import numpy as np
import sgo_cv

W, H = 640, 360


def onSetupParameters(scriptOp):
    return


def onCook(scriptOp):
    RT = sgo_cv.RT
    snap = RT.worker.snapshot() if RT.worker is not None else None
    m = snap.get('mask') if snap else None
    if m is None:
        a = np.zeros((H, W), np.float32)
    else:
        if m.shape != (H, W):
            import cv2
            m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
        a = (m.astype(np.float32) / 255.0)[::-1]
    arr = np.ascontiguousarray(np.dstack([a, a, a, np.ones_like(a)]))
    scriptOp.copyNumpyArray(arr)
