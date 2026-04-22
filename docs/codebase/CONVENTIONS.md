# Coding Conventions

**Analysis Date:** 2026-04-22

## Overview

The InChI project is primarily a C codebase with C++ testing infrastructure. It follows traditional C programming conventions with some modern additions for C++ interoperability. The codebase emphasizes cross-platform compatibility (Windows, Linux) and has been developed over many years by multiple contributors.

---

## Naming Conventions

### Files

**C Source Files:**
- Pattern: Descriptive lowercase with underscores
- Examples: `strutil.c`, `permutation_util.c`, `atropisomers.c`, `ring_detection.c`
- Location: `INCHI-1-SRC/INCHI_BASE/src/`

**C Header Files:**
- Pattern: Same name as corresponding .c file
- Examples: `strutil.h`, `permutation_util.h`, `atropisomers.h`

**C++ Test Files:**
- Pattern: `test_*.cpp` prefix
- Examples: `test_permutation_util.cpp`, `test_enhancedStereo.cpp`, `test_ichiprt1.cpp`
- Location: `INCHI-1-TEST/tests/test_unit/`

### Functions

**C Functions (snake_case):**
- Pattern: Descriptive lowercase with underscores
- Examples: `OrigAtData_Permute`, `CreateOrigInpDataFromMolfile`, `rrand`, `shuffle`, `FreeOrigAtData`
- Verbs for action functions: `Get`, `Set`, `Create`, `Free`, `Alloc`, `Remove`, `Disconnect`

**Internal/Static Functions:**
- Same naming pattern but prefixed with `static` in C, or `static` in C++

### Types

**Structs and Enums (PascalCase):**
- Examples: `INCHI_IOSTREAM`, `ORIG_ATOM_DATA`, `inchi_Output`, `inchi_Radical`
- Location: Header files define types, source files implement

**Typedefs:**
- Pattern: Often end with `_t` or follow PascalCase
- Examples: `AT_NUMB`, `S_CHAR`, `U_CHAR`

### Constants and Macros

**Enum Values (UPPER_CASE):**
- Examples: `INCHI_RADICAL_NONE`, `INCHI_BOND_TYPE_SINGLE`, `INCHI_BOND_STEREO_NONE`

**Define Constants:**
- Pattern: UPPER_CASE with descriptive names
- Examples: `EL_NUMBER_H`, `PERMAXATOMS`, `TARGET_EXE_STANDALONE`, `BYTE(X)`

---

## Code Style

### Formatting

**Indentation:**
- 4 spaces for C/C++ files
- Configured in `.editorconfig`: `indent_size = 4`, `indent_style = space`

**Line Endings:**
- LF (Linux/Unix style)
- Configured in `.editorconfig`: `end_of_line = lf`

**Trailing Whitespace:**
- Trimmed automatically
- Configured in `.editorconfig`: `trim_trailing_whitespace = true`

### File Headers

All source files include a standardized MIT license header:

```c
/*
 * International Chemical Identifier (InChI)
 * Version 1
 * Software version 1.07
 * April 30, 2024
 *
 * MIT License
 *
 * Copyright (c) 2024 IUPAC and InChI Trust
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
```

### C/C++ Interoperability

**extern "C" Blocks:**
All C headers intended to be called from C++ use extern "C" guards:

```c
#ifndef COMPILE_ALL_CPP
#ifdef __cplusplus
extern "C"
{
#endif
#endif

/* Function declarations here */

#ifndef COMPILE_ALL_CPP
#ifdef __cplusplus
}
#endif
#endif
```

### Header Guards

Pattern: `#ifndef _NAME_H_` / `#define _NAME_H_` / `#endif`

```c
#ifndef _PERMUTATION_UTIL_H_
#define _PERMUTATION_UTIL_H_

/* Header content */

#endif // _PERMUTATION_UTIL_H_
```

---

## Documentation Standards

### Function Documentation

**Doxygen-style Comments:**
Header files use Doxygen-style documentation:

```c
/**
 * @brief Get the atomic mass object
 *
 * @param elname Element name
 * @return Returns the atomic mass as integer
 */
int get_atomic_mass_from_elname(const char *elname);
```

