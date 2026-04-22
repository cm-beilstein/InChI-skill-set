# Mathematics of Stereochemistry in InChI Generation

**Analysis Date:** 2026-04-22

## 1. Overview

Stereochemistry—the three-dimensional spatial arrangement of atoms—requires mathematical treatment because molecules with identical connectivity can exist as distinct isomers with different physical and biological properties. The InChI identifier must capture this stereochemical information in a canonical, reproducible way. This document explains the mathematical foundations: the tetrahedral (sp³) stereochemistry calculation using volume determinants, the CIP priority system for canonical ranking, and geometric (E/Z) stereochemistry for double bonds.

Two fundamentally different types of stereochemistry are handled:

1. **Tetrahedral (sp³) stereochemistry**: Four ligands arranged around a central atom in 3D space, creating chiral centers
2. **Geometric (E/Z) stereochemistry**: Cis/trans isomerism around double bonds where rotation is restricted

The InChI system stores stereochemistry as **parity** (ODD/EVEN) rather than directly as R/S or E/Z descriptors, though these can be derived when complete priority information is available.

## 2. Tetrahedral Stereochemistry

### 2.1 The Stereogenic Center

A tetrahedral stereocenter exists when a central atom (typically carbon, nitrogen, phosphorus, or sulfur) has four distinct ligands bonded to it in three-dimensional space. The spatial arrangement cannot be superimposed on its mirror image—this is **chirality**. In 2D molecular drawings, stereochemistry is indicated by wedge/dash notation where:

- **Wedge (solid triangle)**: Bond projects toward the viewer (positive z-direction)
- **Dash (dashed triangle)**: Bond projects away from the viewer (negative z-direction)
- **Plain line**: Bond in the plane of the drawing (z ≈ 0)

The InChI library supports tetrahedral stereocenters on: C, Si, N, P, S, As, Se, and Ge (see Technical Manual Table 5).

### 2.2 Parity Calculation: The Triple Product

The core mathematical operation for tetrahedral stereochemistry is the **scalar triple product**, which calculates the signed volume of a tetrahedron formed by the central atom and three ligands. This volume's sign determines the parity.

Given four position vectors from the central atom to its ligands:
- **v₁, v₂, v₃** = position vectors to three ligands
- **v₄** = position vector to the fourth ligand (implicit or explicit)

The triple product is: **V = v₁ · (v₂ × v₃)**

This is mathematically equivalent to the determinant:

```
| v₁x  v₁y  v₁z |
| v₂x  v₂y  v₂z |  =  v₁x(v₂y·v₃z - v₂z·v₃y) - v₁y(v₂x·v₃z - v₂z·v₃x) + v₁z(v₂x·v₃y - v₂y·v₃x)
| v₃x  v₃y  v₃z |
```

**Sign Interpretation:**
- **V > 0 (positive)**: EVEN parity = counterclockwise arrangement when viewed along v₄ toward the central atom
- **V < 0 (negative)**: ODD parity = clockwise arrangement when viewed along v₄ toward the central atom

In the InChI source (`ichister.c`, line 4315):
```c
parity = triple_product > 0.0 ? AB_PARITY_EVEN : AB_PARITY_ODD;
```

### 2.3 Relationship to R/S Descriptors

**Important Distinction**: InChI parity is algorithm-derived from geometry and is NOT identical to R/S nomenclature. R/S assignment requires both:
1. The spatial arrangement (parity)
2. The CIP priority ranking of all four substituents

Two molecules may have identical InChI parity values but opposite R/S descriptors if their substituent priority orderings differ. For example, swapping the two lowest-priority groups inverts R/S but preserves parity.

**Mapping to R/S** (when complete CIP ranking is available):
- Order substituents by CIP priority (1 = highest, 4 = lowest)
- View molecule with lowest-priority group pointing away
- If 1→2→3 proceeds clockwise → **R** (rectus)
- If 1→2→3 proceeds counterclockwise → **S** (sinister)

With canonical numbering and known priorities, InChI can derive R/S from parity.

## 3. CIP Priority Rules

### 3.1 Cahn-Ingold-Prelog System

The Cahn-Ingold-Prelog (CIP) priority rules establish a canonical ranking of substituents, essential for:
1. Determining R/S configuration
2. Determining E/Z geometry
3. Canonicalization of stereocenters in InChI

### 3.2 Priority Algorithm

**Step 1: Compare atomic numbers**
Compare the atomic numbers (Z) of atoms directly bonded to the stereocenter:
- Higher atomic number = higher priority
- Hydrogen (Z=1) is lowest priority
- Isotope priority: higher mass number > lower mass number

