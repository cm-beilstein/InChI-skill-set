"""Tests for Stage 2: Normalization."""


def test_normalize_ethanol_no_change():
    """Ethanol has correct valencies - no changes."""
    parsed = parse_mol("examples/01-ethanol.mol")
    normalized = normalize(parsed)

    assert all(not a.get("corrected", False) for a in normalized["atoms"])
    assert len(normalized["normalization_log"]) == 0


def test_normalize_implicit_h():
    """Verify implicit hydrogens calculated."""
    parsed = parse_mol("examples/01-ethanol.mol")
    normalized = normalize(parsed)

    carbons = [a for a in normalized["atoms"] if a["element"] == "C"]
    assert carbons[0]["implicit_h"] == 3
    assert carbons[1]["implicit_h"] == 2


def test_normalize_nitro():
    """Test nitro group valency correction."""
    parsed = parse_mol("examples/02-nitrobenzene.mol")
    normalized = normalize(parsed)

    nitrogen = next(a for a in normalized["atoms"] if a["element"] == "N")
    assert nitrogen["valence"] == 5
    assert nitrogen.get("corrected", False)


def test_normalize_carboxylate():
    """Test carboxylate charge handling."""
    parsed = parse_mol("examples/02-acrylate.mol")
    normalized = normalize(parsed)

    charges = [a.get("charge", 0) for a in normalized["atoms"]]
    assert sum(charges) == -1


def test_normalize_sulfonate():
    """Test sulfonate group."""
    parsed = parse_mol("examples/02-methyl-sulfonate.mol")
    normalized = normalize(parsed)

    sulfur = next(a for a in normalized["atoms"] if a["element"] == "S")
    assert sulfur["valence"] == 6


if __name__ == "__main__":
    import sys
    sys.exit(0)