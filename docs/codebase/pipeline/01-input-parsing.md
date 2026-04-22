# Input Parsing Step

**Pipeline Step:** 01 - Input Parsing
**Analysis Date:** 2026-04-22

## Overview

The Input Parsing step is the first processing stage in the InChI generation pipeline. This step accepts molecular structure data in various input formats (primarily MDL MOL files, with support for SD files and InChI strings) and converts them into the internal `inp_ATOM` representation that the InChI library uses for all subsequent processing.

### What This Step Does

The Input Parsing step performs three primary operations:

1. **Format Recognition and Reading**: Detects whether the input is a MOL file (V2000 or V3000 format), an SD file, or an InChI string. The MOL file parser in `mol_fmt1.c` handles header reading, counts line parsing, atom blocks, and bond blocks. The V3000 extended format is handled in `mol_fmt3.c` and `mol_fmt4.c`.

2. **Data Extraction**: Extracts all chemical information from the input format including: element symbols, atom numbers, bond connections and types, atomic charges, radical designations, isotopic mass differences, stereo information (both atomic and bond stereo), 3D coordinates, and polymer/sgroup data for special molecular representations.

3. **Internal Structure Creation**: Converts the format-specific data structures into the canonical internal `inp_ATOM` array structure defined in `inpdef.h`. This creates the foundational data representation used throughout the rest of the pipeline.

### Why It's Needed

The InChI algorithm requires a normalized internal representation to properly process chemical structures. External formats like MDL MOL files contain many equivalent representations of the same chemical structure (different atom ordering, implicit hydrogens, valence conventions, etc.). The Input Parsing step standardizes this input into the internal `inp_ATOM` structure which serves as the single source of truth for all subsequent pipeline stages.

### Position in Pipeline

```
[Input Format] → [Input Parsing] → [Normalization] → [Canonization] → [InChI String]
                    (Step 01)       (Step 02)        (Step 03)         (Output)
```

Input Parsing is the gateway to the entire InChI processing pipeline. Its output (`inp_ATOM` array) is the input to Step 02 (Normalization) where chemical equivalence, tautomer handling, and hydrogen processing occur.

## IUPAC Rules and Standards

The InChI library adheres to established IUPAC (International Union of Pure and Applied Chemistry) standards for chemical identifier generation. Understanding these foundational standards is essential for correctly interpreting how the Input Parsing step processes molecular structures.

### MDL Format Standards

The InChI library accepts molecular structure data primarily in MDL CTfile formats, which are industry-standard file formats developed by MDL Information Systems (now BIOVIA). The two supported versions are:

- **MDL MOL File V2000**: The traditional fixed-width format introduced in 1989, supporting up to 255 atoms and 255 bonds per molecule. This format uses a counts line that specifies atom and bond counts, followed by atom blocks (with element symbols in columns 31-33) and bond blocks. V2000 remains widely supported across chemical software and is the default format for backward compatibility.

- **MDL MOL File V3000**: The extended format introduced in 1999 to address V2000 limitations. V3000 uses a key-value syntax (lines beginning with "M  V30") and supports unlimited atoms and bonds, polymers, stereogenic centers, 3D constraints, and molecular collections. The V3000 parser in `mol_fmt3.c` and `mol_fmt4.c` handles these extended features.

Both formats encode chemical structures using the element symbol system defined by IUPAC, where each element is represented by its standard one- or two-letter atomic symbol (e.g., C for carbon, N for nitrogen, Fe for iron).

### IUPAC Element Rules

The InChI library relies on IUPAC standard element symbols and atomic numbers for chemical identification. The periodic table lookup (performed during the MOL → inp_ATOM conversion in `mol2atom.c`) maps element symbols to their atomic numbers according to IUPAC nomenclature:

- Elements are identified by their official IUPAC symbols (1-3 characters, with the first letter capitalized)
- The `el_number` field in `inp_ATOM` stores the atomic number (Z) from the IUPAC periodic table (6=C, 7=N, 8=O, 26=Fe, etc.)
- The InChI Technical Manual specifies handling of 118 known elements including all stable isotopes and common radioactive isotopes

