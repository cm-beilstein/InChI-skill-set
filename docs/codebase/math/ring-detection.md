# Mathematical Algorithms for Ring Detection in InChI Generation

**Analysis Date:** 2026-04-22

---

## 1. Overview

Ring detection is a fundamental component of InChI canonicalization because molecular identity is fundamentally determined by cyclic topology. Two molecules with identical atom composition but different ring structures—such as benzene (C₆H₆) versus cyclohexane (C₆H₁₂)—are chemically distinct and require unique InChI identifiers. In graph theory, a ring corresponds to a **cycle**: a closed path that returns to its starting vertex without traversing any edge twice. The InChI algorithm must identify all such cycles in the molecular graph to correctly canonicalize the structure and encode ring information in the resulting identifier.

The canonicalization process relies on ring detection to:
- Identify all simple cycles (rings) in the molecular graph
- Detect fused ring systems (multiple rings sharing atoms)
- Determine ring sizes for stereo chemistry handling
- Apply Hückel's rule for aromaticity detection

---

## 2. Graph Theory Background

### 2.1 Cycle Definition

In graph theory, a **cycle** (or simple cycle) is a non-empty trail in which the only repeated vertices are the first and last vertices. In chemical graph terminology, a ring is a closed path of atoms connected by bonds that returns to the starting atom without passing through any atom more than once (except the start/end). The minimum chemically valid ring size is 3 (cyclopropane), as cycles of length 2 would require multi-bonds between the same atom pair.

Formally, let G = (V, E) be an undirected graph where V is the set of atoms (vertices) and E is the set of bonds (edges). A cycle C is a sequence of vertices v₀, v₁, ..., vₖ where v₀ = vₖ and all intermediate vertices are distinct.

### 2.2 Fundamental Cycles and SSSR

For a connected graph with n vertices and m edges, the **cyclomatic number** (number of independent cycles) is m - n + 1. A **cycle basis** is a set of cycles from which all other cycles can be constructed by symmetric difference. The **Smallest Set of Smallest Rings (SSSR)** is the minimal collection of cycles that generates the complete cycle space—a concept directly relevant to InChI's ring enumeration.

The InChI algorithm enumerates all simple cycles using DFS, then filters them to identify unique rings for canonicalization. This exhaustive approach ensures that complex fused systems (naphthalene, anthracene) are correctly handled.

### 2.3 Biconnected Components

A **biconnected component** (or block) is a maximal subgraph in which any two vertices are connected by at least two vertex-disjoint paths. In terms of edges, removing any single edge does not disconnect the component. Biconnected components correspond to ring systems in chemical graphs—fused rings share edges (bonds), while spiro compounds share only a single vertex (atom).

---

## 3. DFS Cycle Finding Algorithm

### 3.1 Algorithm Description

The InChI algorithm employs depth-first search (DFS) to enumerate all simple cycles in the molecular graph. The implementation in `ring_detection.c` (lines 373-402) performs DFS from each atom as a starting point:

```c
void dfs(RingSystems *rs, inp_ATOM* atoms, int **adj, int num_atoms,
         int start, int curr, int *visited, int *path, int path_len) {
    visited[curr] = 1;
    path[path_len] = curr;
    path_len++;

    for (int i = 0; i < num_atoms; ++i) {
        if (adj[curr][i]) {
            if (i == start && path_len > 2) {
                // Found a cycle back to start (ring detected)
                if (is_new_ring(rs, path, path_len)) {
                    create_new_ring(rs, atoms, path, path_len);
                }
            } else if (!visited[i]) {
                // Continue DFS exploration
                dfs(rs, atoms, adj, num_atoms, start, i, visited, path, path_len);
            }
        }
    }
    visited[curr] = 0;  // Backtrack
}
```

### 3.2 Stack-Based Implementation

The algorithm uses a path array as an implicit stack to track the current traversal path. When DFS returns to the starting vertex with a path length ≥ 3, a cycle is identified. The `is_new_ring()` function (lines 348-371) prevents duplicate detection:

```c
int is_new_ring(RingSystems *rs, int *path, int path_len) {
    for (int i = 0; i < rs->count; ++i) {
        if (rs->rings[i].size != path_len) continue;
        int match = 1;
        for (int j = 0; j < path_len; ++j) {
            int found = 0;
            for (int k = 0; k < path_len; ++k) {
                if (rs->rings[i].atom_ids[k] == path[j]) {
                    found = 1; break;
                }
            }
            if (!found) { match = 0; break; }
        }
        if (match) return 0;
    }
    return 1;
}
```

### 3.3 Complexity Analysis

The DFS algorithm runs in O(V + E) time for each starting vertex, making the overall complexity O(V × (V + E)) in worst-case sparse graphs. However, practical molecules have bounded vertex degree (typically ≤ 4), reducing effective complexity. The algorithm uses O(V) auxiliary space for the visited array and path stack.

---

## 4. Tarjan's Algorithm for Ring Systems

### 4.1 Biconnected Components

While DFS finds all cycles, Tarjan's algorithm (implemented in `ichinorm.c` as `MarkRingSystemsInp()`) efficiently partitions the graph into biconnected components—ring systems where removal of any edge disconnects the subgraph. This is essential for fused ring detection.

The algorithm maintains:
- **DFS number** (`nDfsNumber`): Discovery time of each vertex
- **Low-link value** (`nLow`): Minimum DFS number reachable from this vertex

### 4.2 Low-Link Computation

The low-link value is computed as:
```
low[u] = min(disc[u], min{disc[w] | (u, w) is a back edge}, min{low[v] | v is a child of u})
```
This determines whether a vertex is an articulation point separating different biconnected components.

### 4.3 Articulation Point Detection

A vertex v is an articulation point if:
```
low[child] >= disc[v]
```
for any child in the DFS tree. Such vertices separate ring systems in fused compounds (e.g., the bridgehead carbons in naphthalene).

Reference: Tarjan, R. (1972). "Depth-First Search and Linear Graph Algorithms." *SIAM Journal on Computing*, 1(2), 146-160.

---

## 5. Ring Systems in Chemical Graphs

### 5.1 Aromaticity Detection

InChI applies **Hückel's Rule** (4n+2) to detect aromaticity in monocyclic planar systems: a ring is aromatic if it contains (4n + 2) π electrons where n is a non-negative integer. This gives the sequence 2, 6, 10, 14... for aromatic systems. Systems with 4n π electrons (4, 8, 12...) are antiaromatic.

The algorithm examines:
- Alternating single/double bond patterns (conjugation)
- Atomic orbital contributions (p-orbital count)
- Planarity of the ring system

### 5.2 Ring Perception Algorithm

Ring perception in InChI uses the following steps:
1. Build adjacency matrix from atom neighbor list
2. Run DFS to enumerate all simple cycles
3. Filter for unique rings
4. Apply Tarjan's algorithm for ring system partitioning
5. Detect fused rings (sharing 2+ atoms) and spiro rings (sharing exactly 1 atom)

---

## 6. InChI Ring Handling

### 6.1 Ring Systems in InChI Structure

The `RingSystems` structure (defined in `ring_detection.h`, lines 24-29) stores all detected rings:

```c
typedef struct {
    Ring* rings;
    int count;
    Atom2RingMapping* atom_to_ring_mapping;
    int num_atoms;
} RingSystems;

typedef struct Ring {
    int id;
    int *atom_ids;
    int size;
    int nof_atomic_rings;
    int parent_id;
    int *child_ids;
    int child_count;
    int is_fused_ring;
} Ring;
```

Each `inp_ATOM` structure contains `nRingSystem` and `nBlockSystem` fields populated by Tarjan's algorithm to identify ring membership.

### 6.2 Stereo Handling for Ring Bonds

