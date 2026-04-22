# Step 6: Tautomerism Processing

**Input:** Normalized structure with endpoints identified
**Output:** Mobile hydrogen layer data

> **CRITICAL:** Implement tautomer detection yourself. Do NOT use library functions to identify mobile hydrogens or tautomeric endpoints.

## Prototropic Tautomerism

Movement of a hydrogen atom (proton) between atoms with concurrent bond order changes:

```
Keto form:     R-C(=O)-CH2-R'    ↔    R-CH(OH)=C(R')
                |                           |
               O-H (mobile)            C-H (mobile)

Enol form:     R-C(OH)=C(R')-H       ↔    R-C(=O)-CH(R')-
```

## Mobile Hydrogen Detection

### Valid Endpoint Pairs

| Donor | Acceptor | Example |
|-------|----------|---------|
| O with H | O (carbonyl) | Keto-enol |
| O with H | N | Oxim-no |
| N with H | O | Amide-imidol |
| N with H | N | Enamine-imine |

### Ketone-Enol Example: Acetone

```
Input structure:  CH3-C(=O)-CH3
                 |     |
                O    CH2 (mobile H)

Endpoint 1: O (acceptor)
Endpoint 2: CH2 (donor)

Mobile H count: 1

Output layer: /h1+1c2
            ^endpoint c2 has 1 mobile H
```

## InChI Mobile-H Layer Format

```
/h{mobile_H_description}

Format: /h<atom_number>+<count>c<charge>
Multiple: /h1+1c2,3+2c1

Special:
  +n = add n mobile hydrogens at this position
  -n = remove n hydrogens from this position  
  c = has negative charge
  +c = has positive charge (rare)
```

## Mobile-H Layer Examples

### Ethanol (simple, no mobile H)
```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3

/h3H       = 3 H on position 1 (C)
,2H2       = 2 H on position 2 (C)
/,1H3      = 1 H on position 3 (O) + O-H
```

### Acetone (mobile H from CH3)
```
InChI=1S/C3H6O/c1-3(2)4/h1-2H2

Mobile H: positions 1,2 can exchange H
```

### Benzoic Acid (acidic proton)
```
InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)

Note: (H,8,9) = H can move to positions 8 and 9
```

## Tautomer Group Composition

Each tautomer group records:
1. **Endpoints**: Atom numbers participating in H exchange
2. **Mobile H count**: Number of movable protons
3. **Charge**: Any charges that move with the mobile H

## Standard vs Non-Standard InChI

- **Standard InChI** (`InChI=1S/`): Canonical mobile-H, tautomer-invariant
- **Fixed-H InChI** (`InChI=1F/`): Fixed to specific tautomer

## Test Verification

Check expected .inchi files for `/h` layer:
- `/h*` present only if mobile H exist
- Count of mobile H should match structure

## Common Patterns

| Structure | Mobile-H? | Layer |
|-----------|----------|-------|
| Alcohols | No | No /h layer |
| Ketones | Yes | Present |
| Enamines | Yes | Present |
| Carboxylic acids | Yes (OH) | Present |
| Amides | No* | No /h layer |
| Nitro compounds | No | Not tautomeric |

## Next Step

Proceed to `07_ASSEMBLY.md` to compose final InChI string.