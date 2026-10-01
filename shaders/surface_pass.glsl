// PROJECTION surface pass : edge blend + projection mask + opacity for one mapped surface.
// inputs: 0 corner-pinned image.   vec uniforms (set by the builder from the surface's custom parameters):
//   uBlend   = (left, right, top, bottom) soft-edge widths as a fraction of the surface
//   uMask    = (gamma of the blend curve, opacity, mask inset, mask feather)
uniform vec4 uBlend;
uniform vec4 uMask;
layout(location = 0) out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec4 c = texture(sTD2DInputs[0], uv);
    float g = max(uMask.x, 0.1);
    float bl = uBlend.x > 0.0005 ? pow(smoothstep(0.0, uBlend.x, uv.x), g) : 1.0;
    float br = uBlend.y > 0.0005 ? pow(smoothstep(0.0, uBlend.y, 1.0 - uv.x), g) : 1.0;
    float bt = uBlend.z > 0.0005 ? pow(smoothstep(0.0, uBlend.z, 1.0 - uv.y), g) : 1.0;
    float bb = uBlend.w > 0.0005 ? pow(smoothstep(0.0, uBlend.w, uv.y), g) : 1.0;
    float edge = bl * br * bt * bb;
    // projection mask : inset rectangle with feathered edge
    float inset = uMask.z;
    float f = max(uMask.w, 0.0005);
    vec2 d = min(uv - inset, 1.0 - inset - uv);
    float m = smoothstep(0.0, f, min(d.x, d.y));
    fragColor = vec4(c.rgb * edge * m * uMask.y, c.a);
}
