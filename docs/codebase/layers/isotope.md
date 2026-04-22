# InChI Isotope Layer (/i)

**Analysis Date:** 2026-04-22

## Overview

The **Isotope layer** (identified by the `/i` prefix in the InChI identifier) represents the **isotopic composition** of a molecule. This layer is used when a molecule contains atoms that differ in neutron count from the natural isotopic abundance—most commonly deuterium ($^2$H or D) or tritium ($^3$H or T) labeling in organic chemistry, or when specific elements have non-standard isotope ratios.

### When the Layer Is Used

The isotope layer appears in an InChI identifier under these conditions:

1. **Isotopic atoms**: Any atom with non-standard isotopic mass (e.g., $^{13}$C, $^{15}$N, $^{18}$O)
2. **Isotopic hydrogen**: Deuterium or tritium replacing protium ($^1$H)
3. **Enriched elements**: Elements with artificial isotope enrichment

The isotope layer can combine with other layers:
- `/i` — Basic isotope layer (non-mobile atoms)
- `/i+1` — Combined with mobile hydrogen layer (/h)
- `/i+2` — Combined with fixed hydrogen layer (/f)

### Output Format Examples

```
InChI=1S/C2H6O/c1-2-3/h3H2,1H3               # No isotope layer
InChI=1S/C2H6O/c1-2-3/h3H2,1H3/i1+1        # Add /i + isotope atoms + mobile H
InChI=1S/C2H4O2/c1-2(3)4/h1H2/i1+2          # With fixed H layer
```

---

## Code Implementation

### Primary Source File

**`INCHI-1-SRC/INCHI_BASE/src/ichiisot.c`** — The core isotopic processing module (155 lines). This file contains:

- `make_iso_sort_key()` — Creates sorting keys for isotopic atoms
- `set_atom_iso_sort_keys()` — Assigns isotopic sort keys to atoms
- Isotope detection and canonical numbering

### Key Data Structures

#### INChI_IsotopicAtom (from `ichi.h`, line 94-106)

```c
typedef struct tagINChI_IsotopicAtom
{
    AT_NUMB   nAtomNumber;      /* Canonical atom number (1-based)          */
    NUM_H     nIsoDifference;   /* 0=natural; >0=(mass - most_abundant)+1   */
                                   /* Example: 13C has nIsoDifference = 1    */
    NUM_H     nNum_H;           /* Number of 1H (protium) attached          */
    NUM_H     nNum_D;           /* Number of 2H (deuterium) attached        */
    NUM_H     nNum_T;           /* Number of 3H (tritium) attached         */
} INChI_IsotopicAtom;
```

**Field Details:**
- `nAtomNumber`: Canonical atom number in the structure
- `nIsoDifference`: Mass offset from most abundant isotope
  - 0 = natural isotopic abundances
  - 1 = one mass unit above most abundant
  - -1 = one mass unit below most abundant
- `nNum_H`, `nNum_D`, `nNum_T`: Count of each hydrogen isotope attached to this atom

#### INChI_IsotopicTGroup (from `ichi.h`, line 110-116)

```c
typedef struct tagINChI_IsotopicTGroup
{
    AT_NUMB   nTGroupNumber;    /* Tautomeric group number                  */
    AT_NUMB   nNum_H;           /* Number of 1H in tautomer group           */
    AT_NUMB   nNum_D;           /* Number of 2H in tautomer group           */
    AT_NUMB   nNum_T;           /* Number of 3H in tautomer group           */
} INChI_IsotopicTGroup;
```

#### INChI structure containing isotope data (from `ichi.h`, line 237-241)

```c
/* ---- isotopic & isotopic tautomeric layer */
int                  nNumberOfIsotopicAtoms;
INChI_IsotopicAtom   *IsotopicAtom;              /* [nNumberOfIsotopicAtoms] */
int                  nNumberOfIsotopicTGroups;
INChI_IsotopicTGroup *IsotopicTGroup;             /* [nNumberOfIsotopicAtoms] */
```

