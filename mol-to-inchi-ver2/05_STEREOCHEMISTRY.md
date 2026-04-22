# Step 5: Stereochemistry Processing

**Input:** Canonicalized atoms with coordinates
**Output:** Stereocenter parities for InChI layers

> **CRITICAL:** Implement stereochemistry detection yourself. Do NOT use library functions to determine R/S or E/Z configuration.

## Stereochemistry Types

### 1. Tetrahedral (sp³) Stereocenters

Carbon (and N, P, S, Si, As, Se) with 4 different substituents:

```
        L1
        |
    L2-C-L3
        |
        L4

Parity = ODD/EVEN based on spatial arrangement
```

Detection criteria:
- Atom has 4 non-hydrogen neighbors
- All 4 substituents are different
- Has 2D coordinates (wedge/dash) or 3D coordinates

### 2. Double Bond (sp²) Stereochemistry

E/Z (cis/trans) isomerism around C=C:

```
    L1        L1
     \        /
      C=C    C
     /        \
    L2        L2

Parity determines Z (together) vs E (opposite)
```

### 3. Cumulene/Allene Stereochemistry

=CH=CH= chain with alternating substituents
(odd chain length has tetrahedral stereocenter at middle)

## Parity Values

| Value | Meaning |
|-------|--------|
| 0 | Not a stereocenter |
| 1 | ODD (clockwise) |
| 2 | EVEN (counter-clockwise) |
| 3 | User marked unknown |
| 4 | Undefined (symmetry) |
| 5 | Identical isotopes |

## CIP Priority Rules

For R/S determination, use Cahn-Ingold-Prelog priority:

1. Atomic number (higher = higher priority)
2. For ties, examine next atoms outward
3. Multiple bonds = pseudo-atoms
4. Isotopic mass resolves final ties

## Tetrahedral Parity Calculation

Using 2D coordinates, compute triple product:

```
# Get 3 substituents' coordinates relative to stereocenter
v1 = coord(substituent1) - coord(stereocenter)
v2 = coord(substituent2) - coord(stereocenter)  
v3 = coord(substituent3) - coord(stereocenter)

# Triple product: v1 · (v2 × v3)
# Represents signed volume of tetrahedron

triple_product = v1.x * (v2.y * v3.z - v2.z * v3.y) + \
              v1.y * (v2.z * v3.x - v2.x * v3.z) + \
              v1.z * (v2.x * v3.y - v2.y * v3.x)

if triple_product > 0: parity = ODD
if triple_product < 0: parity = EVEN
if triple_product == 0: parity = UNDEFINED (planar)
```

For 2D (no z-coordinates), use wedge/dash convention:
- Wedge = toward viewer (+z)
- Dash = away from viewer (-z)

## Double Bond Parity Calculation

For each end of double bond, compute half-parity:
```
half_parity = based on priorities of 2 substituents
```

Combine half-parities:
```
if z_directions_opposite: combine as E
if z_directions_same: combine as Z
```

## InChI Stereo Layer Format

Tetrahedral (sp3):
```
/t3/m1/2
      ^parity: m=minus(ODD), p=plus(EVEN)
/t3-/m1/2  = S configuration
/t3+/m1/2  = R configuration
```

Double bond (sp2):
```
/b3/m1/2
      ^parity for bond 3
/b3-/m1/2  = trans (E)
/b3+/m1/2  = cis (Z)
```

Combined stereo markers:
```
/s  = absolute
/t  /b = both sp3 and sp2
/m  = markers
```

## Stereochemistry in InChI Output

From test file `CHEBI_140096.mol`:
- If chiral center exists, appears in `/t` layer
- Double bond stereochemistry appears in `/b` layer
- Absolute/relative marks in `/s` layer

## Common Cases

### No Stereochemistry
- Achiral molecules (methane, ethane)
- Meso compounds
- Internal symmetry (benzene)

### With Stereochemistry
- L-Alanine: Has chiral carbon
- Tartaric acid: Has 2 chiral centers
- 2-Butene: Has E/Z isomerism

## Test Verification

Check each test .inchi file for presence of:
- `/t` layer if sp3 stereocenters exist
- `/b` layer if sp2 stereocenters exist
- `/s` layer for absolute/relative/racemic

## Next Step

Proceed to `06_TAUTOMERISM.md` for mobile hydrogen handling.