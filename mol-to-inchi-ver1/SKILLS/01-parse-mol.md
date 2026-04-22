# 01-parse-mol: Parse MOL V2000/V3000 → Internal Structure

## Purpose

Parse MOL file format (either V2000 or V3000) into an internal chemical graph representation containing atoms, bonds, and properties. This is the first stage of the InChI generation pipeline.

## Input

- MOL file (V2000 or V3000 format)

## Output

```python
{
    "format": "V2000" | "V3000",
    "mol_name": str,
    "dimensions": int,
    "atoms": [
        {
            "id": int,
            "element": str,           # "C", "O", "N", etc.
            "x": float,
            "y": float,
            "z": float,
            "charge": int,             # 0, 1, 2, 3, 4 (maps to +3,+2,+1,-1,-2,-3)
            "isotope": int | None,    # Mass number if isotope
            "radical": int | None,   # 1=single, 2=doublet, 3=triplet
            "valence": int | None,   # Override valency
            "stereo": int | None,   # Stereo configuration
            "hydrogens": int | None # Implicit H count
        }
    ],
    "bonds": [
        {
            "source": int,           # Atom ID (1-based)
            "target": int,           # Atom ID (1-based)
            "order": int,            # 1=single, 2=double, 3=triple, 4=aromatic
            "stereo": int | None    # Stereo for double bonds
        }
    ],
    "properties": {
        "atom_aliases": dict,       # Atom ID -> alias string
        "atom_values": dict,        # Atom ID -> value (for query atoms)
        "stereo_groups": dict       # Stereo group info
    }
}
```

## Algorithm

### V2000 Parsing

1. **Read first line**: MOL file name (may be empty)
2. **Read second line**: Blank or user info
3. **Read counts line**:
   - Columns 0-2: Atom count (3 chars)
   - Columns 3-5: Bond count (3 chars)
   - Columns 6-8: Atom list flag
   - Column 9: Chiral flag
   - Columns 12-14: State flag
   - ... additional flags
4. **Parse atoms** (atom_count lines):
   - Columns 0-9: x coordinate (10 chars)
   - Columns 10-19: y coordinate
   - Columns 20-29: z coordinate
   - Columns 30-33: Element symbol
   - Columns 34-37: Mass difference (isotope)
   - Column 38: Charge (0-4)
   - ... stereo and other flags
5. **Parse bonds** (bond_count lines):
   - Columns 0-2: First atom (1-based)
   - Columns 3-5: Second atom
   - Columns 6-8: Bond type (1=single, 2=double, 3=triple, 4=aromatic)
   - Column 9: Stereo config
6. **Parse properties** (M CHG, M RAD, M ISO lines):
   - M CHG: Atom charge modifications
   - M RAD: Atom radical modifications
   - M ISO: Isotope modifications
   - M VAL: Valence modifications

### V3000 Parsing

1. **Read header**: "V3000" or detect from counts line
2. **Read counts**: "M  V30BEGIN ATOMS" block
3. **Parse atom block**: Enhanced atom properties
   - M  V30 ctab; only atoms after ctab
   - Format: M  V30 <atom_id> <element> <x> <y> <z> ...
4. **Parse bond block**: "M  V30BEGIN BONDS" ...
5. **Parse collections**: Sgroups, stereochemistry groups

## Examples

### Example 1: Ethanol (simple V2000)

`examples/01-ethanol.mol`:
```
  -OEChem-04222603522D

  9  8  0     0  0  0  0  0  0999 V2000
      3.7321    0.2500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
      2.8660   -0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
      2.0000    0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
      2.4675   -0.7249    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      3.2646   -0.7249    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      2.3100    0.7869    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      1.4631    0.5600    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      1.6900   -0.2869    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
      4.2690   -0.0600    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  9  1  0  0  0  0
  2  3  1  0  0  0  0
  2  4  1  0  0  0  0
  2  5  1  0  0  0  0
  3  6  1  0  0  0  0
  3  7  1  0  0  0  0
  3  8  1  0  0  0  0
M  END
```

