// GEOMETRY ENGINE  -  procedural sacred geometry.  Builder prepends:  #define GROUP 0|1|2   and common.glsl
//   GROUP 0 : body-attached  (Flower of Life @torso, Metatron @left hand, Sri Yantra @right hand, vesica @between hands, crown)
//   GROUP 1 : head-centred   (radial mandala, Fibonacci spiral / phyllotaxis, recursive fractal)
//   GROUP 2 : far field      (hex lattice, concentric pulses, nested rotating polygons)
// Output: additive light.  rgb = colour, a = peak intensity (used as matte for body/aura modes).
layout(location = 0) out vec4 fragColor;

// ------------------------------------------------------------------------------ individual systems
float flowerOfLife(vec2 p, float R, float rot, float rings, float w, out float outerRing) {
    p = rot2(rot) * p;
    vec2 a1 = vec2(R, 0.0), a2 = vec2(R * 0.5, R * 0.8660254);
    float j0 = p.y / a2.y;
    float i0 = (p.x - j0 * a2.x) / R;
    vec2 base = floor(vec2(i0, j0) + 0.5);
    float I = 0.0;
    for (int di = -2; di <= 2; di++)
        for (int dj = -2; dj <= 2; dj++) {
            vec2 ij = base + vec2(di, dj);
            float hd = max(max(abs(ij.x), abs(ij.y)), abs(ij.x + ij.y));
            float wr = clamp(rings - hd + 1.0, 0.0, 1.0);
            if (wr <= 0.0) continue;
            vec2 c = ij.x * a1 + ij.y * a2;
            float d = abs(length(p - c) - R);
            I = max(I, lineI(d, w) * wr * (hd < 0.5 ? 1.25 : 1.0));
        }
    float Ro = R * (rings + 1.0);
    outerRing = lineI(abs(length(p) - Ro), w * 1.3) * clamp(rings, 0.0, 1.0);
    return I;
}

vec2 metaPt(int i, float d, float rot) {
    if (i == 0) return vec2(0.0);
    float k = float(i <= 6 ? i - 1 : i - 7);
    float a = rot + k * PI / 3.0;
    return (i <= 6 ? d : 2.0 * d) * vec2(cos(a), sin(a));
}
float metatron(vec2 p, float Rm, float rot, float w, float grow) {
    float d2 = 2.0 * Rm;
    if (length(p) > 4.0 * d2 * 0.5 + Rm * 1.6) return 0.0;
    float I = 0.0;
    for (int i = 0; i < 13; i++) {
        vec2 ci = metaPt(i, d2, rot);
        I = max(I, lineI(abs(length(p - ci) - Rm), w) * 0.8 * grow);
        I = max(I, exp(-dot(p - ci, p - ci) / (w * w * 5.0)) * 1.3 * grow);
        for (int j = 0; j < 13; j++) {
            if (j <= i) continue;
            I = max(I, lineI(sdSeg(p, ci, metaPt(j, d2, rot)), w * 0.75) * 0.55 * grow);
        }
    }
    return I;
}

float petalRing(vec2 p, float n, float r0, float len, float wid, float w) {
    vec2 f = foldN(p, n);
    vec2 c1 = vec2(r0, wid), c2 = vec2(r0, -wid);
    float rad = sqrt(len * len + wid * wid);
    float lens = max(length(f - c1) - rad, length(f - c2) - rad);
    return lineI(lens, w);
}

