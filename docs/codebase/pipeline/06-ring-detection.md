# Ring and Cycle Detection

**Analysis Date:** 2026-04-22

## Overview

The Ring and Cycle Detection step identifies all cyclic structures (rings) within a molecular graph and organizes them into ring systems. This is a critical component of the InChI generation pipeline because ring topology fundamentally distinguishes molecular identity—benzene (C₆H₆) is chemically distinct from cyclohexane (C₆H₁₂) despite having the same carbon skeleton count.

The InChI algorithm employs multiple complementary approaches for ring detection:

1. **DFS-based cycle enumeration** (`ring_detection.c`): Finds all simple cycles in the molecular graph using depth-first search
2. **Tarjan's biconnected components** (`ichinorm.c`): Identifies ring systems (fused ring clusters) using the classic algorithm for finding blocks in undirected graphs
3. **BFS-based minimum ring size** (`ichiring.c`): Uses breadth-first search to efficiently determine the smallest ring containing a given bond

Ring detection occurs after hydrogen removal and normalization but before tautomer processing. This ensures that ring bonds are properly accounted for before any hydrogen migration potentially breaks or forms rings.

---

## IUPAC Rules and Standards

### Graph Theory Background

Cycle detection in chemical graphs is fundamentally a graph theory problem. A molecule is represented as an undirected graph where atoms are vertices and chemical bonds are edges. A **ring** (or cycle) is a closed path in the graph that returns to its starting point without repeating vertices (except the start/end). The smallest possible ring in a chemical graph is a 3-membered cycle (cyclopropane), as cycles of length 2 would require multiple bonds between the same two atoms.

InChI employs three distinct algorithmic approaches because each addresses different aspects of ring detection: DFS enumerates all simple cycles, Tarjan's algorithm efficiently partitions atoms into ring systems (biconnected components), and BFS provides fast minimum-ring-size queries for specific bonds.

### InChI Ring Systems

The InChI canonicalization process treats rings as fundamental structural elements. A **ring system** in InChI terminology refers to a set of rings that are interconnected through shared atoms or bonds. The `nRingSystem` field in each `inp_ATOM` structure identifies which ring system an atom belongs to, while `nBlockSystem` distinguishes between separate fused ring blocks within a larger system.

InChI's ring detection is essential for generating unique identifiers—benzene (C₆H₆), cyclohexane (C₆H₁₂), and cyclohexene (C₆H₁₀) all have different InChI strings precisely because their ring topology differs. The canonicalization process must detect all rings and correctly identify fused/spiro relationships to produce a chemically accurate identifier.

### Aromaticity Rules

**Hückel's Rule** (4n+2) defines aromaticity for planar, conjugated monocyclic systems: a ring is aromatic if it contains (4n+2) π electrons where n is a non-negative integer. This gives the well-known sequence of aromatic electron counts: 2, 6, 10, 14... (n = 0, 1, 2, 3...). Conversely, systems with 4n π electrons (4, 8, 12...) are antiaromatic.

InChI detects aromaticity during normalization by examining alternating single/double bond patterns in conjugation with atomic orbital contributions. The algorithm considers both the electron count and the planarity of the ring system. Aromatic rings are marked with special bond types that affect canonicalization, ensuring benzene is distinguished from cyclohexatriene (a hypothetical non-aromatic alternative).

### Ring Detection Algorithms

**DFS-based cycle finding** (`ring_detection.c`): Depth-first search explores all paths from each starting atom, tracking the current path. When the DFS returns to the starting atom with a path length ≥ 3, a cycle is found. This exhaustive approach finds all simple cycles but has O(n!) worst-case complexity—practically mitigated by early termination rules.

**Tarjan's biconnected components** (`ichinorm.c`): Tarjan's 1972 algorithm finds biconnected components (blocks) in O(V+E) time. Each biconnected component represents a ring system—the minimal set of rings where removing any edge would disconnect the graph. The algorithm maintains DFS number and low-point values to identify articulation points separating different blocks. Reference: Tarjan, R. (1972). "Depth-First Search and Linear Graph Algorithms." *SIAM Journal on Computing*, 1(2), 146-160.

**Minimum ring size via BFS** (`ichiring.c`): Breadth-first search from a bond's atom finds the shortest path back to itself, yielding the minimum ring size containing that bond. BFS guarantees finding the shortest path in unweighted graphs, making this approach optimal for minimum-ring queries. Early termination when 2×level exceeds the maximum ring size being tested provides additional efficiency.

### IUPAC Nomenclature Connection

