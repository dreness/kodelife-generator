"""Tests for klproj.generator module."""

import os
import tempfile
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

import pytest
from klproj.generator import KodeProjBuilder
from klproj.types import (
    Parameter,
    ParamType,
    PassType,
    RenderPass,
    ShaderProfile,
    ShaderSource,
    ShaderStage,
    ShaderStageType,
    Vec4,
)


class TestKodeProjBuilderInit:
    """Test KodeProjBuilder initialization."""

    def test_default_initialization(self):
        """Test builder with default values."""
        builder = KodeProjBuilder()
        assert builder.version == 19
        assert builder.api == "MTL"
        assert builder.properties.width == 1920
        assert builder.properties.height == 1080
        assert len(builder.global_params) == 0
        assert len(builder.passes) == 0

    def test_custom_initialization(self):
        """Test builder with custom values."""
        builder = KodeProjBuilder(version=20, api="GL3")
        assert builder.version == 20
        assert builder.api == "GL3"

    def test_different_apis(self):
        """Test builder with different API values."""
        for api in ["GL3", "GL2", "MTL", "ES3"]:
            builder = KodeProjBuilder(api=api)
            assert builder.api == api


class TestKodeProjBuilderProperties:
    """Test setting properties on KodeProjBuilder."""

    def test_set_resolution(self):
        """Test setting project resolution."""
        builder = KodeProjBuilder()
        result = builder.set_resolution(1280, 720)
        assert builder.properties.width == 1280
        assert builder.properties.height == 720
        assert result is builder  # Test method chaining

    def test_set_author(self):
        """Test setting project author."""
        builder = KodeProjBuilder()
        result = builder.set_author("Test Author")
        assert builder.properties.author == "Test Author"
        assert result is builder

    def test_set_comment(self):
        """Test setting project comment."""
        builder = KodeProjBuilder()
        result = builder.set_comment("Test project description")
        assert builder.properties.comment == "Test project description"
        assert result is builder

    def test_method_chaining(self):
        """Test chaining multiple property setters."""
        builder = KodeProjBuilder()
        builder.set_resolution(1920, 1080).set_author("Author").set_comment("Comment")
        assert builder.properties.width == 1920
        assert builder.properties.height == 1080
        assert builder.properties.author == "Author"
        assert builder.properties.comment == "Comment"


class TestKodeProjBuilderParams:
    """Test adding parameters to KodeProjBuilder."""

    def test_add_global_param(self):
        """Test adding a global parameter."""
        builder = KodeProjBuilder()
        param = Parameter(
            param_type=ParamType.CLOCK,
            display_name="Time",
            variable_name="time",
        )
        result = builder.add_global_param(param)
        assert len(builder.global_params) == 1
        assert builder.global_params[0] == param
        assert result is builder

    def test_add_multiple_params(self):
        """Test adding multiple global parameters."""
        builder = KodeProjBuilder()
        param1 = Parameter(ParamType.CLOCK, "Time", "time")
        param2 = Parameter(ParamType.FRAME_RESOLUTION, "Resolution", "resolution")

        builder.add_global_param(param1).add_global_param(param2)
        assert len(builder.global_params) == 2


class TestKodeProjBuilderPasses:
    """Test adding passes to KodeProjBuilder."""

    def test_add_pass(self):
        """Test adding a render pass."""
        builder = KodeProjBuilder()
        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Test Pass",
        )
        result = builder.add_pass(render_pass)
        assert len(builder.passes) == 1
        assert builder.passes[0] == render_pass
        assert result is builder

    def test_add_multiple_passes(self):
        """Test adding multiple render passes."""
        builder = KodeProjBuilder()
        pass1 = RenderPass(PassType.RENDER, label="Pass 1")
        pass2 = RenderPass(PassType.RENDER, label="Pass 2")

        builder.add_pass(pass1).add_pass(pass2)
        assert len(builder.passes) == 2
        assert builder.passes[0].label == "Pass 1"
        assert builder.passes[1].label == "Pass 2"


