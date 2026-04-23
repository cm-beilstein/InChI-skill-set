# Atropisomer Layer Building and Encoding

**Analysis Date:** 2026-04-23

---

## Layer Building Function: set_Atropisomer_t_m_layers()

**Location:** `strutil.c:7121`

**Signature:**
```c
int set_Atropisomer_t_m_layers(const ORIG_ATOM_DATA *orig_inp_data,
                               const INChI *inchi,
                               const INChI_Aux *aux)
```

**Returns:** 1 if layers were modified, 0 otherwise

**Called from:** `ichiprt1.c:1624` during stereo layer generation

---

## Processing Pipeline

### Phase 1: Collect Atropisomeric Atoms (lines 7151-7177)

**Input:** `orig_inp_data->bAtropisomer` flag and per-atom `bAtropisomeric` marks

**Process:**
```c
if (orig_inp_data->bAtropisomer) {
    for (int i = 0; i < orig_inp_data->num_inp_atoms; i++) {
        if (orig_inp_data->at[i].bAtropisomeric) {
            // Get canonical atom number from auxiliaries
            AT_NUMB canon_atom_num = get_canonical_atom_number(aux, i + 1);
            
            // Check if already in parity array
            int parity_idx = get_parity_idx_from_canonical_atom_number(
                canon_atom_num,
                inchi->Stereo->nNumber,
                inchi->Stereo->nNumberOfStereoCenters);
            
            if (parity_idx == -1) {
                // NEW: Add to end of parity array
                parity_idx = inchi->Stereo->nNumberOfStereoCenters;
                inchi->Stereo->nNumberOfStereoCenters++;
                
                inchi->Stereo->nNumber[parity_idx] = canon_atom_num;
                inchi->Stereo->t_parity[parity_idx] = 1;  // AB_PARITY_ODD
                
                ret = 1;  // Mark as modified
            }
        }
    }
}
```

**Key Points:**
- Maps **original atom numbers** to **canonical atom numbers** via `get_canonical_atom_number()`
- Parity for all atropisomeric atoms is set to **`1` (AB_PARITY_ODD / minus)**
- This is **arbitrary** - used only to mark atoms as atropisomeric in the `/t` layer

### Phase 2: Sort by Canonical Number (lines 7179-7197)

**Purpose:** Ensure canonical order in output

**Algorithm:** Simple selection sort
```c
for (int i = 0; i < inchi->Stereo->nNumberOfStereoCenters; i++) {
    int min_idx = i;
    for (int j = i + 1; j < inchi->Stereo->nNumberOfStereoCenters; j++) {
        if (inchi->Stereo->nNumber[j] < inchi->Stereo->nNumber[min_idx]) {
            min_idx = j;
        }
    }
    if (min_idx != i) {
        // Swap nNumber[i] ↔ nNumber[min_idx]
        // Swap t_parity[i] ↔ t_parity[min_idx]  (keep in sync!)
    }
}
```

**Result:** Atoms ordered by ascending canonical number for deterministic output

### Phase 3: Determine /m Layer (lines 7199-7251)

This is the **most complex part** - determining whether atropisomers are **enantiomeric** or **diastereomeric**.

#### Decision Path A: Mixed Classical + Atropisomeric (lines 7200-7214)

```c
int has_classical = 0;
for (int i = 0; i < inchi->Stereo->nNumberOfStereoCenters; i++) {
    AT_NUMB canon = inchi->Stereo->nNumber[i];
    int orig_0based = aux->nOrigAtNosInCanonOrd[canon - 1] - 1;
    if (!orig_inp_data->at[orig_0based].bAtropisomeric) {
        has_classical = 1;  // Found a classical stereocenter
        break;
    }
}

if (has_classical) {
    inchi->Stereo->nCompInv2Abs = 1;  // /m0
    return ret;  // EARLY EXIT
}
```

**Logic:** If structure has **both classical stereocenters AND atropisomers**, the inversion of just the atropisomeric axis gives a **diastereomer** (not enantiomer).

**Output:** `/m0` (absolute configuration, diastereomeric)

#### Decision Path B: Compare Inverted Canonical Orderings (lines 7217-7232)

