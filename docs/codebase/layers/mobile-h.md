# Mobile-H Layer (`/m`)

**Analysis Date:** 2026-04-22

## Overview

The Mobile-H layer (`/m`) in the InChI identifier represents tautomeric mobile hydrogen atoms. Tautomerism is a special type of structural isomerism where molecules exist in equilibrium as different forms due to the reversible migration of hydrogen atoms and associated electrons. This layer captures which hydrogen atoms are mobile across tautomeric groups, allowing the InChI to represent multiple tautomeric forms in a single, canonical identifier.

Tautomeric mobile hydrogens arise when a hydrogen atom can shift between two or more positions within a molecule, typically involving a centerpoint atom (such as carbon, nitrogen, oxygen, or sulfur) connected to multiple endpoint atoms through double bonds or aromatic systems. Common examples include keto-enol tautomerism (where a carbonyl compound interconverts with its enol form), amide-imidic acid tautomerism, and lactam-lactim tautomerism (as in nucleobase pairs like guanine).

The Mobile-H layer is used in the main InChI output when tautomeric groups are detected, appearing as `/m+1`, `/m-1`, `/m+2`, etc. The format indicates the number of mobile hydrogen atoms and negative charges in each tautomeric group. When no tautomerism is present, this layer is omitted entirely from the InChI string. The sign (`+` or `-`) indicates whether hydrogen atoms are being gained or lost relative to the standard form, and multiple tautomeric groups are separated by parentheses.

## Code Implementation

### Key Source Files

| File | Purpose |
|------|--------|
| `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c` | Core tautomer detection and group registration algorithm |
| `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h` | Tautomer data structures and function declarations |
| `INCHI-1-SRC/INCHI_BASE/src/ichimake.c` | InChI construction including Mobile-H layer assembly |
| `INCHI-1-SRC/INCHI_BASE/src/ichiprt2.c` | String output formatting for tautomer layer |
| `INCHI-1-SRC/INCHI_BASE/src/strutil.c` | Memory allocation for `nTautomer` arrays |

### Core Data Structures

**Linear CT Tautomer Format (`ichitaut.h`, lines 104-113):**
```c
#define T_NUM_NO_ISOTOPIC 2    // Non-isotopic elements per endpoint
#define T_NUM_ISOTOPIC    3    // Isotopic hydrogens: D (deuterium), T (tritium), 1H

typedef AT_NUMB AT_TAUTOMER;    // Linear CT Tautomer storage type

typedef struct tagIsotopicTautomerGroup {
    AT_NUMB tgroup_num;        // Ordering number of tautomer group with isotopes > 0
    AT_NUMB num[T_NUM_ISOTOPIC]; // Inverted order: num_T, num_D, num_1H
} AT_ISO_TGROUP;
```

**T_GROUP Structure (`ichitaut.h`, lines 146-169):**
```c
typedef struct tagTautomerGroup {
    AT_RANK num[T_NUM_NO_ISOTOPIC + T_NUM_ISOTOPIC];  // Mobile counts
    AT_RANK num_DA[TG_NUM_DA];    // Donor/Acceptor counts
    T_GROUP_ISOWT iWeight;        // Isotopic weight key
    AT_NUMB nGroupNumber;        // Positive tautomer group ID = atom->endpoint
    AT_NUMB nNumEndpoints;       // Number of endpoints in this group
    AT_NUMB nFirstEndpointAtNoPos; // First index in nEndpointAtomNumber[]
} T_GROUP;
```

**T_ENDPOINT Structure (`ichitaut.h`, lines 251-269):**
```c
typedef struct tagTautomerEndpoint {
    AT_RANK num[T_NUM_NO_ISOTOPIC + T_NUM_ISOTOPIC];
    AT_RANK num_DA[TG_NUM_DA];
    AT_NUMB nGroupNumber;        // Tautomer group number
    AT_NUMB nEquNumber;          // Equivalence number for connected endpoints
    AT_NUMB nAtomNumber;        // Actual atom number
} T_ENDPOINT;
```

**InChI Tautomer Storage (`ichi.h`, line 229):**
```c
AT_NUMB *nTautomer;  // NumGroups; ((NumAt+1, NumH, At1..AtNumAt),...)
```

**Length Field (`ichi.h` and `strutil.c`):**
```c
int lenTautomer;  // Length of the nTautomer array
```