class TestKodeProjBuilderXML:
    """Test XML generation from KodeProjBuilder."""

    def test_build_xml_structure(self):
        """Test that build_xml produces valid XML."""
        builder = KodeProjBuilder()
        xml_str = builder.build_xml()

        # Parse to verify it's valid XML
        root = ET.fromstring(xml_str)
        assert root.tag == "klxml"
        assert root.get("v") == "19"
        assert root.get("a") == "MTL"

    def test_xml_has_document(self):
        """Test that XML contains document element."""
        builder = KodeProjBuilder()
        xml_str = builder.build_xml()
        root = ET.fromstring(xml_str)

        document = root.find("document")
        assert document is not None

    def test_xml_has_properties(self):
        """Test that XML contains properties section."""
        builder = KodeProjBuilder()
        builder.set_resolution(1920, 1080)
        builder.set_author("Test Author")

        xml_str = builder.build_xml()
        root = ET.fromstring(xml_str)

        properties = root.find(".//properties")
        assert properties is not None

        author = properties.find("author")
        assert author is not None
        assert author.text == "Test Author"

    def test_xml_has_params_section(self):
        """Test that XML contains params section."""
        builder = KodeProjBuilder()
        param = Parameter(ParamType.CLOCK, "Time", "time")
        builder.add_global_param(param)

        xml_str = builder.build_xml()
        root = ET.fromstring(xml_str)

        params = root.find(".//params")
        assert params is not None

    def test_xml_parameter_encoding(self):
        """Test that parameters are properly encoded in XML."""
        builder = KodeProjBuilder()
        param = Parameter(
            param_type=ParamType.CLOCK,
            display_name="Test Time",
            variable_name="testTime",
            properties={"running": 1, "speed": 2.0},
        )
        builder.add_global_param(param)

        xml_str = builder.build_xml()
        root = ET.fromstring(xml_str)

        param_elem = root.find(".//param[@type='CLOCK']")
        assert param_elem is not None
        assert param_elem.find("displayName").text == "Test Time"
        assert param_elem.find("variableName").text == "testTime"
        assert param_elem.find("running").text == "1"
        assert param_elem.find("speed").text == "2.0"

    def test_xml_vector_encoding(self):
        """Test that vector properties are properly encoded."""
        builder = KodeProjBuilder()
        param = Parameter(
            param_type=ParamType.CONSTANT_FLOAT4,
            display_name="Color",
            variable_name="color",
            properties={"value": Vec4(1.0, 0.5, 0.25, 1.0)},
        )
        builder.add_global_param(param)

        xml_str = builder.build_xml()
        root = ET.fromstring(xml_str)

        param_elem = root.find(".//param[@type='CONSTANT_FLOAT4']")
        assert param_elem is not None

        value = param_elem.find("value")
        assert value is not None
        assert value.find("x").text == "1.0"
        assert value.find("y").text == "0.5"
        assert value.find("z").text == "0.25"
        assert value.find("w").text == "1.0"

    def test_xml_with_render_pass(self):
        """Test XML generation with a render pass."""
        builder = KodeProjBuilder()

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            sources=[
                ShaderSource(
                    ShaderProfile.GL3,
                    "#version 150\nvoid main() { gl_Position = vec4(0); }",
                )
            ],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            sources=[
                ShaderSource(
                    ShaderProfile.GL3,
                    "#version 150\nout vec4 fragColor;\nvoid main() { fragColor = vec4(1); }",
                )
            ],
        )

        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Test Pass",
            stages=[vertex_stage, fragment_stage],
        )

        builder.add_pass(render_pass)
        xml_str = builder.build_xml()
        root = ET.fromstring(xml_str)

        passes = root.find(".//passes")
        assert passes is not None

        pass_elem = passes.find("pass[@type='RENDER']")
        assert pass_elem is not None

        stages = pass_elem.find("stages")
        assert stages is not None
        assert len(stages.findall("stage")) == 2


