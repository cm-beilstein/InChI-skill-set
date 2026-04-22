# Canonicalization

**Analysis Date:** 2026-04-22

## Overview

The Canonicalization step generates a unique, reproducible ordering of atoms in a chemical structure. This is the critical algorithm that ensures the same chemical structure always produces the same InChI identifier, regardless of how the input molecule was drawn or represented. Without canonicalization, identical structures with atoms listed in different orders would generate different InChI strings, defeating the purpose of a unique identifier.

InChI canonicalization is based on an extension of the Morgan algorithm for graph canonicalization. It works by computing **atom invariants** (characteristics that remain constant under automorphisms) and then using an iterative **equitable partition refinement** process to assign unique ranks to each atom. Atoms with the same rank are constitutionally equivalent (symmetrically equivalent in the molecular graph). The canonical ordering assigns atoms in increasing rank order, breaking ties by comparing neighbor sequences.

The canonicalization step follows normalization and precedes stereochemistry assignment in the pipeline. It operates on the normalized connection table and produces canonical atom numbers that are used throughout subsequent steps to ensure consistent atom referencing.

**Pipeline Position:**
```
Input Parsing → Normalization → CANONICALIZATION → Stereochemistry → Tautomerism → Ring Detection → InChI Assembly → Output
```

## IUPAC Rules and Standards

### Canonicalization Purpose

From the InChI Technical Manual (Section IV.e), canonicalization generates a unique machine ordering of atoms independent of input atom numbering. This is essential for IUPAC identifier standards because:

- **Uniqueness**: The same chemical structure must always produce the same InChI string, regardless of how the molecule was drawn or numbered in the input
- **Reproducibility**: Different practitioners drawing the same molecule must obtain identical InChI identifiers
- **Standardization**: IUPAC requires that chemical identifiers be deterministic and machine-computable

The canonical ordering assigns ranks to atoms based on their chemical environment, ensuring that symmetrically equivalent atoms receive the same rank, while chemically distinct atoms are ordered reproducibly.

### Graph Theory Foundations

Canonicalization is fundamentally a problem in graph theory. The chemical structure is represented as an **undirected labeled graph** where:

- **Vertices** = atoms (with atomic numbers, valence, charge as labels)
- **Edges** = chemical bonds (with bond orders as labels)
- **Automorphisms** = permutations of vertices that preserve the graph structure

The goal is to find a **canonical labeling**—a vertex ordering that is invariant under all automorphisms. This is known as the **graph canonicalization problem**.

Two foundational algorithms established this field:

1. **Morgan's Extended Connectivity Algorithm (1965)**: The first practical algorithm for chemical graph canonicalization, using iterative refinement of atom classes based on neighbor patterns
2. **McKay's nauty algorithm (1981)**: A depth-first search algorithm that is provably correct for finding canonical labelings; used as the basis for InChI canonicalization

### IUPAC Requirements for Uniqueness

IUPAC's requirements for chemical identifiers mandate:

1. **Deterministic Output**: The same input must always produce identical output
2. **No Arbitrary Choices**: The algorithm must produce the same result regardless of implementation details (within the IUPAC specification)
3. **Symmetry Handling**: Equivalent atoms must be treated equivalently—the identifier must not privileged one representation over another
4. **Cross-Platform Consistency**: Identifiers generated on different systems must match

Canonicalization is the mechanism that fulfills these requirements for InChI.

### Key Algorithms

#### Morgan's Extended Connectivity Algorithm

Arthur Morgan's 1965 algorithm introduced the concept of **extended connectivity**—iteratively refined atom classes based on neighbor types:

1. Initial classification by atomic number and valence
2. For each iteration, replace each atom's class with a hash of its neighbors' classes
3. Atoms in the same class remain equivalent; different classes indicate distinct atoms
4. Repeat until the partition stabilizes

This algorithm is the ancestor of InChI's ranking algorithm.

#### McKay's nauty Algorithm

Brendan McKay's **nauty** (No AUTomorphism, Yes) algorithm (1981) provides:

- **Complete canonical labeling**: Unlike Morgan's algorithm which produces a "practical" ordering, nauty guarantees the same canonical labeling regardless of vertex input order
- **Backtracking search**: Systematically explores automorphism space
- **Practical efficiency**: While worst-case exponential, it performs well on chemical graphs

