# Fixed-H Layer (`/h`)

**Analysis Date:** 2026-04-22

## Overview

The Fixed-H layer (`/h`) represents **non-mobile (immobile) hydrogen atoms** in an InChI identifier. This layer captures terminal hydrogens that are permanently attached to their parent atoms and cannot participate in tautomeric shifts. These are hydrogen atoms that are NOT part of mobile groups—so named because they are "fixed" in position and do not move during tautomerization.

### Relationship to Formula Layer

The formula layer (`/f`) provides the complete molecular formula including all hydrogens. The Fixed-H layer extracts and explicitly represents only the non-tautomeric hydrogens—the ones that remain fixed on specific atoms. For tautomeric molecules, the relationship between `/f` and `/h` is critical:

- `/f` contains **all** hydrogen atoms in the molecule (formula)
- `/h` contains only the **terminal (non-mobile) hydrogens** attached to specific atoms
- Mobile/tauto-genic hydrogens are represented in the mobile hydrogen layer (`/m`) instead

### Output Format

The Fixed-H layer has two possible prefix conventions:

| Prefix | Layer Type | Description |
|--------|-----------|-------------|
| `/h` | Non-tautomeric | Immobile hydrogens in non-tautomeric representation |
| `/f/h` | Fixed-H (explicit) | Explicitly marked fixed hydrogens (when `/f` is present) |

**Examples:**
- `/h1,2` — Two immobile hydrogens on atoms 1 and 2 (single character each)
- `/h1,2-4` — One hydrogen on atom 1, two hydrogens on atom 4 (compressed format)

The numbers represent the count of hydrogen atoms attached to each canonical atom, in ascending order of canonical atom numbers. When a number exceeds single digits, the format expands: `1` = 1-9 hydrogens, `10-99` uses 2-3 characters, etc.

---

## Code Implementation

### Key Source Files

The Fixed-H layer implementation spans multiple source files in `INCHI-1-SRC/INCHI_BASE/src/`:

| File | Purpose |
|------|---------|
| `ichi.h` | Main INChI structure definitions (lines 232-235) |
| `ichicant.h` | CANON_STAT structure with nNum_H, nNum_H_fixed (line 329-330) |
| `ichimake.c` | Main InChI string generation, comparison, hashing |
| `ichicano.c` | Canonicalization logic for fixed H detection |
| `ichiread.c` | Parsing InChI strings (Fixed-H layer /f/h) |
| `strutil.c` | Memory allocation/deallocation for hydrogen arrays |

### Core Data Structures

#### INChI Structure (from `ichi.h`)

```c
// Lines 232-235
S_CHAR    *nNum_H;      // number of terminal hydrogen atoms on each atom; in tautomeric
                         // representation these H on tautomeric atoms are not included [nNumberOfAtoms]
S_CHAR    *nNum_H_fixed; // number of terminal hydrogen atoms on tautomeric atoms,
                         // in non-atautomeric representation only [nNumberOfAtoms]
```

#### CANON_STAT Structure (from `ichicant.h`)

```c
// Lines 329-330
S_CHAR* nNum_H;        // number of terminal hydrogen atoms on each atom except tautomeric [num_atoms], in order of canonical numbers
S_CHAR* nNum_H_fixed;  // number of terminal hydrogen atoms on tautomeric atoms (for non-atautomeric representation) [num_atoms]
```

#### Key Distinction

- **`nNum_H`**: Hydrogen count per atom in the **tautomeric representation** (excludes mobile H on tautomeric atoms)
- **`nNum_H_fixed`**: Hydrogen count on **tautomeric atoms** for the **non-tautomeric representation** only

When generating InChI with `bMobileH = TAUT_NON`, the code uses `nNum_H_fixed`. When `bMobileH = TAUT_YES`, it uses `nNum_H`.

#### F CTCN Structure (from `ichicant.h`)

```c
// Lines 173-174
NUM_H* nNumHFixH;      // canonical fixed positions of tautomeric H
int   nLenNumHFixH;    // length = num_atoms
```

This stores the canonical fixed positions of tautomeric hydrogen atoms.

### Initialization (from `strutil.c`)

```c
// Lines 7746-7747
(pINChI->nNum_H = (S_CHAR *)inchi_calloc(num_at, sizeof(pINChI->nNum_H[0]))) &&
(pINChI->nNum_H_fixed = (S_CHAR *)inchi_calloc(num_at, sizeof(pINChI->nNum_H_fixed[0])))
```

Memory is allocated for both arrays when creating an INChI structure.

### Tautomerization Flags

The codebase uses enumerated values to distinguish between representations:

```c
// Used throughout: TAUT_YES and TAUT_NON
// In ichiread.c line 8236:
#define nNum_H( ICOMPONENT ) ((bMobileH==TAUT_YES)? pInChI[ICOMPONENT].nNum_H : pInChI[ICOMPONENT].nNum_H_fixed)
```

This macro selects the appropriate hydrogen array based on whether mobile hydrogens are enabled.

---

