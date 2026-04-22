# Codebase Structure

**Analysis Date:** 2026-04-22

## Directory Layout

```
[project-root]/
├── INCHI-1-SRC/          # Main source code
│   ├── INCHI_BASE/       # Core library (52 .c, 40+ .h files)
│   ├── INCHI_API/        # API demos and libinchi
│   └── INCHI_EXE/        # Command-line executable
├── INCHI-1-DOC/          # Documentation (API ref, tech manual)
├── INCHI-1-TEST/         # Test suite (Python + C)
└── CMake_build/          # Build artifacts
```

## Directory Purposes

### INCHI-1-SRC/ (Source Root)

Contains all production code:
- Core library in `INCHI_BASE/src/`
- API demonstrations in `INCHI_API/demos/`
- Standalone executable in `INCHI_EXE/`

### INCHI-1-SRC/INCHI_BASE/src/ (Core Library)

**Purpose:** Main InChI processing library

**Contains:** 52 C source files + 40+ headers implementing all InChI algorithms

**Key files by functional area:**

| Functional Area | Files |
|----------------|-------|
| **API & Entry** | `inchi_api.h` (main API), `ichi.h` (layer flags), `ichimain.h` (main struct) |
| **Input Parsing** | `mol_fmt1.c` - `mol_fmt4.c`, `readinch.c`, `ichiread.c` |
| **Structure** | `incomdef.h` (types), `ichisize.h` (limits), `mode.h` (modes) |
| **Normalization** | `ichinorm.c`, `ichinorm.h` |
| **Canonicalization** | `ichicano.c`, `ichicans.c`, `ichican2.c` |
| **Stereochemistry** | `ichister.c`, `ichister.h` |
| **Tautomers** | `ichitaut.c`, `ichitaut.h` |
| **InChI Assembly** | `ichimake.c`, `ichimake.h` |
| **Output** | `ichiprt1.c`, `ichiprt2.c`, `ichiprt3.c`, `ichi_io.c` |
| **InChIKey** | `ikey_base26.c`, `ikey_base26.h`, `sha2.c` |
| **Reversal (InChI→Structure)** | `ichirvr1.c` - `ichirvr7.c` |
| **Ring Detection** | `ichiring.c`, `ring_detection.c` |
| **Misc Utilities** | `util.c`, `strutil.c`, `ichierr.c`, `permutation_util.c` |

**Key headers:**
- `inchi_api.h` - Public API structures and functions (1416 lines)
- `ichi.h` - InChI mode flags and layer definitions
- `incomdef.h` - Common chemical definitions
- `ichisize.h` - Size limits (MAX_ATOMS=32766)
- `mode.h` - Processing mode flags
- `ichimain.h` - Main processing structures

### INCHI-1-SRC/INCHI_API/

**Purpose:** API demonstration programs and library build

**Contains:**
```
INCHI_API/
├── demos/
│   ├── inchi_main/      # Main API demo (e_ichimain.c)
│   ├── mol2inchi/       # MOL to InChI converter
│   └── test_ixa/       # IXA API test
├── libinchi/           # Library build files
└── tbb/                # Threading Building Blocks (optional)
```

### INCHI-1-SRC/INCHI_EXE/inchi-1/

**Purpose:** Standalone command-line executable

**Contains:**
```
INCHI_EXE/inchi-1/
├── src/main.c          # Entry point (226 lines)
├── gcc/               # GCC makefiles
└── vc14/             # Visual Studio 2014 project
```

### INCHI-1-SRC/INCHI_BASE/redundant/

**Purpose:** Deprecated or unused files (historical)

**Contains:** Old auxiliary conversion headers

### INCHI-1-DOC/

**Purpose:** Documentation

**Contains:**
- `InChI_API_Reference.pdf` - API documentation
- `TechMan/InChI_TechMan.pdf` - Technical manual
- `assets/` - Images and diagrams

### INCHI-1-TEST/

**Purpose:** Test suite

