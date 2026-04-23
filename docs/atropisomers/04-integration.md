# Atropisomer Integration and Data Flow

**Analysis Date:** 2026-04-23

---

## Complete Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INPUT PARSING (mol*.c)                                   │
│    Read V2000/V3000 molfile                                 │
│    Extract atoms, bonds, 3D coordinates                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. RING DETECTION (ichimake.c → ring_detection.c)          │
│    ip->Atropisomers check                                  │
│    find_rings() → RingSystems structure                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ATROPISOMER DETECTION (atropisomers.c)                  │
│    find_atropisomeric_atoms_and_bonds()                    │
│    Scoring algorithm + planarity checks                    │
│    Mark atoms: bAtropisomeric = 1                          │
│    Set: orig_inp_data->bAtropisomer = 1                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. NORMALIZATION & TAUTOMERISM (ichinorm.c)               │
│    Duplicate structure for preprocessing                    │
│    Copy atropisomer flags forward                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. CANONICALIZATION (ichicano.c)                           │
│    Assign canonical atom numbers                           │
│    Compute canonical orderings (normal + inverted)         │
│    Store in INChI_Aux structure                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. LAYER BUILDING (strutil.c & ichiprt1.c)                │
│    set_Atropisomer_t_m_layers()                            │
│    Collect canonical atoms                                 │
│    Sort by canonical number                                │
│    Determine /m layer (enantiomeric vs diastereomeric)    │
│    Populate INChI_Stereo structure                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. OUTPUT GENERATION (ichiprt1.c)                          │
│    OutputINCHI_StereoLayer() formats /t and /m layers      │
│    Assemble final InChI string                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
               InChI with /t and /m layers
```

---

## Data Structures and Flags

### Input-side Flags

#### in `inp_ATOM` (inpdef.h:187)
```c
AT_NUMB bAtropisomeric;  // Set during detection
                         // Propagated through processing
```

#### in `ORIG_ATOM_DATA` (inpdef.h:466)
```c
int bAtropisomer;  // Master flag: 1 if ANY atropisomers detected
                   // Used to gate layer building
```

#### in `INPUT_PARMS` (ichidrp.h:193)
```c
int Atropisomers;  // User-provided flag: enable/disable detection
                   // From CLI: -Atropisomers
                   // From API: ip->Atropisomers = 1
```

### Canonicalization-side Data

#### in `INChI_Aux`
```c
AT_NUMB *nOrigAtNosInCanonOrd;      // [nNumberOfAtoms]
                                     // For each canonical number,
                                     // which original atom number
AT_NUMB *nOrigAtNosInCanonOrdInv;   // Same for inverted structure
                                     // NULL if not computed
RingSystems *ring_result;            // Ring systems for atropo detection
```

### Output Structure

#### in `INChI_Stereo`
```c
int           nNumberOfStereoCenters;
AT_NUMB      *nNumber;               // Canonical atom numbers
S_CHAR       *t_parity;              // Parities (all 1 for atropo)
int           nCompInv2Abs;          // -1: /m1, +1: /m0
```

---

## Key Function Call Sites

### Detection Initiation (ichimake.c:3908-3925)

```c
orig_inp_data->bAtropisomer = 0;  // Initialize

