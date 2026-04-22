# Step 7: InChI Assembly

**Input:** All processed layers from previous steps
**Output:** Complete InChI string

> **CRITICAL:** Assemble the InChI string yourself using the format specified below. Do NOT use library functions to format the output.

## InChI String Structure

```
InChI=1S/<formula>/<connections>/<mobile_H>/<charge>/<protons>/<isotopes>/<stereo>/<markers>
```

Each layer is optional and omitted if empty.

## Layer Assembly Order

Must follow this exact order (from InChI Technical Manual):

```
/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r
```

## Assembling Each Layer

### 1. Formula Layer `/f`

```
Hill formula: C first, then H, then alphabetical
Examples: C2H6O, C6H6, C7H6O2
```

### 2. Connections Layer `/c`

```
Format: /c<atoms and bonds>

Ethanol: /c1-2-3       (atom 1 connects to 2; 2 connects to 3)
Benzene: /c1-2-3-4-5-6-1  (ring closure)
Multiple: /c1-2,3-4  (disconnected components)
```

### 3. Mobile-H Layer `/h`

```
Format: /h<positions>

Simple: /h3H              (3 H on position 1)
Comma-separated: /h3H,2H2     (3 H at pos1, 2 H at pos2)
With mobile: /h1+1c2         (add 1 mobile H at pos2, has charge)
```

### 4. Charge Layer `/q`

```
Format: /q<charge>

Examples: /q+1, /q-1, /q+2
```

### 5. Removed Protons Layer `/p`

```
Format: /p<count>

Examples: /p+1 (removed 1 proton), /p-1 (added 1)
Note: /p layer is different from /h (mobile H)
```

### 6. Isotope Layer `/i`

```
Format: /i<position><sign><count><element>

Examples: /i1+1D   (deuterium at pos 1)
         /i2-1C13  (C-13 at pos 2)
```

### 7. Stereo Layers

**sp2 (double bond):**
```
/b<parity>
/b1-   = trans/E
/b1+   = cis/Z
```

**sp3 (tetrahedral):**
```
/t<parity>
/t3-   = R/S parity, minus
/t3+   = R/S parity, plus
```

**Stereo markers:**
```
/s    = absolute (default)
/sABS  = absolute
/sREL  = relative
/sRAC  = racemic (unknown)
```

## Example Assembly

### Ethanol (C2H6O)

```
Step 1: Formula        = C2H6O
Step 2: Connections   = 1-2-3 (O-C-C, ring closed)
Step 3: Mobile-H      = 3H,2H2,1H3
Step 4: Charge         = (none)
Step 5: Stereo        = (none)

Result: InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3
```

### Benzoic Acid (C7H6O2)

```
Formula:     C7H6O2
Connections: 8-7(9)6-4-2-1-3-5-6
Mobile-H:   1-5H,(H,8,9)    # (H,8,9) means mobile to those positions

Result: InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)
```

### Benzene (C6H6)

```
Formula:     C6H6
Connections: 1-2-3-4-5-6-1
Mobile-H:    6H

Result: InChI=1S/C6H6/c1-2-3-4-5-6-1/h6H
```

## Compression Notation

InChI uses shorthand:
- `3H` means 3 hydrogens (no comma needed when consecutive)
- Range notation: `1-6H` means H on positions 1 through 6
- `h1-6H` same but in /h layer

## Edge Cases

### Single Atom
```
Cl-  → InChI=1S/Cl
Na+  → InChI=1S/Na
```

### Disconnected Components
```
Cu(II) complex with 2 ligands → InChI=1S/C4H12N2.Cu/c1-4-2-3;/h1-4H;/Cu+2/
```

### Isotopic
```
CD3OD → InChI=1S/CH4O/c1-2/h2H,1H3/i1+1D
```

## Verification

Compare assembled InChI to expected .inchi file:
```bash
diff <(generate_inchi input.mol) expected.inchi
```

## Next Steps

After assembly:
1. Verify against test cases
2. If mismatch, debug earlier step
3. Return to appropriate step for fixes

## Full Pipeline Summary

```
MOL file → Parse → Elements → Normalize → Canonicalize → Stereo → Tautomer → Assemble → InChI
```

Each step is verified before proceeding.

## Test File List

Test files should be in directory specified by environment variable `MOL2INCHI_TEST_DIR` or provided alongside your query.

| Test File | Expected InChI |
|-----------|---------------|
| 01-ethanol.mol | InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3 |
| 65-85-0-2d.mol | InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9) |
| (etc.) | Match corresponding .inchi file |