IUPAC nomenclature directly encodes ring information in systematic names. The **Hantzsch-Widman pyridine/naphthalene system** provides the foundation for heterocyclic nomenclature, while **von Baeyer nomenclature** names bridged bicyclic systems (bicyclo[2.2.1]heptane = norbornane). The **Stereochemistry of Ring Systems** (CIP rules for rings) requires knowing ring sizes and fusion patterns to assign stereochemistry correctly.

InChI's ring detection enables these nomenclature principles to work in reverse: given a molecular graph, InChI identifies rings that would be named systematically, supporting accurate chemical information exchange. The ring system identification is critical for canonicalization because fused rings (like naphthalene) have different preferred IUPAC names than isolated rings.

### Source References

- **InChI Technical Manual**: IUPAC/InChI Trust. *InChI Technical Manual*. https://www.inchi-trust.org/technical-manual/ — Section 4: Ring and Stereochemistry
- **Tarjan, R. (1972)**: "Depth-First Search and Linear Graph Algorithms." *SIAM Journal on Computing*, 1(2), 146-160. https://doi.org/10.1137/0201010
- **Graph Theory**: Diestel, R. (2017). *Graph Theory* (5th ed.). Springer. Chapter 3: Cycles.
- **Hückel's Rule**: Hückel, E. (1931). Quantentheoretische Beiträge zum Benzolproblem. *Zeitschrift für Physik*, 70, 204-286.
- **Biconnected Components**: Hopcroft, J., & Tarjan, R. (1973). "Algorithm 447: Efficient Biconnectivity in a Graph." *Communications of the ACM*, 16(6), 351-361.

---

## Input

The ring detection receives a molecular graph represented as an array of `inp_ATOM` structures:

```c
typedef struct {
    AT_NUMB   neighbor[MAXVAL];    // Atom indices of bonded neighbors
    S_CHAR    bond_type[MAXVAL];    // Bond types (single, double, aromatic)
    int       valence;              // Number of bonds
    // ... other fields
} inp_ATOM;
```

**Input Requirements:**
- All explicit hydrogens must be removed prior to this step
- The graph must be fully connected or each component processed separately
- Bond types must be correctly identified (single, double, triple, aromatic)
- Atom indices are zero-based integers

The algorithm receives `inp_ATOM* atoms` and `int num_atoms` as parameters to the main entry point `find_rings()` in `ring_detection.c`.

---

## Output

The ring detection produces a `RingSystems` structure containing all identified rings and their relationships:

```c
typedef struct Ring {
    int id;                    // Unique ring identifier (0-based)
    int *atom_ids;             // Array of atom indices forming the ring
    int size;                  // Number of atoms in the ring (ring size)
    int nof_atomic_rings;      // Number of atomic (non-fused) rings in this system
    int parent_id;             // ID of parent ring if nested (or -1)
    int *child_ids;            // Array of child ring IDs
    int child_count;           // Number of child rings
    int is_fused_ring;         // Boolean: shares atoms with another ring
} Ring;

typedef struct Atom2RingMapping {
    int atom_id;               // The atom index
    int *ring_ids;             // Rings containing this atom
    int ring_count;            // Number of rings containing this atom
} Atom2RingMapping;

typedef struct {
    Ring* rings;               // Array of all detected rings
    int count;                 // Total number of rings
    Atom2RingMapping* atom_to_ring_mapping;  // Fast lookup: atom -> rings
    int num_atoms;             // Number of atoms in the original molecule
} RingSystems;
```

**Output Data:**

1. **All simple cycles**: Each distinct cycle in the graph is identified and stored
2. **Ring hierarchy**: Parent-child relationships for nested rings (if any)
3. **Fused ring detection**: Rings that share atoms are marked as `is_fused_ring = 1`
4. **Ring system numbering**: Each ring is assigned to a ring system via `nRingSystem` field in `inp_ATOM`
5. **Atom-to-ring mapping**: Fast lookup structure for determining which rings contain any given atom
6. **Atomic ring count**: Each ring system tracks how many individual rings it contains

---

## Pseudo-code Algorithm

### Primary Cycle Finding: DFS-Based Enumeration

The main `find_rings()` function in `ring_detection.c` performs DFS from each atom to enumerate all simple cycles:

```
function find_rings(atoms, num_atoms):
    rs = create RingSystems structure
    adj = build adjacency matrix from atoms
    
    visited = array[num_atoms] initialized to 0
    path = array[num_atoms] initialized to -1
    
    for each atom start in 0..num_atoms-1:
        dfs(rs, atoms, adj, num_atoms, start, start, visited, path, 0)
    
    // Post-processing to establish ring relationships
    determine_ring_hierarchy(rs)
    determine_fused_rings(rs)
    
    return rs
```

The recursive DFS function explores all paths:

```
function dfs(rs, atoms, adj, num_atoms, start, curr, visited, path, path_len):
    visited[curr] = 1
    path[path_len] = curr
    path_len = path_len + 1
    
    for each neighbor i in 0..num_atoms-1 where adj[curr][i] == 1:
        if i == start AND path_len > 2:          // Found a cycle back to start
            if is_new_ring(rs, path, path_len):  // Not already found
                create_new_ring(rs, atoms, path, path_len)
        else if visited[i] == 0:                 // Unvisited, continue DFS
            dfs(rs, atoms, adj, num_atoms, start, i, visited, path, path_len)
    
    visited[curr] = 0   // Backtrack: mark as unvisited for other paths
```

**Key Algorithm Details:**

1. **Cycle validation**: Only paths of length ≥ 3 (triangle or larger) are considered rings
2. **Duplicate prevention**: `is_new_ring()` checks if an equivalent ring was already found
3. **Backtracking**: The visited flag is reset after recursion to allow multiple paths through the same atom
4. **Path tracking**: The current path is maintained in the `path` array during DFS

### Ring Hierarchy Determination

After all rings are found, `determine_ring_hierarchy()` establishes parent-child relationships:

```
function determine_ring_hierarchy(rs):
    for each ring i:
        rs.rings[i].parent_id = -1
        
        for each ring j where i != j:
            if is_subset(rings[i], rings[j]):    // All atoms of i are in j
                rings[i].parent_id = rings[j].id
                add rings[i].id to rings[j].child_ids
```

The subset check ensures nested rings are properly identified.

### Fused Ring Detection

`determine_fused_rings()` counts how many atomic rings each ring system contains:

```
function determine_fused_rings(rs):
    for each ring cur_ring:
        ring_counter = array[rs.count] initialized to 0
        sub_ring_counter(rs, cur_ring, ring_counter)
        
        count = number of non-zero entries in ring_counter
        cur_ring.nof_atomic_rings = count
```

A ring is considered "fused" if it shares atoms with another ring in the same system.

### BFS-Based Minimum Ring Size (ichiring.c)

For specific queries about minimum ring size containing a bond, the BFS approach in `ichiring.c` is more efficient:

```
function is_bond_in_Nmax_memb_ring(atom, at_no, neigh_ord, nMaxRingSize):
    // Initialize BFS from the starting atom
    nAtomLevel[at_no] = 1
    cSource[at_no] = -1
    
    // Add all neighbors to queue with level 2
    for each neighbor i of atom[at_no]:
        nAtomLevel[i] = 2
        cSource[i] = 1 + (i == neigh_ord ? 1 : 0)
        add i to queue
    
    // BFS traversal
    while queue is not empty:
        current = dequeue()
        current_level = nAtomLevel[current]
        
        if 2 * current_level > nMaxRingSize + 4:
            return (min_ring_size >= nMaxRingSize) ? 0 : min_ring_size
        
        for each neighbor next of atom[current]:
            if nAtomLevel[next] == 0:                     // Unvisited
                nAtomLevel[next] = current_level + 1
                cSource[next] = cSource[current]
                enqueue(next)
            else if nAtomLevel[next] + 1 >= current_level:
                // Found a back-edge creating a ring
                ring_size = nAtomLevel[next] + current_level - 2
                if ring_size < min_ring_size:
                    min_ring_size = ring_size
```

### Tarjan's Algorithm for Ring Systems (ichinorm.c)

The `MarkRingSystemsInp()` function uses Tarjan's algorithm to find biconnected components (ring systems):

```
function MarkRingSystemsInp(at, num_atoms, start):
    // Initialize DFS stacks and arrays
    nDfsNumber[atom] = 0 for all atoms
    nLow[atom] = 0 for all atoms
    nStackAtom = empty
    nRingStack = empty
    
    // Start DFS from the start atom
    nDfs = 0
    push start onto nStackAtom and nRingStack
    nLow[start] = nDfsNumber[start] = ++nDfs
    
    repeat until stack is empty:
        // ADVANCE: Explore next unvisited neighbor
        if current atom has unvisited neighbors:
            next = next unvisited neighbor
            if next not visited:
                push next onto stacks
                nLow[next] = nDfsNumber[next] = ++nDfs
            else if nDfsNumber[next] < nDfsNumber[current]:
                // Back edge found
                nLow[current] = min(nLow[current], nDfsNumber[next])
        
        // BACKUP: If no more neighbors, pop and check for biconnected component
        else:
            if current == start:
                break  // Done
            parent = stack second-from-top
            if nLow[current] >= nDfsNumber[parent]:
                // Found biconnected component (ring system)
                increment ring_system_count
                pop atoms from nRingStack until current, marking nBlockSystem
            else:
                nLow[parent] = min(nLow[parent], nLow[current])
            pop current from stacks
```

