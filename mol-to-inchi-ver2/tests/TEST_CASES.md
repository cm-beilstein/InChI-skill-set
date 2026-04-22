# Test Cases for mol-to-inchi Skillset

## Running Tests

Test files should be in a directory specified by `MOL2INCHI_TEST_DIR` environment variable, or provide test `.mol` and `.inchi` files alongside your query.

Each test has a `.mol` file and corresponding `.inchi` file.

## Expected Results

| Mol File | Expected InChI |
|---------|----------------|
| 01-ethanol.mol | InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3 |
| 65-85-0-2d.mol | InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9) |
| CHEBI_140096.mol | See below |
| Fe_N2X.mol | See below |
| Life_Science_0001.mol | ... |
| Life_Science_0002.mol | ... |
| Life_Science_0003.mol | ... |
| Life_Science_0004.mol | ... |
| Life_Science_0005.mol | ... |

## Test Verification Protocol

1. Read `.mol` file
2. Apply pipeline steps 1-7
3. Compare output to corresponding `.inchi` file
4. Debug any mismatches using the step-by-step documentation

## Known Test Cases

### Test 1: Ethanol (01-ethanol.mol)

Input: Simple alcohol C2H6O
Expected: `InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3`

Pipeline:
1. Parse: 9 atoms, 8 bonds (V2000)
2. Elements: C, C, O + H, process 3 C atoms (2 explicit, 6 H)
3. Normalization: Simple, no aromatic/charge groups
4. Canonical: O first, then CH2, then CH3
5. Stereo: None
6. Tautomer: None (alcohol)
7. Assembly: /c1-2-3, /h3H,2H2,1H3

### Test 2: Benzoic Acid (65-85-0-2d.mol)

Input: Aromatic carboxylic acid C7H6O2
Expected: `InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)`

Pipeline differences from ethanol:
1. Parse: 9 atoms, 9 bonds
2. Elements: 7 C, 2 O, explicit H
3. Normalization: Aromatic ring → alternating bonds, carboxyl tautomer
4. Canonical: Ring canonical order
5. Stereo: None (aromatic)
6. Tautomer: OH group mobile
7. Assembly: /c includes ring closure 8-7(9)6...

### Test 3: Iron Complex (Fe_N2X.mol)

Input: Iron complex with nitrogen ligands
Expected: Check corresponding .inchi file

Pipeline challenges:
- Metal coordination bonds
- Charge handling
- Possible disconnected components

## Validation Checklist

For each test, verify:

- [ ] Correct atom count
- [ ] Correct bond count  
- [ ] Element symbols mapped to atomic numbers
- [ ] Implicit H calculated
- [ ] Aromatic bonds resolved (if applicable)
- [ ] Canonical ordering stable
- [ ] Connection layer correct
- [ ] Mobile-H layer correct (if applicable)
- [ ] Charge layer correct (if applicable)
- [ ] Full InChI matches expected

## Debugging Failed Tests

If InChI doesn't match expected:

1. Check formula layer first - should be C#H# elements
2. Check connection layer - bond connectivity must be correct
3. Check hydrogen counts in /h layer
4. Verify no extra layers added

## Test Generator

To add more tests:

1. Add .mol file to test directory
2. Generate .inchi file using reference InChI generator
3. Add entry to table above
4. Verify your algorithm matches