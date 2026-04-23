# Enhanced Stereochemistry in InChI - Overview

**Analysis Date:** 2026-04-23

## What is Enhanced Stereochemistry?

Enhanced stereochemistry is an InChI feature (introduced in v1.02) that allows representation of **stereogroups** - collections of atoms or bonds that share common stereochemical relationships. Unlike standard tetrahedral (R/S) and geometric (E/Z) stereochemistry which are defined per-center or per-bond, enhanced stereochemistry enables grouping of multiple stereocenters as a unit.

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

Enhanced stereochemistry adds new layers to the InChI identifier:

```
InChI=1S/.../c.../h.../b.../t1,2,3/m0/s1(a1,a2)a3,s2(b1)b2,s3(c1)c2
            └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘
              /t    /b    /s    /m
              |     |     |     |
         Double-bond  Tetrahedral  Stereo    Mobile-H
         (geometric)   stereo     groups  inversion flag
```

The `/m` layer contains the inversion flag for enhanced stereo:
- `/m0` = Absolute configuration unchanged
- `/m1` = Inverted (mirrored)

### S-Layer Format (CRITICAL - Multiple Groups per Type!)

The `/s` layer is NOT just `1`, `2`, or `3`. It contains **explicit atom lists** for each stereogroup:

```
/s1(canonical_atoms)canonical_atoms,s2(canonical_atoms),s3(canonical_atoms)
```

Where:
- `s1` = Absolute (STEABS) group atoms
- `s2` = Relative (STERELn) group atoms (multiple groups allowed)
- `s3` = Racemic (STERACn) group atoms (multiple groups allowed)

**Format Details:**
- Each group outputs as `sX(atom1,atom2,...)` where X is 1, 2, or 3
- Multiple groups of the same type are **separate parenthetical groups**
- Atoms are listed using **canonical numbers** (not original atom numbers)
- Groups are sorted by the first canonical atom number in each group

### Example Output

```
InChI=1S/C10H14BrCl7/c1-3(11)5(13)7(15)9(17)10(18)8(16)6(14)4(2)12/h3-10H,1-2H3/t3-,4-,5+,6-,7-,8-,9+,10-/m0/s1(3,5)2(4)(6,8)3(7,9)(10)
```

Breaking down the s-layer:
- `/s1(3,5)` = Absolute group (STEABS): atoms 3,5
- `/s2(4)` = Relative 1 (STEREL1): atom 4  
- `/s2(6,8)` = Relative 2 (STEREL2): atoms 6,8
- `/s3(7,9)` = Racemic 1 (STERAC1): atoms 7,9
- `/s3(10)` = Racemic 2 (STERAC2): atom 10

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

| Version | Change |
|---------|-------|
| 1.00 | Basic tetrahedral and geometric stereo |
| 1.02 | Added enhanced stereochemistry support |
| 1.05 | Improved handling of macrocycles |
| 1.07 | Atropisomer support added (related feature) |

---

## References

- InChI Technical Manual, Section 10: Enhanced Stereochemistry
- CTFile V3000 Format Specification (BIOVIA)
- Source: `mol_fmt3.c` lines 695-780, `ichiprt1.c` lines 3508-3600

---

*Overview: 2026-04-23*