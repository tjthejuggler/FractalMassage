#version 330

#if defined VERTEX_SHADER
in vec3 in_position;
in vec2 in_texcoord_0;
out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 1.0);
    uv = in_texcoord_0;
}
#endif

#if defined FRAGMENT_SHADER
out vec4 fragColor;
in vec2 uv;

uniform vec2 resolution;
uniform vec2 offset;
uniform float zoom;
uniform int max_iter;
uniform float time;
uniform float power;
uniform vec3 color_tint;

// Injection Engine
uniform sampler2D sdf_texture;
uniform vec2 inject_pos;
uniform float inject_scale;
uniform int inject_active; // CHANGED FROM BOOL TO INT

void main() {
    vec2 c = (uv - 0.5) * (resolution / min(resolution.x, resolution.y));
    c = (c / zoom) + offset;

    // INJECTION BLENDING
    vec2 inject_uv = (c - inject_pos) * inject_scale * 0.2 + 0.5;
    vec2 clamped_uv = clamp(vec2(inject_uv.x, 1.0 - inject_uv.y), 0.0, 1.0);
    
    float raw_dist = texture(sdf_texture, clamped_uv).r;
    float sdf_dist = (0.5 - raw_dist); 
    
    float in_bounds = step(0.0, inject_uv.x) * step(inject_uv.x, 1.0) * step(0.0, inject_uv.y) * step(inject_uv.y, 1.0);
    
    // Cast the int to a float for the math (0.0 or 1.0)
    float active_float = float(inject_active);
    float melt_factor = smoothstep(-0.05, 0.05, sdf_dist) * in_bounds * active_float;
    
    c = mix(c, vec2(0.0), melt_factor);

    vec2 z = vec2(0.0);
    int iter = 0;
    
    for(int i = 0; i < max_iter; i++) {
        float r = length(z);
        float theta = atan(z.y, z.x);
        
        r = pow(r, power);
        theta = theta * power;
        
        z = vec2(r * cos(theta), r * sin(theta)) + c;
        
        if(dot(z, z) > 16.0) break; 
        iter++;
    }

    if (iter == max_iter) {
        fragColor = vec4(0.0, 0.0, 0.02, 1.0); 
    } else {
        float float_iter = float(iter) - log2(log2(max(dot(z, z), 0.00001))) + 4.0;
        float t = float_iter / float(max_iter);
        vec3 base_color = vec3(0.5) + vec3(0.5) * cos(6.28318 * (vec3(1.0) * (t + time) + color_tint));
        fragColor = vec4(base_color, 1.0);
    }
}
#endif