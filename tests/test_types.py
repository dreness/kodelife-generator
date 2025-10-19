"""Tests for klproj.types module."""

import pytest
from klproj.types import (
    ShaderProfile,
    ShaderStageType,
    PassType,
    ParamType,
    Vec2,
    Vec3,
    Vec4,
    ProjectProperties,
    Parameter,
    ShaderSource,
    ShaderStage,
    RenderPass,
)


class TestEnums:
    """Test enum definitions."""

    def test_shader_profile_values(self):
        """Test ShaderProfile enum has expected values."""
        assert ShaderProfile.DX9.value == "DX9"
        assert ShaderProfile.ES3.value == "ES3"
        assert ShaderProfile.ES3_300.value == "ES3-300"
        assert ShaderProfile.ES3_310.value == "ES3-310"
        assert ShaderProfile.ES3_320.value == "ES3-320"
        assert ShaderProfile.GL2.value == "GL2"
        assert ShaderProfile.GL3.value == "GL3"
        assert ShaderProfile.MTL.value == "MTL"

    def test_shader_stage_type_values(self):
        """Test ShaderStageType enum has expected values."""
        assert ShaderStageType.VERTEX.value == "VERTEX"
        assert ShaderStageType.TESS_CONTROL.value == "TESS_CONTROL"
        assert ShaderStageType.TESS_EVAL.value == "TESS_EVAL"
        assert ShaderStageType.GEOMETRY.value == "GEOMETRY"
        assert ShaderStageType.FRAGMENT.value == "FRAGMENT"
        assert ShaderStageType.COMPUTE.value == "COMPUTE"

    def test_pass_type_values(self):
        """Test PassType enum has expected values."""
        assert PassType.RENDER.value == "RENDER"
        assert PassType.COMPUTE.value == "COMPUTE"

    def test_param_type_values(self):
        """Test ParamType enum has expected values."""
        assert ParamType.CLOCK.value == "CLOCK"
        assert ParamType.FRAME_RESOLUTION.value == "FRAME_RESOLUTION"
        assert ParamType.FRAME_DELTA.value == "FRAME_DELTA"
        assert ParamType.FRAME_NUMBER.value == "FRAME_NUMBER"
        assert ParamType.INPUT_MOUSE_SIMPLE.value == "INPUT_MOUSE_SIMPLE"
        assert ParamType.DATE.value == "DATE"
        assert ParamType.CONSTANT_FLOAT1.value == "CONSTANT_FLOAT1"
        assert ParamType.CONSTANT_FLOAT2.value == "CONSTANT_FLOAT2"
        assert ParamType.CONSTANT_FLOAT3.value == "CONSTANT_FLOAT3"
        assert ParamType.CONSTANT_FLOAT4.value == "CONSTANT_FLOAT4"
        assert ParamType.TRANSFORM_MVP.value == "TRANSFORM_MVP"


class TestVectors:
    """Test vector data classes."""

    def test_vec2_creation(self):
        """Test Vec2 creation with default and custom values."""
        v1 = Vec2()
        assert v1.x == 0.0
        assert v1.y == 0.0

        v2 = Vec2(1.5, 2.5)
        assert v2.x == 1.5
        assert v2.y == 2.5

    def test_vec3_creation(self):
        """Test Vec3 creation with default and custom values."""
        v1 = Vec3()
        assert v1.x == 0.0
        assert v1.y == 0.0
        assert v1.z == 0.0

        v2 = Vec3(1.0, 2.0, 3.0)
        assert v2.x == 1.0
        assert v2.y == 2.0
        assert v2.z == 3.0

    def test_vec4_creation(self):
        """Test Vec4 creation with default and custom values."""
        v1 = Vec4()
        assert v1.x == 0.0
        assert v1.y == 0.0
        assert v1.z == 0.0
        assert v1.w == 0.0

        v2 = Vec4(1.0, 0.5, 0.25, 1.0)
        assert v2.x == 1.0
        assert v2.y == 0.5
        assert v2.z == 0.25
        assert v2.w == 1.0


class TestProjectProperties:
    """Test ProjectProperties data class."""

    def test_default_properties(self):
        """Test ProjectProperties with default values."""
        props = ProjectProperties()
        assert props.creator == "net.hexler.KodeLife"
        assert props.creator_version == "1.2.3.202"
        assert props.version_major == 1
        assert props.version_minor == 1
        assert props.version_patch == 1
        assert props.author == ""
        assert props.comment == ""
        assert props.enabled == 1
        assert props.width == 1920
        assert props.height == 1080
        assert props.format == "RGBA32F"
        assert props.clear_color.x == 0
        assert props.clear_color.y == 0
        assert props.clear_color.z == 0
        assert props.clear_color.w == 1
        assert props.audio_source_type == 0
        assert props.audio_file_path == ""

    def test_custom_properties(self):
        """Test ProjectProperties with custom values."""
        props = ProjectProperties(
            author="Test Author",
            comment="Test project",
            width=1280,
            height=720,
            clear_color=Vec4(1, 1, 1, 1),
        )
        assert props.author == "Test Author"
        assert props.comment == "Test project"
        assert props.width == 1280
        assert props.height == 720
        assert props.clear_color.x == 1


