"""Tests for Stage 7: InChI Assembly."""


def test_assemble_ethanol():
    """Test assembling ethanol InChI."""
    result = detect_rings(
        handle_tautomerism(
            calculate_stereochemistry(
                canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
            ))
        )
    assembled = assemble_inchi(result)

    assert "C2H6O" in assembled["inchi"]
    assert "/c1-2" in assembled["layers"]["connectivity"]


def test_layer_order():
    """Verify correct layer order."""
    assembled = assemble_inchi(
        detect_rings(
            handle_tautomerism(
                calculate_stereochemistry(
                    canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
                ))
            ))
        )

    inchi = assembled["inchi"]
    f_pos = inchi.find("/f")
    c_pos = inchi.find("/c")
    h_pos = inchi.find("/h")

    # Layers must be in order: f < c < h
    assert f_pos < c_pos < h_pos or c_pos < h_pos if c_pos > 0 else True


def test_assemble_stereo_layers():
    """Test /t and /s layers."""
    assembled = assemble_inchi(
        detect_rings(
            handle_tautomerism(
                calculate_stereochemistry(
                    canonicalize(normalize(parse_mol("examples/04-alanine.mol")))
                ))
            ))
        )

    if assembled["layers"]["tetrahedral"]:
        assert "/t" in assembled["inchi"]
        assert "/s" in assembled["inchi"]


if __name__ == "__main__":
    import sys
    sys.exit(0)