in vec4 vCol;
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 c = gl_PointCoord - 0.5;
    float r = length(c) * 2.0;
    float a = smoothstep(1.0, 0.0, r);
    a *= a;
    fragColor = vec4(vCol.rgb * a, a);
}
