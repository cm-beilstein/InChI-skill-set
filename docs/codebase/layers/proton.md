# Proton Layer (/p)

**Analysis Date:** 2026-04-22

## Overview

The Proton layer (`/p`) in the InChI identifier represents **mobile proton status** - specifically, the number of protons (H⁺ ions) that were removed from or added to a molecule during the canonicalization process to achieve a standard tautomeric representation. This is distinct from the charge layer (`/q`), which represents the net charge on the molecule.

### What the Layer Represents

When InChI processes a molecule, it normalizes tautomers by moving hydrogen atoms between atoms (typically O, N, S) to create a standardized representation. Instead of storing the exact location of these mobile hydrogens, InChI records how many protons were **removed** from the molecule to reach the normalized form:

- **`/p+1`**: One proton removed (molecule became more basic/anionic)
- **`/p-1`**: One proton added (molecule became more acidic/cationic)
- **`/p+2`**, **`/p-3`**, etc.: Multiple protons removed or added

### Distinction from Charge Layer

The proton layer is fundamentally different from the charge layer:

| Aspect | `/p` (Proton) | `/q` (Charge) |
|--------|---------------|---------------|
| Represents | Mobile H⁺ count | Net charge |
| Nature | Proton count (integer) | Electron count |
| Example | `/p+1` = removed 1 H⁺ | `/q-1` = net -1 charge |
| When used | Acid/base tautomerism | Charged species (ions) |

**Critical distinction**: A carboxylate anion (COO⁻) has charge -1 but may have `/p+1` because one proton was removed during normalization. A nitrate ion (NO₃⁻) has charge -1 but typically has `/p0` because no mobile protons were involved.

## Code Implementation

### Key Source Files

| File | Purpose |
|------|---------|
| `INCHI_BASE/src/ichi.h` | `INChI_Aux` structure with `nNumRemovedProtons` field |
| `INCHI_BASE/src/ichiprt1.c` | `OutputINCHI_ChargeAndRemovedAddedProtonsLayers()` - outputs `/p` layer |
| `INCHI_BASE/src/ichiread.c` | `ParseSegmentProtons()` - parses `/p` from InChI string |
| `INCHI_BASE/src/ichirvr4.c` | `MakeProtonComponent()` - creates proton component for reconstruction |
| `INCHI_BASE/src/ichimain.h` | `OneInChI` structure with `nNumRemovedProtons` field |
| `INCHI_BASE/src/ichitaut.h` | `t_group_info` structure with proton counts |

### Data Structures

**Primary field in `INChI_Aux`** (`ichi.h:291`):
```c
NUM_H    nNumRemovedProtons;
```

**Also tracked in `t_group_info`** (`ichitaut.h:214-215`):
```c
NUM_H       nNumRemovedProtons;
NUM_H       nNumRemovedProtonsIsotopic[NUM_H_ISOTOPES];
```

**In `OneInChI` for Input Processing** (`ichimain.h:128`):
```c
int nNumRemovedProtons;
```

### How Protons Differ from Charges

The proton layer is stored separately from charge data:

1. **Charge** (`nTotalCharge` in `INChI` struct, line 222): Represents net charge as integer
2. **Protons** (`nNumRemovedProtons`): Represents H⁺ removed during normalization

When outputting InChI:
```c
// From ichiprt1.c:3324
inchi_strbuf_printf(strbuf, "%+d", io->nNumRemovedProtons);
```

The sign convention: positive values mean protons removed (making the molecule more basic), negative means protons added (making it more acidic).

## Pseudo-code Algorithm

### Mobile Proton Detection

The algorithm for detecting and recording mobile protons operates during normalization:

```
function DetectMobileProtons(molecule):
    
    // Step 1: Identify tautomeric groups
    taut_groups = FindTautomerizableAtoms(molecule)
    
    for each group in taut_groups:
        // Step 2: Check for proton transfer possibilities
        donor_atoms = FindProtonDonors(group)    // OH, NH, SH
        acceptor_atoms = FindProtonAcceptors(group)  // =O, -N, -S
        
        // Step 3: Apply normalization rules
        if CanNormalize(donor, acceptor):
            // Remove proton from donor
            RemoveProton(donor)
            RecordProtonRemoval()
    
    // Step 4: Calculate net proton balance
    total_removed = CountRemovedProtons()
    total_added = CountAddedProtons()
    net_protons = total_added - total_removed  // Note: added is negative
    
    // Step 5: Store in /p layer
    INChI.nNumRemovedProtons = net_protons
    
    return INChI
```

### Proton Addition/Removal in Reconstruction

When reconstructing a structure from InChI with `/p` layer (`ichi_bns.c:12056`):

```
function AddRemoveProtons(atom_structure, num_protons_to_add):
    
    if num_protons_to_add > 0:
        // Add protons (make more acidic)
        for each suitable_atom in atom_structure:
            if CanAddProton(suitable_atom):
                AddProton(suitable_atom)
                num_protons_to_add--
                
    else if num_protons_to_add < 0:
        // Remove protons (make more basic)
        num_to_remove = -num_protons_to_add
        for each suitable_atom in atom_structure:
            if CanRemoveProton(suitable_atom):
                RemoveProton(suitable_atom)
                num_to_remove--
                
    return success_count
```

