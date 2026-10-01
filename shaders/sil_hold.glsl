// Silhouette HOLD / afterimage.  inputs: 0 previous hold (feedback), 1 live silhouette mask, 2 uniforms
// While a person is present the hold equals the live mask.  When they leave, the last silhouette stays as a glowing
// afterimage and erodes away through animated noise as the EXIT dissolve progresses.
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    float prev = texture(sTD2DInputs[0], uv).r;
    float cur = texture(sTD2DInputs[1], uv).r;
    float pres = U(S_SC1).y;                         // smoothed presence 0..1
    float dissolve = U(21).w;                         // EXIT dissolve progress 0..1
    float T = U(S_SC2).w;
    float n = vnoise(uv * vec2(ASP(), 1.0) * 9.0 + T * 0.15) * 0.65 + vnoise(uv * 31.0 - T * 0.2) * 0.35;
    float keep = smoothstep(dissolve * 1.1 - 0.15, dissolve * 1.1 + 0.05, n);
    float decay = exp(-U(40).x / 7.0);              // 7 s time constant, frame-rate independent
    float held = prev * mix(decay * keep, 0.0, pres);
    float o = max(cur, held);
    fragColor = vec4(vec3(o), 1.0);
}
