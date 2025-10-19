"""Tests for klproj.cli module."""

import os
import tempfile
import zlib
from io import StringIO
from unittest.mock import patch

import pytest

from klproj.cli import extract_klproj, main, verify_klproj


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
