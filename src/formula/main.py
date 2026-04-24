#!/usr/bin/env python3
"""
Generate Hill molecular formula from MOL files (V2000 and V3000 formats).

This script parses MOL files without external libraries and generates
the molecular formula in Hill format (C first, H last, other elements alphabetically).
"""

import os
import re
import sys
from typing import Dict, Optional, Tuple, List
from pathlib import Path

ELEMENT_TABLE = {
    1: "H", 2: "He", 3: "Li", 4: "Be", 5: "B", 6: "C", 7: "N", 8: "O", 9: "F", 10: "Ne",
    11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar",
    19: "K", 20: "Ca", 21: "Sc", 22: "Ti", 23: "V", 24: "Cr", 25: "Mn", 26: "Fe",
    27: "Co", 28: "Ni", 29: "Cu", 30: "Zn", 31: "Ga", 32: "Ge", 33: "As", 34: "Se",
    35: "Br", 36: "Kr", 37: "Rb", 38: "Sr", 39: "Y", 40: "Zr", 41: "Nb", 42: "Mo",
    43: "Tc", 44: "Ru", 45: "Rh", 46: "Pd", 47: "Ag", 48: "Cd", 49: "In", 50: "Sn",
    51: "Sb", 52: "Te", 53: "I", 54: "Xe", 55: "Cs", 56: "Ba", 57: "La", 58: "Ce",
    59: "Pr", 60: "Nd", 61: "Pm", 62: "Sm", 63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy",
    67: "Ho", 68: "Er", 69: "Tm", 70: "Yb", 71: "Lu", 72: "Hf", 73: "Ta", 74: "W",
    75: "Re", 76: "Os", 77: "Ir", 78: "Pt", 79: "Au", 80: "Hg", 81: "Tl", 82: "Pb",
    83: "Bi", 84: "Po", 85: "At", 86: "Rn", 87: "Fr", 88: "Ra", 89: "Ac", 90: "Th",
    91: "Pa", 92: "U", 93: "Np", 94: "Pu", 95: "Am", 96: "Cm", 97: "Bk", 98: "Cf",
    99: "Es", 100: "Fm", 101: "Md", 102: "No", 103: "Lr", 104: "Rf", 105: "Db",
    106: "Sg", 107: "Bh", 108: "Hs", 109: "Mt", 110: "Ds", 111: "Rg", 112: "Cn",
    113: "Nh", 114: "Fl", 115: "Mc", 116: "Lv", 117: "Ts", 118: "Og",
}

ELEMENT_SYMBOL_TO_NUMBER = {v: k for k, v in ELEMENT_TABLE.items()}

STD_VALENCES = {
    'H': 1, 'He': 0, 'Li': 1, 'Be': 2, 'B': 3, 'C': 4, 'N': 3, 'O': 2, 'F': 1, 'Ne': 0,
    'Na': 1, 'Mg': 2, 'Al': 3, 'Si': 4, 'P': 3, 'S': 2, 'Cl': 1, 'Ar': 0,
    'K': 1, 'Ca': 2, 'Sc': 3, 'Ti': 4, 'V': 5, 'Cr': 3, 'Mn': 2, 'Fe': 3,
    'Co': 3, 'Ni': 3, 'Cu': 2, 'Zn': 2, 'Ga': 3, 'Ge': 4, 'As': 3, 'Se': 2,
    'Br': 1, 'Kr': 0, 'Rb': 1, 'Sr': 2, 'Y': 3, 'Zr': 4, 'Nb': 5, 'Mo': 6,
    'Tc': 6, 'Ru': 6, 'Rh': 6, 'Pd': 4, 'Ag': 1, 'Cd': 2, 'In': 3, 'Sn': 4,
    'Sb': 3, 'Te': 2, 'I': 1, 'Xe': 0, 'Cs': 1, 'Ba': 2, 'La': 3, 'Ce': 4,
    'Pr': 4, 'Nd': 3, 'Pm': 3, 'Sm': 3, 'Eu': 3, 'Gd': 3, 'Tb': 3, 'Dy': 3,
    'Ho': 3, 'Er': 3, 'Tm': 3, 'Yb': 3, 'Lu': 3, 'Hf': 4, 'Ta': 5, 'W': 6,
    'Re': 6, 'Os': 6, 'Ir': 6, 'Pt': 4, 'Au': 3, 'Hg': 2, 'Tl': 3, 'Pb': 4,
    'Bi': 3, 'Po': 4, 'At': 1, 'Rn': 0, 'Fr': 1, 'Ra': 2, 'Ac': 3, 'Th': 4,
    'Pa': 5, 'U': 6, 'Np': 6, 'Pu': 6, 'Am': 4, 'Cm': 4, 'Bk': 4, 'Cf': 4,
    'Es': 4, 'Fm': 4, 'Md': 4, 'No': 4, 'Lr': 3, 'Rf': 4, 'Db': 5, 'Sg': 6,
    'Bh': 6, 'Hs': 6, 'Mt': 6, 'Ds': 6, 'Rg': 5, 'Cn': 4, 'Nh': 5, 'Fl': 6,
    'Mc': 5, 'Lv': 6, 'Ts': 7, 'Og': 8,
}