This IUPAC-compliant element identification ensures interoperability with other chemical informatics systems and guarantees consistent chemical interpretation across different software platforms.

### Standard Valences

Valence handling in InChI follows the IUPAC standard valence conventions defined in Appendix 1 of the InChI Technical Manual. The standard valence table specifies the default bonding capacity for each element:

- Carbon: valence 4 (forms 4 bonds in neutral molecules)
- Nitrogen: valence 3 (primary/secondary) or 5 (quaternary)
- Oxygen: valence 2 (forms 2 bonds)
- Hydrogen: valence 1

The InChI library uses these standard valences to:
1. **Validate input**: Detect potential data errors when explicit valences exceed IUPAC standards
2. **Calculate implicit hydrogens**: When an atom has fewer explicit bonds than its standard valence, the difference is stored as implicit hydrogens in the `num_H` field
3. **Detect aromaticity**: Standard valence rules help distinguish single/double bonds from aromatic bond orders

The `calculate_valences()` function in `mol2atom.c` applies these IUPAC valence rules during structure normalization. When the MOL file specifies an explicit valence that differs from the IUPAC standard, the library preserves this information for subsequent processing.

### Source References

The following authoritative sources document the IUPAC standards and specifications referenced by the InChI library:

1. **InChI Technical Manual** — The primary reference for InChI implementation details, including valence tables, layer definitions, and algorithm specifications. Available from the InChI Trust:
   - https://www.inchi-trust.org/download/104/InChI_TechMan.pdf
   - Appendix 1 contains the complete IUPAC Standard Valence table

2. **IUPAC InChI Project** — Official IUPAC documentation on the International Chemical Identifier:
   - https://www.iupac.org/inchi/
   - Contains historical context, technical specifications, and standardization information

3. **Heller et al. (2015)** — The definitive academic publication describing the InChI identifier:
   - Heller, S.R., McNaught, A., Stein, S., Tchekhovskoi, D., & Pletnev, I.V. (2015). "InChI, the IUPAC International Chemical Identifier". *Journal of Cheminformatics*, 7:23.
   - https://doi.org/10.1186/s13321-015-0068-4
   - Describes the InChI algorithm, structure normalization, and canonicalization approaches

These references provide the authoritative foundation for all chemical parsing and processing operations in the InChI library, ensuring compliance with international chemistry standards.

## Input

### Accepted Input Formats

**Primary Format: MDL MOL File (V2000)**
- Location: `INCHI-1-SRC/INCHI_BASE/src/mol_fmt1.c`, `mol_fmt2.c`
- Structure: Header lines (3), Counts line, Atom block, Bond block, (optional) SGroup block, (optional) Prop block
- Maximum: 255 atoms, 255 bonds in V2000

**Extended Format: MDL MOL File (V3000)**
- Location: `INCHI-1-SRC/INCHI_BASE/src/mol_fmt3.c`, `mol_fmt4.c`
- Supports: Large molecules, polymers, enhanced stereo, 3D constraints, collections
- Maximum: Limited only by memory (`MAX_ATOMS` defined in ichisize.h)

**SD File (Structure-Data File)**
- Multiple MOL records concatenated with `$$$$` delimiters
- Location: Same parsing functions with iteration

