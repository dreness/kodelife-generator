# KodeLife File Format Examples

This document provides practical examples of different features in the KodeLife `.klproj` file format.

## Example 1: Minimal Project

A minimal KodeLife project with a simple fragment shader:

**XML:**

```xml
<?xml version='1.0' encoding='UTF-8'?>
<klxml v='19' a='GL3'>
  <document>
    <properties>
      <creator><![CDATA[net.hexler.KodeLife]]></creator>
      <creatorVersion><![CDATA[1.2.3.202]]></creatorVersion>
      <versionMajor>1</versionMajor>
      <versionMinor>0</versionMinor>
      <versionPatch>0</versionPatch>
      <author><![CDATA[]]></author>
      <comment><![CDATA[Minimal Example]]></comment>
      <enabled>1</enabled>
      <size><x>1280</x><y>720</y></size>
      <format><![CDATA[RGBA32F]]></format>
      <clearColor><x>0</x><y>0</y><z>0</z><w>1</w></clearColor>
    </properties>
    
    <params>
      <uiExpanded>1</uiExpanded>
      <param type='CLOCK'>
        <displayName><![CDATA[time]]></displayName>
        <variableName><![CDATA[time]]></variableName>
        <running>1</running>
        <speed>1</speed>
      </param>
      <param type='FRAME_RESOLUTION'>
        <displayName><![CDATA[resolution]]></displayName>
        <variableName><![CDATA[resolution]]></variableName>
      </param>
    </params>
    
    <passes>
      <pass type='RENDER'>
        <properties>
          <label><![CDATA[Main]]></label>
          <enabled>1</enabled>
          <primitiveType><![CDATA[TRIANGLES]]></primitiveType>
        </properties>
        
        <stages>
          <stage type='FRAGMENT'>
            <properties><enabled>1</enabled></properties>
            <shader>
              <source profile='GL3'><![CDATA[#version 150
uniform float time;
uniform vec2 resolution;
out vec4 fragColor;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    fragColor = vec4(uv, 0.5 + 0.5*sin(time), 1.0);
}
]]></source>
            </shader>
          </stage>
        </stages>
      </pass>
    </passes>
  </document>
</klxml>
```

## Example 2: Shadertoy-Compatible Project

A project configured for Shadertoy compatibility:

**XML:**

```xml
<params>
  <param type='FRAME_RESOLUTION'>
    <displayName><![CDATA[iResolution]]></displayName>
    <variableName><![CDATA[iResolution]]></variableName>
  </param>
  
  <param type='CLOCK'>
    <displayName><![CDATA[iTime]]></displayName>
    <variableName><![CDATA[iTime]]></variableName>
    <running>1</running>
    <speed>1</speed>
  </param>
  
  <param type='INPUT_MOUSE_SIMPLE'>
    <displayName><![CDATA[iMouse]]></displayName>
    <variableName><![CDATA[iMouse]]></variableName>
    <variant>1</variant>
    <normalize>0</normalize>
    <invert><x>0</x><y>1</y></invert>
  </param>
  
  <param type='CONSTANT_TEXTURE_2D'>
    <displayName><![CDATA[iChannel0]]></displayName>
    <variableName><![CDATA[iChannel0]]></variableName>
    <samplerState>
      <minFilter><![CDATA[LINEAR]]></minFilter>
      <magFilter><![CDATA[LINEAR]]></magFilter>
      <wrapS><![CDATA[CLAMP]]></wrapS>
      <wrapT><![CDATA[CLAMP]]></wrapT>
    </samplerState>
  </param>
</params>
```

**Fragment Shader:**

**GLSL:**

```glsl
#version 150

uniform vec2 iResolution;
uniform float iTime;
uniform vec4 iMouse;
uniform sampler2D iChannel0;

out vec4 fragColor;

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    vec2 uv = fragCoord / iResolution.xy;
    vec3 col = texture(iChannel0, uv).rgb;
    col *= 0.5 + 0.5*sin(iTime);
    fragColor = vec4(col, 1.0);
}

void main() { 
    mainImage(fragColor, gl_FragCoord.xy); 
}
```

