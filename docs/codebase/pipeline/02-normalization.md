# InChI Normalization Step

**Analysis Date:** 2026-04-22

## Overview

The **Normalization** step is the second major processing stage in the InChI pipeline. It transforms the preprocessed molecular structure into a standardized internal representation that enables consistent canonicalization and identifier generation.

Normalization addresses a fundamental challenge in chemical identifiers: the same molecule can be represented in many different ways depending on how bonds are drawn, how tautomeric forms are represented, and how mobile hydrogen atoms are positioned. The normalization step resolves these ambiguities by applying a standardized transformation that produces a canonical representation suitable for generating unique, reproducible InChI strings.

The normalization process succeeds the **Preprocessing** step (Step 1) and precedes **Canonicalization** (Step 3). According to the processing order documented in `runichi.c` (lines 930-958), normalization is applied to the preprocessed structure (`prep_inp_data[0]`) to create normalized data (`inp_norm_data[0,1]`), which then serves as input for creating the final InChI output.

The key normalization functions are located in:
- `INCHI-1-SRC/INCHI_BASE/src/ichi_bns.c` - Contains `mark_alt_bonds_and_taut_groups()`, the main normalization procedure
- `INCHI-1-SRC/INCHI_BASE/src/ichinorm.c` - Contains ring system marking, underivatization, and auxiliary normalization functions
- `INCHI-1-SRC/INCHI_BASE/src/ichinorm.h` - Header file with normalization function declarations

## IUPAC Rules and Standards

The InChI normalization procedures are governed by IUPAC recommendations to ensure consistent, reproducible chemical identifiers across different software implementations and data sources.

### Normalization Principles

Per **InChI Technical Manual Section III: Normalization**, the core principle is:

> Normalization removes drawing artifacts while maintaining a complete chemical description. The standardized representation must be chemically meaningful and suitable for generating unique, reproducible identifiers.

**Key Principles:**
- **Chemical Equivalence**: Different representations of the same molecule must produce identical normalized structures
- **Minimal Transformation**: Apply only transformations necessary to achieve canonical representation
- **Preservation of Information**: No chemically significant information (atoms, bonds, stereochemistry) may be lost during normalization
- **Deterministic Output**: Same input always produces same normalized output regardless of original drawing convention

### IUPAC Structure Conventions

The InChI uses the following structure conventions, documented in the InChI Technical Manual:

1. **Bond Order Standardization**
   - Aromatic bonds (delocalized) are converted to alternating single/double bonds
   - Coordinate bonds to metals are flagged for special handling
   - Implicit hydrogens are counted according to standard valences

2. **Proton Accounting**
   - Protons attached to heteroatoms (N, O, P, S) are tracked explicitly
   - pKa-based proton transfer is applied to acids and bases
   - Mobile hydrogen positions are normalized to standard locations

3. **Charge Distribution**
   - Formal charges are distributed according to electronegativity
   - Zwitterionic forms are identified and standardized
   - Charge annihilation rules apply to certain tautomeric reactions

### Specific Normalization Rules

#### Salt Disconnection

Per IUPAC definition, salts are ionic compounds where one component is a cation (typically metal or ammonium) and the other is an anion. InChI normalization:

- **Disconnection Criteria**: Salt components are disconnected when:
  1. Bond between cation and anion is purely ionic (no covalent character)
  2. Component can exist independently with valid valence
  3. Stoichiometry allows clean separation

- **Implementation**: The `bDisconnectSalts` flag enables salt disconnection via `inchi_flag.h` settings
- **Tautomer Interaction**: Salt and tautomer groups may interact; `MergeSaltTautGroups()` handles this

#### Mobile Hydrogen Normalization (Prototropic Tautomerism)

IUPAC rules for prototropic tautomerism (hydrogen migration):

