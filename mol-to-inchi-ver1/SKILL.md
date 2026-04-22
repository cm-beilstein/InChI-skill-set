# mol-to-inchi Skill Set

A modular AI skill set for generating InChI from MOL files.

## Overview

This skill set teaches AI agents how to implement InChI generation from MOL file input through to the final InChI string. Each stage corresponds to a pipeline step in the InChI generation process.

## Pipeline Stages

| Stage | File | Description |
|-------|------|-------------|
| 1 | 01-parse-mol | Parse MOL V2000/V3000 → internal structure |
| 2 | 02-normalize | Valency correction, protonation |
| 3 | 03-canonicalize | Morgan algorithm, graph canonicalization |
| 4 | 04-stereochemistry | Stereo parity, /b /t /s layers |
| 5 | 05-tautomerism | Mobile H handling |
| 6 | 06-ring-detection | Cycle finding, SSR |
| 7 | 07-assemble | Build InChI string from processed data |
| 8 | 08-output | InChI/InChIKey formatting |

## Usage

### Complete Pipeline

For a complete walkthrough, use TUTORIAL.md.

### Individual Stages

Each SKILLS/*.md file can be used independently:
1. Read the skill for the pipeline stage
2. Use examples/*.mol for test input
3. Run tests in tests/*-test.py to verify

### Reference

Use REFERENCE/*.md for detailed documentation:
- LAYERS.md: InChI layer format
- ALGORITHMS.md: Algorithm details
- INPUT-FORMATS.md: MOL file format

## Testing

```python
# Stage tests
pytest skills/mol-to-inchi/SKILLS/tests/01-parse-test.py -v
# ... additional stages

# Integration tests
pytest skills/mol-to-inchi/INTEGRATION/end-to-end-tests.md -v
```

## Directory Structure

```
mol-to-inchi/
├── SKILL.md              # This file
├── README.md             # Overview
├── TUTORIAL.md          # End-to-end walkthrough
├── SKILLS/
│   ├── 01-parse-mol.md
│   ├── 02-normalize.md
│   ├── 03-canonicalize.md
│   ├── 04-stereochemistry.md
│   ├── 05-tautomerism.md
│   ├── 06-ring-detection.md
│   ├── 07-assemble.md
│   ├── 08-output.md
│   ├── examples/
│   │   └── 01-ethanol.mol
│   └── tests/
│       └── *-test.py
├── INTEGRATION/
│   └── end-to-end-tests.md
└── REFERENCE/
    ├── LAYERS.md
    ├── ALGORITHMS.md
    └── INPUT-FORMATS.md
```