**InChI String**
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichiread.c`
- Full InChI syntax parsing (formula, connectivity, stereo, charge, proton layers)

### Key Input Data Structures

**MOL_FMT_DATA** (from `mol_fmt.h`)
```c
typedef struct A_MOL_FMT_DATA {
    MOL_FMT_HEADER_BLOCK hdr;   // Header: name, program, comments
    MOL_FMT_CTAB ctab;          // Connection table
} MOL_FMT_DATA;
```

**MOL_FMT_ATOM** (from `mol_fmt.h` lines 430-492)
```c
typedef struct A_MOL_FMT_ATOM {
    char symbol[ATOM_EL_LEN];    // Element symbol (C, N, O, etc.)
    MOL_COORD x, y, z;        // 3D coordinates
    short mass_difference;   // Isotopic mass difference
    S_CHAR charge;           // Charge (1=+3, 2=+2, 3=+1, 4=doublet, 5=-1, etc.)
    char radical;           // RAD, S (singlet), D (doublet), T (triplet)
    char stereo_parity;     // Stereo configuration
    char valence;          // Explicit valence
    // ... additional fields
} MOL_FMT_ATOM;
```

**MOL_FMT_BOND** (from `mol_fmt.h` lines 504-545)
```c
typedef struct A_MOL_FMT_BOND {
    short atnum1;    // First atom number
    short atnum2;    // Second atom number
    char bond_type;   // 1=single, 2=double, 3=triple, 4=aromatic
    char bond_stereo; // 0=none, 1=up, 4=either, 6=down
    // ... additional fields for queries/reactivity
} MOL_FMT_BOND;
```

## Output

### Internal Representation: inp_ATOM

The primary output of Input Parsing is an array of `inp_ATOM` structures. This structure (defined in `inpdef.h` lines 141-200) contains all chemical information needed for subsequent processing:

```c
typedef struct tagInputAtom {
    char elname[ATOM_EL_LEN];        // Element name (e.g., "C", "N", "O")
    U_CHAR el_number;             // Periodic table number (6=C, 7=N, 8=O)
    AT_NUMB neighbor[MAXVAL];      // Positions of neighboring atoms (0-indexed)
    AT_NUMB orig_at_number;       // Original atom number from input
    AT_NUMB orig_compt_at_numb;   // Atom number within component
    S_CHAR bond_stereo[MAXVAL];   // Bond stereo (1=up, 4=either, 6=down)
    U_CHAR bond_type[MAXVAL];      // Bond type (1-4: single to aromatic)
    S_CHAR valence;              // Coordination number
    S_CHAR chem_bonds_valence;  // Chemical bond valence
    S_CHAR num_H;              // Implicit hydrogens (including D, T)
    S_CHAR num_iso_H[NUM_H_ISOTOPES]; // Isotopic H: 1H, 2H(D), 3H(T)
    S_CHAR iso_atw_diff;         // Isotopic mass difference
    S_CHAR charge;              // Formal charge
    S_CHAR radical;            // RADICAL_SINGLET/DOUBLET/TRIPLET
    // Stereo 0D data
    S_CHAR bUsed0DParity;      // 0D parity flags
    S_CHAR p_parity;          // Tetrahedral parity
    AT_NUMB p_orig_at_num[MAX_NUM_STEREO_ATOM_NEIGH];
    S_CHAR sb_ord[MAX_NUM_STEREO_BONDS];
    S_CHAR sn_ord[MAX_NUM_STEREO_BONDS];
    S_CHAR sb_parity[MAX_NUM_STEREO_BONDS];
    // Ring system analysis (FIND_RING_SYSTEMS==1)
    S_CHAR bCutVertex;
    AT_NUMB nRingSystem;
    AT_NUMB nNumAtInRingSystem;
    AT_NUMB nBlockSystem;
    double x, y, z;           // 3D coordinates
} inp_ATOM;
```

### sp_ATOM Structure

After normalization (Step 02), atoms are converted to the `sp_ATOM` structure (defined in `extr_ct.h` lines 109-210) which is used for canonical numbering:

```c
typedef struct tagAtom {
    char elname[ATOM_EL_LEN];
    AT_NUMB neighbor[MAXVAL];
    AT_NUMB init_rank;           // Canonically assigned rank
    AT_NUMB orig_at_number;
    U_CHAR bond_type[MAXVAL];
    U_CHAR el_number;
    S_CHAR valence;
    S_CHAR chem_bonds_valence;
    S_CHAR num_H;
    S_CHAR num_iso_H[NUM_H_ISOTOPES];
    S_CHAR cFlags;
    S_CHAR iso_atw_diff;
    AT_ISO_SORT_KEY iso_sort_key; // For isotopic sorting
    S_CHAR charge;
    S_CHAR radical;
    AT_NUMB endpoint;            // Tautomer group ID
    // Stereo data
    AT_NUMB stereo_bond_neighbor[MAX_NUM_STEREO_BONDS];
    S_CHAR stereo_bond_ord[MAX_NUM_STEREO_BONDS];
    S_CHAR stereo_bond_parity[MAX_NUM_STEREO_BONDS];
    S_CHAR parity;              // Tetrahedral parity
} sp_ATOM;
```

### Output Parameters

**From CreateOrigInpDataFromMolfile()** (mol2atom.c lines 108-250):
- `orig_at_data->at`: Pointer to `inp_ATOM` array
- `orig_at_data->num_inp_atoms`: Number of atoms
- `orig_at_data->num_inp_bonds`: Number of bonds
- `orig_at_data->num_dimensions`: Dimensionality (0, 2, or 3)
- `orig_at_data->polymer`: Polymer data if present
- `orig_at_data->v3000`: V3000 extended data if present

## Pseudo-code Algorithm

### Main Parsing Flow

```
FUNCTION ReadInputFile(inp_file, options):
    1. Detect input format
       IF starts with "M  V30" THEN format = V3000
       ELSE IF contains InChI key prefix THEN format = InChI
       ELSE format = V2000

    2. IF format == InChI:
          CALL ParseInChIString()        // ichiread.c
          RETURN inp_ATOM array
       ELSE:
          CALL ReadMolfile()             // mol_fmt1.c
          // Reads header, counts, atoms, bonds
          
    3. IF format == V3000:
          CALL MolfileV3000ReadCTAB()     // mol_fmt3.c
          // Extended V3000 parsing
          
    4. CALL MakeInpAtomsFromMolfileData() // mol2atom.c
       // Convert MOL_FMT_ATOM → inp_ATOM
       
    5. FOR each atom i in molfile:
          a. Copy element symbol → at[i].elname
          b. Lookup periodic number → at[i].el_number
          c. Copy charge, radical, isotope
          d. Process aliases (D→H with iso_atw_diff)
          
    6. FOR each bond j in molfile:
          a. Get atom indices (a1, a2)
          b. Add neighbor: at[a1].neighbor += a2
          c. Add bond_type: at[a1].bond_type += type
          d. Process stereo if present
          
    7. CALL calculate_valences()           // mol2atom.c
       // Verify/calculate implicit H
       
    8. RETURN inp_ATOM array with num_atoms, num_bonds
