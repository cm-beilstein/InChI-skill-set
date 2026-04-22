# Testing Patterns

**Analysis Date:** 2026-04-22

## Overview

The InChI project uses a multi-layered testing approach:
1. **Unit Tests (C++)**: Using Google Test (gtest) framework
2. **Executable Tests (Python/pytest)**: Testing the InChI command-line executable
3. **Library Tests (Python/pytest)**: Testing the libinchi library via Python bindings
4. **Meta Tests (Python/pytest)**: Performance and regression testing with database comparisons

---

## Test Framework

### Unit Tests (Google Test)

**Test Runner:**
- Framework: Google Test (gtest) v1.17.0
- Configured via CMake FetchContent
- Integration: `CMakeLists.txt` at root

**CMake Configuration:**
```cmake
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.17.0
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

include(CTest)
include(GoogleTest)
enable_testing()
```

**Test Executable Build:**
- Built as standalone executables from `test_*.cpp` files
- Linked against `gtest_main`, `gmock_main`, `test_dependencies`, `libinchi`

### Python Tests (pytest)

**Configuration:**
- Python version: 3.11 - 3.12
- Framework: pytest 8.3.5
- Configured in `INCHI-1-TEST/pyproject.toml`

**Test Paths:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests/test_executable", "tests/test_meta"]
addopts = "-v"
```

---

## Test File Organization

### Location Pattern

**Unit Tests:**
```
INCHI-1-TEST/tests/test_unit/
├── test_*.cpp          # Source files to test
├── test_*_enhancedStereo.cpp  # Feature-variant tests
├── CMakeLists.txt     # Build configuration
└── fixtures/          # Test data files
    ├── *.sdf
    ├── *.mol
    └── *.sdf.gz
```

**Executable Tests:**
```
INCHI-1-TEST/tests/test_executable/
├── test_*.py          # Test files
├── conftest.py         # Shared fixtures
├── helpers.py         # Helper functions
└── data/              # Test data files
    └── *.sdf.gz
```

**Library Tests:**
```
INCHI-1-TEST/tests/test_library/
├── inchi_tests/       # API test utilities
│   ├── __init__.py
│   ├── inchi_api.py  # Python bindings
│   ├── run_tests.py
│   └── utils.py
├── config/            # Configuration files
└── data/             # Test data
```

### Test File Naming

**Unit Tests:**
- Pattern: `test_<module_name>.cpp` or `test_<module_name>_<feature>.cpp`
- Examples: `test_permutation_util.cpp`, `test_enhancedStereo.cpp`, `test_ichiprt1_enhancedStereo.cpp`

**Executable Tests:**
- Pattern: `test_<feature>.py`
- Examples: `test_io.py`, `test_github_52.py`, `test_organometallics_pubchem.py`

---

## Test Structure (C++ Unit Tests)

### Test Suite Organization

```cpp
#include <gtest/gtest.h>

extern "C"
{
#include "../../../INCHI-1-SRC/INCHI_BASE/src/inpdef.h"
#include "../../../INCHI-1-SRC/INCHI_BASE/src/ichi_io.h"
#include "../../../INCHI-1-SRC/INCHI_BASE/src/ichimain.h"
#include "../../../INCHI-1-SRC/INCHI_BASE/src/permutation_util.h"
}

TEST(test_permutation_util, test_OrigAtData_Permute)
{
    // Arrange: Set up test data
    INCHI_IOSTREAM input_stream;
    const char *molblock = "...";
    inchi_ios_init(&input_stream, INCHI_IOS_TYPE_STRING, nullptr);
    
    // Act: Execute the function under test
    int num_atoms = CreateOrigInpDataFromMolfile(...);
    
    // Assert: Verify results
    ASSERT_EQ(num_atoms, 5);
    
    // Cleanup
    FreeOrigAtData(&atom_data);
}
```

### Assertion Patterns

**Equality Assertions:**
```cpp
ASSERT_EQ(actual, expected);    // Fatal if unequal
EXPECT_EQ(actual, expected);    // Non-fatal if unequal
```

**String Assertions:**
```cpp
EXPECT_STREQ(actual, expected);    // String equality
EXPECT_STRNE(actual, expected);    // String inequality
```

**Pointer Assertions:**
```cpp
EXPECT_NE(ptr, nullptr);
EXPECT_NULLPTR(ptr);
```

### Fixture Usage

**Using GoogleTest Fixtures:**
```cpp
class MyTestFixture : public ::testing::Test {
protected:
    void SetUp() override { /* initialize */ }
    void TearDown() override { /* cleanup */ }
};

