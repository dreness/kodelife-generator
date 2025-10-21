"""
Helper functions for generating Metal shader code.

This module provides utilities for creating Metal Shading Language (MSL) shader
code for KodeLife projects. Based on analysis of KodeLife's Metal shader templates.
"""

from typing import List, Tuple

from .types import Parameter, ParamType, ShaderProfile, ShaderSource


def generate_metal_vertex_shader(
    parameters: List[Parameter], include_shadertoy_compat: bool = False
) -> str:
    """
    Generate a Metal vertex shader with uniform buffer.

    Args:
        parameters: List of parameters to include in uniform buffer
        include_shadertoy_compat: Whether to include Shadertoy-style parameter names

    Returns:
        Complete Metal vertex shader source code

    Example:
        >>> params = create_shadertoy_params()
        >>> mvp_param = create_mvp_param()
        >>> vertex_code = generate_metal_vertex_shader(params + [mvp_param], True)
    """
    # Build uniform struct members
    uniform_members = []
    for param in parameters:
        metal_type = _param_type_to_metal_type(param.param_type)
        if metal_type:
            uniform_members.append(f"    {metal_type} {param.variable_name};")

    uniform_struct = "\n".join(uniform_members) if uniform_members else "    // No uniforms"

    shader_code = f"""#include <metal_stdlib>
using namespace metal;

struct VS_INPUT
{{
    float4 a_position [[attribute(0)]];
    float3 a_normal   [[attribute(1)]];
    float2 a_texcoord [[attribute(2)]];
}};

struct VS_OUTPUT
{{
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
}};

struct VS_UNIFORM
{{
{uniform_struct}
}};

vertex
VS_OUTPUT vs_main(
    VS_INPUT input [[stage_in]],
    constant VS_UNIFORM& u [[buffer(16)]])
{{
    VS_OUTPUT out;
    out.v_position = u.mvp * input.a_position;
    out.v_normal   = input.a_normal;
    out.v_texcoord = input.a_texcoord;
    return out;
}}
"""
    return shader_code


def generate_metal_fragment_shader_shadertoy(
    parameters: List[Parameter],
    texture_params: List[Parameter] = None,
    shader_body: str = None,
) -> str:
    """
    Generate a Metal fragment shader with Shadertoy-compatible wrapper.

    This generates a Metal fragment shader that wraps a mainImage() function,
    similar to how Shadertoy and KodeLife's GL shaders work.

    Args:
        parameters: List of global parameters (iTime, iResolution, etc.)
        texture_params: List of texture parameters (iChannel0, etc.)
        shader_body: Custom shader code for mainImage() body (optional)

    Returns:
        Complete Metal fragment shader source code with mainImage() wrapper

    Example:
        >>> params = create_shadertoy_params()
        >>> textures = [create_texture_param("iChannel0")]
        >>> body = "float2 uv = fragCoord.xy / iResolution.xy; fragColor = float4(uv, 0.0, 1.0);"
        >>> frag_code = generate_metal_fragment_shader_shadertoy(params, textures, body)
    """
    if texture_params is None:
        texture_params = []

    # Build uniform struct members
    uniform_members = []
    for param in parameters:
        metal_type = _param_type_to_metal_type(param.param_type)
        if metal_type:
            uniform_members.append(f"    {metal_type} {param.variable_name};")

    uniform_struct = "\n".join(uniform_members) if uniform_members else "    // No uniforms"

    # Build texture parameters for function signature
    texture_fn_params = []
    texture_fn_args = []
    texture_bindings = []
    for i, param in enumerate(texture_params):
        texture_fn_params.append(f"texture2d<float> {param.variable_name}")
        texture_fn_args.append(param.variable_name)
        texture_bindings.append(f"    texture2d<float> {param.variable_name} [[texture({i})]]")

    # Build mainImage function signature
    if texture_fn_params:
        mainimage_params = ",\n               " + ", ".join(texture_fn_params)
        mainimage_args = ",\n              " + ", ".join(texture_fn_args)
    else:
        mainimage_params = ""
        mainimage_args = ""

    # Build texture bindings for fs_main
    texture_binding_str = ",\n    ".join(texture_bindings) if texture_bindings else ""
    if texture_binding_str:
        texture_binding_str = ",\n    " + texture_binding_str

    # Build parameter list for mainImage signature - just the types
    mainimage_signature_params = []
    for param in parameters:
        metal_type = _param_type_to_metal_type(param.param_type)
        if metal_type:
            mainimage_signature_params.append(f"{metal_type} {param.variable_name}")

    mainimage_signature_str = (
        ", ".join(mainimage_signature_params) if mainimage_signature_params else ""
    )
    if mainimage_signature_str:
        mainimage_signature_str = ",\n               " + mainimage_signature_str

    # Build parameter list for mainImage call (extract from uniform struct)
    uniform_param_names = [
        p.variable_name for p in parameters if _param_type_to_metal_type(p.param_type)
    ]
    uniform_args = ", ".join([f"u.{name}" for name in uniform_param_names])
    if uniform_args:
        uniform_args = ", " + uniform_args

    # Default shader body if none provided
    if shader_body is None:
        shader_body = """float2 uv = fragCoord.xy / iResolution.xy;
    fragColor = float4(uv,0.5+0.5*sin(iTime),1.0);"""

    shader_code = f"""#include <metal_stdlib>
using namespace metal;

struct FS_INPUT
{{
    float3 v_normal;
    float2 v_texcoord;
}};

struct FS_UNIFORM
{{
{uniform_struct}
}};

void mainImage(thread float4&, float2{mainimage_signature_str}{mainimage_params});

fragment
float4 fs_main(
    FS_INPUT In [[stage_in]],
    constant FS_UNIFORM& u[[buffer(16)]]{texture_binding_str})
{{
    float4 col;
    mainImage(col, In.v_texcoord * u.iResolution{uniform_args}{mainimage_args});
    return col;
}}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

void mainImage(thread float4& fragColor, float2 fragCoord{mainimage_signature_str}{mainimage_params})
{{
    {shader_body}
}}
"""
    return shader_code


