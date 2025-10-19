# KodeLife Project File Format (.klproj)

This document describes the KodeLife project file format (`.klproj`) used by the KodeLife real-time shader editor.

## Overview

KodeLife project files (`.klproj`) are **zlib-compressed XML files** that store complete shader projects including:

- Project metadata and settings
- Global and pass-specific parameters
- Multiple render/compute passes
- Shader source code for multiple graphics API profiles
- Render state configuration
- Camera and transform settings

## File Structure

### Compression Layer

`.klproj` files are compressed using zlib compression. To work with these files:

**Decompression:**

**Python:**

```python
import zlib

with open('project.klproj', 'rb') as f:
    compressed = f.read()
    xml_data = zlib.decompress(compressed)
```

**Compression:**

**Python:**

```python
import zlib

with open('project.xml', 'rb') as f:
    xml_data = f.read()
    compressed = zlib.compress(xml_data)
    
with open('project.klproj', 'wb') as f:
    f.write(compressed)
```

### XML Structure

The decompressed XML follows this hierarchy:

**XML:**

```xml
<?xml version='1.0' encoding='UTF-8'?>
<klxml v='VERSION' a='API'>
  <document>
    <properties>...</properties>
    <params>...</params>
    <passes>...</passes>
  </document>
</klxml>
```

## Root Element: `<klxml>`

The root element with file format metadata.

**Attributes:**

- `v` - Format version number (e.g., "19")
- `a` - Graphics API preference (e.g., "MTL" for Metal, "GL3" for OpenGL 3)

## Document Structure

### `<properties>` - Project Metadata

Global project settings and metadata:

**XML:**

```xml
<properties>
  <creator><![CDATA[net.hexler.KodeLife]]></creator>
  <creatorVersion><![CDATA[1.2.3.202]]></creatorVersion>
  <versionMajor>1</versionMajor>
  <versionMinor>1</versionMinor>
  <versionPatch>1</versionPatch>
  <author><![CDATA[Author Name]]></author>
  <comment><![CDATA[Project description]]></comment>
  <enabled>1</enabled>
  <size>
    <x>1920</x>
    <y>1080</y>
  </size>
  <format><![CDATA[RGBA32F]]></format>
  <clearColor>
    <x>0</x><y>0</y><z>0</z><w>1</w>
  </clearColor>
  <audioSourceType>0</audioSourceType>
  <audioFilePath><![CDATA[]]></audioFilePath>
  <selectedRenderPassIndex>0</selectedRenderPassIndex>
  <selectedKontrolPanelIndex>0</selectedKontrolPanelIndex>
  <uiExpandedPreviewDocument>1</uiExpandedPreviewDocument>
  <uiExpandedPreviewRenderPass>1</uiExpandedPreviewRenderPass>
  <uiExpandedProperties>1</uiExpandedProperties>
  <uiExpandedAudio>1</uiExpandedAudio>
</properties>
```

**Key Properties:**

- `creator`, `creatorVersion` - Application identifier
- `versionMajor/Minor/Patch` - Project version
- `author`, `comment` - User metadata
- `enabled` - Whether project is active (0/1)
- `size` - Default resolution (x/y)
- `format` - Color buffer format (e.g., RGBA32F, RGBA8)
- `clearColor` - Background clear color (RGBA as x/y/z/w)
- `audioSourceType` - Audio input type (0 = line in, 1 = file)
- `audioFilePath` - Path to audio file if using file input

### `<params>` - Global Parameters

Global uniform parameters available to all passes:

**XML:**

