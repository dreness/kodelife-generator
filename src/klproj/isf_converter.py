"""
ISF to KodeLife converter.

This module converts ISF shaders to KodeLife projects by:
1. Parsing ISF JSON metadata (see isf_parser.py)
2. Mapping ISF variables to KodeLife parameters
3. Adapting ISF shader code to standard GLSL
4. Generating proper uniform declarations

ISF Specification References:
- Variables: docs/ISF/isf-docs/pages/ref/ref_variables.md
- Functions: docs/ISF/isf-docs/pages/ref/ref_functions.md
- Converting GLSL: docs/ISF/isf-docs/pages/ref/ref_converting.md
- Multi-pass: docs/ISF/isf-docs/pages/ref/ref_multipass.md
"""

from typing import List, Optional
import os

from .isf_parser import ISFShader, ISFInput, parse_isf_file
from .generator import KodeProjBuilder
from .types import (
    Parameter,
    ParamType,
    ShaderProfile,
    ShaderStageType,
    PassType,
    ShaderSource,
    ShaderStage,
    RenderPass,
    Vec2,
    Vec4,
)
from .helpers import create_mvp_param


# ISF to KodeLife parameter type mapping
# ISF input types: docs/ISF/isf-docs/pages/ref/ref_json.md (TYPE values)
ISF_TO_KODELIFE_PARAM_TYPE = {
    'event': ParamType.CONSTANT_FLOAT1,  # Momentary button
    'bool': ParamType.CONSTANT_FLOAT1,   # Boolean (0.0 or 1.0)
    'long': ParamType.CONSTANT_FLOAT1,   # Integer/enum selector
    'float': ParamType.CONSTANT_FLOAT1,  # Floating point value
    'point2D': ParamType.CONSTANT_FLOAT2,  # 2D coordinate
    'color': ParamType.CONSTANT_FLOAT4,  # RGBA color
    'image': ParamType.CONSTANT_TEXTURE_2D,  # Texture input
    'audio': ParamType.CONSTANT_TEXTURE_2D,  # Audio waveform as texture
    'audioFFT': ParamType.CONSTANT_TEXTURE_2D,  # Audio FFT as texture
}


def convert_isf_input_to_parameter(isf_input: ISFInput) -> Optional[Parameter]:
    """
    Convert an ISF input to a KodeLife parameter.

    Args:
        isf_input: ISF input definition

    Returns:
        Parameter object or None if conversion not supported
    """
    param_type = ISF_TO_KODELIFE_PARAM_TYPE.get(isf_input.input_type)
    if param_type is None:
        return None

    properties = {}

    # Set default value
    if isf_input.default is not None:
        if isf_input.input_type in ('bool', 'event'):
            properties['value'] = 1.0 if isf_input.default else 0.0
        elif isf_input.input_type in ('float', 'long'):
            properties['value'] = float(isf_input.default)
        elif isf_input.input_type == 'point2D':
            if isinstance(isf_input.default, list) and len(isf_input.default) >= 2:
                properties['value'] = Vec2(
                    float(isf_input.default[0]),
                    float(isf_input.default[1])
                )
            else:
                properties['value'] = Vec2(0.0, 0.0)
        elif isf_input.input_type == 'color':
            if isinstance(isf_input.default, list):
                vals = [float(v) for v in isf_input.default]
                # Pad to 4 components if needed
                while len(vals) < 4:
                    vals.append(1.0 if len(vals) == 3 else 0.0)
                properties['value'] = Vec4(*vals[:4])
            else:
                properties['value'] = Vec4(1.0, 1.0, 1.0, 1.0)

    # Set min/max range for numeric types
    if isf_input.input_type in ('float', 'long', 'bool', 'event'):
        if isf_input.min_val is not None:
            properties['min'] = float(isf_input.min_val)
        elif isf_input.input_type in ('bool', 'event'):
            properties['min'] = 0.0  # Boolean range is 0-1
        if isf_input.max_val is not None:
            properties['max'] = float(isf_input.max_val)
        elif isf_input.input_type in ('bool', 'event'):
            properties['max'] = 1.0  # Boolean range is 0-1
        # Set default value for event type if not specified
        if isf_input.input_type == 'event' and 'value' not in properties:
            properties['value'] = 0.0  # Events default to off
    elif isf_input.input_type == 'point2D':
        if isf_input.min_val is not None and isinstance(isf_input.min_val, list):
            properties['min'] = Vec2(
                float(isf_input.min_val[0]) if len(isf_input.min_val) > 0 else 0.0,
                float(isf_input.min_val[1]) if len(isf_input.min_val) > 1 else 0.0
            )
        if isf_input.max_val is not None and isinstance(isf_input.max_val, list):
            properties['max'] = Vec2(
                float(isf_input.max_val[0]) if len(isf_input.max_val) > 0 else 1.0,
                float(isf_input.max_val[1]) if len(isf_input.max_val) > 1 else 1.0
            )
    elif isf_input.input_type == 'color':
        if isf_input.min_val is not None and isinstance(isf_input.min_val, list):
            vals = [float(v) for v in isf_input.min_val]
            while len(vals) < 4:
                vals.append(0.0)
            properties['min'] = Vec4(*vals[:4])
        if isf_input.max_val is not None and isinstance(isf_input.max_val, list):
            vals = [float(v) for v in isf_input.max_val]
            while len(vals) < 4:
                vals.append(1.0)
            properties['max'] = Vec4(*vals[:4])

    # Create parameter
    display_name = isf_input.label if isf_input.label else isf_input.name
    return Parameter(
        param_type=param_type,
        display_name=display_name,
        variable_name=isf_input.name,
        ui_expanded=0,
        properties=properties
    )