1. **Endpoint Definition**: Mobile hydrogens migrate between designated endpoint atoms
2. **Valid Endpoints**: O, N, S atoms capable of bearingmobile protons
3. **Path Constraints**: Migration occurs along conjugated pathways
4. **Standard Form**: The form with lowest energy (typically keto over enol) is preferred

- **BNS Algorithm**: Balanced Network Structure solves optimal hydrogen placement
- **Tautomer Groups**: Marked via `MarkTautomerGroups()` in `ichinorm.c`
- **Excluded Cases**: Nitro, nitroso, phosphonate groups are NOT tautomeric per IUPAC rules

#### Charge Annihilation Rules

Charge cancellation via proton transfer:

| Transformation | Condition | Result |
|----------------|-----------|--------|
| +1 and -1 adjacent | Proton migrates | Neutral molecule |
| Carboxylate + ammonium | Proton transfer | Zwitterion |
| Metal cation + anion | Disconnection | Separate components |

- **Flag**: `FLAG_PROTON_CHARGE_CANCEL` tracks charge annihilation events
- **Priority**: Charge annihilation takes precedence over tautomerism

#### Metal Disconnection Rules

Per InChI Technical Manual:

- **Coordination Bonds**: Bonds to metals are flagged but generally preserved
- **Disconnection Option**: `bDisconnectCoord` enables cleavage of metal-ligand bonds
- **Valid Metals**: Alkali metals (Li, Na, K), alkaline earth (Mg, Ca) typically disconnected
- **Transition Metals**: Generally retained due to complex coordination chemistry

### Standard InChI Requirements

An InChI is considered **"Standard InChI"** per IUPAC when:

1. **Complete Representation**: All atoms, bonds, charges, and stereochemistry encoded
2. **Normalization Applied**: Drawing artifacts removed via IUPAC-compliant normalization
3. **Isotopic Handling**: Deuterium (D) and tritium (T) distinguished from hydrogen (H)
4. **Mobile H Flag**: `/h` layer present when tautomeric protons exist
5. **Charge Layers**: `/p` and `/q` layers present when applicable

**Standard vs. Non-Standard InChI:**
| Feature | Standard | Non-Standard |
|---------|----------|---------------|
| Mobile H tracking | Required | Optional |
| Isotopic marking | Required | Optional |
| Stereo layers | Complete | Simplified |
| Retransformability | Guaranteed | Best effort |

### Source References

**Primary Documentation:**
- **InChI Technical Manual**, Section III: Normalization
  - URL: https://www.inchi-standard.org/docs/stdfix.html
  - Covers: bond order, proton, charge, and tautomer normalization rules

- **IUPAC InChI FAQ**, Question 7: Standardization
  - URL: https://www.iupac.org/news-and-events/news/detail/inchi-faq/
  - Clarifies: distinction between Standard and Non-Standard InChI

- **IUPAC InChI Project Documentation**
  - URL: https://www.inchi-standard.org/
  - Technical specifications and implementation guidelines

## Input

### From Previous Step (Preprocessing)

The normalization step receives a preprocessed molecular structure that has already undergone:
1. Copy from original input data to working buffer
2. Correction of odd/incorrect structural features
3. Salt disconnection (if enabled via `bDisconnectSalts`)
4. Proton movement to neutralize charges on heteroatoms
5. Metal disconnection (if enabled via `bDisconnectCoord`)

The preprocessed data is stored in the `prep_inp_data` structure and contains an array of `inp_ATOM` structures representing atoms with their bonds, charges, radicals, and implicit hydrogen counts.

### Internal Structures

**Primary Input Structure (`inp_ATOM` array):**
```c
// From mode.h - atom representation
typedef struct tagINChI_Atom {
    AT_NUMB      el_number;        // Element number (periodic table)
    char         elname[ATOM_EL_NAME_LEN]; // Element symbol
    AT_NUMB      neighbor[MAXVAL]; // Atom indices of neighbors
    S_CHAR       bond_type[MAXVAL]; // Bond order (single=1, double=2, triple=3, aromatic=4)
    // ... additional fields for charges, radicals, stereochemistry, etc.
} inp_ATOM;
```