## Example 3: Audio-Reactive Shader

Using audio spectrum input:

**XML:**

```xml
<params>
  <param type='AUDIO_SPECTRUM_FULL'>
    <displayName><![CDATA[Audio Spectrum]]></displayName>
    <variableName><![CDATA[audioSpectrum]]></variableName>
    <variant>0</variant>
    <samplerState>
      <minFilter><![CDATA[LINEAR]]></minFilter>
      <magFilter><![CDATA[LINEAR]]></magFilter>
      <wrapS><![CDATA[CLAMP]]></wrapS>
      <wrapT><![CDATA[CLAMP]]></wrapT>
    </samplerState>
  </param>
  
  <param type='CONSTANT_FLOAT1'>
    <displayName><![CDATA[Amplitude]]></displayName>
    <variableName><![CDATA[amplitude]]></variableName>
    <value>3.0</value>
    <range><x><x>0</x><y>10</y></x></range>
  </param>
</params>
```

**Fragment Shader:**

**GLSL:**

```glsl
uniform sampler2D audioSpectrum;
uniform float amplitude;

float getAudioValue(float freq) {
    float x = mod(freq, 16.0) / 16.0;
    float y = floor(freq / 16.0) / 16.0;
    return texture(audioSpectrum, vec2(x, y)).a;
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    float freq = uv.x * 255.0;
    float audioLevel = amplitude * getAudioValue(freq);
    float bar = float(audioLevel >= uv.y);
    fragColor = vec4(vec3(bar), 1.0);
}
```

## Example 4: Multi-Pass Feedback

Two-pass setup with feedback loop:

**XML:**

```xml
<passes>
  <!-- Pass A: Process and store -->
  <pass type='RENDER'>
    <properties>
      <label><![CDATA[Buffer A]]></label>
      <enabled>1</enabled>
    </properties>
    
    <params>
      <param type='FRAME_PREV_PASS'>
        <displayName><![CDATA[Previous Pass]]></displayName>
        <variableName><![CDATA[prevPass]]></variableName>
        <attachment>1</attachment>
      </param>
    </params>
    
    <stages>
      <stage type='FRAGMENT'>
        <shader>
          <source profile='GL3'><![CDATA[
uniform sampler2D prevPass;
uniform float time;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec4 prev = texture(prevPass, uv);
    
    // Feedback with decay
    fragColor = prev * 0.95 + vec4(0.1*sin(time + uv.x*10.0));
}
]]></source>
        </shader>
      </stage>
    </stages>
  </pass>
  
  <!-- Pass B: Display -->
  <pass type='RENDER'>
    <properties>
      <label><![CDATA[Display]]></label>
      <enabled>1</enabled>
    </properties>
    
    <params>
      <param type='FRAME_PREV_FRAME'>
        <displayName><![CDATA[Previous Frame]]></displayName>
        <variableName><![CDATA[prevFrame]]></variableName>
      </param>
    </params>
  </pass>
</passes>
```

## Example 5: Custom Parameters

Using various custom parameter types:

**XML:**