def generate_uniform_declarations(parameters: List[Parameter]) -> str:
    """
    Generate GLSL uniform declarations for a list of parameters.

    Args:
        parameters: List of Parameter objects

    Returns:
        String containing uniform declarations
    """
    # Map parameter types to GLSL types
    param_type_to_glsl = {
        ParamType.CLOCK: 'float',
        ParamType.FRAME_DELTA: 'float',
        ParamType.FRAME_NUMBER: 'float',
        ParamType.AUDIO_SAMPLE_RATE: 'float',
        ParamType.FRAME_RESOLUTION: 'vec2',
        ParamType.INPUT_MOUSE_SIMPLE: 'vec4',
        ParamType.DATE: 'vec4',
        ParamType.CONSTANT_FLOAT1: 'float',
        ParamType.CONSTANT_FLOAT2: 'vec2',
        ParamType.CONSTANT_FLOAT3: 'vec3',
        ParamType.CONSTANT_FLOAT4: 'vec4',
        ParamType.CONSTANT_TEXTURE_2D: 'sampler2D',
        ParamType.FRAME_PREV_FRAME: 'sampler2D',
        ParamType.FRAME_PREV_PASS: 'sampler2D',
        ParamType.AUDIO_SPECTRUM_FULL: 'sampler2D',
        ParamType.AUDIO_SPECTRUM_SPLIT: 'sampler2D',
        ParamType.TRANSFORM_MVP: 'mat4',
    }

    declarations = []
    for param in parameters:
        glsl_type = param_type_to_glsl.get(param.param_type)
        if glsl_type:
            declarations.append(f'uniform {glsl_type} {param.variable_name};')

    return '\n'.join(declarations)


