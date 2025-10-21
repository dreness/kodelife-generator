#!/usr/bin/env python3
"""
Batch analysis tool for .klproj files.

Consolidates functionality from:
  - analyze_converted.py
  - analyze_converted_batch.py
  - analyze_undefined_vars.py

Analyzes converted .klproj files for structural issues, missing uniforms,
undefined variables, and other shader problems.

Usage examples:
  # Analyze all files with default checks (structure + uniforms)
  uv run python tools/analyze_batch.py isf_conversions/

  # Run all available checks
  uv run python tools/analyze_batch.py isf_conversions/ --all-checks

  # Run specific checks
  uv run python tools/analyze_batch.py isf_conversions/ --check-uniforms --check-undefined

  # Save results to custom file
  uv run python tools/analyze_batch.py isf_conversions/ --save-results my_analysis.json

  # Deep analysis with original ISF files for context
  uv run python tools/analyze_batch.py isf_conversions/ --check-undefined \\
      --isf-source ~/Library/Graphics/ISF

  # Verbose output
  uv run python tools/analyze_batch.py isf_conversions/ --verbose

  # Quiet mode (only summary)
  uv run python tools/analyze_batch.py isf_conversions/ --quiet
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from klproj.utils.analysis import BatchAnalysisResult, KlprojAnalyzer


class AnalysisReporter:
    """Reporter for analysis progress and results."""

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

    def report_progress(self, current: int, total: int, filename: str):
        """Report analysis progress."""
        if self.quiet:
            return
        print(f"\n[{current}/{total}] Analyzing: {filename}")

    def report_file_result(self, filename: str, result):
        """Report analysis result for a single file."""
        if self.quiet:
            return

        errors = [i for i in result.issues if i.severity == "error"]
        warnings = [i for i in result.issues if i.severity == "warning"]

        if not errors and not warnings:
            print("   ✓ No issues found")
            if self.verbose and result.info:
                for key, value in result.info.items():
                    print(f"      {key}: {value}")
        else:
            if errors:
                print(f"   ✗ {len(errors)} error(s)")
                if self.verbose:
                    for error in errors[:5]:  # Show first 5
                        pass_str = (
                            f" (pass {error.pass_index})"
                            if error.pass_index is not None
                            else ""
                        )
                        print(f"      • {error.message}{pass_str}")
                    if len(errors) > 5:
                        print(f"      ... and {len(errors) - 5} more errors")

            if warnings:
                print(f"   ⚠  {len(warnings)} warning(s)")
                if self.verbose:
                    for warning in warnings[:5]:  # Show first 5
                        pass_str = (
                            f" (pass {warning.pass_index})"
                            if warning.pass_index is not None
                            else ""
                        )
                        print(f"      • {warning.message}{pass_str}")
                    if len(warnings) > 5:
                        print(f"      ... and {len(warnings) - 5} more warnings")

    def print_summary(self, result: BatchAnalysisResult):
        """Print analysis summary."""
        self.print_section("ANALYSIS SUMMARY", width=80)

        print(f"\nFiles analyzed: {result.total_files}")
        print(f"  ✗ Files with errors: {result.files_with_errors}")
        print(f"  ⚠  Files with warnings: {result.files_with_warnings}")
        print(
            f"  ✓ Files without issues: {result.total_files - result.files_with_errors - result.files_with_warnings}"
        )

        print("\nTotal issues:")
        print(f"  ✗ Errors: {result.total_errors}")
        print(f"  ⚠  Warnings: {result.total_warnings}")

        # Show most problematic files
        if result.files_with_errors > 0 and not self.quiet:
            print("\nFiles with most errors:")
            sorted_files = sorted(
                result.file_results.items(),
                key=lambda x: x[1].error_count,
                reverse=True,
            )
            for filename, file_result in sorted_files[:5]:
                if file_result.error_count > 0:
                    print(f"  • {filename}: {file_result.error_count} error(s)")

        # Category breakdown
        if not self.quiet:
            category_counts = {}
            for file_result in result.file_results.values():
                for issue in file_result.issues:
                    category_counts[issue.category] = (
                        category_counts.get(issue.category, 0) + 1
                    )

            if category_counts:
                print("\nIssues by category:")
                for category, count in sorted(
                    category_counts.items(), key=lambda x: -x[1]
                ):
                    print(f"  • {category}: {count}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze .klproj files for issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "input_dir",
        nargs="?",
        default="isf_conversions",
        help="Directory containing .klproj files (default: isf_conversions)",
    )

    # Analysis checks
    parser.add_argument(
        "--check-structure",
        action="store_true",
        help="Check XML structure and basic validity",
    )

    parser.add_argument(
        "--check-uniforms",
        action="store_true",
        help="Check for missing uniform declarations",
    )

    parser.add_argument(
        "--check-undefined",
        action="store_true",
        help="Find undefined variables (deep analysis)",
    )

    parser.add_argument(
        "--all-checks", action="store_true", help="Run all available analysis checks"
    )

    # Options
    parser.add_argument(
        "--isf-source",
        help="ISF source directory for enhanced analysis (used with --check-undefined)",
    )

    parser.add_argument(
        "--save-results",
        metavar="FILE",
        default="analysis_results.json",
        help="Save results to JSON file (default: analysis_results.json)",
    )

    parser.add_argument(
        "--no-save-results",
        action="store_true",
        help="Do not save results to JSON file",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed issues",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output (only show summary)",
    )

    return parser.parse_args()


def main():
    """Main entry point for analysis tool."""
    args = parse_args()

    # Create reporter
    reporter = AnalysisReporter(verbose=args.verbose, quiet=args.quiet)

    reporter.print_header("KLPROJ BATCH ANALYSIS TOOL", width=80)

    # Determine which checks to run
    checks = []
    if args.all_checks:
        checks = ["structure", "uniforms", "undefined_vars"]
    else:
        if args.check_structure:
            checks.append("structure")
        if args.check_uniforms:
            checks.append("uniforms")
        if args.check_undefined:
            checks.append("undefined_vars")

    # Default: structure + uniforms if no checks specified
    if not checks:
        checks = ["structure", "uniforms"]

    reporter.print_section(f"Checks: {', '.join(checks)}", width=80)

    # Find .klproj files
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"Error: Directory not found: {input_path}", file=sys.stderr)
        return 1

    klproj_files = list(input_path.glob("*.klproj"))

    if not klproj_files:
        print(f"No .klproj files found in {input_path}")
        return 1

    reporter.print_section(f"Found {len(klproj_files)} .klproj files", width=80)

    # Create analyzer
    analyzer = KlprojAnalyzer(isf_source_dir=args.isf_source, verbose=args.verbose)

    # Analyze batch
    result = analyzer.analyze_batch(
        files=klproj_files, checks=checks, reporter=reporter.report_progress
    )

    # Report individual results
    if not args.quiet:
        reporter.print_section("FILE RESULTS", width=80)
        for filename, file_result in result.file_results.items():
            reporter.report_file_result(filename, file_result)

    # Save results if requested
    if not args.no_save_results and args.save_results:
        result.save_json(args.save_results)
        print(f"\n💾 Analysis results saved to: {args.save_results}")

    # Print summary
    reporter.print_summary(result)

    # Return exit code based on results
    return 0 if result.total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
