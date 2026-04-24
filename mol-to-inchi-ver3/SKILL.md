---
name: mol-to-inchi-ver3
description: "Generate a standard InChI string from a MOL file through reasoning. No InChI library, no executables, no cheminformatics libraries. Use when: given a MOL file, produce its InChI identifier via step-by-step reasoning through the InChI pipeline (parse, formula, canonicalize, tautomer, stereo, connectivity, assemble). Verify against example pairs in references/examples/."
---

# MOL to InChI (v3)

Generate a standard InChI string from a MOL file by reasoning through the InChI pipeline steps. No InChI library, no executables, no rdkit/datamol.

## Pipeline (Reason in Order)

Work through these 7 steps for every molecule.

### Step 1: Parse MOL → Atoms & Bonds

Read the MOL V2000 file (or V3000):

**Counts line:** `aaabbb lll fff ccc sss xxx rrr ppp nnn V2000`
- `aaa` = number of atoms, `bbb` = number of bonds
- rest are atom lists, chiral flag, etc.

**Atom block (one line per atom):**
| cols 1-10 | cols 11-20 | cols 21-30 | cols 31-34 | cols 35-36 | cols 37-38 | cols 39-40 | cols 41-42 | cols 43-44 |
|---|---|---|---|---|---|---|---|---|---|
| x | y | z | symbol | mass diff | charge | parity | H+1 | valence |

- **Charge codes:** 0=none, 1=+3, 2=+2, 3=+1, 4=-1, 5=-2, 6=-3, 7=radical
- **Mass diff:** -5 to +5 from nominal mass (e.g., 13 for C-13, -2 for C-11)
- **H+1 field:** actual H count = value - 1
- **Parity:** 0=none, 1=odd, 2=even, 3=either

**Bond block:** `a1 a2 type stereo topo react`
- **Type:** 1=single, 2=double, 3=triple, 4=aromatic
- **Stereo:** 0=none, 1=up, 6=down

**Implicit H:** standard valence minus sum(bond orders). Standard valences: C=4, N=3/5, O=2, S=2/4/6, P=3/5.

**Properties block** (optional): `M CHG n a1 c1...`, `M ISO n a1 i1...`, `M RAD n a1 r1...`.

### Step 2: Hill Formula

Order: C first, H first, then alphabetical by symbol.

Example: C₂H₆O — not C₂OH₆, not C₂H₆O.

### Step 3: Canonical Ordering (Extended Connectivity)

1. **Initial partition:** each atom gets key = (atomic number, valence, num_H, isotopic mass)
2. **Iterate:** for each atom, build neighbor pattern hash from (class, bond type) of each neighbor
3. **Split classes** where patterns differ
4. **Repeat** until stable
5. **Assign ranks:** atoms in same class get same rank
6. **Canonical order:** atoms sorted by rank ascending, ties broken by lowest original number

Lower rank = more "central" in the molecule. Terminal atoms get higher ranks.

### Step 4: Tautomer Groups

Mobile H can move between endpoint atoms. Common patterns:

- **PT_02 (keto-enol):** `-C(=O)-CH₂-` ↔ `-C(-OH)=CH-`
- **PT_03 (amido-imidol):** `-C(=O)-NH₂-` ↔ `-C(-OH)=NH-`
- **PT_04 (enamine-imine):** `-C=NH-` ↔ `-CH-NH₂-`

Endpoints: O, N, S atoms adjacent to H-bearing atoms connected by conjugated paths.

The `/h` layer lists canonical positions of mobile H atoms.

### Step 5: Stereochemistry

**CIP Priority (at each stereocenter):**
1. Direct neighbors sorted by atomic number (highest wins)
2. Ties: expand to next atoms, compare by atomic number
3. Multiple bonds count as duplicate atoms
4. Isotopic mass breaks final ties

**Tetrahedral (sp3):**
- View with lowest CIP priority pointing AWAY
- 1→2→3 clockwise = R (rectus, right)
- 1→2→3 counterclockwise = S (sinister, left)
- Parity: R = odd (o), S = even (e)

