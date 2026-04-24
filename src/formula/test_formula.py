#!/usr/bin/env python3
"""Unit tests for formula generation."""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.formula.main import (
    get_element_symbol,
    get_atomic_number,
    count_atoms_from_mol_file,
    format_hill_formula,
    extract_formula_from_inchi,
)


class TestElementLookup(unittest.TestCase):
    """Test element number <-> symbol conversion."""
    
    def test_C(self):
        self.assertEqual(get_element_symbol(6), "C")
        
    def test_H(self):
        self.assertEqual(get_element_symbol(1), "H")
        
    def test_O(self):
        self.assertEqual(get_element_symbol(8), "O")
        
    def test_N(self):
        self.assertEqual(get_element_symbol(7), "N")
        
    def test_S(self):
        self.assertEqual(get_element_symbol(16), "S")
        
    def test_Cl(self):
        self.assertEqual(get_element_symbol(17), "Cl")
        
    def test_Pt(self):
        self.assertEqual(get_element_symbol(78), "Pt")


class TestInchiFormulaExtraction(unittest.TestCase):
    """Test extracting formula from InChI string."""
    
    def test_simple_formula(self):
        inchi = "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"
        self.assertEqual(extract_formula_from_inchi(inchi), "C2H6O")
        
    def test_with_charge(self):
        inchi = "InChI=1S/ClH/h1;/p-1"
        self.assertEqual(extract_formula_from_inchi(inchi), "ClH")
        
    def test_salt(self):
        inchi = "InChI=1S/C25H29.Fe.H.Fe/.Fe"
        self.assertEqual(extract_formula_from_inchi(inchi), "C25H29.Fe.H.Fe")


class TestMolFileParsing(unittest.TestCase):
    """Test MOL file parsing - simple cases."""
    
    def test_ethanol_v2000(self):
        """Ethanol: C2H6O - 9 atoms, 8 bonds."""
        with open("/home/bsmue/code/InChI-skill-set/data/01-ethanol.mol") as f:
            content = f.read()
        atoms = count_atoms_from_mol_file(content, add_implicit_h=False)
        # Expected: 2 C, 1 O, 6 H explicit atoms in the mol file
        self.assertEqual(atoms.get('C'), 2)
        self.assertEqual(atoms.get('O'), 1)
        self.assertEqual(atoms.get('H'), 6, "Should count explicit hydrogens from mol file")
        
    def test_benzene_v2000(self):
        """Benzene: C6H6 - should count explicit hydrogens."""
        with open("/home/bsmue/code/InChI-skill-set/data/65-85-0-2d.mol") as f:
            content = f.read()
        # This is benzoic acid - C7H6O2
        atoms = count_atoms_from_mol_file(content, add_implicit_h=False)
        self.assertEqual(atoms.get('C'), 7, "7 carbons")
        self.assertEqual(atoms.get('O'), 2, "2 oxygens")
        # Benzene ring has 6 H, benzoic acid has no explicit H
        self.assertIsNone(atoms.get('H'), "No explicit H in benzoic acid")


class TestHillFormulaFormat(unittest.TestCase):
    """Test Hill formula formatting."""
    
    def test_simple(self):
        atoms = {'C': 2, 'H': 6, 'O': 1}
        self.assertEqual(format_hill_formula(atoms), "C2H6O")
        
    def test_no_carbon(self):
        atoms = {'H': 2, 'O': 1}
        self.assertEqual(format_hill_formula(atoms), "HO2")
        
    def test_no_hydrogen(self):
        atoms = {'C': 2, 'O': 1}
        self.assertEqual(format_hill_formula(atoms), "C2O")
        
    def test_single_element(self):
        atoms = {'C': 1}
        self.assertEqual(format_hill_formula(atoms), "C")
        
    def test_alphabetic_order(self):
        atoms = {'C': 1, 'Cl': 1, 'N': 1, 'O': 1}
        # C first, then alphabetical: Cl, N, O
        self.assertEqual(format_hill_formula(atoms), "CClNO")


class TestInchiIntegration(unittest.TestCase):
    """Test against known InChI files."""
    
    def test_ethanol(self):
        mol = "/home/bsmue/code/InChI-skill-set/data/01-ethanol.mol"
        inchi = "/home/bsmue/code/InChI-skill-set/data/01-ethanol.inchi"
        
        with open(inchi) as f:
            expected = extract_formula_from_inchi(f.read())
        
        with open(mol) as f:
            content = f.read()
        
        atoms = count_atoms_from_mol_file(content, add_implicit_h=False)
        generated = format_hill_formula(atoms)
        
        # Ethanol: C2H6O - our parsing has explicit H
        # InChI formula includes ALL H (explicit + implicit)
        self.assertEqual(generated, expected, 
            f"Expected {expected}, got {generated}")
        
    def test_cisplatin(self):
        """Cisplatin: Pt with 2 Cl, 2 NH3 - charge: PtCl2H6N2"""
        mol = "/home/bsmue/code/InChI-skill-set/data/cis_platin.mol"
        
        with open(mol) as f:
            content = f.read()
        
        atoms = count_atoms_from_mol_file(content, add_implicit_h=False)
        generated = format_hill_formula(atoms)
        
        # What we generate
        print(f"Cisplatin explicit atoms: {atoms}")
        print(f"Generated: {generated}")


def run_tests():
    """Run unit tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestElementLookup))
    suite.addTests(loader.loadTestsFromTestCase(TestInchiFormulaExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestMolFileParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestHillFormulaFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestInchiIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    run_tests()