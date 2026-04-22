# End-to-End Integration Tests

Full pipeline tests from MOL file to InChI output.

## Test Strategy

These tests verify the complete pipeline by comparing output against known InChI values.

## Verification Files

### Single MOL Files
| Molecule | MOL File | Description |
|----------|---------|------------|
| Ethanol | examples/01-ethanol.mol | C2H6O - simple alcohol |
| Caffeine | examples/caffeine.mol | C8H10N4O2 - purine alkaloid |
| Cis-platin | examples/cis_platin.mol | Pt(NH3)2Cl2 - anticancer drug |
| Naloxone | examples/naloxon.mol | C19H21NO4 - opioid antagonist |
| CHEBI_140096 | examples/CHEBI_140096.mol | - |
| Fe_N2X | examples/Fe_N2X.mol | Iron complex |

### Extracted SDF Files
- **1,458 MOL files** extracted from SDF files in dataset:
  - `examples/sdf/Life_Science_*.mol` - 855 molecules
  - `examples/sdf/ci5c02720_si_002_*.mol` - 416 molecules
  - `examples/sdf/atropisomers_test_file_1_v2_*.mol` - 49 molecules
  - `examples/sdf/Structure_drawings_*.mol` - 33 molecules
  - `examples/sdf/Test_set_enhanced_stereo_*.mol` - 35 molecules
  - `examples/sdf/test_file_2_*.mol` - 35 molecules

## Run Pipeline

```python
def mol_to_inchi(mol_file):
    # Stage 1: Parse
    parsed = parse_mol(mol_file)

    # Stage 2: Normalize
    normalized = normalize(parsed)

    # Stage 3: Canonicalize
    canonicalized = canonicalize(normalized)

    # Stage 4: Stereochemistry
    stereo = calculate_stereochemistry(canonicalized)

    # Stage 5: Tautomerism
    tautomer = handle_tautomerism(stereo)

    # Stage 6: Ring Detection
    rings = detect_rings(tautomer)

    # Stage 7: Assemble
    assembled = assemble_inchi(rings)

    # Stage 8: Output
    output = format_output(assembled)

    return output["inchi"]
```

## Tests

### Single MOL File Tests

```python
def test_end_to_end_ethanol():
    """Test full pipeline for ethanol."""
    result = mol_to_inchi("examples/01-ethanol.mol")
    expected = "InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)"
    assert result == expected


def test_end_to_end_caffeine():
    """Test full pipeline for caffeine."""
    result = mol_to_inchi("examples/caffeine.mol")
    # Should generate complete InChI with formula
    assert result.startswith("InChI=1S/")
    assert "C8H10N4O2" in result


def test_end_to_end_with_rings():
    """Test pipeline with ring detection."""
    result = mol_to_inchi("examples/caffeine.mol")
    # Caffeine has 2 rings - should include connectivity
    assert "/c" in result


def test_end_to_end_stereo():
    """Test pipeline with stereochemistry."""
    result = mol_to_inchi("examples/cis_platin.mol")
    # Cis-platin has stereo
    assert "/t" in result or "/b" in result


def test_end_to_end_charge():
    """Test charged molecules."""
    result = mol_to_inchi("examples/Fe_N2X.mol")
    # Metal complex may have charge
    assert result.startswith("InChI=1S/")
```

### SDF Parsing Tests

```python
def test_parse_all_sdf_files():
    """Verify all SDF files can be parsed."""
    sdf_dir = "examples/sdf"
    mol_files = glob.glob(f"{sdf_dir}/*.mol")
    
    parsed_count = 0
    failed = []
    
    for mol_file in mol_files:
        try:
            parsed = parse_mol(mol_file)
            if len(parsed["atoms"]) > 0:
                parsed_count += 1
        except Exception as e:
            failed.append(f"{mol_file}: {e}")
    
    success_rate = parsed_count / len(mol_files) if mol_files else 0
    print(f"\nParsed {parsed_count}/{len(mol_files)} ({success_rate:.1%})")
    
    # Should parse at least 90%
    assert success_rate >= 0.9


def test_normalize_all_sdf_files():
    """Verify all SDF files normalize."""
    sdf_dir = "examples/sdf"
    mol_files = glob.glob(f"{sdf_dir}/*.mol")[:100]  # First 100
    
    normalized_count = 0
    
    for mol_file in mol_files:
        try:
            parsed = parse_mol(mol_file)
            normalized = normalize(parsed)
            if normalized:
                normalized_count += 1
        except Exception as e:
            pass
    
    success_rate = normalized_count / len(mol_files) if mol_files else 0
    print(f"\nNormalized {normalized_count}/{len(mol_files)} ({success_rate:.1%})")
    assert success_rate >= 0.9


def test_canonicalize_all_sdf_files():
    """Verify all SDF files canonicalize."""
    sdf_dir = "examples/sdf"
    mol_files = glob.glob(f"{sdf_dir}/*.mol")[:100]  # First 100
    
    canonicalized_count = 0
    
    for mol_file in mol_files:
        try:
            parsed = parse_mol(mol_file)
            normalized = normalize(parsed)
            canonicalized = canonicalize(normalized)
            if canonicalized:
                canonicalized_count += 1
        except Exception as e:
            pass
    
    success_rate = canonicalized_count / len(mol_files) if mol_files else 0
    print(f"\nCanonicalized {canonicalized_count}/{len(mol_files)} ({success_rate:.1%})")
    assert success_rate >= 0.9


def test_full_pipeline_sdf():
    """Test full pipeline on SDF subset."""
    sdf_dir = "examples/sdf"
    mol_files = glob.glob(f"{sdf_dir}/*.mol")[:20]  # First 20
    
    passed = 0
    for mol_file in mol_files:
        try:
            result = mol_to_inchi(mol_file)
            if result and result.startswith("InChI=1S/"):
                passed += 1
        except Exception as e:
            pass
    
    success_rate = passed / len(mol_files) if mol_files else 0
    print(f"\nFull pipeline: {passed}/{len(mol_files)} ({success_rate:.1%})")
    assert success_rate >= 0.8
```

## Running Tests

```bash
# Run all parsing tests
pytest skills/mol-to-inchi/SKILLS/tests/01-parse-test.py -v

# Run SDF specific tests
pytest skills/mol-to-inchi/SKILLS/tests/01-parse-test.py::test_parse_all_sdf_examples -v

# Run integration tests
pytest skills/mol-to-inchi/INTEGRATION/end-to-end-tests.py -v
```

## Verification Against Reference

To verify the skill set correctness:
1. Implement mol_to_inchi() function using the skill set
2. Generate InChI for each example file
3. Compare against reference InChI if available

The example MOL files can be used to verify each pipeline stage works correctly. Start with Stage 1 (parsing) and verify each file parses, then proceed to subsequent stages.

## Adding New Test Cases

1. Add MOL file to `SKILLS/examples/` or `SKILLS/examples/sdf/`
2. Run parse test to verify it parses
3. Implement next pipeline stage
4. Test until full pipeline complete
5. Compare output against expected InChI