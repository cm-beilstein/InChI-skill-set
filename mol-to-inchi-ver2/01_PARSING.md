# Step 1: MOL File Parsing

**Input:** MDL MOL file (V2000 or V3000 format)
**Output:** Internal atom array with element symbols, coordinates, bonds

> **CRITICAL:** Implement the parser yourself. Do NOT use OpenBabel, RDKit, CDK, or any chemistry library to parse MOL files. Write your own parser following this specification.

## MOL V2000 Format

```
Line 1:   Molecule name (44 chars max)
Line 2:   Program/source info
Line 3:   Comments (optional)
Line 4:   Counts line: "aaa bbb lll fff ccc sss xxx rrr ppp nnn V2000"
         - aaa = number of atoms (001-999)
         - bbb = number of bonds
         - ccc = chiral flag (0 or 1)
Lines 5+: Atom block - one line per atom:
         xxxxx.xxxxx yyyyy.yyyyy zzzzz.zzzzz SCc v
         - cols 0-9:   x coordinate
         - cols 10-19: y coordinate  
         - cols 20-29: z coordinate
         - cols 31-33: element symbol (1-3 chars)
         - cols 34-35: mass difference (-5 to +5)
         - cols 36-37: charge (0=none, 1=+3, 2=+2, 3=+1, 4=-1, 5=-2, 6=-3)
         - cols 38-39: stereo parity
         - cols 40-41: H count + 1
         - cols 42-43: valence
Bonds:    a1 a2 type stereo topo react
         - a1, a2 = atom numbers (1-based)
         - type: 1=single, 2=double, 3=triple, 4=aromatic
         - stereo: 0=none, 1=up, 6=down
M  END   (terminator)
```

## MOL V3000 Format

```
Lines 1-3: Same header
Line 4:    "V3000 aaabbb ccc ddd e"
M  V30 BEGIN CTAB
M  V30 COUNTS nAtoms nBonds nSgroups n3D nCollections
M  V30 BEGIN ATOM
M  V30 index symbol x y z aamap [key=value ...]
...
M  V30 END ATOM
M  V30 BEGIN BOND
M  V30 index type a1 a2 [CFG=value] [TOPO=value]
...
M  V30 END BOND
M  V30 END CTAB
M  END
```

## Parsing Algorithm

```
function parse_mol_file(filepath):
    lines = read_all_lines(filepath)
    
    # Detect format
    if lines[3].startswith("V3000"):
        return parse_v3000(lines)
    else:
        return parse_v2000(lines)

function parse_v2000(lines):
    atoms = []
    bonds = []
    
    # Parse counts line
    counts = lines[3].split()
    num_atoms = int(counts[0])
    num_bonds = int(counts[1])
    
    # Parse atoms (lines 4 to 4+num_atoms-1)
    for i in range(num_atoms):
        line = lines[4 + i]
        atom = {
            'symbol':    strip(line[31:34]),
            'x':       float(line[0:10]),
            'y':       float(line[10:20]),
            'z':       float(line[20:30]),
            'mass_diff': int(line[34:36]) if line[34:36].strip() else 0,
            'charge':   int(line[36:38]) if line[36:38].strip() else 0,
            'valence': int(line[42:44]) if line[42:44].strip() else 0,
        }
        atoms.append(atom)
    
    # Parse bonds
    atom_start = 4 + num_atoms
    for i in range(num_bonds):
        line = lines[atom_start + i]
        parts = line.split()
        bond = {
            'a1':     int(parts[0]),
            'a2':     int(parts[1]),
            'type':   int(parts[2]),
            'stereo': int(parts[3]) if len(parts) > 3 else 0,
        }
        bonds.append(bond)
    
    return {'atoms': atoms, 'bonds': bonds, 'format': 'V2000'}

function parse_v3000(lines):
    # Find ATOM and BOND blocks
    # Parse "M  V30 index symbol x y z" lines
    # Extract key=value properties
    return {'atoms': atoms, 'bonds': bonds, 'format': 'V3000'}
```

## Test Cases

### Test 1: Ethanol (V2000)

File: `01-ethanol.mol`
```
-OEChem-04222603522D

  9  8  0     0  0  0  0  0  0999 V2000
    3.7321    0.2500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    2.8660   -0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    ...
```

Expected atoms count: 9 (2 C, 1 O, 6 H)
Expected bonds count: 8

### Test 2: Benzoic Acid (V2000)

File: `65-85-0-2d.mol`
Expected: 9 atoms, 9 bonds

### Test 3: V3000 Detection

V3000 files have "V3000" at start of line 4 (not in counts like V2000)

## Verification Commands

```
# Verify atom count
grep -E "^.{3,3}[0-9]{3}" molfile | head -1

# Verify format version
grep "V2000\|V3000" molfile
```

## Key Element Symbols

| Symbol | Atomic Number |
|--------|---------------|
| H      | 1             |
| C      | 6             |
| N      | 7             |
| O      | 8             |
| F      | 9             |
| Na     | 11            |
| Mg     | 12            |
| Al     | 13            |
| Si     | 14            |
| P      | 15            |
| S      | 16            |
| Cl     | 17            |
| K      | 19            |
| Ca     | 20            |
| Fe     | 26            |
| Cu     | 29            |
| Zn     | 30            |
| Br     | 35            |
| I      | 53            |

## Next Step

Proceed to `02_ELEMENTS.md` for element processing.