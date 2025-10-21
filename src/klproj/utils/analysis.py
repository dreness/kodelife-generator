"""
Analysis utilities for .klproj files.

This module provides functionality to extract, parse, and analyze .klproj files
for structural issues, missing uniforms, undefined variables, and other problems.
"""

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set


@dataclass
class AnalysisIssue:
    """Represents a single analysis issue."""

    severity: str  # 'error', 'warning', 'info'
    category: str  # 'structure', 'uniforms', 'undefined_vars', etc.
    message: str
    pass_index: Optional[int] = None
    details: Dict = field(default_factory=dict)


@dataclass
class FileAnalysisResult:
    """Results from analyzing a single .klproj file."""

    file_path: Path
    issues: List[AnalysisIssue] = field(default_factory=list)
    warnings: List[AnalysisIssue] = field(default_factory=list)
    info: Dict = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(issue.severity == "error" for issue in self.issues)

    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return sum(1 for issue in self.issues if issue.severity == "warning")


@dataclass
class BatchAnalysisResult:
    """Results from analyzing multiple .klproj files."""

    file_results: Dict[str, FileAnalysisResult] = field(default_factory=dict)

    @property
    def total_files(self) -> int:
        """Total number of files analyzed."""
        return len(self.file_results)

    @property
    def files_with_errors(self) -> int:
        """Number of files with errors."""
        return sum(1 for result in self.file_results.values() if result.has_errors)

    @property
    def files_with_warnings(self) -> int:
        """Number of files with warnings."""
        return sum(1 for result in self.file_results.values() if result.warning_count > 0)

    @property
    def total_errors(self) -> int:
        """Total number of errors across all files."""
        return sum(result.error_count for result in self.file_results.values())

    @property
    def total_warnings(self) -> int:
        """Total number of warnings across all files."""
        return sum(result.warning_count for result in self.file_results.values())

    def save_json(self, output_path: str):
        """Save analysis results to JSON file."""
        data = {
            "summary": {
                "total_files": self.total_files,
                "files_with_errors": self.files_with_errors,
                "files_with_warnings": self.files_with_warnings,
                "total_errors": self.total_errors,
                "total_warnings": self.total_warnings,
            },
            "files": {
                name: {
                    "errors": [
                        {
                            "severity": issue.severity,
                            "category": issue.category,
                            "message": issue.message,
                            "pass": issue.pass_index,
                            "details": issue.details,
                        }
                        for issue in result.issues
                        if issue.severity == "error"
                    ],
                    "warnings": [
                        {
                            "severity": issue.severity,
                            "category": issue.category,
                            "message": issue.message,
                            "pass": issue.pass_index,
                            "details": issue.details,
                        }
                        for issue in result.issues
                        if issue.severity == "warning"
                    ],
                    "info": result.info,
                }
                for name, result in self.file_results.items()
            },
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)


