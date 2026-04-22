# Architecture

**Analysis Date:** 2026-04-22

## Pattern Overview

**Overall:** Layered Chemical Processing Pipeline

The InChI architecture follows a **layered pipeline pattern** where chemical structure data flows through distinct processing stages:
1. **Input** → Parse molecular structure files (MOL/SDF)
2. **Normalization** → Standardize and clean molecular representation
3. ** canonicalization** → Assign unique atom ordering (canonical numbering)
4. **InChI Generation** → Build layer-based identifier
5. **Output** → Serialize as text InChI string or InChIKey

**Key Characteristics:**
- **Public API layer** - Clear interface via `inchi_api.h` for library consumers
- **Internal layers** - Well-separated processing stages with header-defined interfaces
- **No external dependencies** - Pure C implementation, self-contained
- **Memory-conscious design** - Pre-allocated buffers, explicit allocation tracking

## Layers

### Public API Layer (`inchi_api.h`)

- Purpose: Provide stable interface for external programs linking against libinchi
- Location: `INCHI-1-SRC/INCHI_BASE/src/inchi_api.h`
- Contains: Core data structures (`inchi_Atom`, `inchi_Stereo0D`), function prototypes for InChI generation/parsing
- Depends on: Standard C library only
- Used by: All external applications (including `mol2inchi`, `inchi_main` demos, user code)

Key data structures:
```c
typedef struct tagInchiAtom {
    double x, y, z;              // atom coordinates
    AT_NUM neighbor[MAXVAL];   // adjacency list
    S_CHAR bond_type[MAXVAL];   // bond type (single/double/triple)
    S_CHAR bond_stereo[MAXVAL]; // 2D stereo
    char elname[ATOM_EL_LEN];  // element symbol
    // ...
} inchi_Atom;
```

### Input Parsing Layer

- Purpose: Parse various chemical file formats into internal atomic representation
- Location: `INCHI-1-SRC/INCHI_BASE/src/`
- Key files:
  - `readinch.c/.h` - Parse InChI strings back to internal structure
  - `mol_fmt1.c`, `mol_fmt2.c`, `mol_fmt3.c`, `mol_fmt4.c` - Parse MOL file format
  - `ichiread.c` - High-level structure reading orchestrator
- Contains: Tokenizers, field parsers, format validators
- Depends on: API structures

Data flow:
```
MOL/SDF File → mol_fmt*.c (tokenization) → ichiread.c (assembly) → Internal sp_ATOM[]
```

### Molecular Structure Representation

- Purpose: Internal canonical data structures for chemical graphs
- Location: `INCHI-1-SRC/INCHI_BASE/src/`
- Key files:
  - `incomdef.h` - Common definitions (bond types, atom limits)
  - `mode.h` - Processing mode flags
  - `ichi.h` - InChI layer mode flags
  - `ichisize.h` - Size limits (MAX_ATOMS=32766)

