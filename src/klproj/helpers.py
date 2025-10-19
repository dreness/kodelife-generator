"""
Helper functions for common shader patterns.

This module provides convenience functions for creating commonly-used
parameter configurations and shader setups.
"""

from typing import List

from .types import Parameter, ParamType


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