InChI uses an implementation inspired by nauty's approach for tie-breaking and symmetry detection.

#### Graph Invariants

Canonicalization relies on **graph invariants**—properties preserved under automorphisms:

| Invariant | Description |
|-----------|-------------|
| **Atomic Number** | Element identifier (C=6, N=7, O=8, etc.) |
| **Valence** | Number of bonds (excluding implicit hydrogens) |
| **Ring Count** | Number of rings containing the atom |
| **Aromaticity** | Whether atom is part of an aromatic system |
| **Hybridization** | sp³, sp², sp, or other orbital configuration |

These invariants form the initial partition before iterative refinement.

### InChI Technical Reference

The canonicalization algorithm is specified in:

- **InChI Technical Manual, Section IV.e**: "Canonicalization"
- **InChI Standard**: InChI v1.05 (2021), Annex 2 - Canonicalization Algorithm

The technical manual specifies:
- The invariant computation order
- The refinement procedure
- Tie-breaking rules using neighbor sequences
- Symmetry orbit generation

### Source References

1. **Morgan, A.** (1965). "The Generation of a Unique Machine Order for Chemical Structures: A Developmental Review." *Journal of Chemical Documentation*, 5(2), 100-107. doi:10.1021/c160017a005

2. **McKay, B.D.** (1981). "Practical Graph Isomorphism." *Congressus Numerantium*, 32, 45-87.

3. **McKay, B.D. & Piperno, A.** (2014). "Practical Graph Isomorphism, II." *Journal of Symbolic Computation*, 60, 94-112.

4. **InChI Technical Manual**, Version 1.05, IUPAC (2021). Section IV.e Canonicalization. https://www.inchi-trust.org/download/106/INCHI-1-DOC.zip

5. **Depth-First Article on InChI Canonicalization Algorithm**. "InChI Technical FAQ: Canonicalization." Depth-First LLC. https://depth-first.com/articles/inchi-canonicalization

## Input

The Canonicalization step receives:

- **Normalized Structure (`sp_ATOM* at`)**: Connection table with all implicit hydrogens added, charges normalized, and metal atoms processed
- **Number of Atoms (`int num_atoms`)**: Count of non-hydrogen atoms in the structure
- **Total Atoms + Tautomer Groups (`int num_at_tg`)**: Atom count including tautomeric endpoint pseudo-atoms (typically `num_atoms` for non-tautomeric structures)
- **Tautomer Information (`T_GROUP_INFO* t_group_info`)**: If present, contains tautomeric group definitions for extended canonicalization
- **Atom Sizes (`ATOM_SIZES* s`)**: Pre-computed sizes for allocating canonicalization arrays
- **Canonicalization Mode (`INCHI_MODE nMode`)**: Flags controlling which canonicalization features to compute:
  - `CMODE_ISO`: Isotopic canonicalization
  - `CMODE_STEREO`: Stereo canonicalization
  - `CMODE_ISO_STEREO`: Combined isotopic-stereo canonicalization

## Output

The canonicalization produces multiple arrays stored in the `CANON_STAT` structure:

### Primary Outputs

- **Canonical Ordering (`nCanonOrd`)**: `AT_NUMB*` array where `nCanonOrd[rank-1]` gives the original atom number for that canonical position. For N atoms, ranks range from 1 to N. Atoms with lower canonical numbers are "more central" in the molecule.

- **Symmetry Ranks (`nSymmRank`)**: `AT_RANK*` array where `nSymmRank[atom]` is the symmetry rank (orbit number) of each atom. Symmetrically equivalent atoms have identical symmetry ranks. This represents the automorphism orbits of the molecular graph.

### Secondary Outputs

- **Linear Connection Table (`LinearCT`)**: Flattened connection table in canonical order, used for generating the InChI layer string
- **Isotopic Canonical Data**: Canonical ordering accounting for isotopic substitutions (when `CMODE_ISO` is set)
- **Stereo Canonical Data**: Canonical ordering accounting for stereochemistry (when `CMODE_STEREO` is set)
- **Tautomer Canonical Data**: Canonical ordering for tautomeric structures

