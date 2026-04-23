# Enhanced Stereochemistry - Concerns

**Analysis Date:** 2026-04-23

---

## Known Limitations

### 1. Input Format Restrictions

**Issue**: Only V3000 molfiles support enhanced stereochemistry

**Details**:
- V2000 molfiles cannot specify enhanced stereo groups
- V2000 uses basic per-atom and per-bond parity only
- If V2000 is input, enhanced stereo is silently disabled

**Impact**: Cannot round-trip enhanced stereo through V2000 format

**Fix**: Use only V3000 for files with enhanced stereochemistry

---

### 2. Atom Counting Issues

**Issue**: Collection block may reference atoms outside valid range

**Source**: `mol_fmt3.c:766`

**Details**:
```
ATOMS=(10 1 2 3 4 5 6 7 8 9 10)  // but molecule has only 8 atoms
```

**Impact**: Parser may crash or produce invalid InChI

**Current Handling**:
```c
if (atom_id > num_atoms) {
    // Warning issued, but parsing continues
    // Atom may be silently ignored
}
```

---

### 3. Duplicate Group Membership

**Issue**: Same atom cannot belong to multiple groups

**Details**:
```
M  V30 MDLV30/STEABS ATOMS=(2 3 4)
M  V30 MDLV30/STEREL1 ATOMS=(2 5 6)  // Atom 3 duplicated!
```

**Impact**: Undefined behavior - may use first or last assignment

**Current Handling**: No explicit check in current version

---

### 4. Relative Group Specification

**Issue**: STEREL groups don't fully specify the relationship

**Details**: 
- Specification says "atoms are in the same stereogroup"
- Does NOT specify whether same-side or opposite-side
- Interpretation is application-dependent

**Impact**: Different viewers may interpret relationships differently

**Spec Note**: CTfile Format states STEREL means "or" (either) relationship

---

### 5. Racemic Group Ambiguity

**Issue**: STERAC indicates unknown configuration but not the degree

**Details**:
- A single atom: definitely racemic
- Multiple atoms: are all racemic individually?
- Or is the molecule 50/50 mixture?

**Impact**: Cannot distinguish between:
- Mixture of enantiomers
- Unknown absolute configuration

---

### 6. Inversion Flag Complexity

**Issue**: `/m` layer inversion can be confusing

**Details**:
- `/m0` = Not inverted (matches absolute input)
- `/m1` = Inverted (mirrored)
- Multiple groups can have different inversion states

**Example**:
```
/t1m,2m/m0,1/s1,s2
```

Here atoms 1-2 are in one group with /m0, and in another group with /m1

**Impact**: Difficult to interpret complex cases

---

## Implementation Gaps

### 7. Missing R-Group Support

**Issue**: Enhanced stereo doesn't work with R-group structures

**Source**: `mol_fmt3.c:113-143`

**Details**:
- R-group logic is processed separately
- Enhanced stereo in R-groups may be lost

**Workaround**: Use fully-specified structures before InChI conversion

---

### 8. Polymer S-Group Interaction

**Issue**: Enhanced stereo in polymer S-groups incompletely supported

**Details**:
- S-groups (SUP, SRU, MON, etc.) can contain stereocenters
- Current implementation may not preserve group relationships

**Impact**: Complex polymers may lose enhanced stereo information

---

## Output Format Concerns

### 9. Verbose Output for Large Molecules

**Issue**: Extensive `/t` layers for many stereocenters

**Example**:
```
InChI=1S/C100H200O50/c1-2-3-...-100/
t1m,2m,3m,4m,5m,6m,7m,8m,9m,10m,
11m,12m,13m,14m,15m,16m,17m,18m,19m,20m,
21m,22m,.../m0/s1
```

**Impact**: Very long InChI strings

---

### 10. Layer Ordering

**Issue**: Enhanced stereo layers must appear in specific order

**Required Order**:
```
/c /h /m /q /p /i /b /t /s
```

**Details**:
- `/t` must come after `/b` (double bond stereo)
- `/s` must be last before reconnected `/r`

**Impact**: Generating standard-compliant InChI requires careful ordering

---

## Compatibility Issues

### 11. Legacy Software Compatibility

**Issue**: Older InChI readers may not understand enhanced stereo

**Details**:
- InChI 1.00 readers: Will ignore `/t`, `/m`, `/s` layers
- May treat as basic stereo or error
- InChI 1.02+: Full support

**Mitigation**:
```bash
# Generate both enhanced and basic
inchi-1 mol.mol -EnhancedStereochemistry -out-basic.txt  # Will be silently ignored
inchi-1 mol.mol -out-enhanced.txt  # With enhanced stereo
```

---

### 12. InChI to Structure Conversion

**Issue**: Reversing enhanced stereo is not fully supported

**Source**: `ichirvr*.c` files

**Details**:
- `/t` layer can be read
- `/m` inversion may not reconstruct original absolute configuration
- `/s` layer is often lost in round-trip

**Impact**: Cannot reliably convert InChI back to enhanced stereo molfile

---

## Performance Considerations

### 13. Memory Usage

**Issue**: Enhanced stereo uses additional memory per atom

**Details**:
- `nStereoKind[max_atoms]`: 1 byte per atom
- `INChI_Stereo`: Dynamic allocation for parity arrays
- Large molecules: Memory scales linearly

**Mitigation**:
- Use `-LargeMolecules` flag only when needed
- Enable enhanced stereo only for molecules with stereocenters

---

## Debugging Tips

### Problem: Enhanced Stereo Not Appearing

1. Check input is V3000 format (look for "V3000" in line 4)
2. Verify collection block is inside CTAB
3. Check that atoms exist in molecule (check atom IDs)
4. Ensure `-EnhancedStereochemistry` flag is set (CLI) or `bEnhancedStereo=1` (API)

### Problem: Wrong Parities

1. Verify input coordinates are correct
2. Check for 2D vs 3D confusion (2D may give undefined parity)
3. Confirm atoms have correct connectivity

### Problem: Round-Trip Failure

1. Cannot round-trip through basic InChI (without enhanced flag)
2. Must use InChI to InChI comparison, not structure comparison

---

## Summary of Priority Issues

| Priority | Issue | Status |
|----------|-------|--------|
| High | Duplicate group membership | Not checked |
| High | Invalid atom references | Warning only |
| Medium | R-group interaction | Not supported |
| Medium | Round-trip loss | Known limitation |
| Low | Verbose output | Expected behavior |
| Low | Legacy compatibility | By design |

---

## References

- `mol_fmt3.c`: Lines 695-780 - Collection parsing
- `ichiprt1.c`: Lines 3508-3600 - Output generation  
- CTFile V3000 Specification (BIOVIA, 2020)
- InChI Technical Manual: Section 10

---

*Concerns: 2026-04-23*