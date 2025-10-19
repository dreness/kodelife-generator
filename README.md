# KodeLife Project Generator

A Python library for creating [KodeLife](https://hexler.net/kodelife) `.klproj` files programmatically. Build shader projects with multiple passes, parameters, and shader profiles (OpenGL, Metal, DirectX) using a clean, well-documented Python API.

## Features

- 🎨 **Multi-Profile Support** - Create shaders for GL2, GL3, Metal, DirectX, and OpenGL ES
- 🔧 **Fluent API** - Easy-to-use builder pattern for constructing projects
- 📝 **Well Documented** - Comprehensive docstrings and type hints throughout
- 🚀 **Shadertoy Compatible** - Built-in helpers for Shadertoy-style shaders
- 🎬 **Multi-Pass Rendering** - Support for complex multi-pass effects
- 🎛️ **Rich Parameters** - Time, resolution, mouse, audio, custom uniforms, and more

## Quick Start

### Installation

This project uses [uv](https://github.com/astral-sh/uv) for Python package management. Install it first:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd kodelife-generator

# Install the package in development mode
uv pip install -e .
```

> **Note**: All commands in this README use `uv run` which automatically manages the virtual environment for you.

### Your First Shader

Run an example to verify installation:

```bash
cd examples
uv run python simple_gradient.py
```

This creates [`simple_gradient.klproj`](examples/simple_gradient.py) - open it in KodeLife!

### Create Your Own

Create a file `my_shader.py`:

```python
#!/usr/bin/env python3
from klproj import *

# Fragment shader code
FRAGMENT = """#version 150
out vec4 fragColor;
uniform vec2 iResolution;
uniform float iTime;

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution;
    vec3 col = 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0,2,4));
    fragColor = vec4(col, 1.0);
}
"""

# Minimal vertex shader (required)
VERTEX = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }
"""

# Build the project
builder = KodeProjBuilder(api="GL3")
builder.set_resolution(1920, 1080)

# Add Shadertoy-compatible parameters
for param in create_shadertoy_params():
    builder.add_global_param(param)

# Create shaders
vertex = ShaderStage(
    stage_type=ShaderStageType.VERTEX,
    enabled=1, hidden=1,
    sources=[ShaderSource(ShaderProfile.GL3, VERTEX)],
    parameters=[create_mvp_param()]
)

fragment = ShaderStage(
    stage_type=ShaderStageType.FRAGMENT,
    enabled=1,
    sources=[ShaderSource(ShaderProfile.GL3, FRAGMENT)]
)

# Create pass and save
pass1 = RenderPass(
    pass_type=PassType.RENDER,
    label="Rainbow",
    stages=[vertex, fragment]
)

builder.add_pass(pass1)
builder.save("my_shader.klproj")
print("✓ Created my_shader.klproj - open it in KodeLife!")
```

Run it:

```bash
uv run python my_shader.py
```

## Common Tasks

### Change Resolution

```python
builder.set_resolution(1280, 720)  # HD
builder.set_resolution(3840, 2160)  # 4K
```

### Add Mouse Interaction

```python
builder.add_global_param(create_mouse_param("iMouse"))
```

### Multi-Platform Support

```python
fragment = ShaderStage(
    stage_type=ShaderStageType.FRAGMENT,
    sources=[
        ShaderSource(ShaderProfile.GL3, glsl_code),
        ShaderSource(ShaderProfile.MTL, metal_code),
        ShaderSource(ShaderProfile.ES3, gles_code),
    ]
)
```

### Custom Parameters

```python
from klproj import Parameter, ParamType, Vec4

color_param = Parameter(
    param_type=ParamType.CONSTANT_FLOAT4,
    display_name="Tint Color",
    variable_name="tintColor",
    properties={
        'value': Vec4(1.0, 0.5, 0.2, 1.0),
        'min': Vec4(0, 0, 0, 0),
        'max': Vec4(1, 1, 1, 1),
    },
)
builder.add_global_param(color_param)
```

## Examples and Tutorials

### Examples

Check the [`examples/`](examples/) directory for complete, runnable examples:

- **Simple Gradient** - Basic shader with color gradients
- **Animated Rainbow** - Time-based animation
- **Shadertoy Template** - Full Shadertoy compatibility
- **Multi-Profile** - Same shader for GL3, GL2, Metal, and ES3

```bash
cd examples
uv run python animated_rainbow.py
uv run python shadertoy_template.py
```

### Tutorials

- 📘 [Porting GLSL Fragment Shaders](tutorials/01_porting_glsl_fragment_shader.md) - Learn how to convert existing GLSL shaders
- 🍎 [Porting Metal Shaders](tutorials/02_porting_metal_shader.md) - Convert Metal shaders from macOS applications

## CLI Tools

The package includes command-line tools for working with `.klproj` files:

```bash
# Convert ISF file(s) to .klproj
uv run klproj convert shader.fs                           # Output to same directory
uv run klproj convert shader1.fs shader2.fs -o output/    # Convert multiple files
uv run klproj convert shader.fs -w 1280 --height 720      # Custom dimensions
uv run klproj convert shader.fs -a GL2                    # Use GL2 profile

# Extract a .klproj file to XML
uv run klproj extract input.klproj output.xml

# Verify a .klproj file
uv run klproj verify myshader.klproj
```

## API Overview

### Core Classes

- **[`KodeProjBuilder`](src/klproj/generator.py)** - Main builder for creating projects
- **[`RenderPass`](src/klproj/types.py)** - Defines a rendering or compute pass
- **[`ShaderStage`](src/klproj/types.py)** - Vertex, fragment, or compute shader stage
- **[`ShaderSource`](src/klproj/types.py)** - Shader code for a specific profile
- **[`Parameter`](src/klproj/types.py)** - Uniform parameters (time, resolution, custom values)

### Enums

- **`ShaderProfile`** - GL2, GL3, MTL, ES3, DX9
- **`ShaderStageType`** - VERTEX, FRAGMENT, COMPUTE, GEOMETRY
- **`PassType`** - RENDER, COMPUTE
- **`ParamType`** - CLOCK, FRAME_RESOLUTION, INPUT_MOUSE, etc.

### Helper Functions

- **[`create_shadertoy_params()`](src/klproj/helpers.py)** - Standard Shadertoy uniforms (iTime, iResolution, iMouse, etc.)
- **[`create_mvp_param()`](src/klproj/helpers.py)** - Model-View-Projection matrix
- **[`create_time_param()`](src/klproj/helpers.py)** - Time parameter
- **[`create_resolution_param()`](src/klproj/helpers.py)** - Resolution parameter
- **[`create_mouse_param()`](src/klproj/helpers.py)** - Mouse input parameter

## Documentation

- 📖 [KodeLife File Format](docs/KODELIFE_FILE_FORMAT.md) - Complete format specification
- 📚 [API Reference](docs/API.md) - Detailed API documentation
- 🎓 [Examples Index](examples/README.md) - All example scripts

## Project Structure

```text
kodelife-generator/
├── src/klproj/           # Main package
│   ├── __init__.py       # Public API exports
│   ├── types.py          # Data classes and enums
│   ├── generator.py      # Project builder
│   ├── helpers.py        # Helper functions
│   └── cli.py            # Command-line tools
├── tutorials/            # Step-by-step guides
├── examples/             # Example scripts
├── docs/                 # Documentation
└── extras/               # Additional resources
    ├── tools/            # Legacy tools
    └── kodelife-format-analysis/  # Format analysis files
```

## Troubleshooting

**Import errors?**

```bash
# Make sure you installed the package
uv pip install -e .
```

**Shader won't open?**

- Check for Python errors in the console
- Verify the .klproj file was created
- Make sure KodeLife is installed

**Black screen in KodeLife?**

- Check shader compilation errors in KodeLife console
- Make sure you're returning `vec4(color, 1.0)` with alpha=1.0
- Verify all uniforms are declared

## Resources

- [KodeLife Official Site](https://hexler.net/kodelife)
- [KodeLife Documentation](https://hexler.net/kodelife/docs)
- [Shadertoy](https://www.shadertoy.com) - Shader examples and inspiration
- [The Book of Shaders](https://thebookofshaders.com) - Learn shader programming

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- [KodeLife](https://hexler.net/kodelife)
- Anthropic's [Claude Sonnet 4.5](https://www.anthropic.com/news/claude-sonnet-4-5)
- [Hopper Disassembler](https://www.hopperapp.com)
