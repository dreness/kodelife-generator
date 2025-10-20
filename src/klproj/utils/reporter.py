"""
Progress and results reporting utilities.

This module provides classes for displaying conversion progress,
results summaries, and formatted output.
"""

import sys
from pathlib import Path
from typing import Union

from .batch_processor import ConversionResult
from .isf_discovery import ISFInfo


class ConversionReporter:
    """
    Reports progress and results for batch conversions.

    Provides formatted console output with progress indicators,
    status messages, and summary statistics.
    """

    def __init__(self, verbose: bool = False, quiet: bool = False):
        """
        Initialize reporter.

        Args:
            verbose: Enable verbose output with additional details
            quiet: Suppress progress output (only show summary)
        """
        self.verbose = verbose
        self.quiet = quiet
        self._current_file = 0
        self._total_files = 0

    def print_header(self, title: str, width: int = 80):
        """
        Print a formatted header.

        Args:
            title: Header title text
            width: Total width of header in characters
        """
        if self.quiet:
            return

        print("=" * width)
        print(title)
        print("=" * width)

    def print_section(self, title: str, width: int = 80):
        """
        Print a formatted section separator.

        Args:
            title: Section title
            width: Total width in characters
        """
        if self.quiet:
            return

        print(f"\n{title}")
        print("-" * width)

    def report_discovery(self, multipass_count: int, single_count: int):
        """
        Report discovered ISF files.

        Args:
            multipass_count: Number of multipass shaders found
            single_count: Number of single-pass shaders found
        """
        if self.quiet:
            return

        total = multipass_count + single_count
        print(f"\nFound {total} ISF files:")
        print(f"  Multipass shaders: {multipass_count}")
        print(f"  Single-pass shaders: {single_count}")

    def report_selection(self, selected: list, selection_strategy: str = ""):
        """
        Report selected files for conversion.

        Args:
            selected: List of selected files/ISFInfo objects
            selection_strategy: Description of selection strategy
        """
        if self.quiet:
            return

        print(f"\nSelected {len(selected)} files for conversion")
        if selection_strategy:
            print(f"Strategy: {selection_strategy}")

        if self.verbose and len(selected) <= 20:
            print("\nFiles to convert:")
            for item in selected:
                if isinstance(item, ISFInfo):
                    tag = "[MULTI]" if item.is_multipass else "[SINGLE]"
                    print(f"  {tag} {item.name}")
                else:
                    print(f"  {Path(item).name}")

    def report_progress(
        self, current: int, total: int, filename: str, file_info: Union[Path, ISFInfo, None] = None
    ):
        """
        Report progress during batch conversion.

        Args:
            current: Current file number (1-indexed)
            total: Total number of files
            filename: Name of current file
            file_info: Optional ISFInfo or Path object for additional context
        """
        if self.quiet:
            return

        self._current_file = current
        self._total_files = total

        # Determine tag
        tag = ""
        if isinstance(file_info, ISFInfo):
            tag = "[MULTIPASS]" if file_info.is_multipass else "[SINGLE]"
            tag += f" ({file_info.num_passes} pass{'es' if file_info.num_passes > 1 else ''})"

        print(f"\n[{current}/{total}] {tag} {filename}")

    def report_file_success(self, output_path: Path, file_size: int = None):
        """
        Report successful file conversion.

        Args:
            output_path: Path to converted .klproj file
            file_size: Optional file size in bytes
        """
        if self.quiet:
            return

        if file_size is None and output_path.exists():
            file_size = output_path.stat().st_size

        size_str = f" ({file_size:,} bytes)" if file_size else ""
        print(f"   ✓ Created {output_path.name}{size_str}")

    def report_file_error(self, error_msg: str):
        """
        Report file conversion error.

        Args:
            error_msg: Error message
        """
        # Always show errors, even in quiet mode
        truncated = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg
        print(f"   ✗ Error: {truncated}", file=sys.stderr)

    def report_file_skip(self, reason: str):
        """
        Report skipped file.

        Args:
            reason: Reason for skipping
        """
        if not self.quiet:
            print(f"   ⊘ Skipped: {reason}")

    def print_summary(self, result: ConversionResult, stats: dict = None):
        """
        Print conversion summary.

        Args:
            result: ConversionResult object
            stats: Optional dictionary with additional statistics
        """
        self.print_section("CONVERSION SUMMARY", width=80)

        print(f"\nFiles processed: {result.total_processed}")
        print(f"  ✓ Successful: {result.success_count}")
        print(f"  ✗ Failed: {result.error_count}")

        if result.skip_count > 0:
            print(f"  ⊘ Skipped: {result.skip_count}")

        # Success rate
        if result.total_processed > 0:
            success_rate = (result.success_count / result.total_processed) * 100
            print(f"\nSuccess rate: {success_rate:.1f}%")

        # Show failed files
        if result.failed and not self.quiet:
            print(f"\n✗ Failed conversions ({len(result.failed)}):")
            for file_path, error in result.failed[:10]:  # Show first 10
                error_short = error[:80] + "..." if len(error) > 80 else error
                print(f"  • {file_path.name}: {error_short}")

            if len(result.failed) > 10:
                print(f"  ... and {len(result.failed) - 10} more")

        # Show statistics
        if stats:
            print("\nOutput statistics:")
            print(f"  Directory: {stats.get('output_dir', 'N/A')}")
            if "total_size_mb" in stats:
                print(f"  Total size: {stats['total_size_mb']:.2f} MB")
            if "api" in stats:
                print(f"  API: {stats['api']}")
            if "resolution" in stats:
                print(f"  Resolution: {stats['resolution']}")

    def print_info(self, message: str):
        """
        Print informational message.

        Args:
            message: Message to print
        """
        if not self.quiet:
            print(message)

    def print_warning(self, message: str):
        """
        Print warning message.

        Args:
            message: Warning message
        """
        print(f"⚠️  {message}", file=sys.stderr)

    def print_error(self, message: str):
        """
        Print error message.

        Args:
            message: Error message
        """
        print(f"❌ {message}", file=sys.stderr)
