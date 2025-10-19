# Tutorial: Porting a Metal Shader to KodeLife

This tutorial demonstrates how to port existing Metal shaders (commonly used in macOS/iOS applications) to KodeLife.

## Overview

Metal is Apple's modern graphics API for macOS, iOS, and other Apple platforms. If you have existing Metal shaders from app development or other projects, this tutorial shows you how to create a KodeLife project that uses them.

## Prerequisites

- Python 3.8 or later
- `klproj` package installed
- macOS with Metal support (for testing)
- Basic understanding of Metal Shading Language (MSL)

## Example: Simple Metal Fragment Shader

Let's start with a simple Metal fragment shader that might come from a macOS application:

```metal
// Original Metal fragment shader from a macOS app
#include <metal_stdlib>
using namespace metal;

fragment float4 fragment_main(float4 position [[position]]) {
    return float4(1.0, 0.0, 0.0, 1.0);  // Red
}
```

## Step 1: Understanding KodeLife's Metal Shader Structure

KodeLife uses a specific structure for Metal shaders:

1. **Vertex Shader Input Structure** - Defines vertex attributes
2. **Vertex Shader Output Structure** - Data passed to fragment shader
3. **Uniform Structure** - Parameters passed to shaders
4. **Shader Functions** - Named entry points

Here's how a KodeLife Metal shader is structured:

```metal
#include <metal_stdlib>
using namespace metal;

// Vertex shader input
struct VS_INPUT {
    float4 a_position [[attribute(0)]];
    float3 a_normal   [[attribute(1)]];
    float2 a_texcoord [[attribute(2)]];
};

// Vertex to Fragment
struct VS_OUTPUT {
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
};

// Uniforms
struct VS_UNIFORM {
    float4x4 mvp;
    float2 resolution;
    float time;
};

// Vertex shader
vertex VS_OUTPUT vs_main(
    VS_INPUT input [[stage_in]],
    constant VS_UNIFORM& u [[buffer(16)]]
) {
    VS_OUTPUT out;
    out.v_position = u.mvp * input.a_position;
    out.v_normal = input.a_normal;
    out.v_texcoord = input.a_texcoord;
    return out;
}

// Fragment shader
fragment float4 ps_main(
    VS_OUTPUT input [[stage_in]],
    constant PS_UNIFORM& u [[buffer(16)]]
) {
    return float4(1.0, 0.0, 0.0, 1.0);
}
```

## Step 2: Porting a Simple Fragment Shader

Let's port a gradient shader to KodeLife:

### Original Metal Code (from an app)

```metal
#include <metal_stdlib>
using namespace metal;

struct FragmentInput {
    float4 position [[position]];
    float2 texCoord;
};

fragment float4 gradient_fragment(FragmentInput in [[stage_in]]) {
    float2 uv = in.texCoord;
    float3 color = float3(uv.x, uv.y, 0.5);
    return float4(color, 1.0);
}
```

### Adapted for KodeLife

Create `create_metal_gradient.py`:

```python
#!/usr/bin/env python3
"""Create a Metal gradient shader for KodeLife."""

from klproj import (
    KodeProjBuilder,
    RenderPass,
    PassType,
    ShaderStage,
    ShaderStageType,
    ShaderSource,
    ShaderProfile,
    create_resolution_param,
    create_mvp_param,
)

VERTEX_SHADER = """#include <metal_stdlib>
using namespace metal;

struct VS_INPUT {
    float4 a_position [[attribute(0)]];
    float3 a_normal   [[attribute(1)]];
    float2 a_texcoord [[attribute(2)]];
};

struct VS_OUTPUT {
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
};

struct VS_UNIFORM {
    float4x4 mvp;
    float2 resolution;
};

vertex VS_OUTPUT vs_main(
    VS_INPUT input [[stage_in]],
    constant VS_UNIFORM& u [[buffer(16)]]
) {
    VS_OUTPUT out;
    out.v_position = u.mvp * input.a_position;
    out.v_normal = input.a_normal;
    out.v_texcoord = input.a_texcoord;
    return out;
}
"""

FRAGMENT_SHADER = """#include <metal_stdlib>
using namespace metal;

struct PS_INPUT {
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
};

struct PS_OUTPUT {
    float4 color [[color(0)]];
};

struct PS_UNIFORM {
    float2 resolution;
};

fragment PS_OUTPUT ps_main(
    PS_INPUT input [[stage_in]],
    constant PS_UNIFORM& u [[buffer(16)]]
) {
    PS_OUTPUT out;
    
    // Create gradient based on texture coordinates
    float2 uv = input.v_texcoord;
    float3 color = float3(uv.x, uv.y, 0.5);
    out.color = float4(color, 1.0);
    
    return out;
}
"""

def main():
    builder = KodeProjBuilder(api="MTL")
    builder.set_resolution(1920, 1080)
    builder.set_author("Your Name")
    builder.set_comment("Metal gradient shader")
    
    # Add resolution parameter
    builder.add_global_param(create_resolution_param("resolution"))
    
    # Create vertex shader stage
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,
        sources=[ShaderSource(ShaderProfile.MTL, VERTEX_SHADER)],
        parameters=[create_mvp_param()],
    )
    
    # Create fragment shader stage
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.MTL, FRAGMENT_SHADER)],
    )
    
    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Metal Gradient",
        stages=[vertex_stage, fragment_stage],
        width=1920,
        height=1080,
    )
    
    builder.add_pass(render_pass)
    builder.save("metal_gradient.klproj")
    print("Created metal_gradient.klproj")

if __name__ == "__main__":
    main()
```

## Step 3: Advanced Example - Animated Metal Shader

Let's port an animated shader with time-based effects:

