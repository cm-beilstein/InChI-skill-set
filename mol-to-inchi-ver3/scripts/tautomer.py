#!/usr/bin/env python3
"""
tautomer.py — Tautomer group detection (PT_02 keto-enol).
Usage: python3 scripts/tautomer.py <atoms.json> <canonical_nums.json>
"""

import sys
import json


def find_keto_enol(atoms, canonical_nums):
    groups = []
    n = len(atoms)
    for i, atom in enumerate(atoms):
        if atom['el_num'] != 6:
            continue
        double_bonds = [j for j, bt in enumerate(atom['bond_types']) if bt == 2]
        for j in double_bonds:
            neigh = atom['neighbors'][j]
            nb = atoms[neigh]
            if nb['el_num'] == 8:
                cni = canonical_nums[i]
                cnj = canonical_nums[neigh]
                groups.append({'type': 'PT_02', 'endpoint_O': cnj, 'endpoint_C': cni})
    return groups


def main():
    if len(sys.argv) < 3:
        print("Usage: tautomer.py <atoms.json> <canonical_nums.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        atoms = json.load(f)
    with open(sys.argv[2]) as f:
        canonical_nums = json.load(f)
    groups = find_keto_enol(atoms, canonical_nums)
    print(f"Tautomer groups: {groups}")


if __name__ == '__main__':
    main()