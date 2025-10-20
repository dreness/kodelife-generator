"""
Type definitions for KodeLife project generation.

This module contains all data classes, enums, and type definitions used
to construct KodeLife .klproj files.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class ShaderProfile(Enum):
    """
    Supported shader profile types.

    KodeLife supports multiple shader languages and versions:
    - DX9: DirectX 9 HLSL
    - ES3: OpenGL ES 3.0 (various versions)
    - GL2: OpenGL 2.x (legacy)
    - GL3: OpenGL 3.x+ (modern)
    - MTL: Metal (macOS/iOS)
    """

    DX9 = "DX9"
    ES3 = "ES3"
    ES3_300 = "ES3-300"
    ES3_310 = "ES3-310"
    ES3_320 = "ES3-320"
    GL2 = "GL2"
    GL3 = "GL3"
    MTL = "MTL"


class ShaderStageType(Enum):
    """
    Shader pipeline stage types.

    Represents different stages in the graphics pipeline:
    - VERTEX: Vertex shader (transforms vertices)
    - TESS_CONTROL: Tessellation control shader
    - TESS_EVAL: Tessellation evaluation shader
    - GEOMETRY: Geometry shader
    - FRAGMENT: Fragment/pixel shader (colors pixels)
    - COMPUTE: Compute shader (general purpose GPU computation)
    """

    VERTEX = "VERTEX"
    TESS_CONTROL = "TESS_CONTROL"
    TESS_EVAL = "TESS_EVAL"
    GEOMETRY = "GEOMETRY"
    FRAGMENT = "FRAGMENT"
    COMPUTE = "COMPUTE"


class PassType(Enum):
    """
    Render pass types.

    - RENDER: Standard graphics rendering pass
    - COMPUTE: Compute shader pass
    """

    RENDER = "RENDER"
    COMPUTE = "COMPUTE"


class ParamType(Enum):
    """
    Parameter types for uniforms.

    These represent various built-in and custom parameter types that can be
    passed to shaders.

    ISF-Related Parameters (see docs/ISF/isf-docs/pages/ref/ref_variables.md):
    - CLOCK: Maps to ISF uniform float TIME (seconds since start)
    - FRAME_RESOLUTION: Maps to ISF uniform vec2 RENDERSIZE (render target dimensions)
    - DATE: Maps to ISF uniform vec4 DATE (year, month, day, seconds)
    - FRAME_DELTA: Maps to ISF uniform float TIMEDELTA (time since last frame)
    - FRAME_NUMBER: Maps to ISF uniform int FRAMEINDEX (frame counter)

    Time/Frame Parameters:
    - CLOCK: Time in seconds
    - FRAME_DELTA: Time since last frame
    - FRAME_NUMBER: Current frame number
    - DATE: Current date/time (year, month, day, seconds)

    Resolution/Input:
    - FRAME_RESOLUTION: Current frame resolution (width, height)
    - INPUT_MOUSE_SIMPLE: Mouse position/state

    Audio:
    - AUDIO_SAMPLE_RATE: Audio sample rate
    - AUDIO_SPECTRUM_FULL: Full audio spectrum
    - AUDIO_SPECTRUM_SPLIT: Split audio spectrum

    Constants:
    - CONSTANT_FLOAT1/2/3/4: Custom float constants (1-4 components)
    - CONSTANT_TEXTURE_2D: Custom texture input

    Frame Buffers:
    - FRAME_PREV_FRAME: Previous frame texture
    - FRAME_PREV_PASS: Previous pass texture (used for ISF persistent buffers)

    Transforms:
    - TRANSFORM_MVP: Model-View-Projection matrix
    """

    CLOCK = "CLOCK"
    FRAME_RESOLUTION = "FRAME_RESOLUTION"
    FRAME_DELTA = "FRAME_DELTA"
    FRAME_NUMBER = "FRAME_NUMBER"
    INPUT_MOUSE_SIMPLE = "INPUT_MOUSE_SIMPLE"
    DATE = "DATE"
    AUDIO_SAMPLE_RATE = "AUDIO_SAMPLE_RATE"
    AUDIO_SPECTRUM_FULL = "AUDIO_SPECTRUM_FULL"
    AUDIO_SPECTRUM_SPLIT = "AUDIO_SPECTRUM_SPLIT"
    CONSTANT_FLOAT1 = "CONSTANT_FLOAT1"
    CONSTANT_FLOAT2 = "CONSTANT_FLOAT2"
    CONSTANT_FLOAT3 = "CONSTANT_FLOAT3"
    CONSTANT_FLOAT4 = "CONSTANT_FLOAT4"
    CONSTANT_TEXTURE_2D = "CONSTANT_TEXTURE_2D"
    FRAME_PREV_FRAME = "FRAME_PREV_FRAME"
    FRAME_PREV_PASS = "FRAME_PREV_PASS"
    TRANSFORM_MVP = "TRANSFORM_MVP"


@dataclass
class Vec2:
    """
    2D vector.

    Attributes:
        x: X component
        y: Y component
    """

    x: float = 0.0
    y: float = 0.0


@dataclass
class Vec3:
    """
    3D vector.

    Attributes:
        x: X component
        y: Y component
        z: Z component
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Vec4:
    """
    4D vector.

    Attributes:
        x: X component
        y: Y component
        z: Z component
        w: W component
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0


@dataclass
class ProjectProperties:
    """
    Global project properties.

    These settings control the overall behavior and metadata of the KodeLife project.

    Attributes:
        creator: Creator application name (default: "net.hexler.KodeLife")
        creator_version: Creator application version
        version_major: Project format major version
        version_minor: Project format minor version
        version_patch: Project format patch version
        author: Project author name
        comment: Project description/comment
        enabled: Whether the project is enabled (1) or disabled (0)
        width: Default project width in pixels
        height: Default project height in pixels
        format: Pixel format (e.g., "RGBA32F")
        clear_color: Background clear color (RGBA)
        audio_source_type: Audio source type (0 = none, 1 = file, 2 = input)
        audio_file_path: Path to audio file (if audio_source_type == 1)
    """

    creator: str = "net.hexler.KodeLife"
    creator_version: str = "1.2.3.202"
    version_major: int = 1
    version_minor: int = 1
    version_patch: int = 1
    author: str = ""
    comment: str = ""
    enabled: int = 1
    width: int = 1920
    height: int = 1080
    format: str = "RGBA32F"
    clear_color: Vec4 = field(default_factory=lambda: Vec4(0, 0, 0, 1))
    audio_source_type: int = 0
    audio_file_path: str = ""


@dataclass
class Parameter:
    """
    Uniform parameter definition.

    Parameters are uniforms that can be passed to shaders. They can represent
    time, resolution, mouse input, custom values, textures, and more.

    Attributes:
        param_type: Type of parameter (from ParamType enum)
        display_name: Human-readable name shown in UI
        variable_name: Variable name used in shader code
        ui_expanded: Whether the parameter UI is expanded (1) or collapsed (0)
        properties: Type-specific properties (dict of property name to value)

    Example:
        # Simple time parameter
        time_param = Parameter(
            param_type=ParamType.CLOCK,
            display_name="Time",
            variable_name="iTime",
            properties={'running': 1, 'speed': 1.0}
        )

        # Custom float constant with min/max
        custom_param = Parameter(
            param_type=ParamType.CONSTANT_FLOAT1,
            display_name="Speed",
            variable_name="speed",
            properties={
                'value': 1.0,
                'min': 0.0,
                'max': 10.0
            }
        )
    """

    param_type: ParamType
    display_name: str
    variable_name: str
    ui_expanded: int = 0
    properties: Dict = field(default_factory=dict)


@dataclass
class ShaderSource:
    """
    Shader source code for a specific profile.

    Each shader stage can have multiple source implementations for different
    shader profiles (GL2, GL3, Metal, etc.). KodeLife will use the appropriate
    one based on the current rendering API.

    Attributes:
        profile: Shader profile/language (from ShaderProfile enum)
        code: Shader source code as a string

    Example:
        # GLSL 3.0 fragment shader
        gl3_source = ShaderSource(
            profile=ShaderProfile.GL3,
            code=\"\"\"#version 150
            out vec4 fragColor;
            void main() {
                fragColor = vec4(1.0, 0.0, 0.0, 1.0);
            }
            \"\"\"
        )

        # Metal fragment shader
        metal_source = ShaderSource(
            profile=ShaderProfile.MTL,
            code=\"\"\"#include <metal_stdlib>
            using namespace metal;
            fragment float4 ps_main() {
                return float4(1.0, 0.0, 0.0, 1.0);
            }
            \"\"\"
        )
    """

    profile: ShaderProfile
    code: str


@dataclass
class ShaderStage:
    """
    Shader pipeline stage.

    A shader stage represents one step in the graphics pipeline (e.g., vertex,
    fragment, compute). Each stage can have multiple source code implementations
    for different shader profiles, OR it can reference an external file for
    live-reload/file-watching workflow.

    Attributes:
        stage_type: Type of shader stage (from ShaderStageType enum)
        enabled: Whether this stage is enabled (1) or disabled (0)
        hidden: Whether this stage is hidden in UI (1) or visible (0)
        sources: List of shader source code for different profiles
        parameters: List of stage-specific parameters
        file_watch: Whether to watch an external file for changes (default: False)
        file_watch_path: Path to external shader file to watch (default: "")

    File Watching:
        When file_watch=True and file_watch_path is set, KodeLife will load
        shader code from the external file and reload it on changes. This
        enables using external IDEs and allows coding agents to iterate quickly.

    Example:
        # Fragment shader with embedded source code
        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            hidden=0,
            sources=[
                ShaderSource(ShaderProfile.GL3, glsl_code),
                ShaderSource(ShaderProfile.MTL, metal_code),
            ],
            parameters=[]
        )

        # Fragment shader with file watching
        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            file_watch=True,
            file_watch_path="/path/to/shader.fs",
            sources=[]  # Sources can be empty when file watching
        )
    """

    stage_type: ShaderStageType
    enabled: int = 1
    hidden: int = 0
    sources: List[ShaderSource] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    file_watch: bool = False
    file_watch_path: str = ""


@dataclass
class RenderPass:
    """
    Render or compute pass.

    A pass represents a complete rendering or compute operation. Projects can
    have multiple passes that run in sequence, allowing for multi-pass effects.

    Attributes:
        pass_type: Type of pass (RENDER or COMPUTE)
        label: Human-readable pass name
        enabled: Whether this pass is enabled (1) or disabled (0)
        primitive_type: Primitive type for rendering (e.g., "TRIANGLES", "POINTS")
        stages: List of shader stages in this pass
        parameters: List of pass-specific parameters
        width: Render target width in pixels
        height: Render target height in pixels

    Example:
        # Simple render pass with vertex and fragment shaders
        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Main Pass",
            enabled=1,
            primitive_type="TRIANGLES",
            stages=[vertex_stage, fragment_stage],
            parameters=[],
            width=1920,
            height=1080
        )
    """

    pass_type: PassType
    label: str = "Pass A"
    enabled: int = 1
    primitive_type: str = "TRIANGLES"
    stages: List[ShaderStage] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    width: int = 1920
    height: int = 1080
