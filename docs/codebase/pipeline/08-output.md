# Output Step - Serializing InChI to Text Format

**Analysis Date:** 2026-04-22

## Overview

The **Output** step is the final stage in the InChI processing pipeline that serializes the canonicalized internal InChI structure into human-readable text format. This step transforms the processed chemical representation into the standard InChI string, optionally generating the InChIKey hash identifier, and producing auxiliary information for structure reconstruction.

The output system supports multiple formats:
- **Standard InChI**: `InChI=1S/{layers}` - The canonical, reversible form
- **Non-standard InChI**: `InChI=1/{layers}` - Without normalization
- **Beta InChI**: `InChI=1B/{layers}` - Beta version format
- **InChIKey**: A 27-character hash-based identifier (e.g., `XXXXXXXXXXXXXXXXXX-XXXXXXXXXX-X`)

This step is invoked from the main InChI generation workflow after canonicalization is complete. The output functions are located in `INCHI-1-SRC/INCHI_BASE/src/ichiprt1.c` (primary), `ichiprt2.c` (helpers), and `ichiprt3.c` (string generation).

## IUPAC Rules and Standards

The InChI system is an IUPAC-standardized chemical identifier with defined specifications for format, validation, and representation. This section documents the official standards governing InChI output.

### InChI String Format

The complete InChI string format follows this specification:

```
InChI=1S/{formula_layer}/{connection_layer}/{hydrogen_layer}/{charge_layer}/{stereo_layer}/{isotopic_layer}/{fixedH_layer}
```

**Version Prefix:**
- `InChI=1S/` — Standard InChI version 1 (normalized, canonical form)
- `InChI=1/` — Non-standard InChI (no normalization applied)
- `InChI=1B/` — Beta version (experimental features)

Each layer is preceded by a slash (`/`) delimiter. Empty layers omit the forward slash. The version identifier (`1S`, `1`, or `1B`) immediately follows `InChI=` with no intervening characters.

### InChIKey Format

The InChIKey is a fixed 27-character hashed representation of an InChI string:

```
XXXXXXXXXXXXXXXXXX-XXXXXXXXXX-X
       |              |  |
       |              |  +-- Protonation flag (N/O/M/S/T)
       |              +----- Reconnection flag
       +---------------------- 24-character layer hash block
```

**Structure:**
- **Block 1** (24 chars): SHA-256 hash of layers 1-9, encoded in base-26 using triplet tables
- **Block 2** (10 chars): Encodes protonation state; final 2 chars are reconnection and protonation flags
- **Block 3** (1 char): Protonation flag (N=none, O=over/under, M=metal, S=salt, T=tautomer)

The hash encoding uses a custom base-26 alphabet (A-Z, excluding "E" and ambiguous character pairs) to avoid forming English words. This ensures the InChIKey is visually distinguishable from dictionary words.

### Standard vs Nonstandard InChI

**Standard InChI** (`InChI=1S/...`):
- Undergoes full canonicalization and normalization
- Produces unique, reversible identifiers
- IUPAC-recommended for database and interchange use
- Includes standardized tautomer handling, hydrogen normalization, and charge representation

**Non-standard InChI** (`InChI=1/...`):
- Skips normalization steps
- Retains original atom ordering and bond representation
- Useful for preserving specific structural representations
- May produce multiple InChI strings for the same chemical structure

Standard InChI is preferred for data interchange; non-standard InChI preserves original input for comparison and special-purpose applications where canonicalization would obscure meaningful differences.

### Output Options

The InChI library supports multiple output modes controlled by flags:

| Option | Flag | Description |
|--------|------|-------------|
| Plain text | `/plain` | Raw InChI string without XML封装 |
| XML output | (default) | XML-wrapped output with metadata |
| With AuxInfo | default | Includes auxiliary reconstruction data |
| Short AuxInfo | `/SAUX` | Condensed auxiliary information only |
| No AuxInfo | `/NOAUX` | Excludes auxiliary information |
| With comments | `/Com` | Human-readable layer comments |

### Auxiliary Information

Auxiliary information (AuxInfo) provides mapping data for structure reconstruction from the InChI string:

```
/AuxInfo=1/{norm_flags}/{atom_map}/{stereo}/{isotopic}/{reversibility}
```

**Purpose of AuxInfo:**
- Maps canonical atom numbers to original input atom numbers
- Preserves equivalence class information for isomorphic structures
- Stores original charge, radical, and valence data
- Enables exact reconstruction of input structure from InChI string

AuxInfo is essential for reversible structure handling—without it, the original structure cannot be recovered from the InChI string alone.

### Validation

InChI validation operates at multiple levels:

1. **Structure validation**: Check for valid atom types, valences, and bond connectivity
2. **String validation**: Verify InChI string syntax and layer format
3. **InChIKey validation**: Confirm hash integrity through re-computation

Invalid structures produce error InChIs prefixed with `InChI=` but containing error indicators rather than valid layer data. The validation system ensures chemical reasonableness (正确的 valence, no impossible bonds) while accepting unconventional or unstable structures when explicitly allowed.

### Source References

**InChI Technical Manual:**
> InChI Technical Manual, version 1.05. IUPAC, 2014. https://www.iupac.org/web/c2005-0282-1w

**IUPAC InChI FAQ:**
> InChI Frequently Asked Questions. IUPAC InChI Trust. https://www.inchi-trust.org/technical-faq-2/

**Heller et al. (2015) — The InChI Identifier Generator:**
> Heller, S. R., et al. "The InChI Identifier Generator: Implementation of the InChI methodology." *Journal of Cheminformatics* 7, 26 (2015). doi:10.1186/s13321-015-0071-7

---

## Input

The Output step receives a fully processed **INChI structure** containing:

```c
typedef struct tagINChI {
    /* Connection layer */
    int  lenConnTable;           // Length of connection table
    AT_NUMB *nConnTable;         // Connection table in canonical order
    
    /* Formula layer */
    char *szHillFormula;         // Hill formula (e.g., "C6H6" for benzene)
    
    /* Hydrogen layer */
    int  nNumberOfAtoms;         // Number of atoms
    short *nNum_H;               // Number of hydrogens on each atom
    
    /* Charge layer */
    int  nTotalCharge;           // Total charge on structure
    
    /* Stereo layer */
    INChI_Stereo *Stereo;        // Stereo center/bond information
    
    /* Isotopic layer */
    int nNumberOfIsotopicAtoms;  // Count of isotopic atoms
    IsotopicAtom *IsotopicAtom;  // Isotopic atom data
    
    /* Tautomer layer */
    int lenTautomer;             // Length of tautomer data
    short *nTautomer;            // Tautomer information
    
    /* Fixed-H layer (optional) */
    INChI *FixedH;                // Fixed hydrogen layer
} INChI;
```

Additionally, the step receives:
- **INChI_Aux structure**: Auxiliary information for structure reconstruction
- **ORIG_ATOM_DATA**: Original atom data including coordinates
- **INPUT_PARMS**: User-specified output options
- **num_components2[]**: Component counts for each structure type

## Output

### Plain Text InChI String

The primary output is a text string following the InChI layer syntax:

```
InChI=1S/{main_layers}/{stereo_layer}/{isotopic_layer}/{fixedH_layer}
```

**Layer Components:**

| Layer | Tag | Example | Description |
|-------|-----|---------|-------------|
| Version | `InChI=1S` | `InChI=1S/` | Standard InChI version 1 |
| Formula | `/f` or main | `C6H6` | Hill formula |
| Connections | `/c` | `c1ccccc1` | Connection table |
| Hydrogens | `/h` | `h1H` | Hydrogen distribution |
| Charge | `/q` | `q+1` | Charge layer |
| Protons | `/p` | `p+1` | Removed protons |
| Double bond stereo | `/b` | `b1-3` | Double bond stereo |
| SP3 stereo | `/t` | `t1` | Tetrahedral stereo |
| Stereo type | `/s` | `s1` | Absolute/relative/racemic |
| Isotopic atoms | `/i` | `i3-5` | Isotopic atom positions |
| Fixed-H formula | `/f` | `C6H6` | Fixed-H layer formula |
| Fixed-H layer | `/h` | `h1H` | Fixed hydrogen positions |
| Transposition | `/o` | `o1-2` | H-transposition |
| Reconnected | `/r` | `r...` | Reconnected metal bonds |

