"""
Command-line interface for klproj tools.

This module provides CLI commands for working with .klproj files:
- extract: Decompress .klproj to XML
- verify: Display .klproj contents
- convert: Convert ISF shaders to .klproj format
  - Accepts individual ISF files or JSON files from find_shaders.py
  - JSON format: {"multipass": [...], "single_pass": [...]}
- create: Create .klproj with file watching for external shader files
"""

import argparse
import json
import sys
import zlib
from pathlib import Path

from .generator import KodeProjBuilder
from .helpers import (
    create_default_vertex_stage,
    create_fragment_file_watch_stage,
    create_shadertoy_params,
    create_vertex_file_watch_stage,
)
from .isf_converter import convert_isf_to_kodelife
from .types import PassType, RenderPass, ShaderProfile


def extract_klproj(input_path: str, output_path: str) -> int:
    """
    Extract and decompress a .klproj file to XML format.

    Args:
        input_path: Path to .klproj file
        output_path: Path for output XML file

    Returns:
        0 on success, 1 on error
    """
    try:
        with open(input_path, "rb") as f:
            compressed = f.read()
            decompressed = zlib.decompress(compressed)

        with open(output_path, "wb") as f:
            f.write(decompressed)

        print(f"Extracted: {input_path} -> {output_path} ({len(decompressed)} bytes)")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def verify_klproj(filename: str) -> int:
    """
    Verify and display the contents of a .klproj file.

    Args:
        filename: Path to .klproj file

    Returns:
        0 on success, 1 on error
    """
    try:
        with open(filename, "rb") as f:
            compressed = f.read()
            xml_data = zlib.decompress(compressed)
            print(xml_data.decode("utf-8"))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def load_paths_from_json(json_path: str) -> list:
    """
    Load ISF shader paths from a JSON file created by find_shaders.py.

    Args:
        json_path: Path to JSON file

    Returns:
        List of ISF file paths (strings)
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    paths = []

    # Extract multipass shader paths
    if "multipass" in data:
        for shader in data["multipass"]:
            if isinstance(shader, dict) and "path" in shader:
                paths.append(shader["path"])
            elif isinstance(shader, str):
                paths.append(shader)

    # Extract single-pass shader paths
    if "single_pass" in data:
        for path in data["single_pass"]:
            if isinstance(path, str):
                paths.append(path)

    return paths


def convert_isf(
    input_files: list,
    output_dir: str = None,
    width: int = 1920,
    height: int = 1080,
    api: str = "GL3",
) -> int:
    """
    Convert ISF file(s) to .klproj format.

    Args:
        input_files: List of ISF file paths or JSON files from find_shaders.py
        output_dir: Optional output directory (default: same as input)
        width: Project width in pixels
        height: Project height in pixels
        api: Graphics API to use (GL3, GL2)

    Returns:
        0 on success, 1 on error
    """
    success_count = 0
    error_count = 0

    # Expand JSON files into ISF paths
    expanded_files = []
    for input_file in input_files:
        if input_file.endswith(".json"):
            try:
                json_paths = load_paths_from_json(input_file)
                print(f"Loaded {len(json_paths)} shader paths from {input_file}")
                expanded_files.extend(json_paths)
            except Exception as e:
                print(f"✗ Error loading JSON file {input_file}: {e}", file=sys.stderr)
                error_count += 1
        else:
            expanded_files.append(input_file)

    for input_file in expanded_files:
        try:
            # Determine output path
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                base_name = Path(input_file).stem
                output_path = str(Path(output_dir) / f"{base_name}.klproj")
            else:
                output_path = None  # Let converter use default

            # Convert the file
            result_path = convert_isf_to_kodelife(
                isf_file_path=input_file,
                output_path=output_path,
                api=api,
                width=width,
                height=height,
            )

            print(f"✓ Converted: {input_file} -> {result_path}")
            success_count += 1

        except Exception as e:
            print(f"✗ Error converting {input_file}: {e}", file=sys.stderr)
            error_count += 1

    # Print summary if multiple files
    if len(expanded_files) > 1:
        print(f"\nSummary: {success_count} succeeded, {error_count} failed")

    return 0 if error_count == 0 else 1


def create_watch_project(
    fragment_shader: str,
    vertex_shader: str = None,
    output_path: str = None,
    width: int = 1920,
    height: int = 1080,
    api: str = "GL3",
) -> int:
    """
    Create a .klproj that watches external shader files.

    This creates a KodeLife project configured to watch and reload shader
    files from disk. This enables using external IDEs and allows coding
    agents to iterate quickly.

    Args:
        fragment_shader: Path to fragment shader file (.fs)
        vertex_shader: Optional path to vertex shader file (.vs)
        output_path: Output .klproj path (default: based on fragment shader name)
        width: Project width in pixels
        height: Project height in pixels
        api: Graphics API to use (GL3, GL2, MTL)

    Returns:
        0 on success, 1 on error
    """
    try:
        # Convert paths to absolute paths
        fragment_path = str(Path(fragment_shader).resolve())

        # Determine output path
        if not output_path:
            base_name = Path(fragment_shader).stem
            output_path = f"{base_name}_watch.klproj"

        # Ensure output directory exists
        output_dir = Path(output_path).parent
        if output_dir != Path("."):
            output_dir.mkdir(parents=True, exist_ok=True)

        # Create builder
        profile = ShaderProfile[api] if hasattr(ShaderProfile, api) else ShaderProfile.GL3
        builder = KodeProjBuilder(api=api)
        builder.set_resolution(width, height)
        builder.set_author("klproj-generator")
        builder.set_comment(f"File-watching project for {Path(fragment_shader).name}")

        # Add standard parameters
        for param in create_shadertoy_params():
            builder.add_global_param(param)

        # Create vertex stage
        if vertex_shader:
            vertex_path = str(Path(vertex_shader).resolve())
            vertex_stage = create_vertex_file_watch_stage(vertex_path)
        else:
            # Use default embedded vertex shader
            vertex_stage = create_default_vertex_stage(profile)

        # Create fragment stage with file watching
        fragment_stage = create_fragment_file_watch_stage(fragment_path)

        # Create render pass
        render_pass = RenderPass(
            pass_type=PassType.RENDER,
            label="Main Pass",
            enabled=1,
            stages=[vertex_stage, fragment_stage],
            width=width,
            height=height,
        )

        builder.add_pass(render_pass)
        builder.save(output_path)

        print(f"✓ Created file-watching project: {output_path}")
        print(f"  Fragment shader: {fragment_path}")
        if vertex_shader:
            print(f"  Vertex shader: {vertex_path}")
        else:
            print("  Vertex shader: (embedded default)")
        return 0

    except Exception as e:
        print(f"✗ Error creating project: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="KodeLife .klproj file utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract .klproj to XML")
    extract_parser.add_argument("input", help="Input .klproj file")
    extract_parser.add_argument("output", help="Output XML file")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify and display .klproj contents")
    verify_parser.add_argument("input", help="Input .klproj file")

    # Convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert ISF file(s) to .klproj format",
        description="Convert ISF shader files or JSON file lists to .klproj format",
    )
    convert_parser.add_argument(
        "inputs", nargs="+", help="Input ISF file(s) or JSON file from find_shaders.py"
    )
    convert_parser.add_argument(
        "-o", "--output-dir", help="Output directory (default: same as input file)"
    )
    convert_parser.add_argument(
        "-w", "--width", type=int, default=1920, help="Project width in pixels (default: 1920)"
    )
    convert_parser.add_argument(
        "--height", type=int, default=1080, help="Project height in pixels (default: 1080)"
    )
    convert_parser.add_argument(
        "-a", "--api", choices=["GL2", "GL3"], default="GL3", help="Graphics API (default: GL3)"
    )

    # Create command (file watching)
    create_parser = subparsers.add_parser(
        "create",
        help="Create .klproj with file watching for external shaders",
        description="Create a KodeLife project that watches external shader files for live reloading",
    )
    create_parser.add_argument("fragment", help="Fragment shader file (.fs) to watch")
    create_parser.add_argument(
        "-v",
        "--vertex",
        help="Vertex shader file (.vs) to watch (optional, default embedded shader used)",
    )
    create_parser.add_argument(
        "-o", "--output", help="Output .klproj path (default: <fragment_name>_watch.klproj)"
    )
    create_parser.add_argument(
        "-w", "--width", type=int, default=1920, help="Project width in pixels (default: 1920)"
    )
    create_parser.add_argument(
        "--height", type=int, default=1080, help="Project height in pixels (default: 1080)"
    )
    create_parser.add_argument(
        "-a",
        "--api",
        choices=["GL2", "GL3", "MTL"],
        default="GL3",
        help="Graphics API (default: GL3)",
    )

    args = parser.parse_args()

    if args.command == "extract":
        return extract_klproj(args.input, args.output)
    elif args.command == "verify":
        return verify_klproj(args.input)
    elif args.command == "convert":
        return convert_isf(
            input_files=args.inputs,
            output_dir=args.output_dir,
            width=args.width,
            height=args.height,
            api=args.api,
        )
    elif args.command == "create":
        return create_watch_project(
            fragment_shader=args.fragment,
            vertex_shader=args.vertex,
            output_path=args.output,
            width=args.width,
            height=args.height,
            api=args.api,
        )
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
