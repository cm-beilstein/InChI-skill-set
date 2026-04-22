# Graph Theory and Canonicalization Mathematics in InChI Generation

**Analysis Date:** 2026-04-22

## 1. Overview

Graph theory provides the mathematical foundation for chemical structure identification. The challenge that canonicalization solves is deceptively simple: given a molecule represented in many different ways—different atom ordering in a connection table, different drawing orientations, different SMILES strings—the canonicalization algorithm must always produce the identical unique identifier. This is the **isomorphism problem** for chemical graphs: determining when two molecular representations describe the same structure. For InChI, the canonicalization process assigns a unique numbering to each atom in a molecule such that any representation of the same structure yields identical atom labels, enabling the generation of a unique, reproducible InChI string.

## 2. Molecular Graph Representation

A molecular structure is represented as a **labeled undirected graph** G = (V, E) where:

- **Vertices (V)**: Atoms in the molecule. Hydrogen atoms are typically excluded from the graph vertices in canonicalization and added later as terminal atoms, following the approach established by Morgan. This creates a **hydrogenless constitution**—the core connectivity skeleton.

- **Edges (E)**: Chemical bonds connecting atoms. Each edge carries a bond type attribute:
  - Single bond: 1
  - Double bond: 2
  - Triple bond: 3
  - Aromatic bond: 4

Formally, this is written as a function w: E → {1, 2, 3, 4} assigning bond weights. Heavy atoms (non-hydrogen) form the vertex set, with hydrogen atoms treated as terminal attributes rather than vertices. This representation is similar to hydrogen-suppressed graphs in chemical graph theory, pioneered by Morgan and refined in the InChI Technical Manual.

The vertex labels include:
- **Atomic number** (Z): the element identifier (C=6, N=7, O=8, etc.)
- **Valence**: the number of bonds excluding implicit hydrogens
- **Aromaticity flag**: whether the atom participates in an aromatic system
- **Ring count**: number of rings containing the atom

## 3. Graph Isomorphism

**Definition (Graph Isomorphism)**: Two graphs G₁ = (V₁, E₁) and G₂ = (V₂, E₂) are **isomorphic** if there exists a bijective function f: V₁ → V₂ (a vertex permutation) such that for all edges {u, v} ∈ E₁, the edge {f(u), f(v)} ∈ E₂ and edge weights are preserved: w({u, v}) = w({f(u), f(v)}). The permutation f is called an **isomorphism** between the graphs.

For molecular graphs, isomorphism means the two chemical structures are identical—the same atoms connected in the same way. The **automorphism group** of a graph is the set of all permutations f that map the graph to itself while preserving structure; elements of this group represent **symmetry operations** on the molecule. Symmetrically equivalent atoms lie in the same **automorphism orbit** (or symmetry class).

The isomorphism problem is computationally challenging. While chemical graphs (with bounded valence and typically <1000 atoms) are tractable, general graph isomorphism lies in the **NP** class but is not known to be NP-complete. McKay's nauty algorithm provides practical polynomial-time performance through **partition refinement** and **backtracking search** with automorphism pruning.

## 4. Morgan Algorithm (1965)

The Morgan algorithm, developed by Harry L. Morgan at Chemical Abstracts Service in 1965, introduced **extended connectivity**—an iterative method for distinguishing atoms based on their chemical environments.

### 4.1 Initial Atom Invariants

Each atom is assigned an initial **class** (a numerical identifier) based on:
1. **Atomic number** (primary): higher atomic number → higher class
2. **Valence** (secondary): for atoms with identical atomic number, valence distinguishes connectivity
3. **Aromaticity** (tertiary): aromatic atoms receive different initial classes

Morgan's original formulation used the number of non-hydrogen atoms attached to each atom as the initial value, corresponding to primary through quaternary carbon classification (1, 2, 3, 4 connections).

### 4.2 Iteration Process

The algorithm iteratively refines atom classes:

**Step 1**: Assign initial classes based on atomic number and valence.