```xml
<params>
  <uiExpanded>1</uiExpanded>
  
  <!-- Clock parameter -->
  <param type='CLOCK'>
    <displayName><![CDATA[Clock]]></displayName>
    <variableName><![CDATA[time]]></variableName>
    <uiExpanded>1</uiExpanded>
    <running>1</running>
    <direction>1</direction>
    <speed>1</speed>
    <loop>0</loop>
    <loopStart>0</loopStart>
    <loopEnd>6.28319</loopEnd>
  </param>
  
  <!-- Resolution parameter -->
  <param type='FRAME_RESOLUTION'>
    <displayName><![CDATA[Frame Resolution]]></displayName>
    <variableName><![CDATA[resolution]]></variableName>
    <uiExpanded>1</uiExpanded>
  </param>
  
  <!-- Mouse input -->
  <param type='INPUT_MOUSE_SIMPLE'>
    <displayName><![CDATA[Mouse]]></displayName>
    <variableName><![CDATA[mouse]]></variableName>
    <uiExpanded>1</uiExpanded>
    <variant>0</variant>
    <normalize>1</normalize>
    <invert><x>0</x><y>0</y></invert>
  </param>
  
  <!-- Audio spectrum -->
  <param type='AUDIO_SPECTRUM_SPLIT'>
    <displayName><![CDATA[Audio Spectrum]]></displayName>
    <variableName><![CDATA[spectrum]]></variableName>
    <uiExpanded>1</uiExpanded>
    <split><x>500</x><y>5000</y></split>
    <scale><x>1</x><y>10</y><z>20</z></scale>
  </param>
  
  <!-- Constant float -->
  <param type='CONSTANT_FLOAT1'>
    <displayName><![CDATA[Custom Value]]></displayName>
    <variableName><![CDATA[myFloat]]></variableName>
    <uiExpanded>1</uiExpanded>
    <value>1.5</value>
    <range><x><x>0</x><y>10</y></x></range>
  </param>
  
  <!-- Texture -->
  <param type='CONSTANT_TEXTURE_2D'>
    <displayName><![CDATA[Texture]]></displayName>
    <variableName><![CDATA[tex0]]></variableName>
    <uiExpanded>1</uiExpanded>
    <variant>0</variant>
    <samplerState>
      <minFilter><![CDATA[LINEAR]]></minFilter>
      <magFilter><![CDATA[LINEAR]]></magFilter>
      <wrapS><![CDATA[CLAMP]]></wrapS>
      <wrapT><![CDATA[CLAMP]]></wrapT>
    </samplerState>
    <imageParams>
      <accessMode><![CDATA[READ_ONLY]]></accessMode>
    </imageParams>
  </param>
</params>
```

**Common Parameter Types:**

- `CLOCK` - Time variable
- `FRAME_RESOLUTION` - Resolution vec2
- `FRAME_DELTA` - Delta time between frames
- `FRAME_NUMBER` - Frame counter
- `INPUT_MOUSE_SIMPLE` - Mouse position
- `DATE` - Current date/time
- `AUDIO_SAMPLE_RATE` - Audio sample rate
- `AUDIO_SPECTRUM_FULL` - Full audio spectrum texture
- `AUDIO_SPECTRUM_SPLIT` - Split band audio spectrum
- `CONSTANT_FLOAT1/2/3/4` - Float constants
- `CONSTANT_TEXTURE_2D` - 2D texture sampler
- `FRAME_PREV_FRAME` - Previous frame buffer
- `FRAME_PREV_PASS` - Previous pass output
- `TRANSFORM_MVP` - Model-View-Projection matrix

### `<passes>` - Render/Compute Passes

Container for all render and compute passes:

**XML:**

```xml
<passes>
  <pass type='RENDER'>
    <properties>...</properties>
    <params>...</params>
    <stages>...</stages>
  </pass>
  
  <pass type='COMPUTE'>
    <properties>...</properties>
    <params>...</params>
    <stages>...</stages>
  </pass>
</passes>
```

**Pass Types:**

- `RENDER` - Standard graphics rendering pass
- `COMPUTE` - Compute shader pass

## Render Pass Structure

### `<properties>` - Pass Settings

**XML:**

