# InChI Assembly

**Analysis Date:** 2026-04-22

## Overview

The **InChI Assembly** is the final step in the InChI processing pipeline where all canonicalized and normalized data from previous processing stages is assembled into a complete, standardized InChI string. This step receives the structured data from canonicalization (05-canonicalization.md), tautomer enumeration, ring detection, and stereochemistry processing, then composes these into the layered string format defined by the InChI standard.

The InChI string follows a layered architecture where each layer encodes specific chemical information:

- **Main layers** (`/c`, `/h`, `/f`): Formula, connections, and mobile hydrogens
- **Charge/proton layer** (`/q`, `/p`): charge and removed protons
- **Stereo layers** (`/s`, `/b`, `/t`, `/m`): stereochemistry information
- **Isotopic layer** (`/i`): isotopic labeling
- **Fixed H layer** (`/f` for reconnected): fixed hydrogen positions

The assembly process also generates the **InChIKey** - a hash-based identifier derived from the InChI string that enables fast database lookup and uniqueness verification.

**Position in pipeline:** Step 7 of 9 (following stereochemistry processing and before/parallel to output formatting)

---

## IUPAC Rules and Standards

The InChI standard is governed by IUPAC (International Union of Pure and Applied Chemistry) and defines strict rules for string construction, layer ordering, and formatting. All InChI strings produced by this assembly must comply with these standards.

### InChI Layer Structure

The InChI Technical Manual (Section II.d) defines five distinct layer types, each encoding specific chemical information:

| Layer | Prefix | Information Encoded |
|-------|--------|---------------------|
| **Main Layer** | `/c`, `/f`, `/h` | Chemical formula, connectivity, mobile hydrogen atoms |
| **Charge Layer** | `/q`, `/p` | Formal charge and removed/added protons |
| **Stereo Layer** | `/s`, `/b`, `/t`, `/m` | Stereochemistry (sp2, sp3, bond, markers) |
| **Isotopic Layer** | `/i` | Isotopic labeling (e.g., D, T, 13C) |
| **Fixed Hydrogen Layer** | `/f` (reconnected) | Fixed positions of reconnected hydrogens |

Each layer except the Main layer is optional and may be omitted if no relevant data exists.

### Layer Order Rules

The InChI Technical Manual specifies strict ordering of layers within the string. Layers MUST appear in the following order:

```
/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r
```

| Layer | Order Position | Required? |
|-------|---------------|-----------|
| `/f` (formula) | 1 | Always first |
| `/c` (connections) | 2 | Required with atoms |
| `/h` (mobile H) | 3 | If mobile H present |
| `/m` (stereo markers) | 4 | If used |
| `/q` (charge) | 5 | If charged |
| `/p` (removed protons) | 6 | If tautomeric protons removed |
| `/i` (isotopes) | 7 | If isotopic labeling |
| `/b` (stereo bonds) | 8 | If used | Geometric (cis/trans) double bond stereo |
| `/t` (sp3 stereo) | 9 | If tetrahedral stereo | Tetrahedral centers (sp3 carbon, nitrogen, etc.) |
| `/s` (stereo type) | 10 | If used | Absolute/relative/racemic flag |
| `/r` (reconnected Fixed H) | 11 | If FixedH layer | Metal reconnection |

This ordering ensures consistent parsing and backward compatibility.

### Standard InChI Format

Standard InChI is the canonical form defined by IUPAC for chemical identifier interchange:

```
InChI=1S/{layers}
```

| Component | Meaning |
|-----------|---------|
| `InChI=1` | InChI identifier, version 1 |
| `S` | Standard (mandatory for compliant strings) |
| `/` | Layer separator |

**Example:**
```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H2
```

The `S` after the version number indicates this is a **Standard InChI** - the only format recommended for database exchange and chemical information systems.

### Nonstandard Options

While Standard InChI (`InChI=1S/`) is preferred, the standard supports several nonstandard variants:

| Format | Prefix | Description |
|--------|--------|-------------|
| **Fixed Hydrogen** | `InChI=1F/` | All tautomeric hydrogens fixed at specific positions |
| **Non-standard** | `InChI=1/` | Accepts non-standard features (discouraged) |
| **Non-standard** | `InChI=1Snon/` | Non-standard with standard layer ordering |
| **Beta** | `InChI=1B/` | Experimental/beta features |

**FixedH format** (commonly used for exact structure representation):
```
InChI=1F/C6H6/c1-2-3-4-5-6-1/h1-6H
```

**Note:** Nonstandard InChI strings may not be accepted by all chemical databases. Use Standard InChI whenever possible.

### InChIKey Generation

The **InChIKey** is a hash-based identifier derived from the InChI string, enabling fast database lookups without parsing the full string:

