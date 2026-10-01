"""
sgo_cv  -  computer-vision backend for the Sacred Geometry Organism.

* Worker thread runs MediaPipe PoseLandmarker (+segmentation mask) and HandLandmarker on frames pushed from TD.
  If mediapipe is unavailable it falls back to OpenCV background subtraction + contour analysis.
* A scripted "demo performer" produces the same joint layout so the whole installation runs with nobody in front
  of the camera.

Coordinate convention everywhere in this module's OUTPUT: x 0..1 left->right, y 0..1 bottom->top (TouchDesigner UV),
in the MIRRORED camera image.
"""
import math
import os
import sys
import threading
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(HERE)
PYLIBS = os.path.join(ROOT_DIR, 'pylibs')
MODELS = os.path.join(ROOT_DIR, 'models')

# MediaPipe pose indices for the 13 joints we publish
#            head  lsh rsh lel rel lwr rwr lhip rhip lkn rkn lan ran
MP_IDX = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
JOINT_NAMES = ['head', 'lsh', 'rsh', 'lel', 'rel', 'lwr', 'rwr', 'lhip', 'rhip', 'lkn', 'rkn', 'lan', 'ran']
# index pairs (left, right) so we can swap sides consistently
PAIRS = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]


def _clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


# ======================================================================= CV worker
class CVWorker(threading.Thread):
    def __init__(self, backend='auto'):
        super().__init__(daemon=True)
        self.backend_req = backend
        self.backend = 'starting'
        self.err = ''
        self.running = True
        self.evt = threading.Event()
        self.frame = None            # float32 HxWx4 straight from TOP.numpyArray (row 0 = bottom)
        self.lock = threading.Lock()
        self.out = dict(ts=0.0, pose=None, hands=[], mask=None, fps=0.0, seq=0)
        self.conf = 0.5
        self.thresh = 0.35
        self.learn = 0.004
        self.reset_bg = False
        self._bg = None
        self.frames_in = 0

    # ---- API used from the TD main thread
    def submit(self, arr):
        self.frame = arr
        self.evt.set()

    def snapshot(self):
        with self.lock:
            return self.out

    def stop(self):
        self.running = False
        self.evt.set()

    # ---- init models
    def _init_mp(self):
        if PYLIBS not in sys.path:
            sys.path.append(PYLIBS)               # appended: TD's own numpy / cv2 keep priority
        import mediapipe as mp
        from mediapipe.tasks import python as mpp
        from mediapipe.tasks.python import vision
        self.mp = mp
        self.vision = vision
        self.mpp = mpp
        self._mk_models()
        self.backend = 'mediapipe'

    def _mk_models(self):
        vision, mpp = self.vision, self.mpp
        vid = vision.RunningMode.VIDEO
        c = float(self.conf)
        self.pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=mpp.BaseOptions(model_asset_path=os.path.join(MODELS, 'pose_landmarker_lite.task')),
            running_mode=vid, num_poses=1, output_segmentation_masks=True,
            min_pose_detection_confidence=c, min_pose_presence_confidence=c, min_tracking_confidence=c))
        self.hand = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
            base_options=mpp.BaseOptions(model_asset_path=os.path.join(MODELS, 'hand_landmarker.task')),
            running_mode=vid, num_hands=2,
            min_hand_detection_confidence=c, min_hand_presence_confidence=c, min_tracking_confidence=c))
        self._mk_conf = c

    # ---- thread body
    def run(self):
        want = self.backend_req
        if want in ('auto', 'mediapipe'):
            try:
                self._init_mp()
            except Exception as e:                # noqa
                self.err = 'mediapipe unavailable: %r' % (e,)
                self.backend = 'opencv'
        else:
            self.backend = 'opencv'
        import cv2
        self.cv2 = cv2
        t_last, n, fps = time.time(), 0, 0.0
        tick = 0
        while self.running:
            if not self.evt.wait(0.5):
                continue
            self.evt.clear()
            f = self.frame
            if f is None:
                continue
            try:
                if self.backend == 'mediapipe':
                    if abs(self._mk_conf - self.conf) > 0.04:
                        self._mk_models()
                    res = self._run_mp(f, tick)
                else:
                    res = self._run_cv(f)
                tick += 1
            except Exception as e:                # noqa
                self.err = 'cv error: %r' % (e,)
                continue
            n += 1
            now = time.time()
            if now - t_last > 1.0:
                fps, n, t_last = n / (now - t_last), 0, now
            res['fps'] = fps
            res['ts'] = now
            with self.lock:
                res['seq'] = self.out['seq'] + 1
                self.out = res

    # ---- MediaPipe path
    def _run_mp(self, f, tick):
        mp = self.mp
        rgb = np.ascontiguousarray((f[::-1, :, :3] * 255.0).astype(np.uint8))      # top-down RGB
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts = int(time.monotonic() * 1000)
        if ts <= getattr(self, '_last_ts', -1):
            ts = self._last_ts + 1
        self._last_ts = ts
        pr = self.pose.detect_for_video(img, ts)
        pose, mask = None, None
        if pr.pose_landmarks:
            lm = pr.pose_landmarks[0]
            pose = np.array([[p.x, p.y, getattr(p, 'visibility', 1.0) or 0.0] for p in lm], np.float32)
            if pr.segmentation_masks:
                m = pr.segmentation_masks[0].numpy_view()
                mask = np.ascontiguousarray((np.clip(np.squeeze(m), 0, 1) * 255).astype(np.uint8))
        hands = []
        if tick % 2 == 0 or self.out.get('hands'):
            hr = self.hand.detect_for_video(img, ts + 0)
            for h in (hr.hand_landmarks or []):
                hands.append(np.array([[p.x, p.y, p.z] for p in h], np.float32))
        return dict(pose=pose, hands=hands, mask=mask)

    # ---- OpenCV fallback path (silhouette only)
    def _run_cv(self, f):
        cv2 = self.cv2
        bgr = np.ascontiguousarray((f[::-1, :, [2, 1, 0]] * 255.0).astype(np.uint8))
        small = cv2.GaussianBlur(bgr, (5, 5), 0)
        if self._bg is None or self.reset_bg or self._bg.shape != small.shape:
            self._bg = small.astype(np.float32)
            self.reset_bg = False
        diff = cv2.absdiff(small, cv2.convertScaleAbs(self._bg)).max(axis=2).astype(np.float32) / 255.0
        m = (diff > float(self.thresh) * 0.4).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        # slow background learning only where nothing moves
        a = float(self.learn)
        still = (m == 0)[..., None]
        self._bg = np.where(still, self._bg * (1 - a) + small.astype(np.float32) * a, self._bg)
        h, w = m.shape
        pose = None
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            if cv2.contourArea(c) > 0.02 * w * h:
                x, y, bw, bh = cv2.boundingRect(c)
                M = cv2.moments(c)
                cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']
                pts = c[:, 0, :].astype(np.float32)
                top = pts[pts[:, 1] <= y + 0.06 * bh]
                hx, hy = (top[:, 0].mean(), top[:, 1].mean()) if len(top) else (cx, y)
                up = pts[pts[:, 1] < y + 0.6 * bh]
                lo = up[up[:, 0] < cx]
                hi = up[up[:, 0] >= cx]
                lw = lo[np.argmin(lo[:, 0])] if len(lo) else (x, cy)
                rw = hi[np.argmax(hi[:, 0])] if len(hi) else (x + bw, cy)
                shw = 0.22 * bh
                J = {0: (hx, hy + 0.05 * bh), 11: (cx - shw / 2, y + 0.2 * bh), 12: (cx + shw / 2, y + 0.2 * bh),
                     13: ((cx - shw / 2 + lw[0]) / 2, (y + 0.2 * bh + lw[1]) / 2),
                     14: ((cx + shw / 2 + rw[0]) / 2, (y + 0.2 * bh + rw[1]) / 2),
                     15: tuple(lw), 16: tuple(rw), 23: (cx - shw / 3, y + 0.55 * bh), 24: (cx + shw / 3, y + 0.55 * bh),
                     25: (cx - shw / 3, y + 0.77 * bh), 26: (cx + shw / 3, y + 0.77 * bh),
                     27: (cx - shw / 3, y + bh), 28: (cx + shw / 3, y + bh)}
                pose = np.zeros((33, 3), np.float32)
                for k, (px, py) in J.items():
                    pose[k] = (px / w, py / h, 0.6)
        return dict(pose=pose, hands=[], mask=m)


