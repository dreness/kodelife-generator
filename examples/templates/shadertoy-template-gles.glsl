#ifdef GL_ES
precision highp float;
#endif

varying vec3 v_normal;
varying vec2 v_texcoord;

uniform vec2 iResolution;
uniform float iTime;
uniform float iTimeDelta;
uniform int iFrame;
uniform vec4 iMouse;
uniform vec4 iDate;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform sampler2D iChannel2;
uniform sampler2D iChannel3;

#define texture(a,b) texture2D(a,b)
#define textureLod(a,b,c) texture2D(a,b)

void mainImage(out vec4, in vec2);

void main(void) {
    mainImage(gl_FragColor, v_texcoord * iResolution.xy);
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// Your shader code goes below this line

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;
    
    // Time varying pixel color
    vec3 col = 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0,2,4));
    
    // Output to screen
    fragColor = vec4(col, 1.0);
}