**Tautomer Group Information (`T_GROUP_INFO`):**
```c
// From ichitaut.h - tautomer tracking
typedef struct tagTautomerGroupsInfo {
    T_GROUP   *t_group;              // Array of tautomer groups
    AT_NUMB   *nEndpointAtomNumber;  // Endpoint atom numbers
    AT_NUMB   *tGroupNumber;         // Group membership for each atom
    int       num_t_groups;          // Number of tautomer groups found
    INCHI_MODE bTautFlags;          // Processing flags
    INCHI_MODE bTautFlagsDone;     // Completion flags
} T_GROUP_INFO;
```

**Charge Group Information (`C_GROUP_INFO`):**
Used to track and normalize charge distributions across the molecule, particularly for handling zwitterions and charged functional groups.

**Balanced Network Structure (`BN_STRUCT`):**
An internal graph representation used by the normalization algorithm to solve the optimization problems involved in standardizing bond orders and charge distributions.

## Output

### Normalized Structures

The normalization step produces one or two normalized structures depending on the processing mode:

1. **Non-tautomeric normalized structure** (`inp_norm_data[TAUT_NON]`): Contains the standardized representation without explicit mobile hydrogen tracking
2. **Tautomeric normalized structure** (`inp_norm_data[TAUT_YES]`): Contains the representation with tautomer groups explicitly marked

### Key Transformations Performed

**1. Aromatic Bond Resolution**
- Input aromatic bonds (represented as bond type 4 or higher) are analyzed and replaced with appropriate single/double bond alternation patterns
- The algorithm uses the Balanced Network Structure (BNS) to find optimal bond assignments that satisfy valence requirements
- From `ichinorm.c` line 5801-5860, the `replace_arom_bonds()` function:
  - Searches for non-standard bond types (> BOND_TRIPLE)
  - Maps them back to original atom numbers
  - Replaces aromatic bonds with explicit single/double bond orders

**2. Tautomer Group Identification**
- The algorithm identifies groups of atoms involved in prototropic tautomerism (mobile hydrogen migration)
- Each tautomer group is represented as a set of endpoint atoms between which hydrogen atoms can migrate
- The `MarkTautomerGroups()` function in `ichinorm.c` performs this analysis using graph algorithms

**3. Charge Group Standardization**
- Charge groups (collections of atoms with interdependent charges) are identified and standardized
- The `MarkChargeGroups()` function handles this, ensuring consistent charge representation
- Particularly important for zwitterions and metal coordination compounds

**4. Salt Group Processing**
- Salt components that were disconnected in preprocessing may be analyzed for tautomeric behavior
- The `MarkSaltChargeGroups()` and `MarkSaltChargeGroups2()` functions handle this analysis
- Salt and tautomer groups may be merged via `MergeSaltTautGroups()`

**5. Radical Handling**
- Aromatic radicals are specially processed via `BnsAdjustFlowBondsRad()` in `ichi_bns.c`
- Multiple radicals on adjacent atoms may be combined or neutralized
- From line 5296-5317, special handling exists for doublet radicals on atoms with alternating bonds

**6. Ring System Marking**
- The `MarkRingSystemsInp()` function in `ichinorm.c` (line 59) identifies:
  - Ring closures and ring systems
  - Cut vertices (atoms whose removal would disconnect the ring system)
  - Block systems (connected components after removing cut vertices)
- This information is crucial for understanding molecular topology during normalization

### Normalization Flags

