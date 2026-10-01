"""Offline test of the CV path (no TouchDesigner): run the REAL CVWorker code on a still portrait and print the
tracking channels the installation would receive.   usage:  python tools/test_cv_offline.py"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'pylibs'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import numpy as np
import cv2
import sgo_cv

img_path = os.path.join(ROOT, 'pylibs', 'matplotlib', 'mpl-data', 'sample_data', 'grace_hopper.jpg')
im = cv2.imread(img_path)
h, w = im.shape[:2]
# fit the portrait into a 16:9 frame like the camera would deliver (person centred, full height)
W, H = 640, 360
sc = H / h
person = cv2.resize(im, (int(w * sc), H))
frame = np.zeros((H, W, 3), np.uint8)
x0 = (W - person.shape[1]) // 2
frame[:, x0:x0 + person.shape[1]] = person
rgba = np.dstack([frame[..., ::-1].astype(np.float32) / 255.0, np.ones((H, W), np.float32)])   # RGB 0..1
rgba = rgba[::-1].copy()                                                                        # TD: row 0 = bottom

wk = sgo_cv.CVWorker('mediapipe')
wk.start()
for _ in range(4):
    wk.submit(rgba)
    time.sleep(1.5)
snap = wk.snapshot()
print('backend:', wk.backend, '| err:', repr(wk.err), '| worker fps: %.1f' % snap['fps'])
print('pose found:', snap['pose'] is not None, '| hands:', len(snap['hands'] or []),
      '| mask:', None if snap['mask'] is None else (snap['mask'].shape, 'coverage %.2f' % (snap['mask'] > 127).mean()))
tr = sgo_cv.Tracker()
ch, present = tr.update(snap, time.time())
print('present:', present)
if ch:
    for k in ('head_x', 'head_y', 'hand_left_x', 'hand_left_y', 'hand_right_x', 'hand_right_y', 'body_center_x',
              'body_center_y', 'shoulder_w', 'depth', 'conf', 'open_l', 'open_r'):
        print('  %-14s %.3f' % (k, ch[k]))
wk.stop()