```python
#!/usr/bin/env python3
"""Create an animated Metal shader."""

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

VERTEX_SHADER = """#include <metal_stdlib>
using namespace metal;

struct VS_INPUT {
    float4 a_position [[attribute(0)]];
    float3 a_normal   [[attribute(1)]];
    float2 a_texcoord [[attribute(2)]];
};

struct VS_OUTPUT {
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
};

struct VS_UNIFORM {
    float4x4 mvp;
    float2 resolution;
    float time;
};

vertex VS_OUTPUT vs_main(
    VS_INPUT input [[stage_in]],
    constant VS_UNIFORM& u [[buffer(16)]]
) {
    VS_OUTPUT out;
    out.v_position = u.mvp * input.a_position;
    out.v_normal = input.a_normal;
    out.v_texcoord = input.a_texcoord;
    return out;
}
"""

FRAGMENT_SHADER = """#include <metal_stdlib>
using namespace metal;

struct PS_INPUT {
    float4 v_position [[position]];
    float3 v_normal;
    float2 v_texcoord;
};

struct PS_OUTPUT {
    float4 color [[color(0)]];
};

struct PS_UNIFORM {
    float2 resolution;
    float time;
};

fragment PS_OUTPUT ps_main(
    PS_INPUT input [[stage_in]],
    constant PS_UNIFORM& u [[buffer(16)]]
) {
    PS_OUTPUT out;
    
    // Normalized coordinates
    float2 uv = input.v_texcoord;
    
    // Animated rainbow effect
    float3 color = 0.5 + 0.5 * cos(
        u.time + float3(uv.x, uv.y, uv.x) + float3(0, 2, 4)
    );
    
    out.color = float4(color, 1.0);
    return out;
}
"""

def main():
    builder = KodeProjBuilder(api="MTL")
    builder.set_resolution(1920, 1080)
    builder.set_comment("Animated Metal rainbow shader")
    
    # Add parameters
    builder.add_global_param(create_resolution_param("resolution"))
    builder.add_global_param(create_time_param("time"))
    
    # Create stages
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,
        sources=[ShaderSource(ShaderProfile.MTL, VERTEX_SHADER)],
        parameters=[create_mvp_param()],
    )
    
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.MTL, FRAGMENT_SHADER)],
    )
    
    # Create pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Metal Rainbow",
        stages=[vertex_stage, fragment_stage],
        width=1920,
        height=1080,
    )
    
    builder.add_pass(render_pass)
    builder.save("metal_rainbow.klproj")
    print("Created metal_rainbow.klproj")

if __name__ == "__main__":
    main()
```

## Common Metal to KodeLife Adaptations

### Buffer Bindings

KodeLife always uses buffer(16) for uniforms:

```metal
// Always use this in KodeLife
constant PS_UNIFORM& u [[buffer(16)]]
```

### Attribute Locations

KodeLife uses fixed attribute locations:

```metal
struct VS_INPUT {
    float4 a_position [[attribute(0)]];  // Position always at 0
    float3 a_normal   [[attribute(1)]];  // Normal always at 1
    float2 a_texcoord [[attribute(2)]];  // TexCoord always at 2
};
```

### Output Structure

Always use this structure for fragment output:

```metal
struct PS_OUTPUT {
    float4 color [[color(0)]];
};
```

### Coordinate Spaces

In KodeLife Metal shaders:
- Use `input.v_texcoord` for normalized [0,1] coordinates
- Use `input.v_texcoord * u.resolution` for pixel coordinates
- Multiply by `u.resolution.xy` to get screen-space coordinates

## Cross-Platform Support

To support both Metal and OpenGL, add multiple shader sources:

```python
from klproj import ShaderProfile

fragment_stage = ShaderStage(
    stage_type=ShaderStageType.FRAGMENT,
    enabled=1,
    sources=[
        ShaderSource(ShaderProfile.MTL, metal_fragment_code),
        ShaderSource(ShaderProfile.GL3, gl3_fragment_code),
        ShaderSource(ShaderProfile.GL2, gl2_fragment_code),
    ],
)
```

## Textures and Samplers

If your Metal shader uses textures:

```metal
struct PS_UNIFORM {
    float2 resolution;
    float time;
};

fragment PS_OUTPUT ps_main(
    PS_INPUT input [[stage_in]],
    constant PS_UNIFORM& u [[buffer(16)]],
    texture2d<float> tex [[texture(0)]],
    sampler smp [[sampler(0)]]
) {
    PS_OUTPUT out;
    float4 texColor = tex.sample(smp, input.v_texcoord);
    out.color = texColor;
    return out;
}
```

Add texture parameters in Python:

```python
from klproj import Parameter, ParamType

texture_param = Parameter(
    param_type=ParamType.CONSTANT_TEXTURE_2D,
    display_name="Input Texture",
    variable_name="tex",
)

fragment_stage.parameters.append(texture_param)
```

## Troubleshooting

### Shader Won't Compile

1. Check buffer binding is `[[buffer(16)]]`
2. Verify attribute locations (0, 1, 2)
3. Make sure output uses `[[color(0)]]`
4. Check that all structs match the required format

### Black Screen

1. Verify vertex shader transforms positions correctly
2. Check fragment shader returns valid colors (alpha = 1.0)
3. Make sure uniforms are declared in both vertex and fragment uniforms

### Performance Issues

1. Minimize texture sampling in loops
2. Use `fast::` math functions where precision allows
3. Avoid branching when possible
4. Use `half` precision for mobile targets

## Resources

- [Metal Shading Language Specification](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf)
- [KodeLife Documentation](https://hexler.net/kodelife)
- [Metal Best Practices](https://developer.apple.com/documentation/metal/best_practices)