**Step 2** (Iteration): For each atom, compute a new class from the multiset of its neighbors' classes from the previous iteration. This is the **extended connectivity** (EC):

```
EC(n+1, atom_i) = Hash(EC(n, neighbors_of_atom_i))
```

The hash function combines the neighbor classes—Morgan originally used a simple sum, while InChI uses lexicographic ordering of neighbor sequences. This process continues until the partition stabilizes (no atom class changes).

**Step 3**: Assign canonical numbers by lexicographically sorting the final class values, breaking ties by neighbor sequence comparison.

### 4.3 Mathematical Formulation

Let n₀ be the initial invariant for atom i (atomic number, valence, aromaticity). For iteration k > 0:

```
EC(i, k) = f(EC(i, k-1), {EC(j, k-1) for all neighbors j of i})
```

where f is a function that combines the atom's own previous class with its neighbors' classes. Morgan's original used:
```
EC_new[i] = Σ EC_old[neighbor_j] × 10^(position of neighbor_j)
```

However, Morgan's algorithm has known limitations:
1. **Oscillatory behavior**: Some graphs can produce cycling class patterns
2. **Incomplete differentiation**: May not distinguish all symmetry classes

These issues were addressed by later researchers and by InChI's use of McKay's algorithm.

## 5. McKay's Nauty Algorithm

Brendan D. McKay's **nauty** (No AUTomorphisms, Yes?) algorithm, developed in 1981, provides a provably correct canonical labeling approach that InChI adapts.

### 5.1 Partition Refinement

The core technique is **individualization and refinement**:

1. **Initial partition**: Atoms are partitioned by their invariants (atomic number, valence, ring count, etc.)
2. **Refinement**: For each cell in the partition, atoms are further split based on the pattern of connections to other cells
3. **Iteration**: Steps 1-2 repeat until a stable equitable partition is reached

The refinement operator is ** equitable**: every atom in a cell has the same number of neighbors in each other cell. Mathematically:

```
for each cell C in partition P:
    for each other cell C' in P:
        count atoms in C connected to C'
    create new subcells based on these counts
```

### 5.2 Search Tree and Pruning

If the equitable partition does not fully resolve (atoms remain in the same cell), nauty performs a **backtracking search**:

1. Select one atom from an unresolved cell
2. Try assigning different target positions
3. Recursively refine further
4. **Prune** using found automorphisms: if we've seen this partial permutation, skip it

This is where automorphism groups are discovered—permutations that map the graph to itself.

### 5.3 Canonical Label Selection

For each leaf of the search tree (a complete labeling), compute a **canonical isomorph**—a deterministic ordering. The lexicographically smallest isomorph across all permutations becomes the canonical labeling.

### 5.4 Why InChI Uses This

Morgan's algorithm, while historically important, does not guarantee uniqueness. Nauty provides:
- **Completeness**: Finds all automorphisms and definitive canonical labeling
- **Correctness**: The same graph always produces the same canonical labeling
- **Efficiency**: Practical performance on chemical graphs despite worst-case exponential complexity

InChI uses a modified nauty algorithm adapted for:
- Layered canonicalization (constitution → mobile-H → charge → isotopes → stereochemistry)
- Mobile hydrogen handling as a first-class phenomenon
- Integration with the InChI layered structure

## 6. InChI Layer-by-Layer Canonicalization

The InChI canonicalization is performed in distinct stages, each adding refinement while preserving previous layers:

### Stage A: Hydrogenless Constitution
The hydrogen atoms are removed; canonical numbering is computed for the carbon/ heteroatom skeleton only. This produces the `/c` (connectivity) layer. The algorithm follows steps:
1. Assign initial colors from Hill order + number of connections
2. Create color lists: (own color, sorted neighbor colors)
3. Reassign colors by lexicographic ordering
4. Repeat until stable
5. Build connection table from final colors

