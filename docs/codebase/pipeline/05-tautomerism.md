# Tautomerism Processing

**Analysis Date:** 2026-04-22

## Overview

The Tautomerism Processing step identifies and processes mobile hydrogen atoms (protons) that can shift between positions within a molecule through prototropic tautomerism. This is one of the most chemically complex steps in the InChI canonicalization pipeline, as it must handle diverse tautomeric systems including keto-enol, amido-imidol, enamine-imine, and many other prototropic tautomer patterns.

Tautomerism in InChI represents the phenomenon where atoms can exchange hydrogen atoms (protons) while simultaneously adjusting bond orders to maintain proper valence. For example, acetone (CH3-C(O)-CH3) exists in equilibrium with its enol form (CH2=C(OH)-CH3). Rather than representing all tautomers, InChI selects a single "canonical" tautomer based on priority rules and encodes the mobile hydrogen information in a separate layer.

This step occurs after normalization but before the final canonicalization (layers are created in sequence: /c, /h, /p, /f, /m, /s). The mobile hydrogen (Mobile-H) layer captures which atoms can have mobile protons that would make different tautomeric forms equivalent - these are atoms where the hydrogen position is not fixed but can shift to other positions in the tautomeric group.

## IUPAC Rules and Standards

### IUPAC Tautomerism Classifications

The IUPAC Gold Book defines three principal classes of tautomerism:

1. **Prototropic tautomerism** - Movement of a proton between atoms, with concomitant shift of a double bond (e.g., keto-enol, amido-imidol)
2. **Ring-chain tautomerism** - Interconversion between open-chain and cyclic forms (e.g., aldehydes ↔ hemiacetals)
3. **Valence tautomerism** - Rearrangement of bonding electrons without proton movement (e.g., cyclobutadiene ↔ butadiene)

InChI currently handles **prototropic tautomerism** comprehensively and provides limited support for ring-chain forms.

### IUPAC Definition

From the InChI Technical Manual: *Tautomerism is a reversible intramolecular movement of a hydrogen atom (proton) from one atom to another accompanied by simultaneous movement of electrons to preserve bond orders.* This formal definition underlies InChI's treatment: the hydrogen moves, but the "canonical" form selected depends on priority rules that determine the preferred tautomer representation.

### InChI Tautomer Rules

InChI defines 11 basic tautomer rules (PT_02 through PT_12) governing which atoms can participate in tautomeric shifts. These rules are enumerated in the InChI Technical Manual and implemented in the tautomer processing code.

| Rule Code | Description | Examples |
|-----------|-------------|----------|
| PT_02_00 | Keto-enol | Carbonyl + CH → C=C-OH |
| PT_03_00 | Amido-imidol | -C(=O)-NH₂ ↔ -C(-OH)=NH |
| PT_04_00 | Enamine-imine | -C=NH ↔ -CH-NH₂ |
| PT_05_00 | Nitroso-oxime | |
| PT_06_00 | Selenium analogs | |
| PT_07_00 | Nitro-aci form | |
| PT_08_00 | Guanidine tautomerism | |
| PT_09_00 | Hydroxamic acid | |
| PT_10_00 | Phosphonic/phosphinic | |
| PT_11_00 | Sulfinic/sulfonic acid | |
| PT_12_00 | Special heterocyclic | |

### Keto-Enol Tautomerism (PT_02_00)

The **keto-enol** tautomerism (PT_02_00) is the most common and widely-applicable prototropic rule. It governs the equilibrium:

```
R-C(=O)-CH₂-R' ⇌ R-CH(OH)=C(R')    (keto form)    (enol form)
```

InChI selects the **keto form** by default (unless the enol is aromatically stabilized), as the keto tautomer typically has lower energy. The mobile hydrogen layer encodes that the proton at the α-carbon and the hydroxyl proton at oxygen are equivalent — either can be the "canonical" position.

### Standard InChI Treatment

**Standard InChI is tautomer-invariant**: regardless of input connectivity, the resulting Standard InChI string represents the same mobile-hydrogen equivalence class. The canonicalization process selects a single tautomeric form based on:

- Atomic priorities (higher atomic number wins)
- Charge/neutrality preference
- Aromaticity considerations

