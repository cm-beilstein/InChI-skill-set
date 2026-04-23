# Atropisomer Detection Algorithm

**Analysis Date:** 2026-04-23

---

## Detection Function: find_atropisomeric_atoms_and_bonds()

**Location:** `atropisomers.c:8`

**Signature:**
```c
int find_atropisomeric_atoms_and_bonds(inp_ATOM* out_at,
                                       int num_atoms,
                                       RingSystems *ring_result,
                                       ORIG_ATOM_DATA *orig_inp_data)
```

**Returns:** 1 if atropisomers found, 0 otherwise

---

## Algorithm Overview

The detection uses a **two-stage process**:
1. **Pairwise bond scoring** with geometric and topological heuristics
2. **Planarity verification** for borderline cases

### Stage 1: Pairwise Bond Examination

```c
for each atom i (0 to num_atoms-1):
    for each neighbor j of atom i (where i < j):
        score = 0
        
        // Score based on heuristics
        score += ...  (see scoring rules below)
        
        // Planarity check
        is_planar = are_4at_in_one_plane(...)
        
        // Decision
        if (score > 10):
            ATROPISOMER = YES
        else if (score > 9 and not is_planar):
            ATROPISOMER = YES
        
        if ATROPISOMER:
            mark_atoms_as_atropisomeric(i, j)
```

---

## Scoring Heuristics

The algorithm evaluates each bond with a **weighted score**:

### Scoring Components

| Component | Score | Rationale |
|-----------|-------|-----------|
| `num_neighbors_j == 3` | +1 | Atom j has at least 3 neighbors |
| `bond_stereo[j] == 0` | +1 | No explicit 2D wedge/hash stereo |
| `has_wedge_bond(i) ∨ has_wedge_bond(j)` | +4 each | Already has 3D stereo markings |
| **negated:** `has_wedge_bond(i) ∧ has_wedge_bond(j)` | -2 each | Don't want mixed 2D/3D |
| `bond_type[j] == 1` (single bond) | +1 | Atropisomers are single bonds |
| `bond_type[j] != 1` | -2 | Multiple bonds can't rotate |
| `atom_i in ring` | +3 | Aromatic preference |
| `atom_j in ring` | +3 | Aromatic preference |
| `nof_wedge_bonds_i > 0` | +4 | Indicates stereochemistry |
| `nof_wedge_bonds_j > 0` | +4 | Indicates stereochemistry |
| **negated:** `nof_wedge_bonds_i == 0` | -3 | Less confidence if no wedges |
| **negated:** `nof_wedge_bonds_j == 0` | -3 | Less confidence if no wedges |
| `has_double_bond(i)` | +2 | Nearby double bonds add steric bulk |
| `has_double_bond(j)` | +2 | Nearby double bonds add steric bulk |
| `not_fused_ring_pivot(i,j)` | +1 | Fused rings not atropisomeric |
| `both_atoms_not_in_same_small_ring` | +1 | Prefer non-ring-constrained |
| **negated:** `both_atoms_in_same_small_ring` | -20 | **Heavy penalty** if in ≤6 ring |

### Scoring Example

**Biaryl (ideal case):**
```
Aryl1-C(aromatic)-C(aromatic)-Aryl2
```

```
score  = 0
       +1 (num_neighbors == 3)
       +1 (no wedge stereo)
       +1 (single bond)
       +3 (aromatic ring)
       +3 (aromatic ring)
       +4 (has wedge bonds)
       +4 (has wedge bonds)
       +2 (nearby double bonds)
       +2 (nearby double bonds)
       +1 (not fused)
       +1 (not in small ring)
       ──
       = 23  ✓ Easily exceeds 10
```

**Ethane (worst case):**
```
CH3-CH3 (no aromatic, no stereo)
```

```
score  = 0
       +1 (neighbors)
       +1 (no wedge)
       +1 (single bond)
       -3 (no wedge bonds)
       -3 (no wedge bonds)
       ──
       = -3  ✗ Fails threshold
```

---

## Decision Thresholds

### Primary Threshold: score > 10
- **Definite atropisomer** (line 152)
- Marks atoms immediately without further checks

### Secondary Threshold: 9 < score ≤ 10
- **Borderline case** (lines 155-162)
- **Only accepted if NOT planar**
- Passes through `are_4at_in_one_plane()` check

### Failure: score ≤ 9 with planar geometry
- **Not an atropisomer**
- Bond may be aromatic or conjugated (planar)

