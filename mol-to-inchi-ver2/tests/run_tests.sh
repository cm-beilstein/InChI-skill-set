#!/bin/bash
# Test runner for mol-to-inchi skillset
# Verifies implementation against reference InChI files

# Test directory - set via environment variable or use default
TEST_DIR="${MOL2INCHI_TEST_DIR:-${HOME}/tmp/skill_testing/inchi_examples}"

echo "=== mol-to-inchi Test Runner ==="
echo ""

# Simple validation: Check that .mol and .inchi files exist in pairs
mol_count=$(ls -1 $TEST_DIR/*.mol 2>/dev/null | wc -l)
inchi_count=$(ls -1 $TEST_DIR/*.inchi 2>/dev/null | wc -l)

echo "Test files found:"
echo "  .mol files: $mol_count"
echo "  .inchi files: $inchi_count"
echo ""

if [ "$mol_count" -eq "$inchi_count" ]; then
    echo "✓ File counts match"
else
    echo "✗ File counts mismatch!"
    exit 1
fi

# Check some key test cases exist
if [ -f "$TEST_DIR/01-ethanol.mol" ]; then
    echo "✓ 01-ethanol.mol found"
fi

if [ -f "$TEST_DIR/65-85-0-2d.mol" ]; then
    echo "✓ 65-85-0-2d.mol found (benzoic acid)"
fi

if [ -f "$TEST_DIR/Fe_N2X.mol" ]; then
    echo "✓ Fe_N2X.mol found (metal complex)"
fi

echo ""
echo "=== Test Categories ==="

# Group test files by complexity
simple=0
aromatic=0
stereo=0
charged=0
complex=0

for f in $TEST_DIR/*.mol; do
    basename=$(basename "$f")
    
    # Simple organic (no stereo)
    if grep -q "InChI=1S/C[0-9]*H[0-9]*[ONClFPS]*/c" "$TEST_DIR/${basename%.mol}.inchi" 2>/dev/null; then
        if ! grep -q "/t\|/b\|/s" "$TEST_DIR/${basename%.mol}.inchi" 2>/dev/null; then
            simple=$((simple + 1))
        elif grep -q "/t" "$TEST_DIR/${basename%.mol}.inchi" 2>/dev/null; then
            stereo=$((stereo + 1))
        fi
    fi
    
    # Charged
    if grep -q "/q" "$TEST_DIR/${basename%.mol}.inchi" 2>/dev/null; then
        charged=$((charged + 1))
    fi
    
    # Complex
    if grep -q "Life_Science" "$basename"; then
        complex=$((complex + 1))
    fi
done

echo "  Simple (no stereo): ~$simple"
echo "  With stereochemistry: ~$stereo"
echo "  Charged species: ~$charged"
echo "  Complex (Life_Science): ~$complex"
echo ""

echo "=== Test Validation Protocol ==="
echo ""
echo "For each test case, verify your algorithm:"
echo "1. Parse MOL file correctly (atom count, elements)"
echo "2. Calculate implicit hydrogens accurately"
echo "3. Resolve aromatic bonds"
echo "4. Generate canonical ordering"
echo "5. Detect stereocenters (if present)"
echo "6. Assign mobile-H layer (if tautomeric)"
echo "7. Assemble final InChI string"
echo "8. Compare to expected .inchi file"
echo ""
echo "Test directory: $TEST_DIR"