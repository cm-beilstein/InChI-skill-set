# Connectivity Layer (`/c`)

**Analysis Date:** 2026-04-22

## Overview

The **Connectivity Layer** (`/c` layer) in an InChI identifier encodes the complete topological structure of a molecule — specifically, which atoms are bonded to which other atoms. While the formula layer (`/f`) only specifies which elements are present and in what quantity, and the isotope layer (`/i`) adds information about isotopic atoms, the connectivity layer provides the actual chemical graph that defines molecular connectivity.

### When It's Used

The connectivity layer is **obligatory** in all non-trivial InChI identifiers. It is required whenever a molecule contains more than one atom. For a singleatom molecule (such as simple ions like `Cl-` or `Na+`), the connectivity layer is omitted since there are no bonds to represent. The layer encodes:

- Which atoms are connected to which
- The order of each bond (single, double, triple)
- Ring closure connections (tracking which atoms complete rings)
- The canonical numbering that makes the identifier unique and reproducible

### Output Format Example (Counter Notation)

The connectivity layer uses **counter notation** to represent the molecular graph. In this format, each atom is listed with its neighbors, and ring closures are marked with matching lowercase letters. Here's a simple example:

```
InChI=1S/C2H6/c1-2/h1-2H3
```

The connectivity portion is `/c` (implied in standard InChI format when not shown). A more explicit example showing counter notation:

```
InChI=1S/C2H6/c1-2/h1-2H3  →  Connectivity layer: /c (atoms 1-2)
```

For a more complex molecule like benzene:

```
InChI=1S/C6H6/c1-2-3-4-5-6-1/h1-2H3-4H3-5H3-6H3
                                        ↑ ring closure notation
```

The counter notation format represents:
- Atom numbers in canonical order
- Neighbors of each atom (bonded atoms)
- Ring closures: `-1` means atom bonds back to atom 1, creating a ring

---

## Code Implementation

### Key Source Files

| File | Purpose |
|------|---------|
| `INCHI-1-SRC/INCHI_BASE/src/ichirvr2.c` | Connection table parsing during InChI reversal (reading) |
| `INCHI-1-SRC/INCHI_BASE/src/ichirvr7.c` | Connection table comparison for InChI equivalence checking |
| `INCHI-1-SRC/INCHI_BASE/src/ichican2.c` | Canonicalization of the connectivity table |
| `INCHI-1-SRC/INCHI_BASE/src/ichimake.c` | Construction of connection string output (`MakeCtStringNew`, `GetDfsOrder4CT`) |
| `INCHI-1-SRC/INCHI_BASE/src/ichisort.c` | Neighbor list creation (`CreateNeighListFromLinearCT`) |
| `INCHI-1-SRC/INCHI_BASE/src/ichiprt2.c` | Connection table string formatting (`MakeCtStringNew`, `MakeCtStringOld`) |
| `INCHI-1-SRC/INCHI_BASE/src/ichiread.c` | Raw connection table parsing and construction |
| `INCHI-1-SRC/INCHI_BASE/src/ring_detection.c` | Ring detection algorithms |

### Data Structures

#### nConnTable (Connection Table Array)

Located in `INCHI-1-SRC/INCHI_BASE/src/ichi.h` (lines 226-227):

```c
int        lenConnTable;
AT_NUMB   *nConnTable;  /* Connection table [nNumberOfAtoms+NumberOfBonds] */
```

The `nConnTable` is a dynamically allocated array of type `AT_NUMB` (typically `short` or `int16`) that stores:
- Atom canonical numbers
- Bond connections (neighbor relationships)
- Ring closure indicators

The format is a **linearized adjacency list** where:
- Each atom is followed by its neighbors
- Ring closures are encoded as special values

#### lenConnTable (Length of Connection Table)

```c
int        lenConnTable;
```

This integer stores the total length of the `nConnTable` array. It is calculated as:

```
lenConnTable = nNumberOfAtoms + nNumberOfBonds
```