## Pseudo-code Algorithm

### Fixed Hydrogen Detection

The detection of fixed (non-mobile) hydrogens involves:

```
1. For each atom in the molecule:
      a. Identify whether the atom participates in tautomerization
      b. Count hydrogens attached to this atom
      
2. If atom is NOT part of any tautomeric group:
      -> These hydrogens are FIXED (immobile)
      -> Store in nNum_H[] at the canonical index
      
3. If atom IS part of a tautomeric group:
      a. In TAUT_YES (mobile H) mode:
         -> The mobile hydrogens are tracked separately
         -> nNum_H[] excludes these atoms entirely
      b. In TAUT_NON (non-mobile H) mode:
         -> Fixed hydrogens on tautomeric atoms go to nNum_H_fixed[]
         -> These represent terminal H remaining on tautomeric atoms
```

### String Generation (from `ichimake.c`)

```c
// Line 2360-2362: MakeHString comment
// 1 character for each atom that has 1 terminal hydrogen atoms
// 2 characters  for each atom that has 2-9 terminal hydrogen atoms
// 3 characters  for each atom that has 10-99 terminal hydrogen atoms, etc.

// MakeHString function signature (from ichimake.h line 243)
int MakeHString( int bAddDelim,
                 S_CHAR *LinearCT,
                 int nLenCT,
                 INCHI_IOS_STRING *buf,
                 int nCtMode,
                 int *bOverflow );
```

### Parsing Fixed-H (from `ichiread.c`)

```c
// Line 8541: FixedH layer "/h"
if (bMobileH == TAUT_NON)    /* FixedH layer "/h"*/
    // Use nNum_H_fixed for storage
else                         /* Main layer (mobileH) "/h"*/
    // Use nNum_H for storage
```

The parser branches based on whether it's reading a Fixed-H layer (`/f/h`) vs. the mobile-H layer (`/h`).

---

## Examples

### Non-tautomeric Hydrogens

For **acetic acid** (CH₃COOH):

```
Input:    O=C(O)C
Formula:  C2H4O2
InChI:   InChI=1S/C2H4O2/c1-2(3)4/h1,3-4H,(H,3,4)
                           ^^^^^^^^
                           Fixed-H layer: atoms 1,3,4 are the O-H and one C-H
```

| Atom | Element | Attached H | Fixed/Mobile |
|------|---------|------------|-------------|
| C1 (carbonyl C) | C | 0 | Fixed (no H) |
| C2 (methyl C) | C | 3 | Fixed (all 3 are non-mobile) |
| O3 (carbonyl O) | O | 0 | Fixed (no H) |
| O4 (alcohol O) | O | 1 | FIXED (this is terminal/non-mobile) |

No tautomeric groups exist, so all hydrogens are fixed. The `/h` layer shows these.

### Tautomeric Case

For **acetoacetic acid** (CH₃COCH₂COOH) — this has a tautomeric equilibrium:

```
InChI=1S/C3H6O3/c1-3(5)6(7)8(4)2/h1-2H,4H2,3H2/t?/m0/s1
```

In this case:
- Fixed-H (`/h`) shows the C-H and CH₂ hydrogens that cannot move
- Mobile-H layer would show the enolizable hydrogens on the carbonyl/enol tautomers

### Comparison Output

The `CompINChI2` function handles fixed hydrogen comparison:

```c
// From ichimake.c line 1854-1863
if (i1n && i1n->nNum_H_fixed && i2n && i2n->nNum_H_fixed) {
    // Compare nNum_H_fixed arrays element by element
    // Return: !i2n->nNum_H_fixed[i] ? 1 : !i1n->nNum_H_fixed[i] ? -1 :
    //          (int)i2n->nNum_H_fixed[i] - (int)i1n->nNum_H_fixed[i];
}
```

### Layer Distinction

| Layer | Prefix | Contains | When Present |
|-------|--------|----------|------------|
| Formula | `/f` | All H atoms | Always (unless /h present) |
| Fixed-H | `/h` | Non-mobile H | In non-tautomeric mode |
| Fixed-H | `/f/h` | Non-mobile H | When /f also used |
| Mobile-H | `/m` | Mobile groups | When tautomerism exists |

---

## References

### Header Definitions

- `ichi.h` (lines 232-235): INChI structure hydrogen members
- `ichicant.h` (lines 329-330): CANON_STAT hydrogen members
- `ichicant.h` (lines 173-174): F_CN hydrogen fixed positions

### Implementation Files

- `strutil.c` (lines 7695-7747): Allocation/setup
- `ichimake.c` (lines 2360-2377): String generation
- `ichiread.c` (lines 8228-8545): Parsing
- `ichicano.c` (lines 1576-1580): Canonicalization

### Related Layers

- **Mobile-H Layer** (`/m`): Complementary—represents mobile/tautomeric hydrogens
- **Formula Layer** (`/f`): Complete formula
- **Isotopic-H Layer** (`/i/h`): Isotopic hydrogen information

---

*Fixed-H layer analysis: 2026-04-22*