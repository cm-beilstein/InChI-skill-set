# InChI Skill Set

A skillset for teaching AI agents to generate valid InChI identifiers from MDL MOL files using pure algorithms — without external cheminformatics libraries.

## What Is This?

This project contains a step-by-step skill for implementing InChI generation from MOL files (V2000/V3000 format). It covers the complete InChI generation pipeline:

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
├── mol-to-inchi-ver2/      # Main skill documentation
│   ├── SKILL.md           # Overview
│   ├── 01_PARSING.md      # MOL file parsing
│   ├── 02_ELEMENTS.md    # Element processing
│   ├── 03_NORMALIZATION.md
│   ├── 04_CANONICALIZATION.md
│   ├── 05_STEREOCHEMISTRY.md
│   ├── 06_TAUTOMERISM.md
│   ├── 07_ASSEMBLY.md
│   └── tests/
│       ├── TEST_CASES.md
│       └── run_tests.sh
├── inchi_examples/        # Sample .inchi files
├── dataset_for_skillset/   # Training data (.sdf, .mol files)
└── README.md
```

## CRITICAL: No External Tools

This skillset teaches generation **without** cheminformatics libraries. Do NOT use:
- OpenBabel
- RDKit
- CDK
- Python chemistry libraries

Only implement the algorithms described in the skill documentation.

## Example Outputs

| Molecule | InChI |
|----------|-------|
| Ethanol | `InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3` |
| Benzene | `InChI=1S/C6H6/c1-2-3-4-5-6-1/h6H` |
| Benzoic acid | `InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)` |

## Quick Start

1. Read `mol-to-inchi-ver2/SKILL.md` for the overview
2. Follow steps 01-07 in order
3. Verify against test cases in `mol-to-inchi-ver2/tests/TEST_CASES.md`

## License

MIT