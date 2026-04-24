#!/usr/bin/env python3
"""
stereo.py — CIP priority and R/S, E/Z calculation.
Usage: python3 scripts/stereo.py <atoms.json> <canonical_nums.json>
"""

import sys
import json


def cip_rank_substituents(atom, atoms, visited, depth=0, max_depth=5):
    if depth > max_depth:
        return []
    subs = []
    for j, neigh in enumerate(atom['neighbors']):
        nb = atoms[neigh]
        bt = atom['bond_types'][j]
        subs.append((nb['el_num'], bt))
    subs.sort(reverse=True)
    return subs


def detect_sp3_stereo(atoms, canonical_nums):
    sp3_centers = []
    for i, atom in enumerate(atoms):
        if len(atom['neighbors']) < 4:
            continue
        parity = atom.get('parity', 0)
        if parity in (0, 3):
            continue

        cni = canonical_nums[i]
        n_h = atom.get('implicit_h', 0)
        if n_h + len(atom['neighbors']) < 4:
            continue

        r = 'R' if parity in (1,) else 'S'
        sp3_centers.append((cni, r))
    return sp3_centers


def detect_sp2_stereo(atoms, canonical_nums):
    sp2_bonds = []
    for i, atom in enumerate(atoms):
        for j, stereo in enumerate(atom['bond_stereo']):
            if stereo in (1, 6):
                neigh = atom['neighbors'][j]
                cni = canonical_nums[i]
                cnj = canonical_nums[neigh]
                direction = '+' if stereo == 1 else '-'
                key = (min(cni, cnj), max(cni, cnj))
                sp2_bonds.append((key, direction))
    return sp2_bonds


def main():
    if len(sys.argv) < 3:
        print("Usage: stereo.py <atoms.json> <canonical_nums.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        atoms = json.load(f)
    with open(sys.argv[2]) as f:
        canonical_nums = json.load(f)

    sp3 = detect_sp3_stereo(atoms, canonical_nums)
    sp2 = detect_sp2_stereo(atoms, canonical_nums)
    print(f"sp3 centers: {sp3}")
    print(f"sp2 bonds: {sp2}")


if __name__ == '__main__':
    main()