ELEMENT_VALENCES = {
    'N': {-2: [1], -1: [2], 0: [3, 5], 1: [4], 2: [3]},
    'O': {-2: [0], -1: [1], 0: [2], 1: [3, 5], 2: [4]},
    'S': {-2: [0], -1: [1, 3, 5, 7], 0: [2, 4, 6], 1: [3, 5], 2: [4]},
    'C': {-2: [2], -1: [3], 0: [4], 1: [3], 2: [2]},
    'P': {-2: [1, 3, 5, 7], -1: [2, 4, 6], 0: [3, 5], 1: [4], 2: [3]},
    'B': {-2: [3], -1: [4], 0: [3], 1: [2], 2: [1]},
    'Si': {-2: [2, 4, 6], -1: [3, 5], 0: [4], 1: [3], 2: [2]},
    'Cl': {-2: [0], -1: [0], 0: [1, 3, 5, 7], 1: [2, 4, 6], 2: [3, 5]},
    'Br': {-2: [0], -1: [0], 0: [1, 3, 5, 7], 1: [2, 4, 6], 2: [3, 5]},
    'I': {-2: [0], -1: [0], 0: [1, 3, 5, 7], 1: [2, 4, 6], 2: [3, 5]},
}

def get_standard_valence(element: str, charge: int = 0) -> int:
    """Get standard neutral valence for element."""
    if element in ELEMENT_VALENCES:
        # Find first valence >= 1 for neutral state
        for val in ELEMENT_VALENCES[element].get(0, []):
            if val > 0:
                return val
    # Fallback
    return STD_VALENCES.get(element, 4)


def calculate_implicit_h(element: str, chem_bonds: int, charge: int = 0, has_metal_neighbor: bool = False) -> int:
    """Calculate implicit hydrogens following InChI logic.
    
    Based on get_num_H from util.c
    """
    if element == 'H' or element not in STD_VALENCES:
        return 0
    
    el_valences = ELEMENT_VALENCES.get(element, {0: [4]})
    
    # Find SMALLEST valence >= chem_bonds for this charge state
    charge_state = max(-2, min(2, charge))
    available_valences = el_valences.get(charge_state, el_valences.get(0, []))
    
    # Special case: N(IV) - don't add H if would be 5
    if element == 'N' and charge == 0 and not has_metal_neighbor:
        # Try neutral state: {3, 5}
        for val in available_valences:
            if val >= chem_bonds:
                if val == 5:
                    val = 3  # Special case
                return max(0, val - chem_bonds)
    
    # Special case: S(IV) - if 4 is selected but bonds == 3, use 3
    if element == 'S' and charge == 0 and not has_metal_neighbor:
        for val in available_valences:
            if val >= chem_bonds:
                if val == 4 and chem_bonds == 3:
                    return 0  # 3-3=0
                return max(0, val - chem_bonds)
    
    # Special case: metal neighbors reduce expected valence
    if has_metal_neighbor and element != 'C':
        for val in available_valences:
            if val > chem_bonds and val > 1:
                return max(0, val - 1 - chem_bonds)
    
    # Standard: find smallest matching valence
    for val in available_valences:
        if val >= chem_bonds:
            return max(0, val - chem_bonds)
    
    return 0


