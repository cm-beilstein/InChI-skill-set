# Enhanced Stereochemistry - Data Structures

**Analysis Date:** 2026-04-23

---

## Core Data Structures

### AT_STEREO_CARB (Tetrahedral Stereo)

From `extr_ct.h`:
```c
typedef struct tagStereoCarb {
    AT_NUMB at_num;     // Atom number in canonical order
    U_CHAR  parity;     // Parity value
                         // 0 = undefined/not specified
                         // 1 = odd (counter-clockwise, R)
                         // 2 = even (clockwise, S)
                         // 3 = unknown
} AT_STEREO_CARB;
```

### AT_STEREO_DBLE (Double Bond Stereo)

From `extr_ct.h`:
```c
typedef struct tagStereoDble {
    AT_NUMB at_num1;   // First atom of stereo double bond
    AT_NUMB at_num2;   // Second atom
    U_CHAR  parity;     // Parity value
                         // 0 = undefined/not specified
                         // 1 = odd (cis/Z)
                         // 2 = even (trans/E)
                         // 3 = unknown
} AT_STEREO_DBLE;
```

### INChI_Stereo (Output Structure)

From `ichi.h`:
```c
typedef struct tagINChI_Stereo {
    int      nNumberOfStereoCenters;        // Count of tetrahedral centers
    AT_NUMB *nNumber;                      // Canonical numbers [nNumberOfStereoCenters]
    S_CHAR  *t_parity;                       // Tetrahedral parities
    AT_NUMB *nNumberInv;                    // Invariant representation numbers
    S_CHAR  *t_parityInv;                  // Invariant parities
    int      nCompInv2Abs;                  // Comparison result
                         // -1: Inv < Abs
                         // +1: Inv > Abs
                         // +2: No /m, /s found
    int      bTrivialInv;                   // Uses trivial inversion
    int      nNumberOfStereoBonds;          // Count of double bonds
    AT_NUMB *nBondAtom1;                     // First atom [nNumberOfStereoBonds]
    AT_NUMB *nBondAtom2;                     // Second atom
    S_CHAR  *b_parity;                       // Bond parities
} INChI_Stereo;
```

### ORIG_ATOM_DATA Input Structure

From `strutil.h`:
```c
typedef struct tagORIG_ATOM_DATA {
    int          num_atoms;
    ATOM_DATA   *at;                        // [num_atoms]
    int          num_bonds;
    BOND_DATA   *bond;                     // [num_bonds]
    // ... other fields ...
    // Enhanced stereo data
    U_CHAR      *nStereoKind;              // [num_atoms]
                         // 0 = no enhanced stereo
                         // MOL_FMT_V3000_STEABS = absolute
                         // MOL_FMT_V3000_STEREL = relative
                         // MOL_FMT_V3000_STERAC = racemic
} ORIG_ATOM_DATA;
```

---

## Constants

From `mol_fmt.h`:
```c
#define MOL_FMT_V3000_STEABS  1   // Absolute stereogroup
#define MOL_FMT_V3000_STEREL 2   // Relative stereogroup
#define MOL_FMT_V3000_STERAC 3   // Racemic stereogroup
```

From `ichi.h` and `inchi_api.h`:
```c
#define AB_PARITY_NONE   0    // No stereochemistry
#define AB_PARITY_ODD    1    // Odd parity (R or Z)
#define AB_PARITY_EVEN   2    // Even parity (S or E)
#define AB_PARITY_UNKN   3    // Unknown
#define AB_PARITY_UNDF   4    // Undefined
```

---

## Memory Layout

### Input Phase (V3000 Parsing)

```
ORIG_ATOM_DATA
├─ num_atoms: 10
├─ at[10]: atom data
│   ├─[0]: {element='C', x, y, z, ...}
│   ├─[1]: {element='C', ...}
│   └─ ...
├─ nStereoKind[10]: {0, 1, 1, 2, 3, 0, ...}
│   │  │  │  │  └─ Racemic
│   │  │  │  └─ Relative
│   │  │  └─ Relative
│   │  └─ Absolute
│   └─ No enhanced stereo
└─ ...
```

### Processing Phase (Canonicalization)

```
CANON_STAT
├─ LinearCTStereoCarb[10]: {at_num, parity}
│   ├─[0]: {1, 1}    // Atom 1, odd (R)
│   ├─[1]: {2, 2}    // Atom 2, even (S)
│   └─ ...
├─ LinearCTStereoDble[5]: {at_num1, at_num2, parity}
└─ ...
```

### Output Phase (InChI Generation)

```
INChI_Stereo
├─ nNumberOfStereoCenters: 6
├─ nNumber[6]: {1, 2, 3, 4, 5, 6}     // Canonical numbers
├─ t_parity[6]: {1, 2, 1, 2, 1, 2}   // R,S,R,S,R,S
├─ nCompInv2Abs: 0                     // /m0
├─ nNumberOfStereoBonds: 2
├─ nBondAtom1[2]: {1, 3}
├─ nBondAtom2[2]: {2, 4}
└─ b_parity[2]: {1, 2}                 // cis, trans
```

---

## Function Signatures

### Parsing Functions

```c
// mol_fmt3.c
int MolfileV3000ReadEnhancedStereo(
    const char *field,        // e.g., "/STEABS"
    int stereo_kind,         // Output: STEABS/STEREL/STERAC
    const char *atom_list    // e.g., "(4 1 2 3 4)"
);
```

### Processing Functions

```c
// strutil.c
int set_EnhancedStereo_t_m_layers(
    const ORIG_ATOM_DATA *orig_inp_data,
    INChI *pINChI,
    INChI_Aux *pINChI_Aux
);
```

### Output Functions

```c
// ichiprt1.c
int OutputINCHI_StereoLayer_EnhancedStereo(
    CANON_GLOBALS *pCG,
    INCHI_IOSTREAM *out_file,
    INCHI_IOS_STRING *strbuf,
    INCHI_OUT_CTL *io,
    const ORIG_ATOM_DATA *orig_inp_data,
    const char *pLF,
    const char *pTAB
);
```

---

## Size Limits

| Parameter | Limit | Notes |
|-----------|-------|-------|
| Max atoms | 32,767 | V3000 removes V2000 limits |
| Max stereo centers | num_atoms | Each atom can be stereo center |
| Max stereogroups | num_atoms | Each group needs at least 1 atom |
| Stereo bonds | num_bonds | Each bond can have stereo |

---

## References

- `extr_ct.h`: Lines 76-87 - Stereo structure definitions
- `ichi.h`: Lines 121-154 - Output structure
- `strutil.h`: Lines 220-240 - Input structure
- `mol_fmt.h`: Lines 113-143 - V3000 stereo constants

---

*Data Structures: 2026-04-23*