```xml
<params>
  <!-- Float slider -->
  <param type='CONSTANT_FLOAT1'>
    <displayName><![CDATA[Speed]]></displayName>
    <variableName><![CDATA[speed]]></variableName>
    <value>1.0</value>
    <range><x><x>0</x><y>5</y></x></range>
  </param>
  
  <!-- Vec2 -->
  <param type='CONSTANT_FLOAT2'>
    <displayName><![CDATA[Offset]]></displayName>
    <variableName><![CDATA[offset]]></variableName>
    <value><x>0</x><y>0</y></value>
    <range>
      <x><x>-1</x><y>1</y></x>
      <y><x>-1</x><y>1</y></y>
    </range>
  </param>
  
  <!-- Vec3 color -->
  <param type='CONSTANT_FLOAT3'>
    <displayName><![CDATA[Color]]></displayName>
    <variableName><![CDATA[color]]></variableName>
    <value><x>1</x><y>0.5</y><z>0</z></value>
    <range>
      <x><x>0</x><y>1</y></x>
      <y><x>0</x><y>1</y></y>
      <z><x>0</x><y>1</y></z>
    </range>
  </param>
  
  <!-- Vec4 -->
  <param type='CONSTANT_FLOAT4'>
    <displayName><![CDATA[Tint]]></displayName>
    <variableName><![CDATA[tint]]></variableName>
    <value><x>1</x><y>1</y><z>1</z><w>0.5</w></value>
  </param>
</params>
```

## Example 6: 3D Scene with Transforms

Full 3D camera and model setup:

**XML:**

```xml
<pass type='RENDER'>
  <properties>
    <transform>
      <projection>
        <type>0</type> <!-- 0=perspective, 1=orthographic -->
        <perspective>
          <fov>60</fov>
          <z><x>0.1</x><y>100</y></z>
        </perspective>
      </projection>
      
      <view>
        <eye><x>0</x><y>2</y><z>5</z></eye>
        <center><x>0</x><y>0</y><z>0</z></center>
        <up><x>0</x><y>1</y><z>0</z></up>
      </view>
      
      <model>
        <scale><x>1</x><y>1</y><z>1</z></scale>
        <rotate><x>0</x><y>45</y><z>0</z></rotate>
        <translate><x>0</x><y>0</y><z>0</z></translate>
      </model>
    </transform>
  </properties>
  
  <params>
    <param type='TRANSFORM_MVP'>
      <displayName><![CDATA[MVP Matrix]]></displayName>
      <variableName><![CDATA[mvp]]></variableName>
    </param>
  </params>
  
  <stages>
    <stage type='VERTEX'>
      <shader>
        <source profile='GL3'><![CDATA[
in vec4 a_position;
in vec3 a_normal;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
]]></source>
      </shader>
    </stage>
  </stages>
</pass>
```

## Example 7: Render State Configuration

Advanced blend and depth settings:

**XML:**

```xml
<renderstate>
  <!-- Enable color writing -->
  <colormask>
    <r>1</r><g>1</g><b>1</b><a>1</a>
  </colormask>
  
  <!-- Alpha blending -->
  <blendstate>
    <enabled>1</enabled>
    <srcBlendRGB><![CDATA[SRC_ALPHA]]></srcBlendRGB>
    <dstBlendRGB><![CDATA[ONE_MINUS_SRC_ALPHA]]></dstBlendRGB>
    <srcBlendA><![CDATA[ONE]]></srcBlendA>
    <dstBlendA><![CDATA[ONE_MINUS_SRC_ALPHA]]></dstBlendA>
    <equationRGB><![CDATA[ADD]]></equationRGB>
    <equationA><![CDATA[ADD]]></equationA>
  </blendstate>
  
  <!-- Backface culling -->
  <cullstate>
    <enabled>1</enabled>
    <ccw>1</ccw> <!-- Counter-clockwise front faces -->
  </cullstate>
  
  <!-- Depth testing -->
  <depthstate>
    <enabled>1</enabled>
    <write>1</write>
    <func><![CDATA[LESS]]></func>
  </depthstate>
</renderstate>
```

**Common Blend Modes:**

- Additive: `srcBlendRGB=SRC_ALPHA`, `dstBlendRGB=ONE`
- Alpha: `srcBlendRGB=SRC_ALPHA`, `dstBlendRGB=ONE_MINUS_SRC_ALPHA`
- Multiply: `srcBlendRGB=DST_COLOR`, `dstBlendRGB=ZERO`

**Depth Functions:**

- `NEVER`, `LESS`, `EQUAL`, `LEQUAL`, `GREATER`, `NOTEQUAL`, `GEQUAL`, `ALWAYS`