if (ip->Atropisomers) {  // User enabled feature
    RingSystems *ring_result = find_rings(out_at, num_atoms);
    
    int ret_ai = find_atropisomeric_atoms_and_bonds(
        out_at, num_atoms, ring_result, orig_inp_data);
    
    // Copy flags back
    if (orig_inp_data->bAtropisomer) {
        for (i = 0; i < num_atoms; i++) {
            orig_inp_data->at[i].bAtropisomeric = 
                out_at[i].bAtropisomeric;
        }
    }
    
    free_ring_system(ring_result);
}
```

### Layer Building (ichiprt1.c:1622-1628)

```c
if (ip->Atropisomers) {
    if (set_Atropisomer_t_m_layers(orig_inp_data, pINChI, pINChI_Aux)) {
        // Mark layers for output
        io.sDifSegs[io.nCurINChISegment][DIFS_t_SATOMS] = DIFV_OUTPUT_FILL_T;
        io.sDifSegs[io.nCurINChISegment][DIFS_m_SP3INV] = DIFV_OUTPUT_FILL_T;
    }
}
```

### Output Formatting (ichiprt1.c:1779-1781)

```c
if (ip->bEnhancedStereo) {
    // Enhanced stereo takes precedence
    intermediate_result = OutputINCHI_StereoLayer_EnhancedStereo(
        pCG, out_file, strbuf, &io, orig_inp_data, pLF, pTAB);
} else {
    // Standard or atropisomer stereo
    intermediate_result = OutputINCHI_StereoLayer(
        pCG, out_file, strbuf, &io, pLF, pTAB);
}
```

---

## Interaction with Other Features

### Enhanced Stereochemistry

**Both can be active simultaneously:**
- Atropisomers populate `/t` and `/m` with axis atoms
- Enhanced stereo adds grouped atoms with STEABS/STEREL/STERAC
- Output order: Atropisomers first (in layer building), then Enhanced Stereo

**Code Order:**
```c
// ichiprt1.c:1622-1633
if (ip->Atropisomers) {
    set_Atropisomer_t_m_layers(...);  // First
}
if (ip->bEnhancedStereo) {
    set_EnhancedStereo_t_m_layers(...);  // Then
}
```

### Tautomerism

**Independent feature**, no special interaction:
- Tautomeric forms processed separately
- Each tautomer gets its own atropisomer detection
- Results combined in final output

### Isotopic Labeling

**Independent**:
- Isotopes don't affect atropisomer detection
- Detection uses atomic numbers, not isotopes
- `/t` layer includes all stereo atoms (both isotopic and atropo)

---

## Command-Line Integration

### CLI Flags

```bash
# Enable atropisomer detection
inchi-1 molecule.mol -Atropisomers

# Combine with other options
inchi-1 molecule.mol -Atropisomers -FixedH -o output.txt
inchi-1 molecule.mol -Atropisomers -LargeMolecules
```

### Parameter Parsing (ichiparm.c)

```c
// Line 282: Set Atropisomers flag
*pbAtropisomers = 1;

// Line 2154: Copy to INPUT_PARMS
ip->Atropisomers = bAtropisomers;
```

---

## API Integration

### Setting the Flag

```c
#include "inchi_api.h"

inp_ATOM *at = ...;  // Atom structure
int num_atoms = ...;

INPUT_PARMS ip;
ip.Atropisomers = 1;  // Enable

char szInChI[INCHI_MAX_SZ];
int ret = MakeINCHI(at, num_atoms, NULL, &ip,
                    szInChI, NULL, NULL, NULL);
```

### Checking Results

```c
if (strstr(szInChI, "/t") && strstr(szInChI, "/m")) {
    // Likely contains atropisomer info
    // But could also be classical stereo
    
    // To be certain, check for "m" suffix in /t layer:
    if (strstr(szInChI, "m,") || strchr(szInChI, 'm')) {
        // Confirmed: contains atropisomeric atoms
    }
}
```

---

## Data Flow Example: Biphenyl

**Input:** Biphenyl with ortho chlorines

```
        Cl
         |
    C(arom)-C(arom)-Cl
         |
       Cl
```

**Step 1: Ring Detection**
- Both carbons identified as aromatic
- Ring systems built

**Step 2: Atropisomer Detection**
```
score = +6 (aromatic)
      + 1 (single bond)
      + 8 (wedge bonds)
      + 4 (double bonds nearby)
      ...
      = 23  ✓ DETECTED

Atoms 0, 1: bAtropisomeric = 1
orig_inp_data->bAtropisomer = 1
```

**Step 3: Canonicalization**
```
Original atom 0 → Canonical atom 5
Original atom 1 → Canonical atom 8

