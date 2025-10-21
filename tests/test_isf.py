"""
Tests for ISF parser and converter functionality.
"""

import os

import pytest

from klproj.isf_converter import (
    adapt_isf_shader_code,
    convert_isf_input_to_parameter,
    convert_isf_to_kodelife,
)
from klproj.isf_parser import ISFShader, parse_isf_file, parse_isf_string

# Sample ISF shaders for testing
SIMPLE_ISF = """/*
{
  "DESCRIPTION": "Simple test shader",
  "CATEGORIES": ["Test"],
  "INPUTS": [
    {
      "NAME": "color",
      "TYPE": "color",
      "DEFAULT": [1.0, 0.5, 0.0, 1.0]
    }
  ],
  "ISFVSN": "2"
}
*/

#version 150
out vec4 fragColor;
uniform vec4 color;
uniform vec2 RENDERSIZE;

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE;
    fragColor = color * vec4(uv, 0.5, 1.0);
}
"""

GENERATOR_ISF = """/*
{
  "DESCRIPTION": "Generator test",
  "CATEGORIES": ["Generator"],
  "INPUTS": [
    {
      "NAME": "speed",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 10.0
    }
  ],
  "ISFVSN": "2"
}
*/

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE;
    float t = TIME * speed;
    gl_FragColor = vec4(0.5 + 0.5 * cos(t + uv.xyx + vec3(0,2,4)), 1.0);
}
"""

FILTER_ISF = """/*
{
  "DESCRIPTION": "Image filter test",
  "CATEGORIES": ["Filter"],
  "INPUTS": [
    {
      "NAME": "inputImage",
      "TYPE": "image"
    },
    {
      "NAME": "brightness",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 2.0
    }
  ],
  "ISFVSN": "2"
}
*/

void main() {
    vec4 pixel = IMG_NORM_PIXEL(inputImage, gl_FragCoord.xy / RENDERSIZE);
    gl_FragColor = pixel * brightness;
}
"""

TRANSITION_ISF = """/*
{
  "DESCRIPTION": "Transition test",
  "CATEGORIES": ["Transition"],
  "INPUTS": [
    {
      "NAME": "startImage",
      "TYPE": "image"
    },
    {
      "NAME": "endImage",
      "TYPE": "image"
    },
    {
      "NAME": "progress",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ],
  "ISFVSN": "2"
}
*/

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE;
    vec4 start = IMG_NORM_PIXEL(startImage, uv);
    vec4 end = IMG_NORM_PIXEL(endImage, uv);
    gl_FragColor = mix(start, end, progress);
}
"""

PERSISTENT_BUFFER_ISF = """/*
{
  "DESCRIPTION": "Persistent buffer test",
  "CATEGORIES": ["Feedback"],
  "INPUTS": [
    {
      "NAME": "decay",
      "TYPE": "float",
      "DEFAULT": 0.95,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ],
  "PASSES": [
    {
      "TARGET": "feedbackBuffer",
      "PERSISTENT": true,
      "FLOAT": true
    }
  ],
  "ISFVSN": "2"
}
*/

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE;
    vec4 feedback = IMG_NORM_PIXEL(feedbackBuffer, uv);
    vec4 newColor = vec4(uv, 0.5 + 0.5 * sin(TIME), 1.0);
    gl_FragColor = mix(newColor, feedback, decay);
}
"""