Ring detection is critical for stereo chemistry because:
- Bonds in small rings (3-4 members) have restricted rotation
- Stereochemistry follows CIP rules for ring systems
- Atropisomerism detection requires ring size information

The BFS-based minimum ring size algorithm in `ichiring.c` efficiently answers queries: "What is the smallest ring containing this bond?"

---

## 7. Mathematical Formulas

### 7.1 DFS Complexity
- **Time Complexity:** O(V + E)
- **Space Complexity:** O(V) for recursion stack and visited array

### 7.2 Low-Link Formula
```
low[u] = min(disc[u], disc[w] for back edges (u,w), low[v] for tree edges (u,v))
```
Where `disc[v]` is the DFS discovery time of vertex v.

### 7.3 Biconnected Component Condition
A vertex v is an articulation point separating biconnected components if:
```
low[child] >= disc[v]
```
for any DFS tree child.

### 7.4 Cyclomatic Number
```
M = E - V + 1
```
Where M is the number of independent cycles in a connected graph.

---

## 8. Code Location

| Component | File | Function/Line |
|-----------|------|---------------|
| DFS Cycle Finding | `INCHI_BASE/src/ring_detection.c` | `find_rings()` (line 476), `dfs()` (line 373) |
| Ring Structures | `INCHI_BASE/src/ring_detection.h` | `Ring`, `RingSystems` (lines 7-29) |
| Minimum Ring Size BFS | `INCHI_BASE/src/ichiring.c` | `is_bond_in_Nmax_memb_ring()` (line 362), `GetMinRingSize()` (line 262) |
| Queue Utilities | `INCHI_BASE/src/ichiring.c` | `QueueCreate()`, `QueueAdd()`, `QueueGet()` (lines 67-118) |
| Tarjan's Algorithm | `INCHI_BASE/src/ichinorm.c` | `MarkRingSystemsInp()` |
| Ring Hierarchy | `INCHI_BASE/src/ring_detection.c` | `determine_ring_hierarchy()` (line 39), `determine_fused_rings()` (line 269) |

---

## 9. Examples

### 9.1 Benzene (C₆H₆)

```
Input: 6 carbon atoms, all C-C bonds aromatic
Output:
  Ring ID: 0, Size: 6
  Atoms: [0, 1, 2, 3, 4, 5]
  is_fused_ring: 0
  nRingSystem = 1 for all atoms
```
The smallest set of smallest rings (SSSR) contains one 6-membered ring.

### 9.2 Naphthalene (C₁₀H₈)

```
Output:
  Ring ID: 0, Size: 6 (first benzene)
  Ring ID: 1, Size: 6 (second benzene)
  Both is_fused_ring: 1
  nof_atomic_rings: 2
  Atoms 0-4: Ring 0; Atoms 5-9: Ring 1
  Atom 5 is bridgehead (in both rings)
```
Two 6-membered rings fused at atoms 4 and 5.

### 9.3 Cyclopropane (C₃H₆)

```
Output:
  Ring ID: 0, Size: 3
  Atoms: [0, 1, 2]
  is_fused_ring: 0
```
The smallest chemically valid ring.

---

## 10. References

1. **Tarjan, R. (1972).** "Depth-First Search and Linear Graph Algorithms." *SIAM Journal on Computing*, 1(2), 146-160. https://doi.org/10.1137/0201010

2. **Hopcroft, J., & Tarjan, R. (1973).** "Algorithm 447: Efficient Biconnectivity in a Graph." *Communications of the ACM*, 16(6), 351-361.

3. **InChI Technical Manual.** IUPAC/InChI Trust. https://www.inchi-trust.org/technical-manual/

4. **Hückel, E. (1931).** "Quantentheoretische Beiträge zum Benzolproblem." *Zeitschrift für Physik*, 70, 204-286.

5. **Diestel, R. (2017).** *Graph Theory* (5th ed.). Springer. Chapter 3: Cycles.

---

*Mathematical ring detection analysis: 2026-04-22*