float sriYantra(vec2 p, float R, float rot, float w, float grow) {
    p = rot2(rot) * p;
    if (length(p) > R * 1.35) return 0.0;
    float I = 0.0;
    // 4 upward + 5 downward interlocking triangles
    for (int i = 0; i < 4; i++) {
        float s = R * (0.86 - 0.17 * float(i)) * grow;
        I = max(I, lineI(polyD(p - vec2(0.0, -0.10 * s), 3.0, s, PI * 0.5), w));
    }
    for (int i = 0; i < 5; i++) {
        float s = R * (0.78 - 0.135 * float(i)) * grow;
        I = max(I, lineI(polyD(p - vec2(0.0, 0.08 * s), 3.0, s, -PI * 0.5), w));
    }
    I = max(I, lineI(ringD(p, vec2(0.0), R * 0.92 * grow), w) * 0.8);
    I = max(I, lineI(ringD(p, vec2(0.0), R * 1.0 * grow), w) * 0.5);
    I = max(I, petalRing(p, 8.0, R * 0.98 * grow, R * 0.12 * grow, R * 0.06 * grow, w) * 0.6);
    I = max(I, petalRing(p, 16.0, R * 1.08 * grow, R * 0.12 * grow, R * 0.045 * grow, w) * 0.5);
    I = max(I, lineI(polyD(p, 4.0, R * 1.22 * grow, PI * 0.25), w) * 0.7);
    I = max(I, exp(-dot(p, p) / (w * w * 8.0)) * 1.4);
    return I;
}

float vesica(vec2 p, vec2 A, vec2 B, float w, float grow, out float pts) {
    float r = length(B - A);
    pts = 0.0;
    if (r < 0.02) return 0.0;
    r *= grow;
    vec2 M = 0.5 * (A + B);
    vec2 dir = normalize(B - A), nrm = vec2(-dir.y, dir.x);
    float I = 0.0;
    I = max(I, lineI(abs(length(p - A) - r), w) * 0.55);
    I = max(I, lineI(abs(length(p - B) - r), w) * 0.55);
    // nested vesica chain along the axis
    for (int k = 0; k < 4; k++) {
        float s = 1.0 - float(k) * 0.22;
        float rr = r * s;
        vec2 a = M - dir * rr * 0.5, b = M + dir * rr * 0.5;
        float lens = max(length(p - a) - rr, length(p - b) - rr);
        I = max(I, lineI(lens, w) * (k == 0 ? 1.1 : 0.65));
    }
    float hh = r * 0.8660254;
    I = max(I, lineI(sdSeg(p, M - nrm * hh, M + nrm * hh), w * 0.8) * 0.6);
    I = max(I, lineI(sdSeg(p, A, B), w * 0.7) * 0.5);
    pts = max(exp(-dot(p - (M + nrm * hh), p - (M + nrm * hh)) / (w * w * 14.0)),
              exp(-dot(p - (M - nrm * hh), p - (M - nrm * hh)) / (w * w * 14.0)));
    return I;
}

float mandala(vec2 p, float Rm, float n, float layers, float w, float rot, float T) {
    p = rot2(rot) * p;
    vec2 f = foldN(p, n);
    float I = 0.0;
    for (int k = 0; k < 8; k++) {
        float fk = float(k);
        float wk = clamp(layers - fk, 0.0, 1.0);
        if (wk <= 0.0) break;
        float rk = Rm * (0.16 + 0.135 * fk);
        I = max(I, lineI(abs(length(p) - rk), w) * 0.45 * wk);                      // ring
        int m = k - 3 * (k / 3);
        if (m == 0)      I = max(I, petalRing(p, n, rk, Rm * 0.12, Rm * 0.05, w) * wk);
        else if (m == 1) I = max(I, lineI(length(f - vec2(rk, 0.0)) - Rm * 0.035, w) * wk);
        else             I = max(I, lineI(polyD(p, n, rk, 0.0), w * 0.9) * 0.8 * wk);
        I = max(I, lineI(sdSeg(f, vec2(rk, 0.0), vec2(rk + Rm * 0.135, 0.0)), w * 0.6) * 0.5 * wk);
        I = max(I, lineI(length(f - vec2(rk, 0.0)) - Rm * 0.02, w) * wk);
    }
    I = max(I, lineI(f.y, w * 0.5) * 0.35 * step(0.0, f.x) * step(length(f), Rm * (0.16 + 0.135 * layers)));
    return I;
}

