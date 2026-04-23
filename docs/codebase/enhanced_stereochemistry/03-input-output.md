# Enhanced Stereochemistry - Input and Output

**Analysis Date:** 2026-04-23

---

## Input: V3000 Molfile Format

Enhanced stereochemistry is specified in V3000 molfiles using the **Collection Block**.

### Collection Block Structure

```
M  V30 BEGIN COLLECTION
M  V30 MDLV30/STEABS ATOMS=(n atom [atom ...])
M  V30 MDLV30/STERELn ATOMS=(n atom [atom ...])
M  V30 MDLV30/STERACn ATOMS=(n atom [atom ...])
M  V30 END COLLECTION
```

### Examples

#### Absolute Stereogroup

```
M  V30 BEGIN COLLECTION
M  V30 MDLV30/STEABS ATOMS=(4 1 2 3 4)
M  V30 END COLLECTION
```

Atoms 1,2,3,4 belong to one absolute stereogroup.

#### Relative Stereogroup

```
M  V30 BEGIN COLLECTION
M  V30 MDLV30/STEREL1 ATOMS=(2 5 6)
M  V30 MDLV30/STEREL2 ATOMS=(2 7 8)
M  V30 END COLLECTION
```

Two relative groups: atoms 5-6 are related, atoms 7-8 are related.

#### Racemic Stereogroup

```
M  V30 BEGIN COLLECTION
M  V30 MDLV30/STERAC1 ATOMS=(1 3)
M  V30 END COLLECTION
```

Atom 3 is in a racemic (undefined) group.

---

## Input: Command Line

### CLI Options

```
inchi-1 <input.mol> [-EnhancedStereochemistry | --EnhancedStereochemistry]
```

The `-EnhancedStereochemistry` flag enables enhanced stereochemistry processing:

```bash
# Process with enhanced stereo
inchi-1 mymolecule.mol -EnhancedStereochemistry -o mymolecule.inchi

# Verbose output
inchi-1 mymolecule.mol -EnhancedStereochemistry -o mymolecule.inchi -v
```

### Combined Options

```bash
# Max output with enhanced stereo
inchi-1 mymol.mol -EnhancedStereochemistry -SLUUD -o out.txt

# Fixed H with enhanced stereo
inchi-1 mymol.mol -EnhancedStereochemistry -FixedH -o fixedh.txt
```

---

## Input: API Usage

### Setting the Flag

```c
#include "inchi_dll_a2.h"

// Create input
struct InputStruct *inp = AllocateInchiInput();

SetInputFile(inp, "mymol.mol");

// Enable enhanced stereochemistry
INPUT_PARMS *ip = get_ip(inp);
ip->bEnhancedStereo = 1;

// Generate InChI
INCHI_IOSTREAM output;
Process(inp, &output);
```

### Checking Results

```c
// After processing, stereo is in the INChI_Stereo struct
for (int i = 0; i < pINChI->Stereo->nNumberOfStereoCenters; i++) {
    printf("Atom %d: parity %d\n",
           pINChI->Stereo->nNumber[i],
           pINChI->Stereo->t_parity[i]);
}
```

---

## Output: InChI String Format

### Standard Enhanced Stereo Output

```
InChI=1S/C10H14BrCl7/c1-3(11)5(13)7(15)9(17)10(18)8(16)6(14)4(2)12/h3-10H,1-2H3/t3-,4-,5+,6-,7-,8-,9+,10-/m0/s1(3,5)2(4)(6,8)3(7,9)(10)
```

Breaking this down:
- `/c1-3(11)5(13)...` = Formula layer with isotope markers
- `/h3-10H,1-2H2` = Hydrogen layer
- `/t3-,4-,5+,6-,7-,8-,9+,10-` = Tetrahedral centers with parities (R/S)
- `/m0` = Mobile-H inversion flag (0 = absolute, not inverted)
- **`/s1(3,5)2(4)(6,8)3(7,9)(10)`** = Enhanced stereo groups (CRITICAL format!)

### S-Layer Detailed Format

The `/s` layer (stereo groups layer) contains explicit atom lists:

| Component | Meaning | Example |
|-----------|----------|---------|
| `s1(...)` | Absolute (STEABS) - appears once | `s1(3,5)` |
| `s2(...)` | Relative (STERELn) - **can have multiple** as `s2(atoms)(atoms)...` | `s2(4)(6,8)` |
| `s3(...)` | Racemic (STERACn) - **can have multiple** as `s3(atoms)(atoms)...` | `s3(7,9)(10)` |

**Key Points:**
1. ONE `s` at beginning (`/s`), then all groups concatenated
2. Each group type (1, 2, 3) prefixed with its number
3. Multiple groups of same type are separate parenthetical entries (no commas)

### Format Examples

**Single STEABS group:**
```
/s1(3,5)
```

**Multiple STEREL groups:**
```
/s2(4)(6,8)
```
This means STEREL1 contains atom 4, STEREL2 contains atoms 6,8.

**Multiple STERAC groups:**
```
/s3(7,9)(10)
```
This means STERAC1 contains atoms 7,9, STERAC2 contains atom 10.

**Mixed types:**
```
/s1(3,5)2(4)(6,8)3(7,9)(10)
```
- STEABS: atoms 3,5
- STEREL1: atom 4
- STEREL2: atoms 6,8
- STERAC1: atoms 7,9
- STERAC2: atom 10

---

## Error Handling

### Invalid Collection Tags

If an unknown collection tag is encountered:

```
Warning: Unknown collection tag "CUSTOM/TAG"
Ignoring collection block
```

### Mismatched Atoms

If atoms referenced in collection don't exist:

```
Error: Collection references non-existent atom 25
```

---

## References

- InChI Technical Manual: Section 10
- `mol_fmt3.c`: Lines 695-780
- `ichiprt1.c`: Lines 3508-3600

---

*Input/Output: 2026-04-23*