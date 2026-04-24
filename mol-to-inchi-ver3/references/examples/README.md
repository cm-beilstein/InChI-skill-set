# Verified MOL/InChI Example Pairs

Use these to verify reasoning. Parse the mol file through the pipeline, then check your output against the expected InChI.

| File | Key Features |
|------|-------------|
| `01-ethanol.mol` | Simple 2-carbon chain, explicit H atoms, C-OH bond |
| `65-85-0-2d.mol` | Small molecule, simple structure |
| `Life_Science_0003.mol` | Sulfonamide, multiple heteroatoms, tautomeric |
| `CHEBI_140096.mol` | Large complex molecule (32 C atoms), multiple rings, sp3 stereo |
| `ci5c02720_si_002_0005.mol` | Medium complex, stereochemistry |
| `ci5c02720_si_002_0001.inchi` | Corresponding InChI for _0005.mol |
| `Test_set_enhanced_stereo_0009.mol` | V3000 format, enhanced stereo (STEABS, STEREL, STERAC collections) |
| `atropisomers_test_file_1_v2_0050.mol` | Atropisomerism (hindered rotation) |
| `Structure_drawings_0016.inchi` | No mol file — just the InChI for reference |

Workflow:
1. Read the mol file and parse it
2. Walk through each pipeline step in SKILL.md
3. Generate the InChI string
4. Compare against the corresponding `.inchi` file
5. If mismatch, review which step caused the error and re-reason