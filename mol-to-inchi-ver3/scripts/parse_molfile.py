#!/usr/bin/env python3
"""
parse_molfile.py — Parse MOL V2000/V3000 files into Python data structures.
Usage: python3 scripts/parse_molfile.py <molecule.mol>

Returns atoms and bonds as Python dicts.
"""

import sys
import re

PERIODIC = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
    'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
    'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Fe': 26, 'Cu': 29,
    'Zn': 30, 'Br': 35, 'I': 53, 'D': 1, 'T': 1,
    'Ti': 22, 'Mn': 25, 'Co': 27, 'Ni': 28, 'Ga': 31, 'Ge': 32,
    'As': 33, 'Se': 34, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39,
    'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45,
    'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50, 'Sb': 51,
    'Te': 52, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58,
    'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64,
    'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70,
    'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76,
    'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82,
    'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88,
    'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94,
    'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100,
    'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105,
    'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110,
    'Rg': 111, 'Cn': 112, 'Nh': 113, 'Fl': 114, 'Mc': 115,
    'Lv': 116, 'Ts': 117, 'Og': 118,
}


def charge_code_to_charge(code):
    if code == 0:
        return 0
    if code == 1:
        return 3
    if code == 2:
        return 2
    if code == 3:
        return 1
    if code == 4:
        return -1
    if code == 5:
        return -2
    if code == 6:
        return -3
    if code == 7:
        return 0
    return 0


def parse_mol_v2000(content):
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if 'V2000' in line or 'V3000' in line:
            counts_idx = i
            break
    else:
        counts_idx = 3
    counts_line = lines[counts_idx].split()
    num_atoms = int(counts_line[0])
    num_bonds = int(counts_line[1])

    atoms = []
    for i in range(num_atoms):
        line = lines[counts_idx + 1 + i]
        x = float(line[0:10].strip())
        y = float(line[10:20].strip())
        z = float(line[20:30].strip())
        symbol = line[31:34].strip()
        mass_diff = int(line[34:36].strip() or '0')
        charge_code = int(line[36:38].strip() or '0')
        parity = int(line[38:40].strip() or '0')
        h_count_field = int(line[40:42].strip() or '0')
        valence_field = int(line[42:44].strip() or '0')

        if symbol == 'D':
            symbol = 'H'
            mass_diff = 2
        elif symbol == 'T':
            symbol = 'H'
            mass_diff = 3

        el_num = PERIODIC.get(symbol, 0)
        explicit_h = max(0, h_count_field - 1)
        charge = charge_code_to_charge(charge_code)

        atoms.append({
            'orig': i + 1,
            'el': symbol,
            'el_num': el_num,
            'x': x, 'y': y, 'z': z,
            'mass_diff': mass_diff,
            'charge': charge,
            'parity': parity,
            'explicit_h': explicit_h,
            'valence_field': valence_field,
            'neighbors': [],
            'bond_types': [],
            'bond_stereo': [],
        })

    bond_start = counts_idx + 1 + num_atoms
    for i in range(num_bonds):
        line = lines[bond_start + i]
        a1 = int(line[0:3].strip())
        a2 = int(line[3:6].strip())
        btype = int(line[6:9].strip())
        stereo = int(line[9:12].strip() or '0')

        atoms[a1 - 1]['neighbors'].append(a2 - 1)
        atoms[a1 - 1]['bond_types'].append(btype)
        atoms[a1 - 1]['bond_stereo'].append(stereo)
        atoms[a2 - 1]['neighbors'].append(a1 - 1)
        atoms[a2 - 1]['bond_types'].append(btype)
        atoms[a2 - 1]['bond_stereo'].append(stereo)

    return atoms


def parse_mol_v3000(content):
    atoms = []
    bonds = []
    lines = content.splitlines()
    i = 0
    while i < len(lines) and 'BEGIN ATOM' not in lines[i]:
        i += 1
    i += 1

    while i < len(lines) and 'END ATOM' not in lines[i]:
        line = lines[i]
        if line.strip().startswith('M  V30'):
            parts = line.split()
            idx = int(parts[2])
            symbol = parts[3]
            x = float(parts[4])
            y = float(parts[5])
            z = float(parts[6])
            charge = 0
            parity = 0
            mass_diff = 0
            for j, p in enumerate(parts[7:]):
                if p == 'CHG=':
                    charge = int(parts[7 + j + 1][4:])
                elif p == 'CFG=':
                    parity = int(parts[7 + j + 1][4:])
                elif p == 'MASS=':
                    mass_diff = int(parts[7 + j + 1][5:])
            if symbol == 'D':
                symbol = 'H'
                mass_diff = 2
            elif symbol == 'T':
                symbol = 'H'
                mass_diff = 3
            el_num = PERIODIC.get(symbol, 0)
            atoms.append({
                'orig': idx, 'el': symbol, 'el_num': el_num,
                'x': x, 'y': y, 'z': z,
                'mass_diff': mass_diff, 'charge': charge, 'parity': parity,
                'explicit_h': 0, 'valence_field': 0,
                'neighbors': [], 'bond_types': [], 'bond_stereo': [],
            })
        i += 1

    while i < len(lines) and 'BEGIN BOND' not in lines[i]:
        i += 1
    i += 1

    while i < len(lines) and 'END BOND' not in lines[i]:
        line = lines[i]
        if line.strip().startswith('M  V30'):
            parts = line.split()
            a1 = int(parts[3])
            a2 = int(parts[4])
            btype = int(parts[2])
            stereo = 0
            for p in parts[5:]:
                if p.startswith('CFG='):
                    stereo = int(p[4:])
            bonds.append({'a1': a1, 'a2': a2, 'type': btype, 'stereo': stereo})
        i += 1

    for bond in bonds:
        atoms[bond['a1'] - 1]['neighbors'].append(bond['a2'] - 1)
        atoms[bond['a1'] - 1]['bond_types'].append(bond['type'])
        atoms[bond['a1'] - 1]['bond_stereo'].append(bond['stereo'])
        atoms[bond['a2'] - 1]['neighbors'].append(bond['a1'] - 1)
        atoms[bond['a2'] - 1]['bond_types'].append(bond['type'])
        atoms[bond['a2'] - 1]['bond_stereo'].append(bond['stereo'])

    return atoms


def parse_mol(content):
    if 'V3000' in content:
        return parse_mol_v3000(content)
    return parse_mol_v2000(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/parse_molfile.py <molecule.mol>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        content = f.read()

    atoms = parse_mol(content)
    print(f"Atoms: {len(atoms)}")
    for i, atom in enumerate(atoms):
        print(f"  {i+1}: {atom['el']} (Z={atom['el_num']}) "
              f"charge={atom['charge']} parity={atom['parity']} "
              f"explicit_H={atom['explicit_h']} mass_diff={atom['mass_diff']}")
        if atom['neighbors']:
            nb = [(atoms[j]['el'], atoms[j]['orig'], bt)
                   for j, bt in zip(atom['neighbors'], atom['bond_types'])]
            print(f"    neighbors: {nb}")

    print(f"Bonds: {sum(len(a['neighbors']) for a in atoms) // 2}")


if __name__ == '__main__':
    main()