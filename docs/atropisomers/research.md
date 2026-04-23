# Atropisomers: Detection and Encoding Research Report

**Generated:** April 23, 2026  
**Sources:** 8+ academic and technical references  
**Confidence:** High (foundational chemistry) to Medium (computational implementation specifics)

---

## Executive Summary

Atropisomers are stereoisomers that arise from hindered rotation about single bonds, most commonly in substituted biaryl compounds like BINAP and binaphthols. Unlike traditional stereocenters (tetrahedral chirality), atropisomers exhibit **axial chirality**—a special form of 3D molecular asymmetry. Detection requires identifying high rotational barriers (typically >93 kJ/mol at 300 K, or ~22 kcal/mol per Ōki's definition), while encoding in chemical identifiers like InChI and SMILES follows Cahn–Ingold–Prelog (CIP) priority rules applied to an axial reference frame rather than a tetrahedral one. Current computational chemistry tools handle atropisomers inconsistently; most require manual stereochemical specification or fail to detect axial chirality algorithmically. InChI provides formal layers for encoding axial stereochemistry, but automated detection from 3D coordinates or connectivity alone remains a research-active area.

---

## 1. Definition and Chemistry of Atropisomers

### 1.1 What Are Atropisomers?

**Atropisomers** are a special class of stereoisomers arising from **hindered rotation about a single bond**, where steric strain or other contributors create a **barrier to rotation high enough to allow isolation of individual rotamers**.

**Key etymological note:** The term "atropisomer" comes from the Greek *atropos* ("not to be turned"), coined by Richard Kuhn in 1933 for Karl Freudenberg's *Stereochemie* volume. The first experimental observation was by Christie and Kenner in 1922, studying tetrasubstituted biphenyls like 6,6'-dinitro-2,2'-diphenylcarboxylic acid.

### 1.2 Axial Chirality

Atropisomers differ fundamentally from classical stereocenters:

- **Central (Point) Chirality:** A tetrahedral carbon bonded to four distinct groups (C-abcd).
- **Axial Chirality:** Chirality arises from a **chiral axis** (usually a constrained bond) rather than an asymmetric atom. The axis itself is the locus of stereochemistry, not a point in space.

In atropisomers, two pairs of chemical groups are arranged in a **non-planar** configuration about an axis of hindered rotation such that the molecule is **not superimposable on its mirror image**.

### 1.3 Energetic Definition (Ōki Criterion)

Michinori Ōki refined atropisomer definition by temperature-dependent interconversion kinetics:

> **An atropisomer is defined as having a half-life (t₁/₂) of at least 1000 seconds at a given temperature, corresponding to an activation energy barrier of ~93 kJ/mol (22 kcal/mol) at 300 K (27 °C).**

This quantitative threshold distinguishes true atropisomers from rapid conformational fluxes. Stability is conferred by **repulsive interactions inhibiting rotation**, involving:
- Steric bulk of ortho and meta substituents
- Bond length and rigidity
- Electronic effects

### 1.4 Structural Classes

**Biaryl compounds (most common):**
- **Biaryls** (e.g., biphenyl with ortho/meta substitution)
- **Binaphthyls** (e.g., BINAP, BINOL)
- **Heteroaromatic analogues** (C-N, N-N bonds)

**Other classes:**
- **Amides and thioamides** — Partial double-bond character of C-N bonds creates barriers
- **Allenes** — C=C=C structural motif with attached groups
- **Cycloaliphatic systems** — Rigidly fused ring systems

### 1.5 Isomeric Classification

When rotation barriers permit isolation, two cases arise:

| Case | Substituent Status | Isomer Type | Enantiomers |
|------|-------------------|------------|-----------|
| **Achiral substituents** | All groups are identical pairs | Enantiomers (atropoenantiomers) | Yes, mirror images |
| **Chiral substituents** | Differ by stereochemistry | Diastereomers (atropodiastereomers) | No, not mirror images |

---

## 2. Stereochemical Assignment and Nomenclature

### 2.1 Cahn–Ingold–Prelog (CIP) Rules for Axial Centers

Atropisomer stereochemistry is assigned using **CIP priority rules** adapted for axial reference frames:

1. **View along the chiral axis** (viewed end-on, not along individual bonds as in tetrahedral case).
2. **Identify substituent priority:**
   - Assign 1–4 to the four groups connected to the axis using standard CIP rules.
   - **Key modification:** "Near" substituents (front-facing from viewer) receive priority **1 and 2**, "far" substituents receive **3 and 4**, regardless of intrinsic CIP ranking.
3. **Determine configuration:** Trace from 1→2→3:
   - **Clockwise (right-handed helix):** Designated **R_a** or **P** (plus) or **Δ** (delta)
   - **Counterclockwise (left-handed helix):** Designated **S_a** or **M** (minus) or **Λ** (lambda)

### 2.2 Newman Projection Method

For biaryl atropisomers:
- View **along the C-C bond** connecting the two aromatic rings.
- Identify ortho/meta substituent priorities using standard CIP.
- Rank "front" pair (priorities 1, 2) > "back" pair (priorities 3, 4).
- Apply R/S or P/M nomenclature.

### 2.3 Helicity Notation (P/M, Δ/Λ)

For visually helical or propeller-shaped molecules:
- **P (plus) or Δ (delta):** Right-handed helix
- **M (minus) or Λ (lambda):** Left-handed helix

This notation is particularly useful for helicenes and molecules that resemble actual screws or propellers.

---

## 3. Detection Methods in Experimental and Computational Settings

### 3.1 Experimental Detection

**Dynamic Nuclear Magnetic Resonance (DNMR) Spectroscopy:**
- Most common experimental approach for atropisomers
- Atropisomerism is a form of **fluxionality** — molecule exchanges between rotamers on NMR timescale
- At low temperature: separate signals for each enantiomer/diastereomer
- At high temperature: coalescence of signals as rotamers interconvert rapidly
- Coalescence temperature and line-broadening can estimate activation energy barriers

**Other experimental methods:**
- **Theory and Hammett equation:** Correlate electronic effects with rotation barriers
- **Reaction outcomes and yields:** Stereoselective reactions reveal presence and stability of atropisomers
- **Crystallography (seed-directed):** Individual enantiomers can be isolated from racemates (e.g., 1,1'-binaphthyl)
- **Chiral HPLC:** Separates enantiomeric atropisomers for individual characterization

### 3.2 Computational Detection Approaches

#### 3.2.1 **Rotational Barrier Estimation**

**Molecular mechanics/dynamics:**
- Construct 3D conformers with Φ (dihedral angle) varied incrementally
- Calculate energy at each rotation angle using force fields (MMFF94, OPLS-AA, GAFF)
- Fit energy curve; barrier = E_max - E_min

**Limitations:**
- Force fields are parameterized for typical sp³-sp³ rotations; less reliable for sterically hindered aromatic rotations
- No single computational approach is universally accurate

**Quantum mechanical approaches (more accurate but slower):**
- DFT geometry optimization at multiple rotation angles (computationally expensive)
- Produces reliable barrier heights but requires significant computational resources

#### 3.2.2 **Steric Clash Detection**

**Graph-based algorithms:**
1. Parse molecular connectivity (atoms, bonds)
2. Calculate 3D coordinates via force field or empirical methods
3. Compute van der Waals distances between ortho/meta substituents across the hindered bond
4. Flag if substituents come into close contact (<van der Waals sum) — indicates high barrier

**Advantages:** Fast, does not require full optimization  
**Disadvantages:** Heuristic; electronic effects and partial double-bond character not captured

#### 3.2.3 **Automated Priority Assignment (CIP Algorithm)**

Converting CIP rules to code:

1. **Atomic number ranking:** Sort neighbors by atomic number (descending)
2. **Iterative refinement:** If ties exist, recursively rank neighbors of tied atoms
3. **Stereochemistry assignment:** Once priorities established, apply R/S or P/M rules via vector cross-product or lookup table

**Current status:**
- Well-established for tetrahedral centers (all modern cheminformatics libraries support this)
- Adapted for axial centers, but **not universally implemented** (many tools require manual input)

#### 3.2.4 **Current Limitations**

**Unresolved challenges:**

| Challenge | Issue | Impact |
|-----------|-------|--------|
| **Automated barrier estimation** | No consensus algorithm; force fields vary | Difficult to detect atropisomers purely from connectivity |
| **Partial double-bond effects** | Amides, thioamides not handled uniformly | Software may miss barriers from C-N π-character |
| **Detection from 2D SMILES/InChI** | No rotational information in linear notation | Atropisomer identity must be specified manually or from 3D structure |
| **3D conformer reliability** | Empirical methods sometimes fail; QM expensive | May not produce realistic geometries for unusual scaffolds |

---

## 4. Encoding Standards: InChI, SMILES, and Beyond

### 4.1 International Chemical Identifier (InChI)

InChI is the most formal standard for chemical structure representation, developed by IUPAC and maintained by the InChI Trust (since 2009).

#### InChI Layer Structure

InChI encodes information in ordered **layers and sub-layers**, separated by `/` delimiter:

```
InChI=1S/formula/c_connectivity/h_hydrogen/.../t_stereochemistry/m_mirroring/s_stereo_type/.../
```

**Relevant layers for atropisomers:**

| Layer | Sub-layer | Purpose | Example |
|-------|-----------|---------|---------|
| **Main** | `/c` | Atom connections (bond topology) | `/c1ccccc1-c2ccccc2` (biphenyl) |
| **Main** | `/h` | Hydrogen count | `/h1H,3H,4H,5H,6H,7H,9H,10H,11H,12H,13H,14H` |
| **Stereochemical** | `/b` | Double bonds and cumulenes | `/b1-,2-` (stereochemistry of double bonds) |
| **Stereochemical** | `/t` | Tetrahedral/tetrahedral stereo (and by extension, axial) | `/t1-` (S configuration on atom 1) |
| **Stereochemical** | `/m` | Mirroring (inverts /t) | `/m0` or `/m1` (toggles enantiomer) |
| **Stereochemical** | `/s` | Stereo type | `/s1` (absolute), `/s2` (relative), `/s3` (racemic) |

#### Axial Chirality Encoding in InChI

**Current practice:**
- InChI `/t` layer can encode both tetrahedral and **axial stereochemistry**
- A single `-` or `+` after an atom number indicates the atom's stereochemical configuration
- For axial centers (biaryl bonds), stereochemistry is typically assigned to one of the axial atoms involved
- The `/m` layer inverts stereochemistry if needed (e.g., to generate enantiomer)

**Example:**
- BINAP (a chiral binaphthyl ligand) has an InChI like: `InChI=1S/.../t6-,7+/m1/s1` (absolute stereochemistry on atoms 6 and 7, mirrored once)

**Standard InChI constraints:**
- `/s1` (absolute only) is mandatory; `/s2` and `/s3` not allowed in standard InChI
- `/f` (fixed-H), `/o`, `/r` layers are excluded
- Unknown stereochemistry treated as undefined (omitted)

#### Limitations of InChI for Atropisomers

1. **Implicit detection:** InChI does **not automatically detect** atropisomers from connectivity alone; stereochemistry must be provided in input
2. **No explicit axial marker:** Biaryl axis is treated like a tetrahedral stereocenter; no special layer distinguishes axial from point chirality
3. **Canonicalization ambiguity:** Which atom in a biaryl pair is tagged for stereochemistry can vary; algorithm standardizes this, but conversion tools must agree

### 4.2 Simplified Molecular Input Line Entry System (SMILES)

SMILES is a linear ASCII notation for molecular structure, less formal than InChI but widely supported.

#### Stereochemistry in SMILES

SMILES specifies **tetrahedral stereochemistry** via:
- `@` = counterclockwise (left turn)
- `@@` = clockwise (right turn)
- Applied to atoms with four distinct neighbors

**Example tetrahedral center:**
```
C[C@H](O)CC  = (S)-1-propanol enantiomer
C[C@@H](O)CC = (R)-1-propanol enantiomer
```

#### SMILES Representation of Atropisomers

**Challenge:** SMILES was designed for **2D/graph-based** representations; it lacks explicit **axial chirality** notation.

**Current workarounds:**
1. **Ignore stereochemistry:** Omit @ markers; SMILES becomes ambiguous but conveys connectivity
2. **Tetrahedral encoding hack:** Assign stereochemistry markers to aromatic atoms (nonstandard, tool-dependent)
3. **Extended notations:** Some implementations (e.g., OpenSMILES, proprietary variants) add custom markers for axial centers
4. **External metadata:** Store axial stereochemistry separately from SMILES string

**Practical limitation:** Most SMILES parsers cannot reliably reconstruct atropisomer stereochemistry from the string alone; 3D coordinates or explicit metadata required.

### 4.3 Other Notations

**Wiswesser Line Notation (WLN), ROSDAL, SLN:**
- Older or less common notations; generally do not handle atropisomers explicitly
- Limited modern adoption

**CAS Registry Numbers:**
- Proprietary numbers; assigned manually by Chemical Abstracts Service
- No algorithmic generation; do not encode stereochemical information

---

## 5. Key Findings: Computational Challenges and Gaps

### 5.1 Detection Challenges

| Challenge | Severity | Current Status |
|-----------|----------|-----------------|
| **Automated barrier prediction** | High | No universal algorithm; force-field dependent |
| **Partial double-bond effects** | High | Amides, thioamides handled inconsistently |
| **2D-to-stereochemistry inference** | Very High | Cannot determine from SMILES/InChI connectivity alone |
| **Heteroaromatic and non-biaryl scaffolds** | Medium | Most tools focus on biaryl; other classes underexplored |

### 5.2 Encoding Challenges

| Format | Strengths | Weaknesses |
|--------|-----------|-----------|
| **InChI** | Formal, standardized; `/t`, `/m`, `/s` layers cover absolute/relative/racemic | Requires pre-computed stereochemistry; no automated detection from connectivity |
| **SMILES** | Human-readable, widely supported | Not designed for axial chirality; @ markers ambiguous for aromatic systems |
| **3D Coordinates (PDB/MOL2)** | Unambiguous representation | Not a chemical "identifier"; file-size bloated; not human-readable |

### 5.3 Software Landscape

**Commercial tools (Chemaxon, OpenEye, etc.):**
- Provide API for CIP priority ranking (tetrahedral)
- Increasingly support extended stereochemistry metadata
- **Atropisomer handling:** Variable; often requires manual curation

**Open-source tools (Chemistry Development Kit, RDKit, OpenBabel):**
- Excellent tetrahedral stereochemistry support
- **Atropisomer support:** Limited or absent; no automated barrier estimation
- No widely-adopted algorithm for axial chirality detection from bare connectivity

**InChI software (official InChI library):**
- Generates/parses standard InChI with `/t` and `/m` layers
- Does **not** automatically detect atropisomers; treats as input-dependent

---

## 6. Canonical Representation and Canonicalization

### 6.1 InChI Canonicalization for Atropisomers

InChI applies a **Morgan-like algorithm** to canonicalize atom numbering:

1. **Rank atoms** by invariants (element, valence, connectivity)
2. **Refine iteratively** using neighbor information
3. **Assign canonical atom numbers** 1, 2, 3, ... in order of rank
4. **Encode stereochemistry** based on canonical numbering

For atropisomers:
- Stereochemical assignments (R/S, P/M) depend on canonical atom order
- Two different input forms of the same molecule converge to identical canonical InChI (including `/t` and `/m` layers)

**Advantage:** Unique identifier per structure  
**Disadvantage:** Requires accurate input stereochemistry; no self-detection

### 6.2 SMILES Canonicalization

Canonical SMILES generation algorithms (Daylight, OpenEye, CDK):
- Convert SMILES to internal molecular graph
- Apply graph canonicalization (e.g., based on Morgan algorithm)
- Emit unique canonical form

**For atropisomers:**
- Most algorithms treat biaryl bonds as single C-C; no special axial logic
- Stereochemistry markers (@, @@) preserved if present, but not verified for correctness
- Two representations of the same atropisomer may yield **different canonical SMILES** if input ordering differs

**No standard resolution:** Each toolkit has its own canonicalization; portable canonical forms are not guaranteed across tools.

---

## 7. Tautomerism and Atropisomerism Interaction

### 7.1 Tautomeric Normalization in InChI

InChI **normalizes tautomeric structures** to a canonical "core parent structure" during generation:

- Example: Acetic acid and acetate ion both normalize to acetic acid core parent
- Different tautomers have the **same standard InChI** but different non-standard InChI with fixed-H layer `/f`

### 7.2 Atropisomerism and Tautomerism Are Distinct

**Important distinction:**
- **Atropisomerism:** Hindered rotation about single/partial-double bond; high activation energy
- **Tautomerism:** Intramolecular proton transfer; typically lower barrier, interconvert readily

For molecules with both features (rare):
- InChI normalization applies first (tautomeric equilibration to core parent)
- Stereochemistry `/t` layer assigned to normalized form
- Atropisomerism encoded after tautomeric core established

---

## 8. Pharmaceutical and Practical Importance

### 8.1 Drug Molecules with Atropisomerism

**Methaqualone:**
- Classical anxiolytic/hypnotic drug
- Exhibits atropisomerism
- Different enantiomers have different bioactivity; FDA approval requires single enantiomer

**Others in development:**
- BINAP, BINOL ligands widely used in asymmetric synthesis
- Emerging atropisomeric scaffolds in oncology, CNS therapeutics

### 8.2 Stereoselectivity in Chemical Synthesis

**Asymmetric synthesis using atropisomeric ligands (e.g., BINAP):**
- Chiral catalyst transfers axial asymmetry to newly formed tetrahedrally chiral products
- Stereochemistry depends on maintaining atropisomer identity during reaction
- Enantiomeric purity must be assured through controlled synthesis or resolution

**Transient atropisomers:**
- Some reactions employ atropisomeric intermediates with lower barriers
- Must conduct reaction faster than racemization; timing critical

---

## 9. Current State-of-the-Art and Research Gaps

### 9.1 What Works Well

- **Detection via experimental methods:** DNMR, crystallography, chiral HPLC are gold standard
- **CIP priority assignment (tetrahedral):** Automated in all modern tools
- **InChI encoding:** Formal standard for structures with known stereochemistry
- **Visualization:** 3D modeling tools (PyMOL, Chimera, etc.) render atropisomers intuitively

### 9.2 Open Research Areas

1. **Automated axial chirality detection from 2D structure + 3D coordinates:**
   - Combine steric clash detection with rotational barrier estimation
   - Goal: No-prior-knowledge stereochemistry assignment

2. **Barrier prediction improvements:**
   - Machine learning models trained on QM data for barrier → stereochemistry correlation
   - Reduce reliance on expensive QM calculations

3. **Extended stereochemistry notation (SMILES):**
   - Standardize axial chirality markers in OpenSMILES or successor notation
   - Ensure parser agreement across tools

4. **Atropisomer databases:**
   - Curated collection of known atropisomeric structures with experimentally verified barriers
   - Enable training of predictive models

5. **Non-biaryl scaffolds:**
   - Characterize atropisomerism in amides, heteroaromatics, allenes
   - Develop detection rules beyond biaryl heuristics

---

## 10. Recommendations for InChI Skill Implementation

Based on the above findings, here are key considerations for encoding atropisomers in an InChI generation algorithm:

### 10.1 Input Requirements

- **3D coordinates or explicit stereochemistry specification required**
  - Cannot infer axial chirality from connectivity alone
  - User must provide either 3D MOL file with wedge/dash bonds or explicit stereochemistry metadata

### 10.2 CIP Priority Assignment for Axial Centers

- Implement standard CIP algorithm adapted for **axial reference frame:**
  - View axis end-on (not along bonds)
  - Assign "front" substituents priority 1 & 2
  - Trace 1→2→3 for R/S or P/M assignment
  
### 10.3 InChI Encoding Strategy

- Assign stereochemistry to one or both atoms at the ends of the hindered bond
- Use `/t` layer: single `-` or `+` after atom number (e.g., `/t6-,7+`)
- Use `/m0` (no mirroring) for explicit enantiomer; `/m1` for mirror image
- Use `/s1` for absolute stereochemistry (standard InChI)

### 10.4 Validation Approach

- **Cross-validate** against:
  - Known atropisomeric structures (BINAP, BINOL, methaqualone)
  - PubChem/ChemSpider entries with verified stereochemistry
  - InChI Trust reference implementations

### 10.5 Scope Definition

- **Phase 1:** Support common biaryl atropisomers (biaryls, binaphthyls, heteroaromatic analogues)
- **Phase 2 (future):** Extend to amides, thioamides, allenes
- **Document limitations** if barrier estimation / automated detection not implemented

---

## 11. References

1. **Wikipedia: Atropisomer** — https://en.wikipedia.org/wiki/Atropisomer  
   Etymology, history, stereochemical assignment, synthesis examples

2. **Wikipedia: Axial Chirality** — https://en.wikipedia.org/wiki/Axial_chirality  
   Definition, CIP rules for axial centers, helicity notation

3. **Wikipedia: Stereochemistry** — https://en.wikipedia.org/wiki/Stereochemistry  
   Comprehensive overview; section on atropisomerism as diastereomer subclass

4. **Wikipedia: International Chemical Identifier (InChI)** — https://en.wikipedia.org/wiki/International_Chemical_Identifier  
   InChI format, layers, examples, standard vs. nonstandard forms, InChIKey

5. **Wikipedia: Simplified Molecular Input Line Entry System (SMILES)** — https://en.wikipedia.org/wiki/Simplified_molecular-input_line-entry_system  
   SMILES definition, isomeric SMILES, stereochemistry notation limitations

6. **InChI Trust Official Website** — https://www.inchi-trust.org/  
   Technical documentation, monthly discussions, version updates (1.07.5 as of Feb 2026)

7. **IUPAC Gold Book** — https://goldbook.iupac.org/  
   Authoritative definitions: axial chirality, helicity, atropisomer, stereochemistry

8. **Chemaxon (Certara)** — https://www.chemaxon.com/  
   Industry cheminformatics tools; overview of commercial approaches to stereo handling

---

## 12. Methodology

**Search strategy:**
- Multi-source web search across academic, chemical informatics, and standards-body resources
- Prioritized authoritative sources (Wikipedia-linked peer-reviewed papers, IUPAC, InChI Trust)
- Synthesized findings into unified narrative covering definition, detection, encoding, and computational gaps

**Confidence levels:**
- **High:** Foundational chemistry definitions, CIP rules, InChI standard layer specifications
- **Medium:** Current state of software atropisomer support (rapidly evolving; verification needed)
- **Medium-to-Low:** Specific barrier values, automated detection success rates (tool-dependent, not comprehensively benchmarked)

---

**Document Version:** 1.0  
**Last Updated:** April 23, 2026
