# Stereo Layer (Tetrahedral, `/s`)

**Analysis Date:** 2026-04-22

## Overview

The tetrahedral stereo layer (`/s`) captures the three-dimensional stereochemistry of atoms with four non-coplanar substituents arranged in a tetrahedral geometry. This layer represents chiral centers, enantiomers, and diastereomers in the InChI identifier—essential information for distinguishing molecules that are otherwise identical in their connectivity but differ in spatial arrangement.

### When the Layer is Used

The tetrahedral stereo layer is generated when a molecule contains:

1. **Stereogenic centers (sp3 carbons, nitrogens, phosphors, etc.)** — atoms bonded to four distinct substituents in a non-planar configuration
2. **Allene-type cumulenes** — atoms with cumulated double bonds showing tetrahedral stereochemistry
3. **Axial chirality** — certain atropisomeric arrangements

The layer is omitted if all stereocenters are undefined, unknown, or if stereochemistry is explicitly not requested via InChI generation options.

### Output Format

The tetrahedral stereo appears in the InChI string as `/s` followed by parity values:

```
InChI=1S/C3H6O/c1-2-3/h2-3H2O/c1-2-3/h2H
```

For absolute stereochemistry, the output uses `/s1` to indicate defined tetrahedral stereo, where the number represents the parity encoding:
- **Parity 1 (Odd)**: Counter-clockwise arrangement when viewed from the priority-4 substituent
- **Parity 2 (Even)**: Clockwise arrangement when viewed from the priority-4 substituent

For stereo layers containing only isotopic information that differs from the non-isotopic layer, the layer outputs `/s1+2` indicating "isotope-only" parity changes.

---

## Code Implementation

### Key Source Files

| File | Purpose |
|------|---------|
| `INCHI-1-SRC/INCHI_BASE/src/ichister.c` | Core stereo parity calculation (4904 lines) |
| `INCHI-1-SRC/INCHI_BASE/src/ichister.h` | Function declarations and definitions |
| `INCHI-1-SRC/INCHI_BASE/src/ichicans.c` | Canonicalization of stereo descriptors to CT |
| `INCHI-1-SRC/INCHI_BASE/src/ichiprt3.c` | String output for tetrahedral stereo (`str_Sp3`) |
| `INCHI-1-SRC/INCHI_BASE/src/ichi.h` | Core `INChI_Stereo` structure definition |
| `INCHI-1-SRC/INCHI_BASE/src/extr_ct.h` | `AT_STEREO_CARB` structure |

### Core Data Structures

#### INChI_Stereo Structure

Defined in `INCHI-1-SRC/INCHI_BASE/src/ichi.h` (lines 121-154):

```c
typedef struct tagINChI_Stereo
{
    int         nNumberOfStereoCenters;
    AT_NUMB    *nNumber;      /* Canonical number of tetrahedral stereogenic atom */
    S_CHAR     *t_parity;     /* tetrahedral atom parities (1=odd, 2=even, 3=unknown) */
    AT_NUMB    *nNumberInv;  /* Canonical number in inverted structure */
    S_CHAR     *t_parityInv; /* inverted atom parities */
    int         nCompInv2Abs; /* -1: Inv < Abs; +1: Inv > Abs; +2: no /m, /s found */
    int         bTrivialInv;  /* 1=> inverted uses trivial inversion */
    int         nNumberOfStereoBonds;
    AT_NUMB    *nBondAtom1;
    AT_NUMB    *nBondAtom2;
    S_CHAR     *b_parity;
} INChI_Stereo;
```

#### AT_STEREO_CARB Structure

Defined in `INCHI-1-SRC/INCHI_BASE/src/extr_ct.h` (lines 76-80):

```c
typedef struct tagStereoCarb
{
    AT_NUMB at_num;     /* Atom number in canonical order */
    U_CHAR  parity;     /* Parity value: 0=undefined, 1=odd, 2=even, 3=unknown */
} AT_STEREO_CARB;
```

### Stereo Parity Values

The parity system uses explicit values:

```c
#define PARITY_ODD   1    /* 3 transpositions (counter-clockwise) */
#define PARITY_EVEN  2    /* 0 or 2 transpositions (clockwise) */
#define PARITY_UNDF  3    /* undefined/unknown geometry */
```

Parity 1 indicates that reordering the four substituents requires an odd number of transpositions to reach sorted order. Parity 2 indicates an even number (including zero) of transpositions.

---

## Pseudo-code Algorithm

### Tetrahedral Stereo Detection

The main entry point is `set_stereo_parity()` in `ichister.c`:

```
set_stereo_parity():
    Initialize count of stereo atoms and bonds
    For each atom in molecule:
        if bCanAtomBeAStereoCenter(atom):
            if set_stereo_atom_parity() == success:
                Increment num_stereo_atoms
        else if bCanAtomHaveAStereoBond(atom):
            if set_stereo_bond_parity() == success:
                Increment num_stereo_bonds
    Return parity arrays
```

### Core Parity Calculation (`set_stereo_atom_parity`)