The normalization process sets flags to track what transformations were applied (from `ichitaut.h` lines 181-210):
- `FLAG_PROTON_NPO_SIMPLE_REMOVED`: Simple proton removal from N,P,O
- `FLAG_PROTON_NP_HARD_REMOVED`: Complex proton removal from N,P
- `FLAG_PROTON_AC_SIMPLE_ADDED`: Simple proton addition to acid groups
- `FLAG_PROTON_AC_SIMPLE_REMOVED`: Simple proton removal from acid groups
- `FLAG_PROTON_CHARGE_CANCEL`: Charge cancellation via proton transfer

## Pseudo-code Algorithm

### Main Normalization Procedure

The primary entry point is `mark_alt_bonds_and_taut_groups()` in `ichi_bns.c`:

```
function mark_alt_bonds_and_taut_groups(at, num_atoms, t_group_info):
    
    // Step 1: Initialize data structures
    Initialize C_GROUP_INFO for charge groups
    Initialize S_GROUP_INFO for salt groups
    Initialize T_GROUP_INFO for tautomer groups
    
    // Step 2: Handle special aromatic radical cases
    for each atom i in structure:
        if atom has doublet radical AND valence == 2 
           AND both bonds are alternating:
            store radical state
            remove radical, add implicit H
    
    // Step 3: Allocate Balanced Network Structure
    pBNS = AllocateAndInitBnStruct(at, num_atoms)
    pBD = AllocateAndInitBnData(pBNS.max_vertices)
    
    // Step 4: Adjust bonds for aromaticity and radicals
    ret = BnsAdjustFlowBondsRad(pBNS, pBD, at, num_atoms)
    
    // Step 5: Charge group processing (if enabled)
    if TG_FLAG_MOVE_POS_CHARGES is set:
        c_group_info = allocate memory for charge groups
        MarkChargeGroups(at, num_atoms, c_group_info, t_group_info, pBNS, pBD)
    
    // Step 6: Salt group processing (if enabled)
    if TG_FLAG_TEST_TAUT__SALTS is set:
        s_group_info = allocate memory for salt candidates
        MarkSaltChargeGroups(at, num_atoms, s_group_info, t_group_info, c_group_info, pBNS, pBD)
        MarkSaltChargeGroups2(..., s_group_info, ...)
    
    // Step 7: Merge salt and tautomer groups (if applicable)
    if both salt and tautomer groups exist:
        MergeSaltTautGroups(at, num_atoms, s_group_info, t_group_info, c_group_info, pBNS)
    
    // Step 8: Tautomer group identification
    if TG_FLAG_VARIABLE_PROTONS is set:
        mark_at_type(at, num_atoms, nAtTypeTotals)
        if charges exist in structure:
            MarkTautomerGroups(at, num_atoms, t_group_info, c_group_info, pBNS, pBD)
    
    // Step 9: Isotopic tautomer group handling
    if isotopic atoms exist:
        MakeIsotopicHGroup(at, num_atoms, s_group_info, t_group_info)
    
    // Step 10: Mark ring systems for reference
    MarkRingSystemsInp(at, num_atoms, 0)
    
    return result_code
```

### Aromatic Bond Resolution

```
function replace_arom_bonds(at_normalized, at_original):
    
    for each atom i in normalized structure:
        for each bond j from atom i:
            if bond_type[j] > BOND_TRIPLE:  // aromatic or special
                // Find corresponding atoms in original structure
                orig_atom1 = at_original[at_normalized[i].orig_at_number]
                orig_atom2 = at_original[at_normalized[neighbor].orig_at_number]
                
                // Get bond type from original structure
                if bond exists between orig_atom1 and orig_atom2:
                    at_normalized[i].bond_type[j] = original_bond_type
                    at_normalized[neighbor].bond_type[corresponding] = original_bond_type
    
    return number_of_errors
```

### Ring System Marking