**Example Outputs:**

```
Water:           InChI=1S/H2O/h1H2
Benzene:         InChI=1S/C6H6/c1-6-2-4-5-3-1/h1-6H
Ethanol:         InChI=1S/C2H6O/c1-2-3/h3H,1-2H2
Acetic acid:     InChI=1S/C2H4O2/c1-2(3)4/h1-2H2,(H,3,4)
Caffeine:        InChI=1S/C8H10N4O2/c1-10-4-9-6-5-11(3-7(10)12)8(13)14/h1-4H,5-6H2,(H,9,12,13,14)
```

### InChIKey

The InChIKey is a hash-based identifier generated from the InChI string:

```
[24-char hash block]-[10-char hash block]-[1 char flag]
XXXXXXXXXXXXXXXXXX-XXXXXXXXXX-X
     |               |    |
     |               |    +-- Protonation flag (S=salts, O=over/under, M=metal)
     |               +------- Protonation flag for reconnected layer
     +----------------------- First hash block (encoded from layers 1-9)
```

**Generation Process:**

1. **Input preparation**: Normalize InChI string (remove spaces, lowercase layers)
2. **SHA-256 hashing**: Compute SHA-256 hash of the normalized string
3. **Base-26 encoding**: Convert hash bytes to base-26 using triplet tables

**Implementation in `ikey_base26.c`:**

```c
// Key generation uses 14-bit triplets from SHA-256 hash
// Each triplet encodes to 3 uppercase letters (A-Z)
// 24-char block = 8 triplets = 112 bits from hash
// Rest of hash bytes are output as hexadecimal for extension

const char* base26_triplet_1(const unsigned char *a) {
    // Extracts bits 0-13 from hash bytes
    UINT32 b0 = (UINT32)a[0];           // 1111 1111
    UINT32 b1 = (UINT32)(a[1] & 0x3f);  // 0011 1111
    UINT32 h = (UINT32)(b0 | b1 << 8);  // 14-bit value
    return t26[h];  // Lookup table: 16384 valid triplets
}
```

The lookup table `t26[]` contains 16,384 valid triplets (A-Z). Invalid combinations (those starting with E or certain T* patterns) are excluded to avoid confusing words.

**Example InChIKeys:**

```
Water:           InChIKey=XLYOFNOQVPJJNP-UHFFFAOYSA-N
Benzene:         InChIKey=UYQJADQFDFLCSZ-UHFFFAOYSA-N
Ethanol:         InChIKey=LFQSCWFLJHTTHZ-UHFFFAOYSA-N
Acetic acid:     InChIKey=QTBSBXVTEAMEQO-UHFFFAOYSA-N
Caffeine:        InChIKey=RYYVLZVUVIJVGH-UHFFFAOYSA-N
```

### Auxiliary Information

The auxiliary information (AuxInfo) provides mapping data for structure reconstruction:

```
/AuxInfo=1/{normalization_type}/{original_atom_numbers}/{stereo}/{isotopic_info}
```

**AuxInfo Layers:**

| Layer | Tag | Example | Description |
|-------|-----|---------|-------------|
| Version | `AuxInfo=1/` | - | AuxInfo version |
| Normalization | `/N:` | `/N:1,2,3,4,5,6` | Original atom numbers |
| Equivalence | `/E:` | `/E:1*2` | Atom equivalence classes |
| Stereo | `/it:` | `/it:` | Stereo information |
| Charge/Valence | `/CRV:` | `/CRV:` | Charge, radical, valence |
| Reversibility | `/rA:`, `/rB:`, `/rC:` | - | Original structure for reversal |

## Pseudo-code Algorithm

### Main Output Function (`OutputINChI1`)

