// SCENE COMPOSITOR : 3D geometry scene + particles + participant silhouette
// inputs: 0 scene3d  1 particles  2 held silhouette  3 contour  4 halo  5 uniforms
//   BODY MODE : geometry lives inside the silhouette    AURA MODE : geometry radiates outward from the body
//   (GEO3.y blends continuously between them; state machine drives it in AUTO)
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec3 scene = texture(sTD2DInputs[0], uv).rgb;
    vec3 par = texture(sTD2DInputs[1], uv).rgb;
    float sil = texture(sTD2DInputs[2], uv).r;
    float contour = texture(sTD2DInputs[3], uv).r;
    float halo = texture(sTD2DInputs[4], uv).r;

    vec4 st0 = U(S_ST0), st1 = U(S_ST1), g3 = U(S_GEO3), sc0 = U(S_SC0);
    float T = U(S_SC2).w;
    float aura = g3.y;
    float hue = U(S_PSY1).w;

    float reach = 0.55 + 0.45 * clamp(st0.y * 0.6 + st0.z + st0.w + st1.y, 0.0, 1.0);   // aura grows as the participant awakens
    float mBody = smoothstep(0.1, 0.7, sil);
    float mAura = clamp(smoothstep(1.0 - reach * 0.85, 1.0, halo * 1.3) * (1.0 - sil) + 0.0, 0.0, 1.0);
    float mask = mix(mBody, mAura, aura);

    // visibility floor : the dormant universe is always faintly there, fully revealed in IDLE / TRANSCENDENCE
    float vis = clamp(0.30 + 0.70 * (st0.x + 0.55 * st1.x + 0.95 * st0.w), 0.0, 1.0);
    // exposure compensation : many layers stack up in TRANSCENDENCE, keep the picture readable
    float expo = mix(1.0, 0.42, st0.w) * mix(1.0, 0.8, st1.x);
    vec3 col = scene * (vis + (1.0 - vis) * mask * 1.5) * expo;

    // luminous contour around the participant
    vec3 cc = pal(T * 0.03 + hue + uv.y * 0.35);
    col += cc * contour * (0.85 + 0.8 * clamp(sc0.z, 0.0, 1.5) + 1.4 * st0.w);
    col += pal(hue + 0.5) * sil * 0.045 * (0.4 + aura);

    col += par * mix(1.0, 0.7, st0.w);
    fragColor = vec4(col, 1.0);
}
