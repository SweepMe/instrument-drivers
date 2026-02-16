import unittest
from pathlib import Path
import ctypes

# add libs folder to sys.path to enable import of pywgfmu
import sys
here = Path(__file__).resolve().parent
libs_folder = here.parent.parent / "libs"
if str(libs_folder) not in sys.path:
    sys.path.insert(0, str(libs_folder))

from pywgfmu import wgfmu


class WGFMUTests(unittest.TestCase):

    def setUp(self):
        wgfmu.load_dll()

    def test_make_char_pointer(self):
        buf = wgfmu.make_char_pointer("pulse")
        # buffer.value gives the nul-terminated bytes
        self.assertEqual(buf.value, b"pulse")

    def test_clear_calls_dll(self):
        wgfmu.clear()

    def test_create_pattern_calls_dll(self):
        wgfmu.create_pattern("pulse", 0.0)

    def test_add_vector_calls_dll_and_validates_bounds(self):
        # valid call
        wgfmu.add_vector("p", 0.001, 1.23)

        # too small
        with self.assertRaises(ValueError):
            wgfmu.add_vector("p", 1e-9, 0.0)

        # too large
        with self.assertRaises(ValueError):
            wgfmu.add_vector("p", 1e6, 0.0)

    def test_make_generic_array_and_make_double_array(self):
        # zero-initialized array
        arr = wgfmu.make_generic_array(3)
        self.assertEqual(len(arr), 3)
        self.assertEqual(list(arr), [0, 0, 0])

        # array from values_list with inferred length
        arr2 = wgfmu.make_generic_array(0, [1, 2, 3], data_type=ctypes.c_int)
        self.assertEqual(len(arr2), 3)
        self.assertEqual(list(arr2), [1, 2, 3])

        # make_double_array from list
        darr = wgfmu.make_double_array([0.1, 0.2])
        print(darr, list(darr), len(darr))
        self.assertEqual(list(darr), [0.1, 0.2])

    def test_add_vector_array_calls_dll_and_validates_lengths(self):
        """Test that add_vector_array calls the DLL with correct arguments"""
        wgfmu.create_pattern("pulse array", 0.0)
        time_vals = [0.001, 0.002]
        volt_vals = [1.0, 2.0]
        wgfmu.add_vector_array("pulse array", time_vals, volt_vals)

        # mismatched lengths raise
        with self.assertRaises(ValueError):
            wgfmu.add_vector_array("pulse", [0.1], [1.0, 2.0])

    def test_get_pattern_force_value_size_reads_value_set_by_dll(self):
        """Test that get_pattern_force_value_size reads the value set by the DLL"""
        size = wgfmu.get_pattern_force_value_size("pulse")
        self.assertEqual(size, 1)


if __name__ == "__main__":
    unittest.main()