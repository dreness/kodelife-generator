#!/usr/bin/env python3
"""
Metal Gradient Shader Example

Creates a gradient shader using Metal Shading Language.
This demonstrates the structure required for Metal shaders in KodeLife.
"""

from klproj import (
    KodeProjBuilder,
    PassType,
    RenderPass,
    ShaderProfile,
    ShaderSource,
    ShaderStage,
    ShaderStageType,
    create_mvp_param,
    create_resolution_param,
)

# Metal vertex shader
VERTEX_SHADER = """#include <metal_stdlib>
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
    float2 resolution;
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

# Metal fragment shader
FRAGMENT_SHADER = """#include <metal_stdlib>
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
    float2 resolution;
};

fragment PS_OUTPUT ps_main(
    PS_INPUT input [[stage_in]],
    constant PS_UNIFORM& u [[buffer(16)]]
) {
    PS_OUTPUT out;

    // Use texture coordinates for gradient
    float2 uv = input.v_texcoord;
    float3 color = float3(uv.x, uv.y, 0.5);
    out.color = float4(color, 1.0);

    return out;
}
"""


def main():
    # Create the project builder
    builder = KodeProjBuilder(api="MTL")
    builder.set_resolution(1920, 1080)
    builder.set_author("klproj Example")
    builder.set_comment("Metal gradient shader example")

    # Add resolution parameter
    builder.add_global_param(create_resolution_param("resolution"))

    # Create vertex shader stage
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,
        sources=[ShaderSource(ShaderProfile.MTL, VERTEX_SHADER)],
        parameters=[create_mvp_param()],
    )

    # Create fragment shader stage
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.MTL, FRAGMENT_SHADER)],
    )

    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Metal Gradient",
        stages=[vertex_stage, fragment_stage],
        width=1920,
        height=1080,
    )

    builder.add_pass(render_pass)
    builder.save("metal_gradient.klproj")
    print("✓ Created metal_gradient.klproj")
    print("  Open it in KodeLife on macOS to see the gradient!")


if __name__ == "__main__":
    main()