```c
if (aux->nOrigAtNosInCanonOrdInv) {  // If inverted ordering available
    int atrop_orderings_differ = 0;
    for (int i = 0; i < orig_inp_data->num_inp_atoms; i++) {
        if (!orig_inp_data->at[i].bAtropisomeric) {
            continue;  // Skip non-atropisomeric atoms
        }
        int cn = get_canonical_atom_number(aux, i + 1);
        if (aux->nOrigAtNosInCanonOrd[cn - 1] !=
            aux->nOrigAtNosInCanonOrdInv[cn - 1]) {
            atrop_orderings_differ = 1;
            break;
        }
    }
    inchi->Stereo->nCompInv2Abs = atrop_orderings_differ ? -1 : 1;
    return ret;  // EARLY EXIT
}
```

**Logic:**
- Compare the **canonical atom numbering** of atropisomeric atoms in the **normal structure** vs the **inverted structure**
- If they differ: the two forms are **mirror images** (enantiomeric)
- If they're the same: the two forms are **not mirror images** (diastereomeric or same)

**Output:**
- `-1` → `/m1` (enantiomeric, mirror images)
- `+1` → `/m0` (diastereomeric, not mirror images)

#### Decision Path C: Fallback - Parity Count (lines 7235-7250)

```c
int n_atrop_defined = 0;
for (int i = 0; i < inchi->Stereo->nNumberOfStereoCenters; i++) {
    AT_NUMB canon = inchi->Stereo->nNumber[i];
    int orig_0based = aux->nOrigAtNosInCanonOrd[canon - 1] - 1;
    if (!orig_inp_data->at[orig_0based].bAtropisomeric) {
        continue;
    }
    if (inchi->Stereo->t_parity[i] == AB_PARITY_ODD ||
        inchi->Stereo->t_parity[i] == AB_PARITY_EVEN) {
        n_atrop_defined++;
    }
}

// Two atoms per axis, so divide by 2
inchi->Stereo->nCompInv2Abs = ((n_atrop_defined / 2) % 2 == 1) ? -1 : 1;
```

**Logic:** Count defined parities in atropisomeric atoms
- Each atropisomeric bond has **2 atoms**
- If **odd count** of defined parities: **odd number of axes** → net chirality → **enantiomeric** (`-1` / `/m1`)
- If **even count**: **even number of axes** → no net chirality → **diastereomeric** (`+1` / `/m0`)

**Example:**
```
Single atropisomeric axis (2 atoms):
  n_atrop_defined = 2
  (2 / 2) % 2 = 1 % 2 = 1 → -1 (enantiomeric) ✓

Two atropisomeric axes (4 atoms):
  n_atrop_defined = 4
  (4 / 2) % 2 = 2 % 2 = 0 → +1 (diastereomeric) ✓

Three atropisomeric axes (6 atoms):
  n_atrop_defined = 6
  (6 / 2) % 2 = 3 % 2 = 1 → -1 (enantiomeric) ✓
```

---

## Output Data Structure

After layer building, the **INChI_Stereo structure** contains:

```c
typedef struct {
    int           nNumberOfStereoCenters;    // Count of stereo atoms (including atropisomers)
    AT_NUMB      *nNumber;                   // [nNumberOfStereoCenters] canonical atom numbers
    S_CHAR       *t_parity;                  // [nNumberOfStereoCenters] parities
    int           nCompInv2Abs;              // Inversion comparison:
                                             //   -1 = /m1 (enantiomeric)
                                             //   +1 = /m0 (diastereomeric)
    int           bTrivialInv;               // (unused for atropisomers)
    // ... other fields for double bonds ...
} INChI_Stereo;
```

---

## Parity Values

All atropisomeric atoms use **`t_parity = 1`** (AB_PARITY_ODD):

```c
#define AB_PARITY_NONE   0   // No stereochemistry
#define AB_PARITY_ODD    1   // Odd parity (R or Z-like)
#define AB_PARITY_EVEN   2   // Even parity (S or E-like)
#define AB_PARITY_UNKN   3   // Unknown
#define AB_PARITY_UNDF   4   // Undefined
```

**Why arbitrary value 1?**
- Atropisomers are **not stereogenic in the classical sense** (no 4 different groups)
- Parity is used only as a **marker** to identify atropisomeric atoms in the `/t` layer
- The actual stereochemistry (enantiomeric vs diastereomeric) is encoded in the **`/m` layer**

