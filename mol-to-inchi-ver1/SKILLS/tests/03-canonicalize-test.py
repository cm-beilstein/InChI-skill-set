"""Tests for Stage 3: Canonicalization."""


def test_canonicalize_ethanol():
    """Test canonical labels for ethanol."""
    normalized = normalize(parse_mol("examples/01-ethanol.mol"))
    canonical = canonicalize(normalized)

    assert all("canonical_label" in a for a in canonical["atoms"])

    canonical2 = canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
    assert labels_match(canonical, canonical2)


def test_canonicalize_different_molecules():
    """Different molecules should have different canonical labels."""
    ethanol_can = canonicalize(normalize(parse_mol("examples/01-ethanol.mol")))
    methanol_can = canonicalize(normalize(parse_mol("examples/03-methanol.mol")))

    assert ethanol_can["canonical_labels"] != methanol_can["canonical_labels"]


def test_canonicalize_isomers():
    """Test canonical labels for isomers."""
    butane = canonicalize(normalize(parse_mol("examples/03-butane.mol")))
    isobutane = canonicalize(normalize(parse_mol("examples/03-isobutane.mol")))

    assert butane["canonical_labels"] != isobutane["canonical_labels"]


def test_canonicalize_preserve_connectivity():
    """Canonicalization preserves connectivity."""
    normalized = normalize(parse_mol("examples/01-ethanol.mol"))
    canonical = canonicalize(normalized)

    assert len(canonical["bonds"]) == len(normalized["bonds"])


if __name__ == "__main__":
    import sys
    sys.exit(0)