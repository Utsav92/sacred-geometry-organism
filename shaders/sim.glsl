// PARTICLE SIMULATION  (256x256 float texture = 65536 particles).   texel = (x, y, vx, vy) in q-space.
// inputs: 0 previous state (Feedback TOP) , 1 held silhouette mask , 2 uniforms
// Emitters : hands, head, body contour (ray-marched on the silhouette), Flower-of-Life vertices, Metatron points,
//            vesica intersections, mandala ring vertices.
// Behaviour: fast hand motion scatters, slow motion orbits the geometry, stillness pulls particles onto symmetric
//            constellation targets, bursts blast outward, curl-noise turbulence everywhere.
layout(location = 0) out vec4 fragColor;

vec2 uvQ(vec2 q) { return q / (vec2(ASP(), 1.0) * 2.0) + 0.5; }
vec2 metaPt(int i, float d, float rot) {
    if (i == 0) return vec2(0.0);
    float k = float(i <= 6 ? i - 1 : i - 7);
    float a = rot + k * PI / 3.0;
    return (i <= 6 ? d : 2.0 * d) * vec2(cos(a), sin(a));
}

void main() {
    float DT = U(40).x;
    ivec2 ip = ivec2(gl_FragCoord.xy);
    int W = int(uTDOutputInfo.res.z);
    float id = float(ip.y * W + ip.x);
    float N = uTDOutputInfo.res.z * uTDOutputInfo.res.w;
    vec4 s = texelFetch(sTD2DInputs[0], ip, 0);

    vec4 sc0 = U(S_SC0), sc2 = U(S_SC2), st1 = U(S_ST1), g0 = U(S_GEO0), g3 = U(S_GEO3);
    vec4 par0 = U(S_PAR0), par1 = U(S_PAR1);
    float T = sc2.w;
    float energy = sc0.z, order = st1.z;
    float act = par0.x, velK = par0.y, turb = par0.z, att = par0.w;
    float life = max(par1.x, 0.3);
    float expand = g3.w, scl = g0.w, rotA = g0.z, sym = max(floor(g0.x + 0.5), 3.0);

    vec2 hl = toQ(U(S_HL).xy), hr = toQ(U(S_HR).xy), hd = toQ(U(S_HEAD).xy), to = toQ(U(S_TORSO).xy);
    vec2 hlv = U(S_HL).zw, hrv = U(S_HR).zw;
    float handSpeed = max(length(hlv * vec2(ASP(), 1.0)), length(hrv * vec2(ASP(), 1.0)));

    if (id / N > act) { fragColor = vec4(0.0, 100.0, 0.0, 0.0); return; }

    float seed = hash11(id * 0.37 + 1.3);
    float cyc = T / life + seed;
    float ph = fract(cyc), gen = floor(cyc);
    bool respawn = (ph < DT * 1.7 / life) || (dot(s, s) < 1e-9) || (abs(s.x) > 30.0) || (abs(s.y) > 30.0);

    vec2 p = s.xy, v = s.zw;

    if (respawn) {
        float r1 = hash11(id * 1.13 + gen * 7.1), r2 = hash11(id * 2.71 + gen * 3.3);
        float r3 = hash11(id * 5.17 + gen * 1.9), r4 = hash11(id * 9.31 + gen * 4.7);
        float dis = U(21).w + st1.y;                                  // exit -> everything comes off the silhouette
        float e = r1;
        if (r4 < clamp(dis * 1.4, 0.0, 0.85)) e = 0.40;               // contour emitter
        float ang = r2 * TAU;
        vec2 dir = vec2(cos(ang), sin(ang));
        float spd = (0.15 + 0.55 * r3) * (0.5 + velK);
        float R = (0.085 + 0.07 * expand) * scl;
        float rotF = rotA * 0.35 + T * 0.02;
        if (e < 0.16) {                                               // left hand
            p = hl + dir * 0.02 * r3;
            v = hlv * vec2(ASP(), 1.0) * (0.6 + 0.8 * r3) + dir * spd * (1.0 + 2.5 * handSpeed);
        } else if (e < 0.32) {                                        // right hand
            p = hr + dir * 0.02 * r3;
            v = hrv * vec2(ASP(), 1.0) * (0.6 + 0.8 * r3) + dir * spd * (1.0 + 2.5 * handSpeed);
        } else if (e < 0.40) {                                        // head
            p = hd + dir * 0.03 * r3;
            v = dir * spd * 0.6;
        } else if (e < 0.62) {                                        // body contour
            bool found = false;
            vec2 q0 = to;
            for (int i = 1; i < 56; i++) {
                vec2 t = q0 + dir * (0.025 * float(i));
                vec2 tu = uvQ(t);
                if (tu.x < 0.0 || tu.x > 1.0 || tu.y < 0.0 || tu.y > 1.0) break;
                if (texture(sTD2DInputs[1], tu).r < 0.5) { p = t; found = true; break; }
            }
            if (!found) p = hd + dir * 0.05;
            v = dir * spd * 0.5 + curl(p * 3.0, T) * 0.05;
        } else if (e < 0.76) {                                        // Flower-of-Life vertices at the torso
            vec2 a1 = vec2(R, 0.0), a2 = vec2(R * 0.5, R * 0.8660254);
            float ii = floor(r2 * 5.0) - 2.0, jj = floor(r3 * 5.0) - 2.0;
            if (max(max(abs(ii), abs(jj)), abs(ii + jj)) > 2.0) { ii = 0.0; jj = 0.0; }
            p = to + rot2(-rotF) * (ii * a1 + jj * a2);
            v = dir * spd * 0.25;
        } else if (e < 0.86) {                                        // Metatron points at the left hand
            float Rm = (0.035 + 0.05 * expand) * scl;
            p = hl + metaPt(int(floor(r2 * 13.0)), 2.0 * Rm, -rotA * 0.5);
            v = dir * spd * 0.3;
        } else if (e < 0.93) {                                        // vesica piscis intersections
            vec2 d = hr - hl;
            float rr = length(d);
            vec2 nrm = rr > 1e-4 ? vec2(-d.y, d.x) / rr : vec2(0.0, 1.0);
            p = 0.5 * (hl + hr) + nrm * rr * 0.866 * (r2 > 0.5 ? 1.0 : -1.0);
            v = dir * spd * 0.5;
        } else {                                                      // mandala ring vertices at the head
            float ex = (0.6 + 0.9 * expand) * scl;
            float Rm = 0.34 * ex;
            float k = floor(r2 * 5.0);
            float jn = floor(r3 * sym);
            float a = jn * TAU / sym + rotA * 0.5;
            p = hd + (Rm * (0.16 + 0.135 * k)) * vec2(cos(a), sin(a));
            v = dir * spd * 0.2;
        }
    } else {
        // ------------------------------------------------------------------ forces
        vec2 f = vec2(0.0);
        // attractors at the hands (open palm pulls harder) and torso
        vec2 dl = hl - p, dr = hr - p, dt = to - p;
        f += att * dl / (dot(dl, dl) + 0.10) * (0.20 + 0.35 * U(21).x);
        f += att * dr / (dot(dr, dr) + 0.10) * (0.20 + 0.35 * U(21).y);
        f += att * dt / (dot(dt, dt) + 0.30) * 0.12;
        // slow movement : orbit around the geometry (torso / head)
        float slow = 1.0 - smoothstep(0.25, 1.1, energy);
        vec2 rel = p - to;
        f += vec2(-rel.y, rel.x) / (length(rel) + 0.08) * 0.9 * slow * (0.4 + velK) * exp(-length(rel) * 0.7);
        vec2 relh = p - hd;
        f += vec2(relh.y, -relh.x) / (length(relh) + 0.08) * 0.5 * slow * (0.4 + velK) * exp(-length(relh) * 0.9);
        // organic turbulence (more with motion energy)
        f += curl(p * 1.7, T * 0.3 + id * 0.0) * turb * 1.6;
        // stillness : symmetric constellation
        float hr_ = hash11(id * 3.1), ha = hash11(id * 4.7), hc = hash11(id * 8.3);
        float ring = floor(hr_ * 6.0);
        float exr = (0.6 + 0.9 * expand) * scl;
        float rad = 0.5 * exr * (0.2 + 0.14 * ring);
        float a = (floor(ha * sym) + 0.5 * mod(ring, 2.0)) * TAU / sym + rotA * 0.3;
        vec2 ctr = hc < 0.55 ? hd : to;
        vec2 target = ctr + rad * vec2(cos(a), sin(a));
        f += (target - p) * order * order * 9.0;
        // burst : blast away from the fastest hand
        vec4 bs = U(22);
        if (bs.z > 0.5) {
            vec2 d = p - toQ(bs.xy);
            float l = length(d) + 1e-3;
            v += d / l * 45.0 * exp(-l * 1.6);
        }
        {   // lingering blast while the burst envelope decays
            vec2 d = p - toQ(U(22).xy);
            float l = length(d) + 1e-3;
            f += d / l * sc2.z * 5.5 * exp(-l * 0.6);
        }
        v += f * DT;
        v *= exp(-DT * (0.85 + 3.2 * order));
        p += v * DT * (0.5 + velK);
    }
    fragColor = vec4(p, v);
}
