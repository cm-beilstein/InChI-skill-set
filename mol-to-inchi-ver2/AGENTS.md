---
name: mol-to-inchi
description: "Generate InChI identifiers from MDL MOL files using pure algorithms"
location: skills/mol-to-inchi/SKILL.md
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# mol-to-inchi Skill

This skill teaches generation of InChI identifiers from MDL MOL files without external cheminformatics libraries.

## Loading the Skill

Since the Claude/OpenCode skill tool only works with built-in skills, reference this skill directly:

1. Read `skills/mol-to-inchi/SKILL.md` for the overview
2. Follow steps 01-07 in order (skip to any step as needed)

## Quick Start

```
1. Parse MOL file (V2000 or V3000)
2. Map elements to atomic numbers
3. Calculate implicit hydrogens
4. Resolve aromatic bonds
5. Canonicalize atom ordering
6. Detect stereocenters
7. Assemble InChI string
```

## Test Cases

Inline test cases are in `skills/mol-to-inchi/tests/TEST_CASES.md`.

## CRITICAL: No External Tools

Do NOT use:
- OpenBabel
- RDKit
- CDK
- Any chemistry library

Only implement the algorithms from the skill documentation.