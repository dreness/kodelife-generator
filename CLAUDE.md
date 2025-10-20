# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library for programmatically creating KodeLife `.klproj` shader project files, with ISF (Interactive Shader Format) parsing and conversion capabilities. KodeLife is a real-time shader editor supporting multiple graphics APIs (OpenGL, Metal, DirectX).

**IMPORTANT**: This project uses `uv` for all Python commands. Always use `uv run` to execute Python scripts, tests, and CLI commands.

## Development Commands

### Package Management
Uses `uv` for Python package management:
```bash
# Install package in development mode
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_isf.py

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_isf.py::TestISFConverter::test_uniform_declarations_generation
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/
```

### CLI Tools
```bash
# Convert ISF file(s) to .klproj
uv run klproj convert shader.fs                           # Output to same directory
uv run klproj convert shader1.fs shader2.fs -o output/    # Convert multiple files
uv run klproj convert shader.fs -w 1280 --height 720      # Custom dimensions
uv run klproj convert shader.fs -a GL2                    # Use GL2 profile

# Convert from JSON file list (created by tools/find_shaders.py)
uv run klproj convert multipass_isf_shaders.json -o output/

# Mix JSON and direct files
uv run klproj convert shader_list.json shader.fs -o output/

# Extract .klproj to XML
uv run klproj extract input.klproj output.xml

# Verify .klproj file
uv run klproj verify myshader.klproj
```

### Examples
```bash
# Run example scripts
cd examples
uv run python simple_gradient.py
uv run python animated_rainbow.py
uv run python shadertoy_template.py
```

## Architecture

### Core Module Structure

**`src/klproj/`** - Main package with 7 core modules + utils subdirectory:

#### Core Modules

1. **`types.py`** - Data model (270+ lines)
   - Enums: `ShaderProfile`, `ShaderStageType`, `PassType`, `ParamType`
   - Data classes: `Vec2/3/4`, `Parameter`, `ShaderSource`, `ShaderStage`, `RenderPass`, `ProjectProperties`
   - No logic, pure data definitions with comprehensive docstrings

2. **`generator.py`** - Project builder (480+ lines)
   - `KodeProjBuilder` class: Fluent API for constructing .klproj files
   - Converts Python data structures → XML → zlib-compressed binary
   - XML generation with proper element nesting and attribute handling
   - **Critical detail**: All shader code is embedded as text in `<source profile="...">` elements

3. **`helpers.py`** - Convenience functions (150+ lines)
   - `create_shadertoy_params()` - Standard Shadertoy uniforms (iTime, iResolution, iMouse, etc.)
   - `create_mvp_param()` - Model-View-Projection matrix for vertex shaders
   - Parameter factory functions for common use cases

4. **`isf_parser.py`** - ISF format parser (300+ lines)
   - Parses ISF shader files (JSON metadata + GLSL code)
   - Classes: `ISFShader`, `ISFInput`, `ISFPass`, `ISFImported`
   - Identifies shader types: generator, filter, transition
   - Extracts inputs, passes, and shader code

5. **`isf_converter.py`** - ISF to KodeLife converter (420+ lines)
   - **Critical conversion logic**: Transforms ISF → KodeLife format
   - **Uniform generation**: `generate_uniform_declarations()` maps `ParamType` → GLSL types
   - **Shader adaptation**: `adapt_isf_shader_code()` performs:
     - Adds `#version` directive if missing
     - **Inserts uniform declarations** for all parameters (TIME, RENDERSIZE, custom inputs)
     - Replaces ISF built-ins (`isf_FragNormCoord` → `gl_FragCoord.xy / RENDERSIZE`)
     - Replaces ISF macros (`IMG_NORM_PIXEL`, `IMG_PIXEL`, `IMG_THIS_PIXEL`, `IMG_SIZE`)
     - Converts `gl_FragColor` → `fragColor` with `out vec4` declaration
   - **Parameter mapping**: ISF input types → KodeLife `ParamType` (float, color, image, etc.)

