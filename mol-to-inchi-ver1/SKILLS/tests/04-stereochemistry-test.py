"""Tests for Stage 4: Stereochemistry."""


def test_stereo_tetrahedral():
    """Test tetrahedral parity calculation."""
    canonical = canonicalize(normalize(parse_mol("examples/04-alanine.mol")))
    stereo = calculate_stereochemistry(canonical)

    assert len(stereo["tetrahedral"]) >= 1
    chiral = stereo["tetrahedral"][0]
    assert chiral["parity"] in [1, 2, 3]


def test_stereo_geometric():
    """Test geometric (E/Z) parity."""
    canonical = canonicalize(normalize(parse_mol("examples/04-but-2-ene.mol")))
    geo_stereo = calculate_stereochemistry(canonical)

    assert len(geo_stereo["geometric"]) >= 1
    assert geo_stereo["geometric"][0]["type"] in ["E", "Z"]


def test_stereo_no_chiral():
    """Molecules without chirality."""
    canonical = canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
    stereo = calculate_stereochemistry(canonical)

    assert len(stereo["tetrahedral"]) == 0
    assert len(stereo["geometric"]) == 0


def test_stereo_type():
    """Test /s stereo type layer."""
    canonical = canonicalize(normalize(parse_mol("examples/04-alanine.mol")))
    stereo = calculate_stereochemistry(canonical)

    assert "type" in stereo


if __name__ == "__main__":
    import sys
    sys.exit(0)