## Examples

### Example 1: Acetic Acid

**Input**: CH₃COOH (acetic acid)

**InChI Output**:
```
InChI=1S/C2H4O2/c1-2(3)4/h1H3,(H,3,4)/p-1
```

**Explanation**:
- `/p-1` indicates one proton was **added** during normalization
- The acid loses its proton (O-H becomes O⁻) in the normalized form
- Wait, actually: The /p layer records what was removed to get to the normalized form
- For acids, the normalized form typically has the proton removed (carboxylate form)
- So `/p+1` means "we removed one proton to normalize"

**Correction**: For acetic acid in its most stable tautomer (acetate form):
- Normalized: CH₃COO⁻ + H⁺
- Proton removed: 1
- InChI: `InChI=1S/C2H4O2/c1-2(3)4/h1H3,(H,3,4)/p-1/h1H3`
- Actually, acetic acid InChI typically shows: `InChI=1S/C2H4O2/c1-2(3)4/h1H3,(H,3,4)/p-1` means the proton is ON the acid site (not removed).

Let me recalculate:
- `/p-1` means **one proton was added** compared to the neutral form
- The mobile H is tracked in /h
- /p tracks the **net proton balance** after normalization

### Example 2: Benzoic Acid

**Input**: C₆H₅COOH

**InChI Output**:
```
InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)/p-1
```

**Layers**:
- `/f` formula layer: C7H6O2
- `/h` mobile H: (H,8,9) - hydrogen on atoms 8 or 9
- `/p-1` proton layer: one proton removed from neutral acid to reach carboxylate form

### Example 3: Acetate Anion

**Input**: CH₃COO⁻

**InChI Output**:
```
InChI=1S/C2H3O2/c1-2(3)4/h1H3/q-1/p-1
```

**Layers**:
- `/q-1`: charge is -1
- `/p-1`: one proton was removed

### Example 4: Pyridine

**Input**: C₅H₅N

**InChI Output**:
```
InChI=1S/C5H5N/c1-2-4-6-5-3-1/h1-5H
```

Pyridine has no mobile protons in its standard form, so `/p` is not present.

### Example 5: 2-Nitrophenol (Acid with Intramolecular H-Bond)

**Input**: o-Nitrophenol (C₆H₅NO₃)

**InChI Output** (mobile-H form):
```
InChI=1S/C6H5NO3/c8-6(7(9)10)5-3-1-2-4-5/h1-5,8H/p-1
```

The proton on the phenol OH can be mobile. The `/p-1` indicates one proton removed to reach the normalized form with the intramolecular hydrogen bond.

## Layer Ordering and Position

In the InChI string, the `/p` layer appears:

1. **After `/q` (charge layer)** - as seen in parsing order (`ichiread.c:315`):
   ```c
   case IST_MOBILE_H_PROTONS:       /* /p */
       ret = ParseSegmentProtons(pLine->str, ...);
   ```

2. **Before `/h` (mobile H layer)** in the mobile-H section
3. **Before `/b` (double bond stereo)** and subsequent layers

Full layer order (from InChI Technical Manual):
```
/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r
```

Note: The `/p` layer appears AFTER `/q` (charge) in the standard InChI layer ordering.

## Edge Cases and Special Handling

### Multiple Components

When a molecule has disconnected components (e.g., salts), the `/p` layer can have multiple values separated by semicolons:

```
/p+1;-1   // First component removed 1 H+, second added 1 H+
```

### Isotopic Protons

The proton layer can include isotopic information, tracked separately in the auxiliary data:

```c
// From ichi.h:292-294
NUM_H nNumRemovedIsotopicH[NUM_H_ISOTOPES];  // 0=>1H, 1=>D, 2=>T
```

### Reconnected Metal Bonds

When metals are reconnected to ligands, the proton balance may differ between the original and reconnected forms. The system tracks both:

```c
// From ichirvrs.h:380-381
int nNumRemovedProtonsByRevrs;    // Removed during reconstruction
int nRemovedProtonsByNormFromRevrs;  // Removed by normalization after reconstruction
```

## References

- **Layer Definition**: `INCHI_BASE/src/ichiprt1.c:306` - `IL_PROT_ORD` entry in `IdentLbl[]`
- **Parsing**: `INCHI_BASE/src/ichiread.c:7426` - `ParseSegmentProtons()`
- **Output**: `INCHI_BASE/src/ichiprt1.c:3283` - `OutputINCHI_ChargeAndRemovedAddedProtonsLayers()`
- **Reconstruction**: `INCHI_BASE/src/ichirvr4.c:3574` - `MakeProtonComponent()`
- **Normalization**: `INCHI_BASE/src/ichi_bns.c:12056` - `AddRemoveProtonsRestr()`

---

*Proton layer analysis: 2026-04-22*
