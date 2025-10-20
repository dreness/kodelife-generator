# KodeLife Generator Tools

Consolidated utility scripts for working with ISF shaders and .klproj files.

## Overview

This directory contains three main tools that replace the previous collection of 9+ scripts in the project root:

1. **`batch_convert.py`** - Batch ISF to .klproj conversion with flexible selection
2. **`analyze_batch.py`** - Analysis of .klproj files for issues and problems
3. **`find_shaders.py`** - ISF shader discovery and cataloging

## Quick Start

```bash
# Convert 30 random ISF files (default behavior)
uv run python tools/batch_convert.py

# Analyze converted files
uv run python tools/analyze_batch.py isf_conversions/

# Find and catalog all ISF shaders
uv run python tools/find_shaders.py --stats-only
```

## Tools

### 1. batch_convert.py

Replaces: `convert_random_isf.py`, `convert_random_batch.py`, `convert_batch_with_multipass.py`, `convert_diverse_batch.py`, `convert_all_multipass.py`

**Features:**
- Multiple selection strategies (random, multipass-only, single-only, mixed, all)
- Progress reporting with detailed statistics
- JSON output for results tracking
- Configurable resolution and API
- Verbose and quiet modes

**Examples:**
```bash
# Convert 50 random files
uv run python tools/batch_convert.py --random 50

# Convert only multipass shaders
uv run python tools/batch_convert.py --multipass-only

# Convert mix: 10 multipass + 5 single-pass
uv run python tools/batch_convert.py --mixed 10 5

# Custom output directory and resolution
uv run python tools/batch_convert.py --random 20 -o output/ -w 1280 --height 720

# Use GL2 API
uv run python tools/batch_convert.py --random 10 -a GL2

# Quiet mode (summary only)
uv run python tools/batch_convert.py --random 10 --quiet

# Multiple ISF directories
uv run python tools/batch_convert.py -d ~/shaders -d ./local_shaders
```

**Options:**
```
-d, --isf-dir DIR         ISF source directory (repeatable)
-o, --output-dir DIR      Output directory (default: ./isf_conversions)
--random N                Convert N random files
--multipass-only          Only multipass shaders
--single-only             Only single-pass shaders
--mixed M N               M multipass + N single-pass
--all                     Convert all found shaders
-w, --width N             Width in pixels (default: 1920)
--height N                Height in pixels (default: 1080)
-a, --api API             Graphics API: GL2, GL3, MTL, ES3 (default: GL3)
--overwrite               Overwrite existing files
--save-results FILE       Save JSON results (default: conversion_results.json)
--no-save-results         Don't save JSON results
-v, --verbose             Detailed output
-q, --quiet               Summary only
```

### 2. analyze_batch.py

Replaces: `analyze_converted.py`, `analyze_converted_batch.py`, `analyze_undefined_vars.py`

**Features:**
- Multiple analysis checks (structure, uniforms, undefined variables)
- Configurable check selection
- Detailed issue reporting with severity levels
- JSON output for automated processing
- Statistics and category breakdown

**Examples:**
```bash
# Default checks (structure + uniforms)
uv run python tools/analyze_batch.py isf_conversions/

# All available checks
uv run python tools/analyze_batch.py isf_conversions/ --all-checks

# Specific checks
uv run python tools/analyze_batch.py isf_conversions/ --check-uniforms --check-undefined

# Custom output file
uv run python tools/analyze_batch.py isf_conversions/ --save-results my_analysis.json

# Deep analysis with ISF source context
uv run python tools/analyze_batch.py isf_conversions/ --check-undefined \
    --isf-source ~/Library/Graphics/ISF

# Verbose mode
uv run python tools/analyze_batch.py isf_conversions/ --verbose
```

**Checks Available:**
- `--check-structure` - XML structure and basic validity
- `--check-uniforms` - Missing uniform declarations
- `--check-undefined` - Undefined variables (deep analysis)
- `--all-checks` - Run all checks

**Options:**
```
input_dir                 Directory with .klproj files (default: isf_conversions)
--check-structure         Check XML structure
--check-uniforms          Check uniforms
--check-undefined         Find undefined variables
--all-checks              Run all checks
--isf-source DIR          ISF source for enhanced analysis
--save-results FILE       Save JSON (default: analysis_results.json)
--no-save-results         Don't save JSON
-v, --verbose             Detailed issue output
-q, --quiet               Summary only
```

### 3. find_shaders.py

Replaces: `find_multipass_isf.py` (enhanced version)

**Features:**
- Scans directories for ISF shaders
- Identifies multipass vs single-pass
- Extracts metadata (categories, inputs, descriptions)
- Category filtering
- Pass count filtering
- Detailed statistics

**Examples:**
```bash
# Find all shaders with statistics
uv run python tools/find_shaders.py --stats-only

# Find with details
uv run python tools/find_shaders.py --verbose

# Search specific directories
uv run python tools/find_shaders.py -d ~/shaders -d ./local_shaders

# Only multipass shaders
uv run python tools/find_shaders.py --multipass-only

# Filter by category
uv run python tools/find_shaders.py --category "Generator"

# Find shaders with many passes
uv run python tools/find_shaders.py --min-passes 5

# Custom output file
uv run python tools/find_shaders.py --output shader_catalog.json
```

