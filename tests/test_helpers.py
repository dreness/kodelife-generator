"""Tests for klproj.helpers module."""

from klproj.helpers import (
    create_default_vertex_stage,
    create_file_watch_stage,
    create_fragment_file_watch_stage,
    create_mouse_param,
    create_mvp_param,
    create_resolution_param,
    create_shadertoy_params,
    create_time_param,
    create_vertex_file_watch_stage,
)
from klproj.types import Parameter, ParamType, ShaderProfile, ShaderStage, ShaderStageType


class TestCreateShadertoyParams:
    """Test create_shadertoy_params function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        params = create_shadertoy_params()
        assert isinstance(params, list)
        assert len(params) > 0

    def test_returns_seven_parameters(self):
        """Test that it returns exactly 7 parameters."""
        params = create_shadertoy_params()
        assert len(params) == 7

    def test_all_are_parameters(self):
        """Test that all items are Parameter objects."""
        params = create_shadertoy_params()
        for param in params:
            assert isinstance(param, Parameter)

    def test_iresolution_parameter(self):
        """Test iResolution parameter."""
        params = create_shadertoy_params()
        iresolution = params[0]

        assert iresolution.param_type == ParamType.FRAME_RESOLUTION
        assert iresolution.display_name == "Frame Resolution"
        assert iresolution.variable_name == "iResolution"

    def test_itime_parameter(self):
        """Test iTime parameter."""
        params = create_shadertoy_params()
        itime = params[1]

        assert itime.param_type == ParamType.CLOCK
        assert itime.display_name == "Clock"
        assert itime.variable_name == "iTime"
        assert itime.properties["running"] == 1
        assert itime.properties["speed"] == 1

    def test_itimedelta_parameter(self):
        """Test iTimeDelta parameter."""
        params = create_shadertoy_params()
        itimedelta = params[2]

        assert itimedelta.param_type == ParamType.FRAME_DELTA
        assert itimedelta.display_name == "Frame Delta"
        assert itimedelta.variable_name == "iTimeDelta"

    def test_iframe_parameter(self):
        """Test iFrame parameter."""
        params = create_shadertoy_params()
        iframe = params[3]

        assert iframe.param_type == ParamType.FRAME_NUMBER
        assert iframe.display_name == "Frame Number"
        assert iframe.variable_name == "iFrame"

    def test_imouse_parameter(self):
        """Test iMouse parameter."""
        params = create_shadertoy_params()
        imouse = params[4]

        assert imouse.param_type == ParamType.INPUT_MOUSE_SIMPLE
        assert imouse.display_name == "Mouse Simple"
        assert imouse.variable_name == "iMouse"
        assert imouse.properties["variant"] == 1
        assert imouse.properties["normalize"] == 0
        assert imouse.properties["invert"]["x"] == 0
        assert imouse.properties["invert"]["y"] == 1

    def test_idate_parameter(self):
        """Test iDate parameter."""
        params = create_shadertoy_params()
        idate = params[5]

        assert idate.param_type == ParamType.DATE
        assert idate.display_name == "Date"
        assert idate.variable_name == "iDate"

    def test_isamplerate_parameter(self):
        """Test iSampleRate parameter."""
        params = create_shadertoy_params()
        isamplerate = params[6]

        assert isamplerate.param_type == ParamType.AUDIO_SAMPLE_RATE
        assert isamplerate.display_name == "Audio Sample Rate"
        assert isamplerate.variable_name == "iSampleRate"

    def test_parameters_order(self):
        """Test that parameters are in the correct order."""
        params = create_shadertoy_params()
        expected_names = [
            "iResolution",
            "iTime",
            "iTimeDelta",
            "iFrame",
            "iMouse",
            "iDate",
            "iSampleRate",
        ]
        actual_names = [p.variable_name for p in params]
        assert actual_names == expected_names


class TestCreateMvpParam:
    """Test create_mvp_param function."""

    def test_returns_parameter(self):
        """Test that function returns a Parameter."""
        param = create_mvp_param()
        assert isinstance(param, Parameter)

    def test_param_type(self):
        """Test parameter type."""
        param = create_mvp_param()
        assert param.param_type == ParamType.TRANSFORM_MVP

    def test_display_name(self):
        """Test display name."""
        param = create_mvp_param()
        assert param.display_name == "Model View Projection Matrix"

    def test_variable_name(self):
        """Test variable name."""
        param = create_mvp_param()
        assert param.variable_name == "mvp"

    def test_no_properties(self):
        """Test that there are no custom properties."""
        param = create_mvp_param()
        assert param.properties == {}


class TestCreateTimeParam:
    """Test create_time_param function."""

    def test_returns_parameter(self):
        """Test that function returns a Parameter."""
        param = create_time_param()
        assert isinstance(param, Parameter)

    def test_default_variable_name(self):
        """Test default variable name."""
        param = create_time_param()
        assert param.variable_name == "time"

    def test_custom_variable_name(self):
        """Test custom variable name."""
        param = create_time_param(variable_name="uTime")
        assert param.variable_name == "uTime"

    def test_default_speed(self):
        """Test default speed."""
        param = create_time_param()
        assert param.properties["speed"] == 1.0

    def test_custom_speed(self):
        """Test custom speed."""
        param = create_time_param(speed=2.5)
        assert param.properties["speed"] == 2.5

    def test_param_type(self):
        """Test parameter type."""
        param = create_time_param()
        assert param.param_type == ParamType.CLOCK

    def test_display_name(self):
        """Test display name."""
        param = create_time_param()
        assert param.display_name == "Time"

    def test_running_property(self):
        """Test that running property is set."""
        param = create_time_param()
        assert param.properties["running"] == 1

    def test_direction_property(self):
        """Test that direction property is set."""
        param = create_time_param()
        assert param.properties["direction"] == 1

    def test_loop_properties(self):
        """Test loop properties."""
        param = create_time_param()
        assert param.properties["loop"] == 0
        assert param.properties["loopStart"] == 0
        assert param.properties["loopEnd"] == 6.28319

    def test_all_properties_with_custom_speed(self):
        """Test that custom speed doesn't affect other properties."""
        param = create_time_param(speed=0.5)
        assert param.properties["running"] == 1
        assert param.properties["speed"] == 0.5
        assert param.properties["loop"] == 0


