# Formula Layer (`/f`)

**Analysis Date:** 2026-04-22

## Overview

The **Formula layer** (`/f`) is the first and most fundamental layer in an InChI identifier. It represents the molecular formula of a chemical compound, specifying the exact number of each element present in the molecule. This layer is **obligatory** - it must always be present in a valid InChI string.

Chemically, the formula layer encodes the empirical (or exact) molecular composition by listing elements in **Hill order**: carbon (C) first if present, followed by hydrogen (H), then all other elements alphabetically. Each element symbol is followed by its atom count; if the count is 1, the number is omitted.

The formula layer appears immediately after the version prefix in an InChI string:

```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3
       └──────┘
       Formula layer (/f)
```

Without the optional `/f` delimiter, the formula is the first part before any slash:

```
InChI=1S/C2H6O   →   InChI=1S/fC2H6O   (formula = C2H6O)
InChI=1/C3H8     →   InChI=1/fC3H8     (formula = C3H8)
```

## Code Implementation

### Key Source Files

| File | Purpose |
|------|---------|
| `INCHI_BASE/src/ichi.h` | INChI struct definition (lines 209-257) |
| `INCHI_BASE/src/ichimak2.c` | Formula generation during InChI creation |
| `INCHI_BASE/src/ichiread.c` | Formula parsing during InChI reading |
| `INCHI_BASE/src/ichiprt1.c` | Pseudo-element handling in formulas |
| `INCHI_BASE/src/ichimake.h` | Function declarations |

### INChI Struct Definition

The `INChI` typedef (defined in `ichi.h` lines 209-257) contains these formula-related members:

```c
typedef struct tagINChI {
    int        nNumberOfAtoms;      // Total number of non-hydrogen atoms
    char      *szHillFormula;      // The Hill formula string (e.g., "C2H6O")
    U_CHAR    *nAtom;            // Atomic numbers [nNumberOfAtoms] from Periodic Table
    S_CHAR    *nNum_H;          // Terminal hydrogen atoms on each atom
    // ...
} INChI;
```

**Key Members:**

| Member | Type | Purpose |
|--------|------|--------|
| `nNumberOfAtoms` | `int` | Count of non-hydrogen atoms in the molecule |
| `szHillFormula` | `char*` | The formatted Hill formula string |
| `nAtom[]` | `U_CHAR[]` | Element atomic numbers (e.g., 6=C, 8=O, 1=H) |
| `nNum_H[]` | `S_CHAR[]` | Number of terminal H atoms on each atom |
| `nTautomer[]` | `AT_NUMB[]` | Mobile hydrogen group definitions |

### Key Functions

**Formula Generation (Creation):**

| Function | Location | Purpose |
|----------|----------|---------|
| `AllocateAndFillHillFormula()` | `ichimak2.c:402` | Allocates memory and generates formula string |
| `GetHillFormulaCounts()` | `ichimak2.c:159` | Estimates atom counts (C, H, length) |
| `MakeHillFormula()` | `ichimak2.c:316` | Builds the formula string |
| `AddElementAndCount()` | `ichimak2.c:279` | Appends element + count to string |
| `GetHillFormulaIndexLength()` | `ichimak2.c:144` | Calculates digit length for counts |

**Formula Parsing (Reading):**

| Function | Location | Purpose |
|----------|----------|---------|
| `GetInChIFormulaNumH()` | `ichiread.c:2215` | Extracts H count from formula string |
| `CountPseudoElementInFormula()` | `ichiprt1.c:5436` | Counts pseudo-elements (Zz) |

### Formula Generation Flow

```
Input: Molfile/SDfile
         ↓
1. Normalize structure (remove duplicate atoms, canonicalize)
         ↓
2. Flatten to atomic number array (nAtom[])
         ↓
3. Flatten to hydrogen counts (nNum_H[])
         ↓
4. Process tautomer groups (nTautomer[]) - add mobile H
         ↓
5. Call AllocateAndFillHillFormula()
         ↓
Output: szHillFormula (e.g., "C6H6O")
```

## Pseudo-code Algorithm

### Step 1: Count Atoms from Structure

```c
function GetHillFormulaCounts(nAtom[], nNum_H[], nNumberOfAtoms, nTautomer, lenTautomer):
    num_C = 0
    num_H = 0
    nFormLen = 0
    
    // Iterate through atomic numbers
    for i from 0 to nNumberOfAtoms - 1:
        // Group consecutive identical elements
        if nAtom[i] equals previous element:
            mult += 1  // increment multiplicity
        else:
            if current element is Carbon:
                num_C += mult
            else if current element is Hydrogen:
                num_H += mult + nNum_H[i]  // include explicit H
            else:
                nFormLen += element_length + digit_length(mult)
            mult = 1
        
        nPrevAtom = nAtom[i]
    
    // Add tautomeric mobile hydrogens
    if nTautomer and lenTautomer > 0:
        for each tautomer group:
            num_H += group_hydrogen_count
    
    // Add carbon and hydrogen totals
    if num_C > 0:
        nFormLen += 1 + digit_length(num_C)  // "C" + count
    if num_H > 0:
        nFormLen += 1 + digit_length(num_H)  // "H" + count
    
    return (num_C, num_H, nFormLen, nNumNonHAtoms)
```

