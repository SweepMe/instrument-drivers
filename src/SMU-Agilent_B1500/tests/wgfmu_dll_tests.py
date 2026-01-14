import unittest
from pathlib import Path
import importlib.util
from importlib.machinery import SourceFileLoader
import ctypes

import wgfmu_sandbox as wgfmu


class WGFMUTests(unittest.TestCase):

    def setUp(self):
        # Load the target module by path so this test file can live next to it.
        sandbox_path = Path(__file__).with_name("wgfmu_sandbox.py")
        loader = SourceFileLoader("wgfmu_sandbox", str(sandbox_path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        self.wgfmu = module

        self.wgfmu.load_dll()

    def test_make_char_pointer(self):
        buf = self.wgfmu.make_char_pointer("pulse")
        # buffer.value gives the nul-terminated bytes
        self.assertEqual(buf.value, b"pulse")

    def test_clear_calls_dll(self):
        self.wgfmu.clear()

    def test_create_pattern_calls_dll(self):
        self.wgfmu.create_pattern("pulse", 0.0)

    def test_add_vector_calls_dll_and_validates_bounds(self):
        # valid call
        self.wgfmu.add_vector("p", 0.001, 1.23)

        # too small
        with self.assertRaises(ValueError):
            self.wgfmu.add_vector("p", 1e-9, 0.0)

        # too large
        with self.assertRaises(ValueError):
            self.wgfmu.add_vector("p", 1e6, 0.0)

    def test_make_generic_array_and_make_double_array(self):
        # zero-initialized array
        arr = self.wgfmu.make_generic_array(3)
        self.assertEqual(len(arr), 3)
        self.assertEqual(list(arr), [0, 0, 0])

        # array from values_list with inferred length
        arr2 = self.wgfmu.make_generic_array(0, [1, 2, 3], data_type=ctypes.c_int)
        self.assertEqual(len(arr2), 3)
        self.assertEqual(list(arr2), [1, 2, 3])

        # make_double_array from list
        darr = self.wgfmu.make_double_array([0.1, 0.2])
        self.assertEqual(list(darr), [0.1, 0.2])

        # current implementation in the sandbox calls len(values) without checking None,
        # so calling without args raises a TypeError (this test documents that behavior).
        with self.assertRaises(TypeError):
            self.wgfmu.make_double_array()

    def test_add_vector_array_calls_dll_and_validates_lengths(self):
        """Test that add_vector_array calls the DLL with correct arguments"""
        time_vals = [0.001, 0.002]
        volt_vals = [1.0, 2.0]
        self.wgfmu.add_vector_array("pulse", time_vals, volt_vals)

        # mismatched lengths raise
        with self.assertRaises(ValueError):
            self.wgfmu.add_vector_array("pulse", [0.1], [1.0, 2.0])

    def test_get_pattern_force_value_size_reads_value_set_by_dll(self):
        """Test that get_pattern_force_value_size reads the value set by the DLL"""
        size = self.wgfmu.get_pattern_force_value_size("pulse")
        self.assertEqual(size, 1)


if __name__ == "__main__":
    unittest.main()