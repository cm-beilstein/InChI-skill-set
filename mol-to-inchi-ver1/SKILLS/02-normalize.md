# 02-normalize: Valency Correction and Protonation

## Purpose

Correct valency violations and handle protonation states. The normalization stage ensures each atom has the correct number of bonds based on its element type, adding or removing electrons as needed to satisfy valency rules.

## Input

```python
{
    "atoms": [...],
    "bonds": [...]
}
```

(from Stage 1: Parsed MOL)

## Output

```python
{
    "atoms": [
        {
            "id": int,
            "element": str,
            "x": float,
            "y": float,
            "z": float,
            "charge": int,
            "implicit_h": int,     # Calculated implicit hydrogens
            "valence": int,       # Total valency after normalization
            "corrected": bool      # Was this atom corrected?
        }
    ],
    "bonds": [...],
    "normalization_log": [
        {"atom_id": int, "action": str, "details": str}
    ]
}
```

## Algorithm

### 1. Build Atomic Valence Table

Standard valencies by element:

| Element | Valence | Notes |
|---------|---------|-------|
| H | 1 | |
| C | 4 | |
| N | 3 or 5 | Amine=3, nitro=5 |
| O | 2 | |
| F | 1 | |
| P | 3 or 5 | phosphate=5 |
| S | 2, 4, or 6 | sulfoxide=4, sulfate=6 |
| Cl | 1 | |
| Br | 1 | |
| I | 1 | |

### 2. Calculate Current Valence

For each atom, sum bond orders from all connected bonds:

```
current_valence = sum(bond.order for bond in connected_bonds)
```

### 3. Add Implicit Hydrogens

Calculate implicit hydrogens to fill valency:

```
valence_deficit = standard_valence - current_valence
implicit_h = max(0, valence_deficit)
```

(For N, handle both trivalent and pentavalent cases)

### 4. Handle Charge Corrections

For atoms with unusual charges that affect valency:
- Nitro groups (N with double-bonded O)
- Quaternary ammonium (N with 4 bonds)
- Sulfonium (S with 3 bonds)
- Oxonium (O with 3 bonds)

## Examples

### Example 1: Ethanol (no correction needed)

Input: Ethanol has C-C, C-O, O-H bonds with standard valencies.

**Calculated:**
- C1: 1 (to C2) + 3 (implicit H) = 4 ✓
- C2: 1 (to C1) + 1 (to O) + 2 (implicit H) = 4 ✓
- O: 1 (to C2) + 1 (to H) = 2 ✓

**Result:** No corrections needed, normalization_log is empty.

### Example 2: Carboxylate (charge correction)

Input: Acrylate ion (-COO-)

```
     O
     ||
    C(-1)
    |
   O(-1)
```

**Calculation:**
- Carbon (carbonyl): 1 (to C) + 2 (double bond to O) = 3, needs +1
- Oxygen (single): 1 (to C) + 1 charge = 1 valence electron, but has +1 charge
- Carbon: 3 + 1 (from charge) = 4 OK

**Correction:** May add explicit H or adjust charge to satisfy valency.

### Example 3: Nitro group

Benzene with nitro group (-NO2):

**Calculation:**
- Nitrogen: 3 bonds (to C, O, O) = 3
- Standard valence for N in nitro = 5
- Deficit: 2 → needs implicit or charge adjustment

**Correction:** Add implicit hydrogens (+1) to N or adjust charge to +1.

## Tests

```python
def test_normalize_ethanol_no_change():
    """Ethanol has correct valencies - no changes."""
    parsed = parse_mol("examples/01-ethanol.mol")
    normalized = normalize(parsed)

    # No corrections needed
    assert all(not a.get("corrected", False) for a in normalized["atoms"])
    assert len(normalized["normalization_log"]) == 0


def test_normalize_implicit_h():
    """Verify implicit hydrogens calculated."""
    parsed = parse_mol("examples/01-ethanol.mol")
    normalized = normalize(parsed)

    # Find carbon atoms - should have implicit H
    carbons = [a for a in normalized["atoms"] if a["element"] == "C"]
    assert carbons[0]["implicit_h"] == 3  # CH3
    assert carbons[1]["implicit_h"] == 2  # CH2


def test_normalize_nitro():
    """Test nitro group valency correction."""
    parsed = parse_mol("examples/02-nitrobenzene.mol")
    normalized = normalize(parsed)

    # Nitrogen in nitro group
    nitrogen = next(a for a in normalized["atoms"] if a["element"] == "N")
    assert nitrogen["valence"] == 5  # Should be pentavalent
    assert nitrogen.get("corrected", False)  # Was corrected


def test_normalize_carboxylate():
    """Test carboxylate charge handling."""
    parsed = parse_mol("examples/02-acrylate.mol")
    normalized = normalize(parsed)

    # Should handle multiple charges
    charges = [a.get("charge", 0) for a in normalized["atoms"]]
    assert sum(charges) == -1  # Net -1 charge


def test_normalize_sulfonate():
    """Test sulfonate group."""
    parsed = parse_mol("examples/02-methyl-sulfonate.mol")
    normalized = normalize(parsed)

    # Sulfur should be hexavalent
    sulfur = next(a for a in normalized["atoms"] if a["element"] == "S")
    assert sulfur["valence"] == 6
```

## Edge Cases

| Edge Case | Handling |
|----------|---------|
| Multiple fragments | Process each fragment independently |
| Radicals | Handle unpaired electrons in valency calculation |
| Metals | Use default metal valency (variable) |
| Hypervalent P/S | Allow 5,6 valency for P, S |
| Non-standard valency | Use M VAL line from MOL if present |
| Ambiguous N | Check connectivity to determine 3 vs 5 |

## Cross-References

- **Previous stage:** `01-parse-mol.md`
- **Next stage:** `03-canonicalize.md` - takes normalized output
- **Valency table:** Derived from InChI Technical Manual