// Final projector grade : black level, gamma, brightness (+ tiny dither to kill banding in dark gradients).
// inputs: 0 image, 1 uniforms
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec3 c = texture(sTD2DInputs[0], uv).rgb;
    vec4 prj = U(S_PRJ);                    // brightness, gamma, black level
    c = max(c - prj.z, 0.0) / max(1.0 - prj.z, 1e-3);
    c = pow(max(c, 0.0), vec3(1.0 / max(prj.y, 0.05)));
    c *= prj.x;
    c += (hash21(uv * uTDOutputInfo.res.zw + U(S_SC2).w) - 0.5) / 255.0;
    fragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}
