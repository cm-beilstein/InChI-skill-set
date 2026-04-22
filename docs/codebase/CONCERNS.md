# Codebase Concerns

**Analysis Date:** 2026-04-22

## Technical Debt

### Incomplete Atropisomer Support

**Issue:** The atropisomer feature (axial chirality handling) has incomplete implementation in the output generation phase.

**File:** `INCHI-1-SRC/INCHI_BASE/src/strutil.c`

**Details:** Lines 7142-7149 contain explicit TODO comments:
- t-layer parities for atropisomers not fully implemented
- m-layer for atropisomers not implemented
- Enantiomeric vs diastereomeric distinction rules unspecified
- Current implementation simply sets all t-parities to `1` (negative/undefined)

**Impact:** Atropisomeric molecules may not get correct stereochemical representation in generated InChI strings.

**Fix approach:** Complete the t- and m-layer implementation with proper parity assignment rules.

### Memory Management Issues in API

**Issue:** Potential memory allocation issues with atom arrays in the API layer.

**File:** `INCHI-1-SRC/INCHI_API/libinchi/src/inchi_dll_a2.c`

**Details:** Line 2940 contains comment `/* TODO: make a full copy (with allocs) of atom arrays */`. This indicates potential issues with shallow copies vs deep copies of data structures.

**Impact:** May lead to memory corruption or use-after-free bugs when API is used in certain ways.

**Fix approach:** Implement proper deep copy semantics for atom arrays.

### IXA Mol Data Refactoring Needed

**Issue:** Extended molecular input handling needs refactoring.

**File:** `INCHI-1-SRC/INCHI_API/libinchi/src/ixa/ixa_mol.c`

**Details:** Line 2426 contains: `TODO: rewrite/refactor IXA_MOL_SetExtMolDataByInChIExtInput`

**Impact:** The function may have edge cases or memory management issues.

**Fix approach:** Rewrite with proper memory management and edge case handling.

### Extended Input Features Isolation Needed

**Issue:** Extended input feature handling not properly isolated from core logic.

**File:** `INCHI-1-SRC/INCHI_API/libinchi/src/ixa/ixa_builder.c`

**Details:** Line 1390 comments: `/* Extended input features (TODO: replace and isolate) */`

**Impact:** Feature entanglement makes maintenance and testing harder.

**Fix approach:** Isolate into separate modules with clean interfaces.

---

## Known Limitations

### V3000 MOL File Limitations

**Issue:** Incomplete handling of V3000 MOL file features.

**Files:**
- `INCHI-1-SRC/INCHI_BASE/src/mol_fmt3.c`

**Details:**
- Line 255: `TODO: treat strings with spaces in double quotes`
- Line 408: `TODO: treat strings with spaces in double quotes`
- Line 937: `TODO: treat possibly long V3000 atom names` - Currently limited to 6 characters
- Line 1398: `TODO: treat new bond types 9 10` - Two newer bond types from V3000 spec not handled

**Impact:** Some valid V3000 MOL files may not parse correctly.

**Fix approach:** Add support for quoted strings, longer atom names, and bond types 9-10.

### Stereo Handling Edge Cases

**Issue:** Bond stereo consideration not fully implemented.

**File:** `INCHI-1-SRC/INCHI_BASE/src/runichi.c`

**Details:** Line 2556: `/* TODO: consider real bond_type, bond_stereo */`

**Impact:** Some stereochemical edge cases may not be correctly represented.

**Fix approach:** Implement proper bond type and stereo consideration.

### SRU/MON Embedded Check

**Issue:** Unclear if single COP (constitutional repeat unit) detection is needed.

**File:** `INCHI-1-SRC/INCHI_BASE/src/runichi3.c`

**Details:** Line 3833: `/* TODO: check if SRU/MON are embedded in a single COP */`

**Impact:** Could lead to incorrect polymer representation.

**Fix approach:** Clarify requirement and implement if needed.

### InChI Read Compatibility

**Issue:** Potential compatibility issue with InChI=1// conversion.

**File:** `INCHI-1-SRC/INCHI_BASE/src/ichiread.c`

**Details:** Line 822: Comment regarding potential dangerous change for `i2s` handling of InChI=1//

**Impact:** InChI to structure conversion may fail for certain inputs.

**Fix approach:** Thorough testing and potential fix before next release.

---

## Security Concerns (Addressed in Recent Versions)

### Historical Security Issues Fixed in v1.07

The following security issues were identified and fixed in v1.07.x releases:

1. **Buffer overflows:** 33 fixed in v1.07.0
2. **NULL pointer dereferences:** 157 fixed in v1.07.0
3. **Memory leaks:** 71 fixed in v1.07.0
4. **Bounds checking:** 530 potential issues addressed with C11 Annex K support
5. **Stack buffer overflow:** Fixed PR #138 (CleanOrigCoord)
6. **Various Google oss-fuzz issues:** Multiple fixes across versions
7. **Coverity Scan bugs:** 127 high/medium impact bugs fixed in v1.07.5

**Files:** Various throughout codebase - see CHANGELOG.md for details.

**Current Status:** Active scanning via Coverity and Google oss-fuzz continues.

---

## Performance Concerns

### Large Molecule Handling

**Issue:** Large molecule support (experimental) may have performance limitations.

**Files:** `INCHI-1-SRC/INCHI_BASE/src/` - Multiple normalization and ring detection modules

**Details:**
- The "LargeMolecules" option allows up to 32,767 atoms but performance degrades significantly
- Ring detection algorithms may not scale optimally
- Memory allocation in normalization can be inefficient

**Impact:** Processing very large molecules (>10,000 atoms) may be slow or run out of memory.

**Fix approach:** Consider algorithmic improvements or parallel processing for future versions.

### Thread Safety Improvements (v1.07.2+)

**Note:** Global variables were removed in v1.07.2 to improve thread safety. The code is now reentrant and thread-safe, but some legacy code paths may have subtle issues.

**Files:** Multiple - prior global variables existed in many modules.

**Current Status:** Multi-threading tests now available via GitHub Actions.

---

## Maintainability Issues

### Code Age and Style

The InChI codebase has evolved over 20+ years (first released ~2000), leading to:

1. **Mixed coding styles:** Different modules were written by different authors over different time periods
2. **Pre-C99 C standard:** Being phased out starting v1.07.5 (see README.md line 331)
3. **Legacy build systems:** Multiple build systems supported (Make, Visual Studio, CMake)

**Impact:** New contributors may find it challenging to understand and maintain the codebase.

**Mitigation:** Doxygen documentation added recently, CMake build system modernized, C99 standard adoption in progress.

### Missing Test Coverage for Edge Cases

**Details:** Based on the oss-fuzz and Coverity fixes, many edge cases were discovered through fuzzing rather than systematic testing.

**Impact:** Some unusual but valid chemical structures may cause unexpected behavior.

**Fix approach:** Continue fuzzing campaigns and add edge case tests.

---

## Experimental Features (Not Fully Functional)

The following experimental options should be used with caution (from README.md lines 355-382):

### Command Line Issues (32-bit Windows MSVC only):
- AMI, AMIOutStd, AMILogStd, AMIPrbNone

### API Experimental Options:
- KET (keto-enol tautomerism)
- 15T (1,5-tautomerism)
- PT_06_00, PT_13_00, PT_16_00, PT_18_00, PT_22_00, PT_39_00 (various tautomerism shifts)
- Polymers105 (legacy polymer mode)
- NoEdits, NPZz, SAtZz (polymer-related pseudo atoms)
- InChI2Struct, InChI2InChI (test modes that produce Fatal Error like v1.06)

**Impact:** Using these options may produce incorrect results or crashes.

**Recommendation:** Avoid or use only for specific testing purposes.

---

## Build and Platform Concerns

### 32-bit Support Removed

**As of v1.07.5:** 32-bit artifacts are no longer shipped. Legacy 32-bit code paths may have accumulated issues.

**Files:** Makefiles and VS projects for 32-bit still exist but untested.

### Library Path Issues

**Issue:** On Linux with Clang/LLVM, libinchi.so may not be found without LD_LIBRARY_PATH configuration.

**Files:** makefile/makefile32 in various INCHI_API directories

**Mitigation:** See README.md lines 309-329 for solutions (ldlp_fix.sh, patchelf, etc.)

**Impact:** Users building from source may encounter runtime linker errors.

---

## Summary of Priority Areas

| Priority | Area | Action |
|----------|------|--------|
| High | Atropisomer output | Complete t/m-layer implementation |
| High | V3000 support | Add string quotes, longer names, bond types |
| Medium | Memory management | Review and fix potential issues in API |
| Medium | IXA refactoring | Complete TODO items |
| Low | Code modernization | Continue C99 adoption |
| Ongoing | Security | Continue fuzzing and Coverity scans |

---

*Concerns audit: 2026-04-22*