float fibonacci(vec2 p, float Rs, float rot, float complexity, float w, float T, out float dots) {
    p = rot2(rot) * p;
    float r = length(p) + 1e-5;
    float th = atan(p.y, p.x);
    float k = 2.0 * log(PHI) / PI;                       // golden spiral : r = a * exp(k * theta)
    float a = Rs * 0.04;
    float I = 0.0;
    for (int arm = 0; arm < 2; arm++) {
        float s = arm == 0 ? 1.0 : -1.0;
        float t = log(r / a) / k;                            // theta such that r matches
        float tt = s * th;
        float n = floor((t - tt) / TAU + 0.5);
        float best = 1e9;
        for (int q = -1; q <= 1; q++) {
            float thq = tt + (n + float(q)) * TAU;
            float rr = a * exp(k * thq);
            best = min(best, abs(r - rr));
        }
        float lim = Rs * 1.15;
        I = max(I, lineI(best * 0.85, w) * step(r, lim) * (arm == 0 ? 0.9 : 0.55));
    }
    // phyllotaxis dots (golden angle)
    float N = 40.0 + 160.0 * complexity;
    float c = Rs * 1.1 / sqrt(N);
    float n0 = floor(r * r / (c * c));
    float dmin = 1e9;
    float offs[7] = float[](0.0, 8.0, -8.0, 13.0, -13.0, 21.0, -21.0);
    for (int i = 0; i < 7; i++) {
        float nn = n0 + offs[i];
        if (nn < 0.0 || nn > N) continue;
        float ang = nn * 2.39996323;
        vec2 dp = c * sqrt(nn) * vec2(cos(ang), sin(ang));
        dmin = min(dmin, length(p - dp));
    }
    dots = exp(-dmin * dmin / (w * w * 9.0)) + 0.1 * exp(-dmin / (w * 6.0));
    return I;
}

float fractalLines(vec2 p, int it, float energy, float T, float scale) {
    float d = 1e9, s = 1.0;
    p *= 1.15 / max(scale, 0.2);
    for (int i = 0; i < 10; i++) {
        if (i >= it) break;
        p = abs(p) - vec2(0.34, 0.16 + 0.10 * energy);
        p = rot2(0.52 + 0.22 * sin(T * 0.17 + float(i) * 0.7) + energy * 0.25) * p;
        p *= 1.48; s *= 1.48;
        d = min(d, abs(length(p) - 0.42) / s);
        d = min(d, abs(p.y) / s);
    }
    return d * max(scale, 0.2) / 1.15;
}

vec4 hexGrid(vec2 uv) {
    vec2 r = vec2(1.0, 1.7320508), h = r * 0.5;
    vec2 a = mod(uv, r) - h, b = mod(uv - h, r) - h;
    vec2 gv = dot(a, a) < dot(b, b) ? a : b;
    return vec4(gv, uv - gv);
}
float hexDist(vec2 p) { p = abs(p); return max(dot(p, vec2(0.5, 0.8660254)), p.x); }

