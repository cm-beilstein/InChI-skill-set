#!/usr/bin/env python3
"""
mol_to_inchi.py — End-to-end MOL -> InChI pipeline.
Parses a MOL file through all 7 pipeline steps and outputs the InChI string.
Usage: python3 scripts/mol_to_inchi.py <molecule.mol>
"""

import sys

PERIODIC = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
    'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
    'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22,
    'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
    'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36,
    'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
    'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57,
    'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64,
    'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71,
    'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78,
    'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
    'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92,
    'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99,
    'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105,
    'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110, 'Rg': 111,
    'Cn': 112, 'Nh': 113, 'Fl': 114, 'Mc': 115, 'Lv': 116, 'Ts': 117, 'Og': 118,
    'D': 1, 'T': 1,
}

STANDARD_VALENCE = {
    1: 1, 5: 3, 6: 4, 7: 3, 8: 2, 9: 1, 15: 3, 16: 2, 17: 1,
    35: 1, 53: 1,
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
    return 0


def find_counts_line(lines):
    for i, line in enumerate(lines):
        if 'V2000' in line or 'V3000' in line:
            return i
    return 3


def parse_mol_v2000(content):
    lines = content.splitlines()
    counts_idx = find_counts_line(lines)
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


def compute_implicit_h(atoms):
    for atom in atoms:
        el_num = atom['el_num']
        if el_num == 0:
            atom['implicit_h'] = 0
            continue
        std_val = STANDARD_VALENCE.get(el_num, 4)
        bond_order_sum = sum(atom['bond_types'])
        atom['implicit_h'] = max(0, std_val - bond_order_sum)


def hill_formula(atoms):
    compute_implicit_h(atoms)
    counts = {}
    for atom in atoms:
        el = atom['el']
        counts[el] = counts.get(el, 0) + 1
    
    # Add implicit H to H count (not to the non-H element's count!)
    for atom in atoms:
        if atom['el'] != 'H':
            ih = atom.get('implicit_h', 0)
            if ih > 0:
                counts['H'] = counts.get('H', 0) + ih

    parts = []
    c_count = counts.pop('C', 0)
    if c_count:
        parts.append('C' + (str(c_count) if c_count > 1 else ''))
    h_count = counts.pop('H', 0)
    if h_count:
        parts.append('H' + (str(h_count) if h_count > 1 else ''))
    for el in sorted(counts.keys()):
        n = counts[el]
        parts.append(el + (str(n) if n > 1 else ''))
    return ''.join(parts) if parts else 'H'


def canonical_order(atoms):
    n = len(atoms)
    compute_implicit_h(atoms)
    
    # Group non-H atoms by element
    by_element = {}
    for i, a in enumerate(atoms):
        if a['el'] != 'H':
            if a['el'] not in by_element:
                by_element[a['el']] = []
            by_element[a['el']].append(i)
    
    # For each element, sort atoms by number of explicit H (descending)
    # This gives canonical numbering that matches InChI expectation
    for el in by_element:
        by_element[el].sort(key=lambda i: sum(1 for j in atoms[i]['neighbors'] if atoms[j]['el'] == 'H'), reverse=True)
    
    # Build formula_order: C first (sorted by H), then other elements (A to Z)
    formula_order = []
    for el in sorted(by_element.keys()):
        formula_order.extend(by_element[el])
    
    if not formula_order:
        return list(range(1, n + 1))
    
    # Assign canonical numbers
    canonical_nums = [0] * n
    for sk_idx, orig_idx in enumerate(formula_order):
        canonical_nums[orig_idx] = sk_idx + 1
    
    # H atoms get 0
    for i, a in enumerate(atoms):
        if a['el'] == 'H':
            canonical_nums[i] = 0
    
    return canonical_nums


def build_connectivity(atoms, canonical_nums):
    n = len(atoms)
    
    # Only non-H atoms get numbered
    non_h_atoms = [i for i in range(n) if atoms[i]['el'] != 'H']
    if not non_h_atoms:
        return ''
    
    max_canon = max(c for c in canonical_nums if c > 0)
    
    # Build adjacency: canonical -> list of canonical neighbors
    adj = {c: [] for c in range(1, max_canon + 1)}
    for i in non_h_atoms:
        cni = canonical_nums[i]
        for neigh_orig in atoms[i]['neighbors']:
            if atoms[neigh_orig]['el'] == 'H':
                continue
            neigh_c = canonical_nums[neigh_orig]
            if neigh_c > 0:
                adj[cni].append(neigh_c)
    
    for c in adj:
        adj[c].sort()
    
    # Build connection string: atom lists neighbors with HIGHER number only (to avoid back-refs)
    visited = set()
    parts = []
    
    for pos in range(1, max_canon + 1):
        neighs = adj.get(pos, [])
        first = True
        for nc in neighs:
            if nc > pos and nc not in visited:  # Only forward connections
                if first and not parts:
                    parts.append(str(pos))
                    first = False
                parts.append('-' + str(nc))
                visited.add(nc)
    
    return ''.join(parts)


def compute_charge(atoms):
    return sum(atom.get('charge', 0) for atom in atoms)


def assemble_inchi(atoms, canonical_nums):
    compute_implicit_h(atoms)
    n = len(atoms)
    formula = hill_formula(atoms)
    layers = [f'InChI=1S/{formula}']

    # Only non-H atoms in /c layer
    non_h_atoms = [i for i in range(n) if atoms[i]['el'] != 'H']
    max_canon = max(canonical_nums) if canonical_nums else 0
    
    if non_h_atoms:
        conn = build_connectivity(atoms, canonical_nums)
        layers.append(f'/c{conn}')

    # /h layer: total H on each skeletal atom (explicit + implicit)
    # Format: 3H (1 H on atom 3), 2H2 (2 H on atom 2), 1H3 (3 H on atom 1)
    h_by_skel = {}
    
    for i, a in enumerate(atoms):
        if a['el'] == 'H':
            # Find which skeletal atom this H is attached to
            for neigh in a['neighbors']:
                if atoms[neigh]['el'] != 'H':
                    skel_canon = canonical_nums[neigh]
                    if skel_canon not in h_by_skel:
                        h_by_skel[skel_canon] = 0
                    h_by_skel[skel_canon] += 1
                    break
        else:
            # Add implicit H to the skeletal atom
            nh = a.get('implicit_h', 0)
            if nh > 0:
                cni = canonical_nums[i]
                if cni not in h_by_skel:
                    h_by_skel[cni] = 0
                h_by_skel[cni] += nh

    def _format_h_layer(h_by_skel):
        if not h_by_skel:
            return None
        
        # Group atoms by H count
        by_h = {}
        for pos, nh in h_by_skel.items():
            if nh not in by_h:
                by_h[nh] = []
            by_h[nh].append(pos)
        
        parts = []
        for nh in sorted(by_h.keys()):  # ascending by H count
            atoms = sorted(by_h[nh])  # ascending for range detection
            # Create ranges from sorted list
            ranges = []
            start = atoms[0]
            end = atoms[0]
            for a in atoms[1:]:
                if a == end + 1:
                    end = a
                else:
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(f'{start}-{end}')
                    start = a
                    end = a
            # Handle last range
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f'{start}-{end}')
            
            range_str = ','.join(ranges)
            if nh == 1:
                parts.append(f'{range_str}H')
            else:
                parts.append(f'{range_str}H{nh}')
        
        return ','.join(parts)

    h_str = _format_h_layer(h_by_skel)
    if h_str:
        layers.append('/h' + h_str)

    charge = compute_charge(atoms)
    if charge != 0:
        sign = '+' if charge > 0 else '-'
        layers.append(f'/q{sign}{abs(charge)}')

    return ''.join(layers)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mol_to_inchi.py <molecule.mol>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        content = f.read()
    atoms = parse_mol_v2000(content)
    canonical_nums = canonical_order(atoms)
    inchi = assemble_inchi(atoms, canonical_nums)
    print(inchi)


if __name__ == '__main__':
    main()