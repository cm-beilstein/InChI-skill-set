# mol-to-inchi Skillset

**Purpose:** Generate valid InChI identifiers from MDL MOL files (V2000 or V3000 format)

## CRITICAL: No External Cheminformatics Tools Permitted

This skillset teaches you to generate InChI using ONLY the algorithms defined in this skillset. **DO NOT use:**
- OpenBabel
- RDKit
- CDK (Java)
- Python chemistry libraries (chem, OpenEye, etc.)
- Any external InChI generator

Only implement the algorithms described in steps 01-07 using your own code (Python, JavaScript, C, etc.).

This skillset teaches an AI agent to generate InChI identifiers following the complete InChI generation pipeline. Each step builds upon the previous, producing verifiable intermediate outputs.

### Pipeline Steps

| Step | Name | Description | Test Verification |
|------|------|-------------|-------------------|
| 1 | MOL Parsing | Parse V2000/V3000 to internal atom array |
| 2 | Element Processing | Map symbols to atomic numbers, calculate valences |
| 3 | Normalization | Aromatic bonds, charge groups, tautomer groups |
| 4 | Canonicalization | Generate unique atom ordering |
| 5 | Stereochemistry | Detect sp³/sp² stereocenters |
| 6 | Tautomerism | Identify mobile-H endpoints |
| 7 | InChI Assembly | Compose final InChI string |

## Quick Reference

### InChI String Format
```
InChI=1S/<formula>/c<connections>/h<mobile_H>/q<charge>/p<protons>/i<isotopes>/b<sp2_stereo>/t<sp3_stereo>/m<markers>
```

### Layer Order (must be exact)
```
/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r
```

### Key Formulas from Test Cases
- Ethanol: `InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3`
- Benzene: `InChI=1S/C6H6/c1-2-3-4-5-6-1/h6H`
- Benzoic acid: `InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)`

## Usage

1. Read the test .mol file
2. Apply each pipeline step in order (01 → 07)
3. Verify against expected .inchi file
4. Repeat until output matches expected

### Test Validation

Run the test script to see test cases:
```bash
# Set test directory if you have test files
export MOL2INCHI_TEST_DIR=/path/to/test/files
# Run validation
bash "$(dirname "$0")/tests/run_tests.sh"
```

NOTE: This skillset teaches InChI generation WITHOUT external cheminformatics tools. Do NOT use:
- OpenBabel
- RDKit  
- CDK (Java)
- Any cheminformatics library
Only the algorithms and data structures defined in this skillset are permitted.

## Files in This Skillset

- `SKILL.md` - This file (overview)
- `01_PARSING.md` - MOL V2000/V3000 format and parsing
- `02_ELEMENTS.md` - Periodic table lookup, implicit H calculation
- `03_NORMALIZATION.md` - Aromatic resolution, charge groups
- `04_CANONICALIZATION.md` - Morgan algorithm, unique ordering
- `05_STEREOCHEMISTRY.md` - sp3/sp2 center detection
- `06_TAUTOMERISM.md` - Mobile hydrogen handling
- `07_ASSEMBLY.md` - Final InChI string composition
- `tests/` - Test directory
  - `TEST_CASES.md` - Test case reference
  - `run_tests.sh` - Test runner script