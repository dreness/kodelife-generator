#version 150

// Shadertoy-compatible uniforms
// zoop
uniform vec2 iResolution;
uniform float iTime;
uniform vec4 iMouse;

out vec4 fragColor;

// Animated plasma effect
// Try editing this file and saving - KodeLife will reload it automatically!

void main() {
    // Normalize coordinates
    vec2 uv = gl_FragCoord.xy / iResolution.xy;

    // Center coordinates
    vec2 p = uv * 2.0 - 1.0;
    p.x *= iResolution.x / iResolution.y; // Correct aspect ratio

    // Animated plasma
    float t = iTime * 0.95;

    float plasma = sin(p.x * 10.0 + t);
    plasma += sin(p.y * 10.0 + t * 1.2);
    plasma += sin((p.x + p.y) * 10.0 + t * 1.5);
    plasma += sin(sqrt(p.x * p.x + p.y * p.y) * 10.0 + t * 2.0);
    plasma *= 0.25;

    // Color mapping
    vec3 color;
    color.r = sin(plasma * 3.14159 + 1.0);
    color.g = sin(plasma * 3.14159 + 2.094);
    color.b = sin(plasma * 3.14159 + 4.189);

    color = color * 0.5 + 0.5; // Remap to [0, 1]

    fragColor = vec4(color, 1.0);
}
