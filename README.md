# Sacred Geometry Organism

A camera watches a participant. Pose, silhouette, hands, head, velocity and stillness drive a living field of sacred
geometry (Flower of Life, Metatron's Cube, Sri Yantra, Fibonacci/phyllotaxis, vesica piscis, hex lattice, mandalas,
recursive fractal, tori, icosahedra, 65,536 GPU particles) inside a psychedelic feedback pipeline, then
projection-mapped to a wall / sculpture / stage.

Built and verified live in TouchDesigner **2025.33230** (Windows).

## Open it
* `SacredGeometryOrganism.toe` — everything is already built. It was saved in **live webcam** mode at *performance*
  quality. Turn `Demomode` **on** (dashboard, System page) for the scripted synthetic participant — handy for rehearsal
  with nobody in front of the camera. Quality can be raised on the same page.
* Rebuild from scratch (idempotent): in the Textport
  `import builtins; builtins.SGO_SECTIONS=None; exec(open(r'C:\Users\Utsav\SacredGeometryOrganism\build\run.py').read())`
* The project loads scripts/shaders from this folder (`scripts/`, `shaders/`, `pylibs/`, `models/`). Keep the folder
  where it is, or edit `DIR` in `build/00_core.py` and rebuild.
* The saved .toe also contains the `mcp_webserver_base` helper used while building (port 9981). Delete it for a show file.

## Network (`/project1`)
`CAMERA_INPUT → COMPUTER_VISION → TRACKING_DATA → GEOMETRY_ENGINE → PARTICLE_ENGINE → PSYCHEDELIC_EFFECTS →
FEEDBACK_SYSTEM → PROJECTION_MAPPING → FINAL_OUTPUT`, plus `CONTROL_DASHBOARD`. Every container ends in `OUT_*` Null
operators. All tracking / state / control values reach every shader through **one 48x1 float "uniform texture"**
(`GEOMETRY_ENGINE/OUT_UNIFORMS`, layout documented in `shaders/common.glsl` and `scripts/pack_cb.py`).

| Stage | What it does |
|---|---|
| COMPUTER_VISION | MediaPipe Pose (+ segmentation mask) and Hands on a worker thread (`scripts/sgo_cv.py`), OpenCV background-subtraction fallback. Mask: Threshold → Blur → Level → Edge → `SIL_MASK / SIL_CONTOUR / SIL_HALO`. `SIL_HELD` keeps the last silhouette as an afterimage. Debug views: `CV_DEBUG`, `SKELETON_OVERLAY`. |
| TRACKING_DATA | `tracking_raw` → Filter → Lag → Math → (Slope = velocity, Speed = rotation phase) → `derived` (hand_distance, body_velocity, motion_energy, hands_above_head, hands_touch, raised_arms…) → `OUT_TRACKING`. `state` = IDLE/AWAKEN/INTERACTION/TRANSCENDENCE/STILLNESS/EXIT as continuous weights → `OUT_STATE`. |
| GEOMETRY_ENGINE | `geo_near/mid/far` GLSL (procedural 2D systems) on parallax planes + `scene3d`: perspective camera driven by the body, instanced Circle/Torus/Script-SOP (icosahedron) wireframes, Copy-SOP Flower of Life, infinite polygon tunnel. |
| PARTICLE_ENGINE | 256x256 float sim (Feedback TOP + GLSL) → Grid→Convert SOP point cloud → GLSL MAT reads the sim texture in its vertex shader (no CPU readback). |
| PSYCHEDELIC_EFFECTS | BODY/AURA matte compositor → kaleidoscope → Noise/Displace → chromatic dispersion + diffraction → Lookup/Ramp iridescence → HSV → Level → Bloom → Edge. |
| FEEDBACK_SYSTEM | Feedback → Transform (rotate, zoom 1.001–1.01 about the head) → Level decay → HSV drift → Displace → lighten-Composite → Feedback. |
| PROJECTION_MAPPING | 3 independent surface COMPs (crop → corner pin/keystone → edge blend → mask), `Mappingmode`: corner pin / multi-surface / **Kantan Mapper** (palette tox loaded; open its editor from the dashboard and point its shape source at `/project1/PROJECTION_MAPPING/source`), brightness/gamma/black level. CamSchnappr (`Palette/Mapping/camSchnappr.tox`) can be dropped in the same way. |
| FINAL_OUTPUT | `OUT_FINAL`, overlays (CV debug, skeleton, silhouette PiP, HUD), calibration pattern, borderless `projector_window` on monitor `Monitor`. |

## Body → art
Left/right hand → Metatron's Cube / Sri Yantra attractors · hand distance → expansion · head → radial-symmetry centre
(mandala, spiral, fractal, kaleidoscope pivot) · torso → Flower of Life origin · velocity → rotation · energy →
fractal depth + turbulence · raised arms → complexity · hands above head → crown mandala · hands touching →
singularity · rapid movement → bursts + trails · stillness → symmetry/`order` rises, particles form constellations ·
leaving → glowing afterimage dissolving into particles.

## Dashboard (`CONTROL_DASHBOARD`, or button *Open dashboard window*)
Pages System, CV, Geometry, Psychedelic, Particles, Depth, Projection. `Statelock` forces a state;
`Demofreeze` + `Democlock` park the demo performer on any moment of its 82 s choreography (rehearsal).
Buttons: reset feedback, recalibrate tracking, open projector, open Kantan editor.

## Performance
`Quality`: performance (960x540, MSAA off, iridescence/bloom/edge bypassed, 35% particles) · standard (1280x720) ·
high (1920x1080). Debug overlays, disabled mapping surfaces and bypassed effects do not cook.
Measured on this machine (Intel UHD 620 laptop GPU): **~20 fps performance mode**, ~9 fps standard.
60 fps at 1080p needs a discrete GPU.
**TouchDesigner Non-Commercial caps all textures at 1280x1280**; 1920x1080 output needs a commercial/Pro licence.

## Tools (run inside TD with `exec(open(path).read())`)
`tools/sync.py` hot-reload scripts + shaders · `tools/check_all.py` audit every node + NaN check ·
`tools/glsl_report.py` shader compile logs · `tools/profile.py` cook times · `tools/test_cv_offline.py` CV test on a still image.

## Known limits / not verified
* Hand-landmark gestures (open palm / pinch) need hands to be visible; verified only that the model loads and runs.
* Projector window, Kantan Mapper shapes and edge-blend were built and cook cleanly but not validated on a physical projector.
* Rapid-movement detection is tuned on the demo performer; adjust `Motionsens` for real people.

## Setup on a new machine
The repo leaves out ~320 MB of third-party files. Restore them once:
```
python -m pip install --target pylibs mediapipe          # use Python 3.11 (TouchDesigner 2025 ships 3.11)
mkdir models
curl -L -o models/pose_landmarker_lite.task https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
curl -L -o models/hand_landmarker.task      https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```
Then open `SacredGeometryOrganism.toe`. Paths are absolute (`C:\Users\Utsav\SacredGeometryOrganism`): clone to that
location, or change `DIR` in `build/00_core.py` and rebuild with `build/run.py`.
Without MediaPipe the OpenCV silhouette fallback and the Demo performer still work.
