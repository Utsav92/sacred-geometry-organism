// ---------------------------------------------------------------------------------------------
// SHARED HEADER  (the builder prepends  #define UNI_IDX <input index of the UNIFORM texture>  )
// The UNIFORM texture is a W x 1 float texture, one vec4 per "slot".  All tracking / state / control
// data reaches every shader through it, so there are no per-shader parameter wires.
// ---------------------------------------------------------------------------------------------
#define PI  3.14159265359
#define TAU 6.28318530718
#define PHI 1.61803398875

const int S_HL = 0;      // left hand   : x y vx vy   (uv, y up ; velocities in screen-heights / s)
const int S_HR = 1;      // right hand
const int S_HEAD = 2;    // head
const int S_TORSO = 3;   // torso centre
const int S_BBOX = 4;    // minx miny maxx maxy
const int S_SC0 = 5;     // hand_distance, body_velocity, motion_energy, stillness
const int S_SC1 = 6;     // depth(0 far..1 near), present, raised_arms, hands_above_head
const int S_SC2 = 7;     // singularity, crown, burst, time(s)
const int S_ST0 = 8;     // state weights : idle awaken interaction transcendence
const int S_ST1 = 9;     // stillness exit order afterimage
const int S_GEO0 = 10;   // symmetry, complexity, rotation(rad), scale
const int S_GEO1 = 11;   // w_flower w_metatron w_yantra w_fibonacci
const int S_GEO2 = 12;   // w_vesica w_hex w_mandala w_fractal
const int S_GEO3 = 13;   // recursion, aura(0 body..1 aura), hq, expand
const int S_PSY0 = 14;   // fb_amount fb_rotation fb_zoom displacement
const int S_PSY1 = 15;   // chroma glow noise hue
const int S_PAR0 = 16;   // count_frac velocity turbulence attraction
const int S_PAR1 = 17;   // decay size order scatter
const int S_PRJ = 18;    // brightness gamma black calib
const int S_FLG = 19;    // debug skeleton silpreview hq
const int S_CAM = 20;    // cam_x cam_y cam_z(dolly) tunnel_warp
const int S_J0 = 24;     // 13 joints : x y conf 0   (head lsh rsh lel rel lwr rwr lhip rhip lkn rkn lan ran)

vec4 U(int i) { return texelFetch(sTD2DInputs[UNI_IDX], ivec2(i, 0), 0); }

#ifdef FIXED_ASPECT
float ASP() { return FIXED_ASPECT; }
#else
float ASP() { return uTDOutputInfo.res.z / uTDOutputInfo.res.w; }
#endif
vec2 toQ(vec2 uv) { return (uv - 0.5) * vec2(ASP(), 1.0) * 2.0; }       // q : y in [-1,1], x in [-asp,asp]
mat2 rot2(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

float hash11(float n) { return fract(sin(n * 127.1) * 43758.5453); }
float hash21(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec2 hash22(vec2 p) { return fract(sin(vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)))) * 43758.5453); }

float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), f.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), f.x), f.y);
}
vec2 curl(vec2 p, float t) {
    const float e = 0.01;
    float n1 = vnoise(p + vec2(0, e) + t), n2 = vnoise(p - vec2(0, e) + t);
    float n3 = vnoise(p + vec2(e, 0) + t), n4 = vnoise(p - vec2(e, 0) + t);
    return vec2(n1 - n2, -(n3 - n4)) / (2.0 * e);
}

// iridescent thin-film-ish palette
vec3 pal(float t) { return 0.5 + 0.5 * cos(TAU * (t + vec3(0.0, 0.33, 0.67))); }

// ---- distance primitives
float sdSeg(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-9), 0.0, 1.0);
    return length(pa - ba * h);
}
float ringD(vec2 p, vec2 c, float r) { return abs(length(p - c) - r); }
// regular n-gon outline distance, circumradius R
float polyD(vec2 p, float n, float R, float rot) {
    p = rot2(-rot) * p;
    float a = atan(p.y, p.x);
    float seg = TAU / n;
    float k = floor(a / seg);
    vec2 v0 = R * vec2(cos(k * seg), sin(k * seg));
    vec2 v1 = R * vec2(cos((k + 1.0) * seg), sin((k + 1.0) * seg));
    return sdSeg(p, v0, v1);
}
// neon line profile.  d = distance, w = half width
float lineI(float d, float w) {
    d = abs(d);
    return exp(-(d * d) / (w * w)) + 0.10 * exp(-d / (w * 7.0));
}
// polar fold into n sectors (mirrored)
vec2 foldN(vec2 p, float n) {
    float a = atan(p.y, p.x), r = length(p);
    float sec = TAU / n;
    a = mod(a + sec * 0.5, sec) - sec * 0.5;
    a = abs(a);
    return r * vec2(cos(a), sin(a));
}
float sstep(float a, float b, float x) { return smoothstep(a, b, x); }
