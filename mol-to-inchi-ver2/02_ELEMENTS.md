# Step 2: Element Processing

**Input:** Parsed atoms with element symbols
**Output:** Atoms with atomic numbers, implicit hydrogens, bond connectivity

> **CRITICAL:** Implement element lookup yourself. Do NOT use library functions to get atomic numbers or valences. Use the tables in this document.

## Periodic Table Lookup

### Standard Valences (IUPAC)

| Element | Atomic # | Default Valence |
|---------|----------|-----------------|
| H       | 1        | 1               |
| C       | 6        | 4               |
| N       | 7        | 3 or 5          |
| O       | 8        | 2               |
| F       | 9        | 1               |
| Si      | 14       | 4               |
| P       | 15       | 3 or 5          |
| S       | 16       | 2, 4, or 6      |
| Cl      | 17       | 1               |
| Br      | 35       | 1               |
| I       | 53       | 1               |

### Atomic Number Mapping

```
ELEMENT_TO_NUMBER = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
    'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
    'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22,
    'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
    'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36,
    'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
    'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57,
    'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64,
    'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71,
    'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78,
    'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
    'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92
}
```

## Implicit Hydrogen Calculation

For each atom:
1. Sum the bond orders (single=1, double=2, triple=3, aromatic=1.5)
2. Compare to standard valence
3. `num_H = standard_valence - bond_order_sum`

```
function calculate_implicit_hydrogens(atoms, bonds):
    # Initialize bond counts for each atom
    for atom in atoms:
        atom.bond_valence_sum = 0
        atom.neighbors = []
        atom.bond_types = []
    
    # Sum bond orders
    for bond in bonds:
        a1_idx = bond.a1 - 1  # Convert to 0-indexed
        a2_idx = bond.a2 - 1
        
        bond_order = bond.type
        if bond.type == 4:  # Aromatic
            bond_order = 1.5
        
        atoms[a1_idx].bond_valence_sum += bond_order
        atoms[a1_idx].neighbors.append(a2_idx)
        atoms[a1_idx].bond_types.append(bond_order)
        
        atoms[a2_idx].bond_valence_sum += bond_order
        atoms[a2_idx].neighbors.append(a1_idx)
        atoms[a2_idx].bond_types.append(bond_order)
    
    # Calculate implicit H
    for atom in atoms:
        std_valence = get_standard_valence(atom.symbol)
        atom.implicit_H = max(0, std_valence - atom.bond_valence_sum)
    
    return atoms
```

## Charge Codes (MOL Format)

| Code | Charge |
|------|--------|
| 0    | none   |
| 1    | +3    |
| 2    | +2    |
| 3    | +1    |
| 4    | -1    |
| 5    | -2    |
| 6    | -3    |
| 7    | doublet radical |

## Isotope Handling

- Mass difference field: -5 to +5 (difference from nominal mass)
- D (deuterium) → H with mass diff +1
- T (tritium) → H with mass diff +2

## Internal Atom Structure

```python
class Atom:
    el_number:      # Atomic number (6=C, 7=N, 8=O)
    elname:        # Element symbol ("C", "N", "O")
    neighbor:      # List of atom indices (0-based)
    bond_type:     # List of bond orders
    orig_at_number:# Original atom number
    num_H:         # Implicit hydrogens
    charge:       # Formal charge
    iso_atw_diff:  # Isotopic mass difference
    radical:      # 0=none, 1=singlet, 2=doublet, 3=triplet
```

## Test Verification

For ethanol (C2H6O):
- Carbon 1 (O-bonded): valence=3 (to O + 2 C), std_valence=4, implicit_H=1
- Carbon 2 (terminal): valence=1 (to C), std_valence=4, implicit_H=3  
- Oxygen: valence=1 (to C), std_valence=2, implicit_H=1

For benzene (C6H6):
- Each carbon: valence=2 (to 2 C), std_valence=4, implicit_H=2

## Next Step

Proceed to `03_NORMALIZATION.md` for structure normalization.