```xml
<properties>
  <label><![CDATA[Pass A]]></label>
  <enabled>1</enabled>
  <selectedShaderStageIndex>4</selectedShaderStageIndex>
  <primitiveIndex>0</primitiveIndex>
  <primitiveType><![CDATA[TRIANGLES]]></primitiveType>
  <instanceCount>1</instanceCount>
  <uiExpanded>1</uiExpanded>
  
  <renderstate>
    <colormask>
      <r>1</r><g>1</g><b>1</b><a>1</a>
      <uiExpanded>0</uiExpanded>
    </colormask>
    
    <blendstate>
      <enabled>0</enabled>
      <srcBlendRGB><![CDATA[SRC_ALPHA]]></srcBlendRGB>
      <dstBlendRGB><![CDATA[ONE_MINUS_SRC_ALPHA]]></dstBlendRGB>
      <srcBlendA><![CDATA[ONE]]></srcBlendA>
      <dstBlendA><![CDATA[ONE_MINUS_SRC_ALPHA]]></dstBlendA>
      <equationRGB><![CDATA[ADD]]></equationRGB>
      <equationA><![CDATA[ADD]]></equationA>
      <uiExpanded>0</uiExpanded>
    </blendstate>
    
    <cullstate>
      <enabled>1</enabled>
      <ccw>1</ccw>
      <uiExpanded>0</uiExpanded>
    </cullstate>
    
    <depthstate>
      <enabled>1</enabled>
      <write>1</write>
      <func><![CDATA[LESS]]></func>
      <uiExpanded>0</uiExpanded>
    </depthstate>
  </renderstate>
  
  <rendertarget>
    <size><x>1920</x><y>1080</y></size>
    <resolutionMode><![CDATA[PROJECT]]></resolutionMode>
    <uiExpanded>1</uiExpanded>
    
    <color>
      <format><![CDATA[RGBA32F]]></format>
      <clear><x>0</x><y>0</y><z>0</z><w>1</w></clear>
      <uiExpanded>0</uiExpanded>
    </color>
    
    <depth>
      <clear>1</clear>
      <uiExpanded>0</uiExpanded>
    </depth>
  </rendertarget>
  
  <transform>
    <uiExpanded>1</uiExpanded>
    
    <projection>
      <type>0</type>
      <perspective>
        <fov>60</fov>
        <z><x>0.1</x><y>1000</y></z>
      </perspective>
      <orthographic>
        <bounds><x>-1</x><y>1</y><z>-1</z><w>1</w></bounds>
        <z><x>-10</x><y>10</y></z>
      </orthographic>
      <uiExpanded>0</uiExpanded>
    </projection>
    
    <view>
      <eye><x>0</x><y>0</y><z>4</z></eye>
      <center><x>0</x><y>0</y><z>0</z></center>
      <up><x>0</x><y>1</y><z>0</z></up>
      <uiExpanded>0</uiExpanded>
    </view>
    
    <model>
      <scale><x>1</x><y>1</y><z>1</z></scale>
      <rotate><x>0</x><y>0</y><z>0</z></rotate>
      <translate><x>0</x><y>0</y><z>0</z></translate>
      <uiExpanded>0</uiExpanded>
    </model>
  </transform>
</properties>
```

**Key Settings:**

- `primitiveType` - Geometry primitive (TRIANGLES, POINTS, LINES, etc.)
- `renderstate` - OpenGL render state (blending, depth, culling)
- `rendertarget` - Output buffer configuration
- `transform` - Camera and model transforms

### `<stages>` - Shader Pipeline Stages

Each pass contains multiple shader stages:

**XML:**

```xml
<stages>
  <stage type='VERTEX'>...</stage>
  <stage type='TESS_CONTROL'>...</stage>
  <stage type='TESS_EVAL'>...</stage>
  <stage type='GEOMETRY'>...</stage>
  <stage type='FRAGMENT'>...</stage>
  <stage type='COMPUTE'>...</stage>
</stages>
```

**Stage Types:**

- `VERTEX` - Vertex shader
- `TESS_CONTROL` - Tessellation control shader
- `TESS_EVAL` - Tessellation evaluation shader
- `GEOMETRY` - Geometry shader
- `FRAGMENT` - Fragment/pixel shader
- `COMPUTE` - Compute shader

### Shader Stage Structure

**XML:**

```xml
<stage type='FRAGMENT'>
  <properties>
    <enabled>1</enabled>
    <hidden>0</hidden>
    <locked>0</locked>
    <fileWatch>0</fileWatch>
    <fileWatchPath><![CDATA[]]></fileWatchPath>
    <uiExpanded>1</uiExpanded>
  </properties>
  
  <params>
    <uiExpanded>1</uiExpanded>
    <!-- Stage-specific parameters -->
  </params>
  
  <shader>
    <!-- Multi-profile shader sources -->
    <source profile='DX9'><![CDATA[
      // DirectX 9 HLSL code
    ]]></source>
    
    <source profile='ES3'><![CDATA[
      // OpenGL ES 3.0 GLSL code
    ]]></source>
    
    <source profile='ES3-300'><![CDATA[
      // OpenGL ES 3.0 (version 300) code
    ]]></source>
    
    <source profile='ES3-310'><![CDATA[
      // OpenGL ES 3.1 code
    ]]></source>
    
    <source profile='ES3-320'><![CDATA[
      // OpenGL ES 3.2 code
    ]]></source>
    
    <source profile='GL2'><![CDATA[
      // OpenGL 2.1 GLSL code
    ]]></source>
    
    <source profile='GL3'><![CDATA[
      // OpenGL 3.x/4.x GLSL code
    ]]></source>
    
    <source profile='MTL'><![CDATA[
      // Metal Shading Language code
    ]]></source>
  </shader>
</stage>
```