## Pseudo-code Algorithm

### Core Canonicalization Function

```c
int Canon_INChI(INCHI_CLOCK *ic, int num_atoms, int num_at_tg,
                sp_ATOM *at, CANON_STAT *pCS, CANON_GLOBALS *pCG,
                INCHI_MODE nMode, int bTautFtcn)
{
    // Step 0: Initialization
    InitializeCanonicalizationGlobals(pCG);
    
    // Step I: Find constitutionally equivalent atoms (non-isotopic)
    // Set tautomer=on, stereo=off, isotopic=off
    GetCanonRanking(at, num_atoms, num_at_tg, pCS->pBCN->ftcn[TAUT_NON],
                  pCS->bKeepSymmRank = 0);
    FixCanonEquivalenceInfo(...);  // Fix if needed
    
    // Step II: Final non-isotopic canonical numbering
    // GetCanonRanking with symmetry ranks preserved
    GetCanonRanking(at, num_atoms, num_at_tg, pCS->pBCN->ftcn[TAUT_NON],
                  pCS->bKeepSymmRank = 1);
    FillOutStereoParities(...);  // Create initial stereo descriptors
    SaveNonIsotopicResults(...);
    
    // Step III-VII: Isotopic and Stereo canonicalization (optional)
    if (nMode & CMODE_ISO) {
        GetIsotopicCanonicalization(...);
    }
    if (nMode & CMODE_STEREO) {
        GetStereoCanonicalization(...);
    }
    
    return SUCCESS;
}
```

### Atom Invariant Computation

The algorithm first computes initial atom invariants that are preserved under automorphisms:

```c
void FillOutAtomInvariant(sp_ATOM *at, int num_atoms, int num_at_tg,
                     ATOM_INVARIANT *pAtomInvariant, CANON_STAT *pCS)
{
    for (i = 0; i < num_atoms; i++) {
        // Hill order number (C=1, H=2, then alphabetical)
        pAtomInvariant[i].b.cNotExactlyHillOrderNumber = at[i].el_info->ordinal_of_Hill;
        
        // Number of connections (valence bonds)
        pAtomInvariant[i].b.cNumberOfConnections = at[i].valence;
        
        // Atomic number
        pAtomInvariant[i].b.cAtomicNumber = at[i].el_info->an;
        
        // Number of attached hydrogens
        #if (HYDROGENS_IN_INIT_RANKS == 1)
        pAtomInvariant[i].b.cNumberOfAttachedHydrogens = at[i].num_bonds;
        #endif
        
        // Tautomer group information
        if (at[i].endpoint_of_tautomer_group) {
            pAtomInvariant[i].cNum_tautomer = num_endpoints_in_group;
        }
        
        // Isotopic information
        if (at[i].iso_sort_key) {
            pAtomInvariant[i].iso_sort_key = at[i].iso_sort_key;
        }
    }
}
```

### Iterative Ranking Algorithm

The core ranking uses equitable partition refinement:

```c
int GetCanonRanking(INCHI_CLOCK *ic, int num_atoms, int num_at_tg,
                 sp_ATOM *at, FTCN *ftcn, int bKeepSymmRank)
{
    // Phase 1: Initial partition by atom invariants
    InitialPartition = PartitionAtomsByInvariant(at, num_atoms);
    
    // Phase 2: Iterative refinement
    do {
        // For each equivalence class, examine neighbor patterns
        for each class C in partition {
            for each atom a in class C {
                // Collect neighbor types (atomic numbers, ranks)
                NeighPattern[a] = CollectNeighborInfo(a, at, current_ranks);
            }
            // Partition by neighbor pattern
            NewClasses = PartitionBy(NeighPattern);
            partition = refine(partition, NewClasses);
        }
        iterations++;
    } while (partition changed);
    
    // Phase 3: Assign ranks from partition
    for each class C in final_partition {
        rank = class_index + 1;
        for each atom a in class C {
            rank[a] = rank;
        }
    }
    
    // Phase 4: Generate canonical ordering
    for rank = 1 to num_atoms {
        atoms_with_rank[rank] = find_all_atoms_with_rank(rank);
        canonical_order.append(atoms_with_rank[rank] sorted by neighbor sequence);
    }
    
    return canonical_order;
}
```