### Step 2: Construct Hill Formula String

```c
function MakeHillFormula(nAtom[], num_atoms, num_C, num_H):
    szLinearCT = allocate(buffer)
    nLen = 0
    
    // Rule 1: Carbon always first
    if num_C > 0:
        nLen += AddElementAndCount("C", num_C)
        if num_H > 0:
            nLen += AddElementAndCount("H", num_H)  // H immediately after C
            num_H = 0
    
    // Rule 2: All other elements alphabetically
    for each atom in nAtom[]:
        if atom != previous:
            if previous is not Carbon or H:
                nLen += AddElementAndCount(element, mult)
            mult = 1
        
    // Rule 3: Hydrogen last (if not after Carbon)
    if num_H > 0:
        nLen += AddElementAndCount("H", num_H)
    
    return szLinearCT  // e.g., "C6H6O"
```

### Step 3: Hill Order Rules

1. **Carbon first** - If C exists, formula starts with `C` followed by count
2. **Hydrogen second** - If C exists, H immediately follows C
3. **All other elements alphabetically** - e.g., Cl, K, N, O, S...
4. **Hydrogen last** - If no carbon, H appears alphabetically (which is first!)

### Step 4: Pseudo-elements (Special Cases)

Pseudo-elements represent fragments or undefined groups. The primary pseudo-element is `Zz`, which can have multipliers and indices:

```
InChI=1B/C4H4N4.2Zz/c1-5-2-7-4-8-3-6-1/h1-4H/z101-1-
        └──────────────────────┘
        Pseudo-element notation (Zz = molecular fragment)
```

Counting pseudo-elements:

```c
function CountPseudoElementInFormula(pseudo, s):
    // Format: [.[int_mult[Zz[int_index]]]]
    // Example: ".2Zz" means 2 copies of pseudo-element
    npseudo = 0
    // Parse and count pseudo-elements in formula string
    return npseudo
```

## Examples

### Simple Organic Molecules

| Input Molecule | Formula Layer | InChI String |
|---------------|--------------|-------------|
| Methane (CH₄) | CH₄ | `InChI=1S/CH4/h1H3` |
| Ethanol (C₂H₆O) | C2H6O | `InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3` |
| Benzene (C₆H₆) | C6H6 | `InChI=1S/C6H6/c1-2-4-6-5-3/h1-6H` |
| Water (H₂O) | H2O | `InChI=1S/H2O/h1H2` |
| Ammonia (NH₃) | H3N | `InChI=1S/H3N/h1H2-1` |
| Carbon dioxide (CO₂) | CO2 | `InChI=1S/CO2/c2-1-3` |

### Inorganic Compounds

| Input Molecule | Formula Layer | InChI String |
|---------------|--------------|-------------|
| Sodium chloride | ClNa | `InChI=1S/ClNa` |
| Calcium carbonate | CaCO3 | `InChI=1S/CH2O3.Ca/c2-1(3)4;/h1-3H;(Ca+2)/` |
| Sulfuric acid | H2O4S | `InChI=1S/H2O4S/h1H2,(S+2)` |

### With Pseudo-elements

| Description | Formula Layer | Usage |
|-------------|--------------|-------|
| Coordination complex with undefined ligand | C2H6O.2Zz | `.2Zz` = 2 copies of undefined fragment |
| Salt with counterion | C6H5NO2.C8H5NO2 | Multiple components separated by `.` |

### Multi-component Formulas

When a structure contains disconnected components (e.g., salts, complexes), each component's formula is concatenated with `.`:

```
Component 1: C6H6 (benzene)
Component 2: H2O (water)
Combined:   C6H6.H2O

InChI=1S/C6H6.H2O/c1-2-4-6-5-3/h1-6H;/h1H2
```

### Tautomeric Forms

For tautomers sharing mobile hydrogen atoms, the formula includes all potentially movable H:

```
Acetoacetic acid tautomers (keto/enol):
Keto form:    C5H8O3  
Enol form:    C5H6O2  (enols have fewer H)

InChI=1S/C5H8O3/c1-3(7)5(8)6-4(2)5/h1H3,(2,3,7-8H)/p+1/fC5H7O3/h2,7,8O;1-2/
                    └─────┘
                    Total H (including mobile)
```

### With Charge

Charged species include the charge in the formula layer via `/h` or as a modifier:

```
Sodium cation:  Na+
InChI=1S/Na

Chloride anion: Cl-
InChI=1S/Cl

Sodium chloride (salt):
InChI=1S/ClNa
```

## Technical Notes

### Memory Management

- `szHillFormula` is dynamically allocated via `AllocateAndFillHillFormula()`
- Freed via `inchi_free()` when INChI struct is deallocated
- Maximum length is determined by `GetHillFormulaCounts()` estimation

### Overflow Handling

The formula generation functions include overflow detection:

```c
int bOverflow = 0;
// ... formula generation ...
if (bOverflow) {
    // Handle truncation or error
}
```

### Comparison

Two InChI identifiers are compared at the formula layer via `CompareHillFormulasNoH()` - this ignores isotopic differences but compares the base formula:

```c
int CompareHillFormulasNoH(char *f1, char *f2, int *num_H1, int *num_H2);
// Returns: 0 if equal, non-zero otherwise
```

---

*Formula layer analysis: 2026-04-22*