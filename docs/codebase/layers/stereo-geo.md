# Geometric Stereo Layer (`/t`)

**Analysis Date:** 2026-04-22

## Overview

The Geometric Stereo layer (`/t`) in InChI represents **cis/trans (E/Z) stereochemistry** associated with double bonds and cumulenes. This layer encodes the three-dimensional arrangement of substituents around stereogenic double bonds, where "cis" (Z, Zusammen) means substituents on the same side, and "trans" (E, Entgegen) means they're on opposite sides.

The `/t` layer is used when a molecule contains one or more stereogenic double bonds - that is, double bonds where the two carbon atoms each have two different substituents, creating potential cis/trans isomerism. The layer appears in the InChI string after the main connectivity layer (`/c`) and before isotopic layers.

InChI uses the standard E/Z notation:
- **Z (Zusammen)** = same side (cis)
- **E (Entgegen)** = opposite sides (trans)

The output format uses:
- `-` (minus) for odd parity = Z (cis)
- `+` (plus) for even parity = E (trans)
- `u` for unknown stereochemistry
- `?` for undefined stereochemistry

**Example output:**
```
InChI=1S/C2H4Cl2/c3-1-2/h1-2H2/t2-/m1/s1
                                    ^^^
                                    /t layer
```

For double bond stereo, the format is:
- `/t1-2` = single stereogenic bond between atoms 1 and 2
- `/t1-2,3-4` = multiple stereogenic bonds

## Code Implementation

### Key Source Files

| File | Purpose |
|------|---------|
| `extr_ct.h` | `AT_STEREO_DBLE` structure definition |
| `inpdef.h` | `sb_parity`, `sn_ord`, `sb_ord` atom fields |
| `ichicant.h` | `LinearCTStereoDble` canonical representation |
| `ichister.c` | Core geometric stereo detection and computation |
| `ichimap4.c` | Canonical ordering of double bond stereo |
| `ichimak2.c` | Building canonical stereo representation |
| `ichiprt2.c` | `MakeStereoString()` output generation |
| `ichiprt3.c` | `/t` layer output orchestration |

### Data Structures

#### AT_STEREO_DBLE

Defined in `extr_ct.h` (line 82-87):

```c
typedef struct tagStereoDble
{
    AT_NUMB at_num1;   // First atom of stereogenic double bond
    AT_NUMB at_num2;   // Second atom of stereogenic double bond
    U_CHAR  parity;    // Parity: 1=odd(cis/Z), 2=even(trans/E), 3=unknown, 4=undefined
} AT_STEREO_DBLE;
```

This structure stores each stereogenic double bond as a canonical (ranked) atom pair with its parity value.

#### sb_parity, sb_ord, sn_ord

Defined in `inp_def.h` (lines 178-184):

```c
S_CHAR sb_ord[MAX_NUM_STEREO_BONDS];   // Stereo bond/neighbor ordering number, starts from 0
S_CHAR sn_ord[MAX_NUM_STEREO_BONDS];   // Order number of the neighbor adjacent to SB
S_CHAR sb_parity[MAX_NUM_STEREO_BONDS]; // Bond parity: same sign=>trans/E, diff signs=>cis/Z
```

The parity calculation uses the relationship between substituent ordering:
- **Same parity** (both even or both odd) → trans/E
- **Different parity** (one even, one odd) → cis/Z

The `sb_parity` array stores packed data with flags for disconnected metal complexes (see `SB_PARITY_FLAG`, `SB_PARITY_SHFT`, `SB_PARITY_MASK` in `inpdef.h` lines 97-101).

#### LinearCTStereoDble

Defined in `ichicant.h` (lines 227, 241):

```c
AT_STEREO_DBLE* LinearCTStereoDble;    // Double bond stereo in linear form
AT_STEREO_DBLE* LinearCTStereoDbleInv; // Inverted structure stereo (for comparison)
int nLenLinearCTStereoDble;            // Number of stereogenic bonds
int nLenLinearCTStereoDbleInv;         // Number in inverted structure
```

The linear representation stores all stereogenic double bonds sorted by canonical atom numbers.

#### INChI_Stereo (Output Structure)

Defined in `ichi.h` (lines 121-154), used for final InChI output:

```c
typedef struct tagINChI_Stereo
{
    int      nNumberOfStereoBonds;
    AT_NUMB *nBondAtom1;  // Canonical number of first atom [nNumberOfStereoBonds]
    AT_NUMB *nBondAtom2;  // Canonical number of second atom [nNumberOfStereoBonds]
    S_CHAR  *b_parity;    // Bond parities [nNumberOfStereoBonds]
} INChI_Stereo;
```

### Parity Constants

From `inchi_api.h` (lines 416-421) and `ichister.c`:

```c
#define AB_PARITY_NONE     0   // No stereogenic bond
#define AB_PARITY_ODD      1   // Odd parity = cis/Z
#define AB_PARITY_EVEN     2   // Even parity = trans/E
#define AB_PARITY_UNKN     3   // Unknown (user-specified)
#define AB_PARITY_UNDF     4   // Undefined (cannot be determined)
```

Output characters (from `ichiprt2.c` line 2089):
```c
static const char parity_char[] = "!-+u?";
//                           0    1   2  3  4
//                         none  -   +  u  ?
```