## Example 8: Multi-Profile Shader

Supporting multiple graphics APIs:

**XML:**

```xml
<shader>
  <!-- OpenGL 3.x+ -->
  <source profile='GL3'><![CDATA[#version 150
uniform float time;
out vec4 fragColor;

void main() {
    fragColor = vec4(sin(time));
}
]]></source>

  <!-- OpenGL ES 3.0 -->
  <source profile='ES3'><![CDATA[#version 300 es
precision highp float;
uniform float time;
out vec4 fragColor;

void main() {
    fragColor = vec4(sin(time));
}
]]></source>

  <!-- Metal -->
  <source profile='MTL'><![CDATA[#include <metal_stdlib>
using namespace metal;

struct FS_UNIFORM {
    float time;
};

fragment float4 fs_main(
    constant FS_UNIFORM& u [[buffer(16)]])
{
    return float4(sin(u.time));
}
]]></source>

  <!-- DirectX 9 -->
  <source profile='DX9'><![CDATA[
float time;

float4 ps_main() : COLOR0
{
    return float4(sin(time), 0, 0, 1);
}
]]></source>
</shader>
```

## Example 9: Compute Shader Pass

Using compute shaders (available in newer profiles):

**XML:**

```xml
<pass type='COMPUTE'>
  <properties>
    <label><![CDATA[Compute]]></label>
    <enabled>1</enabled>
    <workGroupSize><x>16</x><y>16</y><z>1</z></workGroupSize>
  </properties>
  
  <params>
    <param type='CONSTANT_IMAGE_2D'>
      <displayName><![CDATA[Output]]></displayName>
      <variableName><![CDATA[outputImage]]></variableName>
      <imageParams>
        <accessMode><![CDATA[WRITE_ONLY]]></accessMode>
        <format><![CDATA[RGBA32F]]></format>
      </imageParams>
    </param>
  </params>
  
  <stages>
    <stage type='COMPUTE'>
      <shader>
        <source profile='GL3'><![CDATA[#version 430
layout(local_size_x = 16, local_size_y = 16) in;
layout(rgba32f, binding = 0) uniform image2D outputImage;

uniform float time;

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    vec2 uv = vec2(pos) / vec2(1280, 720);
    vec4 color = vec4(uv, sin(time), 1.0);
    imageStore(outputImage, pos, color);
}
]]></source>
      </shader>
    </stage>
  </stages>
</pass>
```

## Example 10: File Watch Mode

Enabling external file editing:

**XML:**

```xml
<stage type='FRAGMENT'>
  <properties>
    <enabled>1</enabled>
    <fileWatch>1</fileWatch>
    <fileWatchPath><![CDATA[/path/to/shader.glsl]]></fileWatchPath>
  </properties>
</stage>
```

This allows editing the shader in an external editor with live reload in KodeLife.

## Creating a .klproj File

To create a working `.klproj` file from XML:

**Python:**

```python
import zlib

# Read your XML
with open('project.xml', 'r', encoding='utf-8') as f:
    xml_data = f.read()

# Compress and save
compressed = zlib.compress(xml_data.encode('utf-8'))
with open('project.klproj', 'wb') as f:
    f.write(compressed)
```

## Tips and Best Practices

1. **Always include multiple API profiles** for compatibility across platforms
2. **Use CDATA sections** for all text content to avoid XML escaping issues
3. **Set appropriate sampler states** for textures (LINEAR/NEAREST, CLAMP/REPEAT)
4. **Enable file watch** during development for faster iteration
5. **Use descriptive variable names** for parameters
6. **Set reasonable ranges** for float parameters with UI sliders
7. **Include comments** in shader code for documentation
8. **Test on target platform** as some features vary by API

## See Also

- [Main Format Documentation](KODELIFE_FILE_FORMAT.md)
- [KodeLife Official Documentation](https://hexler.net/kodelife)
