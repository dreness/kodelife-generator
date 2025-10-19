# KodeLife Project Generator Tutorials

## Available Tutorials

### 1. [Porting a GLSL Fragment Shader](01_porting_glsl_fragment_shader.md)

**Level:** Beginner  
**Time:** 15 minutes

Learn how to port existing GLSL fragment shaders (from Shadertoy, GLSL Sandbox, or custom projects) to KodeLife. This tutorial covers:

- Adapting GLSL code for KodeLife's structure
- Adding required uniforms and parameters
- Creating the Python script to generate `.klproj` files
- Handling resolution, time, and other common parameters

**You'll create:**

- A simple gradient shader
- An animated rainbow effect

### 2. [Porting a Metal Shader](02_porting_metal_shader.md)

**Level:** Intermediate  
**Time:** 20 minutes  
**Platform:** macOS only

Learn how to port Metal Shading Language (MSL) shaders from macOS applications to KodeLife. This tutorial covers:

- Understanding KodeLife's Metal shader structure
- Proper attribute and buffer bindings
- Creating vertex and fragment shader pairs
- Working with Metal-specific features

**You'll create:**

- A Metal gradient shader
- An animated Metal shader with time-based effects

## Quick Reference

### Common Patterns

#### Basic Project Setup

```python
from klproj import KodeProjBuilder

builder = KodeProjBuilder(api="GL3")
builder.set_resolution(1920, 1080)
builder.set_author("Your Name")
```

#### Add Time Parameter

```python
from klproj import create_time_param

builder.add_global_param(create_time_param("time"))
```

#### Add Resolution Parameter

```python
from klproj import create_resolution_param

builder.add_global_param(create_resolution_param("resolution"))
```

#### Shadertoy Compatibility

```python
from klproj import create_shadertoy_params

for param in create_shadertoy_params():
    builder.add_global_param(param)
```

## Tips for Success

### GLSL Shaders

- Always specify the GLSL version: `#version 150`
- Use `out vec4 fragColor` instead of `gl_FragColor`
- Make sure all uniforms are declared
- Test with simple colors first before complex effects

### Metal Shaders

- Use `[[buffer(16)]]` for uniform buffers
- Follow the required struct naming conventions
- Use proper attribute locations (0, 1, 2)
- Remember Metal uses different coordinate systems

### General

- Start simple and build complexity gradually
- Check the console for shader compilation errors
- Use the examples as templates
- Read the error messages - they're usually helpful!

## Additional Resources

- [KodeLife Official Documentation](https://hexler.net/kodelife/docs)
- [The Book of Shaders](https://thebookofshaders.com)
- [Shadertoy](https://www.shadertoy.com)
- [Metal Shading Language Spec](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf)
