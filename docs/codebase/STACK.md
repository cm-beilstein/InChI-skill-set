# Technology Stack

**Analysis Date:** 2026-04-22

## Languages

**Primary:**
- **C** (C99 standard) - Core InChI library and algorithms
- **C++** (C++11 standard) - Some utility components and tests
- **Python** (3.11-3.12) - Test infrastructure and scripts

**Secondary:**
- **Shell scripts** (Bash) - Build and test automation

## Build System

**Primary:**
- **CMake** (3.21+) - Modern cross-platform build system
  - Configuration: `CMakeLists.txt` at project root
  - Build targets: inchi-1 executable, libinchi library, test executables
  - Configured in `INCHI-1-SRC/INCHI_EXE/inchi-1/src/CMakeLists.txt`

**Alternative:**
- **Make** (GNU Makefile) - Legacy build system
  - Files: `makefile` and `makefile32` in target directories
  - Located in: `INCHI-1-SRC/INCHI_EXE/inchi-1/gcc`
  - Auto-detects OS (Linux, macOS, Windows) and compiler (GCC, Clang/LLVM)

**Windows-specific:**
- **Microsoft Visual Studio** (VS 2019/2022)
  - Projects in: `INCHI-1-SRC/INCHI_EXE/inchi-1/vc14`
  - Supports MSVC, Clang/LLVM, Intel oneAPI DPC++

## Compilers

**Supported:**
- **GCC** 4.5+ (64-bit default on Linux/macOS)
- **Clang/LLVM** 8.0+ (32-bit default, macOS native)
- **Microsoft Visual C++** 12.0+ (VS 2013+)
- **Intel oneAPI DPC++/C++** (since v1.07.2)

**Pre-C99 Support:**
- Being phased out starting v1.07.5

## Core Dependencies

**No external dependencies required** - InChI is self-contained with minimal dependencies:

- **Standard C library** - libc, libm
- **Standard C++ library** - libstdc++ (when needed)

**Optional dependencies:**

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| Intel oneTBB | 2021+ | Optional memory allocator for threading | Optional, not used in releases |
| safeclib | latest | C11 bounds-checking functions | Optional, enabled in `bcf_s.h` |

## Testing Frameworks

**Python Testing:**
- **pytest** 8.3.5 - Primary test framework
- **pydantic** 2.11.5 - Data validation in tests

**C++ Testing:**
- **Google Test** (googletest) v1.17.0 - Fetched via CMake FetchContent
  - Used for unit tests in `INCHI-1-TEST/tests/test_unit`

**Chemistry-specific (optional):**
- **RDKit** 2023.9.6 - For invariance tests
- **numpy** <2.0.0 - Required by RDKit

## Source Code Layout

```
INCHI-1-SRC/
├── INCHI_BASE/src/           # Core InChI algorithms (~80 C files)
│   ├── inchi_api.h          # Public API definitions
│   ├── mol_fmt.h            # MOL file format handlers
│   ├── ichi*.c             # Algorithm implementations
│   ├── runichi*.c           # InChI generation
│   ├── ikey*.c             # InChIKey generation
│   ├── sha2.c              # SHA-256 hashing
│   └── ixa.h              # IXA (InChI eXtended API)
├── INCHI_EXE/inchi-1/src/   # CLI executable
├── INCHI_API/
│   ├── libinchi/src/         # Shared library
│   └── demos/              # Example applications
│       ├── inchi_main/     # Using libinchi
│       ├── mol2inchi/      # Mol to InChI conversion
│       └── test_ixa/       # IXA API tests
├── redundant/              # Deprecated/legacy code
└── tbb/                   # Intel TBB (optional)

INCHI-1-TEST/
├── tests/
│   ├── test_unit/           # C++ unit tests (googletest)
│   ├── test_executable/    # pytest functional tests
│   ├── test_library/       # API regression tests
│   └── test_meta/         # Performance/permutation tests
├── src/sdf_pipeline/      # SDF processing utilities
└── pyproject.toml         # Python test dependencies
```

## Configuration

**CMake Configuration:**
- `CMAKE_C_STANDARD` = C99
- `CMAKE_CXX_STANDARD` = C11
- `CMAKE_POSITION_INDEPENDENT_CODE` = ON
- Coverage reporting: Optional via `-DCOVERAGE=ON`

**Build Targets (defined in mode.h):**
- `TARGET_EXE_STANDALONE` - inchi-1 executable
- `TARGET_API_LIB` - libinchi library
- `TARGET_EXE_USING_API` - Executable using API
- `TARGET_LIB_FOR_WINCHI` - GUI library

**Feature Flags:**
- `FIND_RING_SYSTEMS` - Ring detection (default: ON)
- `FIX_DOCANON_RETCODE_RESET_BUG` - Bugfix (default: ON)
- Bounds checking via `bcf_s.h` - Optional C11 Annex K

## Runtime Requirements

**Platforms:**
- Linux (glibc 2.17+, musl)
- macOS (10.15+)
- Windows (10+)
- FreeBSD, OpenBSD, Solaris, AIX

**Memory:**
- Typical: <100MB for single molecule
- Large molecules: Scales with structure size

**Input Formats (built-in):**
- MOL/SDF V2000 and V3000
- Plain text (molecule data)
- InChI string parsing

**Output Formats:**
- InChI string
- InChIKey (27-char hash)
- MOL/SDF

## Development Environment

**Dev Container:**
- `.devcontainer/devcontainer.json` - Pre-configured environment
- Ubuntu-based with all build tools

**CI/CD:**
- GitHub Actions (`.github/workflows/ci.yml`)
- Python 3.12 in containers
- Tests on Ubuntu (glibc) and Alpine (musl)

**Code Quality:**
- Doxygen for API documentation
- Doxygen config: `Doxyfile`

---

*Stack analysis: 2026-04-22*