class TestParameter:
    """Test Parameter data class."""

    def test_basic_parameter(self):
        """Test creating a basic parameter."""
        param = Parameter(
            param_type=ParamType.CLOCK,
            display_name="Time",
            variable_name="iTime",
        )
        assert param.param_type == ParamType.CLOCK
        assert param.display_name == "Time"
        assert param.variable_name == "iTime"
        assert param.ui_expanded == 0
        assert param.properties == {}

    def test_parameter_with_properties(self):
        """Test creating a parameter with properties."""
        param = Parameter(
            param_type=ParamType.CLOCK,
            display_name="Time",
            variable_name="time",
            ui_expanded=1,
            properties={"running": 1, "speed": 2.0},
        )
        assert param.properties["running"] == 1
        assert param.properties["speed"] == 2.0
        assert param.ui_expanded == 1

    def test_parameter_with_vector_properties(self):
        """Test parameter with vector properties."""
        param = Parameter(
            param_type=ParamType.CONSTANT_FLOAT4,
            display_name="Color",
            variable_name="color",
            properties={"value": Vec4(1, 0, 0, 1)},
        )
        assert isinstance(param.properties["value"], Vec4)
        assert param.properties["value"].x == 1


class TestShaderSource:
    """Test ShaderSource data class."""

    def test_shader_source_creation(self):
        """Test creating shader source."""
        code = "#version 150\nvoid main() {}"
        source = ShaderSource(profile=ShaderProfile.GL3, code=code)
        assert source.profile == ShaderProfile.GL3
        assert source.code == code

    def test_multiple_profiles(self):
        """Test creating sources for different profiles."""
        gl3_code = "#version 150\nvoid main() {}"
        mtl_code = "#include <metal_stdlib>"

        gl3_source = ShaderSource(ShaderProfile.GL3, gl3_code)
        mtl_source = ShaderSource(ShaderProfile.MTL, mtl_code)

        assert gl3_source.profile == ShaderProfile.GL3
        assert mtl_source.profile == ShaderProfile.MTL


class TestShaderStage:
    """Test ShaderStage data class."""

    def test_default_shader_stage(self):
        """Test creating shader stage with defaults."""
        stage = ShaderStage(stage_type=ShaderStageType.FRAGMENT)
        assert stage.stage_type == ShaderStageType.FRAGMENT
        assert stage.enabled == 1
        assert stage.hidden == 0
        assert stage.sources == []
        assert stage.parameters == []

    def test_shader_stage_with_sources(self):
        """Test shader stage with sources."""
        source = ShaderSource(ShaderProfile.GL3, "void main() {}")
        stage = ShaderStage(
            stage_type=ShaderStageType.FRAGMENT,
            enabled=1,
            hidden=0,
            sources=[source],
        )
        assert len(stage.sources) == 1
        assert stage.sources[0] == source

    def test_shader_stage_with_parameters(self):
        """Test shader stage with parameters."""
        param = Parameter(
            param_type=ParamType.TRANSFORM_MVP,
            display_name="MVP",
            variable_name="mvp",
        )
        stage = ShaderStage(
            stage_type=ShaderStageType.VERTEX,
            parameters=[param],
        )
        assert len(stage.parameters) == 1
        assert stage.parameters[0] == param

    def test_vertex_stage(self):
        """Test creating a vertex shader stage."""
        stage = ShaderStage(stage_type=ShaderStageType.VERTEX, hidden=1)
        assert stage.stage_type == ShaderStageType.VERTEX
        assert stage.hidden == 1


class TestRenderPass:
    """Test RenderPass data class."""

    def test_default_render_pass(self):
        """Test creating render pass with defaults."""
        pass_obj = RenderPass(pass_type=PassType.RENDER)
        assert pass_obj.pass_type == PassType.RENDER
        assert pass_obj.label == "Pass A"
        assert pass_obj.enabled == 1
        assert pass_obj.primitive_type == "TRIANGLES"
        assert pass_obj.stages == []
        assert pass_obj.parameters == []
        assert pass_obj.width == 1920
        assert pass_obj.height == 1080

    def test_render_pass_with_stages(self):
        """Test render pass with shader stages."""
        vertex_stage = ShaderStage(stage_type=ShaderStageType.VERTEX)
        fragment_stage = ShaderStage(stage_type=ShaderStageType.FRAGMENT)

        pass_obj = RenderPass(
            pass_type=PassType.RENDER,
            label="Main Pass",
            stages=[vertex_stage, fragment_stage],
        )
        assert len(pass_obj.stages) == 2
        assert pass_obj.label == "Main Pass"

    def test_render_pass_with_parameters(self):
        """Test render pass with parameters."""
        param = Parameter(
            param_type=ParamType.CLOCK,
            display_name="Time",
            variable_name="time",
        )
        pass_obj = RenderPass(
            pass_type=PassType.RENDER,
            parameters=[param],
        )
        assert len(pass_obj.parameters) == 1

    def test_compute_pass(self):
        """Test creating a compute pass."""
        pass_obj = RenderPass(
            pass_type=PassType.COMPUTE,
            label="Compute Pass",
        )
        assert pass_obj.pass_type == PassType.COMPUTE
        assert pass_obj.label == "Compute Pass"

    def test_custom_resolution(self):
        """Test render pass with custom resolution."""
        pass_obj = RenderPass(
            pass_type=PassType.RENDER,
            width=1280,
            height=720,
        )
        assert pass_obj.width == 1280
        assert pass_obj.height == 720