The Mobile-H layer (`/m`) then records which atoms participate in the tautomeric group, enabling applications to recognize that different tautomeric structures should be treated as equivalent.

### Nonstandard Extensions

For specialized handling, InChI provides options beyond Standard mode:

- **`15T` option** - Use 15-tautomer generation (generate multiple tautomers instead of single canonical)
- **`KET` option** - Treat all keto-enol tautomers equally (do not prefer keto form)

These options are documented in the InChI Technical Manual and allow applications to extend tautomer handling when the Standard default is inappropriate.

### Source References

- **InChI Technical Manual, Section on Mobile Hydrogen** - Official InChI Trust documentation
- Guasch, L. et al. (2014). "The InChI for Tautomeric Forms." *J. Chem. Inf. Model.*, 54: 2423-2432. DOI: 10.1021/ci500209a
- **InChI Trust Documentation on Tautomerism** - Official technical specifications

## Input

**Canonicalized structure** from the previous normalization step (`INCHI-1-SRC/INCHI_BASE/src/inchi_norm.c` and `INCHI-1-SRC/INCHI_BASE/src/ichi_bns.c`):

- `inp_ATOM` structure containing all atoms with:
  - Element types (`el_number`)
  - Valence and charge information (`valence`, `charge`)
  - Number of hydrogens (`num_H`)
  - Bond connections and bond types
  - Radical state
  - Endpoint assignment (`endpoint` field - marks tautomeric group membership)

Input arrives as a processed molecular graph after normalization has:
- Adjusted charges on heteroatoms
- Set proper bond orders
- Applied normalization rules (decompose groups, normalize charges)

## Output

### Tautomer Groups

The algorithm produces `T_GROUP_INFO` structure (defined in `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h`) containing:

```c
typedef struct tagTautomerGroupsInfo {
    T_GROUP   *t_group;              // Array of tautomer groups
    AT_NUMB   *nEndpointAtomNumber;    // Endpoint atom indices
    int       nNumEndpoints;        // Number of tautomeric endpoints
    int       num_t_groups;        // Number of tautomer groups found
    TNI       tni;                 // Normalization tracking info
    INCHI_MODE bTautFlags;         // Tautomerism flags
} T_GROUP_INFO;
```

Each tautomer group (`T_GROUP`) stores:
- Number of mobile hydrogens (including isotopic)
- Number of negative charges in the group
- Isotopic hydrogen counts (D, T)
- Group ordering number for canonical sorting

### Mobile-H Layer Data

The Mobile-H layer in the resulting InChI string encodes:

1. **Endpoint atoms** - atoms that participate in tautomerism, specified by canonical atom numbers
2. **Mobile hydrogen counts** - number of mobile H (and isotopic variants) at each endpoint
3. **Charge information** - negative charges that can move with the mobile H

Format in InChI string: `/m:...` layer contains:
- Each endpoint's atom number in canonical ordering
- Count of mobile protons (1H, 2H/deuterium, 3H/tritium)
- Negative charge count at that position

Example Mobile-H layer: `/m1+2c/` means:
- 1 endpoint (at canonical position c)
- 2 mobile hydrogens
- 1 negative charge at that endpoint

## Pseudo-code Algorithm

### Mobile-H Detection Algorithm

```
function DetectMobileH(atoms, num_atoms):
    t_group_info = AllocateTGroupInfo()
    
    FOR each atom i in atoms:
        // Check if atom can be a tautomeric endpoint
        eif = GetEndpointInfo(atoms, i)
        IF eif != NULL:
            // Atom is either H-donor or H-acceptor
            IF eif.cDonor OR eif.cAcceptor:
                AddEndpoint(eif, atom i)
    
    // Find connectivity between endpoints
    FOR each endpoint pair (a, b):
        path = FindTautomericPath(a, b)
        IF path IS valid:
            MergeIntoTautomerGroup(a, b, path)
    
    RETURN t_group_info
```

### Endpoint Information Detection (`nGetEndpointInfo`)

From `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c:359`:

```
function nGetEndpointInfo(atom, iat):
    endpoint_valence = GetStandardValence(atom[iat].el_number)
    
    // Reject if not a potential endpoint element
    IF NOT IsCenterPointElement(atom[iat].el_number):
        RETURN 0
    
    // Skip radicals
    IF atom[iat].radical != NONE AND radical != SINGLET:
        RETURN 0
    
    // Check if valence allows proton movement
    IF atom[iat].valence >= endpoint_valence:
        RETURN 0  // Already saturated
    
    // Calculate mobile H count
    mobile = atom[iat].num_H + (atom[iat].charge == -1 ? 1 : 0)
    
    // Determine donor/acceptor status
    valence_gap = atom[iat].chem_bonds_valence - atom[iat].valence
    IF valence_gap == 0:
        // Can donate H, cannot accept
        eif.cDonor = 1
        eif.cAcceptor = 0
    ELSE IF valence_gap == 1:
        // Can accept H, cannot donate
        eif.cDonor = 0
        eif.cAcceptor = 1
    ELSE:
        RETURN 0
    
    RETURN endpoint_valence
```

### Tautomer Enumeration and Selection

```
function EnumerateTautomers(atoms, endpoints):
    taut_groups = []
    
    FOR each connected endpoint set:
        group = CreateTautomerGroup()
        
        FOR each endpoint in set:
            // Add to group counts
            group.num_Mobile += endpoint.num_H
            group.num_NegCharges += (endpoint.charge == -1 ? 1 : 0)
            group.num_D += endpoint.num_iso_H[DEUTERIUM]
            group.num_T += endpoint.num_iso_H[TRITIUM]
        
        // Sort endpoints by canonical rank
        SortByAtomRank(group.endpoints)
        
        AddToGroups(group)
    
    // Assign group ordering
    FOR each group in taut_groups:
        group.nGroupNumber = AssignOrderNumber(group)
    
    RETURN taut_groups
```

### Donor/Acceptor Counting (`AddAtom2DA`)

From `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c:250`:

```
function AddAtom2DA(num_DA[], atom, at_no, bSubtract):
    // TGNUMDA indices:
    // TG_Num_dH: neutral H donors
    // TG_Num_dM: negative charge donors  
    // TG_Num_aH: neutral H acceptors
    // TG_Num_aM: negative charge acceptors
    // TG_Num_dO: acidic O-donors (=C-OH)
    // TG_Num_aO: acidic O-acceptors (-C=O)
    
    IF atom.charge == -1:
        // Can be donor (negatively charged)
        num_DA[TG_Num_dM] += delta
    ELSE IF atom.charge == 0 AND atom.num_H > 0:
        // Neutral H donor
        num_DA[TG_Num_dH] += delta
    
    // Similar logic for acceptors based on bond order gap
```

## Supported Tautomerism Patterns

The InChI library supports multiple specialized tautomerism modes controlled by compilation flags:

| Flag | Pattern | Reference |
|------|---------|----------|
| `TAUT_PT_22_00` | Phosphorus (V) tautomerism | `nGetEndpointInfo_PT_22_00` |
| `TAUT_PT_16_00` | Phosphorus (III) tautomerism | `nGetEndpointInfo_PT_16_00` |
| `TAUT_PT_06_00` | Selenium tautomerism | `nGetEndpointInfo_PT_06_00` |
| `TAUT_PT_39_00` | Tellurium tautomerism | `nGetEndpointInfo_PT_39_00` |
| `TAUT_PT_13_00` | Arsenic tautomerism | `nGetEndpointInfo_PT_13_00` |
| `TAUT_PT_18_00` | Antimony tautomerism | `nGetEndpointInfo_PT_18_00` |
| `KETO_ENOL_TAUT` | Keto-enol tautomerism | `nGetEndpointInfo_KET` |

## Examples

### Example 1: Simple Keto-Enol - Acetone

**Input:** Acetone (CH3-C(O)-CH3)

**Process:**
1. Carbonyl oxygen is acceptor (can accept H, has double bond)
2. Methyl carbon adjacent to C=O can donate H (single bond to H)
3. Tautomer group identified: O + adjacent CH3 carbon

**Output InChI:** `InChI=1S/C3H6O/c1-3(4)2/h1-2H3`

**Mobile-H layer:** `/m1+1c2` with endpoints at canonical positions

**Enol form represented:** CH2=C(OH)-CH3 (the "canonical" selected form)

### Example 2: Amide Tautomerism - Acetamide

**Input:** CH3-C(=O)-NH2

