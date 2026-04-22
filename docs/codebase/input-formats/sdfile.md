# SDfile (Structure-Data File) Format

**Analysis Date:** 2026-04-22

## Overview

The **SDfile** (Structure-Data File), also known as **SDF**, is a cheminformatics file format developed by MDL (Molecular Design Limited, now BIOVIA) that extends the MOL file format to store multiple molecular structures in a single file. Originally designed for pharmaceutical compound registration and screening data management, SDF has become a de facto standard for batch chemical structure processing, database exchange, and high-throughput workflow operations.

The key distinction between a single MOL file and an SDfile is that an SDF contains one or more complete MOL records concatenated together, with each record optionally accompanied by metadata fields that describe properties associated with that molecule. While a MOL file represents exactly one molecule, an SDF can contain thousands or millions of molecules in a single file, making it ideal for processing compound libraries, enumerating virtual screening hits, or transferring database contents. Each molecule in an SDF is self-contained with its complete connection table, and the format maintains backward compatibility with software that reads single MOL files—reading the first record in an SDF yields a valid MOL file.

The SDfile format serves as a critical input format for the InChI Software, enabling batch processing of multiple structures to generate InChI identifiers in a single operation. This capability is essential for database indexing, chemical registry systems, and large-scale structure harmonization workflows.

---

## File Structure

### Multiple MOL Records Concatenated

An SDfile consists of two or more complete MOL records placed sequentially in a single file. Each MOL record follows the V2000 connection table format (see `mol-v2000.md` for detailed specification) containing:

1. **Header Block** (3 lines) - Molecule name, comment, program information
2. **Counts Line** - Number of atoms, bonds, and structural features
3. **Atom Block** - One line per atom with coordinates and properties
4. **Bond Block** - One line per bond with connectivity and type
5. **Properties Block** (optional) - M CHG, M RAD, M ISO, etc.
6. **M END** - End of molecule marker

The InChI software also accepts V3000 format MOL records within SDF files, providing support for molecules exceeding the 999-atom limit of V2000.

### The $$$$ Delimiter

Each molecule record in an SDfile is terminated by a line containing exactly four dollar signs (`$$$$`), which serves as the record separator. This delimiter signals the end of the current MOL record and indicates that any following lines belong to the next molecule.

**Delimiter Rules:**
- Must appear on its own line (no additional characters)
- A blank line may precede it in some implementations
- The last record in the file should also be terminated by `$$$$`
- InChI processes records sequentially until EOF or the delimiter

**Example:**
```
M END
>  <Molecule Name>
Compound A
$$$$
Compound B
[rest of MOL record]
```

### Data Fields Between Records

Unlike a simple MOL file, an SDfile allows storage of arbitrary metadata associated with each molecule. These data fields appear between the `M END` line of one MOL record and the `$$$$` delimiter. They can store any user-defined properties such as compound identifiers, biological activity data, vendor information, or computed molecular properties.

---

## Data Fields

### Structure of Data Fields

Data fields follow a specific format with a header line and one or more value lines:

```
>  <FIELD_NAME>
value_line_1
value_line_2 (optional)
...
```

**Key characteristics:**
- Field names are enclosed in angle brackets: `>  <FIELD_NAME>`
- Multiple consecutive lines of data may follow a single field header
- Empty lines separate different fields
- Field names are case-sensitive in most software
- Values can contain any text including numbers, strings, or multiline data

### Common Field Names

SDfiles commonly use standardized field names for chemical and biological data:

| Field Name | Description | Example |
|------------|-------------|---------|
| `Molecule Name` | Primary identifier | Compound_12345 |
| `CAS#` | Chemical Abstracts Service registry number | 1404-93-9 |
| `Name` | Common/trade name | Vancomycin Hydrochloride |
| `MW` | Molecular weight | 1485.7 |
| `MF` | Molecular formula | C66H75Cl2N9O24 |
| `MFCD` | MDL Catalog ID | MFCD03613611 |
| `Catalog #` | Vendor catalog identifier | BIO-423 |
| `PURITY` | Purity specification | >99% |
| `SMILES` | Canonical SMILES string | CC(C)C... |
| `InChI` | InChI identifier (if pre-computed) | InChI=1S/... |
| `InChIKey` | InChIKey hash | XLYOFNOQVPJJNP-UHFFFAOYSA-N |
| `Formula` | Molecular formula | C66H75Cl2N9O24 |
| `Exact Mass` | Monoisotopic mass | 1484.4561 |
| `LogP` | Partition coefficient | 2.34 |
| `Activity` | Biological activity data | IC50=0.5uM |

### Data Field Examples

From the InChI test fixtures (`test_mols.sdf`), here's a typical data block:

```
M END
>  <Molecule Name>
Compound 20652

>  <Catalog #>
BIO-423

>  <Name>
VANCOMYCIN HYDROCHLORIDE

>  <Category>
Products for Life Science

>  <CAS#>
1404-93-9

>  <MW>
1485.7

>  <PURITY>
'93.5% (Vanomycin base)

>  <MFCD>
MFCD03613611

$$$$
```

**Notes:**
- Some fields have blank values (e.g., no CAS number provided)
- Values may contain leading quotes in certain export formats
- Field order varies by source database
- Custom fields are permitted; InChI ignores them during processing

---

## Processing in InChI

### How InChI Handles Multi-Record SDfiles