**Expected parsed output:**
```python
{
    "format": "V2000",
    "mol_name": "-OEChem-04222603522D",
    "dimensions": 2,
    "atoms": [
        {"id": 1, "element": "O", "x": 3.7321, "y": 0.25, "z": 0.0, "charge": 0},
        {"id": 2, "element": "C", "x": 2.866, "y": -0.25, "z": 0.0, "charge": 0},
        {"id": 3, "element": "C", "x": 2.0, "y": 0.25, "z": 0.0, "charge": 0},
        {"id": 4, "element": "H", "x": 2.4675, "y": -0.7249, "z": 0.0, "charge": 0},
        {"id": 5, "element": "H", "x": 3.2646, "y": -0.7249, "z": 0.0, "charge": 0},
        {"id": 6, "element": "H", "x": 2.31, "y": 0.7869, "z": 0.0, "charge": 0},
        {"id": 7, "element": "H", "x": 1.4631, "y": 0.56, "z": 0.0, "charge": 0},
        {"id": 8, "element": "H", "x": 1.69, "y": -0.2869, "z": 0.0, "charge": 0},
        {"id": 9, "element": "H", "x": 4.269, "y": -0.06, "z": 0.0, "charge": 0}
    ],
    "bonds": [
        {"source": 1, "target": 2, "order": 1},
        {"source": 1, "target": 9, "order": 1},
        {"source": 2, "target": 3, "order": 1},
        {"source": 2, "target": 4, "order": 1},
        {"source": 2, "target": 5, "order": 1},
        {"source": 3, "target": 6, "order": 1},
        {"source": 3, "target": 7, "order": 1},
        {"source": 3, "target": 8, "order": 1}
    ]
}
```

### Example 2: Caffeine (V2000)

`examples/01-caffeine.mol`:
```
  Caffeine

 24 25  0  0  0  0  0  0  0  0999V2000
 [coordinates and atom data for C8H10N4O2]
```

**Expected:** 24 atoms (8C, 10H, 4N, 2O), 25 bonds

### Example 3: Benzene (V3000)

```mdlx
  benzene
  None
  2D structure

  0  0  0  0  0  0  0  0999 V3000
M  V2000, 6 atoms, 6 bonds
M  V30BEGIN ATOMS
M  V30 1 C -0.7140 1.4280 0.0000
M  V30 2 C 0.7140 1.4280 0.0000
M  V30 3 C 1.4280 0.0000 0.0000
M  V30 4 C 0.7140 -1.4280 0.0000
M  V30 5 C -0.7140 -1.4280 0.0000
M  V30 6 C -1.4280 0.0000 0.0000
M  V30END ATOMS
M  V30BEGIN BONDS
M  V30 1 1 2 2
M  V30 2 2 3 2
M  V30 3 3 4 2
M  V30 4 4 5 2
M  V30 5 5 6 2
M  V30 6 6 1 2
M  V30END BONDS
M  END
```

**Expected:** 6 atoms, 6 aromatic bonds (order=4 in V2000 notation)

## Tests

```python
def test_parse_ethanol():
    """Test parsing ethanol MOL file."""
    parsed = parse_mol("examples/01-ethanol.mol")

    assert len(parsed["atoms"]) == 4
    assert parsed["atoms"][0]["element"] == "C"
    assert parsed["atoms"][1]["element"] == "C"
    assert parsed["atoms"][2]["element"] == "O"
    assert parsed["atoms"][3]["element"] == "H"
    assert len(parsed["bonds"]) == 3

    # Verify bond connectivity
    assert {"source": 1, "target": 2} in parsed["bonds"]

def test_parse_caffeine():
    """Test parsing caffeine molecule."""
    parsed = parse_mol("examples/01-caffeine.mol")

    assert len(parsed["atoms"]) == 24  # C8H10N4O2

    # Count elements
    elements = [a["element"] for a in parsed["atoms"]]
    assert elements.count("C") == 8
    assert elements.count("N") == 4
    assert elements.count("O") == 2
    assert elements.count("H") == 10

def test_parse_v3000():
    """Test parsing V3000 format."""
    parsed = parse_mol("examples/01-benzene-v3000.mol")

    assert parsed["format"] == "V3000"
    assert len(parsed["atoms"]) == 6

def test_parse_charges():
    """Test charge parsing from M CHG lines."""
    parsed = parse_mol("examples/01-sodium-acetate.mol")

    # Sodium acetate has charged atoms
    charges = [a["charge"] for a in parsed["atoms"]]
    assert 1 in charges or -1 in charges

def test_parse_isotopes():
    """Test isotope parsing."""
    parsed = parse_mol("examples/01-deuterium-benzene.mol")

    # Should detect isotope
    isotopes = [a["isotope"] for a in parsed["atoms"]]
    assert 2 in isotopes  # Deuterium
```

## Edge Cases

| Edge Case | Handling |
|----------|---------|
| Empty molecule | Return empty atoms/bonds list |
| Query atoms (R groups) | Store in properties.atom_aliases |
| Pseudo-atoms | Parse symbol, mark as pseudo |
| Multiple fragments | Store as separate atom sets |
| M  END missing | Handle gracefully, use EOF |
| V3000 mixed with V2000 | Use V3000 block data |
| 3D coordinates | Store z, ignore in 2D processing |

## Cross-References

- **Input format docs:** `REFERENCE/INPUT-FORMATS.md`
- **Next stage:** `02-normalize.md` - takes parsed output
- **Related:** SDfile format (`REFERENCE/INPUT-FORMATS.md`)