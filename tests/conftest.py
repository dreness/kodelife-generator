"""Pytest configuration and fixtures for klproj tests."""

import os
import tempfile

import pytest
from klproj import (
    KodeProjBuilder,
    Parameter,
    ParamType,
    PassType,
    RenderPass,
    ShaderProfile,
    ShaderSource,
    ShaderStage,
    ShaderStageType,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def simple_vertex_shader():
    """Provide a simple GLSL vertex shader."""
    return """#version 150

in vec4 a_position;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""


@pytest.fixture
def simple_fragment_shader():
    """Provide a simple GLSL fragment shader."""
    return """#version 150

out vec4 fragColor;
uniform vec2 resolution;
uniform float time;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec3 col = vec3(uv, 0.5 + 0.5 * sin(time));
    fragColor = vec4(col, 1.0);
}
"""


@pytest.fixture
def shadertoy_fragment_shader():
    """Provide a Shadertoy-style fragment shader."""
    return """#version 150

out vec4 fragColor;
uniform vec2 iResolution;
uniform float iTime;

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    vec3 col = 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0, 2, 4));
    fragColor = vec4(col, 1.0);
}

void main() {
    mainImage(fragColor, gl_FragCoord.xy);
}
"""


@pytest.fixture
def metal_vertex_shader():
    """Provide a simple Metal vertex shader."""
    return """#include <metal_stdlib>
using namespace metal;

struct VertexIn {
    float4 position [[attribute(0)]];
};

struct VertexOut {
    float4 position [[position]];
};

vertex VertexOut vertex_main(VertexIn in [[stage_in]],
                              constant float4x4& mvp [[buffer(0)]]) {
    VertexOut out;
    out.position = mvp * in.position;
    return out;
}
"""


@pytest.fixture
def metal_fragment_shader():
    """Provide a simple Metal fragment shader."""
    return """#include <metal_stdlib>
using namespace metal;

fragment float4 fragment_main(float4 position [[position]],
                               constant float2& resolution [[buffer(0)]],
                               constant float& time [[buffer(1)]]) {
    float2 uv = position.xy / resolution;
    float3 col = float3(uv, 0.5 + 0.5 * sin(time));
    return float4(col, 1.0);
}
"""


@pytest.fixture
def basic_time_param():
    """Provide a basic time parameter."""
    return Parameter(
        param_type=ParamType.CLOCK,
        display_name="Time",
        variable_name="time",
        properties={"running": 1, "speed": 1.0},
    )


@pytest.fixture
def basic_resolution_param():
    """Provide a basic resolution parameter."""
    return Parameter(
        param_type=ParamType.FRAME_RESOLUTION,
        display_name="Resolution",
        variable_name="resolution",
    )


@pytest.fixture
def basic_mvp_param():
    """Provide a basic MVP parameter."""
    return Parameter(
        param_type=ParamType.TRANSFORM_MVP,
        display_name="MVP",
        variable_name="mvp",
    )


@pytest.fixture
def simple_vertex_stage(simple_vertex_shader, basic_mvp_param):
    """Provide a simple vertex shader stage."""
    return ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,
        sources=[ShaderSource(ShaderProfile.GL3, simple_vertex_shader)],
        parameters=[basic_mvp_param],
    )


@pytest.fixture
def simple_fragment_stage(simple_fragment_shader):
    """Provide a simple fragment shader stage."""
    return ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.GL3, simple_fragment_shader)],
    )


@pytest.fixture
def simple_render_pass(simple_vertex_stage, simple_fragment_stage):
    """Provide a simple render pass with vertex and fragment stages."""
    return RenderPass(
        pass_type=PassType.RENDER,
        label="Simple Pass",
        stages=[simple_vertex_stage, simple_fragment_stage],
        width=1920,
        height=1080,
    )


@pytest.fixture
def basic_builder():
    """Provide a basic KodeProjBuilder."""
    builder = KodeProjBuilder(api="GL3")
    builder.set_resolution(1920, 1080)
    builder.set_author("Test Author")
    return builder


@pytest.fixture
def complete_builder(basic_builder, basic_time_param, basic_resolution_param, simple_render_pass):
    """Provide a complete KodeProjBuilder with params and pass."""
    basic_builder.add_global_param(basic_time_param)
    basic_builder.add_global_param(basic_resolution_param)
    basic_builder.add_pass(simple_render_pass)
    return basic_builder


@pytest.fixture
def multi_profile_fragment_stage(simple_fragment_shader, metal_fragment_shader):
    """Provide a fragment stage with multiple shader profiles."""
    return ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[
            ShaderSource(ShaderProfile.GL3, simple_fragment_shader),
            ShaderSource(ShaderProfile.MTL, metal_fragment_shader),
        ],
    )