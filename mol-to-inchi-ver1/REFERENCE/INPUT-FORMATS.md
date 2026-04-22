# Input Format Reference

Reference for MOL file formats (V2000 and V3000).

## MOL V2000 Format

### Structure

```
<header line>
<counts line>
<atom block>
<bond block>
M  END
```

### Header Line

First line: molecule name (may be blank or user info).

```
  Ethanol
```
or
```
  ChemDraw1014222352D
```

### Counts Line

Columns 0-2: Atom count (3 characters, right-aligned)
Columns 3-5: Bond count
Additional flags for chiral, query, reaction, etc.

```
  4  3  0  0  0  0  0  0  0  0999V2000
```

### Atom Block

Each atom: 10-character wide fields.

| Columns | Field | Example |
|---------|-------|---------|
| 0-9 | x | -3.7500 |
| 10-19 | y | 2.2500 |
| 20-29 | z | 0.0000 |
| 30-33 | Symbol | C |
| 34-37 | Mass diff | 0 |
| 38 | Charge | 0 |

### Bond Block

Each bond: 10-character wide fields.

| Columns | Field | Example |
|---------|-------|---------|
| 0-2 | Atom 1 | 1 |
| 3-5 | Atom 2 | 2 |
| 6-8 | Type | 1 |
| 9 | Stereo | 0 |

Bond types:
- 1 = Single
- 2 = Double
- 3 = Triple
- 4 = Aromatic

### Properties Block

After bonds, before M END:

```
M  CHG  <n>
  <atom> <charge>
...
```

Other properties:
- M CHG: Charges
- M RAD: Radicals
- M ISO: Isotopes
- M VAL: Valence

### Example: Ethanol

```
  Ethanol

  4  3  0  0  0  0  0  0  0  0999V2000
 -3.7500    2.2500     0.0000C   0.0000  0.0000  0.0000  0  0  0  0  0  0  0  0  0  0  0  0
 -2.6250    2.2500     0.0000C   0.0000  0.0000  0.0000  0  0  0  0  0  0  0  0  0  0  0  0
 -1.5000    2.2500     0.0000O   0.0000  0.0000  0.0000  0  0  0  0  0  0  0  0  0  0  0  0
 -0.7500    1.5000     0.0000H   0.0000  0.0000  0.0000  0  0  0  0  0  0  0  0  0  0  0  0
   1  2  1  0
   2  3  1  0
   3  4  1  0
M  END
```

## MOL V3000 Format

### Structure

```
<header>
<M  V30BEGIN ATOMS>
<M  V30 atoms>
<M  V30END ATOMS>
<M  V30BEGIN BONDS>
<M  V30 bonds>
<M  V30END BONDS>
[collections]
M  END
```

### Counts Line

```
0  0  0  0  0  0  0  0999 V3000
```

### Atom Format

M  V30 <id> <element> <x> <y> <z> ...

```
M  V30 1 C -0.7140 1.4280 0.0000
M  V30 2 C 0.7140 1.4280 0.0000
```

### Bond Format

M  V30 <id> <atom1> <atom2> <type>

```
M  V30 1 1 2 2
```

### Example: Benzene (V3000)

```
  benzene
  None
  2D structure

  0  0  0  0  0  0  0  0999 V3000
M  V2000, 6 atoms, 6 bonds
M  V30BEGIN ATOMS
M  V30 1 C -0.7140 1.4280 0.0000
M  V30 2 C 0.7140 1.4280 0.0000
M  V30 3 C 1.4280 0.0000 0.0000
M  V30 4 C 0.7140 -1.4280 0.0000
M  V30 5 C -0.7140 -1.4280 0.0000
M  V30 6 C -1.4280 0.0000 0.0000
M  V30END ATOMS
M  V30BEGIN BONDS
M  V30 1 1 2 2
M  V30 2 2 3 2
M  V30 3 3 4 2
M  V30 4 4 5 2
M  V30 5 5 6 2
M  V30 6 6 1 2
M  V30END BONDS
M  END
```

## SDfile Format

Multiple molecules in one file.

### Structure

Each molecule:

```
<MOL block>
>  <data>
...
$$$$
```

### Data Fields

After M END, before $$$$:

```
>  <tag name>
<value>
```

## Parsing Notes

1. Whitespace-padded fixed-width format (V2000)
2. V3000 uses whitespace-separated tokens
3. Charges stored in M CHG lines, not directly in atoms
4. Isotopes in M ISO lines (mass difference from natural)
5. Radicals in M RAD lines
6. Aromatic bonds use type 4 (not separate flag)

## Element Symbols

Standard elements: H, Li, Be, B, C, N, O, F, Na, Mg, Al, Si, P, S, Cl, K, Ca, etc.

Extended: D (deuterium), R (pseudo/fragment)

## References

- Daylight Theory: MOL file format
- MDL SDF: SDfile format
- InChI Technical Manual