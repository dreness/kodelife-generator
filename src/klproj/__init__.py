"""
KodeLife Project Generator

A Python library for creating KodeLife .klproj files programmatically.
Supports creating complete shader projects with multiple passes, parameters,
and shader profiles (OpenGL, Metal, DirectX).

Also includes ISF (Interactive Shader Format) parsing and conversion utilities.
"""

from .generator import KodeProjBuilder
from .helpers import (
    create_mouse_param,
    create_mvp_param,
    create_resolution_param,
    create_shadertoy_params,
    create_time_param,
)
from .isf_converter import convert_isf_to_kodelife
from .isf_parser import (
    ISFImported,
    ISFInput,
    ISFPass,
    ISFShader,
    parse_isf_file,
    parse_isf_string,
)
from .metal_helpers import (
    create_metal_fragment_source_shadertoy,
    create_metal_vertex_source,
    generate_metal_compute_shader,
    generate_metal_fragment_shader_shadertoy,
    generate_metal_vertex_shader,
)
from .types import (
    Parameter,
    ParamType,
    PassType,
    ProjectProperties,
    RenderPass,
    ShaderProfile,
    ShaderSource,
    ShaderStage,
    ShaderStageType,
    Vec2,
    Vec3,
    Vec4,
)

__version__ = "0.1.0"
__all__ = [
    # Enums
    "ShaderProfile",
    "ShaderStageType",
    "PassType",
    "ParamType",
    # Data types
    "Vec2",
    "Vec3",
    "Vec4",
    "ProjectProperties",
    "Parameter",
    "ShaderSource",
    "ShaderStage",
    "RenderPass",
    # Builder
    "KodeProjBuilder",
    # Helpers
    "create_shadertoy_params",
    "create_mvp_param",
    "create_time_param",
    "create_resolution_param",
    "create_mouse_param",
    # Metal Helpers
    "generate_metal_vertex_shader",
    "generate_metal_fragment_shader_shadertoy",
    "generate_metal_compute_shader",
    "create_metal_vertex_source",
    "create_metal_fragment_source_shadertoy",
    # ISF Parser
    "ISFShader",
    "ISFInput",
    "ISFPass",
    "ISFImported",
    "parse_isf_file",
    "parse_isf_string",
    # ISF Converter
    "convert_isf_to_kodelife",
]
