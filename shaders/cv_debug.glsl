// CV debug view : camera (dimmed) + silhouette tint + contour + skeleton overlay.
// inputs: 0 camera, 1 silhouette mask, 2 contour, 3 skeleton (rgba premult), 4 uniforms
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec3 cam = texture(sTD2DInputs[0], uv).rgb;
    float m = texture(sTD2DInputs[1], uv).r;
    float e = texture(sTD2DInputs[2], uv).r;
    vec4 sk = texture(sTD2DInputs[3], uv);
    vec3 col = cam * 0.55;
    col = mix(col, col * 0.4 + vec3(0.05, 0.55, 0.8) * 0.6, m * 0.55);
    col += vec3(0.9, 1.0, 1.0) * e * 0.9;
    col = col * (1.0 - sk.a) + sk.rgb;
    // tracking markers : head / hands / torso
    vec2 p = vec2(uv.x * ASP(), uv.y);
    vec4 h = U(S_HEAD), l = U(S_HL), r = U(S_HR), t = U(S_TORSO);
    float px = 1.0 / uTDOutputInfo.res.w;
    vec2 pts[4] = vec2[](vec2(h.x * ASP(), h.y), vec2(l.x * ASP(), l.y), vec2(r.x * ASP(), r.y), vec2(t.x * ASP(), t.y));
    vec3 cols[4] = vec3[](vec3(1, 1, 0), vec3(0, 1, 0.4), vec3(1, 0.3, 0.3), vec3(0.4, 0.6, 1));
    for (int i = 0; i < 4; i++) {
        float d = abs(length(p - pts[i]) - 0.03);
        col += cols[i] * smoothstep(px * 2.5, 0.0, d);
    }
    vec4 bb = U(S_BBOX);
    vec2 a = vec2(bb.x * ASP(), bb.y), b = vec2(bb.z * ASP(), bb.w);
    vec2 dd = abs(p - 0.5 * (a + b)) - 0.5 * (b - a);
    float box = abs(max(dd.x, dd.y));
    col += vec3(1.0, 0.8, 0.2) * smoothstep(px * 1.5, 0.0, box) * 0.7;
    fragColor = vec4(col, 1.0);
}
