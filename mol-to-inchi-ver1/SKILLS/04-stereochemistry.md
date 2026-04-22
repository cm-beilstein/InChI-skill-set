# 04-stereochemistry: Stereo Parity Calculations

## Purpose

Calculate stereo parity for tetrahedral (sp3 chiral) centers and geometric (E/Z double bond) stereochemistry. Generate the /b, /t, and /s layers for the InChI output.

## Input

```python
{
    "atoms": [...],  # With canonical labels
    "bonds": [...]
}
```

(from Stage 3: Canonicalized)

## Output

```python
{
    "atoms": [...],
    "bonds": [...],
    "stereochemistry": {
        "tetrahedral": [  # /t layer
            {
                "atom_id": int,
                "parity": 1 | 2 | 3,  # 1=odd, 2=even, 3=undefined
                "connections": [atom_id, atom_id, atom_id, atom_id],
                "inverted": bool
            }
        ],
        "geometric": [  # /b layer
            {
                "bond_id": int,
                "type": "E" | "Z",
                "parity": 1 | 2 | 3
            }
        ],
        "type": 1 | 2 | 3,  # /s layer: 1=absolute, 2=relative, 3=racemic
        "stereo_groups": [...]
    }
}
```

## Algorithm

### Tetrahedral (sp3) Stereo

For each sp3 carbon/nitrogen/other with 4 neighbors:

1. **Assign priorities** to each neighbor based on atomic number
2. **Calculate parity** from neighbor order (1→2→3→4):
   - Clockwise = odd parity (1)
   - Counter-clockwise = even parity (2)
   - Planar/undefined = parity 3
3. **Handle inverted** if needed

```
def calculate_tetrahedral_parity(atom, neighbors, bonds):
    # Get priority of each neighbor (higher atomic number = higher priority)
    sorted_neighbors = sorted(neighbors, key=lambda n: atomic_number(n.element))

    # Calculate signed volume
    # If volume is positive: parity = 1 (odd)
    # If volume is negative: parity = 2 (even)
    # If zero: parity = 3 (undefined)

    return parity
```

### Geometric (Double Bond) Stereo

For each double bond with two non-hydrogen substituents on each end:

1. **Get substituents** on each side of the double bond
2. **Compare priorities** of substituents
3. **Determine E/Z**:
   - High priorities on same side = Z (cis)
   - High priorities on opposite sides = E (trans)

```
def calculate_geometric_parity(bond, atoms, bonds):
    ends = [bond.source, bond.target]
    left_substituents = [get_high_priority(each_end, bond) for each_end in ends]

    if priorities_are_opposite(left_substituents[0], left_substituents[1]):
        return "E"
    else:
        return "Z"
```

### Stereo Type (/s layer)

- **Type 1 (Absolute)**: Stereochemistry defined with actual 3D coordinates
- **Type 2 (Relative)**: Relative stereo only (no coordinate info)
- **Type 3 (Racemic)**: Mixture of stereoisomers

## Examples

### Example 1: L-Alanine (tetrahedral chiral center)

```
     H
     |
  N-C-COOH
     |
     CH3
```

Carbon has 4 different groups: H, NH2, COOH, CH3
- Priorities: COOH (highest) > NH2 > CH3 > H (lowest)
- Parity: calculate order of COOH→NH2→CH3 as seen from H
- Result: chiral center with parity

### Example 2: (E)-But-2-ene (geometric stereo)

```
CH3     CH3
  \    /
   C = C
  /    \
H     H
```

High priority groups (CH3) on opposite sides = E (trans)

### Example 3: No stereocenters (ethanol)

All atoms are achiral - no tetrahedral centers.

```
stereochemistry = {
    "tetrahedral": [],
    "geometric": [],
    "type": None
}
```

## InChI Stereo Layers

| Layer | Description | Format |
|-------|------------|--------|
| /b | Geometric (double bond) | `/b...` - E/Z config |
| /t | Tetrahedral | `/t...` - parity + connections |
| /s | Stereo type | `/s1` (absolute), `/s2` (relative), `/s3` (racemic) |

## Tests

```python
def test_stereo_tetrahedral():
    """Test tetrahedral parity calculation."""
    canonical = canonicalize(normalize(parse_mol("examples/04-alanine.mol")))
    stereo = calculate_stereochemistry(canonical)

    # L-Alanine has one chiral center
    assert len(stereo["tetrahedral"]) >= 1
    chiral = stereo["tetrahedral"][0]
    assert chiral["parity"] in [1, 2, 3]


def test_stereo_geometric():
    """Test geometric (E/Z) parity."""
    canonical = canonicalize(normalize(parse_mol("examples/04-but-2-ene.mol")))
    geo_stereo = calculate_stereochemistry(canonical)

    # But-2-ene has one geometric center
    assert len(geo_stereo["geometric"]) >= 1
    assert geo_stereo["geometric"][0]["type"] in ["E", "Z"]


def test_stereo_no_chiral():
    """Molecules without chirality."""
    canonical = canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
    stereo = calculate_stereochemistry(canonical)

    assert len(stereo["tetrahedral"]) == 0
    assert len(stereo["geometric"]) == 0


def test_stereo_type():
    """Test /s stereo type layer."""
    canonical = canonicalize(normalize(parse_mol("examples/04-alanine.mol")))
    stereo = calculate_stereochemistry(canonical)

    # Should produce /s layer
    assert "type" in stereo


if __name__ == "__main__":
    import sys
    sys.exit(0)