```
function MarkRingSystemsInp(at, num_atoms, start):
    
    // Use depth-first search to find ring systems
    initialize DFS numbering arrays
    initialize stack for atoms and rings
    
    // Start from specified atom
    push start atom onto stacks
    assign DFS number
    
    while stack is not empty:
        // Explore unvisited neighbors
        for each neighbor of current atom:
            if neighbor not visited:
                push neighbor to stack
                assign DFS and low-link numbers
            else if neighbor is on ring stack and not parent:
                // Found back edge - close a ring
                update low-link numbers
                if low-link condition met:
                    mark ring system
                    record cut vertices
    
    return number_of_ring_systems
```

## Examples

### Example 1: Benzene Aromatic Ring Resolution

**Input (after preprocessing):**
```
Benzene with aromatic bonds (bond type = 4):
  C1---C2 (aromatic)
  C2---C3 (aromatic)
  C3---C4 (aromatic)
  C4---C5 (aromatic)
  C5---C6 (aromatic)
  C6---C1 (aromatic)
```

**After Normalization:**
```
Benzene with alternating single/double bonds:
  C1=C2 (double)
  C2-C3 (single)
  C3=C4 (double)
  C4-C5 (single)
  C5=C6 (double)
  C6-C1 (single)
```

The normalization resolves the delocalized aromatic system into an explicit alternating pattern, which is essential for canonical ordering.

### Example 2: Acetophenone Tautomerization

**Input (enol form):**
```
Acetophenone in enol form:
  Ph-C(=O)-CH3  →  Ph-C(OH)=CH2
  
  Atoms:
    C(aromatic)-C(=O)-C
    Where C(=O) has double bond to O
    And C has one H (enol form)
```

**After Normalization:**
```
Mobile hydrogen atoms identified:
  - OH group hydrogen is mobile
  - Terminal =CH2 has mobile H atoms
  
Tautomer group endpoints marked:
  - O atom (one endpoint)
  - Terminal CH2 carbon (other endpoint)
  
Normalized representation tracks potential tautomer:
  - keto form: Ph-CO-CH3
  - enol form: Ph-C(OH)=CH2
```

### Example 3: Zwitterion Charge Normalization

**Input (amino acid with charges):**
```
Glycine zwitterion:
  H3N+(1)-CH(2)-COO-(3)
  
  Atom charges:
    N: +1
    C (alpha): 0
    O: -1
```

**After Normalization:**
```
Charge groups identified:
  - Positive group: H3N+
  - Negative group: COO-
  
Flags set:
  - FLAG_PROTON_CHARGE_CANCEL (to track potential charge neutralization)
  
Normalized structure maintains charges but marks them as part of interdependent charge groups for canonicalization
```

### Example 4: Acetic Acid Proton Handling

**Input:**
```
Acetic acid with acidic hydrogen:
  CH3-C(=O)-OH
  
  Where OH has one explicit hydrogen
  Carboxyl oxygen has implicit hydrogen count = 1
```

**After Normalization:**
```
If TG_FLAG_VARIABLE_PROTONS is set:
  - Acidic hydrogen may be moved to/from carboxylate
  - Creates tautomer-like structure:
    - Form A: CH3-C(=O)-OH
    - Form B: CH3-C(O-)=O + H+
  
Flags may include:
  - FLAG_PROTON_AC_SIMPLE_REMOVED (H moved from acid)
  - FLAG_PROTON_AC_SIMPLE_ADDED (H added to acid)
```

### Example 5: Nitro Group Non-tautomeric Treatment

**Input:**
```
Nitrobenzene:
  Ring-C(=O)-N(=O)=O  (actually: Ring-C(6H4)-NO2)
  
  Nitro group: N bonded to two oxygens
  Both N-O bonds are equivalent (delocalized)
```

**After Normalization:**
```
Nitro group standardized:
  - Both N=O bonds marked as equivalent
  - Treated as charge-delocalized group
  - NOT as tautomeric (hydrogen doesn't move)
  
The BNS algorithm ensures:
  - Negative charge is properly distributed
  - Both oxygens are equivalent in canonical form
```

---

*Normalization documentation: 2026-04-22*