### Symmetry Detection

Symmetry (automorphism orbits) is detected by tracking which atoms are interchangeable:

```c
void DetectSymmetry(AT_RANK *nRank, AT_NUMB *nAtomNumber, int num_at_tg,
                 BCN *pBCN, int bChanged)
{
    // Build automorphism equivalence relation
    // Atoms are equivalent if they can be swapped via graph automorphisms
    
    // Sort atoms by rank
    SortAtomsByRank(nRank, nAtomNumber, num_at_tg);
    
    // Symmetry rank = position of first atom with that rank
    // e.g., for [C1=C(C)=C=C1] (benzene):
    //   canonical_order: [1,2,3,4,5,6]
    //   symmetry_rank:  [1,1,1,1,1,1]  (all carbons equivalent)
}
```

### LinearCT Construction

The canonical connection table is built from canonical ordering:

```c
int UpdateFullLinearCT(int num_atoms, int num_at_tg, sp_ATOM *at,
                    AT_RANK *nRank, AT_RANK *nAtomNumber,
                    CANON_STAT *pCS, CANON_GLOBALS *pCG, int bFirstTime)
{
    // Build canonical ordering: nAtomNumber[rank-1] = original_atom_number
    // nRank[original_atom] = canonical_rank
    
    // For each atom in canonical order:
    for (int i = 0; i < num_atoms; i++) {
        int orig_at = nAtomNumber[i];  // original atom number
        int canon_at = i;              // canonical position (0-indexed)
        
        // For each neighbor of original atom:
        for (int k = 0; k < at[orig_at].valence; k++) {
            int neigh_orig = at[orig_at].neighbor[k];
            int neigh_canon = nRank[neigh_orig];  // canonical position
            
            // Add to LinearCT in canonical order
            LinearCTAppend(canon_at, neigh_canon, bond_type);
        }
    }
    
    // Sort/normalize LinearCT for stable output
    SortLinearCT(LinearCT, nRank);
}
```

## Examples

### Benzene Canonicalization

Benzene (C₆H₆) demonstrates equivalent atom symmetry:

**Input**: 6 carbon atoms, unlabeled in the structure  
**Processing**:
1. Initial partition: all carbons have invariant (C, 2 connections, atomic number 6)
2. Iterative refinement using neighbor patterns:
   - All carbons have identical neighbor patterns (C connected to 2 C atoms)
   - Partition does not refine further
3. Final ranks: all atoms have rank 1 (equivalence class 1)

**Output**:
```
canonical_order: [0, 1, 2, 3, 4, 5]  // C1, C2, C3, C4, C5, C6
symmetry_rank:  [1, 1, 1, 1, 1, 1]   // All equivalent (automorphism orbit 1)
```

The canonical numbering is arbitrary for symmetric atoms but always produces the same InChI when applied consistently.

### Symmetry Breaking: Propane

Propane (C₃H₈) demonstrates symmetry breaking:

**Input**: CH₃-CH₂-CH₃  
**Processing**:
1. Initial partition:
   - Terminal carbons: (C, 1 connection to C, 3 H)
   - Central carbon: (C, 2 connections to C)
2. First refinement breaks the tie:
   - Central carbon has 2 carbon neighbors
   - Terminal carbons have 1 carbon neighbor
3. Final ranks:
   - Terminal carbons: become rank 1 (earliest position wins)
   - Central carbon: rank 2

**Output**:
```
canonical_order: [0, 1, 2]         // CH3, CH2, CH3 (in canonical order)
symmetry_rank:  [1, 2, 1]        // Terminals=1, Central=2
nCanonOrd:      [0, 2, 1]         // Atom 0 becomes position 1
                                 // Atom 2 becomes position 2
                                 // Atom 1 becomes position 3
```

The canonical numbering breaks symmetry by choosing the lexicographically smallest neighbor sequence when atoms are equivalent.

### Complex Symmetry: p-Xylene

p-Xylene demonstrates asymmetric aromatic substitution:

```
     C1       C4
    / \     / \
   H   C   C   H
    \ |   | /
     C2---C3
    / \   / \
   H   C   C   H
    \ |   | /
     C5---C6
    / \   / \
   H   H   H   H
```