class TestISFParser:
    """Test ISF parsing functionality."""

    def test_parse_simple_isf(self):
        """Test parsing a simple ISF shader."""
        shader = parse_isf_string(SIMPLE_ISF)
        assert shader.description == "Simple test shader"
        assert "Test" in shader.categories
        assert len(shader.inputs) == 1
        assert shader.inputs[0].name == "color"
        assert shader.inputs[0].input_type == "color"
        assert shader.isfvsn == "2"
        assert "fragColor" in shader.shader_code

    def test_parse_generator(self):
        """Test identifying a generator shader."""
        shader = parse_isf_string(GENERATOR_ISF)
        assert shader.is_generator
        assert not shader.is_filter
        assert not shader.is_transition
        assert len(shader.inputs) == 1
        assert shader.inputs[0].name == "speed"

    def test_parse_filter(self):
        """Test identifying a filter shader."""
        shader = parse_isf_string(FILTER_ISF)
        assert shader.is_filter
        assert not shader.is_generator
        assert not shader.is_transition
        assert any(inp.name == "inputImage" for inp in shader.inputs)

    def test_parse_transition(self):
        """Test identifying a transition shader."""
        shader = parse_isf_string(TRANSITION_ISF)
        assert shader.is_transition
        assert not shader.is_generator
        assert not shader.is_filter
        input_names = {inp.name for inp in shader.inputs}
        assert "startImage" in input_names
        assert "endImage" in input_names
        assert "progress" in input_names

    def test_parse_with_passes(self):
        """Test parsing ISF with render passes."""
        shader = parse_isf_string(PERSISTENT_BUFFER_ISF)
        assert len(shader.passes) == 1
        assert shader.passes[0].target == "feedbackBuffer"
        assert shader.passes[0].persistent
        assert shader.passes[0].float_precision

    def test_parse_input_types(self):
        """Test parsing different input types."""
        isf = """/*
{
  "INPUTS": [
    {"NAME": "boolVal", "TYPE": "bool", "DEFAULT": true},
    {"NAME": "longVal", "TYPE": "long", "DEFAULT": 1, "VALUES": [0, 1, 2], "LABELS": ["A", "B", "C"]},
    {"NAME": "floatVal", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "point", "TYPE": "point2D", "DEFAULT": [0.5, 0.5]},
    {"NAME": "img", "TYPE": "image"}
  ],
  "ISFVSN": "2"
}
*/
void main() { gl_FragColor = vec4(1.0); }
"""
        shader = parse_isf_string(isf)
        assert len(shader.inputs) == 5
        assert shader.inputs[0].input_type == "bool"
        assert shader.inputs[1].input_type == "long"
        assert shader.inputs[1].values == [0, 1, 2]
        assert shader.inputs[1].labels == ["A", "B", "C"]
        assert shader.inputs[2].min_val == 0.0
        assert shader.inputs[2].max_val == 1.0
        assert shader.inputs[4].input_type == "image"

    def test_invalid_json(self):
        """Test error handling for invalid JSON."""
        invalid_isf = """/*
{
  "INPUTS": [
    {"NAME": "test"  // Missing closing brace
  ]
}
*/
void main() {}
"""
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_isf_string(invalid_isf)

    def test_missing_json(self):
        """Test error handling for missing JSON block."""
        invalid_isf = """
void main() {
    gl_FragColor = vec4(1.0);
}
"""
        with pytest.raises(ValueError, match="No JSON metadata found"):
            parse_isf_string(invalid_isf)