def get_element_symbol(atomic_number: int) -> str:
    """Get element symbol from atomic number."""
    if atomic_number in ELEMENT_TABLE:
        return ELEMENT_TABLE[atomic_number]
    return "??"


def get_atomic_number(element_symbol: str) -> int:
    """Get atomic number from element symbol."""
    symbol = element_symbol.strip()
    if symbol in ELEMENT_SYMBOL_TO_NUMBER:
        return ELEMENT_SYMBOL_TO_NUMBER[symbol]
    return 0


def parse_mol_file_v2000(lines: List[str]) -> Dict[str, int]:
    """Parse MOL V2000 format and count atoms by element, including implicit hydrogens."""
    atoms: Dict[str, int] = {}
    
    if len(lines) < 4:
        return atoms
    
    counts_line = lines[3]
    
    if len(counts_line) < 6:
        return atoms
    
    num_atoms = 0
    num_bonds = 0
    
    try:
        num_atoms = int(counts_line[0:3].strip())
        num_bonds = int(counts_line[3:6].strip())
    except ValueError:
        return atoms
    
    if num_atoms <= 0 or num_atoms > 10000:
        return atoms
    
    atom_block_start = 4
    atom_block_end = atom_block_start + num_atoms
    
    if len(lines) < atom_block_end:
        return atoms
    
    atom_elements: List[Tuple[int, str, int]] = []
    for i in range(atom_block_start, atom_block_end):
        if i >= len(lines):
            break
        line = lines[i]
        if not line.startswith('M  V30'):
            parts = line.split()
            if len(parts) >= 11:
                try:
                    atom_num = i - atom_block_start + 1
                    element = parts[3].strip()
                    valence = int(parts[9])
                    if element:
                        atom_elements.append((atom_num, element, valence))
                except (ValueError, IndexError):
                    pass
    
    chem_bonds_val: Dict[int, int] = {}
    
    bond_block_start = atom_block_end
    bond_block_end = bond_block_start + num_bonds
    
    for i in range(bond_block_start, bond_block_end):
        if i >= len(lines):
            break
        line = lines[i]
        if not line.startswith('M  V30') and not line.startswith('M  END'):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    a1 = int(parts[0])
                    a2 = int(parts[1])
                    bond_order = int(parts[2])
                    chem_bonds_val[a1] = chem_bonds_val.get(a1, 0) + bond_order
                    chem_bonds_val[a2] = chem_bonds_val.get(a2, 0) + bond_order
                except (ValueError, IndexError):
                    pass
    
    # Parse charge block (M  CHG)
    atom_charges: Dict[int, int] = {}
    for i in range(bond_block_end, len(lines)):
        line = lines[i].strip()
        if line.startswith('M  CHG'):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    num_charges = int(parts[2])
                    # Format: M  CHG  count  atom1 charge1  atom2 charge2 ...
                    for j in range(num_charges):
                        if 3 + j*2 + 1 < len(parts):
                            atom_idx = int(parts[3 + j*2])
                            charge = int(parts[3 + j*2 + 1])
                            atom_charges[atom_idx] = charge
                except (ValueError, IndexError):
                    pass
        elif line.startswith('M  END') or line.startswith('M  '):
            continue
    
    for atom_num, element, explicit_valence in atom_elements:
        atoms[element] = atoms.get(element, 0) + 1
        
        if element == 'H' or element not in STD_VALENCES:
            continue
        
        charge = atom_charges.get(atom_num, 0)
        
        # Use charge-dependent valence
        charge_state = max(-2, min(2, charge))
        el_valences = ELEMENT_VALENCES.get(element, {0: [4]})
        available_valences = el_valences.get(charge_state, el_valences.get(0, [4]))
        
        actual_bonds = chem_bonds_val.get(atom_num, 0)
        
        # Find smallest valence >= actual bonds
        chosen_val = None
        for val in available_valences:
            if val >= actual_bonds:
                chosen_val = val
                break
        
        if chosen_val is None:
            chosen_val = min([v for v in available_valences if v > 0], default=4)
        
        # Special case: N(IV) - don't add H if would be 5
        if element == 'N' and charge == 0 and chosen_val == 5:
            chosen_val = 3
        
        if actual_bonds > 0 and actual_bonds < chosen_val:
            implicit_h = chosen_val - actual_bonds
            if implicit_h > 0:
                atoms['H'] = atoms.get('H', 0) + implicit_h
    
    return atoms


