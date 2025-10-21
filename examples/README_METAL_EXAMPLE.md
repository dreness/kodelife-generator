# Metal Shader Examples

This directory contains examples demonstrating how to create Metal shaders for KodeLife using the klproj library's Metal helper functions.

## Available Examples

### 1. Interactive Plasma Tunnel with Mouse Input (⭐ NEW)
**File:** `metal_plasma_tunnel_mouse.py`

An advanced example showing how to incorporate **mouse input** into Metal shaders for real-time interaction.

### 2. Basic Plasma Tunnel
**File:** `metal_shader_example.py`

The original plasma tunnel example without mouse input - good for understanding the base shader structure.

### 3. Simple Gradient
**File:** `metal_gradient.py`

A minimal Metal shader example showing basic structure.

---

## Example 1: Interactive Plasma Tunnel (Mouse Input) ⭐

**Generated file:** `metal_plasma_tunnel_mouse.klproj`

This example demonstrates advanced mouse interaction techniques in Metal shaders.

### What the Shader Does

The generated shader creates an **interactive rotating plasma tunnel effect** with:
- **Mouse X position**: Controls rotation speed (left = slower/reverse, right = faster)
- **Mouse Y position**: Controls plasma frequency (bottom = smooth, top = complex)
- **Mouse position**: Offsets the tunnel center for exploration
- **Mouse distance**: Affects color cycling speed
- Vibrant, cycling colors (cyan, magenta, yellow)
- Multiple sine wave plasma patterns
- Interactive turbulence based on mouse position
- Mouse-reactive edge glow
- Radial brightness falloff creating a tunnel effect
- Glowing center point that follows mouse offset
- Continuous smooth animation with real-time feedback

### Running the Example

```bash
uv run python examples/metal_plasma_tunnel_mouse.py
```

This will create `metal_plasma_tunnel_mouse.klproj` in the current directory.

### Mouse Interaction Details

The `iMouse` parameter provides:
- `iMouse.xy` - Current mouse position in pixels
- `iMouse.zw` - Click position (updated on mouse down)

In this shader:
1. **Rotation Control**: Mouse X position maps to rotation speed (-2.0 to +2.0 multiplier)
2. **Plasma Frequency**: Mouse Y position adjusts frequency (4.0 to 12.0 range)
3. **Center Offset**: Mouse position offsets the tunnel center by 50% of normalized coordinates
4. **Turbulence**: Mouse position adds directional turbulence to plasma patterns
5. **Color Shift**: Distance from center affects color cycling phase
6. **Edge Glow**: Pulsing edge effect reacts to mouse distance

### Expected Visual Output

When you move your mouse:
- **Left/Right**: Watch the tunnel rotation speed up, slow down, or reverse
- **Up/Down**: See plasma patterns become more intricate or smoother
- **Around screen**: Explore different parts of the tunnel as center shifts
- **Corners**: Maximum color cycling and turbulence effects

---

## Example 2: Basic Plasma Tunnel

**File:** `metal_shader_example.py`
**Generated file:** `metal_plasma_tunnel.klproj`

The original plasma tunnel example without mouse input.

### What the Shader Does

The generated shader creates a **rotating plasma tunnel effect** with:
- Vibrant, cycling colors (cyan, magenta, yellow)
- Smooth rotation around the center (fixed speed)
- Multiple sine wave plasma patterns
- Radial brightness falloff creating a tunnel effect
- Glowing center point
- Continuous smooth animation

### Running the Example

```bash
uv run python examples/metal_shader_example.py
```

This will create `metal_plasma_tunnel.klproj` in the current directory.

---

## Opening Examples in KodeLife

All examples follow the same setup process:

1. **Install KodeLife**: Download from [hexler.net/kodelife](https://hexler.net/kodelife)

2. **Set Metal as Graphics API**:
   - Open KodeLife
   - Go to **Preferences** (or **Settings**)
   - Navigate to **Graphics** section
   - Select **Metal** as the graphics API
   - Restart KodeLife if prompted

3. **Open the Generated File**:
   - File → Open
   - Select the `.klproj` file (e.g., `metal_plasma_tunnel_mouse.klproj`)
   - The shader should start rendering immediately

4. **For Interactive Examples**: Move your mouse around the viewport to see effects!

---

## Technical Details

**Graphics API**: Metal (MTL) - Apple's modern graphics framework

**Common Shader Features**:
- Polar coordinate transformations (Cartesian → Polar)
- Time-based 2D rotation matrix
- Multiple layered sine wave functions for plasma effect
- Color mixing using Metal's `mix()` function
- `smoothstep()` for radial gradient
- Exponential function for center glow
- Aspect ratio correction for proper circle rendering

**Performance**: Highly optimized Metal shader code running directly on GPU

## Code Structure

All Metal examples demonstrate:

1. **Creating a Metal-compatible KodeLife project**:
   ```python
   builder = KodeProjBuilder(api="MTL")
   ```

2. **Adding Shadertoy-compatible parameters** (includes `iMouse`):
   ```python
   for param in create_shadertoy_params():
       builder.add_global_param(param)
   ```

3. **Generating Metal vertex shader**:
   ```python
   vertex_stage = ShaderStage(
       stage_type=ShaderStageType.VERTEX,
       sources=[create_metal_vertex_source(global_params + [mvp_param])]
   )
   ```

4. **Generating Metal fragment shader with custom code**:
   ```python
   fragment_stage = ShaderStage(
       stage_type=ShaderStageType.FRAGMENT,
       sources=[
           create_metal_fragment_source_shadertoy(
               global_params,
               shader_body=PLASMA_SHADER  # Custom Metal shader code
           )
       ]
   )
   ```

## Customization

You can modify any plasma tunnel effect by changing parameters in the shader code:

- **Rotation speed**: Change `iTime * 0.5` to adjust rotation rate
- **Plasma frequency**: Modify the multipliers in `sin(dist * 8.0 - iTime * 2.0)`
- **Color scheme**: Adjust the phase offsets in the color cycling (e.g., `sin(iTime + 0.0)`)
- **Tunnel intensity**: Change the `smoothstep()` parameters for brightness falloff
- **Glow strength**: Modify `exp(-dist * 3.0) * 0.3` for center glow intensity
- **Mouse sensitivity**: Adjust multipliers on `mousePos.x` and `mousePos.y`

## Troubleshooting

**Black screen or no animation**:
- Verify Metal API is selected in KodeLife preferences
- Check that your Mac supports Metal (macOS 10.11+ / 2012 or newer Mac)
- Try restarting KodeLife after changing graphics API

**Mouse not responding** (interactive examples):
- Make sure your mouse is over the KodeLife viewport window
- Try clicking once in the viewport to ensure it has focus
- Check that the `.klproj` includes `iMouse` parameter (should be automatic)

**Performance issues**:
- The shaders are optimized for modern GPUs
- If experiencing stuttering, close other GPU-intensive applications
- Reduce KodeLife window size for better performance

**Shader doesn't match description**:
- Ensure you ran the example script to generate a fresh `.klproj` file
- Check that the file wasn't corrupted during transfer
- Try extracting with `uv run klproj extract` to inspect the XML

## See Also

- `/docs/METAL_SUPPORT.md` - Complete Metal shader generation API
- `/docs/METAL_ANALYSIS.md` - Technical analysis of Metal shader format
- `/tests/test_metal_helpers.py` - Metal helper function tests
- [Metal Shading Language Guide](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf)