# ======================================================================= tracker (raw -> channel dict)
class Tracker:
    """Turns the worker's landmarks (or the demo performer) into the raw channel dict, with hold-on-loss."""

    def __init__(self):
        self.last = {}
        self.last_seen = 0.0
        self.sh_w_s = 0.2

    @staticmethod
    def _mirror_pairs(J):
        # make 'l' always the smaller-x side
        if J[1][0] > J[2][0]:
            for a, b in PAIRS:
                J[a], J[b] = J[b], J[a]
        return J

    def from_pose(self, pose, hands, mask, now):
        """pose: (33,3) top-down normalised;  returns dict or None"""
        ch = {}
        if pose is None:
            return None
        J = [(_clamp(float(pose[i][0])), _clamp(1.0 - float(pose[i][1])), float(pose[i][2])) for i in MP_IDX]   # keep joints on screen
        J = self._mirror_pairs(J)
        ch['conf'] = sum(j[2] for j in J[:7]) / 7.0
        # hands: match to wrists, refine fingertip / openness
        op_ = {'l': 0.0, 'r': 0.0}
        pi_ = {'l': 0.0, 'r': 0.0}
        hpos = {}
        for h in hands or []:
            wr = (float(h[0][0]), 1.0 - float(h[0][1]))
            side = 'l' if math.dist(wr, J[5][:2]) <= math.dist(wr, J[6][:2]) else 'r'
            palm = math.dist(h[0][:2], h[9][:2]) + 1e-6
            tips = [math.dist(h[0][:2], h[i][:2]) for i in (8, 12, 16, 20)]
            open_ = _clamp((sum(tips) / 4.0 / palm - 1.0) / 1.0)
            pinch = 1.0 - _clamp(math.dist(h[4][:2], h[8][:2]) / (palm * 0.9))
            op_[side], pi_[side] = open_, pinch
            palmc = ((h[0][0] + h[9][0]) / 2, 1.0 - (h[0][1] + h[9][1]) / 2)
            hpos[side] = palmc
        if 'l' in hpos:
            J[5] = (hpos['l'][0], hpos['l'][1], J[5][2])
        if 'r' in hpos:
            J[6] = (hpos['r'][0], hpos['r'][1], J[6][2])
        ch['open_l'], ch['open_r'] = op_['l'], op_['r']
        ch['pinch_l'], ch['pinch_r'] = pi_['l'], pi_['r']
        ch['have_hands'] = 1.0 if hands else 0.0
        self._fill(ch, J, mask)
        return ch

    def _fill(self, ch, J, mask):
        for n, j in zip(JOINT_NAMES, J):
            ch['j_%s_x' % n], ch['j_%s_y' % n] = j[0], j[1]
        head, lsh, rsh, lwr, rwr, lhip, rhip = J[0], J[1], J[2], J[5], J[6], J[7], J[8]
        ch['head_x'], ch['head_y'] = head[0], head[1]
        ch['hand_left_x'], ch['hand_left_y'] = lwr[0], lwr[1]
        ch['hand_right_x'], ch['hand_right_y'] = rwr[0], rwr[1]
        ch['body_center_x'] = (lsh[0] + rsh[0] + lhip[0] + rhip[0]) / 4.0
        ch['body_center_y'] = (lsh[1] + rsh[1] + lhip[1] + rhip[1]) / 4.0
        ch['shoulder_y'] = (lsh[1] + rsh[1]) / 2.0
        shw = math.dist(lsh[:2], rsh[:2])
        ch['shoulder_w'] = shw
        xs = [j[0] for j in J]
        ys = [j[1] for j in J]
        ch['bbox_minx'], ch['bbox_maxx'] = min(xs) - 0.03, max(xs) + 0.03
        ch['bbox_miny'], ch['bbox_maxy'] = min(ys) - 0.02, max(ys) + 0.08
        # distance participant<->camera : apparent shoulder width (0.10 far .. 0.40 near) -> 0..1
        self.sh_w_s += (shw - self.sh_w_s) * 0.1
        ch['depth'] = _clamp((self.sh_w_s - 0.08) / 0.30)

    def update(self, snap, now, mask_area_min=0.012):
        """snap = worker snapshot.  Returns (channel dict, present flag)"""
        ch = None
        if snap is not None and snap.get('pose') is not None:
            ch = self.from_pose(snap['pose'], snap.get('hands'), snap.get('mask'), now)
        present = ch is not None
        if present:
            self.last, self.last_seen = ch, now
        elif self.last and now - self.last_seen < 0.6:
            ch, present = self.last, True       # short hold during dropouts
        return ch, present


