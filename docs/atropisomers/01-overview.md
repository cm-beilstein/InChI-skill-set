# Atropisomer Detection and Encoding in InChI - Overview

**Analysis Date:** 2026-04-23

## What are Atropisomers?

Atropisomers are stereoisomers that arise from **restricted rotation around a single bond**, typically found in:
- **Biaryls** (aromatic-aromatic bonds)
- **Arylamines** (aromatic-nitrogen bonds)
- **Arylesters** (aromatic-oxygen bonds)
- **Macrocycles** with restricted rotation

Unlike typical stereogenic centers (which require four different groups), atropisomers result from **steric hinderance** preventing free rotation about the bond axis.

### Examples

**Typical Biaryl Atropisomer:**
```
        Ar1
         |
    Ar2-C-C-Ar3  (restricted single bond)
         |
        Ar4
```

The C-C bond cannot rotate freely due to steric bulk of the aryl groups, creating distinct enantiomers or diastereomers.

## InChI Representation

InChI represents atropisomers using the same **stereochemistry layers** as classical stereocenters:

- **`/t` layer**: Lists canonical atom numbers of atropisomeric atoms (marked with "m" suffix)
- **`/m` layer**: Indicates enantiomeric (`/m1`) or diastereomeric (`/m0`) relationship

### Example Output

```
InChI=1B/C28H22/c1-19(2)25-13-9-23(10-14-25)27-24-8-4-20(5-11-24)26-15-12-22(22)17-18-21(17)16/t27m,28m/m1
```

Breaking down the stereo part:
- `/t27m,28m`: Atoms 27 and 28 are atropisomeric (marked with "m")
- `/m1`: Enantiomeric (inverting the bond gives the mirror image)

## Architecture Overview

The implementation uses a **scoring-based heuristic detection** followed by **geometric verification**:

```
┌────────────────────────────────────────┐
│  Input Molfile (with or without 3D)   │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│  Ring System Detection                 │
│  (ichimake.c → ring_detection.c)      │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│  Atropisomer Detection                │
│  (find_atropisomeric_atoms_and_bonds) │
│  - Pairwise bond scoring               │
│  - Planarity verification              │
│  - Mark atoms with bAtropisomeric = 1 │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│  Canonicalization                     │
│  (ichicano.c)                         │
│  Assign canonical numbers              │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│  Layer Building                        │
│  (set_Atropisomer_t_m_layers)         │
│  - Populate /t parity array            │
│  - Determine /m enantiomeric flag      │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│  Output Formatting                    │
│  (ichiprt1.c)                         │
│  InChI string with atropisomer layers │
└────────────────────────────────────────┘
```

## Key Design Decisions

1. **Heuristic-based detection**: Rather than explicit chemical rules, InChI uses a scoring algorithm based on geometry and topology
2. **Marker parity = 1 (minus)**: Atropisomeric atoms get an arbitrary parity value to distinguish them in the /t layer
3. **Inverted structure comparison**: The /m layer is determined by comparing canonical orderings before and after inversion
4. **Separate from enhanced stereochemistry**: Atropisomers and enhanced stereo are independent features but both populate /t and /m

## Enablement

### Command Line
```bash
inchi-1 molecule.mol -Atropisomers
```

### API
```c
INPUT_PARMS ip;
ip.Atropisomers = 1;  // Enable detection
```

## Files Involved

| File | Role |
|------|------|
| `atropisomers.c` | Detection algorithm and scoring |
| `strutil.c` | Layer building (set_Atropisomer_t_m_layers) |
| `ichimake.c` | Orchestration, flag initialization |
| `ichiprt1.c` | Output generation |
| `ichister.c` | Helper functions (planarity detection) |
| `ring_detection.c` | Ring system analysis |
| `inpdef.h` | Data structure definitions (bAtropisomeric) |
| `ichidrp.h` | Input parameters (Atropisomers flag) |

---

*Overview: 2026-04-23*
