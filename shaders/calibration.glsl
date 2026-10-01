// Projection calibration pattern : fine/coarse grid, diagonals, centre cross, coloured corner discs, safe-area frame.
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec2 res = uTDOutputInfo.res.zw;
    float px = 1.0 / res.y;
    vec3 col = vec3(0.02);
    vec2 g16 = abs(fract(uv * vec2(16.0, 9.0) + 0.5) - 0.5) / vec2(16.0, 9.0) * res;
    vec2 g4 = abs(fract(uv * vec2(4.0, 2.25) + 0.5) - 0.5) / vec2(4.0, 2.25) * res;
    col += vec3(0.22) * (1.0 - smoothstep(0.5, 1.5, min(g16.x, g16.y)));
    col += vec3(0.55) * (1.0 - smoothstep(0.8, 2.2, min(g4.x, g4.y)));
    float diag = min(abs(uv.y * res.y - uv.x * res.x * res.y / res.x), abs((1.0 - uv.y) * res.y - uv.x * res.y));
    col += vec3(0.0, 0.7, 0.7) * (1.0 - smoothstep(0.7, 2.0, diag));
    vec2 c = abs(uv - 0.5) * res;
    col += vec3(1.0) * (1.0 - smoothstep(1.0, 3.0, min(c.x, c.y))) * step(max(c.x, c.y), 80.0);
    col += vec3(1.0, 1.0, 0.0) * (1.0 - smoothstep(1.0, 3.0, abs(length(uv * res - 0.5 * res) - 0.22 * res.y)));
    vec2 b = min(uv, 1.0 - uv) * res;
    col += vec3(1.0, 0.2, 0.9) * (1.0 - smoothstep(1.0, 4.0, min(b.x, b.y)));
    vec2 sa = min(abs(uv - 0.05), abs(uv - 0.95)) * res;
    col += vec3(0.2, 1.0, 0.3) * (1.0 - smoothstep(0.5, 2.0, min(sa.x, sa.y))) * step(0.05, uv.x) * step(uv.x, 0.95) * step(0.05, uv.y) * step(uv.y, 0.95) * 0.6;
    vec2 cr[4] = vec2[](vec2(0.0, 1.0), vec2(1.0, 1.0), vec2(0.0, 0.0), vec2(1.0, 0.0));
    vec3 cc[4] = vec3[](vec3(1, 0.1, 0.1), vec3(0.1, 1, 0.1), vec3(0.2, 0.4, 1), vec3(1, 1, 0.1));
    for (int i = 0; i < 4; i++) {
        float d = length((uv - cr[i]) * res);
        col = mix(col, cc[i], smoothstep(70.0, 66.0, d));
        col = mix(col, vec3(0.0), smoothstep(30.0, 26.0, d));
    }
    fragColor = vec4(col, 1.0);
}
