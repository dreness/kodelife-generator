#!/usr/bin/env python3
"""
Animated Rainbow Shader Example

Creates an animated rainbow effect using time-based color cycling.
This is a great starting point for animated shaders.
"""

from klproj import (
    KodeProjBuilder,
    RenderPass,
    PassType,
    ShaderStage,
    ShaderStageType,
    ShaderSource,
    ShaderProfile,
    create_resolution_param,
    create_time_param,
    create_mvp_param,
)

# Fragment shader - animated rainbow effect
FRAGMENT_SHADER = """#version 150

out vec4 fragColor;

uniform vec2 resolution;
uniform float time;

void main() {
    // Normalized coordinates
    vec2 uv = gl_FragCoord.xy / resolution;
    
    // Animated rainbow using cosine palette
    // This creates smooth color cycling based on position and time
    vec3 color = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));
    
    fragColor = vec4(color, 1.0);
}
"""

# Vertex shader
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
    builder.set_resolution(1920, 1080)
    builder.set_author("klproj Example")
    builder.set_comment("Animated rainbow shader using cosine color palette")

    # Add parameters
    builder.add_global_param(create_resolution_param("resolution"))
    builder.add_global_param(create_time_param("time"))

    # Create vertex shader stage
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,
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
        label="Rainbow",
        stages=[vertex_stage, fragment_stage],
        width=1920,
        height=1080,
    )

    builder.add_pass(render_pass)
    builder.save("animated_rainbow.klproj")
    print("✓ Created animated_rainbow.klproj")
    print("  Open it in KodeLife to see the animated rainbow!")


if __name__ == "__main__":
    main()