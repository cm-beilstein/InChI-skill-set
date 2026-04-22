# Mathematical Handling of Mobile Hydrogens and Tautomerism in InChI

**Analysis Date:** 2026-04-22

## 1. Overview

**Prototropic tautomerism** is a reversible intramolecular movement of a hydrogen atom (proton) from one atom to another, accompanied by simultaneous movement of electrons to preserve bond orders. This phenomenon requires mathematical treatment because, for a given molecule, multiple equivalent tautomeric representations exist that differ only in hydrogen positions. The InChI identifier must be **tautomer-invariant**: regardless of which tautomeric form is input, the resulting Standard InChI string represents the same mobile-hydrogen equivalence class.

The mathematical core of InChI's tautomerism handling involves:
- Identifying tautomeric endpoints (atoms that can donate or accept mobile protons)
- Finding valid proton migration paths through the molecular graph
- Enumerating all tautomers and selecting a canonical representation
- Encoding mobile hydrogen information in the `/m` layer

## 2. Mobile Hydrogen Problem

### 2.1 Hydrogen Can Move Between Atoms

In prototropic tautomerism, a hydrogen atom can shift between two or more positions within a molecule, typically involving a centerpoint atom (C, N, O, S) connected to endpoint atoms through alternating double/single bonds:

```
R-C(=O)-CH₂-R'  ⇌  R-CH(OH)=C(R')-H
     keto form                   enol form
```

The hydrogen migrates from the α-carbon to the carbonyl oxygen, with a corresponding shift in the double bond.

### 2.2 Multiple Equivalent Representations

For acetone (CH₃-C(O)-CH₃), both the keto and enol forms are chemically valid and interconvertible. Input files may specify either form, but InChI must produce the same canonical identifier. Similarly, formamide (HCONH₂) can exist as:

```
    O              OH
    ‖    ←═══→    |
  H-C-NH₂      H-C=NH
```

### 2.3 Tautomer Invariance Requirement

**Standard InChI is tautomer-invariant**: This is a fundamental requirement. The canonicalization process selects a single tautomeric form based on atomic priorities, charge/neutrality preferences, and aromaticity considerations. The `/m` layer then records which atoms participate in the tautomeric group, enabling applications to recognize that different tautomeric structures are equivalent.

## 3. Tautomer Rules

InChI defines 11 basic tautomer rules (PT_02 through PT_12) governing which atom combinations can participate in prototropic shifts. These are SMIRKS-like transformations specifying donor-acceptor pairs and allowed migration paths.

| Rule | Description | Transformation |
|------|------------|--------------|
| PT_02_00 | Keto-enol | -C(=O)-CH₂- ↔ -CH(OH)=C- |
| PT_03_00 | Amido-imidol | -C(=O)-NH₂ ↔ -C(-OH)=NH |
| PT_04_00 | Enamine-imine | -C=NH ↔ -CH-NH₂ |
| PT_05_00 | Nitroso-oxime | |
| PT_06_00 | Selenium analogs | |
| PT_07_00 | Nitro-aci form | |
| PT_08_00 | Guanidine | |
| PT_09_00 | Hydroxamic acid | |
| PT_10_00 | Phosphonic/phosphinic | |
| PT_11_00 | Sulfinic/sulfonic acid | |
| PT_12_00 | Special heterocyclic | |

### 3.1 1,3-H Shifts (Most Common)

The **1,3-proton shift** is the most common tautomeric pattern, where a proton moves three atoms along a bond path:

```
Atom A — Atom B — Atom C — Atom D(accepts H)
   donor         migration path
```

This includes keto-enol (A=O, B=C, C=C, D=O as acceptor), amido-imidol, and most standard tautomerisms.

### 3.2 1,5-H Shifts in Aromatic Systems

In aromatic heterocycles, **1,5-proton shifts** occur through 5-membered transition states:

```
Pyrazole:  N—N(1)—C—C—C—N(5)—H
                     ↑                ↑
                  donor            acceptor
```

Special functions handle ring tautomerism:
- `nGet15TautIn6MembAltRing()` - 6-membered rings (1,6-shift)
- `nGet12TautIn5MembAltRing()` - 5-membered rings (1,2-shift)
- `nGet14TautIn7MembAltRing()` - 7-membered rings
- `nGet15TautInAltPath()` - General alternating path finding

## 4. Tautomer Graph Representation

### 4.1 T-Group (Tautomer Group) Structure

The tautomer group (T_GROUP) is defined in `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h:146`:

```c
typedef struct tagTautomerGroup {
    AT_RANK num[T_NUM_NO_ISOTOPIC + T_NUM_ISOTOPIC];  // Mobile counts
    AT_RANK num_DA[TG_NUM_DA];                    // Donor/Acceptor counts
    T_GROUP_ISOWT iWeight;                      // Isotopic weight key
    AT_NUMB nGroupNumber;                      // Tautomer group ID
    AT_NUMB nNumEndpoints;                    // Number of endpoints
    AT_NUMB nFirstEndpointAtNoPos;           // First index in endpoint array
} T_GROUP;
```

Where `T_NUM_NO_ISOTOPIC = 2` (mobile H + negative charges) and `T_NUM_ISOTOPIC = 3` (1H, D, T).

### 4.2 Endpoint Definition

Endpoints are atoms that can donate or accept mobile protons. The `T_ENDPOINT` structure (`ichitaut.h:251`) stores:

```c
typedef struct tagTautomerEndpoint {
    AT_RANK num[T_NUM_NO_ISOTOPIC + T_NUM_ISOTOPIC];
    AT_RANK num_DA[TG_NUM_DA];
    AT_NUMB nGroupNumber;    // Which t-group it belongs to
    AT_NUMB nEquNumber;    // Equivalence number for connected endpoints
    AT_NUMB nAtomNumber;   // Actual atom number in molecule
} T_ENDPOINT;
```

### 4.3 Mobile-H as Edges Between Endpoints

Mobile hydrogens are represented as **edges** connecting endpoints within a tautomer group. The `T_GROUP_INFO` structure (`ichitaut.h:222`) contains:

```c
typedef struct tagTautomerGroupsInfo {
    T_GROUP   *t_group;                   // Array of tautomer groups
    AT_NUMB   *nEndpointAtomNumber;         // Endpoint atom indices
    int       nNumEndpoints;              // Total endpoints
    int       num_t_groups;              // Number of t-groups found
    // ...
} T_GROUP_INFO;
```

## 5. Tautomer Enumeration

### 5.1 Generating All Possible Tautomers

The algorithm enumerates all valid tautomers by:
1. Finding all centerpoint atoms (C, N, P, S, halogens)
2. Identifying endpoint atoms that can donate/accept H
3. Finding valid proton migration paths via BFS/DFS

From `ichitaut.c:nGet15TautInAltPath()`. Paths must:
- Have alternating double/single bonds
- Maintain proper valence at all atoms
- Be within maximum path length (typically 5-6 atoms)

### 5.2 Ranking Each Tautomer

Each tautomer is ranked based on:
- **Aromaticity preference**: Aromatic tautomers preferred
- **Electronegativity**: More electronegative acceptor atoms preferred for H
- **Charge neutrality**: Neutral forms preferred over charged
- **Isotopic weight**: Non-isotopic preferred

The `T_GROUP_ISOWT` key encodes isotopic composition:
```c
iWeight = num_1H + T_GROUP_ISOWT_MULT * (num_D + T_GROUP_ISOWT_MULT * num_T)
// T_GROUP_ISOWT_MULT = 1024
```

### 5.3 Selecting Canonical Representation

The canonical tautomer is selected using the ranking criteria. The algorithm in `CompRankTautomer()` (`ichitaut.c`) compares tautomers by:
1. Number of mobile hydrogens
2. Isotopic composition
3. Endpoint canonical ranks

## 6. InChI Layer Construction

### 6.1 /m Layer for Mobile-H

The Mobile-H layer encodes which atoms participate in tautomeric groups. Format:

```
/m{count}{sign}({endpoint1},{endpoint2},...)
```

- `{count}`: Number of mobile H atoms
- `{sign}`: `+` = gained (more H than standard), `-` = lost (fewer H)
- `{endpointN}`: Canonical atom numbers

Examples:
- `/m+1` — One mobile hydrogen
- `/m-1` — Losing one hydrogen (common for anions)
- `/m+2(2,5)(7,10)` — Two tautomer groups

### 6.2 /h Layer for Fixed-H

The Fixed-H layer (`/h`) stores non-mobile hydrogens that were explicitly added during normalization. Format mirrors `/m`:

```
/h{count}({endpoint1},{endpoint2},...)
```

When tautomeric H is fixed at a specific position, it appears in `/h`, not `/m`.

### 6.3 nTautomer Array Format

The internal storage in `nTautomer[]` (`ichi.h`) uses Linear CT format:

```
[0]            = Total number of t-groups
[for each group g]
  [g+1]       = Number of endpoints + INCHI_T_NUM_MOVABLE
  [next entries]= Mobile counts (num_H, num_charges, isotopic)
  [remaining]  = Canonical endpoint numbers
```

Memory allocation (`strutil.c`):
```c
pINChI->nTautomer = (AT_NUMB *)inchi_calloc(
    ((3 + INCHI_T_NUM_MOVABLE) * num_at) / 2 + 1,
    sizeof(pINChI->nTautomer[0])
);
```

## 7. Mathematical Formulas

### 7.1 Tautomer Group Representation

For a tautomer group G with n endpoints {e₁, e₂, ..., eₙ}:

```
T_G = { endpoints: [rank(e₁), rank(e₂), ..., rank(eₙ)],
       mobile_H: Σ num_H(eᵢ),
       mobile_-: Σ (charge(eᵢ) == -1) }
```

### 7.2 Endpoint Distance Calculation

Valid tautomeric paths are found by BFS. The distance d between endpoints is:

```
d(endpoint_a, endpoint_b) = min_path_length(a, b)
```

Path is valid if:
- Path length ≤ MAX_ALT_PATH_LEN (typically 5-6)
- Alternating bond orders along path
- All atoms maintain valence constraints

### 7.3 Mobile-H Mapping to Canonical Numbers

The canonical ordering maps tautomer endpoints to canonical atom numbers:

```
canonical_pos(e) = Rank[e]
```

The mobile-H layer stores sorted canonical positions:

```
/m{h_count}+{sign}/ → sorted([canonical_pos(e₁), ..., canonical_pos(eₙ)])
```

## 8. Code Location

| Component | File | Key Functions |
|-----------|------|----------------|
| Tautomer detection | `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c` | `DetectTautomers()`, `nGetEndpointInfo()` |
| Endpoint registration | `ichitaut.c` | `RegisterEndPoints()` |
| Ring tautomerism | `ichitaut.c` | `nGet15TautIn6MembAltRing()`, `nGet12TautIn5MembAltRing()` |
| Path finding | `ichitaut.c` | `nGet15TautInAltPath()`, `FindAccessibleEndPoints()` |
| Canonicalization | `INCHI-1-SRC/INCHI_BASE/src/ichirvr*.c` | `CanonTaut()`, `CompRankTautomer()` |
| T-group structure | `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h` | `T_GROUP`, `T_ENDPOINT`, `T_GROUP_INFO` |

## 9. Examples

### 9.1 Acetone (Keto-Enol)

```
Input (keto):    CH₃-C(=O)-CH₃
Input (enol):    CH₂=C(OH)-CH₃

Output:         InChI=1S/C3H6O/c1-3(4)2/h1-2H3
/m layer:       /m1+1c2    (1 endpoint, 1 mobile H at canonical position 2)
```

- Carbonyl O (position 1) accepts H
- α-carbon (position 2) donates H
- Endpoint: canonical position 2
- Mobile H count: 1

### 9.2 Formamide

```
Input:    HCONH₂

Output:  InChI=1S/CH3NO/c2-1-3/h1H2,2H
/m layer: /m1+1c3    (N accepts H: canonical position 3)
```

The amide nitrogen and carbonyl oxygen form the tautomeric pair:
- Amide form: -C(=O)-NH₂ (more stable)
- Imidol form: -C(-OH)=NH

### 9.3 Pyridine-N-Oxide

```
Input:    C₅H₅NO

Process:  N-oxide has mobile H on ring nitrogens
         1,5-H shift through aromatic system
         
Output:  Mobile H layer captures N atoms
```

## 10. References

1. **InChI Technical Manual, Section III: Mobile Hydrogen** - Official InChI Trust documentation on tautomerism handling

2. Guasch, L.; et al. (2014). "The InChI for Tautomeric Forms." *J. Chem. Inf. Model.*, 54, 2423-2432. DOI: 10.1021/ci500209a

3. IUPAC Gold Book - Definition of prototropic tautomerism

4. Source code:
   - `INCHI-1-SRC/INCHI_BASE/src/ichitaut.c` (~7000 lines)
   - `INCHI-1-SRC/INCHI_BASE/src/ichitaut.h`
   - `INCHI-1-SRC/INCHI_BASE/src/ichirvr1.c` through `ichirvr7.c`

---

*Mathematical tautomerism analysis: 2026-04-22*