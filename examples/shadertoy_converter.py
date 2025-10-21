#!/usr/bin/env python3
"""
Convert Shadertoy JSON format to KodeLife .klproj files.
"""

import json
import sys
from pathlib import Path

from klproj import (
    KodeProjBuilder,
    PassType,
    RenderPass,
    ShaderProfile,
    ShaderSource,
    ShaderStage,
    ShaderStageType,
    create_mvp_param,
    create_shadertoy_params,
)


def adapt_shadertoy_code(code: str, is_buffer: bool = False) -> str:
    """
    Adapt Shadertoy shader code to work in KodeLife.

    Args:
        code: The Shadertoy shader code
        is_buffer: Whether this is a buffer pass (affects output handling)

    Returns:
        Adapted shader code
    """
    # Add GLSL version if not present
    if "#version" not in code:
        adapted = "#version 330 core\n\n"
    else:
        adapted = ""

    # Shadertoy uses iChannel0, iChannel1, etc. for inputs
    # These are already sampler2D uniforms in Shadertoy
    # We need to ensure they're declared
    adapted += "// Shadertoy compatibility\n"
    adapted += "uniform sampler2D iChannel0;\n"
    adapted += "uniform sampler2D iChannel1;\n"
    adapted += "uniform sampler2D iChannel2;\n"
    adapted += "uniform sampler2D iChannel3;\n\n"

    # Add output declaration
    adapted += "out vec4 fragColor;\n\n"

    # Add the main wrapper
    adapted += "// Main wrapper\n"
    adapted += "void mainImage(out vec4 fragColor, in vec2 fragCoord);\n\n"
    adapted += "void main() {\n"
    adapted += "    mainImage(fragColor, gl_FragCoord.xy);\n"
    adapted += "}\n\n"

    # Add the original code
    adapted += "// Original Shadertoy code\n"
    adapted += code

    return adapted


def convert_shadertoy_to_klproj(
    json_path: Path,
    output_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
    api: str = "GL3",
) -> Path:
    """
    Convert a Shadertoy JSON file to a KodeLife .klproj file.

    Args:
        json_path: Path to the Shadertoy JSON file
        output_path: Optional output path for .klproj file
        width: Output resolution width
        height: Output resolution height
        api: Graphics API (GL2, GL3, GL4, etc.)

    Returns:
        Path to the created .klproj file
    """
    # Read and parse the Shadertoy JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    # Shadertoy JSON format wraps shader data in array
    if isinstance(data, list) and len(data) > 0:
        shader_data = data[0]
    else:
        shader_data = data

    # Get shader info
    info = shader_data.get("info", {})
    info.get("name", "Untitled")

    # Get render passes
    render_passes = shader_data.get("renderpass", [])

    if not render_passes:
        raise ValueError("No render passes found in Shadertoy JSON")

    # Create output path if not specified
    if output_path is None:
        output_path = json_path.with_suffix(".klproj")

    # Create builder
    builder = KodeProjBuilder(api=api)
    builder.set_resolution(width, height)
    builder.set_author(info.get("username", "Unknown"))
    builder.set_comment(info.get("description", ""))

    # Add standard Shadertoy parameters
    shadertoy_params = create_shadertoy_params()
    for param in shadertoy_params:
        builder.add_global_param(param)

    # Find buffer passes first (they need to be created before the image pass)
    buffer_passes = [p for p in render_passes if p.get("type") == "buffer"]
    image_passes = [p for p in render_passes if p.get("type") == "image"]

    # Get the shader profile
    profile = ShaderProfile[api]

    # Create standard vertex shader
    vertex_code = """#version 330 core
in vec4 a_position;
in vec3 a_normal;
in vec2 a_texcoord;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""

    # Process buffer passes first
    for pass_data in buffer_passes:
        pass_name = pass_data.get("name", "Buffer")
        code = pass_data.get("code", "")

        # Adapt the shader code
        adapted_code = adapt_shadertoy_code(code, is_buffer=True)

        # Create vertex shader stage
        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(profile, vertex_code)],
            parameters=[create_mvp_param()],
        )

        # Create fragment shader stage
        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(profile, adapted_code)],
        )

        # Create render pass
        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label=pass_name,
            stages=[vertex_stage, fragment_stage],
            width=width,
            height=height,
        )

        builder.add_pass(render_pass)

    # Process image pass (final output)
    for pass_data in image_passes:
        pass_name = pass_data.get("name", "Image")
        code = pass_data.get("code", "")

        # Adapt the shader code
        adapted_code = adapt_shadertoy_code(code, is_buffer=False)

        # Create vertex shader stage
        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(profile, vertex_code)],
            parameters=[create_mvp_param()],
        )

        # Create fragment shader stage
        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(profile, adapted_code)],
        )

        # Create render pass
        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label=pass_name,
            stages=[vertex_stage, fragment_stage],
            width=width,
            height=height,
        )

        builder.add_pass(render_pass)

    # Save the project
    builder.save(str(output_path))

    return output_path


def main():
    """CLI entry point for Shadertoy conversion."""
    if len(sys.argv) < 2:
        print("Usage: python shadertoy_converter.py <shadertoy.json> [output.klproj]")
        print("\nConvert a Shadertoy JSON file to a KodeLife .klproj file.")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    try:
        output = convert_shadertoy_to_klproj(json_path, output_path)
        print(f"✓ Created KodeLife project: {output}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