class KlprojAnalyzer:
    """
    Analyze .klproj files for various issues.

    Provides methods to check for structural problems, missing uniforms,
    undefined variables, and other shader-related issues.
    """

    def __init__(self, isf_source_dir: Optional[str] = None, verbose: bool = False):
        """
        Initialize analyzer.

        Args:
            isf_source_dir: Optional path to ISF source files for deep analysis
            verbose: Enable verbose output
        """
        self.isf_source_dir = Path(isf_source_dir) if isf_source_dir else None
        self.verbose = verbose

        # GLSL keywords and built-ins to filter out
        self.glsl_keywords = {
            "void",
            "main",
            "if",
            "else",
            "for",
            "while",
            "do",
            "return",
            "break",
            "continue",
            "in",
            "out",
            "inout",
            "uniform",
            "const",
            "attribute",
            "varying",
            "float",
            "vec2",
            "vec3",
            "vec4",
            "mat2",
            "mat3",
            "mat4",
            "int",
            "bool",
            "sampler2D",
            "samplerCube",
            "true",
            "false",
            "gl_Position",
            "gl_FragCoord",
            "gl_FragColor",
            "fragColor",
            "texture",
            "mix",
            "clamp",
            "abs",
            "fract",
            "sin",
            "cos",
            "dot",
            "length",
            "normalize",
            "floor",
            "ceil",
            "mod",
            "min",
            "max",
            "step",
            "smoothstep",
            "sqrt",
            "pow",
            "exp",
            "log",
            "radians",
            "degrees",
            "r",
            "g",
            "b",
            "a",
            "x",
            "y",
            "z",
            "w",
            "s",
            "t",
            "p",
            "q",
            "rg",
            "gb",
            "ba",
            "rb",
            "xy",
            "yz",
            "zw",
            "xw",
            "rgb",
            "rgba",
            "xyz",
            "xyzw",
            "returnMe",
            "co",
            "c",
            "K",
            "pt",  # Common local variable names
        }

    def extract_to_xml(self, klproj_path: Path) -> Optional[Path]:
        """
        Extract .klproj file to XML using CLI.

        Args:
            klproj_path: Path to .klproj file

        Returns:
            Path to extracted XML file, or None on error
        """
        xml_path = klproj_path.with_suffix(".xml")

        result = subprocess.run(
            ["uv", "run", "klproj", "extract", str(klproj_path), str(xml_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and xml_path.exists():
            return xml_path

        return None

    def check_structure(self, xml_path: Path) -> FileAnalysisResult:
        """
        Check XML structure for basic validity.

        Args:
            xml_path: Path to extracted XML file

        Returns:
            FileAnalysisResult with structural issues
        """
        result = FileAnalysisResult(file_path=xml_path)

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Check root element
            if root.tag != "klxml":
                result.issues.append(
                    AnalysisIssue(
                        severity="error",
                        category="structure",
                        message=f"Root element is '{root.tag}', expected 'klxml'",
                    )
                )

            # Store API info
            result.info["api"] = root.get("a", "UNKNOWN")

            # Find document
            document = root.find("document")
            if document is None:
                result.issues.append(
                    AnalysisIssue(
                        severity="error",
                        category="structure",
                        message="No <document> element found",
                    )
                )
                return result

            # Check global parameters
            params_elem = document.find("params")
            if params_elem is None:
                result.issues.append(
                    AnalysisIssue(
                        severity="warning",
                        category="structure",
                        message="No global <params> element",
                    )
                )
                result.info["global_params"] = 0
            else:
                params = list(params_elem.findall("param"))
                result.info["global_params"] = len(params)

                # Check for standard ISF parameters
                param_names = [
                    p.find("variableName").text
                    for p in params
                    if p.find("variableName") is not None
                ]
                for expected in ["TIME", "RENDERSIZE"]:
                    if expected not in param_names:
                        result.issues.append(
                            AnalysisIssue(
                                severity="warning",
                                category="structure",
                                message=f"Missing expected parameter: {expected}",
                            )
                        )

            # Check passes
            passes_elem = document.find("passes")
            if passes_elem is None:
                result.issues.append(
                    AnalysisIssue(
                        severity="error",
                        category="structure",
                        message="No <passes> element found",
                    )
                )
                return result

            passes = list(passes_elem.findall("pass"))
            result.info["num_passes"] = len(passes)

            if len(passes) == 0:
                result.issues.append(
                    AnalysisIssue(
                        severity="error",
                        category="structure",
                        message="No render passes found",
                    )
                )

        except ET.ParseError as e:
            result.issues.append(
                AnalysisIssue(
                    severity="error",
                    category="structure",
                    message=f"XML parse error: {str(e)}",
                )
            )
        except Exception as e:
            result.issues.append(
                AnalysisIssue(
                    severity="error",
                    category="structure",
                    message=f"Analysis error: {str(e)}",
                )
            )

        return result

    def check_uniforms(self, xml_path: Path) -> FileAnalysisResult:
        """
        Check for missing uniform declarations in shaders.

        Args:
            xml_path: Path to extracted XML file

        Returns:
            FileAnalysisResult with uniform-related issues
        """
        result = FileAnalysisResult(file_path=xml_path)

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            document = root.find("document")

            if document is None:
                return result

            # Get global parameter names
            params_elem = document.find("params")
            param_names = []
            if params_elem is not None:
                for param in params_elem.findall("param"):
                    var_name_elem = param.find("variableName")
                    if var_name_elem is not None and var_name_elem.text:
                        param_names.append(var_name_elem.text)

            # Check each pass
            passes_elem = document.find("passes")
            if passes_elem is None:
                return result

            for i, pass_elem in enumerate(passes_elem.findall("pass")):
                result.info[f"pass_{i}_type"] = pass_elem.get("type", "UNKNOWN")

                # Find fragment shader
                stages_elem = pass_elem.find("stages")
                if stages_elem is None:
                    continue

                frag_stage = None
                for stage in stages_elem.findall("stage"):
                    if stage.get("type") == "FRAGMENT":
                        frag_stage = stage
                        break

                if frag_stage is None:
                    continue

                # Get shader source
                shader_elem = frag_stage.find("shader")
                source_elem = shader_elem.find("source") if shader_elem is not None else None

                if source_elem is None or not source_elem.text:
                    continue

                shader_code = source_elem.text
                result.info[f"pass_{i}_shader_length"] = len(shader_code)

                # Check for #version directive
                if "#version" not in shader_code:
                    result.issues.append(
                        AnalysisIssue(
                            severity="warning",
                            category="uniforms",
                            message="No #version directive in shader",
                            pass_index=i,
                        )
                    )

                # Check for main function
                if "void main()" not in shader_code and "void main(" not in shader_code:
                    result.issues.append(
                        AnalysisIssue(
                            severity="error",
                            category="uniforms",
                            message="No main() function found in shader",
                            pass_index=i,
                        )
                    )

                # Check for output variable
                has_frag_color = "fragColor" in shader_code
                has_gl_frag_color = "gl_FragColor" in shader_code
                if not has_frag_color and not has_gl_frag_color:
                    result.issues.append(
                        AnalysisIssue(
                            severity="warning",
                            category="uniforms",
                            message="No output variable (fragColor or gl_FragColor) found",
                            pass_index=i,
                        )
                    )

                # Check for uniform declarations
                if "uniform" not in shader_code:
                    result.issues.append(
                        AnalysisIssue(
                            severity="warning",
                            category="uniforms",
                            message="No uniform declarations found in shader",
                            pass_index=i,
                        )
                    )

                # Check specific uniforms match global parameters
                for param in param_names:
                    if param in shader_code:
                        # Parameter is used in shader, check for declaration
                        uniform_patterns = [
                            f"uniform float {param}",
                            f"uniform vec2 {param}",
                            f"uniform vec3 {param}",
                            f"uniform vec4 {param}",
                            f"uniform highp float {param}",
                            f"uniform highp vec2 {param}",
                        ]

                        has_uniform = any(pattern in shader_code for pattern in uniform_patterns)

                        if not has_uniform:
                            result.issues.append(
                                AnalysisIssue(
                                    severity="warning",
                                    category="uniforms",
                                    message=f"Parameter '{param}' used but no uniform declaration found",
                                    pass_index=i,
                                    details={"parameter": param},
                                )
                            )

        except Exception as e:
            result.issues.append(
                AnalysisIssue(
                    severity="error",
                    category="uniforms",
                    message=f"Error checking uniforms: {str(e)}",
                )
            )

        return result

    def _extract_shader_variables(self, shader_code: str) -> Dict[str, Set[str]]:
        """Extract declared and used variables from shader code."""
        # Find uniform declarations
        uniform_pattern = r"uniform\s+(?:highp|mediump|lowp)?\s*(\w+)\s+(\w+)"
        uniforms = {match[1] for match in re.findall(uniform_pattern, shader_code)}

        # Find const declarations
        const_pattern = r"const\s+(?:highp|mediump|lowp)?\s*\w+\s+(\w+)"
        consts = set(re.findall(const_pattern, shader_code))

        # Remove comments and strings
        code_clean = re.sub(r"//.*$", "", shader_code, flags=re.MULTILINE)
        code_clean = re.sub(r"/\*.*?\*/", "", code_clean, flags=re.DOTALL)

        # Find potential variable uses
        identifier_pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b"
        potential_vars = re.findall(identifier_pattern, code_clean)

        var_uses = {v for v in potential_vars if v not in self.glsl_keywords and v not in consts}

        return {"uniforms": uniforms, "consts": consts, "potential_uses": var_uses}

    def check_undefined_vars(
        self, xml_path: Path, isf_path: Optional[Path] = None
    ) -> FileAnalysisResult:
        """
        Deep analysis for undefined variables in shaders.

        Args:
            xml_path: Path to extracted XML file
            isf_path: Optional path to original ISF file for enhanced analysis

        Returns:
            FileAnalysisResult with undefined variable issues
        """
        result = FileAnalysisResult(file_path=xml_path)

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            document = root.find("document")

            if document is None:
                return result

            # Get global parameters
            params_elem = document.find("params")
            global_params = set()
            if params_elem is not None:
                for param in params_elem.findall("param"):
                    var_name_elem = param.find("variableName")
                    if var_name_elem is not None and var_name_elem.text:
                        global_params.add(var_name_elem.text)

            # Check each pass
            passes_elem = document.find("passes")
            if passes_elem is None:
                return result

            for i, pass_elem in enumerate(passes_elem.findall("pass")):
                # Find fragment shader
                stages_elem = pass_elem.find("stages")
                if stages_elem is None:
                    continue

                frag_stage = None
                for stage in stages_elem.findall("stage"):
                    if stage.get("type") == "FRAGMENT":
                        frag_stage = stage
                        break

                if frag_stage is None:
                    continue

                # Get shader source
                shader_elem = frag_stage.find("shader")
                source_elem = shader_elem.find("source") if shader_elem is not None else None

                if source_elem is None or not source_elem.text:
                    continue

                shader_code = source_elem.text

                # Extract variables
                vars_info = self._extract_shader_variables(shader_code)

                # Check for undefined uses
                declared = vars_info["uniforms"] | vars_info["consts"] | global_params
                used = vars_info["potential_uses"]

                undefined = used - declared

                if undefined:
                    for var in sorted(undefined):
                        result.issues.append(
                            AnalysisIssue(
                                severity="warning",
                                category="undefined_vars",
                                message=f"Potentially undefined variable: {var}",
                                pass_index=i,
                                details={"variable": var},
                            )
                        )

        except Exception as e:
            result.issues.append(
                AnalysisIssue(
                    severity="error",
                    category="undefined_vars",
                    message=f"Error checking undefined variables: {str(e)}",
                )
            )

        return result

    def analyze_file(
        self, klproj_path: Path, checks: List[str], reporter: Optional[Callable] = None
    ) -> FileAnalysisResult:
        """
        Analyze a single .klproj file with specified checks.

        Args:
            klproj_path: Path to .klproj file
            checks: List of checks to run ('structure', 'uniforms', 'undefined_vars')
            reporter: Optional progress reporter callback

        Returns:
            Combined FileAnalysisResult
        """
        # Extract to XML
        xml_path = self.extract_to_xml(klproj_path)

        if xml_path is None:
            result = FileAnalysisResult(file_path=klproj_path)
            result.issues.append(
                AnalysisIssue(
                    severity="error",
                    category="extraction",
                    message="Failed to extract .klproj to XML",
                )
            )
            return result

        # Combine results from all checks
        combined_result = FileAnalysisResult(file_path=klproj_path)

        try:
            for check in checks:
                if check == "structure":
                    check_result = self.check_structure(xml_path)
                elif check == "uniforms":
                    check_result = self.check_uniforms(xml_path)
                elif check == "undefined_vars":
                    check_result = self.check_undefined_vars(xml_path)
                else:
                    continue

                combined_result.issues.extend(check_result.issues)
                combined_result.info.update(check_result.info)

        finally:
            # Clean up XML file
            if xml_path.exists():
                xml_path.unlink()

        return combined_result

    def analyze_batch(
        self, files: List[Path], checks: List[str], reporter: Optional[Callable] = None
    ) -> BatchAnalysisResult:
        """
        Analyze multiple .klproj files.

        Args:
            files: List of .klproj file paths
            checks: List of checks to run
            reporter: Optional progress reporter callback

        Returns:
            BatchAnalysisResult
        """
        batch_result = BatchAnalysisResult()

        for i, file_path in enumerate(files, 1):
            if reporter:
                reporter(i, len(files), file_path.name)

            result = self.analyze_file(file_path, checks, reporter)
            batch_result.file_results[file_path.name] = result

        return batch_result