nOrigAtNosInCanonOrd[4] = 0 + 1 = 1  (0-based to 1-based)
nOrigAtNosInCanonOrd[7] = 1 + 1 = 2

Inverted structure (mirror image):
nOrigAtNosInCanonOrdInv[4] = 8  (different!)
nOrigAtNosInCanonOrdInv[7] = 5  (different!)
```

**Step 4: Layer Building**
```
Collect atoms 5, 8 → parity = 1

Sort: 5 < 8 ✓

Compare orderings:
  Normal:   5→1, 8→2
  Inverted: 5→8, 8→5
  Different! → nCompInv2Abs = -1 (/m1)

Result:
  INChI_Stereo {
    nNumberOfStereoCenters = 2
    nNumber = [5, 8]
    t_parity = [1, 1]
    nCompInv2Abs = -1
  }
```

**Step 5: Output**
```
InChI=1S/.../t5m,8m/m1
       └─ /t5m,8m = atoms 5,8 are atropisomeric
       └─ /m1 = enantiomeric (mirror images)
```

---

## Debugging and Diagnostics

### Enable Debug Output

In atropisomers.c, uncomment printf statements:
```c
printf(">>> FOUND atropisomer (higher score): atom id %2d atom id %2d  "
       "is planar %d  --> score %2d (%d)\n",
       atom_id1, atom_id2, is_planar, score, both_atoms_in_same_small_ring);
```

Output shows:
- **atom id**: Input atom numbers (0-based)
- **is_planar**: 0=non-planar (✓ for atropo), 1=planar
- **score**: Calculated heuristic score
- **last number**: Ring constraint indicator

### Check Flags in Debugger

```c
// After detection:
if (orig_inp_data->bAtropisomer) {
    for (int i = 0; i < orig_inp_data->num_inp_atoms; i++) {
        if (orig_inp_data->at[i].bAtropisomeric) {
            printf("Atom %d is atropisomeric\n", i);
        }
    }
}

// After layer building:
for (int i = 0; i < pINChI->Stereo->nNumberOfStereoCenters; i++) {
    printf("Stereo atom %d: canon=%d, parity=%d\n",
        i, pINChI->Stereo->nNumber[i], pINChI->Stereo->t_parity[i]);
}
printf("m-layer value: %d\n", pINChI->Stereo->nCompInv2Abs);
```

---

## Common Issues and Solutions

### Issue: Atropisomers Not Detected

**Possible Causes:**
1. `-Atropisomers` flag not set
2. No 3D coordinates (planarity test requires xyz)
3. Score < 9 (bond doesn't meet heuristics)
4. Atoms in small ring (score penalized by -20)

**Solution:**
- Enable flag
- Ensure 3D coordinates are present
- Check debug output for score value

### Issue: Wrong /m Layer Value

**Possible Causes:**
1. Inverted ordering not computed (aux->nOrigAtNosInCanonOrdInv = NULL)
2. Wrong decision path taken (Path C fallback using parity count)
3. Mixed classical+atropo structure (always gets /m0)

**Solution:**
- Ensure canonicalization runs fully
- Add more test cases to validate rules
- Document expected behavior for each case

### Issue: Atropisomers Lost in Round-Trip

**Root Cause:**
- Atropisomer information is **encoding-level** (in `/t` and `/m` layers)
- Reverse conversion (InChI → structure) doesn't reliably reconstruct 3D geometry
- Round-trip requires **same parity recovery mechanism** on both sides

---

## References

- Pipeline: Multiple files in `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/`
- Detection: `atropisomers.c` (182 lines)
- Rings: `ring_detection.c` (600+ lines)
- Layer Building: `strutil.c:7121-7256` (136 lines)
- Output: `ichiprt1.c:1779-1781` (integration point)
- CLI: `ichiparm.c` (parameter parsing)
- API: `inchi_api.h` (public interface)

---

*Integration: 2026-04-23*