### Key Constants

**From `mode.h` (lines 775-785):**
```c
#if ( REMOVE_TGROUP_CHARGE == 1 )
#define INCHI_T_NUM_MOVABLE  1    // H only (charge removed from t-groups)
#else
#define INCHI_T_NUM_MOVABLE  2    // H + negative charges
#endif
```

**From `inchi_api.h` (line 107):**
```c
#define NUM_H_ISOTOPES  3         // Protium (1H), Deuterium (2H), Tritium (3H)
```

### Tautomer Group Header Format

The Linear CT Tautomer format stored in `nTautomer[]` follows this structure for each tautomeric group:

```
[Header]
  [0]          = Number of tautomeric groups (total across all components)
  [for each group #g]
    [g+1]      = Number of endpoints + INCHI_T_NUM_MOVABLE
    [next INCHI_T_NUM_MOVABLE entries]
                = Number of mobile H atoms, negative charges, etc.
    [next (endpoints) entries]
                = Canonical numbers of atoms in this tautomeric group
```

The memory allocation in `strutil.c` (line 7745):
```c
pINChI->nTautomer = (AT_NUMB *)inchi_calloc(
    ((3 + INCHI_T_NUM_MOVABLE) * num_at) / 2 + 1,
    sizeof(pINChI->nTautomer[0])
);
```

## Pseudo-code Algorithm

### Mobile-H Detection Algorithm

```
function DetectMobileHydrogens(molecule):
    // Step 1: Initialize BNS (Balanced Network Structure)
    pBNS = CreateBNS(molecule)
    
    // Step 2: Identify centerpoint candidates
    for each atom in molecule:
        if is_centerpoint_elem(atom):
            centerpoints.add(atom)
    
    // Step 3: Find tautomeric groups
    for each centerpoint in centerpoints:
        // Examine bonds to potential endpoints
        endpoints = find_endpoint_neighbors(centerpoint, pBNS)
        
        if endpoints.count >= 2:
            // Step 4: Test donor/acceptor requirements
            has_donor = endpoints.has_mobile_H_or_charge()
            has_acceptor = endpoints.has_acceptor_capacity()
            
            if has_donor and has_acceptor:
                // Step 5: Find accessible endpoints via BFS
                accessible = FindAccessibleEndPoints(pBNS, endpoints)
                
                // Step 6: Register tautomer group
                RegisterEndPoints(t_group_info, accessible)
```

### RegisterEndPoints Function (`ichitaut.c`, lines 1021-1150)

```
function RegisterEndPoints(t_group_info, EndPoint[], nNumEndPoints):
    t_group = t_group_info.t_group
    num_t = t_group_info.num_t_groups
    
    // Find maximum existing group number
    nNextGroupNumber = find_max_group_number(t_group) + 1
    
    // Determine endpoint grouping
    for each endpoint in EndPoint:
        if endpoint.nGroupNumber != 0:
            merge_into_existing_group(endpoint)
        else if endpoint.nEquNumber matches other:
            merge_by_equivalence(endpoint)
        else:
            create_new_t_group(endpoint)
    
    // Update group membership
    for each merged group:
        assign_new_group_numbers()
    
    return number_of_changes
```

### Endpoint Classification (`ichitaut.c`, lines 359-448)

```
function nGetEndpointInfo(atom, iat):
    // Determine if atom can be an endpoint
    
    // Reject radicals (except singlet)
    if atom.radical and atom.radical != RADICAL_SINGLET:
        return 0
    
    // Get standard valence for element
    nEndpointValence = get_endpoint_valence(atom.el_number)
    
    if nEndpointValence <= atom.valence:
        return 0  // Cannot be endpoint (e.g., >N(+) or >O(-))
    
    // Check for mobile hydrogen or charge
    nMobile = atom.num_H + (atom.charge == -1)
    
    if nMobile + atom.chem_bonds_valence != nEndpointValence:
        return 0  // Non-standard valence
    
    // Classify as donor or acceptor
    if atom.chem_bonds_valence == atom.valence:
        eif.cDonor = 1      // Neutral donor
    else:
        eif.cAcceptor = 1    // Acceptor
    
    return nEndpointValence
```

### Atom-to-Numbers Aggregation (`ichitaut.c`, lines 211-246)