**Graphics API Profiles:**

- `DX9` - DirectX 9 HLSL
- `ES3` - OpenGL ES 3.0
- `ES3-300` - OpenGL ES 3.0 (version 300 es)
- `ES3-310` - OpenGL ES 3.1
- `ES3-320` - OpenGL ES 3.2
- `GL2` - OpenGL 2.1 GLSL
- `GL3` - OpenGL 3.x/4.x core profile
- `MTL` - Metal Shading Language

## Common Patterns

### Shadertoy Compatibility

KodeLife supports Shadertoy-style shaders with these conventions:

**Global Parameters:**

**XML:**

```xml
<param type='FRAME_RESOLUTION'>
  <variableName><![CDATA[iResolution]]></variableName>
</param>
<param type='CLOCK'>
  <variableName><![CDATA[iTime]]></variableName>
</param>
<param type='FRAME_DELTA'>
  <variableName><![CDATA[iTimeDelta]]></variableName>
</param>
<param type='FRAME_NUMBER'>
  <variableName><![CDATA[iFrame]]></variableName>
</param>
<param type='INPUT_MOUSE_SIMPLE'>
  <variableName><![CDATA[iMouse]]></variableName>
</param>
<param type='DATE'>
  <variableName><![CDATA[iDate]]></variableName>
</param>
```

**Fragment Shader Structure:**

**GLSL:**

```glsl
uniform vec2 iResolution;
uniform float iTime;
uniform sampler2D iChannel0;

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    vec2 uv = fragCoord.xy / iResolution.xy;
    fragColor = vec4(uv, 0.5 + 0.5*sin(iTime), 1.0);
}

void main() { mainImage(fragColor, gl_FragCoord.xy); }
```

### Feedback Loops

Using previous frame/pass as input:

**XML:**

```xml
<param type='FRAME_PREV_FRAME'>
  <displayName><![CDATA[Previous Frame]]></displayName>
  <variableName><![CDATA[prevFrame]]></variableName>
  <variant>0</variant>
  <samplerState>
    <minFilter><![CDATA[LINEAR]]></minFilter>
    <magFilter><![CDATA[LINEAR]]></magFilter>
    <wrapS><![CDATA[CLAMP]]></wrapS>
    <wrapT><![CDATA[CLAMP]]></wrapT>
  </samplerState>
</param>
```

### Audio Input

Audio spectrum as texture:

**XML:**

```xml
<param type='AUDIO_SPECTRUM_FULL'>
  <displayName><![CDATA[Audio Spectrum]]></displayName>
  <variableName><![CDATA[spectrum]]></variableName>
  <variant>0</variant>
  <samplerState>
    <minFilter><![CDATA[LINEAR]]></minFilter>
    <magFilter><![CDATA[LINEAR]]></magFilter>
    <wrapS><![CDATA[CLAMP]]></wrapS>
    <wrapT><![CDATA[CLAMP]]></wrapT>
  </samplerState>
</param>
```

## File Format Version History

- **v19** - Current version (KodeLife 1.2.3.202)
  - Multi-profile shader support
  - Compute shader support
  - Enhanced parameter types

## Tools

### Python Utilities

See [`tools/extract_klproj.py`](../tools/extract_klproj.py) for extraction utilities.

**Example Usage:**

**Bash:**

```bash
# Extract all .klproj files to XML
python3 tools/extract_klproj.py
```

## References

- [KodeLife Official Website](https://hexler.net/kodelife)
- [Shadertoy](https://www.shadertoy.com/) - Compatible shader platform
- [OpenGL Shading Language Specification](https://www.khronos.org/opengl/wiki/OpenGL_Shading_Language)
- [Metal Shading Language Specification](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf)
