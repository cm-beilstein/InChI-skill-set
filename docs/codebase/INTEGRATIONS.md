# External Integrations

**Analysis Date:** 2026-04-22

## Overview

InChI is a chemistry-specific identifier system with limited external dependencies. It primarily operates as a standalone library and command-line tool, with optional integrations for enhanced functionality.

## File Formats Handled

### Input Formats

| Format | Versions | Support | Files |
|--------|----------|---------|-------|
| **MOL/SDF** | V2000, V3000 | Native | `mol_fmt1.c`, `mol_fmt2.c`, `mol_fmt3.c`, `mol_fmt4.c` |
| **InChI** | 1.0 | Native | `readinch.c` |
| **Plain text** | - | Native | `util.c` |

**Key Implementation:**
- `INCHI-1-SRC/INCHI_BASE/src/mol_fmt.h` - MOL file format definitions
- `INCHI-1-SRC/INCHI_BASE/src/readinch.h` - InChI parsing
- Reference: A.Dalby et al, J. Chem. Inf. Comput. Sci., 1992, 32, 244-255

### Output Formats

| Format | Description | Implementation |
|--------|-------------|----------------|
| **InChI** | Human-readable identifier | Core algorithms |
| **InChIKey** | 27-character hash | `ikey_base26.c`, `ikey_dll.c` |
| **MOL/SDF** | Structure representation | `ichimake.c` |
| **Auxiliary Info** | Metadata (coordinates, etc.) | `ichiprt*.c` |

## Chemical Structure Processing

### Molecular Analysis

- **Atom typing** - Element identification, isotope handling
- **Bond perception** - Connection table generation
- **Stereochemistry** - 2D/3D stereo, chiral centers
- **Tautomerism** - Mobile hydrogen detection
- **Ring detection** - Cycle finding algorithms (`ring_detection.c`)
- **Aromaticity** - Aromatic system detection

### InChI Layers Generated

The InChI identifier consists of 9 layers. Each layer uses a **distinct prefix character**:

| Layer | Prefix | Description |
|-------|--------|-------------|
| Formula | `/f` | Molecular formula (e.g., `C6H6`) |
| Connectivity | `/c` | Atom connections (obligatory, starts after formula) |
| Charge | `/q` | Proton charges |
| Proton | `/p` | Mobile proton status |
| Mobile-H | `/m` | Mobile hydrogen (tautomerism) |
| Fixed-H | `/h` | Fixed hydrogen atoms |
| Isotope | `/i` | Isotopic composition |
| Stereo (tet) | `/s` | Tetrahedral stereochemistry |
| Stereo (geo) | `/t` | Geometric (cis/trans) stereochemistry |
| Reconnected | `/r` | Metal reconnection |

**Note:** Connectivity (`/c`) is obligatory and implicit — it's the main layer after formula, not prefixed with `c` in output (only formula layers use explicit `/` prefixes). Stereo uses both `/s` (tetrahedral) and `/t` (geometric) prefixes.

Example format:
```
InChI=1S/C6H6/c1-2-4-6-5-3/h1-6H
│       ││ │ │ │ │ └── Fixed-H layer
│       ││ │ │ │ └── Mobile-H layer
│       ││ │ │ └── Stereo (tetrahedral)
│       ││ │ └── Isotope
│       ││ └── Charge
│       │└── Connectivity (implicit)
└── Formula
```

## Command-Line Interface

### Executable: `inchi-1`

**Location:** `INCHI-1-SRC/INCHI_EXE/inchi-1/src/main.c`

**Usage:**
```bash
inchi-1 [options] <input_file> [output_file]
```

**Input Options:**
- `-MOL` - MOL file input (default)
- `-SDF` - SDfile input
- `-InChI` - InChI to structure conversion

**Output Options:**
- `-OutputSDF` - Output as MOL/SDF
- `-AUX` - Include auxiliary information
- `-Hash` - Output InChIKey

**Processing Options:**
- `-FixedH` - Fixed H layer
- `-RecMet` - Metal reconnection
- `-KET/15T` - Tautomerism (experimental)
- `-Polymers105` - Polymer support (legacy/experimental)

### Full Option List