def adapt_isf_shader_code(shader_code: str, isf_shader: ISFShader, parameters: List[Parameter], pass_index: Optional[int] = None) -> str:
    """
    Adapt ISF shader code for KodeLife (GL3 profile).

    This performs transformations to make ISF code compatible with KodeLife's GLSL:
    - Adds uniform declarations for all parameters
    - Replaces ISF built-in variables (isf_FragNormCoord, etc.)
    - Replaces ISF macros (IMG_NORM_PIXEL, IMG_PIXEL, IMG_THIS_PIXEL, IMG_SIZE)
    - Handles PASSINDEX for multi-pass shaders
    - Removes deprecated varying keyword for GL3
    - Ensures proper GLSL version and output variable

    ISF References:
    - Variables: docs/ISF/isf-docs/pages/ref/ref_variables.md
    - Functions: docs/ISF/isf-docs/pages/ref/ref_functions.md
    - Converting: docs/ISF/isf-docs/pages/ref/ref_converting.md

    Args:
        shader_code: Original ISF shader code
        isf_shader: Parsed ISF shader metadata
        parameters: List of parameters that need uniform declarations
        pass_index: Optional pass index for multi-pass shaders (0, 1, 2, ...)

    Returns:
        Adapted shader code
    """
    import re

    code = shader_code

    # Remove version-conditional varying declarations for GL3
    # Remove lines like:
    #   #if __VERSION__ <= 120
    #   varying vec2 texOffsets[5];
    #   #else
    #   in vec2 texOffsets[5];
    #   #endif
    # This is a simplification - we just remove these entirely since they're rarely initialized correctly
    code = re.sub(r'#if\s+__VERSION__\s*<=\s*120\s*\n\s*varying\s+[^\n]+\n\s*#else\s*\n\s*in\s+[^\n]+\n\s*#endif', '', code)

    # Remove standalone varying declarations (deprecated in GL3)
    code = re.sub(r'\bvarying\s+', '// varying ', code)  # Comment out varying keyword

    # Replace ISF built-in variables
    # isf_FragNormCoord -> gl_FragCoord.xy / RENDERSIZE
    code = re.sub(r'\bisf_FragNormCoord\b', '(gl_FragCoord.xy / RENDERSIZE)', code)

    # Replace ISF texture sampling macros
    # IMG_THIS_PIXEL(image) -> texture(image, gl_FragCoord.xy / RENDERSIZE)
    # This must come before IMG_NORM_PIXEL to avoid partial matches
    code = re.sub(r'\bIMG_THIS_PIXEL\s*\(\s*(\w+)\s*\)',
                  r'texture(\1, gl_FragCoord.xy / RENDERSIZE)', code)

    # IMG_NORM_THIS_PIXEL(image) -> texture(image, gl_FragCoord.xy / RENDERSIZE)
    # Equivalent to IMG_THIS_PIXEL in practice
    code = re.sub(r'\bIMG_NORM_THIS_PIXEL\s*\(\s*(\w+)\s*\)',
                  r'texture(\1, gl_FragCoord.xy / RENDERSIZE)', code)

    # IMG_NORM_PIXEL(image, coord) -> texture(image, coord)
    code = re.sub(r'\bIMG_NORM_PIXEL\s*\(\s*(\w+)\s*,\s*([^)]+)\)',
                  r'texture(\1, \2)', code)

    # IMG_PIXEL(image, coord) -> texture(image, coord / vec2(textureSize(image, 0)))
    # Note: This regex captures the image name to use it in textureSize
    def replace_img_pixel(match):
        image_name = match.group(1)
        coord = match.group(2)
        return f'texture({image_name}, ({coord}) / vec2(textureSize({image_name}, 0)))'

    code = re.sub(r'\bIMG_PIXEL\s*\(\s*(\w+)\s*,\s*([^)]+)\)',
                  replace_img_pixel, code)

    # IMG_SIZE(image) -> vec2(textureSize(image, 0))
    code = re.sub(r'\bIMG_SIZE\s*\(\s*(\w+)\s*\)',
                  r'vec2(textureSize(\1, 0))', code)

    # Handle boolean comparisons (ISF bools are converted to floats)
    # Remove '== true' comparisons (float != 0.0 is implicitly true)
    code = re.sub(r'\s*==\s*true\b', ' != 0.0', code)
    # Replace '== false' with '== 0.0'
    code = re.sub(r'\s*==\s*false\b', ' == 0.0', code)
    # Replace '!= true' with '== 0.0'
    code = re.sub(r'\s*!=\s*true\b', ' == 0.0', code)
    # Replace '!= false' with '!= 0.0'
    code = re.sub(r'\s*!=\s*false\b', ' != 0.0', code)

    # Add #version directive if not present
    if '#version' not in code:
        code = '#version 150\n' + code

    # Find where to insert uniform declarations and output variable
    lines = code.split('\n')
    version_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('#version'):
            version_idx = i + 1
            break

    # Generate uniform declarations
    uniform_decls = generate_uniform_declarations(parameters)

    # Ensure we have an out variable for fragment color
    has_out_var = any('out vec4' in line for line in lines)

    # Build the header section to insert
    header_lines = []
    if uniform_decls:
        header_lines.append(uniform_decls)

    # Add PASSINDEX constant for multi-pass shaders
    if pass_index is not None:
        header_lines.append(f'const int PASSINDEX = {pass_index};')

    if not has_out_var:
        header_lines.append('out vec4 fragColor;')

    # Insert header after #version
    if header_lines:
        lines.insert(version_idx, '\n'.join(header_lines))
        code = '\n'.join(lines)

    # Replace gl_FragColor with fragColor if present
    code = code.replace('gl_FragColor', 'fragColor')

    return code