### Stage B: Mobile Hydrogen Addition
Mobile (tautomeric) hydrogens are now added:
1. Use equivalence classes from Stage A
2. Add list of terminal H atoms
3. Minimize: compare connection tables AND hydrogen lists
4. This produces the `/h` (mobile-H) layer

For mobile hydrogens specifically, the algorithm treats each mobile-H group as a **pseudoatom** connected by directed edges to its donor and acceptor atoms. The mobile group has attributes: number of hydrogens, number of negative charges.

### Stage C: Charge and Protonation
For charged structures:
1. Add charge information to the lists to minimize
2. Handle variable protonation states

### Stage D: Isotopic Composition
For isotopic structures, add isotopic weights:
```
iso_weight = nH1 + 32 × (nH2 + 32 × (nH3 + 32 × shift))
```
where nH1 = protium count, nH2 = deuterium count, nH3 = tritium count, shift = mass - rounded atomic mass.

### Stage E: Stereochemistry
Finally, stereochemistry layers are minimized:
1. Compute double bond parity
2. Compute allene parity
3. Compute tetrahedral parity
4. Compare stereochemistry lists across equivalent labelings
5. Choose lexicographically smallest

This staged approach allows InChI to match at different levels: connectivity-only searches ignore higher layers.

## 7. Mathematical Formulas

### Extended Connectivity Recurrence

The core recurrence relation:
```
EC(k+1)[i] = C(EC(k)[i], sorted_multiset{EC(k)[j] for neighbors j of i})
```
where C is a comparison/combination function producing a new class identifier.

### Lexicographic Minimization

For a labeling L, the connection table CT(L) is:
```
CT(L) = [color(atom_1), neighbor_colors(atom_1), color(atom_2), neighbor_colors(atom_2), ...]
```
The canonical labeling L* minimizes CT(L) lexicographically over all labelings consistent with the symmetry equivalence.

### Equitable Partition

A partition P is **equitable** if for every cell C and every other cell C':
```
all atoms in C have the same number of neighbors in C'
```
The refinement operator produces the coarsest equitable refinement coarser than P.

### Graph Invariant Computation

For canonicalization, invariants must satisfy:
1. **Preserved under automorphisms**: if f is an automorphism, invariant(v) = invariant(f(v))
2. **Distinct for different orbits**: if invariant(v) ≠ invariant(w), v and w are in different orbits
3. **Efficiently computable**: polynomial in vertex degree

## 8. Code Location

### Core Files

**`INCHI-1-SRC/INCHI_BASE/src/ichicano.c`** (2742 lines)
- Main canonicalization entry point
- Function `Canon_INChI()`: primary canonicalization driver
- Function `FillOutAtomInvariant()`: computes initial atom properties
- Function `Canon_INChI1()`: hydrogenless constitution (Step A)
- Function `Canon_INChI2()`: non-isotopic canonical numbering with mobile-H (Step B)
- Function `Canon_INChI3()`: full canonicalization including isotopes/stereo

**`INCHI-1-SRC/INCHI_BASE/src/ichican2.c`** (6910 lines)
- Extended canonicalization with isotopic support
- Function `FillOutAtomInvariant2()`: isotopic invariant computation
- Tautomeric structure canonicalization

**`INCHI-1-SRC/INCHI_BASE/src/ichicans.c`** (2383 lines)
- Stereochemistry canonicalization
- Function `MarkKnownEqualStereoBondParities()`: identifies stereochemically equivalent bonds
- Function `MarkKnownEqualStereoCenterParities()`: identifies stereogenic centers
- Function `SetKnownStereoCenterParities()`: computes tetrahedral parity

### Key Functions

- `GetCanonRanking()`: core ranking algorithm with iterative refinement
- `DetectSymmetry()`: automorphism/orbit detection
- `UpdateFullLinearCT()`: connection table construction from canonical ordering
- `FillTautLinearCT()`: tautomeric group handling

## 9. Examples

### Benzene (C₆H₆)

Benzene demonstrates the symmetry problem:

