#!/usr/bin/env python3
"""
Shadertoy-Compatible Shader Example

Creates a shader that's fully compatible with Shadertoy conventions.
Uses all the standard Shadertoy uniforms (iResolution, iTime, iMouse, etc.)
and supports multiple shader profiles.
"""

from klproj import (
    KodeProjBuilder,
    RenderPass,
    PassType,
    ShaderStage,
    ShaderStageType,
    ShaderSource,
    ShaderProfile,
    create_shadertoy_params,
    create_mvp_param,
)

# GLSL 150 (OpenGL 3.x) Fragment Shader
FRAGMENT_GL3 = """#version 150

out vec4 fragColor;

uniform vec2 iResolution;
uniform float iTime;
uniform float iTimeDelta;
uniform int iFrame;
uniform vec4 iMouse;
uniform vec4 iDate;
uniform float iSampleRate;

void mainImage(out vec4 fragColor, in vec2 fragCoord);

void main() {
    mainImage(fragColor, gl_FragCoord.xy);
}

// Shadertoy main function
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    
    // Create animated pattern
    vec2 p = uv * 2.0 - 1.0;
    float d = length(p);
    float a = atan(p.y, p.x);
    
    // Animated colors
    vec3 col = 0.5 + 0.5 * cos(iTime + a + vec3(0, 2, 4));
    
    // Radial pattern
    col *= smoothstep(0.8, 0.2, d);
    
    fragColor = vec4(col, 1.0);
}
"""

# Metal Fragment Shader
FRAGMENT_MTL = """#include <metal_stdlib>
using namespace metal;

struct PS_INPUT {
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
};

struct PS_OUTPUT {
    float4 color [[color(0)]];
};

struct PS_UNIFORM {
    float2 iResolution;
    float iTime;
    float iTimeDelta;
    int iFrame;
    float4 iMouse;
    float4 iDate;
    float iSampleRate;
};

void mainImage(thread float4& fragColor, float2 fragCoord, constant PS_UNIFORM& u);

fragment PS_OUTPUT ps_main(
    PS_INPUT input [[stage_in]],
    constant PS_UNIFORM& u [[buffer(16)]]
) {
    PS_OUTPUT out;
    mainImage(out.color, input.v_texcoord * u.iResolution, u);
    return out;
}

void mainImage(thread float4& fragColor, float2 fragCoord, constant PS_UNIFORM& u) {
    float2 uv = fragCoord / u.iResolution.xy;
    
    float2 p = uv * 2.0 - 1.0;
    float d = length(p);
    float a = atan2(p.y, p.x);
    
    float3 col = 0.5 + 0.5 * cos(u.iTime + a + float3(0, 2, 4));
    col *= smoothstep(0.8, 0.2, d);
    
    fragColor = float4(col, 1.0);
}
"""

# GLSL 120 (OpenGL 2.x) Fragment Shader
FRAGMENT_GL2 = """#ifdef GL_ES
precision highp float;
#endif

uniform vec2 iResolution;
uniform float iTime;
uniform float iTimeDelta;
uniform int iFrame;
uniform vec4 iMouse;
uniform vec4 iDate;
uniform float iSampleRate;

void mainImage(out vec4 fragColor, in vec2 fragCoord);

void main() {
    mainImage(gl_FragColor, gl_FragCoord.xy);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    vec2 p = uv * 2.0 - 1.0;
    float d = length(p);
    float a = atan(p.y, p.x);
    
    vec3 col = 0.5 + 0.5 * cos(iTime + a + vec3(0, 2, 4));
    col *= smoothstep(0.8, 0.2, d);
    
    fragColor = vec4(col, 1.0);
}
"""

# Vertex shaders for different profiles
VERTEX_GL3 = """#version 150

in vec4 a_position;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""

VERTEX_MTL = """#include <metal_stdlib>
using namespace metal;

struct VS_INPUT {
    float4 a_position [[attribute(0)]];
    float3 a_normal   [[attribute(1)]];
    float2 a_texcoord [[attribute(2)]];
};

struct VS_OUTPUT {
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
};

struct VS_UNIFORM {
    float4x4 mvp;
    float2 iResolution;
    float iTime;
    float iTimeDelta;
    int iFrame;
    float4 iMouse;
    float4 iDate;
    float iSampleRate;
};

vertex VS_OUTPUT vs_main(
    VS_INPUT input [[stage_in]],
    constant VS_UNIFORM& u [[buffer(16)]]
) {
    VS_OUTPUT out;
    out.v_position = u.mvp * input.a_position;
    out.v_normal = input.a_normal;
    out.v_texcoord = input.a_texcoord;
    return out;
}
"""

VERTEX_GL2 = """attribute vec4 a_position;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""


def main():
    # Create the project builder
    builder = KodeProjBuilder(api="MTL")
    builder.set_resolution(1920, 1080)
    builder.set_author("klproj Example")
    builder.set_comment("Shadertoy-compatible shader with multi-profile support")

    # Add all Shadertoy-compatible parameters
    for param in create_shadertoy_params():
        builder.add_global_param(param)

    # Create vertex shader stage with multiple profiles
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,
        sources=[
            ShaderSource(ShaderProfile.GL3, VERTEX_GL3),
            ShaderSource(ShaderProfile.GL2, VERTEX_GL2),
            ShaderSource(ShaderProfile.MTL, VERTEX_MTL),
        ],
        parameters=[create_mvp_param()],
    )

    # Create fragment shader stage with multiple profiles
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[
            ShaderSource(ShaderProfile.GL3, FRAGMENT_GL3),
            ShaderSource(ShaderProfile.GL2, FRAGMENT_GL2),
            ShaderSource(ShaderProfile.MTL, FRAGMENT_MTL),
        ],
    )

    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Shadertoy",
        stages=[vertex_stage, fragment_stage],
        width=1920,
        height=1080,
    )

    builder.add_pass(render_pass)
    builder.save("shadertoy_compatible.klproj")
    print("✓ Created shadertoy_compatible.klproj")
    print("  This shader supports GL2, GL3, and Metal!")
    print("  Open it in KodeLife on any platform.")


if __name__ == "__main__":
    main()