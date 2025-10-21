"""
Tests for Metal shader generation helpers.
"""

from klproj import (
    Parameter,
    ParamType,
    ShaderProfile,
    create_metal_fragment_source_shadertoy,
    create_metal_vertex_source,
    create_mvp_param,
    create_shadertoy_params,
    generate_metal_compute_shader,
    generate_metal_fragment_shader_shadertoy,
    generate_metal_vertex_shader,
)


class TestMetalVertexShader:
    """Test Metal vertex shader generation."""

    def test_generate_basic_vertex_shader(self):
        """Test generating a basic Metal vertex shader."""
        params = [create_mvp_param()]
        shader_code = generate_metal_vertex_shader(params)

        # Check for Metal header
        assert "#include <metal_stdlib>" in shader_code
        assert "using namespace metal;" in shader_code

        # Check for vertex function
        assert "vertex" in shader_code
        assert "VS_OUTPUT vs_main(" in shader_code

        # Check for input/output structs
        assert "struct VS_INPUT" in shader_code
        assert "struct VS_OUTPUT" in shader_code
        assert "struct VS_UNIFORM" in shader_code

        # Check for attribute bindings
        assert "[[attribute(0)]]" in shader_code
        assert "[[attribute(1)]]" in shader_code
        assert "[[attribute(2)]]" in shader_code

        # Check for buffer binding
        assert "[[buffer(16)]]" in shader_code

        # Check for MVP matrix
        assert "float4x4 mvp;" in shader_code
        assert "u.mvp * input.a_position" in shader_code

    def test_generate_vertex_shader_with_shadertoy_params(self):
        """Test generating vertex shader with Shadertoy parameters."""
        params = create_shadertoy_params() + [create_mvp_param()]
        shader_code = generate_metal_vertex_shader(params, include_shadertoy_compat=True)

        # Check for Shadertoy uniforms
        assert "float2 iResolution;" in shader_code
        assert "float iTime;" in shader_code
        assert "float iTimeDelta;" in shader_code
        assert "int iFrame;" in shader_code
        assert "float4 iMouse;" in shader_code
        assert "float4 iDate;" in shader_code
        assert "float iSampleRate;" in shader_code

    def test_create_metal_vertex_source(self):
        """Test creating ShaderSource for Metal vertex shader."""
        params = [create_mvp_param()]
        source = create_metal_vertex_source(params)

        assert source.profile == ShaderProfile.MTL
        assert "#include <metal_stdlib>" in source.code
        assert "vertex" in source.code


class TestMetalFragmentShader:
    """Test Metal fragment shader generation."""

    def test_generate_basic_fragment_shader(self):
        """Test generating a basic Metal fragment shader."""
        params = create_shadertoy_params()
        shader_code = generate_metal_fragment_shader_shadertoy(params)

        # Check for Metal header
        assert "#include <metal_stdlib>" in shader_code
        assert "using namespace metal;" in shader_code

        # Check for fragment function
        assert "fragment" in shader_code
        assert "float4 fs_main(" in shader_code

        # Check for input/uniform structs
        assert "struct FS_INPUT" in shader_code
        assert "struct FS_UNIFORM" in shader_code

        # Check for mainImage function
        assert "void mainImage(" in shader_code
        assert "thread float4&" in shader_code

        # Check for Shadertoy uniforms
        assert "float2 iResolution;" in shader_code
        assert "float iTime;" in shader_code

    def test_generate_fragment_shader_with_textures(self):
        """Test generating fragment shader with texture parameters."""
        params = create_shadertoy_params()
        texture_params = [
            Parameter(
                param_type=ParamType.CONSTANT_TEXTURE_2D,
                display_name="Texture",
                variable_name="iChannel0",
            ),
            Parameter(
                param_type=ParamType.CONSTANT_TEXTURE_2D,
                display_name="Texture",
                variable_name="iChannel1",
            ),
        ]

        shader_code = generate_metal_fragment_shader_shadertoy(params, texture_params)

        # Check for texture declarations
        assert "texture2d<float> iChannel0 [[texture(0)]]" in shader_code
        assert "texture2d<float> iChannel1 [[texture(1)]]" in shader_code

        # Check textures are passed to mainImage
        assert "texture2d<float> iChannel0" in shader_code
        assert "texture2d<float> iChannel1" in shader_code

    def test_create_metal_fragment_source(self):
        """Test creating ShaderSource for Metal fragment shader."""
        params = create_shadertoy_params()
        source = create_metal_fragment_source_shadertoy(params)

        assert source.profile == ShaderProfile.MTL
        assert "#include <metal_stdlib>" in source.code
        assert "fragment" in source.code