#### AT_NUMB Type Definition

The `AT_NUMB` typedef is used throughout the codebase for atom numbers. It is defined in the InChI headers as a signed integer type sufficient to store atom indices (typically `int16_t` or `short`):

```c
typedef short AT_NUMB;  /* or int16_t, depending on platform */
```

### Connection Table Format

The connection table uses a **LinearCT** (Linear Connection Table) format:

```
LinearCT[0] = number_of_atoms (n_vertex)
LinearCT[i] = neighbor_atom_number  OR  new_vertex_marker
```

Interpretation:
1. `LinearCT[0]` contains the number of atoms in the component
2. Following elements alternate between parent atoms and their neighbors
3. When `LinearCT[i] > n_vertex`: This marks start of a new parent atom
4. When `LinearCT[i] < n_vertex`: This is a neighbor (bonded atom)

Example for ethane (C2H6):

```
LinearCT = [2, 1, 1, 2]
  ↑    ↑  ↑  ↑
  2 atoms
        neighbor of atom 2 (atom 1)
              new vertex = 1
                    neighbor of atom 1 (atom 2)
```

---

## Pseudo-code Algorithm

### Step-by-Step Connectivity Building

The connectivity layer is constructed during the InChI generation process as follows:

```
function Build_Connectivity_Layer(molecule):
    
    # Step 1: Parse input molecular structure
    atoms = Parse_Molecule_Input(molfile)
    num_atoms = Count_Atoms(atoms)
    
    # Step 2: Create canonical ordering
    canonical_order = Compute_Canonical_Numbering(atoms)
    
    # Step 3: Build connection table
    nConnTable = Allocate_Array(num_atoms + num_bonds)
    lenConnTable = num_atoms + num_bonds
    
    # Step 4: For each atom in canonical order:
    for each atom a in canonical_order:
        nConnTable[index++] = a.canonical_number
        
        # Step 5: Add neighbors (bonds)
        for each bond (a, neighbor) in molecule:
            nConnTable[index++] = neighbor.canonical_number
    
    # Step 6: Identify ring closures
    for each ring r in molecule:
        mark atoms completing the ring with closure notation
    
    return nConnTable, lenConnTable
```

### Ring Notation Handling

Ring detection in InChI uses the algorithms in `ring_detection.c`:

```c
function Detect_Rings(atoms):
    ring_systems = []
    
    # Find all simple rings using cycle detection
    for each atom pair (a1, a2) that could close a ring:
        if Path_Exists(a1, a2, excluding direct bond):
            ring = Find_Shortest_Path(a1, a2)
            if len(ring) <= MAX_RING_SIZE:  # usually 8
                ring_systems.append(ring)
    
    # Determine ring hierarchy (spiro, fused, etc.)
    ring_hierarchy = Determine_Ring_Hierarchy(ring_systems)
    
    return ring_systems, ring_hierarchy
```

Rings are encoded in the connectivity layer using special notation:
- Closing bonds are marked with the target atom number preceded by a dash
- Multiple rings use letters: `1a`, `1b` for different ring closures at atom 1

### Canonicalization

The canonicalization process ensures the InChI connectivity is **unique and reproducible** regardless of input atom ordering:

```c
function Canonicalize_Connectivity(nConnTable, lenConnTable):
    
    # Step 1: Build neighbor list from connection table
    nl = CreateNeighListFromLinearCT(nConnTable, lenConnTable)
    
    # Step 2: Depth-First Search ordering
    dfs_order = GetDfsOrder4CT(nl, lenConnTable)
    
    # Step 3: Assign canonical numbers
    # Lower canonical number = deeper in DFS tree = more "terminal"
    canonical_numbers = Assign_Ranks(dfs_order)
    
    # Step 4: Reorder connection table by canonical numbers
    reordered_ct = Reorder_By_Canonical(nConnTable, canonical_numbers)
    
    return reordered_ct, canonical_numbers
```

