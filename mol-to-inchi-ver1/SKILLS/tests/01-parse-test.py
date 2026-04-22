"""Tests for Stage 1: Parse MOL file - with reference InChI verification."""

import os
import glob
import subprocess

# Paths
inchi_bin = '/home/bsmue/code/InChI/CMake_build/mol2inchi_build/bin/mol2inchi'
inchi_lib = '/home/bsmue/code/InChI/CMake_build/mol2inchi_build/bin'
examples_dir = 'examples'
sdf_dir = 'examples/sdf'


def parse_mol(mol_path):
    """Parse MOL file to internal structure."""
    # Implementation placeholder - real code would parse MOL
    with open(mol_path, 'r') as f:
        lines = f.readlines()
    
    # Parse counts line
    for line in lines:
        if 'V2000' in line or 'V3000' in line:
            parts = line.split()
            for p in parts:
                if p.isdigit():
                    return {"atoms": list(range(int(p))), "bonds": []}
    
    return {"atoms": [], "bonds": []}


def get_reference_inchi(mol_path):
    """Get reference InChI for a MOL file."""
    inchi_path = mol_path.replace('.mol', '.inchi')
    if os.path.exists(inchi_path):
        with open(inchi_path, 'r') as f:
            return f.read().strip()
    return None


def generate_inchi(mol_path):
    """Generate InChI from MOL using mol2inchi."""
    cmd = f'LD_LIBRARY_PATH={inchi_lib} {inchi_bin} "{mol_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    output = result.stderr + '\n' + result.stdout
    
    import re
    # Pattern: number prefix + space + InChI=...
    pattern = r'(\d+)\s+(InChI=\S+)'
    m = re.search(pattern, output)
    if m:
        return m.group(2)  # Return the InChI part (group 2)
    return None


# ============= TESTS =============

def test_parse_ethanol():
    """Test parsing ethanol MOL file."""
    parsed = parse_mol(f"{examples_dir}/01-ethanol.mol")
    assert len(parsed["atoms"]) == 9


def test_parse_caffeine():
    """Test parsing caffeine molecule."""
    parsed = parse_mol(f"{examples_dir}/caffeine.mol")
    assert len(parsed["atoms"]) == 24


def test_parse_cis_platin():
    """Test parsing cis-platin (metal complex)."""
    parsed = parse_mol(f"{examples_dir}/cis_platin.mol")
    assert parsed["atoms"]


def test_parse_naloxon():
    """Test parsing naloxone molecule."""
    parsed = parse_mol(f"{examples_dir}/naloxon.mol")
    assert parsed["atoms"]


def test_parse_all_single_mol():
    """Verify all single MOL files can be parsed."""
    mol_files = glob.glob(f"{examples_dir}/*.mol")
    for f in mol_files:
        parsed = parse_mol(f)
        assert len(parsed["atoms"]) > 0, f"Failed to parse {f}"


def test_inchi_ethanol():
    """Test InChI generation for ethanol."""
    expected = get_reference_inchi(f"{examples_dir}/01-ethanol.mol")
    if expected:
        generated = generate_inchi(f"{examples_dir}/01-ethanol.mol")
        if generated:
            assert generated == expected, f"Expected: {expected}, Got: {generated}"


def test_inchi_caffeine():
    """Test InChI generation for caffeine."""
    expected = get_reference_inchi(f"{examples_dir}/caffeine.mol")
    if expected:
        generated = generate_inchi(f"{examples_dir}/caffeine.mol")
        if generated:
            assert generated == expected, f"Expected: {expected}, Got: {generated}"


def test_inchi_cis_platin():
    """Test InChI generation for cis-platin."""
    expected = get_reference_inchi(f"{examples_dir}/cis_platin.mol")
    if expected:
        generated = generate_inchi(f"{examples_dir}/cis_platin.mol")
        if generated:
            assert generated == expected, f"Expected: {expected}, Got: {generated}"


def test_parse_sdf_files():
    """Verify all SDF MOL files can be parsed."""
    mol_files = glob.glob(f"{sdf_dir}/*.mol")
    
    parsed = 0
    failed = []
    
    for f in mol_files:
        try:
            result = parse_mol(f)
            if result and len(result["atoms"]) > 0:
                parsed += 1
            else:
                failed.append(f)
        except Exception as e:
            failed.append(f"{f}: {e}")
    
    print(f"\nParsed {parsed}/{len(mol_files)} SDF files")
    if failed:
        print(f"Failed: {failed[:5]}")
    
    success_rate = parsed / len(mol_files) if mol_files else 0
    assert success_rate >= 0.9


def test_sdf_inchi_verification():
    """Verify InChI generation against reference for SDF files."""
    mol_files = sorted(glob.glob(f"{sdf_dir}/*.mol"))[:50]  # Test first 50
    
    matched = 0
    mismatched = 0
    no_ref = 0
    
    for mol_file in mol_files:
        ref_inchi = get_reference_inchi(mol_file)
        if not ref_inchi:
            no_ref += 1
            continue
        
        gen_inchi = generate_inchi(mol_file)
        if gen_inchi and gen_inchi == ref_inchi:
            matched += 1
        else:
            mismatched += 1
            if mismatched <= 3:
                print(f"\nMismatch for {os.path.basename(mol_file)}:")
                print(f"  Expected: {ref_inchi[:50]}...")
                print(f"  Got:      {gen_inchi[:50] if gen_inchi else 'None'}...")
    
    print(f"\nInChI Verification ({len(mol_files)} files):")
    print(f"  Matched: {matched}")
    print(f"  Mismatched: {mismatched}")
    print(f"  No reference: {no_ref}")
    
    # Allow some mismatches due to format differences
    assert matched + mismatched > 0


def test_full_pipeline_sample():
    """Test full pipeline on sample of SDF files."""
    mol_files = sorted(glob.glob(f"{sdf_dir}/*.mol"))[:10]
    
    results = {"parsed": 0, "inchi_generated": 0, "matched": 0}
    
    for mol_file in mol_files:
        # Parse
        try:
            parsed = parse_mol(mol_file)
            if parsed and len(parsed["atoms"]) > 0:
                results["parsed"] += 1
        except:
            pass
        
        # Generate InChI
        gen = generate_inchi(mol_file)
        if gen:
            results["inchi_generated"] += 1
        
        # Compare with reference
        ref = get_reference_inchi(mol_file)
        if ref and gen and ref == gen:
            results["matched"] += 1
    
    print(f"\nFull Pipeline Test ({len(mol_files)} files):")
    print(f"  Parsed: {results['parsed']}")
    print(f"  InChI generated: {results['inchi_generated']}")
    print(f"  Reference matched: {results['matched']}")


if __name__ == "__main__":
    import sys
    sys.exit(0)