// ------------------------------------------------------------------------------ main
void main() {
    vec2 uv = vUV.st;
    vec2 q = toQ(uv);
    float px = 2.0 / uTDOutputInfo.res.w;
    float w = px * 1.5 * (1.0 + 0.8 * U(S_GEO3).z);          // thicker lines in performance mode keeps them readable

    vec4 hlv = U(S_HL), hrv = U(S_HR), hdv = U(S_HEAD), tov = U(S_TORSO);
    vec4 sc0 = U(S_SC0), sc1 = U(S_SC1), sc2 = U(S_SC2);
    vec4 st0 = U(S_ST0), st1 = U(S_ST1);
    vec4 g0 = U(S_GEO0), g1 = U(S_GEO1), g2 = U(S_GEO2), g3 = U(S_GEO3);

    float T = sc2.w;
    float order = st1.z;                  // 0 chaotic .. 1 perfectly symmetric
    float sing = sc2.x, crown = sc2.y, burst = sc2.z;
    float sym = floor(g0.x + 0.5);
    float cplx = g0.y, rotA = g0.z, scl = g0.w;
    float expand = g3.w;                  // hand-distance driven expansion (0.2 .. 1.6)

    vec2 hl = toQ(hlv.xy), hr = toQ(hrv.xy), hd = toQ(hdv.xy), to = toQ(tov.xy);
    // stillness -> hands settle into mirror-symmetric positions around the head axis
    float axis = hd.x;
    vec2 hlS = vec2(axis - 0.5 * abs(hr.x - hl.x), 0.5 * (hl.y + hr.y));
    vec2 hrS = vec2(axis + 0.5 * abs(hr.x - hl.x), 0.5 * (hl.y + hr.y));
    hl = mix(hl, hlS, order * 0.9);
    hr = mix(hr, hrS, order * 0.9);

    // singularity pinch : everything is pulled toward the hands' midpoint
    vec2 sp = 0.5 * (hl + hr);
    vec2 qs = q;
    if (sing > 0.001) {
        vec2 dq = q - sp;
        float r = length(dq) + 1e-5;
        qs = sp + dq / r * pow(r, 1.0 - 0.62 * sing);
        qs = mix(q, qs, sing);
    }

    vec3 col = vec3(0.0);
    float peak = 0.0;
    float hueT = U(S_PSY1).w;

#if GROUP == 0
    // ---------- Flower of Life  (torso origin)
    float wF = g1.x;
    if (wF > 0.01) {
        float outer;
        float R = (0.085 + 0.07 * expand) * scl;
        float rings = 1.0 + 2.2 * cplx + 0.8 * st0.w;
        float I = flowerOfLife(qs - to, R, rotA * 0.35 + T * 0.02, rings, w, outer);
        float v = (I + outer * 0.8) * wF;
        col += v * pal(0.02 + hueT);
        peak = max(peak, v);
    }
    // ---------- Metatron's cube  (left hand)
    float wM = g1.y;
    if (wM > 0.01) {
        float Rm = (0.035 + 0.05 * expand) * scl;
        float I = metatron(qs - hl, Rm, -rotA * 0.5, w, 1.0) * wM;
        col += I * pal(0.33 + hueT);
        peak = max(peak, I);
    }
    // ---------- Sri Yantra  (right hand)
    float wY = g1.z;
    if (wY > 0.01) {
        float R = (0.12 + 0.13 * expand) * scl;
        float I = sriYantra(qs - hr, R, rotA * 0.25, w, 1.0) * wY;
        col += I * pal(0.62 + hueT);
        peak = max(peak, I);
    }
    // ---------- Vesica piscis between hands
    float wV = g2.x;
    if (wV > 0.01) {
        float pts;
        float I = vesica(qs, hl, hr, w, 1.0, pts) * wV;
        col += (I + pts * wV * 1.4) * pal(0.12 + hueT);
        peak = max(peak, I);
    }
    // ---------- Crown mandala when hands rise above the head
    if (crown > 0.01) {
        vec2 cp = qs - (hd + vec2(0.0, 0.30 * scl));
        float rc = length(cp);
        vec2 f = foldN(cp, 12.0);
        float Rc = (0.32 + 0.2 * expand) * crown * scl;
        float I = 0.0;
        for (int k = 0; k < 4; k++) {
            float rk = Rc * (0.35 + 0.2 * float(k));
            I = max(I, lineI(abs(rc - rk), w) * 0.7);
            I = max(I, petalRing(cp, 12.0, rk, Rc * 0.1, Rc * 0.04, w) * 0.9);
        }
        I = max(I, lineI(f.y, w * 0.6) * 0.8 * step(rc, Rc * 1.1));
        I = max(I, lineI(polyD(cp, 12.0, Rc * 1.05, T * 0.1), w));
        I *= crown;
        col += I * pal(0.9 + hueT * 1.3);
        peak = max(peak, I);
    }
    // ---------- singularity core
    if (sing > 0.001) {
        vec2 dq = q - sp;
        float r = length(dq);
        float core = exp(-r * r / (0.0016 + 0.0012 * sing)) * 2.5 * sing;
        float ang = atan(dq.y, dq.x);
        float rays = pow(abs(cos(ang * 12.0 + T * 2.0)), 24.0) * exp(-r * 3.0) * sing;
        col += (core + rays) * vec3(1.0, 0.9, 0.8);
        peak = max(peak, core);
    }
#elif GROUP == 1
    // ---------- head-centred radial systems
    vec2 P = qs - hd;
    float ex = (0.6 + 0.9 * expand) * scl;
    // radial symmetry: blend the raw plane with an N-fold kaleidoscope as order rises
    float wMa = g2.z;
    if (wMa > 0.01) {
        float layers = 2.0 + 5.5 * cplx + 1.0 * st0.w;
        float I = mandala(P, 0.34 * ex, max(sym, 3.0), layers, w, rotA * 0.5, T) * wMa;
        col += I * pal(0.5 + hueT);
        peak = max(peak, I);
    }
    float wFi = g1.w;
    if (wFi > 0.01) {
        float dots;
        float I = fibonacci(P, 0.55 * ex, -rotA * 0.3, cplx, w, T, dots);
        float v = (I + dots * 0.9) * wFi;
        col += v * pal(0.18 + hueT);
        peak = max(peak, v);
    }
    float wFr = g2.w;
    if (wFr > 0.01) {
        int it = int(clamp(g3.x, 2.0, 10.0));
        float d = fractalLines(P, it, clamp(sc0.z, 0.0, 1.5), T, 0.8 * ex);
        float I = lineI(d, w) * wFr;
        col += I * pal(0.75 + hueT + d * 3.0);
        peak = max(peak, I);
    }
#else
    // ---------- far field : hex lattice, concentric pulses, nested rotating polygons
    float wH = g2.y;
    vec2 P = qs - hd;
    if (wH > 0.01) {
        vec2 c1 = qs - hl, c2 = qs - hr;
        vec2 warp = (c1 * exp(-dot(c1, c1) * 3.0) + c2 * exp(-dot(c2, c2) * 3.0)) * 0.35;
        vec2 hp = (qs - warp) * (2.2 + 1.2 * cplx) + vec2(0.0, T * 0.05);
        vec4 hg = hexGrid(rot2(rotA * 0.1) * hp);
        float ed = 0.5 - hexDist(hg.xy);
        float I = lineI(ed / (2.2 + 1.2 * cplx), w * 0.8) * wH * 0.55;
        float fade = exp(-dot(qs - to, qs - to) * 0.6);
        col += I * fade * pal(0.45 + hueT + hash21(hg.zw) * 0.25);
        peak = max(peak, I * fade);
    }
    // pulsing concentric rings flowing out of the head
    float I2 = 0.0;
    for (int k = 0; k < 6; k++) {
        float ph = fract(T * 0.12 * (0.5 + sc0.z) + float(k) / 6.0);
        float rr = ph * 1.9 * (0.6 + expand);
        I2 = max(I2, lineI(abs(length(P) - rr), w * 1.2) * (1.0 - ph) * 0.8);
    }
    // nested rotating polygons
    float I3 = 0.0;
    for (int k = 0; k < 6; k++) {
        float fk = float(k);
        float nk = 3.0 + fk;
        float Rk = (0.28 + 0.16 * fk) * (0.7 + 0.6 * expand) * scl;
        float s = ((k / 2) * 2 == k) ? 1.0 : -1.0;
        float wk = clamp(cplx * 7.0 - fk + 1.0, 0.0, 1.0);
        I3 = max(I3, lineI(polyD(P, nk, Rk, s * rotA * (0.4 + 0.1 * fk)), w) * 0.55 * wk);
        I3 = max(I3, lineI(ringD(P, vec2(0.0), Rk), w) * 0.18 * wk);
    }
    float v = (I2 * 0.7 + I3) * (0.35 + 0.65 * g2.z + 0.4 * (st0.x + st0.w));
    col += v * pal(0.58 + hueT);
    peak = max(peak, v);
#endif

    fragColor = vec4(col, clamp(peak, 0.0, 1.0));
}