class TestKodeProjBuilderSave:
    """Test saving .klproj files."""

    def test_save_creates_file(self):
        """Test that save creates a file."""
        builder = KodeProjBuilder()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.klproj")
            builder.save(filepath)
            assert os.path.exists(filepath)

    def test_save_creates_compressed_file(self):
        """Test that saved file is compressed."""
        builder = KodeProjBuilder()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.klproj")
            builder.save(filepath)

            # Read the file and verify it's compressed
            with open(filepath, "rb") as f:
                compressed_data = f.read()

            # Should be able to decompress it
            decompressed = zlib.decompress(compressed_data)
            assert len(decompressed) > 0

            # Decompressed data should be valid XML
            root = ET.fromstring(decompressed)
            assert root.tag == "klxml"

    def test_save_preserves_data(self):
        """Test that saved file contains correct data."""
        builder = KodeProjBuilder()
        builder.set_resolution(1280, 720)
        builder.set_author("Test Author")

        param = Parameter(ParamType.CLOCK, "Time", "time")
        builder.add_global_param(param)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.klproj")
            builder.save(filepath)

            # Read and decompress
            with open(filepath, "rb") as f:
                compressed = f.read()
            decompressed = zlib.decompress(compressed)
            root = ET.fromstring(decompressed)

            # Verify data
            author = root.find(".//author")
            assert author.text == "Test Author"

            size_x = root.find(".//properties/size/x")
            assert size_x.text == "1280"


class TestKodeProjBuilderIntegration:
    """Integration tests for complete project generation."""

    def test_complete_shader_project(self):
        """Test creating a complete shader project."""
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1920, 1080)
        builder.set_author("Test")

        # Add global parameters
        time_param = Parameter(
            param_type=ParamType.CLOCK,
            display_name="Time",
            variable_name="time",
            properties={"running": 1, "speed": 1.0},
        )
        resolution_param = Parameter(
            param_type=ParamType.FRAME_RESOLUTION,
            display_name="Resolution",
            variable_name="resolution",
        )
        builder.add_global_param(time_param)
        builder.add_global_param(resolution_param)

        # Create shader stages
        vertex_code = """#version 150
in vec4 a_position;
uniform mat4 mvp;
void main() {
    gl_Position = mvp * a_position;
}"""

        fragment_code = """#version 150
out vec4 fragColor;
uniform float time;
uniform vec2 resolution;
void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    fragColor = vec4(uv, 0.5 + 0.5 * sin(time), 1.0);
}"""

        mvp_param = Parameter(
            param_type=ParamType.TRANSFORM_MVP,
            display_name="MVP",
            variable_name="mvp",
        )

        vertex_stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            enabled=1,
            hidden=1,
            sources=[ShaderSource(ShaderProfile.GL3, vertex_code)],
            parameters=[mvp_param],
        )

        fragment_stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            sources=[ShaderSource(ShaderProfile.GL3, fragment_code)],
        )

        # Create render pass
        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Main Pass",
            stages=[vertex_stage, fragment_stage],
            width=1920,
            height=1080,
        )

        builder.add_pass(render_pass)

        # Save and verify
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "complete.klproj")
            builder.save(filepath)

            # Verify file exists and is valid
            assert os.path.exists(filepath)

            with open(filepath, "rb") as f:
                compressed = f.read()
            decompressed = zlib.decompress(compressed)
            root = ET.fromstring(decompressed)

            # Verify structure
            assert root.tag == "klxml"
            assert root.get("a") == "GL3"
            assert len(root.findall(".//param")) == 3  # time, resolution, mvp
            assert len(root.findall(".//pass")) == 1
            assert len(root.findall(".//stage")) == 2

    def test_multi_pass_project(self):
        """Test creating a multi-pass project."""
        builder = KodeProjBuilder()

        # Create two simple passes
        pass1 = RenderPass(PassType.RENDER, label="Pass 1")
        pass2 = RenderPass(PassType.RENDER, label="Pass 2")

        builder.add_pass(pass1).add_pass(pass2)

        xml_str = builder.build_xml()
        root = ET.fromstring(xml_str)

        passes = root.findall(".//pass")
        assert len(passes) == 2