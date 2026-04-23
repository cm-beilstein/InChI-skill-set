# Charge Layer (`/q`)

**Analysis Date:** 2026-04-22

## Overview

The Charge layer (`/q`) is an optional component of the InChI identifier that represents the net electrical charge of a molecular structure. It encodes the total formal charge associated with the entire molecule or individual connected components, enabling precise identification of ions, salts, charged complexes, and zwitterions.

The charge layer becomes part of the InChI identifier when a molecule carries a net charge that cannot be derived purely from the molecular formula or hydrogen atom counts. This typically occurs with:

- **Ions**:Cations (e.g., `Na+`, `NH4+`) and anions (e.g., `Cl-`, `COO-`)
- **Salt forms**:When acid-base reactions produce charged species that remain associated
- **Charged complexes**:Metal complexes with formal charges on ligands
- **Zwitterions**:Molecules with both positive and negative charges (net charge = 0 but charge information is preserved)
- **Protonation states**:When explicit protonation affects the charge

InChI uses `/q` followed by an integer to represent the charge:

```
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3
InChI=1S/CH4/h1H4            # methane (no charge layer needed)
InChI=1S/Na/q+1          # sodium cation
InChI=1S/ClH.Na/h1H;/q;+1/p-1  # sodium chloride
InChI=1S/C2H5NO2/c3-1-2(4)5/h1,3H2,(H,4,5)  # glycine zwitterion
```

**Output format examples:**
- `/q+1` - net charge of +1 (cation)
- `/q-2` - net charge of -2 (anion with 2 negative charges)
- `/q+1-2` - charges distributed across components (zwitterion)

The charge layer is placed in the InChI string after the mobile hydrogen layer (`/h`) and before the protons layer (`/p`). When multiple disconnected components exist, each component can have its own charge value, separated by semicolons.

## Code Implementation

### Key Source Files

| File | Purpose |
|------|---------|
| `INCHI_BASE/src/util.c` | Contains `extract_charges_and_radicals()` - parses charge strings from MOL/SDF input |
| `INCHI_BASE/src/ichimak2.c` | Computes `nTotalCharge` from atom charges during InChI generation |
| `INCHI_BASE/src/ichiprt1.c` | Outputs the `/q` layer in generated InChI strings |
| `INCHI_BASE/src/ichiread.c` | Parses `/q` layer when reading InChI strings |
| `INCHI_BASE/src/ichi.h` | Defines the INChI structure containing `nTotalCharge` |
| `INCHI_BASE/src/ichimake.c` | Compares InChI strings, including charge layer |
| `INCHI_BASE/src/ichirvr4.c` | Reverse InChI handling of charges |
| `INCHI_BASE/src/mol_fmt1.c` | Uses `extract_charges_and_radicals()` when parsing MOL files |

### Data Structure

The `nTotalCharge` field is defined in the main INChI structure in `INCHI_BASE/src/ichi.h`:

```c
typedef struct tagINChI {
    int        nErrorCode;  /* 0 = success */
    INCHI_MODE nFlags;
    /* ---- basic & tautomer layer */
    int        nTotalCharge;      /* <-- Charge layer data */
    int        nNumberOfAtoms;
    char      *szHillFormula;
    U_CHAR    *nAtom;       /* atomic numbers [nNumberOfAtoms] */
    int        lenConnTable;
    AT_NUMB   *nConnTable;
    // ... additional fields
} INChI;
```

**Field details:**
- `nTotalCharge`: Integer representing net charge (-256 to +256 per InChI specification)
- `NO_VALUE_INT` (-9999): Used to indicate charge was not specified
- `0`: Neutral (no charge layer output when neutral)

### Extraction Function

The `extract_charges_and_radicals()` function in `INCHI_BASE/src/util.c` (lines 665-735) parses charge and radical notation from element symbol strings:

```c
int extract_charges_and_radicals( char *elname, int *pnRadical, int *pnCharge )
{
    char *q, *r, *p;
    int  nCharge = 0, nRad = 0, charge_len = 0, k, nVal, nSign, nLastSign = 1;

    p = elname;

    /* Parse +, -, and ^ notation */
    while ( (q = strpbrk(p, "+-^")) )
    {
        switch ( *q )
        {
            case '+':
            case '-':
                /* Parse (+2), (+3), (-1), etc. */
                for (k = 0, nVal = 0; ( nSign = ( '+' == q[k] ) ) || ( nSign = -( '-' == q[k] ) ); k++)
                {
                    nVal += ( nLastSign = nSign );
                    charge_len++;
                }
                if ((nSign = (int)strtol(q + k, &r, 10)))
                {
                    nVal += nLastSign * ( nSign - 1 );
                }
                charge_len = (int) ( r - q );
                nCharge += nVal;
                break;
            case '^':
                /* Handle radicals */
                nRad = 1;
                charge_len = 1;
                for (k = 1; q[0] == q[k]; k++)
                {
                    nRad++;
                    charge_len++;
                }
                break;
        }
        /* Remove processed characters */
        memmove(q, q + charge_len, strlen(q + charge_len) + 1);
    }

    *pnRadical = nRad;
    *pnCharge = nCharge;

    return ( nRad || nCharge );
}
```

This function is called during MOL/SDF parsing in `mol_fmt1.c` to extract charges from atom block entries like `C++` (double positive) or `O-` (oxide anion).

### Charge Computation During InChI Generation

In `INCHI_BASE/src/ichimak2.c` (lines 1135-1141), the total charge is computed from atomic charges during normalization:

```c
/* Total charge */
for (i = 0, n = 0; i < num_atoms + num_removed_H; i++)
{
    n += at[i].charge;
}
pINChI->nTotalCharge = n;
```

The function iterates through all atoms (including removed hydrogens) and sums their individual charges to compute the net molecular charge stored in the InChI structure.

### Charge Output

In `INCHI_BASE/src/ichiprt1.c` (lines 3283-3339), the charge layer is output using `OutputINCHI_ChargeAndRemovedAddedProtonsLayers()`:

```c
int OutputINCHI_ChargeAndRemovedAddedProtonsLayers(CANON_GLOBALS *pCG,
                                                   INCHI_IOSTREAM *out_file,
                                                   INCHI_IOS_STRING *strbuf,
                                                   INCHI_OUT_CTL *io,
                                                   char *pLF,
                                                   char *pTAB)
{
    /* Charge layer processing */
    io->nSegmAction = INChI_SegmentAction(io->sDifSegs[io->nCurINChISegment][DIFS_q_CHARGE]);
    if (io->nSegmAction)
    {
        szGetTag(IdentLbl, io->nTag, io->bTag1 = IL_CHRG | io->bFhTag, io->szTag1, &io->bAlways, 1);
        inchi_strbuf_reset(strbuf);
        io->tot_len = 0;
        if (INCHI_SEGM_FILL == io->nSegmAction)
        {
            io->tot_len = str_Charge2(io->pINChISort, io->pINChISort2,
                                      strbuf, &io->bOverflow, io->bOutType, io->num_components,
                                      io->bSecondNonTautPass, io->bOmitRepetitions, io->bUseMulipliers);
        }
        // Output: /q+1, /q-2, etc.
    }
}
```

### Charge Parsing (Reading InChI)

In `INCHI_BASE/src/ichiread.c` (lines 8029-8198), the `ParseSegmentCharge()` function parses the `/q` layer:

```c
int ParseSegmentCharge(const char* str,
    int         bMobileH,
    INChI* pInpInChI[],
    int         ppnNumComponents[])
{
    // str contains "q+1" or "q-2" etc.
    // Validates charge range (-256 to +256)
    // Stores in pInChI[i].nTotalCharge
}
```