```

### Detailed Tokenization (V2000 MOL File)

```
FUNCTION MolfileReadAtomsBlock(ctab, inp_file):
    FOR each line in atom block:
        1. Parse fixed-width fields (columns 0-34):
            - cols 0-2:   x coordinate
            - cols 3-9:  y coordinate
            - cols 10-15: z coordinate
            - cols 31-33: element symbol
        2. Validate element symbol (periodic table lookup)
        3. Store in ctab.atoms[atom_index]
        
FUNCTION MolfileReadBondsBlock(ctab, inp_file):
    FOR each line in bond block:
        1. Parse: atnum1, atnum2, bond_type, bond_stereo
        2. Validate atom numbers exist
        3. Validate bond type (1-8)
        4. Store in ctab.bonds[bond_index]
```

### Conversion Algorithm (MOL_FMT_ATOM → inp_ATOM)

```
FUNCTION MakeInpAtomsFromMolfileData(mfdata):
    // mfdata is MOL_FMT_DATA from parsing
    
    num_atoms = mfdata->ctab.n_atoms
    at = CreateInpAtom(num_atoms)     // Allocate inp_ATOM array
    
    // Convert atoms
    FOR i = 0 TO num_atoms - 1:
        at[i].elname = mfdata->ctab.atoms[i].symbol
        at[i].el_number = get_periodic_table_number(at[i].elname)
        at[i].orig_at_number = i + 1
        
        // Isotopic handling
        IF mfdata->ctab.atoms[i].mass_difference != 0:
            at[i].iso_atw_diff = normalize(mass_difference)
        
        // Charge and radical
        at[i].charge = mfdata->ctab.atoms[i].charge
        at[i].radical = mfdata->ctab.atoms[i].radical
        
        // Alias handling: D → H (iso=2), T → H (iso=3)
        IF at[i].elname == "D" AND at[i].iso_atw_diff == 0:
            at[i].elname = "H"
            at[i].iso_atw_diff = 2
        // Similar for T → H (iso=3)
        
    // Convert bonds
    FOR each bond in mfdata->ctab.bonds:
        a1 = bond.atnum1 - 1      // Convert to 0-indexed
        a2 = bond.atnum2 - 1
        at[a1].neighbor[valence++] = a2
        at[a1].bond_type[bond_idx] = bond.bond_type
        
        // Bond stereo: 1=up, 4=either, 6=down
        at[a1].bond_stereo[bond_idx] = bond.bond_stereo
        
    RETURN at, num_atoms, num_bonds
