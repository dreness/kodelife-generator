"""Integration tests for the klproj package."""

import os
import xml.etree.ElementTree as ET
import zlib

from klproj import (
    KodeProjBuilder,
    Parameter,
    ParamType,
    PassType,
    RenderPass,
    ShaderProfile,
    ShaderSource,
    ShaderStage,
    ShaderStageType,
    create_mouse_param,
    create_mvp_param,
    create_resolution_param,
    create_shadertoy_params,
    create_time_param,
)
from klproj.cli import extract_klproj, verify_klproj


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_create_save_extract_verify(self, temp_dir):
        """Test complete workflow: create -> save -> extract -> verify."""
        # Create a project
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1920, 1080)
        builder.set_author("Integration Test")
        builder.set_comment("Testing end-to-end workflow")

        # Add parameters
        builder.add_global_param(create_time_param())
        builder.add_global_param(create_resolution_param())

        # Create shader stages
        vertex_code = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }"""

        fragment_code = """#version 150
out vec4 fragColor;
uniform float time;
uniform vec2 resolution;
void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    fragColor = vec4(uv, sin(time), 1.0);
}"""

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment_code)],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Main",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        # Save the project
        klproj_path = os.path.join(temp_dir, "test.klproj")
        builder.save(klproj_path)
        assert os.path.exists(klproj_path)

        # Extract it
        xml_path = os.path.join(temp_dir, "extracted.xml")
        result = extract_klproj(klproj_path, xml_path)
        assert result == 0
        assert os.path.exists(xml_path)

        # Verify content
        with open(xml_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Integration Test" in content
        assert "GL3" in content
        assert "time" in content
        assert "resolution" in content

        # Verify using CLI
        result = verify_klproj(klproj_path)
        assert result == 0

    def test_shadertoy_compatible_project(self, temp_dir, shadertoy_fragment_shader):
        """Test creating a Shadertoy-compatible project."""
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1920, 1080)
        builder.set_author("Shadertoy Test")

        # Add all Shadertoy parameters
        for param in create_shadertoy_params():
            builder.add_global_param(param)

        # Create minimal vertex shader
        vertex_code = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }"""

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, shadertoy_fragment_shader)],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Shadertoy",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        # Save and verify
        klproj_path = os.path.join(temp_dir, "shadertoy.klproj")
        builder.save(klproj_path)

        # Extract and check for Shadertoy uniforms
        xml_path = os.path.join(temp_dir, "shadertoy.xml")
        extract_klproj(klproj_path, xml_path)

        with open(xml_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify all Shadertoy uniforms are present
        assert "iResolution" in content
        assert "iTime" in content
        assert "iTimeDelta" in content
        assert "iFrame" in content
        assert "iMouse" in content
        assert "iDate" in content
        assert "iSampleRate" in content

    def test_multi_profile_project(self, temp_dir):
        """Test creating a project with multiple shader profiles."""
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1280, 720)

        # GL3 shaders
        gl3_vertex = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }"""

        gl3_fragment = """#version 150
out vec4 fragColor;
void main() { fragColor = vec4(1.0, 0.0, 0.0, 1.0); }"""

        # Metal shaders
        metal_vertex = """#include <metal_stdlib>
using namespace metal;
vertex float4 vertex_main(float4 position [[attribute(0)]],
                          constant float4x4& mvp [[buffer(0)]]) {
    return mvp * position;
}"""

        metal_fragment = """#include <metal_stdlib>
