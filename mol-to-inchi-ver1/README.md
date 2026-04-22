# mol-to-inchi

A modular AI skill set for generating InChI from MOL files.

## Overview

This skill set teaches AI agents how to implement InChI generation from MOL file input through to the final InChI string. Each stage corresponds to a pipeline step in the InChI generation process.

## Pipeline Stages

| Stage | Skill | Description |
|-------|-------|-------------|
| 1 | 01-parse-mol | Parse MOL V2000/V3000 → internal structure |
| 2 | 02-normalize | Valency correction, protonation |
| 3 | 03-canonicalize | Morgan algorithm, graph canonicalization |
| 4 | 04-stereochemistry | Stereo parity, /b /t /s layers |
| 5 | 05-tautomerism | Mobile H handling |
| 6 | 06-ring-detection | Cycle finding, SSR |
| 7 | 07-assemble | Build InChI string from processed data |
| 8 | 08-output | InChI/InChIKey formatting |

## Usage

Each skill can be used independently or as part of the full pipeline. For a complete walkthrough, start with TUTORIAL.md.

## Quick Start

1. Read TUTORIAL.md for end-to-end understanding
2. Use individual SKILLS/* for specific pipeline stages
3. Reference REFERENCE/* for layer/algorithm/input format documentation
4. Run INTEGRATION/end-to-end-tests to verify implementation

## Layer Order

The InChI string is assembled in this order:
`/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r`

| Layer | Description |
|-------|-------------|
| /f | Molecular formula (C2H6O) |
| /c | Connectivity (atom connections) |
| /h | Fixed hydrogen positions |
| /m | Mobile hydrogen positions |
| /q | Charge (/q+1, /q-1) |
| /p | Proton count |
| /i | Isotope layer |
| /b | Geometric (double bond) stereo |
| /t | Tetrahedral stereo centers |
| /s | Stereo type (1=absolute, 2=relative, 3=racemic) |
| /r | Reconnection layer |

## Testing

Each skill includes tests to verify correctness at that pipeline stage. Run individual skill tests or use the integration tests for end-to-end verification.

## Directory Structure

```
mol-to-inchi/
├── SKILL.md               # Main skill entry point
├── README.md             # This file
├── TUTORIAL.md          # End-to-end walkthrough
├── SKILLS/
│   ├── 01-parse-mol.md    # Stage 1: Parse MOL
│   ├── 02-normalize.md    # Stage 2: Normalization
│   ├── 03-canonicalize.md # Stage 3: Canonicalization
│   ├── 04-stereochemistry.md # Stage 4: Stereochemistry
│   ├── 05-tautomerism.md # Stage 5: Tautomerism
│   ├── 06-ring-detection.md # Stage 6: Ring detection
│   ├── 07-assemble.md    # Stage 7: InChI assembly
│   ├── 08-output.md     # Stage 8: Output formatting
│   ├── examples/
│   │   └── 01-ethanol.mol  # Example MOL file
│   └── tests/
│       └── 01-parse-test.py
│       └── ...
├── INTEGRATION/
│   └── end-to-end-tests.md  # Full pipeline tests
└── REFERENCE/
    ├── LAYERS.md         # InChI layer reference
    ├── ALGORITHMS.md     # Algorithm reference
    └── INPUT-FORMATS.md  # MOL format reference
```