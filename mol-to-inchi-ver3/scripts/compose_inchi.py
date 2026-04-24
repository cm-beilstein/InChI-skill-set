#!/usr/bin/env python3
"""
compose_inchi.py — Assemble InChI layers from canonical data.
Usage: python3 scripts/compose_inchi.py <atoms.json> <canonical_nums.json>
"""

import sys
import json


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


def build_connectivity(atoms, canonical_nums):
    n = len(atoms)
    atom_conn = {}
    for i in range(n):
        cni = canonical_nums[i]
        neigh = [(canonical_nums[neigh], bt)
                 for neigh, bt in zip(atoms[i]['neighbors'], atoms[i]['bond_types'])]
        neigh.sort()
        atom_conn[cni] = [x[0] for x in neigh]

    parts = []
    for pos in range(1, n + 1):
        parts.append(str(pos))
        for nc in atom_conn[pos]:
            parts.append(str(nc))
    return ''.join(parts)


def compute_charge(atoms):
    return sum(atom.get('charge', 0) for atom in atoms)


def compose(atoms, canonical_nums, formula=None):
    compute_implicit_h(atoms)
    n = len(atoms)
    if formula is None:
        c_count = sum(1 for a in atoms if a['el_num'] == 6)
        o_count = sum(1 for a in atoms if a['el_num'] == 8)
        h_count = sum(a.get('implicit_h', 0) for a in atoms)
        formula = f'C{c_count}H{h_count}O{o_count}' if o_count else f'C{c_count}H{h_count}'

    layers = [f'InChI=1S/{formula}']

    conn = build_connectivity(atoms, canonical_nums)
    layers.append(f'/c{conn}')

    h_pos = {}
    for i in range(n):
        cni = canonical_nums[i]
        nh = atoms[i].get('implicit_h', 0)
        if nh > 0:
            h_pos[cni] = nh

    if h_pos:
        parts = []
        for pos in sorted(h_pos.keys()):
            nh = h_pos[pos]
            parts.append(f'{pos}' + ('H' + str(nh) if nh > 1 else 'H'))
        layers.append('/h' + ','.join(parts))

    charge = compute_charge(atoms)
    if charge != 0:
        sign = '+' if charge > 0 else '-'
        layers.append(f'/q{sign}{abs(charge)}')

    return ''.join(layers)


def main():
    if len(sys.argv) < 3:
        print("Usage: compose_inchi.py <atoms.json> <canonical_nums.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        atoms = json.load(f)
    with open(sys.argv[2]) as f:
        canonical_nums = json.load(f)
    result = compose(atoms, canonical_nums)
    print(result)


if __name__ == '__main__':
    main()