# KodeLife Shader Templates

These templates were extracted from the KodeLife application binary and represent the base shader structures used by the application.

## Templates

### 1. Shadertoy Template (Modern GLSL 1.50)

**File:** `shadertoy-template.glsl`

This template uses GLSL version 1.50 (OpenGL 3.2+) and provides:
- Structured vertex data input (`VertexData`)
- Fragment shader output (`fragColor`)
- Standard Shadertoy uniforms:
  - `iResolution` - viewport resolution (in pixels)
  - `iTime` - shader playback time (in seconds)
  - `iTimeDelta` - render time (in seconds)
  - `iFrame` - shader playback frame
  - `iMouse` - mouse pixel coords
  - `iDate` - (year, month, day, time in seconds)
  - `iChannel0-3` - input channel textures

### 2. Shadertoy Template (OpenGL ES)

**File:** `shadertoy-template-gles.glsl`

This template is compatible with OpenGL ES and provides:
- Compatibility defines for `texture` and `textureLod`
- Uses `varying` instead of `in`/`out`
- Uses `gl_FragColor` instead of `out fragColor`
- Precision qualifiers for mobile compatibility
- Same uniform interface as modern template

## Usage

Both templates follow the Shadertoy convention where you implement the `mainImage` function:

```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // fragCoord is pixel coordinate (0 to iResolution)
    // Normalize to 0-1 range:
    vec2 uv = fragCoord / iResolution.xy;
    
    // Your shader code here
    
    fragColor = vec4(color, 1.0);
}
```

## Binary Source

These templates were found at the following addresses in the KodeLife binary:
- Modern GLSL: `0x101b110fb`
- OpenGL ES: `0x101b10e46`

The templates are embedded in the application and used as the basis for new shader projects, particularly those following Shadertoy conventions.