```
set_stereo_atom_parity(atom, neighbors, coords):
    1. Identify 4 neighbors attached to central atom
    2. if any neighbor is Implicit H (reconstructed):
         - parity = undefined
         - return
    3. if 2D coordinates:
         - Check for in-plane ambiguity (Get2DTetrahedralAmbiguity)
         - If ambiguous, mark parity as unknown
    4. if 3D coordinates:
         - Calculate vectors from central atom to each neighbor
         - Compute triple product (v1 × v2) · v3 to determine handedness
         - Sign > 0: clockwise → parity 2
         - Sign < 0: counterclockwise → parity 1
         - Sign ≈ 0: undefined (flat geometry)
    5. Adjust for neighbor ordering:
         - Count transpositions needed to sort neighbors by priority
         - parity = (base_parity + num_transpositions) % 2
    6. return computed parity
```

### Triple Product Calculation

The core geometric calculation uses the scalar triple product to determine the handedness of the tetrahedron:

```
triple_product(v1, v2, v3) = v1 · (v2 × v3)

Where:
    - v1, v2, v3 are vectors from central atom to three substituents
    - Result > 0: counter-clockwise (viewed from above v1 toward origin)
    - Result < 0: clockwise
    - Result ≈ 0: atoms are coplanar (undefined)
```

---

## Examples

### Example 1: Simple Chiral Center (L-Alanine)

**Molecule**: L-alanine (S-alanine)

```
InChI=1S/C3H7NO2/c1-3(5)4-2/h2-4H2,(H,5)/t3-/m0/s1
```

**Breakdown**:
- Layer `/s1` indicates absolute (not relative) tetrahedral stereo
- Stereo center at carbon-3 (the alpha carbon)
- Parity `/m0/s1` shows `m0` (stereo is absolute, not inverted) and `s1` (parity=odd)

### Example 2: D-alanine (R-Alanine)

```
InChI=1S/C3H7NO2/c1-3(5)4-2/h2-4H2,(H,5)/t3-/m1/s1
```

**Comparison**:
- Identical connectivity layer
- `/m1` indicates inverted absolute configuration (mirrored)
- `/s1` still present but compared to `/s` in original structure

### Example 3: Enantiomer Set

| Molecule | InChI Stereo Layer | Parity |
|----------|------------------|--------|
| (R)-2-butanol | `/s1` (if /m0) | Odd |
| (S)-2-butanol | inverted from R | Even to odd |
| Racemic mixture | `/s0` | Layer omitted |

### Example 4: Two Stereocenters

For meso-tartaric acid (identical R,S configuration):

```
InChI=1S/C4H6O6/c5-1(3(7)8)2(6)4(9)10/h1-2H,(H,5),(H,6),(H,7),(H,8),(H,9),(H,10O)/t1/,t2-/m0/s1
```

The `/t` layer indicates connectivity between stereocenters.

---

## Implementation Notes

### Stereogenic Center Eligibility

From `ichister.c` line 52:

```c
int bCanAtomBeAStereoCenter( char *elname, S_CHAR charge, S_CHAR radical )
```

The function checks if an atom CAN be a stereocenter based on:
- Element type (C, N, P, S, B, Si, etc.)
- Formal charge (certain charges invalidate)
- Radical state
- Whether all four substituents are distinct

### Relaxed Criteria

InChI supports "loose" tetrahedral stereo checking for in-ring systems with ambiguous 2D drawings:

```
LooseTSACheck flag (line 2811 in ichiparm.c):
Relax criteria of ambiguous drawing for in-ring tetrahedral stereo
```

This prevents false "undefined" assignments for ring systems where geometry is inherently constrained.

### Isotopic Stereo

The tetrahedral layer also captures isotopic stereochemistry. The `LinearCTIsotopicStereoCarb` array stores separate parities for isotopically-labeled atoms. When only isotopic stereo differs, the layer outputs with a leading `+` character such as `/s1+2`.

---

## Relationship to Other Layers

The `/t` layer (tetrahedral) interacts with:

1. **Connectivity Layers (`/c`, `/h`)**: Required for atom ordering (canonical numbers)
2. **Charge Layer (`/q`)**: Charged atoms affect stereocenter eligibility
3. **Isotope Layer (`/i`)**: Can create isotopic stereocenters distinct from non-isotopic
4. **Mobile H Layer (`/m`)**: Parity inversion flag for tautomeric transformations
5. **Double Bond Stereo (`/b`)**: Tetrahedral centers may be connected by double bonds
6. **Stereo Type (`/s`)**: Absolute/relative/racemic designation

---

## Historical Context

The tetrahedral stereochemistry layer has been part of InChI since version 1.0. The implementation in `ichister.c` underwent significant bug fixes, including the `PES_BIT_FIX_SP3_BUG` flag (line 84) addressing issues with phosphine and arsine stereo centers in earlier versions.

The parity encoding scheme (1=odd, 2=even) follows the CIP priority rules, where the substituent with lowest CIP priority is placed at the back, and the remaining three determine handedness.

---

*Tetrahedral stereo layer analysis: 2026-04-22*