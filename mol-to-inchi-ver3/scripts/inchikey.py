#!/usr/bin/env python3
"""
inchikey.py — Generate InChIKey from InChI string.
Usage: python3 scripts/inchikey.py "<inchi_string>"
"""

import sys
import hashlib

TRIPLET_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def sha256(data):
    return hashlib.sha256(data.encode()).digest()


def base26_triplet(value):
    a = (value // 676) % 26
    b = (value // 26) % 26
    c = value % 26
    return TRIPLET_CHARS[a] + TRIPLET_CHARS[b] + TRIPLET_CHARS[c]


def base26_doublet(value):
    a = value // 26
    b = value % 26
    return TRIPLET_CHARS[a] + TRIPLET_CHARS[b]


def triplet_lookup():
    table = {}
    idx = 0
    for a in range(26):
        for b in range(26):
            for c in range(26):
                s = TRIPLET_CHARS[a] + TRIPLET_CHARS[b] + TRIPLET_CHARS[c]
                if s[0] != 'E':
                    table[idx] = s
                    idx += 1
    return table


def encode_inchikey(major_str, minor_str, charge=0):
    TRIPLET = triplet_lookup()

    major_digest = sha256(major_str)
    minor_digest = sha256(minor_str)

    major_chars = []
    for i in range(4):
        val = major_digest[i * 2] * 256 + major_digest[i * 2 + 1]
        if val >= 16384:
            val = val % 16384
        major_chars.append(TRIPLET.get(val % 16384, 'AAA'))

    val56 = major_digest[8] * 256 + major_digest[9]
    if val56 >= 512:
        val56 = val56 % 512
    major_chars.append(base26_doublet(val56 % 512))

    minor_chars = []
    for i in range(2):
        val = minor_digest[i * 2] * 256 + minor_digest[i * 2 + 1]
        if val >= 16384:
            val = val % 16384
        minor_chars.append(TRIPLET.get(val % 16384, 'AAA'))

    val28 = minor_digest[4] * 256 + minor_digest[5]
    if val28 >= 512:
        val28 = val28 % 512
    minor_chars.append(base26_doublet(val28 % 512))

    major_block = ''.join(major_chars[:14])
    minor_block = ''.join(minor_chars[:9])

    if charge > 12:
        charge = 12
    elif charge < -12:
        charge = -12
    if charge >= 0:
        proto = chr(ord('N') + charge)
    else:
        proto = chr(ord('N') - abs(charge))

    return f'{major_block}-{minor_block}-{proto}-A-S'


def parse_inchi_to_blocks(inchi):
    if not inchi.startswith('InChI='):
        return '', '', 0
    parts = inchi[6:].split('/')
    version = parts[0]
    layers = {}
    for layer in parts[1:]:
        if layer:
            prefix = layer[0]
            layers[prefix] = layer[1:]
    major = ''
    minor = ''
    charge = 0
    if 'f' in layers:
        major += '/f' + layers['f']
    if 'c' in layers:
        major += '/c' + layers['c']
    if 'h' in layers:
        major += '/h' + layers['h']
    if 'q' in layers:
        q = layers['q']
        sign = 1 if q.startswith('+') else -1
        charge = sign * int(q[1:])
        major += '/q' + q
    if 's' in layers:
        minor += '/s' + layers['s']
    if 't' in layers:
        minor += '/t' + layers['t']
    if 'i' in layers:
        minor += '/i' + layers['i']
    if 'm' in layers:
        minor += '/m' + layers['m']
    return major, minor, charge


def main():
    if len(sys.argv) < 2:
        print("Usage: inchikey.py \"InChI=1S/...\"")
        sys.exit(1)
    inchi = sys.argv[1]
    major, minor, charge = parse_inchi_to_blocks(inchi)
    key = encode_inchikey(major, minor, charge)
    print(key)


if __name__ == '__main__':
    main()