# InChI Skill Set

A skillset for teaching AI agents to generate valid InChI identifiers from MDL MOL files using pure algorithms — without external cheminformatics libraries.

## What Is This?

This project contains attempts at creating an InChI skill set for AI agents. There are currently 2 attempts:

- **mol-to-inchi-ver1/** — First attempt at the skill
- **mol-to-inchi-ver2/** — Second attempt (refined approach)

Each version contains step-by-step documentation for implementing InChI generation from MOL files (V2000/V3000 format), covering:

1. **MOL Parsing** — Parse V2000/V3000 to internal atom array
2. **Element Processing** — Map symbols to atomic numbers, calculate valences
3. **Normalization** — Aromatic bonds, charge groups, tautomer groups
4. **Canonicalization** — Generate unique atom ordering (Morgan algorithm)
5. **Stereochemistry** — Detect sp³/sp² stereocenters
6. **Tautomerism** — Identify mobile-H endpoints
7. **Assembly** — Compose final InChI string

## InChI String Format

```
InChI=1S/<formula>/c<connections>/h<mobile_H>/q<charge>/p<protons>/i<isotopes>/b<sp2_stereo>/t<sp3_stereo>/m<markers>
```

Layer order: `/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r`

## Project Structure

```
InChI-skill-set/
├── mol-to-inchi-ver1/      # First attempt
├── mol-to-inchi-ver2/      # Second attempt
├── data/                  # .mol and .inchi files
└── README.md
```

## Data Folder

The `data/` folder contains paired `.mol` molecule files and their corresponding `.inchi` reference files for testing and validation.

## CRITICAL: No External Tools

This skillset teaches generation **without** cheminformatics libraries. Do NOT use:
- OpenBabel
- RDKit
- CDK
- Python chemistry libraries

Only implement the algorithms described in the skill documentation.

## Quick Start

1. Read `mol-to-inchi-ver2/SKILL.md` for the overview (latest attempt)
2. Follow steps 01-07 in order
3. Verify against test cases in `data/` folder

## License

MIT