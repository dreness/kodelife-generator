"""Tests for klproj.cli module."""

import json
import os
import tempfile
import zlib
from io import StringIO
from unittest.mock import patch

import pytest

from klproj.cli import extract_klproj, load_paths_from_json, main, verify_klproj


class TestExtractKlproj:
    """Test extract_klproj function."""

    def test_extract_valid_file(self):
        """Test extracting a valid .klproj file."""
        # Create a test XML content
        xml_content = '<?xml version="1.0"?><klxml><test>data</test></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input file
            input_path = os.path.join(tmpdir, "test.klproj")
            with open(input_path, "wb") as f:
                f.write(compressed)

            # Extract to output file
            output_path = os.path.join(tmpdir, "output.xml")
            result = extract_klproj(input_path, output_path)

            # Verify success
            assert result == 0
            assert os.path.exists(output_path)

            # Verify content
            with open(output_path, "rb") as f:
                extracted = f.read()
            assert extracted == xml_bytes

    def test_extract_nonexistent_file(self):
        """Test extracting a file that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "nonexistent.klproj")
            output_path = os.path.join(tmpdir, "output.xml")

            result = extract_klproj(input_path, output_path)
            assert result == 1

    def test_extract_invalid_compressed_data(self):
        """Test extracting a file with invalid compressed data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with invalid data
            input_path = os.path.join(tmpdir, "invalid.klproj")
            with open(input_path, "wb") as f:
                f.write(b"not valid compressed data")

            output_path = os.path.join(tmpdir, "output.xml")
            result = extract_klproj(input_path, output_path)
            assert result == 1

    def test_extract_creates_output_directory(self):
        """Test that extract can create output directories if needed."""
        xml_content = '<?xml version="1.0"?><klxml><test>data</test></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input file
            input_path = os.path.join(tmpdir, "test.klproj")
            with open(input_path, "wb") as f:
                f.write(compressed)

            # Extract to nested output path
            output_path = os.path.join(tmpdir, "subdir", "output.xml")
            # Create the directory first (as extract doesn't create dirs)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            result = extract_klproj(input_path, output_path)
            assert result == 0
            assert os.path.exists(output_path)


class TestVerifyKlproj:
    """Test verify_klproj function."""

    def test_verify_valid_file(self):
        """Test verifying a valid .klproj file."""
        xml_content = '<?xml version="1.0"?><klxml><test>data</test></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.klproj")
            with open(filepath, "wb") as f:
                f.write(compressed)

            # Capture stdout
            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                result = verify_klproj(filepath)

            assert result == 0
            assert xml_content in captured_output.getvalue()

    def test_verify_nonexistent_file(self):
        """Test verifying a file that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "nonexistent.klproj")
            result = verify_klproj(filepath)
            assert result == 1

    def test_verify_invalid_compressed_data(self):
        """Test verifying a file with invalid compressed data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "invalid.klproj")
            with open(filepath, "wb") as f:
                f.write(b"not valid compressed data")

            result = verify_klproj(filepath)
            assert result == 1

    def test_verify_prints_xml_content(self):
        """Test that verify prints the decompressed XML content."""
        xml_content = '<?xml version="1.0"?><klxml v="19"><document></document></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.klproj")
            with open(filepath, "wb") as f:
                f.write(compressed)

            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                result = verify_klproj(filepath)

            output = captured_output.getvalue()
            assert result == 0
            assert "klxml" in output
            assert "document" in output


