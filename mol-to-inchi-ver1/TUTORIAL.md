# mol-to-inchi Tutorial

## End-to-End Walkthrough

This tutorial walks through generating an InChI from a MOL file, covering each pipeline stage.

## Prerequisites

- Understanding of chemical graph representation
- Familiarity with InChI layer structure
- Basic understanding of valency rules

## Example Molecule: Ethanol (C2H5OH)

### Input MOL (V2000)

```
  -OEChem-04222603522D

  9  8  0     0  0  0  0  0  0999 V2000
      3.7321    0.2500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
      2.8660   -0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
      2.0000    0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
      2.4675   -0.7249    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      3.2646   -0.7249    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      2.3100    0.7869    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      1.4631    0.5600    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      1.6900   -0.2869    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      4.2690   -0.0600    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  9  1  0  0  0  0
  2  3  1  0  0  0  0
  2  4  1  0  0  0  0
  2  5  1  0  0  0  0
  3  6  1  0  0  0  0
  3  7  1  0  0  0  0
  3  8  1  0  0  0  0
M  END
```

Parsed structure shows: 9 atoms (O, 2C, 6H), 8 bonds.

### Stage-by-Stage Execution

---

## Stage 1: Parse MOL File

**Input:** MOL V2000 file
**Output:** Internal chemical graph structure

```
parsed = {
    "atoms": [
        {"id": 1, "element": "O", "x": 3.7321, "y": 0.25, "z": 0.0, "charge": 0},
        {"id": 2, "element": "C", "x": 2.866, "y": -0.25, "z": 0.0, "charge": 0},
        {"id": 3, "element": "C", "x": 2.0, "y": 0.25, "z": 0.0, "charge": 0},
        {"id": 4, "element": "H", "x": 2.4675, "y": -0.7249, "z": 0.0, "charge": 0},
        {"id": 5, "element": "H", "x": 3.2646, "y": -0.7249, "z": 0.0, "charge": 0},
        {"id": 6, "element": "H", "x": 2.31, "y": 0.7869, "z": 0.0, "charge": 0},
        {"id": 7, "element": "H", "x": 1.4631, "y": 0.56, "z": 0.0, "charge": 0},
        {"id": 8, "element": "H", "x": 1.69, "y": -0.2869, "z": 0.0, "charge": 0},
        {"id": 9, "element": "H", "x": 4.269, "y": -0.06, "z": 0.0, "charge": 0}
    ],
    "bonds": [
        {"source": 1, "target": 2, "order": 1},
        {"source": 1, "target": 9, "order": 1},
        {"source": 2, "target": 3, "order": 1},
        {"source": 2, "target": 4, "order": 1},
        {"source": 2, "target": 5, "order": 1},
        {"source": 3, "target": 6, "order": 1},
        {"source": 3, "target": 7, "order": 1},
        {"source": 3, "target": 8, "order": 1}
    ]
}
```

---

## Stage 2: Normalize

**Input:** Parsed atoms and bonds
**Output:** Normalized structure with corrected valencies

Ethanol already has correct valencies (C=4, O=2, H=1), so no changes needed.

```
normalized = {
    "atoms": [same as parsed],
    "bonds": [same as parsed]
}
```

---

## Stage 3: Canonicalize

**Input:** Normalized chemical graph
**Output:** Canonical labels

Using the Morgan algorithm, assign unique labels to each atom:

```
canonical = {
    "C1": 1,  # First carbon
    "C2": 2,  # Second carbon  
    "O": 3,  # Oxygen
    "H": 4    # Hydrogen
}
```

Result: Atoms labeled with their canonical order (starting from 1).

---

## Stage 4: Stereochemistry

**Input:** Canonicalized graph
**Output:** Stereo information

Ethanol has no stereocenters (chiral atoms) and no geometric (double bond) stereo.

```
stereo = {
    "tetrahedral": [],  # No sp3 chiral centers
    "geometric": [],  # No E/Z double bonds
    "type": None      # No stereo
}
```

---

## Stage 5: Tautomerism

**Input:** Normalized graph
**Output:** Mobile hydrogen information

Ethanol has one hydroxyl hydrogen, but it's not mobile (fixed position).

```
tautomer = {
    "mobile_h": []  # No mobile H positions
}
```

---

## Stage 6: Ring Detection

**Input:** Chemical graph
**Output:** Ring information

Ethanol is acyclic (no rings).

```
rings = {
    "ring_count": 0,
    "sssr": []  # No smallest set of smallest rings
}
```

---

## Stage 7: Assemble InChI

**Input:** All layer data
**Output:** InChI string

Layer assembly order: `/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r`

For ethanol:
- /f: C2H6O (formula)
- /c: 1-2 (connectivity: C1 connected to C2)
- /h: (H on atom 3, which is O)
- /m: (no mobile H)
- /q: (no charge)
- /p: (proton count implicit in formula)
- /i: (no isotopes)
- /b: (no geometric stereo)
- /t: (no tetrahedral stereo)
- /s: (no stereo type)
- /r: (no reconnection layer)

```
InChI base string: InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)
```

---

## Stage 8: Output

**Input:** Base InChI string
**Output:** Formatted InChI and InChIKey

Final output:
- InChI: `InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)`
- InChIKey: `LFQSCWFLJHTTHZ-UHFFFAOYSA-N`

---

## Another Example: Caffeine

### Input MOL (simplified)

Caffeine is C8H10N4O2 - more complex with rings and nitrogen atoms.

### Pipeline execution summary:

1. **Parse:** 24 atoms (8C, 10H, 4N, 2O), multiple bonds
2. **Normalize:** Correct N valencies (some N need +1 charge)
3. **Canonicalize:** Unique labels for all 24 atoms
4. **Stereochemistry:** No chiral centers
5. **Tautomerism:** Methyl groups can migrate - /m layer
6. **Ring Detection:** 2 rings detected (6-membered purine rings)
7. **Assemble:** Complete InChI with /f, /c, /m, /r layers
8. **Output:** InChI=1S/C8H10N4O2/c1-12-6(13)8(14)3(15)5(16)7(17)10(12)2-4/

### Expected Output

```
InChI=1S/C8H10N4O2/c1-12-6(13)8(14)3(15)5(16)7(17)10(12)2-4/h3H,2H2,1H3
```

---

## Common Issues and Solutions

| Issue | Stage | Solution |
|-------|-------|----------|
| Valency errors | Normalize | Check element valency table, add/remove electrons |
| Wrong connectivity | Canonicalize | Verify Morgan algorithm iteration |
| Missing stereo | Stereochemistry | Check all sp2 and sp3 centers |
| Mobile H wrong | Tautomerism | Verify tautomer rules for N, O, S |
| Rings missing | Ring Detection | Use SSSR algorithm |

## Testing Your Implementation

Run tests at each stage:

```python
# Test stage 1: Parse
assert len(parsed["atoms"]) == 4

# Test stage 2: Normalize
assert normalized["atoms"][2]["element"] == "O"

# Test stage 3: Canonicalize
assert canonical_labels[1] == 1
```

Integration test:
```python
result = mol_to_inchi("ethanol.mol")
assert result == "InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)"
```