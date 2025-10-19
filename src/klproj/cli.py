"""
Command-line interface for klproj tools.

This module provides CLI commands for working with .klproj files.
"""

import argparse
import sys
import zlib


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

    args = parser.parse_args()

    if args.command == "extract":
        return extract_klproj(args.input, args.output)
    elif args.command == "verify":
        return verify_klproj(args.input)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