**Double bond (sp2, E/Z):**
- At each end: higher CIP priority substituent
- Same side = Z (zusammen) = even (e)
- Opposite sides = E (entgegen) = odd (o)

**/h layer with mobile H:** for mobile H in tautomeric groups, use `/h` notation.

### Step 6: Connectivity String

Build from canonical ordering:

For atom i in canonical order (1-indexed):
- List its neighbors (in canonical order) as `-{neighbor_num}`
- Ring closures: `-{first_atom}` means atom bonds back to start

Format: `1-2-3` means atom 1→2→3 chain.
Benzene: `1-2-3-4-5-6-1` (ring closure back to 1).

### Step 7: Assemble Layers

```
InChI=1S/{formula}/c{connections}/h{ hydrogens }{/q{charge}}{/p{protons}}{/i{isotopes}}{/s{sp2}}{/t{sp3}}{/m{markers}}
```

- `/c` omitted if trivial (single atom) — use `/f` for formula-only
- `/h`: canonical positions of mobile H atoms
- `/q`: charge (`+1`, `-1`, `+2`, etc.)
- `/p`: removed protons from tautomeric acids
- `/i`: isotopic labeling (`2+1D` = position 2 has deuterium)
- `/s`: sp2 (double bond) stereo — `/s+` = Z, `/s-` = E
- `/t`: sp3 (tetrahedral) stereo — `/t+` = R, `/t-` = S
- `/m`: enhanced stereo markers

Layer order: `/f` → `/c` → `/h` → `/m` → `/q` → `/p` → `/i` → `/b` → `/t` → `/s`

## V3000 MOL Files

V3000 uses keyword format (lines start with `M  V30`):

```
M  V30 BEGIN CTAB
M  V30 COUNTS na nb nsg n3d chiral
M  V30 BEGIN ATOM
M  V30 idx sym x y z aamap [CHG= RAD= CFG= MASS= VAL= HCOUNT=]
M  V30 END ATOM
M  V30 BEGIN BOND
M  V30 idx typ a1 a2 [CFG= TOPO=]
M  V30 END BOND
M  V30 END CTAB
M  END
```

- `CFG=1` = odd parity, `CFG=2` = even, `CFG=3` = either
- Collection block for enhanced stereo: `STEABS`, `STERELn`, `STERACn`

## InChIKey (Optional)

SHA-256 hash of InChI string, base-26 encoded (A-Z, no E-start triplets):

1. Major block (14 chars): SHA-256 of formula + connections + mobile H
2. Minor block (9 chars): SHA-256 of stereo + charge + isotopes
3. Protonation flag (1 char)
4. Version flag (1 char, `S` = standard)
5. Format: `XXXXXXXXXXXXXX-YYYYYYYYY-Z-S` (27 chars)

The triplet lookup (14-bit → 3 letters) is in `references/inchikey_base26_table.md`.

## Scripts

Run end-to-end with:
```bash
python3 scripts/mol_to_inchi.py <molecule.mol>
```

Individual steps:
```bash
python3 scripts/parse_molfile.py <molecule.mol>
python3 scripts/hill_formula.py
python3 scripts/canonicalize.py
python3 scripts/compose_inchi.py
python3 scripts/inchikey.py <inchi_string>
```

## References

- `references/formats.md` — MOL V2000/V3000 format details
- `references/periodic_table.md` — Elements, atomic numbers, valences
- `references/cip_rules.md` — Full CIP priority rules
- `references/inchi_format.md` — InChI string layers
- `references/examples/` — Sample mol/inchi pairs for verification
- `references/inchikey_base26_table.md` — Base-26 triplet table for InChIKey

## Workflow

1. Parse the MOL file → atom list + bond list
2. Verify atom count and connectivity
3. Compute Hill formula
4. Compute canonical ordering
5. Identify tautomer groups (if any)
6. Identify stereocenters and double bonds
7. Build connectivity string
8. Assemble all layers
9. Verify against example pairs in `references/examples/`
10. Optionally generate InChIKey