def parse_mol_file_v2000_explicit(lines: List[str]) -> Dict[str, int]:
    """Parse MOL V2000 format - count only explicit atoms."""
    atoms: Dict[str, int] = {}
    
    if len(lines) < 4:
        return atoms
    
    counts_line = lines[3]
    
    if len(counts_line) < 6:
        return atoms
    
    try:
        num_atoms = int(counts_line[0:3].strip())
        num_bonds = int(counts_line[3:6].strip())
    except ValueError:
        return atoms
    
    if num_atoms <= 0 or num_atoms > 10000:
        return atoms
    
    atom_block_start = 4
    atom_block_end = atom_block_start + num_atoms
    
    if len(lines) < atom_block_end:
        return atoms
    
    for i in range(atom_block_start, atom_block_end):
        if i >= len(lines):
            break
        line = lines[i]
        if not line.startswith('M  V30'):
            parts = line.split()
            if len(parts) >= 4:
                element = parts[3].strip()
                if element:
                    atoms[element] = atoms.get(element, 0) + 1
    
    return atoms


def add_implicit_hydrogens(atoms: Dict[str, int], lines: List[str]) -> Dict[str, int]:
    """Add implicit hydrogens based on valence.
    
    Calculate implicit H from: std_valence - actual_bonds + charge_adjustment
    """
    atoms = dict(atoms)  # Don't modify original
    
    if len(lines) < 4:
        return atoms
    
    counts_line = lines[3]
    if len(counts_line) < 6:
        return atoms
    
    try:
        num_atoms = int(counts_line[0:3].strip())
        num_bonds = int(counts_line[3:6].strip())
    except ValueError:
        return atoms
    
    if num_atoms <= 0 or num_atoms > 10000:
        return atoms
    
    atom_block_start = 4
    atom_block_end = atom_block_start + num_atoms
    
    if len(lines) < atom_block_end:
        return atoms
    
    bond_block_start = atom_block_end
    bond_block_end = bond_block_start + num_bonds
    
    chem_bonds: Dict[int, int] = {}
    
    for i in range(bond_block_start, min(bond_block_end, len(lines))):
        line = lines[i]
        if not line.startswith('M  V30') and not line.startswith('M  END'):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    a1 = int(parts[0])
                    a2 = int(parts[1])
                    bond_type = int(parts[2])
                    chem_bonds[a1] = chem_bonds.get(a1, 0) + bond_type
                    chem_bonds[a2] = chem_bonds.get(a2, 0) + bond_type
                except ValueError:
                    pass
    
    implicit_h = 0
    
    for i in range(atom_block_start, min(atom_block_end, len(lines))):
        line = lines[i]
        if line.startswith('M  V30'):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            atom_num = i - atom_block_start + 1
            element = parts[3].strip()
        except (ValueError, IndexError):
            continue
        
        if not element or element == 'H':
            continue
        
        std_val = STD_VALENCES.get(element, 4)
        
        charge = 0
        if len(parts) >= 7:
            try:
                charge = int(parts[6])
            except ValueError:
                pass
        
        chem_val = chem_bonds.get(atom_num, 0)
        
        needed = calculate_implicit_h(element, chem_val, charge)
        if needed > 0:
            implicit_h += needed
    
    if implicit_h > 0:
        atoms['H'] = atoms.get('H', 0) + implicit_h
    
    return atoms


