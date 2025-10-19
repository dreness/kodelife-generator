# KodeLife File Format Documentation

Comprehensive documentation for the KodeLife `.klproj` project file format.

## Overview

KodeLife is a real-time GPU shader editor that saves projects as `.klproj` files. These files are **zlib-compressed XML documents** containing:

- Shader source code for multiple graphics APIs
- Project configuration and metadata
- Rendering passes and pipeline stages
- Global and pass-specific parameters
- Camera transforms and render states
- Audio input configuration

## Quick Start

### Reading a .klproj File

**Python:**

```python
import zlib

with open('project.klproj', 'rb') as f:
    compressed = f.read()
    xml_content = zlib.decompress(compressed).decode('utf-8')
    print(xml_content)
```

### Creating a .klproj File

**Python:**

```python
import zlib

xml_content = """<?xml version='1.0' encoding='UTF-8'?>
<klxml v='19' a='GL3'>
  <document>
    <!-- Your project structure here -->
  </document>
</klxml>"""

compressed = zlib.compress(xml_content.encode('utf-8'))
with open('project.klproj', 'wb') as f:
    f.write(compressed)
```

## Documentation

### [File Format Specification](KODELIFE_FILE_FORMAT.md)

Complete technical specification covering:

- File structure and compression
- XML schema and hierarchy
- All parameter types
- Shader stage configuration
- Graphics API profiles
- Render states

### [Examples](KODELIFE_EXAMPLES.md)

Practical examples demonstrating:

- Minimal projects
- Shadertoy compatibility
- Audio-reactive shaders
- Multi-pass rendering
- Feedback loops
- Custom parameters
- 3D scenes with transforms
- Compute shaders
- Multi-profile shaders

## Key Features

### Multi-API Support

KodeLife projects can contain shader code for multiple graphics APIs:

- **OpenGL** (2.1, 3.x, 4.x)
- **OpenGL ES** (3.0, 3.1, 3.2)
- **Metal** (macOS/iOS)
- **DirectX 9** (Windows)

The application automatically selects the appropriate profile for the current platform.

### Parameter System

Rich parameter system supporting:

- Time and animation controls
- Mouse/touch input
- Audio spectrum analysis
- Custom float/vec2/vec3/vec4 values
- Texture samplers
- Frame buffers (previous frame/pass)
- Transform matrices

### Render Pipeline

Flexible rendering pipeline:

- Multiple render passes
- Compute shader support
- Configurable render states
- Camera and model transforms
- Custom render targets
- Blend modes and depth testing

## Tools

### Extraction Utility

The [`tools/extract_klproj.py`](../tools/extract_klproj.py) script extracts all `.klproj` files to readable XML:

**Bash:**

```bash
python3 tools/extract_klproj.py
```

This creates a `kodelife-format-analysis/` directory with decompressed XML files for inspection.

## File Format Summary

**File Structure:**

```text
.klproj file
└─ zlib compressed
   └─ XML document
      └─ <klxml>
         └─ <document>
            ├─ <properties>     # Project metadata
            ├─ <params>         # Global parameters
            └─ <passes>         # Render/compute passes
               └─ <pass>
                  ├─ <properties>  # Pass configuration
                  ├─ <params>      # Pass parameters
                  └─ <stages>      # Shader stages
                     └─ <stage>
                        ├─ <properties>
                        ├─ <params>
                        └─ <shader>
                           └─ <source profile="...">
                              └─ [Shader Code]
```

## Common Use Cases

### 1. Extracting Shader Code

Extract and study shader code from existing projects for learning purposes.

### 2. Batch Processing

Programmatically modify multiple projects (e.g., updating API versions, changing parameters).

### 3. Version Control

Convert to XML for better diff viewing in version control systems.

### 4. Template Generation

Create project templates with specific configurations.

### 5. Cross-Platform Conversion

Adapt shaders between different graphics APIs.

## Shadertoy Compatibility

KodeLife supports Shadertoy-style shaders with standard uniform names:

- `iResolution` - Viewport resolution
- `iTime` - Current time in seconds
- `iTimeDelta` - Frame delta time
- `iFrame` - Frame number
- `iMouse` - Mouse position/state
- `iDate` - Current date (year, month, day, seconds)
- `iSampleRate` - Audio sample rate
- `iChannel0-3` - Input textures

## Version Information

- **Current Format Version:** 19
- **KodeLife Version:** 1.2.3.202
- **Supported Platforms:** macOS, Windows, Linux, iOS

## Resources

- **Official Website:** [hexler.net/kodelife](https://hexler.net/kodelife)
- **Shadertoy:** [shadertoy.com](https://www.shadertoy.com/)
- **OpenGL Spec:** [khronos.org/opengl](https://www.khronos.org/opengl/)
- **Metal Spec:** [developer.apple.com/metal](https://developer.apple.com/metal/)

## Contributing

To improve this documentation:

1. Analyze additional `.klproj` files
2. Document undocumented features
3. Add more examples
4. Report format changes in new KodeLife versions

## License

This documentation is provided for educational and development purposes. KodeLife is a product of Hexler.

---

**Note:** This documentation was produced by a reverse-engineering effort executed by Claude Sonnet 4.5 and overseen by dre. For official Kodelife product information, consult the [KodeLife site](https://hexler.net/kodelife).