class TestMetalComputeShader:
    """Test Metal compute shader generation."""

    def test_generate_basic_compute_shader(self):
        """Test generating a basic Metal compute shader."""
        params = [
            Parameter(
                param_type=ParamType.CLOCK,
                display_name="Time",
                variable_name="time",
            ),
            Parameter(
                param_type=ParamType.FRAME_RESOLUTION,
                display_name="Resolution",
                variable_name="resolution",
            ),
        ]

        shader_code = generate_metal_compute_shader(params)

        # Check for Metal header
        assert "#include <metal_stdlib>" in shader_code
        assert "#include <simd/simd.h>" in shader_code
        assert "using namespace metal;" in shader_code

        # Check for kernel function
        assert "kernel void cs_main(" in shader_code

        # Check for uniform struct
        assert "struct CS_UNIFORM" in shader_code
        assert "float time;" in shader_code
        assert "float2 resolution;" in shader_code

        # Check for thread position
        assert "[[thread_position_in_grid]]" in shader_code

    def test_generate_compute_shader_with_output_textures(self):
        """Test generating compute shader with output textures."""
        params = [
            Parameter(
                param_type=ParamType.CLOCK,
                display_name="Time",
                variable_name="time",
            ),
        ]

        output_textures = [("outputTexture", 0), ("secondOutput", 1)]

        shader_code = generate_metal_compute_shader(params, output_textures)

        # Check for texture output parameters
        assert "texture2d<float, access::write> outputTexture [[texture(0)]]" in shader_code
        assert "texture2d<float, access::write> secondOutput [[texture(1)]]" in shader_code

    def test_generate_compute_shader_custom_threads(self):
        """Test generating compute shader with custom thread group size."""
        params = []
        threads = (16, 16, 1)

        shader_code = generate_metal_compute_shader(params, threads_per_group=threads)

        # Shader should still be valid
        assert "kernel void cs_main(" in shader_code
        assert "[[thread_position_in_grid]]" in shader_code


class TestMetalTypeMapping:
    """Test Metal type mapping from KodeLife parameter types."""

    def test_all_supported_types_generate_code(self):
        """Test that all supported parameter types generate valid Metal code."""
        test_params = [
            Parameter(ParamType.CLOCK, "Time", "time"),
            Parameter(ParamType.FRAME_RESOLUTION, "Resolution", "resolution"),
            Parameter(ParamType.FRAME_DELTA, "Delta", "delta"),
            Parameter(ParamType.FRAME_NUMBER, "Frame", "frame"),
            Parameter(ParamType.INPUT_MOUSE_SIMPLE, "Mouse", "mouse"),
            Parameter(ParamType.DATE, "Date", "date"),
            Parameter(ParamType.AUDIO_SAMPLE_RATE, "Sample Rate", "sampleRate"),
            Parameter(ParamType.AUDIO_SPECTRUM_SPLIT, "Spectrum", "spectrum"),
            Parameter(ParamType.AUDIO_SPECTRUM_FULL, "Spectrum Full", "spectrumFull"),
            Parameter(ParamType.TRANSFORM_MVP, "MVP", "mvp"),
            Parameter(ParamType.CONSTANT_FLOAT1, "Float", "myFloat"),
            Parameter(ParamType.CONSTANT_FLOAT2, "Float2", "myFloat2"),
            Parameter(ParamType.CONSTANT_FLOAT3, "Float3", "myFloat3"),
            Parameter(ParamType.CONSTANT_FLOAT4, "Float4", "myFloat4"),
        ]

        shader_code = generate_metal_vertex_shader(test_params)

        # Check that all types are represented in the uniform struct
        assert "float time;" in shader_code
        assert "float2 resolution;" in shader_code
        assert "float delta;" in shader_code
        assert "int frame;" in shader_code
        assert "float4 mouse;" in shader_code
        assert "float4 date;" in shader_code
        assert "float sampleRate;" in shader_code
        assert "float3 spectrum;" in shader_code
        assert "float spectrumFull;" in shader_code
        assert "float4x4 mvp;" in shader_code
        assert "float myFloat;" in shader_code
        assert "float2 myFloat2;" in shader_code
        assert "float3 myFloat3;" in shader_code
        assert "float4 myFloat4;" in shader_code


class TestMetalShaderIntegration:
    """Test integration of Metal shader generation with full projects."""

    def test_complete_metal_shader_pair(self):
        """Test generating a complete vertex + fragment shader pair."""
        global_params = create_shadertoy_params()
        mvp_param = create_mvp_param()

        vertex_source = create_metal_vertex_source(global_params + [mvp_param])
        fragment_source = create_metal_fragment_source_shadertoy(global_params)

        # Both shaders should be valid Metal code
        assert vertex_source.profile == ShaderProfile.MTL
        assert fragment_source.profile == ShaderProfile.MTL

        # Vertex shader should reference MVP
        assert "u.mvp" in vertex_source.code

        # Fragment shader should reference time
        assert "iTime" in fragment_source.code

        # Both should use Metal syntax
        assert "#include <metal_stdlib>" in vertex_source.code
        assert "#include <metal_stdlib>" in fragment_source.code