**Key parsing rules:**
- Empty `/q` means no charge information available
- Format: `q<integer>` where integer can be positive (+) or negative (-)
- For multiple components: `q+1;-1` (first component +1, second component -1)
- Multiplier syntax: `3*q+1` means 3 components each with charge +1

## Pseudo-code Algorithm

### Charge Extraction Algorithm

```
FUNCTION extract_charges_and_radicals(element_string):
    1. Initialize: nCharge = 0, nRadical = 0
    2. Find "+" or "-" characters in element_string
    3. WHILE found:
        a. Parse consecutive +/- symbols, counting +1 or -1 each
        b. IF numeric follows (e.g., +2, -1):
           - Add (lastSign * (number - 1)) to nCharge
        c. Remove processed characters from string
    4. RETURN nCharge, nRadical
END FUNCTION

FUNCTION compute_total_charge(atom_array):
    1. Initialize: total = 0
    2. FOR each atom IN atom_array:
        a. total += atom.charge
    3. RETURN total
END FUNCTION
```

### Charge Layer Output Algorithm

```
FUNCTION output_charge_layer(InChI_struct):
    1. nCharge = InChI_struct.nTotalCharge
    2. IF nCharge == 0:
        a. RETURN (no output - neutral)
    3. IF nCharge != NO_VALUE:
        a. Output format string: "/q%+d" (positive) or "/q%d" (negative)
    4. RETURN complete charge layer string
END FUNCTION
```

### Charge Layer Input Parsing Algorithm

```
FUNCTION parse_charge_layer(q_string):
    1. Verify string starts with 'q'
    2. Extract integer value after 'q'
    3. IF value in range [-256, +256]:
        a. Store as nTotalCharge for component
    4. ELSE:
        a. Signal syntax error
    5. RETURN success/failure
END FUNCTION
```

## Examples

### Sodium Cation (Na+)

```
SMILES: [Na+]
InChI: InChI=1S/Na/q+1
```

- Element: Na (sodium)
- Charge: +1
- Output: `/q+1`

### Chloride Ion (Cl-)

```
SMILES: [Cl-]
InChI: InChI=1S/ClH/h1H/p-1
```

- Element: Cl with H (HCl)
- Charge: -1
- Output: `/q-1`

### Sodium Chloride (Disconnected)

```
SMILES: [Na+].[Cl-]
InChI: InChI=1S/ClH.Na/h1H;/q;+1/p-1
```

- Multiple components, each component can have charge
- Format shows 3 Na components (implied from 3 Na total)
- Charge layer omitted when charges balanced to zero overall

### Glycine Zwitterion

```
SMILES: [NH3+]CC(=O)[O-]
InChI: 1S/C2H5NO2/c3-1-2(4)5/h1,3H2,(H,4,5)
```

- NH3+ group: +1 charge (cationic)
- COO- group: -1 charge (anionic)
- Net charge = 0, but charges are preserved as separate components
- Output: `/q+1/p+1` (charge layer then protons layer)

### Oxalate Dianion

```
SMILES: [O-]C(=O)C(=O)[O-]
InChI: 1S/C2H2O4/c3-1(4)2(5)6/h(H,3,4)(H,5,6)/p-2
```

- Two carboxylate groups, each -1
- Net charge: -2
- Output: `/q-2`

### Tetramethylammonium Cation

```
SMILES: C[N+](C)(C)C
InChI: 1S/C4H12N/c1-5(2,3)4/h1-4H3/q+1
```

- Central nitrogen with four methyl groups
- Formal positive charge on N
- Output: `/q+1`

### Sulfate Dianion

```
SMILES: [O-]S(=O)(=O)[O-]
InChI: 1S/O4S/c1-2(3,4)5-1/h1H2/q-2
```

- Four oxygen atoms, two are anionic (-1 each)
- Net charge: -2
- Output: `/q-2`

---

*Charge layer analysis: 2026-04-22*