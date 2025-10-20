#!/usr/bin/env python3
"""
Batch ISF conversion tool with flexible selection strategies.

Consolidates functionality from:
  - convert_random_isf.py
  - convert_random_batch.py
  - convert_batch_with_multipass.py
  - convert_diverse_batch.py
  - convert_all_multipass.py

Usage examples:
  # Convert 30 random ISF files (default)
  uv run python tools/batch_convert.py

  # Convert 50 random files
  uv run python tools/batch_convert.py --random 50

  # Convert only multipass shaders
  uv run python tools/batch_convert.py --multipass-only

  # Convert mix of 10 multipass + 5 single-pass
  uv run python tools/batch_convert.py --mixed 10 5

  # Convert all discovered ISF files
  uv run python tools/batch_convert.py --all

  # Custom output directory and resolution
  uv run python tools/batch_convert.py --random 20 -o output/ -w 1280 --height 720

  # Use GL2 API instead of default GL3
  uv run python tools/batch_convert.py --random 10 -a GL2

  # Quiet mode (only show summary)
  uv run python tools/batch_convert.py --random 10 --quiet

  # Verbose mode (show all details)
  uv run python tools/batch_convert.py --random 10 --verbose
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from klproj.utils.isf_discovery import ISFDiscovery
from klproj.utils.batch_processor import BatchConverter
from klproj.utils.reporter import ConversionReporter


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Batch convert ISF files to .klproj format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # ISF source directories
    parser.add_argument(
        '-d', '--isf-dir',
        action='append',
        dest='isf_dirs',
        help='ISF source directory (can be specified multiple times). '
             'Default: /Users/andre/Library/Graphics/ISF'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default='./isf_conversions',
        help='Output directory for .klproj files (default: ./isf_conversions)'
    )

    # Selection strategies (mutually exclusive)
    strategy = parser.add_mutually_exclusive_group()

    strategy.add_argument(
        '--random',
        type=int,
        metavar='N',
        help='Convert N randomly selected files'
    )

    strategy.add_argument(
        '--multipass-only',
        action='store_true',
        help='Convert only multipass shaders (ignores single-pass)'
    )

    strategy.add_argument(
        '--single-only',
        action='store_true',
        help='Convert only single-pass shaders (ignores multipass)'
    )

    strategy.add_argument(
        '--mixed',
        nargs=2,
        type=int,
        metavar=('MULTI', 'SINGLE'),
        help='Convert M multipass + N single-pass files (shuffled)'
    )

    strategy.add_argument(
        '--all',
        action='store_true',
        help='Convert all discovered ISF files (use with caution!)'
    )

    # Conversion options
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=1920,
        help='Project width in pixels (default: 1920)'
    )

    parser.add_argument(
        '--height',
        type=int,
        default=1080,
        help='Project height in pixels (default: 1080)'
    )

    parser.add_argument(
        '-a', '--api',
        choices=['GL2', 'GL3', 'MTL', 'ES3'],
        default='GL3',
        help='Graphics API profile (default: GL3)'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing .klproj files'
    )

    # Output options
    parser.add_argument(
        '--save-results',
        metavar='FILE',
        default='conversion_results.json',
        help='Save conversion results to JSON file (default: conversion_results.json)'
    )

    parser.add_argument(
        '--no-save-results',
        action='store_true',
        help='Do not save results to JSON file'
    )

    parser.add_argument(
        '--save-discovery',
        metavar='FILE',
        help='Save ISF discovery results to JSON file'
    )

    # Reporting options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output (only show summary)'
    )

    return parser.parse_args()


def main():
    """Main entry point for batch conversion tool."""
    args = parse_args()

    # Create reporter
    reporter = ConversionReporter(verbose=args.verbose, quiet=args.quiet)

    reporter.print_header("ISF BATCH CONVERSION TOOL", width=80)

    # Setup ISF discovery
    isf_dirs = args.isf_dirs if args.isf_dirs else None
    discovery = ISFDiscovery(base_dirs=isf_dirs)

    # Scan for ISF files
    reporter.print_info("\nScanning for ISF files...")
    multipass, single_pass = discovery.scan()

    reporter.report_discovery(len(multipass), len(single_pass))

    if len(multipass) + len(single_pass) == 0:
        reporter.print_error("No ISF files found!")
        return 1

    # Save discovery results if requested
    if args.save_discovery:
        discovery.save_to_json(args.save_discovery)
        reporter.print_info(f"Discovery results saved to: {args.save_discovery}")

    # Select files based on strategy
    selected = []
    strategy_desc = ""

    if args.random:
        all_files = multipass + single_pass
        selected = discovery.select_random(args.random, all_files)
        strategy_desc = f"Random selection ({args.random} files)"

    elif args.multipass_only:
        selected = multipass
        strategy_desc = "Multipass shaders only"

    elif args.single_only:
        selected = single_pass
        strategy_desc = "Single-pass shaders only"

    elif args.mixed:
        num_multi, num_single = args.mixed
        selected = discovery.select_mixed(num_multi, num_single)
        strategy_desc = f"Mixed selection ({num_multi} multipass + {num_single} single-pass)"

    elif args.all:
        selected = multipass + single_pass
        strategy_desc = "All discovered files"

    else:
        # Default: 30 random files
        all_files = multipass + single_pass
        selected = discovery.select_random(30, all_files)
        strategy_desc = "Default random selection (30 files)"

    if len(selected) == 0:
        reporter.print_warning("No files selected for conversion")
        return 0

    reporter.report_selection(selected, strategy_desc)

    # Setup batch converter
    converter = BatchConverter(
        output_dir=args.output_dir,
        api=args.api,
        width=args.width,
        height=args.height,
        overwrite=args.overwrite
    )

    # Convert batch
    reporter.print_section("CONVERTING FILES", width=80)

    result = converter.convert_batch(
        files=selected,
        reporter=reporter.report_progress
    )

    # Report success/errors for each file
    for output_path in result.successful:
        if output_path.exists():
            reporter.report_file_success(output_path)

    for input_path, error in result.failed:
        reporter.report_file_error(f"{input_path.name}: {error}")

    # Save results if requested
    if not args.no_save_results and args.save_results:
        result.save_json(args.save_results)
        reporter.print_info(f"\n💾 Conversion results saved to: {args.save_results}")

    # Get output statistics
    stats = converter.get_stats()

    # Print summary
    reporter.print_summary(result, stats)

    # Return exit code based on results
    return 0 if result.success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
