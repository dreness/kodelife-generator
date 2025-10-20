#!/usr/bin/env python3
"""
Simple Gradient Shader Example

Creates a basic gradient shader that demonstrates the minimum
requirements for a KodeLife project.
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

# Fragment shader - creates a simple gradient
FRAGMENT_SHADER = """#version 150

out vec4 fragColor;

uniform vec2 resolution;

void main() {
    // Normalized coordinates (0 to 1)
    vec2 uv = gl_FragCoord.xy / resolution;

    // Simple gradient from red-green (left) to blue (right)
    vec3 color = vec3(uv.x, uv.y, 0.5);

    fragColor = vec4(color, 1.0);
}
"""

# Vertex shader - minimal required vertex shader
VERTEX_SHADER = """#version 150

in vec4 a_position;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""


def main():
    # Create the project builder
    builder = KodeProjBuilder(api="GL3")
    builder.set_resolution(800, 600)
    builder.set_author("klproj Example")
    builder.set_comment("Simple gradient shader example")

    # Add resolution parameter
    builder.add_global_param(create_resolution_param("resolution"))

    # Create vertex shader stage
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,  # Hide in UI - it's just boilerplate
        sources=[ShaderSource(ShaderProfile.GL3, VERTEX_SHADER)],
        parameters=[create_mvp_param()],
    )

    # Create fragment shader stage
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.GL3, FRAGMENT_SHADER)],
    )

    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Gradient",
        stages=[vertex_stage, fragment_stage],
        width=800,
        height=600,
    )

    builder.add_pass(render_pass)
    builder.save("simple_gradient.klproj")
    print("✓ Created simple_gradient.klproj")
    print("  Open it in KodeLife to see the gradient!")


if __name__ == "__main__":
    main()