6. **`cli.py`** - Command-line interface
   - Entry point: `main()` function
   - Commands: extract, verify, convert
   - Uses `argparse` for CLI argument parsing
   - Convert command: batch ISF to .klproj conversion with custom dimensions and API

7. **`__init__.py`** - Public API
   - Exports all user-facing classes, enums, and functions
   - Single import point: `from klproj import *`

#### Utility Modules (`utils/`)

**`src/klproj/utils/`** - Shared utilities for batch processing and analysis (1350+ lines):

1. **`isf_discovery.py`** - ISF file scanning and cataloging
   - `ISFDiscovery` class: Find and categorize ISF shaders in directories
   - `ISFInfo` dataclass: Structured shader information (path, passes, metadata)
   - Multipass detection and category extraction

2. **`batch_processor.py`** - Batch conversion engine
   - `BatchConverter` class: Convert multiple ISF files with progress tracking
   - `ConversionResult` dataclass: Track success/failure/statistics
   - Handles selection strategies (random, multipass-only, mixed batches)

3. **`analysis.py`** - .klproj file analysis and validation
   - `KlprojAnalyzer` class: Multiple analysis check types
   - `FileAnalysisResult`, `BatchAnalysisResult`, `AnalysisIssue`: Structured results
   - Checks: XML structure, missing uniforms, undefined variables

4. **`reporter.py`** - Progress and results reporting
   - `ConversionReporter` class: Formatted console output with progress bars
   - Verbose/quiet mode support
   - Statistics summaries

### File Format Details

**.klproj files are zlib-compressed XML** with this structure:
```xml
<klxml v="19" a="GL3">
  <document>
    <properties>...</properties>  <!-- Project metadata, resolution, author -->
    <params>...</params>          <!-- Global uniforms (TIME, RENDERSIZE, custom) -->
    <passes>                      <!-- Render/compute passes -->
      <pass type="RENDER">
        <properties>...</properties>  <!-- Pass settings, render state -->
        <params>...</params>          <!-- Pass-specific parameters -->
        <stages>                      <!-- Shader pipeline stages -->
          <stage type="VERTEX">
            <shader>
              <source profile="GL3">/* GLSL code */</source>
              <source profile="MTL">/* Metal code */</source>
            </shader>
          </stage>
          <stage type="FRAGMENT">...</stage>
        </stages>
      </pass>
    </passes>
  </document>
</klxml>
```

**Key insight**: Each shader stage can have multiple `<source>` elements for different graphics APIs (GL2, GL3, MTL, ES3, DX9). KodeLife selects the appropriate one at runtime.

### ISF Conversion Pipeline

1. **Parse ISF** (`isf_parser.py`):
   - Extract JSON metadata from `/* {...} */` comment block
   - Parse INPUTS array → `ISFInput` objects
   - Separate shader code from metadata

2. **Convert parameters** (`isf_converter.py`):
   - Map ISF input types to `ParamType` (e.g., `"float"` → `CONSTANT_FLOAT1`)
   - Create standard ISF parameters: TIME, RENDERSIZE, DATE, TIMEDELTA, FRAMEINDEX
   - Collect all parameters for uniform generation

3. **Adapt shader code** (`isf_converter.py`):
   - **Generate uniform declarations** for all parameters (this was the bug - missing uniforms)
   - Replace ISF-specific syntax with standard GLSL
   - Add `#version` and `out vec4 fragColor` if needed

4. **Build KodeLife project** (`generator.py`):
   - Create vertex shader (required by KodeLife)
   - Create fragment shader with adapted code
   - Package into RenderPass with proper stages
   - Save as compressed XML

### Critical Conversion Detail

**Uniform Declaration Generation** (added to fix rendering issue):
- ISF shaders don't need explicit uniform declarations
- KodeLife uses raw GLSL which requires `uniform` keywords
- `generate_uniform_declarations()` must be called with ALL parameters (global + ISF inputs)
- Uniforms are inserted after `#version` directive but before shader code
- Mapping examples:
  - `CLOCK` → `uniform float TIME;`
  - `FRAME_RESOLUTION` → `uniform vec2 RENDERSIZE;`
  - `CONSTANT_FLOAT4` → `uniform vec4 variableName;`
  - `CONSTANT_TEXTURE_2D` → `uniform sampler2D variableName;`