def evaluate_pass_dimension(expression, width: int, height: int) -> int:
    """
    Evaluate WIDTH/HEIGHT expression from ISF pass.

    ISF passes can have expressions like:
    - "$WIDTH / 2.0"
    - "floor($HEIGHT/4.0)"
    - "max($WIDTH*0.25,1.0)"
    - 1 (integer literal)

    Args:
        expression: Expression string or integer
        width: Project width
        height: Project height

    Returns:
        Evaluated dimension as integer
    """
    import re
    import math

    if expression is None:
        return None

    # If it's already an integer, return it
    if isinstance(expression, int):
        return expression

    # If it's a float, convert to int
    if isinstance(expression, float):
        return int(expression)

    # Otherwise treat as string expression
    expr = str(expression)

    # Replace $WIDTH and $HEIGHT with actual values
    expr = expr.replace('$WIDTH', str(width))
    expr = expr.replace('$HEIGHT', str(height))

    # Create safe evaluation context with math functions
    safe_dict = {
        'floor': math.floor,
        'ceil': math.ceil,
        'max': max,
        'min': min,
        '__builtins__': {}
    }

    try:
        result = eval(expr, safe_dict)
        return int(result)
    except Exception as e:
        print(f"Warning: Could not evaluate dimension expression '{expression}': {e}")
        return None


