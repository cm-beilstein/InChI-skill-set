# Enhanced Stereochemistry - Workflow

**Analysis Date:** 2026-04-23

---

## Complete Processing Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENHANCED STEREO WORKFLOW                        │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Input Detection
┌─────────────────────────────────────────────────────────────────┐
│                    V3000 Molfile                                │
│                         │                                        │
│  Header: "V3000" found? ──YES──► Parse as V3000               │
│                         │                                        │
│                        NO                                        │
│                         ▼                                        │
│              Parse as V2000 (no enhanced stereo)               │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
Step 2: Collection Block Parsing
┌─────────────────────────────────────────────────────────────────┐
│  mol_fmt3.c: MolfileV3000ReadEnhancedStereo()                  │
│                         │                                        │
│  ┌───────────────────────┴───────────────────────┐              │
│  │                                               │              │
│  ▼                                               ▼              │
│ Detect "BEGIN COLLECTION"             Ignore if not present  
│        │                                               │
│  ┌─────┴─────┐                                        │
│  │           │                                        │
│  ▼           ▼                                        │
│ Parse MDLV30/STEABS            Not present ──► No enhanced
│ Parse MDLV30/STERELn                                            
│ Parse MDLV30/STERACn                                              │
│        │                                                     │
│        ▼                                                     │
│ Store in orig_inp_data->nStereoKind[]                         │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
Step 3: Atom/Bond Processing
┌─────────────────────────────────────────────────────────────────┐
│  mol_fmt3.c: MolfileV3000ReadAtomsBlock()                       │
│  mol_fmt3.c: MolfileV3000ReadBondsBlock()                       │
│                         │                                        │
│  For each atom:                                                    │
│    - Store element, coordinates                                    │
│    - Check if atom has enhanced stereo (from nStereoKind[])      │
│    - Mark for later processing                                   │
│                         │                                        │
│  For each bond:                                                  │
│    - Store bond type                                           │
│    - Store bond stereo if applicable                          │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
Step 4: Canonical Numbering
┌─────────────────────────────────────────────────────────────────┐
│  ichicano.c: DetermineCanonicalNumbering()                  │
│                         │                                        │
│  - Build neighbor lists                                        │
│  - Perform DFS-based ranking                                  │
│  - Assign canonical numbers to all atoms                    │
│                         │                                        │
│  The canonical number maps original atom to InChI position  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
Step 5: Enhanced Stereo Building
┌─────────────────────────────────────────────────────────────────┐
│  strutil.c: set_EnhancedStereo_t_m_layers()                    │
│                         │                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Phase 5a: Build /t (tetrahedral) layer                    │  │
│  │                                                           │  │
│  │ For each atom in enhanced stereo group:                  │  │
│  │   1. Get canonical number                                 │  │
│  │   2. Calculate parity (R/S)                              │  │
│  │   3. Add to /t layer entry                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Phase 5b: Build /m (inversion) layer                     │  │
│  │                                                           │  │
│  │ Determine overall inversion type:                       │  │
│  │   /m0 = All absolute (configuration as given)            │  │
│  │   /m1 = Inverted (mirrored from input)                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌───────���───────────────────────────────────────────────────┐  │
│  │ Phase 5c: Build /s (stereo type) layer                   │  │
│  │                                                           │  │
│  │ s1 = All groups absolute                                 │  │
│  │ s2 = Has relative groups                                 │  │
│  │ s3 = Has racemic groups                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
Step 6: Output Generation
┌─────────────────────────────────────────────────────────────────┐
│  ichiprt1.c: OutputINCHI_StereoLayer_EnhancedStereo()           │
│                         │                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Output /t layer:                                         │  │
│  │ Format: /t1,2,3,4m,...                                   │  │
│  │ (m suffix = has enhanced stereo)                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Output /m layer:                                        │  │
│  │ Format: /m0 or /m1 or /m0,1                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Output /s layer:                                         │  │
│  │ Format: /s1(atoms)2(atoms)(atoms)3(atoms)(atoms)        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
Final Output: Enhanced Stereo InChI
```

---

## Detailed Step Analysis

### Step 2: Collection Parsing Details

```c
// From mol_fmt3.c:695
int MolfileV3000ReadEnhancedStereo(..., char *field, int stereo_kind) {
    
    // Parse collection header
    if (strcmp(field, "/STEABS") == 0) {
        stereo_kind = MOL_FMT_V3000_STEABS;
        // Parse ATOMS=(n id id ...)
        nStereoKind[atom_id] = STEABS;
    }
    else if (strcmp(field, "/STEREL") == 0) {
        stereo_kind = MOL_FMT_V3000_STEREL;
        nStereoKind[atom_id] = STEREL;
    }
    else if (strcmp(field, "/STERAC") == 0) {
        stereo_kind = MOL_FMT_V3000_STERAC;
        nStereoKind[atom_id] = STERAC;
    }
}
```

### Step 5a: Tetrahedral Layer Building

```c
// From strutil.c:7266
int set_EnhancedStereo_t_m_layers(const ORIG_ATOM_DATA *orig_inp_data,
                                   INChI *pINChI, INChI_Aux *pINChI_Aux) {
    
    // For each stereo group:
    //   - Get list of atoms
    //   - Get canonical numbers
    //   - Calculate parity
    //   - Add to pINChI->Stereo->t_parity[]
    
    // Build /t layer string: "1m,2m,3m,4m"
    for (i = 0; i < nNumStereoAtoms; i++) {
        // Add canonical number with "m" suffix
    }
}
```

### Step 5b: Inversion Flag

The `/m` layer indicates whether the entire structure has been inverted relative to the input:

```c
// Determine inversion
if (bInv2Abs == -1)  // Inverted < Absolute
    pINChI->Stereo->nCompInv2Abs = -1;  // Output: /m1
else if (bInv2Abs == 1)  // Inverted > Absolute
    pINChI->Stereo->nCompInv2Abs = 1;   // Output: /m0
```

### Step 5c: Stereo Type

```c
// Output /s layer - ONE 's' prefix with all groups concatenated
if (bHasSTEABS && !bHasSTEREL && !bHasSTERAC)
    output_s = "/s1(atoms)";       // Absolute only
else if (bHasSTEREL && !bHasSTERAC)
    output_s = "/s1(atoms)2(atoms)"; // Absolute + Relative
else if (bHasSTEREL && bHasSTERAC)
    output_s = "/s1(atoms)2(atoms)3(atoms)"; // All three types
// Multiple groups of same type use separate parentheses: s2(4)(6,8)
```

---

## Error Cases and Recovery

### Invalid Collection Data

1. **Missing required keyword**:
   ```
   Expected: MDLV30/STEABS
   Got: CUSTOM/TAG
   → Warning, use basic stereo only
   ```

2. **Invalid atom reference**:
   ```
   ATOMS=(10) but molecule has only 5 atoms
   → Error: Invalid atom in collection
   ```

3. **Duplicate membership**:
   ```
   Atom 3 appears in STEABS and STEREL
   → Error: Atom in multiple groups
   ```

---

## Performance Considerations

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Collection parsing | O(n) | n = atoms in collection |
| Canonical numbering | O(n²) | Standard InChI |
| Stereo layer output | O(n) | n = enhanced stereo atoms |

---

## References

- `mol_fmt3.c`: Lines 695-780 - Collection parsing
- `strutil.c`: Lines 7266-7400 - Layer building
- `ichiprt1.c`: Lines 3508-3600 - Output generation

---

*Workflow: 2026-04-23*