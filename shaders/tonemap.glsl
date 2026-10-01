// Feedback output stage : keeps the crisp geometry (psy) on top of the luminous trails (fb), then soft-shoulder tonemap.
// inputs: 0 psy (crisp)  1 feedback accumulation  2 uniforms
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec3 psy = texture(sTD2DInputs[0], uv).rgb;
    vec3 fb = texture(sTD2DInputs[1], uv).rgb;
    float trail = clamp(U(S_PSY0).x, 0.0, 1.0);
    vec3 trails = max(fb - psy, vec3(0.0));                 // luminous trails live behind the crisp frame
    vec3 x = psy + trails * (0.45 + 0.35 * trail);
    x = 1.0 - exp(-x * 1.25);                       // soft shoulder, never clips ugly
    fragColor = vec4(x, 1.0);
}
