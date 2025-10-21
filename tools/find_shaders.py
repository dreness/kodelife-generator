#!/usr/bin/env python3
"""
ISF shader discovery and cataloging tool.

Enhanced version of find_multipass_isf.py with additional features:
  - Detailed ISF metadata extraction
  - Category filtering
  - Multiple output formats
  - Statistics and reporting

Usage examples:
  # Find all ISF shaders in default location
  uv run python tools/find_shaders.py

  # Search specific directories
  uv run python tools/find_shaders.py -d ~/shaders -d ./local_shaders

  # Find only multipass shaders
  uv run python tools/find_shaders.py --multipass-only

  # Find shaders by category
  uv run python tools/find_shaders.py --category "Generator"

  # Save results to custom file
  uv run python tools/find_shaders.py --output shader_catalog.json

  # Verbose output with details
  uv run python tools/find_shaders.py --verbose

  # Show statistics only
  uv run python tools/find_shaders.py --stats-only
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from klproj.utils.isf_discovery import ISFDiscovery


class DiscoveryReporter:
    """Reporter for shader discovery progress and results."""

    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet

    def print_header(self, title: str, width: int = 80):
        """Print a formatted header."""
        if self.quiet:
            return
        print("=" * width)
        print(title)
        print("=" * width)

    def print_section(self, title: str, width: int = 80):
        """Print a section separator."""
        if self.quiet:
            return
        print(f"\n{title}")
        print("-" * width)

    def print_info(self, message: str):
        """Print informational message."""
        if not self.quiet:
            print(message)

    def report_multipass_shader(self, shader):
        """Report details about a multipass shader."""
        if self.quiet or not self.verbose:
            return

        print(f"\n📄 {shader.name}")
        print(f"   Path: {shader.path}")
        if shader.description:
            print(f"   Description: {shader.description}")
        print(f"   Passes: {shader.num_passes}")
        if shader.categories:
            print(f"   Categories: {', '.join(shader.categories)}")
        if shader.inputs:
            input_names = [inp.get("NAME", "unnamed") for inp in shader.inputs]
            print(f"   Inputs: {', '.join(input_names)}")

    def print_statistics(self, multipass, single_pass, categories=None):
        """Print discovery statistics."""
        self.print_section("DISCOVERY STATISTICS", width=80)

        total = len(multipass) + len(single_pass)
        print(f"\nTotal ISF shaders found: {total}")
        print(
            f"  🔄 Multipass: {len(multipass)} ({len(multipass) / max(1, total) * 100:.1f}%)"
        )
        print(
            f"  ⚡ Single-pass: {len(single_pass)} ({len(single_pass) / max(1, total) * 100:.1f}%)"
        )

        if multipass:
            pass_counts = [shader.num_passes for shader in multipass]
            avg_passes = sum(pass_counts) / len(pass_counts)
            max_passes = max(pass_counts)
            print("\nMultipass statistics:")
            print(f"  Average passes: {avg_passes:.1f}")
            print(f"  Maximum passes: {max_passes}")

        if categories:
            print("\nShaders by category:")
            sorted_cats = sorted(categories.items(), key=lambda x: -x[1])
            for category, count in sorted_cats[:10]:
                print(f"  • {category}: {count}")
            if len(categories) > 10:
                print(f"  ... and {len(categories) - 10} more categories")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Discover and catalog ISF shader files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "-d",
        "--isf-dir",
        action="append",
        dest="isf_dirs",
        help="ISF directory to search (can be specified multiple times). "
        "Default: /Users/andre/Library/Graphics/ISF",
    )

    # Filtering options
    parser.add_argument(
        "--multipass-only", action="store_true", help="Only show multipass shaders"
    )

    parser.add_argument(
        "--single-only", action="store_true", help="Only show single-pass shaders"
    )

    parser.add_argument(
        "--category", help="Filter by category (case-insensitive substring match)"
    )

    parser.add_argument(
        "--min-passes",
        type=int,
        metavar="N",
        help="Only show multipass shaders with at least N passes",
    )

    # Output options
    parser.add_argument(
        "-o",
        "--output",
        default="multipass_isf_shaders.json",
        help="Output JSON file (default: multipass_isf_shaders.json)",
    )

    parser.add_argument(
        "--no-save", action="store_true", help="Do not save results to JSON file"
    )

    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show statistics, do not list individual shaders",
    )

    # Reporting options
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed information about each shader",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress output except statistics"
    )

    return parser.parse_args()


def main():
    """Main entry point for shader discovery tool."""
    args = parse_args()

    # Create reporter
    reporter = DiscoveryReporter(verbose=args.verbose, quiet=args.quiet)

    reporter.print_header("ISF SHADER DISCOVERY TOOL", width=80)

    # Setup discovery
    isf_dirs = args.isf_dirs if args.isf_dirs else None
    discovery = ISFDiscovery(base_dirs=isf_dirs)

    # Scan for shaders
    reporter.print_info("\n🔍 Scanning for ISF shaders...")

    multipass, single_pass = discovery.scan()

    if len(multipass) + len(single_pass) == 0:
        print("No ISF shaders found!")
        return 1

    # Apply filters
    filtered_multipass = multipass
    filtered_single = single_pass

    if args.multipass_only:
        filtered_single = []
    elif args.single_only:
        filtered_multipass = []

    if args.category:
        filtered_multipass = discovery.filter_by_category(
            args.category, filtered_multipass
        )
        filtered_single = discovery.filter_by_category(args.category, filtered_single)

    if args.min_passes:
        filtered_multipass = [
            s for s in filtered_multipass if s.num_passes >= args.min_passes
        ]

    # Count shaders by category
    categories = {}
    for shader in multipass + single_pass:
        for cat in shader.categories:
            categories[cat] = categories.get(cat, 0) + 1

    # Show results
    if not args.stats_only:
        if filtered_multipass:
            reporter.print_section(
                f"MULTIPASS SHADERS ({len(filtered_multipass)})", width=80
            )
            for shader in sorted(filtered_multipass, key=lambda s: s.name):
                reporter.report_multipass_shader(shader)

            if not args.verbose and not args.quiet:
                print(f"\nFound {len(filtered_multipass)} multipass shaders")

        if filtered_single and not args.multipass_only:
            if not args.verbose and not args.quiet:
                reporter.print_section(
                    f"SINGLE-PASS SHADERS ({len(filtered_single)})", width=80
                )
                print(f"\nFound {len(filtered_single)} single-pass shaders")
                if len(filtered_single) <= 20:
                    for shader in sorted(filtered_single, key=lambda s: s.name)[:20]:
                        print(f"  • {shader.name}")
                else:
                    for shader in sorted(filtered_single, key=lambda s: s.name)[:10]:
                        print(f"  • {shader.name}")
                    print(f"  ... and {len(filtered_single) - 10} more")

    # Save results
    if not args.no_save and args.output:
        discovery.save_to_json(args.output)
        reporter.print_info(f"\n💾 Results saved to: {args.output}")

    # Print statistics
    reporter.print_statistics(multipass, single_pass, categories)

    return 0


if __name__ == "__main__":
    sys.exit(main())
