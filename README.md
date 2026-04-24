# InChI Skill Set

A skillset for teaching AI agents to generate valid InChI identifiers from MDL MOL files using pure algorithms — without external cheminformatics libraries.

## What Is This?

This project contains attempts at creating an InChI skill set for AI agents. There are currently 3 attempts:

- **mol-to-inchi-ver1/** — First attempt at the skill
- **mol-to-inchi-ver2/** — Second attempt (refined approach)
- **mol-to-inchi-ver3/** — Third attempt (skill-creator and python code allowed, self-improving skill didnt work)

## InChI String Format

```
InChI=1S/<formula>/c<connections>/h<mobile_H>/q<charge>/p<protons>/i<isotopes>/b<sp2_stereo>/t<sp3_stereo>/m<markers>
```

Layer order: `/f → /c → /h → /m → /q → /p → /i → /b → /t → /s → /r`

## Project Structure

```
InChI-skill-set/
├── mol-to-inchi-ver1/      # First attempt
├── mol-to-inchi-ver2/      # Second attempt
├── mol-to-inchi-ver3/      # Third attempt
├── data/                  # .mol and .inchi files
└── README.md
```

## Data Folder

The `data/` folder contains paired `.mol` molecule files and their corresponding `.inchi` reference files for testing and validation.

## Docs Folder

The `docs/` folder contains documentation about the InChI codebase.

## Hill formula 

The `src/formula/` folder contains AI generate Python code to see whether code can be generate to replicate the InChI C code for the Hill formula.


## CRITICAL: No External Tools

This skillset teaches generation **without** cheminformatics libraries. Do NOT use:
- OpenBabel
- Datamol
- RDKit
- CDK
- Python chemistry libraries
- InChI binaries

Only implement the algorithms described in the skill documentation.

## License

MIT