// GPU-instanced particle renderer : one point per particle, position fetched from the simulation texture.
uniform sampler2D uSim;
uniform sampler2D uUni;
uniform vec4 uRes;          // render width, height, 0, 0
out vec4 vCol;

float hash11(float n) { return fract(sin(n * 127.1) * 43758.5453); }
vec3 pal(float t) { return 0.5 + 0.5 * cos(6.28318530718 * (t + vec3(0.0, 0.33, 0.67))); }

void main() {
    int id = gl_VertexID;
    ivec2 ip = ivec2(id & 255, id >> 8);
    vec4 s = texelFetch(uSim, ip, 0);
    vec4 par0 = texelFetch(uUni, ivec2(16, 0), 0);
    vec4 par1 = texelFetch(uUni, ivec2(17, 0), 0);
    vec4 sc0 = texelFetch(uUni, ivec2(5, 0), 0);
    vec4 sc2 = texelFetch(uUni, ivec2(7, 0), 0);
    vec4 st0 = texelFetch(uUni, ivec2(8, 0), 0);
    vec4 psy1 = texelFetch(uUni, ivec2(15, 0), 0);
    float T = sc2.w;
    float life = max(par1.x, 0.3);
    float fid = float(id);
    float seed = hash11(fid * 0.37 + 1.3);
    float ph = fract(T / life + seed);
    float z = (hash11(fid * 1.7) - 0.5) * 2.4 - 0.2;
    vec3 wp = vec3(s.xy * (2.5 - z) / 2.5, z);
    gl_Position = TDWorldToProj(vec4(wp, 1.0));

    float fade = smoothstep(0.0, 0.06, ph) * smoothstep(1.0, 0.55, ph);
    float sp = length(s.zw);
    float h = hash11(fid * 2.13);
    vec3 col = pal(0.62 + 0.35 * h + psy1.w + 0.15 * sp);
    col = mix(col, vec3(1.0), 0.25 * smoothstep(0.5, 2.5, sp));
    float bright = (0.35 + 0.55 * min(sp, 2.0)) * (0.6 + 0.8 * sc2.z + 0.4 * st0.w);
    float size = (1.4 + 3.2 * hash11(fid * 3.7)) * par1.y * (uRes.y / 720.0) * (0.7 + 0.5 * fade);
    gl_PointSize = (float(id) / 65536.0 > par0.x) ? 0.0 : size;
    vCol = vec4(col * bright * fade, 1.0);
}