```
XXXXXXXXXXXXXX-YYYYYYYY-Y-Z
```

| Block | Length | Description |
|-------|--------|-------------|
| Major block | 14 chars | SHA-256 hash of formula + connections + mobile H |
| Minor block | 9 chars | SHA-256 hash of stereo + charge + isotopes |
| Protonation flag | 1 char | A-Z (protonation state) |
| Version | 1 char | A-J (InChI version) |
| Format flag | 1 char | S/N/B (Standard/Non/Beta) |

**Generation algorithm:**

1. **Split InChI** into major block (formula/connections/mobile H) and minor block (stereo/charge/isotopes)
2. **SHA-256 hash** each block separately
3. **Base-26 encode** the hash bytes (using charset `ABCDEFGHIJKLMNOPQRSTUVWXYZ`)
4. **Concatenate** with flags: 14 + 9 + 1 + 1 + 1 = 27 characters

**Example:**
```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H2
→ LFQDQGVMQVDCBZ-UHFFFAOYSA-N
```

The InChIKey enables sub-millisecond database lookups while maintaining a 1:1 mapping with the InChI string.

### Source References

- **InChI Technical Manual Section II.d "The Five InChI 'Layer Types'"** - Official layer definitions
- **InChI Standard Documentation** - IUPAC standard specification
- **IUPAC InChI Website** (https://www.iupac.org/inchi/) - Official InChI resources
- **InChI Trust** (https://www.inchi-trust.org/) - Standard maintainers

---

## Input

The InChI Assembly receives processed data structures from multiple pipeline stages:

### Primary Structures (from `INCHI_SORT` and `INChI`)

| Structure | Source | Purpose |
|-----------|--------|---------|
| `INChI->nNumberOfAtoms` | Canonicalization | Total atom count |
| `INChI->szHillFormula` | Formula generation | Chemical formula string |
| `INChI->naAtoms` | Canonicalization | Atom numbering |
| `INChI_Stereo` | Stereo processing | Stereochemistry data |
| `INChI_IsotopicAtom` | Isotope processing | Isotopic atom data |
| `INChI_Tautomer` | Tautomer enumeration | Mobile H groups |

### Connection Data (from `CANON_GLOBALS`)

```c
// From ichimake.h - connection table format
AT_NUMB *LinearCT    // Canonical ordering of atoms
int nLenCT          // Length of connection table
```

### Input for InChIKey Generation

The assembly also receives the complete InChI string for hash computation:

```c
// From ikey_dll.c - InChIKey input
char *smajor        // Major block (formula + connections + mobile H)
char *sminor       // Minor block (stereo + charge + isotopes)
char *sproto      // Protonization info (if present)
```

---

## Output

### Primary: InChI String

The assembled InChI string with prefix:

```
InChI=1S/{formula}/{connections}/{hydrogens}/{stereo}/{charge}/{isotopes}
```

**Format example:**
```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H2
```

| Component | Prefix | Description |
|----------|--------|-----------|
| Formula | `/c` | Hill formula |
| Connections | `/f` | Connection table |
| Mobile H | `/h` | Hydrogen positions |
| Charge | `/q` | Formal charge |
| Protons | `/p` | Removed protons |
| Stereo | `/s`, `/b`, `/t`, `/m` | Stereochemistry |
| Isotopes | `/i` | Isotopic atoms |
| Fixed H | `/f` (reconnected) | Fixed H positions |

### Secondary: InChIKey

The **InChIKey** is a 27-character hash derived from the InChI string using SHA-256:

```
XXXXXX-YYYYYY-Z
```

| Block | Length | Content |
|-------|--------|---------|
| Major hash | 14 chars | Hash of formula/connections layer |
| Minor hash | 9 chars | Hash of remaining layers |
| Proto flag | 1 char | Protonation state (A-Z) |
| Version | 1 char | InChI version ('A' = v1) |
| Standard | 1 char | Standard/non/beta ('S'/'N'/'B') |

**Generation process** (`ikey_dll.c` lines 385-452):

```c
// 1. SHA-256 hash of major block
sha2_csum( (unsigned char *) smajor, strlen(smajor), digest_major );
// base-26 encode to create first 14 chars
sprintf(tmp, "%-.3s%-.3s%-.3s%-.3s%-.2s",
    base26_triplet_1(digest_major), base26_triplet_2(digest_major),
    base26_triplet_3(digest_major), base26_triplet_4(digest_major),
    base26_dublet_for_bits_56_to_64(digest_major));

// 2. SHA-256 hash of minor block
sha2_csum( (unsigned char *) sminor, strlen(sminor), digest_minor );
// base-26 encode to create next 9 chars

// 3. Append flags
szINCHIKey[slen + 3] = flagproto;   // protonation
szINCHIKey[slen + 4] = '\0';
```

---

## Pseudo-code Algorithm

### Layer Assembly Order

```pseudo
function ComposeInChI(pINChI, pINChI_Aux):
    // Start with InChI prefix
    result = "InChI=1S"  // Standard InChI
    
    // Layer 1: Chemical formula (/c)
    formula = ComposeHillFormula(pINChISort)
    result += "/" + formula
    
    // Layer 2: Connection table (/f)
    if has_atoms:
        connections = ComposeConnections(pCG, pINChISort)
        result += "/f" + connections
    
    // Layer 3: Mobile hydrogens (/h)
    if has_mobile_H:
        hydrogens = ComposeMobileH(pINChISort)
        result += "/h" + hydrogens
    
    // Layer 4: Charge (/q)
    if has_charge:
        charge = ComposeCharge(pINChISort)
        result += "/q" + charge
    
    // Layer 5: Removed protons (/p) - tautomeric only
    if has_removed_protons:
        protons = FormatRemovedProtons(num_removed)
        result += "/p" + protons
    
    // Layer 6: Stereo (/s, /b, /t, /m)
    if has_stereo:
        // sp2 stereo (/s)
        if has_sp2_stereo:
            sp2 = ComposeSp2Stereo(pINChISort)
            result += "/s" + sp2
        // sp3 stereo (/t)
        if has_sp3_stereo:
            sp3 = ComposeSp3Stereo(pINChISort)
            result += "/t" + sp3
    
    // Layer 7: Isotopic (/i)
    if has_isotopes:
        isotopes = ComposeIsotopes(pINChISort)
        result += "/i" + isotopes
    
    return result

function GenerateInChIKey(inchi_string):
    // Parse InChI into blocks
    (smajor, sminor, sproto) = ParseInChI(inchi_string)
    
    // Major hash (formula + connections + mobile H)
    hash_major = SHA256(smajor)
    major_block = base26_encode(hash_major[0:14])
    
    // Minor hash (stereo + charge + isotopes)
    hash_minor = SHA256(sminor)
    minor_block = base26_encode(hash_minor[0:9])
    
    // Determine protonation flag
    proton_flag = GetProtonationChar(sproto)
    
    // Compose InChIKey
    return major_block + "-" + minor_block + proton_flag + "A" + "-S"
```

### String Formatting Functions

The actual implementation uses specialized functions in `ichimake.c`:

```c
// From ichimake.h - string composition functions
int str_HillFormula(INCHI_SORT *pINChISort, ...);      // Formula layer
int str_Connections(CANON_GLOBALS *pCG, INCHI_SORT *pINChISort, ...);  // Connection
int str_H_atoms(INCHI_SORT *pINChISort, ...);        // Mobile H
int str_Charge2(INCHI_SORT *pINChISort, ...);       // Charge
int str_Sp3(INCHI_SORT *pINChISort, ...);         // sp3 Stereo
int str_Sp2(INCHI_SORT *pINChISort, ...);         // sp2 Stereo
int str_IsoAtoms(INCHI_SORT *pINChISort, ...);     // Isotopic atoms
```

### Output Flow (`ichiprt1.c` lines 3163-3508)

```pseudo
function OutputInChIString(out_file, pCG, io):
    // Called by OutputINCHI() - main output function
    
    // 1. Formula layer
    OutputINCHI_MainLayerFormula(pCG, out_file, strbuf, ...)
    
    // 2. Connections layer  
    OutputINCHI_MainLayerConnections(pCG, out_file, strbuf, ...)
    
    // 3. Mobile hydrogens
    OutputINCHI_MainLayerHydrogens(pCG, out_file, strbuf, ...)
    
    // 4. Charge
    OutputINCHI_ChargeAndRemovedAddedProtonsLayers(pCG, out_file, strbuf, ...)
    
    // 5. Stereo (if present)
    OutputINCHI_StereoLayer(pCG, out_file, strbuf, ...)
    OutputINCHI_StereoLayer_EnhancedStereo(pCG, out_file, strbuf, ...)
```

---

## Layer Details

### Formula Layer (`/c`)

Composed from canonicalized atom data using Hill formula convention:

```
C first, then H first, then alphabetical
```

**Example:** `C2H6O` - 2 carbons, 6 hydrogens, 1 oxygen

### Connection Table (`/f`)

Atom connections encoded as canonical ordering:

```
/fA1B2 - atom 1 connected to A, atom 2 connected to B
```

Uses canonical (numbered) atom order from canonicalization.

### Mobile Hydrogens (`/h`)

Positions of tautomerically mobile hydrogen atoms:

```
/h2 - H at position 2 can move
```

### Charge Layer (`/q`)

Formal charge on atoms:

```
/q1 - +1 charge
/q-1 - -1 charge
```

### Stereo Layer (`/s`, `/t`, `/b`, `/m`)

| Prefix | Stereo Type |
|--------|-----------|
| `/s` | sp2 (double bond) stereo |
| `/t` | sp3 (tetrahedral) stereo |
| `/b` | Stereo bonds |
| `/m` | Stereo markers |

### Isotopic Layer (`/i`)

Isotopic atom specifications:

```
/i1-2D - position 1 has deuterium
```

---

## Examples

### Example 1: Ethanol

**Input:** Mol file with C2H6O structure

**InChI Output:**
```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H2
```

**InChIKey:**
```
LFQDQGVMQVDCBZ-UHFFFAOYSA-N
```

**Layer breakdown:**
| Layer | Content |
|-------|---------|
| `/c` | `C2H6O` - formula |
| `/f` | `1-2-3` - connections |
| `/h` | `3H,2H2,1H2` - mobile hydrogens |

### Example 2: Benzene

**Input:** C6H6 aromatic ring

**InChI Output:**
```
InChI=1S/C6H6/c1-2-3-4-5-6-1/h6H
```

**Layer breakdown:**
| Layer | Content |
|-------|---------|
| `/c` | `C6H6` - formula |
| `/f` | `1-2-3-4-5-6-1` - ring connections |
| `/h` | `6H` - 6 mobile hydrogens |

### Example 3: Charged Species (Acetate)

**Input:** CH3COO- ion

**InChI Output:**
```
InChI=1S/C2H3O2/c1-2-3/h1H,2H2,3H-2/q-1
```

**Layer breakdown:**
| Layer | Content |
|-------|---------|
| `/c` | `C2H3O2` - formula |
| `/f` | `1-2-3` - connections |
| `/h` | `1H,2H2,3H` - hydrogens |
| `/q` | `-1` - negative charge |

### Example 4: With Stereochemistry (L-Alanine)

**Input:** L-alanine with chiral center

**InChI Output:**
```
InChI=1S/C3H7NO2/c1-4(2)3(5)6/h4-6H,1-2H2,3H2,(H,7)/t3-/m1/2
```

**Layer breakdown:**
| Layer | Content |
|-------|---------|
| `/c` | `C3H7NO2` - formula |
| `/f` | `1-4(2)3(5)6` - connections |
| `/h` | `4-6H,1-2H2,3H2` - hydrogens |
| `/t` | `3-` - sp3 stereo (tetrahedral) |
| `/m` | `1/2` - absoluteR or inverted |

### Example 5: With Isotope (Deuterated Methanol)

**Input:** CD3OH

**InChI Output:**
```
InChI=1S/CH4O/c1-2/h2H,1H3/i2+1D
```

**Layer breakdown:**
| Layer | Content |
|-------|---------|
| `/c` | `CH4O` - formula |
| `/f` | `1-2` - connections |
| `/h` | `2H,1H3` - hydrogens |
| `/i` | `2+1D` - position 2 has deuterium |

---

## Key Files

| File | Purpose |
|------|---------|
| `INCHI_BASE/src/ichimake.c` | Main assembly functions |
| `INCHI_BASE/src/ichimake.h` | Assembly function declarations |
| `INCHI_BASE/src/ichiprt1.c` | Layer output functions |
| `INCHI_BASE/src/ichiprt3.c` | String composition utilities |
| `INCHI_BASE/src/ikey_dll.c` | InChIKey generation |
| `INCHI_BASE/src/ikey_base26.c` | Base-26 encoding for InChIKey |
| `INCHI_BASE/src/inchi_api.h` | API definitions (InChI= prefix) |

---

## Error Handling

### InChIKey Generation Errors (from `ikey_dll.c`)

| Error Code | Meaning |
|-----------|---------|
| `INCHIKEY_OK` | Success |
| `INCHIKEY_INVALID_INCHI_PREFIX` | Invalid prefix (not "InChI=1") |
| `INCHIKEY_INVALID_STD_INCHI` | Not a valid standard InChI |
| `INCHIKEY_EMPTY_INPUT` | Empty input string |
| `INCHIKEY_NOT_ENOUGH_MEMORY` | Memory allocation failure |
| `INCHIKEY_INVALID_LENGTH` | Invalid InChIKey length |

---

## References

- InChI Technical Manual: Layer definitions
- `ichimake.h`: Function prototypes for string composition
- `inchi_api.h` (line 773): `INCHI_STRING_PREFIX` definition
- `ikey_dll.c` (lines 92-507): Full InChIKey generation algorithm

---

*Pipeline documentation: InChI Assembly (Step 7)*