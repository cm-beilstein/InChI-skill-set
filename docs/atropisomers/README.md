# Atropisomer Detection and Encoding in InChI

This directory contains comprehensive documentation of how the InChI source code detects and encodes atropisomers (axial stereoisomers) in molecular structures.

## Quick Summary

**What:** Atropisomers are stereoisomers arising from restricted rotation around single bonds (e.g., biaryls)

**How Detected:** Heuristic scoring algorithm evaluates bond geometry and topology:
- Score > 10: Definite atropisomer
- 9 < Score ≤ 10 + non-planar geometry: Probable atropisomer
- Otherwise: Not an atropisomer

**How Encoded:** Uses standard InChI `/t` and `/m` layers:
- `/t` layer: Lists canonical atoms with parity = 1, marked with "m" suffix
- `/m` layer: Indicates enantiomeric (`/m1`) or diastereomeric (`/m0`) relationship

**Where Implemented:** Multiple files in InChI source:
- Detection: `atropisomers.c` (182 lines)
- Layer building: `strutil.c:7121-7256` (136 lines)
- Orchestration: `ichimake.c`, `ichiprt1.c`

## Documentation Structure

### 1. [01-overview.md](01-overview.md)
High-level overview of atropisomers and the InChI processing pipeline.

**Read this first to understand:**
- What atropisomers are
- Why InChI needs special handling for them
- Overall architecture and file organization

### 2. [02-detection-algorithm.md](02-detection-algorithm.md)
Deep dive into the detection heuristics and scoring system.

**Read this to understand:**
- Scoring components and their weights
- Decision thresholds (10, 9)
- Planarity checking and geometric verification
- Helper functions (ring detection, coplanarity)
- Examples with score calculations

### 3. [03-layer-building.md](03-layer-building.md)
How atropisomeric atoms are converted to `/t` and `/m` layers.

**Read this to understand:**
- Three-phase process: Collect → Sort → Determine /m
- Parity assignment (all atoms get parity = 1)
- Three decision paths for `/m` layer:
  - Path A: Mixed classical + atropo
  - Path B: Inverted canonical ordering comparison
  - Path C: Fallback parity counting
- Data structure population
- Open questions and TODO items in code

### 4. [04-integration.md](04-integration.md)
Full processing pipeline from input to output, including API and CLI.

**Read this to understand:**
- Complete data flow through InChI
- Data structure changes at each stage
- How flags propagate through the code
- Interaction with enhanced stereochemistry and tautomerism
- Command-line and API usage
- Debugging strategies
- Common issues and solutions

## Key Files in InChI Source

| File | Lines | Purpose |
|------|-------|---------|
| `atropisomers.c` | 182 | Detection algorithm |
| `strutil.c` | 7121-7256 | Layer building |
| `ichimake.c` | 3908-3925 | Detection orchestration |
| `ichiprt1.c` | 1622-1628 | Layer output trigger |
| `ichister.c` | 1190-1214 | Planarity checking |
| `ring_detection.c` | 160-460 | Ring system analysis |
| `inpdef.h` | 187, 466 | Data structure definitions |
| `ichidrp.h` | 193 | Input parameters |
| `ichi.h` | - | INChI_Stereo structure |

## Processing Pipeline (High-Level)

```
Input File
    ↓
Ring Detection (find_rings)
    ↓
Atropisomer Detection (find_atropisomeric_atoms_and_bonds)
    └─ Scoring algorithm + planarity checks
    └─ Mark atoms: bAtropisomeric = 1
    ↓
Canonicalization (canonical numbering + inverted orderings)
    ↓
Layer Building (set_Atropisomer_t_m_layers)
    ├─ Collect canonical atoms
    ├─ Sort by canonical number
    ├─ Determine /m layer (Path A/B/C)
    ↓
Output Generation (OutputINCHI_StereoLayer)
    └─ Format /t and /m into InChI string
    ↓
InChI with /tXm,Ym/mZ
```

## Key Insights

1. **Heuristic, not chemical knowledge:**
   - No aromaticity awareness beyond ring detection
   - No steric bulk database
   - Purely geometric and topological scoring

2. **Arbitrary parity value (1):**
   - All atropisomeric atoms get parity = 1 (minus/odd)
   - Used only as a marker to identify atropo atoms in `/t` layer
   - Actual stereochemistry (enantiomeric vs diastereomeric) is in `/m`

3. **Three decision paths for /m layer:**
   - **Path A** (fast): Mixed classical+atropo → always /m0
   - **Path B** (accurate): Compare inverted canonical orderings → /m1 or /m0
   - **Path C** (fallback): Count defined parities, apply mod 2 logic

4. **Separated from enhanced stereochemistry:**
   - Both features can be active simultaneously
   - Both populate `/t` and `/m`
   - Atropisomers processed first, then enhanced stereo adds more atoms

## Common Questions

**Q: Why is the score threshold 10/9 and not something else?**
A: The thresholds are empirical and documented in the code as TODO—no theoretical justification provided.

**Q: Why do atropisomeric atoms get parity = 1 (minus)?**
A: It's arbitrary. The parity is only used as a marker to distinguish atropo atoms from classical stereocenters in the `/t` layer.

**Q: How is the /m layer determined?**
A: Three decision paths are tried in order:
1. If mixed classical+atropo → /m0 (diastereomeric)
2. If inverted canonical orderings available → compare and decide
3. Fallback: count parities, use mod 2 to get odd/even axis count

**Q: Can atropisomers be detected in 2D structures?**
A: Unlikely. The planarity check requires 3D coordinates (x,y,z).

**Q: How does this interact with enhanced stereochemistry?**
A: Both are independent. Both populate `/t` and `/m`. Atropisomers run first (during layer building), then enhanced stereo is applied.

## Test Coverage

The InChI test suite includes:
- `test_enhancedStereo.cpp`: Contains atropisomer test cases (atropisomers often included with enhanced stereo tests)
- `fixtures/enh_stereo_test_file_*.sdf`: Test molecules with atropisomeric bonds

## References

- **InChI Technical Manual:** Section 10 (Enhanced/Atropisomeric Stereochemistry)
- **InChI API Reference:** `inchi_api.h` public interface
- **CTFile V3000 Specification:** BIOVIA, 2020

## Summary Statistics

| Metric | Value |
|--------|-------|
| Detection algorithm complexity | O(n²) (pairwise bonds) |
| Scoring components | 13+ weighted rules |
| Decision thresholds | 2 (10 and 9) |
| Decision paths for /m layer | 3 (A, B, C) |
| CLI flag | `-Atropisomers` |
| API parameter | `INPUT_PARMS.Atropisomers` |

---

**Analysis Date:** 2026-04-23

**Note:** This documentation is based on analysis of the InChI source code at `../InChI/INCHI-1-SRC/INCHI_BASE/src/`. The code includes several TODO items indicating that some aspects of atropisomer handling are still under development or refinement.