```
Initial colors:    All C atoms = (6, 2)  [atomic number, connections]
Iteration 1 neighbors: All C atoms → {3} neighbors at (6, 2)
Iteration 2 neighbors: Same pattern persists
Final partition: All atoms in one equivalence class
```

Result:
```
Canonical numbering: [1, 2, 3, 4, 5, 6] (arbitrary but consistent)
Symmetry ranks:   [1, 1, 1, 1, 1, 1] (all equivalent)
```

InChI: `InChI=1S/C6H6/c1-2-4-6-3-5-3/h1-6H`

The symmetry rank of 1 for all carbons correctly reflects D₆h automorphism group.

### Ethanol (C₂H₅OH)

The symmetric ethanol molecule:
```
     H
     |
H - C - C - O - H
     |
     H
```

Processing:
```
Initial partition:
- C1 (terminal): (6, 1, 3H)
- C2 (internal): (6, 2, 2H)  
- O: (8, 1, 1H)

First refinement:
- C1: 1 neighbor in class [2]
- C2: 2 neighbors in class [1]
- C1 and C2 are distinguished
```

Final:
```
Canonical: C1=1, C2=2, O=3
Symmetry:  C1 rank 1, C2 rank 2, O rank 3
```

Note that the terminal carbons in n-butane (CH₃-CH₂-CH₂-CH₃) are equivalent:
```
Initial:   [C, C, C, C] → partition by connection count
Refine:   Terminals (1 connection) vs internal (2 connections)
Result:   [1, 2, 2, 1] — symmetry shows ends are equivalent
```

### 2-Chlorobutane

From the Depth-First analysis:

```
Initial colors:
C1: (1,1), C2: (1,2), C3: (1,3), Cl: (2,1), C4: (1,1)

After first iteration:
C1: (2,3), C2: (3,2,3), C3: (4,2,3,5), Cl: (5,4), C4: (2,4)

Final canonical numbering:
C1=1, C2=3, C3=4, Cl=5, C4=2
```

This produces the canonical InChI for 2-chlorobutane regardless of input atom numbering.

## 10. References

### Primary Sources

1. **Morgan, H.L.** (1965). "The Generation of a Unique Machine Description for Chemical Structures." *Journal of Chemical Documentation*, 5(2), 107-113. doi:10.1021/c160017A018

2. **McKay, B.D.** (1981). "Practical Graph Isomorphism." *Congressus Numerantium*, 32, 45-87.

3. **McKay, B.D. & Piperno, A.** (2014). "Practical Graph Isomorphism, II." *Journal of Symbolic Computation*, 60, 94-112. doi:10.1016/j.jsc.2013.09.003

### InChI Technical Documentation

4. **InChI Technical Manual**, Version 1.05, IUPAC (2021). Section IV.e: Canonicalization. Available: https://www.inchi-trust.org/

5. **Heller, S.R.** et al. (2015). "InChI, the IUPAC International Chemical Identifier." *Journal of Cheminformatics*, 7:23. doi:10.1186/s13321-015-0068-4

### Algorithms and Implementations

6. **Weininger, D., Weininger, A., & Weininger, J.L.** (1989). "SMILES. 2. Algorithm for Generation of Unique SMILES Notation." *Journal of Chemical Information and Computer Sciences*, 29(2), 97-101.

7. **Razinger, M.** (1982). "Extended Connectivity in Chemical Graphs." *Theoretica Chimica Acta*, 61, 581-586.

8. **Jochum, C. & Gasteiger, J.** (1977). "Canonical Numbering and Constitutional Symmetry." *Journal of Chemical Information and Computer Sciences*, 17, 113-117.

### External Resources

9. **Depth-First LLC.** "InChI Canonicalization Algorithm." https://depth-first.com/articles/2006/08/12/inchi-canonicalization-algorithm/

10. **Open Babel.** "Canonical Numbering." http://openbabel.org/

---

*Mathematical foundations for InChI canonicalization: 2026-04-22*