def parse_mol_file_v3000(lines: List[str]) -> Dict[str, int]:
    """Parse MOL V3000 format and count atoms by element.
    
    Also extracts bond info for implicit H calculation.
    """
    atoms: Dict[str, int] = {}
    atom_elements: Dict[int, str] = {}  # atom index -> element
    chem_bonds: Dict[int, int] = {}  # atom index -> bond count
    in_atom_section = False
    in_bond_section = False
    atom_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Count line - get number of atoms
        if line.startswith('M  V30 COUNTS'):
            parts = line.split()
            try:
                atom_count = int(parts[2])
            except:
                pass
        
        # Atom section
        if line.startswith('M  V30 BEGIN ATOM'):
            in_atom_section = True
            in_bond_section = False
            continue
        
        if line.startswith('M  V30 END ATOM'):
            in_atom_section = False
            continue
        
        # Bond section
        if line.startswith('M  V30 BEGIN BOND'):
            in_bond_section = True
            in_atom_section = False
            continue
        
        if line.startswith('M  V30 END BOND'):
            in_bond_section = False
            continue
        
        # Parse atom
        if in_atom_section and line.startswith('M  V30'):
            parts = line.split(None, 6)
            if len(parts) >= 4 and parts[0] == 'M' and parts[1] == 'V30':
                try:
                    atom_idx = int(parts[2])
                    element = parts[3].strip()
                    if element and element not in ('M', 'V30', 'BEGIN', 'END', 'COLLECTION', 'BOND'):
                        atoms[element] = atoms.get(element, 0) + 1
                        atom_elements[atom_idx] = element
                        chem_bonds[atom_idx] = 0  # init bond count
                except (ValueError, IndexError):
                    pass
        
        # Parse bond - format: M V30 index bond_type atom1 atom2 [CFG=x]
        if in_bond_section and line.startswith('M  V30'):
            # Extract numeric part before any CFG= or other key-val
            import re
            # Match: M V30 <idx> <bond_type> <at1> <at2> ...
            match = re.match(r'M\s+V30\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
            if match:
                try:
                    bond_type = int(match.group(2))
                    at1 = int(match.group(3))
                    at2 = int(match.group(4))
                    # Add to bond counts (ignore stereobonds for H calc)
                    if at1 in chem_bonds:
                        chem_bonds[at1] = chem_bonds.get(at1, 0) + bond_type
                    if at2 in chem_bonds:
                        chem_bonds[at2] = chem_bonds.get(at2, 0) + bond_type
                except:
                    pass
    
    # Calculate implicit H for each atom
    if chem_bonds:
        for atom_idx, element in atom_elements.items():
            if element == 'H' or element not in STD_VALENCES:
                continue
            
            std_val = STD_VALENCES.get(element, 4)
            actual_bonds = chem_bonds.get(atom_idx, 0)
            
            if actual_bonds > 0 and actual_bonds < std_val:
                implicit_h = std_val - actual_bonds
                atoms['H'] = atoms.get('H', 0) + implicit_h
    
    return atoms


def count_atoms_from_mol_file(mol_content: str, add_implicit_h: bool = True) -> Dict[str, int]:
    """Count atoms by element from mol file content.
    
    If add_implicit_h is True, add implicit hydrogens based on standard valence.
    If False, count only explicit atoms.
    """
    atoms: Dict[str, int] = {}
    lines = mol_content.split('\n')
    
    has_v2000 = any('V2000' in line for line in lines)
    has_v3000 = any('V3000' in line for line in lines)
    has_only_v2000 = has_v2000 and not has_v3000
    
    if has_only_v2000:
        # Pure V2000 - use best parser (treats implicit H correctly)
        if add_implicit_h:
            atoms = parse_mol_file_v2000(lines)
        else:
            atoms = parse_mol_file_v2000_explicit(lines)
        return atoms if atoms else {}
    
    if has_v3000:
        # V3000 or mixed format - use V3000 parser
        atoms = parse_mol_file_v3000(lines)
        if atoms and add_implicit_h:
            atoms = add_implicit_hydrogens(atoms, lines)
        return atoms if atoms else {}
    
    # Fallback
    if add_implicit_h:
        atoms = parse_mol_file_v2000(lines)
    else:
        atoms = parse_mol_file_v2000_explicit(lines)
    
    return atoms if atoms else {}


def format_hill_formula(atoms: Dict[str, int]) -> str:
    """Format atoms dictionary into Hill formula string.
    
    Hill formula ordering:
    - C first if present, then H second (after C)
    - For compounds without C: alphabetical order
    """
    if not atoms:
        return ""
    
    num_c = atoms.get('C', 0)
    num_h = atoms.get('H', 0)
    
    other_elements = {k: v for k, v in atoms.items() if k != 'C' and k != 'H'}
    sorted_elements = sorted(other_elements.keys())
    
    formula_parts = []
    
    if num_c > 0:
        # Has carbon - use Hill ordering (C first, then H, then alphabetical)
        if num_c > 1:
            formula_parts.append("C" + str(num_c))
        else:
            formula_parts.append("C")
            
        if num_h > 0:
            if num_h > 1:
                formula_parts.append("H" + str(num_h))
            else:
                formula_parts.append("H")
        
        for elem in sorted_elements:
            count = other_elements[elem]
            if count > 0:
                if count > 1:
                    formula_parts.append(elem + str(count))
                else:
                    formula_parts.append(elem)
    else:
        # No carbon - use alphabetical ordering
        all_alpha = sorted(atoms.keys())
        for elem in all_alpha:
            count = atoms[elem]
            if count > 0:
                if count > 1:
                    formula_parts.append(elem + str(count))
                else:
                    formula_parts.append(elem)
    
    return ''.join(formula_parts)


def extract_formula_from_inchi(inchi: str) -> Optional[str]:
    """Extract formula from InChI string."""
    if not inchi:
        return None
    
    inchi = inchi.strip()
    
    if not inchi.startswith('InChI='):
        return None
    
    inchi = inchi[6:]
    
    if inchi.startswith('1S/'):
        inchi = inchi[3:]
    elif inchi.startswith('1/'):
        inchi = inchi[2:]
    
    if not inchi:
        return None
    
    formula = inchi.split('/')[0]
    formula = formula.strip()
    
    if formula in ('1', '1S'):
        return None
    
    return formula


def generate_formula_from_mol(mol_file_path: str) -> str:
    """Generate Hill formula from MOL file.
    
    Uses explicit+implicit approach.
    """
    try:
        with open(mol_file_path, 'r') as f:
            content = f.read()
    except (IOError, OSError):
        return ""
    
    atoms = count_atoms_from_mol_file(content, add_implicit_h=True)
    return format_hill_formula(atoms)

def print_hill_formula_test():

    filename_base = "/home/bsmue/code/InChI-skill-set/src/formula/../../data/test_file_2_0094"
    
    filename_mol = filename_base + ".mol"
    filename_inchi = filename_base + ".inchi"

    gen_hill_f_str = generate_formula_from_mol(filename_mol)
    
    inchi_str = ""
    with open(filename_inchi, 'r', encoding='utf-8') as file:
        inchi_str = file.read()
    
    exp_hill_f_str = extract_formula_from_inchi(inchi_str)
    
    print(exp_hill_f_str, gen_hill_f_str)

def print_hill_formula():

    path_name = '/home/bsmue/code/InChI-skill-set/src/formula/../../data'

    directory = Path(path_name)
    
    files = [f for f in directory.iterdir() if f.is_file() and "mol" in f.name]

    count_wrong = 0
    count_correct = 0
    for file in files:
        
        filename_base = path_name + "/" + file.stem
        
        filename_mol = filename_base + ".mol"
        filename_inchi = filename_base + ".inchi"
        
        if os.path.exists(filename_mol) and os.path.exists(filename_inchi):
            
            gen_hill_f_str = generate_formula_from_mol(filename_mol)
            
            inchi_str = ""
            with open(filename_inchi, 'r', encoding='utf-8') as file:
                inchi_str = file.read()
            
            exp_hill_f_str = extract_formula_from_inchi(inchi_str)
            
            count_correct +=  (exp_hill_f_str == gen_hill_f_str)
            count_wrong +=  (exp_hill_f_str != gen_hill_f_str)
            
            if exp_hill_f_str != gen_hill_f_str:
                print(exp_hill_f_str, gen_hill_f_str, file.name)
                
        else:
            print(filename_base)
    
    print(count_correct, count_wrong, count_correct + count_wrong)

if __name__ == '__main__':
    
    
    print_hill_formula()