**Options:**
```
-d, --isf-dir DIR         ISF directory to search (repeatable)
--multipass-only          Only show multipass shaders
--single-only             Only show single-pass shaders
--category CAT            Filter by category
--min-passes N            Min number of passes
-o, --output FILE         Output file (default: multipass_isf_shaders.json)
--no-save                 Don't save JSON
--stats-only              Only statistics
-v, --verbose             Detailed shader info
-q, --quiet               Suppress output except stats
```

## Architecture

### Shared Utilities (`src/klproj/utils/`)

The tools are built on reusable utility modules:

- **`isf_discovery.py`** - ISF file scanning and metadata extraction
  - `ISFDiscovery` class - Find and categorize ISF files
  - `ISFInfo` dataclass - Structured shader information

- **`batch_processor.py`** - Batch conversion processing
  - `BatchConverter` class - Convert multiple files with progress tracking
  - `ConversionResult` dataclass - Track success/failure/statistics

- **`analysis.py`** - .klproj file analysis
  - `KlprojAnalyzer` class - Multiple analysis check types
  - `FileAnalysisResult`, `BatchAnalysisResult` - Structured results

- **`reporter.py`** - Progress and results reporting
  - `ConversionReporter` class - Formatted console output
  - Verbose/quiet mode support

### Design Benefits

1. **Consolidation** - 9+ scripts → 3 tools with shared infrastructure
2. **Consistency** - Unified interface patterns across all tools
3. **Maintainability** - Single source of truth for common operations
4. **Extensibility** - Easy to add new features and selection strategies
5. **Testability** - Modular design with clear responsibilities

## Migration from Old Scripts

| Old Script | New Command |
|------------|-------------|
| `convert_random_isf.py` | `tools/batch_convert.py --random 30` |
| `convert_random_batch.py` | `tools/batch_convert.py --random N` |
| `convert_batch_with_multipass.py` | `tools/batch_convert.py --mixed M N` |
| `convert_diverse_batch.py` | `tools/batch_convert.py --mixed 8 7` |
| `convert_all_multipass.py` | `tools/batch_convert.py --multipass-only` |
| `analyze_converted.py` | `tools/analyze_batch.py DIR/` |
| `analyze_converted_batch.py` | `tools/analyze_batch.py DIR/ --all-checks` |
| `analyze_undefined_vars.py` | `tools/analyze_batch.py DIR/ --check-undefined` |
| `find_multipass_isf.py` | `tools/find_shaders.py` |

## Workflow Examples

### Typical Conversion + Analysis Workflow

```bash
# 1. Find available shaders
uv run python tools/find_shaders.py --stats-only

# 2. Convert a mixed batch
uv run python tools/batch_convert.py --mixed 10 10 -o output/

# 3. Analyze the converted files
uv run python tools/analyze_batch.py output/ --all-checks

# 4. Review results
cat conversion_results.json
cat analysis_results.json
```

### Category-Specific Workflow

```bash
# Find all "Generator" shaders
uv run python tools/find_shaders.py --category Generator --output generators.json

# Extract the paths and convert them
# (You can parse generators.json or use --multipass-only filter)
uv run python tools/batch_convert.py --random 20 -d ~/Library/Graphics/ISF

# Analyze with verbose output
uv run python tools/analyze_batch.py isf_conversions/ --verbose
```

### Testing/QA Workflow

```bash
# Convert a small test batch with detailed logging
uv run python tools/batch_convert.py --random 5 -o test_output/ --verbose

# Run comprehensive analysis
uv run python tools/analyze_batch.py test_output/ --all-checks --verbose

# Review any issues found
cat analysis_results.json | jq '.files | to_entries | .[] | select(.value.errors | length > 0)'
```

## JSON Output Formats

### conversion_results.json
```json
{
  "successful": ["path1.klproj", "path2.klproj"],
  "failed": [
    {"file": "path3.fs", "error": "error message"}
  ],
  "summary": {
    "total_processed": 10,
    "successful": 8,
    "failed": 2,
    "success_rate": "80.0%"
  }
}
```

### analysis_results.json
```json
{
  "summary": {
    "total_files": 10,
    "files_with_errors": 1,
    "total_errors": 2,
    "total_warnings": 15
  },
  "files": {
    "shader.klproj": {
      "errors": [...],
      "warnings": [...],
      "info": {...}
    }
  }
}
```

### multipass_isf_shaders.json (find_shaders.py)
```json
{
  "multipass": [
    {
      "path": "/path/to/shader.fs",
      "passes": [...],
      "description": "...",
      "categories": ["Cat1", "Cat2"]
    }
  ],
  "single_pass": ["/path/to/single.fs", ...],
  "summary": {
    "total": 1000,
    "total_multipass": 100,
    "total_single_pass": 900
  }
}
```

## Tips

1. **Start small**: Test with `--random 5` before running large batches
2. **Use --quiet**: For scripts/automation, suppress progress output
3. **Check JSON**: Use `jq` to parse and filter JSON results
4. **ISF source**: Provide `--isf-source` for better undefined variable analysis
5. **Overwrite carefully**: Use `--overwrite` cautiously to avoid losing work

## Future Enhancements

Potential additions:
- CLI plugin integration (`klproj batch-convert`, `klproj analyze`, etc.)
- Configuration file support (`.klprojrc`)
- Parallel processing for large batches
- Additional analysis checks (performance heuristics, shader complexity)
- Web UI for result visualization

## Contributing

When adding new features:
1. Add functionality to appropriate utility module (`src/klproj/utils/`)
2. Update or create tool in `tools/` that uses the utility
3. Update this README with examples
4. Add tests in `tests/`
