# Algorithm Reference

Reference for key algorithms used in InChI generation.

## Morgan Algorithm (Canonicalization)

### Purpose

Generate unique atom labels (canonical numbers) using iterative bond refinement.

### Overview

1. Initialize each atom with an invariant value
2. Iteratively refine labels based on neighbor labels
3. Use tiebreakers to resolve ties
4. Sort and assign canonical numbers

### Initial Invariants

```
initial_label[atom] = (
    atomic_number,      # Z
    charge,           # q
    degree,          # number of bonds
    isotope          # mass - 10 if isotope
)
```

### Refinement Iteration

```python
def refine_labels(atoms, bonds):
    for iteration in range(max_iterations):
        new_labels = {}
        for atom in atoms:
            # Get sorted neighbor labels
            neighbors = get_neighbors(atom, bonds)
            neighbor_labels = sorted([labels[n.id] for n in neighbors])

            # Combine
            combined = list(atom.label) + neighbor_labels
            new_labels[atom.id] = tuple(combined)

        # Add tiebreaker
        for atom in atoms:
            new_labels[atom.id] = (new_labels[atom.id], atom.id)

        if new_labels == labels:
            break
        labels = new_labels

    return labels
```

### Tiebreaker

When two atoms have identical labels:
1. Use original atom position (lowest first)
2. Then atomic number
3. Then isotope
4. Then charge

## Stereo Parity Calculation

### Tetrahedral (sp3)

Calculate chirality using signed tetrahedron volume.

```python
def tetrahedral_parity(central, substituents):
    # substituents must be 4 atoms in 3D space
    # Vector from central to each substituent
    v1, v2, v3, v4 = [s.position - central.position for s in substituents]

    # Cross products
    cp1 = cross(v1, v2)
    cp2 = cross(v3, v4)

    # Dot products
    d1 = dot(cp1, v3)
    d2 = dot(cp2, v1)

    # Calculate parity
    if d1 > 0 and d2 > 0:
        return 1  # Clockwise (odd)
    elif d1 < 0 and d2 < 0:
        return 2  # Counter-clockwise (even)
    else:
        return 3  # Undefined
```

### Geometric (E/Z)

Double bond stereochemistry.

```python
def geometric_parity(double_bond):
    left_high = get_high_priority_substituent(double_bond.left)
    right_high = get_high_priority_substituent(double_bond.right)

    if left_high.position > right_high.position:
        return "E"  # Opposite sides (trans)
    else:
        return "Z"  # Same side (cis)
```

## Cycle Finding (SSSR)

### Find All Cycles

DFS-based cycle detection.

```python
def find_all_cycles(atoms, bonds):
    cycles = []

    def dfs(start, current, path):
        if current == start and len(path) > 2:
            cycles.append(path[:])
            return

        for neighbor in get_neighbors(current):
            if neighbor in path:
                if neighbor == start and len(path) > 2:
                    cycles.append(path[:])
                continue
            if neighbor not in path:
                path.append(neighbor)
                dfs(start, neighbor, path)
                path.pop()

    for atom in atoms:
        dfs(atom, atom, [atom])

    return cycles
```

### Smallest Set of Smallest Rings (SSSR)

Select minimal independent ring set.

```python
def find_sssr(cycles):
    sssr = []
    covered = set()

    # Sort by size, smallest first
    sorted_cycles = sorted(cycles, key=len)

    for cycle in sorted_cycles:
        cycle_bonds = set(get_bonds(cycle))
        if not cycle_bonds.issubset(covered):
            sssr.append(cycle)
            covered.update(cycle_bonds)

    return sssr
```

## Mobile Hydrogen Detection

### Identify Mobile Sources

Atoms that can lose H (N, O, S with H).

```python
def can_lose_h(atom):
    if atom.element in ["N", "O", "S"]:
        if atom.hydrogens > 0:
            return True
    return False
```

### Find Acceptors

Atoms that can accept H.

```python
def can_accept_h(atom):
    # Lone pair available, no H
    if atom.element in ["N", "O", "S"]:
        if atom.hydrogens == 0 and has_lone_pair(atom):
            return True
    return False
```

## InChIKey Hashing

### SHA-256 Based Hash

```python
import hashlib
import base64

def generate_inchikey(inchi):
    # Modified Base64 for URL safety
    def b64_modified(data):
        encoded = base64.b64encode(data).decode()
        return encoded.replace('+', '/').replace('=', '-')

    # Block 1: Formula + Connectivity
    header = "InChI=1S" + formula + connectivity
    block1 = b64_modified(hashlib.sha256(header.encode()).digest())[:9]

    # Block 2: Additional layers
    additional = layers_h + layers_m + layers_b + layers_t + layers_s
    block2 = b64_modified(hashlib.sha256(additional.encode()).digest())[:8]

    # Layer type
    layer_char = determine_layer_type(layers)

    return f"{block1}-{block2}-{layer_char}"
```

## References

- Morgan Algorithm: Original paper by Morgan (1965)
- InChI Technical Manual: IUPAC/InChI manual
- SSSR: Day, McGhee, Rhodes algorithms