**Step 2: Tie-breaking (iterative)**
If two atoms have the same atomic number, examine their next neighbors:
1. List all atoms bonded to each (excluding the stereocenter)
2. Sort each list by atomic number
3. Compare the sorted lists lexicographically
4. If still tied, continue outward iteratively

**Step 3: Multiple bond handling**
Multiple bonds are treated as "phantom" connections:
- C=O becomes C attached to (O, O)
- C≡N becomes C attached to (N, N, N)
- This is the **duplicate atom** rule

### 3.3 CIP in InChI Canonicalization

During canonicalization (`ichicans.c`), atoms receive **ranks** that encode CIP priority information. These ranks enable:
- Canonical ordering of stereocenters
- Determination of whether parity is absolute or relative
- Detection of meso compounds (internal symmetry)

The canonical numbers assigned to atoms serve as indices in the stereochemistry layer, ensuring reproducibility regardless of input atom ordering.

## 4. Geometric (E/Z) Stereochemistry

### 4.1 Double Bond Stereochemistry

Double bond stereochemistry arises when each carbon of a C=C bond has two different substituents—the restricted rotation prevents interconversion. The arrangement is described by E/Z nomenclature:

- **Z (zusammen, "together")**: Higher-priority substituents on the same side
- **E (entgegen, "opposite")**: Higher-priority substituents on opposite sides

### 4.2 Mathematical Treatment

Unlike tetrahedral centers which use the triple product, double bond stereochemistry uses a **half-parity** approach:

1. **Calculate half-parity at each end** of the double bond
2. **Determine z-direction** for substituents at each carbon (wedge/dash or 3D)
3. **Combine half-parities** accounting for relative z-directions

For each carbon of the double bond:
```c
half_parity = calculate_half_stereo_bond_parity(atom, neighbors, z_direction);
```

**Combining half-parities** (`triple_prod_char` in `ichister.c`):
- If the z-directions at each end point in opposite directions, invert one half-parity
- Final bond parity = product (modulo inversion rules)

The result maps to:
- **EVEN parity** → Z (cis-like): higher-priority groups on same side
- **ODD parity** → E (trans-like): higher-priority groups on opposite sides

### 4.3 Cumulene Stereochemistry

Cumulenes (multiple consecutive double bonds) have special stereochemistry:
- **Odd number of double bonds** (=C=C=): stereocenter on middle carbon
- **Even number of double bonds**: "long stereogenic bond"

The algorithm treats these by examining z-directions from both ends of the cumulated system.

## 5. InChI Stereo Layer Construction

### 5.1 Layer Structure

The stereochemistry information appears in multiple sublayers of the InChI:

| Sublayer | Content | Format |
|----------|---------|--------|
| `/t` | Tetrahedral centers | `t<num>o<num>e<num>...` |
| `/b` | Double bond stereo | `b<num1>o<num2>...` |
| `/s` | Absolute/relative/racemic | `s<value>` (1=absolute, 2=rel, 3=racemic) |
| `/m` | Parity inversion flag | `m<num>` (for transformation) |

**Example**: `InChI=1S/C4H8/c1-3-4-2/h3-4H,1-2H3/b4-3+/t?/m0/s1`

### 5.2 Parity Values

From `extr_ct.h` (lines 253-259):
```c
#define AB_PARITY_NONE   0  /* no parity */
#define AB_PARITY_ODD    1  /* odd parity: clockwise */
#define AB_PARITY_EVEN   2  /* even parity: counterclockwise */
#define AB_PARITY_UNKN   3  /* user marked unknown */
#define AB_PARITY_UNDF   4  /* undefined due to symmetry */
#define AB_PARITY_IISO   5  /* identical isotopes - no stereo */
#define AB_PARITY_CALC   6  /* calculate later from ranks */
```

### 5.3 Inversion Flags

The `/m` flag indicates whether stereochemistry was inverted during structure transformation (e.g., salt formation/removal):
- `m0`: no inversion
- `m1`: parity inverted (odd↔even)
- Applied to track relationship between original and transformed structure

## 6. Mathematical Formulas Summary

### 6.1 Tetrahedral Parity

```
Parity = sign( v₁ · (v₂ × v₃) )

where vᵢ = position_vector(ligand_i) - position_vector(central_atom)

Parity = EVEN  if v₁ · (v₂ × v₃) > 0
Parity = ODD   if v₁ · (v₂ × v₃) < 0
```