# ======================================================================= demo performer
def _smooth(a, b, t):
    t = _clamp((t - a) / max(b - a, 1e-6))
    return t * t * (3 - 2 * t)


def _lerp(a, b, t):
    return a + (b - a) * t


def demo_joints(t, cycle=82.0):
    """Choreographed synthetic participant. Returns (joints[13] -> (x,y), presence 0/1)  TD uv coords."""
    t = t % cycle
    cx = 0.5
    # walk in / out
    if t < 5:
        pres = 0.0
        cx = -0.2
    elif t < 10:
        pres = 1.0
        cx = _lerp(-0.12, 0.5, _smooth(5, 10, t))
    elif t < 67:
        pres, cx = 1.0, 0.5 + 0.03 * math.sin(t * 0.3)
    elif t < 73:
        pres = 1.0
        cx = _lerp(0.5, 1.12, _smooth(67, 73, t))
    else:
        pres, cx = 0.0, 1.2
    # base standing pose
    sc = 1.0
    head = [cx, 0.80]
    lsh, rsh = [cx - 0.075, 0.67], [cx + 0.075, 0.67]
    lhip, rhip = [cx - 0.045, 0.42], [cx + 0.045, 0.42]
    lkn, rkn = [cx - 0.05, 0.24], [cx + 0.05, 0.24]
    lan, ran = [cx - 0.055, 0.06], [cx + 0.055, 0.06]
    lwr, rwr = [cx - 0.11, 0.42], [cx + 0.11, 0.42]
    # phases for the hands
    if 10 <= t < 20:                                   # slow waves
        k = _smooth(10, 12, t)
        lwr = [cx - 0.18 + 0.05 * math.sin(t * 1.1), _lerp(0.42, 0.58, k) + 0.06 * math.cos(t * 0.9)]
        rwr = [cx + 0.18 + 0.05 * math.sin(t * 0.9 + 1), _lerp(0.42, 0.55, k) + 0.06 * math.cos(t * 1.2)]
    elif 20 <= t < 28:                                 # apart / together
        s = 0.5 + 0.5 * math.sin((t - 20) * 0.9)
        d = _lerp(0.05, 0.42, s)
        lwr, rwr = [cx - d, 0.55 + 0.03 * math.sin(t * 2)], [cx + d, 0.55 - 0.03 * math.sin(t * 2)]
    elif 28 <= t < 34:                                 # touch -> singularity
        k = _smooth(28, 30, t) * (1 - _smooth(33, 34, t))
        lwr = [_lerp(cx - 0.11, cx - 0.008, k), _lerp(0.42, 0.55, k)]
        rwr = [_lerp(cx + 0.11, cx + 0.008, k), _lerp(0.42, 0.55, k)]
    elif 34 <= t < 43:                                 # arms up : crown + transcendence
        k = _smooth(34, 36, t) * (1 - _smooth(42, 43.5, t))
        lwr = [_lerp(cx - 0.11, cx - 0.17, k), _lerp(0.42, 0.97, k)]
        rwr = [_lerp(cx + 0.11, cx + 0.17, k), _lerp(0.42, 0.97, k)]
    elif 43 <= t < 52:                                 # rapid movement
        a = 12.0
        lwr = [cx - 0.22 + 0.2 * math.sin(t * a), 0.55 + 0.25 * math.sin(t * a * 0.83 + 1)]
        rwr = [cx + 0.22 + 0.2 * math.sin(t * a * 0.9 + 2), 0.55 + 0.25 * math.cos(t * a * 0.77)]
        head[0] += 0.04 * math.sin(t * 7)
    elif 52 <= t < 67:                                 # stillness: arms slightly out, frozen
        lwr, rwr = [cx - 0.16, 0.47], [cx + 0.16, 0.47]
    # elbows halfway between shoulder and wrist, dropped a bit
    lel = [(lsh[0] + lwr[0]) / 2 - 0.02, (lsh[1] + lwr[1]) / 2 - 0.04]
    rel = [(rsh[0] + rwr[0]) / 2 + 0.02, (rsh[1] + rwr[1]) / 2 - 0.04]
    J = [head, lsh, rsh, lel, rel, lwr, rwr, lhip, rhip, lkn, rkn, lan, ran]
    return [tuple(j) for j in J], pres


def demo_channels(tr, t):
    J, pres = demo_joints(t)
    if pres < 0.5:
        return None
    ch = {'conf': 1.0, 'have_hands': 0.0, 'open_l': 0.5 + 0.5 * math.sin(t * 0.7), 'open_r': 0.5 + 0.5 * math.cos(t * 0.6),
          'pinch_l': 0.0, 'pinch_r': 0.0}
    tr._fill(ch, [(j[0], j[1], 1.0) for j in J], None)
    return ch


# ======================================================================= persistent runtime
class Runtime:
    """Lives in sys.modules so editing a callback DAT never resets the worker thread or tracker state."""

    def __init__(self):
        self.worker = None
        self.tracker = Tracker()
        self.mask_seq = -1
        self.sub_counter = 0

    def start(self, backend='auto'):
        self.stop()
        self.worker = CVWorker(backend)
        self.worker.start()

    def stop(self):
        if self.worker is not None:
            self.worker.stop()
            self.worker = None

    def recalibrate(self):
        self.tracker = Tracker()
        if self.worker is not None:
            self.worker.reset_bg = True


RT = globals().get('RT') or Runtime()
