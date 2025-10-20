"""
ISF file discovery and filtering utilities.

This module provides functionality to scan directories for ISF shader files,
identify multipass vs single-pass shaders, and select files based on various criteria.
"""

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ISFInfo:
    """Information about an ISF shader file."""

    path: Path
    is_multipass: bool
    passes: List[dict] = field(default_factory=list)
    description: str = ""
    categories: List[str] = field(default_factory=list)
    inputs: List[dict] = field(default_factory=list)

    @property
    def name(self) -> str:
        """Get the filename without extension."""
        return self.path.stem

    @property
    def num_passes(self) -> int:
        """Get the number of passes."""
        return len(self.passes) if self.passes else 1


class ISFDiscovery:
    """
    Discover and filter ISF files.

    Scans directories for ISF shader files, parses their metadata,
    and provides methods for filtering and selecting files.
    """

    def __init__(self, base_dirs: Optional[List[str]] = None):
        """
        Initialize ISF discovery.

        Args:
            base_dirs: List of directories to search. If None, uses default locations.
        """
        if base_dirs is None:
            base_dirs = ['/Users/andre/Library/Graphics/ISF']

        self.base_dirs = [Path(d) for d in base_dirs]
        self._multipass_cache: Optional[List[ISFInfo]] = None
        self._single_pass_cache: Optional[List[ISFInfo]] = None

    def _extract_isf_metadata(self, shader_text: str) -> Optional[dict]:
        """
        Extract JSON metadata from ISF shader.

        Args:
            shader_text: The full ISF shader source code

        Returns:
            Parsed JSON metadata or None if not found/invalid
        """
        match = re.match(r'/\*\s*(\{.*?\})\s*\*/', shader_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def scan(self, extensions: Optional[List[str]] = None) -> tuple[List[ISFInfo], List[ISFInfo]]:
        """
        Scan for ISF files and categorize them.

        Args:
            extensions: File extensions to search for (default: ['.fs', '.frag', '.glsl'])

        Returns:
            Tuple of (multipass_shaders, single_pass_shaders)
        """
        if extensions is None:
            extensions = ['.fs', '.frag', '.glsl']

        multipass = []
        single_pass = []

        for base_dir in self.base_dirs:
            if not base_dir.exists():
                continue

            # Find all ISF files
            for ext in extensions:
                pattern = f'*{ext}'
                for file_path in base_dir.rglob(pattern):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        metadata = self._extract_isf_metadata(content)

                        if metadata is None:
                            # File doesn't have ISF metadata, skip it
                            continue

                        # Check for PASSES (multipass shader)
                        is_multipass = 'PASSES' in metadata

                        isf_info = ISFInfo(
                            path=file_path,
                            is_multipass=is_multipass,
                            passes=metadata.get('PASSES', []),
                            description=metadata.get('DESCRIPTION', ''),
                            categories=metadata.get('CATEGORIES', []),
                            inputs=metadata.get('INPUTS', [])
                        )

                        if is_multipass:
                            multipass.append(isf_info)
                        else:
                            single_pass.append(isf_info)

                    except Exception:
                        # Skip files that can't be read or parsed
                        continue

        # Cache results
        self._multipass_cache = multipass
        self._single_pass_cache = single_pass

        return multipass, single_pass

    def get_cached(self) -> tuple[List[ISFInfo], List[ISFInfo]]:
        """
        Get cached scan results, or scan if not cached.

        Returns:
            Tuple of (multipass_shaders, single_pass_shaders)
        """
        if self._multipass_cache is None or self._single_pass_cache is None:
            return self.scan()
        return self._multipass_cache, self._single_pass_cache

    def select_random(self, count: int, from_list: List[ISFInfo]) -> List[ISFInfo]:
        """
        Select N random files from a list.

        Args:
            count: Number of files to select
            from_list: List of ISFInfo objects to select from

        Returns:
            List of randomly selected ISFInfo objects
        """
        if count >= len(from_list):
            return from_list.copy()
        return random.sample(from_list, count)

    def select_mixed(self, num_multipass: int, num_single: int) -> List[ISFInfo]:
        """
        Select a mix of multipass and single-pass shaders.

        Args:
            num_multipass: Number of multipass shaders to select
            num_single: Number of single-pass shaders to select

        Returns:
            List of selected ISFInfo objects (shuffled)
        """
        multipass, single_pass = self.get_cached()

        selected_multi = self.select_random(num_multipass, multipass)
        selected_single = self.select_random(num_single, single_pass)

        combined = selected_multi + selected_single
        random.shuffle(combined)

        return combined

    def filter_by_category(self, category: str, shader_list: List[ISFInfo]) -> List[ISFInfo]:
        """
        Filter shaders by category.

        Args:
            category: Category name to filter by
            shader_list: List of ISFInfo objects to filter

        Returns:
            Filtered list of ISFInfo objects
        """
        return [
            shader for shader in shader_list
            if category.lower() in [cat.lower() for cat in shader.categories]
        ]

    def save_to_json(self, output_path: str):
        """
        Save scan results to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        multipass, single_pass = self.get_cached()

        data = {
            'multipass': [
                {
                    'path': str(shader.path),
                    'passes': shader.passes,
                    'description': shader.description,
                    'categories': shader.categories,
                    'inputs': [inp.get('NAME', '') for inp in shader.inputs]
                }
                for shader in multipass
            ],
            'single_pass': [str(shader.path) for shader in single_pass],
            'summary': {
                'total_multipass': len(multipass),
                'total_single_pass': len(single_pass),
                'total': len(multipass) + len(single_pass)
            }
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