def generate_metal_compute_shader(
    parameters: List[Parameter],
    output_textures: List[Tuple[str, int]] = None,
    threads_per_group: Tuple[int, int, int] = (8, 8, 1),
) -> str:
    """
    Generate a Metal compute shader.

    Args:
        parameters: List of parameters to include in uniform buffer
        output_textures: List of (texture_name, binding_index) tuples for output textures
        threads_per_group: Thread group size (default: 8x8x1)

    Returns:
        Complete Metal compute shader source code

    Example:
        >>> params = [create_time_param(), create_resolution_param()]
        >>> outputs = [("outputTexture", 0)]
        >>> compute_code = generate_metal_compute_shader(params, outputs)
    """
    if output_textures is None:
        output_textures = []

    # Build uniform struct members
    uniform_members = []
    for param in parameters:
        metal_type = _param_type_to_metal_type(param.param_type)
        if metal_type:
            uniform_members.append(f"    {metal_type} {param.variable_name};")

    uniform_struct = "\n".join(uniform_members) if uniform_members else "    // No uniforms"

    # Build texture parameters
    texture_params = []
    for tex_name, binding in output_textures:
        texture_params.append(
            f"    texture2d<float, access::write> {tex_name} [[texture({binding})]]"
        )

    texture_param_str = ",\n".join(texture_params) if texture_params else ""
    if texture_param_str:
        texture_param_str = ",\n" + texture_param_str

    shader_code = f"""#include <metal_stdlib>
#include <simd/simd.h>

using namespace metal;

struct CS_UNIFORM
{{
{uniform_struct}
}};

kernel void cs_main(
    constant CS_UNIFORM& uniform [[buffer(16)]],
    uint3 globalInvocationID [[thread_position_in_grid]]{texture_param_str})
{{
    // Compute shader body
    // TODO: Implement compute logic
}}
"""
    return shader_code


def _param_type_to_metal_type(param_type: ParamType) -> str:
    """
    Map KodeLife parameter types to Metal types.

    Args:
        param_type: KodeLife parameter type

    Returns:
        Metal type string, or empty string if not applicable
    """
    type_map = {
        ParamType.CLOCK: "float",
        ParamType.FRAME_DELTA: "float",
        ParamType.FRAME_NUMBER: "int",
        ParamType.FRAME_RESOLUTION: "float2",
        ParamType.INPUT_MOUSE_SIMPLE: "float4",
        ParamType.DATE: "float4",
        ParamType.AUDIO_SAMPLE_RATE: "float",
        ParamType.AUDIO_SPECTRUM_SPLIT: "float3",
        ParamType.AUDIO_SPECTRUM_FULL: "float",
        ParamType.TRANSFORM_MVP: "float4x4",
        ParamType.CONSTANT_FLOAT1: "float",
        ParamType.CONSTANT_FLOAT2: "float2",
        ParamType.CONSTANT_FLOAT3: "float3",
        ParamType.CONSTANT_FLOAT4: "float4",
        # Note: CONSTANT_TEXTURE_2D is handled separately in fragment shader bindings
    }
    return type_map.get(param_type, "")


def create_metal_vertex_source(parameters: List[Parameter]) -> ShaderSource:
    """
    Create a ShaderSource for Metal vertex shader.

    Args:
        parameters: List of parameters to include

    Returns:
        ShaderSource with generated Metal vertex shader code
    """
    code = generate_metal_vertex_shader(parameters)
    return ShaderSource(profile=ShaderProfile.MTL, code=code)


def create_metal_fragment_source_shadertoy(
    parameters: List[Parameter],
    texture_params: List[Parameter] = None,
    shader_body: str = None,
) -> ShaderSource:
    """
    Create a ShaderSource for Metal fragment shader with Shadertoy wrapper.

    Args:
        parameters: List of global parameters
        texture_params: List of texture parameters
        shader_body: Custom shader code for mainImage() body (optional)

    Returns:
        ShaderSource with generated Metal fragment shader code
    """
    code = generate_metal_fragment_shader_shadertoy(parameters, texture_params, shader_body)
    return ShaderSource(profile=ShaderProfile.MTL, code=code)


def create_texture_samplers_for_metal(texture_params: List[Parameter]) -> List[str]:
    """
    Generate sampler parameter declarations for Metal fragment shader.

    Metal requires separate sampler objects for each texture. This generates
    the appropriate sampler declarations for the fs_main function signature.

    Args:
        texture_params: List of texture parameters

    Returns:
        List of sampler declaration strings

    Example:
        >>> tex_params = [create_texture_param("iChannel0")]
        >>> samplers = create_texture_samplers_for_metal(tex_params)
        >>> # ['sampler iChannel0Smplr [[sampler(0)]]']
    """
    samplers = []
    for i, param in enumerate(texture_params):
        sampler_name = f"{param.variable_name}Smplr"
        samplers.append(f"sampler {sampler_name} [[sampler({i})]]")
    return samplers