The DFS-based canonicalization (`GetDfsOrder4CT` in `ichimake.c`, lines 2156-2330):
1. Start from the most "terminal" atom (fewest/smallest neighbors)
2. Perform DFS, tracking discovery time and descendants
3. Sort atoms by: (a) number of descendants, (b) canonical number
4. This produces a deterministic ordering

---

## Examples

### Example 1: Methane (CH4)

**Structure:**
```
  H
  |
  C
 / \
H   H
  \
   H
```

**InChI:**
```
InChI=1S/CH4/h1H4
```

**Connectivity Analysis:**
- Atoms: 1 carbon (C), 4 hydrogens (H)
- All H atoms are bonded to C
- No rings
- The connectivity layer (implied) is simply: carbon connected to 4 hydrogens

**Connection Table (internal):**
```
nConnTable: [1, 4, 2, 3, 4, 1, 2, 3, 4, 5]
             │     │  │  │  │  │
             C    H1 H2 H3 H4 (next atom)
                       (repeat pattern for each C-H bond)
```

### Example 2: Ethanol (C2H5OH)

**Structure:**
```
H H
| |
C C - O - H
| |
H H
```

**InChI:**
```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3
```

Breaking this down:
- `/c1-2-3` = connectivity: C1 connected to C2, C2 connected to O
- `/h3H` = 3 hydrogens on C1
- `/1-2H2` = 2 hydrogens on C2
- `/3H2H` = 2 hydrogens on O plus 1 on the oxygen-connected hydrogen

**Connection Table:**
```
Atoms in order: C1, C2, O1, H(attached to O)

Connections:
C1 → C2, H1, H2, H3    (4 connections)
C2 → C1, O1, H4       (3 connections)  
O1 → C2, H(O)          (2 connections)
```

### Example 3: Benzene (C6H6)

**Structure:**
```
    C1
   /  \
C6      C2
 |      |
 |      |
C5      C3
   \  /
    C4
```

**InChI:**
```
InChI=1S/C6H6/c1-2-4-6-5-3-1/h1-6H
```

**Connectivity Layer:** The `/c1-2-3-4-5-6-1` notation shows:
- C1 connected to C2 and C6 (ring closure with `-1`)
- C2 connected to C1 and C3
- ... continuing around the ring
- C6 connected to C5 and C1

**Ring Closure Notation:**
- The `-1` at the end means the last carbon bonds back to carbon 1
- Each carbon has exactly 2 neighbors in the ring
- Plus 1 hydrogen each

### Example 4: Cyclopropane (C3H6)

**Structure:** Triangle of 3 carbons, each with 2 hydrogens

**InChI:**
```
InChI=1S/C3H6/c1-2-3-1/h1-3H2
```

**Connectivity:**
- C1 connected to C2 and C3 (ring closure `-1`)
- C2 connected to C1 and C3
- C3 connected to C1 and C2

---

## Key Functions Reference

| Function | File | Line | Purpose |
|----------|------|------|---------|
| `MakeCtStringNew` | `ichiprt2.c` | 607 | Formats connectivity as output string |
| `MakeCtStringOld` | `ichiprt2.c` | 759 | Legacy connectivity formatting |
| `GetDfsOrder4CT` | `ichimake.c` | 2156 | DFS-based canonical ordering |
| `CreateNeighListFromLinearCT` | `ichisort.c` | 701 | Builds adjacency list from linear CT |
| `is_subset` | `ring_detection.c` | 8 | Ring subset detection |
| `determine_ring_hierarchy` | `ring_detection.c` | 39 | Ring system hierarchy |

---

## Notes

- The connectivity layer is the most complex part of the InChI identifier
- Canonical numbers ensure reproducibility regardless of input format
- Ring detection handles fused rings, spiro compounds, and complex polycycles
- The counter notation is optimized for both readability and compactness

---

*Connectivity layer analysis: 2026-04-22*