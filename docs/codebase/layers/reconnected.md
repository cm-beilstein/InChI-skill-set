# Reconnected Layer (/r)

**Analysis Date:** 2026-04-22

## Overview

The reconnected layer (`/r`) is an optional layer in the InChI identifier that provides an alternative representation of organometallic compounds where metal-ligand bonds are preserved rather than disconnected. This layer is particularly important for molecular inorganic chemistry and organometallic compounds where preserving the bonding information to metal centers is chemically significant.

### Purpose

In the standard (disconnected) InChI, metal atoms are treated as disconnected from their ligands based on electronegativity differences. A metal (less electronegative) would have its bonds to non-metals broken, creating separate components. However, for many applications—especially in organometallic chemistry—preserving the metal-ligand connectivity is essential for identifying the complete molecular structure.

The reconnected layer solves this by providing a parallel InChI that keeps all metal bonds intact, allowing:
- Organometallic compounds to be identified as single molecular entities
- Metal centers to be associated with their complete ligand shells
- Differentiation between structural isomers that only differ in metal bonding patterns

### When It's Used

The `/r` layer is automatically generated when:
1. The input structure contains metal atoms bonded to organic or inorganic ligands
2. The `RecMet` option is enabled (or the structure is detected to contain metals)

The reconnected structure is stored as a second InChI in the output alongside the standard disconnected InChI.

---

## Output Format

### InChI Layer Structure

The reconnected layer appears as `/r` followed by a formula component:

```
InChI=1S/[formula]/r[formula]
```

**Example:**
```
InChI=1S/Fe.2H2O/h1H2O/rFe.2H2O/h1H2O
```

The structure breakdown:
| Layer | Content | Description |
|-------|---------|-----------|
| `/f` | `Fe.2H2O` | Main formula (disconnected) |
| `/h` | `h1H2O` | Fixed-H layer |
| `/r` | `Fe.2H2O` | Reconnected formula |
| `/r` | `h1H2O` | Reconnected fixed-H |

### Layer Ordering

The `/r` layer appears after the fixed-H layers for both mobile-H and fixed-H variants. The complete InChI with reconnected layer has this structure:

```
1  |/f| /i|/f/i/h |/r| /r
   |  |    |       |   |
   |  |    |       |   +-- reconnected fixed-H (if present)
   |  |    |       +------ reconnected /rFML
   |  |    +-------------- fixed-H mobile-H isotopic
   |  +------------------- fixed-H formula
   +---------------------- version
```

---

## Code Implementation

### Key Source Files

| File | Purpose |
|------|--------|
| `INCHI-1-SRC/INCHI_BASE/src/strutil.c` | Metal disconnection logic (`MolOrgDisconnectMetal`, `MolecularInorganicsPreprocessing`) |
| `INCHI-1-SRC/INCHI_BASE/src/runichi3.c` | Preprocessing and reconnected structure creation |
| `INCHI-1-SRC/INCHI_BASE/src/ichiprt1.c` | Output formatting and `/r` layer generation |
| `INCHI-1-SRC/INCHI_BASE/src/runichi.c` | Main InChI generation with INCHI_REC index |
| `INCHI-1-SRC/INCHI_BASE/src/ichirvr7.c` | Reversing InChI (reconnection to structure) |
| `INCHI-1-SRC/INCHI_BASE/src/ichidrp.h` | INPUT_PARMS with bMolecularInorganicsReconnectedInChI flag |

### Data Structures

**INPUT_PARMS structure** (`ichidrp.h:190`):
```c
int bMolecularInorganicsReconnectedInChI;  /* Custom flag to indicate reconnected InChI requirement */
```

**InChI Index Constants** (`runichi.c`):
```c
#define INCHI_BAS 0  /* Basic/disconnected InChI */
#define INCHI_REC 1  /* Reconnected InChI */
```

**Preprocessed Data Structure** (`runichi3.c`):
The preprocessing creates two parallel structures:
- `prep_inp_data[INCHI_BAS]`: Metal-disconnected structure
- `prep_inp_data[INCHI_REC]`: Original/reconnected structure

### Constants

**InChI Layer Definition** (`ichiprt1.c:320`):
```c
{"/r", "reconnected bond(s) to metal(s) formula", "formula", 0}
```

---

## Metal Disconnection Algorithm

### Overview

The metal disconnection algorithm in `strutil.c` handles two scenarios:

1. **Standard Metal Disconnection**: Based on electronegativity differences
2. **Molecular Inorganics**: More sophisticated rules from Nauman Ullah Khan

### Standard Metal Disconnection

**Function:** `MolOrgDisconnectMetal()` in `strutil.c`

```
Algorithm:
1. Identify metal atoms using is_el_a_metal()
2. For each metal atom:
   a. Check if atom is isolated or has multiple charges -> keep all bonds
   b. Check if atom is part of a metal-metal bond -> keep those bonds
   c. For metal-ligand bonds:
      - Use electronegativity to determine if bond should be broken
      - Process neighbors in reverse order to handle array updates
3. Clear metal valence after disconnection
4. Add positive charge to metal atom
```

### Molecular Inorganics Preprocessing

**Function:** `MolecularInorganicsPreprocessing()` in `strutil.c:6445`

This function implements a more chemically accurate approach:

```
Algorithm:
1. Identify all metal atoms (periodic numbers 3-118 excluding metalloids)
2. For each metal atom M:
   a. Check if M has a path to ANY other metal
      - If yes -> keep all bonds for M (cluster compound)
   b. Check if M is part of a ring system containing metals
      - If yes -> keep all bonds for M
   c. For each neighbor N:
      - If bond order > 1 OR N is metal -> keep bond
      - Otherwise: lookup electronegativity in binaryArrayMolecularInorganics
        * Value = 1 -> disconnect bond
        * Value = 0 -> keep bond
3. Update neighbor lists after disconnection
```