using namespace metal;
fragment float4 fragment_main() {
    return float4(1.0, 0.0, 0.0, 1.0);
}"""

        # Create stages with multiple profiles
        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[
                ShaderSource(ShaderProfile.GL3, gl3_vertex),
                ShaderSource(ShaderProfile.MTL, metal_vertex),
            ],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[
                ShaderSource(ShaderProfile.GL3, gl3_fragment),
                ShaderSource(ShaderProfile.MTL, metal_fragment),
            ],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Multi-Profile",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        # Save and verify
        klproj_path = os.path.join(temp_dir, "multiprofile.klproj")
        builder.save(klproj_path)

        # Extract and verify both profiles are present
        xml_path = os.path.join(temp_dir, "multiprofile.xml")
        extract_klproj(klproj_path, xml_path)

        root = ET.parse(xml_path).getroot()
        sources = root.findall(".//source")

        # Should have 4 sources total (2 vertex + 2 fragment)
        assert len(sources) == 4

        # Verify both profiles are present
        profiles = [src.get("profile") for src in sources]
        assert "GL3" in profiles
        assert "MTL" in profiles


class TestMultiPassProjects:
    """Test projects with multiple render passes."""

    def test_two_pass_project(self, temp_dir):
        """Test creating a two-pass project."""
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1920, 1080)

        # Create first pass
        vertex_code = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }"""

        fragment1_code = """#version 150
out vec4 fragColor;
void main() { fragColor = vec4(1.0, 0.0, 0.0, 1.0); }"""

        fragment2_code = """#version 150
out vec4 fragColor;
void main() { fragColor = vec4(0.0, 1.0, 0.0, 1.0); }"""

        # Pass 1
        vertex1 = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment1 = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment1_code)],
        )

        pass1 = RenderPass(
            pass_type=PassType.RENDER,
            label="Pass 1",
            stages=[vertex1, fragment1],
        )

        # Pass 2
        vertex2 = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment2 = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment2_code)],
        )

        pass2 = RenderPass(
            pass_type=PassType.RENDER,
            label="Pass 2",
            stages=[vertex2, fragment2],
        )

        builder.add_pass(pass1).add_pass(pass2)

        # Save and verify
        klproj_path = os.path.join(temp_dir, "twopass.klproj")
        builder.save(klproj_path)

        # Extract and verify structure
        xml_path = os.path.join(temp_dir, "twopass.xml")
        extract_klproj(klproj_path, xml_path)

        root = ET.parse(xml_path).getroot()
        passes = root.findall(".//pass")

        assert len(passes) == 2
        assert passes[0].find(".//label").text == "Pass 1"
        assert passes[1].find(".//label").text == "Pass 2"


class TestComplexParameters:
    """Test projects with complex parameter configurations."""

    def test_custom_float_parameters(self, temp_dir):
        """Test project with custom float parameters."""
        from klproj.types import Vec4

        builder = KodeProjBuilder(api="GL3")

        # Add custom float parameters
        color_param = Parameter(
            param_type=ParamType.CONSTANT_FLOAT4,
            display_name="Tint Color",
            variable_name="tintColor",
            properties={
                "value": Vec4(1.0, 0.5, 0.2, 1.0),
                "min": Vec4(0, 0, 0, 0),
                "max": Vec4(1, 1, 1, 1),
            },
        )

        speed_param = Parameter(
            param_type=ParamType.CONSTANT_FLOAT1,
            display_name="Speed",
            variable_name="speed",
            properties={"value": 2.0, "min": 0.0, "max": 10.0},
        )

        builder.add_global_param(color_param)
        builder.add_global_param(speed_param)

        # Add a simple pass
        vertex_code = "#version 150\nin vec4 a_position;\nuniform mat4 mvp;\nvoid main() { gl_Position = mvp * a_position; }"
        fragment_code = "#version 150\nout vec4 fragColor;\nuniform vec4 tintColor;\nvoid main() { fragColor = tintColor; }"

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment_code)],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Custom Params",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        # Save and verify
        klproj_path = os.path.join(temp_dir, "custom_params.klproj")
        builder.save(klproj_path)

        xml_path = os.path.join(temp_dir, "custom_params.xml")
        extract_klproj(klproj_path, xml_path)

        root = ET.parse(xml_path).getroot()

        # Verify color parameter
        color_param_elem = root.find(".//param[@type='CONSTANT_FLOAT4']")
        assert color_param_elem is not None
        assert color_param_elem.find("variableName").text == "tintColor"

        # Verify speed parameter
        speed_param_elem = root.find(".//param[@type='CONSTANT_FLOAT1']")
        assert speed_param_elem is not None
        assert speed_param_elem.find("variableName").text == "speed"

    def test_mouse_interaction_project(self, temp_dir):
        """Test project with mouse interaction."""
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1920, 1080)

        # Add mouse parameter
        builder.add_global_param(create_mouse_param(normalized=True))
        builder.add_global_param(create_time_param())

        # Create shader that uses mouse
        vertex_code = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }"""

        fragment_code = """#version 150
