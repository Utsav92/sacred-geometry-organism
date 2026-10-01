// Synthetic participant : draws a body from the 13 joint slots.   VIEW 0 = white silhouette mask
//                                                                  VIEW 1 = fake "camera" picture (dark room + lit body)
layout(location = 0) out vec4 fragColor;

float cap(vec2 p, vec2 a, vec2 b, float r) { return sdSeg(p, a, b) - r; }
vec2 J(int i) { vec4 j = U(S_J0 + i); return vec2(j.x * ASP(), j.y); }

void main() {
    vec2 uv = vUV.st;
    vec2 p = vec2(uv.x * ASP(), uv.y);
    float pres = U(S_J0).z;

    vec2 head = J(0), lsh = J(1), rsh = J(2), lel = J(3), rel = J(4), lwr = J(5), rwr = J(6);
    vec2 lhip = J(7), rhip = J(8), lkn = J(9), rkn = J(10), lan = J(11), ran = J(12);
    vec2 msh = 0.5 * (lsh + rsh), mhip = 0.5 * (lhip + rhip);

    float d = 1e9;
    d = min(d, length(p - (head + vec2(0.0, 0.015))) - 0.048);               // head
    d = min(d, cap(p, head, msh, 0.020));                                     // neck
    d = min(d, cap(p, lsh, rsh, 0.030));                                      // shoulders
    d = min(d, cap(p, msh, mhip, 0.062));                                     // torso
    d = min(d, cap(p, lhip, rhip, 0.045));                                    // pelvis
    d = min(d, cap(p, lsh, lel, 0.026));  d = min(d, cap(p, lel, lwr, 0.021)); // arms
    d = min(d, cap(p, rsh, rel, 0.026));  d = min(d, cap(p, rel, rwr, 0.021));
    d = min(d, length(p - lwr) - 0.030);  d = min(d, length(p - rwr) - 0.030); // hands
    d = min(d, cap(p, lhip, lkn, 0.036)); d = min(d, cap(p, lkn, lan, 0.027)); // legs
    d = min(d, cap(p, rhip, rkn, 0.036)); d = min(d, cap(p, rkn, ran, 0.027));

    float m = smoothstep(0.004, -0.004, d) * pres;
#if VIEW == 1
    vec3 bg = mix(vec3(0.015, 0.02, 0.035), vec3(0.06, 0.07, 0.10), uv.y) * (1.0 - 0.5 * length(uv - 0.5));
    float rim = smoothstep(0.02, -0.02, d) * 0.5;
    vec3 body = mix(vec3(0.30, 0.34, 0.45), vec3(0.65, 0.70, 0.85), clamp(-d * 14.0, 0.0, 1.0)) + rim * 0.2;
    vec3 col = mix(bg, body, m) + 0.015 * (hash21(uv * 800.0 + U(S_SC2).w) - 0.5);
    fragColor = vec4(col, 1.0);
#else
    fragColor = vec4(vec3(m), 1.0);
#endif
}
