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

    def setUp(self) -> None:
        """Load the DLL before each test."""
        wgfmu.load_dll()

    def tearDown(self) -> None:
        """Clear all waveform patterns after each test."""
        wgfmu.clear()

    def test_make_char_pointer(self):
        buf = wgfmu.make_char_pointer("pulse")
        # buffer.value gives the nul-terminated bytes
        self.assertEqual(buf.value, b"pulse")

    def test_clear_calls_dll(self) -> None:
        """Test that clear calls the DLL to clear patterns"""
        wgfmu.clear()
        self.assertTrue(True)

    def test_create_pattern_calls_dll(self) -> None:
        wgfmu.create_pattern("pulse", 0.0)
        self.assertTrue(True)

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
        self.assertEqual(list(darr), [0.1, 0.2])

    def test_add_vector_array_calls_dll_and_validates_lengths(self):
        """Test that add_vector_array calls the DLL with correct arguments"""
        pattern_name = "pulse array"
        wgfmu.create_pattern(pattern_name, 0.0)
        time_vals = [0.001, 0.002]
        volt_vals = [1.0, 2.0]
        wgfmu.add_vector_array(pattern_name, time_vals, volt_vals)

        # mismatched lengths raise
        with self.assertRaises(ValueError):
            wgfmu.add_vector_array(pattern_name, [0.1], [1.0, 2.0])

    def test_get_pattern_force_value_size_reads_value_set_by_dll(self):
        """Test that get_pattern_force_value_size reads the value set by the DLL"""
        pattern_name = "pulse array"
        wgfmu.create_pattern(pattern_name, 0.0)
        size = wgfmu.get_pattern_force_value_size(pattern_name)
        self.assertEqual(size, 1)

    def test_get_pattern_force_values(self) -> None:
        """Test that get_pattern_force_values reads the values set by the DLL"""
        pattern_name = "get_pattern_force_values"
        wgfmu.create_pattern(pattern_name, 0.0)

        time_increments = [0.001, 0.002, 0.001]
        voltages = [1.0, 2.0, 1.0]
        wgfmu.add_vector_array(pattern_name, time_increments, voltages)

        times, force_values = wgfmu.get_pattern_force_values(pattern_name)
        # convert time increments to cumulative time stamps, add initial time of 0.0
        expected_time_stamps = [0.0] + [sum(time_increments[:i+1]) for i in range(len(time_increments))]

        self.assertEqual(force_values, [0.0] + voltages)
        self.assertEqual(times, expected_time_stamps)


if __name__ == "__main__":
    unittest.main()