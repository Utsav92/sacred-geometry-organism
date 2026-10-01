// Kaleidoscope-style recursive symmetry around the head.   inputs: 0 image, 1 uniforms
// amount rises with stillness / order and with transcendence so the chaos resolves into radial symmetry.
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec4 hd = U(S_HEAD);
    float amt = clamp(U(23).x, 0.0, 1.0);
    float sym = max(floor(U(S_GEO0).x + 0.5), 3.0);
    float rot = U(S_GEO0).z * 0.2;
    vec2 asp = vec2(ASP(), 1.0);
    vec2 d = (uv - hd.xy) * asp;
    float r = length(d), a = atan(d.y, d.x) + rot;
    float sec = TAU / sym;
    a = mod(a, sec);
    a = abs(a - sec * 0.5);
    vec2 f = r * vec2(cos(a - rot), sin(a - rot));
    vec2 fuv = clamp(hd.xy + f / asp, vec2(0.001), vec2(0.999));
    vec3 c0 = texture(sTD2DInputs[0], uv).rgb;
    vec3 c1 = texture(sTD2DInputs[0], fuv).rgb;
    fragColor = vec4(mix(c0, max(c0, c1 * 0.8), amt), 1.0);
}