### Binary Electronegativity Array

**Location:** `strutil.c:6259-6378`

A 118x118 binary array where:
- `binaryArrayMolecularInorganics[i][j] = 1`: Bond between elements i and j should be disconnected
- `binaryArrayMolecularInorganics[i][j] = 0`: Bond should be kept

The array encodes electronegativity differences using the Pauling scale:
- Metal-nonmetal bonds: typically disconnected (value = 1)
- Metal-metal bonds: typically kept (value = 0)
- Nonmetal-nonmetal bonds: typically kept (value = 0)

### Metal Detection

**Function:** `is_el_a_metal()` in `util.c:656`

Returns 1 if the element (by periodic number) is a metal:
- Periodic numbers 3-5, 13, 21-32, 48-52, 72-84, 104-118 (excluding metalloids B, Si, Ge, As, Sb, Te, Po)

---

## Pseudo-code: Metal Atom Reconnection

### Creating Reconnected Structure

```
function CreateReconnectedStructure(orig_at_data, ip, prep_inp_data):
    
    # Copy original structure as reconnected (prep_inp_data[INCHI_REC])
    DuplicateStructure(prep_inp_data[INCHI_REC], orig_at_data)
    
    # Create disconnected structure (prep_inp_data[INCHI_BAS])
    DuplicateStructure(prep_inp_data[INCHI_BAS], orig_at_data)
    
    # Apply metal disconnection to prep_inp_data[INCHI_BAS] only
    if ip->bMolecularInorganics:
        MolecularInorganicsPreprocessing(prep_inp_data[INCHI_BAS], ip)
    else:
        for each atom in prep_inp_data[INCHI_BAS].at:
            if is_el_a_metal(atom):
                MolOrgDisconnectMetal(prep_inp_data[INCHI_BAS], atom)
    
    # Return 2 if reconnected structure differs from disconnected
    return (num_components[INCHI_REC] != num_components[INCHI_BAS]) ? 2 : 1
```

### Generating /r Layer Output

```
function OutputReconnectedLayer(pINChI, io):
    
    # Check if reconnected InChI exists
    if pINChI[INCHI_REC] is NULL or num_components[INCHI_REC] == 0:
        return  # No reconnected layer needed
    
    # Output reconnected formula layer
    PrintFormulaLayer(pINChI[INCHI_REC], io, "/r")
    
    # Output reconnected fixed-H if applicable
    if HasFixedH(pINChI[INCHI_REC]):
        PrintFixedHLayer(pINChI[INCHI_REC], io, "/r/h")
```

---

## Examples

### Example 1: Iron(II) Sulfate Tetrahydrate

**Input Structure:**
```
Fe(2+) with 4 water molecules and sulfate ion
```

**Standard InChI (disconnected):**
```
InChI=1S/Fe.2H2O/h1H2O
```
- Iron is disconnected from sulfate
- Creates separate components: Fe and sulfate

**InChI with Reconnected Layer:**
```
InChI=1S/Fe.2H2O/h1H2O/rFe.2H2O/h1H2O
```
- `/rFe.2H2O` - Reconnected formula preserves Fe-sulfate bond
- `/r/h1H2O` - Reconnected fixed-H layer

### Example 2: Sodium Chloride

**Input:** NaCl (sodium chloride crystal)

**Standard InChI:**
```
InChI=1S/ClH.Na/h1H;/q+1;-1
```

**With Reconnected:**
- Metal is Na (very electropositive)
- Salt disconnection breaks the ionic bond
- Reconnected layer preserves Na-Cl association

### Example 3: Copper(II) Complex

**Input:** [Cu(NH3)4]2+

**Standard InChI:**
- Creates disconnected structure with Cu as separate component

**With Reconnected:**
- Preserves Cu-N bonds in coordination complex
- Proper representation of the coordination compound

---

## Configuration Options

### Command Line Options

| Option | Effect |
|-------|-------|
| `-r` or `-RecMet` | Generate reconnected InChI layer |
| `-MO` | Enable molecular inorganics mode |

### API Configuration

**INPUT_PARMS structure:**
```c
bMolecularInorganics = 1;           // Enable molecular inorganics processing
bMolecularInorganicsReconnectedInChI = 1;  // Generate reconnected layer
```

---

## Integration with Other Layers

### Layer Dependencies

The `/r` layer is generated independently but shares:
- `/f` formula layer structure
- `/h` fixed-H layer structure
- Stereochemistry layers (if present)

### Layer Conflict Handling

When a structure has both mobile-H tautomerism and metal reconnection:
1. Mobile-H is processed first (creating `/h` layer variants)
2. Metal reconnection is processed on each tautomeric form
3. Resulting InChI includes both sets of `/r` layers

---

## Implementation Notes

### Performance Considerations

- Metal disconnection requires O(n) traversal where n = number of atoms
- Binary array lookup is O(1)
- Neighbor list updates are O(m) per disconnection where m = valence

### Edge Cases

1. **Isolated Metal Atom**: No disconnection, keep all bonds
2. **Multiple Charges on Metal**: No disconnection
3. **Metal-Metal Clusters**: Keep all inter-metal bonds
4. **Aromatic Rings with Metals**: Special handling in ring detection
5. **Polymers with Metal Atoms**: Metal detection before polymer processing

### Error Handling

- Failed disconnection: Report warning, continue with original structure
- Memory allocation failure: Fatal error (code 99)
- Invalid metal valence: Adjust and report warning

---

## References

- InChI Technical Manual: Metal disconnection chapter
- IUPAC Recommendations for organometallic InChI
- Source file headers: Nauman Ullah Khan contributions (molecular inorganics)

---

*Reconnected layer documentation: 2026-04-22*