## Testing Architecture

### Test Organization (`tests/`)

- **`test_isf.py`** - ISF parser and converter tests (25 tests)
  - `TestISFParser` - JSON parsing, shader type detection, input extraction
  - `TestISFConverter` - Conversion pipeline, shader adaptation, uniform generation
  - `TestRealISFFiles` - Integration tests with actual ISF files

### Test Patterns

**Inline test shaders**: Tests define ISF shaders as module-level constants:
```python
SIMPLE_ISF = """/*
{
  "INPUTS": [...],
  "ISFVSN": "2"
}
*/
void main() { ... }
"""
```

**Testing shader adaptation**: All `adapt_isf_shader_code()` tests must pass a `parameters` list (third argument) even if empty.

## ISF Format Notes

ISF (Interactive Shader Format) is a JSON+GLSL format:
- JSON metadata in `/* {...} */` comment
- GLSL shader code follows
- Built-in variables: `TIME`, `RENDERSIZE`, `isf_FragNormCoord`
- Built-in macros: `IMG_NORM_PIXEL()`, `IMG_PIXEL()`, `IMG_THIS_PIXEL()`, `IMG_SIZE()`
- Input types: bool, float, long, point2D, color, image, audio, audioFFT

### ISF Documentation Reference

**IMPORTANT**: When working on ISF-related implementation details, consult the upstream ISF docs in `docs/ISF/isf-docs/`.

**Quick Reference** (`docs/ISF/isf-docs/pages/ref/`):
- `ref_variables.md` - Auto-declared variables: `TIME`, `RENDERSIZE`, `isf_FragNormCoord`, `PASSINDEX`, `DATE`, `FRAMEINDEX`, `TIMEDELTA`
- `ref_functions.md` - ISF functions: `IMG_PIXEL()`, `IMG_NORM_PIXEL()`, `IMG_THIS_PIXEL()`, `IMG_SIZE()` + standard GLSL functions
- `ref_json.md` - JSON specification: `INPUTS`, `PASSES`, `PERSISTENT`, `FLOAT`, `TARGET`, `IMPORTED`, `WIDTH`, `HEIGHT`
- `ref_multipass.md` - Multi-pass rendering and persistent buffers with examples
- `ref_converting.md` - Converting GLSL to ISF: texture2D→IMG_NORM_PIXEL, uniform replacements

**Quickstart** (`docs/ISF/isf-docs/pages/quickstart/quickstart.md`):
- Basic ISF structure, inputs, filters, multi-pass, audio, conversion tips

**Primer** (`docs/ISF/isf-docs/pages/primer/`):
- Chapter 1: Introduction to ISF
- Chapter 2: Anatomy of ISF composition (JSON + GLSL)
- Chapter 3: Using ISF compositions
- Chapter 4: Data types, standard variables, functions
- Chapter 5: Vertex shaders
- Chapter 6: Convolution techniques
- Chapter 7: Persistent buffers and multi-pass shaders
- Chapter 8: Audio visualizers (waveforms, FFT)
- Chapter 9: Adapting existing GLSL code to ISF

## Batch Processing Tools

The `tools/` directory contains consolidated utilities for batch ISF conversion and analysis:

### 1. `batch_convert.py` - Batch ISF Conversion

Converts multiple ISF files with flexible selection strategies:

```bash
# Convert 50 random ISF files
uv run python tools/batch_convert.py --random 50

# Convert only multipass shaders
uv run python tools/batch_convert.py --multipass-only

# Convert mix: 10 multipass + 5 single-pass
uv run python tools/batch_convert.py --mixed 10 5

# Custom output directory and resolution
uv run python tools/batch_convert.py --random 20 -o output/ -w 1280 --height 720 -a GL2
```

