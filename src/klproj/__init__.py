"""
KodeLife Project Generator

A Python library for creating KodeLife .klproj files programmatically.
Supports creating complete shader projects with multiple passes, parameters,
and shader profiles (OpenGL, Metal, DirectX).
"""

from .generator import KodeProjBuilder
from .helpers import (
    create_mouse_param,
    create_mvp_param,
    create_resolution_param,
    create_shadertoy_params,
    create_time_param,
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
]