```

## Examples

### Sample MOL File Input (V2000)

```
     RDKit          3D molblock
  -OEChem -16210103062D

  4  3  0  0  0  0  0  0  0  0999 V2000
   -0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2100    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.8817    1.0895    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    2.0123   -0.7126    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
  2  3  2  0
  1  4  1  0
M  END
```

### Resulting inp_ATOM Structure

For the acetone example above, the resulting `inp_ATOM` array (4 atoms) would be:

```c
// Atom 0: C ( carbonyl carbon)
inp_ATOM[0] = {
    .elname = "C",
    .el_number = 6,
    .neighbor = {1, 2, 3},    // bonded to C2, O3, C4
    .bond_type = {1, 2, 1},   // single, double, single
    .bond_stereo = {0, 0, 0},
    .orig_at_number = 1,
    .valence = 3,
    .chem_bonds_valence = 4,  // 1+2+1
    .num_H = 0,               // no implicit H on carbonyl C
    .charge = 0,
    .radical = 0,
    .iso_atw_diff = 0,
    .x = 0.0, .y = 0.0, .z = 0.0
};

// Atom 1: C ( methyl carbon)
inp_ATOM[1] = {
    .elname = "C",
    .el_number = 6,
    .neighbor = {0},           // bonded to C1
    .bond_type = {1},
    .orig_at_number = 2,
    .valence = 1,
    .chem_bonds_valence = 1,
    .num_H = 3,               // CH3: 3 implicit hydrogens
    .charge = 0,
    .radical = 0,
    .iso_atw_diff = 0,
    .x = 1.21, .y = 0.0, .z = 0.0
};

// Atom 2: O ( carbonyl oxygen)
inp_ATOM[2] = {
    .elname = "O",
    .el_number = 8,
    .neighbor = {0},           // bonded to C1
    .bond_type = {2},          // double bond
    .orig_at_number = 3,
    .valence = 1,
    .chem_bonds_valence = 2,
    .num_H = 0,
    .charge = 0,
    .radical = 0,
    .iso_atw_diff = 0,
    .x = 1.8817, .y = 1.0895, .z = 0.0
};

// Atom 3: C ( methyl carbon)
inp_ATOM[3] = {
    .elname = "C",
    .el_number = 6,
    .neighbor = {0},           // bonded to C1
    .bond_type = {1},
    .orig_at_number = 4,
    .valence = 1,
    .chem_bonds_valence = 1,
    .num_H = 3,               // CH3: 3 implicit hydrogens
    .charge = 0,
    .radical = 0,
    .iso_atw_diff = 0,
    .x = 2.0123, .y = -0.7126, .z = 0.0
};
```

### InChI String Input Example

Input: `InChI=1S/C3H6O/c1-3(2)4/h1-2H2`

Parsed output creates equivalent `inp_ATOM` representation:
- Formula layer: C3H6O
- Connection table: 3 carbons connected, oxygen attached
- Hydrogen count: 6 total (implicit + explicit)

## Key Source Files

| File | Purpose |
|------|---------|
| `mol_fmt1.c` | MOL file V2000 parsing - main entry |
| `mol_fmt2.c` | MOL file utility functions |
| `mol_fmt3.c` | MOL file V3000 parsing |
| `mol_fmt4.c` | V3000 SGroups, collections |
| `mol2atom.c` | MOL → inp_ATOM conversion |
| `ichiread.c` | InChI string parsing |
| `inpdef.h` | `inp_ATOM` structure definition |
| `mol_fmt.h` | MOL format structures |
| `extr_ct.h` | `sp_ATOM` structure definition |

---

*Pipeline documentation: Input Parsing step analyzed 2026-04-22*