Key features:
- Selection strategies: random, multipass-only, single-only, mixed, all
- Progress reporting with statistics
- JSON output (`conversion_results.json`)
- Configurable resolution and graphics API

### 2. `analyze_batch.py` - .klproj Analysis

Analyzes converted .klproj files for issues:

```bash
# Default checks (structure + uniforms)
uv run python tools/analyze_batch.py isf_conversions/

# All checks including undefined variable detection
uv run python tools/analyze_batch.py isf_conversions/ --all-checks

# Specific checks with ISF source context
uv run python tools/analyze_batch.py isf_conversions/ --check-undefined \
    --isf-source ~/Library/Graphics/ISF
```

Available checks:
- `--check-structure` - XML structure and validity
- `--check-uniforms` - Missing uniform declarations
- `--check-undefined` - Undefined variables (deep analysis)
- `--all-checks` - Run all checks

### 3. `find_shaders.py` - ISF Discovery

Scans directories for ISF shaders and extracts metadata:

```bash
# Find all shaders with statistics
uv run python tools/find_shaders.py --stats-only

# Only multipass shaders
uv run python tools/find_shaders.py --multipass-only

# Filter by category
uv run python tools/find_shaders.py --category "Generator"
```

**Typical workflow**: Find shaders → Convert batch → Analyze results
```bash
uv run python tools/find_shaders.py --stats-only
uv run python tools/batch_convert.py --mixed 10 10 -o output/
uv run python tools/analyze_batch.py output/ --all-checks
```

## Common Tasks

### Adding a new parameter type
1. Add to `ParamType` enum in `types.py`
2. Add mapping in `helpers.py` factory functions
3. Add GLSL type mapping in `isf_converter.py:generate_uniform_declarations()`
4. Update ISF converter mapping if applicable

### Debugging shader conversion
1. Convert ISF to .klproj
2. Decompress with `zlib.decompress()`
3. Parse XML to check:
   - Global parameters in `<document><params>`
   - Fragment shader source in `<stage type="FRAGMENT"><shader><source profile="GL3">`
   - Verify uniform declarations are present
   - Check ISF built-ins were replaced

### Testing shader output
Can't run KodeLife in CI, so tests verify:
- File is created and non-empty
- XML can be decompressed and parsed
- Shader code contains expected replacements
- Uniform declarations are present

## Repository Layout

```
src/klproj/           # Main package
  ├── types.py        # Data model (enums, dataclasses)
  ├── generator.py    # KodeProjBuilder and XML generation
  ├── helpers.py      # Parameter factory functions
  ├── isf_parser.py   # ISF format parser
  ├── isf_converter.py # ISF to KodeLife converter
  ├── cli.py          # Command-line interface
  ├── __init__.py     # Public API exports
  └── utils/          # Shared utilities (1350+ lines)
      ├── isf_discovery.py    # ISF file scanning
      ├── batch_processor.py  # Batch conversion
      ├── analysis.py         # .klproj analysis
      └── reporter.py         # Progress reporting
tests/                # pytest tests
  ├── test_isf.py     # ISF parser/converter tests
  ├── test_generator.py
  ├── test_helpers.py
  └── ...
examples/             # Runnable example scripts
tutorials/            # Step-by-step guides (markdown)
tools/                # Batch processing utilities
  ├── batch_convert.py # Batch ISF conversion
  ├── analyze_batch.py # .klproj analysis
  └── find_shaders.py  # ISF discovery
docs/                 # Format specs and API docs
  ├── KODELIFE_FILE_FORMAT.md  # Complete XML schema
  └── ISF/                      # ISF format documentation
extras/               # Legacy tools and analysis
isf_conversions/      # Converted ISF files (output)
```

## Known Issues

1. **ISF multi-pass shaders**: Not fully supported - only single-pass conversion works
2. **ISF PASSES**: Persistent buffers and multi-target rendering not converted
3. **ISF IMPORTED**: External shader imports not handled
4. **Vertex shader inputs**: ISF shaders don't specify vertex attributes, so converter uses fixed vertex shader
