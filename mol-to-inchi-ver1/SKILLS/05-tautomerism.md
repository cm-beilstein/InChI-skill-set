# 05-tautomerism: Mobile Hydrogen Handling

## Purpose

Identify mobile hydrogen atoms that can move between positions (tautomerization), generate the /m layer for the InChI output. Mobile hydrogens are those on heteroatoms (N, O, S) that can migrate to another position.

## Input

```python
{
    "atoms": [...],
    "bonds": [...],
    "stereochemistry": {...}
}
```

(from Stage 4: Stereochemistry)

## Output

```python
{
    "atoms": [...],
    "bonds": [...],
    "stereochemistry": {...},
    "tautomerism": {
        "mobile_h": [
            {
                "atom_id": int,      # Original position
                "mobile_to": [int],  # Possible target positions
                "paths": [...]
            }
        ],
        "normalization": str  # /m layer string
    }
}
```

## Algorithm

### Identify Mobile Hydrogen Sources

Mobile hydrogens can exist on:
- Nitrogen (amines, amides, heteroaromatics)
- Oxygen (phenols, alcohols, carboxylic acids)
- Sulfur (thiols, thioacids)

### Calculate Mobile Hydrogen Paths

For each potential mobile H source:
1. Find all atoms that can receive H
2. Build H-shift paths
3. Determine if shift is allowed

```
def find_mobile_h(atoms, bonds):
    mobile_h_sources = []

    for atom in atoms:
        if can_lose_h(atom):
            # Find possible target atoms
            targets = find_h_acceptors(atom, bonds)
            if targets:
                mobile_h_sources.append({
                    "atom": atom.id,
                    "targets": targets
                })

    return mobile_h_sources
```

### Normalization String

Generate /m layer string listing mobile H groups:
- List of atom ranges (e.g., `(3,4,7)` means atoms 3-4-7 are equivalent mobile group)

```
# Example /m layer
/m3,4,7        # Mobile H on atoms 3,4,7 are equivalent
```

## Examples

### Example 1: Amide (mobile H)

Acetamide (CH3CONH2):
- NH2 has mobile H - one or both can move to carbonyl O

```
/m1             # Mobile H on atom 1 (N)
```

### Example 2: Phenol

Phenol (C6H5OH):
- OH hydrogen is mobile to ring carbons ortho/para

```
/m1             # Mobile H on hydroxyl
```

### Example 3: No mobile H (ethanol)

Ethanol has one OH, but the H is fixed (not mobile).

```
tautomerism = {
    "mobile_h": [],
    "normalization": ""
}
```

## Tests

```python
def test_mobile_h_amide():
    """Test amide mobile hydrogens."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/05-acetamide.mol"))
    )
    taut = handle_tautomerism(stereo)

    # Acetamide has mobile H on N
    assert len(taut["mobile_h"]) >= 1


def test_mobile_h_phenol():
    """Test phenol mobile hydrogens."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/05-phenol.mol"))
    )
    taut = handle_tautomerism(stereo)

    # Phenol has mobile H on O
    assert len(taut["mobile_h"]) >= 1


def test_no_mobile_h():
    """Test no mobile hydrogens."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/01-ethanol.mol"))
    )
    taut = handle_tautomerism(stereo)

    assert len(taut["mobile_h"]) == 0
    assert taut["normalization"] == ""


def test_normalization_string():
    """Test /m layer string generation."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/05-acetamide.mol"))
    )
    taut = handle_tautomerism(stereo)

    # Should produce /m layer string
    if taut["mobile_h"]:
        assert "/m" in taut["normalization"] or taut["normalization"].startswith("/m")


if __name__ == "__main__":
    import sys
    sys.exit(0)