Internal atom representation uses `sp_ATOM` (not the public API's `inchi_Atom`):
- Full connectivity information
- Canonical ranking data
- Stereochemistry details
- Tautomer group membership

### Normalization Layer

- Purpose: Standardize chemical representation for canonical processing
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichinorm.c`
- Contains: Remove equivalent representations, standardize pseudoatoms
- Depends on: Input layer, structure representation

Normalization operations:
- Remove duplicate atoms/bonds
- Standardize bond types
- Resolve aromaticity
- Handle stereochemical conventions

### Canonicalization Layer (Core Algorithm)

- Purpose: Generate unique atom ordering - the heart of InChI uniqueness
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichicano.c`, `ichicans.c`
- Contains: Graph traversal, symmetry detection, rank assignment
- Depends on: Normalization layer

The canonicalization algorithm:
1. Compute graph invariants (atom weights, connectivity hashes)
2. Assign initial ranks
3. Resolve symmetry (find equivalent atoms)
4. Iterate until stable ranking
5. Generate canonical ordering

Key functions:
```c
int CandIAtomRank(sCANON_CHAIN *s, ...)       // Main ranking algorithm
int MarkComponentUniquelyOrdered(...)   // Symmetry breaking
int AllCGroupsParity match(...)        // Compare stereochemistry
```

### Stereochemistry Layer

- Purpose: Process 2D/3D stereochemical information
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichister.c`
- Contains: Stereocenter detection, parity calculation, stereobond handling

- Purpose: Handle tautomeric equivalence
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c`
- Contains: Mobile hydrogen detection, tautomer group formation

### Tautomer Processing

- Purpose: Handle prototropic tautomerism (mobile hydrogen)
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c`, `ichirvr*.c` (reher)
- Contains: Tautomer enumeration, ranking, selection
- Depends on: Canonicalization layer

Tautomer handling:
1. Find all movable H positions
2. Generate equivalent tautomers
3. Canonicalize each
4. Select "canonical" tautomer for InChI layer

### Ring and Cycle Detection

- Purpose: Detect and process ring systems
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichiring.c`, `ring_detection.c`
- Contains: Cycle basis computation, ring system labeling

### InChI Assembly Layer

- Purpose: Build final InChI string from canonical data
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichimake.c`
- Contains: Layer generation, string formatting
- Depends on: All processing layers

Generation stages (layer prefixes in parentheses):
```
InChI=1S/C6H6/h1-6H/p+1/s1
        │ │   │    │   │ └── Stereo /s (tetrahedral) or /t (geometric)
        │ │   │    │   └── Isotope /i
        │ │   │    └── Charge /q (protons) and /p (mobile protons)
        │ │   └── Mobile-H /m and Fixed-H /h
        │ └── Connectivity /c (obligatory)
        └── Formula /f (optional)
```

### Output Layer

- Purpose: Serialize InChI to text format
- Location: `INCHI-1-SRC/INCHI_BASE/src/ichiprt*.c`
- Contains: String formatting, InChIKey generation
- Depends on: Assembly layer

Key outputs:
- InChI string (layer-based text)
- InChIKey (hashed representation, 27 chars)
- Auxiliary information (for reconstruction)

### InChIKey Generation

- Purpose: Create compressed hash identifier
- Location: `INCHI-1-SRC/INCHI_BASE/src/ikey_base26.c`
- Uses: SHA-2 hashing, Base26 encoding

## Data Flow

**Main Processing Pipeline:**

1. **Input** - `mol_fmt*.c` parses MOL file
   - Tokenizes SDF/MOL fields
   - Validates element symbols
   - Builds initial atom list

2. **Preprocessing** - `ichiread.c` assembles structure
   - Resolves valence
   - Adds implicit hydrogens
   - Validates 3D coordinates

3. **Normalization** - `ichinorm.c`
   - Removes duplicates
   - Standardizes representation

4. **Tautomer** - `ichitaut.c` + `ichirvr*.c`
   - Identifies mobile H
   - Generates tautomer list

5. **Canonicalization** - `ichicano.c` + `ichicans.c`
   - Computes invariants
   - Assigns ranks
   - Breaks symmetry

6. **Stereo** - `ichister.c`
   - Detects stereocenters
   - Calculates parities

7. **Assembly** - `ichimake.c`
   - Builds layers
   - Formats string

8. **Hash** - `ikey_base26.c`
   - Generates InChIKey

**State Management:**
- Uses C `struct` for all compound data
- Pre-allocated arrays with length tracking
- Explicit memory management via `malloc`/`free`
- Error codes return via `int` (non-zero = error)

## Key Abstractions

**Molecule Representation:**
- Purpose: Encapsulate chemical structure
- Examples: `sp_ATOM[]` array + `num_atoms`
- Pattern: Pre-allocated array with count

**Tautomer List:**
- Purpose: Group equivalent prototropic forms
- Examples: `T_GROUP_INFO` structure
- Pattern: Linked list of alternate forms

**Stereo Container:**
- Purpose: Hold stereochemical data
- Examples: `inchi_Stereo0D` for 0D
- Pattern: Separate from atoms for clarity

**InChI Output Struct:**
- Purpose: Hold generated InChI
- Examples: `INCHI_OUT_CTL`
- Pattern: Single struct with buffer pointers

## Entry Points

**Executable (Command Line):**
- Location: `INCHI-1-SRC/INCHI_EXE/inchi-1/src/main.c`
- Triggers: CLI arguments (`-InChI`, `-Key`, etc.)
- Responsibilities: Parse args, process files, output results

**Library API:**
- Location: `INCHI-1-SRC/INCHI_BASE/src/inchi_api.h`
- Functions:
  - `GetINCHIFromMolfiles()` - Process MOL to InChI
  - `GetINChIFromInChI()` - Parse InChI to structure
  - `InchiToInchiKey()` - Generate InChIKey

**Test Executables:**
- `INCHI-1-SRC/INCHI_API/demos/mol2inchi/src/mol2inchi.c`
- `INCHI-1-SRC/INCHI_API/demos/inchi_main/src/e_ichimain.c`

## Error Handling

**Strategy:** Return code + stored message

**Patterns:**
- Return `0` = success, negative = error
- Error code stored in `STRUCT_DATA.nErrorCode`
- Error message in `pStrErrStruct[]`

Error categories:
```c
typedef enum inp_err_types {
    ok                     // 0
    error_no_memory       // -1
    error_reading_file    // -2
    error_invalid_input  // -3
    // ...
} inp_err_types;
```

## Cross-Cutting Concerns

**Memory:**
- Pre-allocated buffers defined in headers
- Explicit allocation tracking in structures

**IO:**
- Abstract `INCHI_IOSTREAM` for file/stdio
- Supports both file handles and memory buffers

**Validation:**
- Atomic number and valence checks
- Stereochemistry sanity checks
- Bounds checking for arrays

---

*Architecture analysis: 2026-04-22*