**Processing**:
- Positions 1,4 (methyl-substituted carbons): different from 2,3,5,6
- Positions 2,3,5,6 (ring carbons with H): equivalent to each other

**Output**:
```
symmetry_rank: [1, 2, 2, 1, 2, 2]  // Methyl carbons = 1
                                  // Other ring carbons = 2
```

The symmetry ranks correctly identify that atoms 1 and 4 are equivalent (both have methyl groups), as are atoms 2, 3, 5, and 6 in the ring.

## Data Structures

### Key Structures (from `ichicano.h`, `ichicant.h`)

```c
// Connection table arrays
typedef AT_RANK* NEIGH_LIST;

// Partition: canonical numbering
typedef struct tagPartition {
    AT_RANK *Rank;       // rank values
    AT_NUMB *AtNumber;   // atom numbers in rank order
} Partition;

// FTCN: FixHOrTautCanonNumbering
typedef struct tagFixHOrTautCanonNumbering {
    int num_at_tg;
    int num_atoms;
    int nCanonFlags;
    NEIGH_LIST *NeighList;  // length = num_at_tg
    
    AT_RANK *LinearCt;         // connection table
    Partition PartitionCt;     // canonical numbering
    AT_RANK *nSymmRankCt;      // symmetry orbits
    
    // Isotopic variants
    Partition PartitionCtIso;
    AT_RANK *nSymmRankCtIso;
} FTCN;

// BCN: BaseCanonNumbering
typedef struct tagBaseCanonNumbering {
    AT_RANK **pRankStack;     // rank stack for backtracking
    int nMaxLenRankStack;
    int num_max;
    int num_at_tg;
    int num_atoms;
    FTCN ftcn[TAUT_NUM];      // [TAUT_NON], [TAUT_YES]
} BCN;

// CANON_STAT: canonicalization statistics and results
typedef struct tagCanonStat {
    // Statistics
    long lNumBreakTies;
    long lNumNeighListIter;
    
    // Connection tables
    AT_NUMB *LinearCT;
    AT_ISOTOPIC *LinearCTIsotopic;
    AT_STEREO_DBLE *LinearCTStereoDble;
    AT_STEREO_CARB *LinearCTStereoCarb;
    
    // Results
    AT_RANK *nCanonOrd;      // atom numbers in canonical order
    AT_RANK *nSymmRank;     // symmetry ranks (orbits)
    
    // ... many more fields
} CANON_STAT;
```

## Files

### Core Canonicalization Files

- `INCHI-1-SRC/INCHI_BASE/src/ichicano.c` (2742 lines): Main canonicalization algorithm
- `INCHI-1-SRC/INCHI_BASE/src/ichicano.h`: Function declarations
- `INCHI-1-SRC/INCHI_BASE/src/ichicant.h`: Data type definitions
- `INCHI-1-SRC/INCHI_BASE/src/ichican2.c` (6910 lines): Extended canonicalization with isotopic support
- `INCHI-1-SRC/INCHI_BASE/src/ichicans.c` (2383 lines): Stereo and isotopic canonicalization

### Supporting Files

- `INCHI-1-SRC/INCHI_BASE/src/ichimake.c`: Integration with pipeline
- `INCHI-1-SRC/INCHI_BASE/src/ichisort.c`: Sorting and comparison functions
- `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c`: Tautomer canonicalization

## Implementation Notes

### Time Complexity

The canonicalization algorithm has complexity O(n² × d) where n is the number of atoms and d is the refinement depth. For most molecules this converges quickly, but can be expensive for highly symmetric structures (fullerenes, symmetric polyhedra) where many iterations may be needed.

### Memory Usage

Memory allocation is handled through the `CANON_STAT` and `BCN` structures. The `AllocateCS()` function pre-allocates arrays based on atom sizes computed during normalization.

### Thread Safety

The canonicalization functions are not inherently thread-safe but can process multiple independent molecules concurrently if each has its own `CANON_STAT` and `BCN` instances.

### Error Handling

- Returns 0 on success
- Returns positive error code on failure
- Timeout support via `INCHI_CLOCK` prevents infinite loops in pathological cases

---

*Canonicalization pipeline step: 2026-04-22*