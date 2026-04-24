# InChI String Format and Layers

## Standard Format

```
InChI=1S/{formula}/c{connections}{/h{hydrogens}}{/q{charge}}{/p{protons}}{/i{isotopes}}{/s{sp2}}{/t{sp3}}{/m{markers}}
```

- `InChI=1S/` = identifier, version 1, Standard (S is mandatory)
- All layers start with `/` (forward slash)
- Layers appear in strict order

## Layer Order (Mandatory)

```
/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r
```

## /c Layer (Connections) — Obligatory

Canonical atom numbering. Each atom listed with its bonded neighbors.

### Counter Notation
- `1-2-3` = atom 1 connected to atom 2, atom 2 to atom 3
- `1-2-3-1` = atom 3 also bonds back to atom 1 (ring closure)

### Ring Closures
- Simple ring: last atom closes back to first (e.g., `1-2-3-4-5-6-1`)
- Multiple rings on same atom: use letters `1a-1b-1c`
- Fused rings: numbered sequentially, closures indicated

### Format Rules
- Atom numbers: 1, 2, 3, ..., 10, 11, ..., 99, 100, ...
- Neighbors: separated by `-`
- Ring closures: `-{atom}` where atom already appeared

## /h Layer (Mobile Hydrogens)

Canonical positions of atoms bearing mobile H.

Format: `{positions}H{,{positions}H}`

- `1H` = 1 hydrogen on atom 1
- `1-3H2` = 2 hydrogens on atoms 1 and 3
- `6H` = 6 mobile hydrogens on atom 6
- `5-6H,1-2H2,3H` = mixed (5H on 6, 2H on 1 and 2, 1H on 3)

## /q Layer (Charge)

Format: `+n` or `-n`

- `/q1` = +1 charge
- `/q-1` = -1 charge
- `/q+2` = +2 charge

## /p Layer (Removed Protons)

For tautomeric acids: removed mobile protons.

Format: same as `/h` but without `H`.

- `/p-2` = 2 protons removed (negative = removed from acid)

## /i Layer (Isotopes)

Position of isotopic labeling.

Format: `{position}+{mass}{isotope}`

- `2+1D` = position 2 has deuterium
- `3+2T` = position 3 has tritium
- `1+13C` = position 1 has carbon-13

Can chain: `1+1D2+2D` = positions 1 and 2 have D.

## /s Layer (sp2 Double Bond Stereo)

Double bond (geometric) stereochemistry.

- `/s+` = Z configuration (same side, even parity)
- `/s-` = E configuration (opposite sides, odd parity)
- `/s1` = one double bond stereo
- Can chain: `/s+1s-2` = two double bonds, first Z, second E

## /t Layer (sp3 Tetrahedral Stereo)

Tetrahedral stereocenters.

- `/t+` = R configuration (odd parity, clockwise)
- `/t-` = S configuration (even parity, counterclockwise)
- `/t1` = one stereocenter
- Can chain: `/t+1t-2` = two stereocenters, first R, second S

## /m Layer (Enhanced Stereo Markers)

Enhanced stereochemistry flags from V3000 collections.

- `/m0` = absolute stereochemistry
- `/m1` = relative stereochemistry
- `/m2` = racemic mixture

## Non-Standard InChI

Without `S`: `InChI=1/...` — non-standard, less interoperable.

With FixedH: `InChI=1F/...` — all mobile H fixed at specific positions.

## Empty Layers

For single atoms with no bonds:
- Formula only: `InChI=1S/Cl` (no `/c`)
- With charge: `InChI=1S/Cl/q-1`

## Examples

### Benzene
```
InChI=1S/C6H6/c1-2-3-4-5-6-1/h6H
```
- `/c`: 6 atoms in a ring, closure back to 1
- `/h`: 6 mobile hydrogens

### Ethanol
```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3
```
- `/c`: C1-C2-C3(O)
- `/h`: 3H on C1, 2H on C2, 1H on O, 2H on that H

### Acetate ion
```
InChI=1S/C2H3O2/c1-2-3/h1H,2H2,3H-2/q-1
```
- `/c`: chain C1-C2-C3(O)
- `/h`: mobile H
- `/q`: -1 charge
- `/p`: 2 protons removed (acid)