### Comments

**Block Comments:**
- Use `/* ... */` for multi-line comments

**Inline Comments:**
- Use `/* ... */` for code explanations
- Common in complex algorithms explaining chemistry logic

**FIXME/TODO Comments:**
- Present in codebase indicating technical debt
- Format: `/* FIXME: ... */` or `/* TODO: ... */`

---

## Error Handling

### Return Codes

**Integer Error Codes:**
- Positive values: Success or specific conditions
- Negative values: Errors
- Zero: Neutral/pending states

**Common Patterns:**
```c
int return_code = 0;
return_code = SomeFunction(...);
if (return_code < 0) {
    /* handle error */
}
```

**InChI-Specific Error Codes:**
- Defined in headers like `inchi_api.h`
- Examples: `Error 170`, `Error 190` for specific failure modes

### Memory Management

**Allocation:**
- Use `inchi_malloc()`, `inchi_calloc()`, `inchi_free()` wrappers
- Check for NULL after allocation

```c
void* temp = inchi_malloc(size);
if (temp) /* check before use */
{
    memcpy(temp, ...);
}
```

**Cleanup:**
- Explicit cleanup functions like `FreeOrigAtData()`, `FreeINCHI()`
- Pattern: `Free*` prefix for deallocation functions

### Output Structures

**API Output Patterns:**
Uses `inchi_Output` structure with string fields:
```c
inchi_Output output;
inchi_Output *poutput = &output;
poutput->szLog = nullptr;  /* Explicit NULL setting */
poutput->szMessage = nullptr;
FreeINCHI(poutput);
```

---

## Import Organization

### C Includes

**Order (from test files):**
1. System headers: `<gtest/gtest.h>`, `<stdio.h>`, `<stdlib.h>`
2. C++ library headers: `<fstream>` (for test files)
3. Project headers: `extern "C" { ... }` blocks containing C includes
4. Relative paths: `"../../../INCHI-1-SRC/INCHI_BASE/src/..."`

**Example from test file:**
```cpp
#include <gtest/gtest.h>
#include <fstream>

extern "C"
{
#include "../../../INCHI-1-SRC/INCHI_BASE/src/inpdef.h"
#include "../../../INCHI-1-SRC/INCHI_BASE/src/ichi_io.h"
#include "../../../INCHI-1-SRC/INCHI_BASE/src/ichimain.h"
#include "../../../INCHI-1-SRC/INCHI_BASE/src/permutation_util.h"
}
```

### C Source Includes

**Order:**
1. Standard library headers
2. Platform-specific includes (Windows SDK, etc.)
3. Project internal headers
4. Local headers

---

## Build Configuration

### CMake Standards

**CMakeLists.txt Pattern:**
```cmake
cmake_minimum_required(VERSION 3.21 FATAL_ERROR)
project(InChI C CXX)
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 11)
```

**Compiler Flags:**
- Debug: `-g -O0 -fsanitize=address`
- Release: Default optimization

### Platform-Specific Code

**Preprocessor Guards:**
```c
#ifdef _WIN32
/* Windows-specific code */
#else
/* Unix/Linux-specific code */
#endif
```

---

## Module Design Patterns

### Source Organization

**One-to-One File Mapping:**
- Each .c file typically has a corresponding .h file
- Example: `permutation_util.c` + `permutation_util.h`

**Module Prefix Pattern:**
- Functions in a module often share a prefix
- Example: All functions in `permutation_util.c` relate to `OrigAtData_*` operations

### Test Organization

**Co-located Tests:**
- Test files mirror source file names
- Example: `test_permutation_util.cpp` tests `permutation_util.c`

---

## Best Practices Observed

1. **Consistent Header Licensing:** Every source file has the MIT license header
2. **Cross-Platform Considerations:** Code includes Windows/Unix conditional compilation
3. **Memory Safety:** Explicit NULL checks before pointer dereferencing
4. **Error Propagation:** Functions return error codes that callers can check
5. **Clear Naming:** Function names describe their purpose (verb-object pattern)
6. **Modular Design:** Small, focused functions with single responsibility

---

*Convention analysis: 2026-04-22*