class TestISFConverter:
    """Test ISF to KodeLife conversion."""

    def test_convert_simple_isf(self, tmp_path):
        """Test converting a simple ISF to KodeLife."""
        # Create temporary ISF file
        isf_file = tmp_path / "test.fs"
        isf_file.write_text(SIMPLE_ISF)

        # Convert
        output_file = tmp_path / "test.klproj"
        result = convert_isf_to_kodelife(str(isf_file), str(output_file))

        assert result == str(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_convert_generator(self, tmp_path):
        """Test converting a generator shader."""
        isf_file = tmp_path / "generator.fs"
        isf_file.write_text(GENERATOR_ISF)

        output_file = tmp_path / "generator.klproj"
        convert_isf_to_kodelife(str(isf_file), str(output_file))

        assert output_file.exists()

    def test_convert_filter(self, tmp_path):
        """Test converting a filter shader."""
        isf_file = tmp_path / "filter.fs"
        isf_file.write_text(FILTER_ISF)

        output_file = tmp_path / "filter.klproj"
        convert_isf_to_kodelife(str(isf_file), str(output_file))

        assert output_file.exists()

    def test_auto_output_path(self, tmp_path):
        """Test automatic output path generation."""
        isf_file = tmp_path / "myshader.fs"
        isf_file.write_text(SIMPLE_ISF)

        result = convert_isf_to_kodelife(str(isf_file))

        expected = tmp_path / "myshader.klproj"
        assert result == str(expected)
        assert expected.exists()

    def test_adapt_shader_code(self):
        """Test shader code adaptation."""

        shader = ISFShader()
        # Empty parameters list for simple test
        params = []

        # Test adding version directive
        code1 = "void main() { gl_FragColor = vec4(1.0); }"
        adapted1 = adapt_isf_shader_code(code1, shader, params)
        assert "#version 150" in adapted1
        assert "fragColor" in adapted1

        # Test with existing version
        code2 = "#version 150\nvoid main() { gl_FragColor = vec4(1.0); }"
        adapted2 = adapt_isf_shader_code(code2, shader, params)
        assert adapted2.count("#version 150") == 1
        assert "fragColor" in adapted2

    def test_uniform_declarations_generation(self):
        """Test that uniform declarations are generated for parameters."""
        from klproj.types import Parameter, ParamType

        shader = ISFShader()

        # Create test parameters
        params = [
            Parameter(ParamType.CLOCK, "Time", "TIME", properties={}),
            Parameter(ParamType.FRAME_RESOLUTION, "Resolution", "RENDERSIZE", properties={}),
            Parameter(ParamType.CONSTANT_FLOAT1, "Speed", "speed", properties={"value": 1.0}),
            Parameter(ParamType.CONSTANT_FLOAT4, "Color", "color", properties={}),
            Parameter(ParamType.CONSTANT_TEXTURE_2D, "Input", "inputImage", properties={}),
        ]

        code = "void main() { gl_FragColor = vec4(1.0); }"
        adapted = adapt_isf_shader_code(code, shader, params)

        # Check uniform declarations are present
        assert "uniform float TIME;" in adapted
        assert "uniform vec2 RENDERSIZE;" in adapted
        assert "uniform float speed;" in adapted
        assert "uniform vec4 color;" in adapted
        assert "uniform sampler2D inputImage;" in adapted
        assert "out vec4 fragColor;" in adapted

    def test_isf_built_in_replacements(self):
        """Test replacement of ISF-specific built-ins and macros."""

        shader = ISFShader()
        params = []  # Empty for this test

        # Test isf_FragNormCoord replacement
        code_with_frag_coord = """
void main() {
    vec2 uv = isf_FragNormCoord;
    gl_FragColor = vec4(uv, 0.0, 1.0);
}
"""
        adapted = adapt_isf_shader_code(code_with_frag_coord, shader, params)
        assert "isf_FragNormCoord" not in adapted
        assert "(gl_FragCoord.xy / RENDERSIZE)" in adapted

    def test_img_norm_pixel_replacement(self):
        """Test IMG_NORM_PIXEL macro replacement."""

        shader = ISFShader()
        params = []  # Empty for this test

        code_with_img_norm = """
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE;
    vec4 color = IMG_NORM_PIXEL(inputImage, uv);
    gl_FragColor = color;
}
"""
        adapted = adapt_isf_shader_code(code_with_img_norm, shader, params)
        assert "IMG_NORM_PIXEL" not in adapted
        assert "texture(inputImage, uv)" in adapted

    def test_img_pixel_replacement(self):
        """Test IMG_PIXEL macro replacement."""

        shader = ISFShader()
        params = []  # Empty for this test

        code_with_img_pixel = """
void main() {
    vec2 pixelCoord = vec2(100.0, 200.0);
    vec4 color = IMG_PIXEL(myTexture, pixelCoord);
    gl_FragColor = color;
}
"""
        adapted = adapt_isf_shader_code(code_with_img_pixel, shader, params)
        assert "IMG_PIXEL" not in adapted
        assert "texture(myTexture, (pixelCoord) / vec2(textureSize(myTexture, 0)))" in adapted

    def test_img_size_replacement(self):
        """Test IMG_SIZE macro replacement."""

        shader = ISFShader()
        params = []  # Empty for this test

        code_with_img_size = """
void main() {
    vec2 texSize = IMG_SIZE(inputImage);
    vec2 uv = gl_FragCoord.xy / texSize;
    gl_FragColor = vec4(uv, 0.0, 1.0);
}
"""
        adapted = adapt_isf_shader_code(code_with_img_size, shader, params)
        assert "IMG_SIZE" not in adapted
        assert "vec2(textureSize(inputImage, 0))" in adapted

    def test_img_this_pixel_replacement(self):
        """Test IMG_THIS_PIXEL macro replacement."""

        shader = ISFShader()
        params = []  # Empty for this test

        code_with_this_pixel = """
void main() {
    vec4 color = IMG_THIS_PIXEL(inputImage);
    gl_FragColor = color * 0.5;
}
"""
        adapted = adapt_isf_shader_code(code_with_this_pixel, shader, params)
        assert "IMG_THIS_PIXEL" not in adapted
        assert "texture(inputImage, gl_FragCoord.xy / RENDERSIZE)" in adapted

    def test_multiple_isf_replacements(self):
        """Test shader with multiple ISF built-ins."""

        shader = ISFShader()
        params = []  # Empty for this test

        code_with_multiple = """
void main() {
    vec2 uv = isf_FragNormCoord;
    vec2 texSize = IMG_SIZE(inputImage);
    vec4 color1 = IMG_NORM_PIXEL(inputImage, uv);
    vec4 color2 = IMG_PIXEL(inputImage, uv * texSize);
    gl_FragColor = mix(color1, color2, 0.5);
}
"""
        adapted = adapt_isf_shader_code(code_with_multiple, shader, params)

        # Verify all ISF-specific elements are replaced
        assert "isf_FragNormCoord" not in adapted
        assert "IMG_NORM_PIXEL" not in adapted
        assert "IMG_PIXEL" not in adapted
        assert "IMG_SIZE" not in adapted

        # Verify replacements are present
        assert "(gl_FragCoord.xy / RENDERSIZE)" in adapted
        assert "texture(inputImage," in adapted
        assert "textureSize(inputImage, 0)" in adapted
        assert "fragColor" in adapted

    def test_boolean_comparison_replacements(self):
        """Test replacement of boolean comparisons (ISF bools are converted to floats)."""
        from klproj.types import Parameter, ParamType

        shader = ISFShader()
        params = [
            Parameter(
                ParamType.CONSTANT_FLOAT1,
                "Enable Effect",
                "enableEffect",
                properties={"value": 1.0},
            ),
            Parameter(
                ParamType.CONSTANT_FLOAT1,
                "Show Background",
                "showBg",
                properties={"value": 0.0},
            ),
        ]

        code_with_bool_comparisons = """
void main() {
    vec4 color = vec4(0.0);

    // Test == true
    if (enableEffect == true) {
        color.r = 1.0;
    }

    // Test == false
    if (showBg == false) {
        color.g = 1.0;
    }

    // Test != true
    if (enableEffect != true) {
        color.b = 0.5;
    }

    // Test != false
    if (showBg != false) {
        color.a = 0.5;
    }

    gl_FragColor = color;
}
"""
        adapted = adapt_isf_shader_code(code_with_bool_comparisons, shader, params)

        # Boolean literals should be replaced with float comparisons
        assert "== true" not in adapted
        assert "== false" not in adapted
        assert "!= true" not in adapted
        assert "!= false" not in adapted

        # Should contain proper float comparisons
        assert "!= 0.0" in adapted  # From == true and != false
        assert "== 0.0" in adapted  # From == false and != true

    def test_convert_input_parameters(self):
        """Test converting ISF inputs to KodeLife parameters."""
        from klproj.isf_parser import ISFInput
        from klproj.types import ParamType

        # Float input
        float_input = ISFInput(
            name="speed", input_type="float", default=1.0, min_val=0.0, max_val=10.0
        )
        param = convert_isf_input_to_parameter(float_input)
        assert param is not None
        assert param.param_type == ParamType.CONSTANT_FLOAT1
        assert param.variable_name == "speed"
        assert param.properties["value"] == 1.0
        assert param.properties["min"] == 0.0
        assert param.properties["max"] == 10.0

        # Color input
        color_input = ISFInput(name="tint", input_type="color", default=[1.0, 0.5, 0.0, 1.0])
        param = convert_isf_input_to_parameter(color_input)
        assert param is not None
        assert param.param_type == ParamType.CONSTANT_FLOAT4
        assert param.properties["value"].x == 1.0
        assert param.properties["value"].y == 0.5

        # Point2D input
        point_input = ISFInput(name="pos", input_type="point2D", default=[0.5, 0.5])
        param = convert_isf_input_to_parameter(point_input)
        assert param is not None
        assert param.param_type == ParamType.CONSTANT_FLOAT2
        assert param.properties["value"].x == 0.5
        assert param.properties["value"].y == 0.5

    def test_custom_resolution(self, tmp_path):
        """Test converting with custom resolution."""
        isf_file = tmp_path / "test.fs"
        isf_file.write_text(SIMPLE_ISF)

        output_file = tmp_path / "test.klproj"
        convert_isf_to_kodelife(str(isf_file), str(output_file), width=1280, height=720)

        assert output_file.exists()

    def test_img_norm_this_pixel_replacement(self):
        """Test IMG_NORM_THIS_PIXEL macro replacement."""

        shader = ISFShader()
        params = []  # Empty for this test

        code_with_norm_this_pixel = """
void main() {
    vec4 color = IMG_NORM_THIS_PIXEL(inputImage);
    gl_FragColor = color * 0.75;
}
"""
        adapted = adapt_isf_shader_code(code_with_norm_this_pixel, shader, params)
        assert "IMG_NORM_THIS_PIXEL" not in adapted
        assert "texture(inputImage, gl_FragCoord.xy / RENDERSIZE)" in adapted

    def test_multipass_width_height_expressions(self):
        """Test multi-pass shader with WIDTH/HEIGHT dimension expressions."""
        from klproj.isf_converter import evaluate_pass_dimension

        # Test simple division
        result = evaluate_pass_dimension("$WIDTH / 2.0", 1920, 1080)
        assert result == 960

        # Test floor function
        result = evaluate_pass_dimension("floor($HEIGHT * 0.5)", 1920, 1080)
        assert result == 540

        # Test max function
        result = evaluate_pass_dimension("max($WIDTH*0.25, 1.0)", 1920, 1080)
        assert result == 480

        # Test integer literal
        result = evaluate_pass_dimension(256, 1920, 1080)
        assert result == 256

        # Test ceil function
        result = evaluate_pass_dimension("ceil($WIDTH / 16.0)", 1920, 1080)
        assert result == 120

    def test_persistent_vs_nonpersistent_buffers(self, tmp_path):
        """Test that persistent and non-persistent buffers are handled correctly."""

        # Multi-pass shader with both persistent and non-persistent buffers
        multipass_isf = """/*
{
  "DESCRIPTION": "Multi-pass with mixed buffer types",
  "ISFVSN": "2",
  "PASSES": [
    {
      "TARGET": "tempBuffer",
      "PERSISTENT": false,
      "WIDTH": "$WIDTH/2.0",
      "HEIGHT": "$HEIGHT/2.0"
    },
    {
      "TARGET": "persistentBuffer",
      "PERSISTENT": true,
      "FLOAT": true
    },
    {
    }
  ]
}
*/

void main() {
    if (PASSINDEX == 0) {
        // First pass - render to tempBuffer
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
    else if (PASSINDEX == 1) {
        // Second pass - can access tempBuffer, render to persistentBuffer
        vec4 temp = IMG_THIS_PIXEL(tempBuffer);
        vec4 persistent = IMG_THIS_PIXEL(persistentBuffer);
        gl_FragColor = mix(temp, persistent, 0.5);
    }
    else {
        // Final pass - can access both buffers
        vec4 temp = IMG_THIS_PIXEL(tempBuffer);
        vec4 persistent = IMG_THIS_PIXEL(persistentBuffer);
        gl_FragColor = temp + persistent;
    }
}
"""

        isf_file = tmp_path / "multipass.fs"
        isf_file.write_text(multipass_isf)

        output_file = tmp_path / "multipass.klproj"
        result = convert_isf_to_kodelife(str(isf_file), str(output_file))

        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

        # Parse to verify buffer configuration
        from klproj.isf_parser import parse_isf_file

        shader = parse_isf_file(str(isf_file))
        assert len(shader.passes) == 3
        assert not shader.passes[0].persistent  # tempBuffer is not persistent
        assert shader.passes[1].persistent  # persistentBuffer is persistent

    def test_audio_input_types(self):
        """Test audio and audioFFT input type conversion."""
        from klproj.isf_parser import ISFInput
        from klproj.types import ParamType

        # Audio waveform input
        audio_input = ISFInput(
            name="audioInput",
            input_type="audio",
            max_val=256,  # Number of samples
        )
        param = convert_isf_input_to_parameter(audio_input)
        assert param is not None
        assert param.param_type == ParamType.CONSTANT_TEXTURE_2D
        assert param.variable_name == "audioInput"

        # Audio FFT input
        fft_input = ISFInput(
            name="audioFFT",
            input_type="audioFFT",
            max_val=128,  # Number of FFT bins
        )
        param = convert_isf_input_to_parameter(fft_input)
        assert param is not None
        assert param.param_type == ParamType.CONSTANT_TEXTURE_2D
        assert param.variable_name == "audioFFT"

    def test_event_input_type(self):
        """Test event input type conversion (momentary button)."""
        from klproj.isf_parser import ISFInput
        from klproj.types import ParamType

        event_input = ISFInput(name="trigger", input_type="event")
        param = convert_isf_input_to_parameter(event_input)
        assert param is not None
        assert param.param_type == ParamType.CONSTANT_FLOAT1
        assert param.variable_name == "trigger"
        # Events should default to 0.0 (off)
        assert param.properties["value"] == 0.0
        assert param.properties["min"] == 0.0
        assert param.properties["max"] == 1.0

    def test_credit_attribute_parsing(self):
        """Test that CREDIT attribute is correctly parsed."""
        isf_with_credit = """/*
{
  "DESCRIPTION": "Test shader",
  "CREDIT": "by VIDVOX",
  "ISFVSN": "2"
}
*/
void main() { gl_FragColor = vec4(1.0); }
"""
        shader = parse_isf_string(isf_with_credit)
        assert shader.credit == "by VIDVOX"
        assert shader.description == "Test shader"


class TestRealISFFiles:
    """Test with real ISF files from the docs directory."""

    def test_parse_real_isf_files(self):
        """Test parsing the real ISF example files."""
        docs_dir = "/Users/andre/work/graphics/shaders/kodelife-generator/docs/ISF"

        # Test the example files
        example_files = ["e37459.3.frag", "e42912.0.frag"]

        for filename in example_files:
            file_path = os.path.join(docs_dir, filename)
            if os.path.exists(file_path):
                shader = parse_isf_file(file_path)
                assert shader is not None
                assert len(shader.shader_code) > 0
                print(f"✓ Parsed {filename}")

    def test_convert_real_isf_files(self, tmp_path):
        """Test converting real ISF files to KodeLife."""
        docs_dir = "/Users/andre/work/graphics/shaders/kodelife-generator/docs/ISF"

        example_files = ["e37459.3.frag", "e42912.0.frag"]

        for filename in example_files:
            file_path = os.path.join(docs_dir, filename)
            if os.path.exists(file_path):
                output_file = tmp_path / f"{os.path.splitext(filename)[0]}.klproj"
                result = convert_isf_to_kodelife(file_path, str(output_file))
                assert os.path.exists(result)
                assert os.path.getsize(result) > 0
                print(f"✓ Converted {filename} -> {output_file.name}")

    def test_circle_warp_conversion(self, tmp_path):
        """Test Circle Warp ISF file conversion (regression test)."""
        isf_path = "/Users/andre/Library/Graphics/ISF/Circle Warp.fs"

        if not os.path.exists(isf_path):
            pytest.skip("Circle Warp.fs not found")

        # Parse the ISF file
        shader = parse_isf_file(isf_path)
        assert shader is not None
        assert shader.is_filter
        assert any(inp.name == "inputImage" for inp in shader.inputs)

        # Convert it
        output_file = tmp_path / "circle_warp.klproj"
        result = convert_isf_to_kodelife(isf_path, str(output_file))

        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

        # Verify ISF built-ins are properly converted in the shader code
        from klproj.types import Parameter, ParamType

        # Create parameters that would be used for this shader
        params = [
            Parameter(ParamType.FRAME_RESOLUTION, "Resolution", "RENDERSIZE", properties={}),
        ]

        adapted_code = adapt_isf_shader_code(shader.shader_code, shader, params)

        # Should NOT contain ISF-specific elements
        assert "isf_FragNormCoord" not in adapted_code
        assert "IMG_NORM_PIXEL" not in adapted_code
        assert "IMG_PIXEL" not in adapted_code

        # Should contain proper GLSL replacements
        assert (
            "gl_FragCoord.xy / RENDERSIZE" in adapted_code
            or "(gl_FragCoord.xy / RENDERSIZE)" in adapted_code
        )
        assert "texture(inputImage" in adapted_code
        assert "fragColor" in adapted_code
