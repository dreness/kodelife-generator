#!/usr/bin/env python3
"""
Example: Metal Plasma Tunnel with Mouse Interaction

This demonstrates how to incorporate mouse input into a Metal shader for KodeLife.
The mouse affects multiple aspects of the plasma tunnel effect:
- X position controls rotation speed
- Y position controls plasma frequency
- Mouse position offsets the tunnel center
- Creates an interactive, responsive visual experience

EXPECTED OUTPUT:
    When opened in KodeLife with Metal API selected, you should see:
    - Animated rotating plasma/tunnel effect
    - Vibrant colors (cyan, magenta, yellow) that pulse with time
    - Mouse movement changes rotation speed and plasma patterns
    - Tunnel center follows mouse position
    - Smooth radial gradient emanating from center
    - The effect should respond immediately to mouse input
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

# Custom Metal shader code - Interactive plasma tunnel effect
PLASMA_SHADER_WITH_MOUSE = """
// Interactive rotating plasma tunnel effect
// Normalize coordinates to [-1, 1] range
float2 uv = (fragCoord.xy / iResolution.xy) * 2.0 - 1.0;
uv.x *= iResolution.x / iResolution.y;  // Correct aspect ratio

// Mouse interaction: iMouse.xy contains mouse position, iMouse.zw contains click position
// Normalize mouse coordinates to [-1, 1] range
float2 mousePos = (iMouse.xy / iResolution.xy) * 2.0 - 1.0;
mousePos.x *= iResolution.x / iResolution.y;

// Use mouse X position to control rotation speed (range: -2.0 to 2.0)
float rotationSpeed = mousePos.x * 2.0;

// Offset tunnel center based on mouse position for interactive exploration
uv -= mousePos * 0.5;

// Create rotating coordinates with mouse-controlled speed
float angle = iTime * (0.5 + rotationSpeed);
float2x2 rot = float2x2(cos(angle), -sin(angle), sin(angle), cos(angle));
uv = rot * uv;

// Calculate distance and angle for polar coordinates
float dist = length(uv);
float angle_uv = atan2(uv.y, uv.x);

// Use mouse Y position to control plasma frequency (range: 4.0 to 12.0)
float plasmaFreq = 8.0 + mousePos.y * 4.0;

// Create plasma patterns using sine waves with mouse-influenced frequency
float plasma1 = sin(dist * plasmaFreq - iTime * 2.0);
float plasma2 = sin(angle_uv * 6.0 + iTime * 1.5);
float plasma3 = sin(dist * 5.0 + angle_uv * 4.0 - iTime);

// Add mouse-influenced turbulence
float turbulence = sin(dist * 10.0 + mousePos.x * 3.14159) *
                   cos(angle_uv * 8.0 + mousePos.y * 3.14159);

// Combine plasma patterns with turbulence
float plasma = (plasma1 + plasma2 + plasma3 + turbulence * 0.3) / 3.3;

// Create vibrant color cycling influenced by mouse position
float colorShift = length(mousePos) * 2.0;
float3 color1 = float3(
    0.5 + 0.5 * sin(iTime + colorShift + 0.0),
    0.5 + 0.5 * sin(iTime + colorShift + 2.0),
    0.5 + 0.5 * sin(iTime + colorShift + 4.0)
);
float3 color2 = float3(
    0.5 + 0.5 * cos(iTime - colorShift + 1.0),
    0.5 + 0.5 * cos(iTime - colorShift + 3.0),
    0.5 + 0.5 * cos(iTime - colorShift + 5.0)
);

// Mix colors based on plasma value
float3 finalColor = mix(color1, color2, plasma * 0.5 + 0.5);

// Add radial brightness falloff for tunnel effect
// Distance from current position (affected by mouse offset)
float brightness = 1.0 - smoothstep(0.0, 1.5, dist);
finalColor *= brightness * 1.5;

// Add center glow that follows the mouse-influenced center
float glow = exp(-dist * 3.0) * 0.3;

// Add mouse-reactive edge glow
float edgeGlow = smoothstep(0.5, 1.2, dist) * (1.0 - smoothstep(1.2, 1.8, dist));
edgeGlow *= 0.2 + 0.3 * sin(iTime * 3.0 + length(mousePos) * 6.28);

