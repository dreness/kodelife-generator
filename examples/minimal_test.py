"""
Minimal test case - the simplest possible shader that should work.
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
)

# Simplest possible fragment shader - just output red
FRAGMENT_SHADER = """#version 150

out vec4 fragColor;

void main() {
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red
}
"""

# Simplest possible vertex shader - FIXED attribute names
VERTEX_SHADER = """#version 150

in vec4 a_position;
in vec3 a_normal;
in vec2 a_texcoord;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""


def main():
    builder = KodeProjBuilder(api="GL3")
    builder.set_resolution(1280, 720)

    # Vertex stage
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.GL3, VERTEX_SHADER)],
        parameters=[create_mvp_param()],
    )

    # Fragment stage
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.GL3, FRAGMENT_SHADER)],
    )

    # Render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Test",
        enabled=1,
        stages=[vertex_stage, fragment_stage],
        width=1280,
        height=720,
    )

    builder.add_pass(render_pass)
    builder.save("minimal_test.klproj")
    print("✓ Created: minimal_test.klproj")


if __name__ == "__main__":
    main()
