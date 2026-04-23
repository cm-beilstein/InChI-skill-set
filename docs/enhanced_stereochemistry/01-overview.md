# Enhanced Stereochemistry in InChI - Overview

**Analysis Date:** 2026-04-23

## What is Enhanced Stereochemistry?

Enhanced stereochemistry is an InChI feature that allows representation of **stereogroups** - collections of atoms or bonds that share common stereochemical relationships. Unlike standard tetrahedral (R/S) and geometric (E/Z) stereochemistry which are defined per-center or per-bond, enhanced stereochemistry enables grouping of multiple stereocenters as a unit.

### Standard vs Enhanced Stereochemistry

| Aspect | Standard | Enhanced |
|--------|----------|-----------|
| **Tetrahedral** | Per-atom parity (R/S) | Grouped into ABS, REL, RAC collections |
| **Geometric** | Per-bond E/Z | Grouped into ABS, REL, RAC collections |
| **Definition** | Individual centers/bonds | Collections of related stereocenters |

### Stereogroup Types

| Type | Tag | Description | Example |
|------|-----|-------------|---------|
| **Absolute** | `MDLV30/STEABS` | All centers have known absolute configuration | All R or all S |
| **Relative** | `MDLV30/STERELn` | Centers relative to each other | "Same side" or "opposite sides" |
| **Racemic** | `MDLV30/STERACn` | Unknown configuration (mixture) | Either R or S |

The `n` suffix in REL and RAC is an index (1, 2, 3...) allowing multiple groups.

### Use Cases

1. **Macrocycles**: Many chiral centers that must be described as a group
2. **Complex natural products**: Polycyclic compounds with multiple stereocenters
3. **Relative stereochemistry**: When absolute configuration is unknown but relationships are known
4. **Racemic mixtures**: When individual center configurations are undetermined
5. **Atropisomers**: Axial chirality in biaryls

## InChI Enhanced Stereo Layers

Enhanced stereochemistry adds new layers to the InChI identifier. Here's a real example from the unit tests:

```
InChI=1B/C10H14BrCl7/c1-3(11)5(13)7(15)9(17)10(18)8(16)6(14)4(2)12/h3-10H,1-2H3/t3-,4-,5+,6-,7-,8-,9+,10-/m0/s1(3,5)2(4)(6,8)3(7,9)(10)
```

| Layer | Position in Example | Description |
|-------|---------------------|-------------|
| `InChI=1B` | start | version (1) + flag (B) |
| `/C10H14BrCl7` | after InChI=1B | molecular formula |
| `/c...` | after `/C...` | connectivity (atom connections) |
| `/h...` | after `/c...` | hydrogen layer |
| `/t...` | after `/h...` | tetrahedral stereochemistry (parities) |
| `/m0` | after `/t...` | mobile-H inversion flag (0=unchanged, 1=inverted) |
| `/s...` | after `/m0` | enhanced stereo groups (s1=ABS, s2=REL, s3=RAC) |

The `/m` layer contains the inversion flag for enhanced stereo:
- `/m0` = Absolute configuration unchanged
- `/m1` = Inverted (mirrored)

### How Inversion Works

When the `/m1` flag is set, stereochemistry is inverted via the `invert_parities()` function in `strutil.c`:

**Parity Values:**
- t-layer: `2` = "+" (e.g., R), `1` = "-" (e.g., S)
- m-layer: `-1` = `/m0` (unchanged), `1` = `/m1` (inverted)

**Inversion Process:**
1. For each stereogroup, find the atom with the lowest canonical number
2. If that atom has defined parity (`2`), flip ALL parities in the group:
   - `1` → `2` (minus becomes plus)
   - `2` → `1` (plus becomes minus)
3. Mark the group as inverted (`nCompInv2Abs = -1`)

**Example:**
```
Input:  /t3-,4-,5+,6-/m0/s1(3,4)(5)(6)
After inversion (/m1):
        /t3+,4+,5-,6-/m1/s1(3,4)(5)(6)
```

Each center's R/S designation is literally mirrored.

### S-Layer Format (CRITICAL - Multiple Groups per Type!)

The `/s` layer is NOT just `1`, `2`, or `3`. It contains **explicit atom lists** for each stereogroup:

```
/s1(3,5)2(4)(6,8)3(7,9)(10)
```

ONE `s` at beginning, then groups concatenated:
- `s1` = Absolute (STEABS) - appears as `s1(atoms)`
- `s2` = Relative (STERELn) - appears as `s2(atoms)(atoms)...` (multiple allowed)
- `s3` = Racemic (STERACn) - appears as `s3(atoms)(atoms)...` (multiple allowed)

**Format Details:**
- Each group outputs as `X(atom1,atom2,...)` where X is 1, 2, or 3
- Multiple groups of the same type are **separate parenthetical groups**
- Atoms are listed using **canonical numbers** (not original atom numbers)
- Groups are sorted by the first canonical atom number in each group

### Example Output

```
InChI=1B/C10H14BrCl7/c1-3(11)5(13)7(15)9(17)10(18)8(16)6(14)4(2)12/h3-10H,1-2H3/t3-,4-,5+,6-,7-,8-,9+,10-/m0/s1(3,5)2(4)(6,8)3(7,9)(10)
```

Breaking down the s-layer (`/s` prefix + groups):
- `1(3,5)` = Absolute group (STEABS): atoms 3,5
- `2(4)` = Relative 1 (STEREL1): atom 4  
- `2(6,8)` = Relative 2 (STEREL2): atoms 6,8
- `3(7,9)` = Racemic 1 (STERAC1): atoms 7,9
- `3(10)` = Racemic 2 (STERAC2): atom 10

---

## Command Line Usage

Enable enhanced stereochemistry processing with the `-EnhancedStereochemistry` option:

```
inchi-1 some.mol -EnhancedStereochemistry
```

Or use the long form:

```
inchi-1 some.mol --EnhancedStereochemistry
```

In the API, set the flag:

```c
ip->bEnhancedStereo = 1;  // Enable enhanced stereochemistry
```

---

## History

---

## References


---

*Overview: 2026-04-23*