class TestMainCLI:
    """Test main CLI entry point."""

    def test_main_no_arguments(self):
        """Test main with no arguments."""
        with patch("sys.argv", ["klproj"]):
            result = main()
            assert result == 1

    def test_main_extract_command(self):
        """Test main with extract command."""
        xml_content = '<?xml version="1.0"?><klxml><test>data</test></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "test.klproj")
            output_path = os.path.join(tmpdir, "output.xml")

            with open(input_path, "wb") as f:
                f.write(compressed)

            with patch("sys.argv", ["klproj", "extract", input_path, output_path]):
                result = main()

            assert result == 0
            assert os.path.exists(output_path)

    def test_main_verify_command(self):
        """Test main with verify command."""
        xml_content = '<?xml version="1.0"?><klxml><test>data</test></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.klproj")
            with open(filepath, "wb") as f:
                f.write(compressed)

            captured_output = StringIO()
            with patch("sys.argv", ["klproj", "verify", filepath]):
                with patch("sys.stdout", captured_output):
                    result = main()

            assert result == 0
            assert xml_content in captured_output.getvalue()

    def test_main_invalid_command(self):
        """Test main with an invalid command."""
        with patch("sys.argv", ["klproj", "invalid"]):
            # argparse raises SystemExit for invalid commands
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2  # argparse uses exit code 2 for errors

    def test_main_extract_missing_arguments(self):
        """Test main extract with missing arguments."""
        with patch("sys.argv", ["klproj", "extract", "input.klproj"]):
            with pytest.raises(SystemExit):
                main()

    def test_main_verify_missing_arguments(self):
        """Test main verify with missing arguments."""
        with patch("sys.argv", ["klproj", "verify"]):
            with pytest.raises(SystemExit):
                main()


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_extract_and_verify_workflow(self):
        """Test a complete extract and verify workflow."""
        # Create a test .klproj file
        xml_content = '<?xml version="1.0"?><klxml v="19" a="GL3"><document></document></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            klproj_path = os.path.join(tmpdir, "test.klproj")
            xml_path = os.path.join(tmpdir, "extracted.xml")

            # Create .klproj file
            with open(klproj_path, "wb") as f:
                f.write(compressed)

            # Extract it
            with patch("sys.argv", ["klproj", "extract", klproj_path, xml_path]):
                result = main()
            assert result == 0
            assert os.path.exists(xml_path)

            # Verify the original
            captured_output = StringIO()
            with patch("sys.argv", ["klproj", "verify", klproj_path]):
                with patch("sys.stdout", captured_output):
                    result = main()
            assert result == 0
            assert "GL3" in captured_output.getvalue()

    def test_cli_with_real_project_file(self):
        """Test CLI with a realistic project file structure."""
        from klproj import KodeProjBuilder, Parameter, ParamType

        # Create a real project
        builder = KodeProjBuilder(api="GL3")
        builder.set_resolution(1280, 720)
        builder.set_author("Test CLI")
        builder.add_global_param(
            Parameter(ParamType.CLOCK, "Time", "time", properties={"running": 1})
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            klproj_path = os.path.join(tmpdir, "test.klproj")
            xml_path = os.path.join(tmpdir, "extracted.xml")

            # Save project
            builder.save(klproj_path)

            # Extract using CLI
            with patch("sys.argv", ["klproj", "extract", klproj_path, xml_path]):
                result = main()
            assert result == 0

            # Verify content
            with open(xml_path, "rb") as f:
                content = f.read().decode("utf-8")
            assert "GL3" in content
            assert "Test CLI" in content
            assert "time" in content

    def test_error_handling_with_permission_denied(self):
        """Test error handling when file permissions are denied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # This test is platform-dependent and might not work on all systems
            # On Windows, permission handling is different
            if os.name == "posix":  # Unix-like systems
                input_path = os.path.join(tmpdir, "test.klproj")
                output_path = os.path.join(tmpdir, "output.xml")

                # Create a file with some content
                xml_content = '<?xml version="1.0"?><test/>'
                compressed = zlib.compress(xml_content.encode("utf-8"))
                with open(input_path, "wb") as f:
                    f.write(compressed)

                # Make output directory read-only
                readonly_dir = os.path.join(tmpdir, "readonly")
                os.makedirs(readonly_dir, mode=0o444)
                output_path = os.path.join(readonly_dir, "output.xml")

                try:
                    result = extract_klproj(input_path, output_path)
                    # Should fail due to permissions
                    assert result == 1
                finally:
                    # Restore permissions for cleanup
                    os.chmod(readonly_dir, 0o755)


class TestCLIHelpers:
    """Test CLI helper functionality."""

    def test_extract_preserves_encoding(self):
        """Test that extract preserves UTF-8 encoding."""
        # Create XML with special characters
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><klxml><author>Test™</author></klxml>'
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "test.klproj")
            output_path = os.path.join(tmpdir, "output.xml")

            with open(input_path, "wb") as f:
                f.write(compressed)

            result = extract_klproj(input_path, output_path)
            assert result == 0

            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "™" in content

    def test_verify_handles_large_files(self):
        """Test that verify can handle larger files."""
        # Create a larger XML structure
        xml_content = '<?xml version="1.0"?><klxml>'
        xml_content += "<data>" + "x" * 10000 + "</data>" * 100
        xml_content += "</klxml>"
        xml_bytes = xml_content.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "large.klproj")
            with open(filepath, "wb") as f:
                f.write(compressed)

            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                result = verify_klproj(filepath)

            assert result == 0
            output = captured_output.getvalue()
            assert len(output) > 10000  # Should have decompressed the large content


class TestLoadPathsFromJSON:
    """Test load_paths_from_json function."""

    def test_load_multipass_shaders(self):
        """Test loading multipass shader paths from JSON."""
        test_data = {
            "multipass": [
                {"path": "/path/to/shader1.fs"},
                {"path": "/path/to/shader2.fs"},
            ],
            "single_pass": [],
            "summary": {"total": 2},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "test.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            paths = load_paths_from_json(json_path)
            assert len(paths) == 2
            assert "/path/to/shader1.fs" in paths
            assert "/path/to/shader2.fs" in paths

    def test_load_single_pass_shaders(self):
        """Test loading single-pass shader paths from JSON."""
        test_data = {
            "multipass": [],
            "single_pass": ["/path/to/shader3.fs", "/path/to/shader4.fs"],
            "summary": {"total": 2},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "test.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            paths = load_paths_from_json(json_path)
            assert len(paths) == 2
            assert "/path/to/shader3.fs" in paths
            assert "/path/to/shader4.fs" in paths

    def test_load_mixed_shaders(self):
        """Test loading both multipass and single-pass shaders."""
        test_data = {
            "multipass": [
                {"path": "/path/to/multi1.fs"},
                {"path": "/path/to/multi2.fs"},
            ],
            "single_pass": ["/path/to/single1.fs", "/path/to/single2.fs"],
            "summary": {"total": 4},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "test.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            paths = load_paths_from_json(json_path)
            assert len(paths) == 4
            assert "/path/to/multi1.fs" in paths
            assert "/path/to/single1.fs" in paths

    def test_load_empty_json(self):
        """Test loading JSON with no shaders."""
        test_data = {"multipass": [], "single_pass": [], "summary": {"total": 0}}

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "test.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            paths = load_paths_from_json(json_path)
            assert len(paths) == 0

    def test_load_json_with_missing_keys(self):
        """Test loading JSON with missing keys."""
        test_data = {"summary": {"total": 0}}

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "test.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            paths = load_paths_from_json(json_path)
            assert len(paths) == 0

    def test_load_json_backwards_compatible_format(self):
        """Test loading JSON with path strings in multipass (backward compatibility)."""
        test_data = {
            "multipass": ["/path/to/shader1.fs", "/path/to/shader2.fs"],
            "single_pass": ["/path/to/shader3.fs"],
            "summary": {"total": 3},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "test.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            paths = load_paths_from_json(json_path)
            assert len(paths) == 3
            assert "/path/to/shader1.fs" in paths
            assert "/path/to/shader2.fs" in paths
            assert "/path/to/shader3.fs" in paths


class TestConvertWithJSON:
    """Test convert command with JSON file input."""

    def test_convert_json_file(self):
        """Test converting ISF shaders from a JSON file."""
        # Create a simple ISF shader
        isf_shader = """/*
{
  "INPUTS": [],
  "ISFVSN": "2"
}
*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""

        test_data = {
            "multipass": [],
            "single_pass": [],
            "summary": {"total": 1},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create an ISF file
            isf_path = os.path.join(tmpdir, "test_shader.fs")
            with open(isf_path, "w") as f:
                f.write(isf_shader)

            # Add it to JSON
            test_data["single_pass"] = [isf_path]

            # Create JSON file
            json_path = os.path.join(tmpdir, "shaders.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            # Output directory
            output_dir = os.path.join(tmpdir, "output")

            # Test using main CLI
            with patch("sys.argv", ["klproj", "convert", json_path, "-o", output_dir]):
                result = main()

            # Verify success
            assert result == 0
            output_file = os.path.join(output_dir, "test_shader.klproj")
            assert os.path.exists(output_file)

    def test_convert_mixed_json_and_direct_files(self):
        """Test converting a mix of JSON file and direct ISF files."""
        isf_shader1 = """/*
{
  "INPUTS": [],
  "ISFVSN": "2"
}
*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""
        isf_shader2 = """/*
{
  "INPUTS": [],
  "ISFVSN": "2"
}
*/
void main() {
    gl_FragColor = vec4(0.0, 1.0, 0.0, 1.0);
}
"""

        test_data = {
            "multipass": [],
            "single_pass": [],
            "summary": {"total": 1},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create ISF files
            isf1_path = os.path.join(tmpdir, "shader1.fs")
            with open(isf1_path, "w") as f:
                f.write(isf_shader1)

            isf2_path = os.path.join(tmpdir, "shader2.fs")
            with open(isf2_path, "w") as f:
                f.write(isf_shader2)

            # JSON with shader1
            test_data["single_pass"] = [isf1_path]
            json_path = os.path.join(tmpdir, "shaders.json")
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            # Output directory
            output_dir = os.path.join(tmpdir, "output")

            # Convert: JSON + direct ISF file
            with patch("sys.argv", ["klproj", "convert", json_path, isf2_path, "-o", output_dir]):
                result = main()

            # Verify both were converted
            assert result == 0
            assert os.path.exists(os.path.join(output_dir, "shader1.klproj"))
            assert os.path.exists(os.path.join(output_dir, "shader2.klproj"))
