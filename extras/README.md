# Extras Directory

This directory contains additional resources, tools, and analysis files that supported the development of the `klproj` library but are not essential for using it.

## Contents

### Tools (`tools/`)

Legacy Python scripts that were used during development:

- **`klproj_generator.py`** - Original monolithic generator script (now refactored into `src/klproj/`)
- **`extract_klproj.py`** - Tool for extracting `.klproj` files to XML
- **`verify_klproj.py`** - Tool for verifying `.klproj` file contents
- **`examples/`** - Original example scripts (preserved for reference)

These tools have been superseded by the main `klproj` package and CLI, but are kept here for reference and historical purposes.

### Format Analysis (`kodelife-format-analysis/`)

XML extracts from various KodeLife project files used to understand the `.klproj` format:

- `shadertoy.xml` - Shadertoy-compatible shader example
- `audio-input.xml` - Audio input shader example
- `midi-input.xml` - MIDI input example
- `compute-mandelbrot.xml` - Compute shader example
- `spectrum-*.xml` - Audio spectrum shader examples

These files were instrumental in understanding the KodeLife project file format and informed the design of the `klproj` library.

### Documentation

- **`EXTRACTION_SUMMARY.md`** - Summary of the extraction process
- **`FINDINGS_kodelife_examples_analysis.md`** - Analysis findings
- **`KLPROJ_GENERATOR_GUIDE.md`** - Original generator guide
- **`KODELIFE_FORMAT_SUMMARY.md`** - Format specification summary

## Why "Extras"?

These files are valuable for:

- Understanding the project's development history
- Reference when extending the library
- Learning about the KodeLife file format
- Debugging edge cases

However, they're not needed for normal use of the `klproj` library, so they're kept separate from the main project structure.

## Using Legacy Tools

If you want to use the legacy tools directly:

```bash
cd extras/tools
python extract_klproj.py input.klproj output.xml
python verify_klproj.py file.klproj
```

**Note:** The new CLI tools in the main package are recommended instead:

```bash
klproj extract input.klproj output.xml
klproj verify file.klproj
```

## Format Analysis

The XML files in `kodelife-format-analysis/` can be studied to understand:

- XML structure of `.klproj` files
- Parameter types and their properties
- Shader stage configurations
- Render state options
- Multi-pass setups

Open them in any text editor to explore the KodeLife project format.
