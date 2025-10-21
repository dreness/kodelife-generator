"""
Test embedded version of plasma shader to verify the shader code works.
"""

from klproj import (
    KodeProjBuilder,
    PassType,
    RenderPass,
    ShaderProfile,
    ShaderSource,
    ShaderStage,
    ShaderStageType,
    create_default_vertex_stage,
    create_shadertoy_params,
)

# Read the plasma shader
with open("plasma.fs", "r") as f:
    PLASMA_SHADER = f.read()


def main():
    """Create embedded version of plasma shader."""
    builder = KodeProjBuilder(api="GL3")
    builder.set_resolution(1280, 720)
    builder.set_author("Embedded Plasma Test")
    builder.set_comment("Testing if plasma shader works when embedded")

    # Add standard Shadertoy parameters
    for param in create_shadertoy_params():
        builder.add_global_param(param)

    # Create stages with EMBEDDED shader (not file-watched)
    vertex_stage = create_default_vertex_stage()

    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.GL3, PLASMA_SHADER)],
    )

    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Main Pass",
        enabled=1,
        stages=[vertex_stage, fragment_stage],
        width=1280,
        height=720,
    )

    builder.add_pass(render_pass)
    builder.save("plasma_embedded_test.klproj")

    print("✓ Created: plasma_embedded_test.klproj")
    print()
    print("This version has the SAME shader code as plasma.fs,")
    print("but it's EMBEDDED in the .klproj file (not file-watched).")
    print()
    print("Open both in KodeLife to compare:")
    print("  - plasma_watch.klproj (file-watched, may not render)")
    print("  - plasma_embedded_test.klproj (embedded, should render)")
    print()
    print("This will help identify if the issue is with:")
    print("  1. The shader code itself (both won't render)")
    print("  2. The file watching feature (only embedded renders)")


if __name__ == "__main__":
    main()
