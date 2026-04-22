# Step 4: Canonicalization

**Input:** Normalized atom structure
**Output:** Canonical atom ordering (numbers 1-N)

> **CRITICAL:** Implement canonicalization yourself following Morgan's algorithm. Do NOT use library functions to generate canonical numbers.

## Purpose

Canonicalization assigns a unique, reproducible ordering to atoms in a molecule. This ensures that the same molecule drawn in different ways (different atom numbers) produces the same InChI output.

## Core Algorithm: Morgan's Extended Connectivity

Based on Morgan's algorithm with refinements:

### Phase 1: Initial Classification

Initial rank by atomic number and valence:
```
rank[x][0] = (atomic_number, total_valence)
```

Example: ethanol (C2H6O)
- C1: (6, 4) - connected to C2, O1, implicit H
- C2: (6, 4) - connected to C1, 3H
- O1: (8, 2) - connected to C1, H

Initial classes: {(8,2): [O1], (6,4): [C1,C2]}

### Phase 2: Iterative Refinement

For each iteration, compute new class based on neighbors' classes:

```
for iteration in 1..max_iterations:
    for each atom:
        new_class = hash(neighbor_classes_sorted)
    
    if no change in classes:
        break
    
    assign ranks based on new classes
```

### Phase 3: Symmetry Detection

Atoms with identical classes are symmetry-equivalent:
- Same symmetry rank = can be interchanged by graph automorphism

### Phase 4: Canonical Ordering

Assign canonical numbers:
1. Sort atoms by final class (lower = more central)
2. For ties, use neighbor sequence comparison
3. Result: canonical_order[0..N-1]

## Canonical Numbering Example

### Ethanol: CH3-CH2-OH

```
Initial atoms (by index):
  1: C (connected to: 2,3 H,4 H,5 H)  
  2: C (connected to: 1,6 H,7 H,8 H)
  3: O (connected to: 2,9 H)

After canonicalization:
  Canonical position 1: C2 (terminal CH3, connects to C1, 3H)
  Canonical position 2: O1 (connects to C2, H)
  Canonical position 3: C1 (central CH2, connects to C2, O1, 2H)

Result: canonical_order = [3, 1, 2]
         (atom 2 = position 1, atom 1 = positions 2&3, atom 3 = position 4 in final InChI)
```

## The Connection Table

After canonicalization, build linear connection table:

```
LinearCT format:
  [num_atoms, atom1, neighbor1, neighbor2, ..., atom2, neighbor1, ...]

Example: ethanol simplified (without H)
  LinearCT = [2, 1, 2, 2, 1]
  Interpretation: 2 heavy atoms
                  atom1 connected to atom2
                  atom2 connected to atom1
```

## Ring Handling

Ring detection must occur before canonicalization:
- Find all simple cycles
- Identify ring systems (fused, spiro)
- Encode ring closures with `-n` notation

## InChI Connection Layer Format

Connections encoded as:
```
/c1-2-3  = atom 1 connects to 2, atom 2 connects to 3
/c1-2-3-1 = atom 1 connects to 2, 2 to 3, 3 back to 1 (ring)
/c1-2,3-4 = disconnected fragment, atom 1→2, atom 3→4
```

## Canonicalization for Benzene

Benzene has 6 equivalent carbons due to D6h symmetry. Canonical ordering picks one consistently:

```
InChI: /c1-2-3-4-5-6-1/h6H
       ^ring closure back to 1

Every carbon has: 2 ring neighbors + 1 H
All receive same rank, then sorted deterministically
```

## Code Structure

```python
def canonicalize(atoms):
    # Phase 1: Initial classification
    classes = initial_classification(atoms)
    
    # Phase 2: Iterative refinement
    while True:
        new_classes = refine_classes(classes, atoms)
        if new_classes == classes:
            break
        classes = new_classes
    
    # Phase 3: Symmetry ranks
    symmetry_ranks = compute_symmetry(classes)
    
    # Phase 4: Canonical ordering
    order = assign_canonical_numbers(classes, symmetry_ranks)
    
    return order, symmetry_ranks
```

## Test Verification

For test files (specify via `MOL2INCHI_TEST_DIR` or provide inline):
- Match computed canonical order to expected connections
- Verify ring closures for cyclic molecules

## Next Step

Proceed to `05_STEREOCHEMISTRY.md` for stereochemical handling.