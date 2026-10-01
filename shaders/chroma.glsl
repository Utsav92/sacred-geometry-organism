// Chromatic separation, prismatic dispersion and diffraction ghosts.  inputs: 0 image, 1 uniforms
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec4 hd = U(S_HEAD);
    vec4 psy1 = U(S_PSY1);
    float energy = clamp(U(S_SC0).z, 0.0, 1.5), burst = U(S_SC2).z, T = U(S_SC2).w;
    vec2 d = uv - hd.xy;
    float r = length(d * vec2(ASP(), 1.0));
    float amt = psy1.x * 0.0030 * (1.0 + 0.9 * energy + 0.6 * burst);
    vec3 col;
    col.r = texture(sTD2DInputs[0], uv + d * amt * (1.0 + r)).r;
    col.g = texture(sTD2DInputs[0], uv).g;
    col.b = texture(sTD2DInputs[0], uv - d * amt * (1.0 + r)).b;
    // diffraction ghosts : faint spectral copies of bright structure, stepped outward from the head
    vec3 gh = vec3(0.0);
    for (int k = 1; k <= 5; k++) {
        float fk = float(k);
        vec3 s = texture(sTD2DInputs[0], uv - d * amt * fk * 3.0).rgb;
        float l = dot(s, vec3(0.3, 0.5, 0.2));
        gh += pal(fk * 0.17 + T * 0.04 + psy1.w) * l * (0.045 / fk);
    }
    fragColor = vec4(col + gh * psy1.x, 1.0);
}