### Planarity Test Details

```c
int is_planar = are_4at_in_one_plane(at_coord, 0.03);
// at_coord[4][3] = xyz coordinates of:
//   [0] = atom i
//   [1] = atom j
//   [2] = one neighbor of i (not j)
//   [3] = one neighbor of j (not i)
//
// min_sine = 0.03
// Returns 1 if all 4 atoms are coplanar within tolerance
```

---

## Helper Functions

### is_fused_ring_pivot()
**Location:** `ring_detection.c:404`

Detects if two atoms are part of a fused ring system:
```c
int is_fused_ring_pivot(const RingSystems *rs,
                        const inp_ATOM * atoms,
                        int atom_id1, int atom_id2)
```

Returns 1 if:
- Both atoms are neighbors
- Both have ≥2 rings
- They share a ring with ≥2 fused rings
- They share ≥2 child rings

### are_atoms_in_same_small_ring()
**Location:** `ring_detection.c:160`

Checks if two atoms are in the same ring ≤ max_ring_size:
```c
int are_atoms_in_same_small_ring(const inp_ATOM* atoms,
                                 int num_atoms,
                                 const RingSystems *rs,
                                 int atom_id1, int atom_id2,
                                 int max_ring_size)
```

For atropisomers, called with `max_ring_size = 6`

### are_4at_in_one_plane()
**Location:** `ichister.c:1190`

Geometric planarity check using **triple scalar product**:
```c
int are_4at_in_one_plane(double at_coord[][3], double min_sine)
```

**Algorithm:**
1. Take 4 atoms at coordinates [0], [1], [2], [3]
2. For each atom k, compute vectors to other 3 atoms
3. Calculate triple scalar product (cross · dot)
4. Return 1 if `min_actual_min_sine <= min_sine` for all k

**Tolerance:** `min_sine = 0.03` (sine of ~1.7°)

---

## Atom Marking

Once an atropisomeric bond is identified:

```c
orig_inp_data->bAtropisomer = 1;        // Global flag: structure has atropisomers
out_at[atom_id1].bAtropisomeric = 1;    // Mark atom 1
out_at[atom_id2].bAtropisomeric = 1;    // Mark atom 2
```

These flags propagate through:
1. Copied back to `orig_inp_data->at[]` in ichimake.c
2. Used in layer building (set_Atropisomer_t_m_layers)
3. Checked during output generation

---

## Debugging Output

The code includes debug output (printf):
```c
printf(">>> FOUND atropisomer (higher score): atom id %2d atom id %2d  "
       "is planar %d  --> score %2d (%d)\n",
       atom_id1, atom_id2, is_planar, score, both_atoms_in_same_small_ring);
```

Output shows:
- Atom IDs (input numbering)
- Planarity result (0=non-planar, 1=planar)
- Score value
- Ring constraint indicator

---

## Limitations

1. **Score threshold is empirical** - No theoretical justification for 10/9
2. **Planarity check uses 3D coords** - 2D drawings may fail
3. **No validation against chemistry rules** - Purely geometric/topological
4. **Single bond only** - Doesn't detect atropisomerism in multiple bonds
5. **Small ring constraint** - May exclude valid atropisomers in larger rings
6. **No organic chemistry knowledge** - Doesn't understand aromaticity, steric bulk, or known examples

---

## Examples: Score Calculation

### Example 1: Biaryl (Biphenyl with Ortho Substituents)

```
        Cl
         |
    H3C-C-C-Cl
         |
        CH3
```

- Both Cs in aromatic ring: +6
- Single bond: +1
- Both have 3 neighbors: +1
- Likely has wedge bonds: +8
- Nearby double bonds (aromatic): +4
- Not in same ring: +1
- Total: ~21 ✓ ATROPISOMER

### Example 2: Ethane

```
H3C-CH3
```

- Single bond: +1
- Both have 1 neighbor (H): -1
- No aromatic: 0
- No wedges: -6
- Total: -6 ✗ NOT ATROPISOMER

### Example 3: Cyclohexane Bond

```
Two C's in cyclohexane ring
```

- Single bond: +1
- In same ring: -20
- Total: ~-19 ✗ NOT ATROPISOMER

---

## References

- Source: `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/atropisomers.c`
- Ring detection: `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/ring_detection.c`
- Planarity: `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/ichister.c:1190`

---

*Detection Algorithm: 2026-04-23*
