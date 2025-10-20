"""
Helper functions for common shader patterns.

This module provides convenience functions for creating commonly-used
parameter configurations and shader setups.
"""

from typing import List, Optional

from .types import Parameter, ParamType, ShaderProfile, ShaderSource, ShaderStage, ShaderStageType


def create_shadertoy_params() -> List[Parameter]:
    """
    Create standard Shadertoy-compatible global parameters.

    This creates the standard set of uniforms used by Shadertoy shaders:
    - iResolution: Frame resolution (vec2)
    - iTime: Time in seconds (float)
    - iTimeDelta: Time since last frame (float)
    - iFrame: Frame number (int)
    - iMouse: Mouse position/state (vec4)
    - iDate: Current date (year, month, day, seconds) (vec4)
    - iSampleRate: Audio sample rate (float)

    Note: These are similar to ISF standard variables but use Shadertoy naming.
    ISF equivalent: docs/ISF/isf-docs/pages/ref/ref_variables.md

    Returns:
        List of Parameter objects for Shadertoy compatibility

    Example:
        builder = KodeProjBuilder()
        for param in create_shadertoy_params():
            builder.add_global_param(param)
    """
    return [
        Parameter(
            param_type=ParamType.FRAME_RESOLUTION,
            display_name="Frame Resolution",
            variable_name="iResolution",
        ),
        Parameter(
            param_type=ParamType.CLOCK,
            display_name="Clock",
            variable_name="iTime",
            properties={
                "running": 1,
                "direction": 1,
                "speed": 1,
                "loop": 0,
                "loopStart": 0,
                "loopEnd": 6.28319,
            },
        ),
        Parameter(
            param_type=ParamType.FRAME_DELTA,
            display_name="Frame Delta",
            variable_name="iTimeDelta",
        ),
        Parameter(
            param_type=ParamType.FRAME_NUMBER,
            display_name="Frame Number",
            variable_name="iFrame",
        ),
        Parameter(
            param_type=ParamType.INPUT_MOUSE_SIMPLE,
            display_name="Mouse Simple",
            variable_name="iMouse",
            properties={"variant": 1, "normalize": 0, "invert": {"x": 0, "y": 1}},
        ),
        Parameter(param_type=ParamType.DATE, display_name="Date", variable_name="iDate"),
        Parameter(
            param_type=ParamType.AUDIO_SAMPLE_RATE,
            display_name="Audio Sample Rate",
            variable_name="iSampleRate",
        ),
    ]


def create_mvp_param() -> Parameter:
    """
    Create MVP (Model-View-Projection) matrix parameter for vertex shaders.

    This creates a parameter that provides the combined transformation matrix
    used to transform vertex positions from model space to clip space.

    Returns:
        Parameter for MVP matrix

    Example:
        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            parameters=[create_mvp_param()],
            ...
        )
    """
    return Parameter(
        param_type=ParamType.TRANSFORM_MVP,
        display_name="Model View Projection Matrix",
        variable_name="mvp",
    )


def create_time_param(variable_name: str = "time", speed: float = 1.0) -> Parameter:
    """
    Create a simple time parameter.

    Args:
        variable_name: Variable name in shader (default: "time")
        speed: Time speed multiplier (default: 1.0)

    Returns:
        Parameter for time

    Example:
        builder.add_global_param(create_time_param("uTime", speed=0.5))
    """
    return Parameter(
        param_type=ParamType.CLOCK,
        display_name="Time",
        variable_name=variable_name,
        properties={
            "running": 1,
            "direction": 1,
            "speed": speed,
            "loop": 0,
            "loopStart": 0,
            "loopEnd": 6.28319,
        },
    )


def create_resolution_param(variable_name: str = "resolution") -> Parameter:
    """
    Create a resolution parameter.

    Args:
        variable_name: Variable name in shader (default: "resolution")

    Returns:
        Parameter for resolution

    Example:
        builder.add_global_param(create_resolution_param("uResolution"))
    """
    return Parameter(
        param_type=ParamType.FRAME_RESOLUTION,
        display_name="Resolution",
        variable_name=variable_name,
    )


def create_mouse_param(
    variable_name: str = "mouse", normalized: bool = False, invert_y: bool = True
) -> Parameter:
    """
    Create a mouse input parameter.

    Args:
        variable_name: Variable name in shader (default: "mouse")
        normalized: Whether to normalize coordinates to [0,1] (default: False)
        invert_y: Whether to invert Y axis (default: True)

    Returns:
        Parameter for mouse input

    Example:
        builder.add_global_param(create_mouse_param("uMouse", normalized=True))
    """
    return Parameter(
        param_type=ParamType.INPUT_MOUSE_SIMPLE,
        display_name="Mouse",
        variable_name=variable_name,
        properties={
            "variant": 1,
            "normalize": 1 if normalized else 0,
            "invert": {"x": 0, "y": 1 if invert_y else 0},
        },
    )


