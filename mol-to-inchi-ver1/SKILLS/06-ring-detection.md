# 06-ring-detection: Cycle Finding and Ring Set Identification

## Purpose

Detect all rings in the molecule, identify the Smallest Set of Smallest Rings (SSSR), and generate the /r layer for reconnection information.

## Input

```python
{
    "atoms": [...],
    "bonds": [...],
    "stereochemistry": {...},
    "tautomerism": {...}
}
```

(from Stage 5: Tautomerism)

## Output

```python
{
    "atoms": [...],
    "bonds": [...],
    "rings": {
        "all_rings": [...],
        "sssr": [...],  # Smallest Set of Smallest Rings
        "reconnection": {
            "groups": [...],
            "string": str  # /r layer
        }
    }
}
```

## Algorithm

### Cycle Detection

Use depth-first search (DFS) to find all cycles:

```
def find_all_cycles(atoms, bonds):
    cycles = []
    visited = set()

    def dfs(start, current, path):
        if current == start and len(path) > 2:
            cycles.append(path)
            return

        for neighbor in get_neighbors(current):
            if neighbor not in path or (neighbor == start and len(path) > 2):
                dfs(start, neighbor, path + [neighbor])

    for atom in atoms:
        dfs(atom, atom, [atom])

    return cycles
```

### Smallest Set of Smallest Rings (SSSR)

Select minimal independent rings that cover all ring bonds:

```
def find_sssr(cycles):
    sssr = []
    covered = set()

    # Sort by size, select smallest first
    sorted_cycles = sorted(cycles, key=len)

    for cycle in sorted_cycles:
        cycle_bonds = get_cycle_bonds(cycle)
        if not cycle_bonds.issubset(covered):
            sssr.append(cycle)
            covered.update(cycle_bonds)

    return sssr
```

### Reconnection Layer

For metal compounds, track which rings connect to metals:

```
def build_reconnection(sssr, atoms, bonds):
    groups = []

    for ring in sssr:
        if contains_metal(ring):
            # Ring connects to metal
            metal_atoms = [a for a in ring if a.element in METALS]
            groups.append(metal_atoms)

    return groups
```

## Examples

### Example 1: Benzene

Benzene has one 6-membered ring.

```
sssr = [[C1, C2, C3, C4, C5, C6]]  # One ring
```

### Example 2: Naphthalene

Two fused 6-membered rings = 2 rings in SSSR.

```
sssr = [
    [C1,C2,C3,C4,C5,C6],   # Ring 1
    [C1,C4,C7,C8,C9,C10]   # Ring 2 (fused)
]
```

### Example 3: Acetic acid (no rings)

```
rings = {
    "all_rings": [],
    "sssr": []
}
```

## Tests

```python
def test_ring_benzene():
    """Test benzene ring detection."""
    result = detect_rings(
        handle_tautomerism(
            calculate_stereochemistry(
                canonicalize(normalize(parse_mol("examples/06-benzene.mol")))
            ))
        )

    assert len(result["rings"]["sssr"]) == 1
    assert len(result["rings"]["sssr"][0]) == 6


def test_ring_naphthalene():
    """Test naphthalene ring detection."""
    result = detect_rings(...)

    # Two fused rings
    assert len(result["rings"]["sssr"]) == 2


def test_no_rings():
    """Test acyclic molecule."""
    result = detect_rings(...)

    assert len(result["rings"]["sssr"]) == 0


def test_ring_size():
    """Test ring sizes are minimal."""
    result = detect_rings(...)

    for ring in result["rings"]["sssr"]:
        assert len(ring) <= len(other_ring) for other_ring in result["rings"]["all_rings"]
```


## Cross-References

- **Previous stage:** `05-tautomerism.md`
- **Next stage:** `07-assemble.md` - takes ring info
- **Algorithm:** SSSR (Smallest Set of Smallest Rings)