This assigns `nRingSystem` and `nBlockSystem` values to each atom, enabling quick ring system identification.

---

## Examples

### Benzene Ring (C₆H₆)

For benzene, the algorithm identifies:

```
Input: 6 carbon atoms in a hexagonal arrangement
       All C-C bonds are aromatic (alternating single/double conceptually)
       All C-H bonds are explicit H (removed before this step)

Output:
    Ring ID: 0, Size: 6, nof_atomic_rings: 1, parent_id: -1
    Atoms: [0, 1, 2, 3, 4, 5]
    is_fused_ring: 0
    
    RingSystems.count = 1
    All atoms mapped to ring 0
    nRingSystem = 1 for all 6 atoms
    nNumAtInRingSystem = 6 for all atoms
```

The benzene ring is a single atomic ring (not fused), containing 6 atoms.

### Naphthalene (C₁₀H₈)

Naphthalene contains two fused benzene rings:

```
Input: 10 carbon atoms in two fused hexagonal rings

Output:
    Ring ID: 0, Size: 6 (first benzene), nof_atomic_rings: 2, is_fused_ring: 1
    Ring ID: 1, Size: 6 (second benzene), nof_atomic_rings: 2, is_fused_ring: 1
    
    Parent-child relationship:
        Both rings share parent_id = -1 (top-level ring system)
        No explicit parent since they're at the same level in the system
    
    Atom mapping:
        Atoms 0-5: belong to ring 0
        Atoms 5-9: belong to ring 1
        Atom 5 (bridgehead): belongs to both rings
    
    RingSystems.count = 2
    nRingSystem = 1 for all atoms (same ring system)
    nNumAtInRingSystem = 10 for all atoms
    nBlockSystem properly identifies the fused system
```

The algorithm correctly identifies:
- Two distinct 6-membered rings
- Both are fused (share atom 5)
- The fused ring system contains 2 atomic rings

### Anthracene (Linear Fused System)

For anthracene (three linearly fused benzene rings):

```
Output:
    Ring ID: 0, Size: 6 (left ring)
    Ring ID: 1, Size: 6 (middle ring)  
    Ring ID: 2, Size: 6 (right ring)
    
    All three is_fused_ring = 1
    All have nof_atomic_rings = 3
    
    Atom mapping:
        Atoms 0-4: belong to rings 0 and 1
        Atoms 5-9: belong to rings 1 and 2
        Atoms at bridges: in two rings each
```

### Cyclopropane (Smallest Ring)

For cyclopropane (3-membered ring):

```
Output:
    Ring ID: 0, Size: 3, nof_atomic_rings: 1
    Atoms: [0, 1, 2]
    is_fused_ring: 0
```

The algorithm correctly handles the minimum ring size of 3.

### Spiro Compounds

For spiro compounds (two rings sharing exactly one atom):

```
Output for spiro[4.5]decane:
    Ring ID: 0, Size: 5 (5-membered ring)
    Ring ID: 1, Size: 6 (6-membered ring)
    
    Both have parent_id = -1
    is_fused_ring = 0 (they only share the spiro atom)
    
    Atom mapping:
        Spiro atom (bridgehead): belongs to both rings
        Other atoms: belong to only one ring each
```

The spiro atom is in both rings but is not considered a "fused" bond—fused means sharing a bond (2+ atoms), not just sharing an atom.

---

## Integration Points

The ring detection integrates with other pipeline components:

1. **Called from `ichimake.c`** (line 3910): After normalization, ring detection is invoked to support atropisomer analysis
2. **Used by `atropisomers.c`**: The `RingSystems` structure is passed to determine if ring rotation is restricted
3. **Marks atoms**: The algorithm populates `nRingSystem` and `nNumAtInRingSystem` in `inp_ATOM` structures for downstream use
4. **Memory management**: Caller is responsible for calling `free_ring_system()` to release allocated memory

---

## Key Files

| File | Purpose |
|------|---------|
| `INCHI_BASE/src/ring_detection.c` | Main DFS-based cycle finding algorithm |
| `INCHI_BASE/src/ring_detection.h` | Data structures for ring representation |
| `INCHI_BASE/src/ichiring.c` | BFS-based minimum ring size queries |
| `INCHI_BASE/src/ichiring.h` | Queue-based ring size utilities |
| `INCHI_BASE/src/ichinorm.c` | Tarjan's algorithm for ring system blocks |
| `INCHI_BASE/src/ichimake.c` | Pipeline invocation point (line 3906-3910) |
| `INCHI_BASE/src/atropisomers.c` | Consumes ring detection results |

---

*Ring detection analysis: 2026-04-22*
