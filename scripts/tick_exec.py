# Execute DAT  COMPUTER_VISION/tick  -  runs every frame:
#   * (re)starts the CV worker thread when needed, feeds it the mirrored camera frame at the analysis rate
#   * forces the cook of the tracking + final-output chain so the installation keeps running with no viewer open
import numpy as np
ROOT = '__ROOT__'
KEEP_ALIVE = ['/TRACKING_DATA/tracking_raw', '/COMPUTER_VISION/mask_script', '/FEEDBACK_SYSTEM/OUT_FEEDBACK',
              '/FINAL_OUTPUT/OUT_FINAL']


def onFrameStart(frame):
    import sgo_cv
    ctl = op(ROOT + '/CONTROL_DASHBOARD')
    if ctl is None:
        return
    RT = sgo_cv.RT
    demo = bool(ctl.par.Demomode.eval())
    if demo:
        if RT.worker is not None:
            RT.stop()
    else:
        backend = ctl.par.Cvbackend.eval()
        if RT.worker is None or RT.worker.backend_req != backend or not RT.worker.is_alive():
            RT.start(backend)
        w = RT.worker
        w.conf = float(ctl.par.Detectconf.eval())
        w.thresh = float(ctl.par.Silthreshold.eval())
        RT.sub_counter += 1
        every = max(1, int(round(60.0 / max(1, int(ctl.par.Cvrate.eval())))))
        if RT.sub_counter % every == 0:
            top = op(ROOT + '/COMPUTER_VISION/cv_frame')
            try:
                arr = top.numpyArray(delayed=True)
            except Exception:
                arr = None
            if arr is not None and arr.size:
                if arr.dtype == np.uint8:
                    arr = arr.astype(np.float32) / 255.0
                w.submit(arr)
    for p in KEEP_ALIVE:
        o = op(ROOT + p)
        if o is not None:
            try:
                o.cook(force=True)
            except Exception:
                pass
    return