When the InChI executable receives an SDfile as input, it processes each MOL record sequentially according to the following workflow:

1. **Record Detection**: The parser reads the file looking for `M END` markers followed by `$$$$` delimiters
2. **MOL Parsing**: Each MOL record is parsed independently using the same logic as single MOL file processing
3. **InChI Generation**: Each molecule is converted to its InChI string representation
4. **Output**: Results are written sequentially to the output file

**Input Type Detection:**
The InChI software detects SDfile input automatically when:
- Multiple `M END` markers are found in the input
- The file contains one or more `$$$$` delimiters
- The `nInputType` is set to `INPUT_SDFILE` in the API

**Command-Line Usage:**
```bash
# Basic SDfile processing
inchi-1 input.sdf output.txt

# With output options
inchi-1 input.sdf output.txt -InChI2Struct

# Output only structures (reconstruct MOL from InChI)
inchi-1 input.sdf output.sdf -OutputSDF
```

### Options for Processing

The InChI software provides several options specific to SDfile handling:

| Option | Flag | Description |
|--------|------|-------------|
| Output as SDF | `-OutputSDF` | Convert InChI back to MOL format and write as SDF |
| Split components | `-OutputSDF_Split` | Write each component (salts, mixtures) as separate records |
| Preserve D/T isotopes | `-OutputSDF_DT` | Output hydrogen isotopes as D (deuterium) and T (tritium) |
| Data field extraction | `-SDFDataTags` | Extract specific data fields to output |
| Record limit | `-MaxRecordsN` | Process only first N records (not always exposed) |

**API Usage (C):**
```c
// Setting up SDfile input in the InChI API
input->nInputType = INPUT_SDFILE;  // 2 = SDfile
strcpy(input->szInputFName, "compounds.sdf");

// Optional: Extract specific data field during processing
strcpy(input->szSdfDataHeader, "CAS#");  // Store CAS number with output
```

**SDF Data Field Handling:**
- InChI preserves the `Molecule Name` field from the MOL header (line 1) during output
- Custom data fields are passed through when using `-OutputSDF`
- The API allows specification of which data field to extract alongside the InChI

### Batch Processing Behavior

When processing large SDfiles:

1. **Memory**: Each molecule is processed independently; memory usage remains constant regardless of file size
2. **Error Handling**: Invalid MOL records are skipped with error messages; processing continues with the next record
3. **Output Format**: Each line in the output contains: `<original_name> <InChI_string> <InChIKey>`
4. **Progress**: No built-in progress indicator; large files may take significant time

---

## Example

### Complete SDfile Example

```
Compound A
Example SDF for documentation
  MyProgram 1.0

  3  2  0  0  0  0  0  0  0  0999 V2000
   -0.5000   0.0000   0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5000   0.0000   0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.0000   0.0000   0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0
  2  3  2  0  0  0
M END
>  <Molecule Name>
Ethanol

>  <CAS#>
64-17-5

>  <MW>
46.07

>  <Formula>
C2H6O

$$$$
Compound B
Example SDF - Record 2
  MyProgram 1.0

  4  3  0  0  0  0  0  0  0  0999 V2000
   -0.7000   0.0000   0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000   0.0000   0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.7000   0.0000   0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4000   0.0000   0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0
  2  3  1  0  0  0
  3  4  1  0  0  0
M END
>  <Molecule Name>
Propanol

>  <CAS#>
71-23-8

>  <MW>
60.10

>  <Formula>
C3H8O

$$$$
```

### Processing This File

```bash
# Generate InChI for each molecule
inchi-1 example.sdf output.txt

# Output would contain:
# Ethanol InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3
# Propanol InChI=1S/C3H8O/c1-2-3-4/h4H,1-3H2

# Convert InChI back to MOL and preserve data fields
inchi-1 example.sdf output.sdf -OutputSDF
```

---

## References

### Primary Specification Documents

1. **BIOVIA CTFile Formats**
   - Official specification: "CTFile Formats" (formerly MDL)
   - Published by: Dassault Systèmes BIOVIA
   - SDF is documented as an extension of MOL V2000/V3000

2. **Chemaxon Documentation**
   - URL: `https://docs.chemaxon.com/display/docs/formats_mdl-molfiles-rgfiles-sdfiles-rxnfiles-rdfiles-formats.md`
   - Comprehensive reference for SDfile format specifications

3. **Wikipedia - Chemical Table File**
   - URL: `https://en.wikipedia.org/wiki/Chemical_table_file`
   - Background on CTFile family including SDF

### InChI Technical Resources

1. **InChI Trust Technical FAQ**
   - URL: `https://www.inchi-trust.org/technical-faq`
   - Documents SDfile as supported input format for InChI generation

2. **InChI Software Documentation**
   - Input format documentation for `inchi-1` executable
   - SDF processing options and command-line flags

3. **InChI FAQ Documents**
   - `INCHI-1-DOC/FAQ/2019/FAQ/16. Creating InChIs/16.4...`
     Documents stereochemistry handling in SDF input
   - `INCHI-1-DOC/FAQ/2019/FAQ/16. Creating InChIs/16.5...`
     Documents handling of coordinate-less (0D) SDF files

### Related Documentation

- `mol-v2000.md` - Detailed specification for MOL V2000 format (base format for SDF records)
- `mol-v3000.md` - Extended MOL format for large molecules in SDF

---

*Input format documentation: 2026-04-22*
