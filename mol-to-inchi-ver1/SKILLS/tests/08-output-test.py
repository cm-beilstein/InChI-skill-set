"""Tests for Stage 8: Output Formatting."""


def test_output_ethanol():
    """Test ethanol InChI output."""
    assembled = assemble_inchi(
        detect_rings(
            handle_tautomerism(
                calculate_stereochemistry(
                    canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
                ))
            ))
        )
    output = format_output(assembled)

    assert output["inchi"].startswith("InChI=1S/")
    assert "C2H6O" in output["inchi"]


def test_inchikey_format():
    """Test InChIKey format."""
    output = format_output(
        assemble_inchi(
            detect_rings(
                handle_tautomerism(
                    calculate_stereochemistry(
                        canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
                    ))
                ))
            ))
        )

    key = output["inchi_key"]
    assert len(key) == 27
    assert key.count('-') == 2


def test_inchikey_stability():
    """Same input produces same InChIKey."""
    output1 = format_output(assemble_inchi(...))
    output2 = format_output(assemble_inchi(...))

    assert output1["inchi"] == output2["inchi"]
    assert output1["inchi_key"] == output2["inchi_key"]


def test_inchikey_collision():
    """Different molecules should have different keys."""
    output_ethanol = format_output(assemble_inchi(...))
    output_methanol = format_output(assemble_inchi(methanol_result))

    assert output_ethanol["inchi_key"] != output_methanol["inchi_key"]


if __name__ == "__main__":
    import sys
    sys.exit(0)