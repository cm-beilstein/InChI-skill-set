# Atropisomer Detection and Encoding: Research Report

*Generated: 2026-04-23 | Sources: 15+ | Confidence: High*

## Executive Summary

Atropisomers are stereoisomers arising from hindered rotation about single bonds, where energy barriers are high enough to allow isolation of individual conformers. This report covers the theoretical foundations, energy thresholds for stability, nomenclature systems (M/P and Ra/Sa), and major software implementations including RDKit (2023+) and ChemAxon (deprecated). Key software implementations provide detection algorithms, file format encodings (CXSMILES, MOL, MRV), and enhanced stereochemistry support.

## 1. Theoretical Foundations

### 1.1 Definition

Atropisomers (from Greek "atropos" meaning "not to be turned") are a subclass of conformers that can be isolated as separate chemical species arising from restricted rotation about a single bond. The classic example is ortho-substituted biphenyls where steric hindrance between ortho substituents prevents free rotation about the central C-C bond.

Reference: [IUPAC Gold Book - atropisomers](https://goldbook.iupac.org/terms/view/A00511)

The phenomenon was first experimentally detected by George Christie and James Kenner in 1922 in a tetra-substituted biphenyl diacid.

Reference: [Wikipedia - Atropisomer](https://en.wikipedia.org/wiki/Atropisomer)

### 1.2 Energy Barrier Classification (LaPlante Classes)

The pharmaceutical industry uses a classification system based on rotational energy barriers to assess atropisomer stability (developed by Linda LaPlante):

| Class | ΔG‡ (kcal/mol) | Half-life (T₁/₂) | Practical Implication |
|-------|---------------|-------------------|----------------------|
| Class 1 | <20 kcal/mol | seconds | Atropisomers rotate freely; treated as single compounds |
| Class 2 | 20-30 kcal/mol | hours to days | Separable with chiral SFC; may interconvert in vivo |
| Class 3 | >30 kcal/mol | days to years | Stable, isolable enantiomers |

Reference: [Wuxi AppTec - QM Torsion Scan for Analysis of Atropisomers](https://wuxibiology.com/qm-torsion-scan-for-analysis-of-atropisomers/)

A threshold of ~20 kcal/mol is commonly used to distinguish atropisomers from rapidly interconverting conformers. The original definition by Michinori Ōki (1983) set the threshold at ΔG‡ > 93 kJ/mol (~22 kcal/mol) at 300K, corresponding to a half-life of at least 1000 seconds.

### 1.3 Axial Chirality and Nomenclature

Atropisomers exhibit axial chirality. The IUPAC-recommended stereodescriptors are:

- **Ra/Sa** (or **M/P**): Used to specify absolute configuration
- **P (Delta)** or **M (Lambda)**: Helicity descriptors for clockwise or counterclockwise rotation

Using the helicity rule: Looking along the chirality axis, if the path from the higher-priority substituent on the front ring to the higher-priority substituent on the back ring is clockwise, the configuration is **P**; if counterclockwise, it's **M**.

Using the Ra/Sa system: Two higher-ranking substituents are chosen (one from each pair) using CIP priority rules. The chirality is **Ra** if the path from the first substituent through the axis to the second is clockwise when looking toward the second substituent.

Reference: [IUPAC Gold Book - axial chirality](https://goldbook.iupac.org/terms/view/A00547)

Reference: [IUPAC Blue Book P-9](http://iupac.qmul.ac.uk/BlueBook/P9.html)

## 2. Software Implementations

### 2.1 RDKit

#### 2.1.1 Overview

RDKit added native atropisomer support in release 2023.09 (merged PR #6903, December 2023). The implementation was contributed by Tad Hurst (Collaborative Drug Discovery, Inc.).

Reference: [RDKit PR #6903 - atropisomer handling added](https://github.com/rdkit/rdkit/pull/6903)

#### 2.1.2 Core Functions

The RDKit `Atropisomers` namespace provides the following functions:

```cpp
// Detect atropisomer chirality from 3D conformation
void detectAtropisomerChirality(ROMol& mol, const Conformer* conf);

// Generate wedge/hash bonds from atropisomer configuration
void wedgeBondsFromAtropisomers(const ROMol& mol, const Conformer* conf, 
                               std::map<int, std::unique_ptr<WedgeInfoBase>>& wedgeBonds);

// Check if molecule has atropisomers
bool doesMolHaveAtropisomers(const ROMol& mol);

// Get atoms and bonds involved in a specific atropisomer bond
bool getAtropisomerAtomsAndBonds(const Bond* bond, AtropAtomAndBondVec atomAndBonds[2], 
                                 const ROMol& mol);

// Enhanced stereo group handling
void getAllAtomIdsForStereoGroup(const ROMol& mol, const StereoGroup& group, 
                                std::vector<unsigned int>& atomIds, 
                                const std::map<int, std::unique_ptr<WedgeInfoBase>>& wedgeBonds);

void cleanupAtropisomerStereoGroups(ROMol& mol);
```

Reference: [RDKit C++ API - Atropisomers Namespace](http://rdkit.org/new_docs/cppapi/namespaceRDKit_1_1Atropisomers.html)

#### 2.1.3 Detection Algorithm

RDKit's detection algorithm:

1. Identifies potential atropisomer bonds (single bonds connecting two aromatic rings)
2. Requires at least three ortho ligands on each side of the bond
3. Uses 3D coordinates to determine the stereochemical configuration
4. Calculates the rotation direction (CW or CCW) needed to overlap the lowest-indexed chain on each end
5. During sanitization, removes atropisomer labels from:
   - Bonds in rings
   - Bonds where either atom is not SP2
   - Bonds where both ends have equivalent branches

```cpp
// Example: Detecting atropisomers in Python
from rdkit import Chem
from rdkit.Chem import AllChem

# Load molecule with 3D coordinates
mol = Chem.MolFromSmiles('N1(C2=C(I)C=CC=C2C)C(Br)=CC=C1C')
mol = AllChem.AddHs(mol)
AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())

# Detect atropisomer chirality
Chem.rdAtropisomers.detectAtropisomerChirality(mol, mol.GetConformer())

# Check if molecule has atropisomers
has_atrop = Chem.rdAtropisomers.doesMolHaveAtropisomers(mol)
```

#### 2.1.4 File Format Support

| Format | Encoding Method | Notes |
|--------|----------------|--------|
| **CXSMILES** | Wedge/hash bonds on side bonds | Most expressive |
| **MOL/V2000** | Bond stereo flags | STEREOATROPCCW/STEREOATROPCW |
| **MRV** | Enhanced stereo groups | Both atoms marked in stereo group |

The internal representation uses BondStereo enumeration:
- `STEREOATROPCCW` (8): Counter-clockwise configuration
- `STEREOATROPCW` (9): Clockwise configuration

Reference: [RDKit PR #6903](https://github.com/rdkit/rdkit/pull/6903)

#### 2.1.5 Enhanced Stereochemistry

Atropisomers can be included in enhanced stereo groups (or/and groups):

```python
# Finding atropisomer bonds for enhanced stereo groups
from rdkit import Chem

mol = Chem.MolFromSmiles('...')
for bond in mol.GetBonds():
    if bond.GetStereo() in (Chem.rdchem.BondStereo.STEREOATROPCW, 
                          Chem.rdchem.BondStereo.STEREOATROPCCW):
        print(f"Atropisomer bond: {bond.GetBeginAtomIdx()} -> {bond.GetEndAtomIdx()}")
        # Get atoms for stereo group inclusion
        atropo_aids = [bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()]
```

Reference: [RDKit Issue #7557](https://github.com/rdkit/rdkit/issues/7557)

#### 2.1.6 CIP Labeling

RDKit supports CIP labeling for atropisomers using the pseudo-CIP or proper CIP labeler:

```python
from rdkit.Chem import rdCIPLabeler

# Assign CIP labels (including M/P for atropisomers)
rdCIPLabeler.AssignCIPLabels(mol)

# Check labels
for bond in mol.GetBonds():
    if bond.HasProp('_CIPCode'):
        print(f"Bond {bond.GetIdx()}: {bond.GetProp('_CIPCode')}")
```

Reference: [RDKit Issue #8526](https://github.com/rdkit/rdkit/issues/8526)

#### 2.1.7 Conformer Generation

ETKDG (Experimental Torsion Knowledge Distance Geometry) conformer generators now support maintaining atropisomer stereochemistry:

- ETKDGv1, v2, v3 all support atropisomers
- The `enforceChirality` option helps preserve configured atropisomers
- Issue noted: Some ETKDG versions may generate conformers that violate specified chirality

Reference: [RDKit Issue #5283](https://github.com/rdkit/rdkit/issues/5283)

Reference: [RDKit Issue #7098](https://github.com/rdkit/rdkit/pull/7098)

#### 2.1.8 Stereoisomer Enumeration

The `rdEnumerateStereoisomers` module can enumerate atropisomers when explicitly assigned:

```python
from rdkit.Chem import rdEnumerateStereoisomers

enumerator = rdEnumerateStereoisomers.StereoisomerEnumerator(mol)
# Note: Currently only assigned atropisomers are enumerated
# Unassigned atropisomer detection is not yet implemented
```

Reference: [RDKit - rdEnumerateStereoisomers module](https://rdkit.org/docs/source/rdkit.Chem.rdEnumerateStereoisomers.html)

### 2.2 ChemAxon (MarvinSketch)

#### 2.2.1 Status

**IMPORTANT**: ChemAxon's atropisomer checker is **deprecated** as of recent versions. It remains in the product but is no longer actively supported.

Reference: [Chemaxon - Atropisomer Checker](https://d2.chemaxon.com/display/docs/structure-checker_atropisomer.md)

https://docs.chemaxon.com/lts-neon/structure-checker_atropisomer.html

#### 2.2.2 Detection Algorithm

The deprecated ChemAxon checker:
- Searches for stereoisomers containing two aromatic rings connected by a single bond
- Requires at least three ortho ligands
- No fixer is available

#### 2.2.3 CIP Stereo Descriptor

ChemAxon implements the AtropStereoDescriptor for CIP stereochemistry:

| AtropStereoValue | Meaning |
|-----------------|---------|
| **EVEN** | Positive angle (0 to π), analogous to R |
| **ODD** | Negative angle (0 to -π), analogous to S |
| **UNKNOWN** | Angle near 0 or π (5° threshold), or no 2D info |
| **WIGGLY** | Axis or associated bonds are undefined |

Reference: [Chemaxon Docs - CIP Stereo Chemistry](https://docs.chemaxon.com/latest/representation_cip-stereo-chemistry.html)

#### 2.2.4 Nomenclature in MarvinSketch

- Assigns **M** and **P** stereodescriptors to biaryl structures with at least 3 ortho substituents
- Atropisomers should be drawn with solid wedged and hashed bonds within the aromatic rings
- Applies exclusively to biaryl compounds with 3+ (2+1) ortho substituents

Reference: [Chemaxon - Axial stereoisomerism documentation](https://dl.chemaxon.com/docs/HTML/docs167110/Axial_stereoisomerism_-_atropisomerism.html)

### 2.3 Other Tools and Workflows

#### 2.3.1 Atropisomer Risk Assessment Workflow

A Python-based workflow for atropisomer risk assessment is available:

Reference: [GitHub - manolitopere/atropisomers_workflow](https://github.com/manolitopere/atropisomers_workflow)

Features:
- Substructure detection using predefined SMARTS motifs
- Steric filtering for hindered rotational bonds
- GIC (Gaussian Internal Coordinate) scan setup
- Scan parsing and TS validation
- Barrier correction using experimental benchmark regressions
- LaPlante class assignment

#### 2.3.2 Computational QM Analysis

For energy barrier calculation:

1. **QM Torsion Scan**: Calculate energy profile by scanning dihedral angles
2. **Transition State Optimization**: Locate the rotation transition state
3. **Barrier Calculation**: ΔG‡ = (G_TS - G_ground state) × 627.509 kcal/mol per Hartree

Typical methods:
- DFT with ωB97x-D/6-31g(d)
- Single-point energy at M06-2X/def2-TZVP
- Solvent correction using PCM

Reference: [Wuxi AppTec - QM Torsion Scan](https://wuxibiology.com/qm-torsion-scan-for-analysis-of-atropisomers/)

Reference: [Rowan Documentation - Studying Atropisomerism with Dihedral Scans](https://docs.rowansci.com/tutorials/dihedral-scans-i)

## 3. Key Takeaways

1. **RDKit** (2023+) is the primary actively maintained open-source tool with full atropisomer support
2. **ChemAxon** atropisomer checker is deprecated and no longer supported
3. The **20 kcal/mol threshold** is standard for classifying atropisomer stability
4. Atropisomer detection requires **3D coordinates** for accurate stereochemistry assignment
5. File formats: **CXSMILES** provides the most complete representation via wedge/hash bonds
6. Enhanced stereochemistry groups support atropisomer bonds for "or" and "and" stereo specifications
7. QM torsion scans remain the gold standard for accurate energy barrier prediction
8. Substructure-based detection is a fast prescreening method but requires validation

## 4. Sources

1. [IUPAC Gold Book - atropisomers](https://goldbook.iupac.org/terms/view/A00511)
2. [IUPAC Gold Book - axial chirality](https://goldbook.iupac.org/terms/view/A00547)
3. [IUPAC Blue Book P-9](http://iupac.qmul.ac.uk/BlueBook/P9.html)
4. [Wikipedia - Atropisomer](https://en.wikipedia.org/wiki/Atropisomer)
5. [RDKit PR #6903 - atropisomer handling](https://github.com/rdkit/rdkit/pull/6903)
6. [RDKit C++ API - Atropisomers Namespace](http://rdkit.org/new_docs/cppapi/namespaceRDKit_1_1Atropisomers.html)
7. [RDKit Issue #8526 - Molecular Drawing](https://github.com/rdkit/rdkit/issues/8526)
8. [RDKit Issue #7557 - Enhanced stereo groups](https://github.com/rdkit/rdkit/issues/7557)
9. [Chemaxon - Atropisomer Checker](https://d2.chemaxon.com/display/docs/structure-checker_atropisomer.md)
10. [Chemaxon - CIP Stereo Chemistry](https://docs.chemaxon.com/latest/representation_cip-stereo-chemistry.html)
11. [Chemaxon - Axial stereoisomerism](https://dl.chemaxon.com/docs/HTML/docs167110/Axial_stereoisomerism_-_atropisomerism.html)
12. [Wuxi AppTec - QM Torsion Scan](https://wuxibiology.com/qm-torsion-scan-for-analysis-of-atropisomers/)
13. [Rowan Documentation - Dihedral Scans](https://docs.rowansci.com/tutorials/dihedral-scans-i)
14. [GitHub - manolitopere/atropisomers_workflow](https://github.com/manolitopere/atropisomers_workflow)
15. [RDKit - rdEnumerateStereoisomers](https://rdkit.org/docs/source/rdkit.Chem.rdEnumerateStereoisomers.html)

## 5. Methodology

This report was generated through multi-source web searches using the following sub-questions:
- What are atropisomers and their detection criteria?
- How does RDKit implement atropisomer support?
- What is the status of ChemAxon atropisomer handling?
- What energy thresholds define stable atropisomers?
- What nomenclature systems exist for axial chirality?

Sources were cross-referenced to ensure accuracy. Claims are supported by inline citations.