def adapt_isf_vertex_shader_code(vertex_code: str, parameters: List[Parameter], api: str = "GL3") -> str:
    """
    Adapt ISF vertex shader code for KodeLife.

    ISF vertex shaders may use ISF-specific functions and variables:
    - isf_vertShaderInit() - ISF framework initialization
    - isf_FragNormCoord - Normalized texture coordinates
    - RENDERSIZE - Render target dimensions

    This function:
    - Adds #version directive
    - Adds uniform declarations
    - Replaces isf_vertShaderInit() with gl_Position calculation
    - Replaces isf_FragNormCoord with computed normalized position
    - Handles varying/out keyword transitions for GL3

    Args:
        vertex_code: Original ISF vertex shader code
        parameters: List of parameters that need uniform declarations
        api: Graphics API (GL3, GL2, etc.)

    Returns:
        Adapted vertex shader code
    """
    import re

    code = vertex_code

    # Handle version-conditional varying/in/out declarations
    # ISF uses #if __VERSION__ <= 120 to switch between varying and in/out
    # For GL3 (version 150+), we want the 'out' declarations
    if api == "GL3":
        # Remove the #if/#else/#endif structure and keep only the 'out' declarations
        def replace_conditional_varying(match):
            # Extract the varying and in/out declarations
            varying_decl = match.group(1).strip()
            out_decl = match.group(2).strip()
            # Return the 'out' declaration for GL3
            return out_decl

        # Match: #if __VERSION__ <= 120\nvarying ...\n#else\nout ...\n#endif
        code = re.sub(
            r'#if\s+__VERSION__\s*<=\s*120\s*\n(.*?)\n\s*#else\s*\n(.*?)\n\s*#endif',
            replace_conditional_varying,
            code,
            flags=re.DOTALL
        )

    # Remove standalone varying keyword (deprecated in GL3)
    code = re.sub(r'\bvarying\s+', 'out ', code)

    # Remove isf_vertShaderInit() calls - we'll handle vertex initialization ourselves
    code = re.sub(r'\bisf_vertShaderInit\s*\(\s*\)\s*;', '', code)

    # Replace isf_FragNormCoord with a computed value
    # In vertex shaders, this represents the normalized vertex position
    # We need to add vertex attributes and compute it
    if 'isf_FragNormCoord' in code:
        # We'll need to add vertex attributes for texture coordinates
        # For now, compute it from the vertex position
        # Assuming the default KodeLife quad goes from -1 to 1, we convert to 0-1
        code = re.sub(
            r'\bisf_FragNormCoord\b',
            '((a_position.xy + 1.0) * 0.5)',
            code
        )

    # Add #version directive if not present
    if '#version' not in code:
        if api == "GL3":
            code = '#version 150\n' + code
        else:
            code = '#version 120\n' + code

    # Find where to insert uniform declarations and attributes
    lines = code.split('\n')
    version_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('#version'):
            version_idx = i + 1
            break

    # Generate uniform declarations
    uniform_decls = generate_uniform_declarations(parameters)

    # Add necessary vertex attributes if not present
    has_position_attr = any('a_position' in line for line in lines)
    has_mvp_uniform = any('mvp' in line and 'uniform' in line for line in lines)

    # Check if we need gl_Position calculation
    has_gl_position = any('gl_Position' in line for line in lines)

    # Build the header section to insert
    header_lines = []

    # Add vertex attribute declaration for GL3
    if not has_position_attr and api == "GL3":
        header_lines.append('in vec4 a_position;')
    elif not has_position_attr and api == "GL2":
        header_lines.append('attribute vec4 a_position;')

    # Add MVP uniform if not present
    if not has_mvp_uniform:
        header_lines.append('uniform mat4 mvp;')

    # Add other uniform declarations
    if uniform_decls:
        header_lines.append(uniform_decls)

    # Insert header after #version
    if header_lines:
        lines.insert(version_idx, '\n'.join(header_lines))

    # If the vertex shader doesn't set gl_Position, add it
    if not has_gl_position:
        # Find the main function and add gl_Position as the first line
        for i, line in enumerate(lines):
            if 'void main()' in line or 'void main (' in line:
                # Find the opening brace
                brace_idx = i
                for j in range(i, len(lines)):
                    if '{' in lines[j]:
                        brace_idx = j
                        break
                # Insert gl_Position calculation after the opening brace
                lines.insert(brace_idx + 1, '    gl_Position = mvp * a_position;')
                break

    code = '\n'.join(lines)

    return code


def create_vertex_shader(api: str = "GL3") -> str:
    """
    Create a minimal vertex shader for ISF conversion.

    Args:
        api: Graphics API (GL3, GL2, etc.)

    Returns:
        Vertex shader source code
    """
    if api == "GL3":
        return """#version 150
in vec4 a_position;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""
    else:  # GL2
        return """#version 120