```
function AddAtom2num(num[], atom, at_no, bSubtract):
    // Aggregate atom properties into tautomer group counts
    
    nMobile = (atom.charge == -1)
    
    if bSubtract == 1:
        num[1] -= nMobile
        nMobile += atom.num_H
        num[0] -= nMobile
        // Subtract isotopic H
        for k in 0..T_NUM_ISOTOPIC-1:
            num[T_NUM_NO_ISOTOPIC + k] -= atom.num_iso_H[NUM_H_ISOTOPES - k - 1]
    else:
        // Add to counts
        num[1] += nMobile
        nMobile += atom.num_H
        num[0] += nMobile
        // Add isotopic H
```

## Examples

### Keto-Enol Tautomerism

**Compound:** Acetylacetone (2,4-pentanedione)
```
     O           OH
     ||    <=>    |
  O=C-CH2-C=   HO-C-CH2-C
```

**InChI Output:**
```
InChI=1S/C5H8O2/c1-4(6)5-2-3/h1,3H2/t6/m0/s1
```

Breaking down the layers:
- `/c1` — Main layer (formula, connections, H-fixed)
- `/h1` — Fixed hydrogen layer
- `/f` — Charges (if any)
- `/i` — Isotopic layer
- Mobile-H would appear as `/m` if tautomerism is significant

**Note:** The Mobile-H layer in standard InChI may be omitted for some keto-enol tautomers depending on the relative stability of the forms. The algorithm in `ichitaut.c` handles various proton transfer patterns including:

- PT_22_00: 1,2-proton transfer (e.g., keto-enol in aldehydes/ketones)
- PT_16_00: 1,6-proton transfer 
- PT_06_00: 1,6-proton transfer with aromatic systems
- PT_39_00, PT_13_00, PT_18_00: Various ring-fused systems

### Amide Tautomerism

**Compound:** Acetamide (or primary amides in general)
```
     O           OH
     ||    <=>    |
  CH3-C-NH2  CH3-C=N-H
```

**InChI Output:**
```
InChI=1S/C2H5NO/c1-2(3)4-5/h3H2/t5/m0/s1
```

### Generic Output Format

The actual string format for the Mobile-H layer is produced by `MakeTautString()` in `ichiprt2.c` (lines 1167-1330):

```
N      = number of tautomeric groups
n      = number of endpoints + 1 in a tautomeric group #1
h      = number of hydrogen atoms in the tautomeric group
m      = number of negative charges
c(1..n-1) = canonical numbers of atoms in the t-group
```

Example with actual numbers:
- `/m+1` — One tautomeric group with +1 mobile hydrogen
- `/m-1` — One tautomeric group losing 1 hydrogen (common in deprotonation)
- `/m+2` — Two mobile hydrogens in the tautomeric system
- `/m+2(2,1)(4,5)` — Two tautomeric groups; first has atoms 2,1; second has 4,5

## Additional Patterns

### Ring Tautomerism

The InChI library handles special ring tautomerism patterns:

| Pattern | Function | Description |
|--------|---------|------------|
| 1,5-Tautomer in 6-membered ring | `nGet15TautIn6MembAltRing()` | Proton transfer in alternate 6-membered rings |
| 1,2-Tautomer in 5-membered ring | `nGet12TautIn5MembAltRing()` | Proton transfer in alternate 5-membered rings |
| 1,4-Tautomer in 7-membered ring | `nGet14TautIn7MembAltRing()` | Extended ring systems |
| 1,5-Tautomer paths | `nGet15TautInAltPath()` | General alternate path finding |

These are defined in `ichitaut.c` (lines 422-476) and are activated via mode flags in `mode.h`.

### Charged Groups (Onium Ions)

The code also handles charged tautomeric groups:

```c
typedef struct tagChargeGroup {
    AT_RANK num[2];    // [0]: number of (+), [1]: atoms that have H
    AT_RANK num_CPoints;
    AT_NUMB nGroupNumber;
    U_CHAR cGroupType;
} C_GROUP;
```

Salt tautomerism (for compounds like carboxylic acids) is handled by `MergeSaltTautGroups()` (lines 3953-4150), allowing the merging of salt-forming groups when acidic protons are present.

---

*Mobile-H layer analysis: 2026-04-22*