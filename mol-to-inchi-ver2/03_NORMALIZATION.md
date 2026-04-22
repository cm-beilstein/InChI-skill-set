# Step 3: Structure Normalization

**Input:** Atoms with implicit hydrogens, bond connectivity
**Output:** Normalized structure with aromatic bonds resolved, charge groups marked

> **CRITICAL:** Implement normalization yourself. Do NOT use library functions to resolve aromatic bonds or detect charge groups.

## Normalization Goals

1. **Aromatic bond resolution**: Convert aromatic bonds to alternating single/double
2. **Charge group identification**: Group atoms with interdependent charges
3. **Tautomer group preparation**: Mark potential mobile-H endpoints
4. **Salt disconnection**: Separate ionic components if applicable

## Aromatic Bond Resolution

Aromatic bonds (type 4 in MOL) are delocalized. InChI resolves them to alternating single/double bonds for canonicalization:

```
Input:  benzene with aromatic bonds (type 4)
Output: alternating single/double bonds:
        
        C1=C2    (double)
        C2-C3    (single)  
        C3=C4    (double)
        C4-C5    (single)
        C5=C6    (double)
        C6-C1    (single)
```

Algorithm:
```
function resolve_aromatic_bonds(atoms):
    for each aromatic bond:
        # Find alternating pattern that satisfies valences
        # Prefer pattern starting with double bond on more substituted carbon
        bond1.type = 2
        bond2.type = 1
    
    return atoms
```

## Charge Group Identification

Charge groups track interdependent charges that can neutralize each other:
- Adjacent +1 and -1 charges
- Zwitterionic forms (e.g., -COO- and -NH3+)

```
function find_charge_groups(atoms):
    charge_groups = []
    
    for each charged atom:
        # Find adjacent opposite charges
        for each neighbor:
            if opposite_charge(neighbor):
                create_charge_group([atom, neighbor])
    
    return charge_groups
```

## Tautomer Group Marking

Potential tautomeric endpoints are atoms that can gain/lose a proton:

| Element | Can Donate? | Can Accept? |
|---------|-----------|-------------|
| O       | Yes (with H) | Yes (with lone pair) |
| N       | Yes (with H) | Yes (with lone pair) |
| S       | Yes (with H) | Yes (with lone pair) |
| C       | No        | Sometimes    |

Endpoint detection:
```
function find_endpoint(atoms):
    for atom in atoms:
        if atom.element in [O, N, S]:
            if atom.charge <= 0 and atom.num_H > 0:
                atom.is_endpoint_donor = True
            if atom.valence < max_valence:
                atom.is_endpoint_acceptor = True
    
    return atoms
```

## Standard InChI Normalization Rules

1. **Keto-enol prefer keto form**: Carbonyl + adjacent CH → prefer C=O over C=C-OH
2. **Amide prefer amide form**: -C(=O)-NH2 ↔ -C(-OH)=NH, prefer amide
3. **Charge cancellation**: Adjacent +1/-1 → neutralize with proton transfer
4. **Metal disconnection**: Disconnect alkali metals from organic anions

## Output After Normalization

After normalization, each atom has:
- `endpoint`: Whether atom can participate in tautomerism
- `charge_group_id`: ID of charge group (0 if none)
- `ring_system`: Ring system number
- Fixed bond orders (no aromatic type 4)

## Test Cases

### Ethanol (C2H6O)
- No aromatic bonds
- No charge groups
- No tautomeric endpoints (simple alcohol)
- Output: Same as input, but with implicit H calculated

### Benzoic Acid (C7H6O2)
- Aromatic ring bonds resolved
- Carboxyl group: one -OH (donor), one C=O (acceptor)
- Forms tautomer group for acid-base

### Benzene (C6H6)
- All 6 aromatic bonds resolved to alternating pattern
- No charge groups
- No tautomeric endpoints

## Next Step

Proceed to `04_CANONICALIZATION.md` for unique atom ordering.