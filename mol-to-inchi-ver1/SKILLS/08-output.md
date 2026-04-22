# 08-output: InChI/InChIKey Formatting

## Purpose

Format the final InChI string and generate the InChIKey (hash-based identifier). The InChIKey is a 27-character hash derived from the InChI string using SHA-256.

## Input

```python
{
    "inchi": str,
    "layers": {...}
}
```

(from Stage 7: InChI Assembly)

## Output

```python
{
    "inchi": str,           # "InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)"
    "inchi_key": str,       # "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"
    "standard": bool        # Is standard InChI?
}
```

## InChI String Format

### Standard InChI

```
InChI=1S/<formula>/<layers>
```

- `InChI=1S` = Standard InChI version 1
- Non-standard options: `InChI=1` (1S not required)

### InChIKey Format

27 characters in 3 blocks of 9:

```
XXXXXXXXX-XXXXXXXXX-A
│         │ │     │
│         │ │     └── 1 char (layer indicator)
│         │ └────── 8 chars (hash block 2)
│         └──────── 9 chars (hash block 1)
└──────────────── 9 chars (SHA-256 first 9 bytes)
```

- Block 1 (9 chars): SHA-256 hash of InChI (version layer + formula + connectivity)
- Block 2 (8 chars): Additional layers hash
- Block A (1 char): Layer summary
  - `N` = Standard
  - `F` = Fixed H layer
  - `M` = Mobile H layer  
  - `R` = Reconnected layer
  - `O` = Isotope layer
  - etc.

## Algorithm

### Generate InChIKey

```
def generate_inchikey(inchi):
    # Calculate hash blocks
    block1 = sha256(inchi_without_layers)[:9]
    block2 = sha256(additional_layers)[:8]
    
    # Layer indicator
    layer_char = determine_layer_char(layers)
    
    return f"{block1}-{block2}-{layer_char}"
```

### SHA-256 Hashing

Use standard SHA-256, then encode in modified Base64 (B芙RY89 with `/` instead of `+`):

```python
import hashlib
import base64

def sha256_hash(data):
    h = hashlib.sha256(data.encode()).digest()
    encoded = base64.b64encode(h).decode()
    # Replace + with /, = with -
    encoded = encoded.replace('+', '/').replace('=', '-')
    return encoded[:27]
```

## Examples

### Example 1: Ethanol

```
InChI: InChI=1S/C2H6O/c1-2/h1H2,(H,3,4)
InChIKey: LFQSCWFLJHTTHZ-UHFFFAOYSA-N
```

| Block | Value |
|-------|-------|
| 1 | `LFQSCWFLJ` |
| 2 | `HTTHZ-UH` |
| 3 | `FFAOYSA-N` |

### Example 2: Caffeine

```
InChI: InChI=1S/C8H10N4O2/c1-12-6(13)8(14)3(15)5(16)7(17)10(12)2-
       4/h3H,2H2,1H3
InChIKey: RYYVEVVNFCQBTK-UHFFFAOYSA-N
```

### Example 3: Benzene

```
InChI: InChI=1S/c1-6/h1-6H
InChIKey: UHOVQNZEXAWPGC-UHFFFAOYSA-N
```

## Tests

```python
def test_output_ethanol():
    """Test ethanol InChI output."""
    assembled = assemble_inchi(...)
    output = format_output(assembled)

    assert output["inchi"].startswith("InChI=1S/")
    assert "C2H6O" in output["inchi"]


def test_inchikey_format():
    """Test InChIKey format."""
    output = format_output(assemble_inchi(...))

    key = output["inchi_key"]
    assert len(key) == 27
    assert key.count('-') == 2  # Two dashes


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
```

## Cross-References

- **Previous stage:** `07-assemble.md`
- **Final output:** Complete InChI and InChIKey
- **Hashing:** SHA-256 as defined in InChI Technical Manual