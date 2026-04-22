# 07-assemble: Build InChI String

## Purpose

Assemble all processed data from previous stages into the final InChI string. This combines formula, connectivity, hydrogen, mobile H, charge, proton, isotope, stereo, and ring information into the proper InChI format.

## Input

```python
{
    "atoms": [...],
    "bonds": [...],
    "stereochemistry": {...},
    "tautomerism": {...},
    "rings": {...}
}
```

(from Stage 6: Ring Detection)

## Output

```python
{
    "inchi": str,  # Base InChI string (e.g., "InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)")
    "layers": {
        "formula": str,      # /fC2H6O
        "connectivity": str,  # /c1-2
        "fixed_h": str,      # /h...
        "mobile_h": str,     # /m...
        "charge": str,      # /q...
        "proton": str,      # /p...
        "isotope": str,     # /i...
        "geometric": str,    # /b...
        "tetrahedral": str,   # /t...
        "stereo_type": str,   # /s...
        "reconnection": str  # /r...
    }
}
```

## InChI Layer Order

**Critical:** Layers must be assembled in this exact order:

```
/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r
```

| Layer | Substring | Example |
|-------|----------|---------|
| /f | Formula | `/fC2H6O` |
| /c | Connectivity | `/c1-2` |
| /h | Fixed H | `/h3,4` |
| /m | Mobile H | `/m3,4,7` |
| /q | Charge | `/q+1` or `/q-1` |
| /p | Proton count | `/p+1` |
| /i | Isotope | `/i1+2` |
| /b | Geometric | `/b1,2` |
| /t | Tetrahedral | `/t1,2,3` |
| /s | Stereo type | `/s1` |
| /r | Reconnection | `/r1-2` |

## Algorithm

### Formula Layer (/f)

```
def build_formula(atoms):
    counts = count_elements(atoms)
    formula = sort_by_symbol(counts)  # C first, then H, then alphabetical
    return "/f" + formula_string
```

### Connectivity Layer (/c)

```
def build_connectivity(atoms, bonds, canonical_labels):
    # Use canonical labels for atom ordering
    connections = []
    for bond in ordered_bonds:
        c1 = canonical_labels[bond.source]
        c2 = canonical_labels[bond.target]
        connections.append(f"{c1}-{c2}")
    return "/c" + ",".join(connections)
```

### Fixed H Layer (/h)

Atoms with explicit or fixed hydrogens (non-mobile):

### Mobile H Layer (/m)

Mobile hydrogen groups:

### Additional Layers

- **Charge (/q):** Net charge
- **Proton (/p):** Proton count difference
- **Isotope (/i):** Isotope labels
- **Geometric (/b):** E/Z stereo
- **Tetrahedral (/t):** Chiral centers
- **Stereo type (/s):** 1=absolute, 2=relative, 3=racemic
- **Reconnection (/r):** Ring reconnection

## Examples

### Example 1: Ethanol (InChI=1S/C2H6O/c1-2/h1H2,(H,3,4))

```
Layers:
- /fC2H6O
- /c1-2
- /h(H,3,4)  (fixed H on O)
```

### Example 2: Acetamide

```
/fC2H5NO/c1-2/m3
         └─┬─┘
         mobile H on N
```

### Example 3: L-Alanine

```
/fC3H7NO2/c2/t1/m3-4/s1
                  └┬┘
              absolute stereo
```

## Tests

```python
def test_assemble_ethanol():
    """Test assembling ethanol InChI."""
    result = detect_rings(...)
    assembled = assemble_inchi(result)

    # Check base InChI
    assert "C2H6O" in assembled["inchi"]
    assert "/c1-2" in assembled["layers"]["connectivity"]


def test_layer_order():
    """Verify correct layer order."""
    assembled = assemble_inchi(detect_rings(...))

    inchi = assembled["inchi"]
    f_pos = inchi.find("/f")
    c_pos = inchi.find("/c")
    # Later layers should appear after earlier ones

    assert f_pos < c_pos


def test_assemble_proton():
    """Test /p layer."""
    assembled = assemble_inchi(detect_rings(...))

    # Should have /p if protons differ from formula


def test_assemble_stereo():
    """Test /t and /s layers."""
    assembled = assemble_inchi(detect_rings(...))

    if assembled["layers"]["tetrahedral"]:
        assert "/t" in assembled["inchi"]
        assert "/s" in assembled["inchi"]


if __name__ == "__main__":
    import sys
    sys.exit(0)