def create_file_watch_stage(
    stage_type: ShaderStageType,
    file_path: str,
    parameters: Optional[List[Parameter]] = None,
) -> ShaderStage:
    """
    Create a shader stage that watches an external file.

    This creates a shader stage configured to load shader code from an external
    file and reload it when the file changes. This enables using external IDEs
    with KodeLife and allows coding agents to iterate quickly.

    Args:
        stage_type: Type of shader stage (VERTEX, FRAGMENT, etc.)
        file_path: Path to the external shader file to watch
        parameters: Optional list of stage-specific parameters

    Returns:
        ShaderStage configured for file watching

    Example:
        # Create a fragment shader that watches an external file
        fragment = create_file_watch_stage(
            ShaderStageType.FRAGMENT,
            "/path/to/shader.fs"
        )

        # With custom parameters
        vertex = create_file_watch_stage(
            ShaderStageType.VERTEX,
            "/path/to/shader.vs",
            parameters=[create_mvp_param()]
        )
    """
    return ShaderStage(
        stage_type=stage_type,
        enabled=1,
        hidden=0,
        file_watch=True,
        file_watch_path=file_path,
        sources=[],
        parameters=parameters or [],
    )


def create_vertex_file_watch_stage(
    file_path: str,
    mvp: bool = True,
) -> ShaderStage:
    """
    Create a vertex shader stage that watches an external file.

    Convenience function for creating file-watching vertex shader stages,
    with optional automatic MVP matrix parameter.

    Args:
        file_path: Path to the external vertex shader file (.vs)
        mvp: Whether to include MVP matrix parameter (default: True)

    Returns:
        Vertex ShaderStage configured for file watching

    Example:
        vertex = create_vertex_file_watch_stage("/path/to/shader.vs")
    """
    params = [create_mvp_param()] if mvp else []
    return create_file_watch_stage(
        ShaderStageType.VERTEX,
        file_path,
        parameters=params,
    )


def create_fragment_file_watch_stage(
    file_path: str,
    parameters: Optional[List[Parameter]] = None,
) -> ShaderStage:
    """
    Create a fragment shader stage that watches an external file.

    Convenience function for creating file-watching fragment shader stages.

    Args:
        file_path: Path to the external fragment shader file (.fs)
        parameters: Optional list of fragment-specific parameters

    Returns:
        Fragment ShaderStage configured for file watching

    Example:
        fragment = create_fragment_file_watch_stage("/path/to/shader.fs")
    """
    return create_file_watch_stage(
        ShaderStageType.FRAGMENT,
        file_path,
        parameters=parameters,
    )


def create_default_vertex_stage(
    profile: ShaderProfile = ShaderProfile.GL3,
) -> ShaderStage:
    """
    Create a default passthrough vertex shader stage.

    This creates a simple vertex shader that passes through vertex positions
    and texture coordinates without modification. Useful when you only need
    a fragment shader.

    Args:
        profile: Shader profile to use (default: GL3)

    Returns:
        Vertex ShaderStage with default passthrough shader

    Example:
        vertex = create_default_vertex_stage()
    """
    # Default vertex shader code based on profile
    if profile in [ShaderProfile.GL3, ShaderProfile.GL2]:
        code = """#version 150
in vec3 vertexPosition;
in vec2 vertexTexCoord;
out vec2 texCoord;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * vec4(vertexPosition, 1.0);
    texCoord = vertexTexCoord;
}
"""
    elif profile == ShaderProfile.MTL:
        code = """#include <metal_stdlib>
using namespace metal;

struct VertexIn {
    float3 position [[attribute(0)]];
    float2 texCoord [[attribute(1)]];
};

struct VertexOut {
    float4 position [[position]];
    float2 texCoord;
};

vertex VertexOut vertex_main(VertexIn in [[stage_in]],
                              constant float4x4& mvp [[buffer(0)]]) {
    VertexOut out;
    out.position = mvp * float4(in.position, 1.0);
    out.texCoord = in.texCoord;
    return out;
}
"""
    else:
        code = "// Unsupported profile"

    return ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=0,
        sources=[ShaderSource(profile=profile, code=code)],
        parameters=[create_mvp_param()],
    )