Available via `--help` or documented in `INCHI-1-DOC/InChI_UserGuide.md`

## Library API (libinchi)

### C API

**Public Header:** `INCHI-1-SRC/INCHI_BASE/src/inchi_api.h` (1416 lines)

**Core Functions:**
```c
int GetInchiFromMolfile(const char *molfile,
                         inchi_Output *inchi_Out,
                         const char *options);
                         
int GetInchiFromInchi(const char *inchi,
                      inchi_Output *inchi_Out,
                      const char *options);

char *GetInchiKeyFromInchi(const char *inchi);
```

**Data Structures:**
- `inchi_Atom` - Atom representation
- `inchi_Bond` - Bond representation
- `inchi_Output` - InChI output container
- `INCHISTERMOPS` - Processing options

### Extended API (IXA)

**Header:** `INCHI-1-SRC/INCHI_BASE/src/ixa.h`

Provides low-level building block access:
- `ixa_read_inchi.c` - Parse InChI strings
- `ixa_mol.c` - Molecule construction
- `ixa_builder.c` - Structure builder
- `ixa_inchikey_builder.c` - InChIKey generation

### DLL Exports

**Windows:** `INCHI-1-SRC/INCHI_API/libinchi/src/inchi_dll*.c`
- `inchi_dll_a.c` / `inchi_dll_b.c` - API implementations
- `inchi_dll_main.c` - Entry points

## Hashing

### SHA-256

**Implementation:** Internal (`INCHI-1-SRC/INCHI_BASE/src/sha2.c`)

- Used for InChIKey generation
- Based on standard SHA-2 algorithm
- 256-bit output, mapped to A-Z alphabet (Base-26)

### InChIKey Structure

```
XXXXXXXXXXXXX-XXXXXXXXXX-X
|      |        |
|      |        +-- Protonation indicator
|      +----------- Connection layer hash
+------------------ Formula layer hash
```

## Optional Integrations

### Intel Threading Building Blocks (oneTBB)

**Location:** `INCHI-1-SRC/INCHI_API/tbb/`

**Purpose:** Optional memory allocator for threading
- Header: `tbbmalloc_proxy.h`
- Not used in official releases
- Requires separate installation

**Note:** Pre-compiled binaries do NOT include oneTBB

### Bounds-Checking Functions

**Library:** safeclib or equivalent

**Purpose:** C11 Annex K security functions
- Enabled via `bcf_s.h`
- Optional enhancement

### RDKit (Testing)

**Purpose:** Validation in invariance tests
- Used in `INCHI-1-TEST/tests/test_library/`
- Not required for core functionality

## Build Integration

### CMake Integration

```cmake
cmake -B build -S INCHI-1-SRC/INCHI_EXE/inchi-1/src
cmake --build build
```

### Make Integration

```bash
cd INCHI-1-SRC/INCHI_EXE/inchi-1/gcc
make -f makefile
```

### Visual Studio Integration

Solutions in `INCHI-1-SRC/INCHI_EXE/inchi-1/vc14/`

## Test Infrastructure

### Python Test Suite

**Framework:** pytest
**Dependencies:** pydantic, pytest, (optional: RDKit)

**Test Types:**
- Executable tests: `test_executable/`
- API tests: `test_library/`
- Unit tests: `test_unit/` (C++ googletest)
- Meta tests: `test_meta/`

### Running Tests

```bash
# Python tests
pytest INCHI-1-TEST/tests/test_executable

# C++ unit tests
cd CMake_build && ctest

# Regression tests
python INCHI-1-TEST/tests/test_library/inchi_tests/run_tests.py
```

## External Resources

### Documentation

- **User Guide:** `INCHI-1-DOC/UserGuide/InChI_UserGuide.md`
- **API Reference:** `INCHI-1-DOC/APIReference/InChI_API_Reference.md`
- **Doxygen:** Auto-generated at https://iupac-inchi.github.io/InChI/

### Standards

- InChI standard: IUPAC-developed
- InChI Trust: Standards body
- MIT License: Open source

### Database Integration

InChI is used by major chemical databases:
- PubChem
- ChemSpider
- ChEMBL
- ZINC
- NPD (National PD)

---

*Integration audit: 2026-04-22*