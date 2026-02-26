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

// Variables passed in from Python (state.py)
uniform vec2 resolution;
uniform vec2 offset;
uniform float zoom;
uniform int max_iter;
uniform float time;

// LLM / GUI Controls
uniform float power;
uniform vec3 color_tint;

void main() {
    // 1. Map the screen pixels to the mathematical complex plane
    vec2 c = (uv - 0.5) * (resolution / min(resolution.x, resolution.y));
    c = (c / zoom) + offset;

    vec2 z = vec2(0.0);
    int iter = 0;
    
    // 2. The Core Fractal Math (Polar Coordinates for smooth morphing)
    for(int i = 0; i < max_iter; i++) {
        float r = length(z);
        float theta = atan(z.y, z.x);
        
        // Apply the "Fractal Dimension" shape modifier
        r = pow(r, power);
        theta = theta * power;
        
        z = vec2(r * cos(theta), r * sin(theta)) + c;
        
        if(dot(z, z) > 16.0) {
            break; // Point escaped
        }
        iter++;
    }

    // 3. Coloring the pixels
    if (iter == max_iter) {
        // "Inside" of the fractal
        fragColor = vec4(0.0, 0.0, 0.02, 1.0); 
    } else {
        // "Outside" - Smooth continuous shading
        float float_iter = float(iter) - log2(log2(max(dot(z, z), 0.00001))) + 4.0;
        float t = float_iter / float(max_iter);
        
        // Procedural color palette mixed with your custom GUI color_tint
        vec3 base_color = vec3(0.5) + vec3(0.5) * cos(6.28318 * (vec3(1.0) * (t + time) + color_tint));
        fragColor = vec4(base_color, 1.0);
    }
}
#endif