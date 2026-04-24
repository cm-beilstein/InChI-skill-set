# InChIKey Base-26 Triplet Table

SHA-256 produces 32 bytes (256 bits). InChIKey uses base-26 encoding (A-Z, 26 letters).
Each triplet encodes 14 bits: 2^14 = 16384 valid values.
26^3 = 17576 possible, so 1192 values are unused.

## Encoding Scheme

**Major block (14 chars):**
- 4 triplets × 14 bits = 56 bits
- 1 doublet × 9 bits = 9 bits
- Total: 65 bits → 14 characters

**Minor block (9 chars):**
- 2 triplets × 14 bits = 28 bits
- 1 doublet × 9 bits = 9 bits
- Total: 37 bits → 9 characters

## Doublet Encoding (9 bits)

9 bits can represent 0-511. Map to 2 letters:
- Bits 0-511 → 512 valid doublets
- Omit doublets starting with E
- Example: `AA`, `AB`, ..., `AZ`, `BA`, ..., `ZY` (no `E`-start)

## Triplet Encoding (14 bits)

14 bits can represent 0-16383. Map to 3 letters:
- `triplet[0]` = `AAA`, `triplet[1]` = `AAB`, ...
- Omit triplets starting with `E`
- Full lookup table: 16384 entries

## InChIKey Format

```
XXXXXXXXXXXXXX-YYYYYYYYY-Z-S
```
14 + 1 + 9 + 1 + 1 + 1 = 27 characters

- 14 chars: major hash (4 triplets + 1 doublet)
- `-`: separator
- 9 chars: minor hash (2 triplets + 1 doublet)
- 1 char: protonation flag (N=0, O=+1, ..., Z=+12, M=-1, ..., A=<-12)
- 1 char: version (`A`=v1)
- 1 char: format (`S`=standard, `N`=non-standard, `B`=beta)

## SHA-256 Hash Steps

1. Take InChI string as bytes
2. Pad: append `0x80`, then zeros until length ≡ 448 mod 512, then 64-bit big-endian length
3. Process 512-bit blocks through 64 rounds
4. Output: 8 × 32-bit words (256 bits)

## Full InChIKey Algorithm

```
major = SHA256("InChI=1S/" + formula + "/c" + connections + "/h" + mobile_H)
minor = SHA256("/i" + isotopes + "/s" + sp2 + "/t" + sp3 + "/q" + charge)

major_block = base26_encode(major[:14])   # 14 chars
minor_block = base26_encode(minor[:9])    # 9 chars

if charge > 0: proto = chr(ord('N') + charge)
elif charge < 0: proto = chr(ord('N') - abs(charge))
else: proto = 'N'

inchi_key = major_block + "-" + minor_block + proto + "A-S"
```

## Example

Benzene: `InChI=1S/C6H6/c1-2-3-4-5-6-1/h6H`

Major = SHA-256 of `/c1-2-3-4-5-6-1/h6H`
→ hash → `LFQDQGVMQVDCBZ`
Minor = SHA-256 of `/s`
→ hash → `UHFFFAOY`
Protonation = `N`
Version = `A`
Format = `S`

InChIKey: `LFQDQGVMQVDCBZ-UHFFFAOY-N-A-S` (27 chars)