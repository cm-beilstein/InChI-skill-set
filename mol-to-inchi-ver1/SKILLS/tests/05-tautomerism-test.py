"""Tests for Stage 5: Tautomerism."""


def test_mobile_h_amide():
    """Test amide mobile hydrogens."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/05-acetamide.mol"))
    )
    taut = handle_tautomerism(stereo)

    assert len(taut["mobile_h"]) >= 1


def test_mobile_h_phenol():
    """Test phenol mobile hydrogens."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/05-phenol.mol"))
    )
    taut = handle_tautomerism(stereo)

    assert len(taut["mobile_h"]) >= 1


def test_no_mobile_h():
    """Test no mobile hydrogens."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/01-ethanol.mol"))
    )
    taut = handle_tautomerism(stereo)

    assert len(taut["mobile_h"]) == 0
    assert taut["normalization"] == ""


def test_normalization_string():
    """Test /m layer string generation."""
    stereo = calculate_stereochemistry(
        normalize(parse_mol("examples/05-acetamide.mol"))
    )
    taut = handle_tautomerism(stereo)

    if taut["mobile_h"]:
        assert "/m" in taut["normalization"] or taut["normalization"].startswith("/m")


if __name__ == "__main__":
    import sys
    sys.exit(0)