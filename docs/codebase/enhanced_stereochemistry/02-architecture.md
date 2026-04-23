# Enhanced Stereochemistry - Architecture

**Analysis Date:** 2026-04-23

---

## Data Flow Architecture

```
Input File (V3000 molfile)
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  mol_fmt3.c: MolfileV3000ReadEnhancedStereo()          │
│  └─ Parse Collection Block (STEABS, STERELn, STERACn)│
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  SETTINGS: orig_inp_data->nStereoKind[]                │
│  Stores: stereo_kind, atom_list for each group       │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  strutil.c: set_EnhancedStereo_t_m_layers()         │
│  - Creates /t layer entries for all centers           │
│  - Creates /m layer with inversion flags               │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  ichiprt1.c: OutputINCHI_StereoLayer_EnhancedStereo() │
│  - Formats enhanced stereo output                      │
│  - Outputs /t, /m, /s layers                         │
└─────────────────────────────────────────────────────────┘
        │
        ▼
InChI String with Enhanced Stereo
```

---

## Key Source Files

### Input Processing

| File | Function | Purpose |
|------|----------|---------|
| `mol_fmt3.c` | `MolfileV3000ReadEnhancedStereo()` | Parse V3000 collection block |
| `mol_fmt3.c` | ` MolfileV3000ReadBondsBlock()` | Parse enhanced bond stereo |
| `mol_fmt.h` | `MOL_FMT_V3000_STEABS`, `STEREL`, `STERAC` | Constants |

### Core Processing

| File | Function | Purpose |
|------|----------|---------|
| `strutil.c` | `set_EnhancedStereo_t_m_layers()` | Build t/m layers from groups |
| `ichister.c` | `set_stereo_parity()` | Calculate parity for centers |
| `ichiprt1.c` | `OutputINCHI_StereoLayer_EnhancedStereo()` | Format output |

### Data Structures

From `extr_ct.h`:
```c
typedef struct tagStereoCarb {
    AT_NUMB at_num;     // Atom number in canonical order
    U_CHAR  parity;     // Parity: 0=undefined, 1=odd, 2=even, 3=unknown
} AT_STEREO_CARB;

typedef struct tagStereoDble {
    AT_NUMB at_num1;    // First atom of stereogenic double bond
    AT_NUMB at_num2;   // Second atom
    U_CHAR  parity;     // Parity: 1=odd(cis/Z), 2=even(trans/E), 3=unknown
} AT_STEREO_DBLE;
```

From `ichi.h`:
```c
typedef struct tagINChI_Stereo {
    int      nNumberOfStereoCenters;
    AT_NUMB *nNumber;          // Canonical numbers
    S_CHAR  *t_parity;        // Tetrahedral parities
    int     nCompInv2Abs;     // -1: Inv < Abs; +1: Inv > Abs; +2: no /m,/s
    int     bTrivialInv;       // Uses trivial inversion
    int     nNumberOfStereoBonds;
    AT_NUMB *nBondAtom1;
    AT_NUMB *nBondAtom2;
    S_CHAR  *b_parity;        // Double bond parities
} INChI_Stereo;
```

From `ichidrp.h` (INPUT_PARMS):
```c
int bEnhancedStereo;  // Enable enhanced stereochemistry
```

---

## Processing Pipeline

### Phase 1: Input Parsing

```
V3000 molfile
    │
    ▼ (mol_fmt3.c)
┼──────────────────────────────────────┤
│ Detect "V3000" in counts line        │
│ Detect COLLECTION block             │
│ Parse STEABS/STERELn/STERACn groups  │
│ Store in orig_inp_data->nStereoKind[]│
└──────────────────────────────────────┘
```

### Phase 2: Canonicalization

```
Original structure
    │
    ▼ (ichicano.c)
┼──────────────────────────────────────┤
│ Build LinearCTStereoCarb[]           │
│ Build LinearCTStereoDble[]           │
│ Assign canonical numbers           │
│ Calculate parities                  │
└──────────────────────────────────────┘
```

### Phase 3: Enhanced Stereo Layer Building

```
SETTINGS (stereo groups)
    │
    ▼ (strutil.c)
┼──────────────────────────────────────┤
│ For each group:                      │
│   - Get atom list from collection    │
│   - Get canonical numbers            │
│   - Calculate parity                │
│   - Set /t layer entry              │
│ Build /m layer (inversion flags)   │
└──────────────────────────────────────┘
```

### Phase 4: Output Generation

```
INChI_Stereo structure
    │
    ▼ (ichiprt1.c)
┼──────────────────────────────────────┤
│ Check bEnhancedStereo flag         │
│ Call OutputINCHI_StereoLayer_...() │
│ Format as /t#m# /m# /s#          │
└──────────────────────────────────────┘
```

---

## Stereo Group Storage

Enhanced stereo groups are stored in the original input data structure:

```c
typedef struct tagORIG_ATOM_DATA {
    // ... other fields ...
    U_CHAR *nStereoKind;      // [nAtoms] - Enhanced stereo kind per atom
    // STEABS, STEREL, STERAC per atom
} ORIG_ATOM_DATA;
```

Each atom stores:
- `0` = No enhanced stereo
- `MOL_FMT_V3000_STEABS` = In absolute stereogroup
- `MOL_FMT_V3000_STEREL` = In relative stereogroup  
- `MOL_FMT_V3000_STERAC` = In racemic stereogroup

---

## Key Functions Reference

| Function | Location | Purpose |
|----------|----------|---------|
| `MolfileV3000ReadEnhancedStereo()` | mol_fmt3.c:695 | Parse collection block |
| `set_EnhancedStereo_t_m_layers()` | strutil.c:7266 | Build t/m layers |
| `OutputINCHI_StereoLayer_EnhancedStereo()` | ichiprt1.c:3508 | Generate output |
| `CreateLinearCTStereoCarb()` | ichicant.c | Build stereo array |
| `set_stereo_parity()` | ichister.c | Calculate parities |

---

## Layer Output Format

### Tetrahedral (/t) Layer

For enhanced stereo, `/t` lists all tetrahedral centers with their parities:

```
/t1,2,3,4,5
```

Where each number represents a canonical atom with tetrahedral stereo.

### Mobile-H Inversion (/m) Layer

```
/m0        // Absolute, configuration as given
/m1        // Inverted (mirrored)
/m0,1       // Mix of absolute and inverted groups
```

### Stereo Type (/s) Layer

```
/s1        // Absolute (default)
/s2        // Relative
/s3        // Racemic
```

---

## References

- `ichi.h`: INChI_Stereo structure definition
- `extr_ct.h`: AT_STEREO_CARB, AT_STEREO_DBLE
- `ichidrp.h`: INPUT_PARMS with bEnhancedStereo
- `ichicant.h`: CANON_STAT with stereo arrays

---

*Architecture: 2026-04-23*