```
function OutputINChI1(pCG, strbuf, pINChISort, ...):
    Initialize output control structure (io)
    Set line separators (LF, TAB)
    
    // For each component in structure:
    for each component i in num_components:
        // Analyze what layers are present
        Detect stereo layers (sp2, sp3, isotopic)
        Detect isotopic atoms
        Detect tautomeric groups
        
    // Build InChI string layer by layer:
    OutputINCHI_VersionAndKind()       // "InChI=1S/"
    OutputINCHI_MainLayerFormula()      // "C6H6"
    OutputINCHI_MainLayerConnections()  // "/c1ccccc1"
    OutputINCHI_MainLayerHydrogens()    // "/h1-6H"
    OutputINCHI_ChargeAndRemovedProtonsLayers()  // "/q+1"
    OutputINCHI_StereoLayer()           // "/b1-3/t1-2"
    OutputINCHI_IsotopicLayer()         // "/i3"
    OutputINCHI_FixedHLayerWithSublayers()  // "/fC6H6/h..."
    OutputAUXINFO_HeaderAndNormalization_type()  // AuxInfo
    
    return success/failure
```

### String Generation Functions (`ichiprt3.c`)

**Formula Layer:**
```
function str_HillFormula(pINChISort, strbuf, ...):
    for each component:
        if component_formula == previous_formula:
            increment_multiplier  // "*2" for second identical component
        else:
            output_multiplier_if_any
            output formula_string
    return string_length
```

**Connection Layer:**
```
function str_Connections(pINChISort, strbuf, ...):
    for each component:
        if connections == previous_connections:
            increment_multiplier
        else:
            output_multiplier_if_any
            MakeCtStringNew()  // Format: "c1ccccc1" or "c1:2:3"
    return string_length
```

**Hydrogen Layer:**
```
function str_H_atoms(pINChISort, strbuf, ...):
    for each component:
        if H_distribution == previous_H:
            increment_multiplier
        else:
            output_multiplier_if_any
            MakeHString()  // Format: "h1H" or "h1:2H"
            MakeTautString()  // Tautomer groups if present
    return string_length
```

### InChIKey Generation

```
function GenerateInChIKey(inchi_string):
    // Step 1: Normalize InChI
    normalized = normalize_inchi_string(inchi_string)
    
    // Step 2: Compute SHA-256 hash
    hash = SHA256(normalized)
    
    // Step 3: Extract and encode 8 triplets
    key_part1 = ""
    for i in 0 to 7:
        bits = extract_14_bits(hash, i * 14)
        key_part1 += triplet_table[bits]  // Lookup from t26[]
    
    // Step 4: Extract and encode 1 doublet (9 bits)
    bits = extract_9_bits(hash, 112)
    key_part2 = doublet_table[bits]  // Lookup from d26[]
    
    // Step 5: Add protonation flags
    flag1 = determine_protonation_flag(inchi_string)
    flag2 = determine_reconnected_flag(inchi_string)
    
    return key_part1 + "-" + key_part2 + "-" + flag1 + flag2
```

### Tag Constants (from `ichiprt1.c`)

```c
// InChI layer identifiers
const INCHI_TAG IdentLbl[] = {
    {"/",  "fixed_H",     "fixed-H", 0},   // IL_FIXH_ORD
    {"/",  "isotopic",    "isotopic", 0},  // IL_ISOT_ORD  
    {"/",  "stereo",      "stereo", 0},    // IL_STER_ORD
    {"",   "version",     "version", 1},    // IL_VERS_ORD
    {"/",  "formula",     "formula", 1},    // IL_FML__ORD
    {"/c", "connections", "connections", 1}, // IL_CONN_ORD
    {"/h", "H_atoms",    "H", 1},           // IL_ALLH_ORD
    {"/q", "charge",     "charge", 1},      // IL_CHRG_ORD
    {"/p", "protons",    "protons", 0},      // IL_PROT_ORD
    {"/b", "dbond",      "dbond", 0},       // IL_DBND_ORD
    {"/t", "sp3",        "sp3", 0},         // IL_SP3S_ORD
    {"/m", "sp3:inverted", "abs.inverted", 0}, // IL_INVS_ORD
    {"/s", "type",       "type", 0},        // IL_TYPS_ORD
    {"/i", "atoms",      "atoms", 1},       // IL_ATMS_ORD
    {"/f", "formula",    "formula", 1},     // IL_FMLF_ORD
    {"/h", "H_fixed",    "H-fixed", 1},      // IL_HFIX_ORD
    {"/o", "transposition", "transposition", 0}, // IL_TRNS_ORD
    {"/r", "reconnected", "formula", 0}     // IL_REC__ORD
};
```

