# CIP Priority Rules

Cahn-Ingold-Prelog (CIP) priority rules determine stereochemical ranking.

## Basic Rules

### Rule 1: Atomic Number
Atoms directly bonded to the stereocenter are sorted by atomic number (highest = rank 1).
Higher atomic number = higher priority.

### Rule 2: Expansion
If two atoms have identical atomic numbers, expand one bond layer outward and compare the next atoms.
The atom with the higher-ranked second-shell atom wins.

### Rule 3: Multiple Bonds
Atoms connected by multiple bonds are treated as pseudo-atoms:
- Double bond to atom X → counts as X appearing TWICE
- Triple bond to atom X → counts as X appearing THREE times

### Rule 4: Isotopic Mass
If all atoms are identical, use isotopic mass as final tiebreaker.
Heavier isotope = higher priority.

## Tetrahedral (sp3) Stereo

1. Identify the 4 substituents bonded to the stereocenter
2. Rank them 1-4 by CIP rules (1=highest, 4=lowest)
3. Orient the molecule so substituent 4 (lowest priority) points AWAY from viewer
4. View substituents 1→2→3:
   - Clockwise → R (rectus, right)
   - Counterclockwise → S (sinister, left)
5. In InChI: R = odd parity (`/t+`), S = even parity (`/t-`)

**Note:** "points away" means substituent 4 is behind the plane of the other three.

## Double Bond (sp2, E/Z) Stereo

1. At each end of the double bond, identify the two substituents
2. Rank each pair by CIP rules
3. At each end: higher priority vs. lower priority substituent
4. Compare across the double bond:
   - Both higher-priority groups on SAME side → Z (zusammen, together) → even parity (`/s+`)
   - On OPPOSITE sides → E (entgegen, opposite) → odd parity (`/s-`)

## Allene / Cumulene Stereo

For cumulated double bonds (allenes, ketenes):
1. Treat the central atom as having two perpendicular pi systems
2. At each end: rank the two substituents by CIP
3. View along the axis; highest priority on one end vs. highest on other
4. Parity based on relative orientation.

## Enhanced Stereochemistry (V3000 Collections)

- **STEABS**: Each stereocenter explicitly marked R or S in the molfile
- **STERELn**: Relative stereo groups — atoms in the same STEREL group have known relative configuration
- **STERACn**: Racemic — configuration unknown (equal mixture of enantiomers)

## Example: Lactic Acid

CH₃-CH(OH)-COOH

At the chiral carbon (C2):
- Substituents: CH₃, OH, COOH, H
- CIP ranking: OH (O, Z=8) > COOH (C bonded to O) > CH₃ (C bonded to H) > H (H)
- With H as lowest priority pointing away: OH→COOH→CH₃ clockwise → R configuration

## Example: trans-2-butene

CH₃-CH=CH-CH₃

At each double bond carbon:
- Carbon 2: substituents are CH₃ and H
- Carbon 3: substituents are CH₃ and H
- At C2: CH₃ (rank 1) > H (rank 2)
- At C3: CH₃ (rank 1) > H (rank 2)
- CH₃ groups on opposite sides → E (trans) → odd parity (`/s-`)