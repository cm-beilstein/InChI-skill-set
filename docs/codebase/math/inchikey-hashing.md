# InChIKey Hashing Algorithm

**Analysis Date:** 2026-04-22

## 1. Overview

The InChIKey is a fixed-length, URL-safe identifier derived from the International Chemical Identifier (InChI). Hashing is necessary because InChI strings vary in length and contain characters that are problematic for database indexing and web usage (slashes, parentheses, special characters). The InChIKey provides a compact, consistent 27-character representation that uniquely identifies a chemical structure while enabling efficient indexing, searching, and web-based chemical informatics applications.

## 2. Hashing Requirements

**Fixed 27-Character Output:** The InChIKey must produce exactly 27 characters in a consistent format regardless of the input InChI string length. This constraint ensures uniform database field sizes, predictable URL lengths, and reliable string handling across different software systems.

**Collision Resistance:** The hashing algorithm must minimize the probability of two different InChI strings producing the same InChIKey (a hash collision). Given the fixed 27-character output space, the birthday paradox dictates that collisions become probable after approximately 2^(n/2) hashes are generated. With 27 base-26 characters representing approximately 127 bits of entropy (26^27 ≈ 2^127), the theoretical collision space remains astronomically large.

**One-Way Property:** It must be computationally infeasible to reverse-engineer the original InChI from an InChIKey. The one-way nature of the hash function ensures that the detailed chemical structure information cannot be recovered from the compact identifier, which is important for proprietary or sensitive chemical data.

## 3. SHA-256 Algorithm

**Cryptographic Hash Function:** The InChIKey generation uses SHA-256 (Secure Hash Algorithm 2) as specified in NIST FIPS 180-4. SHA-256 produces a 256-bit (32-byte) hash output and is currently considered cryptographically secure against known attack vectors including collision attacks and preimage attacks.

**NIST Standard (FIPS 180-4):** SHA-256 is defined in the NIST Secure Hash Standard (SHS), specifically FIPS PUB 180-4 published by the National Institute of Standards and Technology. The implementation in `sha2.c` follows the RFC 6234 standard and has been validated for conformance. The algorithm was originally designed by the NSA and published in 2001 as part of the SHA-2 family.

**Message Preprocessing:** Before hash computation, the input message undergoes padding to ensure its length is a multiple of 512 bits (64 bytes). Padding involves appending a '1' bit followed by enough '0' bits, with the final 64 bits representing the original message length in big-endian format. This preprocessing enables processing messages of arbitrary length.

**64 Rounds of Compression:** The SHA-256 compression function processes 512-bit message blocks through 64 rounds of mixing operations. Each round uses a fixed round constant K[i] and combines the current hash state with the message schedule derived from the input block. The compression function mixes message words with the state through logical operations (XOR, AND, OR, rotation) and modular addition. The 64 round constants (defined in `sha2.c` lines 128-193) prevent symmetry attacks and ensure proper diffusion of bits.

## 4. Base-26 Encoding

**Converting Hash to 27 Characters:** SHA-256 produces 256 bits, but the InChIKey uses only 27 base-26 characters. The encoding strategy uses triplets (14 bits each) and doublets (9 bits) to efficiently pack the hash bits into letter representations. Since 2^14 = 16,384 and 26^3 = 17,576 are approximately equal, three base-26 letters can encode 14 bits with high efficiency.

**Why Base-26 (vs Base-64 or Base-32):** Base-26 uses only uppercase English letters (A-Z), making InChIKeys URL-safe, case-insensitive for database storage, and human-readable. Base-64 includes lowercase, uppercase, numbers, and special characters (+, /, =), which can cause issues in URLs and file names. Base-32, while URL-safe, wastes more space than base-26. The all-letter format also facilitates chemical database integration and avoids character encoding issues.

**Character Set Restrictions:** The character set is restricted to uppercase letters A-Z only. No numbers, special characters, or lowercase letters appear in the standard InChIKey. This restriction ensures maximum compatibility across file systems, databases, and web frameworks. The triplet lookup table in `ikey_base26.c` (lines 73-579) maps 14-bit values to 16384 valid triplets, omitting triplets starting with 'E' to avoid common English letter confusion.

## 5. Layer Hashing

**Each Layer Hashed Separately:** The InChI contains multiple logical layers (formula, connectivity, stereochemistry). Each layer is hashed independently to create two separate hash components: the "major" hash and the "minor" hash. This separation enables partial structure matching and layer-specific analysis.

**Formula Layer Hash:** The major hash incorporates the chemical formula information (layer "/f"). This layer contains the molecular formula (e.g., C6H6 for benzene) and is considered the most fundamental identifier. The formula string is passed to SHA-256 to produce the first 256-bit digest.

**Connectivity Layer Hash:** The connectivity layer (/c) describes atom connections and bond types. When present, this layer is concatenated with the formula layer before hashing for the major component. The major hash thus represents the core molecular graph.

**Stereo Layer Hash:** The minor hash incorporates stereochemical information (/i, /m, /s layers). This includes isotopic labeling, ionic state, and 3D stereochemistry. The minor hash is computed separately and appended after a hyphen separator. This design enables queries for structural analogs by ignoring the minor hash.

## 6. InChIKey Structure

