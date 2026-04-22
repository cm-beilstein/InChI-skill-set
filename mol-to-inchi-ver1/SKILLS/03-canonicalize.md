# 03-canonicalize: Graph Canonicalization (Morgan Algorithm)

## Purpose

Generate unique (canonical) atom labels using the Morgan algorithm to ensure the same molecule always produces the same atom numbers regardless of input order. This creates a standardized labeling scheme for the molecule.

## Input

```python
{
    "atoms": [...],
    "bonds": [...]
}
```

(from Stage 2: Normalized structure)

## Output

```python
{
    "atoms": [...],  # Same as input, but with canonical_label added
    "bonds": [...],
    "canonical_labels": {
        original_id: canonical_number  # 1, 2, 3, ...
    },
    "invariants": [  # Final equivalence class values
        {"atom_id": int, "class": int}
    ]
}
```

## Algorithm (Morgan)

### Step 1: Initialize Labels

Assign each atom its initial "invariant" value based on:
- Atomic number (element)
- Atomic mass (isotope)
- Charge
- Number of connections (degree)

```
initial_label[atom] = f(element, isotope, charge, degree)
```

### Step 2: Iterative Refinement

Repeat until no changes:

```
FOR iteration = 1 to max_iterations:
    # Build new labels from neighbor labels
    FOR each atom:
        new_label = combine(current_label, [neighbor_labels])
    
    # Handle ties: use tiebreaker (atom index)
    new_label = new_label + tiebreaker
    
    # Check for changes
    IF any atom has changed label:
        current_label = new_label
    ELSE:
        BREAK  # Stable - canonical labels found
```

### Step 3: Assign Canonical Numbers

Atoms with unique labels get sequential numbers (1, 2, 3, ...).
Atoms with identical labels are in the same equivalence class.

### Tiebreaker (Stability)

If two atoms have the same label, use:
1. Atom index (original position in MOL file)
2. Atomic number
3. Isotope
4. Charge

## Simplified Morgan Algorithm

```
def morgan_canonicalize(atoms, bonds):
    # Step 1: Calculate initial invariants
    labels = {}
    for atom in atoms:
        labels[atom.id] = (
            atomic_number(atom.element),
            atom.charge,
            degree(atom, bonds),
            atom.isotope or 0
        )
    
    # Step 2: Refine iteratively
    for iteration in range(10):
        new_labels = {}
        for atom in atoms:
            neighbors = get_neighbors(atom, bonds)
            neighbor_labels = sorted([labels[n.id] for n in neighbors])
            combined = tuple(list(labels[atom.id]) + neighbor_labels)
            new_labels[atom.id] = combined
        
        # Add unique tiebreaker
        for atom in atoms:
            new_labels[atom.id] = (new_labels[atom.id], atom.id)
        
        if new_labels == labels:
            break
        labels = new_labels
    
    # Step 3: Sort and assign canonical numbers
    sorted_atoms = sorted(atoms, key=lambda a: labels[a.id])
    for i, atom in enumerate(sorted_atoms, 1):
        atom.canonical_label = i
    
    return atoms
```

## Examples

### Example 1: Ethanol

```
Atoms: C1 - C2 - O - H
Initial invariants: (6, 0, 1), (6, 0, 2), (8, 0, 1), (1, 0, 1)
```

After refinement:
- C1 gets canonical label 1
- C2 gets canonical label 2 (more connections)
- O gets canonical label 3
- H gets canonical label 4

### Example 2: Propane (same algorithm handles larger molecules)

```
CH3-CH2-CH3

Initial: (6,0,1), (6,0,2), (6,0,2), (6,0,1), (H x8)
After refinement: Terminal carbons same, middle carbons same
```

### Example 3: Benzene

All 6 carbons are equivalent initially. After Morgan:
- Each carbon gets unique canonical number based on tiebreaker

## Tests

```python
def test_canonicalize_ethanol():
    """Test canonical labels for ethanol."""
    normalized = normalize(parse_mol("examples/01-ethanol.mol"))
    canonical = canonicalize(normalized)

    # Check canonical labels assigned
    assert all("canonical_label" in a for a in canonical["atoms"])

    # Same molecule should always produce same labels
    canonical2 = canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
    assert labels_match(canonical, canonical2)


def test_canonicalize_different_molecules():
    """Different molecules should have different canonical labels."""
    ethanol_can = canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
    methanol_can = canonicalize(normalize(parse_mol("examples/03-methanol.mol")))

    # Different label sets
    assert ethanol_can["canonical_labels"] != methanol_can["canonical_labels"]


def test_canonicalize_isomers():
    """Test canonical labels for isomers."""
    butane = canonicalize(normalize(parse_mol("examples/03-butane.mol")))
    isobutane = canonicalize(normalize(parse_mol("examples/03-isobutane.mol")))

    # Different canonical representation
    assert butane["canonical_labels"] != isobutane["canonical_labels"]


def test_canonicalize_preserve_connectivity():
    """Canonicalization preserves connectivity."""
    normalized = normalize(parse_mol("examples/01-ethanol.mol"))
    canonical = canonicalize(normalized)

    # Same bonds, just canonical labels added
    assert len(canonical["bonds"]) == len(normalized["bonds"])
```


## Cross-References

- **Previous stage:** `02-normalize.md`
- **Next stage:** `04-stereochemistry.md` - uses canonical labels
- **Algorithm:** Morgan algorithm, also see nauty (optional)