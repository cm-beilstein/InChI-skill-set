# Enhanced Stereochemistry - Unit Tests

**Analysis Date:** 2026-04-23

---

## Test Files Location

Unit tests for enhanced stereochemistry are located in:
```
/home/bsmue/code/InChI/INCHI-1-TEST/tests/test_unit/
```

### Test Source Files

| File | Purpose |
|------|---------|
| `test_enhancedStereo.cpp` | Main enhanced stereo tests (1276 lines) |
| `test_ichiprt1_enhancedStereo.cpp` | Output generation tests |
| `test_strutil_enhancedStereo.cpp` | Layer building tests |

### Test Fixtures

| File | Contents |
|------|---------|
| `fixtures/enh_stereo_test_file_1.sdf` | 25 test molecules with enhanced stereo |
| `fixtures/enh_stereo_test_file_2.sdf` | Additional test molecules |

---

## Key Test Case Examples

### Test 1: Basic Enhanced Stereochemistry

From `test_enhancedStereo.cpp:55-125`

**Input V3000:**
```
M  V30 MDLV30/STERAC2 ATOMS=(1 1)
M  V30 MDLV30/STERAC1 ATOMS=(2 2 3)
M  V30 MDLV30/STEABS ATOMS=(2 4 5)
M  V30 MDLV30/STEREL1 ATOMS=(2 12 13)
M  V30 MDLV30/STEREL2 ATOMS=(1 14)
```

**Expected InChI:**
```
InChI=1B/C10H14BrCl7/c1-3(11)5(13)7(15)9(17)10(18)8(16)6(14)4(2)12/h3-10H,1-2H3/t3-,4-,5+,6-,7-,8-,9+,10-/m0/s1(3,5)2(4)(6,8)3(7,9)(10)
```

**S-Layer Breakdown:**
- `/s1(3,5)` = STEABS: atoms 3,5
- `/s2(4)` = STEREL1
- `/s2(6,8)` = STEREL2
- `/s3(7,9)` = STERAC1
- `/s3(10)` = STERAC2

### Test 2: Atropisomer

From `test_enhancedStereo.cpp:127-200`

**Input V3000:**
```
M  V30 MDLV30/STEABS ATOMS=(2 2 3)
M  V30 MDLV30/STEABS ATOMS=(2 5 6)
```

**Expected InChI contains:**
```
InChI=1B/.../s1(2,3,5,6)
```

---

## Test Framework

### API Call Pattern

```c
#include "inchi_api.h"

const char *molblock = "...V3000 molfile...";
char options[] = "-EnhancedStereochemistry";
inchi_Output output;

int result = MakeINCHIFromMolfileText(molblock, options, &output);
// result = 0 means success
// result = 1 means error

EXPECT_STREQ(output.szInChI, expected_inchi);
FreeINCHI(&output);
```

### Options String

The enhanced stereochemistry is enabled with:
```c
char options[] = "-EnhancedStereochemistry";
```

This sets `ip->bEnhancedStereo = 1` internally.

---

## Running Tests

### Build and Run

```bash
cd /home/bsmue/code/InChI/INCHI-1-TEST/tests/test_unit
mkdir -p build
cd build
cmake ..
make
./test_enhancedStereo
```

### Specific Test

```bash
./test_enhancedStereo --gtest_filter=test_enhancedStereo.test_EnhancedStereochemistry_1
```

---

## Test Categories

### 1. Single Group Type Tests

| Test | Group Type | Description |
|------|------------|-------------|
| `test_EnhancedStereochemistry_1` | Mixed (ALL types) | STEABS + STEREL + STERAC |
| `test_EnhancedStereochemistry_3` | STEREL only | Multiple relative groups |
| `test_EnhancedStereochemistry_4` | STERAC only | Multiple racemic groups |

### 2. Atropisomer Tests

| Test | Description |
|------|-------------|
| `test_EnhancedStereochemistry_2_atropisomer` | Axial chirality |
| `test_EnhancedStereochemistry_3_atropisomer` | Multiple atropisomers |

### 3. Edge Cases

| Test | Description |
|------|-------------|
| `test_EnhancedStereochemistry_NoCollection` | No collection block |
| `test_EnhancedStereochemistry_V2000Input` | V2000 format (no collection possible) |

---

## Expected Output Patterns

### Pattern 1: All Types Present

**Input:** 1 STEABS, 1 STEREL, 1 STERAC

**S-layer:**
```
/s1(a1)2(a2),s3(a3)
```

### Pattern 2: Multiple Same Type

**Input:** 2 STEREL groups, 2 STERAC groups

**S-layer:**
```
/s2(a1)(a2),s3(b1)(b2)
```

### Pattern 3: Only ONE Type

**Input:** 1 STEABS group with 4 atoms

**S-layer:**
```
/s1(a1,a2,a3,a4)
```

---

## Verification Against Tests

All documentation should be verified against these test cases:

1. **S-layer format** - Must match `/s1(...)s2(...)s3(...)` with parentheses
2. **Canonical numbers** - Atoms are referenced by canonical number, not input number
3. **Multiple groups** - Each group appears as separate parenthetical group
4. **Group sorting** - Groups sorted by first canonical atom in each group

---

## References

- Test file: `/home/bsmue/code/InChI/INCHI-1-TEST/tests/test_unit/test_enhancedStereo.cpp`
- Test fixtures: `/home/bsmue/code/InChI/INCHI-1-TEST/tests/test_unit/fixtures/`
- API: `inchi_api.h` - `MakeINCHIFromMolfileText()`

---

*Unit Tests: 2026-04-23*