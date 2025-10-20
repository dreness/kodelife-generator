"""
Batch conversion processing utilities.

This module provides functionality to convert multiple ISF files to .klproj format
with progress tracking, error handling, and result reporting.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Union

from ..isf_converter import convert_isf_to_kodelife
from .isf_discovery import ISFInfo


@dataclass
class ConversionResult:
    """Results from batch conversion."""

    successful: List[Path] = field(default_factory=list)
    failed: List[tuple[Path, str]] = field(default_factory=list)
    skipped: List[tuple[Path, str]] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        """Number of successful conversions."""
        return len(self.successful)

    @property
    def error_count(self) -> int:
        """Number of failed conversions."""
        return len(self.failed)

    @property
    def skip_count(self) -> int:
        """Number of skipped files."""
        return len(self.skipped)

    @property
    def total_processed(self) -> int:
        """Total number of files processed (successful + failed + skipped)."""
        return self.success_count + self.error_count + self.skip_count

    def save_json(self, output_path: str):
        """
        Save results to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        data = {
            "successful": [str(p) for p in self.successful],
            "failed": [{"file": str(path), "error": error} for path, error in self.failed],
            "skipped": [{"file": str(path), "reason": reason} for path, reason in self.skipped],
            "summary": {
                "total_processed": self.total_processed,
                "successful": self.success_count,
                "failed": self.error_count,
                "skipped": self.skip_count,
                "success_rate": f"{(self.success_count / max(1, self.total_processed)) * 100:.1f}%",
            },
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)


class BatchConverter:
    """
    Convert multiple ISF files to .klproj format.

    Handles batch conversion with progress tracking, error handling,
    and configurable output options.
    """

    def __init__(
        self,
        output_dir: str,
        api: str = "GL3",
        width: int = 1920,
        height: int = 1080,
        overwrite: bool = False,
    ):
        """
        Initialize batch converter.

        Args:
            output_dir: Directory to save converted .klproj files
            api: Graphics API to use (GL3, GL2, etc.)
            width: Project width in pixels
            height: Project height in pixels
            overwrite: Whether to overwrite existing .klproj files
        """
        self.output_dir = Path(output_dir)
        self.api = api
        self.width = width
        self.height = height
        self.overwrite = overwrite

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename for safe filesystem use.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename with only alphanumeric, dash, and underscore characters
        """
        return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in filename)

    def _get_output_path(self, input_path: Path) -> Path:
        """
        Generate output path for a given input file.

        Args:
            input_path: Path to input ISF file

        Returns:
            Path to output .klproj file
        """
        base_name = input_path.stem
        safe_name = self._sanitize_filename(base_name)
        return self.output_dir / f"{safe_name}.klproj"

    def convert_file(
        self, input_file: Union[Path, ISFInfo], reporter: Optional[Callable] = None
    ) -> tuple[bool, Optional[Path], Optional[str]]:
        """
        Convert a single ISF file.

        Args:
            input_file: Path to ISF file or ISFInfo object
            reporter: Optional callback for progress reporting

        Returns:
            Tuple of (success, output_path, error_message)
        """
        # Extract path from ISFInfo if needed
        if isinstance(input_file, ISFInfo):
            input_path = input_file.path
        else:
            input_path = Path(input_file)

        # Check if file exists
        if not input_path.exists():
            return False, None, f"File not found: {input_path}"

        # Determine output path
        output_path = self._get_output_path(input_path)

        # Check if output already exists and we're not overwriting
        if output_path.exists() and not self.overwrite:
            return False, None, "Output file already exists (use --overwrite to replace)"

        try:
            # Convert the file
            result_path = convert_isf_to_kodelife(
                isf_file_path=str(input_path),
                output_path=str(output_path),
                api=self.api,
                width=self.width,
                height=self.height,
            )

            return True, Path(result_path), None

        except Exception as e:
            return False, None, str(e)

    def convert_batch(
        self,
        files: List[Union[Path, ISFInfo]],
        reporter: Optional[Callable] = None,
        continue_on_error: bool = True,
    ) -> ConversionResult:
        """
        Convert a batch of ISF files.

        Args:
            files: List of file paths or ISFInfo objects to convert
            reporter: Optional callback for progress reporting (called with index, total, filename)
            continue_on_error: Whether to continue processing after errors

        Returns:
            ConversionResult object with success/failure information
        """
        result = ConversionResult()

        for i, file_item in enumerate(files, 1):
            # Get file path and name
            if isinstance(file_item, ISFInfo):
                input_path = file_item.path
                display_name = file_item.name
            else:
                input_path = Path(file_item)
                display_name = input_path.stem

            # Report progress
            if reporter:
                reporter(i, len(files), display_name, file_item)

            # Convert file
            success, output_path, error = self.convert_file(file_item, reporter)

            if success:
                result.successful.append(output_path)
            else:
                result.failed.append((input_path, error))
                if not continue_on_error:
                    break

        return result

    def get_stats(self) -> dict:
        """
        Get statistics about the output directory.

        Returns:
            Dictionary with statistics about converted files
        """
        klproj_files = list(self.output_dir.glob("*.klproj"))

        total_size = sum(f.stat().st_size for f in klproj_files)

        return {
            "output_dir": str(self.output_dir),
            "file_count": len(klproj_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "api": self.api,
            "resolution": f"{self.width}x{self.height}",
        }
