# Tutorial: Porting a GLSL Fragment Shader to KodeLife

This tutorial demonstrates how to port an existing GLSL fragment shader to KodeLife using the `klproj` Python library.

## Overview

Many shader developers have existing GLSL fragment shaders (from Shadertoy, GLSL Sandbox, or custom projects) that they want to use in KodeLife. This tutorial shows you how to create a `.klproj` file from a simple GLSL fragment shader.

## Prerequisites

- Python 3.8 or later
- `klproj` package installed (`pip install -e .` from the project root)
- A GLSL fragment shader you want to port

## Example: Simple Gradient Shader

Let's start with a simple GLSL fragment shader that creates a colorful gradient:

```glsl
// Original GLSL fragment shader
void main() {
    vec2 uv = gl_FragCoord.xy / vec2(800.0, 600.0);
    vec3 color = vec3(uv.x, uv.y, 0.5);
    gl_FragColor = vec4(color, 1.0);
}
```

## Step 1: Adapt the Shader Code

KodeLife uses a specific format for shaders. For GLSL 150 (OpenGL 3.x), we need to:

1. Add the GLSL version directive
2. Use `out vec4` instead of `gl_FragColor`
3. Add proper uniforms for resolution

Here's the adapted shader:

```glsl
#version 150

out vec4 fragColor;

uniform vec2 resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec3 color = vec3(uv.x, uv.y, 0.5);
    fragColor = vec4(color, 1.0);
}
```

## Step 2: Create the Python Script

Create a new Python file `create_gradient.py`:

```python
#!/usr/bin/env python3
"""Create a simple gradient shader for KodeLife."""

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

# Fragment shader code
FRAGMENT_SHADER = """#version 150

out vec4 fragColor;

uniform vec2 resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec3 color = vec3(uv.x, uv.y, 0.5);
    fragColor = vec4(color, 1.0);
}
"""

# Simple vertex shader (required by KodeLife)
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
    builder.set_author("Your Name")
    builder.set_comment("Simple gradient shader")
    
    # Add resolution parameter
    builder.add_global_param(create_resolution_param("resolution"))
    
    # Create vertex shader stage
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,  # Hide vertex shader in UI
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
    builder.save("gradient.klproj")
    print("Created gradient.klproj - open it in KodeLife!")

if __name__ == "__main__":
    main()
```

## Step 3: Run the Script

```bash
python create_gradient.py
```

This creates `gradient.klproj` which you can open in KodeLife.

## Advanced Example: Animated Shader

Let's port a more complex shader with animation:

```glsl
// Original animated shader
uniform float time;
uniform vec2 resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec3 color = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));
    gl_FragColor = vec4(color, 1.0);
}
```

Adapted for KodeLife:

```python
#!/usr/bin/env python3
"""Create an animated rainbow shader."""

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

FRAGMENT_SHADER = """#version 150

out vec4 fragColor;

uniform float time;
uniform vec2 resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec3 color = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));
    fragColor = vec4(color, 1.0);
}
"""

VERTEX_SHADER = """#version 150

in vec4 a_position;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""

def main():
    builder = KodeProjBuilder(api="GL3")
    builder.set_resolution(1920, 1080)
    builder.set_comment("Animated rainbow shader")
    
    # Add parameters
    builder.add_global_param(create_resolution_param("resolution"))
    builder.add_global_param(create_time_param("time"))
    
    # Create stages
    vertex_stage = ShaderStage(
        stage_type=ShaderStageType.VERTEX,
        enabled=1,
        hidden=1,
        sources=[ShaderSource(ShaderProfile.GL3, VERTEX_SHADER)],
        parameters=[create_mvp_param()],
    )
    
    fragment_stage = ShaderStage(
        stage_type=ShaderStageType.FRAGMENT,
        enabled=1,
        sources=[ShaderSource(ShaderProfile.GL3, FRAGMENT_SHADER)],
    )
    
    # Create pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Rainbow",
        stages=[vertex_stage, fragment_stage],
        width=1920,
        height=1080,
    )
    
    builder.add_pass(render_pass)
    builder.save("rainbow.klproj")
    print("Created rainbow.klproj")

if __name__ == "__main__":
    main()
```

## Common Shader Adaptations

### Resolution

```glsl
// Before
gl_FragCoord.xy / vec2(1920.0, 1080.0)

// After (add uniform)
uniform vec2 resolution;
gl_FragCoord.xy / resolution
```

### Time

```glsl
// Before (if using a hardcoded value or custom time)
float time = 1.5;

// After (add uniform)
uniform float time;
```

### Output

```glsl
// Before (GLSL 120 or older)
gl_FragColor = vec4(color, 1.0);

// After (GLSL 150+)
out vec4 fragColor;
fragColor = vec4(color, 1.0);
```

## Multi-Profile Support

To support multiple shader profiles (OpenGL 2, OpenGL 3, Metal, etc.), add multiple sources:

```python
fragment_stage = ShaderStage(
    stage_type=ShaderStageType.FRAGMENT,
    enabled=1,
    sources=[
        ShaderSource(ShaderProfile.GL3, gl3_fragment_code),
        ShaderSource(ShaderProfile.GL2, gl2_fragment_code),
        ShaderSource(ShaderProfile.MTL, metal_fragment_code),
    ],
)
```

## Next Steps

- Explore the [Metal shader tutorial](02_porting_metal_shader.md) for macOS-specific shaders
- Check out the [examples](../examples/) directory for more complex projects
- Read the [API documentation](../docs/API.md) for complete reference

## Troubleshooting

### Shader doesn't compile in KodeLife

1. Check the GLSL version directive matches your target profile
2. Verify all uniforms are declared correctly
3. Make sure you're using the correct output variable name
4. Check the KodeLife console for compilation errors

### Missing uniforms

Make sure to add parameters for all uniforms used in your shader:

```python
builder.add_global_param(create_resolution_param("resolution"))
builder.add_global_param(create_time_param("time"))
builder.add_global_param(create_mouse_param("mouse"))