out vec4 fragColor;
uniform vec4 mouse;
uniform float time;
void main() {
    vec2 m = mouse.xy;
    fragColor = vec4(m, sin(time), 1.0);
}"""

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment_code)],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Mouse Interactive",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        # Save and verify
        klproj_path = os.path.join(temp_dir, "mouse.klproj")
        builder.save(klproj_path)

        xml_path = os.path.join(temp_dir, "mouse.xml")
        extract_klproj(klproj_path, xml_path)

        with open(xml_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "mouse" in content
        assert "INPUT_MOUSE_SIMPLE" in content
        assert "normalize" in content


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_minimal_gradient_shader(self, temp_dir):
        """Test creating a minimal gradient shader project."""
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1920, 1080)
        builder.set_author("Gradient Example")

        builder.add_global_param(create_resolution_param())

        vertex_code = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }"""

        fragment_code = """#version 150
out vec4 fragColor;
uniform vec2 resolution;
void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    fragColor = vec4(uv.x, uv.y, 0.5, 1.0);
}"""

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment_code)],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Gradient",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        klproj_path = os.path.join(temp_dir, "gradient.klproj")
        builder.save(klproj_path)

        # Verify file is valid
        assert os.path.exists(klproj_path)
        assert os.path.getsize(klproj_path) > 0

        # Verify can be decompressed
        with open(klproj_path, "rb") as f:
            compressed = f.read()
        decompressed = zlib.decompress(compressed)
        root = ET.fromstring(decompressed)
        assert root.tag == "klxml"

    def test_animated_rainbow_shader(self, temp_dir):
        """Test creating an animated rainbow shader."""
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1920, 1080)
        builder.set_author("Rainbow Example")

        builder.add_global_param(create_resolution_param())
        builder.add_global_param(create_time_param())

        vertex_code = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() { gl_Position = mvp * a_position; }"""

        fragment_code = """#version 150
out vec4 fragColor;
uniform vec2 resolution;
uniform float time;
void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec3 col = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));
    fragColor = vec4(col, 1.0);
}"""

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment_code)],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Rainbow",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        klproj_path = os.path.join(temp_dir, "rainbow.klproj")
        builder.save(klproj_path)

        # Verify
        xml_path = os.path.join(temp_dir, "rainbow.xml")
        extract_klproj(klproj_path, xml_path)

        with open(xml_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Rainbow Example" in content
        assert "time" in content
        assert "resolution" in content
        assert "cos(time" in content or "cos" in content

    def test_method_chaining_workflow(self, temp_dir):
        """Test using method chaining for fluent API."""
        # Create entire project using method chaining
        builder = (
            KodeProjBuilder(api="GL3")
            .set_resolution(1280, 720)
            .set_author("Chaining Test")
            .set_comment("Testing method chaining")
            .add_global_param(create_time_param())
            .add_global_param(create_resolution_param())
        )

        # Add pass
        vertex_code = "#version 150\nin vec4 a_position;\nuniform mat4 mvp;\nvoid main() { gl_Position = mvp * a_position; }"
        fragment_code = "#version 150\nout vec4 fragColor;\nvoid main() { fragColor = vec4(1.0); }"

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[create_mvp_param()],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment_code)],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Test",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)

        klproj_path = os.path.join(temp_dir, "chaining.klproj")
        builder.save(klproj_path)

        # Verify
        assert os.path.exists(klproj_path)
        xml_path = os.path.join(temp_dir, "chaining.xml")
        extract_klproj(klproj_path, xml_path)

        with open(xml_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Chaining Test" in content
        assert "Testing method chaining" in content