class TestCreateResolutionParam:
    """Test create_resolution_param function."""

    def test_returns_parameter(self):
        """Test that function returns a Parameter."""
        param = create_resolution_param()
        assert isinstance(param, Parameter)

    def test_default_variable_name(self):
        """Test default variable name."""
        param = create_resolution_param()
        assert param.variable_name == "resolution"

    def test_custom_variable_name(self):
        """Test custom variable name."""
        param = create_resolution_param(variable_name="uResolution")
        assert param.variable_name == "uResolution"

    def test_param_type(self):
        """Test parameter type."""
        param = create_resolution_param()
        assert param.param_type == ParamType.FRAME_RESOLUTION

    def test_display_name(self):
        """Test display name."""
        param = create_resolution_param()
        assert param.display_name == "Resolution"

    def test_no_properties(self):
        """Test that there are no custom properties."""
        param = create_resolution_param()
        assert param.properties == {}


class TestCreateMouseParam:
    """Test create_mouse_param function."""

    def test_returns_parameter(self):
        """Test that function returns a Parameter."""
        param = create_mouse_param()
        assert isinstance(param, Parameter)

    def test_default_variable_name(self):
        """Test default variable name."""
        param = create_mouse_param()
        assert param.variable_name == "mouse"

    def test_custom_variable_name(self):
        """Test custom variable name."""
        param = create_mouse_param(variable_name="uMouse")
        assert param.variable_name == "uMouse"

    def test_param_type(self):
        """Test parameter type."""
        param = create_mouse_param()
        assert param.param_type == ParamType.INPUT_MOUSE_SIMPLE

    def test_display_name(self):
        """Test display name."""
        param = create_mouse_param()
        assert param.display_name == "Mouse"

    def test_default_normalized(self):
        """Test default normalized setting."""
        param = create_mouse_param()
        assert param.properties["normalize"] == 0

    def test_custom_normalized_true(self):
        """Test custom normalized=True."""
        param = create_mouse_param(normalized=True)
        assert param.properties["normalize"] == 1

    def test_custom_normalized_false(self):
        """Test custom normalized=False."""
        param = create_mouse_param(normalized=False)
        assert param.properties["normalize"] == 0

    def test_default_invert_y(self):
        """Test default invert_y setting."""
        param = create_mouse_param()
        assert param.properties["invert"]["y"] == 1

    def test_custom_invert_y_false(self):
        """Test custom invert_y=False."""
        param = create_mouse_param(invert_y=False)
        assert param.properties["invert"]["y"] == 0

    def test_custom_invert_y_true(self):
        """Test custom invert_y=True."""
        param = create_mouse_param(invert_y=True)
        assert param.properties["invert"]["y"] == 1

    def test_invert_x_always_zero(self):
        """Test that invert x is always 0."""
        param1 = create_mouse_param(invert_y=True)
        param2 = create_mouse_param(invert_y=False)
        assert param1.properties["invert"]["x"] == 0
        assert param2.properties["invert"]["x"] == 0

    def test_variant_property(self):
        """Test that variant property is set."""
        param = create_mouse_param()
        assert param.properties["variant"] == 1

    def test_combined_custom_options(self):
        """Test creating param with multiple custom options."""
        param = create_mouse_param(variable_name="customMouse", normalized=True, invert_y=False)
        assert param.variable_name == "customMouse"
        assert param.properties["normalize"] == 1
        assert param.properties["invert"]["y"] == 0
        assert param.properties["invert"]["x"] == 0


