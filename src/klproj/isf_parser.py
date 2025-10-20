"""
ISF (Interactive Shader Format) parser.

This module provides functionality to parse ISF files and extract their
metadata and shader code for conversion to KodeLife projects.

ISF Specification References:
- JSON Format: docs/ISF/isf-docs/pages/ref/ref_json.md
- Variables: docs/ISF/isf-docs/pages/ref/ref_variables.md
- Multi-pass: docs/ISF/isf-docs/pages/ref/ref_multipass.md
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ISFInput:
    """
    ISF input parameter definition.

    Corresponds to entries in the INPUTS array in ISF JSON.
    See: docs/ISF/isf-docs/pages/ref/ref_json.md (INPUTS section)

    Supported types: event, bool, long, float, point2D, color, image, audio, audioFFT
    """

    name: str
    input_type: str
    label: Optional[str] = None
    default: Optional[Any] = None
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    identity: Optional[Any] = None
    values: Optional[List[int]] = None  # For 'long' type
    labels: Optional[List[str]] = None  # For 'long' type


@dataclass
class ISFPass:
    """
    ISF rendering pass definition.

    Corresponds to entries in the PASSES array for multi-pass shaders.
    See: docs/ISF/isf-docs/pages/ref/ref_multipass.md
    """

    target: Optional[str] = None  # None means render to final output
    persistent: bool = False
    float_precision: bool = False
    width: Optional[str] = None
    height: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None
    main: Optional[str] = None  # Custom entry point function name


@dataclass
class ISFImported:
    """ISF imported image definition."""

    name: str
    path: str


@dataclass
class ISFShader:
    """Parsed ISF shader file."""

    isfvsn: str = "2"
    vsn: Optional[str] = None
    description: Optional[str] = None
    credit: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    inputs: List[ISFInput] = field(default_factory=list)
    passes: List[ISFPass] = field(default_factory=list)
    imported: List[ISFImported] = field(default_factory=list)
    shader_code: str = ""

    # Convenience properties
    @property
    def is_filter(self) -> bool:
        """Check if this is an image filter (has inputImage)."""
        return any(inp.name == "inputImage" for inp in self.inputs)

    @property
    def is_transition(self) -> bool:
        """Check if this is a transition (has startImage, endImage, progress)."""
        input_names = {inp.name for inp in self.inputs}
        return {"startImage", "endImage", "progress"}.issubset(input_names)

    @property
    def is_generator(self) -> bool:
        """Check if this is a generator (not a filter or transition)."""
        return not (self.is_filter or self.is_transition)


def parse_isf_file(file_path: str) -> ISFShader:
    """
    Parse an ISF file and extract metadata and shader code.

    Args:
        file_path: Path to the ISF file

    Returns:
        ISFShader object containing parsed metadata and code

    Raises:
        ValueError: If the file is not a valid ISF file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return parse_isf_string(content)


def parse_isf_string(content: str) -> ISFShader:
    """
    Parse ISF content from a string.

    Args:
        content: ISF file content

    Returns:
        ISFShader object containing parsed metadata and code

    Raises:
        ValueError: If the content is not valid ISF
    """
    # Extract JSON metadata from comment block
    json_match = re.match(r"/\*\s*(\{.*?\})\s*\*/", content, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON metadata found in ISF file (must start with /* { ... } */)")

    json_str = json_match.group(1)

    try:
        metadata = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON metadata in ISF file: {e}") from e

    # Extract shader code (everything after the JSON comment)
    shader_code = content[json_match.end() :].strip()

    # Parse metadata
    shader = ISFShader()
    shader.shader_code = shader_code
    shader.isfvsn = metadata.get("ISFVSN", "2")
    shader.vsn = metadata.get("VSN")
    shader.description = metadata.get("DESCRIPTION")
    shader.credit = metadata.get("CREDIT")
    shader.categories = metadata.get("CATEGORIES", [])

    # Parse inputs
    for input_dict in metadata.get("INPUTS", []):
        isf_input = ISFInput(
            name=input_dict["NAME"],
            input_type=input_dict["TYPE"],
            label=input_dict.get("LABEL"),
            default=input_dict.get("DEFAULT"),
            min_val=input_dict.get("MIN"),
            max_val=input_dict.get("MAX"),
            identity=input_dict.get("IDENTITY"),
            values=input_dict.get("VALUES"),
            labels=input_dict.get("LABELS"),
        )
        shader.inputs.append(isf_input)

    # Parse passes
    for pass_dict in metadata.get("PASSES", []):
        isf_pass = ISFPass(
            target=pass_dict.get("TARGET"),  # Can be None for final output
            persistent=bool(pass_dict.get("PERSISTENT", False)),
            float_precision=bool(pass_dict.get("FLOAT", False)),
            width=pass_dict.get("WIDTH"),
            height=pass_dict.get("HEIGHT"),
            description=pass_dict.get("DESCRIPTION"),
            name=pass_dict.get("NAME"),
            main=pass_dict.get("MAIN"),
        )
        shader.passes.append(isf_pass)

    # Parse imported images
    imported_data = metadata.get("IMPORTED", {})
    # IMPORTED can be either a dict or a list (usually empty list)
    if isinstance(imported_data, dict):
        for name, import_info in imported_data.items():
            if isinstance(import_info, dict):
                path = import_info.get("PATH", "")
            else:
                path = str(import_info)
            shader.imported.append(ISFImported(name=name, path=path))
    # If it's a list, it's usually empty or has different structure - skip for now

    return shader


def get_isf_type() -> str:
    """Get a human-readable description of the ISF type."""
    # This would be a method on ISFShader but shown here for clarity
    pass
