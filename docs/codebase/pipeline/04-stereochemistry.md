# Stereochemistry Processing

**Analysis Date:** 2026-04-22

## Overview

The Stereochemistry Processing step in the InChI pipeline handles the detection and calculation of stereochemical information from molecular structures. This step is critical because stereochemistry (the 3D spatial arrangement of atoms) determines whether molecules are chiral or geometric isomers—molecules with identical connectivity but different spatial arrangements that give them different chemical properties.

The InChI library handles three main types of stereochemistry:

1. **Tetrahedral (sp³) stereocenters** - Atoms bonded to four different substituents arranged in 3D space (e.g., chiral carbon)
2. **Double bond (sp²) stereochemistry** - Cis/trans or E/Z isomerism around double bonds
3. **Cumulene/allene stereochemistry** - Stereoisomerism in cumulated double bond systems (e.g., allenes, ketenes)

This step follows canonicalization in the pipeline because stereochemistry must be computed on the canonically-numbered structure where atom ordering is standardized. The output from this step is stored in the `INChI_Stereo` structure, which contains both the stereogenic atoms/bonds and their calculated parities.

## IUPAC Rules and Standards

The InChI library's stereochemistry handling is grounded in IUPAC recommendations for chemical nomenclature. The following standards define how stereochemistry is expressed in the InChI format.

### CIP Sequence Rules