TEST_F(MyTestFixture, TestCaseName) {
    // Use fixture resources
}
```

---

## Test Structure (Python Tests)

### pytest Fixtures (conftest.py)

```python
import pytest

@pytest.fixture
def run_inchi_exe():
    """Fixture that provides a callable to run InChI executable."""
    def _run(molfile: str, *options):
        # Execute InChI and return result
        ...
    return _run

@pytest.fixture
def sdf_path():
    return Path(__file__).parent.absolute().joinpath("data/test_io.sdf.gz")
```

### Test Functions

```python
def test_executable_rejects_scsr_extension(molfile_v3000_scsr_extension, run_inchi_exe):
    result = run_inchi_exe(molfile_v3000_scsr_extension)
    assert "Error 190 (no InChI; Unknown element(s): Thr) inp" in result.stderr
```

---

## Mocking

### C++ Unit Tests

**Direct Implementation:**
- No external mocking framework detected
- Tests use real implementation from `test_dependencies` library

**Test Dependencies:**
- Built statically from all C sources in `INCHI-1-SRC/INCHI_BASE/src/`
- Linked to test executables

```cmake
file(GLOB BASE_SOURCES CONFIGURE_DEPENDS
     "${P_BASE}/*.c"
     "${P_BASE}/*.h"
)
add_library(test_dependencies STATIC ${BASE_SOURCES})
target_link_libraries(${test_name} PRIVATE gtest_main gmock_main test_dependencies libinchi)
```

### Python Tests

**Executable Simulation:**
- Tests use actual compiled InChI executable
- Called via subprocess in fixtures

---

## Test Data (Fixtures)

### SDF Molfile Fixtures

**Location:** `INCHI-1-TEST/tests/test_unit/fixtures/`

**File Types:**
- `.sdf` - SDF (Structure-DataFile) format
- `.mol` - MDL Molfile format
- `.sdf.gz` - Compressed SDF files

**Example Molfile Format:**
```
test_mol_2
  Ketcher  1302610202D 1   1.00000     0.00000     0
                                                                         (
 13 12  0  0  0  0  0  0  0  0999 V2000
    2.9420   -4.1000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0     0  0
M  END
```

### Database Regression Data

**Location:** `INCHI-1-TEST/tests/test_library/data/`

**Formats:**
- `.sqlite` - SQLite database for regression reference
- `.sdf.gz` - SDF files with input structures

---

## Running Tests

### C++ Unit Tests

```bash
# Build with CMake
cd CMake_build/full_build
cmake ../..
cmake --build .

# Run all tests
ctest --output-on-failure

# Run specific test
./test_permutation_util

# Run with coverage
cmake -DCOVERAGE=ON ..
make coverage
```

### Python Tests

```bash
# Run all pytest tests
cd INCHI-1-TEST
pytest

# Run specific test file
pytest tests/test_executable/test_io.py

# Run with verbose output
pytest -v
```

### Running Tests via GitHub Actions

**Workflow:** `.github/workflows/ci.yml`

```yaml
- name: Unit Tests
  run: cmake --build build && ctest --output-on-failure

- name: Regression Tests
  run: pytest tests/test_library/
```

---

## Test Coverage

### Coverage Configuration

**CMake Option:**
```cmake
option(COVERAGE "Enable coverage reporting" OFF)

if(COVERAGE)
    add_compile_options(--coverage -O0 -g)
    add_link_options(--coverage)
    add_custom_target(coverage
        COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
        COMMAND find . -name '*.gcno' -exec gcov -b -c {} +
    )
endif()
```

**Coverage Command:**
```bash
cmake -DCOVERAGE=ON ../
make coverage
```

---

## Test Types

### Unit Tests (test_unit/)

**Scope:**
- Individual functions from C modules
- Testing specific InChI generation features
- Testing permutation utilities, stereo handling, molfile parsing

**Examples:**
- `test_permutation_util.cpp` - Atom permutation functions
- `test_enhancedStereo.cpp` - Enhanced stereochemistry handling
- `test_ichiprt1.cpp` - InChI string output formatting
- `test_mol_fmt.cpp` - Molfile format parsing

### Executable Tests (test_executable/)

**Scope:**
- Testing InChI command-line executable
- Error handling for invalid inputs
- Large molecule handling
- V3000 molfile features

**Examples:**
- `test_io.py` - Input/output handling
- `test_github_52.py` - GitHub issue regression tests
- `test_organometallics_pubchem.py` - Organometallic compound handling

### Library Tests (test_library/)

**Scope:**
- Testing Python bindings to libinchi
- API function testing
- Regression testing against known good results

**Test Infrastructure:**
- `inchi_api.py` - Python wrapper for libinchi
- `run_tests.py` - Test runner for API tests

### Meta Tests (test_meta/)

**Scope:**
- Performance benchmarking
- Large-scale regression testing
- Permutation invariance testing with SQLite database

### Invariance Tests

**Purpose:**
- Verify InChI output remains consistent when molecule representation changes
- Test atom ordering doesn't affect output

**Command:**
```bash
pytest tests/test_library/ -k invariance
```

---

## Common Test Patterns

### Molfile Input Testing

```cpp
// Setup molfile input stream
INCHI_IOSTREAM input_stream;
const char *molblock =
    "\n"
    "  InChIV10                                     \n"
    "\n"
    "  5  4  0  0  0  0  0  0  0  0  1 V2000\n"
    "    1.2124    0.0000    0.0000 O   0  0  0     0  0  0  0  0  0\n"
    /* ... more atom data ... */
    "M  END\n"
    "$$$$\n";
inchi_ios_init(&input_stream, INCHI_IOS_TYPE_STRING, nullptr);
inchi_ios_print_nodisplay(&input_stream, molblock);
```

### API Call Testing

```cpp
// Test InChI generation from molfile
char options[] = "-EnhancedStereochemistry";
inchi_Output output;
inchi_Output *poutput = &output;
const char expected_inchi[] = "InChI=1B/...";

EXPECT_EQ(MakeINCHIFromMolfileText(molblock, options, poutput), 0);
EXPECT_STREQ(poutput->szInChI, expected_inchi);

FreeINCHI(poutput);
```

### Error Condition Testing

```python
def test_executable_rejects_scsr_extension(molfile_v3000_scsr_extension, run_inchi_exe):
    result = run_inchi_exe(molfile_v3000_scsr_extension)
    assert "Error 190 (no InChI; Unknown element(s): Thr) inp" in result.stderr
```

---

## Test Maintenance Guidelines

### Adding New Tests

1. **Unit Tests:**
   - Add `test_<module>.cpp` in `INCHI-1-TEST/tests/test_unit/`
   - Use existing `CMakeLists.txt` globs - new tests auto-added

2. **Executable Tests:**
   - Add `test_<feature>.py` in `INCHI-1-TEST/tests/test_executable/`
   - Add fixtures in `conftest.py` as needed

3. **Library Tests:**
   - Add new API test functions in Python
   - Use existing test fixtures

### Test Data Management

- Keep test molfiles small and focused
- Use fixtures directory for shared data
- Use descriptive SDF IDs
- Document test expectations clearly in assertions

---

## Testing Best Practices Observed

1. **Multi-Level Testing:** Combined unit, executable, library, and meta tests
2. **Fixture Reuse:** Shared test fixtures via conftest.py
3. **Clear Assertions:** Specific error message matching in Python tests
4. **Memory Cleanup:** Explicit Free*() calls in C++ tests
5. **Reference Databases:** SQLite for regression testing
6. **Coverage Option:** Optional code coverage with CMake flag
7. **Cross-Platform Build:** CMake for consistent test infrastructure
8. **GitHub Actions Integration:** Automated testing in CI pipeline

---

*Testing analysis: 2026-04-22*