---

## InChI String Output Example

### Input: Biphenyl with Ortho Substituents

```
     Cl
      |
 H3C-C(aromatic)-C(aromatic)-Cl
      |
     CH3
```

### Detection & Layer Building:

1. Detection: Atoms C1, C2 marked as `bAtropisomeric = 1`
2. Canonicalization: C1 → atom 5, C2 → atom 8 (example canonical numbers)
3. Collect: Both atoms added to `t_parity[]` with parity = 1
4. Sort: Already in order (5 < 8)
5. Inversion comparison: Inverted structure has different canonical ordering
6. Result: `nCompInv2Abs = -1` (enantiomeric)

### InChI Output:

```
InChI=1B/C12H8Cl2/c1-7-5-3-6-8(10-7)9-11(2)12(4)4/t8m,9m/m1
       │     │ │                    │        │    │  │   │
       │     │ │                    │        │    │  │   └─ /m1: enantiomeric
       │     │ │                    │        │    │  └────── /t: atoms with parity
       │     │ │                    │        └─── /c: connectivity
       │     │ └────────────────────────────────── /h: hydrogen
       │     └──────────────────────────────────── /C: formula
       └──────────────────────────────────────── InChI=1B: version
```

Breaking down `/t8m,9m/m1`:
- `/t8m,9m` = atoms 8,9 are atropisomeric (marked with "m")
- `/m1` = they are enantiomeric (mirror images)

---

## Data Flow Summary

```
Input Structure
    ↓
Ring Detection
    ↓
find_atropisomeric_atoms_and_bonds()
    ├─ Mark atoms: bAtropisomeric = 1
    └─ Set: bAtropisomer = 1
    ↓
Canonicalization (ichicano.c)
    ├─ Get canonical numbers
    └─ Build inverted ordering
    ↓
set_Atropisomer_t_m_layers()
    ├─ Phase 1: Collect canonical atoms
    ├─ Phase 2: Sort by canonical number
    ├─ Phase 3: Determine /m layer
    │   ├─ Path A: Mixed classical+atropo → /m0
    │   ├─ Path B: Inverted comparison → /m1 or /m0
    │   └─ Path C: Parity count → /m1 or /m0
    └─ Result: INChI_Stereo populated
    ↓
Output (ichiprt1.c)
    └─ Format /t and /m layers into InChI string
```

---

## Key Implementation Details

### Canonical Number Lookup

```c
AT_NUMB canon_atom_num = get_canonical_atom_number(aux, i + 1);
// aux->nOrigAtNosInCanonOrd[] maps canonical → original
// get_canonical_atom_number() performs reverse lookup
```

### Parity Index Lookup

```c
int parity_idx = get_parity_idx_from_canonical_atom_number(
    canon_atom_num,
    inchi->Stereo->nNumber,
    inchi->Stereo->nNumberOfStereoCenters);
// Returns -1 if not found, otherwise index in array
```

### Inverted Ordering Comparison

```c
if (aux->nOrigAtNosInCanonOrdInv) {  // Check availability
    if (aux->nOrigAtNosInCanonOrd[cn - 1] !=
        aux->nOrigAtNosInCanonOrdInv[cn - 1]) {
        // Different canonical numbers → enantiomeric
    }
}
```

---

## TODO Items in Code

From `strutil.c:7142-7149`:
```c
//TODO
// - t layer parities for atropisomers
//    -> t-parity[atom] = 1 (-)
//    -> should parity be set to (+) ???
// - m layer for atropisomers
//    -> enantiomeric atropisomers: m1 (inchi->Stereo->nCompInv2Abs = -1; //m1)
//    -> diastereomeric atropisomers: m0 (inchi->Stereo->nCompInv2Abs = 1; //m0) ???
//        -> rules?
```

**Open Questions:**
1. Should parity be `+1` (even) instead of `-1` (odd)?
2. Are the `/m` layer rules correct for all cases?
3. Are more comprehensive tests/rules needed?

---

## References

- Source: `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/strutil.c:7121-7256`
- Called from: `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/ichiprt1.c:1624`
- Data structures: `ichi.h`, `extr_ct.h`, `ichidrp.h`

---

*Layer Building: 2026-04-23*