The Cahn-Ingold-Prelog (CIP) priority rules establish ranking for stereochemical descriptors. These rules are codified in IUPAC Blue Book Section P-9 (https://iupac.qmul.ac.uk/BlueBook/P9.html).

**Priority ranking (highest to lowest):**
1. Atomic number (Z) of atoms directly bonded to the stereocenter
2. For ties, examine next atoms outward, iterating until a distinction is found
3. Handle multiple bonds as pseudo-atoms (duplicate connected atoms)
4. Isotopic mass affects priority when all else is equal

The InChI implementation uses atomic numbers from the Periodic Table, with isotopic mass differences resolving otherwise equivalent stereocenters (e.g., deuterium vs. hydrogen).

### R/S Descriptor System

The R/S (rectus/sinister) system specifies tetrahedral stereochemistry. For a tetrahedral stereocenter:

- **R (rectus, "right")**: When viewing along the lowest-priority bond toward the stereocenter, the other three substituents proceed clockwise (priority 1 → 2 → 3)
- **S (sinister, "left")**: The same arrangement proceeding counterclockwise

This system requires constructing a priority ranking of all four substituents, then orienting the molecule so the lowest-priority group points away. The InChI library calculates parity (ODD/EVEN) which maps to S/R descriptors based on the priority ordering derived from atomic numbers.

### E/Z Descriptor System

The E/Z system specifies geometric isomerism about double bonds (IUPAC P-92). Each carbon of the C=C double bond has two substituents:

- **Z (zusammen, "together")**: Higher-priority substituents on the same side
- **E (entgegen, "opposite")**: Higher-priority substituents on opposite sides

Priority follows CIP rules at each end of the double bond. InChI bond parity (ODD/EVEN) corresponds to E/Z: even parity indicates Z (cis-like), odd parity indicates E (trans-like).

### InChI Stereo Treatment

InChI uses a parity-based system that maps to but is distinct from R/S and E/Z descriptors:

**Tetrahedral centers:**
InChI supports stereocenters on specific elements (Table 5 of the Technical Manual):
- Carbon (C), Silicon (Si), Nitrogen (N), Phosphorus (P), Sulfur (S), Arsenic (As), Selenium (Se)

The parity is calculated as ODD (clockwise) or EVEN (counterclockwise) based on the spatial arrangement. However, this is NOT equivalent to R/S because R/S additionally depends on the atomic priority ranking derived from CIP rules. Two molecules may have identical InChI parity but different R/S descriptors if their substituent priority orderings differ.

**Double bond stereochemistry:**
InChI bond parity applies to:
- Standard C=C double bonds
- Alternating bonds (conjugated systems)
- Cumulene stereochemistry

The parity combines half-parities from each end of the bond, accounting for z-direction vectors to determine relative orientation.

**Parity vs. R/S mapping:**
InChI stores raw parity (ODD/EVEN) rather than absolute R/S because R/S requires knowledge of the complete priority ranking, which may not be derivable from molecular graphs alone. When generating canonical labels, the library computes R/S from both the coordinates and the atomic priority rankings derived during canonicalization.

### Source References

- **IUPAC Blue Book P-9**: Stereochemical specification - https://iupac.qmul.ac.uk/BlueBook/P9.html
- **IUPAC Blue Book P-92**: E/Z descriptor system for double bonds
- **IUPAC Blue Book P-93**: R/S descriptor system for tetrahedral centers
- **InChI Technical Manual**: Section on Stereochemistry (Table 5 lists supported elements)
- **Wikipedia**: Cahn-Ingold-Prelog priority rules - https://en.wikipedia.org/wiki/Cahn%E2%80%93Ingold%E2%80%93Prelog_priority_rule

## Input

The stereochemistry processing receives its input from the canonicalization step (`ichican.c`), specifically:

- **`sp_ATOM* at_output`**: Canonically numbered output structure containing normalized atom data
- **`inp_ATOM* at`**: Original input structure containing coordinate information (2D/3D)
- **`inp_ATOM* at_removed_H`**: Array of explicitly removed hydrogen atoms (for stereochemistry calculation)
- **`int num_removed_H`**: Count of removed explicit hydrogens

The input includes:
- Atom coordinates (x, y, z) from the original input structure
- Bond types and bond stereo flags (wedge/dash in 2D, explicit 3D coordinates)
- Implicit hydrogen counts (`num_H`) and isotopic hydrogen data (`num_iso_H[]`)
- Information about whether atoms can be stereocenters based on element type and charge

### Key Input Structures

```c
// From ichister.h - Main entry point
int set_stereo_parity( CANON_GLOBALS *pCG,
                       inp_ATOM* at,
                       sp_ATOM* at_output,
                       int num_at,
                       int num_removed_H,
                       int *nMaxNumStereoAtoms,
                       int *nMaxNumStereoBonds,
                       INCHI_MODE nMode,
                       int bPointedEdgeStereo,
                       int vABParityUnknown,
                       int bLooseTSACheck,
                       int bStereoAtZz );
```

## Output

### INChI_Stereo Structure

The output is stored in the `INChI_Stereo` structure (defined in `ichi.h`):

```c
typedef struct tagINChI_Stereo {
    int         nNumberOfStereoCenters;
    AT_NUMB    *nNumber;      // Canonical numbers of tetrahedral stereogenic atoms
    S_CHAR     *t_parity;     // Tetrahedral atom parities
    
    AT_NUMB    *nNumberInv;   // For inverted structure
    S_CHAR     *t_parityInv;  // Inverted tetrahedral parities
    
    int         nCompInv2Abs; // Relationship between inverted and absolute stereo
    int         bTrivialInv;  // Flag for trivial inversion
    
    int         nNumberOfStereoBonds;
    AT_NUMB    *nBondAtom1;   // First atom of stereogenic bond
    AT_NUMB    *nBondAtom2;   // Second atom of stereogenic bond
    S_CHAR     *b_parity;     // Bond parities
} INChI_Stereo;
```

### Parity Values

Parity values are defined in `extr_ct.h` and represent the spatial arrangement:

| Value | Name | Meaning |
|-------|------|---------|
| 0 | `AB_PARITY_NONE` | Not a stereocenter |
| 1 | `AB_PARITY_ODD` | Odd parity (clockwise arrangement) |
| 2 | `AB_PARITY_EVEN` | Even parity (counter-clockwise arrangement) |
| 3 | `AB_PARITY_UNKN` | User marked as unknown |
| 4 | `AB_PARITY_UNDF` | Undefined due to symmetry or geometry |
| 5 | `AB_PARITY_IISO` | Identical isotopes prevent stereochemistry |
| 6 | `AB_PARITY_CALC` | Parity to be calculated later from ranks |

## Pseudo-code Algorithm

### Main Entry: set_stereo_parity()

```pseudo
function set_stereo_parity(at, at_output, num_at, num_removed_H):
    // Clear all stereo descriptors
    for each atom i in at_output:
        clear stereo_bond_neighbor[i]
        clear stereo_bond_parity[i]
        clear parity[i]
    
    // Estimate maximum numbers of stereo atoms and bonds
    max_stereo_atoms = 0
    max_stereo_bonds = 0
    for each atom i:
        if can_be_stereo_atom_with_isotopic_H(at, i):
            max_stereo_atoms += count
        if can_be_stereo_bond_with_isotopic_H(at, i):
            max_stereo_bonds += count
    
    // Process each atom for tetrahedral stereocenters
    for each atom i from 0 to num_at-1:
        if set_stereo_atom_parity(at_output, at, i, at_removed_H, num_removed_H):
            // Stereo atom found, parity stored in at_output[i].stereo_atom_parity
    
    // Process each atom for stereogenic bonds
    for each atom i from 0 to num_at-1:
        if set_stereo_bonds_parity(at_output, at, i, at_removed_H, num_removed_H):
            // Stereo bond found, parity stored in at_output[i].stereo_bond_parity
```

### Tetrahedral Stereocenter Detection: set_stereo_atom_parity()

```pseudo
function set_stereo_atom_parity(out_at, at, cur_at, at_removed_H, num_removed_H):
    
    // Step 1: Check if atom can be a stereocenter
    if NOT can_be_stereo_center(at[cur_at]):
        return AB_PARITY_NONE
    
    // Step 2: Check for identical isotopic hydrogens
    if more than one identical H isotope:
        return AB_PARITY_IISO
    
    // Step 3: Collect neighbor coordinates
    neighbors = []
    for each explicit H in at_removed_H attached to cur_at:
        add coordinate to neighbors
    
    for each bonded neighbor in at[cur_at]:
        add coordinate to neighbors
    
    // Step 4: Handle 3 vs 4 neighbors
    if neighbors.count == 3:
        // Calculate 4th position (implicit H or lone pair)
        implicit_pos = -sum(explicit_neighbors)
        add implicit_pos to neighbors
    
    // Step 5: Check for planar/invalid geometry
    if all neighbors in plane:
        return AB_PARITY_UNDF
    
    // Step 6: Calculate triple product for parity
    // Triple product > 0 means clockwise (ODD), < 0 means counter-clockwise (EVEN)
    triple = triple_product(v0, v1, v2)
    if triple > 0:
        return AB_PARITY_ODD
    else:
        return AB_PARITY_EVEN
```

### Double Bond Stereochemistry: set_stereo_bonds_parity()

```pseudo
function set_stereo_bonds_parity(out_at, at, at_1, at_removed_H, num_removed_H):
    
    // Step 1: Find stereogenic bonds (double bonds or alternating bonds)
    for each bond from at_1:
        if bond is double OR bond is alternating:
            if opposite atom can have stereo bond:
                // Found a potential stereogenic bond
    
    // Step 2: For each end of the stereogenic bond, calculate half-parity
    for each end atom of the bond:
        half_parity = half_stereo_bond_parity(at, atom, ...)
        
    // Step 3: Combine half-parities
    // If z-directions are opposite (dot product < 0), invert one parity
    final_parity = combine_half_parities(half_parity1, half_parity2)
    
    return final_parity
```

### Half Stereo Bond Parity Calculation: half_stereo_bond_parity()

This function calculates the parity for one end of a stereogenic bond (the "half-parity"):

```pseudo
function half_stereo_bond_parity(at, cur_at, at_removed_H, num_removed_H):
    
    // Step 1: Get coordinates of all neighbors
    // Step 2: If only 2 neighbors, create a 3rd (implicit H or fictitious)
    // Step 3: Normalize vectors to unit length
    // Step 4: Find perpendicular vectors and create new basis
    // Step 5: Project onto new XY plane
    // Step 6: Calculate angles between projections
    // Step 7: Determine parity from angle ordering
    
    // Return values:
    //  -4 = AB_PARITY_UNDF (geometry undefined)
    //  -3 = AB_PARITY_UNKN (geometry unknown to user)
    //  -2 = -AB_PARITY_EVEN
    //  -1 = -AB_PARITY_ODD
    //   0 = AB_PARITY_NONE (not adjacent to stereobond)
    //   1 = AB_PARITY_ODD
    //   2 = AB_PARITY_EVEN
    //   3 = AB_PARITY_UNKN
    //   4 = AB_PARITY_UNDF
    //   5 = AB_PARITY_IISO
```

## Examples

### Example 1: Tetrahedral Carbon Stereocenter

For a chiral carbon like in bromochlorofluoromethane (CBrClFH):

**Input Structure:**
```
        Br (1)
         \
          C (0)
         / 
        F (2)
        |
        H (3)
```

**Processing:**
1. Atom C(0) is identified as potentially stereogenic (C, charge=0)
2. Has 4 neighbors: Br, Cl, F, H
3. For 2D input, wedge/dash determines if neighbors are above/below plane
4. Triple product calculation:
   - Vectors: v(Br), v(Cl), v(F) from center
   - Calculate triple product to determine chirality
   - If 3 neighbors in plane with 4th pointing up → calculate parity

**Output:**
- `nNumber[0] = canonical_number(C)`
- `t_parity[0] = AB_PARITY_ODD` or `AB_PARITY_EVEN`

### Example 2: Cis/Trans Double Bond Stereochemistry

For 2-butene (CH₃-CH=CH-CH₃):

**Input:**
```
   CH3(1)          CH3(3)
      \           /
       C(0) == C(2)
      /           \
     H(4)          H(5)
```

**Processing:**
1. Find double bond between C(0) and C(2)
2. For C(0): Calculate half-parity from neighbors (CH3, H)
3. For C(2): Calculate half-parity from neighbors (CH3, H)
4. Combine half-parities considering z-directions
5. If both CH3 on same side → cis (parity even)
6. If CH3 on opposite sides → trans (parity odd)

**Output:**
- `nBondAtom1[0] = canonical_number(C0)`
- `nBondAtom2[0] = canonical_number(C2)`
- `b_parity[0] = AB_PARITY_EVEN` (cis) or `AB_PARITY_ODD` (trans)

### Example 3: Allene/Cumulene Stereochemistry

For allene (CH₂=C=CH₂) with substituents:

**Processing:**
1. Detect cumulene chain: =C=C= or longer
2. Chain length determines stereochemistry type
3. Odd chain length (e.g., =C=C=) → stereocenter on middle atom
4. Even chain length → "long stereogenic bond"
5. Use triple product of z-directions from each end

### Example 4: Undefined Stereochemistry

When stereochemistry cannot be determined:

```c
// In ichister.c, undefined cases:
// - All neighbors in plane (2D drawing ambiguity)
// - Bond lengths too short to determine
// - Identical substituents (symmetry)
// - User marked as unknown ("Either" stereochemistry)

if (all_neighbors_in_plane):
    return AB_PARITY_UNDF
    
if (identical_substituents):
    return AB_PARITY_IISO
```

### Example 5: Isotopic Stereochemistry

For molecules with isotopic labeling (e.g., CHDBrClF):

```c
// Track different H isotopes:
// num_iso_H[0] = non-isotopic H count
// num_iso_H[1] = 1H count  
// num_iso_H[2] = 2H (Deuterium) count
// num_iso_H[3] = 3H (Tritium) count

// If different isotopes can create stereochemistry:
// t_parity for non-isotopic calculation
// t_parityInv for isotopic calculation
// nCompInv2Abs indicates relationship between them
```

## Key Source Files

| File | Purpose |
|------|---------|
| `INCHI_BASE/src/ichister.c` | Main stereochemistry processing (4904 lines) |
| `INCHI_BASE/src/ichister.h` | Header with function declarations |
| `INCHI_BASE/src/ichi.h` | `INChI_Stereo` structure definition |
| `INCHI_BASE/src/extr_ct.h` | Parity value definitions |

## Key Functions

| Function | Purpose |
|----------|---------|
| `set_stereo_parity()` | Main entry point, orchestrates all stereo detection |
| `set_stereo_atom_parity()` | Calculates tetrahedral stereocenter parity |
| `set_stereo_bonds_parity()` | Calculates double bond and cumulene parity |
| `half_stereo_bond_parity()` | Calculates half-parity for one end of stereobond |
| `bCanAtomBeAStereoCenter()` | Determines if atom can be tetrahedral stereocenter |
| `bCanAtomHaveAStereoBond()` | Determines if atom can participate in stereobond |
| `triple_prod()` | Calculates triple product for parity determination |
| `GetStereocenter0DParity()` | Handles 0D (no coordinates) parity calculation |

## Stereochemistry Flags

The InChI library uses several flags to control stereochemistry processing (from `ichister.h`):

```c
#define PES_BIT_POINT_EDGE_STEREO    1  // Use pointed edge for stereo
#define PES_BIT_PHOSPHINE_STEREO     2  // Enable phosphine stereochemistry
#define PES_BIT_ARSINE_STEREO        4  // Enable arsine stereochemistry  
#define PES_BIT_FIX_SP3_BUG          8  // Fix SP3 stereo calculation bug
```

## Edge Cases Handled

1. **2D vs 3D coordinates**: 2D drawings use wedge/dash conventions; 3D uses explicit coordinates
2. **Planar ambiguity**: When 4 atoms appear in plane (undefined)
3. **Implicit hydrogens**: Reconstructed from valence information
4. **Isotopic hydrogens**: Treated as different atoms for stereochemistry
5. **Ring systems**: Special handling for stereochemistry in rings
6. **Cumulenes**: Complex stereochemistry in chains of double bonds
7. **N/V stereobonds**: Nitrogen and phosphorus can have stereochemistry via lone pairs

---

*Pipeline documentation: Stereochemistry Processing step*