### Input Atom Representation (from `inpdef.h`, line 157-160)

```c
S_CHAR num_iso_H[NUM_H_ISOTOPES]; /* number of implicit 1H, 2H(D), 3H(T) < 16 */
S_CHAR iso_atw_diff;              /* =0 => natural isotopic abundances     */
                                 /* >0 => (mass) - (mass of the most abundant isotope) + 1   */
                                 /* <0 => (mass) - (mass of the most abundant isotope)      */
```

### Constants (from `incomdef.h`, line 60-61)

```c
#define NUM_H_ISOTOPES        3  /* number of hydrogen isotopes: protium, deuterium, tritium */
#define ATW_H                 1  /* hydrogen atomic weight */
```

---

## Algorithm

### Pseudo-code: Isotope Detection and Processing

```
FUNCTION detect_isotopic_atoms(atoms[], num_atoms):
    
    isotopic_atoms = []
    
    FOR each atom IN atoms:
        # Check for non-standard isotopes
        IF atom.iso_atw_diff != 0:
            # Create isotopic atom record
            iso_atom.atom_number = atom.canonical_number
            iso_atom.iso_difference = atom.iso_atw_diff
            
            # Check attached hydrogen isotopes
            iso_atom.num_H = atom.num_iso_H[0]    # 1H (protium)
            iso_atom.num_D = atom.num_iso_H[1]    # 2H (deuterium)
            iso_atom.num_T = atom.num_iso_H[2]    # 3H (tritium)
            
            ADD iso_atom TO isotopic_atoms
            
        # Handle explicit D or T (element name 'D' or 'T')
        IF atom.elname == "D":
            iso_atom.iso_difference = 2
            iso_atom.num_D = 1
            ADD iso_atom TO isotopic_atoms
            
        IF atom.elname == "T":
            iso_atom.iso_difference = 3
            iso_atom.num_T = 1
            ADD iso_atom TO isotopic_atoms
    
    RETURN isotopic_atoms
```

### Pseudo-code: Sort Key Generation

The function `make_iso_sort_key()` (from `ichiisot.c`, line 47-60) creates a composite sorting key:

```
FUNCTION make_iso_sort_key(iso_atw_diff, num_1H, num_2H, num_3H):
    
    iso_sort_key = 0
    mult = 1
    
    # Encode in order: 1H count, 2H count, 3H count, mass difference
    iso_sort_key += mult * num_1H
    mult *= AT_ISO_SORT_KEY_MULT
    
    iso_sort_key += mult * num_2H
    mult *= AT_ISO_SORT_KEY_MULT
    
    iso_sort_key += mult * num_3H
    mult *= AT_ISO_SORT_KEY_MULT
    
    iso_sort_key += mult * iso_atw_diff
    
    RETURN iso_sort_key
```

This sort key enables efficient canonical ordering of isotopic atoms for reproducible InChI generation.

---

## String Generation (Output Format)

### MakeIsoAtomString() Function

Located in `ichiprt2.c` (line 1701), this function generates the `/i` layer string:

```
FUNCTION MakeIsoAtomString(IsotopicAtom, nNumberOfIsotopicAtoms, strbuf):
    
    # Letter codes for hydrogen isotopes
    letter[] = ['i', 't', 'd', 'h']   # Used internally
    
    FOR each isotopic_atom IN IsotopicAtom:
        # Output canonical atom number
        APPEND canonical_number TO strbuf
        
        # Output mass difference
        APPEND mass_difference TO strbuf
        
        # Output counts with letter codes (if non-zero)
        IF isotopic_atom.num_T > 0:
            APPEND 't' + count TO strbuf    # Tritium
            
        IF isotopic_atom.num_D > 0:
            APPEND 'd' + count TO strbuf    # Deuterium
            
        IF isotopic_atom.num_H > 0:
            APPEND 'h' + count TO strbuf    # Protium
    
    RETURN length
```

