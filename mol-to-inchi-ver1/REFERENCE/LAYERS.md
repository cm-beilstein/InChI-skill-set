# InChI Layer Reference

Complete reference for InChI layer structure and formatting.

## Base Structure

```
InChI=1S/<formula>/<layers>
```

- `InChI=1S` = Standard InChI version 1

## Layer Order

**Critical:** Layers MUST appear in this order:

```
/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r
```

## Formula Layer (/f)

Molecular formula without stereochemistry.

| Format | Example |
|--------|---------|
| `/fC<n>H<m>N<o>...` | `/fC2H6O` |

- Elements sorted: C first, then H, then alphabetical
- No charge or isotope info
- Subscripts not used (C2 = C2, not C₂)

## Connectivity Layer (/c)

Atom connections using canonical labels.

| Format | Example |
|--------|---------|
| `/c<atom>-<atom>,...` | `/c1-2` |

- Uses canonical numbers from Morgan algorithm
- Atoms separated by commas
- Ranges use hyphen: `1-5` = `1,2,3,4,5`

## Fixed Hydrogen Layer (/h)

Non-mobile (fixed) hydrogen positions.

| Format | Example |
|--------|---------|
| `/h<atoms>` | `/h(H,3,4)` |

- Uses canonical atom numbers
- Groups in parentheses

## Mobile Hydrogen Layer (/m)

Mobile (tautomer) hydrogen groups.

| Format | Example |
|--------|---------|
| `/m<atom>,...` | `/m3,4,7` |

- Lists all atoms with equivalent mobile H

## Charge Layer (/q)

Total charge.

| Format | Example |
|--------|---------|
| `/q+<n>` | `/q+1` |
| `/q-<n>` | `/q-1` |

## Proton Count Layer (/p)

Difference in proton count from standard.

| Format | Example |
|--------|---------|
| `/p+<n>` | `/p+1` |
| `/p-<n>` | `/p-1` |

## Isotope Layer (/i)

Isotope positions.

| Format | Example |
|--------|---------|
| `/i<atom>+<mass>` | `/i1+2` |

- `<atom>` = canonical number
- `<mass>` = mass number

## Geometric Stereo Layer (/b)

Double bond (E/Z) stereochemistry.

| Format | Example |
|--------|---------|
| `/b<atom>.<atom>,...` | `/b1.2` |

- Uses bond canonical numbers with priorities

## Tetrahedral Stereo Layer (/t)

Tetrahedral (sp3) chiral centers.

| Format | Example |
|--------|---------|
| `/t<atom>,...` | `/t1,2,3` |

- Lists canonical numbers of chiral centers

## Stereo Type Layer (/s)

Type of stereochemistry.

| Value | Meaning |
|-------|---------|
| `/s1` | Absolute (3D coordinates) |
| `/s2` | Relative |
| `/s3` | Racemic |

## Reconnection Layer (/r)

Ring-atom reconnection for metals.

| Format | Example |
|--------|---------|
| `/r<connections>` | `/r1-2` |

## Full Examples

### Ethanol
```
InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)
```

| Layer | Value |
|-------|-------|
| /f | C2H6O |
| /c | 1-2 |
| /h | (H,3,4) |

### Caffeine
```
InChI=1S/C8H10N4O2/c1-12-6(13)8(14)3(15)5(16)7(17)10(12)2-4/h3H,2H2,1H3
```

### Benzene
```
InChI=1S/c1-6/h1-6H
```

### L-Alanine
```
InChI=1S/C3H7NO2/c2/t1/m3-4/s1
```

## InChIKey

27-character hash derived from InChI.

Format: `<block1>-<block2>-<type>`

- Block 1: First 9 chars of SHA-256(formula + connectivity)
- Block 2: 8 chars from additional layers
- Type: Layer indicator (N, F, M, R, O, etc.)

Reference: See 08-output.md