## Examples

### Complete Output Examples

**Water (H2O):**
```
InChI=1S/H2O/h1H2
InChIKey=XLYOFNOQVPJJNP-UHFFFAOYSA-N

AuxInfo=1S.1.0.N+0000000.0...000000.E+000000.0000000000000000000000000000000000000000000000000000000000000000.-1.0.0
```

**Benzene (C6H6):**
```
InChI=1S/C6H6/c1-6-2-4-5-3-1/h1-6H
InChIKey=UYQJADQFDFLCSZ-UHFFFAOYSA-N

AuxInfo=1S.1.0.N+0000012+0000034+0000056.0...000000.E+000001*000002*000003*000004*000005*000006.0.0.0000000000000000000000000000000000000000000000000000000000000000.-1.0.0
```

**Ethanol (C2H5OH):**
```
InChI=1S/C2H6O/c1-2-3/h3H,1-2H2
InChIKey=LFQSCWFLJHTTHZ-UHFFFAOYSA-N

AuxInfo=1S.1.0.N+0000012+000003.0...000000.E+000001*000002*000003.0.0.0000000000000000000000000000000000000000000000000000000000000000.-1.0.0
```

**Caffeine (C8H10N4O2):**
```
InChI=1S/C8H10N4O2/c1-10-4-9-6-5-11(3-7(10)12)8(13)14/h1-4H,5-6H2,(H,9,12,13,14)
InChIKey=RYYVLZVUVIJVGH-UHFFFAOYSA-N
```

### Error Output

```
Error: InChI=1//null (null structure)
Warning: InChI=1S// (structure with no atoms)
```

### With Isotopic Information

**Deuterium-labeled water:**
```
InChI=1S/H2O/h1H2/i1+1
InChIKey=XLYOFNOQVPJJNP-UHFFFAOYSA-N
```

### With Stereo Information

**L-Alanine (chiral):**
```
InChI=1S/C3H7NO2/c1-2(4)3(5)6/h2H,1,4-6H2/t2-/m1/s1
InChIKey=QGXXKDAPDFCHTZ-ZZDSAMQSSA-N
```

The `/s1` indicates absolute stereo configuration.

### With Charge

**Acetate ion:**
```
InChI=1S/C2H4O2/c1-2(3)4/h1-2H2,(H,3,4)/q-1
InChIKey=QTBSBXVTEAMEQO-UHFFFAOYSA-N
```

## Key Source Files

| File | Purpose |
|------|---------|
| `INCHI-1-SRC/INCHI_BASE/src/ichiprt1.c` | Main output functions, layer definitions, InChI string building |
| `INCHI-1-SRC/INCHI_BASE/src/ichiprt2.c` | Helper functions, number formatting, equality checking |
| `INCHI-1-SRC/INCHI_BASE/src/ichiprt3.c` | String generation for each layer (formula, connections, H, charge) |
| `INCHI-1-SRC/INCHI_BASE/src/ikey_base26.c` | InChIKey generation, base-26 encoding tables |
| `INCHI-1-SRC/INCHI_BASE/src/ikey_dll.c` | InChIKey DLL interface |

## Output Options

The output behavior can be controlled through `bINChIOutputOptions`:

| Option | Value | Effect |
|--------|-------|--------|
| `INCHI_OUT_NO_AUX_INFO` | 0x0001 | Do not output auxiliary information |
| `INCHI_OUT_SHORT_AUX_INFO` | 0x0002 | Output short version of AuxInfo |
| `INCHI_OUT_ONLY_AUX_INFO` | 0x0004 | Output only auxiliary information |
| `INCHI_OUT_EMBED_REC` | 0x0008 | Embed reconnected InChI into disconnected |
| `INCHI_OUT_PLAIN_TEXT` | 0x0100 | Plain text output without XML tags |
| `INCHI_OUT_PLAIN_TEXT_COMMENTS` | 0x0200 | Plain text with human-readable comments |

---

*Pipeline documentation: Output step*