### Output Format Patterns

| Isotope | Mass Difference | InChI Letter |
|---------|--------------|------------|
| protium ($^1$H) | 0 | (none), or 'h' if explicit |
| deuterium ($^2$H/D) | 1 | 'd' |
| tritium ($^3$H/T) | 2 | 't' |
| $^{13}$C | 1 | (number) |
| $^{15}$N | 1 | (number) |
| $^{18}$O | 2 | (number) |

---

## Examples

### Example 1: Deuterium-labeled Acetic Acid

**Input SMILES:** `CC(=O)O` with one deuterium on methyl carbon

**SMILES with Deuterium:**
```
[2H]C(=O)O    # or CC(=O)O with D on first carbon
```

**Generated InChI:**
```
InChI=1S/C2H4O2/c1-2(3)4/h1H2/i1+1
```

**Breakdown:**
- `/i1` — Isotope layer present
- `+1` — Combined with mobile hydrogen (`/h`) layer
- The number `1` indicates atom 1 has an attached isotope

### Example 2: Perdeuterated Ethanol

**SMILES:**
```
CCO
[2H]C([2H])([2H])[2H]    # Fully deuterated ethanol: CD3CD2OD
```

**InChI:**
```
InChI=1S/C2H6O/c1-2-3/h3H2,1H3/i1+2
```

### Example 3: Multiple Isotopes

**Compound:** $^{13}$C-labeled glucose

**InChI (approximate):**
```
InChI=1S/C6H12O6/c1-2(3)4(6)5(7)/h8H2/i1C,2C,3C,4C,5C,6C
```

Here `i1C` through `i6C` indicate carbon atoms 1-6 are $^{13}$C.

### Example 4: Deuterium + Fixed H Layer

When deuterium is involved in mobile hydrogen exchange, it appears in the combined `/i+1` or `/i+2` layer:

```
InChI=1S/C2H4O/c1-2/h1H2/i1+1    # With mobile H containing D
InChI=1S/C2H4O/c1-2/h1H2/i1+2    # With fixed H containing D
```

---

## Integration Points

### Layer Comparison (ichimake.c)

The isotope layer is compared across InChI variants during canonicalization (line 1384):

```c
if (i1 && !i1->bDeleted && (i1->nNumberOfIsotopicAtoms || i1->nNumberOfIsotopicTGroups))
{
    *psDifSegs |= DIFV_NEQ2PRECED;
}
```

### Reverse InChI Processing (ichirvr7.c)

When reading an InChI string, isotopic atoms are restored (line 1457):

```c
INChI_IsotopicAtom* k_IsotopicAtom = (&pOneInput->pInpInChI[iINChI][j][k])->IsotopicAtom;
```

### Printing/Output (ichiprt3.c)

The isotope layer is output conditionally (line 1326):

```c
if (pINChI_Prev->nNumberOfIsotopicAtoms > 0 && !*bOverflow)
{
    MakeIsoAtomString(pINChI_Prev->IsotopicAtom, ...);
}
```

---

## Key Files Summary

| File | Purpose |
|------|---------|
| `INCHI_BASE/src/ichiisot.c` | Core isotope processing algorithms |
| `INCHI_BASE/src/ichi.h` | Data structure definitions |
| `INCHI_BASE/src/ichiprt2.c` | String generation |
| `INCHI_BASE/src/ichiprt3.c` | Output formatting |
| `INCHI_BASE/src/ichimake.c` | Canonicalization, layer comparison |
| `INCHI_BASE/src/ichiread.c` | Input parsing, reverse InChI |
| `INCHI_BASE/src/inpdef.h` | Input atom structure |
| `INCHI_BASE/src/incomdef.h` | Constants |

---

*Isotope layer analysis: 2026-04-22*