attribute vec4 a_position;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * a_position;
}
"""


def load_custom_vertex_shader(isf_file_path: str, api: str = "GL3") -> Optional[str]:
    """
    Check for and load a custom vertex shader (.vs file) with the same base name as the ISF file.

    Args:
        isf_file_path: Path to the ISF file
        api: Graphics API (used if adaptation is needed)

    Returns:
        Vertex shader source code if .vs file exists, None otherwise
    """
    # Get the base filename without extension
    base_path = os.path.splitext(isf_file_path)[0]
    vs_path = base_path + '.vs'

    # Check if .vs file exists
    if os.path.exists(vs_path):
        try:
            with open(vs_path, 'r', encoding='utf-8') as f:
                vs_code = f.read()
            print(f"Using custom vertex shader: {os.path.basename(vs_path)}")
            return vs_code
        except Exception as e:
            print(f"Warning: Could not load vertex shader from {vs_path}: {e}")
            return None

    return None


def convert_isf_to_kodelife(
    isf_file_path: str,
    output_path: Optional[str] = None,
    api: str = "GL3",
    width: int = 1920,
    height: int = 1080
) -> str:
    """
    Convert an ISF file to a KodeLife project.

    Supports both single-pass and multipass ISF shaders.
    If a .vs file with the same base name exists, it will be used as the vertex shader.

    Args:
        isf_file_path: Path to the ISF file
        output_path: Optional output path for .klproj file.
                    If None, uses same name as ISF file with .klproj extension
        api: Graphics API to use (default: GL3)
        width: Project width in pixels (default: 1920)
        height: Project height in pixels (default: 1080)

    Returns:
        Path to the created .klproj file

    Raises:
        ValueError: If ISF file is invalid
    """
    # Parse ISF file
    isf_shader = parse_isf_file(isf_file_path)

    # Determine output path
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(isf_file_path))[0]
        output_dir = os.path.dirname(isf_file_path)
        output_path = os.path.join(output_dir, f"{base_name}.klproj")

    # Create builder
    builder = KodeProjBuilder(api=api)
    builder.set_resolution(width, height)

    # Set project metadata
    if isf_shader.description:
        builder.properties.comment = isf_shader.description
    if isf_shader.vsn:
        builder.properties.author = f"ISF v{isf_shader.vsn}"

    # Add standard ISF parameters
    # TIME uniform
    time_param = Parameter(
        param_type=ParamType.CLOCK,
        display_name="Time",
        variable_name="TIME",
        ui_expanded=1,
        properties={'running': 1, 'speed': 1.0, 'direction': 1}
    )
    builder.add_global_param(time_param)

    # RENDERSIZE uniform
    resolution_param = Parameter(
        param_type=ParamType.FRAME_RESOLUTION,
        display_name="Render Size",
        variable_name="RENDERSIZE",
        ui_expanded=1
    )
    builder.add_global_param(resolution_param)

    # DATE uniform
    date_param = Parameter(
        param_type=ParamType.DATE,
        display_name="Date",
        variable_name="DATE",
        ui_expanded=0
    )
    builder.add_global_param(date_param)

    # TIMEDELTA uniform
    delta_param = Parameter(
        param_type=ParamType.FRAME_DELTA,
        display_name="Time Delta",
        variable_name="TIMEDELTA",
        ui_expanded=0
    )
    builder.add_global_param(delta_param)

    # FRAMEINDEX uniform
    frame_param = Parameter(
        param_type=ParamType.FRAME_NUMBER,
        display_name="Frame Index",
        variable_name="FRAMEINDEX",
        ui_expanded=0
    )
    builder.add_global_param(frame_param)

    # Convert ISF inputs to parameters
    isf_params = []
    for isf_input in isf_shader.inputs:
        param = convert_isf_input_to_parameter(isf_input)
        if param:
            builder.add_global_param(param)
            isf_params.append(param)

    # Collect all global parameters for uniform generation
    all_global_params = [time_param, resolution_param, date_param, delta_param, frame_param] + isf_params

    # Create buffer parameters for multipass rendering
    buffer_params = {}  # Maps buffer name -> Parameter

    if isf_shader.passes:
        # Multipass shader
        for pass_idx, isf_pass in enumerate(isf_shader.passes):
            if isf_pass.target:
                # Create a texture parameter for this buffer
                # Use FRAME_PREV_PASS for persistent buffers to get feedback from previous frame
                buffer_param = Parameter(
                    param_type=ParamType.FRAME_PREV_PASS if isf_pass.persistent else ParamType.CONSTANT_TEXTURE_2D,
                    display_name=isf_pass.target,
                    variable_name=isf_pass.target,
                    ui_expanded=0
                )
                buffer_params[isf_pass.target] = buffer_param

                # Add persistent buffers to global parameters so they get uniform declarations
                if isf_pass.persistent:
                    all_global_params.append(buffer_param)

    # Load custom vertex shader if available (will be adapted per pass)
    # Check for custom .vs file first
    custom_vertex_code = load_custom_vertex_shader(isf_file_path, api)
    vertex_profile = ShaderProfile.GL3 if api == "GL3" else ShaderProfile.GL2

    # Create passes
    if isf_shader.passes:
        # Multipass: Create one KodeLife pass for each ISF pass
        for pass_idx, isf_pass in enumerate(isf_shader.passes):
            # Determine pass dimensions
            pass_width = width
            pass_height = height

            if isf_pass.width:
                evaluated = evaluate_pass_dimension(isf_pass.width, width, height)
                if evaluated:
                    pass_width = evaluated
            if isf_pass.height:
                evaluated = evaluate_pass_dimension(isf_pass.height, width, height)
                if evaluated:
                    pass_height = evaluated

            # Collect parameters for this pass
            # All global params already include persistent buffers from all passes
            pass_params = all_global_params.copy()

            # Add non-persistent buffer parameters from previous passes only
            # (persistent buffers are already in all_global_params)
            for prev_pass_idx in range(pass_idx):
                prev_pass = isf_shader.passes[prev_pass_idx]
                if prev_pass.target and prev_pass.target in buffer_params:
                    # Only add if it's not persistent (persistent ones are already in all_global_params)
                    if not prev_pass.persistent:
                        pass_params.append(buffer_params[prev_pass.target])

            # Adapt vertex shader with parameters
            if custom_vertex_code:
                vertex_code = adapt_isf_vertex_shader_code(custom_vertex_code, pass_params, api)
            else:
                vertex_code = create_vertex_shader(api)

            # Create vertex stage
            vertex_stage = ShaderStage(
                stage_type=ShaderStageType.VERTEX,
                enabled=1,
                hidden=1,
                sources=[ShaderSource(vertex_profile, vertex_code)],
                parameters=[create_mvp_param()]
            )

            # Create fragment shader with uniform declarations
            # Pass the pass_index so PASSINDEX is defined correctly for multi-pass shaders
            fragment_code = adapt_isf_shader_code(isf_shader.shader_code, isf_shader, pass_params, pass_index=pass_idx)
            fragment_stage = ShaderStage(
                stage_type=ShaderStageType.FRAGMENT,
                enabled=1,
                hidden=0,
                sources=[ShaderSource(vertex_profile, fragment_code)]
            )

            # Determine pass label
            label = isf_pass.description or isf_pass.name or f"Pass {pass_idx + 1}"
            if isf_pass.target:
                label = f"{label} → {isf_pass.target}"

            # Create render pass
            render_pass = RenderPass(
                pass_type=PassType.RENDER,
                label=label,
                enabled=1,
                primitive_type="TRIANGLES",
                stages=[vertex_stage, fragment_stage],
                width=pass_width,
                height=pass_height
            )

            builder.add_pass(render_pass)

    else:
        # Single-pass shader (no PASSES defined)
        # Adapt vertex shader with parameters
        if custom_vertex_code:
            vertex_code = adapt_isf_vertex_shader_code(custom_vertex_code, all_global_params, api)
        else:
            vertex_code = create_vertex_shader(api)

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(vertex_profile, vertex_code)],
            parameters=[create_mvp_param()]
        )

        # Create fragment shader with uniform declarations
        fragment_code = adapt_isf_shader_code(isf_shader.shader_code, isf_shader, all_global_params)
        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            hidden=0,
            sources=[ShaderSource(vertex_profile, fragment_code)]
        )

        # Determine label based on ISF type
        if isf_shader.is_filter:
            label = "ISF Filter"
        elif isf_shader.is_transition:
            label = "ISF Transition"
        else:
            label = "ISF Generator"

        if isf_shader.description:
            label = isf_shader.description[:30]  # Truncate long descriptions

        # Create render pass
        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label=label,
            enabled=1,
            primitive_type="TRIANGLES",
            stages=[vertex_stage, fragment_stage],
            width=width,
            height=height
        )

        builder.add_pass(render_pass)

    # Save project
    builder.save(output_path)

    return output_path