class TestHelpersIntegration:
    """Integration tests for helper functions."""

    def test_all_helpers_return_parameters(self):
        """Test that all helper functions return Parameter objects."""
        mvp = create_mvp_param()
        time = create_time_param()
        resolution = create_resolution_param()
        mouse = create_mouse_param()

        assert isinstance(mvp, Parameter)
        assert isinstance(time, Parameter)
        assert isinstance(resolution, Parameter)
        assert isinstance(mouse, Parameter)

    def test_unique_param_types(self):
        """Test that different helpers create different param types."""
        mvp = create_mvp_param()
        time = create_time_param()
        resolution = create_resolution_param()
        mouse = create_mouse_param()

        param_types = {
            mvp.param_type,
            time.param_type,
            resolution.param_type,
            mouse.param_type,
        }
        assert len(param_types) == 4  # All should be unique

    def test_shadertoy_compatibility(self):
        """Test that shadertoy params are compatible with standard params."""
        shadertoy_params = create_shadertoy_params()
        custom_time = create_time_param("iTime")
        custom_resolution = create_resolution_param("iResolution")

        # Should have compatible types
        assert shadertoy_params[1].param_type == custom_time.param_type
        assert shadertoy_params[0].param_type == custom_resolution.param_type

    def test_helper_functions_are_idempotent(self):
        """Test that calling helpers multiple times gives consistent results."""
        param1 = create_time_param("time", 1.0)
        param2 = create_time_param("time", 1.0)

        assert param1.param_type == param2.param_type
        assert param1.variable_name == param2.variable_name
        assert param1.properties == param2.properties

    def test_different_speeds_create_different_params(self):
        """Test that different speeds create different parameters."""
        time1 = create_time_param(speed=1.0)
        time2 = create_time_param(speed=2.0)

        assert time1.properties["speed"] != time2.properties["speed"]


