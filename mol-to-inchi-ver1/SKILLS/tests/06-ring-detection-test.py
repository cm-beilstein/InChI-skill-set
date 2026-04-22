"""Tests for Stage 6: Ring Detection."""


def test_ring_benzene():
    """Test benzene ring detection."""
    result = detect_rings(
        handle_tautomerism(
            calculate_stereochemistry(
                canonicalize(normalize(parse_mol("examples/06-benzene.mol")))
            ))
        )

    assert len(result["rings"]["sssr"]) == 1
    assert len(result["rings"]["sssr"][0]) == 6


def test_ring_naphthalene():
    """Test naphthalene ring detection."""
    result = detect_rings(
        handle_tautomerism(
            calculate_stereochemistry(
                canonicalize(normalize(parse_mol("examples/06-naphthalene.mol")))
            ))
        )

    assert len(result["rings"]["sssr"]) == 2


def test_no_rings():
    """Test acyclic molecule."""
    result = detect_rings(
        handle_tautomerism(
            calculate_stereochemistry(
                canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
            ))
        )

    assert len(result["rings"]["sssr"]) == 0


def test_ring_size():
    """Test ring sizes are minimal."""
    result = detect_rings(
        handle_tautomerism(
            calculate_stereochemistry(
                canonicalize(normalize(parse_mol("examples/06-benzene.mol")))
            ))
        )

    for ring in result["rings"]["sssr"]:
        for other in result["rings"]["all_rings"]:
            if other != ring:
                assert len(ring) <= len(other)


if __name__ == "__main__":
    import sys
    sys.exit(0)