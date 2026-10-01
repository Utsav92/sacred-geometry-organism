// Operator overlays on the output.  inputs: 0 art  1 CV debug picture  2 skeleton (premult rgba)  3 silhouette  4 HUD text  5 uniforms
//   CV debug view      : replaces the picture with the camera / segmentation / tracking diagnostic
//   skeleton overlay   : bones + joints drawn over the art
//   silhouette preview : picture-in-picture of the participant mask
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec4 flg = U(S_FLG);                         // cvdebug, skeleton, silpreview, hq
    vec3 col = texture(sTD2DInputs[0], uv).rgb;
    if (flg.x > 0.5) col = texture(sTD2DInputs[1], uv).rgb;
    if (flg.y > 0.5) {
        vec4 sk = texture(sTD2DInputs[2], uv);
        col = col * (1.0 - sk.a) + sk.rgb;
    }
    if (flg.z > 0.5) {
        vec2 puv = (uv - vec2(0.015, 0.02)) / vec2(0.24, 0.135);
        if (puv.x > 0.0 && puv.x < 1.0 && puv.y > 0.0 && puv.y < 1.0) {
            float m = texture(sTD2DInputs[3], puv).r;
            col = mix(vec3(0.02, 0.02, 0.05), vec3(0.85, 0.95, 1.0), m);
            vec2 e = min(puv, 1.0 - puv) * uTDOutputInfo.res.zw;
            col = mix(col, vec3(0.4, 0.9, 1.0), 1.0 - smoothstep(1.0, 2.5, min(e.x, e.y)));
        }
    }
    if (flg.x > 0.5) {
        vec4 hud = texture(sTD2DInputs[4], uv);
        col = col * (1.0 - hud.a) + hud.rgb;
    }
    fragColor = vec4(col, 1.0);
}