**Process:**
1. Amide N is donor (has H)
2. Amide O is acceptor (double bond)
3. Imidol form: CH2=C(-OH)-NH (less favorable tautomer)

**Output:** The algorithm selects the amide form (more stable) but records the N as endpoint in Mobile-H layer.

### Example 3: Multiple Tautomeric Sites

**Input:** 2,4-Pentanedione (acetylacetone)
```
CH3-C(=O)-CH2-C(=O)-CH3
```

**Process:**
1. Two equivalent C=O groups
2. CH2 in middle can donate to either C=O
3. Creates large tautomer group with 4 endpoints

**Output:** Mobile-H reflects the delocalized nature: protons can move among multiple positions.

### Example 4: Heterocyclic Tautomerism - Pyrazole

**Input:** Pyrazole (C3N2H4)

**Process:**
1. Both nitrogens participate
2. N-H form ↔ N form tautomerism
3. Two tautomeric forms have different positions for mobile H

**Output:** Mobile-H layer properly tracks the N atoms that can share the mobile proton.

## Key Data Structures

### ENDPOINT_INFO

From `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h:276`:

```c
typedef struct tagEndpointInfo {
    S_CHAR cMoveableCharge;      // Charge that can move with H
    S_CHAR cNeutralBondsValence;
    S_CHAR cMobile;           // Number of mobile H
    S_CHAR cDonor;            // 1 = can donate H
    S_CHAR cAcceptor;          // 1 = can accept H
    S_CHAR cKetoEnolCode;      // For keto-enol: 1=carbon, 2=oxygen
} ENDPOINT_INFO;
```

### TNI (Tautomer Normalization Info)

Tracks protons removed during normalization that relate to tautomerism:

```c
typedef struct tagTautomerNormInfo {
    NUM_H       nNumRemovedExplicitH;
    NUM_H       nNumRemovedProtons;
    NUM_H       nNumRemovedProtonsIsotopic[NUM_H_ISOTOPES];
    INCHI_MODE  bNormalizationFlags;  // Flags showing what normalization occurred
} TNI;
```

### Normalization Flags

From `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h:181`:

- `FLAG_PROTON_NPO_SIMPLE_REMOVED` - Simple removed positive-charge proton
- `FLAG_PROTON_NP_HARD_REMOVED` - Hard removed positive proton
- `FLAG_PROTON_AC_SIMPLE_ADDED` - Simple added acidic proton
- `FLAG_PROTON_AC_SIMPLE_REMOVED` - Simple removed acidic proton
- `FLAG_PROTON_AC_HARD_ADDED` - Hard added acidic proton
- `FLAG_PROTON_AC_HARD_REMOVED` - Hard removed acidic proton

These flags indicate the normalization steps applied that affect tautomer interpretation.

## Files Involved

| File | Purpose |
|------|---------|
| `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c` | Main tautomer processing implementation (~7000 lines) |
| `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h` | Tautomer data structure definitions |
| `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c:nGetEndpointInfo` | Core endpoint detection |
| `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c:AddAtom2DA` | Donor/acceptor counting |
| `INCHI-1-SRC/INCHI_BASE/src/ichi_bns.c` | Balanced network structure for path finding |
| `INCHI-1-SRC/INCHI_BASE/src/ichiqueu.c` | Queue-based tautomer path finding |

## Important Algorithms

### Finding Tautomeric Paths (`nGet15TautInAltPath`)

Uses BFS/DFS to find valid paths through which protons can migrate. The algorithm checks:

1. **Path length** - tautomeric paths limited in length (typically 5-membered paths in rings)
2. **Alternating double-single bonds** - path must alternate between possible double/single bonds
3. **Valence constraints** - atoms along path must maintain proper valence

From `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h:477`:

```c
int nGet15TautInAltPath( CANON_GLOBALS *pCG,
    inp_ATOM *atom, int nStartAtom,
    T_ENDPOINT *EndPoint, T_BONDPOS *BondPos,
    // ... path finding output ...
);
```

### Ring Tautomerism

Special handling for tautomers in rings (`nGet15TautIn6MembAltRing`, `nGet12TautIn5MembAltRing`):

- 5-membered ring: 1,5-proton shift
- 6-membered ring: 1,6-proton shift
- Must have alternating bond orders

---

*Pipeline step analysis: 2026-04-22*