## Pseudo-code Algorithm

### Geometric Stereo Detection

The algorithm for detecting and computing double bond stereochemistry involves several steps:

```
FUNCTION DetectGeometricStereo(atoms[], num_atoms):
    
    FOR each atom i in atoms:
        FOR each bond j from atom i:
            IF bond is double AND bond is stereogenic:
                // Stereogenic if both ends have two different substituents
                atom1 = bond.end1
                atom2 = bond.end2
                
                // Get substituents on each side of double bond
                subs1 = GetSubstituents(atom1, bond)
                subs2 = GetSubstituents(atom2, bond)
                
                // Check if all four substituents are different
                IF AllDifferent(subs1[0], subs1[1], subs2[0], subs2[1]):
                    // Compute parity for each half of the bond
                    parity1 = HalfStereoBondParity(atom1, bond)
                    parity2 = HalfStereoBondParity(atom2, bond)
                    
                    // Combine parities: same sign = trans, different = cis
                    combined_parity = CombineParities(parity1, parity2)
                    
                    // Store in sb_parity array
                    AddStereoBond(atom1, atom2, combined_parity)
    
    RETURN stereo_bonds[]
```

### Parity Computation

```
FUNCTION HalfStereoBondParity(atom, bond):
    
    neighbors = GetNeighbors(atom)
    // Remove the double bond neighbor
    other_neighbors = neighbors EXCEPT bond.partner
    
    IF other_neighbors has exactly 1 atom:
        // Need exactly one hydrogen (for 2D) or well-defined geometry
        h_count = CountHydrogens(other_neighbors[0])
        
        IF h_count == 1:
            // Determine if substituent is "before" or "after" double bond
            // in the sorted neighbor list
            position = GetRelativePosition(atom, bond.partner, other_neighbors[0])
            
            RETURN position // parity based on position
        ELSE:
            RETURN AB_PARITY_UNDF  // Cannot determine
    ELSE:
        // Use 3D coordinates if available, otherwise undefined
        IF Has3DCoordinates(atom):
            RETURN Compute3DParity(atom)
        ELSE:
            RETURN AB_PARITY_UNDF
```

### Canonicalization of Double Bond Stereo

```
FUNCTION CanonicalizeStereoBonds(LinearCTStereoDble, ranks):
    
    // Sort by canonical (ranked) atom numbers
    SORT LinearCTStereoDble BY (ranks[at_num1], ranks[at_num2])
    
    // Create inverted representation for comparison
    LinearCTStereoDbleInv = CreateInverted(LinearCTStereoDble)
    
    // Compare to determine if inversion needed
    IF LinearCTStereoDbleInv < LinearCTStereoDble:
        UseInverted = TRUE
        AdjustParities(LinearCTStereoDble) // flip 1<->2
    
    RETURN LinearCTStereoDble
```

## Examples

### Cis-2-butene

```
Structure: CH3-CH=CH-CH3 (cis configuration)
          H   CH3
           \ /
            C
           / \
         CH3   H

InChI: InChI=1S/C4H8/c1-3-4-2/h3-4H,1-2H3/b4-3+/t?-
                   └─┬──┘└┬┘└┬┘└──┘└──────┘
                   /c   /h   /t    parity
```

### Trans-2-butene

```
Structure: CH3-CH=CH-CH3 (trans configuration)
          H   H
           \ /
            C
           / \
         CH3  CH3

InChI: InChI=1S/C4H8/c1-3-4-2/h3-4H,1-2H3/b4-3+/t?-+
                   └─┬──┘└┬┘└┬┘└──┘└──────┘
                   /c   /h   /t    parity
```

### Multiple Stereogenic Bonds

```
Structure: 1,4-disubstituted cyclohexene with cis double bond

InChI: InChI=1S/C8H12Cl2O2/c1-2-6-8(11)7(10-2)5-3-4-9/h6-8H,1-5H2/b2-1+,7-6-/t?-
                   └──────────┬──────────┘└──────┬─────┘
                        /c            /h           /t
```

### Unknown Stereochemistry

```
Input: Double bond where stereochemistry is not specified

InChI: InChI=1S/C2H4Cl2/c3-1-2/h1-2H2/t2-/m1/s1/u
                                                                   │
                                                                   /u = unknown
```

### Complex: Cumulene Stereo

Cumulenes (multiple conjugated double bonds) can also have geometric stereochemistry:

```
Structure: CH3-CH=CH=CH-CH3 (all-trans)

InChI: InChI=1S/C5H8/c1-3-5-4-2/h3-5H,1-2H3/b4-3+,5-4-/t?-+ 
```

## Stereo Type Layer (/s)

The `/t` layer is complemented by the `/s` layer which specifies the type of stereochemistry:

- `/s` = absolute (default)
- `/s2` = relative
- `/s3` = racemic

This controls how the stereochemistry is interpreted in the context of the complete InChI.

## References

- InChI Technical Manual: Stereo Chemistry
- `ichister.c` - Contains `half_stereo_bond_parity()` (line 2121) and `get_stereo_bond_parity()` (line 3512)
- `ichimap4.c` - Stereo mapping and canonicalization
- `ichiprt2.c` - `MakeStereoString()` for output generation

---

*Layer analysis: 2026-04-22*
