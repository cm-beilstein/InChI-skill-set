# MOL V2000/V3000 Format Details

## V2000 Fixed-Column Format

### Counts Line
```
cols 1-3:   aaa = number of atoms (001-999)
cols 4-6:   bbb = number of bonds (001-999)
cols 7-9:   lll = number of atom lists
cols 10-12:  fff = number of 3D objects
cols 13-15:  ccc = chiral flag (0 or 1)
cols 16-18:  sss = number of stereotext entries
cols 19-21:  xxx = number of property lines
cols 22-24:  rrr = registration number flag
cols 25-27:  ppp = number of links
cols 28-31:  nnn = explicit H count
cols 32-34:        V2000 or V3000
```

### Atom Line (10 fixed-width fields)
```
cols  1-10:  x coordinate (floating point)
cols 11-20:  y coordinate
cols 21-30:  z coordinate
cols 31-34:  element symbol (1-3 chars)
cols 35-36:  mass difference (-5 to +5, 0=natural)
cols 37-38:  charge code (0=none, 1=+3, 2=+2, 3=+1, 4=-1, 5=-2, 6=-3, 7=radical)
cols 39-40:  stereo parity (0=none, 1=odd, 2=even, 3=either)
cols 41-42:  H count + 1 (0-4 = actual 1-4 H atoms)
cols 43-44:  valence (0=auto, 1-14=explicit)
cols 45-50:  (unused, always 0)
```

### Bond Line
```
cols 1-3:   atom 1 number (1-indexed)
cols 4-6:   atom 2 number
cols 7-9:   bond type (1=single, 2=double, 3=triple, 4=aromatic, 5=single/double, 6=single/aromatic, 7=double/aromatic, 8=any)
cols 10-12: stereo (0=none, 1=up, 2=down, 3=cumulen, 4=either)
cols 13-15: topology (0=either, 1=ring, 2=chain)
cols 16-18: reacting center (0=either, -1=not center, 1=center)
```

### Properties Block
```
M  CHG n a1 c1 a2 c2 ...     charge: n pairs of (atom, charge)
M  RAD n a1 r1 a2 r2 ...     radical: 1=singlet, 2=doublet, 3=triplet
M  ISO n a1 i1 a2 i2 ...     isotope: absolute mass number
M  END                        end of molecule
```

## V3000 Keyword Format

### Counts Line (Header Compatibility)
Line 4: `0  0  0  0  0 999 V3000`

### CTAB Block
```
M  V30 BEGIN CTAB
M  V30 COUNTS na nb nsg n3d chiral    na=atoms, nb=bonds, nsg=sgroups, n3d=3d, chiral=0/1
M  V30 BEGIN ATOM
M  V30 idx sym x y z aamap [props]
...
M  V30 END ATOM
M  V30 BEGIN BOND
M  V30 idx typ a1 a2 [props]
...
M  V30 END BOND
M  V30 END CTAB
M  END
```

### V3000 Atom Properties
| Keyword | Description |
|---------|-------------|
| CHG | Formal charge (-5 to +5) |
| RAD | Radical (1=singlet, 2=doublet, 3=triplet) |
| CFG | Stereochemistry parity (1=odd, 2=even, 3=either) |
| MASS | Isotopic mass (absolute) |
| VAL | Valence (0=normal, -1=zero) |
| HCOUNT | Explicit hydrogen count |

### V3000 Bond Properties
| Keyword | Description |
|---------|-------------|
| CFG | Bond stereo (0=none, 1=up, 4=either, 6=down) |
| TOPO | Topology (0=either, 1=ring, 2=chain) |

### Enhanced Stereo Collections
```
M  V30 BEGIN COLLECTION
M  V30 MDLV30/STEABS ATOMS=(n atom1 atom2 ...)
M  V30 MDLV30/STERELn ATOMS=(n atom1 atom2 ...)   n=1,2,3...
M  V30 MDLV30/STERACn ATOMS=(n atom1 atom2 ...)
M  V30 END COLLECTION
```
- STEABS: absolute stereo
- STERELn: relative stereo
- STERACn: racemic mixture

## SDF (SDFile) Format

Multiple MOL records separated by `$$$$` delimiter:
```
[MOL record 1]
$$$$
[MOL record 2]
$$$$
...
```

## Common Pitfalls

1. **Atom symbols**: Case-sensitive. Use standard symbols (C, N, O, etc.). "Cl" and "BR" are valid; "c", "n", "o" may not be recognized.
2. **Hydrogen**: Explicit H atoms should be included in atom count. Alternatively, valence + H+1 field determines implicit H.
3. **Charge**: V2000 uses codes (1=+3, not +1). V3000 uses direct values (CHG=1 = +1).
4. **Aromatic bonds**: Type 4, not "single" or "double". Recognized as delocalized.
5. **Sulfur/Selenium**: S (16), Se (34). Both can have valences 2, 4, 6.
6. **Phosphorus**: P (15), valence 3 or 5.
7. **Implicit H counting**: Standard valence minus sum(bond orders). E.g., carbonyl C (type 2) has bond order 2, so implicit H = 4-2 = 2.
8. **Star atoms**: `*` in V3000 represents unknown/placeholder atoms.