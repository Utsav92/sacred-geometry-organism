// Skeleton overlay: bones + joints drawn from the 13 joint slots.  RGBA (premultiplied), transparent background.
layout(location = 0) out vec4 fragColor;

vec2 J(int i) { vec4 j = U(S_J0 + i); return vec2(j.x * ASP(), j.y); }

void main() {
    vec2 uv = vUV.st;
    vec2 p = vec2(uv.x * ASP(), uv.y);
    float pres = U(S_J0).z;
    float px = 1.0 / uTDOutputInfo.res.w;
    float w = px * 1.6;
    // bones : head-msh, shoulders, arms, torso sides, hips, legs
    int A[12] = int[](1, 3, 2, 4, 1, 2, 1, 2, 7, 7, 9, 8);
    int B[12] = int[](3, 5, 4, 6, 7, 8, 2, 8, 8, 9, 11, 10);
    float I = 0.0;
    for (int i = 0; i < 12; i++) I = max(I, exp(-pow(sdSeg(p, J(A[i]), J(B[i])) / w, 2.0)));
    I = max(I, exp(-pow(sdSeg(p, J(8), J(10)) / w, 2.0)));
    I = max(I, exp(-pow(sdSeg(p, J(10), J(12)) / w, 2.0)));
    vec2 msh = 0.5 * (J(1) + J(2));
    I = max(I, exp(-pow(sdSeg(p, J(0), msh) / w, 2.0)));
    float dots = 0.0;
    for (int i = 0; i < 13; i++) {
        float r = (i == 5 || i == 6) ? 0.016 : (i == 0 ? 0.02 : 0.009);
        dots = max(dots, smoothstep(r + w, r - w, length(p - J(i))));
    }
    vec3 col = vec3(0.2, 1.0, 0.8) * I + vec3(1.0, 0.35, 0.7) * dots;
    float a = clamp(max(I, dots), 0.0, 1.0) * pres;
    fragColor = vec4(col * pres, a);
}