finalColor += float3(glow + edgeGlow);

// Add subtle vignette
float vignette = 1.0 - length(uv + mousePos * 0.3) * 0.3;
finalColor *= vignette;

fragColor = float4(finalColor, 1.0);
"""


def main():
    """Create a Metal shader project with interactive mouse-controlled plasma tunnel."""

    print("=" * 70)
    print("CREATING METAL SHADER: Interactive Plasma Tunnel (Mouse Input)")
    print("=" * 70)

    # Create builder with Metal API
    builder = KodeProjBuilder(api="MTL")
    builder.set_resolution(1280, 720)
    builder.set_author("Metal Shader Generator")
    builder.set_comment("Interactive plasma tunnel with mouse input - Metal shader demo")

    # Add Shadertoy-compatible global parameters (includes iMouse)
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

    # Generate Metal fragment shader with interactive plasma effect
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        parameters=[],  # No per-stage texture parameters in this example
        sources=[
            create_metal_fragment_source_shadertoy(
                global_params, texture_params=None, shader_body=PLASMA_SHADER_WITH_MOUSE
            )
        ],
        enabled=True,
        hidden=False,
    )

    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Interactive Plasma Tunnel",
        stages=[vertex_stage, fragment_stage],
        width=1280,
        height=720,
    )

    builder.add_pass(render_pass)

    # Save the project
    output_file = "metal_plasma_tunnel_mouse.klproj"
    builder.save(output_file)

    print(f"\n✓ Created Metal shader project: {output_file}")
    print("\n" + "=" * 70)
    print("HOW TO USE:")
    print("=" * 70)
    print("1. Open KodeLife application")
    print("2. Go to Preferences > Graphics and select 'Metal' as the API")
    print("3. Open the generated file: metal_plasma_tunnel_mouse.klproj")
    print("4. Move your mouse around the viewport to interact!")
    print("\n" + "=" * 70)
    print("MOUSE INTERACTION:")
    print("=" * 70)
    print("- Mouse X position: Controls rotation speed")
    print("  * Left side → rotates slower/backwards")
    print("  * Right side → rotates faster/forwards")
    print("- Mouse Y position: Controls plasma frequency")
    print("  * Bottom → lower frequency (smoother patterns)")
    print("  * Top → higher frequency (more complex patterns)")
    print("- Mouse position: Offsets the tunnel center")
    print("  * Move mouse to explore different parts of the tunnel")
    print("- Distance from center: Affects color cycling speed")
    print("\n" + "=" * 70)
    print("VISUAL EFFECTS:")
    print("=" * 70)
    print("- Vibrant cycling colors (cyan, magenta, yellow)")
    print("- Smooth rotation controlled by mouse X")
    print("- Radial tunnel effect with center glow")
    print("- Mouse-reactive edge glow")
    print("- Plasma patterns that respond to mouse Y")
    print("- Interactive turbulence based on mouse position")
    print("- Subtle vignette that follows mouse offset")
    print("- Continuous animation")
    print("\n" + "=" * 70)
    print("TECHNICAL DETAILS:")
    print("=" * 70)
    print("- Graphics API: Metal (MTL)")
    print("- Resolution: 1280x720")
    print("- Input Parameters:")
    print("  * iMouse (float4): Mouse position and click state")
    print("  * iTime (float): Animation time")
    print("  * iResolution (float2): Viewport resolution")
    print("- Shader Features:")
    print("  * Polar coordinate transformations")
    print("  * Mouse-controlled rotation matrix")
    print("  * Dynamic plasma frequency adjustment")
    print("  * Multiple sine wave plasma patterns")
    print("  * Mouse-influenced turbulence")
    print("  * Interactive color cycling")
    print("  * Radial brightness falloff")
    print("  * Center glow with mouse offset")
    print("  * Edge glow with mouse reactivity")
    print("=" * 70)

    # Show a snippet of the generated Metal shader
    print("\nGenerated Metal Fragment Shader (first 50 lines):")
    print("=" * 70)
    metal_code = fragment_stage.sources[0].code
    lines = metal_code.split("\n")
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3d}│ {line}")
    if len(lines) > 50:
        print("    │ ... (shader continues)")
    print("=" * 70)


if __name__ == "__main__":
    main()