### 6.2 Volume of Tetrahedron

The absolute value of the triple product equals 6× the volume of the tetrahedron formed by the central atom and three ligands:

```
Volume = |v₁ · (v₂ × v₃)| / 6
```

### 6.3 Canonical Number Ordering

InChI uses **canonical numbers** (assigned during graph canonicalization) as indices in the stereochemistry layer. This ensures the same molecule produces identical stereo layers regardless of input atom ordering:

```
Stereo layer atom = canonical_number(atom_in_original_input)
```

The parity is stored as a function of these canonical indices.

## 7. Code Location

### 7.1 Primary Implementation Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| `INCHI_BASE/src/ichister.c` | Main stereochemistry calculation (4904 lines) | `set_stereo_parity()`, `set_stereo_atom_parity()`, `triple_prod()` |
| `INCHI_BASE/src/ichister.h` | Function declarations | |
| `INCHI_BASE/src/ichicans.c` | Canonical number assignment with stereo ranks | Rank assignment for CIP priorities |
| `INCHI_BASE/src/extr_ct.h` | Parity definitions (lines 253-259) | `AB_PARITY_ODD`, `AB_PARITY_EVEN` |

### 7.2 Key Functions

**In `ichister.c`:**
- `set_stereo_parity()` (line 4398): Main entry point, orchestrates all stereo detection
- `set_stereo_atom_parity()` (line 3945): Calculates tetrahedral stereocenter parity
- `set_stereo_bonds_parity()` (line 3056): Calculates double bond and cumulene parity
- `half_stereo_bond_parity()` (line 2414): Calculates half-parity for one end of stereobond
- `triple_prod()` (line 347): Scalar triple product calculation
- `GetStereocenter0DParity()` (line 3734): Handles 0D (no coordinates) parity calculation

**Parity determination** (line 4315):
```c
parity = triple_product > 0.0 ? AB_PARITY_EVEN : AB_PARITY_ODD;
```

## 8. Examples

### 8.1 (R)- vs (S)-Lactic Acid

Lactic acid (CH₃-CH(OH)-COOH) has a chiral carbon:

**Structure:**
```
        H (4)
         \
    CH₃ - C* (2) - COOH (1)
         /
        OH (3)
```

With canonical numbering 1=COOH, 2=central C, 3=OH, 4=CH₃:

- CIP priorities: 1 (O,O) > 3 (O) > 4 (C) > H
- Viewing with H away, 1→3→4 proceeds clockwise → **S configuration**
- If the spatial arrangement differs (different 3D coordinates), the parity reverses

**InChI output** would include `/t2f-1/` indicating tetrahedral center at canonical position 2 with parity derived from the geometry.

### 8.2 (E)- vs (Z)-But-2-ene

2-Butene (CH₃-CH=CH-CH₃) exhibits cis/trans isomerism:

**E (trans)-but-2-ene:**
```
    CH₃        CH₃
      \      /
       C  =  C
      /      \
     H        H
```
Higher-priority groups (CH₃) on opposite sides → EVEN parity (Z-like mapping)

**Z (cis)-but-2-ene:**
```
    CH₃      H
      \    /
       C=C
      /    \
     H     CH₃
```
Higher-priority groups on same side → ODD parity

**InChI:** `/b2-3/f-2.3.6/m0/s1` indicates bond between canonical atoms 2-3 with geometric stereo.

## 9. References

1. **IUPAC Blue Book P-9**: Stereochemical specification
   - https://iupac.qmul.ac.uk/BlueBook/P9.html
   - Defines R/S and E/Z descriptor systems

2. **IUPAC Blue Book P-93**: R/S descriptor for tetrahedral centers

3. **IUPAC Blue Book P-92**: E/Z descriptor for double bonds

4. **InChI Technical Manual**: Official stereochemistry documentation
   - Section on stereochemistry layers
   - Table 5: Elements supporting tetrahedral stereo

5. **CIP Priority Rules**: Cahn-Ingold-Prelog priority rules
   - Wikipedia: https://en.wikipedia.org/wiki/Cahn%E2%80%93Ingold%E2%80%93Prelog_priority_rule
   - IUPAC recommendations for stereochemical nomenclature

6. **Source Code**:
   - `INCHI_BASE/src/ichister.c`: Main stereochemistry implementation
   - `INCHI_BASE/src/extr_ct.h`: Parity constant definitions
   - `INCHI_BASE/src/ichicans.c`: Canonicalization with stereo ranks

---

*Mathematics documentation: Stereochemistry in InChI generation*
