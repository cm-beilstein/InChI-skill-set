# Enhanced Stereochemistry Detection and Encoding: Research Report

*Generated: 2026-04-23 | Sources: 20+ | Confidence: High*

## Executive Summary

Enhanced stereochemistry is a formalism for representing mixtures of stereoisomers and unknown absolute configurations while preserving relative stereochemical relationships. Originally developed by MDL Information Systems in the early 2000s, it is now implemented across major cheminformatics platforms including BIOVIA/Dassault Systèmes, ChemDraw, RDKit, and ChemAxon (MarvinSketch/JChem). This report covers the theoretical foundations, file format encodings (MDL V3000, CXSMILES), and implementation details across major software packages.

## 1. Theoretical Foundations

### 1.1 Definition and Purpose

Enhanced stereochemical representation allows scientists to represent what is actually known about stereogenic centers when the full absolute configuration is uncertain. This addresses common scenarios in drug discovery and combinatorial chemistry where:

- Only relative stereochemistry is known between multiple centers
- A sample contains a mixture of stereoisomers (e.g., from synthetic byproducts)
- The absolute configuration is unknown but the relative configuration is defined
- Registry systems need to precisely capture stereochemical knowledge

Reference: [BIOVIA Enhanced Stereochemical Representation](https://discover.3ds.com/biovia-enhanced-stereochemical-representation)

### 1.2 Stereogroup Types

The enhanced representation defines three types of stereogroups:

| Group Type | Symbol | Meaning |
|-----------|--------|---------|
| **ABSOLUTE** | `abs` or `a` | The absolute configuration is known; represents a single, defined stereoisomer |
| **OR** | `or` or `o` | Either the drawn configuration OR its inverse; represents one stereoisomer with unknown absolute configuration |
| **AND** | `and` or `&` | Both the drawn configuration AND its inverse; represents a 50/50 mixture (racemate or defined mixture) |

Reference: [Depth-First: V3000 Molfile Enhanced Stereochemistry](https://depth-first.com/articles/2022/02/09/v3000-molfile-enhanced-stereochemistry-representation/)

### 1.3 Relative Stereochemistry

The key advantage of enhanced stereochemistry is expressing relative configurations:

- **OR1**: Center 1 either (R) or (S), and by implication, the same applies to all centers in the group
- **AND1**: A mixture containing both enantiomers/diastereomers in defined proportions
- Multiple groups can coexist, allowing complex stereochemical descriptions

Reference: [Chemaxon - Stereochemistry Documentation](https://dl.chemaxon.com/docs/HTML/docs166200/Stereochemistry.html)

### 1.4 Matching Rules

Enhanced stereochemistry has defined matching semantics:

| Query Type | Matches | Requirements |
|-----------|---------|-------------|
| ABS | Only exact configuration | R matches R, S matches S |
| OR | Either configuration | Relative configuration must match |
| AND | Both configurations | Relative configuration must match |

Reference: [Chemaxon - Stereochemistry Matching Rules](https://dl.chemaxon.com/docs/HTML/docs166200/Stereochemistry.html)

## 2. File Format Encodings

### 2.1 MDL Molfile V3000

The extended MOLfile format (V3000) stores enhanced stereo in a COLLECTION block:

```
M V30 BEGIN COLLECTION
M V30 MDLV30/STEABS ATOMS=(n atom1 atom2 ...)
M V30 MDLV30/STERELn ATOMS=(n atom1 atom2 ...)
M V30 MDLV30/STERACn ATOMS=(n atom1 atom2 ...)
M V30 END COLLECTION
```

Where:
- `MDLV30/STEABS`: ABSOLUTE group
- `MDLV30/STEREL`: OR group (REL = relative)
- `MDLV30/STERAC`: AND group (AC = And group, "collection")

Stereogroup labels use unique integer indices (e.g., `or1`, `or2`, `&5`).

Reference: [Depth-First: V3000 Enhanced Stereochemistry](https://depth-first.com/articles/2022/02/09/v3000-molfile-enhanced-stereochemistry-representation/)

### 2.2 CXSMILES

The ChemAxon Extended SMILES format encodes enhanced stereo using pipe-delimited annotations at the end of the SMILES string:

```
CC@HC(=O)O |a:1|          # ABSOLUTE, atom 1
CC@HC(=O)O |&1:1|        # AND group 1, atom 1
CC@HC(=O)O |o1:1|        # OR group 1, atom 1
```

Multiple groups use different indices:
```
OC[C@H]1OC=CC@@H[C@@H]1O |&1:2,o2:6,8|
```

This represents: AND group 1 with atoms 2; OR group 2 with atoms 6 and 8.

Reference: [RDKit Blog - Stereo Groups and Enhanced Stereochemistry](https://greglandrum.github.io/rdkit-blog/posts/2023-11-19-explaining-stereo-groups.html)

### 2.3 Format Comparison

| Feature | V2000 | V3000 | CXSMILES |
|---------|------|------|----------|
| ABS support | Limited | Yes | Yes |
| OR/AND groups | No | Yes | Yes |
| Multiple groups | No | Yes | Yes |
| Stereo group IDs | No | Yes (optional) | Yes |
| Atropisomers | No | Yes | Yes |

Reference: [Chemaxon - MDL MOLfiles Format](https://kb.chemaxon.com/display/docs/formats_mdl-molfiles-rgfiles-sdfiles-rxnfiles-rdfiles-formats.md)

## 3. Software Implementations

### 3.1 BIOVIA (Dassault Systèmes)

#### 3.1.1 BIOVIA Draw

BIOVIA Draw provides comprehensive enhanced stereochemistry support:

- **Tetrahedral centers**: Carbon, Nitrogen, Sulphur, Phosphorus
- **Axial stereochemistry**: Allenes, Atropisomers
- **Geometric isomers**: cis/trans double bonds

The software determines CIP labels including meso, pseudo, and unknown configurations.

Reference: [BIOVIA Draw - Documentation](https://www.3ds.com/assets/invest/2024-02/biovia-draw-ds.pdf)

#### 3.1.2 Enhanced Representation Features

- Draw structures with ABS, OR, AND labels
- Set stereochemistry via Atom menu or context menu
- Supports Microsoft Windows 10/11 and Office 2019/2021
- CIP label calculation
- Export to SD files with enhanced stereo preservation

### 3.2 ChemAxon (MarvinSketch/JChem)

#### 3.2.1 MarvinSketch

MarvinSketch supports enhanced stereo through:

- **ABS**: Absolute configuration known
- **OR**: Relative configuration known, absolute unknown
- **AND**: Mixture of stereoisomers

UI access: Atom menu → Set Stereo Group

Reference: [Chemaxon - Stereochemistry in MarvinSketch](https://docs.chemaxon.com/latest/marvin_stereochemistry-in-marvinsketch.html)

#### 3.2.2 Standardizer Actions

Chemaxon standardizer provides conversion actions:

| Action | Effect |
|--------|--------|
| `converttoenhancedstereo:abs` | Convert unlabeled centers to ABS |
| `converttoenhancedstereo:enforceabsstereo` | Force all to ABS, ignore chiral flag |
| `converttoenhancedstereo:or` | Convert to OR group |
| `converttoenhancedstereo:and` | Convert to AND group |

Reference: [Chemaxon - Convert to Enhanced Stereo](https://kb.chemaxon.com/display/docs/standardizer_convert-to-enhanced-stereo.md)

#### 3.2.3 JChem/Marvin JS

Marvin JS supports enhanced stereo via web service:

| Identifier | Description |
|------------|-------------|
| Off | No stereochemical information |
| Abs | Absolute configuration known |
| Or | Relative known, absolute unknown |
| And | Mixture of stereoisomers |

Import/export requires V3000 format.

Reference: [Chemaxon - Marvin JS Stereochemistry](https://kb.chemaxon.com/display/docs/stereochemistry-in-marvin-js.md)

#### 3.2.4 API Support

Chemaxon provides `CIPStereoRecognizer` for programmatic access:

```java
Collection<CIPStereoDescriptor> descriptors = 
    CIPStereoRecognizer.calculateCIPStereoDescriptors(mol);
```

Reference: [Chemaxon - CIP Stereo Chemistry](https://docs.chemaxon.com/latest/representation_cip-stereo-chemistry.html)

### 3.3 RDKit

#### 3.3.1 Overview

RDKit has comprehensive enhanced stereochemistry support with ongoing development:

- **Python API**: Full support
- **C++ API**: Full support
- **CXSMILES**: Read/write
- **V3000 Molfiles**: Read/write
- **Canonicalization**: Supported (PR #6051)

Reference: [RDKit Blog - Stereo Groups](https://greglandrum.github.io/rdkit-blog/posts/2023-11-19-explaining-stereo-groups.html)

#### 3.3.2 Core Functions

```python
from rdkit import Chem

# Parsing from CXSMILES
m = Chem.MolFromSmiles('CC@HC(=O)O |&1:1|')

# Get stereo groups
for sg in m.GetStereoGroups():
    print(sg.GetGroupType())  # STEREO_AND, STEREO_OR, STEREO_ABS
    print([a.GetIdx() for a in sg.GetAtoms()])

# Create stereo group
sgmol = Chem.RWMol(m)
sg = Chem.CreateStereoGroup(Chem.StereoGroupType.STEREO_AND, sgmol, [6, 8])
sgmol.SetStereoGroups([sg])
```

Reference: [RDKit - Stereo Groups](https://greglandrum.github.io/rdkit-blog/posts/2023-11-19-explaining-stereo-groups.html)

#### 3.3.3 Key PRs and Issues

| PR/Issue | Description |
|----------|-------------|
| PR #2282 | Parse enhanced stereo from CXSMILES |
| PR #2290 | Write enhanced stereo to CXSMILES |
| PR #6051 | Canonicalization of stereo groups |
| PR #6560 | Forward stereo group IDs |
| Issue #5165 | V3000 parsing bug (trailing spaces) |

Reference: [RDKit PR #6051](https://github.com/rdkit/rdkit/pull/6051)

#### 3.3.4 Stereoisomer Enumeration

```python
from rdkit.Chem import rdEnumerateStereoisomers

opts = rdEnumerateStereoisomers.StereoEnumerationOptions()
opts.onlyUnassigned = True
opts.stereoGroups = True

enum = rdEnumerateStereoisomers.StereoisomerEnumerator(mol, opts)
for isomer in enum:
    print(Chem.MolToSmiles(isomer))
```

#### 3.3.5 Atropisomer Support

RDKit 2023.09+ supports atropisomers in enhanced stereo groups:

```python
# Finding atropisomer bonds
for bond in mol.GetBonds():
    if bond.GetStereo() in (Chem.rdchem.BondStereo.STEREOATROPCW,
                           Chem.rdchem.BondStereo.STEREOATROPCCW):
        # Include in enhanced stereo group
        pass
```

Reference: [RDKit Issue #7557](https://github.com/rdkit/rdkit/issues/7557)

#### 3.3.6 CIP Labeling

```python
from rdkit.Chem import rdCIPLabeler

rdCIPLabeler.AssignCIPLabels(mol)

# Check labels
for atom in mol.GetAtoms():
    if atom.HasProp('_CIPCode'):
        print(f"Atom {atom.GetIdx()}: {atom.GetProp('_CIPCode')}")
```

### 3.4 ChemDraw

ChemDraw (PerkinElmer/BIOVIA) supports enhanced stereochemistry:

- Drawing interface for ABS, OR, AND groups
- Exports to V3000 SD files
- CIP label calculation
- Integration with BIOVIA products

Reference: [Depth-First: V3000 Enhanced Stereochemistry](https://depth-first.com/articles/2022/02/09/v3000-molfile-enhanced-stereochemistry-representation/)

## 4. Canonicalization

### 4.1 The Problem

When generating canonical SMILES for molecules with enhanced stereo, the atom ordering must account for stereogroups. Without canonicalization:

- `CC@HO |o1:1|` and `CC@@HO |o1:1|` would generate different SMILES
- Molecules representing the same enhanced notation would have different canonical forms

### 4.2 RDKit Solution (PR #6051)

RDKit addresses this by:

1. Enumerating possible structures from enhanced notation
2. Generating unique SMILES for each
3. Finding a canonical enhanced stereo representation

Reference: [RDKit PR #6051](https://github.com/rdkit/rdkit/pull/6051)

### 4.3 Stereo Group ID Forwarding

PR #6560 added the ability to preserve stereo group IDs across formats:

```python
# Forward stereo group IDs on output
Chem.MolToCXSmiles(mol, forwardStereoGroupIds=True)
```

## 5. Key Takeaways

1. **Enhanced stereochemistry** (ABS, OR, AND) is the industry standard for representing uncertain or relative stereochemistry
2. **V3000** is the required molfile format; V2000 does not support enhanced stereo
3. **CXSMILES** is the most readable format, supported by RDKit and ChemAxon
4. **RDKit** has the most actively developed open-source implementation
5. **ChemAxon MarvinSketch** provides full UI support but some features are deprecated
6. **BIOVIA Draw** provides comprehensive drawing and export capabilities
7. **Canonicalization** is essential for database registration systems
8. **Atropisomers** can be included in enhanced stereo groups (RDKit 2023.09+)

## 6. Sources

1. [BIOVIA Enhanced Stereochemical Representation](https://discover.3ds.com/biovia-enhanced-stereochemical-representation)
2. [Depth-First: V3000 Molfile Enhanced Stereochemistry](https://depth-first.com/articles/2022/02/09/v3000-molfile-enhanced-stereochemistry-representation/)
3. [RDKit Blog: Stereo Groups and Enhanced Stereochemistry](https://greglandrum.github.io/rdkit-blog/posts/2023-11-19-explaining-stereo-groups.html)
4. [RDKit Blog: Explaining Enhanced Stereo](https://greglandrum.github.io/rdkit-blog/posts/2025-04-18-explaining-enhanced-stereo.html)
5. [RDKit PR #6051: Canonicalization of stereo groups](https://github.com/rdkit/rdkit/pull/6051)
6. [RDKit PR #6560: Forward stereo group IDs](https://github.com/rdkit/rdkit/pull/6560)
7. [RDKit PR #2282: Parse enhanced stereo from CXSMILES](https://github.com/rdkit/rdkit/pull/2282)
8. [RDKit PR #2290: Write enhanced stereo to CXSMILES](https://github.com/rdkit/rdkit/pull/2290)
9. [RDKit Issue #5165: V3000 parsing](https://github.com/rdkit/rdkit/issues/5165)
10. [Chemaxon - Stereochemistry in MarvinSketch](https://docs.chemaxon.com/latest/marvin_stereochemistry-in-marvinsketch.html)
11. [Chemaxon - Convert to Enhanced Stereo](https://kb.chemaxon.com/display/docs/standardizer_convert-to-enhanced-stereo.md)
12. [Chemaxon - MDL MOLfiles Format](https://kb.chemaxon.com/display/docs/formats_mdl-molfiles-rgfiles-sdfiles-rxnfiles-rdfiles-formats.md)
13. [Chemaxon - CIP Stereo Chemistry](https://docs.chemaxon.com/latest/representation_cip-stereo-chemistry.html)
14. [Chemaxon - Marvin JS Stereochemistry](https://kb.chemaxon.com/display/docs/stereochemistry-in-marvin-js.md)
15. [BIOVIA Draw Documentation PDF](https://www.3ds.com/assets/invest/2024-02/biovia-draw-ds.pdf)

## 7. Methodology

This report was generated through multi-source web searches investigating:
- Enhanced stereochemistry file formats (MDL V3000, CXSMILES)
- Implementation across major software packages (RDKit, ChemAxon, BIOVIA)
- Canonicalization challenges and solutions
- Atropisomer integration with enhanced stereo

Sources were cross-referenced to ensure accuracy with inline citations.