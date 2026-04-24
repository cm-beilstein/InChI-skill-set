#!/usr/bin/env python3
"""
canonicalize.py — Extended connectivity canonicalization.
Usage: python3 scripts/canonicalize.py <atoms.json>
Returns canonical ordering and ranks.
"""

import sys
import json
import hashlib


def compute_implicit_h(atoms):
    ST_VAL = {1: 1, 5: 3, 6: 4, 7: 3, 8: 2, 9: 1, 15: 3, 16: 2, 17: 1, 35: 1, 53: 1}
    for atom in atoms:
        el = atom['el_num']
        if el == 0:
            atom['implicit_h'] = 0
            continue
        std_val = ST_VAL.get(el, 4)
        bos = sum(atom['bond_types'])
        atom['implicit_h'] = max(0, std_val - bos)


def canonical_order(atoms):
    n = len(atoms)
    compute_implicit_h(atoms)

    classes = []
    for atom in atoms:
        key = (atom['el_num'], len(atom['neighbors']), atom.get('implicit_h', 0),
               atom.get('iso_mass', 0))
        classes.append(key)

    changed = True
    iteration = 0
    max_iter = 100
    while changed and iteration < max_iter:
        changed = False
        iteration += 1
        new_classes = []
        for i, atom in enumerate(atoms):
            neigh_patterns = []
            for j, neigh_idx in enumerate(atom['neighbors']):
                bt = atom['bond_types'][j]
                neigh_class = classes[neigh_idx]
                neigh_patterns.append((neigh_class, bt))
            neigh_patterns.sort()
            new_key = (classes[i], tuple(neigh_patterns))
            if new_key != classes[i]:
                changed = True
            new_classes.append(new_key)
        classes = new_classes

    seen = {}
    rank_map = {}
    next_rank = 1
    for i, cls in enumerate(classes):
        if cls not in seen:
            seen[cls] = next_rank
            rank_map[i] = next_rank
            next_rank += 1
        else:
            rank_map[i] = seen[cls]

    atom_order = sorted(range(n), key=lambda i: (rank_map[i], i))
    canonical_nums = [0] * n
    for canon_pos, orig_idx in enumerate(atom_order):
        canonical_nums[orig_idx] = canon_pos + 1

    ranks = [rank_map[i] for i in range(n)]
    return canonical_nums, ranks, atom_order


def main():
    with open(sys.argv[1]) as f:
        atoms = json.load(f)
    canonical_nums, ranks, order = canonical_order(atoms)
    print("Canonical ordering (1-indexed):", canonical_nums)
    print("Ranks:", ranks)


if __name__ == '__main__':
    main()