class TestCreateFileWatchStage:
    """Test create_file_watch_stage function."""

    def test_returns_shader_stage(self):
        """Test that function returns a ShaderStage."""
        stage = create_file_watch_stage(
            ShaderStageType.FRAGMENT, "/path/to/shader.fs", shader_code=""
        )
        assert isinstance(stage, ShaderStage)

    def test_stage_type(self):
        """Test that stage type is set correctly."""
        stage = create_file_watch_stage(
            ShaderStageType.VERTEX, "/path/to/shader.vs", shader_code=""
        )
        assert stage.stage_type == ShaderStageType.VERTEX

    def test_file_watch_enabled(self):
        """Test that file watching is enabled."""
        stage = create_file_watch_stage(
            ShaderStageType.FRAGMENT, "/path/to/shader.fs", shader_code=""
        )
        assert stage.file_watch is True

    def test_file_watch_path(self):
        """Test that file watch path is set correctly."""
        path = "/path/to/shader.fs"
        stage = create_file_watch_stage(ShaderStageType.FRAGMENT, path, shader_code="")
        assert stage.file_watch_path == path

    def test_sources_empty(self):
        """Test that sources list is empty for file watching."""
        stage = create_file_watch_stage(
            ShaderStageType.FRAGMENT, "/path/to/shader.fs", shader_code=""
        )
        assert stage.sources == []

    def test_enabled_by_default(self):
        """Test that stage is enabled by default."""
        stage = create_file_watch_stage(
            ShaderStageType.FRAGMENT, "/path/to/shader.fs", shader_code=""
        )
        assert stage.enabled == 1

    def test_not_hidden(self):
        """Test that stage is not hidden by default."""
        stage = create_file_watch_stage(
            ShaderStageType.FRAGMENT, "/path/to/shader.fs", shader_code=""
        )
        assert stage.hidden == 0

    def test_no_parameters_by_default(self):
        """Test that no parameters are added by default."""
        stage = create_file_watch_stage(
            ShaderStageType.FRAGMENT, "/path/to/shader.fs", shader_code=""
        )
        assert stage.parameters == []

    def test_custom_parameters(self):
        """Test that custom parameters can be added."""
        params = [create_mvp_param()]
        stage = create_file_watch_stage(
            ShaderStageType.VERTEX, "/path/to/shader.vs", parameters=params, shader_code=""
        )
        assert len(stage.parameters) == 1
        assert stage.parameters[0].param_type == ParamType.TRANSFORM_MVP


class TestCreateVertexFileWatchStage:
    """Test create_vertex_file_watch_stage function."""

    def test_returns_shader_stage(self):
        """Test that function returns a ShaderStage."""
        stage = create_vertex_file_watch_stage("/path/to/shader.vs", shader_code="")
        assert isinstance(stage, ShaderStage)

    def test_stage_type_is_vertex(self):
        """Test that stage type is VERTEX."""
        stage = create_vertex_file_watch_stage("/path/to/shader.vs", shader_code="")
        assert stage.stage_type == ShaderStageType.VERTEX

    def test_file_watch_enabled(self):
        """Test that file watching is enabled."""
        stage = create_vertex_file_watch_stage("/path/to/shader.vs", shader_code="")
        assert stage.file_watch is True

    def test_file_watch_path(self):
        """Test that file watch path is set correctly."""
        path = "/path/to/shader.vs"
        stage = create_vertex_file_watch_stage(path, shader_code="")
        assert stage.file_watch_path == path

    def test_mvp_included_by_default(self):
        """Test that MVP parameter is included by default."""
        stage = create_vertex_file_watch_stage("/path/to/shader.vs", shader_code="")
        assert len(stage.parameters) == 1
        assert stage.parameters[0].param_type == ParamType.TRANSFORM_MVP

    def test_mvp_can_be_disabled(self):
        """Test that MVP parameter can be disabled."""
        stage = create_vertex_file_watch_stage("/path/to/shader.vs", mvp=False, shader_code="")
        assert len(stage.parameters) == 0