**Two-Part Format (AAAAAAA-BBBBB):** The InChIKey consists of two hash blocks separated by a hyphen. The first block contains 14 characters derived from the major hash. The second block contains 13 characters derived from the minor hash. The total length including the hyphen is 27 characters (14 + 1 + 13 - 1 = 27, accounting for overlap).

**14 Characters + 13 Characters:** The major block uses four triplets (4 × 14 = 56 bits) plus one doublet (9 bits), totaling 65 bits encoded as 14 characters. The minor block uses two triplets (28 bits) plus one doublet (9 bits), totaling 37 bits encoded as 13 characters. The different lengths reflect the relative importance and information content of each layer.

**Version Identifier:** The final character of the InChIKey indicates the InChI version. Current InChI version 1 uses 'O' or 'S' flags to indicate standard vs. non-standard InChI, followed by version indicators. This enables future algorithm changes while maintaining backward compatibility with existing identifiers.

## 7. Mathematical Formulas

**SHA-256 Compression:**
```
H[i] = Σᵢ Kᵢ ⊕ CompressionRound(M[i], H[i-1])

Where:
- Kᵢ = Round constant (64 constants from FIPS 180-4)
- M[i] = 512-bit message block i
- H[i-1] = Previous hash state (8 thirty-two-bit words)
- ⊕ = XOR operation
```

**Base-26 Triplet Encoding:**
```
T = floor(HashBits / 16384)  // 14-bit value
Triplet = LookupTable[T]      // Maps 0-16383 to "AAA"-"ZZY"

Each triplet encodes 14 bits:
26^3 = 17,576 possible values
2^14 = 16,384 valid values
Unused = 1,192 values (omitted from lookup table)
```

**InChIKey Assembly:**
```
MajorBlock[14] = triplet_1(digest_major) || triplet_2(digest_major) || 
                 triplet_3(digest_major) || triplet_4(digest_major) ||
                 dublet_56_64(digest_major)

MinorBlock[13] = triplet_1(digest_minor) || triplet_2(digest_minor) ||
                 dublet_28_36(digest_minor)

InChIKey = MajorBlock + '-' + MinorBlock + VersionFlag + ProtonationFlag
```

## 8. Code Location

**ikey_base26.c:** `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/ikey_base26.c`
- Contains the triplet lookup table (16,384 entries)
- Implements base26_triplet_1 through base26_triplet_4 functions
- Implements base26_dublet_for_bits_28_to_36 and base26_dublet_for_bits_56_to_64
- Handles the conversion from SHA-256 binary digest to base-26 character representation

**ikey_dll.c:** `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/ikey_dll.c`
- Contains the main InChIKey generation function (lines 380-452)
- Orchestrates the hashing process using SHA-256
- Concatenates major and minor hash components
- Adds version and protonation flags

**sha2.c:** `/home/bsmue/code/InChI/INCHI-1-SRC/INCHI_BASE/src/sha2.c`
- FIPS-180-2 compliant SHA-256 implementation
- Implements sha2_starts, sha2_update, sha2_finish, and sha2_csum functions
- Contains the 64 round constants and compression logic
- Uses big-endian byte ordering for NIST compliance

## 9. Security Considerations

**Collision Resistance:** SHA-256 provides 256-bit security against collision attacks. Finding two inputs producing the same hash requires approximately 2^128 operations (the birthday bound). With 27 base-26 characters representing ~127 bits of effective entropy, the InChIKey space remains sufficiently large. No practical collision attacks against SHA-256 are known as of 2026.

**Birthday Paradox Analysis:** With 26^27 ≈ 2^127 possible InChIKeys, the probability of a random collision becomes significant (50%) after approximately 2^63 InChIKeys are generated. Given the estimated 100+ million known chemicals, collision risk remains negligible. The chemical structure space is also constrained by physical laws, further reducing collision probability.

**Preimage Resistance:** SHA-256 provides 256-bit preimage resistance, meaning finding an input that produces a specific hash requires approximately 2^256 operations. The one-way property ensures that even with computational advances, recovering the original InChI from an InChIKey remains infeasible. This protects proprietary or sensitive chemical information encoded in InChI strings.

**Quantum Computing Threat:** Grover's algorithm could theoretically reduce SHA-256 security to 128 bits on a quantum computer. However, practical quantum computers capable of this attack do not exist as of 2026. The NIST post-quantum cryptography standardization process is monitoring this threat for future algorithm updates.

## 10. References

**NIST FIPS 180-4:** Secure Hash Standard (SHS)
- Publication: https://csrc.nist.gov/publications/detail/fips/180/4/final
- Defines SHA-256, SHA-384, SHA-512, SHA-224 algorithms
- Specifies message padding, hash computation, and validation tests

**RFC 6234:** US Secure Hash Algorithms (SHA and HMAC)
- https://datatracker.ietf.org/doc/html/rfc6234
- Provides C reference implementations compatible with FIPS 180-4

**InChI Technical Manual Section V:** InChIKey
- IUPAC InChI Trust official documentation
- Specifies InChIKey format, generation, and validation
- Available at: https://www.inchi-trust.org/technical-manual/

**InChIKey Generation Source Code:**
- `INCHI-1-SRC/INCHI_BASE/src/ikey_dll.c` - Main generation logic
- `INCHI-1-SRC/INCHI_BASE/src/ikey_base26.c` - Base-26 encoding
- `INCHI-1-SRC/INCHI_BASE/src/sha2.c` - SHA-256 implementation

---

*Document generated: 2026-04-22*
