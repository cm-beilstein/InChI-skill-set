# Periodic Table — Elements, Atomic Numbers, Standard Valences

## Element Data

| Symbol | Atomic # | Name | Std Valence | Symbol | Atomic # | Name | Std Valence |
|--------|---------|------|-----------|--------|---------|------|-----------|
| H | 1 | Hydrogen | 1 | | He | 2 | Helium | 0 |
| Li | 3 | Lithium | 1 | | Be | 4 | Beryllium | 2 |
| B | 5 | Boron | 3 | | C | 6 | Carbon | 4 |
| N | 7 | Nitrogen | 3 (prim/sec), 5 (tert) | | O | 8 | Oxygen | 2 |
| F | 9 | Fluorine | 1 | | Ne | 10 | Neon | 0 |
| Na | 11 | Sodium | 1 | | Mg | 12 | Magnesium | 2 |
| Al | 13 | Aluminum | 3 | | Si | 14 | Silicon | 4 |
| P | 15 | Phosphorus | 3 or 5 | | S | 16 | Sulfur | 2, 4, 6 |
| Cl | 17 | Chlorine | 1 | | Ar | 18 | Argon | 0 |
| K | 19 | Potassium | 1 | | Ca | 20 | Calcium | 2 |
| Sc | 21 | Scandium | 3 | | Ti | 22 | Titanium | 4 |
| V | 23 | Vanadium | 5 | | Cr | 24 | Chromium | 3, 6 |
| Mn | 25 | Manganese | 2, 4, 7 | | Fe | 26 | Iron | 2, 3 |
| Co | 27 | Cobalt | 2, 3 | | Ni | 28 | Nickel | 2, 3 |
| Cu | 29 | Copper | 1, 2 | | Zn | 30 | Zinc | 2 |
| Ga | 31 | Gallium | 3 | | Ge | 32 | Germanium | 4 |
| As | 33 | Arsenic | 3, 5 | | Se | 34 | Selenium | 2, 4, 6 |
| Br | 35 | Bromine | 1 | | Kr | 36 | Krypton | 0 |
| Rb | 37 | Rubidium | 1 | | Sr | 38 | Strontium | 2 |
| Y | 39 | Yttrium | 3 | | Zr | 40 | Zirconium | 4 |
| Nb | 41 | Niobium | 3, 5 | | Mo | 42 | Molybdenum | 4, 6 |
| Tc | 43 | Technetium | 4 | | Ru | 44 | Ruthenium | 3, 4 |
| Rh | 45 | Rhodium | 3 | | Pd | 46 | Palladium | 2, 4 |
| Ag | 47 | Silver | 1 | | Cd | 48 | Cadmium | 2 |
| In | 49 | Indium | 3 | | Sn | 50 | Tin | 2, 4 |
| Sb | 51 | Antimony | 3, 5 | | Te | 52 | Tellurium | 2, 4, 6 |
| I | 53 | Iodine | 1, 3, 5, 7 | | Xe | 54 | Xenon | 0 |
| Cs | 55 | Cesium | 1 | | Ba | 56 | Barium | 2 |
| La | 57 | Lanthanum | 3 | | Ce | 58 | Cerium | 3 |
| Pr | 59 | Praseodymium | 3 | | Nd | 60 | Neodymium | 3 |
| Pm | 61 | Promethium | 3 | | Sm | 62 | Samarium | 2, 3 |
| Eu | 63 | Europium | 2, 3 | | Gd | 64 | Gadolinium | 3 |
| Tb | 65 | Terbium | 3 | | Dy | 66 | Dysprosium | 3 |
| Ho | 67 | Holmium | 3 | | Er | 68 | Erbium | 3 |
| Tm | 69 | Thulium | 3 | | Yb | 70 | Ytterbium | 2, 3 |
| Lu | 71 | Lutetium | 3 | | Hf | 72 | Hafnium | 4 |
| Ta | 73 | Tantalum | 5 | | W | 74 | Tungsten | 4, 6 |
| Re | 75 | Rhenium | 4, 7 | | Os | 76 | Osmium | 2, 3, 4 |
| Ir | 77 | Iridium | 3, 4 | | Pt | 78 | Platinum | 2, 4 |
| Au | 79 | Gold | 1, 3 | | Hg | 80 | Mercury | 1, 2 |
| Tl | 81 | Thallium | 1, 3 | | Pb | 82 | Lead | 2, 4 |
| Bi | 83 | Bismuth | 3, 5 | | Po | 84 | Polonium | 2, 4 |
| At | 85 | Astatine | 1 | | Rn | 86 | Radon | 0 |
| Fr | 87 | Francium | 1 | | Ra | 88 | Radium | 2 |
| Ac | 89 | Actinium | 3 | | Th | 90 | Thorium | 4 |
| Pa | 91 | Protactinium | 5 | | U | 92 | Uranium | 4, 6 |

## Isotopes

| Symbol | Atomic # | Mass Shift in InChI | Symbol | Atomic # | Mass Shift |
|--------|---------|-------------------|--------|---------|---------|
| D (Deuterium) | 1 | +1 (iso_mass = 2) | T (Tritium) | 1 | +2 (iso_mass = 3) |
| 13C | 6 | +7 (iso_mass = 13) | 14N | 7 | +7 (iso_mass = 14) |
| 18O | 8 | +10 (iso_mass = 18) | | | |

**Isotopic mass in InChI**: absolute mass number stored. When provided in MOL mass_diff field (-5 to +5), converted to iso_mass:
- Positive mass_diff: add to average atomic mass
- Negative mass_diff: subtract from average
- Mass diff 0: natural abundance

For InChI `/i` layer: isotope mass followed by element symbol and position.
Example: `2+1D` = position 2 has deuterium.

## CIP Tiebreaker Weights

When atomic numbers are equal, use isotopic mass to break ties:
heavier isotope = higher priority.