class TestCreateFragmentFileWatchStage:
    """Test create_fragment_file_watch_stage function."""

    def test_returns_shader_stage(self):
        """Test that function returns a ShaderStage."""
        stage = create_fragment_file_watch_stage("/path/to/shader.fs", shader_code="")
        assert isinstance(stage, ShaderStage)

    def test_stage_type_is_fragment(self):
        """Test that stage type is FRAGMENT."""
        stage = create_fragment_file_watch_stage("/path/to/shader.fs", shader_code="")
        assert stage.stage_type == ShaderStageType.FRAGMENT

    def test_file_watch_enabled(self):
        """Test that file watching is enabled."""
        stage = create_fragment_file_watch_stage("/path/to/shader.fs", shader_code="")
        assert stage.file_watch is True

    def test_file_watch_path(self):
        """Test that file watch path is set correctly."""
        path = "/path/to/shader.fs"
        stage = create_fragment_file_watch_stage(path, shader_code="")
        assert stage.file_watch_path == path

    def test_no_parameters_by_default(self):
        """Test that no parameters are added by default."""
        stage = create_fragment_file_watch_stage("/path/to/shader.fs", shader_code="")
        assert stage.parameters == []

    def test_custom_parameters(self):
        """Test that custom parameters can be added."""
        params = [create_time_param()]
        stage = create_fragment_file_watch_stage(
            "/path/to/shader.fs", parameters=params, shader_code=""
        )
        assert len(stage.parameters) == 1
        assert stage.parameters[0].param_type == ParamType.CLOCK


class TestCreateDefaultVertexStage:
    """Test create_default_vertex_stage function."""

    def test_returns_shader_stage(self):
        """Test that function returns a ShaderStage."""
        stage = create_default_vertex_stage()
        assert isinstance(stage, ShaderStage)

    def test_stage_type_is_vertex(self):
        """Test that stage type is VERTEX."""
        stage = create_default_vertex_stage()
        assert stage.stage_type == ShaderStageType.VERTEX

    def test_file_watch_disabled(self):
        """Test that file watching is disabled for default shader."""
        stage = create_default_vertex_stage()
        assert stage.file_watch is False

    def test_has_sources(self):
        """Test that sources list is not empty."""
        stage = create_default_vertex_stage()
        assert len(stage.sources) > 0

    def test_default_profile_gl3(self):
        """Test that default profile is GL3."""
        stage = create_default_vertex_stage()
        assert stage.sources[0].profile == ShaderProfile.GL3

    def test_custom_profile(self):
        """Test that custom profile can be set."""
        stage = create_default_vertex_stage(profile=ShaderProfile.MTL)
        assert stage.sources[0].profile == ShaderProfile.MTL

    def test_has_source_code(self):
        """Test that source code is not empty."""
        stage = create_default_vertex_stage()
        assert len(stage.sources[0].code) > 0

    def test_includes_mvp_parameter(self):
        """Test that MVP parameter is included."""
        stage = create_default_vertex_stage()
        assert len(stage.parameters) == 1
        assert stage.parameters[0].param_type == ParamType.TRANSFORM_MVP

    def test_gl3_shader_contains_version(self):
        """Test that GL3 shader contains version directive."""
        stage = create_default_vertex_stage(profile=ShaderProfile.GL3)
        assert "#version" in stage.sources[0].code

    def test_metal_shader_contains_metal_stdlib(self):
        """Test that Metal shader contains metal_stdlib."""
        stage = create_default_vertex_stage(profile=ShaderProfile.MTL)
        assert "metal_stdlib" in stage.sources[0].code


class TestFileWatchIntegration:
    """Integration tests for file watch helper functions."""

    def test_vertex_and_fragment_watch_together(self):
        """Test creating both vertex and fragment file watch stages."""
        vertex = create_vertex_file_watch_stage("/path/to/shader.vs", shader_code="")
        fragment = create_fragment_file_watch_stage("/path/to/shader.fs", shader_code="")

        assert vertex.stage_type == ShaderStageType.VERTEX
        assert fragment.stage_type == ShaderStageType.FRAGMENT
        assert vertex.file_watch is True
        assert fragment.file_watch is True

    def test_mixed_embedded_and_watch(self):
        """Test mixing embedded and file watch stages."""
        vertex = create_default_vertex_stage()
        fragment = create_fragment_file_watch_stage("/path/to/shader.fs", shader_code="")

        assert vertex.file_watch is False
        assert fragment.file_watch is True
        assert len(vertex.sources) > 0
        assert len(fragment.sources) == 0
