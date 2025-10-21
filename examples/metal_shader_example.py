#!/usr/bin/env python3
"""
Example: Creating a Metal shader project for KodeLife

This demonstrates how to use the Metal shader generation helpers
to create a complete .klproj file with a visually distinctive Metal shader.

EXPECTED OUTPUT:
    When opened in KodeLife with Metal API selected, you should see:
    - Animated rotating plasma/tunnel effect
    - Vibrant colors (cyan, magenta, yellow) that pulse with time
    - Smooth radial gradient emanating from center
    - Continuous rotation and color cycling
    - The effect should animate smoothly at 60fps
"""

from klproj import (
    KodeProjBuilder,
    PassType,
    RenderPass,
    ShaderStage,
    ShaderStageType,
    create_metal_fragment_source_shadertoy,
    create_metal_vertex_source,
    create_mvp_param,
    create_shadertoy_params,
)

# Custom Metal shader code - Rotating plasma tunnel effect
PLASMA_SHADER = """// Rotating plasma tunnel effect
    float2 uv = (fragCoord.xy / iResolution.xy) * 2.0 - 1.0;
    uv.x *= iResolution.x / iResolution.y;  // Correct aspect ratio

    // Create rotating coordinates
    float angle = iTime * 0.5;
    float2x2 rot = float2x2(cos(angle), -sin(angle), sin(angle), cos(angle));
    uv = rot * uv;

    // Calculate distance and angle for polar coordinates
    float dist = length(uv);
    float angle_uv = atan2(uv.y, uv.x);

    // Create plasma patterns using sine waves
    float plasma1 = sin(dist * 8.0 - iTime * 2.0);
    float plasma2 = sin(angle_uv * 6.0 + iTime * 1.5);
    float plasma3 = sin(dist * 5.0 + angle_uv * 4.0 - iTime);

    // Combine plasma patterns
    float plasma = (plasma1 + plasma2 + plasma3) / 3.0;

    // Create vibrant color cycling
    float3 color1 = float3(0.5 + 0.5 * sin(iTime + 0.0),
                           0.5 + 0.5 * sin(iTime + 2.0),
                           0.5 + 0.5 * sin(iTime + 4.0));
    float3 color2 = float3(0.5 + 0.5 * cos(iTime + 1.0),
                           0.5 + 0.5 * cos(iTime + 3.0),
                           0.5 + 0.5 * cos(iTime + 5.0));

    // Mix colors based on plasma value
    float3 finalColor = mix(color1, color2, plasma * 0.5 + 0.5);

    // Add radial brightness falloff for tunnel effect
    float brightness = 1.0 - smoothstep(0.0, 1.5, dist);
    finalColor *= brightness * 1.5;

    // Add center glow
    float glow = exp(-dist * 3.0) * 0.3;
    finalColor += float3(glow);

    fragColor = float4(finalColor, 1.0);"""


def main():
    """Create a Metal shader project with rotating plasma tunnel effect."""

    print("=" * 70)
    print("CREATING METAL SHADER: Rotating Plasma Tunnel")
    print("=" * 70)

    # Create builder with Metal API
    builder = KodeProjBuilder(api="MTL")
    builder.set_resolution(1280, 720)
    builder.set_author("Metal Shader Generator")
    builder.set_comment("Rotating plasma tunnel effect - Metal shader demo")

    # Add Shadertoy-compatible global parameters
    for param in create_shadertoy_params():
        builder.add_global_param(param)

    # Generate Metal vertex shader
    global_params = create_shadertoy_params()
    mvp_param = create_mvp_param()

    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        parameters=[mvp_param],
        sources=[create_metal_vertex_source(global_params + [mvp_param])],
        enabled=True,
        hidden=True,  # Hide vertex shader in KodeLife UI
    )

    # Generate Metal fragment shader with custom plasma effect
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        parameters=[],  # No per-stage texture parameters in this example
        sources=[
            create_metal_fragment_source_shadertoy(
                global_params, texture_params=None, shader_body=PLASMA_SHADER
            )
        ],
        enabled=True,
        hidden=False,
    )

    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Plasma Tunnel",
        stages=[vertex_stage, fragment_stage],
        width=1280,
        height=720,
    )

    builder.add_pass(render_pass)

    # Save the project
    output_file = "metal_plasma_tunnel.klproj"
    builder.save(output_file)

    print(f"\n✓ Created Metal shader project: {output_file}")
    print("\n" + "=" * 70)
    print("HOW TO USE:")
    print("=" * 70)
    print("1. Open KodeLife application")
    print("2. Go to Preferences > Graphics and select 'Metal' as the API")
    print("3. Open the generated file: metal_plasma_tunnel.klproj")
    print("4. You should see a rotating plasma tunnel effect with:")
    print("   - Vibrant cycling colors (cyan, magenta, yellow)")
    print("   - Smooth rotation around the center")
    print("   - Radial tunnel effect with center glow")
    print("   - Continuous animation")
    print("\n" + "=" * 70)
    print("TECHNICAL DETAILS:")
    print("=" * 70)
    print("- Graphics API: Metal (MTL)")
    print("- Resolution: 1280x720")
    print("- Shader Features:")
    print("  * Polar coordinate transformations")
    print("  * Multiple sine wave plasma patterns")
    print("  * Time-based rotation matrix")
    print("  * Color cycling and mixing")
    print("  * Radial brightness falloff")
    print("  * Center glow effect")
    print("=" * 70)

    # Show a snippet of the generated Metal shader
    print("\nGenerated Metal Fragment Shader (first 40 lines):")
    print("=" * 70)
    metal_code = fragment_stage.sources[0].code
    lines = metal_code.split("\n")
    for i, line in enumerate(lines[:40], 1):
        print(f"{i:3d}│ {line}")
    print("    │ ... (shader continues)")
    print("=" * 70)


if __name__ == "__main__":
    main()