**Contains:**
```
INCHI-1-TEST/
├── tests/
│   ├── test_executable/   # CLI tests
│   ├── test_library/      # API tests
│   ├── test_unit/         # Unit tests
│   └── test_meta/         # Meta tests
├── src/                   # Test runner
└── pyproject.toml         # Python test config
```

### CMake_build/

**Purpose:** CMake build output directory

**Contains:** Generated build files and object files

## Key File Locations

### Entry Points

- **CLI executable:** `INCHI-1-SRC/INCHI_EXE/inchi-1/src/main.c` (line 224)
- **Main API:** `INCHI-1-SRC/INCHI_BASE/src/inchi_api.h`
- **Main processing:** `INCHI-1-SRC/INCHI_BASE/src/ichimain.c`

### Configuration

- **Root CMake:** `CMakeLists.txt`
- **API version:** `INCHI-1-SRC/INCHI_BASE/src/ichisize.h` (MAX_ATOMS=32766)

### Core Logic

- **Canonicalization:** `INCHI-1-SRC/INCHI_BASE/src/ichicano.c` (107KB)
- **InChI Assembly:** `INCHI-1-SRC/INCHI_BASE/src/ichimake.c` (217KB)
- **InChIKey:** `INCHI-1-SRC/INCHI_BASE/src/ikey_base26.c` (111KB)
- **MOL parsing:** `INCHI-1-SRC/INCHI_BASE/src/mol_fmt*.c` (split for organization)

### Testing

- **Python tests:** `INCHI-1-TEST/tests/`
- **Test runner:** `INCHI-1-TEST/src/`

## Naming Conventions

### Source Files

- **C implementation:** `module_name.c` (e.g., `ichican2.c`)
- **Header:** `module_name.h` (e.g., `ichican2.h` - usually paired .h for large modules)
- **Pattern:** Prefixed with domain identifier
  - `ichi*` - InChI generation
  - `mol_fmt*` - MOL file format
  - `ichirvr*` - InChI reversal
  - `ikey*` - InChIKey

### Internal Functions

- **Pattern:** Descriptive lowercase with underscores
  - `GetINCHIFromMolfiles()` - Public API
  - `CandIAtomRank()` - Internal canonicalization
  - `MarkComponentUniquelyOrdered()` - Symmetry breaking

### Data Structures

- **Pattern:** `tag` prefix for struct tags in headers
  - `tagInchiAtom` → `inchi_Atom`
  - `tagINCHI_CLOCK`

## Where to Add New Code

### New Feature / Algorithm

- **Implementation:** `INCHI-1-SRC/INCHI_BASE/src/`
- **Naming:** Prefix with relevant domain (`ichican*.c`, `ichister*.c`)
- **Headers:** Add to existing or create new `.h` file

### New File Format Support

- **Location:** New `mol_fmtN.c` in `INCHI-1-SRC/INCHI_BASE/src/`
- **Pattern:** Follow existing `mol_fmt1.c` structure

### New Output Format

- **Location:** `INCHI-1-SRC/INCHI_BASE/src/ichiprt*.c`
- **Pattern:** Add to existing printer modules

### Bug Fix

- **Location:** Same file as bug location
- **Testing:** Add to `INCHI-1-TEST/tests/`

### New Test

- **Unit test:** `INCHI-1-TEST/tests/test_unit/`
- **API test:** `INCHI-1-TEST/tests/test_library/`
- **CLI test:** `INCHI-1-TEST/tests/test_executable/`

## Special Directories

### INCHI-1-SRC/INCHI_BASE/src/tbb/

- **Purpose:** Intel Threading Building Blocks headers (optional)
- **Generated:** No
- **Committed:** Yes (headers only, no library)

### INCHI-1-SRC/INCHI_BASE/redundant/

- **Purpose:** Deprecated code retained for reference
- **Generated:** No
- **Committed:** Yes
- **Note:** Not actively used in builds

### CMake_build/

- **Purpose:** Build artifacts
- **Generated:** Yes (by CMake)
- **Committed:** No (in .gitignore)

### .planning/

- **Purpose:** GSD planning artifacts
- **Generated:** Yes (by GSD workflow)
- **Committed:** Yes

---

*Structure analysis: 2026-04-22*